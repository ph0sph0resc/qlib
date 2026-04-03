# __init__.py

## 模块概述

该模块是 `qlib.contrib.strategy.optimizer` 的入口模块，导出了投资组合优化相关的类。

## 导入的类

- **BaseOptimizer**: 优化器基类
- **PortfolioOptimizer**: 投资组合优化器（全局最小方差、均值方差、风险平价）
- **EnhancedIndexingOptimizer**: 增强指数优化器

## 优化器分类

### 1. 基础优化器 (BaseOptimizer)

抽象基类，定义了优化器的接口。

**特点：**
- 提供统一的优化接口
- 支持自定义优化方法

### 2. 投资组合优化器 (PortfolioOptimizer)

支持多种经典投资组合优化方法的实现。

**支持的方法：**

- **"gmv"**: 全局最小方差投资组合
- **"mvo"**: 均值方差优化
- **"rp"**: 风险平价
- **"inv"**: 反波动率

**特点：**
- 无卖空且全投资
- 支持换仓率限制
- 支持 L2 正则化

### 3. 增强指数优化器 (EnhancedIndexingOptimizer)

专门用于增强指数投资组合的优化器。

**特点：**
- 最大化超额收益
- 控制跟踪误差
- 支持因子偏离限制
- 支持强制持有/卖出约束

## 使用示例

### PortfolioOptimizer

```python
from qlib.contrib.strategy.optimizer import PortfolioOptimizer
import numpy as np

# 创建优化器
optimizer = PortfolioOptimizer(
    method="mvo",       # 均值方差优化
    lamb=0.5,         # 风险厌恶参数
    delta=0.2,         # 换仓率限制
    alpha=0.01         # L2正则化
)

# 准备数据
S = np.cov(returns.T)  # 协方差矩阵
r = np.mean(returns, axis=1)  # 期望收益
w0 = np.ones(n) / n  # 初始权重

# 优化
weights = optimizer(S, r, w0)
print(f"Optimized weights: {weights}")
```

### EnhancedIndexingOptimizer

```python
from qlib.contrib.strategy.optimizer import EnhancedIndexingOptimizer

# 创建优化器
optimizer = EnhancedIndexingOptimizer(
    lamb=1.0,         # 风险厌恶参数
    delta=0.2,         # 换仓率限制
    b_dev=0.01,        # 基准偏离限制
    f_dev=[0.1, 0.1, 0.1],  # 因子偏离限制
    epsilon=5e-5       # 最小权重
)

# 准备数据
r = expected_returns          # 期望收益
F = factor_exposure          # 因子暴露
cov_b = factor_covariance     # 因子协方差
var_u = specific_variance    # 特质风险
w0 = current_weights        # 当前权重
wb = benchmark_weights       # 基准权重

# 优化
weights = optimizer(
    r=r, F=F, cov_b=cov_b, var_u=var_u,
    w0=w0, wb=wb
)
print(f"Enhanced weights: {weights}")
```

## 优化器选择指南

| 优化器 | 适用场景 | 优点 | 缺点 |
|--------|----------|------|------|
| GMV | 风险厌恶 | 最小化风险 | 忽视收益 |
| MVO | 风险-收益权衡 | 经典理论 | 参数敏感 |
| RP | 风险分散 | 自动风险分配 | 计算复杂 |
| INV | 简单快速 | 易实现 | 不考虑相关性 |
| EnhancedIndexing | 超额收益 | 风险可控 | 需要风险模型 |

## 优化问题对比

### 全局最小方差 (GMV)

```math
min_w   w' Σ w
s.t.   w ≥ 0
        Σw = 1
```

### 均值方差优化 (MVO)

```math
min_w   - w' r + λ * w' Σ w
s.t.   w ≥ 0
        Σw = 1
        Σ|w - w₀| ≤ δ
```

### 风险平价 (RP)

```math
min_w   Σᵢ [wᵢ - (w' Σ w) / ((Σ w)ᵢ * N)]²
s.t.   w ≥ 0
        Σw = 1
```

### 增强指数优化

```math
max_w   d' r - λ * (v' Σ_b v + σᵤ² ⊙ d²)
s.t.   w ≥ 0
        Σw = 1
        Σ|w - w₀| ≤ δ
        d ≥ -b_dev
        d ≤ b_dev
        v ≥ -f_dev
        v ≤ f_dev
```

其中：
- d = w - w_b: 基准偏离
- v = d @ F: 因子偏离

## 注意事项

1. **PortfolioOptimizer**:
   - 协方差矩阵必须为正定
   - 收益和权重维度必须匹配
   - 换仓率限制可能导致无解

2. **EnhancedIndexingOptimizer**:
   - 需要准备风险模型数据
   - 约束条件可能冲突
   - 优化失败会返回当前权重

3. **通用注意事项**:
   - 权重和为 1.0
   - 权重非负
   - 监控优化状态和收敛情况

## 相关文档

- [base.py 文档](./base.md) - 优化器基类
- [optimizer.py 文档](./optimizer.md) - 投资组合优化器
- [enhanced_indexing.py 文档](./enhanced_indexing.md) - 增强指数优化器
