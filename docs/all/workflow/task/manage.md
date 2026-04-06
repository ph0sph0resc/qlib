# workflow/task/manage/manage.md 模块文档

## 文件概述

TaskManager可以自动获取未使用的任务并管理一组任务的生命周期，包括错误处理。这些功能可以并发运行任务并确保每个任务只使用一次。Task Manager将所有任务存储在MongoDB中。

## 任务结构

TaskManager中的任务由三部分组成：

1. **任务描述**：定义任务
2. **任务状态**：任务状态
3. **任务结果**：用户可以获取包含任务描述和任务结果的任务

**任务格式：**

```python
{
    '_id': ObjectId,          # MongoDB的文档ID
    'def': Binary,             # pickle序列化的任务定义
    'filter': dict,             # JSON-like数据，用于过滤任务
    'status': str,              # 'waiting' | 'running' | 'done' | 'part_done'
    'res': Binary,              # pickle序列化的任务结果
    'priority': int,            # 任务优先级（可选）
}
```

## 类与函数

### TaskManager 类

任务管理器类，管理MongoDB中的任务。

#### 类常量

```python
STATUS_WAITING = "waiting"      # 等待训练
STATUS_RUNNING = "running"      # 训练中
STATUS_DONE = "done"           # 所有工作完成
STATUS_PART_DONE = "part_done"  # 完成一些步骤，等待下一步
```

#### 类属性

```python
ENCODE_FIELDS_PREFIX = ["def", "res"]  # 需要编码的字段前缀
```

#### 方法

##### __init__() 方法

初始化任务管理器，记得首先说明MongoDB url和数据库名称。TaskManager实例服务于特定的任务池。此模块的静态方法服务整个MongoDB。

**参数：**
- `task_pool` - MongoDB中Collection（任务池）的名称

##### list() 方法（静态）

列出db中所有collection（task_pool）。

**返回：**
- 列表 - 所有collection名称

##### _encode_task() 方法

编码任务。

**参数：**
- `task` - 任务信息

**返回：**
- dict - 编码后的任务

##### _decode_task() 方法

解码任务。MongoDB需要JSON，所以需要通过pickle将Python对象转换为JSON对象。

**参数：**
- `task` - 任务信息

**返回：**
- dict - JSON要求的任务

##### _dict_to_str() 方法

将字典转换为字符串字典。

##### _decode_query() 方法

解码查询。如果查询包含任何`_id`，则需要`ObjectId`来解码。

**参数：**
- `query` - 查询字典

**返回：**
- dict - 解码后的查询

##### replace_task() 方法

用新任务替换旧任务。

**参数：**
- `task` - 旧任务
- `new_task` - 新任务

##### insert_task() 方法

插入一个任务。

**参数：**
- `task` - 等待插入的任务

**返回：**
- pymongo.results.InsertOneResult

##### insert_task_def() 方法

插入任务到任务池。

**参数：**
- `task_def` - 任务定义

**返回：**
- pymongo.results.InsertOneResult

##### create_task() 方法

如果task_def_l中的任务是新任务，则将新任务插入到task_pool，并记录inserted_id。如果一个任务不是新任务，则只查询其_id。

**参数：**
- `task_def_l` - 任务列表
- `dry_run` - 是否插入新任务到任务池
- `print_nt` - 是否打印新任务

**返回：**
- List[str] - task_def_l的_id列表

##### fetch_task() 方法

使用查询获取任务。

**参数：**
- `query` - 查询字典，默认为{}
- `status` - 状态，默认为STATUS_WAITING

**返回：**
- dict - 解码后的任务

##### safe_fetch_task() 方法（上下文管理器）

使用查询和上下文管理器从task_pool获取任务。

**参数：**
- `query` - 查询字典
- `status` - 状态

**返回：**
- dict - 解码后的任务

##### task_fetcher_iter() 方法

任务获取器迭代器。

**参数：**
- `query` - 查询字典

##### query() 方法

在collection中查询任务。

**参数：**
- `query` - 查询字典
- `decode` - 是否解码

**返回：**
- dict - 解码后的任务

##### re_query() 方法

使用_id查询任务。

**参数：**
- `_id` - 文档ID

**返回：**
- dict - 解码后的任务

##### commit_task_res() 方法

提交结果到task['res']。

**参数：**
- `task` - 任务
- `res` - 要保存的结果
- `status` - 状态，默认为STATUS_DONE

##### return_task() 方法

将任务返回到状态。通常在错误处理中使用。

**参数：**
- `task` - 任务
- `status` - 状态，默认为STATUS_WAITING

##### remove() 方法

使用查询删除任务。

**参数：**
- `query` - 查询字典

##### task_stat() 方法

计算每个状态的任务数。

**参数：**
- `query` - 查询字典，默认为{}

**返回：**
- dict - 状态统计字典

##### reset_waiting() 方法

将所有running任务重置为waiting状态。可用于某些运行任务意外退出的情况。

**参数：**
- `query` - 查询字典，默认为{}

##### reset_status() 方法

重置查询的任务状态。

**参数：**
- `query` - 查询字典
- `status` - 状态

##### prioritize() 方法

为任务设置优先级。

**参数：**
- `task` - 任务
- `priority` - 目标优先级

##### wait() 方法

多进程处理时，主进程可能无法从TaskManager获取任何内容，因为还有一些running任务。因此主进程应该等待所有任务被其他进程或机器训练完成。

**参数：**
- `query` - 查询字典，默认为{}

### run_task() 函数

当任务池不为空（有WAITING任务）时，使用task_func在task_pool中获取和运行任务。

**参数：**
- `task_func` - 函数，def (task_def, **kwargs) -> <res which will be committed>
- `task_pool` - 任务池名称（MongoDB中的Collection）
- `query` - 查询字典
- `force_release` - 程序是否强制释放资源
- `before_status` - 要被获取和训练的任务状态
- `after_status` - 训练后的任务状态
- `**kwargs` - task_func的参数

**四种状态转换：**

| before_status | after_status | 说明 |
|------------|-------------|------|
| STATUS_WAITING | STATUS_DONE | 使用task["def"]作为task_func参数，任务尚未开始 |
| STATUS_WAITING | STATUS_PART_DONE | 使用task["def"]作为task_func参数 |
| STATUS_PART_DONE | STATUS_PART_DONE | 使用task["res"]作为task_func参数，任务已开始但未完成 |
| STATUS_PART_DONE | STATUS_DONE | 使用task["res"]作为task_func参数 |

**返回：**
- bool - 是否运行过任务

## CLI使用

可以通过命令行使用TaskManager：

```bash
# 列出所有任务池
python -m qlib.workflow.task.manage list

# 等待任务完成
python -m qlib.workflow.task.manage -t <pool_name> wait

# 查看任务状态
python -m qlib.workflow.task.manage -t <pool_name> task_stat

# 查询特定任务
python -m qlib.workflow.task.manage -t <your task pool> query '{"_id": "615498be837d0053acbc5d58"}'
```

## 使用示例

### 创建和运行任务

```python
from qlib.workflow.task.manage import TaskManager, run_task

# 创建任务管理器
tm = TaskManager(task_pool='my_pool')

# 创建任务
task_def = {
    'model': {'class': 'LGBModel', ...},
    'dataset': {'class': 'DatasetH', ...},
}
tm.create_task([task_def])

# 运行任务
def train_func(task_def, **kwargs):
    # 训练逻辑
    model = train_model(task_def)
    return model

run_task(train_func, 'my_pool')
```

### 并发任务运行

```python
import concurrent.futures

def train_worker(task_pool):
    run_task(train_func, task_pool, force_release=True)

# 启动多个worker
with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
    for i in range(4):
        executor.submit(train_worker, 'my_pool')
```

### 查询和管理任务

```python
# 查询任务状态
stats = tm.task_stat()
print(stats)  # {'waiting': 10, 'running': 2, 'done': 100}

# 重置卡住的任务
tm.reset_waiting()

# 删除特定任务
tm.remove({'status': 'done'})
```

## 注意事项

1. **MongoDB要求**：必须在使用TaskManager前配置MongoDB
2. **任务唯一性**：通过'filter'字段判断任务是否已存在
3. **并发安全**：find_one_and_update确保原子性更新
4. **优先级排序**：按priority降序排序，数字越大优先级越高
5. **异常处理**：使用safe_fetch_task时，异常会自动返回任务
6. **上下文管理**：safe_fetch_task使用with语句确保资源清理
7. **编码字段**：'def'和'res'字段需要pickle编码/解码
8. **序列化版本**：使用C.dump_protocol_version指定pickle协议版本
