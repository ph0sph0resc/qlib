# qlib.rl.order_execution 模块文档

## 模块概述

`qlib.rl.order_execution` 模块提供了订单执行（Order Execution）的强化学习框架。

**注意**：目前仅支持单资产订单执行，多资产支持正在开发中。

## 主要组件

### 解释器（Interpreters）

| 类 | 说明 |
|----|------|
| `FullHistoryStateInterpreter` | 完整历史状态解释器，包含今天和昨天的数据 |
| `CurrentStepStateInterpreter` | 当前步骤状态解释器，仅使用最新状态 |
| `CategoricalActionInterpreter` | 分类动作解释器，将离散动作转换为连续值 |
| `TwapRelativeActionInterpreter` | TWAP 相对动作解释器 |

### 网络策略（Network & Policy）

| 类 | 说明 |
|----|------|
| `Recurrent` | 循环神经网络策略 |
| `AllOne` | 全1策略（基准策略） |
| `PPO` | PPO 策略 |

### 奖励函数（Reward）

| 类 | 说明 |
|----|------|
| `PAPenaltyReward` | PA 惩罚奖励，鼓励高 PA 但惩罚短时间内的集中交易 |

### 模拟器（Simulator）

| 类 | 说明 |
|----|------|
| `SingleAssetOrderExecutionSimple` | 单资产订单执行简单模拟器 |

### 状态和策略（State & Strategy）

| 类 | 说明 |
|----|------|
| `SAOEState` | 单资产订单执行状态 |
| `SAOEMetrics` | 单资产订单执行指标 |
| `SAOEStateAdapter` | 状态适配器 |
| `SAOEStrategy` | 基于 SAOEState 的 RL 策略 |
| `ProxySAOEStrategy` | 代理策略，允许外部决策 |
| `SAOEIntStrategy` | 带解释器的策略 |

## 使用示例

```python
from qlib.rl.order_execution import (
    FullHistoryStateInterpreter,
    CategoricalActionInterpreter,
    PAPenaltyReward,
    SingleAssetOrderExecutionSimple,
    SAOEIntStrategy,
)

# 创建状态解释器
state_interpreter = FullHistoryStateInterpreter(
    max_step=100,
    data_ticks=240,
    data_dim=16,
    processed_data_provider=provider
)

# 创建动作解释器
action_interpreter = CategoricalActionInterpreter(
    values=10,  # 10个离散动作
    max_step=100
)

# 创建奖励函数
reward_fn = PAPenaltyReward(penalty=100.0)

# 创建策略
strategy = SAOEIntStrategy(
    policy=policy_config,
    state_interpreter=state_interpreter,
    action_interpreter=action_interpreter,
    reward=reward_fn
)
```

## 相关文档

- [interpreter.md](./interpreter.md) - 解释器详细文档
- [reward.md](./reward.md) - 奖励函数详细文档
- [strategy.md](./strategy.md) - 策略详细文档
- [state.md](./state.md) - 状态详细文档
- [simulator_simple.md](./simulator_simple.md) - 模拟器详细文档
