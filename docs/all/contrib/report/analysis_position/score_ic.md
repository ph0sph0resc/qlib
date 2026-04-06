# analysis_position/score_ic.py

## 模块概述

`qlib.contrib.report.analysis_position.score_ic.py` 提供了计算和展示预测得分与标签的 IC（信息系数）的功能。该模块用于评估预测模型的准确性和稳定性。

## 核心函数

### score_ic_graph

**说明**: 计算并展示预测得分与标签的 IC（信息系数）和 Rank IC 时序图。

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
SH600004    2017-12-11  -0.013502      -0.013502
            2017-12-12  -0.072367      -0.072367
            2017-12-13  -0.068605      -0.068605
            2017-12-14   0.012440       0.012440
            2017-12-15  -0.102778      -0.102778
```

#### IC 指标说明

**IC (Information Coefficient)**:

- **计算方式**: Pearson 相关系数
- **公式**: `IC = corr(score, label)`
- **范围**: [-1, 1]
- **含义**:
  - 接近 1: 预测值与真实值强正相关
  - 接近 -1: 预测值与真实值强负相关
  - 接近 0: 没有线性关系

**Rank IC**:

- **计算方式**: Spearman 相关系数
- **公式**: `Rank IC = corr(rank(score), rank(label))`
- **范围**: [-1, 1]
- **含义**:
  - 接近 1: 预测排序与真实排序高度一致
  - 接近 -1: 预测排序与真实排序相反
  - 接近 0: 没有排序关系

#### 图表结构

生成单个图表，包含两条曲线：

| 曲线 | 说明 |
|------|------|
| IC | 每日预测得分的 IC 值 |
| Rank IC | 每日预测得分的 Rank IC 值 |

#### 坐标说明

- **X 轴**: 交易日
- **Y 轴**: IC 或 Rank IC 值

#### 返回值

- 如果 `show_notebook=True`，在 Notebook 中显示图表
- 如果 `show_notebook=False`，返回包含 plotly Figure 对象的列表

---

## 辅助函数

### _get_score_ic

**说明**: 计算预测得分的 IC 和 Rank IC。

#### 函数签名

```python
def _get_score_ic(pred_label: pd.DataFrame):
```

#### 参数说明

| 参数 | 类型 | 说明 |
|------|------|------|
| pred_label | pd.DataFrame | 包含 score 和 label 列的数据 |

#### 返回值

返回一个 DataFrame，包含两列：

| 列名 | 计算方式 | 说明 |
|------|---------|------|
| ic | 按日期分组的 label.corr(score) | Pearson 相关系数 |
| rank_ic | 按日期分组的 label.corr(score, method='spearman') | Spearman 相关系数 |

#### 计算逻辑

1. 删除缺失值
2. 按日期分组
3. 计算每组的 Pearson 相关系数（IC）
4. 计算每组的 Spearman 相关系数（Rank IC）

---

## 使用示例

### 示例 1: 基础使用

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
```

### 示例 2: 使用 rangebreaks

```python
from qlib.contrib.report.utils import guess_plotly_rangebreaks

# 推断日期断点
rangebreaks = guess_plotly_rangebreaks(
    pred_label.index.get_level_values('datetime')
)

# 生成图表并应用 rangebreaks
ap.score_ic_graph(pred_label, rangebreaks=rangebreaks)
```

### 示例 3: 返回图表对象

```python
# 返回图表对象
figures = ap.score_ic_graph(pred_label, show_notebook=False)

# 获取图表
fig = figures[0]

# 自定义图表样式
fig.update_layout(
    title='预测得分 IC 分析',
    height=500,
    plot_bgcolor='white'
)

# 显示图表
fig.show()
```

### 示例 4: 保存图表

```python
import os

# 创建输出目录
output_dir = 'ic_reports'
os.makedirs(output_dir, exist_ok=True)

# 生成图表
figures = ap.score_ic_graph(pred_label, show_notebook=False)

# 保存图表
fig = figures[0]
output_path = os.path.join(output_dir, 'score_ic_analysis.html')
fig.write_html(output_path)
print(f"已保存: {output_path}")
```

### 示例 5: 对比多个模型

```python
# 假设有多个模型的预测结果
models = {
    'model_1': pred_df_1,
    'model_2': pred_df_2,
    'model_3': pred_df_3,
}

for name, pred in models.items():
    # 合并预测得分和标签
    pred_label = pd.concat(
        [features_df, pred],
        axis=1,
        sort=True
    ).reindex(features_df.index)
    pred_label.columns = ['label', 'score']

    print(f"\n分析模型: {name}")
    ap.score_ic_graph(pred_label)
```

### 示例 6: 滚动窗口分析

```python
import pandas as pd

# 定义滚动窗口
window_size = 60  # 约三个月

# 获取所有日期
all_dates = pred_label.index.get_level_values('datetime').unique()

for i in range(0, len(all_dates) - window_size, 30):  # 每30天分析一次
    window_start = all_dates[i]
    window_end = all_dates[i + window_size - 1]

    # 筛选窗口内的数据
    window_data = pred_label[
        pred_label.index.get_level_values('datetime').between(
            window_start,
            window_end
        )
    ]

    print(f"\n分析窗口: {window_start} ~ {window_end}")
    ap.score_ic_graph(window_data)
```

---

## IC 指标解读

### IC 统计特征

```python
def analyze_ic_stats(pred_label):
    """分析 IC 统计特征"""
    # 计算 IC
    ic_df = _get_score_ic(pred_label)

    # 计算统计量
    stats = {
        'mean': ic_df.mean(),
        'std': ic_df.std(),
        'min': ic_df.min(),
        'max': ic_df.max(),
        'median': ic_df.median(),
        'ic/mean': ic_df.mean() / ic_df.std(),
        'positive_ratio': (ic_df > 0).sum() / len(ic_df) * 100
    }

    print("IC 统计特征:")
    print(f"\n{'指标':<20} {'IC':<15} {'Rank IC':<15}")
    print("=" * 50)
    for stat_name, stat_value in stats.items():
        if isinstance(stat_value, pd.Series):
            ic_val = stat_value['ic']
            rank_ic_val = stat_value['rank_ic']
            print(f"{stat_name:<20} {ic_val:<15.6f} {rank_ic_val:<15.6f}")

    return stats

# 使用
stats = analyze_ic_stats(pred_label)
```

### IC 评估标准

| 指标 | IC 评级 | Rank IC 评级 |
|------|---------|-------------|
| 均值 | > 0.05: 优秀<br>0.03-0.05: 良好<br>0.01-0.03: 一般<br>< 0.01: 较差 | > 0.08: 优秀<br>0.05-0.08: 良好<br>0.02-0.05: 一般<br>< 0.02: 较差 |
| 标准差 | < 0.08: 优秀<br>0.08-0.12: 良好<br>0.12-0.18: 一般<br>> 0.18: 较差 | < 0.10: 优秀<br>0.10-0.15: 良好<br>0.15-0.22: 一般<br>> 0.22: 较差 |
| IC/标准差 | > 0.5: 优秀<br>0.3-0.5: 良好<br>0.15-0.3: 一般<br>< 0.15: 较差 | > 0.6: 优秀<br>0.4-0.6: 良好<br>0.2-0.4: 一般<br>< 0.2: 较差 |
| 正值比例 | > 60%: 优秀<br>50%-60%: 良好<br>40%-50%: 一般<br>< 40%: 较差 | > 65%: 优秀<br>55%-65%: 良好<br>45%-55%: 一般<br>< 45%: 较差 |

---

## 高级分析

### IC 时序分析

```python
def analyze_ic_time_series(pred_label):
    """分析 IC 时序特征"""
    # 计算 IC
    ic_df = _get_score_ic(pred_label)

    print("IC 时序分析:")

    # 按年分组
    ic_df['year'] = pd.to_datetime(ic_df.index).year
    yearly_stats = ic_df.groupby('year').agg(['mean', 'std', 'count'])

    print("\n年度 IC 统计:")
    print(yearly_stats)

    # 按月分组
    ic_df['month'] = pd.to_datetime(ic_df.index).month
    monthly_stats = ic_df.groupby(['year', 'month']).agg(['mean', 'std'])

    print("\n月度 IC 均值（部分）:")
    print(monthly_stats['mean'].head(12))

    # 趋势分析
    x = np.arange(len(ic_df))
    y_ic = ic_df['ic'].values
    y_rank_ic = ic_df['rank_ic'].values

    slope_ic, _ = np.polyfit(x, y_ic, 1)
    slope_rank_ic, _ = np.polyfit(x, y_rank_ic, 1)

    print("\nIC 趋势:")
    print(f"  IC 斜率: {slope_ic:.6f}")
    print(f"  Rank IC 斜率: {slope_rank_ic:.6f}")

    if slope_ic > 0.001:
        print("  IC 趋势: 明显上升")
    elif slope_ic < -0.001:
        print("  IC 趋势: 明显下降")
    else:
        print("  IC 趋势: 稳定")

    return {
        'yearly_stats': yearly_stats,
        'monthly_stats': monthly_stats,
        'slope_ic': slope_ic,
        'slope_rank_ic': slope_rank_ic
    }

# 使用
time_series_analysis = analyze_ic_time_series(pred_label)
```

### IC 稳定性分析

```python
def analyze_ic_stability(pred_label, window=20):
    """分析 IC 稳定性"""
    # 计算 IC
    ic_df = _get_score_ic(pred_label)

    print("IC 稳定性分析:")

    # 滚动窗口统计
    rolling_mean = ic_df['ic'].rolling(window=window).mean()
    rolling_std = ic_df['ic'].rolling(window=window).std()

    # 计算稳定性指标
    stability = {
        'mean_of_std': rolling_std.mean(),
        'std_of_mean': rolling_mean.std(),
        'max_drawdown': (rolling_mean - rolling_mean.cummax()).min(),
        'volatility': rolling_mean.std() / rolling_mean.mean() if rolling_mean.mean() != 0 else np.inf
    }

    print(f"\n滚动窗口 ({window}天) 统计:")
    print(f"  标准差均值: {stability['mean_of_std']:.6f}")
    print(f"  均值标准差: {stability['std_of_mean']:.6f}")
    print(f"  最大回撤: {stability['max_drawdown']:.6f}")
    print(f"  波动率: {stability['volatility']:.6f}")

    # 评估
    if stability['mean_of_std'] < 0.08 and stability['volatility'] < 0.5:
        print("\n评级: IC 稳定性优秀")
    elif stability['mean_of_std'] < 0.12 and stability['volatility'] < 1.0:
        print("\n评级: IC 稳定性良好")
    else:
        print("\n评级: IC 稳定性一般")

    return stability

# 使用
stability = analyze_ic_stability(pred_label, window=20)
```

### IC 与收益关系分析

```python
def analyze_ic_return_relationship(pred_label, returns):
    """分析 IC 与收益的关系"""
    # 计算 IC
    ic_df = _get_score_ic(pred_label)

    # 确保收益数据与 IC 对齐
    aligned_returns = returns.reindex(ic_df.index)

    # 计算 IC 分组收益
    ic_df['ic_group'] = pd.qcut(ic_df['ic'], 5, labels=['Q1', 'Q2', 'Q3', 'Q4', 'Q5'])

    group_returns = []
    for group in ['Q1', 'Q2', 'Q3', 'Q4', 'Q5']:
        mask = ic_df['ic_group'] == group
        group_returns.append({
            'group': group,
            'mean_ic': ic_df.loc[mask, 'ic'].mean(),
            'mean_return': aligned_returns.loc[mask].mean(),
            'count': mask.sum()
        })

    return_df = pd.DataFrame(group_returns)

    print("IC 分组收益分析:")
    print(return_df)

    # 计算相关性
    correlation = ic_df['ic'].corr(aligned_returns)
    print(f"\nIC 与收益的相关性: {correlation:.6f}")

    return return_df, correlation

# 使用
# ic_return_analysis = analyze_ic_return_relationship(pred_label, returns)
```

---

## 最佳实践

### 1. 数据准备

```python
def prepare_ic_data(pred_score, features_df):
    """准备 IC 分析数据"""
    # 确保列名正确
    pred_score = pred_score.copy()
    features_df = features_df.copy()

    # 重命名列
    pred_score.columns = ['score']
    features_df.columns = ['label']

    # 合并数据
    pred_label = pd.concat(
        [features_df, pred_score],
        axis=1,
        sort=True
    )

    # 删除缺失值
    pred_label = pred_label.dropna()

    return pred_label

# 使用
pred_label = prepare_ic_data(pred_df, features_df)
```

### 2. 定期监控

```python
import pandas as pd

# 按月监控
monitor_dates = pd.date_range(start_date, end_date, freq='MS')

for date in monitor_dates:
    month_start = date
    month_end = date + pd.offsets.MonthEnd(1)

    # 筛选月度数据
    month_data = pred_label[
        pred_label.index.get_level_values('datetime').between(
            month_start,
            month_end
        )
    ]

    print(f"\n分析月份: {month_start} ~ {month_end}")
    ap.score_ic_graph(month_data)
```

### 3. 多时间周期分析

```python
# 分析不同时间周期的 IC
periods = {
    '1m': 20,    # 约 1 个月
    '3m': 60,    # 约 3 个月
    '6m': 120,   # 约 6 个月
    '1y': 252,   # 约 1 年
}

for period_name, window in periods.items():
    print(f"\n分析周期: {period_name}")

    # 使用滚动窗口分析
    ic_df = _get_score_ic(pred_label)
    rolling_ic = ic_df['ic'].rolling(window=window).mean()
    rolling_rank_ic = ic_df['rank_ic'].rolling(window=window).mean()

    # 创建图表
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=rolling_ic.index,
        y=rolling_ic.values,
        name=f'IC ({period_name})',
        mode='lines'
    ))
    fig.add_trace(go.Scatter(
        x=rolling_rank_ic.index,
        y=rolling_rank_ic.values,
        name=f'Rank IC ({period_name})',
        mode='lines'
    ))

    fig.update_layout(
        title=f'{period_name} 滚动 IC',
        height=500
    )
    fig.show()
```

### 4. 异常检测

```python
def detect_ic_anomalies(pred_label, threshold=2.0):
    """检测 IC 异常"""
    # 计算 IC
    ic_df = _get_score_ic(pred_label)

    # 计算统计量
    mean_ic = ic_df['ic'].mean()
    std_ic = ic_df['ic'].std()

    # 检测异常
    anomalies = ic_df[
        (ic_df['ic'] - mean_ic).abs() > threshold * std_ic
    ]

    if len(anomalies) > 0:
        print("检测到 IC 异常:")
        for date, row in anomalies.iterrows():
            print(f"  日期: {date}, IC: {row['ic']:.6f}, Rank IC: {row['rank_ic']:.6f}")
    else:
        print("未检测到 IC 异常")

    return anomalies

# 使用
anomalies = detect_ic_anomalies(pred_label, threshold=2.0)
```

---

## 常见问题

### Q: IC 和 Rank IC 有什么区别？

A:
- **IC (Pearson 相关系数）**:
  - 衡量线性关系
  - 对异常值敏感
  - 反映预测的精确程度

- **Rank IC (Spearman 相关系数）**:
  - 衡量排序一致性
  - 对异常值稳健
  - 反映预测的排名准确性

在因子投资中，Rank IC 通常更重要，因为我们关心的是能否选出相对更好的股票。

### Q: IC 多少算好？

A: 一般标准：
- **IC > 0.05**: 优秀
- **IC = 0.03-0.05**: 良好
- **IC = 0.01-0.03**: 一般
- **IC < 0.01**: 较差

同时要考虑 IC 的标准差，IC/标准差 > 0.5 通常认为有较好的风险调整后预测能力。

### Q: 为什么 IC 有时候是负值？

A: 可能的原因：
1. **预测方向错误**: 模型预测的排序与真实收益相反
2. **标签计算错误**: 标签的定义与预期不符
3. **过拟合**: 模型在测试集上失效
4. **市场环境变化**: 模型不再适应新的市场环境

建议检查标签计算和模型参数。

### Q: 如何提高 IC？

A: 从以下几个方面改进：
1. **改进模型**:
   - 增加更多特征
   - 使用更复杂的模型
   - 调整模型超参数
   - 使用集成学习

2. **优化标签**:
   - 检查标签定义是否正确
   - 尝试不同的标签计算方式
   - 调整预测周期

3. **数据处理**:
   - 更好的数据清洗
   - 处理缺失值和异常值
   - 特征工程

4. **模型选择**:
   - 尝试不同的模型类型
   - 使用交叉验证方法

### Q: IC 的稳定性如何评估？

A: 从以下维度评估：
1. **标准差**: 标准差越小越稳定
2. **波动率**: IC 的变异系数
3. **正值比例**: 正值比例越高越稳定
4. **时序趋势**: IC 是否有明显的上升或下降趋势

### Q: 可以分析日内 IC 吗？

A: 可以，但需要注意：
1. 确保预测得分和标签都是日内级别的
2. 调整分析的统计频率（如每小时）
3. 考虑日内数据的特殊性（如开盘、收盘等）

### Q: IC 与策略收益的关系是什么？

A: 通常情况下：
- **高 IC**: 策略收益应该较好
- **IC 稳定**: 策略收益应该稳定
- **IC 下降**: 策略收益可能下降

但还需要考虑其他因素：
- 交易成本
- 换手率
- 市场环境
- 策略实现细节

### Q: 如何在报告中使用 IC 分析？

A: 建议的 IC 分析报告包含：
1. **整体统计**: IC 和 Rank IC 的均值、标准差等
2. **时序图**: IC 随时间的变化
3. **稳定性分析**: 滚动窗口的 IC 统计
4. **分组分析**: IC 高低组的收益对比
5. **趋势分析**: IC 的上升趋势或下降趋势

这样的报告可以全面评估模型的预测能力。
