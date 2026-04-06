# qlib/rl/order_execution/state.py 模块文档

## 文件概述
定义订单执行的状态和指标数据结构。

## 类与函数

### SAOEMetrics

```python
class SAOEMetrics(TypedDict):
    """
    SAOE（单资产订单执行）在一个"周期"内累积的指标。
    可以是一天、一个时间段（例如30分钟）的累积，
    或者每分钟单独计算。

    Warnings
    --------
    类型提示是针对单个元素的。在很多情况下，
    它们可以被向量化。例如，``market_volume``可能是float列表（或ndarray）
    而不是单个float。
    """
```

SAOE指标类型定义。

#### 主要字段

**市场信息**：
- **stock_id**: `str`
  - 股票代码
- **datetime**: `pd.Timestamp | pd.DatetimeIndex`
  - 时间戳（这是DataFrame中的索引）
- **direction**: `int`
  - 订单方向（0=卖，1=买）
- **market_volume**: `np.ndarray | float`
  - 该期间的市场总成交量
- **market_price**: `np.ndarray | float`
  - 成交价格。如果是一段时间，则是市场平均成交价格

**策略记录**：
- **amount**: `np.ndarray | float`
  - 策略意图交易的总数量
- **inner_amount**: `np.ndarray | float`
  - 低层策略意图交易的总数量
  - **deal_amount**: `np.ndarray | float`
  - 成功生效的数量（必须小于等于inner_amount）
- **trade_price**: `np.ndarray | float`
  - 该策略的平均成交价格
- **trade_value**: `np.ndarray | float`
  - 交易的总价值。在简单模拟中，trade_value = deal_amount * price
- **position**: `np.ndarray | float`
  - 该"周期"后剩余的持仓

**累积指标**：
- **ffr**: `np.ndarray | float`
  - 完成了日订单的百分比
- **pa**: `np.ndarray | float`
  - 相对于基准（即使用TWAP策略执行该订单的成交价格）的价格优势
  - 请注意这里可能存在数据泄漏）
  - 单位为BP（基点，1/10000）

### SAOEState

```python
class SAOEState(NamedTuple):
    """持有SAOE模拟器状态的数据结构。"""
```

SAOE状态命名元组。

#### 主要字段

- **order**: `Order`
  - 我们正在处理的订单
- **cur_time**: `pd.Timestamp`
  - 当前时间，例如9:30
- **cur_step**: `int`
  - 当前步骤，例如0
- **position**: `float`
  - 当前剩余执行量
- **history_exec**: `pd.DataFrame`
  - 参考 `SingleAssetOrderExecution.history_exec`
- **history_steps**: `pd.DataFrame`
  - 参考 `SingleAssetOrderExecution.history_steps`
- **metrics**: `Optional[SAOEMetrics]`
  - 每日指标，仅在交易处于"done"状态时可用
- **backtest_data**: `BaseIntradayBacktestData`
  - 状态中包含回测数据
  - 实际上，只需要该数据的时间索引
  - 包含完整数据以便算法（例如VWAP）可以基于原始数据实现
  - 解释器可以按需使用，但应小心不要泄漏未来数据
- **ticks_per_step**: `int`
  - 每步的tick数
- **ticks_index**: `pd.DatetimeIndex`
  - 一天内所有可用的交易tick（不受订单限制），例如[9:30, 9:31, ..., 14:59]
- **ticks_for_order**: `pd.DatetimeIndex`
  - 被订单可交易的tick切片，例如[9:45, 9:46, ..., 14:44]

## 使用示例

### 创建SAOEState

```python
from qlib.rl.order_execution.state import SAOEState
From qlib.backtest import Order

order = Order(
    stock_id="SH600000",
    amount=1000,
    direction=OrderDir.BUY,
    start_time=pd.Timestamp("2020-01-01 09:30:00"),
    end_time=pd.Timestamp("2020-01-01 14:59:00"),
)

state = SAOEState(
    order=order,
    cur_time=pd.Timestamp("2020-01-01 09:30:00"),
    cur_step=0,
    position=1000,
    history_exec=pd.DataFrame(...),
    history_steps=pd.DataFrame(...),
    metrics=None,
    backtest_data=...,
    ticks_per_step=30,
    ticks_index=pd.DatetimeIndex(...),
    ticks_for_order=pd.DatetimeIndex(...),
)
```

### 访问指标

```python
# 在done时访问指标
if state.metrics:
    print(f"FFR: {state.metrics['ffr']}")
    print(f"PA: {state.metrics['pa']}")

# 访问历史
print(f"History steps: {len(state.history_steps)}")
print(f"History exec: {len(state.history_exec)}")
```

### 计算PA（价格优势）

```python
# PA计算公式
def calculate_price_advantage(exec_price, baseline_price, direction):
    if direction == OrderDir.BUY:
        # 买入：基准价格越小越好
        pa = (1 - exec_price / baseline_price) * 10000
    else:  # 卖出：基准价格越大越好
        pa = (exec_price / baseline_price - 1) * 10000
    return pa  # 单位：BP
```

## 数据流

```
订单执行过程
    │
    ├─▶ 初始化
    │     │
    │     └─▶ SAOEState(
    │           order=订单,
    │           cur_time=开始时间,
    │           cur_step=0,
    │           position=订单数量,
    │           history_exec=[],
    │           history_steps=[],
    │           ...)
    │
    └─▶ while not done():
    │     │
    │     ├─▶ 获取动作
    │     │     │
    │     │     └─▶ action = policy(observation)
    │     │
    │     ├─▶ 执行动作
    │     │     │
    │     │     ├─▶ 执行交易
    │     │     │
    │     │     └─▶ 更新状态
    │     │         cur_time += timedelta
    │     │         cur_step += 1
    │     │         position -= 成交量
    │     │
    │     │     └─▶ 记录指标
    │     │         history_steps.append({
    │     │             datetime=cur_time,
    │     │             position=position,
    │     │             pa=calculate_pa(),
    │     │             ...
    │     │         })
    │     │
    │     └─▶ 检查是否完成
    │         if position <= 0 or cur_time >= 订单结束时间:
    │             metrics = 计算最终指标()
    │             break
    │
    └─▶ 返回最终状态（包含metrics）
```

## 与其他模块的关系

### qlib.rl.order_execution.simulator_simple
- **SingleAssetOrderExecutionSimple**: 使用SAOEState
- 维护状态和指标

### qlib.rl.order_execution.simulator_qlib
- **SingleAssetOrderExecution**: 使用SAOEState
- 与Qlib回测集成

### qlib.rl.order_execution.reward
- **PAPenaltyReward**: 基于SAOEState计算奖励
- 使用SAOEMetrics中的PA指标

### qlib.rl.order_execution.interpreter
- **StateInterpreter**: 从SAOEState创建观测
- 可以访问所有状态字段

## 设计原则

### 1. 不可变性
- 使用NamedTuple确保状态不可变
- 避免意外修改

### 2. 类型安全
- 使用TypedDict定义指标
- 清晰的字段类型

### 3. 性能优化
- 使用DataFrame存储历史
- 避免深拷贝

### 4. 可扩展性
- 可以添加自定义字段
- 向后兼容
