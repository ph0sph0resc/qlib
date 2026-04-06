# data/_libs/rolling.pyx 模块文档

## 文件概述

此文件使用Cython实现了高性能的滚动（rolling）运算函数，为大幅提升时间序列计算的效率。包括滚动均值、斜率、R平方和残差等统计函数。

## 函数说明

### rolling()

**功能**:
- 通用滚动函数
- 对numpy数组进行滚动窗口计算
- 支持任意滚动运算对象

**参数**:
- `r`: 滚动运算对象（Rolling类实例）
- `a`: 输入数组
- 返回：计算结果数组

**使用示例**:
```python
import numpy as np

data = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0])
result = rolling(Rolling(3))(data)  # 3日滚动
# result: [nan, 1.666, 6.66, 6.66, 6.66]
```

### rolling_mean()

**功能**:
- 滚动均值（Rolling Mean）
- 使用累积和方法提高计算效率

**参数**:
- `r`: 滚动均值运算对象（Mean类实例）
- `a`: 输入数组
- 返回：滚动均值数组

**数学公式**:
```
Mean(t) = (x[1] + x[2] + ... + x[t]) / (t - na_count)
```
- 其中x为当前窗口数据，t为窗口大小，na_count为NaN计数

**使用示例**:
```python
import numpy as np

data = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
result = rolling_mean(Rolling(3))(data)
# result: [nan, 1.666, 6.66, 6.66, 6.66]
```

### rolling_slope()

**功能**:
- 滚动线性回归斜率（Rolling Slope）
- 计算线性回归：y = a*x + b

**参数**:
- `r`: 滚动斜率运算对象（Slope类实例）
- `a`: 输入数组
- 返回：滚动斜率数组

**数学公式**:
```
N = t - na_count
slope = (N*Σ(xy) - Σx*Σy) / (N*Σ(x²) - (Σx)²)
```
- N为窗口有效大小（去NaN计数），xy为Σ(x²)，x为Σ(x)，y为Σ(y)

**使用示例**:
```python
import numpy as np

# 创建时间序列
t = np.arange(1, 101)
# 添加趋势
y = t + np.random.randn(100) * 0.01

# 记算滚动斜率
result = rolling_slope(Rolling(10))(y)
# result: 滚动10日斜率
```

### rolling_rsquare()

**功能**:
- 滚动R平方（Rolling Rsquare）
- 计算线性回归的R平方：R² = Σ(y - ŷ)² / Σ(x - x̄)²

**参数**:
- `r`: 滚动R平方运算对象（Rsquare类实例）
- `a`: 输入数组
- 返回：滚动R平方数组

**数学公式**:
```
N = t - na_count
R² = Σ(y - ŷ)² / Σ(x - x̄)²
R² = Σ(y)² / Σ(x - x̄)² * Σ(x - x̄)²
```
- t为窗口数据，N为有效大小（去NaN计数）

**使用示例**:
```python
import numpy as np

# 创建价格序列
prices = np.cumprod([1.0] * 100) * 0.99)
# 添加波动
prices += np.random.randn(100) * 0.5

# 计算滚动R平方
result = rolling_rsquare(Rolling(10))(prices)
# result: 滚动10日R平方
```

### rolling_resi()

**功能**:
- 滚动回归残差（Rolling Resi）
- 计算线性回归的残差：Resi = y - ŷ̂

**参数**:
- `r`: 滚动残差运算对象（Resi类实例）
- `a`: 输入数组
- 返回：滚动残差数组

**数学公式**:
```
N = t - na_count
slope = (N*Σ(xy) - Σx*Σy) / (N*Σ(x²) - (Σx)²)
x_mean = Σ(x) / N
y_mean = Σ(y) / N
Resi = y - (slope*t + x_mean)
```
- t为窗口数据，N为有效大小（去NaN计数）

**使用示例**：
```python
import numpy as np

# 创建价格序列
prices = np.cumprod([1.0] * 100) * 0.99)
# 添加波动
prices += np.random.randn(100) * 0.5

# 计算滚动残差
result = rolling_resi(Rolling(10))(prices)
# result: 残�动10日残差
```

## 类说明

### Rolling 类（抽象）

**说明**:
- 滚动运算基类
- 维护窗口和双端队列

**主要属性**:
- `window`: 滚动窗口大小
- `barv`: 双端队列（用于存储窗口数据）
- `na_count`: NaN计数

**主要方法**:

```python
def __init__(self, window: int)
```
- 初始化滚动窗口
- 参数：window: �口大小

```python
def update(self, val) -> float
```
- 更新窗口数据
- 参数：
- val: 新数据值
- 返回：更新后的值
- 子类需实现此方法

### Mean 类

**继承关系**:
- 继承自 Rolling

**说明**:
- 滚动均值类
- 使用累积和方法计算

**主要方法**:

```python
def update(self, val) -> float
```
- 更新均值
- 实现细节见数学公式部分

### Slope 类

**继承关系**:
- 继承自 Rolling

**说明**:
- 滚动斜率类
- 计算线性回归斜率

**主要方法**:

```python
def update(self, val) -> float
```
- 更新斜率
- 实现细节见数学公式部分

### Rsquare 类

**继承关系**:
- 继承自 Rolling

**说明**:
- 滚动R平方类
- 计算R平方

**主要方法**:

```python
def update(self, val) -> float
```
- 更新R平方
- 实现细节见数学公式部分

### Resi 类

**继承关系**:
- 继承自 Rolling

**说明**:
- 滚动残差类
- 计算回归残差

**主要方法**:

```python
def update(self, val) -> float
```
- 更新残差
- 实现细节见数学公式部分

## 设计模式

### 滚动模式

```
窗口大小 = N
    ↓
双端队列维护窗口数据
    ↓
新数据进入队列
    ↓
满？ → 移除队首元素
    ↓
更新累加和
    ↓
NaN处理 → 更新na_count
    ↓
返回值
```

### 在线更新公式

```
# Mean更新
self.vsum += val (或减去旧值)
self.barv.push_back(val)
if isnan(val):
    self.na_count += 1
else:
    self.na_count -= 1
self.barv.pop_front()
```

### 性能优化

1. **Cython加速**：使用C语言编译，性能比纯Python快10-100倍
2. **双端队列**：使用collections.deque避免列表操作开销
3. **向量化操作**：使用numpy的向量化操作
4. **避免重复计算**：中间结果缓存（i_sum、x_sum等）
5. **内存效率**：使用原地操作减少内存分配

## 注意事项

1. **线程安全**：
- 此类不是线程安全的
- �免在多线程环境中使用
2. **NaN处理**：
- 使用isnan()检测NaN值
- 未处理的NaN值会累积到na_count中
3. **窗口边界**：
- �口固定，保证数据正确性
- 开始阶段可能有NaN填充
4. **数值溢出**：
- 使用numpy的异常处理机制
5. **类型兼容**：
- 使用float32或float64类型
6. **初始化顺序**：
- 初始化后队列中的数据顺序很重要

## 相关文件

- **qlib/data/ops.py**: 使用滚动运算的Python封装
- **qlib/data/_libs/expanding.pyx**: Expanding运算符
- **qlib/data/base.py**: 表达式基类
- **numpy**: 数值计算
