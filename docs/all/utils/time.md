# utils/time.py 模块文档

## 文件概述
提供时间相关的工具函数，包括交易日历管理、频率处理、时间对齐等功能。

## 常量

### 时间段定义
```python
CN_TIME = [
    datetime.strptime("9:30", "%H:%M"),   # 上午开盘
    datetime.strptime("11:30", "%H:%M"),  # 上午收盘
    datetime.strptime("13:00", "%H:%M"),  # 下午开盘
    datetime.strptime("15:00", "%H:%M"),  # 下午收盘
]

US_TIME = [
    datetime.strptime("9:30", "%H:%M"),   # 开盘
    datetime.strptime("16:00", "%H:%M"),  # 收盘
]

TW_TIME = [
    datetime.strptime("9:00", "%H:%M"),   # 开盘
    datetime.strptime("13:30", "%H:%M"),  # 收盘
]
```

## 主要函数

### get_min_cal 函数
**签名：** `get_min_cal(shift: int = 0, region: str = REG_CN) -> List[time]`

**功能：** 获取日内的分钟级交易日历

**参数：**
- `shift`: 时间偏移（默认0）
  - 正值：向前偏移
  - 负值：向后偏移
- `region`: 区域（"cn"、"us"、"tw"），默认中国

**逻辑：**
```
1. 中国：上午(9:30-11:30) + 下午(13:00-15:00)
2. 台湾：上午(9:00-13:30)
3. 美国：(9:30-16:00)
4. 应用shift偏移
```

**返回：** 分钟时间列表（List[time]）

**示例：**
```python
# 获取中国所有分钟
cal = get_min_cal(region="cn")  # 240个时间点

# 偏移1分钟
cal_shifted = get_min_cal(shift=1, region="cn")
```

---

### is_single_value 函数
**签名：** `is_single_value(start_time, end_time, freq, region: str = REG_CN) -> bool`

**功能：** 判断股票市场是否只有一个数据点

**参数：**
- `start_time`: 开始时间
- `end_time`: 结束时间
- `freq`: 频率
- `region`: 区域

**判断逻辑（区域特定）：**
- **中国**:
  - 结束-开始 < 频率：单值
  - 11:29或14:59时刻：单值
- **台湾**:
  - 结束-开始 < 频率：单值
  - 13:25之后时刻：单值
- **美国**:
  - 结束-开始 < 频率：单值
  - 15:59时刻：单值

**返回：** 是否只有单个数据点

---

### Freq 类
**功能：** 频率解析和处理类

**主要属性（静态）：**
- `NORM_FREQ_MONTH = "month"`: 规范化月份频
- `NORM_FREQ_WEEK = "week"`: 规范化周频
- `NORM_FREQ_DAY = "day"`: 规范化日频
- `NORM_FREQ_MINUTE = "min"`: 规范化分钟频
- `SUPPORT_CAL_LIST`: 支持的日历频率列表

**主要方法：**

1. `__init__(freq: Union[str, "Freq"])`
   - 初始化频率对象
   - 支持字符串或Freq对象
   - 解析并存储count和base

2. `__eq__(freq) -> bool`
   - 比较频率是否相等

3. `__str__() -> str`
   - 返回频率字符串（与Qlib文件名对齐）

4. `parse(freq: str) -> Tuple[int, str]` (静态方法)
   - 解析频率字符串为统一格式
   - 支持格式：
     - "day" → (1, "day")
     - "2mon" → (2, "month")
     - "10w" → (10, "week")
     - `^([0-9]*)(month|mon|week|w|day|d|minute|min)$`
   - 返回：(数量, 规范化频率单位)

5. `get_timedelta(n: int, freq: str) -> pd.Timedelta` (静态方法)
   - 获取时间差对象
   - 例如：`get_timedelta(2, "day")` → `2days`

6. `get_min_delta(left_freq, right_freq) -> int` (静态方法)
   - 计算两个频率的分钟差值
   - 返回：左频率 - 右频率（分钟数）

7. `get_recent_freq(base_freq, freq_list) -> Optional["Freq"]` (静态方法)
   - 从频率列表获取最接近base_freq的频率
   - 返回：最接近的频率对象（仅大于0的差值）

**示例：**
```python
# 创建频率对象
freq_day = Freq("day")
freq_2week = Freq("2w")

# 解析字符串
count, base = Freq.parse("5min")  # (5, "min")

# 计算时间差
delta = Freq.get_timedelta(3, "day")  # 3days

# 比较频率
if freq_day == Freq("1d"):
    print("相同")

# 获取最近频率
freq_list = ["1min", "5min", "30min", "1h", "1d"]
recent = Freq.get_recent_freq("15min", freq_list)  # 30min
```

---

### time_to_day_index 函数
**签名：** `time_to_day_index(time_obj: Union[str, datetime], region: str = REG_CN) -> int`

**功能：** 将时间转换为日内的分钟索引

**参数：**
- `time_obj`: 时间（字符串或datetime对象）
- `region`: 区域

**逻辑：**
- 中国：9:30-11:30为0-119，13:00-15:00为120-239
- 美国：9:30-16:00为0-390
- 台湾：9:00-13:30为0-270

**返回：** 分钟索引（0-239）

---

### get_day_min_idx_range 函数
**签名：** `get_day_min_idx_range(start: str, end: str, freq: str, region: str) -> Tuple[int, int]`

**功能：** 获取日内在时间范围(闭区间)的分钟索引

**参数：**
- `start`: 开始时间（如"9:30"）
- `end`: 结束时间（如"14:30"）
- `freq`: 采样频率（如"1min"）
- `region`: 区域

**逻辑：**
1. 将时间字符串转换为time对象
2. 获取日历并按freq采样
3. 使用bisect查找start和end的索引
4. 闭区间：left用bisect_left，right用bisect_right-1

**返回：** (起始索引, 结束索引)

---

### concat_date_time 函数
**签名：** `concat_date_time(date_obj: date, time_obj: time) -> pd.Timestamp`

**功能：** 拼接日期和时间为Timestamp

**参数：**
- `date_obj`: 日期对象
- `time_obj`: 时间对象

**返回：** pd.Timestamp

---

### cal_sam_minute 函数
**签名：** `cal_sam_minute(x: pd.Timestamp, sam_minutes: int, region: str = REG_CN) -> pd.Timestamp`

**功能：** 将分钟级数据对齐到采样日历

**参数：**
- `x`: 要对齐的datetime
- `sam_minutes`: 采样分钟数（如5表示5分钟采样）
- `region`: 区域

**示例：**
- 10:38对齐到5分钟采样 → 10:35
- 10:37对齐到5分钟采样 → 10:35
- 10:40对齐到5分钟采样 → 10:40

**逻辑：**
1. 获取采样日历
2. 使用bisect找到最接近的采样点
3. 返回对齐后的时间

**返回：** 对齐后的pd.Timestamp

---

### epsilon_change 函数
**签名：** `epsilon_change(date_time: pd.Timestamp, direction: str = "backward") -> pd.Timestamp`

**功能：** 将时间改变极小量（1秒）

**参数：**
- `date_time`: 原始时间
- `direction`: 方向（"backward"或"forward"）

**用途：**
- 排除时间边界问题
- 用于区间端点处理

**返回：** 偏移后的时间

## 市场时间段

```mermaid
graph LR
    subgraph 中国
        A[9:30] --> B[11:30]
        C[13:00] --> D[15:00]
    subgraph 美国
        E[9:30] --> F[16:00]
    subgraph 台湾
        G[9:00] --> H[13:30]
```

## 频率解析流程

```mermaid
graph TD
    A[频率字符串] --> B[正则匹配]
    B --> C[提取数量]
    B --> D[提取单位]
    C --> E[转换数量为int]
    D --> F[映射到规范单位]
    E --> G[返回(count, base)]
    F --> G
```

## 时间对齐示例

```python
from qlib.utils.time import cal_sam_minute, get_min_cal
import pandas as pd

# 原始时间点
timestamp = pd.Timestamp("2020-01-01 10:38:00")

# 对齐到5分钟采样
aligned = cal_sam_minute(timestamp, sam_minutes=5, region="cn")
print(aligned)  # 2020-01-01 10:35:00

# 获取5分钟日历
cal_5min = get_min_cal(region="cn")[::5]
print(cal_5min[:5])
# [datetime.time(9, 30),
#  datetime.time(9, 35),
#  datetime.time(9, 40),
#  datetime.time(9, 45),
#  datetime.time(9, 50)]
```

## 频率比较示例

```python
from qlib.utils.time import Freq

# 创建频率
freq1 = Freq("5min")
freq2 = Freq("30min")

# 比较
if freq1 == freq2:
    print("相同")
else:
    print("不同")

# 解析
count, base = Freq.parse("2w")
print(count)  # 2
print(base)   # "week"

# 计算时间差
delta = Freq.get_min_delta("1h", "30min")
print(delta)  # 30 (60-30=30)

# 获取最近频率
freqs = ["1min", "5min", "30min", "1h", "1d"]
nearest = Freq.get_recent_freq("15min", freqs)
print(nearest)  # 30min
```

## 与其他模块的关系
- `qlib.config`: 区域配置
- `qlib.constant`: 区域常量
- `pandas`: 时间处理
