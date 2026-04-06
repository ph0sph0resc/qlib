# qlib/rl/trainer/trainer.py 模块文档

## 文件概述
训练器类，用于在特定任务上训练策略。与传统深度学习训练器不同，该训练器的迭代是"收集"而不是"epoch"或"mini-batch"。

## 类与函数

### Trainer

```python
class Trainer:
    """
    在特定任务上训练策略的工具。

    与传统DL训练器不同，该训练器的迭代是 "收集"，
    而不是 "epoch"或 "mini-batch"。
    在每次收集中，:class:`Collector` 收集一些策略-环境交互，并将它们
    累积到回放缓冲区中。该缓冲区用作 *数据* 来训练策略。
    在每次收集结束时，策略被*更新*若干次。

    该API与`PyTorch Lightning <https://pytorch-lightning.readthedocs.io/>`有某种相似，
    但它本质上不同，因为该训练器是为RL应用构建的，因此
    大多数配置都在RL上下文中。
    我们仍在寻找方法来合并现有的训练器库，因为看起来像
    花费大力构建一个像那些库一样强大的训练器，而且，那不是我们的主要目标。

    它与`Tianshou的内置训练器 <https://tianshou.readthedocs.io/en/master/api/tianshou.trainer.html>`本质上不同
    因为它比那复杂得多。

    参数
    ----------
    max_iters
        停止前的最大迭代次数。
    val_every_n_iters
        每n次迭代（即训练收集）执行一次验证。
    logger
        用于记录回测结果的日志记录器。日志记录器必须存在，
        因为没有日志记录器，所有信息都将丢失。
    finite_env_type
        有限环境实现的类型。
    concurrency
        并行工作线程数。
    fast_dev_run
        创建用于调试的子集。
        其实现取决于训练容器的实现。
        对于:class:`~qlib.rl.vessel.TrainingVessel`，如果大于零，
        将使用大小为`fast_dev_run`的随机子集
        代替`train_initial_states`和`val_initial_states`。
    """

    should_stop: bool
    """设置为停止训练。"""

    metrics: dict
    """在训练/验证/测试中产生的数值指标。
    在训练/验证过程中，指标将是最新episode的指标。
    当每次训练/验证的迭代结束时，指标将是
    在此次迭代中遇到的所有episode的聚合。

    在每次新的训练迭代中清除。

    在fit中，验证指标将以`val/`为前缀。"""

    current_iter: int
    """训练的当前迭代（收集）。"""

    loggers: List[LogWriter]
    """日志记录器列表。"""
```

#### 主要属性

- **should_stop**: `bool`
  - 停止训练的标志
  - 由回调（如EarlyStopping）设置

- **metrics**: `dict`
  - 当前迭代的指标
  - 包含训练和验证指标

- **current_iter**: `int`
  - 当前迭代次数
  - 从0开始计数

- **loggers**: `List[LogWriter]`
  - 日志记录器列表
  - 用于记录训练过程

- **vessel**: `TrainingVesselBase`
  - 训练容器
  - 包含所有训练组件

#### 主要方法

1. **`initialize(self) -> None`**
   - 初始化整个训练过程
   - 设置`should_stop`、`current_iter`等

2. **`initialize_iter(self) -> None`**
   - 初始化一次迭代/收集
   - 清空`metrics`字典

3. **`state_dict(self) -> dict`**
   - 将当前训练状态放入字典
   - 包含vessel、callbacks、loggers等状态

4. **`load_state_dict(self, state_dict: dict) -> None`**
   - 从字典加载所有训练状态
   - 恢复训练中断的位置

5. **`fit(self, vessel: TrainingVesselBase, ckpt_path: Path | None = None) -> None`**
   - 训练RL策略
   - 管理训练循环、验证、早停等
   - 支持从checkpoint恢复

6. **`test(self, vessel: TrainingVesselBase) -> None`**
   - 测试RL策略
   - 使用`test_seed_iterator`提供的初始状态

7. **`venv_from_iterator(self, iterator: Iterable[InitialStateType]) -> FiniteVectorEnv`**
   - 从迭代器创建向量化环境
   - 支持并行训练

8. **`_metrics_callback(self, on_episode: bool, on_collect: bool, log_buffer: LogBuffer) -> None`**
   - 更新全局计数器
   - 聚合指标到metrics字典

## 训练流程

```
初始化
    │
    ▼
fit(vessel)
    │
    ├─▶ load_state_dict()? (如果提供了ckpt_path)
    │     │
    │     └─▶ 初始化或恢复训练状态
    │
    ├─▶ on_fit_start()
    │
    ├─▶ while not should_stop:
    │     │
    │     ├─▶ 初始化迭代
    │     │
    │     ├─▶ on_iter_start()
    │     │
    │     ├─▶ 训练
    │     │     │
    │     │     ├─▶ 创建向量环境
    │     │     │   (从train_seed_iterator)
    │     │     │
    │     │     ├─▶ vessel.train(vector_env)
    │     │     │   (收集 + 更新策略）
    │     │     │
    │     │     └─▶ 删除向量环境（避免内存泄漏）
    │     │
    │     ├─▶ 验证? (如果val_every_n_iters匹配)
    │     │     │
    │     │     ├─▶ 创建向量环境
    │     │     │   (从val_seed_iterator)
    │     │     │
    │     │     ├─▶ vessel.validate(vector_env)
    │     │     │
    │     │     └─▶ 删除向量环境
    │     │
    │     ├─▶ 更新迭代计数
    │     │
    │     ├─▶ 检查停止条件
    │     │
    │     ├─▶ on_iter_end()
    │     │
    │     └─▶ 检查max_iters
    │
    └─▶ on_fit_end()
```

## 组件关系

### qlib.rl.trainer.vessel.TrainingVessel

- **包含**: 模拟器、解释器、策略、奖励
- **实现**: 训练、验证、测试逻辑
- **迭代器**: 提供训练、验证、测试的初始状态

### qlib.rl.trainer.callbacks.Callback

- **钩子**: 在训练过程的不同点调用
- **类型**: Checkpoint、EarlyStopping、MetricsWriter等

### qlib.rl.utils.FiniteVectorEnv

- **并行**: 提供并行环境执行
- **类型**: dummy、subproc、shmem

### tianshou.policy.BasePolicy

- **策略**: 要训练的RL策略
- **算法**: PPO、DQN、SAC等

### qlib.rl.utils.LogWriter

- **日志**: 记录训练指标
- **类型**: ConsoleWriter、CsvWriter等

## 使用示例

### 基本训练

```python
from qlib.rl.trainer import Trainer, TrainingVessel
from qlib.rl.trainer.callbacks import Checkpoint, EarlyStopping, MetricsWriter

# 创建容器
vessel = TrainingVessel(
    simulator_fn=simulator_factory,
    state_interpreter=state_interpreter,
    action_interpreter=action_interpreter,
    policy=policy,
    reward=reward_fn,
    train_initial_states=train_orders,
    val_initial_states=val_orders,
    buffer_size=20000,
    episode_per_iter=1000,
    update_kwargs={"batch_size": 64, "repeat": 10},
)

# 创建回调
callbacks = [
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
]

# 创建训练器
trainer = Trainer(
    max_iters=100,
    val_every_n_iters=5,
    callbacks=callbacks,
    finite_env_type="subproc",
    concurrency=4,
)

# 开始训练
trainer.fit(vessel)
```

### 恢复训练

```python
# 从checkpoint恢复
trainer.fit(vessel, ckpt_path=Path("./checkpoints/latest.pth"))
```

## 训练模式

### 训练模式

```python
trainer.current_stage = "train"
```

- 执行`vessel.train()`
- 策略处于训练模式
- 指标以正常名称记录

### 验证模式

```python
trainer.current_stage = "val"
```

- 执行`vessel.validate()`
- 策略处于评估模式
- 指标以"val/"前缀记录

### 测试模式

```python
trainer.current_stage = "test"
```

- 执行`vessel.test()`
- 策略处于测试模式
- 指标独立记录

## 状态保存和恢复

### 保存状态

```python
# 在训练过程中保存
state_dict = trainer.state_dict()
torch.save(state_dict, "checkpoint.pth")
```

**保存的内容**：

```python
{
    "vessel": vessel.state_dict(),
    "callbacks": {callback_name: callback.state_dict() ...},
    "loggers": {logger_name: logger.state_dict() ...},
    "should_stop": should_stop,
    "current_iter": current_iter,
    "current_episode": current_episode,
    "current_stage": current_stage,
    "metrics": metrics,
}
```

### 恢复状态

```python
# 加载并恢复
state_dict = torch.load("checkpoint.pth", weights_only=False)
trainer.load_state_dict(state_dict)
```

## 最佳实践

### 1. 回调使用

```python
# 必须的回调
callbacks = [
    Checkpoint(...),      # 保存模型
    EarlyStopping(...),   # 早停
    MetricsWriter(...),   # 记录指标
]
```

### 2. 验证配置

```python
# 定期验证
trainer = Trainer(
    val_every_n_iters=5,  # 每5次迭代验证一次
)
```

### 3. 并行配置

```python
# 配置并行
trainer = Trainer(
    finite_env_type="subproc",  # 子进程并行
    concurrency=4,              # 4个worker
)
```

### 4. 日志配置

```python
# 配置日志
trainer = Trainer(
    loggers=[
        ConsoleWriter(),
        CsvWriter(Path("./results")),
    ],
)
```

### 5. 检查点管理

```python
# 定期保存
checkpoint = Checkpoint(
    every_n_iters=10,       # 每10次迭代保存
    time_interval=3600,       # 或每小时保存
)
```

## 注意事项

1. **内存管理**:
   - 及时删除向量环境
   - 避免内存泄漏

2. **线程安全**:
   - 回调可能跨线程调用
   - 注意共享状态

3. **状态一致性**:
   - state_dict和load_state_dict必须匹配
   - 版本兼容性需要考虑

4. **指标聚合**:
   - 训练和验证指标分别处理
   - 验证指标添加前缀
