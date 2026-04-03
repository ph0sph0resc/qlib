# backtest/report.py 模块文档

## 文件概述

该模块实现了回测系统的报告和指标计算功能，负责计算投资组合指标和交易指标。报告类是回测系统生成分析结果的核心组件。

主要包含：
1. `PortfolioMetrics`: 投资组合指标类
2. `Indicator`: 交易指标类

## 类详解

### PortfolioMetrics 类

**继承关系:** 无

**类说明:** 投资组合指标类，用于记录和分析投资组合的日频表现。

**支持的指标:**
- `account`: 总资产价值（股票+现金）
- `return`: 收益率（不含交易成本）
- `total_turnover`: 累积换手率
- `turnover`: 换手率
- `total_cost`: 累积交易成本
- `cost`: 成本率
- `value`: 股票价值（不含现金）
- `cash`: 现金余额
- `bench`: 基准收益

#### 属性

**指标数据:**
- `accounts: OrderedDict` - 账户价值字典
- `returns: OrderedDict` - 收益率字典
- `total_turnovers: OrderedDict` - 累积换手率字典
- `turnovers: OrderedDict` - 换手率字典
- `total_costs: OrderedDict` - 累积成本字典
- `costs: OrderedDict` - 成本率字典
- `values: OrderedDict` - 股票价值字典
- `cashes: OrderedDict` - 现金字典
- `benches: OrderedDict` - 基准收益字典

**状态:**
- `latest_pm_time: Optional[pd.Timestamp]` - 最新的指标时间

**配置:**
- `freq: str` - 频率
- `benchmark_config: dict` - 基准配置
- `bench: Optional[pd.Series]` - 基准Series

#### 方法

##### __init__(self, freq: str = "day", benchmark_config: dict = {}) -> None

**功能:** 初始化投资组合指标

**参数说明:**
- `freq`: 交易频率（默认"day"）
- `benchmark_config`: 基准配置
  - `benchmark`: 基准代码或Series或list
  - `start_time`: 起始时间
  - `end_time`: 结束时间

**基準数据格式:**
1. **pd.Series**:
   - index: 交易日期
   - value: 从T-1到T的变化
2. **list**: 使用列表中股票的平均变化作为基準
3. **str**: 使用该股票代码的日变化作为基準

##### init_vars(self) -> None

**功能:** 初始化变量

##### init_bench(self, freq: str | None = None, benchmark_config: dict | None = None) -> None

**功能:** 初始化基准数据

##### _cal_benchmark(benchmark_config: Optional[dict], freq: str) -> Optional[pd.Series] [staticmethod]

**功能:** 计算基准数据

**返回值:** 基准Series或None

##### _sample_benchmark(self, bench: pd.Series, trade_start_time: Union[str, pd.Timestamp], trade_end_time: Union[str, pd.Timestamp]) -> Optional[float]

**功能:** 采样基准收益

**返回值:** 基准收益值

##### is_empty(self) -> bool

**功能:** 判断是否为空

**返回值:** True表示为空

##### get_latest_date(self) -> pd.Timestamp

**功能:** 获取最新日期

**返回值:** 最新日期

##### get_latest_account_value(self) -> float

**功能:** 获取最新账户价值

**返回值:** 账户价值

##### get_latest_total_cost(self) -> Any

**功能:** 获取最新总成本

**返回值:** 总成本

##### get_latest_total_turnover(self) -> Any

**功能:** 获取最新总换手率

**返回值:** 总换手率

##### update_portfolio_metrics_record(self, trade_start_time: Union[str, pd.Timestamp] = None, trade_end_time: Union[str, pd.Timestamp] = None, account_value: float | None = None, cash: float | None = None, return_rate: float | None = None, total_turnover: float | None = None, turnover_rate: float | None = None, total_cost: float | None = None, cost_rate: float | None = None, stock_value: float | None = None, bench_value: float | None = None) -> None

**功能:** 更新投资组合指标记录

**参数说明:**
- `trade_start_time`: 交易开始时间
- `trade_end_time`: 交易结束时间
- `account_value`: 账户价值
- `cash`: 现金余额
- `return_rate`: 收益率（含成本）
- `total_turnover`: 总换手率
- `turnover_rate`: 换手率
- `total_cost`: 总成本
- `cost_rate`: 成本率
- `stock_value`: 股票价值
- `bench_value`: 基准收益

##### generate_portfolio_metrics_dataframe(self) -> pd.DataFrame

**功能:** 生成投资组合指标DataFrame

**返回值:** 指标DataFrame

**返回格式:**
```python
# DataFrame结构
columns = [
    'account',      # 总资产价值
    'return',       # 收益率
    'total_turnover', # 累积换手率
    'turnover',     # 换手率
    'total_cost',   # 累积成本
    'cost',         # 成本率
    'value',        # 股票价值
    'cash',         # 现金
    'bench',        # 基准收益
]
index = trading_date  # 交易日期
```

##### save_portfolio_metrics(self, path: str) -> None

**功能:** 保存投资组合指标到文件

**参数说明:**
- `path`: 文件路径

##### load_portfolio_metrics(self, path: str) -> None

**功能:** 从文件加载投资组合指标

**参数说明:**
- `path`: 文件路径

**文件格式:**
```csv
datetime,account,return,total_turnover,turnover,total_cost,cost,value,cash,bench
2020-01-01,1000000.0,0.01,100000.0,0.01,1000.0,0.001,900000.0,100000.0,0.005
...
```

---

### Indicator 类

**继承关系:** 无

**类说明:** 交易指标类，用于计算和记录订单级别的交易指标。

**支持的交易指标:**

| 指标 | 说明 | 计算方式 |
|------|------|----------|
| amount | 目标交易数量 | 策略生成 |
| deal_amount | 实际成交数量 | 订单执行 |
| inner_amount | 内层总目标数量 | 内层决策累加 |
| trade_price | 平均成交价格 | 成交金额/数量 |
| trade_value | 总成交金额 | 成交价格×数量 |
| trade_cost | 总交易成本 | 开仓/平仓成本+冲击成本 |
| trade_dir | 交易方向 | BUY/SELL |
| ffr | 充填率 | deal_amount/amount |
| pa | 价格优势 | (成交价/基准价-1)×方向 |
| pos | 胜率 | (pa>0)的股票比例 |
| base_price | 基准价格 | 用于计算价格优势 |
| base_volume | 基准成交量 | 用于加权计算基准价格 |

**支持的交易指标:**

| 指标 | 说明 | 计算方式 |
|------|------|----------|
| ffr | 充填率 | 可选mean/amount_weighted/value_weighted |
| pa | 价格优势 | 可选mean/amount_weighted/value_weighted |
| pos | 胜率 | (pa>0)的比例 |
| deal_amount | 总成交数量 | 绝对值求和 |
| value | 总成交金额 | 绝对值求和 |
| count | 订单数量 | 统计订单数 |

#### 属性

**配置:**
- `order_indicator_cls: Type[BaseOrderIndicator]` - 订单指标类
- `indicator_config: dict` - 指标配置

**数据存储:**
- `order_indicator_his: dict` - 订单指标历史
- `trade_indicator_his: dict` - 交易指标历史

**当前数据:**
- `order_indicator: BaseOrderIndicator` - 当前订单指标
- `trade_indicator: Dict[str, Optional[BaseSingleMetric]]` - 当前交易指标

#### 方法

##### __init__(self, order_indicator_cls: Type[BaseOrderIndicator] = NumpyOrderIndicator) -> None

**功能:** 初始化交易指标

**参数说明:**
- `order_indicator_cls`: 订单指标类（默认NumpyOrderIndicator）

##### reset(self) -> None

**功能:** 重置指标

##### record(self, trade_start_time: Union[str, pd.Timestamp]) -> None

**功能:** 记录指标到历史

**参数说明:**
- `trade_start_time`: 交易开始时间

##### _update_order_trade_info(self, trade_info: List[Tuple[Order, float, float, float]]]) -> None

**功能:** 更新订单交易信息（内部方法）

**参数说明:**
- `trade_info`: 交易信息列表 [(order, trade_val, trade_cost, trade_price)]

##### _update_order_fulfill_rate(self) -> None

**功能:** 更新订单充填率

##### update_order_indicators(self, trade_info: List[Tuple[Order, float, float, float]]) -> None

**功能:** 更新订单指标

**参数说明:**
- `trade_info`: 交易信息列表

##### _agg_order_trade_info(self, inner_order_indicators: List[BaseOrderIndicator]) -> None

**功能:** 聚合订单交易信息（内部方法）

##### _update_trade_amount(self, outer_trade_decision: BaseTradeDecision) -> None

**功能:** 更新交易数量

##### _get_base_vol_pri(self, inst: str, trade_start_time: pd.Timestamp, trade_end_time: pd.Timestamp, direction: OrderDir, decision: BaseTradeDecision, trade_exchange: Exchange, pa_config: dict = {}) -> Tuple[Optional[float], Optional[float]]

**功能:** 获取基准量和价格（内部方法）

**返回值:** 元组 (base_volume, base_price)

##### _agg_base_price(self, inner_order_indicators: List[BaseOrderIndicator], decision_list: List[Tuple[BaseTradeDecision, pd.Timestamp, pd.Timestamp]], trade_exchange: Exchange, pa_config: dict = {}) -> None

**功能:** 聚合基准价格（内部方法）

##### _agg_order_price_advantage(self) -> None

**功能:** 聚合订单价格优势（内部方法）

##### agg_order_indicators(self, inner_order_indicators: List[BaseOrderIndicator], decision_list: List[Tuple[BaseTradeDecision, pd.Timestamp, pd.Timestamp]], outer_trade_decision: BaseTradeDecision, trade_exchange: Exchange, indicator_config: dict = {}) -> None

**功能:** 聚合订单指标

**参数说明:**
- `inner_order_indicators`: 内层订单指标列表
- `decision_list`: 决策列表
- `outer_trade_decision`: 外层交易决策
- `trade_exchange`: 交易所
- `indicator_config`: 指标配置

##### _cal_trade_fulfill_rate(self, method: str = "mean") -> Optional[BaseSingleMetric]

**功能:** 计算交易充填率

**参数说明:**
- `method`: 加权方法（mean/amount_weighted/value_weighted）

**返回值:** 充填率指标

##### _cal_trade_price_advantage(self, method: str = "mean") -> Optional[BaseSingleMetric]

**功能:** 计算交易价格优势

**参数说明:**
- `method`: 加权方法（mean/amount_weighted/value_weighted）

**返回值:** 价格优势指标

##### _cal_trade_positive_rate(self) -> Optional[BaseSingleMetric]

**功能:** 计算交易胜率

**返回值:** 胜率指标

##### _cal_deal_amount(self) -> Optional[BaseSingleMetric]

**功能:** 计算成交数量

**返回值:** 成交数量指标

##### _cal_trade_value(self) -> Optional[BaseSingleMetric]

**功能:** 计算成交金额

**返回值:** 成交金额指标

##### _cal_trade_order_count(self) -> Optional[BaseSingleMetric]

****功能:** 计算订单数量

**返回值:** 订单数量指标

##### cal_trade_indicators(self, trade_start_time: Union[str, pd.Timestamp], freq: str, indicator_config: dict = {}) -> None

**功能:** 计算交易指标

**参数说明:**
- `trade_start_time`: 交易开始时间
- `freq`: 频率
- `indicator_config`: 指标配置

##### get_order_indicator(self, raw: bool = True) -> Union[BaseOrderIndicator, Dict[Text, pd.Series]]

**功能:** 获取订单指标

**参数说明:**
- `raw`: 是否返回原始对象（True）或Series字典（False）

**返回值:** 订单指标对象或Series字典

##### get_trade_indicator(self) -> Dict[str, Optional[BaseSingleMetric]]

**功能:** 获取交易指标

**返回值:** 交易指标字典

##### generate_trade_indicators_dataframe(self) -> pd.DataFrame

**功能:** 生成交易指标DataFrame

**返回值:** 交易指标DataFrame

## 使用示例

### 使用PortfolioMetrics

```python
from qlib.backtest.report import PortfolioMetrics

# 创建投资组合指标
portfolio_metrics = PortfolioMetrics(
    freq="day",
    benchmark_config={
        "benchmark": "SH000300",  # 沪深300
        "start_time": "2020-01-01",
        "end_time": "2021-12-31",
    },
)

# 更新指标
portfolio_metrics.update_portfolio_metrics_record(
    trade_start_time=pd.Timestamp("2020-01-01"),
    trade_end_time=pd.Timestamp("2020-01-01"),
    account_value=1e6,
    cash=9e5,
    return_rate=0.01,
    total_turnover=1e5,
    turnover_rate=0.5,
    total_cost=1000,
    cost_rate=0.001,
    stock_value=9.9e5,
    bench_value=0.005,
)

# 生成DataFrame
df = portfolio_metrics.generate_portfolio_metrics_dataframe()
print(df)

# 保存到文件
portfolio_metrics.save_portfolio_metrics("portfolio_metrics.csv")

# 从文件加载
new_pm = PortfolioMetrics()
new_pm.load_portfolio_metrics("portfolio_metrics.csv")
```

### 使用Indicator

```python
from qlib.backtest.report import = Indicator
from qlib.backtest.high_performance_ds import NumpyOrderIndicator

# 创建交易指标
indicator = Indicator(order_indicator_cls=NumpyOrderIndicator)

# 更新订单指标
trade_info = [
    (order1, 10000, 15, 10.0),
    (order2, 5000, 7.5, 5.0),
]
indicator.update_order_indicators(trade_info)

# 计算交易指标
indicator.cal_trade_indicators(
    trade_start_time=pd.Timestamp("2020-01-01"),
    freq="day",
    indicator_config={
        "show_indicator": True,
        "pa_config": {
            "agg": "twap",
            "price": "$close",
        },
        "ffr_config": {
            'weight_method': 'value_weighted',
        }
    },
)

# 获取指标
order_indicator = indicator.get_order_indicator(raw=True)
trade_indicator = indicator.get_trade_indicator()

print(f"充填率: {trade_indicator['ffr']}")
print(f"价格优势: {trade_indicator['pa']}")
print(f"胜率: {trade_indicator['pos']}")

# 生成DataFrame
indicator_df = indicator.generate_trade_indicators_dataframe()
print(indicator_df)
```

## 相关模块

- `backtest.account.py`: 账户类，使用指标类
- `backtest.executor.py`: 执行器类，更新指标
- `backtest.high_performance_ds`: 高性能数据结构

## 重要概念

### 投资组合指标

投资组合指标记录每日的财务状态：

1. **account**: 总资产价值（股票+现金）
2. **return**: 收益率（考虑交易成本）
3. **turnover**: 换手率
4. **cost**: 成本率
5. **value**: 股票价值
6. **cash**: 现金余额
7. **bench**: 基准收益

### 交易指标

交易指标分析订单执行质量：

1. **ffr (充填率)**: 实际成交/目标数量
   - 反映订单执行能力
   - 可按mean/amount_weighted/value_weighted加权

2. **pa (价格优势)**: (成交价/基准价-1)×方向
   - 正值表示成交优于基准
   - 可按mean/amount_weighted/value_weighted加权

3. **pos (胜率)**: 胜率
   - 价格优势为正的订单比例
   - 反映交易选择质量

4. **deal_amount**: 总成交数量
5. **value**: 总成交金额
6. **count**: 订单数量

### 指标配置

支持多种指标配置：

```python
indicator_config = {
    "show_indicator": True,  # 是否显示指标
    "pa_config": {
        "agg": "twap",  # "twap"或"vwap"
        "price": "$close",  # 或使用交易所deal_price
    },
    "ffr_config": {
        'weight_method': 'mean',  # mean/amount_weighted/value_weighted
    },
}
```

### 基准数据

基準数据支持多种格式：

1. **pd.Series**: 直接提供基准序列
2. **list**: 使用列表股票的平均变化
3. **str**: 使用该股票代码的日变化

## 注意事项

1. **时间对齐**: 确保指标时间和交易日历对齐
2. **成本考虑**: 收益率考虑交易成本，与原回测定义一致
3. **基准缺失**: 基准数据缺失时会填充为0
4. **指标聚合**: 嵌套执行时指标会从内层聚合到外层
5. **价格优势**: 内层指标的价格优势无意义
6. **数据类型**: 指标类支持Pandas和Numpy两种实现
