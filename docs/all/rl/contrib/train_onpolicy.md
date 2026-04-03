# qlib/rl/contrib/train_onpolicy.py 模块文档

## 文件概述
完整的在线策略（On-Policy）强化学习训练流程，包括数据加载、模型训练、验证和回测。

## 主要函数

### seed_everything

```python
def seed_everything(seed: int) -> None
```

设置所有随机种子以确保可重复性：
- PyTorch（CPU和CUDA）
- NumPy
- Python random
- cuDNN deterministic mode

### LazyLoadDataset

```python
class LazyLoadDataset(Dataset):
    def __init__(
        self,
        data_dir: str,
        order_file_path: Path,
        default_start_time_index: int,
        default_end_time_index: int,
    ) -> None
```

延迟加载的数据集类，减少内存使用。

**特点**：
- 只在`__getitem__`时加载实际数据
- 一次性加载ticks index（假设不同日期相同）
- 将订单文件路径作为初始状态

### train_and_test

```python
def train_and_test(
    env_config: dict,
    simulator_config: dict,
    trainer_config: dict,
    data_config: dict,
    state_interpreter: StateInterpreter,
    action_interpreter: ActionInterpreter,
    policy: BasePolicy,
    reward: Reward,
    run_training: bool,
    run_backtest: bool,
) -> None
```

主训练和测试函数。

**训练流程**：
1. 创建训练和验证数据集
2. 设置回调函数（checkpoint、early stopping等）
3. 调用`trainer.train()`进行训练

**回测流程**：
1. 加载测试数据集
2. 使用训练好的策略进行回测
3. 保存结果到CSV

### main

```python
def main(config: dict, run_training: bool, run_backtest: bool) -> None
```

主函数，协调整个流程。

**步骤**：
1. 设置随机种子
2. 添加额外模块路径
3. 初始化state/action解释器
4. 创建policy网络
5. 初始化policy
6. 调用train_and_test()

## 训练架构

```
┌──────────────────────────────────────────────────┐
│                    main()                     │
│  (协调训练和回测流程)                       │
└──────────────┬──────────────────────────────────┘
               │
               ├─▶ train_and_test()
               │     │
               │     ├─▶ ┌────────────────────┬─────────────────┐
               │     │     │                │                 │
               │     │     ▼                ▼                 │
               │     │  LazyLoadDataset  LazyLoadDataset    │
               │     │  (训练集)       (验证集)          │
               │     │     │                │                 │
               │     │     └─▶─────────────────────────┘                 │
               │     │                │                            │
               │     │                └──────────────────────────┬─────┐
               │     │                             │             │      │
               │     └────────────────────────────┬─────┘             │      │
               │                                      │             │      ▼
               │                                      ▼             │    trainer.train()
               │                                Callbacks             │      │
               │                                 - Checkpoint           │      │
               │                                 - MetricsWriter       │      │
               │                                 - EarlyStopping      │      │
               │                                      │      └────────────────┘
               │                                      │
               ├─▶ run_backtest?                  │
               │     │                             │
               │     └─▶ ┌─────────────────────────┐      │
               │          │                       │      │
               │          ▼                       ▼      │
               │     LazyLoadDataset (测试集)       │      │
               │          │                       │      │
               │          └──────────────────────────┬───┘      │
               │                                 │             │
               │                                 ▼             │
               │                            trainer.backtest()      │
               │                                 │      └────────────────┘
               └──────────────────────────────────────────────┘
```

## 配置结构

### 完整配置示例

```yaml
# config.yaml
runtime:
  seed: 42
  use_cuda: true

env:
  extra_module_paths: []
  parallel_mode: subproc
  concurrency: 4

simulator:
  data_granularity: 1
  time_per_step: 30
  vol_limit: 0.1

data:
  source:
    feature_root_dir: /path/to/features
    order_dir: /path/to/orders
    feature_columns_today:
      - $open
      - $close
      - $volume
    feature_columns_yesterday:
      - $open_1
      - $close_1
    default_start_time_index: 60
    default_end_time_index: 390

state_interpreter:
  class: FullHistoryStateInterpreter
  module_path: qlib.rl.order_execution.interpreter
  kwargs:
    max_step: 12
    data_ticks: 390
    data_dim: 3
    processed_data_provider:
      class: PickleProcessedDataProvider
      module_path: qlib.rl.data.pickle_styled
      kwargs:
        data_dir: /path/to/features

action_interpreter:
  class: CategoricalActionInterpreter
  module_path: qlib.rl.order_execution.interpreter
  kwargs:
    values: 11

network:
  class: Recurrent
  module_path: qlib.rl.order_execution.network
  kwargs:
    hidden_dim: 64
    output_dim: 32
    rnn_type: gru

policy:
  class: PPO
  module_path: qlib.rl.order_execution.policy
  kwargs:
    lr: 0.0001
    weight_decay: 0.0001
    discount_factor: 1.0
    max_grad_norm: 100.0
    reward_normalization: true

reward:
  class: PAPenaltyReward
  module_path: qlib.rl.order_execution.reward
  kwargs:
    penalty: 100.0

trainer:
  max_epoch: 100
  episode_per_collect: 1000
  batch_size: 64
  repeat_per_collect: 10
  val_every_n_epoch: 5
  checkpoint_every_n_iters: 10
  earlystop_patience: 10
  checkpoint_path: ./checkpoints
```

## 命令行使用

```bash
# 训练和回测
python -m qlib.rl.contrib.train_onpolicy \
    --config_path config.yaml

# 只训练（不回测）
python -m qlib.rl.contrib.train_onpolicy \
    --config_path config.yaml \
    --no_training

# 只回测（跳过训练）
python -m qlib.rl.contrib.train_onpolicy \
    --config_path config.yaml \
    --run_backtest
```

## 输出文件

### 训练输出
- `./checkpoints/train_result.csv`: 训练指标
- `./checkpoints/validation_result.csv`: 验证指标
- `./checkpoints/checkpoints/`: 模型checkpoint
- `./checkpoints/latest.pth`: 最新checkpoint

### 回测输出
- `./checkpoints/backtest_result.csv`: 回测结果

## 组件初始化流程

```
配置加载
    │
    ▼
读取state_interpreter配置
    │
    ├─▶ 创建StateInterpreter实例
    └─▶ 设置observation_space
    │
    ▼
读取action_interpreter配置
    │
    ├─▶ 创建ActionInterpreter实例
    └─▶ 设置action_space
    │
    ▼
读取network配置
    │
    ├─▶ 更新kwargs添加observation_space
    ├─▶ 创建network实例
    └─▶ 获取output_dim
    │
    ▼
读取policy配置
    │
    ├─▶ 更新kwargs
    │     │
    │     ├─▶ obs_space: state_interpreter.observation_space
    │     ├─▶ action_space: action_interpreter.action_space
    │     └─▶ network: network实例
    │
    ├─▶ 创建policy实例
    │
    └─▶ 如果use_cuda: policy.cuda()
```

## 与其他模块的关系

### qlib.rl.trainer
- **Trainer**: 训练循环管理
- **TrainingVessel**: 训练容器
- **Callbacks**: 训练回调

### qlib.rl.order_execution
- **Interpreter**: state和action解释器
- **Policy**: PPO、DQN等策略
- **Network**: Recurrent等网络

### qlib.rl.data
- **Native data**: 加载处理器数据
- **Pickle data**: 加载pickle格式数据

## 性能优化

### 1. 数据加载
- LazyLoadDataset减少内存使用
- 多进程数据加载
- 缓存ticks index

### 2. 模型训练
- GPU支持（use_cuda）
- Batch训练
- 多worker并行训练

### 3. 检查点管理
- 定期保存checkpoint
- 保存最新checkpoint
- 支持从checkpoint恢复

## 注意事项

1. **随机种子**：
   - 训练前设置种子
   - 确保可重复性

2. **设备管理**：
   - 自动检测CUDA可用性
   - 支持CPU和GPU

3. **模块路径**：
   - 支持添加额外模块路径
   - 用于自定义策略或网络

4. **数据格式**：
   - 订单文件格式需要匹配
   - 特征列名需要正确
