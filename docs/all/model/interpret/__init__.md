# model/interpret/__init__.py 模块文档

## 文件概述

模型解释（Interpret）模块的入口文件。该模块提供模型可解释性工具，帮助用户理解模型的预测行为和特征重要性。

## 模块功能概述

模型解释性是机器学习中的重要组成部分，Qlib提供了以下功能：

1. **特征重要性分析**: 识别哪些特征对模型预测最重要
2. **模型特定解释器**: 针对不同模型（如LightGBM）提供专用解释器

## 导出内容

该模块主要包含以下内容（通过`from .base import`导入）：

- **FeatureInt**: 特征解释器抽象基类
- **LightGBMFInt**: LightGBM模型的特征解释器

## 使用示例

### 基本使用

```python
from qlib.model.interpret import FeatureInt, LightGBMFInt

# LightGBM特征解释
fint = LightGBMFInt()
fint.model = lgbm_model

# 获取特征重要性
importance = fint.get_feature_importance()
print(importance)
```

## 设计理念

### 统一的解释接口

Qlib采用统一的模型解释接口设计：
- 所有解释器继承自`FeatureInt`基类
- 提供一致的API获取特征重要性
- 支持不同模型的专用解释器

## 与其他模块的关系

### 依赖关系

```
model/interpret/
└── base.py    # 解释器基类和实现
```

### 协作模块

1. **qlib.model.base**: 基础模型接口
2. **qlib.contrib.model**: 具体模型实现使用解释器
3. **qlib.workflow**: 工作流中集成模型解释

## 扩展指南

如需实现自定义模型解释器：

1. 继承`FeatureInt`类
2. 实现`get_feature_importance`方法：
   ```python
   from qlib.model.interpret.base import FeatureInt
   import pandas as pd

   class MyModelFInt(FeatureInt):
       def __init__(self):
           self.model = None

       def get_feature_importance(self) -> pd.Series:
           """获取特征重要性"""
           return pd.Series(
               self.model.feature_importances_,
               index=self.model.feature_names
           ).sort_values(ascending=False)
   ```

3. 使用自定义解释器：
   ```python
   fint = MyModelFInt()
   fint.model = my_model
   importance = fint.get_feature_importance()
   ```

## 注意事项

1. **模型绑定**: 使用前必须将解释器与模型绑定
2. **结果格式**: 特征重要性返回`pd.Series`，索引为特征名
3. **排序**: 结果通常按重要性降序排列
4. **标准化**: 不同模型的重要性度量可能不同
