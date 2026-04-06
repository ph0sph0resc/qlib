# qlib.rl.data.native 模块文档

## 模块概述

`qlib.rl.data.native` 模块提供了 Qlib 原生格式（Handler 格式）的数据处理功能。

该模块包括：

- 日内回测数据类
- 数据帧回测数据类
- 处理后的数据类
- 数据加载和缓存函数

## 主要组件

### IntradayBacktestData

```python
class IntradayBacktestData(BaseIntradayBacktestData)
```

**说明**：Qlib 模拟器的回测数据。

#### 构造方法

```python
def __init__(
    self,
    order: Order,
    exchange: Exchange,
    ticks_index: pd.DatetimeIndex,
    ticks_for_order: pd.DatetimeIndex,
) -> None
```

**参数**：
- `order`: 订单对象
- `exchange`: 交易所对象
- `ticks_index`: 所有刻度的时间索引
- `ticks_for_order`: 订单范围内的刻度时间索引

#### 方法

##### `get_deal_price() -> pd.Series`

**说明**：返回成交价格序列。

**实现**：通过 `exchange.get_deal_price()` 获取

##### `get_volume() -> pd.Series`

**说明**：返回成交量序列。

**实现**：通过 `exchange.get_volume()` 获取

##### `get_time_index() -> pd.DatetimeIndex`

**说明**：返回时间索引。

**实现**：从交易所的报价数据中提取

### DataframeIntradayBacktestData

```python
class DataframeIntradayBacktestData(BaseIntradayBacktestData)
```

**说明**：从数据帧创建的回测数据。

#### 构造方法

```python
def __init__(
    self,
    df: pd.DataFrame,
    price_column: str = "$close0",
    volume_column: str = "$volume0"
) -> None
```

**参数**：
- `df`: 包含回测数据的 DataFrame
- `price_column`: 价格列名，默认为 "$close0"
- `volume_column`: 成交量列名，默认为 "$volume0"

#### 方法

##### `get_deal_price() -> pd.Series`

**说明**：返回价格序列。

**实现**：返回 `self.df[self.price_column]`

##### `get_volume() -> pd.Series`

**说明**：返回成交量序列。

**实现**：返回 `self.df[self.volume_column]`

##### `get_time_index() -> pd.DatetimeIndex`

**说明**：返回时间索引。

**实现**：返回 `self.df.index`

### HandlerIntradayProcessedData

```python
class HandlerIntradayProcessedData(BaseIntradayProcessedData)
```

**说明**：用于处理 Handler（二进制格式）风格数据的子类。

#### 构造方法

```python
def __init__(
    self,
    data_dir: Path,
    stock_id: str,
    date: pd.Timestamp,
    feature_columns_today: List[str],
    feature_columns_yesterday: List[str],
    backtest: bool = False,
    index_only: bool = False,
) -> None
```

**参数**：
- `data_dir`: 数据目录路径
- `stock_id`: 股票 ID
- `date`: 日期
- `feature_columns_today`: 今天数据的特征列
- `feature_columns_yesterday`: 昨天数据的特征列
- `backtest`: 是否使用回测数据，默认为 False
- `index_only`: 是否只加载索引，默认为 False

**实现逻辑**：
1. 构建文件路径（根据 `backtest` 选择子目录）
2. 使用安全的方式加载 pickle 文件
3. 使用 Handler 获取数据
4. 根据 `index_only` 决定是否加载特征数据

### HandlerProcessedDataProvider

```python
class HandlerProcessedDataProvider(ProcessedDataProvider)
```

**说明**：Handler 格式处理数据的提供者。

#### 构造方法

```python
def __init__(
    self,
    data_dir: str,
    feature_columns_today: List[str],
    feature_columns_yesterday: List[str],
    backtest: bool = False,
) -> None
```

**参数**：
- `data_dir`: 数据目录路径
- `feature_columns_today`: 今天数据的特征列
- `feature_columns_yesterday`: 昨天数据的特征列
- `backtest`: 是否使用回测数据，默认为 False

## 辅助函数

### get_ticks_slice

```python
def get_ticks_slice(
    ticks_index: pd.DatetimeIndex,
    start: pd.Timestamp,
    end: pd.Timestamp,
    include_end: bool = False,
) -> pd.DatetimeIndex
```

**说明**：获取时间范围内的刻度。

**参数**：
- `ticks_index`: 完整的刻度时间索引
- `start`: 开始时间
- `end`: 结束时间
- `include_end`: 是否包含结束时间，默认为 False

**返回**：切片后的时间索引

### load_backtest_data

```python
@cachetools.cached(cache=cachetools.LRUCache(100))
def load_backtest_data(
    order: Order,
    trade_exchange: Exchange,
    trade_range: TradeRange,
) -> IntradayBacktestData
```

**说明**：加载回测数据（带缓存）。

**参数**：
- `order`: 订单对象
- `trade_exchange`: 交易交易所
- `trade_range`: 交易范围

**返回**：回测数据对象

**实现逻辑**：
1. 从交易所获取完整的刻度索引
2. 根据订单时间范围筛选刻度
3. 如果是时间范围，使用 `get_ticks_slice` 获取刻度
4. 创建回测数据对象

### load_handler_intraday_processed_data

```python
@cachetools.cached(cache=cachetools.LRUCache(100))
def load_handler_intraday_processed_data(
    data_dir: Path,
    stock_id: str,
    date: pd.Timestamp,
    feature_columns_today: List[str],
    feature_columns_yesterday: List[str],
    backtest: bool = False,
    index_only: bool = False,
) -> HandlerIntradayProcessedData
```

**说明**：加载 Handler 格式处理数据（带缓存）。

**参数**：
- `data_dir`: 数据目录路径
- `stock_id`: 股票 ID
- `date`: 日期
- `feature_columns_today`: 今天数据的特征列
- `feature_columns_yesterday`: 昨天数据的特征列
- `backtest`: 是否使用回测数据
- `index_only`: 是否只加载索引

**返回**：处理后的数据对象

## 使用示例

### 使用 DataFrame 创建回测数据

```python
import pandas as pd
from qlib.rl.data.native import DataframeIntradayBacktestData

# 创建 DataFrame
df = pd.DataFrame({
    '$close0': [100.0, 101.0, 102.0],
    '$volume0': [1000, 2000, 1500]
}, index=pd.date_range('09:30', '09:32', freq='1min'))

# 创建回测数据
backtest_data = DataframeIntradayBacktestData(
    df=df,
    price_column='$close0',
    volume_column='$volume0'
)

# 获取数据
prices = backtest_data.get_deal_price()
volumes = backtest_data.get_volume()
```

### 使用交易所创建回测数据

```python
from qlib.rl.data.native import load_backtest_data
from qlib.backtest import Exchange, Order
from qlib.backtest.decision import TradeRangeByTime

# 创建交易所和订单
exchange = Exchange(...)
order = Order(...)
trade_range = TradeRangeByTime(start_time='09:30', end_time='15:00')

# 加载回测数据
backtest_data = load_backtest_data(
    order=order,
    trade_exchange=exchange,
    trade_range=trade_range
)
```

### 使用 Handler 加载处理数据

```python
from pathlib import Path
import pandas as pd
from qlib.rl.data.native import HandlerProcessedDataProvider

# 定义特征列
feature_columns_today = [
    "$open", "$high", "$low", "$close", "$vwap",
    "$bid", "$ask", "$volume", "$bidV", "$askV"
]
feature_columns_yesterday = [f"{c}_1" for c in feature_columns_today]

# 创建数据提供者
provider = HandlerProcessedDataProvider(
    data_dir="/path/to/data",
    feature_columns_today=feature_columns_today,
    feature_columns_yesterday=feature_columns_yesterday,
    backtest=False
)

# 获取数据
processed_data = provider.get_data(
    stock_id="AAPL",
    date=pd.Timestamp("2020-01-01"),
    feature_dim=10,
    time_index=pd.date_range("09:30", "15:00", freq="1min")
)

# 访问数据
today_data = processed_data.today
yesterday_data = processed_data.yesterday
```

### 只加载索引

```python
from qlib.rl.data.native import load_handler_intraday_processed_data

# 只加载索引，不加载特征数据（节省内存）
processed_data = load_handler_intraday_processed_data(
    data_dir=Path("/path/to/data"),
    stock_id="AAPL",
    date=pd.Timestamp("2020-01-01"),
    feature_columns_today=feature_columns_today,
    feature_columns_yesterday=feature_columns_yesterday,
    index_only=True
)

# today 和 yesterday 只包含索引，没有特征数据
```

## 性能优化

### 缓存配置

```python
# load_backtest_data 使用订单的 day key 作为缓存键
@cachetools.cached(cache=cachetools.LRUCache(100))
def load_backtest_data(...):
    ...

# load_handler_intraday_processed_data 使用 (stock_id, date, backtest, index_only) 作为缓存键
@cachetools.cached(cache=cachetools.LRUCache(100))
def load_handler_intraday_processed_data(...):
    ...
```

### 索引优化

```python
# 使用 index_only=True 可以大幅减少内存使用
processed_data = provider.get_data(
    stock_id="AAPL",
    date=pd.Timestamp("2020-01-01"),
    feature_dim=feature_dim,
    time_index=time_index
)

# 在数据提供者内部设置 index_only
provider = HandlerProcessedDataProvider(
    data_dir=data_dir,
    feature_columns_today=feature_columns_today,
    feature_columns_yesterday=feature_columns_yesterday,
    backtest=False
)

# 修改提供者的 get_data 方法...
```

## 安全性

该模块使用 `restricted_pickle_load` 来安全地加载 pickle 文件，避免潜在的安全风险。

```python
from qlib.utils.pickle_utils import restricted_pickle_load

path = os.path.join(data_dir, "backtest" if backtest else "feature", f"{stock_id}.pkl")
with open(path, "rb") as fstream:
    dataset = restricted_pickle_load(fstream)  # 安全加载
```

## 注意事项

1. **缓存键**：确保缓存键能够正确区分不同的数据
2. **内存管理**：使用 `index_only=True` 可以节省内存
3. **安全性**：始终使用 `restricted_pickle_load` 加载文件
4. **时间范围**：注意 `include_end` 参数的含义
5. **特征列匹配**：确保 today 和 yesterday 的特征列数量一致

## 相关文档

- [base.md](./base.md) - 基类定义
- [pickle_styled.md](./pickle_styled.md) - Pickle 格式数据处理
- [integration.md](./integration.md) - 集成工具
