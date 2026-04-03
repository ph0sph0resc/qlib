# qlib.rl.data 模块文档

## 模块概述

`qlib.rl.data` 模块提供了强化学习回测所需的数据处理功能，包括：

- 原始市场数据的加载和处理
- 数据清理和特征工程
- 多种数据格式支持（Pickle 格式、Handler 格式等）
- 数据缓存机制以提高性能

## 子模块

| 子模块 | 说明 |
|--------|------|
| `base` | 回测数据的基类定义 |
| `pickle_styled` | Pickle 格式数据的处理 |
| `native` | Qlib 原生格式数据的处理 |
| `integration` | 与 NeuTrader 等外部工具的集成 |

## 核心概念

### 回测数据类型

1. **BaseIntradayBacktestData**：原始市场数据
   - 成交价格
   - 成交量
   - 时间索引

2. **BaseIntradayProcessedData**：处理后的市场数据
   - "今天"的数据
   - "昨天"的数据（用于辅助决策）

### 数据提供者

**ProcessedDataProvider**：处理数据的提供者接口，用于获取特定股票和日期的处理数据。

## 数据格式

### Pickle 格式

- 用于 OPD 论文的数据格式
- 非 Qlib 标准格式
- 使用 Python 3.8 序列化
- 需要缓存优化以避免重复读取

### Handler 格式

- Qlib 的标准二进制格式
- 通过 Handler 读取
- 支持特征列配置

## 使用示例

### 加载回测数据

```python
from qlib.rl.data.pickle_styled import load_simple_intraday_backtest_data
from pathlib import Path
import pandas as pd

data_dir = Path("/path/to/data")
stock_id = "AAPL"
date = pd.Timestamp("2020-01-01")

# 加载简单回测数据
backtest_data = load_simple_intraday_backtest_data(
    data_dir=data_dir,
    stock_id=stock_id,
    date=date,
    deal_price="close"
)

# 获取数据
prices = backtest_data.get_deal_price()
volumes = backtest_data.get_volume()
time_index = backtest_data.get_time_index()
```

### 加载处理后的数据

```python
from qlib.rl.data.pickle_styled import PickleProcessedDataProvider
import pandas as pd

# 创建数据提供者
provider = PickleProcessedDataProvider(data_dir=data_dir)

# 获取处理后的数据
processed_data = provider.get_data(
    stock_id="AAPL",
    date=pd.Timestamp("2020-01-01"),
    feature_dim=16,
    time_index=time_index
)

# 访问今天和昨天的数据
today_data = processed_data.today
yesterday_data = processed_data.yesterday
```

### 加载订单

```python
from qlib.rl.data.pickle_styled import load_orders
from pathlib import Path

# 加载订单
orders = load_orders(
    order_path=Path("/path/to/orders.pkl"),
    start_time=pd.Timestamp("09:30:00"),
    end_time=pd.Timestamp("15:00:00")
)

for order in orders:
    print(f"Stock: {order.stock_id}, Amount: {order.amount}")
```

## 性能优化

### 缓存机制

模块中的数据加载函数都使用了缓存机制：

```python
# 使用 lru_cache 缓存
@lru_cache(maxsize=10)
def _read_pickle(filename_without_suffix: Path) -> pd.DataFrame:
    ...

# 使用 cachetools 缓存
@cachetools.cached(cache=cachetools.LRUCache(100))
def load_handler_intraday_processed_data(...):
    ...
```

### 内存估计

- `_read_pickle` 缓存：10 * ~40MB = ~400MB
- `load_xxx` 缓存：100 * ~50KB = ~5MB

## 注意事项

1. **Python 版本**：Pickle 文件使用 Python 3.8 序列化，低于 3.7 的版本可能无法加载
2. **数据格式**：Pickle 格式是 OPD 论文格式，非 Qlib 标准格式
3. **缓存管理**：注意缓存大小，避免内存溢出
4. **数据验证**：使用前验证数据维度和列名
5. **线程安全**：缓存机制在多线程环境下需要注意

## 相关文档

- [base.md](./base.md) - 基类定义文档
- [pickle_styled.md](./pickle_styled.md) - Pickle 格式数据处理文档
- [native.md](./native.md) - 原生数据处理文档
- [integration.md](./integration.md) - 集成工具文档
