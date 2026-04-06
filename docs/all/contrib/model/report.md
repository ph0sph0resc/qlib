# report 模块详细文档

## 模块概述

`report` 模块提供了回测报告和指标计算的功能，主要包含两个核心类：
- **PortfolioMetrics**：投资组合绩效指标跟踪和记录
- **Indicator**：交易执行指标记录和分析

该模块负责：
1. 记录投资组合每日的收益、成本、换手率、账户价值等指标
2. 计算和记录基准收益率
3. 跟踪交易执行的详细指标（成交率、价格优势等）
4. 支持指标的持久化存储和加载

---

## 类文档

### PortfolioMetrics

投资组合绩效指标类，用于跟踪和记录投资组合的每日绩效指标。

#### 初始化方法

```python
def __init__(self, freq: str = "day", benchmark_config: dict = {})
```

**参数说明：**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `freq` | str | "day" | 交易频率（'day', '1min' 等） |
| `benchmark_config` | dict | {} | 基准配置字典，详见下文 |

**benchmark_config 配置项：**

| 配置项 | 类型 | 说明 |
|--------|------|------|
| `benchmark` | Union[str, list, pd.Series] | 基准定义<br>- `pd.Series`：直接提供收益率序列，index为交易日期，值为收益率<br>- `list`：使用股票池的日均变化作为基准<br>- `str`：基准指数代码，默认为 SH000300（沪深300） |
| `start_time` | Union[str, pd.Timestamp] | 基准开始时间（如果 benchmark 是 Series 则忽略） |
| `end_time` | Union[str, pd.Timestamp] | 基准结束时间（如果 benchmark 是 Series 则忽略） |

**使用示例：**
```python
from qlib.backtest.report import PortfolioMetrics

# 使用默认基准（沪深300）
metrics = PortfolioMetrics(freq="day")

# 使用自定义基准配置
metrics = PortfolioMetrics(
    freq="day",
    benchmark_config={
        "benchmark": "SH000905",  # 中证500
        "start_time": "2020-01-01",
        "end_time": "2020-12-31"
    }
)

# 直接提供基准收益率序列
import pandas as pd
bench_series = pd.Series([0.01, 0.005, -0.01], index=pd.to_datetime(['2020-01-01', '2020-01-02', '2020-01-03']))
metrics = PortfolioMetrics(
    freq="day",
    benchmark_config={"benchmark": bench_series}
)
```

---

#### 主要方法

##### init_vars

初始化所有指标变量。

**函数签名：**
```python
def init_vars(self) -> None
```

**说明：**
初始化以下 OrderedDict 容器：
- `accounts`：账户总价值（现金+证券）
- `returns`：策略收益率（不含交易费用）
- `total_turnovers`：总换手额
- `turnovers`：换手率
- `total_costs`：总交易成本
- `costs`：交易成本率
- `values`：证券市值（不含现金）
- `cashes`：现金余额
- `benches`：基准收益率

##### init_bench

初始化基准数据。

**函数签名：**
```python
def init_bench(self, freq: str | None = None, benchmark_config: dict | None = None) -> None
```

##### _cal_benchmark

计算基准收益率序列（静态方法）。

**函数签名：**
```python
@staticmethod
def _cal_benchmark(benchmark_config: Optional[dict], freq: str) -> Optional[pd.Series]
```

**返回值：**
- 类型：`Optional[pd.Series]`
- 说明：基准收益率序列，如果没有配置基准则返回 None

##### _sample_benchmark

采样指定时间段的基准收益率。

**函数签名：**
```python
def _sample_benchmark(
    self,
    bench: pd.Series,
    trade_start_time: Union[str, pd.Timestamp],
    trade_end_time: Union[str, pd.Timestamp],
) -> Optional[float]
```

**返回值：**
- 类型：`Optional[float]`
- 说明：该时间段的基准收益率

##### is_empty

检查指标记录是否为空。

**函数签名：**
```python
def is_empty(self) -> bool
```

##### get_latest_date

获取最新的交易时间。

**函数签名：**
```python
def get_latest_date(self) -> pd.Timestamp
```

##### get_latest_account_value

获取最新的账户价值。

**函数签名：**
```python
def get_latest_account_value(self) -> float
```

##### get_latest_total_cost

获取最新的总交易成本。

**函数签名：**
```python
def get_latest_total_cost(self) -> Any
```

##### get_latest_total_turnover

获取最新的总换手额。

**函数签名：**
```python
def get_latest_total_turnover(self) -> Any
```

##### update_portfolio_metrics_record

更新投资组合指标记录。

**函数签名：**
```python
def update_portfolio_metrics_record(
    self,
    trade_start_time: Union[str, pd.Timestamp] = None,
    trade_end_time: Union[str, pd.Timestamp] = None,
    account_value: float | None = None,
    cash: float | None = None,
    return_rate: float | None = None,
    total_turnover: float | None = None,
    turnover_rate: float | None = None,
    total_cost: float | None = None,
    cost_rate: float | None = None,
    stock_value: float | None = None,
    bench_value: float | None = None,
) -> None
```

**参数说明：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `trade_start_time` | str/pd.Timestamp | 是 | 交易开始时间 |
| `trade_end_time` | str/pd.Timestamp | 否 | 交易结束时间 |
| `account_value` | float | 是 | 账户总价值（现金+证券） |
| `cash` | float | 是 | 现金余额 |
| `return_rate` | float | 是 | 收益率（不含交易费用） |
| `total_turnover` | float | 是 | 总换手额 |
| `turnover_rate` | float | 是 | 换手率 |
| `total_cost` | float | 是 | 总交易成本 |
| `cost_rate` | float | 是 | 交易成本率 |
| `stock_value` | float | 是 | 证券市值 |
| `bench_value` | float | 否 | 基准收益率（如果为 None，会自动计算） |

**使用示例：**
```python
# 更新每日指标
metrics.update_portfolio_metrics_record(
    trade_start_time="2020-01-02",
    trade_end_time="2020-01-03",
    account_value=1050000.0,
    cash=50000.0,
    return_rate=0.05,
    total_turnover=100000.0,
    turnover_rate=0.1,
    total_cost=1000.0,
    cost_rate=0.001,
    stock_value=1000000.0
)
```

##### generate_portfolio_metrics_dataframe

生成投资组合指标 DataFrame。

**函数签名：**
```python
def generate_portfolio_metrics_dataframe(self) -> pd.DataFrame
```

**返回值：**
- 类型：`pandas.DataFrame`
- 说明：包含以下列的DataFrame
  - `account`：账户总价值
  - `return`：收益率
  - `total_turnover`：总换手额
  - `turnover`：换手率
  - `total_cost`：总交易成本
  - `cost`：交易成本率
  - `value`：证券市值
  - `cash`：现金余额
  - `bench`：基准收益率

**使用示例：**
```python
# 获取指标 DataFrame
df = metrics.generate_portfolio_metrics_dataframe()
print(df.head())
```

##### save_portfolio_metrics

保存投资组合指标到 CSV 文件。

**函数签名：**
```python
def save_portfolio_metrics(self, path: str) -> None
```

**参数说明：**
- `path`：文件路径

**使用示例：**
```python
# 保存到文件
metrics.save_portfolio_metrics("/path/to/metrics.csv")
```

##### load_portfolio_metrics

从文件加载投资组合指标。

**函数签名：**
```python
def load_portfolio_metrics(self, path: str) -> None
```

**参数说明：**
- `path`：文件路径

**文件格式要求：**
CSV 文件必须包含以下列：
`['account', 'return', 'total_turnover', 'turnover', 'cost', 'total_cost', 'value', 'cash', 'bench']`

**使用示例：**
```python
# 从文件加载
metrics = PortfolioMetrics()
metrics.load_portfolio_metrics("/path/to/metrics.csv")
```

---

### Indicator

交易指标类，用于记录和分析交易执行的详细指标。

#### 初始化方法

**函数签名：**
```python
def __init__(self, order_indicator_cls: Type[BaseOrderIndicator] = NumpyOrderIndicator) -> None
```

**参数说明：**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `order_indicator_cls` | Type | NumpyOrderIndicator | 订单指标类类型 |

#### 指标说明

**订单级别指标：**

| 指标名 | 说明 |
|--------|------|
| `amount` | 外部策略给出的目标交易数量 |
| `deal_amount` | 实际成交数量 |
| `inner_amount` | 内部策略的总目标数量 |
| `trade_price` | 平均成交价 |
| `trade_value` | 总交易金额 |
| `trade_cost` | 总交易成本 |
| `trade_dir` | 交易方向 |
| `ffr` | 完全成交率（Full Fill Rate） |
| `pa` | 价格优势（Price Advantage） |
| `pos` | 胜率（Win Rate） |
| `base_price` | 基准价格 |
| `base_volume` | 基准成交量 |

**注意：**
- `base_price` 和 `base_volume` 不能为 NaN，即使该步没有交易
- `base_price` 不以聚合方式计算

---

#### 主要方法

##### reset

重置指标记录。

**函数签名：**
```python
def reset(self) -> None
```

##### record

记录当前时间的指标到历史记录。

**函数签名：**
```python
def record(self, trade_start_time: Union[str, pd.Timestamp]) -> None
```

##### update_order_indicators

更新订单级别指标。

**函数签名：**
```python
def update_order_indicators(self, trade_info: List[Tuple[Order, float, float, float]]) -> None
```

**参数说明：**

| 参数 | 类型 | 说明 |
|------|------|------|
| `trade_info` | List[Tuple] | 交易信息列表，每个元组包含：(Order, trade_value, trade_cost, trade_price) |

##### agg_order_indicators

聚合订单级别指标到交易级别指标。

**函数签名：**
```python
def agg_order_indicators(
    self,
    inner_order_indicators: List[BaseOrderIndicator],
    decision_list: List[Tuple[BaseTradeDecision, pd.Timestamp, pd.Timestamp]],
    outer_trade_decision: BaseTradeDecision,
    trade_exchange: Exchange,
    indicator_config: dict = {},
) -> None
```

**参数说明：**

| 参数 | 类型 | 说明 |
|------|------|------|
| `inner_order_indicators` | List[BaseOrderIndicator] | 内部执行器的订单指标列表 |
| `decision_list` | List[Tuple] | 决策列表，每个元组包含：(BaseTradeDecision, start_time, end_time) |
| `outer_trade_decision` | BaseTradeDecision | 外部交易决策 |
| `trade_exchange` | Exchange | 交易交易所对象 |
| `indicator_config` | dict | 指标配置，可包含 `pa_config` |

**indicator_config 配置项：**

```python
{
    "pa_config": {
        "agg": "twap",    # 或 "vwap"
        "price": "deal_price"  # 当前仅支持 deal_price
    }
}
```

##### cal_trade_indicators

计算交易级别指标。

**函数签名：**
```python
def cal_trade_indicators(
    self,
    trade_start_time: Union[str, pd.Timestamp],
    freq: str,
    indicator_config: dict = {},
) -> None
```

**参数说明：**

| 参数 | 类型 | 说明 |
|------|------|------|
| `trade_start_time` | str/pd.Timestamp | 交易开始时间 |
| `freq` | str | 交易频率 |
| `indicator_config` | dict | 指标配置 |

**indicator_config 配置项：**

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `show_indicator` | bool | False | 是否打印指标 |
| `ffr_config` | dict | {} | 完全成交率配置 |
| `pa_config` | dict | {} | 价格优势配置 |

**ffr_config 和 pa_config 配置：**

```python
{
    "weight_method": "mean",  # 或 "amount_weighted", "value_weighted"
}
```

##### get_order_indicator

获取订单级别指标。

**函数签名：**
```python
def get_order_indicator(self, raw: bool = True) -> Union[BaseOrderIndicator, Dict[Text, pd.Series]]
```

**参数说明：**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `raw` | bool | True | 是否返回原始对象 |

**返回值：**
- 如果 `raw=True`：返回 `BaseOrderIndicator` 对象
- 如果 `raw=False`：返回字典 `Dict[Text, pd.Series]`

##### get_trade_indicator

获取交易级别指标。

**函数签名：**
```python
def get_trade_indicator(self) -> Dict[str, Optional[BaseSingleMetric]]
```

**返回值：**
- 类型：`Dict[str, Optional[BaseSingleMetric]]`
- 说明：包含以下指标的字典：
  - `ffr`：完全成交率
  - `pa`：价格优势
  - `pos`：胜率
  - `deal_amount`：成交数量
  - `value`：成交金额
  - `count`：订单数量

##### generate_trade_indicators_dataframe

生成交易指标 DataFrame。

**函数签名：**
```python
def generate_trade_indicators_dataframe(self) -> pd.DataFrame
```

**返回值：**
- 类型：`pandas.DataFrame`
- 说明：包含所有交易指标的 DataFrame

---

## 完整使用流程示例

### 示例 1：PortfolioMetrics 使用

```python
import qlib
from qlib.backtest.report import PortfolioMetrics

# 初始化 QLib
qlib.init(provider_uri="~/.qlib/qlib_data/cn_data", region="cn")

# 创建投资组合指标记录器
metrics = PortfolioMetrics(
    freq="day",
    benchmark_config={
        "benchmark": "SH000905",
        "start_time": "2020-01-01",
        "end_time": "2020-12-31"
    }
)

# 在回测过程中每日更新指标
def update_daily_metrics(date, portfolio_info):
    metrics.update_portfolio_metrics_record(
        trade_start_time=date,
        trade_end_time=next_trading_day,
        account_value=portfolio_info['total_value'],
        cash=portfolio_info['cash'],
        return_rate=portfolio_info['return'],
        total_turnover=portfolio_info['turnover'],
        turnover_rate=portfolio_info['turnover_rate'] / portfolio_info['total_value'],
        total_cost=portfolio_info['cost'],
        cost_rate=portfolio_info['cost'] / portfolio_info['total_value'],
        stock_value=portfolio_info['stock_value']
    )

# 获取指标 DataFrame
df = metrics.generate_portfolio_metrics_dataframe()

# 计算累计收益
df['cumulative_return'] = (1 + df['return']).cumprod() - 1
df['cumulative_bench'] = (1 + df['bench']).cumprod() - 1

# 计算超额收益
df['excess_return'] = df['cumulative_return'] - df['cumulative_bench']

print(df.head())

# 保存指标
metrics.save_portfolio_metrics("/path/to/portfolio_metrics.csv")
```

### 示例 2：Indicator 使用

```python
from qlib.backtest.report import Indicator
from qlib.backtest.high_performance_ds import NumpyOrderIndicator

# 创建交易指标记录器
indicator = Indicator(order_indicator_cls=NumpyOrderIndicator)

# 更新订单级别指标
trade_info = [
    (order1, trade_value1, trade_cost1, trade_price1),
    (order2, trade_value2, trade_cost2, trade_price2),
]
indicator.update_order_indicators(trade_info)

# 计算交易级别指标
indicator.cal_trade_indicators(
    trade_start_time="2020-01-02",
    freq="day",
    indicator_config={
        "show_indicator": True,
        "ffr_config": {"weight_method": "value_weighted"},
        "pa_config": {"weight_method": "value_weighted"}
    }
)

# 记录到历史
indicator.record("2020-01-02")

# 重置以便下一个交易周期
indicator.reset()

# 获取历史指标 DataFrame
df = indicator.generate_trade_indicators_dataframe()
print(df.head())

# 保存指标
df.to_csv("/path/to/trade_indicators.csv")
```

### 示例 3：从文件加载指标并分析

```python
from qlib.backtest.report import PortfolioMetrics
import pandas as pd
import matplotlib.pyplot as plt

# 从文件加载
metrics = PortfolioMetrics()
metrics.load_portfolio_metrics("/path/to/portfolio_metrics.csv")

# 获取 DataFrame
df = metrics.generate_portfolio_metrics_dataframe()

# 分析
print("=== 回测绩效分析 ===")
print(f"初始资金: {df['account'].iloc[0]:,.2f}")
print(f"最终资金: {df['account'].iloc[-1]:,.2f}")
print(f"总收益率: {(df['account'].iloc[-1] / df['account'].iloc[0] - 1) * 100:.2f}%")
print(f"年化收益率: {(df['account'].iloc[-1] / df['account'].iloc[0]) ** (252 / len(df)) - 1 * 100:.2f}%")
print(f"总交易成本: {df['total_cost'].sum():,.2f}")
print(f"平均换手率: {df['turnover'].mean() * 100:.2f}%")

# 计算基准和超额收益
df['cumulative_return'] = (1 + df['return']).cumprod() - 1
df['cumulative_bench'] = (1 + df['bench']).cumprod() - 1
df['cumulative_excess'] = df['cumulative_return'] - df['cumulative_bench']

print(f"基准总收益: {df['cumulative_bench'].iloc[-1] * 100:.2f}%")
print(f"超额收益: {df['cumulative_excess'].iloc[-1] * 100:.2f}%")

# 绘制收益曲线
plt.figure(figsize=(12, 6))
plt.plot(df.index, df['cumulative_return'] * 100, label='策略')
plt.plot(df.index, df['cumulative_bench'] * 100, label='基准')
plt.plot(df.index, df['cumulative_excess'] * 100, label='超额')
plt.xlabel('日期')
plt.ylabel('累计收益率 (%)')
plt.title('累计收益曲线')
plt.legend()
plt.grid(True)
plt.savefig('/path/to/performance_chart.png')
plt.show()
```

### 示例 4：多级别交易指标聚合

```python
from qlib.backtest.report import Indicator
from qlib.backtest.high_performance_ds import NumpyOrderIndicator

# 创建多级指标记录器
outer_indicator = Indicator(order_indicator_cls=NumpyOrderIndicator)
inner_indicators = [
    Indicator(order_indicator_cls=NumpyOrderIndicator),
    Indicator(order_indicator_cls=NumpyOrderIndicator)
]

# 假设内部执行器已经更新了指标
# ...

# 聚合到外部级别
outer_indicator.agg_order_indicators(
    inner_order_indicators=[ind.order_indicator for ind in inner_indicators],
    decision_list=[
        (inner_decision1, start_time1, end_time1),
        (inner_decision2, start_time2, end_time2)
    ],
    outer_trade_decision=outer_decision,
    trade_exchange=exchange,
    indicator_config={
        "pa_config": {
            "agg": "vwap",
            "price": "deal_price"
        }
    }
)

# 计算外部级别的交易指标
outer_indicator.cal_trade_indicators(
    trade_start_time="2020-01-02",
    freq="day",
    indicator_config={"show_indicator": True}
)
```

---

## 指标计算公式

### 完全成交率（FFR）

FFR 度量订单的执行效率：

```
FFR = deal_amount / amount
```

**加权方法：**
- `mean`：简单平均
- `amount_weighted`：按成交数量加权
- `value_weighted`：按成交金额加权

### 价格优势（PA）

PA 度量成交价格相对于基准价格的优劣：

```
PA = sign * (trade_price / base_price - 1)
```

其中：
- `sign = 1 - trade_dir * 2`（买入为 1，卖出为 -1）
- 对于买入，PA > 0 表示成交价低于基准价（更有利）
- 对于卖出，PA > 0 表示成交价高于基准价（更有利）

### 胜率（POS）

POS 度量有利交易的比例：

```
POS = count(PA > 0) / count(PA != NaN)
```

---

## 注意事项

1. **基准数据**：确保基准配置正确，否则可能导致计算错误
2. **数据对齐**：所有指标的时间索引必须对齐
3. **基准价格**：`base_price` 不能为 NaN，即使该步没有交易
4. **持久化**：保存和加载指标时确保格式一致
5. **聚合方法**：多级指标聚合时需要确保使用同一个 Exchange 对象

---

## 相关模块

- `qlib.backtest.decision.Order`：订单类
- `qlib.backtest.exchange.Exchange`：交易所类
- `qlib.backtest.high_performance_ds`：高性能数据结构
- `qlib.utils.resam`：重采样工具
