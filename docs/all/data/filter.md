# data/filter.py 模块文档

## 文件概述

此文件实现了动态标的物过滤器，用于根据特定规则筛选标的物。支持按名称、表达式规则等多种方式过滤，并可组合多个过滤器形成过滤管道。

## 类与函数

### BaseDFilter 类（抽象）

**继承关系**:
- 继承自 abc.ABC

**说明**:
- 动态标的物过滤器抽象基类
- 用户可继承此类实现自定义过滤器

**主要方法**:

```python
@staticmethod
def from_config(config) -> BaseDFilter
```
- 从配置字典创建过滤器实例
- 子类必须实现

```python
@abstractmethod
def to_config(self) -> dict
```
- 将过滤器转换为配置字典
- 子类必须实现

### SeriesDFilter 类

**继承关系**:
- 继承自 BaseDFilter

**说明**:
- 基于特征系列的动态标的物过滤器抽象类
- 支持在指定时间范围内应用过滤规则

**主要属性**:
- `filter_start_time`: 过滤器起始时间
- `filter_end_time`: 过滤器结束时间
- `keep`: 是否保留不符合规则的标的物

**主要方法**:

```python
def __init__(self, fstart_time=None, fend_time=None, keep=False)
```
- 初始化系列过滤器
- 参数：
  - fstart_time: 过滤器开始时间
  - fend_time: 过滤器结束时间
  - keep: 是否保留不存在的特征

```python
def _getTimeBound(self, instruments) -> tuple
```
- 获取所有标的物的时间边界
- 返回：(lbound, ubound)

```python
def _toSeries(self, time_range, target_timestamp) -> pd.Series
```
- 将目标时间戳转换为布尔序列
- 时间范围内为True，其他为False

```python
def _filterSeries(self, timestamp_series, filter_series) -> pd.Series
```
- 使用按位与操作过滤时间戳序列
- 返回：过滤后的布尔序列

```python
def _toTimestamp(self, timestamp) -> list
```
- 将布尔序列转换为时间范围元组列表
- 返回：[(start, end), ...]元组列表

```python
def __call__(self, instruments, start_time=None, end_time=None, freq="day")
```
- 调用过滤器获取过滤后的标的物
- 返回：过滤后的标的物字典

```python
@abstractmethod
def _getFilterSeries(self, instruments, fstart, fend) -> pd.DataFrame
```
- 抽象方法：获取过滤序列
- 子类必须实现

```python
def filter_main(self, instruments, start_time=None, end_timeTime=None)
```
- 实现过滤主逻辑
- 处理时间边界和过滤规则应用

### NameDFilter 类

**继承关系**:
- 继承自 SeriesDFilter

**说明**:
- 基于标的物名称的过滤器
- 使用正则表达式匹配标的物名称

**主要属性**:
- `name_rule_re`: 名称匹配正则表达式

**主要方法**:

```python
def __init__(self, name_rule_re, fstart_time=None, fend_time=None)
```
- 初始化名称过滤器
- 参数：name_rule_re: 正则表达式

```python
def _getFilterSeries(self, instruments, fstart, fend) -> dict
```
- 根据名称规则生成过滤序列
- 匹配的标的物返回True序列

```python
@staticmethod
def from_config(config) -> NameDFilter
```
- 从配置创建名称过滤器

```python
def to_config(self) -> dict
```
- 转换为配置字典

### ExpressionDFilter 类

**继承关系**:
- 继承自 SeriesDFilter

**说明**:
- 基于表达式的过滤器
- 根据表达式计算结果筛选标的物

**主要属性**:
- `rule_expression`: 过滤规则表达式

**主要方法**:

```python
def __init__(self, rule_expression, fstart_time=None, fend_time=None, keep=False)
```
- 初始化表达式过滤器
- 参数：
  - rule_expression: 表达式字符串
- keep: 是否保留不存在的特征

```python
def _getFilterSeries(self, instruments, fstart, fend) -> dict
```
- 根据表达式计算生成过滤序列
- 使用DatasetD.dataset计算表达式

```python
@staticmethod
def from_config(config) -> ExpressionDFilter
```
- 从配置创建表达式过滤器

```python
def to_config(self) -> dict
```
- 转换为配置字典

## 流程图

### 过滤流程

```
原始标的物字典
    ↓
确定时间边界
    ↓
获取过滤序列(_getFilterSeries)
    ↓
应用过滤规则(_filterSeries)
    ↓
转换为时间戳格式(_toTimestamp)
    ↓
返回过滤后的标的物
```

### 过滤器管道

```
原始标的物
    ↓
Filter 1
    ↓
Filter 2
    ↓
...
    ↓
Filter N
    ↓
最终标的物
```

## 与其他模块的关系

### 依赖模块
- **qlib.data.data**: 访问DatasetD
- **pandas/numpy**: 数据处理
- **re**: 正则匹配
- **typing**: 类型注解

## 设计模式

### 过滤器模式

采用管道模式组合多个过滤器：

```python
instruments = [
    {"filter_type": "NameDFilter", "name_rule_re": "SH[0-9]{4}"},
    {"filter_type": "ExpressionDFilter", "rule_expression": "$close/$open > 5"},
    ...
]
```

### 时间对齐

```
原始时间范围
    ↓
过滤器时间范围
    ↓
取交集
    ↓
应用过滤
```

## 使用示例

### 名称过滤

```python
from qlib.data import D
from qlib.data.filter import NameDFilter

# 创建名称过滤器
filter_name = NameDFilter(
    name_rule_re="SH[0-9]{4}",  # 匹配SH开头的股票
    fstart_time="2020-01-01",
    fend_time="2020-12-31"
)

# 使用过滤器
instruments = D.instruments(
    market="all",
    filter_pipe=filter_name
)
```

### 表达式过滤

```python
from qlib.data.filter import ExpressionDFilter

# 创建表达式过滤器
filter_expr = ExpressionDFilter(
    rule_expression="$close/$open > 2",  # 收盘比大于2
    fstart_time="2020-01-01",
    fend_time="2020-12-31",
    keep=False
)

# 使用过滤器
instruments = D.instruments(
    market="csi300",
    filter_pipe=filter_expr
)
```

### 过滤器管道

```python
# 组合多个过滤器
filter_pipe = [
    ExpressionDFilter(
        rule_expression="$close > 10",
        fstart_time="2020-01-01"
    ),
    NameDFilter(
        name_rule_re="SH[0-9]{4}",
        fend_time="2020-12-31"
    ),
    ExpressionDFilter(
        rule_expression="$volume > 1000000",
        keep=True
    )
]

# 应用过滤器管道
instruments = D.instruments(
    market="all",
    filter_pipe=filter_pipe
)
```

### 配置方式

```python
# 使用字典配置
instruments = D.instruments({
    "market": "csi300",
    "filter_pipe": [
        {
            "filter_type": "ExpressionDFilter",
            "rule_expression": "$close > 20",
            "filter_start_time": "2020-01-01",
            "filter_end_time": "2020-06-30"
        },
        {
            "filter_type": "NameDFilter",
            "name_rule_re": "SH[0-9]{4}"
        }
    ]
})
```

## 扩展点

### 自定义过滤器

```python
from qlib.data.filter import SeriesDFilter

class CustomFilter(SeriesDFilter):
    def __init__(self, param1, param2, fstart_time=None, fend_time=None):
        super().__init__(fstart_time, fend_time)
        self.param1 = param1
        self.param2 = param2

    def _getFilterSeries(self, instruments, fstart, fend):
        # 自定义过滤逻辑
        all_filter_series = {}
        for inst in instruments.keys():
            # 计算过滤规则
            filter_calendar = Cal.calendar(fstart, fend, freq=self.filter_freq)
            filter_series = pd.Series([...], index=filter_calendar)
            all_filter_series[inst] = filter_series
        return all_filter_series

    @staticmethod
    def from_config(config):
        return CustomFilter(
            param1=config["param1"],
            param2=config["param2"],
            fstart_time=config.get("filter_start_time"),
            fend_time=config.get("filter_end_time")
        )

    def to_config(self):
        return {
            "filter_type": "CustomFilter",
            "param1": self.param1,
            "param2": self.param2,
            "filter_start_time": str(self.filter_start_time) if self.filter_start_time else None,
            "filter_end_time": str(self.filter_end_time) if self.filter_end_time else None,
        }
```

### 复杂过滤器

```python
# 结合多个条件
filter_expr = ExpressionDFilter(
    rule_expression="($close > 20) & ($volume > 1000000)",
    fstart_time="2020-01-01",
    fend_time="2020-12-31"
)

# 使用Ref操作
filter_expr = ExpressionDFilter(
    rule_expression="Ref($close, 1) / Ref($close, 5) > 1.05",  # 5日涨幅超过5%
    fstart_time="2020-01-01",
    fend_time="2020-12-31"
)
```

## 注意事项

1. **时间对齐**: 过滤器时间范围和实际数据时间范围取交集
2. **keep参数**: keep=True时保留不存在的特征
3. **性能考虑**: 表达式过滤器使用disk_cache=0避免缓存
4. **正则表达式**: 名称过滤使用re模块
5. **可组合性**: 多个过滤器可以组合形成管道
6. **配置兼容**: 支持from_config/to_config序列化
7. **过滤顺序**: 过滤器管道按顺序应用
8. **动态过滤**: 支持不同时间范围的不同过滤规则

## 相关文件

- **qlib/data/data**: 提供InstrumentProvider接口
- **qlib.data.dataset**: DatasetD.dataset()用于表达式计算
- **qlib/contrib/data**: 社区贡献的过滤器实现
