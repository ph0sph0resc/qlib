# data/cache.py 模块文档

## 文件概述

此文件实现了Qlib的多层缓存机制，包括内存缓存和磁盘缓存，用于优化数据访问性能。缓存系统支持表达式缓存、数据集缓存和日历缓存，并提供LRU淘汰策略和过期管理。

## 类与函数

### QlibCacheException 类

**继承关系**:
- 继承自 RuntimeError

**说明**:
- Qlib缓存异常类
- 用于标识缓存相关的运行时错误

### MemCacheUnit 类

**继承关系**:
- 继承自 abc.ABC

**主要属性**:
- `size_limit`: 缓存大小限制，0表示无限制
- `_size`: 当前缓存总大小
- `od`: OrderedDict对象，维护缓存项顺序

**主要方法**:

```python
def __init__(self, *args, size_limit=0, **kwargs)
```
- 初始化内存缓存单元
- 参数：
  - size_limit: 缓存大小限制
  - kwargs: 扩展参数

```python
def __setitem__(self, key, value)
```
- 设置缓存项，自动调整大小和触发淘汰
- 实现LRU淘汰策略：访问后移到末尾
- 超过大小限制时移除最旧项

```python
def __getitem__(self, key)
```
- 获取缓存项，访问后移到末尾

```python
def __contains__(self, key) -> bool
```
- 检查键是否存在

```python
def __len__(self) -> int
```
- 返回缓存项数量

```python
def __repr__(self) -> str
```
- 返回缓存对象的字符串表示

```python
def set_limit_size(self, limit)
```
- 动态设置缓存大小限制

```python
@property
def limited(self) -> bool
```
- 返回是否有大小限制

```python
@property
def total_size(self) -> int
```
- 返回当前缓存总大小

```python
def clear(self)
```
- 清空缓存

```python
def popitem(self, last=True) -> tuple
```
- 移除缓存项
- last=True: 移除最旧项，last=False: 移除最新项

```python
def pop(self, key)
```
- 移除指定键的缓存项

```python
def _adjust_size(self, key, value)
```
- 调整缓存大小（内部方法）

```python
@abstractmethod
def _get_value_size(self, value) -> int
```
- 抽象方法：获取值的字节大小
- 子类必须实现

### MemCacheLengthUnit 类

**继承关系**:
- 继承自 MemCacheUnit

**说明**:
- 基于长度的缓存单元
- 每个缓存项大小计为1

**主要方法**:

```python
def _get_value_size(self, value) -> int
```
- 返回1，固定大小

### MemCacheSizeofUnit 类

**继承关系**:
- 继承自 MemCacheUnit

**说明**:
- 基于sys.getsizeof()的缓存单元
- 使用sys.getsizeof()计算值的大小

**主要方法**:

```python
def _get_value_size(self, value) -> int
```
- 返回sys.getsizeof(value)

### MemCache 类

**继承关系**:
- 无直接父类

**主要属性**:
- `__calendar_mem_cache`: 日历内存缓存单元
- `__instrument_mem_cache`: 标的物内存缓存单元
- `__feature_mem_cache`: 特征内存缓存单元

**主要方法**:

```python
def __init__(self, mem_cache_size_limit=None, limit_type="length")
```
- 初始化三路内存缓存
- 参数：
  - mem_cache_size_limit: 缓存大小限制，None则使用配置默认值
  - limit_type: 限制类型，"length"或"sizeof"

```python
def __getitem__(self, key) -> MemCacheUnit
```
- 根据键获取对应的缓存单元
- 键值：'c'为日历，'i'为标的物，'f'为特征

```python
def clear(self)
```
- 清空所有缓存

### MemCacheExpire 类

**继承关系**:
- 无直接父类

**主要属性**:
- `CACHE_EXPIRE`: 缓存过期时间（秒）

**主要方法**:

```python
@staticmethod
def set_cache(mem_cache, key, value)
```
- 设置缓存项，附带时间戳
- 存储格式：{key: (value, timestamp)}

```python
@staticmethod
def get_cache(mem_cache, key) -> tuple
```
- 获取缓存项
- 返回： (value, expired)
- expired: True表示缓存已过期

### CacheUtils 类

**继承关系**:
- 无直接父类

**主要属性**:
- `LOCK_ID`: Redis锁标识，固定为"QLIB"

**主要方法**:

```python
@staticmethod
def organize_meta_file()
```
- 整理元数据文件（占位函数）

```python
@staticmethod
def reset_lock()
```
- 重置Redis所有锁

```python
@staticmethod
def visit(cache_path: Union[str, Path])
```
- 访问缓存文件，更新元数据
- 增加访问计数和最后访问时间

```python
@staticmethod
def acquire(lock, lock_name)
```
- 获取Redis锁
- 处理已获取锁的异常情况

```python
@staticmethod
@contextlib.contextmanager
def reader_lock(redis_t, lock_name: str)
```
- 读者锁上下文管理器
- 支持多个读者并发访问
- 使用读者-写者锁模式

```python
@staticmethod
@contextlib.contextmanager
def writer_lock(redis_t, lock_name: str)
```
- 写者锁上下文管理器
- 独占式锁，写时独占访问

### BaseProviderCache 类

**继承关系**:
- 无直接父类

**主要属性**:
- `provider`: 包装的数据提供者
- `logger`: 模块日志记录器

**主要方法**:

```python
def __init__(self, provider)
```
- 初始化缓存包装器
- 包装提供者以添加缓存功能

```python
def __getattr__(self, attr)
```
- 代理访问提供者的属性
- 支持透明访问提供者方法

```python
@staticmethod
def check_cache_exists(cache_path: Union[str, Path], suffix_list=Iterable=(".index", ".meta")) -> bool
```
- 检查缓存文件是否存在
- 检查主文件和所有后缀文件

```python
@staticmethod
def clear_cache(cache_path: Union[str, Path])
```
- 清除缓存文件
- 删除主文件和所有关联文件(.meta, .index等)

```python
@staticmethod
def get_cache_dir(dir_name: str, freq: str = None) -> Path
```
- 获取缓存目录路径
- 根据频率创建对应的缓存目录

### ExpressionCache 类

**继承关系**:
- 继承自 BaseProviderCache

**说明**:
- 表达式缓存抽象基类
- 包装ExpressionProvider添加缓存机制

**主要方法**:

```python
def expression(self, instrument, field, start_time, end_time, freq) -> pd.Series
```
- 获取表达式数据（带缓存）
- 优先使用缓存，失败时回退到provider

```python
@abstractmethod
def _uri(self, instrument, field, start_time, end_time, freq) -> str
```
- 抽象方法：生成表达式缓存文件URI
- 子类必须实现

```python
@abstractmethod
def _expression(self, instrument, field, start_time, end_time, freq) -> pd.Series
```
- 抽象方法：使用缓存获取表达式数据
- 子类必须实现

```python
def update(self, cache_uri: Union[str, Path], freq: str = "day") -> int
```
- 更新表达式缓存到最新日历
- 返回：0(成功)/1(无需更新)/2(更新失败)

### DatasetCache 类

**继承关系**:
- 继承自 BaseProviderCache

**说明**:
- 数据集缓存抽象基类
- 包装DatasetProvider添加缓存机制

**主要属性**:
- `HDF_KEY`: HDF存储键，默认为"df"

**主要方法**:

```python
def dataset(self, instruments, fields, start_time=None, end_time=None, freq="day",
           disk_cache=1, inst_processors=[]) -> pd.DataFrame
```
- 获取数据集（带缓存）
- disk_cache=0: 跳过缓存
- disk_cache=1: 使用缓存
- disk_cache=2: 替换缓存

```python
@abstractmethod
def _uri(self, instruments, fields, start_time, end_time, freq, **kwargs) -> str
```
- 抽象方法：生成数据集缓存文件URI
- 子类必须实现

```python
@abstractmethod
def _dataset(self, instruments, fields, start_time=None, end_time=None,
             freq="day", disk_cache=1, inst_processors=[]) -> pd.DataFrame
```
- 抽象方法：使用缓存获取数据集
- 子类必须实现

```python
@abstractmethod
def _dataset_uri(self, instruments, fields, start_time=None, end_time=None,
                freq="day", disk_cache=1, inst_processors=[]) -> str
```
- 抽象方法：获取数据集缓存URI
- 子类必须实现

```python
def update(self, cache_uri: Union[str, Path], freq: str = "day") -> int
```
- 更新数据集缓存到最新日历
- 返回：0(成功)/1(无需更新)/2(更新失败)

```python
@staticmethod
def cache_to_origin_data(data, fields) -> pd.DataFrame
```
- 将缓存数据转换为原始数据格式
- 处理字段名规范化

```python
@staticmethod
def normalize_uri_args(instruments, fields, freq) -> tuple
```
- 规范化URI参数

### DiskExpressionCache 类

**继承关系**:
- 继承自 ExpressionCache

**说明**:
- 磁盘表达式缓存实现（用于服务器端）
- 支持二进制文件格式存储

**主要属性**:
- `r`: Redis连接
- `remote`: 是否为远程客户端模式

**主要方法**:

```python
def __init__(self, provider, **kwargs)
```
- 初始化磁盘表达式缓存
- 建立Redis连接
- remote=True: 客户端模式，禁用写入

```python
def get_cache_dir(self, freq: str = None) -> Path
```
- 获取表达式缓存目录

```python
def _uri(self, instrument, field, start_time, end_time, freq) -> str
```
- 生成缓存文件URI哈希值

```python
def _expression(self, instrument, field, start_time=None, end_time=None, freq="day") -> pd.Series
```
- 实现表达式缓存逻辑
- 优先读取缓存
- 缓存不存在时生成缓存（非原始特征）

```python
def gen_expression_cache(self, expression_data, cache_path, instrument, field, freq, last_update)
```
- 生成表达式缓存文件
- 格式：.bin(数据) + .meta(元数据)

)

```python
def update(self, sid, cache_uri, freq: str = "day") -> int
```
- 更新表达式缓存
- 追加新数据并更新元信息

### DiskDatasetCache 类

**继承关系**:
- 继承自 DatasetCache

**说明**:
- 磁盘数据集缓存实现（用于服务器端）
- 支持HDF格式存储和索引优化

**主要属性**:
- `r`: Redis连接
- `remote`: 是否为远程客户端模式

**主要方法**:

```python
def __init__(self, provider, **kwargs)
```
- 初始化磁盘数据集缓存
- 建立Redis连接

```python
@staticmethod
def _uri(instruments, fields, start_time, end_time, freq, disk_cache=1, inst_processors=[], **kwargs) -> str
```
- 生成数据集缓存URI哈希值

```python
def get_cache_dir(self, freq: str = None) -> Path
```
- 获取数据集缓存目录

```python
@classmethod
def read_data_from_cache(cls, cache_path: Union[str, Path], start_time, end_time, fields) -> pd.DataFrame
```
- 从磁盘缓存读取数据集
- 使用索引文件快速定位数据

```python
def _dataset(self, instruments, fields, start_time=None, end_time=None,
             freq="day", disk_cache=0, inst_processors=[]) -> pd.DataFrame
```
- 实现数据集缓存逻辑
- disk_cache=0: 跳过
- disk_cache=1: 使用
- disk_cache=2: 替换

```python
def _dataset_uri(self, instruments, fields, start_time=None, end_time=None,
                 freq="day", disk_cache=0, inst_processors=[]) -> str
```
- 获取数据集缓存URI
- disk_cache=0: 仅检查表达式缓存
- disk_cache=1: 返回缓存文件URI

```python
def gen_dataset_cache(self, cache_path: Union[str, Path], instruments, fields, freq, inst_processors=[])
```
- 生成数据集缓存
- 格式：主文件(HDF) + .index(索引) + .meta(元数据)

```python
def update(self, cache_uri, freq: str = "day") -> int
```
- 更新数据集缓存
- 追加新数据并更新索引

#### IndexManager 类

**说明**:
- 磁盘数据集索引管理内部类
- 负责维护数据集的时间索引

**主要方法**:

```python
def __init__(self, cache_path: Union[str, Path])
```
- 初始化索引管理器

```python
def get_index(self, start_time=None, end_time=None) -> pd.DataFrame
```
- 获取时间索引数据

```python
def sync_to_disk(self)
```
- 同步索引数据到磁盘

```python
def sync_from_disk(self)
```
- 从磁盘同步索引数据

```python
def update(self, data, sync=True)
```
- 更新索引数据

```python
def append_index(self, data, to_disk=True)
```
- 追加索引数据

```python
@staticmethod
def build_index_from_data(data, start_index=0) -> pd.DataFrame
```
- 从数据构建索引

### SimpleDatasetCache 类

**继承关系**:
- 继承自 DatasetCache

**说明**:
- 简单数据集缓存实现
- 使用Pickle格式存储
- 适用于本地或客户端使用

**主要属性**:
- `local_cache_path`: 本地缓存路径

**主要方法**:

```python
def __init__(self, provider)
```
- 初始化简单数据集缓存
- 从配置读取缓存路径

```python
def _uri(self, instruments, fields, start_time, end_time, freq, disk_cache=1, inst_processors=[], **kwargs) -> str
```
- 生成缓存文件URI

```python
def _dataset(self, instruments, fields, start_time=None, end_time=None,
             freq="day", disk_cache=1, inst_processors=[]) -> pd.DataFrame
```
- 实现简单数据集缓存逻辑
- 使用Pickle格式

### DatasetURICache 类

**继承关系**:
- 继承自 DatasetCache

**说明**:
- 数据集URI缓存实现
- 用于服务器端管理缓存URI

**主要方法**:

```python
def _uri(self, instruments, fields, start_time, end_time, freq, disk_cache=1, inst_processors=[], **kwargs) -> str
```
- 生成数据集URI

```python
def dataset(self, instruments, fields, start_time=None, end_time=None,
            freq="day", disk_cache=0, inst_processors=[]) -> pd.DataFrame
```
- 实现数据集URI缓存逻辑
- 检查URI缓存有效性

### CalendarCache 类

**继承关系**:
- 继承自 BaseProviderCache

**说明**:
- 日历缓存抽象基类（占位）

### MemoryCalendarCache 类

**继承关系**:
- 继承自 CalendarCache

**说明**:
- 内存日历缓存实现
- 使用MemCacheExpire实现过期管理

**主要方法**:

```python
def calendar(self, start_time=None, end_time=None, freq="day", future=False) -> list
```
- 获取日历（带内存缓存）
- 使用MemCacheExpire检查缓存过期

## 流程图

### 缓存查找流程

```
数据请求
    ↓
MemCache (内存缓存)
    ↓
命中？ → 返回数据
    ↓
未命中 → DiskCache (磁盘缓存)
    ↓
命中？ → 返回数据
    ↓
未命中 → Provider (数据提供者)
    ↓
生成数据并缓存
```

### 读者-写者锁流程

```
读者1请求
    ↓
读者锁 → 增加读者计数
    ↓
    无写者？ → 读取数据
    ↓
减少读者计数
    ↓
0个读者？ → 释放读锁

写者请求
    ↓
写者锁 → 等待0个读者
    ↓
写入数据
    ↓
释放写锁
```

## 与其他模块的关系

### 依赖模块

- **qlib.config**: 配置管理（缓存路径、大小等）
- **qlib.utils**: 工具函数（哈希、规范化等）
- **redis_lock**: Redis分布式锁
- **pandas/numpy**: 数据处理

### 被导出模块

- **qlib.data.data**: 数据提供者基类
- **qlib.data.base**: 表达式基类

## 设计模式

### 缓存策略模式

采用多级缓存策略：

```
LRU内存缓存 (MemCache)
    ↓
磁盘缓存 (DiskCache)
    ↓
数据提供者 (Provider)
    ↓
存储后端 (Storage)
```

### 缓存键生成

使用哈希生成统一缓存键：

```python
# 表达式缓存键
cache_key = hash_args(instrument, field, freq)

# 数据集缓存键
cache_key = hash_args(instruments, fields, freq, disk_cache, inst_processors)
```

### 锁模式

使用Redis分布式锁实现并发安全：

```
写操作
    ↓
获取写锁
    ↓
写入数据
    ↓
释放写锁

读操作（多读者）
    ↓
获取读锁
    ↓
增加读者计数
    ↓
读取数据
    ↓
减少读者计数
    ↓
0个读者时释放读锁
```

## 使用示例

### 配置缓存

```python
import qlib

# 配置内存缓存
qlib.init(
    mem_cache_size_limit=1000,
    mem_cache_limit_type="length"
)

# 配置磁盘缓存
qlib.init(
    expression_cache={
        "class": "DiskExpressionCache",
        "module_path": "qlib.data.cache"
    },
    dataset_cache={
        "class": "DiskDatasetCache",
        "module_path": "qlib.data.cache"
    }
)
```

### 使用全局缓存

```python
from qlib.data.cache import H

# 直接访问内存缓存
calendar_cache = H["c"]  # 日历缓存
instrument_cache = H["i"]  # 标的物缓存
feature_cache = H["f"]  # 特征缓存

# 设置缓存
H["f"][cache_key] = data_series
```

## 扩展点

### 自定义缓存实现

```python
from qlib.data.cache import ExpressionCache
from pathlib import Path

class CustomExpressionCache(ExpressionCache):
    def _uri(self, instrument, field, start_time, end_time, freq):
        # 自定义URI生成逻辑
        return f"{instrument}_{field}_{freq}"

    def _expression(self, instrument, field, start_time, end_time, freq):
        # 自定义缓存读写逻辑
        cache_path = self._uri(instrument, field, start_time, end_time, freq)
        # 实现缓存读取和生成
        return cached_data

    def update(self, cache_uri, freq="day"):
        # 自定义更新逻辑
        pass
```

### 自定义缓存单元

```python
from qlib.data.cache import MemCacheUnit

class CustomMemCacheUnit(MemCacheUnit):
    def _get_value_size(self, value):
        # 自定义大小计算逻辑
        return len(str(value))  # 示例：基于字符串长度
```

## 注意事项

1. **缓存一致性**: 内存和磁盘缓存需要保持一致
2. **并发安全**: 使用Redis锁避免写入冲突
3. **过期管理**: MemCacheExpire支持缓存过期
4. **LRU淘汰**: MemCacheUnit实现LRU淘汰策略
5. **元数据维护**: visit()方法维护访问统计
6. **格式转换**: cache_to_origin_data()处理字段名转换
7. **远程模式**: remote=True时禁用写操作
8. **路径管理**: 自动创建缓存目录结构

## 相关文件

- **qlib/data/data.py**: 数据提供者实现
- **qlib/data/base.py**: 表达式基类
- **qlib/config**: 配置管理
- **qlib/utils**: 工具函数
