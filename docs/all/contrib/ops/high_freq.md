# qlib.contrib.ops.high_freq

## 模块概述

`qlib.contrib.ops.high_freq` 模块提供了一系列用于高频数据处理的操作符。这些操作符主要用于处理分钟级的高频金融数据，支持日内累计、空值填充、数据切片等操作。

所有操作符都继承自 Qlib 的 `ElemOperator` 或 `PairOperator`，可以无缝集成到 Qlib 的表达式中。

---

## 函数说明

### get_calendar_day

使用内存缓存加载高频日历日期。

**参数：**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| freq | str | 否 | "1min" | 读取日历文件的频率 |
| future | bool | 否 | False | 是否包含未来交易日 |

**返回值：**
- `_calendar` - 日期数组

**注意事项：**
- 加载日历操作较慢，建议在多进程启动前预先加载

---

### get_calendar_minute

使用内存缓存加载高频分钟日历。

**参数：**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| freq | str | 否 | "day" | 读取日历文件的频率 |
| future | bool | 否 | False | 是否包含未来交易日 |

**返回值：**
- `_calendar` - 分钟级别日历数组

---

## 类说明

### DayCumsum

日内累计操作符，在指定时间范围内对特征值进行累计。

#### 构造方法参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| feature | Expression | 是 | - | 特征实例 |
| start | str | 否 | "9:30" | 交易时段开始时间 |
| end | str | 否 | "14:59" | 交易时段结束时间 |
| data_granularity | int | 否 | 1 | 数据粒度（分钟数） |

#### 时间说明

- **"9:30"** 表示时间区间 (9:30, 9:31) 在交易中
- **"14:59"** 表示时间区间 (14:59, 15:00) 在交易中，但 (15:00, 15:01) 不在交易中
- `start="9:30"` 和 `end="14:59"` 表示全天交易

#### 返回值

返回一个序列，每个值等于在 `start` 到 `end` 时间范围内的累计值，超出该范围的值为零。

#### 使用示例

```python
from qlib.contrib.ops.high_freq import DayCumsum
from qlib.data.ops import Ref

# 创建日内累计特征，从 9:30 到 14:59 累计成交额
day_volume = DayCumsum(
    feature=Ref("$volume", 1),
    start="9:30",
    end="14:59",
    data_granularity=1
)
```

---

### DayLast

日内最后值操作符。

#### 构造方法参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| feature | Expression | 是 | - | 特征实例 |

#### 返回值

返回一个序列，每个值等于该日的最后一个值。

#### 使用示例

```python
from qlib.contrib.ops.high_freq import DayLast

# 获取每日收盘价
daily_close = DayLast(feature=Ref("$close", 0))
```

---

### FFillNan

前向填充空值操作符。

#### 构造方法参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| feature=Ref("$close", 0) | Expression | 是 | - | 特征实例 |

#### 返回值

返回前向填充空值后的特征序列。

#### 使用示例

```python
from qlib.contrib.ops.high_freq import FFillNan

# 前向填充收盘价的空值
filled_close = FFillNan(feature=Ref("$close", 0))
```

---

### BFillNan

后向填充空值操作符。

#### 构造方法参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| feature | Expression | 是 | - | 特征实例 |

#### 返回值

返回后向填充空值后的特征序列。

#### 使用示例

```python
from qlib.contrib.ops.high_freq import BFillNan

# 后向填充收盘价的空值
filled_close = BFillNan(feature=Ref("$close", 0))
```

---

### Date

日期操作符，提取特征对应的日期。

#### 构造方法参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| feature | Expression | 是 | - | 特征实例 |

#### 返回值

返回一个序列，每个值是对应的日期。

#### 使用示例

```python
from qlib.contrib.ops.high_freq import Date

# 提取收盘价对应的日期
date_series = Date(feature=Ref("$close", 0))
```

---

### Select

条件选择操作符。

#### 构造方法参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| feature_left | Expression | 是 | - | 选择条件 |
| feature_right | Expression | 是 | - | 选择值 |

#### 返回值

返回满足条件（`feature_left`）的值（`feature_right`）。

#### 使用示例

```python
from qlib.contrib.ops.high_freq import Select

# 当成交量大于 0 时选择收盘价
selected_price = Select(
    feature_left=Ref("$volume", 0) > 0,
    feature_right=Ref("$close", 0)
)
```

---

### IsNull

判断是否为空值操作符。

#### 构造方法参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| feature | Expression | 是 | - | 特征实例 |

#### 返回值

返回一个布尔序列，指示特征是否为空值。

#### 使用示例

```python
from qlib.contrib.ops.high_freq import IsNull

# 检测收盘价是否存在空值
null_mask = IsNull(feature=Ref("$close", 0))
```

---

### IsInf

判断是否为无穷值操作符。

#### 构造方法参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| feature | Expression | 是 | - | 特征实例 |

#### 返回值

返回一个布尔序列，指示特征是否为无穷值。

#### 使用示例

```python
from qlib.contrib.ops.high_freq import IsInf

# 检测收益率是否存在无穷值
inf_mask = IsInf(feature=returns)
```

---

### Cut

数据切片操作符，删除指定数量的首尾元素。

#### 构造方法参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| feature | Expression | 是 | - | 特征实例 |
| left | int | 否 | None | 删除前 l 个元素（l > 0，None 表示 0） |
| right | int | 否 | None | 删除后 -r 个元素（r < 0，None 表示 0） |

#### 约束条件

- `left > 0`（如果提供）
- `right < 0`（如果提供）

#### 返回值

返回删除了指定首尾元素后的序列。注意：从原始数据删除，不是切片数据。

#### 使用示例

```python
from qlib.contrib.ops.high_freq import Cut

# 删除前 5 个元素和后 10 个元素
cut_feature = Cut(
    feature=Ref("$close", 0),
    left=5,
    right=-10
)
```

---

## 完整使用示例

```python
import qlib
from qlib.data import D
from qlib.contrib.ops.high_freq import DayCumsum, DayLast, FFillNan, Date, Select, IsNull

# 初始化 Qlib
qlib.init(provider_uri="~/.qlib/qlib_data/cn_data", region="cn")

# 定义高频数据表达式
instruments = ["SH600000"]
fields = {
    # 日内累计成交量
    "day_volume": DayCumsum(Ref("$volume", 1), "9:30", "14:59"),
    # 每日收盘价
    "daily_close": DayLast(Ref("$close", 0)()),
    # 前向填充空值的收盘价
    "filled_close": FFillNan(Ref("$close", 0)),
    # 提取日期
    "date": Date(Ref("$close", 0)),
    # 条件选择：成交量大于 0 时的收盘价
    "selected_close": Select(Ref("$volume", 0) > 0, Ref("$close", 0)),
}

# 加载数据
df = D.features(instruments, fields, freq="1min")
print(df.head())
```

---

## 注意事项

1. **日历缓存**：`get_calendar_day` 和 `get_calendar_minute` 使用内存缓存提高性能
2. **时间粒度**：`data_granularity` 必须能整除 240（全天分钟数）
3. **时区假设**：默认使用中国股市交易时间
4. **性能优化**：建议在多进程启动前预先加载日历数据
