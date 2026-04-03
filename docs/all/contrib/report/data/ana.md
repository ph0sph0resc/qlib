# data/ana.py

## 模块概述

`qlib.contrib.report.data.ana` 模块提供了丰富的特征分析器实现。这些分析器用于分析数据特征的统计特性、分布、缺失值、无穷大值等。该模块包含一个基础类和多个具体分析器。

## 模块结构

```mermaid
graph TD
    A[FeaAnalyser) --> B[NumFeaAnalyser]
    A --> C[ValueCNT]
    A --> D[FeaNanAna)
    A --> E[FeaNanAnaRatio]
    B --> F[FeaDistAna]
    B --> G[FeaInfAna]
    B --> H[FeaACAna]
    B --> I[FeaSkewTurt]
    B --> J[FeaMeanStd]
    A --> K[RawFeaAna)
    A --> L[CombFeaAna]
```

---

## 类详细说明

### 1. CombFeaAna - 组合分析器

**说明**: 将多个子分析器组合在一起，在单个图表中显示多个分析结果。

#### 构造方法

```python
def __init__(self, dataset: pd.DataFrame, *fea_ana_cls):
```

**参数说明**:

| 参数 | 类型 | 说明 |
|------|------|------|
| dataset | pd.DataFrame | 要分析的数据集 |
| *fea_ana_cls | FeaAnalyser 子类 | 要组合的分析器类 |

**要求**: 至少需要 2 个分析器类。

#### 方法说明

##### skip

```python
def skip(self, col):
    return np.all(list(map(lambda fa: fa.skip(col), self._fea_ana_l)))
```

**说明**: 如果所有子分析器都跳过该特征，则跳过该特征。

##### calc_stat_values

```python
def calc_stat_values(self):
    """The statistics of features are finished in the underlying analysers"""
```

**说明**: 底层分析器已经完成了特征的统计计算。

##### plot_all

```python
def plot_all(self, *args, **kwargs):
```

**说明**: 绘制所有特征的图表，每个特征显示多个分析结果。

**布局**: 使用 `row_n` 参数控制每个特征的子图行数。

#### 使用示例

```python
from qlib.contrib.report.data.ana import (
    CombFeaAna, FeaMeanStd, FeaSkewTurt
)

# 组合均值标准差和偏度峰度分析器
fa = CombFeaAna(
    dataset=df,
    FeaMeanStd,
    FeaSkewTurt
)

# 绘制所有特征
fa.plot_all(wspace=0.3, sub_figsize=(12, 6), col_n=3, row_n=2)
```

---

### 2. NumFeaAnalyser - 数值特征分析器

**说明**: 数值特征分析器的基类，继承自 `FeaAnalyser`。自动跳过非数值类型的特征。

#### 方法说明

##### skip

```python
def skip(self, col):
    is_obj = np.issubdtype(self._dataset[col], np.dtype("O"))
    if is_obj:
        logger.info(f"{col} is not numeric and is skipped")
    return is_obj
```

**说明**: 检查特征是否为数值类型。如果不是数值类型（object 类型），则跳过该特征。

#### 使用示例

```python
# 通常不直接使用，而是作为其他分析器的基类
```

---

### 3. ValueCNT - 值计数分析器

**说明**: 统计每个特征在不同时间点的唯一值数量。

#### 构造方法

```python
def __init__(self, dataset: pd.DataFrame, ratio: bool = False):
```

**参数说明**:

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| dataset | pd.DataFrame | 必需 | 要分析的数据集 |
| ratio | bool | False | 是否计算比例，True 时计算唯一值占总数量的比例 |

#### 计算逻辑

```python
def calc_stat_values(self):
    self._val_cnt = {}
    for col, item in self._dataset.items():
        if not super().skip(col):
            self._val_cnt[col] = item.groupby(DT_COL_NAME, group_keys=False).apply(lambda s: len(s.unique()))
    self._val_cnt = pd.DataFrame(self._val_cnt)
    if self.ratio:
        self._val_cnt = self._val_cnt.div(self._dataset.groupby(DT_COL_NAME, group_keys=False).size(), axis=0)

    ymin, ymax = self._val_cnt.min().min(), self._val_cnt.max().max()
    self.ylim = (ymin - 0.05 * (ymax - ymin), ymax + 0.05 * (ymax - ymin))
```

1. 按日期分组
2. 统计每天每个特征的唯一值数量
3. 如果 ratio=True，则除以当天的总数据量
4. 计算 Y 轴范围

#### 使用示例

```python
from qlib.contrib.report.data.ana import Value

# 统计唯一值数量
fa = ValueCNT(df, ratio=False)
fa.plot_all(wspace=0.3, sub_figsize=(12, 3), col_n=5)

# 统计唯一值比例
fa = ValueCNT(df, ratio=True)
fa.plot_all(wspace=0.3, sub_figsize=(12, 3), col_n=5)
```

---

### 4. FeaDistAna - 特征分布分析器

**说明**: 绘制特征的直方图，展示数据的分布情况。

#### 继承关系

```
FeaAnalyser -> NumFeaAnalyser -> FeaDistAna
```

#### 方法说明

##### plot_single

```python
def plot_single(self, col, ax):
    sns.histplot(self._dataset[col], ax=ax, kde=False, bins=100)
    ax.set_xlabel("")
    ax.set_title(col)
```

**说明**: 使用 seaborn 的 histplot 函数绘制直方图。

**参数**:
- `kde=False`: 不显示核密度估计
- `bins=100`: 使用 100 个 bins

#### 使用示例

```python
from qlib.contrib.report.data.ana import FeaDistAna

fa = FeaDistAna(df)
fa.plot_all(wspace=0.3, sub_figsize=(12, 3), col_n=5)
```

---

### 5. FeaInfAna - 无穷大值分析器

**说明**: 分析特征中的无穷大值（inf/-inf）数量。

#### 继承关系

```
FeaAnalyser -> NumFeaAnalyser -> FeaInfAna
```

#### 方法说明

##### calc_stat_values

```python
def calc_stat_values(self):
    self._inf_cnt = {}
    for col, item in self._dataset.items():
        if not super().skip(col):
            self._inf_cnt[col] = item.apply(np.isinf).astype(np.int).groupby(DT_COL_NAME, group_keys=False).sum()
    self._inf_cnt = pd.DataFrame(self._inf_cnt)
```

**计算逻辑**:
1. 检查每个值是否为无穷大（np.isinf）
2. 按日期分组统计无穷大值的数量

##### skip

```python
def skip(self, col):
    return (col not in self._inf_cnt) or (self._inf_cnt[col].sum() == 0)
```

**说明**: 只显示包含无穷大值的特征。

##### plot_single

```python
def plot_single(self, col, ax):
    self._inf_cnt[col].plot(ax=ax, title=col)
    ax.set_xlabel("")
```

#### 使用示例

```python
from qlib.contrib.report.data.ana import FeaInfAna

fa = FeaInfAna(df)
fa.plot_all(wspace=0.3, sub_figsize=(12, 3), col_n=5)
```

---

### 6. FeaNanAna - 缺失值分析器

**说明**: 分析特征中的缺失值（NaN）数量。

#### 继承关系

```
FeaAnalyser -> FeaNanAna
```

#### 方法说明

##### calc_stat_values

```python
def calc_stat_values(self):
    self._nan_cnt = self._dataset.isna().groupby(DT_COL_NAME, group_keys=False).sum()
```

**计算逻辑**: 按日期分组统计缺失值数量。

##### skip

```python
def skip(self, col):
    return (col not in self._nan_cnt) or (self._nan_cnt[col].sum() == 0)
```

**说明**: 只显示包含缺失值的特征。

##### plot_single

```python
def plot_single(self, col, ax):
    self._nan_cnt[col].plot(ax=ax, title=col)
    ax.set_xlabel("")
```

#### 使用示例

```python
from qlib.contrib.report.data.ana import FeaNanAna

fa = FeaNanAna(df)
fa.plot_all(wspace=0.3, sub_figsize=(12, 3), col_n=5)
```

---

### 7. FeaNanAnaRatio - 缺失值比例分析器

**说明**: 分析特征中的缺失值比例。

#### 继承关系

```
FeaAnalyser -> FeaNanAnaRatio
```

#### 方法说明

##### calc_stat_values

```python
def calc_stat_values(self):
    self._nan_cnt = self._dataset.isna().groupby(DT_COL_NAME, group_keys=False).sum()
    self._total_cnt = self._dataset.groupby(DT_COL_NAME, group_keys=False).size()
```

**计算逻辑**:
1. 计算缺失值数量
2. 计算总数据量

##### plot_single

```python
def plot_single(self, col, ax):
    (self._nan_cnt[col] / self._total_cnt).plot(ax=ax, title=col)
    ax.set_xlabel("")
```

**说明**: 绘制缺失值比例。

#### 使用示例

```python
from qlib.contrib.report.data.ana import FeaNanAnaRatio

fa = FeaNanAnaRatio(df)
fa.plot_all(wspace=0.3, sub_figsize=(12, 3), col_n=5)
```

---

### 8. FeaACAna - 自相关分析器

**说明**: 分析特征的自相关性。

#### 继承关系

```
**FeaAnalyser -> NumFeaAnalyser -> FeaACAna
```

#### 方法说明

##### calc_stat_values

```python
def calc_stat_values(self):
    self._fea_corr = pred_autocorr_all(self._dataset.to_dict("series"))
    df = pd.DataFrame(self._fea_corr)
    ymin, ymax = df.min().min(), df.max().max()
    self.ylim = (ymin - 0.05 * (ymax - ymin), ymax + 0.05 * (ymax - ymin))
```

**计算逻辑**:
1. 使用 `pred_autocorr_all` 函数计算自相关
2. 计算 Y 轴范围

##### plot_single

```python
def plot_single(self, col, ax):
    self._fea_corr[col].plot(ax=ax, title=col, ylim=self.ylim)
    ax.set_xlabel("")
```

#### 使用示例

```python
from qlib.contrib.report.data.ana import FeaACAna

fa = FeaACAna(df)
fa.plot_all(wspace=0.3, sub_figsize=(12, 3), col_n=5)
```

---

### 9. FeaSkewTurt - 偏度和峰度分析器

**说明**: 分析特征的偏度（skewness）和峰度（kurtosis）。

#### 继承关系

```
FeaAnalyser -> NumFeaAnalyser -> FeaSkewTurt
```

#### 方法说明

##### calc_stat_values

```python
def calc_stat_values(self):
    self._skew = datetime_groupby_apply(self._dataset, "skew")
    self._kurt = datetime_groupby_apply(self._dataset, pd.DataFrame.kurt)
```

**计算逻辑**:
1. 按日期分组计算偏度
2. 按日期分组计算峰度

##### plot_single

```python
def plot_single(self, col, ax):
    self._skew[col].plot(ax=ax, label="skew")
    ax.set_xlabel("")
    ax.set_ylabel("skew")
    ax.legend()

    right_ax = ax.twinx()

    self._kurt[col].plot(ax=right_ax, label="kurt", color="green")
    right_ax.set_xlabel("")
    right_ax.set_ylabel("kurt")
    right_ax.grid(None)  # set grid to None to avoid two layers of grid

    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = right_ax.get_legend_handles_labels()

    ax.legend().set_visible(False)
    right_ax.legend(h1 + h2, l1 + l2)
    ax.set_title(col)
```

**说明**: 使用双 Y 轴绘制偏度和峰度。

#### 使用示例

```python
from qlib.contrib.report.data.ana import FeaSkewTurt

fa = FeaSkewTurt(df)
fa.plot_all(wspace=0.3, sub_figsize=(12, 3), col_n=5)
```

---

### 10. FeaMeanStd - 均值和标准差分析器

**说明**: 分析特征的均值和标准差随时间的变化。

#### 继承关系

```
FeaAnalyser -> NumFeaAnalyser -> FeaMeanStd
```

#### 方法说明

##### calc_stat_values

```python
def calc_stat_values(self):
    self._std = self._dataset.groupby(DT_COL_NAME, group_keys=False).std()
    self._mean = self._dataset.groupby(DT_COL_NAME, group_keys=False).mean()
```

**计算逻辑**:
1. 按日期分组计算均值
2. 按日期分组计算标准差

##### plot_single

```python
def plot_single(self, col, ax):
    self._mean[col].plot(ax=ax, label="mean")
    ax.set_xlabel("")
    ax.set_ylabel("mean")
    ax.legend()
    ax.tick_params(axis="x", rotation=90)

    right_ax = ax.twinx()

    self._std[col].plot(ax=right_ax, label="std", color="green")
    right_ax.set_xlabel("")
    right_ax.set_ylabel("std")
    right_ax.tick_params(axis="x", rotation=90)
    right_ax.grid(None)  # set grid to None to avoid two layers of grid

    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = right_ax.get_legend_handles_labels()

    ax.legend().set_visible(False)
    right_ax.legend(h1 + h2, l1 + l2)
    ax.set_title(col)
```

**说明**: 使用双 Y 轴绘制均值和标准差。

#### 使用示例

```python
from qlib.contrib.report.data.ana import FeaMeanStd

fa = FeaMeanStd(df)
fa.plot_all(wspace=0.3, sub_figsize=(12, 3), col_n=5)
```

---

### 11. RawFeaAna - 原始值分析器

**说明**: 直接显示特征的原始值，不做进一步分析。

#### 构造方法

```python
def __init__(self, dataset: pd.DataFrame):
    """
    Motivation:
    - display values without further analysis
    """
```

**说明**: 直接显示原始值，不做任何统计分析。

#### 方法说明

##### calc_stat_values

```python
def calc_stat_values(self):
    ymin, ymax = self._dataset.min().min(), self._dataset.max().max()
    self.ylim = (ymin - 0.05 * (ymax - ymin), ymax + 0.05 * (ymax - ymin))
```

**计算逻辑**: 计算数据的最小值和最大值，用于设置 Y 轴范围。

##### plot_single

```python
def plot_single(self, col, ax):
    self._dataset[col].plot(ax=ax, title=col, ylim=self.ylim)
    ax.set_xlabel("")
```

#### 使用示例

```python
from qlib.contrib.report.data.ana import RawFeaAna

fa = RawFeaAna(df)
fa.plot_all(wspace=0.3, sub_figsize=(12, 3), col_n=5)
```

---

## 完整使用示例

### 示例 1: 基础特征分析

```python
import pandas as pd
import numpy as np
from qlib.contrib.report.data.ana import (
    FeaMeanStd, FeaDistAna, FeaNanAna,
    FeaInfAna, FeaSkewTurt
)

# 准备数据
np.random.seed(42)
dates = pd.date_range('2020-01-01', periods=100)
instruments = [f'STOCK{i:04d}' for i in range(10)]

index = pd.MultiIndex.from_product(
    [instruments, dates],
    names=['instrument', 'datetime']
)

# 创建特征数据
data = pd.DataFrame({
    'feature1': np.random.randn(len(index)),
    'feature2': np.random.randn(len(index)) * 2,
    'feature3': np.random.randn(len(index)) * 0.5,
}, index=index)

# 分析均值和标准差
print("=== 均值和标准差分析 ===")
fa_mean_std = FeaMeanStd(data)
fa_mean_std.plot_all(wspace=0.3, sub_figsize=(12, 3), col_n=3)

# 分析分布
print("\n=== 分布分析 ===")
fa_dist = FeaDistAna(data)
fa_dist.plot_all(wspace=0.3, sub_figsize=(12, 3), col_n=3)

# 分析偏度和峰度
print("\n=== 偏度和峰度分析 ===")
fa_skew = FeaSkewTurt(data)
fa_skew.plot_all(wspace=0.3, sub_figsize=(12, 3), col_n=3)
```

### 示例 2: 缺失值和无穷大值分析

```python
from qlib.contrib.report.data.ana import FeaNanAna, FeaNanAnaRatio, FeaInfAna

# 添加一些缺失值
data_with_nan = data.copy()
data_with_nan.loc[data_with_nan['feature1'] > 2, 'feature1'] = np.nan
data_with_nan.loc[data_with_nan['feature2'] < -3, 'feature2'] = np.nan

# 添加一些无穷大值
data_with_inf = data.copy()
data_with_inf.loc[data_with_inf['feature3'] > 1, 'feature3'] = np.inf

# 分析缺失值数量
print("=== 缺失值数量分析[内容过长，已省略]...")
fa_nan = FeaNanAna(data_with_nan)
fa_nan.plot_all(wspace=0.3, sub_figsize=(12, 3), col_n=3)

# 分析缺失值比例
print("\n=== 缺失值比例分析 ===")
fa_nan_ratio = FeaNanAnaRatio(data_with_nan)
fa_nan_ratio.plot_all(wspace=0.3, sub_figsize=(12, 3), col_n=3)

# 分析无穷大值
print("\n=== 无穷大值分析 ===")
fa_inf = FeaInfAna(data_with_inf)
fa_inf.plot_all(wspace=0.3, sub_figsize=(12, 3), col_n=3)
```

### 示例 3: 组合分析器

```python
from qlib.contrib.report.data.ana import CombFeaAna, FeaMeanStd, FeaSkewTurt

# 组合均值标准差和偏度峰度分析器
print("=== 组合分析：均值标准差 + 偏度峰度 ===")
fa_combined = CombFeaAna(
    dataset=data,
    FeaMeanStd,
    FeaSkewTurt
)
fa_combined.plot_all(wspace=0.3, sub_figsize=(12, 6), col_n=3, row_n=2)
```

### 示例 4: 使用真实 Qlib 数据

```python
import qlqlib
import pandas as pd
from qlib.data import D
from qlib.contrib.report.data.ana import (
    FeaMeanStd, FeaDistAna, FeaNanAna,
    FeaInfAna, FeaSkewTurt
)

# 初始化 Qlib
qlib.init(provider_uri='~/.qlib/qlib_data/cn_data', region='cn')

# 获取数据
instruments = D.instruments('csi500')
fields = [
    '$close',
    '$volume',
    'Ref($close, 1)/$close - 1',  # 收益率
    '$volume / Ref($volume, 1)',  # 成交量变化
]

dates = pd.date_range('2020-01-01', '2020-12-31')
data = D.features(instruments, fields, dates[0], dates[-1])
data.columns = ['close', 'volume', 'return', 'volume_change']

# 转换为 MultiIndex 格式
data = data.reset_index()
data = data.set_index(['instrument', 'datetime'])

# 分析数据
print("=== Qlib 数据分析 ===")

# 均值和标准差
fa_mean_std = FeaMeanStd(data)
fa_mean_std.plot_all(wspace=0.3, sub_figsize=(12, 3), col_n=2)

# 分布分析
fa_dist = FeaDistAna(data)
fa_dist.plot_all(wspace=0.3, sub_figsize=(12, 3), col_n=2)

# 偏度和峰度
fa_skew = FeaSkewTurt(data)
fa_skew.plot_all(wspace=0.3, sub_figsize=(12, 3), col_n=2)
```

---

## 最佳实践

### 1. 数据准备

```python
# 确保数据索引包含 'datetime' 级别
assert 'datetime' in data.index.names

# 使用 MultiIndex 结构 [instrument, datetime]
assert data.index.names == ['instrument', 'datetime']
```

### 2. 分析器选择

```python
# 数据概览
fa_raw = RawFeaAna(data)

# 统计特性
fa_mean_std = FeaMeanStd(data)
fa_skew = FeaSkewTurt(data)

# 分布检查
fa_dist = FeaDistAna(data)

# 数据质量
fa_nan = FeaNanAna(data)
fa_nan_ratio = FeaNanAnaRatio(data)
fa_inf = FeaInfAna(data)

# 时间特性
fa_ac = FeaACAna(data)

# 组合分析
fa_combined = CombFeaAna(data, FeaMeanStd, FeaSkewTurt)
```

### 3. 参数调整

```python
# 调整子图大小
fa.plot_all(
    sub_figsize=(12, 3),  # 每个子图的大小
    col_n=3,               # 每行的子图数量
    wspace=0.3,             # 水平间距
    hspace=0.4              # 垂直间距
)
```

### 4. 性能考虑

```python
# 对于大数据集，先使用抽样分析
if len(data) > 100000:
    data_sample = data.sample(100000)
    fa = FeaMeanStd(data_sample)
else:
    fa = FeaMeanStd(data)
```

---

## 常见问题

### Q: 如何只分析特定特征？

A: 重写 `skip` 方法：

```python
class CustomAnalyser(FeaMeanStd):
    def skip(self, col):
        # 只分析 feature1 和 feature2
        return col not in ['feature1', 'feature2']

fa = CustomAnalyser(data)
fa.plot_all(wspace=0.3, sub_figsize=(12, 3), col_n=2)
```

### Q: 如何自定义绘图样式？

A: 重写 `plot_single` 方法：

```python
class CustomDistAnalyser(FeaDistAna):
    def plot_single(self, col, ax):
        # 使用不同的颜色和 bins 数量
        sns.histplot(
            self._dataset[col],
            ax=ax,
            kde=True,
            bins=50,
            color='red'
        )
        ax.set_xlabel("")
        ax.set_title(f"{col} (Custom)")

fa = CustomDistAnalyser(data)
fa.plot_all(wspace=0.3, sub_figsize=(12, 3), col_n=3)
```

### Q: 如何组合多个分析器？

A: 使用 `CombFeaAna`：

```python
fa = CombFeaAna(
    dataset=data,
    FeaMeanStd,
    FeaSkewTurt,
    FeaDistAna
)
fa.plot_all(wspace=0.3, sub_figsize=(12, 9), col_n=3, row_n=3)
```

### Q: 如何保存图表？

A: 在绘图后使用 matplotlib 保存：

```python
import matplotlib.pyplot as plt

fa = FeaMeanStd(data)
fa.plot_all(wspace=0.3, sub_figsize=(12, 3), col_n=3)

# 保存当前图形
plt.savefig('feature_analysis.png', dpi=300, bbox_inches='tight')
```

### Q: 如何处理大量特征？

A: 使用迭代的方式，每次分析一部分：

```python
features = data.columns.tolist()
batch_size = 10

for i in range(0, len(features), batch_size):
    batch_features = features[i:i+batch_size]
    batch_data = data[batch_features]

    fa = FeaMeanStd(batch_data)
    fa.plot_all(wspace=0.3, sub_figsize=(12, 3), col_n=batch_size)
```

### Q: FeaACAna 需要什么依赖？

A: `FeaACAna` 需要 `qlib.contrib.eva.alpha` 中的 `pred_autocorr_all` 函数。确保该模块可用。

### Q: 为什么有些分析器没有显示？

A: 分析器自动跳过：
1. 非数值类型的特征（`NumFeaAnalyser` 及其子类）
2. 没有缺失值的特征（`FeaNanAna`, `FeaNanAnaRatio`）
3. 没有无穷大值的特征（`FeaInfAna`）

可以通过重写 `skip` 方法来改变这种行为。

---

## 分析器对比

| 分析器 | 继承自 | 分析内容 | 适用场景 |
|--------|--------|---------|---------|
| CombFeaAna | FeaAnalyser | 组合多个分析器 | 综合分析 |
| FeaMeanStd | NumFeaAnalyser | 均值和标准差 | 统计特性 |
| FeaSkewTurt | NumFeaAnalyser | 偏度和峰度 | 分布形态 |
| FeaDistAna | NumFeaAnalyser | 数据分布 | 分布检查 |
| FeaNanAna | FeaAnalyser | 缺失值数量 | 数据质量 |
| FeaNanAnaRatio | FeaAnalyser | 缺失值比例 | 数据质量 |
| FeaInfAna | NumFeaAnalyser | 无穷大值 | 数据质量 |
| FeaACAna | NumFeaAnalyser | 自相关 | 时序特性 |
| RawFeaAna | FeaAnalyser | 原始值 | 数据概览 |
| ValueCNT | FeaAnalyser | 唯一值计数 | 数据特征 |
