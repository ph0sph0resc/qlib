# data/dataset/handler.py 模块文档

## 文件概述

此文件实现了数据处理器（Data Handler）的核心类，负责数据加载、处理和查询。DataHandler采用分层设计，支持数据加载器（Loader）、处理器（Processor）和存储层（Storage）的灵活组合。

## 类与函数

### DataHandlerABC 类

**继承关系**:
- 继承自 Serializable

**说明**:
- 数据处理器抽象接口
- 不假设内部数据结构
- 只定义外部用户的接口（以DataFrame为内部数据结构）

**主要方法**:

```python
@abstractmethod
def fetch(self, selector, level, col_set, data_key, squeeze, proc_func)
```
- 抽象方法：获取数据
- 参数：
  - selector: 选择器（时间戳、slice、索引等）
  - level: 索引级别（datetime/instrument）
  - col_set: 列集合
  - data_key: 数据键（raw/infer/learn）
  - - squeeze: 是否压缩维度
  - proc_func: 处理函数
- 子类必须实现

### DataHandler 类

**继承关系**:
- 继承自 DataHandlerABC

**说明**:
- 数据处理器的标准实现
- 使用DataLoader加载数据
- 维护双层索引（datetime & instrument）

**主要属性**:
- `_data`: 底层DataFrame
- `data_loader`: 数据加载器实例
- `instruments`: 标的物列表
- `start_time`: 起始时间
- `end_time`: 结束时间
- `fetch_orig`: 是否返回原始数据而非副本

**主要方法**:

```python
def __init__(self, instruments=None, start_time=None, end_time=None,
             data_loader=None, init_data=True, fetch_orig=True)
```
- 初始化数据处理器
- 参数：
  - instruments: 标的物范围
  - start_time/end_time: 时间范围
  - data_loader: 数据加载器实例或配置
  - init_data: 是否初始化数据
  - fetch_orig: 是否返回原始数据

```python
def config(self, handler_kwargs=None, **kwargs)
```
- 配置数据处理器
- 参数：handler_kwargs传递给DataHandler

```python
def setup_data(self, enable_cache=False)
```
- 设置底层数据
- 参数：enable_cache是否启用缓存

```python
def fetch(self, selector, level, col_set, data_key, squeeze, proc_func)
```
- 获取数据
- 参数：
  - selector: 选择器（时间戳、slice、索引等）
  - level: 索引级别
  - col_set: 列集合
  - data_key: 数据键
  - squeeze: 是否压缩维度
  - proc_func: 处理函数

```python
def get_cols(self, col_set=CS_ALL)
```
- 获取列名
- 参数：col_set列集合

```python
def get_range_selector(self, cur_date, periods)
```
- 获取范围选择器（按周期数）
- 参数：
  - cur_date: 当前日期
  - periods: 周期数

```python
def get_range_iterator(self, periods, min_periods=None, **kwargs)
```
- 获取范围迭代器

### DataHandlerLP 类

**继承关系**:
- 继承自 DataHandler

**说明**:
- 可学习处理器（Learnable Processor）
- 支持学习/推理分离的数据处理流程
- 生成三段数据：DK_R（原始）、DK_I（推理）、DK_L（学习）

**主要属性**:
- `_infer`: 推理数据（推理用）
- `_learn`: 学习数据
- `infer_processors`: 推理处理器列表
- `learn_processors`: 学习处理器列表
- `shared_processors`: 共享处理器列表
- `process_type`: 处理类型（dependent/append）
- `drop_raw`: 是否删除原始数据

**主要方法**:

```python
def __init__(self, instruments=None, start_time=None, end_time=None,
             data_loader=None, infer_processors=[], learn_processors=[],
             shared_processors=[], process_type='append', drop_raw=False, **kwargs)
```
- 初始化学习处理器
- 参数：
  - infer_processors: 推理阶段处理器
  - learn_processors: 学习阶段处理器
  - shared_processors: 共享处理器
  - process_type: 处理类型
  - drop_raw: 是否删除原始数据

```python
def config(self, processor_kwargs=None, **kwargs)
```
- 配置处理器

```python
def setup_data(self, init_type='fit_seq', **kwargs)
```
- 设置数据
- 参数：init_type初始化类型

```python
def fit(self)
```
- 拟合处理器（不处理数据）
- 在学习阶段调用

```python
def fit_process_data(self)
```
- 拟合并处理数据（fit + process）
- 在学习阶段调用

```python
def process_data(self, with_fit=False)
```
- 处理数据（按类型应用处理器）
- 参数：with_fit是否先fit

```python
def fetch(self, selector, level, col_set, data_key, squeeze, proc_func)
```
- 获取数据
- 参数：同DataHandler.fetch

```python
def get_cols(self, col_set=CS_ALL, data_key=DK_I)
```
- 获取列名

```python
@classmethod
def cast(cls, handler)
```
- 转换为DataHandlerLP类型
- 用于持久化处理器状态

```python
@classmethod
def from_df(cls, df)
```
- 从DataFrame创建DataHandlerLP
- 用于快速创建处理器

## 流程图

### 数据加载流程

```
用户请求
    ↓
DataHandler.setup_data()
    ↓
DataLoader.load()
    ↓
lazy_sort_index() # 确保索引有序
    ↓
DataFrame (_data)
```

### 数据获取流程

```
用户请求
    ↓
DataHandler.fetch()
    ↓
确定数据键（DK_I/DK_L）
    ↓
获取对应DataFrame (_infer/_learn)
    ↓
应用处理器（如需要）
    ↓
返回数据
```

### 学习/推理分离流程

```
原始数据 (_data)
    ↓
共享处理器
    ↓
    ├─ 推理数据 (_infer)
    │   ↓
    │   学习阶段共享
    ↓
    └─ 学习处理器
        ↓
        学习数据 (_learn)
    ↓
        丢弃原始数据（如需要）
```

## 与其他模块的关系

### 依赖模块
- **qlib.data**: 数据提供者接口
- **qlib.log**: 日志记录
- **qlib.utils**: 工具函数（实例化、时间处理等）
- **pandas/numpy**: 数据处理

### 被导入模块
- **qlib.data.dataset.loader**: 数据加载器
- **qlib.data.dataset.storage**: 处理器存储
- **qlib.data.dataset.processor**: 数据处理器

## 设计模式

### 处理器模式

```
数据加载
    ↓
存储层（Storage）
    ↓
处理器链（Processor Chain）
    ↓
数据（DataFrame）
```

### 数据键模式

```
DK_R: 原始数据（未处理）
DK_I: 推理数据（推理用）
DK_L: 学习数据（学习用）
```

### 处理器应用顺序

```
共享处理器
    ↓
推理处理器
    ↓
学习处理器
```

## 使用示例

### 基础使用

```python
from qlib.data.dataset import DataHandler

# 创建数据处理器
handler = DataHandler(
    instruments=['SH600000', 'SH600004'],
    start_time='2020-01-01',
    end_time='2020-12-31',
    data_loader=my_loader
)

# 获取数据
data = handler.fetch(
    selector='2020-01-01':'2020-06-30',
    level='datetime'
)
```

### 学习/推理分离

```python
from qlib.data.dataset import DataHandlerLP

# 创建学习处理器
handler = DataHandlerLP(
    data_loader=my_loader,
    infer_processors=[
        {'class': 'Fillna', 'kwargs': {'fields_group': 'feature'}}
    ],
    learn_processors=[
        {'class': 'ZScoreNorm', 'kwargs': {
            'fit_start_time': '2020-01-01',
            'fit_end_time': '2015-12-31'
        }}
    ],
    drop_raw=True
)

# 拟合处理器
handler.fit_process_data()

# 获取数据
train_data = handler.fetch(...)
infer_data = handler.fetch(...)
```

### 自定义存储

```python
from qlib.data.dataset.storage import BaseHandlerStorage

class MyStorage(BaseHandlerStorage):
    def fetch(self, selector, level, col_set, fetch_orig=True):
        # 自定义存储逻辑
        return custom_data

# 使用存储
handler = DataHandler(
    data_loader=loader,
    storage=MyStorage(df)
)
```

### 持久化处理器

```python
import pickle

# 保存处理器状态
with open('handler.pkl', 'wb') as f:
    pickle.dump(handler, f)

# 加载处理器状态
with open('handler.pkl', 'rb') as f:
    handler = pickle.load(f)
```

## 扩展点

### 自定义数据加载器

```python
from qlib.data.dataset import DataHandler, DataLoader

class CustomLoader(DataLoader):
    def load(self, instruments, start_time, end_time):
        # 自定义加载逻辑
        return custom_dataframe

# 使用加载器
handler = DataHandler(
    data_loader=CustomLoader()
)
```

### 自定义处理器

```python
from qlib.data.dataset.processor import Processor

class CustomProcessor(Processor):
    def __call__(self, df):
        # 自定义处理逻辑
        df['custom_field'] = df['field1'] * 2
        return df

# 使用处理器
handler = DataHandlerLP(
    data_loader=loader,
    infer_processors=[
        {'class': 'CustomProcessor'}
    ]
)
```

## 注意事项

1. **索引顺序**: 使用lazy_sort_index确保索引有序
2. **数据副本**: fetch_orig控制是否返回副本
3. **处理器链式**: 处理器按链式应用
4. **数据一致性**: 学习/推理数据保持一致
5. **序列化**: 支持pickle序列化
6. **性能优化**: 使用向量化操作
7. **错误处理**: 妃善的异常捕获和日志
8. **类型安全**: 使用类型注解提高代码质量

## 相关文件

- **qlib.data.dataset.loader**: 数据加载器
- **qlib.data.dataset.storage**: 处理器存储
- **qlib.data.dataset.processor**: 数据处理器
- **qlib.contrib.data**: 社区贡献实现
