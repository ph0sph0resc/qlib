# workflow/__init__.py 模块文档

## 文件概述

`qlib.workflow` 模块是Qlib机器学习工作流的核心模块，提供了实验管理、记录器、在线策略和任务管理的完整功能。该模块设计为比直接使用MLflow更直观和强大的接口。

**设计动机：**

- **更好的设计**：相比MLflow原生设计，该模块提供了记录对象和丰富的方法（更直观），而不是每次都使用run_id
- **更丰富的功能**：提供了针对量化投资定制的功能，例如：
  - 在运行开始时记录代码差异
  - log_object和load_object用于直接操作Python对象，而不是log_artifact和download_artifact
- **（弱）支持多样化后端**：虽然当前主要基于MLflow，但架构支持未来扩展其他后端

## 类与函数

### QlibRecorder 类

全局系统类，用于管理实验。

#### 属性

- `exp_manager: ExpManager` - 实验管理器实例

#### 方法

##### start() 方法

启动实验的上下文管理器，只能在`with`语句中使用。

```python
with R.start(experiment_name='test', recorder_name='recorder_1'):
    model.fit(dataset)
    R.log_params(...)
    ...
```

**参数：**
- `experiment_id: Optional[str]` - 要启动的实验ID
- `experiment_name: Optional[str]` - 要启动的实验名称
- `recorder_id: Optional[str]` - 要启动的记录器ID
- `recorder_name: Optional[str]` - 要启动的记录器名称
- `uri: Optional[str]` - 实验的跟踪URI，默认值在qlib.config中设置
- `resume: bool` - 是否恢复指定的记录器

**返回：**
- 激活的记录器（ActiveRun对象）

**异常处理：**
- 如果在with块中发生异常，会自动将实验状态设置为FAILED

##### start_exp() 方法

启动实验的底层方法。使用此方法时，需要手动结束实验。

**参数：**
- `experiment_id: Optional[str]` - 要启动的实验ID
- `experiment_name: Optional[str]` - 要启动的实验名称
- `recorder_id: Optional[str]` - 要启动的记录器ID
- `recorder_name: Optional[str]` - 要启动的记录器名称
- `uri: Optional[str]` - 实验的跟踪URI
- `resume: bool` - 是否恢复指定的记录器

**返回：**
- 被启动的实验实例

##### end_exp() 方法

手动结束实验。将结束当前活动实验及其活动记录器，并将状态设置为指定值。

**参数：**
- `recorder_status: str` - 记录器的状态（SCHEDULED、RUNNING、FINISHED、FAILED），默认为FINISHED

##### search_records() 方法

获取符合搜索条件的记录的pandas DataFrame。

**参数：**
- `experiment_ids: List[str]` - 实验ID列表
- `filter_string: str` - 过滤查询字符串，默认搜索所有运行
- `run_view_type: int` - 视图类型（ACTIVE_ONLY、DELETED_ONLY或ALL）
- `max_results: int` - 放入DataFrame的最大运行数
- `order_by: List[str]` - 排序的列列表（如"metrics.rmse"）

**返回：**
- pandas.DataFrame，其中每个metric、parameter和tag都扩展为各自的列（metrics.*、params.*、tags.*）

##### list_experiments() 方法

列出所有现有实验（已删除的除外）。

**返回：**
- 字典 {name -> experiment}，包含所有存储的实验信息

##### list_recorders() 方法

列出指定ID或名称实验的所有记录器。

**参数：**
- `experiment_id: Optional[str]` - 实验ID
- `experiment_name: Optional[str]` - 实验名称

**返回：**
- 字典 {id -> recorder}，包含所有存储的记录器信息

**行为：**
- 如果不提供实验ID或名称，尝试检索默认实验并列出其所有记录器
- 如果默认实验不存在，会先创建默认实验，然后在其下创建新记录器

##### get_exp() 方法

获取指定ID或名称的实验。当`create`参数为True时，如果没有找到有效实验，会自动创建新实验；否则只检索特定实验或抛出错误。

**参数：**
- `experiment_id: Optional[str]` - 实验ID
- `experiment_name: Optional[str]` - 实验名称
- `create: bool` - 如果实验尚未创建，是否自动创建新实验
- `start: bool` - 如果创建了新实验，是否启动它

**返回：**
- 指定ID或名称的实验实例

**行为逻辑：**
- 如果`create`为True：
  - 如果存在活动实验：
    - 未指定ID或名称，返回活动实验
    - 指定ID或名称，返回指定实验。未找到则创建新实验
  - 如果不存在活动实验：
    - 未指定ID或名称，创建默认实验
    - 指定ID或名称，返回指定实验，未找到则创建
- 如果`create`为False：
  - 如果存在活动实验：
    - 未指定ID或名称，返回活动实验
    - 指定ID或名称，返回指定实验，未找到则抛出错误
  - 如果不存在活动实验：
    - 未指定ID或名称，如果默认实验存在则返回，否则抛出错误
    - 指定ID或名称，返回指定实验，未找到则抛出错误

##### delete_exp() 方法

删除指定ID或名称的实验。至少提供ID或名称中的一个，否则会抛出错误。

**参数：**
- `experiment_id: Optional[str]` - 实验ID
- `experiment_name: Optional[str]` - 实验名称

##### get_uri() 方法

获取当前实验管理器的URI。

**返回：**
- 当前实验管理器的URI字符串

##### set_uri() 方法

重置当前实验管理器的**默认**URI。

**参数：**
- `uri: Optional[str]` - 要设置的URI

**注意：**
- 当URI是文件路径时，请使用绝对路径而不是如"~/mlruns/"这样的字符串
- 后端不支持这种字符串格式

##### uri_context() 方法

临时将exp_manager的default_uri设置为指定URI的上下文管理器。

**参数：**
- `uri: str` - 临时的URI

##### get_recorder() 方法

获取记录器。

**参数：**
- `recorder_id: Optional[str]` - 记录器ID
- `recorder_name: Optional[str]` - 记录器名称
- `experiment_id: Optional[str]` - 实验ID
- `experiment_name: Optional[str]` - 实验名称

**返回：**
- 记录器实例

**行为逻辑：**
- 如果存在活动记录器：
  - 未指定ID或名称，返回活动记录器
  - 指定ID或名称，返回指定记录器
- 如果不存在活动记录器：
  - 未指定ID或名称，抛出错误
  - 指定ID或名称，且必须提供对应的experiment_name，返回指定记录器，否则抛出错误

**注意：**
- 如果多个记录器满足查询条件（例如通过experiment_name查询），如果使用mlflow后端，将返回具有最新start_time的记录器

##### delete_recorder() 方法

删除指定ID或名称的记录器。至少提供ID或名称中的一个，否则会抛出错误。

**参数：**
- `recorder_id: Optional[str]` - 记录器ID
- `recorder_name: Optional[str]` - 记录器名称

##### save_objects() 方法

将对象保存为实验中的工件（artifacts）。支持从本地文件/目录保存，或直接保存对象。

**参数：**
- `local_path: Optional[str]` - 如果提供，则将文件或目录保存到artifact URI
- `artifact_path: Optional[str]` - 在URI中存储工件的相对路径
- `**kwargs: Dict[Text, Any]` - 要保存的对象，例如 {"pred.pkl": pred}

**行为：**
- 如果存在活动记录器：通过活动记录器保存对象
- 如果不存在活动记录器：系统会创建默认实验和新记录器，并在其下保存对象

**注意：**
- 如果想将对象保存到特定记录器，建议先通过get_recorder API获取特定记录器，然后使用该记录器保存对象

##### load_object() 方法

从实验中的工件加载对象。

**参数：**
- `name: str` - 要加载的对象名称

**返回：**
- 加载的对象

##### log_params() 方法

在实验期间记录参数。

**参数：**
- `**kwargs` - 键值对，name1=value1, name2=value2, ...

**行为：**
- 如果存在活动记录器：通过活动记录器记录参数
- 如果不存在活动记录器：系统会创建默认默认实验和新记录器，并在其下记录参数

##### log_metrics() 方法

在实验期间记录指标。

**参数：**
- `step: Optional[int]` - 步骤号
- `**kwargs` - 键值对，name1=value1, name2=value2, ...

**行为：**
- 如果存在活动记录器：通过活动记录器记录指标
- 如果不存在活动记录器：系统会创建默认实验和新记录器，并在其下记录指标

##### log_artifact() 方法

将本地文件或目录记录为当前活动的工件。

**参数：**
- `local_path: str` - 要写入的文件路径
- `artifact_path: Optional[str]` - 如果提供，在artifact_uri中写入的目录

**行为：**
- 如果存在活动记录器：通过活动记录器记录工件
- 如果不存在活动记录器：系统会创建默认实验和新记录器，并在其下记录工件

##### download_artifact() 方法

将工件文件或目录从运行下载到本地目录（如果适用），并返回其本地路径。

**参数：**
- `path: str` - 所需工件的相对源路径
- `dst_path: Optional[str]` - 要下载指定工件的本地文件系统目标目录的绝对路径。该目录必须已存在。如果未指定，工件将下载到本地文件系统上新的唯一命名目录。

**返回：**
- str - 所需工件的本地路径

##### set_tags() 方法

为记录器设置标签。

**参数：**
- `**kwargs` - 键值对，name1=value1, name2=value2, ...

**行为：**
- 如果存在活动记录器：通过活动记录器设置标签
- 如果不存在活动记录器：系统会创建默认实验和新记录器，并在其下设置标签

### RecorderWrapper 类

包装类，用于QlibRecorder，检测用户在已启动实验时是否重新初始化qlib。

#### 方法

##### register() 方法

注册提供商，检测是否已激活QlibRecorder。

**参数：**
- `provider` - 要注册的提供商

**异常：**
- 如果_provider已存在且exp_manager.active_experiment不为None，抛出RecorderInitializationError

### 全局变量 R

```python
R: QlibRecorderWrapper = RecorderWrapper()
```

全局记录器实例，用于管理所有实验和记录操作。

## 工作流程图

```
实验启动流程：
R.start() → exp_manager.start_exp() → 创建或获取实验
→ 创建或获取记录器 → 启动记录器 → 返回上下文管理器

实验结束流程：
with块结束 → R.end_exp() → exp_manager.end_exp() → 结束记录器 → 清空活动实验

记录流程：
R.log_params/log_metrics() → get_exp(start=True) → get_recorder(start=True)
→ recorder.log_params/log_metrics() → 保存到后端
```

## 与其他模块的关系

- **qlib.workflow.expm** - ExpManager类，管理所有实验
- **qlib.workflow.exp** - Experiment类，表示单个实验
- **qlib.workflow.recorder** - Recorder类，管理单个运行记录
- **qlib.workflow.record_temp** - RecordTemp类，生成特定格式的实验结果
- **qlib.workflow.online** - 在线策略管理模块
- **qlib.workflow.task** - 任务管理模块
- **mlflow** - 后端存储实现
- **qlib.config.C** - 配置管理

## 使用示例

### 基础用法

```python
from qlib import R
from qlib.workflow import R

# 启动实验并自动管理
with R.start(experiment_name='my_experiment', recorder_name='run_1'):
    # 记录参数
    R.log_params(learning_rate=0.01, batch_size=32)

    # 记录指标
    for epoch in range(10):
        loss = train_model()
        R.log_metrics(train_loss=loss, step=epoch)

    # 保存模型
    R.save_objects(trained_model=model)
```

### 检索实验

```python
# 列出所有实验
experiments = R.list_experiments()

# 列出特定实验的所有记录器
recorders = R.list_recorders(experiment_name='my_experiment')

# 检索记录
import pandas as pd
records = R.search_records(
    experiment_ids=['exp_id'],
    order_by=["metrics.m DESC"],
    max_results=10
)
```

### 加载之前的结果

```python
# 获取特定记录器
recorder = R.get_recorder(
    recorder_id='2e7a4efd66574fa49039e00ffaefa99d',
    experiment_name='my_experiment'
)

# 加载保存的对象
model = recorder.load_object("trained_model.pkl")
pred = recorder.load_object("pred.pkl")
```

## 注意事项

1. **上下文管理**：建议使用`with R.start()`上下文管理器，这样可以自动处理异常和资源清理
2. **线程安全**：当前实现不是线程安全的，多线程环境下需要额外同步机制
3. **MLflow限制**：
   - 参数值长度限制为1000（已从默认500扩展）
   - 工件列表最多返回50000条记录
4. **URI路径**：使用文件URI时，请使用绝对路径而非"~"这样的相对路径表示
5. **实验名称唯一性**：通过名称查询记录器时，如果有多个同名记录器，只返回最新的一个
