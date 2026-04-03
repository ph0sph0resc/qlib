# ql qlib.rl.data.pickle_styled 模块文档

## 模块概述

`qlib.rl.data.pickle_styled` 模块提供了从 pickle 格式文件读取金融数据的工具。

**注意**：
- 这是 OPD 论文（https://seqml.github.io/opd/）使用的数据格式，**不是** Qlib 的标准数据格式
- 所有函数都使用 `@lru_cache` 包装，节省重复读取的 I/O 成本
- 建议使用 `get_xxx_yyy` 函数而不是 `XxxYyy` 类（虽然它们功能相同），因为前者针对缓存进行了优化
- Pickle 文件使用 Python 3.8 序列化，Python 3.7 以下版本可能无法加载

## 类型定义

### DealPriceType

```python
DealPriceType = Literal["bid_or_ask", "bid_or_ask_fill", "close"]
```

**说明**：几种成交价格的类型。

| 值 | 说明 |
|----|------|
| `"bid_or_ask"` | 如果卖出，使用 `$bid0` 列；如果买入，使用 `$ask0` 列 |
| `"bid_or_ask_fill"` | 基于 `"bid_or_ask"`，如果价格为 0，则使用另一个价格（`$ask0` / `$bid0`） |
| `"close"` | 使用收盘价（`$close0`）作为成交价格 |

## 主要组件

### SimpleIntradayBacktestData

```python
class SimpleIntradayBacktestData(BaseIntradayBacktestData)
```

**说明**：简单模拟器的回测数据。

#### 构造方法

```python
def __init__(
    self,
    data_dir: Path | str,
    stock_id: str,
    date: pd.Timestamp,
    deal_price: DealPriceType = "close",
    order_dir: int | None = None,
) -> None
```

**参数**：
- `data_dir`: 数据目录路径
- `stock_id`: 股票 ID
- `date`: 日期
- `deal_price`: 成交价格类型，默认为 "close"
- `order_dir`: 订单方向（如果 `deal_price` 不是 "close"，则必须提供）

#### 方法

##### `get_deal_price() -> pd.Series`

**说明**：返回可以用时间索引的成交价格序列。

**实现逻辑**：
- 根据 `deal_price_type` 选择合适的列
- 如果是 `"bid_or_ask_fill"`，价格为 0 时用另一个价格填充

##### `get_volume() -> pd.Series`

**说明**：返回可以用时间索引的成交量序列。

**实现**：返回 `self.data["$volume0"]`

##### `get_time_index() -> pd.DatetimeIndex`

**说明**：返回时间索引。

**实现**：返回 `self.data.index`

### PickleIntradayProcessedData

```python
class PickleIntradayProcessedData(BaseIntradayProcessedData)
```

**说明**：用于处理 pickle 格式数据的 `IntradayProcessedData` 子类。

#### 构造方法

```python
def __init__(
    self,
    data_dir: Path | str,
    stock_id: str,
    date: pd.Timestamp,
    feature_dim: int,
    time_index: pd.Index,
) -> None
```

**参数**：
- `data_dir`: 数据目录路径
- `stock_id`: 股票 ID
- `date`: 日期
- `feature_dim`: 特征维度
- `time_index`: 时间索引

**实现逻辑**：
1. 加载 pickle 数据
2. 推断列名（因为原始数据中没有包含）
3. 尝试新格式数据，如果失败则使用旧格式数据
4. 分离今天和昨天的数据

### PickleProcessedDataProvider

```python
class PickleProcessedDataProvider(ProcessedDataProvider)
```

**说明**：Pickle 格式处理数据的提供者。

#### 构造方法

```python
def __init__(self, data_dir: Path) -> None
```

**参数**：
- `data_dir`: 数据目录路径

## 辅助函数

### load_simple_intraday_backtest_data

```python
@lru_cache(maxsize=10)
def load_simple_intraday_backtest_data(
    data_dir: Path,
    stock_id: str,
    date: pd.Timestamp,
    deal_price: DealPriceType = "close",
    order_dir: int | None = None,
) -> SimpleIntradayBacktestData
```

**说明**：加载简单日内回测数据（带缓存）。

**缓存大小**：10 * ~40MB = ~400MB

### load_pickle_intraday_processed_data

```python
@cachetools.cached(cache=cachetools.LRUCache(100))
def load_pickle_intraday_processed_data(
    data_dir: Path,
    stock_id: str,
    date: pd.Timestamp,
    feature_dim: int,
    time_index: pd.Index,
) -> BaseIntradayProcessedData
```

**说明**：加载 pickle 格式处理数据（带缓存）。

**缓存大小**：100 * ~50KB = ~5MB

### load_orders

```python
def load_orders(
    order_path: Path,
    start_time: pd.Timestamp = None,
    end_time: pd.Timestamp = None,
) -> Sequence[Order]
```

**说明**：加载订单，并设置订单的开始时间和结束时间。

**参数**：
- `order_path`: 订单文件路径（可以是文件或目录）
- `start_time`: 开始时间，默认为 "0:00:00"
- `end_time`: 结束时间，默认为 "23:59:59"

**返回**：订单序列

**实现逻辑**：
1. 如果是文件，直接读取；如果是目录，合并所有文件
2. 处理旧格式的 "date" 列（重命名为 "datetime"）
3. 确保日期时间格式正确
4. 过滤掉数量为 0 的订单

## 使用示例

### 加载回测数据

```python
from pathlib import Path
import pandas as pd
from qlib.rl.data.pickle_styled import load_simple_intraday_backtest_data
from qlib.backtest.decision import OrderDir

data_dir = Path("/path/to/data")
stock_id = "AAPL"
date = pd.Timestamp("2020-01-01")

# 加载买入订单的数据
buy_data = load_simple_intraday_backtest_data(
    data_dir=data_dir,
    stock_id=stock_id,
    date=date,
    deal_price="bid_or_ask",
    order_dir=OrderDir.BUY
)

# 获取数据
prices = buy_data.get_deal_price()
volumes = buy_data.get_volume()
time_index = buy_data.get_time_index()
```

### 加载处理后的数据

```python
from pathlib import Path
import pandas as pd
from qlib.rl.data.pickle_styled import load_pickle_intraday_processed_data

data_dir = Path("/path/to/data")
stock_id = "AAPL"
date = pd.Timestamp("2020-01-01")
time_index = pd.date_range("09:30", "15:00", freq="1min")

# 加载处理数据
processed_data = load_pickle_intraday_processed_data(
    data_dir=data_dir,
    stock_id=stock_id,
    date=date,
    feature_dim=16,
    time_index=time_index
)

# 访问今天和昨天的数据
today = processed_data.today
yesterday = processed_data.yesterday
```

### 使用数据提供者

```python
from pathlib import Path
from qlib.rl.data.pickle_styled import PickleProcessedDataProvider

# 创建数据提供者
provider = PickleProcessedDataProvider(data_dir=Path("/path/to/data"))

# 获取数据
processed_data = provider.get_data(
    stock_id="AAPL",
    date=pd.Timestamp("2020-01-01"),
    feature_dim=16,
    time_index=time_index
)
```

### 加载订单

```python
from pathlib import Path
import pandas as pd
from qlib.rl.data.pickle_styled import load_orders

# 加载订单文件
orders = load_orders(
    order_path=Path("/path/to/orders.pkl"),
    start_time=pd.Timestamp("09:30:00"),
    end_time=pd.Timestamp("15:00:00")
)

# 遍历订单
for order in orders:
    print(f"Stock: {order.stock_id}")
    print(f"Amount: {order.amount}")
    print(f"Direction: {order.direction}")
    print(f"Start: {order.start_time}")
    print(f"End: {order.end_time}")
```

### 不同成交价格类型

```python
from qlib.backtest.decision import OrderDir

# 买入订单，使用 ask 价格
buy_data_bid_ask = load_simple_intraday_backtest_data(
    data_dir=data_dir,
    stock_id=stock_id,
    date=date,
    deal_price="bid_or_ask",
    order_dir=OrderDir.BUY
)

# 卖出订单，使用 bid 价格（如果价格为 0，则使用 ask 填充）
sell_data_fill = load_simple_intraday_backtest_data(
    data_dir=data_dir,
    stock_id=stock_id,
    date=date,
    deal_price="bid_or_ask_fill",
    order_dir=OrderDir.SELL
)

# 使用收盘价
close_data = load_simple_intraday_backtest_data(
    data_dir=data_dir,
    stock_id=stock_id,
    date=date,
    deal_price="close"
)
```

## 内部函数

### _infer_processed_data_column_names

```python
def _infer_processed_data_column_names(shape: int) -> List[str]
```

**说明**：根据数据形状推断列名。

**支持的形状**：
- `16`: 16 维特征（包括价格、成交量、买卖盘信息等）
- `6`: 6 维特征（高、低、开、收、均价、成交量）
- `5`: 5 维特征（高、低、开、收、成交量）

### _find_pickle

```python
def _find_pickle(filename_without_suffix: Path) -> Path
```

**说明**：查找 pickle 文件，支持 `.pkl` 和 `.pkl.backtest` 后缀。

**参数**：
- `filename_without_suffix`: 不带后缀的文件名

**返回**：找到的文件路径

**异常**：
- `FileNotFoundError`: 如果找不到文件
- `ValueError`: 如果找到多个匹配的文件

### _read_pickle

```python
@lru_cache(maxsize=10)
def _read_pickle(filename_without_suffix: Path) -> pd.DataFrame
```

**说明**：读取 pickle 文件并处理日期列（带缓存）。

**实现逻辑**：
1. 找到文件（支持多种后缀）
2. 读取 pickle
3. 将日期列转换为 datetime 类型
4. 恢复原始索引结构

## 注意事项

1. **Python 版本**：Pickle 文件使用 Python 3.8 序列化
2. **缓存管理**：注意缓存大小，避免内存溢出
3. **数据格式**：这是 OPD 论文格式，非 Qlib 标准格式
4. **列名推断**：原始数据没有列名，需要根据形状推断
5. **订单过滤**：`load_orders` 会过滤掉数量为 0 的订单

## 相关文档

- [base.md](./base.md) - 基类定义
- [native.md](./native.md) - 原生格式数据处理
- [integration.md](./integration.md) - 集成工具
