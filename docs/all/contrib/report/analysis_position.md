# analysis_position 模块

## 模块概述

`qlib.contrib.report.analysis_position` 模块提供了用于分析和可视化持仓数据的各种函数。该模块包含以下核心功能：

- **report_graph**: 生成回测报告图表，展示收益、回撤、换手率等指标
- **cumulative_return_graph**: 买入、卖出、持有股票的累积收益分析
- **score_ic_graph**: 预测得分与标签的 IC（信息系数）分析
- **risk_analysis_graph**: 风险分析，包括整体和月度风险指标
- **rank_label_graph**: 每日交易股票的排名百分比分析

## 子模块结构

```
analysis_position/
├── __init__.py              # 模块初始化，导出所有图表函数
├── report.py                # 回测报告图表
├── cumulative_return.py      # 累积收益图表
├── score_ic.py             # IC 分析图表
├── risk_analysis.py        # 风险分析图表
├── rank_label.py          # 排名标签图表
└── parse_position.py      # 持仓数据解析工具
```

## 核心函数详细说明

### 1. report_graph

**位置**: `analysis_position.report.report_graph`

**说明**: 显示回测报告图表，包含累积收益、最大回撤、超额收益、换手率等多个子图。

#### 函数签名

```python
def report_graph(
    report_df: pd.DataFrame,
    show_notebook: bool = True
) -> [list, tuple]:
```

#### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| report_df | pd.DataFrame | 必需 | 回测数据 |
| show_notebook | bool | True | 是否在 Notebook 中显示图表 |

#### report_df 数据格式要求

| 必需列 | 类型 | 说明 |
|--------|------|------|
| return | float | 每日收益率 |
| cost | float | 每日交易成本 |
| bench | float | 基准指数每日收益率 |
| turnover | float | 每日换手率 |

数据索引必须是日期类型。

**示例数据**:

```python
                            return      cost        bench       turnover
date
2017-01-04  0.003421    0.000864    0.011693    0.576325
2017-01-05  0.000508    0.000447    0.000721    0.227882
2017-01-06  -0.003321   0.000212    -0.004322   0.102765
```

#### 图表结构

生成的图表包含 7 个子图：

1. **累积收益对比**: 策略累积收益 vs 基准收益
2. **无成本回撤**: 不考虑交易成本的最大回撤
3. **含成本回撤**: 考虑交易成本的最大回撤
4. **超额收益（无成本）**: 策略收益减去基准收益
5. **超额收益（含成本）**: 策略收益减去基准收益和成本
6. **换手率**: 每日换手率
7. **超额收益回撤**: 超额收益的回撤分析

#### 使用示例

```python
import qlib
import pandas as pd
from qlib.utils.time import Freq
from qlib.backtest import backtest, executor
from qlib.contrib.strategy import TopkDropoutStrategy

# 初始化 Qlib
qlib.init(provider_uri='~/.qlib/qlib_data/cn_data', region='cn')

CSI300_BENCH = "SH000300"
FREQ = "day"

# 策略配置
STRATEGY_CONFIG = {
    "topk": 50,
    "n_drop": 5,
    "signal": pred_score,  # 预测分数
}

# 执行器配置
EXECUTOR_CONFIG = {
    "time_per_step": "day",
    "generate_portfolio_metrics": True,
}

# 回测配置
backtest_config = {
    "start_time": "2017-01-01",
    "end_time": "2020-08-01",
    "account": 100000000,
    "benchmark": CSI300_BENCH,
    "exchange_kwargs": {
        "freq": FREQ,
        "limit_threshold": 0.095,
        "deal_price": "close",
        "open_cost": 0.0005,
        "close_cost": 0.0015,
        "min_cost": 5,
    },
}

# 执行回测
strategy_obj = TopkDropoutStrategy(**STRATEGY_CONFIG)
executor_obj = executor.SimulatorExecutor(**EXECUTOR_CONFIG)
portfolio_metric_dict, indicator_dict = backtest(
    executor=executor_obj,
    strategy=strategy_obj,
    **backtest_config
)

# 获取报告数据
analysis_freq = "{0}{1}".format(*Freq.parse(FREQ))
report_normal_df, positions_normal = portfolio_metric_dict.get(analysis_freq)

# 显示报告图表
from qlib.contrib.report import analysis_position as ap
ap.report_graph(report_normal_df)

# 或返回图表对象
figures = ap.report_graph(report_normal_df, show_notebook=False)
```

---

### 2. cumulative_return_graph

**位置**: `analysis_position.cumulative_return.cumulative_return_graph`

**说明**: 分析买入、卖出和持有股票的累积收益，展示不同交易动作的盈利能力。

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
|------|------|--------|------|
| position | dict | 必需 | 持仓数据，回测结果 |
| report_normal | pd.DataFrame | 必需 | 报告数据，包含 return, cost, bench, turnover |
| label_data | pd.DataFrame | 必需 | 标签数据，包含 label 列 |
| show_notebook | bool | True | 是否在 Notebook 中显示 |
| start_date | str | None | 开始日期 |
| end_date | str | None | 结束日期 |

#### label_data 数据格式要求

**重要**: 标签 T 是从 T 到 T+1 的变化，建议使用 close 价格计算。

| 必需列 | 类型 | 说明 |
|--------|------|------|
| label | float | 下一期收益率，如 Ref($close, -1)/$close - 1 |

索引必须是 MultiIndex，包含 instrument 和 datetime。

**示例数据**:

```python
                                                label
instrument  datetime
SH600004        2017-12-11  -0.013502
                2017-12-12  -0.072367
                2017-12-13  -0.068605
```

#### 图表说明

生成 4 组图表（buy, sell, buy_minus_sell, hold），每组包含：

- **累积收益线图**: 每日平均收益的累积
- **权重柱状图**: 每日交易的总权重
- **收益直方图**: 每日收益分布（红色线表示平均值）

**坐标轴说明**:
- X 轴：交易日
- Y 轴上方：`(((Ref($close, -1)/$close - 1) * weight).sum() / weight.sum()).cumsum()`
- Y 轴下方：每日权重总和
- sell 图中 y < 0 表示盈利，其他情况 y > 0 表示盈利
- buy_minus_sell 图中，weight 的 y 值是 buy_weight + sell_weight

#### 使用示例

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
ap.cumulative_return_graph(
    positions,
    report_normal_df,
    features_df
)

# 或返回图表对象
figures = ap.cumulative_return_graph(
    positions,
    report_normal_df,
    features_df,
    show_notebook=False
)
```

---

### 3. score_ic_graph

**位置**: `analysis_position.score_ic.score_ic_graph`

**说明**: 计算并展示预测得分与标签的 IC（信息系数）和 Rank IC。

#### 函数签名

```python
def score_ic_graph(
    pred_label: pd.DataFrame,
    show_notebook: bool = True,
    **kwargs
) -> [list, tuple]:
```

#### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| pred_label | pd.DataFrame | 必需 | 预测得分和标签数据 |
| show_notebook | bool | True | 是否在 Notebook 中显示 |
| **kwargs | - | - | 其他参数，如 rangebreaks |

#### pred_label 数据格式要求

| 必需列 | | | 说明 |
|--------|-|-|------|
| score | float | | 预测得分 |
| label | float | | 真实标签值 |

索引必须是 MultiIndex，包含 instrument 和 datetime。

**示例数据**:

```python
instrument  datetime        score         label
SH600004  2017-12-11    0.123         -0.013502
          2017-12-12   -0.456         -0.072367
          2017-12-13    0.789         -0.068605
```

#### IC 指标说明

- **IC (Information Coefficient)**: Pearson 相关系数，衡量预测值与真实值的线性关系
- **Rank IC**: Spearman 相关系数，衡量预测值排序与真实值排序的一致性

#### 使用示例

```python
from qlib.data import D
from qlib.contrib.report import analysis_position as ap

# 获取预测数据
pred_df_dates = pred_df.index.get_level_values(level='datetime')

# 计算标签（未来收益率）
features_df = D.features(
    D.instruments('csi500'),
    ['Ref($close, -2)/Ref($close, -1) - 1'],
    pred_df_dates.min(),
    pred_df_dates.max()
)
features_df.columns = ['label']

# 合并预测得分和标签
pred_label = pd.concat(
    [features_df, pred],
    axis=1,
    sort=True
).reindex(features_df.index)

# 显示 IC 图表
ap.score_ic_graph(pred_label)

# 或返回图表对象
figures = ap.score_ic_graph(pred_label, show_notebook=False)
```

---

### 4. risk_analysis_graph

**位置**: `analysis_position.risk_analysis.risk_analysis_graph`

**说明**: 生成风险分析图表，包括整体风险指标和月度风险趋势。

#### 函数签名

```python
def risk_analysis_graph(
    analysis_df: pd.DataFrame = None,
    report_normal_df: pd.DataFrame = None,
    report_long_short_df: pd.DataFrame = None,
    show_notebook: bool = True
) -> Iterable[py.Figure]:
```

#### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| analysis_df | pd.DataFrame | None | 风险分析数据 |
| report_normal_df | pd.DataFrame | None | 报告数据，用于月度分析 |
| report_long_short_df | pd.DataFrame | None | 多空报告数据 |
| show_notebook | bool | True | 是否在 Notebook 中显示 |

#### analysis_df 数据格式

索引是 MultiIndex，columns 名称为 ['risk']。

**示例数据**:

```python
                                                          risk
excess_return_without_cost mean               0.000692
                           std                0.005374
                           annualized_return  0.174495
                           information_ratio  2.045576
                           max_drawdown      -0.079103
excess_return_with_cost    mean               0.000499
                           std                0.005372
                           annualized_return  0.125625
                           information_ratio  1.473152
                           max_drawdown      -0.088263
```

#### 图表内容

1. **整体风险指标柱状图**: 年化收益、最大回撤、信息比率、标准差
2. **月度风险趋势图**: 年化收益、最大回撤、信息比率、标准差的月度变化

#### 使用示例

```python
import qlib
from qlib.utils.time import Freq
from qlib.backtest import backtest, executor
from qlib.contrib.evaluate import risk_analysis
from qlib.contrib.strategy import TopkDropoutStrategy
from qlib.contrib.report import analysis_position as ap

# 执行回测（参考 report_graph 示例）
# ... 回测代码 ...

# 计算风险指标
analysis_freq = "{0}{1}".format(*Freq.parse(FREQ))
report_normal_df, positions_normal = portfolio_metric_dict.get(analysis_freq)

analysis = dict()
analysis["excess_return_without_cost"] = risk_analysis(
    report_normal_df["return"] - report_normal_df["bench"],
    freq=analysis_freq
)
analysis["excess_return_with_cost"] = risk_analysis(
    report_normal_df["return"] - report_normal_df["bench"] - report_normal_df["cost"],
    freq=analysis_freq
)

analysis_df = pd.concat(analysis)

# 显示风险分析图表
ap.risk_analysis_graph(analysis_df, report_normal_df)

# 或返回图表对象
figures = ap.risk_analysis_graph(
    analysis_df,
    report_normal_df,
    show_notebook=False
)
```

---

### 5. rank_label_graph

**位置**: `analysis_position.rank_label.rank_label_graph`

**说明**: 分析每日买入、卖出、持有股票在所有股票中的排名百分比。

#### 函数签名

```python
def rank_label_graph(
    position: dict,
    label_data: pd.DataFrame,
    start_date: str = None,
    end_date: str = None,
    show_notebook: bool = True
) -> Iterable[go.Figure]:
```

#### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| position | dict | 必需 | 持仓数据 |
| label_data | pd.DataFrame | 必需 | 标签数据 |
| start_date | str | None | 开始日期 |
| end_date | str | None | 结束日期 |
| show_notebook | bool | True | 是否在 Notebook 中显示 |

#### rank_label 说明

**计算方式**: `sell_df['label'].rank(ascending=False) / len(sell_df)`

- **0%**: 标签值最大的股票
- **100%**: 标签值最小的股票
- **理想情况**:
  - Buy: 接近 0%（买入表现最好的股票）
  - Sell: 接近 100%（卖出表现最差的股票）
  - Hold: 中间值（持有表现中等的股票）

#### 使用示例

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
    'n_drop': 230
}
strategy = TopkDropoutStrategy(**sparas)

# 执行回测
_, positions = backtest(pred_df, strategy, **bparas)

# 准备标签数据
pred_df_dates = pred_df.index.get_level_values(level='datetime')
features_df = D.features(
    D.instruments('csi500'),
    ['Ref($close, -1)/$close - 1'],
    pred_df_dates.min(),
    pred_df_dates.max()
)
features_df.columns = ['label']

# 显示排名标签图表
ap.rank_label_graph(
    positions,
    features_df,
    pred_df_dates.min(),
    pred_df_dates.max()
)

# 或返回图表对象
figures = ap.rank_label_graph(
    positions,
    features_df,
    pred_df_dates.min(),
    pred_df_dates.max(),
    show_notebook=False
)
```

---

## 辅助工具函数

### parse_position

**位置**: `analysis_position.parse_position.parse_position`

**说明**: 将持仓字典转换为 DataFrame 格式，并标注交易状态。

#### 函数签名

```python
def parse_position(position: dict = None) -> pd.DataFrame:
```

#### 返回数据格式

| 列名 | 类型 | 说明 |
|------|------|------|
| amount | float | 持仓数量 |
| cash | float | 现金余额 |
| count | int | 持仓次数 |
| price | float | 持仓价格 |
| status | int | {0: 持有, -1: 卖出, 1: 买入} |
| weight | float | 权重 |

索引: MultiIndex [instrument, datetime]

#### 使用示例

```python
from qlib.contrib.report.analysis_position import parse_position

# 解析持仓数据
position_df = parse_position(positions)
print(position_df.head())
```

### get_position_data

**位置**: `analysis_position.parse_position.get_position_data`

**说明**: 整合持仓数据与标签/报告数据。

#### 函数签名

```python
def get_position_data(
    position: dict,
    label_data: pd.DataFrame,
    report_normal: pd.DataFrame = None,
    calculate_label_rank: bool = False,
    start_date: str = None,
    end_date: str = None
) -> pd.DataFrame:
```

## 完整工作流程示例

```python
import qlib
import pandas as pd
from qlib.data import D
from qlib.utils.time import Freq
from qlib.backtest import backtest, executor
from qlib.contrib.evaluate import risk_analysis
from qlib.contrib.strategy import TopkDropoutStrategy
from qlib.contrib.report import analysis_position as ap

# 1. 初始化 Qlib
qlib.init(provider_uri='~/.qlib/qlib_data/cn_data', region='cn')

# 2. 准备数据
instruments = D.instruments('csi500')
fields = [
    'Ref($close, -1)/$close - 1',  # 标签：未来收益率
]
dates = pd.date_range('2017-01-01', '2020-12-31')
data = D.features(instruments, fields, dates[0], dates[-1])

# 3. 假设有预测分数 pred_score
# ... 获取预测分数 ...

# 4. 配置策略
STRATEGY_CONFIG = {
    "topk": 50,
    "n_drop": 5,
    "signal": pred_score,
}

EXECUTOR_CONFIG = {
    "time_per_step": "day",
    "generate_portfolio_metrics": True,
}

backtest_config = {
    "start_time": "2017-01-01",
    "end_time": "2020-08-01",
    "account": 100000000,
    "benchmark": "SH000300",
    "exchange_kwargs": {
        "freq": "day",
        "limit_threshold": 0.095,
        "deal_price": "close",
        "open_cost": 0.0005,
        "close_cost": 0.0015,
        "min_cost": 5,
    },
}

# 5. 执行回测
strategy_obj = TopkDropoutStrategy(**STRATEGY_CONFIG)
executor_obj = executor.SimulatorExecutor(**EXECUTOR_CONFIG)
portfolio_metric_dict, indicator_dict = backtest(
    executor=executor_obj,
    strategy=strategy_obj,
    **backtest_config
)

# 6. 获取报告数据
analysis_freq = "{0}{1}".format(*Freq.parse("day"))
report_normal_df, positions = portfolio_metric_dict.get(analysis_freq)

# 7. 生成各种报告图表

# 回测报告
ap.report_graph(report_normal_df)

# 风险分析
analysis = {
    "excess_return_without_cost": risk_analysis(
        report_normal_df["return"] - report_normal_df["bench"],
        freq=analysis_freq
    ),
    "excess_return_with_cost": risk_analysis(
        report_normal_df["return"] - report_normal_df["bench"] - report_normal_df["cost"],
        freq=analysis_freq
    )
}
analysis_df = pd.concat(analysis)
ap.risk_analysis_graph(analysis_df, report_normal_df)

# 累积收益分析
ap.cumulative_return_graph(positions, report_normal_df, data)

# 排名标签分析
ap.rank_label_graph(positions, data)

# IC 分析
pred_label = pd.concat([data, pred_score], axis=1, sort=True).reindex(data.index)
pred_label.columns = ['label', 'score']
ap.score_ic_graph(pred_label)
```

## 最佳实践

1. **数据准备**: 确保标签数据使用正确的收益率计算方式（通常使用 Ref($close, -1)/$close - 1）
2. **日期对齐**: 确保所有数据的日期范围和频率一致
3. **回测配置**: 根据实际需求调整交易成本、限制阈值等参数
4. **图表展示**: 在 Notebook 中使用默认设置，在脚本中设置 show_notebook=False 并保存图表
5. **风险分析**: 同时分析有成本和无成本的情况，评估交易成本的影响

## 常见问题

### Q: label_data 中的标签应该如何计算？

A: 标签 T 表示从 T 到 T+1 的变化。最常见的做法是：
```
label = Ref($close, -1) / $close - 1
```
这表示当前时刻的 close 价格相对下一时刻 close 的收益率。

### Q: 为什么累积收益图中 sell 的回撤 y < 0 表示盈利？

A: 因为卖出时，如果股票下跌（负收益），意味着卖出是正确的决策，避免了损失，所以是盈利。其他情况下，正收益表示盈利。

### Q: IC 和 Rank IC 有什么区别？

A:
- IC（Pearson 相关系数）：衡量线性关系，对异常值敏感
- Rank IC（Spearman 相相关数）：衡量排序一致性，更稳健
- 通常 Rank IC 更适合评估因子选股效果

### Q: 如何自定义图表样式？

A: 可以通过返回图表对象然后修改：

```python
figures = ap.report_graph(report_normal_df, show_notebook=False)
fig = figures[0]
fig.update_layout(title='自定义标题')
fig.show()
```
