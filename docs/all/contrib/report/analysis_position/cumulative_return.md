# analysis_position/cumulative_return.py

## 模块概述

`qlib.contrib.report.analysis_position.cumulative_return.py` 提供了分析买入、卖出和持有股票累积收益的功能。该模块通过分析策略在不同交易动作下的表现，评估策略的选股能力和时机把握能力。

## 核心函数

### cumulative_return_graph

**说明**: 生成买入、卖出、持有股票的累积收益图表，展示每种交易动作的盈利能力。

#### 函数签名

```python
def cumulative_return_graph(
    position: dict,
    report_normal: pd.DataFrame,
    label_data: pd.DataFrame,
    show_notebook: bool = True,
    start_date: str = None,
    end_date: str = None
) -> Iterable[go.Figure]:
```

#### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------||======|========|------|
| position | dict | 必需 | 持仓数据，回测结果 |
| report_normal | pd.DataFrame | 必需 | 报告数据，包含 return, cost, bench, turnover |
| label_data | pd.DataFrame | 必需 | 标签数据，包含 label 列 |
| show_notebook | bool | True | 是否在 Notebook 中显示 |
| start_date | str | None | 开始日期 |
| end_date | str | None | 结束日期 |

#### 数据格式要求

**position (持仓数据）**:
回测返回的持仓字典，包含每日的股票持仓信息。

**report_normal (报告数据）**:

| 必需列 | | | 说明 |
|--------|-|-|------|
| return | float | | 每日收益率 |
| cost | float | | 每日交易成本 |
| bench | float | | 基准指数收益率 |
| turnover | float | | 每日换手率 |

**示例**:

```python
                            return      cost        bench       turnover
date
2017-01-04  0.003421    0.000864    0.011693    0.576325
2017-01-05  0.000508    0.000447    0.000721    0.227882
```

**label_data (标签数据）**:

| 必需列 | | | 说明 |
|--------|-|-|------|
| label | float | | 下一期收益率 |

**重要**: 标签 T 是从 T 到 T+1 的变化，建议使用 `Ref($close, -1)/$close - 1` 计算。

索引必须是 MultiIndex，包含 instrument 和 datetime。

**示例**:

```python
                                                label
instrument  datetime
SH600004        2017-12-11  -0.013502
                2017-12-12  -0.072367
                2017-12-13  -0.068605
                2017-12-14  0.012440
                2017-12-15  -0.102778
```

#### 图表结构

生成 4 组图表，每组包含 3 个子图：

| 图表组 | 子图 1 | 子图 2 | 子图 3 |
|--------|--------|--------|--------|
| buy | 累积买入收益 | 买入权重 | 买入收益分布 |
| sell | 累积卖出收益 | 卖出权重 | 卖出收益分布 |
| buy_minus_sell | 累积多空收益 | 买入+卖出权重 | 多空收益分布 |
| hold | 累积持有收益 | 持有权重 | 持有收益分布 |

#### 图表详细说明

##### 子图 1: 累积收益线图

- **X 轴**: 交易日
- **Y 轴**: 累积收益
- **计算公式**: `(((Ref($close, -1)/$close - 1) * weight).sum() / weight.sum()).cumsum()`

**说明**: 展示每种交易动作的平均收益累积变化。

##### 子图 2: 权重柱状图

- **X 轴**: 交易日
- **Y 轴**: 权重总和
- **sell 图**: y 值是 buy_weight + sell_weight

**说明**: 展示每种交易动作的持仓权重变化。

##### 子图 3: 收益分布直方图

- **X 轴**: 单日收益
- **Y 轴**: 频次
- **红色线**: 平均收益

**说明**: 展示每种交易动作的收益分布情况。

#### 收益解读

- **buy**: y > 0 表示盈利，理想情况下 cum_buy 持续上涨
- **sell**: y < 0 表示盈利（卖出下跌的股票），理想情况下 cum_sell 持续下跌
- **buy_minus_sell**: y > 0 表示盈利，理想情况下 cum_buy_minus_sell 持续上涨
- **hold**: y > 0 表示盈利，理想情况下 cum_hold 持续上涨

#### 返回值

- 如果 `show_notebook=True`，在 Notebook 中显示图表
- 如果 `show_notebook=False`，返回包含 plotly Figure 对象的迭代器

---

## 辅助函数

### _get_cum_return_data_with_position

**说明**: 计算买入、卖出、持有股票的累积收益数据。

#### 函数签名

```python
def _get_cum_return_data_with_position(
    position: dict,
    report_normal: pd.DataFrame,
    label_data: pd.DataFrame,
    start_date: str = None,
    end_date: str = None
):
```

#### 返回值

包含计算指标的 DataFrame，包含以下列：

| 列名 | 计算方式 | 说明 |
|------|---------|------|
| hold_value | (label * weight).sum() | 持有股票的总收益 |
| hold_mean | hold_value / weight.sum() | 持有股票的平均收益 |
| hold_weight | weight.sum() | 持有股票的总权重 |
| buy_value | (label * weight).sum() | 买入股票的总收益 |
| buy_mean | buy_value / weight.sum() | 买入股票的平均收益 |
| buy_weight | weight.sum() | 买入股票的总权重 |
| sell_value | (label * weight).sum() | 卖出股票的总收益 |
| sell_mean | sell_value / weight.sum() | 卖出股票的平均收益 |
| sell_weight | weight.sum() | 卖出股票的总权重 |
| buy_minus_sell_value | buy_value - sell_value | 多空总收益 |
| buy_minus_sell_mean | buy_mean - sell_mean | 多空平均收益 |
| buy_plus_sell_weight | buy_weight + sell_weight | 买入+卖出总权重 |
| cum_hold | hold_mean.cumsum() | 持有累积收益 |
| cum_buy | buy_mean.cumsum() | 买入累积收益 |
| cum_sell | sell_mean.cumsum() | 卖出累积收益 |
| cum_buy_minus_sell | buy_minus_sell_mean.cumsum() | 多空累积收益 |

#### 计算逻辑

1. 解析持仓数据，识别买入、卖出、持有操作
2. 计算每种操作的总收益和平均收益
3. 计算累积收益

#### 状态说明

```python
status = {
    0: 'hold',   # 持有
    1: 'buy',    # 买入
    -1: 'sell'    # 卖出
}
```

---

### _get_figure_with_position

**说明**: 生成累积收益图表。

#### 函数签名

```python
def _get_figure_with_position(
    position: dict,
    report_normal: pd.DataFrame,
    label_data: pd.DataFrame,
    start_date: str = None,
    end_date: str = None
) -> Iterable[go.Figure]:
```

#### 返回值

生成 4 个图表的迭代器，分别对应 buy、sell、buy_minus_sell、hold。

#### 图表配置

每组图表采用 2 行 2 列的布局：

- **第 1 行左**: 累积收益线图（2 行高度）
- **第 1 行右**: 收益分布直方图（1 行高度）
- **第 2 行左**: 权重柱状图（1 行高度）

**布局规格**:
```python
specs = [
    [{"rowspan": 1}, {"rowspan": 2}],
    [{"rowspan": 1}, None]
]
```

---

## 使用示例

### 示例 1: 基础使用

```python
from qlib.data import D
from qlib.contrib.evaluate import backtest
from qlib.contrib.strategy import TopkDropoutStrategy
from qlib.contrib.report import analysis_position as ap

# 回测参数
bparas = {
    'limit_threshold': 0.095,
    'account': 1000000000
}

sparas = {
    'topk': 50,
    'n_drop': 5
}
strategy = TopkDropoutStrategy(**sparas)

# 执行回测
report_normal_df, positions = backtest(pred_df, strategy, **bparas)

# 准备标签数据
pred_df_dates = pred_df.index.get_level_values(level='datetime')
features_df = D.features(
    D.instruments('csi500'),
    ['Ref($close, -1)/$close - 1'],
    pred_df_dates.min(),
    pred_df_dates.max()
)
features_df.columns = ['label']

# 显示累积收益图表
ap.cumulative_return_graph(positions, report_normal_df, features_df)
```

### 示例 2: 指定日期范围

```python
import pandas as pd

# 指定分析的时间范围
start_date = '2018-01-01'
end_date = '2019-12-31'

ap.cumulative_return_graph(
    positions,
    report_normal_df,
    features_df,
    start_date=start_date,
    end_date=end_date
)
```

### 示例 3: 返回图表对象

```python
# 返回图表对象
figures = ap.cumulative_return_graph(
    positions,
    report_normal_df,
    features_df,
    show_notebook=False
)

# 遍历所有图表
for i, fig in enumerate(figures):
    fig.update_layout(title=f'累积收益 {i+1}')
    fig.show()
```

### 示例 4: 保存图表

```python
import os

# 创建输出目录
output_dir = 'cumulative_return_reports'
os.makedirs(output_dir, exist_ok=True)

# 生成图表
figures = ap.cumulative_return_graph(
    positions,
    report_normal_df,
    features_df,
    show_notebook=False
)

# 保存图表
names = ['buy', 'sell', 'buy_minus_sell', 'hold']
for name, fig in zip(names, figures):
    output_path = os.path.join(output_dir, f'{name}_cumulative_return.html')
    fig.write_html(output_path)
    print(f"已保存: {output_path}")
```

### 示例 5: 对比多个策略

```python
# 假设有多个策略的结果
strategy_results = {
    'strategy_1': (report_df_1, positions_1),
    'strategy_2': (report_df_2, positions_2),
    'strategy_3': (report_df_3, positions_3),
}

for name, (report_df, pos) in strategy_results.items():
    print(f"分析策略: {name}")
    ap.cumulative_return_graph(pos, report_df, features_df)
```

---

## 图表解读指南

### 如何解读买入图表

#### 累积买入收益 (cum_buy)

- **持续上涨**: 买入的股票表现良好，选股能力强
- **震荡不前**: 买入的股票表现一般
- **持续下跌**: 买入的股票表现不佳，可能需要调整选股逻辑

#### 买入权重 (buy_weight)

- **高波动**: 频繁调仓
- **稳定增长**: 逐步建仓
- **逐渐降低**: 减少新买入

#### 买入收益分布

- **红色线（平均收益）> 0**: 平均买入盈利
- **分布偏右**: 大部分买入盈利
- **分布偏左**: 大部分买入亏损

### 如何解读卖出图表

#### 累积卖出收益 (cum_sell)

- **持续下跌**: 卖出的股票下跌，避免损失，卖出决策正确
- **震荡不前**: 卖出的股票表现一般
- **持续上涨**: 卖出的股票继续上涨，可能卖早了

**注意**: 卖出图表中，y < 0 表示盈利（因为卖出下跌的股票避免了损失）。

#### 卖出权重 (sell_weight)

- **高波动**: 频繁减仓
- **稳定**: 持续减持
- **间歇性**: 周期性调仓

#### 卖出收益分布

- **红色线（平均收益）< 0**: 平均卖出正确
- **分布偏左**: 大部分卖出正确（股票下跌）
- **分布偏右**: 大部分卖出不正确（股票上涨）

### 如何解读多空图表

#### 累积多空收益 (cum_buy_minus_sell)

- **持续上涨**: 多空策略有效，买入表现好且卖出正确
- **震荡**: 多空效果一般
- **持续下跌**: 多空策略失败，可能选股或时机有问题

#### 多空组合权重 (buy_plus_sell_weight)

- **高**: 交易活跃，换手率高
- **低**: 交易不活跃，持仓稳定

### 如何解读持有图表

#### 累积持有收益 (cum_hold)

- **持续上涨**: 持有的股票表现良好，持仓逻辑正确
- **震荡**: 持有的股票表现一般
- **持续下跌**: 持有的股票表现不佳，可能需要调整持仓逻辑

#### 持有权重 (hold_weight)

- **稳定**: 策略持仓稳定
- **波动**: 频繁调整持仓

---

## 性能指标解读

### 关键指标

| 指标 | 计算方式 | 理想表现 |
|------|---------|---------|
| 买入平均收益 | buy_mean | > 0 |
| 卖出平均收益 | sell_mean | < 0 |
| 多空平均收益 | buy_mean - sell_mean | > 0 |
| 持有平均收益 | hold_mean | > 0 |
| 买入年化收益 | cum_buy[-1] / len * 252 | > 0 |
| 卖出年化收益 | cum_sell[-1] / len * 252 | < 0 |
| 多空年化收益 | cum_buy_minus_sell[-1] / len * 252 | > 0 |
| 持有年化收益 | cum_hold[-1] / len * 252 | > 0 |

### 综合评估

#### 优秀策略

- buy_mean > 0 且持续上升
- sell_mean < 0 且持续下降
- buy_minus_sell_mean > 0 且持续上升
- hold_mean > 0 且持续上升

#### 一般策略

- buy_mean > 0 但波动较大
- sell_mean < 0 但波动较大
- buy_minus_sell_mean > 0 但波动较大
- hold_mean > 0 但波动较大

#### 需要改进的策略

- buy_mean < 0 或 cum_buy 持续下降
- sell_mean > 0 或 cum_sell 持续上升
- buy_minus_sell_mean < 0 或 cum_buy_minus_sell 持续下降
- hold_mean < 0 或 cum_hold 持续下降

---

## 最佳实践

### 1. 数据准备

```python
# 确保 label_data 使用正确的标签计算
# 标签 T 是从 T 到 T+1 的变化
label_data = D.features(
    instruments,
    ['Ref($close, -1)/$close - 1'],  # 正确的标签定义
    start_date,
    end_date
)
```

### 2. 定期监控

```python
# 定期分析累积收益
import pandas as pd

# 按季度分析
quarters = pd.date_range(start_date, end_date, freq='Q')

for i in range(len(quarters) - 1):
    q_start = quarters[i]
    q_end = quarters[i+1] - pd.Timedelta(days=1)

    print(f"分析季度: {q_start} ~ {q_end}")
    ap.cumulative_return_graph(
        positions,
        report_normal_df,
        features_df,
        start_date=q_start,
        end_date=q_end
    )
```

### 3. 对比基准

```python
# 可以修改代码添加基准对比
# 比如将持仓收益与基准收益对比
```

### 4. 异常检测

```python
# 检测异常的买入或卖出
cum_data = _get_cum_return_data_with_position(
    positions,
    report_normal_df,
    features_df
)

# 检测买入收益异常
buy_anomaly = cum_data['buy_mean'] > cum_data['buy_mean'].mean() + 3 * cum_data['buy_mean'].std()
if buy_anomaly.any():
    print("警告: 检测到异常的买入收益")
    print(cum_data[buy_anomaly])
```

---

## 常见问题

### Q: 为什么卖出图表中 y < 0 表示盈利？

A: 因为卖出操作的目标是卖出表现不好的股票。如果股票下跌（label < 0），卖出是正确的决策，避免了损失。所以 cum_sell < 0 表示"卖出决策"是正确的，避免了损失。

### Q: buy_minus_sell 代表什么？

A: buy_minus_sell = buy_mean - sell_mean，表示多空策略的收益：
- 买入表现好的股票（希望 label > 0）
- 卖出表现差的股票（希望 label < 0，即避免损失）

如果 buy_minus_sell > 0，说明多空策略整体盈利。

### Q: 如何判断策略是否有效？

A: 综合观察以下指标：
1. **cum_buy 持续上涨**: 买入决策正确
2. **cum_sell 持续下降**: 卖出决策正确
3. **cum_buy_minus_sell 持续上涨**: 多空策略有效
4. **cum_hold 持续上涨**: 持仓逻辑正确

### Q: 如果 buy_mean 为负数怎么办？

A: 可能的原因：
1. **选模型题**: 买入的股票表现不好
2. **标签计算错误**: 标签的定义与预期不符
3. **时机问题**: 买入后股票立即下跌
4. **市场环境**: 在熊市中买入

建议检查标签计算和选股逻辑。

### Q: 如何优化买入卖出逻辑？

A: 基于图表分析：
1. **buy_mean 低**: 改进选股模型，提高预测准确性
2. **sell_mean 高**: 调整卖出阈值，避免卖飞
3. **权重波动大**: 调整调仓频率，降低交易成本
4. **hold_mean 低**: 优化持仓管理逻辑

### Q: 可以分析日内交易吗？

A: 代码注释中提到 "FIXME: support HIGH-FREQ"，目前支持日度数据。要支持日内数据，需要修改日期格式处理部分。

### Q: 如何自定义图表？

A: 通过返回图表对象然后修改：

```python
figures = ap.cumulative_return_graph(
    positions,
    report_normal_df,
    features_df,
    show_notebook=False
)

# 修改第一个图表（buy 图表）
fig = next(figures)
fig.update_layout(
    title='买入收益分析',
    height=600
)

# 修改子图样式
for trace in fig.data:
    if 'cum' in trace.name:
        trace.update(line=dict(width=3, color='blue'))

fig.show()
```
