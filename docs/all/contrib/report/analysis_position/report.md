# analysis_position/report.py

## 模块概述

`qlib.contrib.report.analysis_position.report.py` 提供了生成回测报告图表的核心功能。该模块生成的图表包含累积收益、最大回撤、超额收益、换手率等多个子图，全面展示回测结果。

## 核心函数

### report_graph

**说明**: 显示回测报告图表，展示策略的各项绩效指标。

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

**必需列**:

| 列名 | 类型 | 说明 |
|------|------|------|
| return | float | 每日收益率 |
| cost | float | 每日交易成本 |
| bench | float | 基准指数每日收益率 |
| turnover | float | 每日换手率 |

**数据示例**:

```python
                            return      cost        bench       turnover
date
2017-01-04  0.003421    0.000864    0.011693    0.576325
2017-01-05  0.000508    0.000447    0.000721    0.227882
2017-01-06  -0.003321   0.000212    -0.004322   0.102765
2017-01-09  0.006753    0.000212    0.006874    0.105864
2017-01-10  -0.000416   0.000440    -0.003350   0.208396
```

**要求**:
- 索引名称必须是 "date"
- 索引类型应该是日期时间类型

#### 图表结构

生成的图表包含 7 个子图，采用 7 行 1 列的布局：

| 子图位置 | 内容 | 说明 |
|---------|------|------|
| 第 1 行 | cum_bench, cum_return_wo_cost, cum_return_w_cost | 累积收益对比 |
| 第 2 行 | return_wo_mdd | 不考虑成本的最大回撤 |
| 第 3 行 | return_w_cost_mdd | 考虑成本的最大回撤 |
| 第 4 行 | cum_ex_return_wo_cost, cum_ex_return_w_cost | 超额收益（无成本和有成本） |
| 第 5 行 | turnover | 每日换手率 |
| 第 6 行 | cum_ex_return_w_cost_mdd | 超额收益回撤（有成本） |
| 第 7 行 | cum_ex_return_wo_cost_mdd | 超额收益回撤（无成本） |

#### 图表详细说明

##### 子图 1: 累积收益对比

- **cum_bench**: 基准收益的累积
- **cum_return_wo_cost**: 策略收益的累积（不考虑成本）
- **cum_return_w_cost**: 策略收益的累积（考虑成本）

**用途**: 对比策略与基准的表现，评估成本的影响

。

##### 子图 2: 无成本最大回撤

- **return_wo_mdd**: 累积收益（无成本）相对于历史高点的回撤

**计算公式**: `return_wo_mdd = cum_return_wo_cost - cum_return_wo_cost.cummax()`

**用途**: 评估不考虑成本时的最大回撤

##### 子图 3: 含成本最大回撤

- **return_w_cost_mdd**: 累积收益（含成本）相对于历史高点的回撤

**计算公式**: `return_w_cost_mdd = (return - cost).cumsum() - ((return - cost).cumsum()).cummax()`

**用途**: 评估考虑成本时的最大回撤，更贴近实际交易

##### 子图 4: 超额收益（无成本和有成本）

- **cum_ex_return_wo_cost**: 策略收益减去基准收益的累积（无成本）
- **cum_ex_return_w_cost**: 策略收益减去基准收益和成本的累积

**计算公式**:
```python
cum_ex_return_wo_cost = (return - bench).cumsum()
cum_ex_return_w_cost = (return - bench - cost).cumsum()
```

**用途**: 评估策略相对于基准的超额收益

##### 子图 5: 换手率

- **turnover**: 每日换手率

**用途**: 评估策略的交易频率，识别高换手策略

##### 子图 6: 超额收益回撤（有成本）

- **cum_ex_return_w_cost_mdd**: 超额收益（含成本）的回撤

**用途**: 评估超额收益的风险

##### 子图 7: 超额收益回撤（无成本）

- **cum_ex_return_wo_cost_mdd**: 超额收益（无成本）的回撤

**用途**: 评估不考虑成本时的超额收益风险

#### 特殊标记

图表中使用灰色矩形标记两个最大回撤期间：

1. **整体最大回撤期间**（上半部分灰色区域）
   - 从累积收益的历史高点
   - 到随后的最低点

2. **超额收益最大回撤期间**（下半部分灰色区域）
   - 从超额收益的历史高点
   - 到随后的最低点

#### 返回值

- 如果 `show_notebook=True`，在 Notebook 中显示图表
- 如果 `show_notebook=False`，返回包含 plotly Figure 对象的列表

---

## 辅助函数

### _calculate_maximum

**说明**: 计算最大回撤的开始和结束日期。

#### 函数签名

```python
def _calculate_maximum(
    df: pd.DataFrame,
    is_ex: bool = False
):
```

#### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| df | pd.DataFrame | 必需 | 包含累积收益的数据 |
| is_ex | bool | False | 是否为超额收益 |

#### 返回值

元组 `(start_date, end_date)`，表示最大回撤的开始和结束日期。

#### 计算逻辑

```python
if is_ex:
    # 超额收益的最大回撤
    end_date = df["cum_ex_return_wo_cost_mdd"].idxmin()
    start_date = df.loc[df.index <= end_date]["cum_ex_return_wo_cost"].idxmax()
else:
    # 整体收益的最大回撤
    end_date = df["return_wo_mdd"].idxmin()
    start_date = df.loc[df.index <= end_date]["cum_return_wo_cost"].idxmax()
```

---

### _calculate_mdd

**说明**: 计算最大回撤。

#### 函数签名

```python
def _calculate_mdd(series):
```

#### 参数说明

| 参数 | 类型 | 说明 |
|------|------|------|
| series | pd.Series | 累积收益序列 |

#### 返回值

回撤序列，每个点表示相对于历史高点的回撤。

#### 计算公式

```python
mdd = series - series.cummax()
```

---

### _calculate_report_data

**说明**: 计算报告所需的所有指标。

#### 函数签名

```python
def _calculate_report_data(df: pd.DataFrame) -> pd.DataFrame:
```

#### 参数说明

| 参数 | 类型 | 说明 |
|------|------|------|
| df | pd.DataFrame | 包含 return, cost, bench, turnover 的数据 |

#### 返回值

包含所有计算指标的 DataFrame。

#### 计算指标

| 指标 | 计算公式 | 说明 |
|------|---------|------|
| cum_bench | bench.cumsum() | 基准累积收益 |
| cum_return_wo_cost | return.cumsum() | 策略累积收益（无成本） |
| cum_return_w_cost | (return - cost).cumsum() | 策略累积收益（含成本） |
| return_wo_mdd | cum_return_wo_cost - cum_return_wo_cost.cummax() | 无成本回撤 |
| return_w_cost_mdd | cum_return_w_cost.cummax() - cum_return_w_cost | 含成本回撤 |
| cum_ex_return_wo_cost | (return - bench).cumsum() | 超额累积收益（无成本） |
| cum_ex_return_w_cost | (return - bench - cost).cumsum() | 超额累积收益（含成本） |
| cum_ex_return_wo_cost_mdd | 计算回撤 | 超额收益回撤（无成本） |
| cum_ex_return_w_cost_mdd | 计算回撤 | 超额收益回撤（含成本） |
| turnover | turnover | 换手率 |

---

### _report_figure

**说明**: 生成回测报告图表。

#### 函数签名

```python
def _report_figure(df: pd.DataFrame) -> [list, tuple]:
```

#### 参数说明

| 参数 | 类型 | 说明 |
|------|------|------|
| df | pd.DataFrame | 包含 return, cost, bench, turnover 的数据 |

#### 返回值

包含单个 plotly Figure 对象的列表。

#### 图表配置

**布局配置**:
- 高度: 1200
- 行宽比例: [1, 1, 1, 3, 1, 1, 3]
- 垂直间距: 0.01
- X 轴共享: True

**Y 轴配置**:
- 所有 Y 轴显示网格线和刻度标签
- X 轴仅在最后一个子图显示

**形状标记**:
- 灰色矩形标记最大回撤期间
- 上半部分：整体最大回撤
- 下半部分：超额收益最大回撤

---

## 使用示例

### 示例 1: 基础使用

```python
import qlib
import pandas as pd
from qlib.utils.time import Freq
from qlib.backtest import backtest, executor
from qlib.contrib.strategy import TopkDropoutStrategy
from qlib.contrib.report import analysis_position as ap

# 初始化 Qlib
qlib.init(provider_uri='~/.qlib/qlib_data/cn_data', region='cn')

# 配置策略
STRATEGY_CONFIG = {
    "topk": 50,
    "n_drop": 5,
    "signal": pred_score,  # 预测分数
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
        "limit_threshold": 0.095
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
analysis_freq = "{0}{1}".format(*Freq.parse("day"))
report_normal_df, positions_normal = portfolio_metric_dict.get(analysis_freq)

# 显示报告图表
ap.report_graph(report_normal_df)
```

### 示例 2: 返回图表对象

```python
# 返回图表对象而不是直接显示
figures = ap.report_graph(report_normal_df, show_notebook=False)

# 获取图表
fig = figures[0]

# 自定义图表样式
fig.update_layout(
    title='自定义回测报告',
    height=1500
)

# 显示图表
fig.show()
```

### 示例 3: 保存图表

```python
import os

# 返回图表对象
figures = ap.report_graph(report_normal_df, show_notebook=False)

# 保存为 HTML
output_dir = 'reports'
os.makedirs(output_dir, exist_ok=True)

fig = figures[0]
fig.write_html(os.path.join(output_dir, 'backtest_report.html'))
print("报告已保存到:", os.path.join(output_dir, 'backtest_report.html'))
```

### 示例 4: 批量生成多策略报告

```python
# 假设有多个策略
strategies = {
    'topk50_n_drop5': TopkDropoutStrategy(topk=50, n_drop=5, signal=pred_score),
    'topk30_n_drop3': TopkDropoutStrategy(topk=30, n_drop=3, signal=pred_score),
    'topk100_n_drop10': TopkDropoutStrategy(topk=100, n_drop=10, signal=pred_score),
}

results = {}

# 对每个策略执行回测
for name, strategy in strategies.items():
    portfolio_metric_dict, _ = backtest(
        executor=executor_obj,
        strategy=strategy,
        **backtest_config
    )
    analysis_freq = "{0}{1}".format(*Freq.parse("day"))
    report_df, _ = portfolio_metric_dict.get(analysis_freq)
    results[name] = report_df

# 为每个策略生成报告
for name, report_df in results.items():
    print(f"生成策略 {name} 的报告...")
    ap.report_graph(report_df)
```

---

## 图表解读指南

### 如何读取回测报告

#### 1. 评估整体表现（子图 1）

观察累积收益曲线：
- **策略收益 > 基准收益**: 策略跑赢市场
- **cum_return_wo_cost vs cum_return_w_cost**: 评估交易成本的影响
  - 两条线接近：成本影响小
  - 两条线差距大：成本影响大

#### 2. 评估风险（子图 2-3）

观察回撤曲线：
- **最大回撤值**: 曲线的最低点
  - < -20%: 高风险
  - -20% ~ -10%: 中等风险
  - > -10%: 低风险
- **回撤频率**: 曲线下降的次数
- **回撤持续时间**: 灰色区域的宽度

#### 3. 评估超额收益（子图 4）

观察超额收益曲线：
- **cum_ex_return_wo_cost**: 无成本的超额收益
- **cum_ex_return_w_cost**: 含成本的超额收益
- **理想情况**: 持续上涨

#### 4. 评估交易频率（子图 5）

观察换手率：
- **高换手率（> 0.8）**: 频繁调仓，成本高
- **中等换手率（0.3-0.8）**: 适中
- **低换手率（< 0.3）**: 持仓稳定

#### 5. 评估超额收益风险（子图 6-7）

观察超额收益回撤：
- **cum_ex_return_w_cost_mdd**: 含成本的超额收益回撤
- **cum_ex_return_wo_cost_mdd**: 无成本的超额收益回撤
- **理想情况**: 回撤小且回撤恢复快

### 常见指标评估标准

| 指标 | 优秀 | 良好 | 一般 | 较差 |
|------|------|------|------|------|
| 年化收益率 | > 20% | 10%-20% | 5%-10% | < 5% |
| 最大回撤 | < -10% | -10% ~ -15% | -15% ~ -25% | > -25% |
| 夏普比率 | > 2.0 | 1.5-2.0 | 1.0-1.5 | < 1.0 |
| 换手率 | 0.3-0.6 | 0.6-0.8 | 0.8-1.0 | > 1.0 |
| 超额收益 | > 15% | 10%-15% | 5%-10% | < 5% |

---

## 最佳实践

### 1. 数据准备

```python
# 确保 report_df 格式正确
required_columns = ['return', 'cost', 'bench', 'turnover']
assert all(col in report_df.columns for col in required_columns)

# 确保索引是日期类型
assert isinstance(report_df.index, pd.DatetimeIndex)
```

### 2. 对比多个策略

```python
# 使用相同的基准和配置，对比不同策略
figures = []

for name, report_df in strategy_results.items():
    fig_list = ap.report_graph(report_df, show_notebook=False)
    fig = fig_list[0]
    fig.update_layout(title=f'策略: {name}')
    figures.append(fig)

# 保存所有报告
for i, fig in enumerate(figures):
    fig.write_html(f'strategy_report_{i}.html')
```

### 3. 性能分析

```python
# 从报告中提取关键指标
report_data = _calculate_report_data(report_normal_df)

# 计算年化收益率
annual_return = report_data['cum_return_w_cost'].iloc[-1] / len(report_data) * 252

# 计算最大回撤
max_drawdown = report_data['return_w_cost_mdd'].min()

print(f"年化收益率: {annual_return:.2%}")
print(f"最大回撤: {max_drawdown:.2%}")
```

### 4. 自定义报告

```python
# 创建自定义的报告函数
def custom_report(report_df, title="回测报告"):
    fig_list = _report_figure(report_df.copy())
    fig = fig_list[0]

    # 自定义布局
    fig.update_layout(
        title=title,
        height=1400,
        font=dict(size=12),
        plot_bgcolor='white'
    )

    # 自定义颜色
    fig.update_traces(
        selector=dict(name='cum_return_wo_cost'),
        line=dict(color='blue', width=2)
    )

    return fig

# 使用自定义报告
fig = custom_report(report_normal_df, "Top50 策略回测报告")
fig.show()
```

---

## 常见问题

### Q: 为什么报告中有 7 个子图？

A: 每个子图展示不同的绩效维度：
1. 累积收益对比（整体表现）
2-3. 回撤分析（风险评估）
4. 超额收益（相对表现）
5. 换手率（交易成本）
6-7. 超额收益回撤（超额收益风险）

### Q: 如何理解灰色区域？

A: 灰色区域标记了最大回撤期间：
- 上半部分：策略整体收益的最大回撤
- 下半部分：策略相对基准的最大回撤

这些区域帮助快速识别策略表现最差的时期。

### Q: cum_return_wo_cost 和 cum_return_w_cost 哪个更重要？

A: 两个都很重要：
- **cum_return_wo_cost**: 评估策略本身的选股能力
- **cum_return_w_cost**: 评估考虑成本后的实际收益

两者的差距反映了交易成本的影响。

### Q: 如何处理数据缺失？

A: 确保 report_df 没有缺失值：

```python
# 检查缺失值
if report_df.isna().any().any():
    print("警告: 数据中存在缺失值")
    print(report_df.isna().sum())

    # 填充或删除缺失值
    report_df = report_df.fillna(method='ffill')
```

### Q: 如何在报告中添加自定义指标？

A: 可以扩展 report_df 添加新列：

```python
# 添加自定义指标
report_df['custom_indicator'] = report_df['return'] * report_df['turnover']

# 生成报告
ap.report_graph(report_df)
```

但需要注意，默认的报告图表只会显示预定义的指标。

### Q: 如何修改图表样式？

A: 通过返回图表对象然后修改：

```python
figures = ap.report_graph(report_normal_df, show_notebook=False)
fig = figures[0]

# 修改样式
fig.update_layout(
    template='plotly_dark',  # 使用暗色主题
    font=dict(family='Arial', size=14),
    margin=dict(l=50, r=50, t=80, b=50)
)

fig.show()
```
