# space.py

## 模块概述

该模块定义了参数调优的搜索空间，使用 hyperopt 的搜索空间语法。

## 搜索空间定义

### TopkAmountStrategySpace

Topk 策略的搜索空间定义。

**参数说明：**

| 参数名 | 可选值 | 说明 |
|--------|--------|------|
| topk | [30, 35, 40] | 持有股票数量 |
| buffer_margin | [200, 250, 300] | 缓冲边界 |

**使用示例：**

```python
from qlib.contrib.tuner.space import TopkAmountStrategySpace

# 在tuner配置中使用
tuner_config = {
    "strategy": {
        "class": "TopkAmountStrategy",
        "module_path": "qlib.contrib.contrib.strategy",
        "space": TopkAmountStrategySpace
    },
    ...
}
```

### QLibDataLabelSpace

Qlib 数据标签的搜索空间定义。

**参数说明：**

| 参数名 | 可选值 | 说明 |
|--------|--------|------|
| labels | 表达式列表 | 标签计算表达式 |

**可选标签表达式：**

1. `["Ref($vwap, -2)/Ref($vwap, -1) - 1]`
   - 使用 VWAP 的 2 日相对变化
   - 常用于价格动量

2. `["Ref($close, -5)/$close - 1]`
   - 使用收盘价的 5 日相对变化
   - 常用于收益预测

**使用示例：**

```python
from qlib.contrib.tuner.space import QLibDataLabelSpace

# 在tuner配置中使用
tuner_config = {
    "data_label": {
        "space": QLibDataLabelSpace
    },
    ...
}
```

## 自定义搜索空间

### 基本定义

```python
from hyperopt import hp

# 定义搜索空间
MySpace = {
    "learning_rate": hp.loguniform("lr", -7, -2),  # [1e-7, 1e-2]
    "n_estimators": hp.choice("n_estimators", [100, 200, 500]),
    "max_depth": hp.choice("max_depth", [3, 5, 7]),
    "min_child_weight": hp.uniform("min_child", 0.0, 0.5),
    "subsample": hp.uniform("subsample", 0.6, 1.0),
    "colsample_bytree": hp.uniform("colsample", 0.6, 1.0)
}
```

### Hyperopt搜索空间类型

#### 1. loguniform（对数均匀分布）

```python
hp.loguniform(name, low, high)

# 示例
learning_rate = hp.loguniform("lr", np.log(0.0001), np.log(0.1))
# 生成范围: [0.0001, 0.1]
```

**适用场景：**
- 学习率
- 正则化参数
- 尺度参数

#### 2. uniform（均匀分布）

```python
hp.uniform(name, low, high)

# 示例
dropout = hp.uniform("dropout", 0.0, 0.5)
subsample = hp.uniform("subsample", 0.5, 1.0)
```

**适用场景：**
- 丢弃率
- 采样率
- 权重系数

#### 3. choice（离散选择）

```python
hp.choice(name, options)

# 示例
n_estimators = hp.choice("n_estimators", [100, 200, 500])
max_depth = hp.choice("max_depth", [3, 5, 7, 9])
activation = hp.choice("activation", ["relu", "tanh", "sigmoid"])
```

**适用场景：**
- 整数参数
- 类别选择
- 算法选择

#### 4. randint（随机整数）

```python
hp.randint(name, low, high)

# 示例
batch_size = hp.randint("batch_size", 16, 256)
```

**适用场景：**
- 批量大小
- 隐藏层单元数

#### 5. quniform（准均匀分布）

```python
hp.quniform(name, low, high, q)

# 示例
learning_rate = hp.quniform("lr", 0.001, 0.1, 0.001)
# 只生成 0.001 的倍数
```

**适用场景：**
- 需要特定精度的参数



### 条件搜索空间

```python
from hyperopt import hp, hp

# 条件空间示例
space = hp.choice("model_type", [
    {
        "type": "lightgbm",
        "learning_rate": hp.loguniform("lr", -7, -2),
        "n_estimators": hp.choice("n_estimators", [100, 200, 500])
    },
    {
        "type": "xgboost",
        "learning_rate": hp.loguniform("lr", -6, -1),
        "max_depth": hp.choice("max_depth", [3, 5, 7])
    }
])
```

### 混合搜索空间

```python
# LightGBM 搜索空间
LGBMSpace = {
    "learning_rate": hp.loguniform("lr", -7, -2),
    "n_estimators": hp.choice("n_estimators", [100, 200, 500]),
    "max_depth": hp.choice("max_depth", [3, 5, 7]),
    "min_child_weight": hp.uniform("min_child", 0.0, 0.5),
    "subsample": hp.uniform("subsample", 0.6, 1.0),
    "colsample_bytree": hp.uniform("colsample", 0.6, 1.0),
    "reg_alpha": hp.loguniform("reg_alpha", -5, 0),
    "reg_lambda": hp.loguniform("reg_lambda", -5, 0)
}

# XGBoost 搜索空间
XGBoostSpace = {
    "learning_rate": hp.loguniform("lr", -6, -1),
    "max_depth": hp.choice("max_depth", [3, 5, 7]),
    "min_child_weight": hp.uniform("min_child", 0.0, 0.5),
    "subsample": hp.uniform("subsample", 0.6, 1.0),
    "colsample_bytree": hp.uniform("colsample", 0.6, 1.0),
    "reg_alpha": hp.loguniform("reg_alpha", -5, 0),
    "reg_lambda": hp.loguniform("reg_lambda", -5, 0)
}

# 策略搜索空间
StrategySpace = {
    "topk": hp.choice("topk", [20, 30, 40, 50]),
    "n_drop": hp.choice("n_drop", [2, 3, 5, 10]),
    "hold_thresh": hp.choice("hold_thresh", [1, 2, 3])
}
```

## 完整配置示例

### 单模型调优

```yaml
# config.yaml
experiment:
  name: my_tuner_experiment
  dir: ./experiments

optimization_criteria:
  report_type: pred_long
  report_factor: information_ratio
  optim_type: max

data:
  class: DataHandlerLP
  module_path: qlib.data.dataset.handler
  kwargs:
    instruments: all
    start_time: 2018-01-01
    end_time: 2021-12-31

time_period:
  train: (2018-01-01, 2020-12-31)
  valid: (2021-01-01, 2021-06-30)
  test: (2021-07-01, 2021-12-31)

backtest:
  exchange: Exchange
  start_time: 2021-07-01
  end_time: 2021-12-31

tuner_pipeline:
  - model:
      class: LGBModel
      module_path: qlib.contrib.model.lgboost
      space: LGModelSpace
    strategy:
      class: TopkDropoutStrategy
      module_path: qlib.contrib.strategy
      space: TopkAmountStrategySpace
    max_evals: 50
```

### 多模型对比调优

```yaml
tuner_pipeline:
  # LightGBM 调优
  - model:
      class: LGBModel
      module_path: qlib.contrib.model.lgboost
      space: LGModelSpace
    strategy:
      class: TopkDropoutStrategy
      module_path: qlib.contrib.strategy
      space: TopkAmountStrategySpace
    max_evals: 50

  # XGBoost 调优
  - model:
      class: XGBModel
      module_path: qlib.contrib.model.xgboost
      space: XGBoostSpace
    strategy:
      class: TopkDropoutStrategy
      module_path: qlib.contrib.strategy
      space: TopkAmountStrategySpace
    max_evals: 50
```

## 注意事项

1. **空间设计**:
   - 合理设置参数范围
   - 避免过大或过小的值
   - 考虑参数之间的相互作用

2. **搜索效率**:
   - 优先调整重要参数
   - 限制搜索空间大小
   - 使用合适的分布类型

3. **参数约束**:
   - 注意参数之间的依赖关系
   - 使用条件空间处理依赖
   - 验证参数组合的有效性

4. **日志记录**:
   - 记录搜索空间定义
   - 追踪探索的参数
   - 分析优化结果

5. **调试技巧**:
   - 从小空间开始测试
   - 使用固定参数验证
   - 检查参数传递是否正确

## 相关文档

- [tuner.py 文档](./tuner.md) - 调优器实现
- [pipeline.py 文档](./pipeline.md) - 管道实现
- [config.py 文档](./config.md) - 配置管理
