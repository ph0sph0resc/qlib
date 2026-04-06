# config.py

## 模块概述

该模块实现了调优配置管理，负责加载、解析和组织调优配置。

## 类定义

### TunerConfigManager

调优配置管理器，统一管理所有配置项。

#### 构造方法参数

| 参数名 | 类型 | 必需 | 说明 |
|--------|------|------|------|
| config_path | str | 是 | YAML配置文件路径 |

**支持的配置格式：**

- YAML 文件
- 包含所有必要配置的字典

#### 属性

- **config_path** (str): 配置文件路径
- **config** (dict): 原始配置字典
- **pipeline_ex_config** (PipelineExperimentConfig): 实验配置
- **pipeline_config** (list): tuner配置列表
- **optim_config** (OptimizationConfig): 优化标准
- **time_config** (dict): 时间段配置
- **data_config** (dict): 数据配置
- **backtest_config** (dict): 回测配置
- **qlib_client_config** (dict): Qlib客户端配置

---

## 配置结构

### 完整配置示例

```yaml
# 实验配置
experiment:
  name: my_tuner_experiment
  dir: ./experiments
  tuner_ex_dir: ./tuner_results
  estimator_ex_dir: ./estimator_results
  tuner_module_path: qlib.contrib.tuner.tuner
  tuner_class: QLibTuner

# 优化标准
optimization_criteria:
  report_type: pred_long
  report_factor: information_ratio
  optim_type: max

# 时间段
time_period:
  train: (2018-01-01, 2020-12-31)
  valid: (2021-01-01, 2021-06-30)
  test: (2021-07-01, 2021-12-31)

# 数据配置
data:
  class: DataHandlerLP
  module_path: qlib.data.dataset.handler
  kwargs:
    instruments: all
    start_time: 2018-01-01
    end_time: 2021-12-31
    fit_start_time: 2018-01-01
    fit_end_time: 2020-12-31

# 回测配置
backtest:
  exchange:
    class: Exchange
    module_path: qlib.backtest.exchange
    kwargs:
      limit_threshold: 0.095
      deal_price: close
      open_cost: 0.0005
      close_cost: 0.0015
      min_cost: 5.0
  start_time: 2021-07-01
  end_time: 2021-12-31

# Tuner管道
tuner_pipeline:
  # 第一个tuner
  - model:
      class: LGBModel
      module_path: qlib.contrib.model.lgboost
      kwargs:
        loss: mse
        colsample_bytree: 0.8
        min_child_weight: 0.1
      space: LGModelSpace
    strategy:
      class: TopkDropoutStrategy
      module_path: qlib.contrib.strategy
      kwargs:
        topk: 30
        n_drop: 5
        hold_thresh: 1
      space: TopkAmountStrategySpace
    trainer:
      kwargs:
        early_stopping_rounds: 20
        verbose: False
    max_evals: 50
```

---

### PipelineExperimentConfig

实验配置类，管理实验相关的配置。

#### 构造方法参数

| 参数名 | 类型 | 必需 | 说明 |
|--------|------|------|------|
| config | dict | 是 | 实验配置字典 |
| TUNER_CONFIG_MANAGER | TunerConfigManager | 是 | 配置管理器实例 |

#### 属性

- **name** (str): 实验名称
- **global_dir** (str): 全局目录（配置文件所在目录）
- **tuner_ex_dir** (str): tuner结果目录
- **estimator_ex_dir** (str): estimator结果目录
- **tuner_module_path** (str): tuner模块路径
- **tuner_class** (str): tuner类名

**默认值：**

```python
name = "tuner_experiment"
global_dir = 配置文件所在目录
tuner_ex_dir = global_dir / name
estimator_ex_dir = tuner_ex_dir / "estimator_experiment"
tuner_module_path = "qlib.contrib.tuner.tuner"
tuner_class = "QLibTuner"
```

**目录创建：**

- 自动创建 `tuner_ex_dir`
- 自动创建 `estimator_ex_dir`

**配置备份：**

- 保存原始配置到 `tuner_ex_dir/tuner_config.yaml`

---

### OptimizationConfig

优化标准配置类，定义优化目标。

#### 构造方法参数

| 参数名 | 类型 | 必需 | 说明 |
|--------|------|------|------|
| config | dict | 是 | 优化标准配置字典 |
| TUNER_CONFIG_MANAGER | TunerConfigManager | 是 | 配置管理器实例 |

#### 属性

- **report_type** (str): 报告类型
- **report_factor** (str): 报告因子
- **optim_type** (str): 优化类型

**report_type 可选值：**

- `"pred_long"`: 做多预测结果
- `"pred_long_short"`: 多空预测结果
- `"pred_short"`: 做空预测结果
- `"excess_return_without_cost"`: 不含成本超额收益
- `"excess_return_with_cost"`: 含成本超额收益
- `"model"`: 模型性能

**report_factor 可选值：**

- `"annualized_return"`: 年化收益
- `"information_ratio"`: 信息比率
- `"max_drawdown"`: 最大回撤
- `"mean"`: 均值
- `"std"`: 标准差
- `"model_score"`: 模型得分
- `"model_pearsonr"`: 模型皮尔逊相关系数

**optim_type 可选值：**

- `"min"`: 最小化指标
- `"max"`: 最大化指标
- `"correlation"`"`: 最大化相关（距离1）

**默认值：**

```python
report_type = "pred_long"
report_factor = "information_ratio"
optim_type = "max"
```

## 使用示例

### 基本使用

```python
from qlib.contrib.tuner.config import TunerConfigManager

# 加载配置
config_manager = TunerConfigManager("/path/to/config.yaml")

# 访问配置
print(f"Experiment name: {config_manager.pipeline_ex_config.name}")
print(f"Tuner count: {len(config_manager.pipeline_config)}")
print(f"Optimization type: {config_manager.optim_config.optim_type}")
```

### 访问子配置

```python
# 实验配置
exp_config = config_manager.pipeline_ex_config
print(f"Name: {exp_config.name}")
print(f"Tuner dir: {exp_config.tuner_ex_dir}")
print(f"Estimator dir: {exp_config.estimator_ex_dir}")

# 优化配置
optim_config = config_manager.optim_config
print(f"Report type: {optim_config.report_type}")
print(f"Report factor: {optim_config.report_factor}")
print(f"Optimization type: {optim_config.optim_type}")

# 其他配置
time_config = config_manager.time_config
data_config = config_manager.data_config
backtest_config = config_manager.backtest_config
tuner_configs = config_manager.pipeline_config
```

### 验证配置

```python
from qlib.contrib.tuner.config import TunerConfigManager

# 加载配置
config_manager = TunerConfigManager("/path/to/config.yaml")

# 验证优化配置
optim_config = config_manager.optim_config
assert optim_config.report_type in [
    "pred_long", "pred_long_short", "pred_short",
    "excess_return_without_cost", "excess_return_with_cost",
    "model"
], f"Invalid report_type: {optim_config.report_type}"

assert optim_config.report_factor in [
    "annualized_return", "information_ratio", "max_drawdown",
    "mean", "std", "model_pearsonr", "model_score"
], f"Invalid report_factor: {optim_config.report_factor}"

assert optim_config.optim_type in [
    "min", "max", "correlation"
], f"Invalid optim_type: {optim_config.optim_type}"
```

## 注意事项

1. **配置文件**:
   - 使用 YAML 格式
   - 确保缩进正确
   - 检查参数名称和类型

2. **路径处理**:
   - 支持相对路径和绝对路径
   - 自动创建必要的目录
   - 保存配置备份

3. **参数验证**:
   - 检查必需参数是否存在
   - 验证参数值的有效性
   - 提供有意义的错误消息

4. **默认值**:
   - 提供合理的默认值
   - 确保向后兼容性
   - 记录使用的默认值

5. **扩展性**:
   - 支持自定义配置项
   - 允许通过 kwargs 传递额外参数
   - 灵活适应不同需求

## 自定义配置

### 扩展OptimizationConfig

```python
from qlib.contrib.tuner.config import OptimizationConfig

class CustomOptimizationConfig(OptimizationConfig):
    def __init__(self, config, TUNER_CONFIG_MANAGER):
        super().__init__(config, TUNER_CONFIG_MANAGER)

        # 添加自定义参数
        self.custom_metric = config.get("custom_metric", None)
        self.weight_scheme = config.get("weight_scheme", "equal")
```

### 配置模板

```yaml
# 模板配置
# 可以作为基础，然后具体化
experiment:
  name: ${EXPERIMENT_NAME}
  dir: ${WORK_DIR}/experiments

optimization_criteria:
  report_type: ${REPORT_TYPE}
  report_factor: ${REPORT_FACTOR}
  optim_type: ${OPTIM_TYPE}
```

## 相关文档

- [tuner.py 文档](./tuner.md) - Tuner实现
- [pipeline.py 文档](./pipeline.md) - 管道实现
- [space.py 文档](./space.md) - 搜索空间定义
- [launcher.py 文档](./launcher.md) - 启动器
