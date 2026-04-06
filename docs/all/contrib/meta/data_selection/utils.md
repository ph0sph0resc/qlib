# utils.py

## 模块概述

该模块提供了数据选择元学习所需的工具函数、损失函数和基础类。主要包含：

- **ICLoss**: 信息系数（Information Coefficient）损失函数
- **preds_to_weight_with_clamp**: 预测值转换为权重的函数
- **SingleMetaBase**: 单元元学习基类

## 类定义

### ICLoss

信息系数损失函数，用于优化预测值与真实标签之间的相关性。

#### 构造方法参数

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|----------|------|
| skip_size | int | 50 | 每天跳过的最小样本数，避免样本量过小的日期 |

#### 方法

##### forward(pred, y, idx)

前向计算 IC 损失。

**参数说明：**

- **pred** (Tensor): 模型预测值
- **y** (Tensor): 真实标签值
- **idx** (MultiIndex): 索引，假设级别为 (date, inst)，且已排序

**返回值：**

- **Tensor**: 负的 IC 均值（因为损失要最小化）

**算法流程：**

1. 根据 idx 识别不同日期的分界点
2. 对每个日期单独计算 Spearman 相关系数
3. 跳过样本数小于 `skip_size` 或标准差为 0 的日期
4. 返回所有有效日期 IC 的均值的相反数

**注意事项：**

- 由于模型精度问题，结果可能与 `pandas.corr()` 略有不同
- 标准差为 0 的情况通常发生在测试数据末尾，由 `fillna(0.)` 导致

---

### SingleMetaBase

单元元学习基类，提供权重限制功能。

#### 构造方法参数

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|----------|------|
| hist_n | int | - | 历史步数（未使用） |
| clip_weight | float | None | 权重截断阈值 |
| clip_method | str | "clamp" | 截断方法："tanh" 或 "clamp" |

#### 方法

##### is_enabled()

检查是否启用了权重限制。

**返回值：**

- **bool**: 是否启用权重限制

**逻辑说明：**

- `clip_weight` 为 None 时返回 True
- `clip_method` 为 "sigmoid" 且 `clip_weight > 0` 时返回 True
- `clip_method` 为 "tanh" 或 "clamp" 且 `clip_weight > 1.0` 时返回 True

---

## 函数定义

### preds_to_weight_with_clamp(preds, clip_weight=None, clip_method="tanh")

将预测值转换为权重，可选择性地应用权重限制。

**参数说明：**

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|----------|------|
| preds | Tensor | - | 原始预测值 |
| clip_weight | float | None | 截断阈值 |
| clip_method | str | "tanh" | 截断方法 |

**截断方法说明：**

1. **"clamp"**: 将权重限制在 [1/clip_weight, clip_weight] 范围内
2. **"tanh"**: 使用 tanh 函数进行平滑截断
3. **"sigmoid"**: 使用 sigmoid 函数将权重归一化

**返回值：**

- **Tensor**: 转换后的权重

**算法示例：**

```python
# clamp 方法
weights = torch.exp(preds)
weights = weights.clamp(1.0 / clip_weight, clip_weight)

# tanh 方法
weights = torch.exp(torch.tanh(preds) * np.log(clip_weight))

# sigmoid 方法
weights = nn.Sigmoid()(preds) * clip_weight
weights = weights / torch.sum(weights) * weights.numel()
```

## 使用示例

### 使用 ICLoss

```python
import torch
from qlib.contrib.meta.data_selection.utils import ICLoss

# 创建损失函数
criterion = ICLoss(skip_size=50)

# 假设有预测值、标签和索引
pred = torch.randn(1000)
label = torch.randn(1000)
idx = pd.MultiIndex.from_tuples([...], names=['datetime', 'instrument'])

# 计算损失
loss = criterion(pred, label, idx)
print(f"IC Loss: {loss.item()}")
```

### 使用权重转换

```python
from qlib.contrib.meta.data_selection.utils import preds_to_weight_with_clamp

preds = torch.randn(100)

# 使用 tanh 方法限制权重
weights = preds_to_weight_with_clamp(
    preds,
    clip_weight=2.0,
    clip_method="tanh"
)

print(f"Weights sum: {weights.sum().item()}")
print(f"Max weight: {weights.max().item()}")
print(f"Min weight: {weights.min().item()}")
```

## 注意事项

1. **ICLoss 计算成本高**: 需要对每个日期单独计算相关性
2. **权重截断的重要性**: 防止极端权重导致投资组合不稳定
3. **不同截断方法的适用场景**:
   - "clamp": 适用于需要硬限制的场景
   - "tanh": 适用于需要平滑过渡的场景
   - "sigmoid": 适用于需要完全归一化的场景

## 相关文档

- [net.py 文档](./net.md) - 使用这些工具函数的网络结构
- [model.py 文档](./model.md) - 使用损失函数的元学习模型
