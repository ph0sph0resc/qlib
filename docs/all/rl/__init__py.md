# qlib/rl/__init__.py 模块文档

## 文件概述
RL模块的初始化文件，导出强化学习相关的核心接口类。

## 导出的类

### Interpreter
状态和动作解释器的基类。

- **位置**: `qlib/rl/interpreter.py`
- **用途**: 作为类型检查使用，不直接实例化

### StateInterpreter
状态解释器，将模拟器状态转换为策略所需的观测值。

- **位置**: `qlib/rl/interpreter.py`
- **继承**: `Interpreter`
- **用途**: 将 `StateType`` 转换为 `ObsType`

### ActionInterpreter
动作解释器，将策略动作转换为模拟器可执行的动作。

- **位置**: `qlib/rl/interpreter.py`
- **继承**: `Interpreter`
- **用途**: 将 `PolicyActType`` 转换为 `ActType`

### Reward
奖励函数基类，用于计算强化学习中的即时奖励。

- **位置**: `qlib/rl/reward.py`
- **泛型参数**: `SimulatorState`
- **用途**: 根据模拟器状态计算奖励值

### RewardCombination
多个奖励函数的组合类。

- **位置**: `qlib/rl/reward.py`
- **继承**: `Reward`
- **用途**: 将多个奖励函数按权重组合

### Simulator
模拟器基类，定义强化学习环境的核心行为。

- **位置**: `qlib/rl/simulator.py`
- **泛型参数**: `InitialStateType`, `StateType`, `ActType`
- **用途**: 定义环境的重置、状态更新和终止条件

## RL框架架构

```
┌─────────────────────────────────────────────────────────┐
│                    Trainer                          │
│  (训练循环管理，负责迭代和验证)                  │
└──────────────┬──────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────┐
│               TrainingVessel                     │
│  (包含simulator、interpreter、policy的容器)            │
└──────────────┬──────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────┐
│                 Simulator                          │
│  (环境模拟器，定义MDP的核心行为)                    │
│                                                     │
│  方法:                                                │
│  - step(action): 接收动作，更新内部状态                    │
│  - get_state(): 返回当前状态                           │
│    - done(): 检查是否终止                          │
└──────────────┬──────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────┐
│             StateInterpreter                     │
│  (状态→观测转换器)                                      │
│                                                     │
│  方法:                                                │
│    - interpret(state): 返回观测值                      │
│    - observation_space: 返回观测空间                   │
└──────────────┬──────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────┐
│            ActionInterpreter                     │
│  (动作→执行动作转换器)                                    │
│                                                     │
│  方法:                                                │
│    - interpret(state, action): 返回执行动作              │
│    - action_space: 返回动作空间                      │
└──────────────┬──────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────┐
│                Reward                              │
│  (奖励函数)                                             │
│                                                     │
│  方法:                                                │
│    - reward(state): 返回奖励值                        │
└─────────────────────────────────────────────────────────┘

```

## 数据流

```
初始状态 (Order)
    │
    ▼
Simulator.__init__(initial)
    │
    ├─▶ step(action) ───┐
    │                   │
    │                   ▼
    │           ActionInterpreter.interpret(state, action)
    │                   │
    │                   ▼
    │           更新模拟器内部状态
    │                   │
    │                   ▼
    │           StateInterpreter.interpret(new_state)
    │                   │
    │                   ▼
    │           Reward.reward(state)
    │                   │
    │                   ▼
    │           (obs, reward, done)
    └──────────────────┘
```

## 与其他模块的关系

### qlib.backtest
- **Simulator**: 使用 `qlib.backtest.Exchange` 和 `qlib.backtest.Executor` 来模拟真实交易环境
- **Order**: `Simulator` 的初始状态通常是 `qlib.backtest.Order` 对象

### qlib.data
- **数据加载**: Simulator 从 `qlib.data` 模块加载市场数据
- **特征计算**: 使用 `qlib.data` 的特征计算能力

### tianshou
- **集成**: `Trainer` 与 Tianshou 的 `BasePolicy`、`Collector`、`VectorEnv` 集成
- **训练流程**: 使用 Tianshou 的 RL 算法实现（PPO、A2C、SAC等）

## 使用示例

```python
from qlib.rl import Simulator, StateInterpreter, ActionInterpreter, Reward
from qlib.rl.trainer import Trainer, TrainingVessel

# 定义模拟器
class MySimulator(Simulator[Order, MyState, float]):
    def step(self, action):
        # 更新状态
        pass
    def get_state(self):
        # 返回当前状态
        pass
    def done(self):
        # 检查是否完成
        pass

# 定义解释器
state_interpreter = MyStateInterpreter()
action_interpreter = MyActionInterpreter()
reward_fn = MyReward()

# 创建容器
vessel = TrainingVessel(
    simulator_fn=MySimulator,
    state_interpreter=state_interpreter,
    action_interpreter=action_interpreter,
    policy=policy,
    reward=reward_fn,
    train_initial_states=orders,
)

# 训练
trainer = Trainer(max_iters=100, val_every_n_iters=10)
trainer.fit(vessel)
```

## 类型系统

RL模块使用泛型确保类型安全：

- **InitialStateType**: 创建模拟器的初始数据类型
- **StateType**: 模拟器内部状态类型
- **ActType**: 模拟器接受的动作类型
- **ObsType**: 策略接收的观测值类型
- **PolicyActType**: 策略输出的动作类型

这种类型系统确保：
1. 不同组件之间的类型兼容性
2. 编译时的类型检查
3. 更好的代码提示和文档
