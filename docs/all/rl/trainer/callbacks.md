# qlib/rl/trainer/callbacks.md 模块文档

## 文件概述
回调模块，模仿在训练期间插入自定义配方的hook（类似于Keras / PyTorch Lightning的hooks，但针对RL上下文定制）。

## 类与函数

### Callback

```python
class Callback:
    """所有回调的基类。"""

    def on_fit_start(self, trainer: Trainer, vessel: TrainingVesselBase) -> None:
        """在整个训练过程开始之前调用。"""

    def on_fit_end(self, trainer: Trainer, vessel: TrainingVesselBase) -> None:
        """在整个训练过程结束时调用。"""

    def on_train_start(self, trainer: Trainer, vessel: TrainingVesselBase) -> None:
        """当每次训练收集开始时调用。"""

    def on_train_end(self, trainer: Trainer, vessel: TrainingVesselBase) -> None:
        """当训练结束时调用。
        要访问训练期间产生的所有输出，在trainer和vessel中缓存数据，
        并在此hook中后处理它们。"""

    def on_validate_start(self, trainer: Trainer, vessel: TrainingVesselBase) -> None:
        """当每次验证运行开始时调用。"""

    def on_validate_end(self, trainer: Trainer, vessel: TrainingVesselBase) -> None:
        """当验证结束时调用。"""

    def on_test_start(self, trainer: Trainer, vessel: TrainingVesselBase) -> None:
        """当每次测试运行开始时调用。"""

    def on_test_end(self, trainer: Trainer, vessel: TrainingVesselBase) -> None:
        """当测试结束时调用。"""

    def on_iter_start(self, trainer: Trainer, vessel: TrainingVesselBase) -> None:
        """当每次迭代（即收集）开始时调用。"""

    def on_iter_end(self, trainer: Trainer, vessel: TrainingVesselBase) -> None:
        """在每次迭代的末尾调用。
        这是在current_iter增加后调用的，
        当上一次迭代被认为完成时。"""

    def state_dict(self) -> Any:
        """获取回调的state dict以便暂停和恢复。"""

    def load_state_dict(self, state_dict: Any) -> None:
        """从保存的state dict恢复回调。"""
```

回调基类，定义所有可用的hook。

**Hook调用顺序**：

```
训练开始：
on_fit_start
└─▶ 循环
    │ on_iter_start
    │ on_train_start
    │ 训练收集
    │ on_train_end
    │ on_validate_start (如果到了验证时间)
    │ 验证
    │ on_validate_end
    │ on_iter_end
└────────────┘
on_fit_end
```

### EarlyStopping

```python
class EarlyStopping(Callback):
    """当监控的指标停止改善时停止训练。

    早停回调将在每次验证结束时触发。
    它将检查验证中产生的指标，
    并获取名为monitor（monitor默认为reward）的指标
    来检查它是否不再增加/减少。
    如果发现不再增加/减少，
    trainer.should_stop将被设置为true，
    并且训练终止。

    实现参考：https://github.com/keras-team/keras/blob/v2.9.0/keras/callbacks.py#L1744-L1893
    """

    def __init__(
        self,
        monitor: str = "reward",
        min_delta: float = 0.0,
        patience: int = 0,
        mode: Literal["min", "max"] = "max",
        baseline: float | None = None,
        restore_best_weights: bool = False,
    ):
```

早停回调，当监控的指标停止改善时停止训练。

**参数详解**：

- **monitor**: 要监控的指标名称（默认为"reward"）
- **min_delta**: 被视为改善的最小变化量
- **patience**: 在停止之前等待的步数
- **mode**: 监控模式（"min"或"max"）
- **baseline**: 可选的基准值
- **restore_best_weights**: 是否在停止时恢复最佳权重

**工作流程**：

1. 每次验证结束检查监控指标
2. 如果指标优于最佳值，更新最佳值和重置等待计数
3. 如果等待计数超过patience，设置停止标志
4. 如果启用，恢复最佳权重

### MetricsWriter

```python
class MetricsWriter(Callback):
    """将训练指标转储到文件。"""

    def __init__(self, dirpath: Path) -> None:
```

将训练指标转储到文件。

**输出文件**：

- `train_result.csv`: 训练指标
- `validation_result.csv`: 验证指标

**工作流程**：

1. 每次训练结束，收集训练指标
2. 每次验证结束，收集验证指标
3. 写入对应的CSV文件

### Checkpoint

```python
class Checkpoint(Callback):
    """定期保存checkpoint以便持久化和恢复。

    参考：https://github.com/PyTorchLightning/pytorch-lightning/blob/bfa8b7be/pytorch_lightning/callbacks/model_checkpoint.py

    参数
    ----------
    dirpath
        保存checkpoint文件的目录
    filename
        Checkpoint文件名。可以包含命名格式选项以自动填充。
        例如：{iter:03d}-{reward:.2f}.pth
        支持的参数名为：
        - iter (int)
        - trainer.metrics中的指标
        - 时间字符串，格式为%Y%m%d%H%M%S
    save_latest
        在latest.pth中保存最新checkpoint
        如果是link，latest.pth将创建为软链接
        如果是copy，latest.pth将存储为单独的副本
        设置为none以禁用此功能
    every_n_iters
        在训练的每n次迭代后保存checkpoint，
        如果适用则在验证之后
    time_interval
        再次保存checkpoint之前的最大时间（秒）
    save_on_fit_end
        在fit结束时保存最后一个checkpoint
        如果该处已有checkpoint则不执行任何操作
    """

    def __init__(
        self,
        dirpath: Path,
        filename: str = "{iter:03d}.pth",
        save_latest: Literal["link", "copy"] | None = "link",
        every_n_iters: int | None = None,
        time_interval: int | None = None,
        save_on_fit_end: bool = True,
    ):
```

定期保存checkpoint以便持久化和恢复。

**参数详解**：

- **dirpath**: 保存checkpoint的目录
- **filename**: 文件名模板（支持格式化）
- **save_latest**: 保存最新checkpoint的方式（"link"或"copy"）
- **every_n_iters**: 每N次迭代保存一次
- **time_interval**: 保存checkpoint的最大时间间隔（秒）
- **save_on_fit_end**: 是否在训练结束时保存

**支持的格式化参数**：

- `iter`: 当前迭代次数
- `time`: 时间字符串（%Y%m%d%H%M%S%S）
- `trainer.metrics`中的任何指标

**文件名示例**：

```python
# 简单迭代
"{iter:03d}.pth" → "001.pth"

# 带奖励
"{iter:03d}-{reward:.2f}.pth" → "001-12.34.pth"

# 带时间
"{iter:03d}-{reward:.2f}-{time}.pth" → "001-12.34-20250326143015.pth"
```

## 使用示例

### 使用EarlyStopping

```python
from qlib.rl.trainer.callbacks import EarlyStopping

early_stopping = EarlyStopping(
    monitor="val/reward",
    patience=10,
    mode="max",
    min_delta=0.01,
    restore_best_weights=True,
)

callbacks = [early_stopping]
```

### 使用MetricsWriter

```python
from qlib.rl.trainer.callbacks import MetricsWriter
from pathlib import Path

metrics_writer = MetricsWriter(dirpath=Path("./results"))
callbacks = [metrics_writer]
```

### 使用Checkpoint

```python
from qlib.rl.trainer.callbacks import Checkpoint
from pathlib import Path

checkpoint = Checkpoint(
    dirpath=Path("./checkpoints"),
    filename="{iter:03d}-{reward:.2f}.pth",
    save_latest="copy",
    every_n_iters=5,
    time_interval=3600,  # 每小时保存一次
    save_on_fit_end=True,
)

callbacks = [checkpoint]
```

### 组合使用

```python
from qlib.rl.trainer.callbacks import Checkpoint, EarlyStopping, MetricsWriter

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
```

## 保存和恢复

### 状态字典

所有回调都支持保存和恢复状态：

```python
# 保存状态
state_dict = callback.state_dict()

# 恢复状态
callback.load_state_dict(state_dict)
```

### 早停状态

```python
{
    "wait": 等待计数,
    "best": 最佳值,
    "best_weights": 最佳权重,
    "best_iter": 最佳迭代,
}
```

## 与其他模块的关系

### qlib.rl.trainer.Trainer

- **调用**: 在训练循环的适当位置调用hook
- **管理**: 维护回调列表

### qlib.rl.trainer.vessel.TrainingVessel

- **访问**: 回调可以访问vessel的状态
- **恢复**: 可以加载vessel的checkpoint

### tianshou.policy.BasePolicy

- **权重保存**: Checkpoint保存policy的state_dict
- **权重恢复**: 可以从checkpoint恢复policy权重

## 最佳实践

### 1. 组合回调

```python
# 推荐的组合
callbacks = [
    Checkpoint(...),           # 保存模型
    EarlyStopping(...),       # 早停
    MetricsWriter(...),        # 记录指标
]
```

### 2. 文件命名

```python
# 使用有意义的文件名
filename = "{iter:03d}-{val/reward:.2f}.pth"
```

### 3. 磁盘空间管理

```python
# 设置合理的保存间隔
every_n_iters = 10  # 不要太频繁
```

### 4. 恢复策略

```python
# 早停时恢复最佳权重
restore_best_weights = True
```

## 注意事项

1. **Hook顺序**: Hook按预定义的顺序调用
2. **线程安全**: 回调应该考虑线程安全
3. **异常处理**: 回调中的错误会影响训练
4. **磁盘空间**: 注意checkpoint可能占用大量空间
