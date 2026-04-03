# __init__.py

## 模块概述

该模块是 `qlib.contrib.strategy` 的入口模块，导出了多种交易策略类。

## 导入的类

### 信号策略 (signal_strategy.py)

- **TopkDropoutStrategy**: Topk 丢弃策略，基于得分选择股票并定期调仓
- **WeightStrategyBase**: 权重策略基类，基于权重分配生成交易决策
- **EnhancedIndexingStrategy**: 增强指数策略，在跟踪误差约束下优化投资组合

### 规则策略 (rule_strategy.py)

- **TWAPStrategy**: 时间加权平均价格策略，将订单分解到多个时间点
- **SBBStrategyBase**: 选择更优交易时段策略基类
- **SBBStrategyEMA**: 基于EMA信号的选择更优交易时段策略

### 成本控制策略 (cost_control.py)

- **SoftTopkStrategy**: 软Topk策略，考虑交易影响的预算约束再平衡

## 策略分类

### 1. 信号策略

基于模型预测信号进行投资组合管理的策略。

**特点：**
- 使用机器学习模型的预测得分
- 选择特定数量或权重的股票
- 支持动态调仓

**适用场景：**
- 主动管理
- 因子投资
- 量化选股

### 2. 规则策略

基于预定义规则执行交易订单的策略。

**特点：**
- 不依赖预测信号
- 专注于订单执行优化

- 降低市场冲击成本

**适用场景：**
- 大额订单分批执行
- 算法交易
- 执行优化

### 3. 成本控制策略

在执行策略中考虑交易成本和市场影响的策略。

**特点：**
- 控制换仓成本
- 限制单次交易影响
- 确定性的买入卖出

**适用场景：**
- 资金管理
- 机构交易
- 风险控制

## 使用示例

### TopkDropoutStrategy

```python
from qlib.contrib.strategy import TopkDropoutStrategy
from qlib.model import LSTM
from qlib.data import Dataset

# 创建策略
strategy = TopkDropoutStrategy(
    signal=(LSTM(), Dataset(...)),
    topk=30,                    # 持有30只股票
    n_drop=5,                    # 每次调仓替换5只
    method_sell="bottom",          # 卖出得分最低的
    method_buy="top",            # 买入得分最高的
    hold_thresh=1,               # 至少持有1天
    only_tradable=True,          # 只交易可交易股票
    risk_degree=0.95             # 95%仓位
)
```

### TWAPStrategy

```python
from qlib.contrib.strategy import TWAPStrategy
from qlib.backtest.decision import TradeDecisionWO

# 创建子订单
outer_decision = TradeDecisionWO([order1, order2, ...])

# 创建TWAP策略
twap_strategy = TWAPStrategy(
    outer_trade_decision=outer_decision,
    trade_exchange=exchange
)

# 每个时间段执行一部分订单
decision = twap_strategy.generate_trade_decision()
```

### SoftTopkStrategy

```python
from qlib.contrib.strategy import SoftTopkStrategy

# 创建软Topk策略
strategy = SoftTopkStrategy(
    signal=(model, dataset),
    topk=30,
    trade_impact_limit=0.3,    # 每次最大变动30%
    risk_degree=0.95,
    buy_method="first_fill"
)
```

### EnhancedIndexingStrategy

```python
from qlib.contrib.strategy import EnhancedIndexingStrategy

# 创建增强指数策略
strategy = EnhancedIndexingStrategy(
    signal=(model, dataset),
    riskmodel_root="/path/to/riskmodel",
    market="csi500",
    turn_limit=0.2,
    optimizer_kwargs={
        "lamb": 1.0,
        "delta": 0.2,
        "b_dev": 0.01
    }
)
```

## 策略选择指南

| 策略类型 | 适用场景 | 优点 | 缺点 |
|----------|----------|------|------|
| TopkDropoutStrategy | 主动选股 | 简单直观，易于理解 | 忽略持仓成本 |
| WeightStrategyBase | 精细权重控制 | 灵活，可自定义 | 实现复杂 |
| EnhancedIndexingStrategy | 跟踪指数 | 风险可控，超额收益 | 需要风险模型 |
| TWAPStrategy | 大额订单 | 降低市场冲击 | 执行时间长 |
| SoftTopkStrategy | 预算约束上 | 成本可控 | 实现复杂 |

## 策略组合

### 信号策略 + 规则策略

```python
# 先用信号策略生成目标持仓
signal_strategy = TopkDropoutStrategy(...)

# 再用TWAP执行订单
twap_strategy = TWAPStrategy(
    outer_trade_decision=signal_strategy.generate_trade_decision()
)
```

### 层级策略

```python
# 使用策略工厂创建多层级策略
from qlib.contrib.strategy import StrategyExecutor

executor = StrategyExecutor(
    signal_strategy=TopkDropoutStrategy(...),
    execution_strategy=TWAPStrategy(...)
)

executor.run()
```

## 自定义策略

### 继承 WeightStrategyBase

```python
from qlib.contrib.strategy import WeightStrategyBase

class MyCustomStrategy(WeightStrategyBase):
    def __init__(self, custom_param=1.0, **kwargs):
        super().__init__(**kwargs)
        self.custom_param = custom_param

    def generate_target_weight_position(
        self, score, current,
        trade_start_time, trade_end_time, **kwargs
    ):
        # 实现自定义权重分配逻辑
        weights = {}
        for stock, s in score.items():
            weights[stock] = max(0, s) / sum(max(0, x) for x in score)
        return weights
```

## 注意事项

1. **信号策略**:
   - 需要定期更新预测信号
   - 考虑预测信号的滞后性

2. **规则策略**:
   - 需要配置合适的执行参数
   - 考虑交易时间和流动性

3. **成本控制**:
   - 准确估计交易成本
   - 平衡收益和成本

4. **风险控制**:
   - 监控投资组合风险指标
   - 设置合理的风险限制

5. **回测验证**:
   - 在实盘使用前充分回测
   - 考虑交易成本和滑点

## 相关文档

- [signal_strategy.py 文档](./signal_strategy.md) - 信号策略详细实现
- [rule_strategy.py 文档](./rule_strategy.md) - 规则策略详细实现
- [cost_control.py 文档](./cost_control.md) - 成本控制策略详细实现
- [order_generator.py 文档](./order_generator.md) - 订单生成器
- [optimizer/](./optimizer/) - 投资组合优化器
