# analysis_position/rank_label.py

## 模块概述

`qlib.contrib.report.analysis_position.rank_label.py` 提供了分析每日交易股票排名百分比的功能。该模块通过计算买入、卖出、持有股票在所有股票中的平均排名，评估策略的选股能力。

## 核心函数

### rank_label_graph

**说明**: 生成买入、卖出、持有股票的排名百分比图表，展示策略选股的时机把握能力。

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
| position | dict | 必需 | 持仓数据，回测结果 |
| label_data | pd.DataFrame | 必需 | 标签数据，包含 label 列 |
| start_date | str | None | 开始日期 |
| end_date | str | None | 结束日期 |
| show_notebook | bool | True | 是否在 Notebook 中显示 |

#### 数据格式要求

**position (持仓数据）**:
回测返回的持仓字典，包含每日的股票持仓信息。

**label_data (标签数据）**:

| 必需列 | | | 说明 |
|--------|-|-|------|
| label | float | | 下一期收益率 |

**重要**: 标签 T 是从 T 到 T+1 的变化，建议使用 `Ref($close, -1)/$close - 1` 计算。

索引必须是 MultiIndex，包含 instrument 和 datetime。

**示例数据**:

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

生成 3 个图表，分别对应 Buy、Sell、Hold 操作：

| 图表 | 说明 |
|------|------|
| Buy | 每日买入股票的平均排名百分比 |
| Sell | 每日卖出股票的平均排名百分比 |
| Hold | 每日持有股票的平均排名百分比 |

#### 坐标说明

- **X 轴**: 交易日
- **Y 轴**: label-rank-ratio (%)，标签排名百分比

#### 排名百分比说明

**计算方式**: `rank_ratio = label.rank(ascending=False) / len(label) * 100`

- **0%**: 标签值最大的股票（表现最好）
- **100%**: 标签值最小的股票（表现最差）
- **50%**: 中位数

**平均排名**: 每日某种操作（买入/卖出/持有）股票的平均 rank_ratio

#### 理想表现

| 操作 | 理想排名范围 | 说明 |
|------|------------|------|
| Buy | 0-20% | 买入排名靠前的股票（表现好） |
| Sell | 80-100% | 卖出排名靠后的股票（表现差） |
| Hold | 30-70% | 持有排名中等的股票 |

#### 返回值

- 如果 `show_notebook=True`，在 Notebook 中显示图表
- 如果 `show_notebook=False`，返回包含 plotly Figure 对象的迭代器

---

## 辅助函数

### _get_figure_with_position

**说明**: 生成排名分析图表。

#### 函数签名

```python
def _get_figure_with_position(
    position: dict,
    label_data: pd.DataFrame,
    start_date: str = None,
    end_date: str = None
) -> Iterable[go.Figure]:
```

#### 返回值

生成 3 个图表的迭代器，分别对应 Buy、Sell、Hold。

#### 计算逻辑

1. 解析持仓数据，计算标签排名
2. 按日期分组，计算每天每种操作的平均排名
3. 生成折线图展示排名变化

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
ap.rank_label_graph(positions, features_df)
```

### 示例 2: 指定日期范围

```python
import pandas as pd

# 指定分析的时间范围
start_date = '2018-01-01'
end_date = '2019-12-31'

ap.rank_label_graph(
    positions,
    features_df,
    start_date=start_date,
    end_date=end_date
)
```

### 示例 3: 返回图表对象

```python
# 返回图表对象
figures = ap.rank_label_graph(
    positions,
    features_df,
    show_notebook=False
)

# 遍历所有图表
names = ['Buy', 'Sell', 'Hold']
for name, fig in zip(names, figures):
    fig.update_layout(title=f'{name} 股票的排名百分比')
    fig.show()
```

### 示例 4: 保存图表

```python
import os

# 创建输出目录
output_dir = 'rank_label_reports'
os.makedirs(output_dir, exist_ok=True)

# 生成图表
figures = ap.rank_label_graph(
    positions,
    features_df,
    show_notebook=False
)

# 保存图表
names = ['buy', 'sell', 'hold']
for name, fig in zip(names, figures):
    output_path = os.path.join(output_dir, f'{name}_rank_label.html')
    fig.write_html(output_path)
    print(f"已保存: {output_path}")
```

### 示例 5: 对比多个策略

```python
# 假设有多个策略的结果
strategy_results = {
    'topk50_n_drop5': positions_1,
    'topk30_n_drop3': positions_2,
    'topk100_n_drop10': positions_3,
}

for name, pos in strategy_results.items():
    print(f"\n分析策略: {name}")
    ap.rank_label_graph(pos, features_df)
```

### 示例 6: 定期分析排名变化

```python
import pandas as pd

# 按月分析
months = pd.date_range(start_date, end_date, freq='MS')

for i in range(len(months) - 1):
    m_start = months[i]
    m_end = months[i+1] - pd.Timedelta(days=1)

    print(f"\n分析月份: {m_start} ~ {m_end}")
    ap.rank_label_graph(
        positions,
        features_df,
        start_date=m_start,
        end_date=m_end
    )
```

---

## 图表解读指南

### 如何解读 Buy 图表

#### 理想表现

- **接近 0%**: 持续买入表现最好的股票
- **稳定在 0-20%**: 买入策略优秀
- **持续上升**: 选股能力下降
- **持续下降**: 选股能力提升



#### 可能的问题

- **平均排名 > 50%**: 买入表现较差的股票，选股逻辑可能有问题
- **波动很大**: 选股标准不稳定
- **趋势向上**: 策略在后期表现变差

#### 改进建议

如果 Buy 平均排名过高（> 40%）：
1. **检查预测模型**: 可能模型需要改进
2. **验证标签计算**: 确保标签定义正确
3. **调整选股阈值**: 可能需要调整 topk 参数
4. **增加特征**: 添加更多预测特征

### 如何解读 Sell 图表

#### 理想表现

- **接近 100%**: 持续卖出表现最差的股票
- **稳定在 80-100%**: 卖出策略优秀
- **持续下降**: 卖出策略变差
- **持续上升**: 卖出策略变好

#### 可能的问题

- **平均排名 < 50%**: 卖出表现较好的股票，可能卖早了
- **波动很大**: 卖出时机不稳定
- **趋势向下**: 后期卖出决策变差

#### 改进建议

如果 Sell 平均排名过低（< 60%）：
1. **调整卖出策略**: 可能需要调整 n_drop 参数
2. **延长持仓期**: 减少频繁卖出
3. **优化时机**: 改进卖出时机的判断
4. **考虑止盈**: 添加止盈逻辑

### 如何解读 Hold 图表

#### 理想表现

- **稳定在 30-70%**: 持有的股票表现中等
- **波动较小**: 持仓策略稳定
- **趋势稳定**: 持仓逻辑一致

#### 可能的问题

- **平均排名接近 0%**: 持有过多的优质股票，可能应该加大仓位
- **平均排名接近 100%**: 持有过多的劣质股票，持仓逻辑可能有问题
- **波动很大**: 持仓策略不稳定

#### 改进建议

如果 Hold 平均排名异常：
1. **调整仓位管理**: 优化权重分配
2. **检查持仓逻辑**: 验证持仓判断条件
3. **增加止损**: 添加止损保护

---

## 综合评估

### 完整评估框架

```python
from qlib.contrib.report.analysis_position.parse_position import (
    parse_position,
    get_position_data
)

def evaluate_ranking_quality(position, label_data):
    """评估排名质量"""
    # 获取带排名的数据
    position_data = get_position_data(
        position=position,
        label_data=label_data,
        calculate_label_rank=True
    )

    # 按状态分组
    buy_data = position_data[position_data['status'] == 1]
    sell_data = position_data[position_data['status'] == -1]
    hold_data = position_data[position_data['status'] == 0]

    # 计算平均排名
    if not buy_data.empty:
        buy_avg_rank = buy_data.groupby(level='datetime')['rank_label_mean'].mean().mean()
    else:
        buy_avg_rank = None

    if not sell_data.empty:
        sell_avg_rank = sell_data.groupby(level='datetime')['rank_label_mean'].mean().mean()
    else:
        sell_avg_rank = None

    if not hold_data.empty:
        hold_avg_rank = hold_data.groupby(level='datetime')['rank_label_mean'].mean().mean()
    else:
        hold_avg_rank = None

    # 打印结果
    print("排名质量评估:")
    print(f"  Buy 平均排名: {buy_avg_rank:.2f}%")
    print(f"  Sell 平均排名: {sell_avg_rank:.2f}%")
    print(f"  Hold 平均排名: {hold_avg_rank:.2f}%")

    # 评估
    scores = {}

    # Buy 评分
    if buy_avg_rank is not None:
        if buy_avg_rank <= 20:
            scores['buy'] = '优秀'
        elif buy_avg_rank <= 40:
            scores['buy'] = '良好'
        elif buy_avg_rank <= 60:
            scores['buy'] = '一般'
        else:
            scores['buy'] = '较差'

    # Sell 评分
    if sell_avg_rank is not None:
        if sell_avg_rank >= 80:
            scores['sell'] = '优秀'
        elif sell_avg_rank >= 60:
            scores['sell'] = '良好'
        elif sell_avg_rank >= 40:
            scores['sell'] = '一般'
        else:
            scores['sell'] = '较差'

    # Hold 评分
    if hold_avg_rank is not None:
        if 30 <= hold_avg_rank <= 70:
            scores['hold'] = '优秀'
        elif 20 <= hold_avg_rank <= 80:
            scores['hold'] = '良好'
        else:
            scores['hold'] = '一般'

    print("\n评分:")
    for key, score in scores.items():
        print(f"  {key}: {score}")

    return {
        'buy_avg_rank': buy_avg_rank,
        'sell_avg_rank': sell_avg_rank,
        'hold_avg_rank': hold_avg_rank,
        'scores': scores
    }

# 使用
ranking_quality = evaluate_ranking_quality(positions, features_df)
```

### 排名趋势分析

```python
def analyze_ranking_trend(position_data):
    """分析排名趋势"""
    # 按日期分组
    daily_ranks = position_data.groupby(level='datetime').agg({
        'rank_label_mean': lambda x: {
            'buy': x[x.index.get_level_values(0) == 1].mean(),
            'sell': x[x.index.get_level_values(0) == -1].mean(),
            'hold': x[x.index.get_level_values(0) == 0].mean()
        }
    })

    # 转换为 DataFrame
    trend_data = pd.DataFrame([
        daily_ranks.loc[date, 'rank_label_mean']
        for date in daily_ranks.index
    ], index=daily_ranks.index)

    # 计算趋势
    print("排名趋势分析:")

    for col in trend_data.columns:
        # 计算线性趋势
        x = np.arange(len(trend_data))
        y = trend_data[col].dropna().values

        if len(y) > 2:
            slope, _ = np.polyfit(x[:len(y)], y, 1)
            print(f"\n{col}:")
            print(f"  趋势斜率: {slope:.4f}")
            if slope > 0.1:
                print(f"  趋势: 明显上升（变差）")
            elif slope > 0.01:
                print(f"  趋势: 轻微上升")
            elif slope < -0.1:
                print(f"  趋势: 明显下降（变好）")
            elif slope < -0.01:
                print(f"  趋势: 轻微下降")
            else:
                print(f"  趋势: 稳定")

# 使用
position_data = get_position_data(
    position=positions,
    label_data=features_df,
    calculate_label_rank=True
)
analyze_ranking_trend(position_data)
```

---

## 最佳实践

### 1. 定期监控

```python
import pandas as pd

# 每月分析一次
monitor_dates = pd.date_range(start_date, end_date, freq='MS')

for date in monitor_dates:
    month_start = date
    month_end = date + pd.offsets.MonthEnd(1)

    print(f"\n分析月份: {month_start} ~ {month_end}")
    ap.rank_label_graph(
        positions,
        features_df,
        start_date=month_start,
        end_date=month_end
    )
```

### 2. 异常检测

```python
def detect_ranking_anomalies(position_data, threshold=2.0):
    """检测排名异常"""
    # 计算每日平均排名
    daily_ranks = position_data.groupby(level='datetime')['rank_label_mean'].mean()

    # 计算统计量
    mean_rank = daily_ranks.mean()
    std_rank = daily_ranks.std()

    # 检测异常
    anomalies = daily_ranks[
        (daily_ranks - mean_rank).abs() > threshold * std_rank
    ]

    if len(anomalies) > 0:
        print("检测到排名异常:")
        for date, rank in anomalies.items():
            print(f"  日期: {date}, 排名: {rank:.2f}%")

    return anomalies

# 使用
position_data = get_position_data(
    position=positions,
    label_data=features_df,
    calculate_label_rank=True
)
anomalies = detect_ranking_anomalies(position_data)
```

### 3. 对比基准

```python
def compare_with_benchmark(position_data, benchmark_data):
    """与基准对比排名"""
    # 计算策略排名
    strategy_ranks = position_data.groupby(level='datetime')['rank_label_mean'].mean()

    # 计算基准排名（假设 benchmark_data 有 label 列）
    benchmark_ranks = benchmark_data.groupby(level='datetime')['label'].apply(
        lambda x: 100 - x.rank(ascending=True) / len(x) * 100
    )

    # 对比
    comparison = pd.DataFrame({
        'strategy': strategy_ranks,
        'benchmark': benchmark_ranks
    })

    print("策略 vs 基准排名对比:")
    print(comparison.describe())

    return comparison

# 使用
# comparison = compare_with_benchmark(position_data, benchmark_data)
```

---

## 常见问题

### Q: 为什么排名百分比在 0-100 之间？

A: 排名百分比 = (排名倒数 / 总数) * 100
- label.rank(ascending=False): 降序排名，最大值为 1
- 除以总数：得到相对排名
- 乘以 100：转换为百分比

### Q: Buy 的平均排名越低越好吗？

A: 是的。Buy 的平均排名越低，表示买入的股票标签值越大（表现越好），说明选股能力强。

### Q: Sell 的平均排名越高越好吗？

A: 是的。Sell 的平均排名越高，表示卖出的股票标签值越小（表现越差），说明卖出决策正确。

### Q: 如果 Buy 和 Sell 的平均排名都接近 50% 怎么办？

A: 这表示策略的选股和卖出都没有明显的优势，可能：
1. **预测模型**: 预测能力一般
2. **市场环境**: 市场没有明显趋势
3. **策略参数**: topk/n_drop 参数可能不合适

建议：
- 改进预测模型
- 调整策略参数
- 增加更多特征

### Q: Hold 的平均排名应该在什么范围？

A: 理想情况下在 30-70% 之间，表示持有的股票表现中等。如果：
- 接近 0%: 持有过多优质股票，应该加大仓位
- 接近 100%: 持有过多劣质股票，持仓逻辑有问题

### Q: 排名图表波动很大怎么办？

A: 可能的原因：
1. **数据不稳定**: 标签数据有噪音
2. **策略不稳定**: 选股标准变化大
3. **市场波动**: 市场在某些时期剧烈波动

建议：
- 平滑标签数据
- 稳定选股逻辑
- 分析波动大的时间段

### Q: 如何改进排名质量？

A: 根据不同情况：

**Buy 排名过高**:
1. 改进预测模型
2. 增加更多特征
3. 调整模型参数
4. 使用更复杂的模型

**Sell 排名过低**:
1. 调整卖出阈值
2. 延长持仓周期
3. 添加止盈止损逻辑
4. 优化卖出时机

**Hold 排名异常**:
1. 调整持仓管理
2. 优化权重分配
3. 添加风险控制

### Q: 可以分析日内交易的排名吗？

A: 当前版本主要支持日度数据。对于日内数据，需要：
1. 确保标签数据是日度级别
2. 或者修改代码支持日内排名计算

### Q: 排名与收益的关系是什么？

A: 排名反映了选股能力，收益体现了最终结果：

- **好排名 + 高收益**: 策略优秀
- **好排名 + 低收益**: 交易成本高或市场环境差
- **差排名 + 高收益**: 运气成分或排名不是关键因素
- **差排名 + 低收益**: 策略需要改进
