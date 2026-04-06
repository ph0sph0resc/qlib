# data/inst_processor.py 模块文档

## 文件概述

此文件定义了标的物处理器（Instrument Processor）抽象接口，用于在数据加载过程中对单个标的物的数据进行处理。处理器可以就地修改数据，需要注意数据副本问题。

## 类与函数

### InstProcessor 类（抽象）

**继承关系**:
- 继承自 abc.ABC

**说明**:
- 标的物处理器抽象基类
- 在Handler的inst_processors链中被调用
- 支持对单个标的物的DataFrame进行数据处理

**主要方法**:

```python
@abstractmethod
def __call__(self, df: pd.DataFrame, instrument, *args, **kwargs)
```
- 处理数据
- **重要**：此函数可能就地修改df的内容！
- 参数：
  - df: 原始DataFrame或前一个处理器的结果
  - instrument: 标的物代码
  - -args, **kwargs: 扩展参数
- 返回：处理后的DataFrame（可能就地修改）

```python
def __str__(self)
```
- 返回处理器的字符串表示
- 格式：ClassName:json_dict

## 流程图

### 处理器链流程

```
原始数据
    ↓
InstProcessor 1
    ↓
InstProcessor 2
    ↓
...
    ↓
InstProcessor N
    ↓
最终数据
```

### Handler集成

```python
# 在DatasetHandler中
inst_processors = [
    {"class": "TimeRangeFilter", "kwargs": {...}},
    {"class": "CustomProcessor", "kwargs": {...}}
]

# 在数据加载时应用
for proc in inst_processors:
    df = proc(df, instrument=inst)
```

## 与其他模块的关系

### 依赖模块
- **pandas**: DataFrame处理
- **abc**: 抽象基类
- **json**: 序列化支持
- **typing**: 类型注解

### 被导入模块
- 在DatasetHandler中导入和使用

## 设计模式

### 处理器模式

采用链式处理模式：

```
DataLoader加载数据
    ↓
DatasetHandler应用inst_processors
    ↓
每个标的物独立处理
    ↓
返回处理后的数据集
```

### 就地修改警告

```python
# 错误示例（可能丢失原始数据）
original_data = df.copy()  # 正确：先复制
processed_data = my_processor(original_data)  # 处理器可能就地修改

# 正确使用（处理器返回新DataFrame）
original_data = df
processed_data = my_processor(original_data)  # 如果处理器不修改原始数据
```

## 使用示例

### 基础处理器

```python
from qlib.data.inst_processor import InstProcessor
import pandas as pd

class SimpleProcessor(InstProcessor):
    def __call__(self, df: pd.DataFrame, instrument, *args, **kwargs):
        # 移除包含NaN的行
        df = df.dropna()
        return df
```

### 带参数处理器

```python
class ParameterProcessor(InstProcessor):
    def __init__(self, threshold=0.5):
        self.threshold = threshold

    def __call__(self, df: pd.DataFrame, instrument, *args, **kwargs):
        # 只保留特定范围的值
        df = df[(df['close'] > self.threshold)]
        return df
```

### 组合使用

```python
from qlib.data.dataset import DatasetH

# 创建处理器链
inst_processors = [
    {"class": "FilterNan", "kwargs": {"fields_group": "feature"}},
    {"class": "MinmaxNorm", "kwargs": {
        "fit_start_time": "2010-01-01",
        "fit_end_time": "2015-12-31"
    }}
]

# 配置DataHandler
handler = DatasetH(
    data_loader=loader,
    inst_processors=inst_processors
)
```

## 扩展点

### 时间范围过滤处理器

```python
from qlib.data.inst_processor import InstProcessor
from qlib.data import D
import pandas as pd

class TimeRangeFilter(InstProcessor):
    def __init__(self, start_time=None, end_time=None, freq="day"):
        self.start_time = pd.Timestamp(start_time) if start_time else None
        self.end_time = pd.Timestamp(end_time) if end_time else None
        self.freq = freq

    def __call__(self, df: pd.DataFrame, instrument, *args, **kwargs):
        if df.empty:
            return df

        # 获取日历
        calendar = D.calendar(
            start_time=self.start_time,
            end_time=self.end_time,
            freq=self.freq
        )

        # 对齐到日历
        df = df.reindex(calendar)

        return df
```

### 基于指标的过滤处理器

```python
class IndicatorFilter(InstProcessor):
    def __init__(self, indicators):
        self.indicators = set(indicators)

    def __call__(self, df: pd.DataFrame, instrument, *args, **kwargs):
        # 只保留在指定指标列表中的股票
        if instrument in self.indicators:
            return df
        else:
            return pd.DataFrame()  # 返回空DataFrame
```

### 数据验证处理器

```python
class DataValidator(InstProcessor):
    def __call__(self, df: pd.DataFrame, instrument, *args, **kwargs):
        # 验证数据质量
        if df.empty:
            return df

        # 检查异常值
        if df.isnull().all().all():
            return df  # 全部为NaN，保留

        # 移除无限值
        import numpy as np
        df = df.replace([np.inf, -np.inf], np.nan)

        return df
```

### 统计处理器

```python
class StatisticsCollector(InstProcessor):
    def __init__(self):
        self.stats = {}

    def __call__(self, df: pd.DataFrame, instrument, *args, **kwargs):
        # 收集统计信息
        self.stats[instrument] = {
            'rows': len(df),
            'columns': len(df.columns),
            'has_data': len(df) > 0,
            'missing_ratio': df.isnull().mean().mean()
        }
        return df

    def get_statistics(self):
        return self.stats
```

## 注意事项

1. **就地修改风险**: 处理器可能就地修改DataFrame，使用前需要了解行为
2. **数据副本**: 如需保留原始数据，应在调用处理器前复制
3. **异常处理**: 处理器应妥善处理异常情况
4. **性能考虑**: 处理器应避免不必要的拷贝操作
5. **类型安全**: 确保处理后的DataFrame类型正确
6. **日志记录**: 可添加日志记录处理过程
7. **可序列化**: 使用__str__方法支持序列化
8. **参数传递**: 支持*args和**kwargs灵活传参

## 相关文件

- **qlib/data/dataset/handler.py**: 使用处理器的Handler类
- **qlib/data/dataset/processor.py**: 提供预定义处理器
- **qlib/contrib/data/**handler.py**: 社区贡献的处理器实现
