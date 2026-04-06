# analysis_position/parse_position.py

## 模块概述

`qlib.contrib.report.analysis_position.parse_position.py` 提供了持仓数据解析和处理的工具函数。该模块将回测返回的持仓字典转换为结构化的 DataFrame 格式，并支持添加标签、基准等额外信息。

## 核心函数

### parse_position

**说明**: 将持仓字典解析为 DataFrame 格式，并标注交易状态（买入、卖出、持有）。

#### 函数签名

```python
def parse_position(position: dict = None) -> pd.DataFrame:
```

#### 参数说明

| 参数 | 类型 | 说明 |
|------|------|------|
| position | dict | 持仓数据，回测返回的持仓字典 |

#### 返回值

返回一个 DataFrame，包含持仓的详细信息。

**返回数据格式**:

| 列名 | 类型 | 说明 |
|------|------|------|
| amount | float | 持仓数量 |
| cash | float | 现金余额 |
| count | int | 持仓次数 |
| price | float | 持仓价格 |
| status | int | 交易状态 {0: 持有, -1: 卖出, 1: 买入} |
| weight | float | 持仓权重 |

**索引**: MultiIndex [instrument, datetime]

#### 交易状态说明

| status 值 | 含义 | 说明 |
|----------|------|------|
| 0 | hold | 持有，股票在当前交易日和前一交易日都在持仓中 |
| 1 | buy | 买入，股票在当前交易日持仓，但前一交易日不在 |
| -1 | sell | 卖出，股票在当前交易日不在持仓，但前一交易日在 |

#### 返回数据示例

```python
                                        amount      cash      count    price status weight
instrument  datetime
SZ000547    2017-01-04  44.154290   211405.285654   1   205.189575  1   0.031255
SZ300202    2017-01-04  60.638845   211405.285654   1   154.356506  1   0.032290
SH600158    2017-01-04  46.531681   211405.285654   1   153.895142  1   0.024704
SH600545    2017-01-04  197.173093  211405.285654   1   48.607037   1   0.033063
SZ000930    2017-01-04  103.938300  211405.285654   1   80.759453   1   0.028958
```

#### 计算逻辑

1. **持仓权重**: 使用 `get_stock_weight_df` 计算每只股票的权重
2. **状态标注**:
   - 比较当前交易日和前一交易日的持仓列表
   - T 存在，T-1 不存在 → status = 1（买入）
   - T 不存在，T-1 存在 → status = -1（卖出）
   - T 和 T-1 都存在 → status = 0（持有）

#### 使用示例

```python
from qlib.contrib.report.analysis_position import parse_position

# 偔回测后得到 positions
# _, positions = backtest...()

# 解析持仓数据
position_df = parse_position(positions)

# 查看前几行
print(position_df.head())

# 查看统计数据
print(f"总行数: {len(position_df)}")
print(f"交易天数: {position_df.index.get_level_values('datetime').nunique()}")
print(f"涉及股票数: {position_df.index.get_level_values('instrument').nunique()}")

# 统计交易状态
status_counts = position_df.groupby('status').size()
print(f"\n交易状态统计:")
print(f"  买入 (1): {status_counts.get(1, 0)}")
print(f"  持有 (0): {status_counts.get(0, 0)}")
print(f"  卖出 (-1): {status_counts.get(-1, 0)}")
```

---

### get_position_data

**说明**: 整合持仓数据与标签/报告数据，生成完整的分析数据集。

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

#### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| position | dict | 必需 | 持仓数据 |
| label_data | pd.DataFrame | 必需 | 标签数据 |
| report_normal | pd.DataFrame | None | 报告数据，用于添加基准列 |
| calculate_label_rank | bool | False | 是否计算标签排名 |
| start_date | str | None | 开始日期 |
| end_date | str | None | 结束日期 |

#### 返回值

返回整合后的 DataFrame，包含以下列：

| 列名 | | | 说明 |
|------|-|-|------|
| amount | float | | 持仓数量 |
| cash | float | | 现金余额 |
| count | int | | 持仓次数 |
| price | float | | 持仓价格 |
| status | int | | 交易状态 {0, 1, -1} |
| weight | float | | 持仓权重 |
| label | float | | 标签值（未来收益率） |
| rank_ratio | float | | 标签排名百分比（calculate_label_rank=True） |
| rank_label_mean | float | | 平均标签排名（calculate_label_rank=True） |
| excess_return | float | | 超额收益（calculate_label_rank=True） |
| bench | float | | 基准收益率（report_normal 不为 None） |

**索引**: MultiIndex [instrument, datetime]

#### 使用示例

```python
from qlib.contrib.report.analysis_position import get_position_data
from qlib.data import D

# 准备数据
# positions, report_normal_df 已从回测获得

# 获取标签数据
instruments = D.instruments('csi500')
dates = pd.date_range('2020-01-01', '2020-12-31')
label_data = D.features(
    instruments,
    ['Ref($close, -1)/$close - 1'],
    dates[0],
    dates[-1]
)
label_data.columns = ['label']

# 不计算标签排名
position_data = get_position_data(
    position=positions,
    label_data=label_data,
    report_normal=report_normal_df,
    start_date='2020-06-01',
    end_date='2020-12.31'
)

# 计算标签排名
position_data_with_rank = get_position_data(
    position=positions,
    label_data=label_data,
    report_normal=report_normal_df,
    calculate_label_rank=True
)

# 查看数据
print(position_data_with_rank.head())
```

---

##只用于函数

### _add_label_to_position

**说明**: 将标签数据合并到持仓数据中。

#### 函数签名

```python
def _add_label_to_position(
    position_df: pd.DataFrame,
    label_data: pd.DataFrame
) -> pd.DataFrame:
```

#### 参数说明

| 参数 | 类型 | 说明 |
|------|------|------|
| position_df | pd.DataFrame | 持仓 DataFrame |
| label_data | pd.DataFrame | 标签数据 |

#### 返回值

合并后的 DataFrame，包含所有持仓列和 label 列。

---

### _add_bench_to_position

**说明**: 将基准数据合并到持仓数据中。

#### 函数签名

```python
def _add_bench_to_position(
    position_df: pd.DataFrame = None,
    bench: pd.Series = None
) -> pd.DataFrame:
```

#### 参数说明

| 参数 | 类型 | 说明 |
|------|------|------|
| position_df | pd.DataFrame | 持仓 DataFrame |
| bench | pd.Series | 基准收益率序列 |

#### 返回值

合并后的 DataFrame，包含所有持仓列和 bench 列。

**注意**: 基准数据会向前对齐（shift(-1)），因为持仓的收益是相对于下一期的。

---

### _calculate_label_rank

**说明**: 计算标签的排名和相关统计量。

#### 函数签名

```python
def _calculate_label_rank(df: pd.DataFrame) -> pd.DataFrame:
```

#### 参数说明

| 参数 | 类型 | 说明 |
|------|------|------|
| df | pd.DataFrame | 包含 label 和 status 列的数据 |

#### 返回值

添加了排名相关列的 DataFrame：

| 新增列 | 计算方式 | 说明 |
|--------|---------|------|
| rank_ratio | label.rank(ascending=False) / len * 100 | 标签排名百分比（0-100） |
| rank_label_mean | 按 status 分组的 rank_ratio 均值 | 每种交易状态的平均排名 |
| excess_return | label - label.mean() | 相对于均值的超额收益 |

**排名说明**:
- rank_ratio = 0: 标签值最大
- rank_ratio = 100: 标签值最小

---

## 完整使用示例

### 示例 1: 基础持仓解析

```python
from qlib.contrib.report.analysis_position import parse_position

# 假设从回测获得 positions
# _, positions = backtest(...)

# 解析持仓
position_df = parse_position(positions)

# 基本信息
print(f"持仓数据形状: {position_df.shape}")
print(f"\n列名: {position_df.columns.tolist()}")

# 按日期分组，查看每日持仓情况
daily_positions = position_df.groupby(level='datetime')

print("\n每日持仓统计:")
for date, group in list(daily_positions)[:5]:  # 查看前5天
    print(f"\n日期: {date}")
    print(f"  持仓股票数: {len(group)}")
    print(f"  总权重: {group['weight'].sum():.4f}")
    print(f"  现金: {group['cash'].iloc[0]:.2f}")
    print(f"  买入数: {(group['status']==1).sum()}")
    print(f"  卖出数: {(group['status']==-1).sum()}")
    print(f"  持有数: {(group['status']==0).sum()}")
```

### 示例 2: 分析交易频率

```python
import pandas as pd

# 解析持仓
position_df = parse_position(positions)

# 统计每天的交易状态
daily_status = position_df.groupby(level='datetime').agg({
    'status': lambda x: {
        'buy': (x == 1).sum(),
        'sell': (x == -1).sum(),
        'hold': (x == 0).sum()
    }
})

print("每日交易统计:")
print(daily_status.head())

# 计算平均交易频率
avg_buy = daily_status['status'].apply(lambda x: x['buy']).mean()
avg_sell = daily_status['status'].apply(lambda x: x['sell']).mean()

print(f"\n平均每日买入数: {avg_buy:.2f}")
print(f"平均每日卖出数: {avg_sell:.2f}")
```

### 示例 3: 整合标签数据

```python
from qlib.contrib.report.analysis_position import get_position_data
from qlib.data import D

# 准备标签数据
instruments = D.instruments('csi500')
dates = pd.date_range('2020-01-01', '2020-12-31')
label_data = D.features(
    instruments,
    ['Ref($close, -1)/$close - 1'],
    dates[0],
    dates[-1]
)
label_data.columns = ['label']

# 整合数据
position_data = get_position_data(
    position=positions,
    label_data=label_data,
    report_normal=report_normal_df
)

# 分析持仓收益
print("持仓收益统计:")
print(f"\n整体平均收益: {position_data['label'].mean():.6f}")
print(f"整体收益标准差: {position_data['label'].std():.6f}")

# 按交易状态分组分析
status_returns = position_data.groupby('status')['label'].agg(['mean', 'std', 'count'])

print("\n各交易状态的收益统计:")
status_returns.index = status_returns.index.map({
    1: 'buy',
    0: 'hold',
    -1: 'sell'
})
print(status_returns)
```

### 示例 4: 计算标签排名

```python
# 计算标签排名
position_data = get_position_data(
    position=positions,
    label_data=label_data,
    calculate_label_rank=True
)

# 分析买入、卖出、持有的排名分布
rank_stats = position_data.groupby('status')['rank_label_mean'].describe()

print("各交易状态的标签排名统计:")
rank_stats.index = rank_stats.index.map({
    1: 'buy',
    0: 'hold',
    -1: 'sell'
})
print(rank_stats)

# 理想情况下:
# - buy 的 rank_label_mean 应该接近 0（买入标签值最大的股票）
# - sell 的 rank_label_mean 应该接近 100（卖出标签值最小的股票）
# - hold 的 rank_label_mean 应该在中间
```

### 示例 5: 按时间窗口分析

```python
import pandas as pd

# 解析持仓并添加标签
position_data = get_position_data(
    position=positions,
    label_data=label_data,
    calculate_label_rank=True
)

# 按月分组分析
monthly_data = position_data.groupby(
    [position_data.index.get_level_values('datetime').year,
     position_data.index.get_level_values('datetime').month]
)

print("月度持仓统计:")
for (year, month), group in list(monthly_data)[:6]:  # 查看6个月
    print(f"\n{year}-{month:02d}:")
    print(f"  持仓股票数: {len(group)}")
    print(f"  平均收益: {group['label'].mean():.6f}")

    if 'rank_label_mean' in group.columns:
        buy_rank = group[group['status']==1]['rank_label_mean'].mean()
        sell_rank = group[group['status']==-1]['rank_label_mean'].mean()
        hold_rank = group[group['status']==0]['rank_label_mean'].mean()

        print(f"  买入平均排名: {buy_rank:.2f}%")
        print(f"  卖出平均排名: {sell_rank:.2f}%")
        print(f"  持有平均排名: {hold_rank:.2f}%")
```

### 示例 6: 识别频繁交易股票

```python
# 解析持仓
position_df = parse_position(positions)

# 统计每只股票的交易次数
stock_trade_count = position_df.groupby(level='instrument').agg({
    'status': lambda x: {
        'buy_count': (x == 1).sum(),
        'sell_count': (x == -1).sum(),
        'total_transactions': ((xabs() > 0)).sum()
    }
})

# 计算总交易次数
stock_trade_count['total_transactions'] = stock_trade_count['status'].apply(
    lambda x: x['buy_count'] + x['sell_count']
)

# 找出交易最频繁的股票
top_traded = stock_trade_count['total_transactions'].nlargest(10)

print("交易最频繁的股票:")
for stock, count in top_traded.items():
    print(f"  {stock}: {count} 次交易")
```

### 示例 7: 持仓稳定性分析

```python
# 解析持仓
position_df = parse_position(positions)

# 计算每只股票的持仓天数
stock_hold_days = position_df.groupby(level='instrument').size()

# 统计持仓天数分布
print("持仓天数统计:")
print(f"  平均持仓天数: {stock_hold_days.mean():.1f}")
print(f"  中位数持仓天数: {stock_hold_days.median():.1f}")
print(f"  最长持仓天数: {stock_hold_days.max()}")
print(f"  最短持仓天数: {stock_hold_days.min()}")

# 持仓天数分布
print("\n持仓天数分位数:")
for percentile in [10, 25, 50, 75, 90]:
    value = stock_hold_days.quantile(percentile / 100)
    print(f"  {percentile}%: {value:.1f} 天")
```

---

## 最佳实践

### 1. 数据验证

```python
def validate_position_df(position_df):
    """验证持仓数据的完整性"""
    # 检查必需的列
    required_columns = ['amount', 'cash', 'count', 'price', 'status', 'weight']
    assert all(col in position_df.columns for col in required_columns), \
        "缺少必需的列"

    # 检查索引
    assert position_df.index.names == ['instrument', 'datetime'], \
        "索引名称不正确"

    # 检查 status 值
    valid_status = position_df['status'].isin([-1, 0, 1]).all()
    assert valid_status, "status 值必须为 -1, 0, 1"

    # 检查权重
    assert (position_df['weight'] >= 0).all(), "权重不能为负数"

    print("✓ 持仓数据验证通过")

# 使用
position_df = parse_position(positions)
validate_position_df(position_df)
```

### 2. 性能优化

```python
# 对于大数据集，可以只解析特定时间范围
def parse_position_subset(position, start_date, end_date):
    """只解析特定时间范围的持仓数据"""
    # 过滤时间范围
    filtered_position = {
        date: data
        for date, data in position.items()
        if start_date <= pd.Timestamp(date) <= pd.Timestamp(end_date)
    }

    return parse_position(filtered_position)

# 使用
start_date = '2020-06-01'
end_date = '2020-12-31'
position_df_subset = parse_position_subset(positions, start_date, end_date)
```

### 3. 自定义分析

```python
def analyze_position_performance(position_data):
    """自定义持仓性能分析"""
    # 计算各种统计量
    stats = {}

    # 整体统计
    stats['overall'] = {
        'mean_return': position_data['label'].mean(),
        'std_return': position_data['label'].std(),
        'total_transactions': (position_data['status'] != 0).sum()
    }

    # 按交易状态分组
    for status, status_name in [(1, 'buy'), (0, 'hold'), (-1, 'sell')]:
        subset = position_data[position_data['status'] == status]
        stats[status_name] = {
            'mean_return': subset['label'].mean(),
            'std_return': subset['label'].std(),
            'count': len(subset)
        }

    return stats

# 使用
position_data = get_position_data(positions, label_data)
stats = analyze_position_performance(position_data)
print(stats)
```

---

## 常见问题

### Q: 为什么 status 有 -1, 0, 1 三个值？

A: 这三个值表示不同的交易状态：
- 1: 买入，股票在当前交易日有持仓，但前一交易日没有
- 0: 持有，股票在当前交易日和前一交易日都有持仓
- -1: 卖出，股票在当前交易日没有持仓，但前一交易日有

### Q: weight 是如何计算的？

A: weight 表示每只股票的持仓权重，总和为 1（或接近 1）。计算使用 `get_stock_weight_df` 函数，该函数从持仓字典中提取权重信息。

### Q: label 和 bench 为什么会向前对齐？

A: 因为持仓的收益是相对于下一期的：
- position 在 T 时刻的持仓
- 收益是 T 到 T+1 的变化
- 所以需要使用 shift(-1) 对齐

### Q: calculate_label_rank 有什么作用？

A: 计算标签的排名，用于评估策略的选股能力：
- buy 的平均排名应该接近 0（买入表现最好的股票）
- sell 的平均排名应该接近 100（卖出表现最差的股票）
- hold 的平均排名应该在中间

### Q: 如何处理缺失值？

A: `get_position_data` 会自动处理索引对齐，但建议在调用前检查数据：

```python
# 检查缺失值
print("标签数据缺失值:", label_data.isna().sum().sum())
print("报告数据缺失值:", report_normal_df.isna().sum().sum())
```

### Q: 可以添加自定义列吗？

A: 可以，在获取 position_data 后添加：

```python
position_data = get_position_data(positions, label_data)

# 添加自定义列
position_data['custom_metric'] = position_data['label'] * position_data['weight']
position_data['abs_return'] = position_data['label'].abs()
```
