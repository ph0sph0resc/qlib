# data/_libs/expanding.pyx 模块文档

## 文件概述

此文件使用Cython实现了扩展（Expanding）运算函数，支持对整个历史数据进行累积统计运算，包括扩展均值、斜率、R平方和残差等。

## 函数说明

### expanding()

**功能**:
- 通用扩展函数
- 对numpy数组进行扩展窗口计算
- 支持任意扩展运算对象

**参数**:
- `r`: 扩展运算对象（Expanding类实例）
- `a`: 输入数组
- 返回：计算结果数组

**使用示例**:
```python
import numpy as np

data = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
result = expanding(Expanding())(data)
# result: [1.0, 1.5, 2.0, 3.0, 4.0, 5.0]
```

### expanding_mean()

**功能**:
- 扩展均值（Expanding Mean）
- 对整个历史数据计算累积均值
- 使用累积和方法提高效率

**参数**:
- `r`: 扩展均值运算对象（Mean类实例）
- `a`: 输入数组
- 返回：扩展均值数组

**数学公式**：
```
Mean(t) = Σ(y[t] / t
```
- 其中y为当前窗口数据，t为窗口大小

**使用示例**:
```python
import numpy as np

# 创建价格序列
t = np.arange(1, 101)
# 添加趋势
y = t * 1.0 + np.random.randn(100) * 0.05

# 计算扩展均值
result = expanding_mean(Expanding())(y)
# result: [1.0, 1.05, 1.05, ...]
```

### expanding_slope()

**功能**:
- 扩展斜率（Expanding Slope）
- 计算线性回归斜率：y = a*x + b

**参数**:
- `r`: 扩展斜率运算对象（Slope类实例）
- `a`: 输入数组
- 返回：扩展斜率数组

**数学公式**：
```
size_t = size_t = t
xy = Σ(x*t) = Σ(x*size_t)
x² = Σ(x²*size_t²)
y² = Σ(y²*size_t²)
xy = Σ(x*y*size_t)
slope = (xy² - x²*y) / (x²*y² - xy²)
```
- 其中：t为当前数据长度

**使用示例**：
```python
import numpy as np

# 创建价格序列
t = np.arange(1, 101)
# 添加趋势
y = t * 1.0 + np.random.randn(100) * 0.05

# 计算扩展斜率
result = expanding_slope(Expanding())(y)
# result: [1.0, 1.05, 1.05, ...]
```

### expanding_rsquare()

**功能**:
- 扩展R平方（Expanding Rsquare）
- 计算R平方：R² = Σ(y - ŷ)² / Σ(x - x̄)²

**参数**:
- `r`: 扩展R平方运算对象（Rsquare类实例）
- `a`: 输入数组
- 返回：扩展R平方数组

**数学公式**：
```
size_t = size_t = t
x̄² = Σ(x²*size_t²)
ȳ² = Σ(y²*size_t²)
xy = Σ(x*y*size_t)
y² = Σ(y²*size_t²)
y² = Σ(y²*size_t²)
xy = Σ(x*y*size_t²)
R² = xy² / √(xy² * Σ(x - x̄²)
```
- 其中：x̄² = Σ(x²)，xy² = Σ(y²)

**使用示例**：
```python
import numpy as np

# 创建价格序列
t = np.arange(1, 101)
# 添加波动
y = t * 1.0 + np.random.randn(100) * 0.5

# 计算扩展R平方
result = expanding_rsquare(Expanding())(y)
# result: [1.0, 1.05, 1.05, ...]
```

### expanding_resi()

**功能**:
- 扩展残差（Expanding Resi）
- 计算回归残差：Resi = y - ŷ̂

**参数**:
- `r`: 扩展残差运算对象（Resi类实例）
- `a`: 输入数组
- 返回：扩展残差数组

**数学公式**：
```
size_t = size_t = t
x̄² = Σ(x²*size_t²)
ȳ² = Σ(y²*size_t²)
xy = Σ(x*y*size_t)
y² = Σ(y²*size_t²)
R² = xy² / √(xy² * Σ(x - x̄²)
x_mean = Σ(x) / N
y_mean = Σ(y) / N
Resi = y - (slope*t + x_mean)
```
- 其中：N为数据长度

**使用示例**：
```python
import numpy as np

# 创建价格序列
t = np.arange(1, 101)
# 添加波动
y = t * 1.0 + np.random.randn(100) * 0.5

# 计算扩展残差
result = expanding_resi(Expanding())(y)
# result: [1.0, 1.05, 1.05, ...]
```

## 类说明

### Expanding 类（抽象）

**说明**:
- 扩展运算基类
- 维护动态双端队列

**主要属性**:
- `barv`: vector队列（用于存储数据）
- `na_count`: NaN计数

**主要方法**:

```python
def __init__(self)
```
- 初始化扩展运算对象
- barv使用vector队列提高性能

```python
def update(self, val) -> float
```
- 更新队列数据
- 参数：
- val: 新数据值
- 返回：更新后的值
- 子类需实现此方法

### Mean 类

**继承关系**:
- 继承自 Expanding

**说明**:
- 扩展均值类
- 计算整个历史数据的均值
- 使用累积和方法计算

**主要方法**:

```python
def update(self, val) -> float
```
- 更新均值
- 实现细节见数学公式部分

### Slope 类

**继承关系**:
- 继承自 Expanding

**说明**:
- 扩展斜率类
- 计算整个历史数据的线性回归斜率

**主要方法**:

```python
def update(self, val) -> float
```
- 更新斜率
- 实现细节见数学公式部分

### Rsquare 类

**继承关系**:
- 继承自 Expanding

**说明**:
- 扩展R平方类
- 计算整个历史数据的R平方

**主要方法**:

```python
def update(self, val) -> float
```
- 更新R平方
- 实现细节见数学公式部分

### Resi 类

**继承关系**:
- 继承自 Expanding

**说明**:
- 扩展残差类
- 计算整个历史数据的回归残差

**主要方法**:

```python
def update(self, val) -> float
```
- 更新残差
- 实现细节见数学公式部分

## 设计模式

### 扩展模式

```
窗口大小动态增长（扩展运算）
    ↓
双端队列维护所有历史数据
    ↓
对每个新值计算并更新累加统计
    ↓
返回计算结果
```

### 更新值流程

```
barv.push_back(val)  # 新值入队尾
    ↓
更新累加统计（i_sum, x_sum等）
    ↓
更新其他统计（xy, x², y², xy²等）
    ↓
返回最终值
```

### 在线更新公式

```
# Mean更新
self.vsum += val  # 累加当前值
if isnan(val):
    self.na_count += 1  # 增加NaN计数
else:
    self.na_count -= 1  # 非减旧值
self.barv.pop_front()  # 移除旧值
```

## 性能优化

1. **Cython加速**：使用C语言编译，性能比纯Python快10-100倍
2. **vector队列**：使用collections.deque避免列表操作开销
3. **向量化操作**：使用numpy的向量化操作
4. **避免重复计算**：中间结果缓存（i_sum、x_sum、xy²、y²等）
5. **内存效率**：使用原地操作减少内存分配
6. **类型兼容**：
- 使用float32或float64类型
7. **数值稳定**：
- 处理潜在的数值溢出问题

## 注意事项

1. **线程安全**：
- 此类不是线程安全的
- 避免在多线程环境中使用
2. **NaN处理**：
- 使用isnan()检测NaN值
- 未处理的NaN值会累积到na_count中
3. **数据一致性**：
- 输入数组应与原始数据类型一致
4. **初始化顺序**：
- 初始化后队列中的数据顺序很重要
- **内存管理**：
- 大数组可能导致内存问题，及时处理

## 相关文件

- **qlib/data/ops.py**: 使用滚动/扩展运算的Python封装
- **qlib/data/_libs/rolling.pyx**: Rolling运算符
- **qlib/data/base.py**: 表达式基类
- **numpy**: 数值计算
