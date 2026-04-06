# PyTorch Transformer 模型

## 模块概述

`pytorch_transformer.py` 实现了一个基于 Transformer 架构的深度学习模型，用于量化金融领域的预测任务。该模型继承自 Qlib 的 `Model` 基类，提供了完整的训练、验证和预测功能，并支持 GPU 加速、早停机制和多种优化器配置。

## 类定义

### 1. TransformerModel

TransformerModel 是 Qlib 中用于量化金融预测的主要模型类，封装了完整的训练和预测流程。

```python
class TransformerModel(Model):
    def __init__(
        self,
        d_feat: int = 20,
        d_model: int = 64,
        batch_size: int = 2048,
        nhead: int = 2,
        num_layers: int = 2,
        dropout: float = 0,
        n_epochs=100,
        lr=0.0001,
        metric="",
        early_stop=5,
        loss="mse",
        optimizer="adam",
        reg=1e-3,
        n_jobs=10,
        GPU=0,
        seed=None,
        **kwargs,
    ):
```

#### 参数说明

| 参数名称 | 类型 | 默认值 | 描述 |
|---------|------|--------|------|
| d_feat | int | 20 | 输入特征维度 |
| d_model | int | 64 | Transformer 模型的隐藏层维度 |
| batch_size | int | 2048 | 训练时的批处理大小 |
| nhead | int | 2 | 多头注意力机制的头数 |
| num_layers | int | 2 | Transformer 编码器的层数 |
| dropout | float | 0 | Dropout 正则化率 |
| n_epochs | int | 100 | 训练的最大 epoch 数 |
| lr | float | 0.0001 | 学习率 |
| metric | str | "" | 评估指标（当前版本未使用） |
| early_stop | int | 5 | 早停机制的 patience 值 |
| loss | str | "mse" | 损失函数类型（目前仅支持 MSE） |
| optimizer | str | "adam" | 优化器类型（支持 adam 或 gd） |
| reg | float | 1e-3 | 正则化参数 |
| n_jobs | int | 10 | 并行任务数（目前未使用） |
| GPU | int | 0 | GPU 设备编号（-1 表示使用 CPU） |
| seed | int | None | 随机种子 |

#### 核心功能

##### use_gpu 属性

```python
@property
def use_gpu(self):
    return self.device != torch.device("cpu")
```

返回布尔值，表示是否使用 GPU 加速。

##### 损失函数

```python
def mse(self, pred, label):
    loss = (pred.float() - label.float()) ** 2
    return torch.mean(loss)

def loss_fn(self, pred, label):
    mask = ~torch.isnan(label)
    if self.loss == "mse":
        return self.mse(pred[mask], label[mask])
    raise ValueError("unknown loss `%s`" % self.loss)
```

- `mse()`: 计算均方误差损失
- `loss_fn()`: 带掩码的损失计算，忽略 NaN 值

##### 评估指标

```python
def metric_fn(self, pred, label):
    mask = torch.isfinite(label)
    if self.metric in ("", "loss"):
        return -self.loss_fn(pred[mask], label[mask])
    raise ValueError("unknown metric `%s`" % self.metric)
```

计算模型评估指标（当前版本仅返回负损失值）。

##### 训练与测试

```python
def train_epoch(self, x_train, y_train):
    # 单 epoch 训练实现

def test_epoch(self, data_x, data_y):
    # 单 epoch 测试实现
```

- `train_epoch()`: 执行单个 epoch 的训练
- `test_epoch()`: 执行单个 epoch 的测试，返回平均损失和得分

##### 模型拟合

```python
def fit(
    self,
    dataset: DatasetH,
    evals_result=dict(),
    save_path=None,
):
```

训练模型的主函数：
1. 准备训练、验证和测试数据
2. 执行多 epoch 训练
3. 实现早停机制
4. 保存最佳模型参数

##### 预测

```python
def predict(self, dataset: DatasetH, segment: Union[Text, slice] = "test"):
```

使用训练好的模型进行预测：
1. 准备预测数据
2. 执行批处理预测
3. 返回预测结果的 Pandas Series

### 2. PositionalEncoding

位置编码模块，为 Transformer 模型添加序列位置信息。

```python
class PositionalEncoding(nn.Module):
    def __init__(self, d_model, max_len=1000):
        super(PositionalEncoding, self).__init__()
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0).transpose(0, 1)
        self.register_buffer("pe", pe)

    def forward(self, x):
        return x + self.pe[: x.size(0), :]
```

#### 参数说明

| 参数名称 | 类型 | 默认值 | 描述 |
|---------|------|--------|------|
| d_model | int | - | 模型的隐藏层维度 |
| max_len | int | 1000 | 最大序列长度 |

### 3. Transformer

Transformer 模型的核心网络结构。

```python
class Transformer(nn.Module):
    def __init__(self, d_feat=6, d_model=8, nhead=4, num_layers=2, dropout=0.5, device=None):
        super(Transformer, self).__init__()
        self.feature_layer = nn.Linear(d_feat, d_model)
        self.pos_encoder = PositionalEncoding(d_model)
        self.encoder_layer = nn.TransformerEncoderLayer(d_model=d_model, nhead=nhead, dropout=dropout)
        self.transformer_encoder = nn.TransformerEncoder(self.encoder_layer, num_layers=num_layers)
        self.decoder_layer = nn.Linear(d_model, 1)
        self.device = device
        self.d_feat = d_feat

    def forward(self, src):
        # src [N, F*T] --> [N, T, F]
        src = src.reshape(len(src), self.d_feat, -1).permute(0, 2, 1)
        src = self.feature_layer(src)

        # src [N, T, F] --> [T, N, F]
        src = src.transpose(1, 0)

        mask = None
        src = self.pos_encoder(src)
        output = self.transformer_encoder(src, mask)

        # [T, N, F] --> [N, T*F]
        output = self.decoder_layer(output.transpose(1, 0)[:, -1, :])

        return output.squeeze()
```

#### 参数说明

| 参数名称 | 类型 | 默认值 | 描述 |
|---------|------|--------|------|
| d_feat | int | 6 | 输入特征维度 |
| d_model | int | 8 | 模型的隐藏层维度 |
| nhead | int | 4 | 多头注意力机制的头数 |
| num_layers | int | 2 | Transformer 编码器的层数 |
| dropout | float | 0.5 | Dropout 正则化率 |
| device | torch.device | None | 计算设备 |

#### 前向传播过程

1. **特征重构**：将输入的 `[N, F*T]` 形状数据重构为 `[N, T, F]`（N：样本数，T：时间步数，F：特征数）
2. **特征投影**：通过线性层将输入特征投影到 d_model 维度
3. **位置编码**：添加位置信息编码
4. **Transformer 编码**：通过 Transformer 编码器处理序列数据
5. **输出解码**：取最后一个时间步的输出，通过线性层得到预测结果

## 架构图

```mermaid
graph TD
    A[Input Data<br/>[N, F*T]] --> B[Feature Reconstruction<br/>[N, T, F]]
    B --> C[Feature Projection<br/>[N, T, d_model]]
    C --> D[Position Encoding<br/>[T, N, d_model]]
    D --> E[Transformer Encoder<br/>[T, N, d_model]]
    E --> F[Last Step Output<br/>[N, d_model]]
    F --> G[Linear Decoder<br/>[N, 1]]
    G --> H[Output<br/>[N]]
```

## 使用示例

### 基础使用

```python
from qlib.contrib.model.pytorch_transformer import TransformerModel
from qlib.data.dataset import DatasetH

# 准备数据集
dataset = DatasetH(...)

# 初始化模型
model = TransformerModel(
    d_feat=20,
    d_model=64,
    batch_size=2048,
    nhead=2,
    num_layers=2,
    dropout=0,
    n_epochs=100,
    lr=0.0001,
    early_stop=5,
    loss="mse",
    optimizer="adam",
    reg=1e-3,
    GPU=0
)

# 训练模型
evals_result = {}
model.fit(dataset, evals_result)

# 预测
preds = model.predict(dataset, segment="test")
```

### 配置文件使用

在 Qlib 的工作流配置文件中使用：

```yaml
# workflow_config_transformer.yaml
model:
    class: TransformerModel
    module_path: qlib.contrib.model.pytorch_transformer
    kwargs:
        d_feat: 20
        d_model: 64
        batch_size: 2048
        nhead: 2
        num_layers: 2
        dropout: 0
        n_epochs: 100
        lr: 0.0001
        early_stop: 5
        loss: mse
        optimizer: adam
        reg: 0.001
        GPU: 0

dataset:
    ...
```

通过命令行运行：

```bash
qrun examples/benchmarks/Transformer/workflow_config_transformer_Alpha360.yaml
```

## 总结

该实现提供了一个完整的 Transformer 模型用于量化金融预测任务，包含：
- 灵活的超参数配置
- 完整的训练和评估流程
- GPU 加速支持
- 早停机制
- 模型保存和加载
- 与 Qlib 框架的无缝集成

模型采用经典的 Transformer 架构，通过位置编码和注意力机制捕捉时间序列数据中的依赖关系，适用于股票价格预测、收益率预测等量化金融任务。
