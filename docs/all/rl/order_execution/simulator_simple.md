# qlib/rl/order_execution/simulator_simple.md 模块文档

## 文件概述
简化的单资产订单执行（SAOE）模拟器。与基于Qlib回测的版本不同，该模拟器直接使用pickle风格的市场数据。

## 类与函数

### SingleAssetOrderExecutionSimple

```python
class SingleAssetOrderExecutionSimple(Simulator[Order, SAOEState, float]):
    """单资产订单执行（SAOE）模拟器。

    由于没有"日历"在简单位器中，使用ticks进行交易。
。
    tick是pickle风格数据文件中的一条记录（行）。
    每个tick都被视为一个独立的交易机会。
    如果不需要这样细的粒度，使用 ``ticks_per_step``来
    延长每步的ticks。

    在每一步中，交易数量被"均匀地"分到每个tick，
    然后受交易量最大执行量（即 ``vol_threshold``）的限制，
    如果是最后一步，尝试确保所有数量都被执行。

    参数
    ----------
    order
        启动SAOE模拟器的种子是一个订单。
    data_dir
        加载回测数据的路径。
    feature_columns_today
        今天特征的特征列。
    feature_columns_yesterday
        昨天特征的特征列。
    data_granularity
        连续数据条目之间的tick数。
    ticks_per_step
        每步的tick数。
    vol_threshold
        最大执行量（除以市场执行量）。
    """
```

#### 主要属性

**状态属性**：
- **order**: `Order`
  - 待处理的订单
- **position**: `float`
  - 当前剩余待执行的数量
- **cur_time**: `pd.Timestamp`
  - 当前时间
- **cur_step**: `int`
  - 当前步骤数

**历史记录**：
- **history_exec**: `pd.DataFrame`
  - 每个可能交易时间点的所有执行历史
  - 索引为datetime
  - 包含SAOEMetrics的所有字段

- **history_steps**: `pd.DataFrame`
  - 每个步骤的位置
  - 索引为datetime（步骤的开始时间）
  - 包含SAOEMetrics的所有字段

**指标**：
- **metrics**: `Optional[SAOEMetrics]`
  - 仅在done时可用
  - 包含整个订单周期的累积指标

**价格基准**：
- **twap_price**: `float`
  - 用于计算价格优势的基准价格
  - 定义为订单开始时间到结束时间内的平均价格

**数据**：
- **ticks_index**: `pd.Datetime的所有可用tick（不受订单限制）`
- **ticks_for_order**: `pd.DatetimeIndex`
  - 可用于交易的tick切片（按订单限制）`

#### 主要方法

1. **`__init__(self, order, data_dir, feature_columns_today, feature_columns_yesterday, data_granularity, ticks_per_step, vol_threshold)`**
   - 初始化模拟器
   - 加载回测数据
   - 初始化状态和指标

2. **`step(self, amount: float) -> None`**
   - 执行SAOE的一步
   - 参数：
     - `amount`: 希望交易的数量
  . 注意：模拟器不保证所有数量都能成功交易
  . 执行流程：
     1. 根据市场成交量限制拆分交易量
     2. 更新内部状态
     3. 记录执行历史
     4. 计算指标（如果done）

3. **`get_state(self) -> SAOEState`**
   - 返回当前状态

4. **`done(self) -> bool`**
   - 检查是否完成
   - 条件：position < 1e-6 或 cur_time >= order.end_time

5. **`get_backtest_data(self) -> BaseIntradayBacktestData`**
   - 获取回测数据
   - 支持handler格式和pickle格式

6. **`_split_exec_vol(self, exec_vol_sum: float) -> np.ndarray`**
   - 将交易量拆分到每分钟
   - 应用交易量限制
   - 在最后一步确保完成所有数量

7. **`_metrics_collect(self, datetime, market_vol, market_price, amount, exec_vol) -> SAOEMetrics`**
   - 收集单个步骤的指标
   - 计算FFR、PA等指标

## 执行流程

```
初始化
  │
  ├─▶ 加载回测数据
  │     │
  │     ├─▶ 尝试handler格式（native.py）
  │     │. └─▶ 成功 → 使用HandlerIntradayBacktestData
  │     │
  │     └─▶ 失败 → 尝试pickle格式（pickle_styled.py）
  │         │. └─▶ 使用SimpleIntradayBacktestData
  │
  ├─▶ 初始化状态
  │     │
  │     ├─▶ position = order.amount
  │     ├─▶ cur_time = ticks_for_order[0]
  │     └─▶ cur_step = 0
  │
  └─▶ 计算TWAP价格
      │
      └─▶ while not done():
              │
              ├─▶ 获取动作: amount = policy(obs)
              │
              ├─▶ step(amount)
              │     │
              │     ├─▶ 获取市场数据（backtest_data）
              │     │
              │     ├─▶ 拆分交易量（均匀分到各tick）
              │     │. └─▶ exec_vol = amount / len(market_ticks)
              │     │
              │     ├─▶ 应用交易量限制
              │     │. └─▶ exec_vol = min(exec_vol, vol_threshold * market_volume)
              │     │
              │     ├─▶ 在最后一步强制完成
              │     │. └─▶ exec_vol[-1] += position - sum(exec_vol)
              │     │
              │     ├─▶ 计算成交价格和成交量
              │     ├─▶ 更新position -= sum(exec_vol)
              │     ├─▶ 记录执行历史
              │     ├─▶ 计算指标（FFR、PA等）
              │     ├─▶ 检查是否完成
              │     └─▶ done = position < EPS or cur_time >= order.end_time
              │
              └─▶ 更新cur_time和cur_step
```

## TWAP策略

交易量按TWAP（时间加权平均价格）策略分配：

```python
# 每个tick分配相同数量
exec_vol = np.repeat(amount / len(market_ticks), len(market_ticks))

# 应用交易量限制
exec_vol = np.minimum(exec_vol, vol_threshold * market_volume)

# 在最后一步确保完成
if is_last_step:
    exec_vol[-1] += position - exec_vol.sum()
```

## 指标计算

### FFR（完成比例）
```python
ffr = deal_amount / order.amount
```

### PA（价格优势）
```python
# 买入：TWAP价格越低越好
if direction == OrderDir.BUY:
    pa = (1 - exec_price / twap_price) * 10000

# 卖出：TWAP价格越高越好
else:
    pa = (exec_price / twap_price - 1) * 10000
```

## 使用示例

```python
from qlib.rl.order_execution import SingleAssetOrderExecutionSimple
from qlib.backtest import Order
import pandas as pd

# 创建订单
order = Order(
    stock_id="SH600000",
    amount=1000,
    direction=OrderDir.BUY,
    start_time=pd.Timestamp("2020-01-01 09:30:00"),
    end_time=pd.Timestamp("2020-01-01 14:59:00"),
)

# 创建模拟器
simulator = SingleAssetOrderExecutionSimple(
    order=order,
    data_dir=Path("/path/to/data"),
    feature_columns_today=["$open", "$close", "$volume"],
    feature_columns_yesterday=["$open_1", "$close_1", "$volume_1"],
    data_granularity=1,  # 每分钟一个数据点
    ticks_per_step=30,        # 每30分钟一个决策
    vol_threshold=0.1,       # 不超过市场成交量的10%
)

# 执行订单
while not simulator.done():
    state = simulator.get_state()

    # 获取观测
    obs = {
        "position": state.position / state.order.amount,
        "cur_step": state.cur_step,
        "cur_time": state.cur_time,
    }

    # 获取动作（这里使用TWAP）
    remaining_steps = len(state.ticks_for_order) // simulator.ticks_per_step
    twap_amount = state.position / remaining_steps
    action = min(state.position, twap_amount)

    # 执行一步
    simulator.step(action)

# 访问最终指标
if simulator.metrics:
    print(f"Final FFR: {simulator.metrics['ffr']:.4f}")
    print(f"Final PA: {simulator.metrics['pa']:.4f}")
```

## 与其他模块的关系

### qlib.rl.order_execution.state
- **SAOEState**: 模拟器返回的状态类型
- **SAOEMetrics**: 历史记录和指标的类型定义

### qlib.rl.data.pickle_styled
- **SimpleIntradayBacktestData**: 用于加载回测数据
- **PickleIntradayProcessedData**: 用于加载已处理特征

### qlib.rl.data.native
- **HandlerIntradayProcessedData**: 如果可用，用作备选数据源

### qlib.rl.order_execution.simulator_qlib
- **SingleAssetOrderExecution**: 基于Qlib回测的实现
- 该实现功能更完整，但依赖Qlib回测框架

## 性能优化

### 1. 数据缓存
- 使用LRU缓存回测数据
- 缓存键为股票代码和日期

### 2. 内存管理
- history_exec和history_steps使用DataFrame存储
- 考虑使用内存高效的数据结构

### 3. 向量化操作
- 使用numpy向量化计算
- 避免Python循环

### 4. 时间索引优化
- 使用get_loc进行快速索引
- 预先计算_next_time以避免重复计算

## 注意事项

1. **数据格式**：
   - 优先使用handler格式（生产环境）
   - pickle格式主要用于研究/向后兼容

2. **时间对齐**：
   - 确保数据粒度与ticks_per_step匹配
   - 检查边界条件

3. **数值稳定性**：
   - 使用EPS处理浮点数比较
   - 避免除零错误

4. **交易记录**：
   - 保留完整的执行历史用于分析
   - 包括每笔交易的详细信息
