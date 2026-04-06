# data/ops.py 模块文档

## 文件概述

操作符模块，定义了所有数据操作的原子操作符，包括算术、比较、逻辑、引用、滚动和扩展窗口等。

## 函数列表

该模块定义了以下操作符函数：

### 基算术操作符

- `Abs(expr)` - 绝对值
- `Add(expr_left, expr_right)` - 加法
- `Sub(expr_left, expr_right)` - 减法
- `Mul(expr_left, expr_right)` - 乘法
- `Div(expr_left, expr_right)` - 除法
- `Gt(expr_left, expr_right)` - 大于
- `Lt(expr_left, expr_right)` - 小于
- `Le(expr_left, expr_right)` - 小于等于
- `Ge(expr_left, expr_right)` - 大于等于
- `Le(expr_left, expr_right)` - 大于或等于
- `Eq(expr_left, expr_right)` - 等于
- `Ne(expr_left, expr_right)` - 不等于
- `Not(expr_left, expr_right)` - 不等于
- `And(expr_left, expr_right)` - 逻辑与
- `Or(expr_left, expr_right)` - 逻辑或
- `Gt(expr_left, expr_right)` - 大于
- `Le(expr_left, expr_right)` - 小于或等于
- `Lt(expr_left, expr_right)` - 小于
- `Ge(expr_left, expr_right)` - 大于或等于
- `Ge(expr_left, expr_right)` - 大于或等于
- `Eq(expr_left, expr_right)` - 等于等于
- `Ne(expr_left, expr_right)` - 不等于
- `If(condition, expr_true, expr_false)` - 条件

### 比较操作符

- `Sign(expr)` - 取符号
- `Log(expr)` - 对数

### 元素操作符

- `Ref(expr, N)` - 引用
- `Feature(expr)` - 原始特征
- `PFeature(expr)` - PIT特征

### 滚动窗口操作符

- `Rolling(expr, N)` - 滚动窗口
- `Ref(expr, N)` - 滚动窗口引用

### 扩展窗口操作符

- `Expanding(expr, N)` - 扩展窗口

### 滚动函数符

- `Mean(expr, N)` - 均值
- `Std(expr, N)` - 标准差
- `Sum(expr, N)` - 和
- `Var(expr, N)` - 方差
- `Max(expr) | - 最大值
- `Min(expr)` - 最小值
- `IdxMax(expr)` - 最大索引
- `IdxMin(expr)` - 最小索引

### 逻辑操作符

- `If(condition, expr_true, expr_false)` - 条件
- `Not(expr)` - 逻辑非
- `And(expr_left, expr_right)` - 逻辑与
- `Or(expr_left, expr_right)` - 逻辑或
- `Mask(expr_left)` - 掩码掩

### 时间序列操作符

- `Resample(expr)` - 重采样
- `Quantile(expr, q)` - 分位数

### 条件操作符

- `ChangeInstrument(expr, feature)` - 切换交易标的

### 配置函数

- `Operators` - 操作符注册表

## 设计模式

### 表达式系统工作原理

```
用户输入表达式字符串
    ↓
解析字段字符串
    ↓
ExpressionD.get_expression_instance(field)
    ↓
    表达式实例
    ↓
    计算表达式数据
    ↓
    表达式实例.load()
    ↓
    数据加载
    ↓
    返回Series结果
```

**设计特点：**
1. **表达式惰性求值** - 只有在实际计算时才计算
2. **缓存机制** - 计算结果会自动缓存到内存
3. **多数据源支持** - 支持原始字段、PIT特征等
4. **类型安全** - 自动处理类型转换（如pd.Timestamp）
5. **窗口操作优化** - 提供Cython实现以获得最佳性能

## 使用示例

### 示例1：基本算术运算
```python
from qlib.data import D

# 获取收盘价序列
close = D.features(
    instruments=["SH600000"],
    field="$close",
    start_time="2020-01-01",
    end_time="2020-12-31",
    freq="day"
)

# 计算5日收益率
return_rate = D.expression(
    instruments=["SH600000"],
    field="$close / Ref($close, 1) - 1",
    start_time="2020-01-01",
    end_time="2020-12-31",
    freq="day"
)

# 计算20日波动率
volatility = D.expression(
    instruments=["SH600000"],
    field="Std($close, 20) / Ref($close, 1), - 1) * 100",
    start_time="2020-01-01",
    end_time="2020-12-31",
    freq="day"
)
```

### 示例2：复杂表达式组合
```python
# 计算多因子
mom_20 = D.expression(
    instruments=["SH600000"],
    field="Mean($close, 20) / Ref($close, 1))",
    start_time="2020-01-01",
    end_time="2020-12-31",
    freq="day"
)

# 条件过滤
import qlib.data.filter

config = {
    "filter_type": "ExpressionDFilter",
    "rule_expression": "$close > 50",
    "keep": False,
}

# 使用表达式过滤器获取大盘股
instruments = D.instruments("all")
filtered = config(instruments)
```

### 示例3：窗口技术指标
```python
# 计算布林带
import qlib.data import D

# 获取20日布林带
upper = D.expression(
    instruments=["SH600000"],
    field="Mean($close, 20) + 2 * Std($close, 20)",
    start_time="2020-01-01",
    end_time="2020-12-31",
    freq="day"
)

lower = D.expression(
    instruments=["SH600000"],
    field="Mean($close, 20) - 2 * Std($close, 20)",
    start_time="2020-01-01",
    end_time="2020-12-31",
    freq="day"
)

# 检算布林带宽度
width = D.expression(
    instruments=["SH600000"],
    field="Std($close, 20) + 2 * Std($close, 20)",
    start_time="2020-01-01",
    end_time="2020-12-31",
    freq="day"
)
)
```

### 示例4：PIT数据查询
```python
import qlib.data import D

# 获取季度营收数据
quarter_re = D.features(
    instruments=["SH600000"],
    field="P($pe, 4)",
    start_time="2020-01-01",
    end_time="2020-12-31",
    freq="day"
)

# 获取前5个季度的数据
quarter_re_5 = D.features(
    instruments=["SH600000"],
    field="P($pe, 5)",
    start_time="2020-01-01",
    end_time="2020-12-31",
    freq="day"
)
```

## 相关模块

- `qlib.data.base` - 表达式基类
- `qlib.data.cache` - 缓存管理
- `qlib.data.filter` - 动态过滤器
- `qlib.data.inst_processor` - 仪器处理器接口