# data/__init__.py

## 模块概述

`qlib.contrib.report.data.__init__.py` 是数据分析模块的初始化文件。该模块设计用于分析和可视化数据特征。

## 模块说明

该模块提供了一套综合的分析类，用于：

## 使用示例

```python
from qlib.contrib.report.data.ana import FeaMeanStd
import pandas as pd

# 准备数据
fa = FeaMeanStd(ret_df)
fa.plot_all(wspace=0.3, sub_figsize=(12, 3), col_n=5)
```

## 可用的分析器

从 `qlib.contrib.report.data.ana` 模块导入以下分析器：

- `FeaMeanStd`: 均值和标准差分析
- `FeaSkewTurt`: 偏度和峰度分析
- `FeaDistAna`: 特征分布分析
- `FeaNanAna`: 缺失值分析
- `FeaNanAnaRatio`: 缺失值比例分析
- `FeaInfInfAna`: 无穷大值分析
- `FeaACAna`: 自相关分析
- `ValueCNT`: 值计数分析
- `RawFeaAna`: 原始值分析
- `CombFeaAna`: 组合分析器

## 快速开始

### 基础分析

```python
from qlib.contrib.report.data.ana import FeaMeanStd, FeaDistAna

# 分析均值和标准差
fa_mean_std = FeaMeanStd(data)
fa_mean_std.plot_all(wspace=0.3, sub_figsize=(12, 3), col_n=5)

# 分析分布
fa_dist = FeaDistAna(data)
fa_dist.plot_all(wspace=0.3, sub_figsize=(12, 3), col_n=5)
```

### 组合分析

```python
from qlib.contrib.report.data.ana import CombFeaAna, FeaMeanStd, FeaSkewTurt

# 组合多个分析器
fa = CombFeaAna(
    dataset=data,
    FeaMeanStd,
    FeaSkewTurt
)
fa.plot_all(wspace=0.3, sub_figsize=(12, 3), col_n=5)
```

## 数据要求

所有分析器要求输入的数据满足以下格式：

1. **索引**: 必须包含 `datetime` 级别
2. **列**: 可以有多列，每列对应一个特征
3. **聚合**: 按时间维度（`datetime`）聚合计算统计数据

**示例数据格式**:

```python
                return
datetime   instrument
2007-02-06  equity_tA     0.010087
            equity_spx     0.000786
```

## 注意事项

1. **数据准备**: 确保数据索引包含 `datetime` 级别
2. **数值类型**: 数值分析器会自动跳过非数值类型的特征
3. **缺失值**: 某些分析器会自动处理缺失值
4. **性能**: 对于大数据集，建议使用抽样分析

## 相关模块

- `qlib.contrib.report.data.base`: 基础分析器类
- `qlib.contrib.report.data.ana`: 具体分析器实现
