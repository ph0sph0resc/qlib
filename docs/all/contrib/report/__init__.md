# __init__.py

## 模块概述

`qlib.contrib.report.__init__.py` 是 Qlib 报告模块的初始化文件，定义了报告功能中可以使用的图表名称列表。

## 常量定义

### GRAPH_NAME_LIST

```python
GRAPH_NAME_LIST = [
    "analysis_position.report_graph",
    "analysis_position.score_ic_graph",
    "analysis_position.cumulative_return_graph",
    "analysis_position.risk_analysis_graph",
    "analysis_position.rank_label_graph",
    "analysis_model.model_performance_graph",
]
```

**说明**: 报告模块可用的图表名称列表。

**包含的图表**:
- `analysis_position.report_graph`: 回测报告图表
- `analysis_position.score_ic_graph`: IC（信息系数）图表
- `analysis_position.cumulative_return_graph`: 累积收益图表
- `analysis_position.risk_analysis_graph`: 风险分析图表
- `analysis_position.rank_label_graph`: 排名标签图表
- `analysis_model.model_performance_graph`: 模型性能图表

## 使用示例

```python
from qlib.contrib.report import GRAPH_NAME_LIST

# 查看所有可用的图表名称
for graph_name in GRAPH_NAME_LIST:
    print(graph_name)
```

## 图表功能映射

| 图表名称 | 功能描述 | 所在模块 |
|---------|---------|---------|
| report_graph | 显示回测报告，包含收益、最大回撤、换手率等指标 | analysis_position |
| score_ic_graph | 显示预测得分与标签的IC值 | analysis_position |
| cumulative_return_graph | 显示买入、卖出和持有的累积收益 | analysis_position |
| risk_analysis_graph | 显示风险分析指标，包括月度分析 | analysis_position |
| rank_label_graph | 显示每日买入、卖出、持有股票的排名百分比 | analysis_position |
| model_performance_graph | 显示模型性能指标，包括分组收益、IC、自相关等 | analysis_model |
