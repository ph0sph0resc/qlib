# __init__.py

## 模块概述

该模块是 `qlib.contrib.meta.data_selection.data_selection` 子模块的入口文件，导出了元学习数据选择的核心类。

## 导入类

该模块从同一包的其他模块导入了以下类：

- **MetaDatasetDS**: 从 `dataset.py`` 导入，元学习数据选择数据集类
- **MetaTaskDS**: 从 `dataset.py` 导入，元学习数据选择任务类
- **MetaModelDS**: 从 `model.py` 导入，元学习数据选择模型类

## 设计模式

该模块采用了**模块封装模式**，将相关功能组织在同一个子包中，通过 `__init__.py` 提供统一的导入接口。

## 导出列表

```python
__all__ = ["MetaDatasetDS", "MetaTaskDS", "MetaModelDS"]
```

## 注意事项

1. 该 `__init__.py` 文件与上一级 `__init__.py` 功能重复，主要用于模块内部组织
2. 外部使用者建议从 `qlib.contrib.meta` 导入
3. 所有类都需要完整的参数配置才能正常工作

## 依赖关系

```
MetaModelDS
    └── MetaDatasetDS
            └── MetaTaskDS
                    ├── dataset (qlib.data.dataset.DatasetH)
                    ├── model (qlib.model.base.BaseModel)
                    └── meta_info (pd.DataFrame)
```

## 相关文档

- [dataset.py 文档](./dataset.md) - 数据集和任务的详细实现
- [model.py 文档](./model.md) - 模型的详细实现
- [net.py 文档](./net.md) - 网络结构
- [utils.py 文档](./utils.md) - 工具函数
