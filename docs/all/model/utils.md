# model/utils.py 模块文档

## 文件概述

提供PyTorch相关的工具类，用于模型训练和数据处理：
- **ConcatDataset**: 连接多个数据集的工具类
- **IndexSampler**: 带索引的采样器

这些工具类主要用于深度学习模型的训练，特别是需要同时处理多个输入的场景。

## 类定义

### ConcatDataset 类

**继承关系**: `torch.utils.data.Dataset` → `ConcatDataset`

**职责**: 将多个数据集按索引连接，返回元组形式的数据

#### 初始化
```python
def __init__(self, *datasets):
    self.datasets = datasets
```

**参数说明**:
- `*datasets`: 可变数量的Dataset对象
- 所有Dataset必须具有相同的长度（取最小值）

#### 方法签名

##### `__getitem__(self, i) -> tuple`
```python
def __getitem__(self, i):
    return tuple(d[i] for d in self.datasets)
```

**功能**:
- 获取所有数据集中索引为`i`的元素
- 返回一个元组，包含各数据集对应位置的元素

**示例**:
```python
from torch.utils.data import TensorDataset
from qlib.model.utils import ConcatDataset

ds1 = TensorDataset(torch.randn(100, 10), torch.randn(100))
ds2 = TensorDataset(torch.randn(100, 5), torch.randn(100))

concat_ds = ConcatDataset(ds1, ds2)

# 获取索引为0的数据
# 返回: (tensor1, label1, tensor2, label2)
data = concat_ds[0]
# data[0]: ds1的特征 (10维)
# data[1]: ds1的标签
# data[2]: ds2的特征 (5维)
# data[3]: ds2的标签
```

##### `__len__(self) -> int`
```python
def __len__(self):
    return min(len(d) for d in self.datasets)
```

**功能**:
- 返回所有数据集长度的最小值
- 确保所有数据集都能被完整遍历

**使用场景**:
```python
# 在DataLoader中使用
data_loader = DataLoader(concat_ds, batch_size=32)

for batch in data_loader:
    # batch包含多个数据集的数据
    features1, labels1, features2, labels2 = batch
```

### IndexSampler 类

**职责**: 包装采样器，返回采样结果的同时返回原始索引

#### 初始化
```python
def __init__(self, sampler):
    self.sampler = sampler
```

**参数说明**:
- `sampler`: PyTorch采样器对象（如RandomSampler、SequentialSampler）

#### 方法签名

##### `__getitem__(self, i: int) -> tuple`
```python
def __getitem__(self, i: int):
    return self.sampler[i], i
```

**功能**:
- 返回采样器的第`i`个采样结果
- 同时返回原始索引`i`

**示例**:
```python
from torch.utils.data import RandomSampler
from qlib.model.utils import IndexSampler

sampler = RandomSampler(dataset)
indexed_sampler = IndexSampler(sampler)

# 获取第0个采样结果
# 返回: (sampled_index, 0)
sample, original_idx = indexed_sampler[0]
```

##### `__len__(self) -> int`
```python
def __len__(self):
    return len(self.sampler)
```

**功能**:
- 返回采样器的长度

**使用场景**:
```python
# 在训练中追踪原始索引
sampler = RandomSampler(dataset)
indexed_sampler = IndexSampler(sampler)

for i in range(len(indexed_sampler)):
    idx, original_idx = indexed_sampler[i]
    data = dataset[idx]
    # 使用original_idx记录或调试
```

## 设计模式

###与其他PyTorch工具的对比

| 类 | 功能 | 返回形式 |
|-----|------|----------|
| `ConcatDataset` (torch) | 连接数据集 | 返回单个数据集的元素 |
| `ConcatDataset` (qlib) | 连接多个数据集 | 返回所有数据集元素的元组 |
| `RandomSampler` | 随机采样 | 返回采样索引 |
| `IndexSampler` | 索引采样 | 返回(采样索引, 原始索引) |

## 使用示例

### 场景1：多模态数据训练

```python
from qlib.model.utils import ConcatDataset
from torch.utils.data import TensorDataset, DataLoader

# 假设有不同来源的特征
price_features = TensorDataset(price_data)
volume_features = TensorDataset(volume_data)
sentiment_features = TensorDataset(sentiment_data)

# 连接所有数据集
combined = ConcatDataset(price_features, volume_features, sentiment_features)

# DataLoader会返回所有特征的元组
loader = DataLoader(combined, batch_size=32, shuffle=True)

for batch in loader:
    price, volume, sentiment = batch
    # 训练模型使用多模态特征
    output = model(price, volume, sentiment)
```

### 场景2：带索引追踪的训练

```python
from qlib.model.utils import IndexSampler
from torch.utils.data import RandomSampler, DataLoader

sampler = RandomSampler(dataset)
indexed_sampler = IndexSampler(sampler)

loader = DataLoader(dataset, sampler=indexed_sampler, batch_size=32)

for batch in loader:
    data, indices = batch
    # indices是原始的批次索引
    # 用于记录或调试
    log_batch_info(indices)
    output = model(data)
```

### 场景3：训练和验证数据并行处理

```python
from qlib.model.utils import ConcatDataset

# 训练和验证数据需要同时获取
train_ds = TensorDataset(train_data)
val_ds = TensorDataset(val_data)

# 连接后，每次迭代同时获取训练和验证数据
paired_ds = ConcatDataset(train_ds, val_ds)

for train_batch, val_batch in DataLoader(paired_ds):
    # 同时使用训练和验证数据
    train_loss = model.train_step(train_batch)
    val_loss = model.validate_step(val_batch)
```

## 应用场景

### 1. 多输入模型

```python
class MultiInputModel(nn.Module):
    def forward(self, feature1: torch.Tensor, feature2: torch.Tensor):
        # 处理多个输入特征
        x1 = self.branch1(feature1)
        x2 = self.branch2(feature2)
        return torch.cat([x1, x2], dim=1)

# 使用ConcatDataset
ds1 = TensorDataset(f1)
ds2 = TensorDataset(f2)
combined = ConcatDataset(ds1, ds2)

for f1_batch, f2_batch in DataLoader(combined):
    output = model(f1_batch, f2_batch)
```

### 2. 原地数据增强

```python
# 原始数据和增强数据一起训练
original_ds = TensorDataset(original_data)
augmented_ds = TensorDataset(augmented_data)

combined = ConcatDataset(original_ds, augmented_ds)

for orig, aug in DataLoader(combined):
    # 损失函数考虑原始和增强数据
    loss = loss_fn(model(orig), target) + loss_fn(model(aug), target)
```

### 3. 索引记录和调试

```python
from qlib.model.utils import IndexSampler

sampler = RandomSampler(dataset, num_samples=100)
indexed_sampler = IndexSampler(sampler)

# 记录采样的原始索引
sampled_indices = [indexed_sampler[i][0] for i in range(100)]
original_indices = [indexed_sampler[i][1] for i in range(100)]

print(f"采样索引: {sampled_indices}")
print(f"原始索引: {original_indices}")
```

## 限制和注意事项

1. **长度一致性**: ConcatDataset要求所有数据集具有相同长度，取最小值
2. **类型安全**: 确保所有数据集返回的数据类型兼容
3. **内存使用**: 所有数据集同时加载到内存，注意大数据集的内存消耗
4. **索引范围**: IndexSampler假设采样器支持整数索引访问

## 性能优化建议

1. **预取数据**: 使用DataLoader的`num_workers`参数并行加载数据
2. **缓存结果**: 对于重复访问的数据，考虑缓存机制
3. **批处理**: 适当增大batch_size以利用并行计算

## 与其他模块的关系

### 依赖模块

- `torch.utils.data.Dataset`: PyTorch数据集基类
- `torch.utils.data.Sampler`: PyTorch采样器基类

### 被依赖模块

- `qlib.contrib.model.pytorch`: PyTorch模型实现
- `qlib.model.trainer`: 训练器可能使用这些工具类
