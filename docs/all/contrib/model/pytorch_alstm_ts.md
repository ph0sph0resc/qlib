# ALSTM_TS (Attention LSTM with Timeseries) 模块文档

## 模块概述

`pytorch_alstm_ts.py` 模块实现了带时间序列支持的注意力LSTM模型（ALSTM_TS），与ALSTM相比，该版本支持：

1. **时间序列数据**：直接处理多时间步的时序数据
2. **注意力机制**：自动关注重要的时间步
3. **GRU/LSTM支持**：支持GRU和LSTM作为基础RNN
4. **简洁的数据格式**：输入为[batch, feature_dim * seq_len]

### 核心特性

1. **自动序列重塑**：将展平的特征重塑为[batch, seq_len, feature_dim]
2. **注意力加权**：对RNN输出应用注意力机制
3. **双头输出**：结合最终状态和注意力输出

## 核心类

### ALSTM

带时间序列支持的注意力LSTM模型，继承自 `Model` 基类。

#### 构造方法参数表

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| d_feat | int | 6 | 输入特征维度（每时间步） |
| hidden_size | int | 64 | 隐藏层大小 |
| num_layers | int | 2 | RNN层数 |
| dropout | float | 0.0 | Dropout比率 |
| n_epochs | int | 200 | 训练轮数 |
| lr | float | 0.001 | 学习率 |
| metric | str | "" | 早停使用的评估指标 |
| batch_size | int | 2000 | 批次大小 |
| early_stop | int | 20 | 早停轮数 |
| loss | str | "mse" | 损失函数类型 |
| optimizer | str | "adam" | 优化器类型 |
| GPU | int | 0 | GPU ID |
| seed | int | None | 随机种子 |

## 使用示例

### 基本使用

```python
from qlib.contrib.model.pytorch_alstm_ts import ALSTM

model = ALSTM(
    d_feat=6,
    hidden_size=64,
    num_layers=2,
    dropout=0.2,
    n_epochs=200,
    lr=0.001,
    batch_size=2000,
    early_stop=20,
    loss="mse",
    optimizer="adam",
    GPU=0,
    seed=42
)

model.fit(dataset)
preds = model.predict(dataset)
```

## 注意事项

1. 输入数据格式为：[batch, feature_dim * seq_len]
2. 模型会自动将数据重塑为[batch, seq_len, feature_dim]
3. 输出为展平的一维向量

## 与ALSTM的区别

| 特性 | ALSTM_TS | ALSTM |
|------|----------|--------|
| 输入格式 | [batch, feature*seq] | [batch, seq, feature+1] |
| 标签处理 | 独立标签 | 在特征最后一列中 |
| 数据加载器 | 标准PyTorch Data | ConcatDataset |
| 使用场景 | 时序预测 | 通用时序任务 |

## 版本历史

- 支持GRU和LSTM
- 支持注意力机制
- 自动处理时间序列重塑
