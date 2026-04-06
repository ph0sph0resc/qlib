# data/base.py 模块文档

## 文件概述

此文件定义了Qlib表达式引擎的核心基类，包括Expression、Feature、ExpressionOps等，是实现数据表达式计算的基础架构。

## 类与函数

### Expression 类

**继承关系**:
- 无直接父类
- 作为所有表达式类的基类

**主要属性**:
- 无（抽象基类）

**主要方法**:

```python
def __str__(self) -> str
```
- 返回表达式类型的类名
- 用于表达式序列化和调试

```python
def __repr__(self) -> str
```
- 返回表达式的字符串表示
- 调用`__str__`

```python
def __gt__(self, other) -> Expression
```
- 重载大于运算符 `>`
- 返回Gt表达式对象

```python
def __ge__(self, other) -> Expression
```
- 重载大于等于运算符 `>=`
- 返回Ge表达式对象

```python
def __lt__(self, other) -> Expression
```
- 重载小于运算符 `<`
- 返回Lt表达式对象

```python
def __le__(self, other) -> Expression
```
- 重载小于等于运算符 `<=`
- 返回Le表达式对象

```python
def __eq__(self, other) -> Expression
```
- 重载等于运算符 `==`
- 返回Eq表达式对象

```python
def __ne__(self, other) -> Expression
```
- 重载不等于运算符 `!=`
- 返回Ne表达式对象

```python
def __add__(self, other) -> Expression
```
- 重载加法运算符 `+`
- 返回Add表达式对象

```python
def __radd__(self, other) -> Expression
```
- 反向加法，支持 `other + expression`
- 返回Add表达式对象

```python
def __sub__(self, other) -> Expression
```
- 重载减法运算符 `-`
- 返回Sub表达式对象

```python
def __rsub__(self, other) -> Expression
```
- 反向减法，支持 `other - expression`
- 返回Sub表达式对象

```python
def __mul__(self, other) -> Expression
```
- 重载乘法运算符 `*`
- 返回Mul表达式对象

```python
def __rmul__(self, other) -> Expression
```
- 反向乘法，支持 `other * expression`
- 返回Mul表达式对象

```python
def __div__(self, other) -> Expression
```
- 重载除法运算符 `/`
- 返回Div表达式对象

```python
def __rdiv__(self, other) -> Expression
```
- 反向除法，支持 `other / expression`
- 返回Div表达式对象

```python
def __truediv__(self, other) -> Expression
```
- 重载真除法运算符 `/`（Python 3.x）
- 返回Div表达式对象

```python
def __rtruediv__(self, other) -> Expression
```
- 反向真除法
- 返回Div表达式对象

```python
def __pow__(self, other) -> Expression
```
- 重载幂运算符 `**`
- 返回Power表达式对象

```python
def __rpow__(self, other) -> Expression
```
- 反向幂运算
- 返回Power表达式对象

```python
def __and__(self, other) -> Expression
```
- 重载按位与运算符 `&`
- 返回And表达式对象

```python
def __rand__(self, other) -> Expression
```
- 反向按位与
- 返回And表达式对象

```python
def __or__(self, other) -> Expression
```
- 重载按位或运算符 `|`
- 返回Or表达式对象

```python
def __ror__(self, other) -> Expression
```
- 反向按位或
- 返回Or表达式对象

```python
def load(self, instrument, start_index, end_index, *args) -> pd.Series
```
- 加载特征/表达式数据
- 处理缓存和错误委托给`_load_internal`
- 参数：
  - instrument: 标的物代码
  - start_index: 特征起始索引（在日历中）
  - end_index: 特征结束索引
  - *args: 额外参数，可能包含freq（频率）或cur_pit、period（PIT数据）
- 返回：特征为pd.Series，索引为日历索引

```python
@abstractmethod
def _load_internal(self, instrument, start_index, end_index, *args) -> pd.Series
```
- 抽象方法：内部加载实现
- 子类必须实现此方法
- 负责具体的特征/表达式数据加载逻辑

```python
@abstractmethod
def get_longest_back_rolling(self) -> int
```
- 抽象方法：获取最长回溯窗口大小
- 返回表达式访问历史数据的最大长度
- 用于确定需要加载的数据范围

```python
@abstractmethod
def get_extended_window_size(self) -> tuple
```
- 抽象方法：获取扩展窗口大小
- 返回 (左扩展, 右扩展) 元组
- 用于确定计算表达式需要额外加载的数据范围

### Feature 类

**继承关系**:
- 继承自 Expression

**主要属性**:
- `_name`: 特征名称

**主要方法**:

```python
def __init__(self, name=None)
```
- 初始化特征对象
- 参数：
  - name: 特征名称，若为None则使用类名

```python
def __str__(self) -> str
```
- 返回特征的字符串表示，格式为 `$name`

```python
def _load_internal(self, instrument, start_index, end_index, freq) -> pd.Series
```
- 从FeatureProvider加载原始特征数据
- 调用`FeatureD.feature()`

```python
def get_longest_back_rolling(self) -> int
```
- 返回0，原始特征不需要回溯

```python
def get_extended_window_size(self) -> tuple
```
- 返回 (0, 0)，原始特征不需要扩展窗口

### PFeature 类

**继承关系**:
- 继承自 Feature

**主要方法**:

```python
def __str__(self) -> str
```
- 返回PIT特征的字符串表示，格式为 `$$name`

```python
def _load_internal(self, instrument, start_index, end_index, cur_time, period=None) -> pd.Series
```
- 从PITProvider加载PIT特征数据
- 参数：
  - cur_time: 当前观察时间（pd.Timestamp）
  - period: 可选，指定查询的期数
- 调用`PITD.period_feature()`

### ExpressionOps 类

**继承关系**:
- 继承自 Expression

**主要属性**:
- 无（抽象基类）

**主要方法**:
- 无额外定义，作为运算符表达式的基类

## 流程图

### 表达式加载流程

```
用户请求: D.features(instruments, fields)
    ↓
DatasetProvider.dataset()
    ↓
ExpressionProvider.expression()
    ↓
Expression.load(instrument, start_index, end_index, *args)
    ↓
检查内存缓存 (H["f"])
    ↓
_load_internal(instrument, start_index, end_index, *args)
    ↓
缓存结果
    ↓
返回pd.Series
```

### 表达式运算流程

```
原始特征: $close
    ↓
Ref($close, 1)
    ↓
Mean(Ref($close, 1), 5)
    ↓
完整表达式树
```

## 与其他模块的关系

### 依赖模块

- **qlib.data.data**: 提供FeatureD、CalendarD等数据访问接口
- **qlib.log**: 日志记录
- **qlib.data.ops**: 表达式运算符定义

### 被导入模块

- **ops.py**: 导入Operators，用于表达式实例化
- **pit.py**: P类和PRef类在pit.py中定义，但继承自此处基类
- **data.py**: 提供数据访问实际实现

## 设计模式

### 表达式模式

采用组合模式构建表达式树：

```
Expression (抽象基)
    ├── Feature (叶子节点)
    ├── PFeature (PIT叶子节点)
    └── ExpressionOps (中间节点)
            ├── ElemOperator (单目运算符)
            ├── PairOperator (双目运算符)
            └── Rolling (滚动运算符)
```

### 运算符重载模式

通过重载Python的魔法方法实现运算符表达式：

```python
# 用户代码
expr = $close + $open

# 内部处理
# $close + $open 实际执行为
Add(Feature("close"), Feature("open"))
```

## 使用示例

### 基础特征使用

```python
from qlib.data.base import Feature

# 创建特征
close_feature = Feature("close")
open_feature = Feature("open")

# 字符串表示
print(close_feature)  # 输出: $close
```

### 表达式运算

```python
from qlib.data.base import Feature
from qlib.data.ops import Ref, Mean
import qlib.data.ops as ops

# 构建复杂表达式
ma_5 = Mean(Ref(Feature("close"), 5)
# 等价于 ops.Mean(ops.Ref(ops.Feature("close"), 5))

print(ma_5)  # 输出表达式树
```

## 扩展点

### 创建自定义特征类

```python
from qlib.data.base import Feature

class CustomFeature(Feature):
    def __init__(self, name, custom_param):
        super().__init__(name)
        self.custom_param = custom_param

    def _load_internal(self, instrument, start_index, end_index, *args):
        # 自定义加载逻辑
        series = super()._load_internal(instrument, start_index, end_index, *args)
        # 处理特征
        return processed_series
```

### 创建自定义表达式

```python
from qlib.data.base import Expression, ExpressionOps

class CustomExpression(ExpressionOps):
    def __init__(self, feature, param):
        super().__init__()
        self.feature = feature
        self.param = param

    def _load_internal(self, instrument, start_index, end_index, *args):
        series = self.feature.load(instrument, start_index, end_index, *args)
        # 自定义运算逻辑
        return processed_series

    def get_longest_back_rolling(self):
        return self.feature.get_longest_back_rolling()

    def get_extended_window_size(self):
        return self.feature.get_extended_window_size()
```

## 注意事项

1. **缓存机制**: Expression.load()内部使用H["f"]内存缓存
2. **索引一致性**: 所有表达式使用统一的日历索引
3. **类型安全**: 运算符重载确保返回Expression类型
4. **PIT支持**: PFeature类专门处理PIT(Point-In-Time)数据
5. **错误处理**: load()方法会捕获并记录加载错误
6. **性能优化**: get_longest_back_rolling和get_extended_window_size用于优化数据加载范围

## 相关文件

- **qlib/data/ops.py**: 表达式运算符实现
- **qlib/data/data.py**: 数据提供者实现
- **qlib/data/pit.py**: PIT数据支持
- **qlib/contrib/data**: 社区贡献的数据处理器
