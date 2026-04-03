# workflow/utils.py 模块文档

## 文件概述

实验退出处理模块，处理程序异常退出时自动结束实验。

## 函数

### experiment_exit_handler() 函数

处理程序异常退出时的实验退出处理函数。

**行为：**
- 设置异常挂钩（sys.excepthook）来处理未捕获异常
- 注册atexit处理器，在程序正常结束时将实验状态设置为FINISHED

**限制：**
- 如果在程序中使用pdb，excepthook在结束时不会被触发，状态将为FINISHED

### experiment_exception_hook() 函数

未捕获异常的异常挂钩，自动将实验状态设置为FAILED。

**参数：**
- \`exc_type\` - 异常类型
- \`value\` - 异常值
- \`tb\` - 异常追踪

**行为：**
- 记录异常信息
- 打印异常追踪
- 调用R.end_exp将状态设置为FAILED

## 使用示例

### 自动退出处理

```python
from qlib.workflow.utils import experiment_exit_handler

# 注册退出处理器（通常在R.start之前调用）
experiment_exit_handler()

with R.start(experiment_name='my_exp'):
    # 如果发生异常，实验会自动标记为FAILED
    # 如果正常结束，实验会标记为FINISHED
    model.fit(dataset)
```

### 手动异常处理

```python
from qlib.workflow.utils import experiment_exception_hook

# 设置异常挂钩
sys.excepthook = experiment_exception_hook

# 运行代码，如果有未捕获异常会自动处理
```

## 注意事项

1. **atexit顺序**：atexit处理器应该在最后，因为只要程序结束就会被调用
2. **pdb限制**：使用pdb时，excepthook不会被触发
3. **状态优先级**：异常处理优先于atexit处理
4. **实验结束**：一旦R结束，再次调用R.end_exp不会生效
