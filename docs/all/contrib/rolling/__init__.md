# qlib.contrib.rolling.__init__

## 模块概述

`qlib.contrib.rolling` 模块提供滚动训练和预测的功能。该模块专注于将特定任务离线转换为滚动训练模式，用于测试滚动模型的效果。

## 模块定位

### 与其他模块的区别

- **MetaController**：专注于学习如何处理任务（学习如何学习），而 Rolling 专注于如何将单个任务拆分为时间序列上的多个任务并运行
- **OnlineStrategy**：专注于服务模型的在线部署，模型可以随时间更新。Rolling 更简单，仅用于离线测试滚动模型，不共享 OnlineStrategy 的接口

### 核心功能

该模块专注于离线将特定任务转换为滚动训练模式，为简化实现，以下因素被忽略：
- 任务之间的依赖关系（例如时间序列依赖）

## 使用方式

### 命令行使用

```bash
# 基础滚动训练
python -m qlib.contrib.rolling.base --conf_path <配置文件路径> run

# 使用 DDG-DA 方法滚动训练
python -m qlib.contrib.rolling.ddgda --conf_path <配置文件路径> run

#子命令模式
python -m qlib.contrib.rolling base --conf_path <配置文件路径> run
python -m qlib.contrib.rolling ddgda --conf_path <配置文件路径> run
```

### Python 代码使用

```python
from qlib.contrib.rolling.base import Rolling

# 创建滚动训练实例
rolling = Rolling(
    conf_path="workflow_config.yaml",
    exp_name="rolling_experiment",
    horizon=20,
    step=20
)

# 运行滚动训练
rolling.run()
```

## 重要说明

在运行示例前，请清理之前的结果：

```bash
rm -r mlruns
```

因为 MLflow 不支持永久删除实验（会被移动到 .trash），同名实验创建时会报错。

## 子模块

| 子模块 | 说明 |
|--------|------|
| `base` | 基础滚动训练实现 |
| `ddgda` | 基于 DDG-DA 的滚动训练 |

## 配置示例

典型的配置文件（YAML 格式）包含以下部分：

```yaml
qlib_init:
    provider_uri: ~/.qlib/qlib_data/cn_data
    region: cn

task:
    model:
        class: LGBModel
        module_path: qlib.contrib.model.gbdt
    dataset:
        class: DatasetH
        module_path: qlib.data.dataset
        kwargs:
            handler:
                class: Alpha158
                module_path: qlib.contrib.data.handler
                kwargs:
                    start_time: "2010-01-01"
                    end_time: "2020-12-31"
            segments:
                train: ["2010-01-01", "2015-12-31"]
                test: ["2016-01-01", "2020-12-31"]
    record:
        - class: SignalRecord
          module_path: qlib.workflow.record_temp
```

## 输出结构

滚动训练会生成以下输出：

1. **滚动模型实验**：包含多个滚动周期的训练结果
2. **合并结果实验**：包含合并后的预测和评估结果

```
mlruns/
├── rolling_models_YYYYMMDDHHMMSS/  # 各滚动周期的模型
└── rolling/                         # 合并后的预测和评估
    └── <recorder_id>/
        ├── pred.pkl                  # 合并的预测
        ├── label.pkl                 # 合并的标签
        └── ...                       # 评估指标
```

## 注意事项

1. **数据泄露**：确保滚动步长（step）和预测时域（horizon）正确设置，避免数据泄露
2. **实验清理**：每次运行前清理 `mlruns` 目录
3. **配置文件**：配置文件中的 `qlib_init` 部分会被忽略，需要在代码中单独初始化 Qlib
