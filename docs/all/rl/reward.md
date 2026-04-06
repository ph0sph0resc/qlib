# qlib.rl.reward 模块文档

## 模块概述

`qlib.rl.reward` 模块定义了奖励计算的接口和组合模式，用于评估智能体在环境中的表现。

奖励函数是强化学习的核心组件，通过定义奖励信号来引导智能体的学习方向。

## 主要组件

### Reward

```python
class Reward(Generic[SimulatorState])
```

**说明**：奖励计算组件基类，接收模拟器状态作为输入，返回一个实数（奖励值）。

子类需要实现 `reward(simulator_state)` 方法来定义自己的奖励计算逻辑。

#### 属性

| 属性名 | 类型 | 说明 |
|--------|------|------|
| `env` | `Optional[EnvWrapper]` | 环境包装器的弱引用，通常由框架自动设置 |

#### 方法

##### `__call__(simulator_state: SimulatorState) -> float`

**说明**：调用奖励计算函数。

**参数**：
- `simulator_state`: 从模拟器获取的状态，通过 `simulator.get_state()` 获得

**返回**：奖励值（浮点数）

##### `reward(simulator_state: SimulatorState) -> float`

**说明**：**抽象方法**，实现奖励计算逻辑。

。

**参数**：
- `simulator_state`: 从模拟器获取的状态，通过 `simulator.get_state()` 获得

**返回**：奖励值（浮点数）

**抛出**：`NotImplementedError` - 如果子类未实现此方法

##### `log(name: str, value: Any) -> None`

**说明**：记录标量值到日志系统。

**参数**：
- `name`: 指标名称
- `value`: 要记录的值

**注意**：需要 `self.env` 已设置，否则会断言失败

### RewardCombination

```python
class RewardCombination(Reward)
```

**说明**：多个奖励的组合计算类，支持加权组合。

#### 构造方法

```python
def __init__(self, rewards: Dict[str, Tuple[Reward, float]]) -> None
```

**参数**：
- `rewards`: 奖励字典，格式为 `{name: (reward_fn, weight)}`
  - `name`: 奖励名称（用于日志记录）
  - `reward_fn`: 奖励函数对象
  - `weight`: 奖励权重

#### 方法

##### `reward(simulator_state: Any) -> float`

**说明**：计算组合奖励。

**参数**：
- `simulator_state`: 从模拟器获取的状态

**返回**：所有奖励的加权和

## 使用示例

### 基本奖励函数

```python
from qlib.rl.reward import Reward

class ProfitReward(Reward):
    """基于利润的奖励函数"""
    def reward(self, simulator_state):
        return simulator_state['profit']

class RiskPenaltyReward(Reward):
    """风险惩罚奖励函数"""
    def __init__(self, penalty_coeff=0.1):
        self.penalty_coeff = penalty_coeff

    def reward(self, simulator_state):
        position_change = abs(simulator_state['position_change'])
        return -self.penalty_coeff * position_change
```

### 组合奖励函数

```python
from qlib.rl.reward import RewardCombination

profit_reward = ProfitReward()
risk_penalty = RiskPenaltyReward(penalty_coeff=0.5)

combined_reward = RewardCombination({
    'profit': (profit_reward, 1.0),
    'risk_penalty': (risk_penalty, 0.5)
})
```

## 注意事项

1. 保持奖励值在合理的数值范围内
2. `reward` 方法会在每个步骤调用，应保持高效
3. 确保使用 `log` 方法前 `self.env` 已设置
