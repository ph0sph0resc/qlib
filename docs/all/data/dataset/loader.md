# data/dataset/loader.py 模块文档

## 文件概述

此文件实现了各种数据加载器（Data Loader），负责从不同数据源加载原始数据。支持Qlib内置加载器、静态数据加载器、嵌套加载器等多种模式。

## 类与函数

### DataLoader 类（抽象）

**继承关系**:
- 继承自 abc.ABC

**说明**:
- 数据加载器抽象基类
- 负责从原始数据源加载数据为DataFrame格式

**主要方法**:

```python
@abstractmethod
def load(self, instruments, start_time=None, end_time=None) -> pd.DataFrame
```
- 抽象方法：加载数据
- 参数：
  - instruments: 标的物范围（市场名或配置）
  - start_time: 起始时间
  - end_time: 结束时间
- 返回：MultiIndex DataFrame (instrument, datetime)

### DLWParser 类

**继承关系**:
- 继承自 DataLoader

**说明**:
- 数据加载器与解析器基类
- 支持字段定义和列名解析
- 可以定义单个或多个字段组

**主要属性**:
- `is_group`: 是否为分组模式
- `fields`: 字段定义字典或元组

**主要方法**:

```python
def __init__(self, config)
```
- 初始化解析器
- 参数：config字段配置
- 支持格式：{group_name: fields_info}或直接fields_info

```python
def _parse_fields_info(self, fields_info) -> tuple
```
- 解析字段信息
- 返回：(表达式列表, 列名列表)

```python
@abstractmethod
def load_group_df(self, instruments, exprs, names, start_time, end_time, gp_name=None)
```
- 抽象方法：加载特定组的数据

```python
def load(self, instruments=None, start_time=None, end_time=None)
```
- 加载数据
- 调用load_group_df处理每个组

### QlibDataLoader 类

**继承关系**:
- 继承自 DLWParser

**说明**:
- Qlib内置数据加载器
- 使用Qlib的D接口加载数据
- 支持过滤器和处理器

**主要属性**:
- `filter_pipe`: 过滤器管道
- `swap_level`: 是否交换MultiIndex层级
- `freq`: 数据频率
- `inst_processors`: 标的物处理器列表

**主要方法**:

```python
def __init__(self, config, filter_pipe=None, swap_level=True,
             freq="day", inst_processors=None)
```
- 初始化Qlib数据加载器
- 参数：
  - config: 字段配置
  - filter_pipe: 过滤器管道
  - swap_level: 是否交换索引顺序
  - freq: 数据频率
  - inst_processors: 标的物处理器

```python
def load_group_df(self, instruments, exprs, names, start_time, end_time, gp_name=None)
```
- 加载特定组数据
- 使用D.features()加载数据

### StaticDataLoader 类

**继承关系**:
- 继承自 DataLoader, Serializable

**说明**:
- 静态数据加载器
- 支持从文件或DataFrame加载静态数据
- 支持多种文件格式（pickle、parquet等）

**主要属性**:
- `include_attr`: 序列化属性列表
- `_config`: 配置或路径
- `join`: 合并方式
- `_data`: 缓存的数据

**主要方法**:

```python
def __init__(self, config, join="outer")
```
- 初始化静态加载器
- 参数：
  - config: 配置字典或文件路径或DataFrame
  - join: 合并方式（outer/inner/left）

```python
def load(self, instruments=None, start_time=None, end_time=None)
```
- 加载数据
- 支持按标的物、时间范围过滤

### NestedDataLoader 类

**继承关系**:
- 继承自 DataLoader

**说明**:
- 嵌套数据加载器
- 组合多个DataLoader
- 按持合并不同来源的数据

**主要属性**:
- `data_loader_l`: 数据加载器列表
- `join`: 合并方式

**主要方法**:

```python
def __init__(self, dataloader_l, join="left")
```
- 初始化嵌套加载器
- 参数：
  - dataloader_l: 数据加载器配置列表
  - join: 合并方式

```python
def load(self, instruments=None, start_time=None, end_time=None)
```
- 加载数据
- 顺序应用每个加载器并合并数据

### DataLoaderDH 类

**继承关系**:
- 继承自 DataLoader

**说明**:
- 基于DataHandler的数据加载器
- 支持从DataHandler加载数据
- 适用于在线场景

**主要属性**:
- `handlers`: 数据处理器或处理器字典
- `is_group`: 是否为分组模式
- `fetch_kwargs`: 获取数据的额外参数

**主要方法**:

```python
def __init__(self, handler_config, fetch_kwargs={}, is_group=False)
```
- 初始化数据加载器
- 参数：
  - handler_config: 处理器配置
  - fetch_kwargs: 获取参数
  - is_group: 是否分组

```python
def load(self, instruments=None, start_time=None, end_time=None)
```
- 加载数据
- 使用DataHandler.fetch()获取数据

## 流程图

### 数据加载流程

```
用户请求
    ↓
DataLoader.load()
    ↓
根据类型选择加载器
    ↓
QlibDataLoader → D.features()
    ↓
StaticDataLoader → 文件读取
    ↓
NestedDataLoader → 多个加载器组合
    ↓
返回DataFrame
```

### 分组加载流程

```
配置多个字段组
    ↓
DLWParser解析配置
    ↓
对每个组调用load_group_df
    ↓
合并所有组数据
    ↓
返回完整DataFrame
```

## 与其他模块的关系

### 依赖模块
- **qlib.data**: 数据提供者接口
- **pandas/numpy**: 数据处理
- **pickle**: 序列化支持
- **pathlib**: 路径处理

### 被导入模块
- **qlib.contrib.data**: 社区贡献的加载器

## 设计模式

### 加载器模式

```
抽象层（DataLoader）
    ↓
Qlib内置
    ↓
静态/嵌套
    ↓
自定义
```

### 字段配置模式

```
单字段组
    ↓
DLWParser
    ↓
DataLoader

多字段组
    ↓
DLWParser
    ↓
{group1: fields1, group2: fields2, ...}
```

## 使用示例

### Qlib数据加载

```python
from qlib.data.dataset import QlibDataLoader

# 配置加载器
loader = QlibDataLoader(
    config={
        "group1": [
            "$close", "$open", "$high", "$low"
        ],
        "group2": [
            ["Ref($close, 1)", "MA5"],
            ["Ref($close, 1)", "MA10"]
        ]
    },
    filter_pipe=[filter_config],
    inst_processors=[processor_config]
)

# 加载数据
data = loader.load(
    instruments=['SH600000'],
    start_time='2020-01-01',
    end_time='2020-12-31'
)
```

### 静态数据加载

```python
from qlib.data.dataset import StaticDataLoader

# 从文件加载
loader = StaticDataLoader(
    config={
        "group1": "/path/to/data.parquet",
        "group2": "/path/to/other.csv"
    }
)

# 加载数据
data = loader.load()
```

### 嵌套加载

```python
from qlib.data.dataset import NestedDataLoader

# 组合多个加载器
loader = NestedDataLoader(
    dataloader_l=[
        {"class": "QlibDataLoader", ...},
        {"class": "StaticDataLoader", ...}
    ],
    join="left"
)

# 加载数据
data = loader.load()
```

### 自定义加载器

```python
from qlib.data.dataset import DataLoader

class CustomLoader(DataLoader):
    def load(self, instruments, start_time=None, end_time=None):
        # 自定义加载逻辑
        return load_custom_data(instruments, start_time, end_time)

# 使用
handler = DataHandler(data_loader=CustomLoader())
```

## 扩展点

### 自定义解析器

```python
from qlib.data.dataset import DLWParser

class CustomParser(DLWParser):
    def load_group_df(self, instruments, exprs, names, start_time, end_time, gp_name):
        # 自定义加载逻辑
        return load_custom_data(instruments, exprs)

# 使用
parser = CustomParser(config={...})
```

### 嵌套配置

```python
loader = NestedDataLoader([
    {
        "class": "QlibDataLoader",
        "kwargs": {
            "config": {...},
            "filter_pipe": [...]
        }
    },
    {
        "class": "CustomLoader",
        "module_path": "my_module"
    }
])
```

## 注意事项

1. **格式支持**: 支持多种数据格式（pickle、parquet、csv）
2. **安全加载**: 使用restricted_pickle_load保证安全
3. **数据合并**: 支持多种合并方式（outer/inner/left）
4. **过滤支持**: QlibDataLoader支持过滤器管道
5. **处理器支持**: 支持标的物处理器链
6. **分组模式**: 支持按组定义和加载数据
7. **缓存友好**: 支持序列化和反序列化
8. **错误处理**: 提供清晰的错误信息

## 相关文件

- **qlib.data.dataset.handler**: 数据处理器
- **qlib.contrib.data**: 社区贡献的加载器
- **qlib.data**: 数据提供者接口
