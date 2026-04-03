# utils/resam.py 模块文档

## 文件概述
提供时间序列数据重采样功能，支持日历重采样、特征数据重采样等操作。

## 主要函数

### resam_calendar 函数
**签名：**
```python
resam_calendar(
    calendar_raw: np.ndarray,
    freq_raw: Union[str, Freq],
    freq_sam: Union[str, Freq],
    region: str = None
) -> np.ndarray
```

**功能：** 将原始频率的日历重采样为采样频率的日历

**参数：**
- `calendar_raw`: 原始日历（np.ndarray）
- `freq_raw`: 原始频率（str或Freq对象）
- `freq_sam`: 采样频率（str或Freq对象）
- `region`: 区域（"cn"、"us"等），默认使用配置值

**假设：**
- 每天固定长度（240）的日历

**处理逻辑：**
```
1. 如果freq_sam是xminute类型：
   a. 原始频率必须是minute或min
   b. 原始频率必须高于采样频率
   c. 使用cal_sam_minute对齐分钟数据

2. 否则：
   a. 将日历转换为日级日历
   b. 根据freq_sam类型采样：
      - day: 每freq_sam.count天采样一次
      - week: 提取每周第一天，然后每freq_sam.count周采样
      - month: 提取每月第一天，然后每freq_sam.count月采样
```

**返回：** 采样后的日历（np.ndarray）

**示例：**
```python
# 从分钟日历重采样为5分钟日历
cal_5min = resam_calendar(cal_1min, "1min", "5min", region="cn")

# 从日历重采样为周历
cal_week = resam_calendar(cal_day, "day", "1w", region="cn")
```

---

### get_higher_eq_freq_feature 函数
**签名：**
```python
get_higher_eq_freq_feature(
    instruments,
    fields,
    start_time=None,
    end_time=None,
    freq="day",
    disk_cache=1
) -> (pd.DataFrame, str)
```

**功能：** 获取高于或等于指定频率的特征数据

**参数：**
- `instruments`: 标的代码
- `fields`: 特征字段
- `start_time`: 开始时间（可选）
- `end_time`: 结束时间（可选）
- `freq`: 目标频率（默认"day"）
- `disk_cache`: 是否使用磁盘缓存（默认1）

**逻辑流程：**
```
1. 尝试直接加载目标频率的特征
2. 如果失败，根据目标频率尝试：
   a. 如果目标是月/周/日频：
      - 先尝试加载日频数据
      - 失败则尝试加载分钟数据
   b. 如果目标是分钟频：
      - 加载分钟数据
```

**返回：** (特征DataFrame, 实际使用的频率)

---

### resam_ts_data 函数
**签名：**
```python
resam_ts_data(
    ts_feature: Union[pd.DataFrame, pd.Series],
    start_time: Union[str, pd.Timestamp] = None,
    end_time: Union[str, pd.Timestamp] = None,
    method: Union[str, Callable] = "last",
    method_kwargs: dict = {}
)
```

**功能：** 重采样时间序列数据

**参数：**
- `ts_feature`: 原始时间序列特征（DataFrame或Series）
- `start_time`: 开始采样时间（可选）
- `end_time`: 结束采样时间（可选）
- `method`: 采样方法（默认"last"）
  - str: SeriesGroupBy或DataFrameGroupby的属性名
  - callable: 自定义函数
  - None: 不进行操作
- `method_kwargs`: 方法参数（默认空字典）

**处理方式：**

**方式1：MultiIndex[instrument, datetime]**
```python
# 对每个标的的数据应用method
result = resam_ts_data(
    feature,
    start_time="2010-01-04",
    end_time="2010-01-05",
    method="last"
)
```

**方式2：Index[datetime]**
```python
# 直接对数据应用method
result = resam_ts_data(
    feature,
    start_time="2010-01-04",
    end_time="2010-01-05",
    method="last"
)
```

**method参数类型：**
1. **字符串：** pandas方法名
   - "last": 取最后一个值
   - "first": 取第一个值
   - "mean": 计算平均值
   - "sum": 计算总和
2. **函数：** 自定义聚合函数
   - 需要接受Series或DataFrame并返回标量或Series

**返回：** 重采样后的数据（DataFrame/Series/标量），空数据返回None

---

### get_valid_value 函数
**签名：** `get_valid_value(series, last=True) -> float`

**功能：** 获取Series中第一个或最后一个非NaN值

**参数：**
- `series`: pd.Series（不能为空）
- `last`: 是否获取最后一个有效值（默认True）

**逻辑：**
- `last=True`: `series.ffill().iloc[-1]`
- `last=False`: `series.bfill().iloc[0]`

**返回：** 非NaN值或NaN

---

### _ts_data_valid 函数
**签名：** `_ts_data_valid(ts_feature, last=False)`

**功能：** 获取Series/DataFrame中第一个或最后一个非NaN值

**参数：**
- `ts_feature`: Series或DataFrame
- `last`: 是否获取最后一个有效值（默认False）

**逻辑：**
- 如果是DataFrame：对每列应用get_valid_value
- 如果是Series：直接应用get_valid_value
- 其他类型：抛出TypeError

---

### ts_data_last 函数
**签名：** (partial包装)

**功能：** 获取最后一个非NaN值（部分应用）

**等价于：** `_ts_data_valid(ts_feature, last=True)`

---

### ts_data_first 函数
**签名：** (partial包装)

**功能：** 获取第一个非NaN值（部分应用）

**等价于：** `_ts_data_valid(ts_feature, last=False)`

## 重采样流程

```mermaid
graph TD
    A[原始日历] --> B{freq_sam类型?}
    B -->|xminute| C[对齐分钟数据]
    B -->|day/week/month| D[转换为日级]
    C --> E[返回采样日历]
    D --> F[提取首日]
    F --> G{目标频率?}
    G -->|day| H[按天数采样]
    G -->'week| I[提取周首]
    I --> J[按周数采样]
    G -->'month| K[提取月首]
    K --> L[按月数采样]
    H --> E
    J --> E
    L --> E
```

## 时间序列重采样流程

```mermaid
graph TD
    A[原始特征] --> B[选择时间范围]
    B --> C{索引类型?}
    C -->|MultiIndex| D[按标的分组]
    C -->'SingleIndex| E[直接应用]
    D --> F[应用method]
    E --> F
    F --> G[返回结果]
```

## 使用示例

### 日历重采样
```python
from qlib.utils.resam import resam_calendar
import numpy as np

# 原始1分钟日历
cal_1min = np.array([...])  # 240个时间点/天

# 重采样为5分钟
cal_5min = resam_calendar(cal_1min, "1min", "5min", region="cn")

# 重采样为日频
cal_day = resam_calendar(cal_1min, "1min", "1d", region="cn")
```

### 特征重采样
```python
from qlib.utils.resam import resam_ts_data

# 多索引数据
feature = df  # Index: MultiIndex[instrument, datetime]

# 按日期范围重采样
result = resam_ts_data(
    feature,
    start_time="2020-01-01",
    end_time="2020-12-31",
    method="mean"
)

# 使用自定义函数
def custom_agg(x):
    return x.mean() * 2

result = resam_ts_data(
    feature,
    start_time="2020-01-01",
    end_time="2020-01-31",
    method=custom_agg
)
```

### 获取有效值
```python
from qlib.utils.resam import ts_data_last, ts_data_first

# 获取最后一个非NaN值
last_val = ts_data_last(series)

# 获取第一个非NaN值
first_val = ts_data_first(series)
```

## 与其他模块的关系
- `qlib.data`: 数据访问
- `qlib.utils.time`: 频率处理
- `qlib.config`: 配置管理
