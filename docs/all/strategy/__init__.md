# strategy/__init__.py 模块文档

## 文件概述
此文件是策略模块的初始化文件，主要负责导出策略相关的核心类。目前该文件为空，仅作为模块包的标记文件。

## 模块导出
- `BaseStrategy`: 所有交易策略的基类
- `RLStrategy`: 基于强化学习的策略基类
- `RLIntStrategy`: 基于强化学习且带有解释器的策略类

## 相关模块
- `qlib.strategy.base`: 策略基类实现
- `qlib.backtest`: 回测引擎
- `qlib.rl`: 强化学习模块
