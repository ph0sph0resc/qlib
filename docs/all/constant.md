# constant.py 模块文档

## 文件概述
定义Qlib使用的常量，包括区域标识、数值常量和类型提示。

## 区域常量

### 区域标识
```python
REG_CN = "cn"    # 中国市场
REG_US = "us"    # 美国市场
REG_TW = "tw"    # 台湾市场
```

**用途：**
- 指定数据区域
- 配置交易日历
- 设置交易规则

## 数值常量

```python
EPS = 1e-12               # 避免除零的小量（机器学习epsilon）
INF = int(1e18)           # 无穷大整数
ONE_DAY = pd.Timedelta("1day")   # 一天的时间差
ONE_MIN = pd.Timedelta("1min")   # 一分钟的时间差
EPS_T = pd.Timedelta("1s")      # 一秒的时间差（用于右区间端点排除）
```

**用途说明：**

1. **EPS = 1e-12**
   - 用于机器学习数值稳定性
   - 避免除零的除法错误
   - 示例：`(x1 - x2) / (abs(x1) + EPS)`

2. **INF = int(1e18)**
   - 表示无穷大的整数
   - 用于数值比较和优化
   - 远大于实际可能的股票价格或数量

3. **ONE_DAY**
   - 标准化一天的时间差
   - 用于日期计算和滑动窗口

4. **ONE_MIN**
   - 标准化一分钟的时间差
   - 用于分钟级数据处理

5. **EPS_T = 1s**
   - 时间维度的小量
   - 用于时间区间端点处理
   - 确保右区间端点被正确排除

## 类型提示

```python
float_or_ndarray = TypeVar("float_or_ndarray", float, np.ndarray)
```

**功能：** 类型变量，表示可以是float或np.ndarray

**用途：**
- 类型注解
- 泛型函数定义

**示例：**
```python
from typing import Union
from qlib.constant import float_or_ndarray

def my_func(value: float_or_ndarray) -> float_or_ndarray:
    return value * 2
```

## 使用示例

### 区域选择
```python
from qlib.constant import REG_CN, REG_US, REG_TW

# 中国市场
region = REG_CN

# 美国市场
region = REG_US

# 台湾市场
region = REG_TW
```

### 数值使用
```python
from qlib.constant import EPS, INF, ONE_DAY

# 防免除零
result = (value1 - value2) / (abs(value2) + EPS)

# 无穷大数
max_value = INF

# 日期计算
next_date = current_date + ONE_DAY
```

### 时间区间处理
```python
from qlib.constant import EPS_T

# 排除右端点
end_time_inclusive = end_time - EPS_T
```

## 与其他模块的关系
- `pandas`: 时间差（pd.Timedelta）
- `numpy`: 数值常量（np.ndarray）
- `typing`: 类型提示

## 注意事项

1. **区域常量**
   - 不要硬编码区域字符串
   - 始终使用这些常量

2. **数精度**
   - EPS对于浮点计算足够小
   - INF足够大以表示实际无穷

3. **时间差**
   - 使用ONE_DAY和ONE_MIN进行标准化
   - 避免直接使用数字（如86400秒）
