# data/dataset/__init__.py 模块文档

## 文件概述

此文件是数据集（dataset）模块的入口文件，导出DataHandler、Dataset等核心类，用于数据加载、处理和管理。

## 导出的核心类

### 数据处理类

- **DataHandler**: 数据处理器的抽象基类
- **DataHandlerLP**: 带习处理器（支持学习/推理分离处理）
- **Dataset**: 数据集抽象基类
- **DatasetH**: 基于DataHandler的数据集
- **TSDataSampler**: 时间序列数据采样器
- **TSDatasetH**: 时间序列数据集

### 数据存储类

- **BaseHandlerStorage**: 处理器存储抽象基类
- **NaiveDFStorage**: 简单DataFrame存储
- **HashingStockStorage**: 哈希化股票存储（优化随机访问）

### 数据加载器类

- **DataLoader**: 数据加载器抽象基类
- **DLWParser**: 数据加载器与解析器基类
- **QlibDataLoader**: Qlib数据加载器
- **StaticDataLoader**: 静态数据加载器
- **NestedDataLoader**: 嵌套数据加载器
- **DataLoaderDH**: 基于DataHandler的数据加载器

### 数据处理器类

- **Processor**: 数据处理器抽象基类
- **DropnaProcessor**: 删除NaN处理器
- **DropnaLabel**: 删除标签NaN处理器
- **DropCol**: 删除列处理器
- **FilterCol**: 过滤列处理器
- **TanhProcess**: Tanh去噪处理器
- **ProcessInf**: 处理无穷大处理器
- **Fillna**: 填充NaN处理器
- **MinMaxNorm**: 最小-最大归一化处理器
- **ZScoreNorm**: Z-Score归一化处理器
- **RobustZScoreNorm**: 鲁健Z-Score归一化处理器
- **CSZScoreNorm**: 截面Z-Score归一化处理器
- **CSRankNorm**: 截面Rank归一化处理器
- **CSZFillna**: 截面填充NaN处理器
- **HashStockFormat**: 哈希化股票格式转换处理器
- **TimeRangeFilter**: 时间范围过滤器

### 数据权重类

- **Reweighter**: 数据权重抽象基类

## 模块依赖关系

```
qlib.data.dataset
├── __init__.py (本文档)
├── handler.py (DataHandler、DatasetH、TSDataSampler等)
├── loader.py (各类DataLoader)
├── processor.py (各类Processor)
├── storage.py (HandlerStorage实现)
├── utils.py (工具函数)
└── weight.py (Reweighter)
```

## 使用示例

### 基础数据使用

```python
from qlib.data.dataset import DatasetH

# 创建数据集
dataset = DatasetH(
    handler=handler_config,
    segments={
        'train': ('2010-01-01', '2014-12-31'),
        'valid': ('2015-01-01', '2016-12-31'),
        'test': ('2016-01-01', '2016-12-31'),
    }
)

# 获取训练数据
train_data = dataset.prepare('train')
```

### 时间序列采样

```python
from qlib.data.dataset import TSDatasetH

# 创建时间序列数据集
ts_dataset = TSDatasetH(
    handler=handler_config,
    segments={'train': ('2020-01-01', '2020-12-31')},
    step_len=30
)

# 获取采样器
sampler = ts_dataset.prepare('train')

# 访问数据
for i in range(len(sampler)):
    sample = sampler[i]
    # sample形状：(batch_size, step_len, num_features)
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
handler = DatasetH(
    processor=[{'class': 'CustomProcessor'}]
)
```

## 相关模块

- **qlib.data**: 数据提供者接口
- **qlib.contrib.data**: 社区贡献的数据处理器和加载器
