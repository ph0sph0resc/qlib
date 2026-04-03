# data/storage/file_storage.py 模块文档

## 文件概述

此文件实现了基于文件系统的存储后端（File Storage），包括FileCalendarStorage、FileInstrumentStorage和FileFeatureStorage。这是Qlib默认的数据存储实现，使用文本文件和二进制文件格式存储数据。

## 类与函数

### FileStorageMixin 类

**继承关系**:
- 无直接父类

**说明**:
- 文件存储混入类
- 简化provider_uri、freq、storage_name、file_name等属性

**主要属性**:

```python
@property
def provider_uri(self)
```
- 获取provider URI
- 优先级：1. self._provider_uri，2. C中的provider_uri

```python
@property
def dpm(self)
```
- 获取数据路径管理器
- 优先级：1. C.dpm，2. C.DataPathManager(self._provider_uri)

```python
@property
def support_freq(self) -> List[str]
```
- 获取支持的频率列表
- 自动检测provider_uri或C中的可用频率

```python
@property
def uri(self) -> Path
```
- 获取文件URI路径
- 自动检查频率支持性

```python
def check(self)
```
- 检查文件URI是否存在
- 抛出ValueError

### FileCalendarStorage 类

**继承关系**:
- 继承自 FileStorageMixin, CalendarStorage

**说明**:
- 日历文件的文件存储实现
- 支持文本文件格式（.txt）

**主要属性**:

```python
@property
def file_name(self) -> str
```
- 返回文件名
- 格式：`{freq}_future.txt`或`{freq}.txt`

```python
@property
def _freq_file(self) -> str
```
- 返回实际读取的频率
- 可能与请求频率不同，支持重采样

**主要方法**:

```python
def __init__(self, freq, future, provider_uri=None, **kwargs)
```
- 初始化日历文件存储
- 参数：
  - freq: 数据频率
  - future: 是否包含未来交易日
  - provider_uri: 自定义provider URI
- kwargs: 扩展参数

```python
def _read_calendar(self) -> List[CalVT]
```
- 从文件读取日历数据
- 返回：时间戳字符串列表
- 格式：每行一个时间戳字符串

```python
def _write_calendar(self, values: Iterable[CalVT], mode="wb")
```
- 写入日历数据到文件
- 参数：
  - values: 时间戳列表
  - mode: "wb"（写）或"ab"（追加）

```python
def load_calendar(self, freq, future) -> List[CalVT]
```
- 加载日历数据（带缓存）
- 检查缓存，缺失时从文件读取
- 支持频率转换

```python
def extend(self, values: Iterable[CalVT])
```
- 扩展日历数据
- 使用追加模式写

```python
def clear(self)
```
- 清空日历数据

```python
def index(self, value: CalVT) -> int
```
- 获取时间戳索引
- 返回：二分查找位置

```python
def insert(self, index: int, value: CalVT)
```
- 在指定位置插入时间戳

```python
def remove(self, value: CalVT)
```
- 移除时间戳

```python
def __setitem__(self, i: Union[int, slice], values: Union[CalVT, Iterable[CalVT]])
```
- 设置日历数据
- 支持单个位置、切片设置

```python
def __delitem__(self, i: Union[int, slice])
```
- 删除日历数据
- 支持单个位置、切片删除

```python
def __getitem__(self, i: Union[int, slice]) -> Union[CalVT, List[CalVT]]
```
- 获取日历数据
- 支持单个位置、切片访问

```python
def __len__(self) -> int
```
- 返回日历长度

### FileInstrumentStorage 类

**继承关系**:
- 继承自 FileStorageMixin, InstrumentStorage

**说明**:
- 标的物文件的文件存储实现
- 使用制表符分隔的文本格式（.txt）

**主要常量**:

```python
INSTRUMENT_SEP = "\t"
INSTRUMENT_START_FIELD = "start_datetime"
INSTRUMENT_END_FIELD = "end_datetime"
SYMBOL_FIELD_NAME = "instrument"
```

**主要属性**:

```python
@property
def file_name(self) -> str
```
- 返回文件名
- 格式：`{market}.txt`

**主要方法**:

```python
def _read_instrument(self) -> Dict[InstKT, InstVT]
```
- 从文件读取标的物数据
- 返回：{标的物代码: [(开始时间, 结束时间), ...]}

```python
def _write_instrument(self, data: Dict[InstKT, InstVT] = None)
```
- 写入标的物数据到文件
- 格式：每行：标的物代码\t开始时间\t结束时间

```python
def clear(self) -> None
```
- 清空标的物数据

```python
def data(self) -> Dict[InstKT, InstVT]
```
- 获取所有标的物数据

```python
def __setitem__(self, k: InstKT, v: InstVT) -> None
```
- 设置指定标的物的数据

```python
def __delitem__(self, k: InstKT) -> None
```
- 删除指定标的物

```python
def __getitem__(self, k: InstKT) -> InstVT
```
- 获取指定标的物的数据

```python
def __delitem__(self, k: InstKT)
```
- 删除指定标的物

```python
def update(self, *args, **kwargs) -> None
```
- 更新标的物数据
- 支持dict.update()接口

```python
def __len__(self) -> int
```
- 返回标的物数量

### FileFeatureStorage 类

**继承关系**:
- 继承自 FileStorageMixin, FeatureStorage

**说明**:
- 特征文件的文件存储实现
- 使用二进制格式存储（.bin）
- 支持高效的范围访问

**主要属性**:

```python
@property
def file_name(self) -> str
```
- 返回文件名
- 格式：`{instrument.lower()}/{field.lower()}.{freq.lower()}.bin`

**主要方法**:

```python
def clear(self)
```
- 清空特征数据
- 写入空文件

```python
@property
def data(self) -> pd.Series
```
- 获取所有特征数据
- 等用[:]切片访问

```python
def write(self, data_array: Union[List, np.ndarray], index: int = None)
```
- 写入特征数据
- 行为：
  - index=None: 追加到末尾
  - index指定且 > 当前end_index: 从end_index+1到index-1填充NaN
  - else: append到末尾

```python
@property
def start_index(self) -> Union[int, None]
```
- 获取特征的起始索引
- 返回：第一个数据点的索引

```python
@property
def end_index(self) -> Union[int, None]
```
- 获取特征的结束索引
- 返回：最后一个数据点的索引

```python
def __getitem__(self, i: Union[int, slice]) -> Union[Tuple[int, float], pd.Series]
```
- 获取特征数据
- 行为：
  - 单个索引：返回 (索引, 值值)
  - 切片访问：返回Series
- 如果文件不存在：返回None或空Series

```python
def __len__(self) -> int
```
- 返回特征长度

## 与其他模块的关系

### 依赖模块
- **qlib.data.storage.storage**: 存储抽象接口
- **qlib.data.cache**: 缓存机制
- **pathlib**: 路径处理
- **pandas/numpy**: 数据结构
- **qlib.config**: 配置管理

### 梫导出模块
- **qlib.data/data**: 数据提供者使用存储

## 设计模式

### 文件组织结构

```
数据目录/
├── calendars/
│   ├── day.txt (基础日历)
│   ├── day_future.txt (包含未来交易日)
│   ├── 1min.txt (1分钟频率）
│   └── instruments/
│   └── sh600000.txt (标的物)
└── features/
    └── sh600000/
│       └── close.day.bin
│       └── open.day.bin
│       └── ...
```

### 存储优化

```
二进制特征存储：
- 使用np.fromfile/tofile直接读取大块数据
- 使用.seek()定位到精确字节位置
- 使用float32类型节省空间
- 颶索引：f.seek(index * 4, 0)

文本日历存储：
- 使用np.loadtxt()读取
- 捏缓加载机制
```

### 写入优化

```
追加模式：
f.seek(0, 2)  # 定位到文件末尾
f.write(data_array.tobytes())  # 批量写入

替换模式：
# 定位到替换位置
f.seek(index * 4, 0)
f.write(data_array.tobytes())  # �量写入
```

### 缓存管理

```
文件大小检查：
if not self.uri.exists():
    self._write_calendar(values=[])

索引计算：
size_bytes = os.path.getsize(cp_cache_uri)
ele_size = np.dtype('<f').itemsize
assert size_bytes % ele_size == 0
ele_n = size_bytes // ele_size - 1
```

## 使用示例

### 日历存储使用

```python
from qlib.data.storage.file_storage import FileCalendarStorage

# 创建日历存储实例
storage = FileCalendarStorage(freq='day', future=False)

# 写入日历
calendar_data = ['2020-01-01', '2020-01-02', ...]
storage.write(calendar_data)

# 读取日历
data = storage.data  # 返回：[Timestamp('2020-01-01'), Timestamp('2020-01-02'), ...]

# 获取索引
index = storage.index(pd.Timestamp('2020-01-01'))  # 返回：0

# 长展日历
storage.extend(['2020-12-31'])
```

### 标的物存储使用

```python
from qlib.data.storage.file_storage import FileInstrumentStorage

# 创建标的物存储实例
storage = FileInstrumentStorage(market='csi300', freq='day')

# 写入标的物数据
inst_data = {
    'SH600000': [(Timestamp('2020-01-01'), Timestamp('2020-12-31')],
    'SH600004': [(Timestamp('2020-01-01'), Timestamp('2020-12-31')],
    ...
}
storage.update(inst_data)

# 读取标的物数据
data = storage.data  # 返回：{inst: [(start, end), ...]}
```

### 特征存储使用

```python
from qlib.data.storage.file_storage import FileFeatureStorage
import numpy as np
import pandas as pd

# 创建特征存储实例
storage = FileFeatureStorage(instrument='SH600000', field='close', freq='day')

# 写入特征数据
data = np.random.rand(100).astype(np.float32)
storage.write(data, index=0)

# 读取特征数据
data = storage.data  # 返回：pd.Series with RangeIndex(0, 100)

# 茌取特定范围
data = storage[10:20]  # 返回：pd.Series with RangeIndex(10, 20)
```

## 扩展点

### 自定义文件存储

```python
from qlib.data.storage.storage import FileCalendarStorage
from pathlib import Path

class MyFileStorage(FileCalendarStorage):
    def __init__(self, freq, future, **kwargs):
        super().__init__(freq, future, **kwargs)
        # 自定义存储路径
        self.custom_path = Path("/custom/calendars")

    @property
    def uri(self) -> Path:
        return self.custom_path / f"{freq}_future.txt"

    def load_calendar(self, freq, future):
        # 从自定义路径加载
        return super().load_calendar(freq, future)
```

### 支持自定义格式

```python
class CSVInstrumentStorage(FileInstrumentStorage):
    def __init__(self, market, freq, **kwargs):
        super().__init__(market, freq, **kwargs)
        # 使用CSV格式
        self.file_name = f"{market}.csv"
        self.field_delim = ','

    def _read_instrument(self):
        import pandas as pd
        df = pd.read_csv(self.uri, header=['instrument', 'start_time', 'end_time'])
        instruments = {}
        for _, row in df.iterrows():
            instruments[row['instrument']] = []
            if pd.notna(row['start_time']) or pd.notna(row['end_time']):
                continue
            instruments[row['instrument']].append((row['start_time'], row['end_time']))
        return instruments

    def _write_instrument(self, data):
        import pandas as pd
        df_list = []
        for inst, time_ranges in data.items():
            for start, end in time_ranges:
                df_list.append({
                    'instrument': inst,
                    'start_datetime': start,
                    'end_datetime': end
                })
        df = pd.concat(df_list, ignore_index=True)
        df.to_csv(self.uri, index=False, header=True, sep=self.field_delim)
```

### 支持自定义序列化

```python
class ParquetFeatureStorage(FileFeatureStorage):
    def __init__(self, instrument, field, freq, **kwargs):
        super().__init__(instrument, field, freq, **kwargs)
        # 使用Parquet格式
        self.file_name = f"{instrument.lower()}/{field.lower()}.{freq}.parquet"

    def write(self, data_array, index=None):
        # 写入Parquet文件
        df = pd.DataFrame(data_array, index=range(index, index+len(data_array)))
        df.to_parquet(self.uri, compression='snappy')

    def __getitem__(self, i):
        # 读取Parquet文件
        df = pd.read_parquet(self.uri)
        return df.iloc[i]
```

### 高级存储抽象

```python
from abc import ABC

class HDF5FeatureStorage(FeatureStorage, ABC):
    def __init__(self, instrument, field, freq, **kwargs):
        super().__init__(instrument, field, freq, **kwargs)
        self.file_name = f"{instrument.lower()}/{field.lower()}.{freq}.h5"

    def write(self, data_array, index=None):
        # 写入HDF5文件
        df = pd.DataFrame(data_array, index=range(index, index+len(data_array)))
        with pd.HDFStore(self.file_name, 'w') as store:
            store.put('df', 'data')
            store.close()

    def __getitem__(self, i):
        # 读取HDF5文件
        with pd.HDFStore(self.file_name, 'r') as store:
            df = store.select('data', start=i, stop=i+1)
        return df
```
```

## 注意事项

1. **文件格式规范**：
   - 日历文件：每行一个时间戳
   - 标的物文件：三列（代码、开始时间、结束时间），制表符分隔
   - 特征文件：二进制格式（索引+值）
2. **性能优化**：
   - 使用向量化操作
   - 二进制文件使用内存映射
   - 文件缓冲读取
3. **路径管理**：
   - 使用pathlib.Path进行跨平台操作
   - 支持自动创建目录
4. **错误处理**：
   - 文件不存在时自动创建
   - 提供清晰的错误信息
5. **线程安全**：
   - 文件读写操作不是线程安全的
6. **缓存兼容**：
   - 与Qlib的缓存系统配合使用
7. **频率转换**：
   - 支持日历频率重采样
8. **数据完整性**：
   - 写入时进行边界检查
9. **资源管理**：
   - 及时关闭文件句柄

## 相关文件

- **qlib.data/storage/storage.py**: 存储抽象接口
- **qlib.data/cache.py**: 缓存机制
- **qlib/config**: 配置管理
- **pandas/numpy**: 数据处理
- **pathlib**: 淯径处理
- **qlib.log**: 日志记录
