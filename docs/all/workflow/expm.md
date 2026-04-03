# workflow/expm.py 模块文档

## 文件概述

本模块定义了`ExpManager`和`MLflowExpManager`类，用于管理多个实验。ExpManager是一个单例，可以获取不同实验并与它们进行比较。

**设计动机：**

ExpManager和全局Config（即`C`）都是单例。它们共享同一个变量，称为"**默认uri**"。

当用户启动一个实验时，用户可能想将URI设置为一个特定URI（在此期间覆盖**默认uri**），然后取消设置**特定uri**并回退到**默认uri**。`ExpManager._active_exp_uri`就是那个**特定uri**。

## 类与函数

### ExpManager 类

管理实验的ExpManager类。API设计与MLflow类似。

#### 属性

- `default_uri: str` - 默认跟踪URI（来自qlib.config.C）
- `_active_exp_uri: Optional[str]` - 当前活动的实验URI（覆盖默认uri）
- `_default_exp_name: Optional[str]` - 默认实验名称
- `active_experiment: Optional[Experiment]` - 当前活动的实验（每次只能有一个）

#### 方法

##### __init__() 方法

初始化ExpManager。

**参数：**
- \`uri: Text\` - 跟踪URI
- \`default_exp_name: Optional[Text]\` - 默认实验名称

##### start_exp() 方法

启动一个实验。此方法包括首先获取或创建一个实验，然后将其设置为活动状态。

**参数：**
- \`experiment_id: Optional[Text]\` - 活动实验的ID
- \`experiment_name: Optional[Text]\` - 活动实验的名称
- \`recorder_id: Optional[Text]\` - 要启动的记录器ID
- \`recorder_name: Optional[Text]\` - 要启动的记录器名称
- \`uri: Optional[Text]\` - 当前跟踪URI
- \`resume: bool\` - 是否恢复实验和记录器
- \`**kwargs\` - 其他参数

**返回：**
- 一个活动的实验

**行为：**
- 设置\`_active_exp_uri\`
- 调用子类的\`_start_exp\`方法

##### _start_exp() 方法

启动实验的内部方法，由子类实现。

##### end_exp() 方法

结束一个活动的实验。

**参数：**
- \`recorder_status: Text\` - 实验的活动记录器的状态
- \`**kwargs\` - 其他参数

**行为：**
- 将\`_active_exp_uri\`设置为None
- 调用子类的\`_end_exp\`方法

##### _end_exp() 方法

结束实验的内部方法，由子类实现。

##### create_exp() 方法

创建一个实验。

**参数：**
- \`experiment_name: Optional[Text]\` - 实验名称，必须是唯一的

**返回：**
- 一个实验对象

**异常：**
- ExpAlreadyExistError - 如果实验已存在

##### search_records() 方法

获取符合搜索条件的记录的pandas DataFrame。

**参数：**
- \`experiment_ids: Optional[List[str]]\` - 实验ID列表
- \`**kwargs\` - 其他搜索条件

**返回：**
- pandas.DataFrame，其中每个metric、parameter和tag都扩展为各自的列（metrics.*、params.*、tags.*）

##### get_exp() 方法

检索一个实验。包括获取一个活动实验，以及获取或创建一个特定的实验。

**参数：**
- \`experiment_id: Optional[Text]\` - 要返回的实验ID
- \`experiment_name: Optional[Text]\` - 要返回的实验名称
- \`create: bool\` - 如果实验之前未创建过，是否自动创建新实验
- \`start: bool\` - 如果创建了新实验，是否启动它

**返回：**
- 一个实验对象

**行为逻辑：**

**如果\`create\`为True：**
- 如果存在活动实验：
  - 未指定ID或名称，返回活动实验
  - 指定ID或名称，返回指定实验。未找到则创建具有给定ID或名称的新实验。如果\`start\`设置为True，则将实验设置为活动状态
- 如果不存在活动实验：
  - 未指定ID或名称，创建默认实验
  - 指定ID或名称，返回指定实验。未找到则创建新实验。如果\`start\`设置为True，则将实验设置为活动状态

**如果\`create\`为False：**
- 如果存在活动实验：
  - 未指定ID或名称，返回活动实验
  - 指定ID或名称，返回指定实验。未找到则抛出错误
- 如果不存在活动实验：
  - 未指定ID或名称，如果默认实验存在则返回，否则抛出错误
  - 指定ID或名称，返回指定实验。未找到则抛出错误

##### _get_or_create_exp() 方法

获取或创建一个实验。尝试首先获取有效实验，如果发生异常，则根据给定的ID和名称自动创建新实验。

**参数：**
- \`experiment_id: Optional[Text]\` - 实验ID
- \`experiment_name: Optional[Text]\` - 实验名称

**返回：**
- 元组 (object, bool) - 实验和是否为新建的标志

**行为：**
- 对于file协议，使用FileLock避免并发创建实验冲突
- 对于其他协议（如http），使用双重检查避免创建实验冲突

##### _get_exp() 方法

通过名称或ID获取特定实验。如果不存在，则抛出ValueError。

**参数：**
- \`experiment_id: Optional[Text]\` - 实验ID
- \`experiment_name: Optional[Text]\` - 实验名称

**返回：**
- Experiment - 搜索到的实验

**异常：**
- ValueError - 如果找不到实验

##### delete_exp() 方法

删除一个实验。

**参数：**
- \`experiment_id: Optional[Text]\` - 实验ID
- \`experiment_name: Optional[Text]\` - 实验名称

##### default_uri 属性

从qlib.config.C获取默认跟踪URI。

##### default_uri 属性 (setter)

设置默认跟踪URI到qlib.config.C。

##### uri 属性

获取默认跟踪URI或当前URI。

**返回：**
- 跟踪URI字符串

##### list_experiments() 方法

列出所有现有实验。

**返回：**
- 字典 {name -> experiment}，包含所有存储的实验信息

### MLflowExpManager 类

使用MLflow实现ExpManager的类。

#### 继承关系

\`\`\`
MLflowExpManager(ExpManager)
\`\`\`

#### 属性

- \`client\` - MLflow客户端实例

#### 方法

##### client 属性

获取MLflow客户端实例。

**注意：**
- 每次都创建新客户端，测试表明创建客户端速度很快

##### _start_exp() 方法

启动MLflow实验。

**参数：**
- \`experiment_id: Optional[Text]\` - 实验ID
- \`experiment_name: Optional[Text]\` - 实验名称
- \`recorder_id: Optional[Text]\` - 记录器ID
- \`recorder_name: Optional[Text]\` - 记录器名称
- \`resume: bool\` - 是否恢复记录器

**返回：**
- 活动的实验

**行为：**
- 创建或获取实验
- 设置活动实验
- 启动实验

##### _end_exp() 方法

结束MLflow实验。

**参数：**
- \`recorder_status: Text\` - 记录器状态

**行为：**
- 如果存在活动实验，结束它并清空活动实验引用

##### create_exp() 方法

创建一个MLflow实验。

**参数：**
- \`experiment_name: Optional[Text]\` - 实验名称

**返回：**
- MLflowExperiment实例

**异常：**
- ExpAlreadyExistError - 如果实验已存在

##### _get_exp() 方法

获取一个MLflow实验。

**参数：**
- \`experiment_id: Optional[Text]\`` - 实验ID
- \`experiment_name: Optional[Text]\` - 实验名称

**返回：**
- MLflowExperiment实例

**行为：**
- 如果提供ID，通过ID获取实验
- 如果提供名称，通过名称获取实验
- 检查实验的生命周期阶段是否为"DELETED"，如果是则抛出错误

**异常：**
- ValueError - 如果找不到实验

##### search_records() 方法

搜索记录。

**参数：**
- \`experiment_ids: Optional[List[str]]\` - 实验ID列表
- \`**kwargs\` - 搜索条件
  - \`filter_string\`: str - 过滤字符串
  - \`run_view_type\`: int - 运行视图类型
  - \`max_results\`: int - 最大结果数
  - \`order_by\`: List[str] - 排序字段

**返回：**
- MLflow的search_runs结果

##### delete_exp() 方法

删除一个实验。

**参数：**
- \`experiment_id: Optional[Text]\` - 实验ID
- \`experiment_name: Optional[Text]\` - 实验名称

**异常：**
- ValueError - 如果删除失败

##### list_experiments() 方法

列出所有实验。

**返回：**
- 字典 {name -> experiment}，包含所有存储的实验信息

**行为：**
- 根据MLflow版本使用不同的API（v2+使用search_experiments，v1使用list_experiments）

## 实验管理器流程图

\`\`\`mermaid
graph TD
    A[创建ExpManager] --> B[设置default_uri]
    B --> C{启动实验?}
    C -->|是| D[start_exp]
    C -->|否| E[get_exp或create_exp]
    D --> F[_start_exp]
    E --> G{create=True?}
    G -->|是| H[create_exp]
    G -->|否| I[_get_exp]
    F --> J[设置active_exp]
    H --> J
    I --> J
    J --> K[创建/获取记录器]
    K --> L[设置active_recorder]
    L --> M[记录数据]
    M --> N{结束实验?}
    N -->|是| O[end_exp]
    N -->|否| M
    O --> P[_end_exp]
    P --> Q[清空active_exp]
\`\`\`

## 与其他模块的关系

- **qlib.workflow.exp** - Experiment类，ExpManager管理多个Experiment
- **qlib.workflow.recorder** - Recorder类
- **mlflow** - 后端存储实现
- **qlib.config.C** - 配置管理，共享default_uri
- **filelock** - 用于避免并发创建实验冲突

## 使用示例

### 创建实验管理器

\`\`\`python
from qlib.workflow.expm import MLflowExpManager

# 创建实验管理器
expm = MLflowExpManager(
    uri='file:///mlruns',
    default_exp_name='my_default_exp'
)

# 列出所有实验
experiments = expm.list_experiments()
print(experiments)
\`\`\`

### 启动和结束实验

\`\`\`python
# 启动实验
exp = expm.start_exp(
    experiment_name='my_exp',
    recorder_name='run_1'
)

# 获取当前活动的实验
active_exp = expm.get_exp()
print(active_exp.name)

# 结束实验
expm.end_exp(recorder_status='FINISHED')
\`\`\`

### 获取或创建实验

\`\`\`python
# 获取或创建实验（如果不存在会创建）
exp = expm.get_exp(
    experiment_name='my_exp',
    create=True,
    start=True
)

# 只获取实验（不存在会抛出错误）
try:
    exp = expm.get_exp(
        experiment_name='non_existing_exp',
        create=False
    )
except ValueError:
    print("实验不存在")
\`\`\`

### 搜索记录

\`\`\`python
import pandas as pd

# 搜索特定实验的记录
records = expm.search_records(
    experiment_ids=['exp_id'],
    filter_string='metrics."my_param"="a" and tags."my_tag"="b"',
    max_results=100,
    order_by=["metrics.rmse DESC"]
)

print(records.head())
\`\`\`

## 注意事项

1. **单例模式**：ExpManager设计为单例，全局配置共享default_uri
2. **并发安全**：对于file协议，使用FileLock避免并发创建实验冲突；对于其他协议使用双重检查
3. **URI优先级**：_active_exp_uri优先于default_uri
4. **实验生命周期**：删除的实验（lifecycle_stage=DELETED）不会被列出
5. **MLflow版本兼容性**：根据MLflow版本自动选择API（search_experiments或list_experiments）
