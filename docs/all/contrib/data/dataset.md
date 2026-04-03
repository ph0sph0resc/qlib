# `dataset.py`

## 模块概述

`qlib.contrib.data.dataset` 模块提供了内存增强的时间序列数据集类 \`MTSDatasetH\`。这个数据集专为深度学习模型设计，支持内存状态管理和灵活的采样策略。

该模块是 Qlib 中处理时间序列数据的核心组件，特别适合需要跨样本记忆的模型（如 RNN、LSTM 等）。

## 类说明

### MTSDatasetH

内存增强时间序列数据集（Memory Augmented Time Series Dataset）。

#### 构造方法

\`\`\`python
def __init__(
    self,
    handler,              # 数据处理器
    segments,            # 数据分割配置
    seq_len=60,         # 序列长度
    horizon=0,          # 预测视界
    num_states=0,        # 记忆状态数量
    memory_mode="sample", # 记忆模式（sample 或 daily）
    batch_size=-1,       # 批次大小（<0 表示按天采样）
    n_samples=None,       # 每天的样本数
    shuffle=True,         # 是否打乱数据
    drop_last=False,       # 是否丢弃最后不完整的批次
    input_size=None,      # 输入大小（向后兼容）
)
\`\`\` 

**参数说明：**

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| \`handler\` | DataHandler | 必填 | 数据处理器 |
| \`segments\` | dict | 必填 | 数据分割配置 |
| \`seq_len\` | int | 60 | 时间序列长度 |
| \`horizon\` | int | 0 | 标签预测视界（0 表示自动推断） |
| \`num_states\` | int | 0 | 记忆状态维度 |
| \`memory_mode\` | str | "sample" | 记忆模式："sample" 或 "daily" |
| \`batch_size\` | int | -1 | 批次大小，负值表示按天采样 |
| \`n_samples\` | int | None | 每天的采样数量 |
| \`shuffle\` | bool | True | 是否打乱数据 |
| \`drop_last\` | bool | False | 是否丢弃最后不完整的批次 |
| \`input_size\` | int | None | 输入特征大小（用于 Alpha360 兼容） |

#### 重要方法

##### \`setup_data(handler_kwargs=None, **kwargs)\`

设置数据，预处理并构建数据索引。

**功能：**
- 从 handler 获取数据
- 转换为 numpy 数组
- 构建批次切片
- 初始化记忆状态

##### \`train()\`

启用训练模式。

**效果：**
- 恢复原始的 batch_size, n_samples, drop_last, shuffle 设置
- 允许数据打乱

##### \`eval()\`

启用评估模式。

**效果：**
- 设置 batch_size = -1（按天采样）
- 禁用数据打乱
- 不丢弃最后不完整的批次

##### \`assign_data(index, vals)\`

分配记忆状态数据。

**参数：**
- \`index\`：索引位置
- \`vals\`：要分配的值（numpy 数组或 torch 张量）

##### \`clear_memory()\`

清空所有记忆状态。

##### \`restore_index(index)\`

根据索引恢复原始数据索引。

**返回：** (instrument, datetime) 元组

##### \`restore_daily_index(daily_index)\`

根据日期索引恢复原始日期。

**返回：** pandas Index

#### 迭代器

数据集实现了迭代器接口，可以用于批处理：

\`\`\`python
for batch in dataset:
    data = batch["data"]      # 特征数据
    label = batch["label"]    # 标签数据
    state = batch["state"]    # 记忆状态
    index = batch["index"]    # 数据索引
    daily_index = batch["daily_index"]      # 日期索引
    daily_count = batch["daily_count"]      # 每天的样本数
\`\`\`

**批次数据结构：**

| 键 | 类型 | 说明 |
|------|------|------|
| \`data\` | torch.Tensor | 特征数据 [batch_size, seq_len, feature_dim] |
| \`label\` | torch.Tensor | 标签数据 [batch_size] |
| \`state\` | torch.Tensor | 记忆状态 [batch_size, seq_len, num_states] |
| \`index\` | np.ndarray | 数据索引 |
| \`daily_index\` | np.ndarray | 日期索引 |
| \`daily_count\` | np.ndarray | 每天的样本数 |

#### 采样模式

##### 1. 正常采样（batch_size > 0）

- 随机选择样本
- 适用于训练阶段
- 支持样本级别的记忆

##### 2. 按天采样（batch_size < 0）

- 每次获取所有股票的数据
- 适用于评估/推理阶段
- 支持天级别的记忆
- 可以通过 \`n_samples\` 进行子采样

## 使用示例

### 基本使用

\`\`\`python
from qlib.contrib.data.dataset import MTSDatasetH
from qlib.contrib.data.handler import Alpha158

# 创建数据处理器
handler = Alpha158(
    instruments="csi500",
    start_time="2020-01-01",
    end_time="2023-12-31"
)

# 创建数据集
dataset = MTSDatasetH(
    handler=handler,
    segments={
        "train": ("2020-01-01", "2021-12-31"),
        "valid": ("2022-01-01", "2022-12-31"),
        "test": ("2023-01-01", "2023-12-31")
    },
    seq_len=60,
    batch_size=128,
    num_states=32,
    memory_mode="sample"
)

# 设置数据
dataset.setup_data()

# 训练模式
dataset.train()
for batch in dataset:
    # 训练逻辑
    pass

# 评估模式
dataset.eval()
for batch in dataset:
    # 评估逻辑
    pass
\`\`\`

### 带记忆状态的使用

\`\`\`python
# 创建带记忆的数据集
dataset = MTSDatasetH(
    handler=handler,
    segments=segments,
    seq_len=60,
    num_states=32,        # 启用32维记忆状态
    memory_mode="daily",   # 使用天级别记忆
    batch_size=-1,         # 按天采样
)

dataset.setup_data()

# 在训练循环中更新记忆
for batch in dataset:
    # 前向传播
    outputs = model(batch["data"], batch["state"])
    
    # 更新记忆状态
    new_states = outputs["memory_states"]
    dataset.assign_data(batch["index"], new_states)
\`\`\`

### 训练/评估切换

\`\`\`python
# 训练阶段
dataset.train()
for epoch in range(num_epochs):
    for batch in dataset:
        # 训练逻辑
        pass

# 评估阶段
dataset.eval()
for batch in dataset:
    # 评估逻辑
    pass

# 清空记忆
dataset.clear_memory()
\`\`\`

## 数据流程图

\`\`\`mermaid
graph TD
    A[原始数据] --> B[DataHandler]
    B --> C[setup_data]
    C --> D[预处理]
    D --> E[构建切片索引]
    E --> F[初始化记忆]
    F --> G[数据集就绪]
    
    G --> H{采样模式}
    H -->|训练| I[正常采样]
    H -->|评估| J[按天采样]
    
    I --> K[生成批次]
    J --> K
    K --> L[返回字典: data, label, state, index]
\`\`\`

## 性能优化

1. **内存优化**：
   - 预取数据到 numpy 数组
   - 使用共享内存避免复制
   - 支持批量索引访问

2. **缓存机制**：
   - 预先构建所有切片索引
   - 避免重复计算

3. **并行处理**：
   - 支持按天并行采样
   - 可以指定 \`n_samples\` 进行子采样

## 注意事项

1. **horizon 参数**：
   - 如果设为 \`horizon=0\`，会自动从标签表达式推断
   - 使用 \`num_states > 0\` 时必须指定 \`horizon\` 以避免数据泄露

2. **memory_mode 选择**：
   - \`"sample"\`：每个样本独立记忆，适合 batch_size > 0
   - \`"daily"\`：每天共享记忆，适合 batch_size < 0

3. **批次大小**：
   - 正值：普通批次采样
   - 负值：按天采样（绝对值表示每天的数据数量）

4. **设备支持**：
   - 自动检测 CUDA 可用性
   - 数据自动转换为相应设备的张量

5. **数据泄露**：
   - 确保标签视界设置正确
   - 记忆状态不应包含未来信息

## 相关模块

- \`qlib.data.dataset.DatasetH\`：基础数据集类
- \`qlib.data.dataset.handler\`：数据处理器
- \`qlib.contrib.data.handler\`：贡献模块的数据处理器

## 参考资源

- [Qlib 数据集文档](https://qlib.readthedocs.io/en/latest/component/data.html#dataset)
- [时间序列记忆网络](https://arxiv.org/abs/1511.04242)
