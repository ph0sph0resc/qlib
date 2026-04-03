# qlib/rl/strategy/single_order.py 模块文档

## 文件概述
单订单策略模块，用于生成恰好一个订单的交易决策。

## 类与函数

### SingleOrderStrategy

```python
class SingleOrderStrategy(BaseStrategy):
    """用于生成恰好一个订单的交易策略。"""

    def __init__(
        self,
        order: Order,
        trade_range: TradeRange | None = None,
    ) -> None:
        super().__init__()

        self._order = order
        self._trade_range = trade_range

    def generate_trade_decision(
        self,
        execute_result: list | None = None,
    ) -> TradeDecisionWO:
        oh: OrderHelper = self.common_infra.get("trade_exchange").get_order_helper()
        order_list = [
            oh.create(
                code=self._order.stock_id,
                amount=self._order.amount,
                direction=self._order.direction,
            ),
        ]
        return TradeDecisionWO(order_list, self, self._trade_range)
```

单订单策略，生成恰好一个订单的交易决策。

#### 主要属性

- **_order**: `Order`
  - 要执行的订单对象
  - 包含股票代码、数量、方向、时间等信息

- **_trade_range**: `TradeRange | None`
  - 交易时间范围
  - 通常为`TradeRangeByTime`

#### 主要方法

1. **`generate_trade_decision(self, execute_result: list | None = None) -> TradeDecisionWO`**
   - 生成交易决策
   - 参数：
     - `execute_result`: 执行结果（此策略不使用）
   - 返回：包含单个订单的`TradeDecisionWO`

## 执行流程

```
策略初始化
    │
    ├─▶ order: Order
    │  └─▶ trade_range: TradeRange
    │
    ▼
generate_trade_decision()
    │
    ├─▶ 获取OrderHelper
    │  │   └─▶ oh = trade_exchange.get_order_helper()
    │
    ├─▶ 创建订单
    │  │   └─▶ oh.create(
    │  │           code=order.stock_id,
    │  │           amount=order.amount,
    │  │           direction=order.direction,
    │  │       )
    │
    └─▶ 返回TradeDecisionWO
```

## 使用示例

### 基本使用

```python
from qlib.rl.strategy.single_order import SingleOrderStrategy
from qlib.backtest import Order
from qlib.backtest.decision import TradeRangeByTime, OrderDir
import pandas as pd

# 创建订单
order = Order(
    stock_id="SH600000",
    amount=1000,
    direction=OrderDir.BUY,
    start_time=pd.Timestamp("2020-01-01 09:30:00"),
    end_time=pd.Timestamp("2020-01-01 14:59:00"),
)

# 创建交易范围
trade_range = TradeRangeByTime(
    start_time=pd.Timestamp("09:30:00"),
    end_time=pd.Timestamp("14:59:00"),
)

# 创建策略
strategy = SingleOrderStrategy(
    order=order,
    trade_range=trade_range,
)

# 生成交易决策
decision = strategy.generate_trade_decision()
print(decision)
```

### 在回测中使用

```python
from qlib.backtest import get_strategy_executor
from qlib.rl.strategy.single_order import SingleOrderStrategy

strategy_config = {
    "class": "SingleOrderStrategy",
    "module_path": "qlib.rl.strategy.single_order",
    "kwargs": {
        "order": order,
        "trade_range": trade_range,
    },
}

strategy, executor = get_strategy_executor(
    start_time=pd.Timestamp("2020-01-01"),
    end_time=pd.Timestamp("2020-01-02"),
    strategy=strategy_config,
    executor=executor_config,
    ...
)
```

## 与其他模块的关系

### qlib.backtest
- **Order**: 策略的输入
- **TradeRange**: 定义交易时间范围
- **OrderHelper**: 用于创建订单
- **BaseStrategy**: 策略的基类
- **TradeDecisionWO**: 交易决策类型

### qlib.rl.order_execution
- **SingleAssetOrderExecution**: 使用SingleOrderStrategy
- 通过策略获取订单执行配置

### qlib.strategy.base
- **BaseStrategy**: 继承自该基类
- 实现生成交易决策的接口

## 设计特点

### 1. 简单性
- 专门处理单个订单
- 不需要复杂的决策逻辑

### 2. 固定性
- 订单在创建时确定
- 方向、数量、时间都固定

### 3. 无状态
- 策略是无状态的
- 不依赖执行历史

### 4. 灵活性
- 可以轻松集成到其他系统
- 支持配置化

## 注意事项

1. **订单完整性**：确保订单参数完整
2. **时间范围**：trade_range应该与订单时间一致
3. **执行结果**：该策略不使用execute_result参数
4. **单次调用**：通常每个交易日只调用一次
