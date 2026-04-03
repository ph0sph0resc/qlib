# Qlib 架构设计文档

## 概述

Qlib是Microsoft开源的量化投资平台，包含数据处理、模型训练、回测、投资组合优化和订单执行的完整流程。平台支持Python 3.8-3.12，集成了PyTorch、LightGBM、XGBoost、CatBoost等多种机器学习框架。

```python
# 典型使用模式
import qlib
from qlib.constant import REG_CN
from qlib.data import D

# 初始化
qlib.init(provider_uri="~/.qlib/qlib_data/cn_data", region=REG_CN)

# 获取数据
instruments = D.instruments("csi500")
fields = ["$close", "$volume", "Ref($close, 1)", "Mean($close, 3)"]
df = D.features(instruments, fields, start_time="2020-01-01", end_time="2020-12-31")
```

## 核心架构

### 分层设计

Qlib采用分层架构，从数据访问到策略执行形成完整闭环：

```
┌─────────────────────────────────────────────────────────────┐
│                    用户层 (User Layer)                    │
│  examples/benchmarks/  用户脚本和示例             │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                  扩展层 (Contrib Layer)                │
│  contrib/model/     模型实现                        │
│  contrib/strategy/  策略实现                      │
│  contrib/data/      数据处理器                      │
│  contrib/report/     分析报告                       │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                  核心层 (Core Layer)                  │
│  data/            数据访问和计算                   │
│  model/           模型接口                        │
│  workflow/         实验管理                        │
│  backtest/         回测引擎                        │
│  strategy/         策略接口                        │
│  rl/              强化学习框架                     │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                  存储层 (Storage Layer)                │
│  LocalProvider     本地文件存储                   │
│  RedisCache       分布式缓存                       │
│  MLflow          实验跟踪                       │
└─────────────────────────────────────────────────────────────┘
```

### 模块间交互

数据通过统一的接口在模块间流动：

```python
# 数据层 → 模型层
dataset = D.features(instruments, fields, start_time, end_time)
model = LGBModel(...)
model.fit(dataset)  # 训练
predictions = model.predict(dataset)  # 预测

# 模型层 → 策略层

strategy = TopkDropoutStrategy(signal=(model, dataset), topk=50, n_drop=5)

# 策略层 → 回测层
executor = SimulatorExecutor(...)
with R.start(experiment_name="test"):
    backtest_result = executor.backtest(
        start_time="2017-01-01",
        end_time="2020-12-31",
        strategy=strategy,
        account=100000000
    )
```

## 数据管理层 (qlib/data/)

### Provider架构

数据访问基于Provider抽象，每个Provider负责特定类型的数据：

```python
# Provider接口
class CalendarProvider:
    def calendar(self, start_time, end_time, freq): ...

class InstrumentProvider:
    def list_instruments(self, market, filter_pipe): ...

class FeatureProvider:
    def features(self, instruments, fields, start_time, end_time): ...

class ExpressionProvider:
    def expression(self, instruments, field, start_time, end_time): ...

class DatasetProvider:
    def dataset(self, instruments, fields, start_time, end_time): ...
```

### 表达式计算

表达式系统支持复杂的技术指标计算：

```python
# 基础表达式
fields = [
    "$close",           # 原始字段
    "Ref($close, 1)",   # 引用前一日收盘价
    "Mean($close, 3)",  # 3日均值
    "Std($close, 20)",  # 20日标准差
    "$close / Ref($close, 1) - 1",  # 日收益率
]

# 组合表达式
features = D.features(instruments, fields, start_time, end_time)
```

### 缓存系统

两级缓存提升数据访问性能：

```python
# 内存缓存（默认启用）
mem_cache_size_limit: 500  # MB
mem_cache_expire: 3600      # 1小时

# 磁盘缓存（可选）
expression_cache: DiskExpressionCache
dataset_cache: DiskDatasetCache
local_cache_path: ~/.cache/qlib_simple_cache
```

## 模型层 (qlib/model/)

### 模型继承体系



```python
BaseModel
├── Model              # 可学习模型
│   ├── ModelFT       # 可微调模型
│   │   └── LGBModel, XGBModel, DNNModelPytorch
│   └── GBDTModel, LinearModel
└── RiskModel          # 风险模型
```

### 统一接口

所有可学习模型遵循相同的接口：

```python
class Model(BaseModel):
    def fit(self, dataset, reweighter):
        """训练模型"""

    def predict(self, dataset, segment="test"):
        """生成预测"""

    def save(self, path):
        """保存模型"""

    @classmethod
    def load(cls, path):
        """加载模型"""
```

### 集成学习实现

LightGBM和XGBoost的集成实现展示了标准模式：

```python
# 配置示例
model_config = {
    "class": "LGBModel",
    "module_path": "qlib.contrib.model.gbdt",
    "kwargs": {
        "loss": "mse",
        "objective": "regression",
        "learning_rate": 0.05,
        "num_leaves": 31,
    }
}

model = init_instance_by_config(model_config)
```

## 工作流管理 (qlib/workflow/)

### 实验记录器

QlibRecorder管理实验生命周期：

```python
from qlib.workflow import R

with R.start(experiment_name="my_experiment"):
    # 记录参数
    R.log_params(learning_rate=0.01, epochs=100)

    # 记录指标
    R.log_metrics(ic=0.05, rank_ic=0.12)

    # 保存对象
    R.save_objects(trained_model=model, dataset=dataset)

    # 加载对象
    recorder = R.get_recorder()
    loaded_model = recorder.load_object("trained_model")
```

### MLflow集成

实验自动跟踪到MLflow：

```yaml
exp_manager:
  class: MLflowExpManager
  module_path: qlib.workflow.expm
  kwargs:
    uri: "file://./mlruns"
    default_exp_name: "Experiment"
```

## 回测引擎 (qlib/backtest/)

### 核心组件

```python
Exchange       # 交易所模拟，处理订单成交
Account        # 账户管理，跟踪资金和持仓
BaseExecutor   # 执行器基类
Order          # 订单类
TradeDecision  # 交易决策类
```

### 执行流程

```python
executor = SimulatorExecutor(exchange=exchange, account=account)

# 单步执行
executor.run_one_step(execute_result=execute_result, trade_decision=trade_decision)

# 完整回测
result = executor.backtest(
    start_time="2017-01-01",
    end_time="2020-12-31",
    strategy=strategy,
    account=100000000
)

# 结果分析
print(f"年化收益: {result['annualized_return']}")
print(f"最大回撤: {result['max_drawdown']}")
```

## 交易策略 (qlib/strategy/)

### 策略类型

```python
BaseStrategy                    # 策略基类
├── BaseSignalStrategy            # 信号策略
│   └── TopkDropoutStrategy      # Top-K选股策略
├── RLStrategy                   # 强化学习策略
└── TWAPStrategy                 # 时间加权平均价格策略
```

### 信号策略实现

```python
from qlib.contrib.strategy.signal_strategy import TopkDropoutStrategy

strategy = TopkDropoutStrategy(
    signal=(model, dataset),  # 模型+数据集生成信号
    topk=50,                  # 选择前50只
    n_drop=5,                  # 每次交易替换5只
    risk_degree=0.95           # 风险控制
)
```

## 强化学习框架 (qlib/rl/)

### 环境组件

RL环境基于Gym接口构建：

```python
Simulator        # 模拟器基类，定义环境状态
Reward           # 奖励函数
StateInterpreter  # 状态解释器（状态→观察）
ActionInterpreter # 动作解释器（动作→环境动作）
EnvWrapper       # Gym环境包装器
```

### 训练系统

基于Tianshou框架的RL训练：

```yaml
policy:
  class: PPO
  module_path: qlib.rl.order_execution.policy
  kwargs:
    lr: 0.0001
    update_epoch: 10

trainer:
  max_iters: 1000
  episode_per_iter: 10
  update_per_iter: 5
```

### 订单执行场景

RL应用于订单执行优化：

```python
# 环境配置
env_config = {
    "simulator": SingleAssetOrderExecution,
    "state_interpreter": FullHistoryStateInterpreter,
    "action_interpreter": CategoricalActionInterpreter,
    "reward": PPOReward,
}

# 训练
trainer = Trainer(..., env_config=env_config)
trainer.train()
```

## 设计模式

### 抽象工厂模式

Provider创建通过配置动态实例化：

```python
def init_instance_by_config(config: dict):
    """根据配置创建实例"""
    module = importlib.import_module(config["module_path"])
    cls = getattr(module, config["class"])
    return cls(**config.get("kwargs", {}))
```

### 策略模式

数据操作、模型算法、执行策略均可灵活替换：

```python
# 可替换的数据处理器
processor_config = {
    "class": "Alpha158",
    "module_path": "qlib.contrib.data.handler"
}

# 可替换的模型
model_config = {
    "class": "LGBModel",
    "module_path": "qlib.contrib.model.gbdt"
}
```

### 模板方法模式

基类定义算法骨架，子类实现细节：

```python
class Model(BaseModel):
    def fit(self, dataset, reweighter):
        # 1. 数据准备
        ds = self._prepare_dataset(dataset)

        # 2. 模型训练（子类实现）
        self._fit_backend(ds)

        # 3. 后处理
        self._post_fit()
```

### 门面模式

D类提供统一的数据访问接口：

```python
from qlib.data import D

# 所有数据操作通过D类
D.calendar(...)
D.instruments(...)
D.features(...)
```

### 责任链模式

嵌套执行器支持多时间频率的复杂策略：

```python
# 外层：日级投资组合策略
outer_executor = SimulatorExecutor(...)

# 内层：分钟级订单执行策略
inner_executor = SimulatorExecutor(...)

# 嵌套执行
nested_executor = NestedExecutor(outer_executor=outer_executor, inner_executor=inner_executor)
```

## 配置系统

### 配置结构

```python
# 核心配置类
C = QlibConfig()

# 设置配置
C.set(
    mode="client",        # client/server
    region=REG_CN,          # REG_CN/REG_US/REG_TW
    provider_uri="~/.qlib/qlib_data/cn_data",
    redis_cache=False,
    expression_cache=None,
    dataset_cache=None
)
```

### 区域配置

不同市场区域有默认配置：

```python
REG_CN:
  trade_unit: 100
  limit_threshold: 0.095
  deal_price: close

REG_US:
  trade_unit: 1
  limit_threshold: None
  deal_price: close

REG_TW:
  trade_unit: 1000
  limit_threshold: 0.1
  deal_price: close
```

## 性能优化

### 多进程计算

数据计算支持并行：

```python
# CPU配置
kernels: NUM_USABLE_CPU
joblib_backend: multiprocessing

# 使用方法
features = D.features(
    instruments,
    fields,
    start_time,
    end_time,
    n_jobs=4  # 使用4个进程
)
```

### Cython优化

性能关键操作使用Cython编译：

```python
# rolling.pyx → rolling.so
# expanding.pyx → expanding.so

# 使用示例
from qlib.data._libs import rolling, expanding
```

### 缓存策略

三级缓存提升重复查询性能：

```
1. 内存缓存（最快，容量限制）
2. 磁盘缓存（快速，持久化）
3. 数据源（最慢，原始数据）
```

## 扩展指南

### 添加自定义模型

```python
from qlib.model.base import Model

class MyCustomModel(Model):
    def _fit_backend(self, dataset):
        """实现训练逻辑"""
        x = dataset.load_data()
        y = dataset.load_label()
        # ... 训练代码

    def _predict_backend(self, dataset):
        """实现预测逻辑"""
        x = dataset.load_data()
        # ... 预测代码
        return predictions
```

### 添加自定义策略

```python
from qlib.strategy.base import BaseStrategy

class MyCustomStrategy(BaseStrategy):
    def generate_trade_decision(self, execute_result):
        """生成交易决策"""
        # ... 策略逻辑
        return trade_decision
```

### 添加数据处理器

```python
from qlib.data.dataset.processor import Processor

class MyProcessor(Processor):
    def __call__(self, df):
        """处理数据"""
        # ... 处理逻辑
        return df
```

## 最佳实践

### 1. 使用配置文件

推荐使用YAML配置而非硬编码：

```yaml
model:
  class: LGBModel
  module_path: qlib.contrib.model.gbdt
  kwargs:
    loss: mse
    objective: regression

strategy:
  class: TopkDropoutStrategy
  module_path: qlib.contrib.strategy.signal_strategy
  kwargs:
    topk: 50
    n_drop: 5
```

### 2. 使用实验记录

所有实验都应使用R记录器：

```python
with R.start(experiment_name="experiment"):
    R.log_params(**config)
    model.fit(dataset)
    R.log_metrics(ic=calculate_ic(model, dataset))
```

### 3. 分离数据段

确保训练/验证/测试数据分离：

```yaml
dataset:
  class: DatasetH
  module_path: qlib.data.dataset
  kwargs:
    segments:
      train: [2008-01-01, 2014-12-31]
      valid: [2015-01-01, 2016-12-31]
      test: [2017-01-01, 2017-12-31]
```

### 4. 风险控制

策略中包含风险控制参数：

```python
strategy = TopkDropoutStrategy(
    signal=(model, dataset),
    topk=50,
    n_drop=5,
    risk_degree=0.95,      # 风险控制
    risk_degree_gap=0.10     # 风险容忍度
)
```

## 相关文档

### API 文档

**API 接口文档**

- [API 总览](api/README.md) - API文档入口
- [API Data](api/data.md) - 数据层API参考
- [API Model](api/model.md) - 模型层API参考
- [API Backtest](api/backtest.md) - 回测层API参考
- [API Strategy](api/strategy.md) - 策略层API参考
- [API Workflow](api/workflow.md) - 工作流层API参考

**类设计文档**

- [Model Classes](api/classes_model.md) - 所有模型类的设计
- [Backtest Classes](api/classes_backtest.md) - 所有回测类的设计
- [Data Classes](api/classes_data.md) - 所有数据类的设计
- [Strategy Classes](api/classes_strategy.md) - 所有策略类的设计
- [Workflow Classes](api/classes_workflow.md) - 所有不作流类的设计
- [RL Classes](api/classes_rl.md) - 所有强化学习类的设计
- [Contrib Classes](api/classes_contrib.md) - 所有扩展类的设计

- [架构设计文档](../ARCHITECTURE_DESIGN.md) - 系统架构和设计模式
- [CLAUDE.md](../CLAUDE.md) - 项目开发指南
- [官方文档](https://qlib.readthedocs.io/) - 完整的在线文档

## 总结

Qlib的架构设计具有以下特点：

1. **高度解耦**：各模块通过清晰接口交互
2. **灵活配置**：支持多种数据源、模型、策略
3. **高性能**：多进程计算、Cython优化、三级缓存
4. **可扩展**：抽象基类支持自定义实现
5. **企业级**：MLflow集成、实验跟踪、分布式缓存
6. **完整工具链**：从数据到策略到回测的完整流程

这种设计使得Qlib既能满足快速原型开发，又能支持生产级量化研究。
