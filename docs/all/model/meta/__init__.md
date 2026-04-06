# model/meta/__init__.py 模块文档

## 文件概述

元学习（Meta-Learning）模块的入口文件。该模块提供元学习相关功能，帮助模型通过学习"如何学习"来提高性能。

## 模块功能概述

元学习是机器学习的前沿领域，Qlib的元学习模块支持：

1. **MetaTask**: 元学习任务，包含基础任务和元信息
2. **MetaTaskDataset**: 元学习数据集，管理多个元任务
3. **MetaModel**: 元学习模型，指导基础模型学习

## 导出内容

```python
from .task import MetaTask
from .dataset import MetaTaskDataset

__all__ = ["MetaTask", "MetaTaskDataset"]
```

## 核心概念

### 元学习（Meta-Learning）

元学习也称为"学会学习"（Learning to Learn）：

1. **传统学习**: 模型从数据中学习任务特定的模式
2. **元学习**: 模型从多个任务中学习通用的学习策略
3. **应用**: 少样本学习、快速适应、任务迁移

### Qlib中的元学习

Qlib将元学习分为两类：

1. **MetaTaskModel**: 修改任务定义
   - 学习如何创建更好的基础任务
   - 在训练前优化任务配置

2. **MetaGuideModel**: 指导训练过程
   - 在训练过程中动态调整
   - 实时优化训练策略

## 使用示例

### 基本使用

```python
from qlib.model.meta import MetaTask, MetaTaskDataset

# 创建元任务
meta_task = MetaTask(
    task=base_task_config,
    meta_info=meta_input_data
)

# 创建元数据集
meta_dataset = MetaTaskDataset(
    segments={"train": (0, 0.7), "test": (0.7, 1.0)}
)

# 准备元任务
train_tasks = meta_dataset.prepare_tasks("train")
```

## 设计理念

### 分层学习框架

```
元学习层（Meta Learning）
    ↓ 指导
基础学习层（Base Learning）
    ↓ 生成
预测层（Prediction）
```

### 处理模式

MetaTask支持三种处理模式：

1. **PROC_MODE_FULL ("full")**: 完整处理，包含训练和测试数据
2. **PROC_MODE_TEST ("test")**: 仅测试数据
3. **PROC_MODE_TRANSFER ("transfer")**: 仅元信息，用于迁移

## 与其他模块的关系

### 依赖关系

```
model/meta/
├── task.py      # 元任务定义
├── dataset.py   # 元数据集
└── model.py     # 元模型接口
```

### 协作模块

1. **qlib.model.base**: 基础模型接口
2. **qlib.data.dataset**: 数据集接口
3. **qlib.workflow**: 工作流集成

## 扩展指南

### 实现自定义元任务

```python
from qlib.model.meta import MetaTask

class CustomMetaTask(MetaTask):
    def __init__(self, task, meta_info, mode="full"):
        super().__init__(task, meta_info, mode)
        # 自定义初始化

    def get_meta_input(self):
        # 自定义元输入处理
        processed_info = self._process_meta_info(self.meta_info)
        return processed_info
```

### 实现自定义元数据集

```python
from qlib.model.meta import MetaTaskDataset

class CustomMetaDataset(MetaTaskDataset):
    def _prepare_seg(self, segment):
        # 自定义段处理逻辑
        tasks = []
        for task_config in self.task_configs:
            meta_task = self._create_meta_task(task_config)
            tasks.append(meta_task)
        return tasks
```

## 注意事项

1. **模式匹配**: 确保处理模式与使用场景匹配
2. **数据隔离**: 元数据和基础数据应该分开管理
3. **迁移能力**: 元模型应该支持跨数据集迁移
4. **效率考虑**: 元学习计算开销较大，注意性能优化
