# model/interpret/base.py 模块文档

## 文件概述

定义了Qlib的模型解释（Interpret）核心类，提供模型可解释性工具：
- **FeatureInt**: 特征解释器抽象基类
- **LightGBMFInt**: LightGBM模型的特征解释器

这些类帮助用户理解模型的预测行为，识别重要特征。

## 类定义

### FeatureInt 类

**继承关系**: 抽象基类

**职责**: 定义特征解释器的统一接口

#### 方法签名

##### `get_feature_importance() -> pd.Series`
```python
@abstractmethod
def get_feature_importance(self) -> pd.Series:
    """get feature importance

    Returns
    -------
        The index is the feature name.

        The greater the value, the higher importance.
    """
```

**功能**:
- 获取特征重要性
- 返回一个`pd.Series`，索引为特征名
- 值越大表示特征越重要

**返回值格式**:
```python
# 示例返回值
pd.Series({
    "feature_1": 0.85,
    "feature_2": 0.73,
    "feature_3": 0.52,
    ...
}, name="importance")
```

**子类实现要求**:
1. 返回`pd.Series`类型
2. 索引为特征名称
3. 值表示特征重要性（值越大越重要）
4. 建议按重要性降序排列

### LightGBMFInt 类

**继承关系**: FeatureInt → LightGBMFInt

**职责**: LightGBM模型的特征解释器

#### 初始化
```python
def __init__(self):
    self.model = None
```

**属性**:
- `model`: LightGBM模型对象

#### 方法签名

##### `get_feature_importance(*args, **kwargs) -> pd.Series`
```python
def get_feature_importance(self, *args, **kwargs) -> pd.Series:
    """get feature importance

    Notes
    -----
        parameters reference:
        https://lightgbm.readthedocs.io/en/latest/pythonapi/lightgbm.Booster.html?highlight=feature_importance#lightgbm.Booster.feature_importance
    """
    return pd.Series(
        self.model.feature_importance(*args, **kwargs), index=self.model.feature_name()
    ).sort_values(  # pylint: disable=E1101
        ascending=False
    )
```

**参数说明**:
- `*args, **kwargs`: 传递给`lightgbm.Booster.feature_importance()`的参数

**功能**:
- 调用LightGBM的`feature_importance()`方法
- 返回按重要性降序排列的特征重要性Series

**支持的参数**（参考LightGBM文档）:

| 参数 | 说明 |
|------|------|
| `feature_importance_type='split'` | 基于分裂次数的重要性 |
| `feature_importance_type='gain'` | 基于增益的重要性（默认） |

**示例**:
```python
from qlib.model.interpret.base import LightGBMFInt
import lightgbm as lgb

# 训练LightGBM模型
train_data = lgb.Dataset(X_train, label=y_train)
params = {"objective": "regression", "metric": "mse"}
model = lgb.train(params, train_data)

# 创建解释器
fint = LightGBMFInt()
fint.model = model

# 获取特征重要性（默认使用gain）
importance_gain = fint.get_feature_importance()
print("基于增益的特征重要性:")
print(importance_gain)

# 获取基于分裂次数的重要性
importance_split = fint.get_feature_importance(feature_importance_type='split')
print("\n基于分裂次数的特征重要性:")
print(importance_split)
```

**返回示例**:
```python
# 基于增益的重要性
feature_1    1250.34
feature_2     890.21
feature_3     567.89
feature_4     234.56
...
Name: importance, dtype: float64
```

## 类继承关系图

```
FeatureInt (抽象基类)
└── LightGBMFInt
```

## 使用示例

### 示例1：基本特征重要性分析

```python
from qlib.model.interpret.base import LightGBMFInt

# 假设已经训练好LightGBM模型
fint = LightGBMFInt()
fint.model = lgbm_model

# 获取特征重要性
importance = fint.get_feature_importance()

# 打印top 10特征
print(importance.head(10))

# 可视化
import matplotlib.pyplot as plt
importance.head(20).plot(kind='barh', figsize=(10, 8))
plt.title('Top 20 Feature Importance (LightGBM)')
plt.xlabel('Importance (Gain)')
plt.tight_layout()
plt.show()
```

### 示例2：特征选择

```python
from qlib.model.interpret.base import LightGBMFInt

# 获取特征重要性
fint = LightGBMFInt()
fint.model = lgbm_model
importance = fint.get_feature_importance()

# 选择前50个重要特征
top_features = importance.head(50).index.tolist()

# 使用重要特征重新训练模型
X_train_selected = X_train[top_features]
X_test_selected = X_test[top_features]

model = lgb.LGBMRegressor()
model.fit(X_train_selected, y_train)
```

### 示例3：特征重要性对比

```python
from qlib.model.interpret.base import LightGBMFInt

# 对比两种重要性度量
fint = LightGBMFInt()
fint.model = lgbm_model

# 基于增益
importance_gain = fint.get_feature_importance(
    feature_importance_type='gain'
)

# 基于分裂次数
importance_split = fint.get_feature_importance(
    feature_importance_type='split'
)

# 标准化后对比
importance_gain_norm = importance_gain / importance_gain.sum()
importance_split_norm = importance_split / importance_split.sum()

comparison = pd.DataFrame({
    'gain': importance_gain_norm,
    'split': importance_split_norm
})

print("特征重要性对比（标准化）:")
print(comparison.head(10))
```

## 设计模式

### 1. 策略模式

- 不同模型的解释器实现相同的接口
- 用户可以统一调用`get_feature_importance()`

### 2. 适配器模式

- LightGBMFInt适配LightGBM的特定API
- 提供统一的接口给用户

## 与其他模块的关系

### 依赖模块

- `pandas`: 数据处理
- `lightgbm`: LightGBM模型库

### 被依赖模块

- `qlib.contrib.model.lgb`: LightGBM模型实现
- `qlib.workflow`: 工作流中使用特征重要性分析

## 扩展指南

### 实现XGBoost特征解释器

```python
from qlib.model.interpret.base import FeatureInt
import pandas as pd
import xgboost as xgb

class XGBoostFInt(FeatureInt):
    """XGBoost模型的特征解释器"""

    def __init__(self):
        self.model = None

    def get_feature_importance(
        self,
        importance_type='weight'
    ) -> pd.Series:
        """获取特征重要性

        Parameters
        ----------
        importance_type : str
            'weight': 基于特征使用次数
            'gain': 基于平均增益
            'cover': 基于平均覆盖度
        """
        importances = self.model.get_booster().get_score(
            importance_type=importance_type
        )

        # 获取所有特征名
        feature_names = self.model.get_booster().feature_names

        # 填充缺失特征
        full_importances = {
            name: importances.get(name, 0)
            for name in feature_names
        }

        return pd.Series(full_importances).sort_values(ascending=False)

# 使用
fint = XGBoostFInt()
fint.model = xgb_model
importance = fint.get_feature_importance(importance_type='gain')
```

### 实现PyTorch模型特征解释器

```python
from qlib.model.interpret.base import FeatureInt
import pandas as pd
import torch
import torch.nn as nn

class PyTorchFInt(FeatureInt):
    """PyTorch模型的特征解释器（基于梯度）"""

    def __init__(self):
        self.model = None
        self.feature_names = None

    def get_feature_importance(
        self,
        X: torch.Tensor,
        y: torch.Tensor
    ) -> pd.Series:
        """基于梯度的重要性"""
        X.requires_grad_(True)

        # 前向传播
        output = self.model(X)
        loss = nn.functional.mse_loss(output, y)

        # 反向传播
        loss.backward()

        # 计算梯度绝对值
        gradients = torch.abs(X.grad).mean(dim=0)

        # 转换为Series
        importance = pd.Series(
            gradients.detach().numpy(),
            index=self.feature_names
        ).sort_values(ascending=False)

        return importance

# 使用
fint = PyTorchFInt()
fint.model = pytorch_model
fint.feature_names = feature_names

# 计算特征重要性
X_tensor = torch.tensor(X_test, dtype=torch.float32)
y_tensor = torch.tensor(y_test, dtype=torch.float32)
importance = fint.get_feature_importance(X_tensor, y_tensor)
```

## 注意事项

1. **模型类型**: LightGBMFInt仅支持LightGBM模型
2. **参数传递**: 支持将参数传递给底层的`feature_importance()`方法
3. **结果排序**: 结果按重要性降序排列，便于查看top特征
4. **内存效率**: 特征重要性计算通常很快，内存消耗小

## 应用场景

### 1. 模型诊断

```python
# 检查模型是否依赖过多特征
importance = fint.get_feature_importance()
print(f"使用特征数量: {(importance > 0).sum()}")
```

### 2. 特征工程

```python
# 识别重要特征，优化特征工程
important_features = importance[importance > importance.quantile(0.75)].index
print("高重要性最特征:", important_features.tolist())
```

### 3. 模型对比

```python
# 对比不同模型使用的特征
fint1.model = model1
fint2.model = model2

importance1 = fint1.get_feature_importance()
importance2 = fint2.get_feature_importance()

print("模型1使用特征:", importance1.index.tolist())
print("模型2使用特征:", importance2.index.tolist())
```
