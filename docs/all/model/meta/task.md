# model/meta/task.py 模块文档

## 文件概述

定义了Qlib元学习（Meta-Learning）的任务组件：
- **MetaTask**: 元任务，包含基础任务和元信息

MetaTask是元学习框架的基本单元，封装了基础任务配置和元学习所需的额外信息。

## 类定义

### MetaTask 类

**职责**: 单个元任务，作为MetaDataset的组件

#### 类属性

```python
PROC_MODE_FULL = "full"        # 完整处理模式
PROC_MODE_TEST = "test"        # 测试模式
PROC_MODE_TRANSFER = "transfer"  # 迁移模式
```

#### 初始化
```python
def __init__(self, task: dict, meta_info: object, mode: str = PROC_MODE_FULL):
    self.task = task
    self.meta_info = meta_info
    self.mode = mode
```

**参数说明**:

| 参数 | 类型 | 说明 |
|------|------|------|
| `task` | dict | 基础任务配置字典，包含模型和数据集配置 |
| `meta_info` | object | 元信息，用于元学习的数据或上下文 |
| `mode` | str | 处理模式，默认为`PROC_MODE_FULL` |

**功能**:
- 存储基础任务配置
- 存储原始的元输入信息
- 设置处理模式

#### 方法签名

##### `get_dataset() -> Dataset`
```python
def get_dataset(self) -> Dataset:
    return init_instance_by_config(self.task["dataset"], accept_types=Dataset)
```

**功能**:
- 从任务配置中获取数据集
- 使用`init_instance_by_config`实例化数据集
- 返回Dataset对象

**示例**:
```python
from qlib.model.meta.task import MetaTask

# 创建元任务
meta_task = MetaTask(
    task={
        "model": {...},
        "dataset": {
            "class": "DatasetH",
            "module_path": "qlib.data.dataset",
            "kwargs": {...}
        }
    },
    meta_info={"performance": 0.85}
)

# 获取数据集
dataset = meta_task.get_dataset()
# dataset是一个Dataset实例
```

##### `get_meta_input() -> object`
```python
def get_meta_input(self) -> object:
    """Return the **processed** meta_info"""
    return self.meta_info
```

**功能**:
- 返回处理后的元信息
- 当前实现直接返回原始meta_info
- 子类可以重写以提供预处理逻辑

##### `__repr__()` -> str
```python
def __repr__(self):
    return f"MetaTask(task={self.task}, meta_info={self.meta_info})"
```

**功能**:
- 返回MetaTask的字符串表示
- 用于调试和日志输出

## 处理模式详解

### PROC_MODE_FULL（"full"）

**说明**: 完整处理模式

**包含信息**:
- 训练数据（X_train, y_train）
- 测试数据（X_test, y_test）
- 元信息（meta_info）

**使用场景**:
- 元模型训练阶段
- 需要完整的历史数据学习模式

**示例**:
```python
# 训练阶段的元任务
meta_task = MetaTask(
    task=task_config,
    meta_info={
        "X_train": train_features,
        "y_train": train_labels,
        "X_test": test_features,
        "y_test": test_labels,
        "performance": test_score
    },
    mode="full"
)
```

### PROC_MODE_TEST（"test"）

**说明**: 测试模式

**包含信息**:
- 测试数据（X_test, y_test）
- 元信息（meta_info）

**不包含**:
- 训练数据（X_train, y_train）

**使用场景**:
- 元模型推理阶段
- 仅需要测试数据的场景

**示例**:
```python
# 推理阶段的元任务
meta_task = MetaTask(
    task=task_config,
    meta_info={
        "X_test": test_features,
        "y_test": test_labels
    },
    mode="test"
)
```

### PROC_MODE_TRANSFER（"transfer"）

**说明**: 迁移模式

**包含信息**:
- 仅元信息（meta_info）

**不包含**:
- 训练数据
- 测试数据

**使用场景**:
- 跨数据集迁移学习
- 元模型在不同数据集间迁移

**示例**:
```python
# 迁移阶段的元任务
meta_task = MetaTask(
    task=task_config,
    meta_info={
        "task_characteristics": {
            "data_size": 1000,
            "feature_dim": 50,
            "domain": "finance"
        }
    },
    mode="transfer"
)
```

## 使用示例

### 示例1：基本使用

```python
from qlib.model.meta.task import MetaTask

# 定义基础任务
task_config = {
    "model": {
        "class": "LGBModel",
        "module_path": "qlib.contrib.model.gbdt",
        "kwargs": {
            "loss": "mse",
            "colsample_bytree": 0.8
        }
    },
    "dataset": {
        "class": "DatasetH",
        "module_path": "qlib.data.dataset",
        "kwargs": {
            "handler": {
                "class": "Alpha158",
                "module_path": "qlib.contrib.data.handler"
            }
        }
    }
}

# 定义元信息
meta_info = {
    "task_id": "task_001",
    "performance": {
        "train_score": 0.82,
        "test_score": 0.78
    },
    "hyperparameters": {
        "learning_rate": 0.1,
        "num_trees": 100
    }
}

# 创建元任务
meta_task = MetaTask(
    task=task_config,
    meta_info=meta_info,
    mode="full"
)

# 使用元任务
dataset = meta_task.get_dataset()
meta_input = meta_task.get_meta_input()
print(f"Mode: {meta_task.mode}")
```

### 示例2：元模型训练

```python
# 准备元任务列表
train_meta_tasks = []

for task_config in task_configs:
    # 训练基础模型
    model = init_instance_by_config(task_config["model"])
    dataset = init_instance_by_config(task_config["dataset"])
    model.fit(dataset)

    # 评估模型
    test_pred = model.predict(dataset, segment="test")
    performance = evaluate_performance(test_pred, test_labels)

    # 创建元任务
    meta_task = MetaTask(
        task=task_config,
        meta_info={
            "model_performance": performance,
            "task_config": task_config
        },
        mode="full"
    )
    train_meta_tasks.append(meta_task)

# 训练元模型
meta_model.fit(train_meta_tasks)
```

### 示例3：元模型推理

```python
# 准备测试元任务
test_meta_tasks = []

for task_config in test_task_configs:
    # 创建测试元任务（不需要训练数据）
    meta_task = MetaTask(
        task=task_config,
        meta_info={
            "task_characteristics": extract_characteristics(task_config)
        },
        mode="test"
"    )
    test_meta_tasks.append(meta_task)

# 元模型推理，生成优化后的任务
optimized_tasks = meta_model.inference(test_meta_tasks)

# 使用优化后的任务
for task_config in optimized_tasks:
    model = init_instance_by_config(task_config["model"])
    dataset = init_instance_by_config(task_config["dataset"])
    model.fit(dataset)
```

### 示例4：跨数据集迁移

```python
# 在源数据集上训练元模型
source_tasks = load_tasks_from_source_dataset()
source_meta_tasks = [
    MetaTask(task, extract_meta_info(task), mode="full")
    for task in source_tasks
]
meta_model.fit(source_meta_tasks)

# 迁移到目标数据集
target_tasks = load_tasks_from_target_dataset()
target_meta_tasks = [
    MetaTask(
        task,
        extract_task_characteristics(task),
        mode="transfer"  # 仅迁移模式，不需要具体数据
    )
    for task in target_tasks
]

# 使用学到的知识优化目标任务
optimized_tasks = meta_model.inference(target_meta_tasks)
```

## 数据处理模式对比

| 模式 | X_train | y_train | X_test | y_test | meta_info | 使用场景 |
|------|---------|---------|--------|--------|-----------|----------|
| `full` | ✓ | ✓ | ✓ | ✓ | ✓ | 元模型训练 |
| `test` | ✗ | ✗ | ✓ | ✓ | ✓ | 元模型推理 |
| `transfer` | ✗ | ✗ | ✗ | ✗ | ✓ | 跨数据集迁移 |

## 设计模式

### 1. 数据封装模式

- MetaTask封装任务配置和元信息
- 提供统一的数据访问接口

### 2. 策略模式

- 通过mode参数选择不同的处理策略
- 支持灵活的数据处理方式

## 与其他模块的关系

### 依赖模块

- `qlib.data.dataset.Dataset`: 数据集接口
- `qlib.utils`: 工具函数（init_instance_by_config）

### 被依赖模块

- `qlib.model.meta.dataset`: MetaTaskDataset使用MetaTask
- `qlib.model.meta.model`: MetaModel使用MetaTask

## 扩展指南

### 实现自定义元任务

```python
from qlib.model.meta.task import MetaTask
import pandas as pd

class EnhancedMetaTask(MetaTask):
    """增强的元任务，支持预处理"""

    def __init__(self, task, meta_info, mode="full"):
        super().__init__(task, meta_info, mode)
        self._processed = False

    def get_meta_input(self):
        """返回处理后的元信息"""
        if not self._processed:
            self.meta_info = self._preprocess_meta_info(self.meta_info)
            self._processed = True
        return self.meta_info

    def _preprocess_meta_info(self, meta_info):
        """预处理元信息"""
        if "performance" in meta_info:
            # 标准化性能指标
            perf = meta_info["performance"]
            meta_info["normalized_score"] = (
                perf["test_score"] / perf["train_score"]
            )

        if "hyperparameters" in meta_info:
            # 提取关键超参数
            meta_info["key_params"] = {
                "lr": meta_info["hyperparameters"].get("learning_rate"),
                "trees": meta_info["hyperparameters.get("num_trees")
            }

        return meta_info

# 使用
meta_task = EnhancedMetaTask(
    task=task_config,
    meta_info=raw_meta_info,
    mode="full"
)

# 获取处理后的元信息
processed_info = meta_task.get_meta_input()
```

### 实现带缓存的元任务

```python
class CachedMetaTask(MetaTask):
    """支持缓存的元任务"""

    def __init__(self, task, meta_info, mode="full", cache_dir=None):
        super().__init__(task, meta_info, mode)
        self.cache_dir = cache_dir
        self._dataset_cache = None

    def get_dataset(self):
        """获取数据集（支持缓存）"""
        if self._dataset_cache is None:
            dataset = super().get_dataset()

            # 如果启用缓存，保存到文件
            if self.cache_dir is not None:
                cache_file = os.path.join(
                    self.cache_dir,
                    f"dataset_{hash(str(self.task))}.pkl"
                )
                if os.path.exists(cache_file):
                    # 从缓存加载
                    dataset = load_from_cache(cache_file)
                else:
                    # 保存到缓存
                    save_to_cache(dataset, cache_file)

            self._dataset_cache = dataset

        return self._dataset_cache
```

## 注意事项

1. **模式选择**: 根据使用场景选择正确的PROC_MODE
2. **元信息设计**: meta_info应包含元学习所需的充分信息
3. **序列化**: MetaTask对象应该是可序列化的，以便持久化
4. **内存管理**: 大型元信息注意内存使用

## 性能优化建议

1. **惰性加载**: 延迟加载数据集，按需获取
2. **缓存机制**: 缓存常用对象（如数据集）
3. **批量处理**: 对多个MetaTask进行批量处理
4. **预处理**: 提前预处理元信息，减少重复计算

## 应用场景

### 1. 超参数优化

```python
# 记录不同超参数组合的性能
for lr in [0.01, 0.05, 0.1]:
    for trees in [50, 100, 200]:
        # 训练模型
        model.train(lr=lr, trees=trees)
        performance = model.evaluate()

        # 创建元任务
        meta_task = MetaTask(
            task={"model": {"lr": lr, "trees": trees}},
            meta_info={"performance": performance},
            mode="full"
        )
        meta_tasks.append(meta_task)

# 元模型学习最优超参数
meta_model.fit(meta_tasks)
```

### 2. 模型选择

```python
# 记录不同模型的性能
for model_type in ["lgbm", "xgb", "catboost"]:
    model = create_model(model_type)
    model.fit(data)
    performance = model.evaluate()

    meta_task = MetaTask(
        task={"model_type": model_type},
        meta_info={"performance": performance},
        mode="full"
    )
    meta_tasks.append(meta_task)

# 元模型学习模型选择策略
meta_model.fit(meta_tasks)
```

### 3. 在线元学习

```python
# 持续更新元任务和元模型
meta_model = OnlineMetaModel()

while True:
    # 获取新任务
    new_task = get_new_task()
    performance = train_and_evaluate(new_task)

    # new创建元任务
    meta_task = MetaTask(
        task=new_task,
        meta_info={"performance": performance},
        mode="full"
    )

    # 增量更新元模型
    meta_model.update([meta_task])
```
