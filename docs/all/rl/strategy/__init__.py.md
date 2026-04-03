# qlib/rl/strategy/__init__.py 模块文档

## 文件概述
strategy模块的__init__.py文件，当前为空文件。

## 模块结构

```
qlib/rl/strategy/
└── single_order.py    # 单订单策略
```

## 模块功能

### single_order.py
提供用于生成精确一个订单的交易决策的策略：
- **SingleOrderStrategy**: 单订单策略基类

## 使用场景

### 单订单执行
在单订单执行场景中，策略需要生成恰好一个订单的交易决策。

```python
from qlib.backtest import Order
from qlib.backtest.decision import TradeRangeByTime

order = Order(
    stock_id="SH600000",
    amount=1000,
    direction=OrderDir.BUY,
    start_time=pd.Timestamp("2020-01-01 09:30:00"),
    end_time=pd.Timestamp("2020-01-01 14:59:00"),
)

trade_range = TradeRangeByTime(
    start_time=pd.Timestamp("09:30:00"),
    end_time=pd.Timestamp("14:59:00"),
)
```

## 与其他模块的关系

### qlib.backtest
- **Order**: 策略的输入
- **TradeRange**: 定义交易时间范围
- **BaseStrategy**: SingleOrderStrategy的基类
- **OrderHelper**: 用于创建订单

### qlib.rl.order_execution
- **SingleAssetOrderExecution**: 使用SingleOrderStrategy
- 通过策略获取订单执行配置

### qlib.strategy.base
- 提供策略基类
- 定义生成交易决策的接口

## 扩展性

1. **简单性**: 专门针对单订单场景
2. **清晰性**: 只生成一个订单，逻辑简单
3. **可扩展**: 可以继承添加自定义逻辑

## 注意事项

1. **场景限制**: 只适用于单订单执行
2. **时间范围**: 需要正确定交易时间范围
3. **方向固定**: 订单方向在创建时确定
