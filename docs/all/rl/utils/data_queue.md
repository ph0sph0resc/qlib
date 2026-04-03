# qlib/rl/utils/data_queue.md 模块文档

## 文件概述
数据队列类，在主进程（生产者）产生数据并存入队列。子进程（消费者）可以从队列中检索数据点。数据点通过读取`dataset`生成。

## 类与函数

### DataQueue

```python
class DataQueue(Generic[T]):
    """
    主进程（生产者）产生数据并存储到队列中。
    子进程（消费者）可以检索数据点。
    数据点通过读取``dataset``生成。

    :class:`DataQueue`是短暂的。当``repeat``耗尽时，必须创建新的DataQueue。

    参见: class:`qlib.rl.utils.FiniteVectorEnv`的文档以了解更多背景。

    参数
    ----------
    dataset
        要读取数据的数据集。必须实现``__len__``和``__getitem__``。
    repeat
        迭代数据点多少次。使用``-1``永远迭代。
    shuffle
        如果``shuffle``为true，项目将按随机顺序读取。
    producer_num_workers
        数据加载的并发工作线程数。
    queue_maxsize
        在队列阻塞之前可放入的最大项数。

    示例
    --------
    >>> data_queue = DataQueue(my_dataset)
    >>> with data_queue:
    ...     ...

    在worker中：

    >>> for data in data_queue:
    ...     print(data)
    """
```

#### 主要属性

- **dataset**: `Sequence[T]`
  - 数据集对象
  - 必须实现`__len__`和`__getitem__`

- **repeat**: `int`
  - 迭代次数
  - -1表示无限迭代

- **shuffle**: `bool`
  - 是否随机打乱顺序

- **producer_num_workers**: `int`
  - 数据加载的并发worker数

- **queue_maxsize**: `int`
  - 队列最大大小

#### 主要方法

1. **`__enter__(self) -> DataQueue`**
   - 激活数据队列
   - 启动生产者线程

2. **`__exit__(self, exc_type, exc_val, exc_tb)`**
   - 清理数据队列

3. **`cleanup(self) -> None`**
   - 标记队列为完成
   - 清空队列中的剩余项

4. **`get(self, block: bool = True) -> Any`**
   - 从队列获取数据
   - 支持超时和阻塞模式

5. **`put(self, obj: Any, block: bool = True, timeout: int | None = None) -> None`**
   - 将数据放入队列

6. **`mark_as_done(self) -> None`**
   - 标记队列为完成

7. **`done(self) -> int`**
   - 检查队列是否完成

8. **`activate(self) -> DataQueue`**
   - 激活队列，启动生产者线程

9. **`__iter__(self) -> Generator[Any, None, None]`**
   - 迭代队列中的数据
   - 实现生成器接口

10. **`_consumer(self) -> Generator[Any, None, None]`**
   - 消费者生成器
   - 从队列获取数据

11. **`_producer(self) -> None`**
   - 生产者线程函数
   - 使用PyTorch DataLoader加载数据

## 数据流

```
主进程
  │
  ├─▶ DataQueue(dataset, repeat=-1, shuffle=True)
  │     │
  │     ├─▶ 激活生产者线程
  │     │     │
  │     │     └─▶ _producer() - 后台运行
  │     │          │
  │     │          ├─▶ 创建DataLoader
  │     │          │   (使用PyTorch多进程加载）
  │     │          │
  │     │          └─▶ for repeat in range(infinite):
  │     │               │
  │     │               ├─▶ for data in dataloader:
  │     │               │     │
  │     │               │     ├─▶ 检查是否完成
  │     │               │     │. └─▶ 如果完成则返回
  │     │               │     │
  │     │               │     ├─▶ put(data)到队列
  │     │               │     │
  │     │               │     └─▶ mark_as_done()
  │     │
  │     │     └─▶ 标记队列完成
  │
  ├─▶ 消费者进程（多个）
  │     │
  │     └─▶ for data in DataQueue:
  │          │
  │          └─▶ get()从队列
  │
  └────────────┘
```

## 生产者线程

### DataLoader使用

```python
# 使用PyTorch DataLoader进行多进程加载
from torch.utils.data import DataLoader

dataloader = DataLoader(
    dataset=dataset,
    batch_size=None,          # 每个数据点单独处理
    num_workers=producer_num_workers,
    shuffle=shuffle,
    collate_fn=lambda t: t,  # 身份处理函数
)
```

### 迭代策略

```python
# 无限迭代
repeat = 10**18 if repeat == -1 else repeat

# 有限迭代
repeat = repeat
```

### 队列管理

- 使用multiprocessing.Queue进行进程间通信
- 使用multiprocessing.Value标记完成状态

## 使用示例

### 基本使用

```python
from qlib.rl.utils import DataQueue
import pandas as pd

# 创建数据集
dataset = pd.DataFrame({
    "data": [1, 2, 3, 4, 5],
})

# 创建数据队列
data_queue = DataQueue(
    dataset=dataset,
    repeat=-1,  # 无限迭代
    shuffle=True,
)

# 使用上下文管理器
with data_queue:
    for data in data_queue:
        print(data)
```

### 在训练中使用

```python
from qlib.rl.utils import DataQueue

# 创建数据队列用于训练
train_queue = DataQueue(
    dataset=train_dataset,
    repeat=-1,  # 无限迭代训练数据
    shuffle=True,
    producer_num_workers=4,  # 4个数据加载worker
    queue_maxsize=100,
)

# 在环境工厂中使用
def env_factory():
    return EnvWrapper(
        simulator_fn,
        state_interpreter,
        action_interpreter,
        data_queue,  # 提供初始状态
        reward_fn,
    )
```

## 与其他模块的关系

### qlib.rl.utils.FiniteVectorEnv
- **使用**: 从DataQueue消耗数据
- **协议**：NaN观测表示队列耗尽
- **管理**: 追踪活跃的worker

### qlib.rl.trainer.TrainingVessel
- **使用**: 创建DataQueue作为种子迭代器
- **训练模式**: repeat=-1（无限迭代）
- **验证/测试**: repeat=1（每个数据点使用一次）

### torch.utils.data.DataLoader
- **数据加载**: 使用DataLoader的多进程功能
- **打乱**: 利用DataLoader的shuffle机制

## 性能优化

### 1. 多进程数据加载
- 使用PyTorch DataLoader的num_workers
- 充分利用CPU核心

### 2. 队列大小
- 适当的queue_maxsize避免内存问题
- 默认值为CPU核心数

### 3. 超时处理
- get()支持超时以避免第一次等待
- 后续调用使用短超时

### 4. 清理策略
- cleanup()确保资源释放
- 等待队列清空

## 注意事项

1. **线程安全**：
   - 使用multiprocessing.Value进行状态同步
   - 避免竞态条件

2. **资源释放**：
   - 确保队列被正确清空
   - 避免进程泄漏

3. **超时处理**：
   - 第一次get()有较长超时
   - 后续get()超时较短

4. **数据一致性**：
   - 确保dataset实现正确
   - __len__和__getitem__必须匹配

5. **迭代控制**：
   - repeat=-1表示无限迭代
   - 使用mark_as_done()正确终止
