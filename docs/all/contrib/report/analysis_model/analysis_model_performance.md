# analysis_model/analysis_model_performance.py

## 模块概述

`qlib.contrib.report.analysis_model.analysis_model_performance.py` 提供了全面的模型性能分析功能。该模块生成分组收益分析、IC（信息系数）分析、自相关分析、换手率分析等多种性能指标的可视化图表。

## 核心函数

### model_performance_graph

**说明**: 全面分析模型预测性能，生成多种性能指标的可视化图表。

#### 函数签名

```python
def model_performance_graph(
    pred_label: pd.DataFrame,
    lag: int = 1,
    N: int = 5,
    reverse: bool = False,
    rank: bool = False,
    graph_names: list = ["group_return", "pred_ic", "pred_autocorr"],
    show_notebook: bool = True,
    show_nature_day: bool = False,
    **kwargs
) -> [list, tuple]:
```

#### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| pred_label | pd.DataFrame | 必需 | 预测得分和标签数据 |
| lag | int | 1 | 滞后期数，用于自相关计算 |
| N | int | 5 | 分组数量，默认 5 组 |
| reverse | bool | False | 是否反转得分（乘以 -1） |
| rank | bool | False | 是否计算 Rank IC |
| graph_names | list | ["group_return", "pred_ic", "pred_autocorr"] | 要生成的图表类型列表 |
| show_notebook | bool | True | 是否在 Notebook 中显示 |
| show_nature_day | bool | False | 是否显示非交易日 |
| **kwargs | - | - | 其他参数，如 rangebreaks |

#### pred_label 数据格式要求

| 必需列 | | | 说明 |
|--------|-|-|------|
| score | float | | 预测得分 |
| label | float | | 真实标签（通常为未来收益率） |

索引必须是 MultiIndex，包含 instrument 和 datetime。

**示例数据**:

```python
instrument  datetime        score         label
SH600004    2017-12-11  -0.013502      -0.013502
            2017-12-12  -0.072367      -0.072367
            2017-12-13  -0.068605      -0.068605
            2017-12-14   0.012440       0.012440
            2017-12-15  -0.102778      -0.102778
```

#### 支持的图表类型

| 图表名称 | 说明 | 包含子图 |
|---------|------|---------|
| group_return | 分组收益分析 | 累积收益图、long-short-short 和 long-average 分布图 |
| pred_ic | 预测 IC 分析 | IC 时序图、月度 IC 热力图、IC 分布和 Q-Q 图 |
| pred_autocorr | 自相关分析 | 自相关时序图 |
| pred_turnover | 换手率分析 | Top 和 Bottom 换手率时序图 |

---

## 详细图表说明

### 1. group_return（分组收益分析）

**说明**: 根据预测得分将股票分为 N 组，分析各组的收益表现。

#### 计算逻辑

1. 按预测得分降序排序
2. 将股票均匀分为 N 组（Group1, Group2, ..., GroupN）
3. Group1 包含得分最高的股票，GroupN 包含得分最低的股票
4. 计算各组的平均收益并累积

#### 生成的子图

##### 累积收益图

- X 轴：日期
- Y 轴：累积收益
- 显示各组（Group1 到 GroupN）的累积收益曲线

##### long-short 和 long-average 分布图

- long-short = Group1 - GroupN（做多高分组，做空低分组）
- long-average = Group1 - 整体平均（做多高分组，做空市场平均）
- 使用 DistplotGraph 显示分布

#### 使用示例

```python
am.model_performance_graph(
    pred_label,
    graph_names=["group_return"]
)
```

---

### 2. pred_ic（预测 IC 分析）

**说明**: 计算预测得分与真实标签之间的 IC（信息系数）和 Rank IC。

#### IC 指标说明

- **IC (Information Coefficient)**: Pearson 相关系数
  - 衡量预测值与真实值的线性关系
  - 范围：[-1, 1]，值越大表示预测越准确
- **Rank IC**: Spearman 相关系数
  - 衡量预测排序与真实排序的一致性
  - 对异常值更稳健

#### 生成的子图

##### IC 时序图（Bar Graph）

- X 轴：日期
- Y 轴：IC 值
- 显示每日 IC 和 Rank IC 的变化趋势

##### 月度 IC 热力图

- X 轴：月份
- Y 轴：年份
- 颜色表示 IC 值的大小
- 识别模型在特定月份的表现

##### IC 分布图（Distplot）

- X 轴：IC 值
- Y 轴：频次
- 显示 IC 值的分布情况

##### IC Q-Q 图

- X 轴：正态分布分位数
- Y 轴：实际 IC 分位数
- 比较实际 IC 分布与正态分布

#### 使用示例

```python
# 生成 IC 分析（包含 IC 和 Rank IC）
am.model_performance_graph(
    pred_label,
    graph_names=["pred_ic"]
)

# 只计算 IC
am.model_performance_graph(
    pred_label,
    rank=False,
    graph_names=["pred_ic"]
)
```

---

### 3. pred_autocorr（自相关分析）

**说明**: 分析预测得分的自相关性。

#### 计算逻辑

```python
score_last = score.shift(lag)
autocorr = score.rank(pct=True).corr(score_last.rank(pct=True))
```

#### 应用场景

- 识别预测信号的时间序列特性
- 判断预测值是否具有持续性
- 评估换手策略的合理性

#### 图表说明

- X 轴：时间
- Y 轴：自相关系数
- 接近 1 表示预测信号具有很强的持续性
- 接近 0 表示预测信号随机变化

#### 使用示例

```python
# 生成自相关分析（lag=1）
am.model_performance_graph(
    pred_label,
    lag=1,
    graph_names=["pred_autocorr"]
)

# 使用更大的滞后期
am.model_performance_graph(
    pred_label,
    lag=5,
    graph_names=["pred_autocorr"]
)
```

---

### 4. pred_turnover（换手率分析）

**说明**: 分析多头和空头持仓的换手率。

#### 计算逻辑

- Top 换手率：得分最高的 1/N 股票中，与上一期相比发生变化的比例
- Bottom 换手率：得分最低的 1/N 股票中，与上一期相比发生变化的比例

#### 应用场景

- 评估策略的交易频率
- 计算交易成本
- 优化持仓周期

#### 图表说明

- 两条曲线：Top 换手率和 Bottom 换手率
- 值越大表示持仓变化越频繁
- 通常 Top 换手率会大于 Bottom 换手率

#### 使用示例

```python
# 生成换手率分析（N=5，即分析前 20% 和后 20% 的股票）
am.model_performance_graph(
    pred_label,
    N=5,
    graph_names=["pred_turnover"]
)
```

---

## 辅助函数

### ic_figure

**说明**: 生成 IC 图表，支持自定义范围断点。

#### 函数签名

```python
def ic_figure(
    ic_df: pd.DataFrame,
    show_nature_day: bool = True,
    **kwargs
) -> go.Figure
```

#### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| ic_df | pd.DataFrame | 必需 | IC 数据 |
| show_nature_day | bool | True | 是否显示非交易日 |
| **kwargs | - | | rangebreaks 等参数 |

#### 使用示例

```python
# 计算 IC
ic_df = pd.DataFrame({
    'IC': [0.05, 0.03, 0.08, -0.02, 0.04],
    'Rank IC': [0.06, 0.04, 0.09, -0.01, 0.05]
}, index=pd.date_range('2020-01-01', periods=5))

# 生成 IC 图表
fig = am.ic_figure(ic_df)
fig.show()
```

---

## 完整使用示例

### 示例 1: 基础模型性能分析

```python
import pandas as pd
import numpy as np
from qlib.contrib.report import analysis_model as am

# 准备数据
np.random.seed(42)
instruments = [f'STOCK{i:04d}' for i in range(100)]
dates = pd.date_range('2020-01-01', periods=252)

# 生成预测得分
pred_score = np.random.randn(len(instruments) * len(dates)) * 0.1

# 生成标签（假设模型有一定预测能力）
true_score = pred_score + np.random.randn(len(pred_score)) * 0.05

# 创建 MultiIndex
index = pd.MultiIndex.from_product(
    [instruments, dates],
    names=['instrument', 'datetime']
)

# 创建 DataFrame
pred_label = pd.DataFrame({
    'score': pred_score,
    'label': true_score
}, index=index)

# 生成所有默认图表
am.model_performance_graph(pred_label)
```

### 示例 2: 自定义图表组合

```python
# 只生成分组收益和 IC 分析
am.model_performance_graph(
    pred_label,
    graph_names=["group_return", "pred_ic"]
)
```

### 示例 3: 反转预测得分

```python
# 有时候模型预测的是负向关系，可以反转得分
am.model_performance_graph(
    pred_label,
    reverse=True,  # score *= -1
    graph_names=["group_return"]
)
```

### 示例 4: 调整分组数量

```python
# 使用 10 个分组（更细致的分析）
am.model_performance_graph(
    pred_label,
    N=10,
    graph_names=["group_return"]
)
```

### 示例 5: 添加换手率分析

```python
# 生成分组收益、IC、自相关和换手率分析
am.model_performance_graph(
    pred_label,
    graph_names=[
        "group_return",
        "pred_ic",
        "pred_autocorr",
        "pred_turnover"
    ]
)
```

### 示例 6: 使用 rangebreaks 隐藏非交易日

```python
from qlib.contrib.report.utils import guess_plotly_rangebreaks

# 推断日期断点
rangebreaks = guess_plotly_rangebreaks(
    pred_label.index.get_level_values('datetime')
)

# 生成图表并应用 rangebreaks
am.model_performance_graph(
    pred_label,
    rangebreaks=rangebreaks
)
```

### 示例 7: 完整的模型评估流程

```python
import qlib
import pandas as pd
from qlib.data import D
from qlib.contrib.model.gbdt import LGBModel
from qlib.contrib.report import analysis_model as am

# 1. 初始化 Qlib
qlib.init(provider_uri='~/.qlib/qlib_data/cn_data', region='cn')

# 2. 准备数据
instruments = D.instruments('csi500')
fields = [
    'Ref($close, -1)/$close - 1',  # 标签
    '$volume / Ref($volume, 1)',    # 特征
    'Ref($close, 1)/$close',      # 特征
]
dates = pd.date_range('2018-01-01', '2020-12-31')

data = D.features(instruments, fields, dates[0], dates[-1])
data.columns = ['label', 'feature1', 'feature2']

# 3. 训练模型
model = LGBModel(
    loss='mse',
    col_sample_bytree=0.8,
    subsample=0.8,
    n_estimators=100,
    learning_rate=0.05
)

model.fit(
    data.loc[:'2019-12-31'],
    data.loc[:'2019-12-31']['label']
)

# 4. 预测
pred = model.predict(data.loc['2020-01-01':])

# 5. 准备分析数据
test_data = data.loc['2020-01-01':]
pred_label = pd.DataFrame({
    'score': pred.values,
    'label': test_data['label'].values
}, index=pred.index)

# 6. 模型性能分析
print("=== 模型性能分析 ===")
print("\n1. 分组收益分析")
am.model_performance_graph(
    pred_label,
    graph_names=["group_return"]
)

print("\n2. IC 分析")
am.model_performance_graph(
    pred_label,
    graph_names=["pred_ic"]
)

print("\n3. 自相关分析")
am.model_performance_graph(
    pred_label,
    lag=1,
    graph_names=["pred_autocorr"]
)

print("\n4. 换手率分析")
am.model_performance_graph(
    pred_label,
    N=5,
    graph_names=["pred_turnover"]
)

print("\n5. 综合分析")
am.model_performance_graph(
    pred_label,
    graph_names=[
        "group_return",
        "pred_ic",
        "pred_autocorr",
        "pred_turnover"
    ]
)
```

---

## 性能指标解读指南

### 分组收益分析

| 指标 | 理想表现 | 说明 |
|------|---------|------|
| Group1 累积收益 | 明显 > GroupN 累积收益 | 模型能够正确排序股票 |
| long-short | 持续为正 | 多空策略有效 |
| long-average | 持续为正 | 选股超越市场平均 |
| 各组收益差异 | 单调递减 | 预测得分与收益正相关 |

### IC 分析

| 指标 | 理想表现 | 说明 |
|------|---------|------|
| IC 均值 | > 0 | 总体具有预测能力 |
| IC 标准差 | 相对较小 | 预测稳定 |
| IC/标准差 | > 2 | 具有统计显著性 |
| IC 时序 | 持续为正 | 预测能力稳定 |
| 月度 IC | 均匀分布 | 无明显周期性 |

### 自相关分析

| 指标 | 理想表现 | 说明 |
|------|---------|------|
| 自相关系数 | 适中（0.3-0.7） | 信号有持续性但不过度 |
| 自相关过高（>0.8） | 降低换手 | 可以减少交易频率 |
| 自相关过低（<0.2） | 频繁调仓 | 交易成本高 |

### 换手率分析

| 指标 | 理想表现 | 说明 |
|------|---------|------|
| Top 换手率 | 适中（0.5-0.8） | 适当调仓 |
| Bottom 换手率 | 较低 | 底部持仓稳定 |
| 换手率差异 | 较大 | 顶部股票变化快 |

---

## 最佳实践

### 1. 数据对齐

```python
# 确保 pred_label 中的 score 和 label 完全对应
assert len(pred_label['score']) == len(pred_label['label'])
assert not pred_label.isna().any().any()
```

### 2. 标签计算

```python
# label 通常使用未来收益率
label = 'Ref($close, -1)/$close - 1'
```

### 3. 分组数量选择

```python
# N=5：适合大多数情况
# N=10：更细致的分析
# N=3：简单直观
```

### 4. 滞后期选择

```python
# lag=1：分析相邻期的相关性
# lag=5：分析一周后的相关性
```

### 5. 图表选择

```python
# 快速评估：只看 group_return 和 pred_ic
# 深入分析：查看所有图表
```

### 6. 反转得分

```python
# 如果模型预测负向关系，使用 reverse=True
am.model_performance_graph(
    pred_label,
    reverse=True
)
```

### 7. 日期处理

```python
# 使用 rangebreaks 隐藏非交易日
from qlib.contrib.report.utils import guess_plotly_rangebreaks

rangebreaks = guess_plotly_rangebreaks(
    pred_label.index.get_level_values('datetime')
)
am.model_performance_graph(
    pred_label,
    rangebreaks=rangebreaks
)
```

---

## 常见问题

### Q: IC 和 Rank IC 哪个更重要？

A: 通常 Rank IC 更重要，因为它衡量的是排序一致性，对异常值更稳健。在因子投资中，我们关心的是能否选出相对更好的股票，而不是精确预测收益值。

### Q: 为什么 Group1 的累积收益有时会低于 GroupN？

A: 可能的原因：
1. **过拟合**: 模型在训练集上表现好，但在测试集上失效
2. **数据泄漏**: 标签计算不当，使用了未来数据
3. **标签定义**: 标签的预测方向与模型预期相反（尝试 reverse=True）
4. **市场环境变化**: 模型在不同市场环境下表现不同

### Q: 如何解释自相关系数？

A:
- **接近 1**: 预测信号变化缓慢，可以降低换手频率
- **接近 0**: 预测信号变化快，需要频繁调仓
- **负值**: 预测信号震荡，可能存在问题

### Q: 换手率多少是合理的？

A: 取决于投资策略：
- **长期策略**: 换手率 0.2-0.4（月度调仓）
- **中期策略**: 换手率 0.5↓0.8（周度调仓）
- **短期策略**: 换手率 0.8-1.0（日度调仓）

### Q: 如何保存图表？

A: 设置 show_notebook=False 返回图表对象，然后保存：

```python
figures = am.model_performance_graph(pred_label, show_notebook=False)

# 保存为 HTML
for i, fig in enumerate(figures):
    fig.write_html(f'performance_chart_{i}.html')

# 保存为 PNG（需要安装 kaleido）
for i, fig in enumerate(figures):
    fig.write_image(f'performance_chart_{i}.png')
```

### Q: show_nature_day 参数有什么用？

A: 当 show_nature_day=True 时，图表会显示非交易日；当 False 时，只显示交易日。通常设置为 False 以提高图表可读性。

### Q: 如何优化模型性能？

A: 根据分析结果：

**GroupN 收益高**:
- 检查标签计算是否正确
- 考虑使用 reverse=True
- 改进模型训练

**IC 低**:
- 增加更多特征
- 使用更复杂的模型
- 调整模型超参数

**自相关低**:
- 可能需要更频繁调仓
- 考虑增加滞后期分析

**换手率高**:
- 可能交易成本高
- 考虑调整持仓周期
- 增加换手率限制
