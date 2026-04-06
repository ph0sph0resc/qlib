# `__init__.py`

## 模块概述

`qlib.contrib.meta` 模块是 Qlib 中元学习（Meta-Learning）相关的核心模块，提供了用于元学习的数据集接口。元学习是一种"学会学习"的机器学习方法，能够通过多个任务的学习经验来快速适应新任务。

该模块主要提供了三种元学习数据集接口：
- `MetaTaskDS`：基于任务的元学习数据集
- `MetaDatasetDS`：基于数据集的元学习数据集
- `MetaModelDS`：基于模型的元学习数据集

## 导出内容

| 类名 | 说明 |
|------|------|
| `MetaTaskDS` | 任务级元学习数据集 |
| `MetaDatasetDS` | 数据集级元学习数据集 |
| `MetaModelDS` | 模型级元学习数据集 |

## 使用示例

```python
from qlib.contrib.meta import MetaTaskDS, MetaDatasetDS, MetaModelDS

# 使用元学习数据集进行任务训练
# 具体使用方式请参考各个类的详细文档
```

## 相关模块

- `qlib.contrib.meta.data_selection`：数据选择相关的元学习实现

## 注意事项

1. 元学习数据集通常用于需要跨任务迁移学习的场景
2. 不同的元学习数据集适用于不同的元学习策略
3. 使用前需要准备好相关的任务和数据集配置

## 参考资源

- [元学习相关论文](https://arxiv.org/abs/1703.03400)
- [Qlib 元学习示例](https://github.com/microsoft/qlib/tree/main/examples/meta)
