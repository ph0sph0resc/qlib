# workflow/task/gen.py 模块文档

## 文件概述

任务生成器模块可以基于TaskGen和任务模板生成许多任务。

## 类与函数

### task_generator() 函数

使用TaskGen列表和任务模板列表生成不同的任务。

**参数：**
- `tasks` - 任务模板列表或单个任务
- `generators` - TaskGen列表或单个TaskGen

**返回：**
- 任务列表

**示例：**
- 有3个任务模板a,b,c和2个TaskGen A,B。A从a模板生成2个任务，B从a模板生成3个任务
- task_generator([a, b, c], [A, B])最终生成3*2*3=18个任务

### TaskGen 类

生成不同任务的基类。

#### 方法

##### __call__() 方法

generate方法的语法糖。

### RollingGen 类

滚动窗口任务生成器。实现TaskGen类。

#### 类常量

```python
ROLL_EX = "expanding"  # 固定开始日期，扩展结束日期
ROLL_SD = "sliding"     # 固定分段大小，从开始日期滑动
```

#### 属性

- `step` - 滚动步长
- `rtype` - 滚动类型（扩展或滑动）
- `test_key` - 测试分段键（默认为"test"）
- `train_key` - 训练分段键（默认为"train"）
- `trunc_days` - 截断的天数以避免未来信息泄漏
- `task_copy_func` - 复制整个任务的函数
- `ta` - TimeAdjuster实例

#### 方法

##### __init__() 方法

初始化RollingGen。

**参数：**
- `step` - 滚动步长（默认40）
- `rtype` - 滚动类型（默认ROLL_EX）
- `ds_extra_mod_func` - 额外修改函数（如handler_mod）
- `test_key` - 测试分段键
- `train_key` - 训练分段键
- `trunc_days` - 截断天数
- `task_copy_func` - 任务复制函数（默认copy.deepcopy）

##### gen_following_tasks() 方法

为任务生成后续的滚动任务，直到test_end。

**参数：**
- `task` - Qlib任务格式
- `test_end` - 最新滚动任务包含test_end

**返回：**
- Generator[List[dict]] - 后续任务生成器

##### generate() 方法

将任务转换为滚动任务。

**参数：**
- `task` - 描述任务的字典

**返回：**
- List[dict] - 任务列表

**流程：**
1. 复制任务
2. 计算分段
3. 首次滚动：
   - 对齐分段
   - 初始化测试分段
   - 如果需要，截断分段
   - 更新任务分段
4. 生成后续滚动任务

### MultiHorizonGenBase 类

多期限任务生成器基类。实现TaskGen类。

#### 属性

- `horizon` - 可能的期限
- `label_leak_n` - 获取完整标签的未来天数
- `ta` - TimeAdjuster实例
- `test_key` - 测试分段键

#### 方法

##### __init__() 方法

初始化MultiHorizonGenBase。

**参数：**
- `horizon` - 可能的任务期限
- `label_leak_n` - 未来天数

**说明：**
- 用户在T天做出预测，标签是T+1天买入、T+2天卖出的收益
- label_leak_n为2（即2天的信息泄漏用于利用此样本）

##### set_horizon() 方法

更改任务期限（子类必须实现）。

**参数：**
- `task` - Qlib任务
- `hr` - 任务期限

##### generate() 方法

基于现有任务为不同期限生成任务。

**参数：**
- `task` - 任务模板

**返回：**
- List[dict] - 任务列表

**流程：**
1. 遍历horizon列表
2. 为每个期限创建任务副本
3. 设置期限
4. 对齐分段
5. 截断分段
6. 添加任务到结果列表

## 辅助函数

### handler_mod() 函数

使用RollingGen时帮助修改handler结束时间。

**处理情况：**
- Handler的数据end_time早于数据集test_data的分段
  - 将handler的数据end_time扩展

### trunc_segments() 函数

为了避免未来信息泄漏，应该根据test_start_time截断分段。

**参数：**
- `ta` - TimeAdjuster
- `segments` - 分段字典
- `days` - 天数
- `test_key` - 测试分段键

**注意：**
- 此函数会原地修改segments

## 滚动任务生成流程

```
原始任务
    ↓
对齐分段
    ↓
截断分段
    ↓
首滚动任务
    ↓
更新任务分段
    ↓
更多任务?
   ├──是 → 滑动分段
   │        ↓
   │    ────→
   └──否 → 返回
```

## 使用示例

### 滚动窗口任务

```python
from qlib.workflow.task.gen import RollingGen, task_generator

# 创建滚动生成器
rg = RollingGen(step=40, rtype=RollingGen.ROLL_EX)

# 生成任务
tasks = task_generator(
    tasks=task_template,
    generators=rg
)
```

### 多期限任务

```python
from qlib.workflow.task.gen import MultiHorizonGenBase

# 创建多期限生成器（子类需实现set_horizon）
hg = MultiHorizonGenBase(horizon=[5, 10, 20], label_leak_n=2)

# 生成任务
tasks = hg.generate(task_template)
```

### 处理器修改

```python
from qlib.workflow.task.gen import handler_mod

# 修改handler结束时间以避免未来信息泄漏
handler_mod(task, rolling_gen)
```

## 注意事项

1. **分段对齐**：使用TimeAdjuster对齐到交易日期
2. **未来信息泄漏**：trunc_days参数用于避免未来信息泄漏
3. **任务复制**：使用task_copy_func共享任务间的对象
4. **滚动类型**：ROLL_EX（扩展）和ROLL_SD（滑动）两种模式
5. **Handler修改**：ds_extra_mod_func用于扩展handler的end_time
