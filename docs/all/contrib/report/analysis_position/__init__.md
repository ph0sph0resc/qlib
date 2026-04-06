# analysis_position/__init__.py

## 模块概述

`qlib.contrib.report.analysis_position.__init__.py` 是持仓分析模块的初始化文件，导出了所有持仓分析相关的图表生成函数。

## 导出函数

```python
from .cumulative_return import cumulative_return_graph
from .score_ic import score_ic_graph
from .report import report_graph
from .rank_label import rank_label_graph
from .risk_analysis import risk_analysis_graph

__all__ = [
    "cumulative_return_graph",
    "score_ic_graph",
    "report_graph",
    "rank_label_graph",
    "risk_analysis_graph"
]
```

## 导出函数说明

### cumulative_return_graph

**位置**: `analysis_position.cumulative_return.cumulative_return_graph`

**说明**: 分析买入、卖出和持有股票的累积收益，展示不同交易动作的盈利能力。

**主要用途**:
- 评估策略在不同交易动作下的表现
- 识别买入、卖出、持有决策的优劣
- 分析策略的选股能力

### score_ic_graph

**位置**: `analysis_position.score_ic.score_ic_graph`

**说明**: 计算并展示预测得分与标签的 IC（信息系数）和 Rank IC。

**主要用途**:
- 评估预测模型的准确性
- 分析 IC 的时序变化
- 识别模型的稳定性

### report_graph

**位置**: `analysis_position.report.report_graph`

**说明**: 生成回测报告图表，包含累积收益、最大回撤、超额收益、换手率等多个子图。

**主要用途**:
- 全面展示回测结果
- 对比策略收益与基准收益
- 分析交易成本的影响

### rank_label_graph

**位置**: `analysis_position.rank_label.rank_label_graph`

**说明**: 分析每日买入、卖出、持有股票在所有股票中的排名百分比。

**主要用途**:
- 评估策略的选股能力
- 检查策略是否买入表现好的股票
- 检查策略是否卖出表现差的股票

### risk_analysis_graph

**位置**: `analysis_position.risk_analysis.risk_analysis_graph`

**说明**: 生成风险分析图表，包括整体风险指标和月度风险趋势。

**主要用途**:
- 分析策略的风险特征
- 评估收益风险比
- 监控风险指标的时间变化

## 使用示例

### 基础导入

```python
from qlib.contrib.report import analysis_position as ap
```

### 导入所有函数

```python
from qlib.contrib.report.analysis_position import (
    cumulative_return_graph,
    score_ic_graph,
    report_graph,
    rank_label_graph,
    risk_analysis_graph
)
```

### 完整分析流程

```python
import qlib
import pandas as pd
from qlib.data import D
from qlib.utils.time import Freq
from qlib.backtest import backtest, executor
from qlib.contrib.evaluate import risk_analysis
from qlib.contrib.strategy import TopkDropoutStrategy
from qlib.contrib.report import analysis_position as ap

# 初始化 Qlib
qlib.init(provider_uri='~/.qlib/qlib_data/cn_data', region='cn')

# 准备数据
# ... (准备预测分数 pred_score) ...

# 配置策略
STRATEGY_CONFIG = {
    "topk": 50,
    "n_drop": 5,
    "signal": pred_score,
}

EXECUTEOR_CONFIG = {
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

# 执行回测
strategy_obj = TopkDropoutStrategy(**STRATEGY_CONFIG)
executor_obj = executor.SimulatorExecutor(**EXECUTEOR_CONFIG)
portfolio_metric_dict, indicator_dict = backtest(
    executor=executor_obj,
    strategy=strategy_obj,
    **backtest_config
)

# 获取报告数据
analysis_freq = "{0}{1}".format(*Freq.parse("day"))
report_normal_df, positions = portfolio_metric_dict.get(analysis_freq)

# 准备标签数据
pred_df_dates = pred_score.index.get_level_values(level='datetime')
features_df = D.features(
    D.instruments('csi500'),
    ['Ref($close, -1)/$close - 1'],
    pred_df_dates.min(),
    pred_df_dates.max()
)
features_df.columns = ['label']

# 生成所有分析图表

# 1. 回测报告
print("=== 回测报告 ===")
ap.report_graph(report_normal_df)

# 2. 风险分析
print("\n=== 风险分析 ===")
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

# 3. 累积收益分析
print("\n=== 累积收益分析 ===")
ap.cumulative_return_graph(positions, report_normal_df, features_df)

# 4. 排名标签分析
print("\n=== 排名标签分析 ===")
ap.rank_label_graph(positions, features_df)

# 5. IC 分析
print("\n=== IC 分析 ===")
pred_label = pd.concat([features_df, pred_score], axis=1, sort=True)
pred_label.columns = ['label', 'score']
ap.score_ic_graph(pred_label)
```

## 函数快速参考

| 函数名 |主要参数 | 主要输出 |
|---------|---------|---------|
| report_graph | report_df | 累积收益、回撤、超额收益、换手率图表 |
| cumulative_return_graph | position, report_normal, label_data | 买入、卖出、持有的累积收益图表 |
| score_ic_graph | pred_label | IC 和 Rank IC 时序图 |
| risk_analysis_graph | analysis_df, report_normal_df | 风险指标柱状图和月度趋势图 |
| rank_label_graph | position, label_data | 买入、卖出、持有的排名百分比图 |

## 常见使用场景

### 场景 1: 快速评估策略表现

```python
# 只生成回测报告
ap.report_graph(report_normal_df)
```

### 场景 2: 深入分析交易决策

```python
# 分析买入、卖出、持有的累积收益
ap.cumulative_return_graph(positions, report_normal_df, label_data)

# 分析买入、卖出、持有的排名
ap.rank_label_graph(positions, label_data)
```

### 场景 3: 模型预测能力评估

```python
# 分析 IC
ap.score_ic_graph(pred_label)

# 分析风险指标
ap.risk_analysis_graph(analysis_df, report_normal_df)
```

### 场景 4: 完整的策略评估报告

```python
# 生成所有图表
ap.report_graph(report_normal_df)
ap.risk_analysis_graph(analysis_df, report_normal_df)
ap.cumulative_return_graph(positions, report_normal_df, label_data)
ap.rank_label_graph(positions, label_data)
ap.score_ic_graph(pred_label)
```

## 注意事项

1. **数据对齐**: 确保所有输入数据的日期范围和频率一致
2. **标签计算**: label_data 中的标签应该是未来收益率
3. **图表显示**: 在脚本中使用时，设置 `show_notebook=False` 并手动处理返回的图表
4. **性能考虑**: 对于大量数据，可以考虑使用抽样或时间窗口分析
