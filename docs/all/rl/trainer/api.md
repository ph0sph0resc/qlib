# qlib/rl/trainer/api.md 模块文档

## 文件概述
简化的训练和回测API函数，提供快速启动训练和回测的方式。

## 主要函数

### train

```python
def train(
    simulator_fn: Callable[[InitialStateType], Simulator],
    state_interpreter: StateInterpreter,
    action_interpreter: ActionInterpreter,
    initial_states: Sequence[InitialStateType],
    policy: BasePolicy,
    reward: Reward,
    vessel_kwargs: Dict[str, Any],
    trainer_kwargs: Dict[str, Any],
) -> None
```

使用RL框架提供的并行训练策略。

**实验性API**：参数可能会很快变化。

**参数详解**：

- **simulator_fn**: 接受初始种子，返回模拟器的可调用对象
- **state_interpreter**: 解释模拟器的状态
- **action_interpreter**: 解释策略的动作
- **initial_states**: 迭代初始状态，每个状态将精确运行一次
- **policy**: 要训练的策略
- **reward**: 奖励函数
- **vessel_kwargs**: 传递给TrainingVessel的关键字参数，如`episode_per_iter`
- **trainer_kwargs**: 传递给Trainer的关键字参数，如`finite_env_type`、`concurrency`

**训练流程**：
```
1. 创建TrainingVessel容器
2. 创建Trainer实例
3. 调用trainer.fit(vessel)
```

### backtest

```python
def backtest(
    simulator_fn: Callable[[InitialStateType], Simulator],
    state_interpreter: StateInterpreter,
    action_interpreter: ActionInterpreter,
    initial_states: Sequence[InitialStateType],
    policy: BasePolicy,
    logger: LogWriter | List[LogWriter],
    reward: Reward | None = None,
    finite_env_type: FiniteEnvType = "subproc",
    concurrency: int = 2,
) -> None
```

使用RL框架提供的并行回测策略。

**实验性API**：参数可能会很快变化。

**参数详解**：

- **simulator_fn**: 接受初始种子，返回模拟器的可调用对象
- **state_interpreter**: 解释模拟器的状态
- **action_interpreter**: 解释策略的动作
- **initial_states**: 迭代初始状态，每个状态将精确运行一次
- **policy**: 要测试的策略
- **logger**: 记录回测结果的日志记录器（必须有，否则所有信息将丢失）
- **reward**: 可选的奖励函数，用于回测时测试奖励和记录
- **finite_env_type**: 有限环境实现的类型
- **concurrency**: 并行工作线程数

**回测流程**：
```
1. 创建TrainingVessel容器（测试模式）
2. 创建Trainer实例
3. 调用trainer.test(vessel)
```

## 使用示例

### 训练示例

```python
from qlib.rl.trainer.api import train
from qlib.rl.trainer.callbacks import Checkpoint, EarlyStopping, MetricsWriter
from tianshou.data import Collector, VectorReplayBuffer

# 训练
train(
    simulator_fn=simulator_factory,
    state_interpreter=state_interpreter,
    action_interpreter=action_interpreter,
    initial_states=train_orders,
    policy=policy,
    reward=reward_fn,
    vessel_kwargs={
        "episode_per_iter": 1000,
        "update_kwargs": {
            "batch_size": 64,
            "repeat": 10,
        },
    },
    trainer_kwargs={
        "max_iters": 100,
        "val_every_n_iters": 5,
        "callbacks": [
            Checkpoint(
                dirpath=Path("./checkpoints"),
                every_n_iters=10,
                save_latest="copy",
            ),
            EarlyStopping(
                monitor="val/reward",
                patience=10,
            ),
            MetricsWriter(dirpath=Path("./checkpoints")),
        ],
        "finite_env_type": "subproc",
        "concurrency": 4,
    },
)
```

### 回测示例

```python
from qlib.rl.trainer.api import backtest
from qlib.rl.utils import CsvWriter

# 回测
backtest(
    simulator_fn=simulator_factory,
    state_interpreter=state_interpreter,
    action_interpreter=action_interpreter,
    initial_states=test_orders,
    policy=policy,
    logger=CsvWriter(Path("./results")),
    reward=reward_fn,  # 可选
    finite_env_type="subproc",
    concurrency=2,
)
```

## 训练架构对比

### 高级API（Trainer + TrainingVessel）

```python
vessel = TrainingVessel(...)
trainer = Trainer(...)
trainer.fit(vessel)
```

- **优点**：更多控制，更灵活
- **缺点**：需要更多代码

### 低级API（train函数）

```python
train(
    simulator_fn=...,
    state_interpreter=...,
    action_interpreter=...,
    initial_states=...,
    policy=...,
    reward=...,
    vessel_kwargs=...,
    trainer_kwargs=...,
)
```

- **优点**：更简洁，快速启动
- **缺点**：控制较少

## 组件关系

### qlib.rl.trainer.Trainer

- **使用**: `trainer.fit()`和`trainer.test()`
- **管理**: 训练循环、验证、回调

### qlib.rl.trainer.vessel.TrainingVessel

- **创建**: 由`train()`函数创建
- **包含**: 模拟器、解释器、策略、奖励

### tianshou.policy.BasePolicy

- **类型**: `policy`参数的类型
- **实现**: PPO、DQN、SAC等算法

### qlib.rl.utils.FiniteVectorEnv

- **并行**: 使用并行环境进行训练
- **类型**: `finite_env_type`参数指定

## 最佳实践

### 1. 日志配置

```python
# 训练时使用多种日志记录器
from qlib.rl.trainer.callbacks import MetricsWriter

metrics_writer = MetricsWriter(dirpath=Path("./checkpoints"))
```

### 2. 模型保存

```python
# 定期保存checkpoint
from qlib.rl.trainer.callbacks import Checkpoint

checkpoint = Checkpoint(
    dirpath=Path("./checkpoints"),
    filename="{iter:03d}-{reward:.2f}.pth",
    save_latest="copy",  # 或 "link"
    every_n_iters=10,
)
```

### 3. 早停机制

```python
# 防止过拟合
from qlib.rl.trainer.callbacks import EarlyStopping

early_stopping = EarlyStopping(
    monitor="val/reward",      # 监控的指标
    min_delta=0.0,           # 最小改善阈值
    patience=10,              # 容忍步数
    mode="max",               # 最大化模式
    restore_best_weights=True, # 恢复最佳权重
)
```

### 4. 并行配置

```python
# 根据资源配置并行数量
import os
concurrency = min(4, os.cpu_count())  # 使用CPU核心数
```

## 注意事项

1. **实验性**：这些API可能会很快变化
2. **日志必需**：回测时必须提供logger
3. **类型安全**：使用类型注解避免错误
4. **参数一致性**：确保解释器和策略的空间一致
