# __init__.py

## 模块概述

该模块是 `qlib.contrib.tuner` 的入口模块。当前模块为空，仅包含 skip-file 和 flake8 跳过指令。

## 模块结构

```
qlib.contrib.tuner
├── __init__.py          # 当前文件（空）
├── launcher.py          # 启动器，运行tuner管道
├── tuner.py             # Tuner基类和QLibTuner实现
├── space.py             # 搜索空间定义
├── pipeline.py          # 管道管理类
└── config.py            # 配置管理类
```

## 使用说明

虽然 `__init__.py` 为空，但可以通过导入子模块使用调优功能：

```python
from qlib.contrib.tuner.launcher import run
from qlib.contrib.tuner.tuner import QLibTuner
from qlib.contrib.tuner.pipeline import Pipeline
from qlib.contrib.tuner.config import TunerConfigManager
```

## 注意事项

1. 该模块主要被内部使用
2. 外部使用者通常通过 `tuner` 命令行工具使用
3. 参见其他文件的详细文档了解具体功能

## 相关文档

- [launcher.py 文档](./launcher.md) - 启动器实现
- [tuner.py 文档](./tuner.md) - Tuner实现
- [space.py 文文件](./space.md) - 搜索空间定义
- [pipeline.py 文件](./pipeline.md) - 管道实现
- [config.py 文件](./config.md) - 配置管理
