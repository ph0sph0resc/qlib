# __init__.py

## 模块概述

该模块是 `qlib.contrib.workflow` 的入口模块，导出了实验记录相关的类。

## 导入的类

- **MultiSegRecord**: 多段信号记录类，用于生成多段的信号预测和评估
- **SignalMseRecord**: 信号MSE记录类，用于计算预测的均方误差

## 模块结构

```
qlib.contrib.workflow
├── __init__.py          # 当前文件，导出主要类
└── record_temp.py        # MultiSegRecord 和 SignalMseRecord 的实现
```

## 使用示例

### MultiSegRecord

```python
from qlib.contrib.workflow import MultiSegRecord
from qlib.model import LightGBM
from qlib.data import Dataset

# 创建模型和数据集
model = LightGBM(...)
dataset = Dataset(...)

# 创建多段记录器
multi_recorder = MultiSegRecord(
    model=model,
    dataset=dataset,
    recorder=recorder
)

# 生成多段预测和评估
segments = {
    "train": ("2018-01-01", "2020-12-31"),
    "valid": ("2021-01-01", "2021-06-30"),
    "test": ("2021-07-01", "2021-12-31")
}

multi_recorder.generate(segments, save=True)
```

### SignalMseRecord

```python
from qlib.contrib.workflow import SignalMseRecord

# 创建MSE记录器
mse_recorder = SignalMseRecord(
    recorder=recorder
)

# 生成MSE指标
mse_recorder.generate()

# 列出生成的文件
files = mse_recorder.list()
print(f"Generated files: {files}")
```

## 类功能对比

| 记录器 | 主要功能 | 输入 | 输出 |
|--------|----------|------|------|
| MultiSegRecord | 多段预测和IC评估 | 模型、数据集 | IC指标、Rank IC |
| SignalMseRecord | MSE和RMSE计算 | 预测和标签 | MSE、RMSE |

## 注意事项

1. **MultiSegRecord**:
   - 需要完整的模型和数据集
   - 支持多个分段同时评估
   - 自动计算IC和Rank IC指标

2. **SignalMseRecord**:
   - 依赖于SignalRecord生成的预测和标签
   - 自动过滤NaN值
   - 同时计算MSE和RMSE

3. **通用注意事项**:
   - 确保recorder正确配置
   - 检查数据集格式
   - 验证模型训练状态

## 相关文档

- [record_temp.py 文档](./record_temp.md) - 记录器详细实现
