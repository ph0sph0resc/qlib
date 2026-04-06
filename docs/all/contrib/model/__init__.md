# qlib.contrib.model 模块详细文档

## 模块概述

`qlib.contrib.model` 模块是 Qlib 框架的社区贡献模型集合，提供了多种机器学习和深度学习模型实现，用于量化投资中的市场预测和资产评分任务。

该模块通过动态导入的方式加载各种模型，如果依赖的库未安装，相应的模型会被跳过并给出提示。这种设计使得用户可以根据需要安装特定的依赖包，而不必安装所有模型所需的依赖。

### 模块特点

- **灵活的依赖管理**：所有模型都是可选依赖，未安装依赖时不会导致模块导入失败
- **统一的接口**：所有模型都继承自 `qlib.model.base.Model` 基类，提供一致的训练和预测接口
- **模型多样性**：涵盖了从传统机器学习模型到深度学习模型的多种实现
- **GPU 支持**：大多数 PyTorch 模型支持 GPU 加速训练
- **特征重要性**：部分模型提供了特征重要性分析功能

## 模型类列表

### 传统机器学习模型

#### 1. CatBoostModel

**描述**：基于 CatBoost 库实现的梯度提升决策树模型。

**特点**：
- 支持回归（RMSE）和分类（Logloss）任务
- 自动检测并使用 GPU 加速
- 支持样本权重
- 提供特征重要性分析

**依赖**：`catboost`

**适用场景**：处理类别特征较多、数据量较大的场景

#### 2. DEnsembleModel

**描述**：双集成模型（Double Ensemble Model），通过样本重加权（Sample Re-weighting）和特征选择（Feature Selection）两种策略来提升模型性能。

**特点**：
- 训练多个子模型组成集成
- 动态调整样本权重，关注难以预测的样本
- 动态选择特征，剔除不重要的特征
- 支持自定义采样比例和子模型权重

**依赖**：`lightgbm`

**适用场景**：需要处理样本不平衡或特征冗余较多的场景

#### 3. LGBModel

**描述**：基于 LightGBM 库实现的梯度提升决策树模型。

**特点**：
- 支持回归（MSE）和分类（binary）任务
- 高效的内存使用和训练速度
- 支持微调（finetune）功能
- 集成 Qlib 的日志记录系统

**依赖**：`lightgbm`

**适用场景**：大规模数据集的快速训练和预测

#### 4. XGBModel

**描述**：基于 XGBoost 库实现的梯度提升决策树模型。

**特点**：
- 支持多种损失函数
- 强大的正则化能力
- 支持样本权重
- 提供特征重要性分析

**依赖**：`xgboost`

**适用场景**：需要高精度预测的场景

#### 5. LinearModel

**描述**：线性模型，支持多种变体。

**特点**：
- 支持四种估计器：
  - `ols`：普通最小二乘法
  - `nnls`：非负最小二乘法（约束系数为正）
  - `ridge`：岭回归（L2 正则化）
  - `lasso`：Lasso 回归（L1 正则化）
- 计算速度快，可解释性强
- 支持拟合截距项

**依赖**：`scipy`, `sklearn`

**适用场景**：特征较少、需要快速基线模型的场景

### 深度学习模型

#### 6. ALSTM

**描述**：注意力增强的长短期记忆网络（Attention-Enhanced LSTM），在传统 LSTM 的基础上增加了注意力机制。

**特点**：
- 结合 LSTM 的时序建模能力和注意力机制
- 自动学习不同时间步的重要性
- 支持多层 LSTM 和 dropout
- 支持 GPU 加速

**依赖**：`torch`

**适用场景**：需要捕捉时序数据中关键信息的场景

#### 7. GATs

**描述**：图注意力网络（Graph Attention Networks），将资产关系建模为图结构，使用注意力机制学习资产间的关联。

**特点**：
- 基于 GRU 或 LSTM 作为基础模型
- 学习资产间的注意力权重
- 支持预训练模型加载
- 支持多层网络结构

**依赖**：`torch`

**适用场景**：需要利用资产间关联信息的场景

#### 8. GRU

**描述**：门控循环单元网络，相比 LSTM 参数更少，训练更快。

**特点**：
- 门控单元（更新门和重置门）
- 较少的参数量，更快的训练速度
- 支持多层和 dropout
- 支持 GPU 加速

**依赖**：`torch`

**适用场景**：大规模时序数据，需要平衡速度和性能的场景

#### 9. LSTM

**描述**：经典的长短期记忆网络，擅长捕捉长距离依赖关系。

**特点**：
- 输入门、遗忘门、输出门三重门控
- 有效解决梯度消失问题
- 支持多层和 dropout
- 支持 GPU 加速

**依赖**：`torch`

**适用场景**：需要捕捉长期依赖关系的时序预测场景

#### 10. DNNModelPytorch

**描述**：基于 PyTorch 实现的深度神经网络模型，提供高度可定制的网络结构。

**特点**：
- 灵活的网络层配置
- 支持自定义模型（通过 `pt_model_uri`）
- 支持数据并行训练
- 支持多种优化器和学习率调度器
- 集成 Qlib 工作流日志

**依赖**：`torch`

**适用场景**：需要自定义网络结构的场景

#### 11. TabnetModel

**描述**：基于 TabNet 的可解释深度学习模型，特别适合处理表格数据。

**特点**：
- 使用可解释的注意力机制选择特征
- 支持预训练和微调
- 自动特征重要性排序
- 适合处理表格数据

**依赖**：`torch`

**适用场景**：表格数据预测，需要模型可解释性的场景

#### 12. SFM_Model

**描述**：Stock Frequency Model（股票频率模型），结合频域分析和时序建模。

**特点**：
- 使用频率信息增强模型
- 结合时域和频域特征
- 独特的门控机制

**依赖**：`torch`

**适用场景**：需要利用频域信息进行预测的场景

#### 13. TCN

**描述**：时间卷积网络，使用一维卷积处理时序数据。

**特点**：
- 并行计算，训练速度快
- 感受野随网络深度指数增长
- 稳定的梯度传播
- 支持残差连接

**依赖**：`torch`

**适用场景**：需要快速训练和并行处理的时序预测场景

#### 14. ADD

**描述**：Anomaly-aware Dual De-bias Model（异常感知双重去偏模型），用于缓解数据中的分布偏移和异常值问题。

**特点**：
- 双重去偏机制
- 异常值检测和处理
- 可调节的去偏参数
- 支持 GRU 或 LSTM 作为基础模型

**依赖**：`torch`

**适用场景**：数据存在分布偏移或异常值的场景

## 模块变量

### all_model_classes

**类型**：`tuple`

**描述**：包含所有可用模型类的元组，用于遍历或获取所有模型。

**包含内容**：
- CatBoostModel
- DEnsembleModel
- LGBModel
- XGBModel
- LinearModel
- ALSTM
- GATs
- GRU
- LSTM
- DNNModelPytorch
- TabnetModel
- SFM_Model
- TCN
- ADD

**注意**：如果某个模型的依赖未安装，对应的位置会是 `None`。

### pytorch_classes

**类型**：`tuple`

**描述**：包含所有 PyTorch 模型类的元组。

**包含内容**：
- ALSTM
- GATs
- GRU
- LSTM
- DNNModelPytorch
- TabnetModel
- SFM_Model
- TCN
- ADD

## 使用示例

### 基础使用示例

```python
from qlib import init
from qlib.data import D
from qlib.workflow import R
from qlib.contrib.model import LGBModel

# 初始化 Qlib
init(provider_uri="~/.qlib/qlib_data/cn_data", region="cn")

# 加载数据集
ds = R.get_dataset()

# 创建模型实例
model = LGBModel(
    loss="mse",
    colsample_bytree=0.8,
    learning_rate=0.05,
    num_leaves=31,
)

# 训练模型
model.fit(ds)

# 进行预测
pred = model.predict(ds, segment="test")
print(pred.head())
```

### 使用 CatBoost 模型

```python
from qlib.contrib.model import CatBoostModel

# 创建 CatBoost 模型
model = CatBoostModel(
    loss="RMSE",
    depth=6,
    learning_rate=0.1,
    l2_leaf_reg=3.0,
)

# 训练
model.fit(ds, num_boost_round=500, early_stopping_rounds=30)

# 预测
pred = model.predict(ds, segment="test")

# 获取特征重要性
fi = model.get_feature_importance()
print(fi.head(10))
```

### 使用 XGBoost 模型

```python
from qlib.contrib.model import XGBModel

# 创建 XGBoost 模型
model = XGBModel(
    objective="reg:squarederror",
    max_depth=6,
    eta=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
)

# 训练
model.fit(ds, num_boost_round=500, early_stopping_rounds=30)

# 预测
pred = model.predict(ds, segment="test")
```

### 使用线性模型

```python
from qlib.contrib.model import LinearModel

# 使用岭回归
model = LinearModel(
    estimator="ridge",
    alpha=1.0,
    fit_intercept=True,
)

# 训练
model.fit(ds)

# 预测
pred = model.predict(ds, segment="test")

# 查看系数
print(f"Coef: {model.coef_}")
print(f"Intercept: {model.intercept_}")
```

### 使用 LSTM 模型

```python
from qlib.contrib.model import LSTM

# 创建 LSTM 模型
model = LSTM(
    d_feat=6,
    hidden_size=64,
    num_layers=2,
    dropout=0.2,
    n_epochs=200,
    lr=0.001,
    batch_size=2000,
    early_stop=20,
    GPU=0,  # 使用第 0 号 GPU
)

# 训练
model.fit(ds)

# 预测
pred = model.predict(ds, segment="test")
```

### 使用 ALSTM 模型（带注意力机制）

```python
from qlib.contrib.model import ALSTM

# 创建 ALSTM 模型
model = ALSTM(
    d_feat=6,
    hidden_size=64,
    num_layers=2,
    dropout=0.2,
    n_epochs=200,
    lr=0.001,
    GPU=0,
)

# 训练
model.fit(ds)

# 预测
pred = model.predict(ds, segment="test")
```

### 使用 TCN 模型

```python
from qlib.contrib.model import TCN

# 创建 TCN 模型
model = TCN(
    d_feat=6,
    n_chans=128,
    kernel_size=5,
    num_layers=5,
    dropout=0.5,
    n_epochs=200,
    lr=0.0001,
    GPU=0,
)

# 训练
model.fit(ds)

# 预测
pred = model.predict(ds, segment="test")
```

### 使用自定义 DNN 模型

```python
from qlib.contrib.model import DNNModelPytorch

# 创建自定义的 DNN 模型
model = DNNModelPytorch(
    lr=0.001,
    max_steps=300,
    batch_size=2000,
    early_stop_rounds=50,
    optimizer="adam",
    GPU=0,
    pt_model_kwargs={
        "input_dim": 158,
        "layers": (256, 128, 64),
    },
)

# 训练
model.fit(ds)

# 预测
pred = model.predict(ds, segment="test")
```

### 使用双集成模型

```python
from qlib.contrib.model import DEnsembleModel

# 创建双集成模型
model = DEnsembleModel(
    base_model="gbm",
    loss="mse",
    num_models=6,
    enable_sr=True,  # 启用样本重加权
    enable_fs=True,  # 启用特征选择
    bins_sr=10,
    bins_fs=5,
    early_stopping_rounds=50,
)

# 训练
model.fit(ds)

# 预测
pred = model.predict(ds, segment="test")
```

### 遍历所有可用模型

```python
from qlib.contrib.model import all_model_classes

# 遍历所有模型
for model_cls in all_model_classes:
    if model_cls is not None:
        print(f"可用模型: {model_cls.__name__}")
```

### 处理可选依赖

```python
try:
    from qlib.contrib.model import CatBoostModel
    model = CatBoostModel(loss="RMSE")
    print("CatBoost 模型可用")
except (ImportError, AttributeError) as e:
    print(f"CatBoost 模型不可用: {e}")
    print("请安装 catboost: pip install catboost")
```

### 在工作流配置文件中使用

```yaml
# workflow_config.yaml
model:
    class: LGBModel
    module_path: qlib.contrib.model
    kwargs:
        loss: mse
        colsample_bytree: 0.8
        learning_rate: 0.05
        num_leaves: 31
        verbose: -1
```

### 使用样本重加权

```python
from qlib.contrib.model import LGBModel
from qlib.data.dataset.weight import Reweighter

# 创建重加权器
reweighter = Reweighter()

# 创建模型并训练
model = LGBModel(loss="mse")
model.fit(ds, reweighter=reweighter)

# 预测
pred = model.predict(ds, segment="test")
```

### 模型微调（LightGBM）

```python
from qlib.contrib.model import LGBModel

# 创建并训练基础模型
model = LGBModel(loss="mse")
model.fit(ds)

# 使用微调器进一步训练
model.finetune(ds, num_boost_round=10, reweighter=reweighter)

# 预测
pred = model.predict(ds, segment="test")
```

## 常见问题

### 1. 模型导入失败

如果遇到 "ModuleNotFoundError" 的提示，说明相应模型的依赖库未安装。请根据提示安装对应的库：

```bash
# 安装 CatBoost
pip install catboost

# 安装 LightGBM
pip install lightgbm

# 安装 XGBoost
pip install xgboost

# 安装 PyTorch
pip install torch

# 安装 scikit-learn 和 scipy
pip install scikit-learn scipy
```

### 2. GPU 使用

大多数 PyTorch 模型支持 GPU 训练。通过设置 `GPU` 参数来指定使用的 GPU：

```python
# 使用第 0 号 GPU
model = LSTM(GPU=0)

# 使用 CPU
model = LSTM(GPU=-1)

# 使用指定设备
model = DNNModelPytorch(GPU="cuda:1")
```

### 3. 数据格式要求

所有模型期望的数据格式：
- 特征列：二维结构，每行表示一个样本
- 标签列：一维结构，每个样本对应一个标签值
- 不支持多标签训练（除特定模型外）

### 4. 模型选择建议

根据任务特点选择合适的模型：

- **大规模数据集**：LGBModel, XGBModel
- **类别特征多**：CatBoostModel
- **需要快速基线**：LinearModel
- **时序依赖强**：LSTM, ALSTM, GRU
- **需要并行训练**：TCN, DNNModelPytorch
- **需要模型可解释**：TabnetModel
- **资产间关联重要**：GATs
- **数据偏移问题**：ADD
- **样本不平衡**：DEnsembleModel

## 参考资料

- [Qlib 官方文档](https://qlib.readthedocs.io/)
- [CatBoost 文档](https://catboost.ai/docs/)
- [LightGBM 文档](https://lightgbm.readthedocs.io/)
- [XGBoost 文档](https://xgboost.readthedocs.io/)
- [PyTorch 文档](https://pytorch.org/docs/)
