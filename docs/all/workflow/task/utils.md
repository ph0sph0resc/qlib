# workflow/task/utils.py 模块文档

## 文件概述

任务管理的一些工具函数，包括时间调整、MongoDB连接、记录器列表等。

## 函数

### get_mongodb() 函数

获取MongoDB中的数据库，这意味着需要在首说明MongoDB的地址和数据库名称。

**配置示例：**

```python
# 使用qlib.init():
mongo_conf = {
    "task_url": task_url,       # MongoDB URL
    "task_db_name": task_db_name, # 数据库名称
}
qlib.init(..., mongo=mongo_conf)

# qlib.init()之后：
C["mongo"] = {
    "task_url" : "mongodb://localhost:27017/",
    "task_db_name" : "rolling_db"
}
```

**返回：**
- Database - 数据库实例

**异常：**
- KeyError - 如果未配置C['mongo']

### list_recorders() 函数

列出一个实验中所有可以通过filter的记录器。

**参数：**
- `experiment` - 实验名称或Experiment实例
- `rec_filter_func` - 可调用函数，返回True以保留给定记录器，默认为None

**返回：**
- dict - 过滤后的字典{rid: recorder}

### TimeAdjuster 类

查找适当日期和调整日期的类。

#### 方法

##### __init__() 方法

初始化TimeAdjuster。

**参数：**
- `future` - 是否包含未来数据
- `end_time` - 结束时间，None表示使用日历的结束时间

##### set_end_time() 方法

设置结束时间。None表示使用日历的结束时间。

**参数：**
- `end_time` - 结束时间

##### get() 方法

通过索引获取日期时间。

**参数：**
- `idx` - 日历中的索引

**返回：**
- pd.Timestamp or None - 日期时间

##### max() 方法

返回最大日历日期时间。

**返回：**
- pd.Timestamp - 最大日期时间

##### align_idx() 方法

将time_point在日历中的索引对齐。

**参数：**
- `time_point` - 时间点
- `tp_type` - 时间点类型（"start"或"end"）

**返回：**
- int - 索引

##### cal_interval() 方法

计算交易日间隔（time_point_A - time_point_B）。

**参数：**
- `time_point_A` - 时间点A
- `time_point_B` - 时间点B（time_point_A的过去）

**返回：**
- int - A和B之间的交易日间隔

##### align_time() 方法

将time_point对齐到日历的交易日期。

**参数：**
- `time_point` - 时间点
- `tp_type` - 时间点类型（"start"或"end"）

**返回：**
- pd.Timestamp - 对齐后的交易日期

##### align_seg() 方法

将给定日期对齐到交易日。

**参数：**
- `segment` - 分段（dict或tuple）

**返回：**
- Union[dict, tuple] - 对齐后的开始和结束交易日（pd.Timestamp）

##### truncate() 方法

根据test_start_date截断分段。

**参数：**
- `segment` - 时间分段
- `test_start` - 测试开始时间
- `days` - 要截断的交易日数（基于test_start）

**返回：**
- tuple - 新分段

**说明：**
- data in this segment可能需要'days'数据
- 'days'是基于'test_start'的
- 例如，如果label包含2天的未来信息，预测期限1天
  - 预测目标为`Ref($close, -2)/Ref($close, -1) - 1`
  - 'days'应该是2 + 1 == 3天

##### shift() 方法

移动分段的日期时间。

**参数：**
- `seg` - 日期时间分段
- `step` - 滚动步长
- `rtype` - 滚动类型（"sliding"或"expanding"）

**返回：**
- tuple - 新分段

**异常：**
- KeyError - 如果分段索引（start和end）超出self.cal

##### 类常量

```python
SHIFT_SD = "sliding"   # 滑动（固定分段大小）
SHIFT_EX = "expanding"  # 扩展（固定开始日期，扩展结束日期）
```

### replace_task_handler_with_cache() 函数

用缓存handler替换任务中的handler。它将自动缓存文件并将其保存在cache_dir。

**参数：**
- `task` - 任务字典
- `cache_dir` - 缓存目录路径（默认为"."）

**返回：**
- dict - 新任务

**示例：**

```python
import qlib
qlib.auto_init()
import datetime

# 简化任务
task = {
    "dataset": {
        "kwargs": {
            'handler': {
                'class': 'Alpha158', 
                'module_path': 'qlib.contrib.data.handler', 
                'kwargs': {
                    'start_time': datetime.date(2008, 1, 1), 
                    'end_time': datetime.date(2020, 8, 1), 
                    'fit_start_time': datetime.date(2008, 1, 1), 
                    'fit_end_time': datetime.date(2014, 12, 31), 
                    'instruments': 'CSI300'
                }
            }
        }
    }
}

new_task = replace_task_handler_with_cache(task)
print(new_task)
# {'dataset': {'kwargs': {'handler': 'file...Alpha158.3584f5f8b4.pkl'}}
```

## 使用示例

### 时间调整

```python
from qlib.workflow.task.utils import TimeAdjuster

# 创建时间调整器
ta = TimeAdjuster(future=True, end_time='2021-12-31')

# 对齐时间
aligned_time = ta.align_time('2021-01-01', tp_type='start')
print(aligned_time)

# 计算间隔
interval = ta.cal_interval('2021-06-01', '2021-01-01')
print(interval)  # 交易天数

# 对齐分段
segment = {'train': ('2008-01-01', '2014-12-31'), 'test': ('2017-01-01', '2020-08-01')}
aligned_seg = ta.align_seg(segment)
print(aligned_seg)
```

### 列出记录器

```python
from qlib.workflow.task.utils import list_recorders
from qlib.workflow import R

# 列出特定实验的记录器
recorders = list_recorders('my_exp')

# 使用过滤器
online_recorders = list_recorders('my_exp', rec_filter_func=lambda rec: rec.status == 'FINISHED')
```

### 缓存handler

```python
from qlib.workflow.task.utils import replace_task_handler_with_cache

# 替换任务中的handler为缓存版本
cached_task = replace_task_handler_with_cache(
    task=task,
    cache_dir='./handler_cache'
)
```

## 注意事项

1. **MongoDB配置**：使用TaskManager前必须配置C['mongo']
2. **时间对齐**：TimeAdjuster处理交易日历对齐，处理None值（无界索引/边界）
3. **缓存机制**：replace_task_handler_with_cache使用文件路径格式"file://"
4. **日期处理**：所有日期时间使用pd.Timestamp，支持字符串或Timestamp对象
5. **分段格式**：支持dict或tuple格式的分段
6. **文件路径**：cache_dir使用Path对象，支持相对和绝对路径
