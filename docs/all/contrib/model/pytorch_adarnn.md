# ADARNN (Adaptive RNN) 模块文档

## 模块概述

`pytorch_adarnn.py` 模块实现了自适应RNN（Adaptive RNN）模型，该模型结合了**领域自适应**和**Boosting**技术，用于跨域时序预测。

### 核心特性

1. **领域自适应**：通过迁移学习机制，将源域知识迁移到目标域
2. **动态**调整**：基于Boosting策略动态调整不同时间步的权重
3. **多种迁移损失**：支持MMD、CORAL、Cosine、KL、JS等多种域适应损失
4. **双阶段训练**：预训练阶段 + Boosting阶段

## 核心类

### ADARNN

自适应RNN模型，继承自 `Model` 基类。

#### 构造方法参数表

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| d_feat | int | 6 | 输入特征维度 |
| hidden_size | int | 64 | 隐藏层大小 |
| num_layers | int | 2 | RNN层数 |
| dropout | float | 0.0 | Dropout比率 |
| n_epochs | int | 200 | 总训练轮数 |
| pre_epoch | int | 40 | 预训练阶段轮数 |
| dw | float | 0.5 | 迁移损失权重 |
| loss_type | str | "cosine" | 迁移损失类型 |
| len_seq | int | 60 | 序列长度 |
| lr | float | 0.001 | 学习率 |
| metric | str | "mse" | 评估指标 |
| batch_size | int | 2000 | 批次大小 |
| early_stop | int | 20 | 早停轮数 |
| n_splits | int | 2 | 数据域分割数 |
| GPU | int | 0 | GPU ID |
| seed | int | None | 随机种子 |

## 使用示例

```python
from qlib.contrib.model.pytorch_adarnn import ADARNN

model = ADARNN(
    d_feat=6,
    hidden_size=64,
    n_epochs=200,
    pre_epoch=40,
    loss_type="cosine",
    len_seq=60,
    n_splits=2
)

model.fit(dataset)
preds = model.predict(dataset)
```
