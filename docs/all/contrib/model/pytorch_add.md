# ADD (Adversarial Domain Discrimination) 模块文档

## 模块概述

`pytorch_add.py` 模块实现了对抗域判别（Adversarial Domain Discrimination，ADD）模型，该模型使用对抗学习将特征分解为：

1. **市场特征（market_feature）**：捕获市场整体趋势
2. **超额收益特征（excess_feature）**：捕获个股的超额收益信息

### 核心特性

1. **对抗域适应**：使用梯度反转层（Gradient Reversal）进行对抗学习
2. **双任务学习**：同时预测超额收益和市场状态
3. **特征重构**：通过解码器重构输入特征，提高表示学习质量
4. **预训练支持**：支持从预训练的LSTM/GRU模型初始化

## 核心类

### ADD

对抗域判别模型，继承自 `Model` 基类。

#### 构造方法参数表

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| d_feat | int | 6 | 输入特征维度 |
| hidden_size | int | 64 | 隐藏层大小 |
| num_layers | int | 2 | RNN层数 |
| dropout | float | 0.0 | 编码器Dropout比率 |
| dec_dropout | float | 0.0 | 解码器Dropout比率 |
| n_epochs | int | 200 | 训练轮数 |
| lr | float | 0.001 | 学习率 |
| metric | str | "mse" | 评估指标 |
| batch_size | int | 5000 | 批次大小 |
| early_stop | int | 20 | 早停轮数 |
| base_model | str | "GRU" | 基础RNN类型 |
| model_path | str | None | 预训练模型路径 |
| optimizer | str | "adam" | 优化器类型 |
| gamma | float | 0.1 | 梯度反转学习率 |
| gamma_clip | float | 0.4 | 梯度反转系数上限 |
| mu | float | 0.05 | 特征重构损失权重 |
| GPU | int | 0 | GPU ID |
| seed | int | None | 随机种子 |

#### 损失函数

模型使用三个损失项：

1. **超额预测损失**：预测个股超额收益的MSE
2. **市场预测损失**：预测市场状态的交叉熵
3. **特征重构损失**：重构输入特征的MSE

```python
total_loss = loss_excess + loss_market + mu * loss_reconstruction
```

## 使用示例

### 基本使用

```python
from qlib.contrib.model.pytorch_add import ADD

model = ADD(
    d_feat=6,
    hidden_size=64,
    num_layers=2,
    dropout=0.2,
    dec_dropout=0.5,
    n_epochs=200,
    lr=0.001,
    batch_size=5000,
    base_model="GRU",
    gamma=0.1,
    gamma_clip=0.4,
    mu=0.05
)

model.fit(dataset)
preds = model.predict(dataset)
```

### 使用预训练模型

```python
model = ADD(
    base_model="LSTM",
    model_path="./pretrained_lstm.pth",
    mu=0.05
)

model.fit(dataset)
```

## 注意事项

1. 模型自动将市场标签分为三类（低、中、高收益）
2. 对抗训练需要合理调整gamma参数
3. mu参数控制特征重构的重要性

## 版本历史

- 支持LSTM和GRU作为基础模型
- 支持预训练模型加载
- 支持对抗域适应
