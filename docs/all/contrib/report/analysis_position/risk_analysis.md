# analysis_position/risk_analysis.py

## 模块概述

`qlib.contrib.report.analysis_position.risk_analysis.py` 提供了风险分析的功能，包括整体风险指标分析和月度风险趋势分析。该模块帮助评估策略的风险特征和收益质量。

## 核心函数

### risk_analysis_graph

**说明**: 生成风险分析图表，包括整体风险指标柱状图和月度风险趋势图。

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
| analysis_df | pd.DataFrame | None | 风险分析数据，整体风险指标 |
| report_normal_df | pd.DataFrame | None | 报告数据，用于月度分析 |
| report_long_short_df | pd.DataFrame | None | 多空报告数据（当前版本不支持） |
| show_notebook | bool | True | 是否在 Notebook 中显示 |

#### analysis_df 数据格式要求

**索引**: MultiIndex

**必需列**:

| 列名 | 类型 | 说明 |
|------|------|------|
| risk | float | 风险指标值 |

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

**包含的风险指标**:

| 指标 | 英文 | 中文 | 说明 |
|------|------|------|------|
| mean | mean | 均值 | 平均收益率 |
| std | std | 标准差 | 收益波动性 |
| annualized_return | annualized_return | 年化收益率 | 按年化的平均收益 |
| information_ratio | information_ratio | 信息比率 | 风险调整后收益 |
| max_drawdown | max_drawdown | 最大回撤 | 从高点到低点的最大跌幅 |

#### report_normal_df 数据格式要求

| 必需列 | | | 说明 |
|--------|-|-|------|
| return | float | | 每日收益率 |
| cost | float | | 每日交易成本 |
| bench | float | | 基准指数收益率 |

索引为日期时间类型。

#### 图表结构

生成两类图表：

1. **整体风险指标柱状图**: 显示年化收益、最大回撤、信息比率、标准差等指标
2. **月度风险趋势图**: 显示年化收益、最大回撤、信息比率、标准差的月度变化

---

## 辅助函数

### _get_risk_analysis_data_with_report

**说明**: 获取带有报告数据的风险分析数据。

#### 函数签名

```python
def _get_risk_analysis_data_with_report(
    report_normal_df: pd.DataFrame,
    date: pd.Timestamp
) -> pd.DataFrame:
```

#### 返回值

包含风险分析结果的 DataFrame。

---

### _get_all_risk_analysis

**说明**: 将风险分析数据转换为标准格式。

#### 函数签名

```python
def _get_all_risk_analysis(risk_df: pd.DataFrame) -> pd.DataFrame:
```

#### 返回值

转换后的风险指标 DataFrame，不包含 mean 列。

---

### _get_monthly_risk_analysis_with_report

**说明**: 获取月度风险分析数据。

#### 函数签名

```python
def _get_monthly_risk_analysis_with_report(
    report_normal_df: pd.DataFrame
) -> pd.DataFrame:
```

#### 计算逻辑

1. 按月分组报告数据
2. 对每个月计算风险指标
3. 将数据对齐到月末

#### 返回值

包含月度风险指标的 DataFrame。

---

### _get_monthly_analysis_with_feature

**说明**: 获取特定特征的月度分析数据。

#### 函数签名

```python
def _get_monthly_analysis_with_feature(
    monthly_df: pd.DataFrame,
    feature: str = "annualized_return"
) -> pd.DataFrame:
```

#### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| monthly_df | pd.DataFrame | 必需 | 月度风险分析数据 |
| feature | str | "annualized_return" | 要提取的特征 |

#### 返回值

按月份组织的特征数据 DataFrame。

---

## 使用示例

### 示例 1: 基础风险分析

```python
import qlib
import pandas as pd
from qlib.utils.time import Freq
from qlib.backtest import backtest, executor
from qlib.contrib.evaluate import risk_analysis
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
analysis_freq = "{0}{1}".format(*Freq.parse("day"))
report_normal_df, positions_normal = portfolio_metric_dict.get(analysis_freq)

# 计算风险指标
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
```

### 示例 2: 只显示整体风险指标

```python
# 只提供 analysis_df，不提供 report_normal_df
# 这样只会显示整体风险指标，不会显示月度趋势
ap.risk_analysis_graph(analysis_df=analysis_df)
```

### 示例 3: 返回图表对象

```python
# 返回图表对象而不是直接显示
figures = ap.risk_analysis_graph(
    analysis_df=analysis_df,
    report_normal_df=report_normal_df,
    show_notebook=False
)

# 遍历所有图表
for i, fig in enumerate(figures):
    print(f"图表 {i+1}:")
    fig.show()
```

### 示例 4: 对比多个策略的风险

```python
# 假设有多个策略的风险分析结果
strategy_risks = {
    'strategy_1': (analysis_df_1, report_df_1),
    'strategy_2': (analysis_df_2, report_df_2),
    'strategy_3': (analysis_df_3, report_df_3),
}

for name, (analysis_df, report_df) in strategy_risks.items():
    print(f"\n策略: {name}")
    ap.risk_analysis_graph(analysis_df, report_df)
```

### 示例 5: 自定义风险指标计算

```python
from qlib.contrib.evaluate import risk_analysis

# 计算策略收益的风险指标
strategy_return = report_normal_df["return"]
strategy_risk = risk_analysis(strategy_return, freq="day")

# 计算基准收益的风险指标
bench_return = report_normal_df["bench"]
bench_risk = risk_analysis(bench_return, freq="day")

# 计算超额收益的风险指标
excess_return_wo_cost = report_normal_df["return"] - report_normal_df["bench"]
excess_risk_wo_cost = risk_analysis(excess_return_wo_cost, freq="day")

excess_return_w_cost = report_normal_df["return"] - report_normal_df["bench"] - report_normal_df["cost"]
excess_risk_w_cost = risk_analysis(excess_return_w_cost, freq="day")

# 合并所有风险指标
all_risks = {
    'strategy': strategy_risk,
    'benchmark': bench_risk,
    'excess_wo_cost': excess_risk_wo_cost,
    'excess_w_cost': excess_risk_w_cost
}

analysis_df = pd.concat(all_risks)

# 显示风险分析
ap.risk_analysis_graph(analysis_df, report_normal_df)
```

---

## 风险指标解读

### 年化收益率 (Annualized Return)

**说明**: 将平均收益率按年化计算。

**计算公式**: `annualized_return = mean_return * 252`

**评估标准**:

| 年化收益率 | 评级 |
|-----------|------|
| > 20% | 优秀 |
| 10%-20% | 良好 |
| 5%-10% | 一般 |
| < 5% | 较差 |

### 最大回撤 (Maximum Drawdown)

**说明**: 从历史高点到随后的最低点的最大跌幅。

**计算公式**: `mdd = (cummax - value) / cummax`

**评估标准**:

| 最大回撤 | 评级 |
|---------|------|
| < -10% | 低风险 |
| -10% ~ -15% | 中低风险 |
| -15% ~ -25% | 中高风险 |
| > -25% | 高风险 |

### 标准差 (Standard Deviation)

**说明**: 收益率的标准差，衡量波动性。

**评估标准**:

| 标准差 | 评级 |
|-------|------|
| < 1.0% | 低波动 |
| 1.0%-1.5% | 中低波动 |
| 1.5%-2.0% | 中高波动 |
| > 2.0% | 高波动 |

### 信息比率 (Information Ratio)

**说明**: 风险调整后的收益指标。

**计算公式**: `IR = (mean_return - risk_free_rate) / std_return`

**评估标准**:

| 信息比率 | 评级 |
|---------|------|
| > 2.0 | 优秀 |
| 1.5-2.0 | 赛好 |
| 1.0-1.5 | 一般 |
| < 1.0 | 较差 |

---

## 月度风险分析

### 月度指标说明

月度风险分析展示以下指标的月度变化：

1. **年化收益率**: 每个月的年化收益率
2. **最大回撤**: 每个月的最大回撤
3. **信息比率**: 每个月的信息比率
4. **标准差**: 每个月的收益波动性

### 如何解读月度图表

#### 年化收益率月度图

- **持续为正**: 每个月都盈利
- **波动较大**: 收益不稳定
- **季节性明显**: 存在季节性模式

#### 最大回撤月度图

- **值越小**: 月内回撤越大
- **波动大**: 风险不稳定
- **逐渐改善**: 风险管理能力提升

#### 信息比率月度图

- **持续 > 1**: 风险调整后收益持续良好
- **波动大**: 收益质量不稳定
- **趋势向上**: 风险调整能力提升

#### 标准差月度图

- **值小**: 月内波动小
- **值大**: 月内波动大
- **趋势**: 判断波动性的变化趋势

---

## 综合风险评估

### 风险收益比评估

```python
def evaluate_risk_return(analysis_df):
    """评估风险收益比"""
    # 提取关键指标
    annual_return = analysis_df.loc[('excess_return_without_cost', 'annualized_return'), 'risk']
    max_drawdown = analysis_df.loc[('excess_return_without_cost', 'max_drawdown'), 'risk']
    ir = analysis_df.loc[('excess_return_without_cost', 'information_ratio'), 'risk']

    # 计算风险收益比
    risk_return_ratio = annual_return / abs(max_drawdown)

    print(f"年化收益率: {annual_return:.2%}")
    print(f"最大回撤: {max_drawdown:.2%}")
    print(f"信息比率: {ir:.2f}")
    print(f"风险收益比: {risk_return_ratio:.2f}")

    # 评估
    if risk_return_ratio > 1.5:
        print("评级: 优秀")
    elif risk_return_ratio > 1.0:
        print("评级: 良好")
    elif risk_return_ratio > 0.5:
        print("评级: 一般")
    else:
        print("评级: 较差")

    return risk_return_ratio

# 使用
evaluate_risk_return(analysis_df)
```

### 成本影响评估

```python
def evaluate_cost_impact(analysis_df):
    """评估交易成本的影响"""
    # 无成本指标
    ann_ret_wo_cost = analysis_df.loc[('excess_return_without_cost', 'annualized_return'), 'risk']
    ir_wo_cost = analysis_df.loc[('excess_return_without_cost', 'information_ratio'), 'risk']

    # 有成本指标
    ann_ret_w_cost = analysis_df.loc[('excess_return_with_cost', 'annualized_return'), 'risk']
    ir_w_cost = analysis_df.loc[('excess_return_with_cost', 'information_ratio'), 'risk']

    # 计算影响
    ret_impact = ann_ret_w_cost - ann_ret_wo_cost
    ir_impact = ir_w_cost - ir_wo_cost

    print(f"年化收益率影响: {ret_impact:.2%}")
    print(f"信息比率影响: {ir_impact:.2f}")

    print(f"\n无成本年化收益率: {ann_ret_wo_cost:.2%}")
    print(f"有成本年化收益率: {ann_ret_w_cost:.2%}")
    print(f"\n无成本信息比率: {ir_wo_cost:.2f}")
    print(f"有成本信息比率: {ir_w_cost:.2f}")

    return ret_impact, ir_impact

# 使用
evaluate_cost_impact(analysis_df)
```

---

## 最佳实践

### 1. 定期风险监控

```python
import pandas as pd

# 按季度分析风险
quarters = pd.date_range(start_date, end_date, freq='Q')

for i in range(len(quarters) - 1):
    q_start = quarters[i]
    q_end = quarters[i+1] - pd.Timedelta(days=1)

    # 筛选该季度的数据
    q_report = report_normal_df.loc[q_start:q_end]

    # 计算风险指标
    q_analysis = {
        'excess_return': risk_analysis(
            q_report["return"] - q_report["bench"],
            freq="day"
        )
    }
    q_analysis_df = pd.concat(q_analysis)

    print(f"\n季度: {q_start} ~ {q_end}")
    ap.risk_analysis_graph(q_analysis_df, q_report)
```

### 2. 滚动风险分析

```python
def rolling_risk_analysis(report_df, window=60):
    """滚动窗口风险分析"""
    results = []

    for i in range(len(report_df) - window + 1):
        # 获取窗口数据
        window_df = report_df.iloc[i:i+window]

        # 计算风险指标
        excess_return = window_df["return"] - window_df["bench"]
        risk_metrics = risk_analysis(excess_return, freq="day")

        # 记录结果
        end_date = window_df.index[-1]
        results.append({
            'date': end_date,
            'annualized_return': risk_metrics['annualized_return'],
            'max_drawdown': risk_metrics['max_drawdown'],
            'information_ratio': risk_metrics['information_ratio'],
            'std': risk_metrics['std']
        })

    return pd.DataFrame(results).set_index('date')

# 使用
rolling_risks = rolling_risk_analysis(report_normal_df, window=60)
rolling_risks.plot(subplots=True, figsize=(12, 10))
```

### 3. 风险归因分析

```python
def risk_attribution_analysis(report_df):
    """风险归因分析"""
    # 分离不同来源的风险
    excess_return = report_df["return"] - report_df["bench"]

    # 计算各部分风险
    total_risk = risk_analysis(excess_return, freq="day")

    # 系统性风险（与基准相关的部分）
    systematic_risk = risk_analysis(
        excess_return * report_df["bench"],
        freq="day"
    )

    # 特异性风险（与基准无关的部分）
    # 这里简化处理，实际可能需要更复杂的方法

    print("风险归因:")
    print(f"总风险（年化）: {total_risk['annualized_return']:.2%}")
    print(f"系统性风险贡献: {systematic_risk['annualized_return']:.2%}")
    print(f"总风险（标准差）: {total_risk['std']:.4f}")
    print(f"系统性风险（标准差）: {systematic_risk['std']:.4f}")

# 使用
risk_attribution_analysis(report_normal_df)
```

---

## 常见问题

### Q: 为什么有两个分析结果（without_cost 和 with_cost）？

A: 为了评估交易成本的影响：
- `excess_return_without_cost`: 不考虑交易成本的超额收益
- `excess_return_with_cost`: 考虑交易成本后的超额收益

两者的差异反映了交易成本对策略表现的影响。

### Q: 月度分析有什么用？

A: 月度分析帮助识别：
1. **季节性模式**: 策略在特定月份的表现
2. **风险变化**: 风险特征的时序变化
3. **稳定性评估**: 策略的稳定性

### Q: 如何理解信息比率？

A: 信息比率衡量风险调整后的收益：
- IR > 2.0: 单位风险带来的收益很高
- IR = 1.0: 单位风险带来的收益等于风险
- IR < 1.0: 单位风险带来的收益低于风险

### Q: 最大回撤如何影响评估？

A: 最大回撤是重要的风险指标：
- **绝对值小**: 风险控制好
- **持续时间短**: 恢复快
- **频率低**: 策略稳定

### Q: 如何比较不同策略的风险？

A: 使用相同的时间窗口和基准：

```python
strategies = {
    'strategy_1': (analysis_df_1, report_df_1),
    'strategy_2': (analysis_df_2, report_df_2),
}

# 提取关键指标
comparison = pd.DataFrame({
    name: {
        '年化收益率': df.loc[('excess_return_without_cost', 'annualized_return'), 'risk'],
        '最大回撤': df.loc[('excess_return_without_cost', 'max_drawdown'), 'risk'],
        '信息比率': df.loc[('excess_return_without_cost', 'information_ratio'), 'risk'],
        '标准差': df.loc[('excess_return_without_cost', 'std'), 'risk']
    }
    for name, (df, _) in strategies.items()
})

print(comparison.T)
```

### Q: report_long_short_df 参数有什么用？

A: 该参数用于分析多空策略的风险，但当前版本不支持。未来的版本可能会添加对多空策略风险分析的支持。
