# data/__init__.py 模块文档

## 文件概述

这是data模块的入口文件，负责导出所有Provider和缓存类。它提供了Qlib数据访问的统一接口。

## 导出的类和函数

### D 类 - 全局数据访问入口

**说明：** D是Qlib的全局数据访问入口类，通过门面模式提供统一的数据访问接口。

**导出内容：**
- `D.calendar(...)` - 交易日历访问
- `D.instruments(...)` - 股票池访问
- `D.features(...)` - 特征数据获取
- `D.list(...)` - 列出股票信息

## Provider类

### CalendarProvider - 交易日历提供者

**继承关系：** 无

**类说明：** 交易日历提供者的基类，定义获取交易日历的接口。

#### 方法

##### calendar(start_time=None, end_time=None, freq="day", future=False)

**功能：** 获取交易日历

**参数说明：**
| 参数 | 类型 | 说明 |
|------|------|------|
| start_time | str | 开始时间，格式如"2010-01-01" |
| end_time | str | 结束时间，格式如"2020-12-31" |
| freq | str | 数据频率："day"/"week"/"month"/"year" |
| future | bool | 是否包含未来交易日，默认False |

**返回值：**
- `List[pd.Timestamp]` - 交易日历列表

**示例：**
```python
from qlib.data import D

# 获取2020年所有交易日
calendar = D.calendar("2020-01-01", "2020-12-31", freq="day")

# 获取未来交易日
future_calendar = D.calendar("2025-01-01", future=True)
```

---

##### locate_index(start_time, end_time, freq="day", future=False)

**功能：** 定位时间索引

**参数说明：**
| 参数 | 类型 | 说明 |
|------|------|------|
| start_time | pd.Timestamp/str | 开始时间 |
| end_time | pd.Timestamp/str | 结束时间 |
| freq | str | 数据频率 |
| future | bool | 是否包含未来 |

**返回值：**
- `Tuple[pd.Timestamp, pd.Timestamp, int, int]` - (实际开始时间, 实际结束时间, 开始索引, 结束索引)

**示例：**
```python
start_index, end_index = D.locate_index("2020-01-01", "2020-12-31", freq="day")
```

---

##### _get_calendar(freq, future)

**功能：** 加载交易日历数据（内部方法）

**参数说明：**
| 参数 | 类型 | 说明 |
|------|------|------|
| freq | str | 数据频率 |
| future | bool | 是否包含未来 |

**返回值：**
- `List[pd.Timestamp]` - 交易日历列表

**说明：**** 该方法从文件系统加载交易日历数据，并存储到内存缓存中。

---

##### load_calendar(freq, future)

**功能：** 交易日历加载器（抽象方法）

**参数说明：**
| 参数 | 类型 | 说明 |
|------|------|------|
| freq | str | 数据频率 |
| future | bool | 是否包含未来 |

**返回值：**
- `List[pd.Timestamp]` - 交易日历列表

**说明：**** 子类需要实现此方法来从数据源加载交易日历。

---

##### _uri(start_time, end_time, freq, future=False)

**功能：** 生成URI（内部方法）

**返回值：** `str` - URI字符串

---

### InstrumentProvider - 股票池提供

**继承关系：** 无

**类说明：** 股票池提供者的基类，定义获取股票池的接口。

#### 方法

##### instruments(market="all", filter_pipe=None, as_list=False)

**功能：** 获取股票池配置

**参数说明：**
| 参数 | 类型 | 说明 |
|------|------|------|
| market | str/list | 市场名称或代码列表 |
| filter_pipe | list | 动态过滤器列表 |
| as_list | bool | 是否返回列表 |

**返回值：**
- `dict` - 股票池配置字典

**示例：**
```python
# 获取沪深300股票池
instruments = D.instruments("csi300")

# 使用过滤器
instruments = D.instruments(
    market="csi500",
    filter_pipe=[
        {
            "filter_type": "ExpressionDFilter",
            "rule_expression": "$close > 50",
        "filter_start_time": None,
            "filter_end_time": None,
        "keep": False,
        }
    ]
)
)
```

---

##### list_instruments(instruments, start_time=None, end_time=None, freq="day", as_list=False)

**功能：** 列出股票列表

**参数说明：**
| 参数 | 类型 | 说明 |
|------|------|------|
| instruments | dict/list | 股票池配置 |
| start_time | str | 开始时间 |
| end_time | str | 结束时间 |
| freq | str | 数据频率 |
| as_list | bool | 返回列表或字典 |

**返回值：**
- `dict/list` | 股票列表或股票时间范围字典

**示例：**
```python
# 列出股票列表
stocks = D.list_instruments(instruments, start_time="2020-01-01", end_time="2020-12-31")
```

---

##### get_inst_type(inst)

**功能：** 获取股票池类型

**参数说明：**
| 参数 | 类型 | 说明 |
|------|------|------|
| inst | any | 股票池配置 |

**返回值：**
- `str` - "LIST"/"DICT"

**返回值说明：**
- "LIST" - 列表形式
- "DICT" - 字典形式
- 也可以是列表/tuple/pd.Index对象

---

##### _uri(instruments, start_time=None, end_time=None, freq="day", as_list=False)

**功能：** 生成URI（内部方法）

**返回值：** `str` - URI字符串

---

### FeatureProvider - 特征数据提供者

**继承关系：** 无

**类说明：** 特征数据提供者的基类，定义获取原始特征数据的接口。

#### 方法

##### feature(instrument, field, start_time, end_time, freq="day")

**功能：** 获取单个特征

**参数说明：**
| 参数 | 类型 | 说明 |
|------|------|------|
| instrument | str | 股票代码 |
| field | str | 特征字段名 |
| start_time | str | 开始时间 |
| end_time | str | 结束时间 |
| freq | str | 数据频率 |

**返回值：**
- `pd.Series` - 特征值序列，索引为日期时间

**示例：**
```python
# 获取收盘价
close = D.features(
    instruments=["SH600000"],
    field="$close",
    start_time="2020-01-01",
    end_time="2020-01-10"
)

# 获取成交量
volume = D.features(
    instruments=["SH600000"],
    field="$volume",
    start_time="2020-01-01",
    end_time="2020-01-10"
)
```

---

### PITProvider - 时点数据提供者

**继承关系：** 无

**类说明：** 时点数据提供者的基类，支持Point-in-Time(PIT)数据库。

#### 方法

##### period_feature(instrument, field, start_index, end_index, cur_time, period=None)

**功能：** 获取时点特征

**参数说明：**
| 参数 | 类型 | 说明 |
|------|------|------|
| instrument | str | 股票代码 |
| field | str | 特征字段名 |
| start_index | int | 开始索引，相对于cur_time |
| end_index | int | 结束索引，相对于cur_time |
| cur_time | pd.Timestamp | 当前时间点 |
| period | int | 周期数编号 |

**返回值：**
- `pd.Series` - 时点特征值序列，索引为整数

**示例：**
```python
# 获取前5个季度的营收
pe = D.period_feature(
    instrument="SH600000",
    field="pe",
    start_index=0,
    end_index=4,
    cur_time="2020-12-31",
    period=4
)

# 返回2020Q1的营收
```

---

### ExpressionProvider - 表达式数据提供者

**继承关系：** 无

**类说明：** 表达式数据提供者的基类，支持复杂的表达式计算。

#### 方法

##### get_expression_instance(field)

**功能：** 获取表达式实例

**参数说明：**
| 参数 | 类型 | 说明 |
|------|------|------|
| field | str | 特征字段字符串 |

**返回值：**
- `Expression` - 表达式实例

**说明：** 解析字段字符串并返回对应的表达式对象。

---

##### expression(instrument, field, start_time=None, end_time=None, freq="day")

**功能：** 计算表达式数据

**参数说明：**
| 参数 | 类型 | 说明 |
|------|------|------|
| instrument | str | 股票代码 |
| field | str | 表达式字符串 |
| start_time | str | 开始时间 |
| end_time | str | 结束时间 |
| freq | str | 数据频率 |

**返回值：**
- `pd.Series` - 表达式计算结果，索引为日期时间

**示例：**
```python
# 计算收益率
return_rate = D.expression(
    instrument="SH600000",
    field="$close / Ref($close, 1) - 1",
    start_time="2020-01-01",
    end_time="2020-12-31",
    freq="day"
)

# 计算移动平均
ma_20 = D.expression(
    instrument="SH600000",
    field="Mean($close, 20)",
    start_time="2020-01-01",
    end_time="2020-12-31",
    freq="day"
)
```

---

### DatasetProvider - 数据集提供者

**继承关系：** 无

**类说明：** 数据集提供者的基类，定义获取批量特征数据的接口。

#### 方法

##### dataset(instruments, fields, start_time=None, end_time=None, freq="day", inst_processors=[])

**功能：** 获取批量特征数据

**参数说明：**
| 参数 | 类型 | 说明 |
|------|------|------|
| instruments | list/dict | 股票列表或股票池配置 |
| fields | list | 特征字段列表 |
| start_time | str | 开始时间 |
| end_time | str | 结束时间 |
| freq | str | 数据频率 |
| inst_processors | list | 数据处理器列表 |

**返回值：**
- `pd.DataFrame` - 特征数据框，索引为(股票代码, 日期时间)

**示例：**
```python
# 获取多个特征
features = D.dataset(
    instruments=["SH600000", "SH600001"],
    fields=["$close", "$volume"],
    start_time="2020-01-01",
    end_time="2020-12-31",
    freq="day"
)
```

---

##### _uri(instruments, fields, start_time, end_time, freq, disk_cache=1, inst_processors=[])

**功能：** 生成数据集URI（内部方法）

**返回值：** `str` - URI字符串

---

## 缓存类

### ExpressionCache - 表达式缓存基类

**继承关系：** 无

**类说明：** 表达式缓存机制的基类，允许用户自定义表达式缓存。

**主要方法：**
- `expression(instrument, field, start_time, end_time, freq)` - 获取表达式数据
- `_uri(instrument, field, start_time, end_time, freq)` - 获取缓存文件URI
- `update(cache_uri, freq)` - 更新表达式缓存

### DatasetCache - 数据集缓存基类

**继承关系：** 无

**类说明：** 数据集缓存机制的基类，允许用户自定义数据集缓存。

**主要方法：**
- `dataset(...)` - 获取数据集数据
- `update(cache_uri, freq)` - 更新数据集缓存

**实现类：**
- `DiskExpressionCache` - 磁盘表达式缓存（服务器端）
- `DiskDatasetCache` - 磁盘数据集缓存（服务器端）
- `SimpleDatasetCache` - 简单数据集缓存（客户端本地）
- `DatasetURICache` - 数据集URI缓存（客户端）

### CalendarCache - 交易日历缓存

**继承关系：** 无

**类说明：** 交易日历缓存基类

**实现类：**
- `MemoryCalendarCache` - 内存交易日历缓存

### MemCache - 内存缓存单元

**继承关系：** 无

**类说明：** 内存缓存单元的基类，支持大小限制。

**实现类：**
- `MemCacheLengthUnit` - 按数量限缓存单元
- `MemCacheSizeofUnit` - 按大小限缓存单元

## 相关模块

- `qlib.data.base` - 表达式基类和运算符
- `qlib.data.cache` - 缓存管理
- `qlib.data.client` - WebSocket客户端
- `qlib.data.filter` - 动态过滤器
- `qlib.data.inst_processor` - 数据处理器
- `qlib.data.pit` - 时点数据
- `qlib.data.storage` - 存储接口

## 使用示例

```python
import qlib
from qlib.data import D

# 获取交易日历
calendar = D.calendar("2020-01-01", "2020-12-31")

# 获取股票池
instruments = D.instruments("csi500")

# 获取特征数据
features = D.features(
    instruments=instruments,
    fields=["$close", "$volume", "Ref($close, 1)"],
    start_time="2020-01-01",
    end_time="2020-12-31"
)

# 计算复杂表达式
ma_20 = D.expression(
    instrument="SH600000",
    field="Mean($close, 20)"
)
```
