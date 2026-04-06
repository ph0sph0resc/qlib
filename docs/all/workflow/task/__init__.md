# workflow/task/__init__.py 模块文档

## 文件概述

task模块实现了任务相关的工作工作流。

## 典型任务工作工作流

| 步骤 | 描述 |
|------|------|
| TaskGen | 生成任务 |
| TaskManager(可选） | 管理生成的任务 |
| 运行任务 | 从TaskManager获取任务并运行任务 |

## 子模块

- **gen.py** - TaskGen，生成不同任务
- **collect.py** - Collector，收集和处理结果
- **manage.py** - TaskManager，管理任务生命周期
- **utils.py** - 工具函数（TimeAdjuster、list_recorders等）

## 功能概述

### 任务生成（gen.py）

- **TaskGen** - 任务生成器基类
- **RollingGen** - 滚动窗口任务生成器
- **MultiHorizonGenBase** - 多期限任务生成器基类

### 结果收集（collect.py）

- **Collector** - 收集器基类
- **MergeCollector** - 合并多个收集器的结果
- **RecorderCollector** - 从Recorder收集结果

### 任务管理（manage.py）

- **TaskManager** - 基于MongoDB的任务管理器
- **run_task** - 运行任务的主函数

### 工具（utils.py）

- **TimeAdjuster** - 时间调整器，对齐日历
- **list_recorders** - 列出记录器
- **get_mongodb** - 获取MongoDB实例
- **replace_task_handler_with_cache** - 替换任务中的handler为缓存

## 使用示例

### 生成任务

```python
from qlib.workflow.task.gen import RollingGen, task_generator

# 创建rolling生成器
rg = RollingGen(step=40, rtype=RollingGen.ROLL_EX)

# 生成任务
tasks = task_generator(
    tasks=task_template,
    generators=rg
)
```

### 收集结果

```python
from qlib.workflow.task.collect import RecorderCollector

# 创建收集器
collector = RecorderCollector(
    experiment='my_exp',
    process_list=[RollingGroup()],
    artifacts_path={'pred': 'pred.pkl'}
)

# 收集结果
results = collector()
```

### 管理任务

```python
from qlib.workflow.task.manage import TaskManager, run_task

# 创建任务管理器
tm = TaskManager(task_pool='my_pool')

# 插入任务
tm.insert_task_def(task_def)

# 运行任务
run_task(task_func=train_func, task_pool='my_pool')
```

## 注意事项

1. **任务模板**：任务模板定义数据集、模型和记录器配置
2. **MongoDB依赖**：TaskManager需要配置MongoDB
3. **时间对齐**：使用TimeAdjuster处理日历对齐和时间段调整
4. **并发安全**：TaskManager支持并发任务执行，每个任务只使用一次
5. **任务状态**：任务有四种状态（waiting、running、part_done、done）
