# data/pit.py 模块文档

## 文件概述

Point-in-Time (PIT)数据库支持模块，提供对齐量金融中点-in-time数据的查询和操作功能。支持季度、月度、年度等不同频率的数据存储。

## 概念说明

Qlib的PIT数据模型：
- **索引格式**：时间索引如0表示开始数据，时间索引如1表示第二天
- **数据格式**：`.bin`文件存储二进制数据
- **数据值类型**：`float32` - 特征值为32位浮点数
- **数据记录类型**：`date` - 交易日期，`period` - 季度编码如202001表示第一季度
- **时间索引**：`index` - 数据记录的时间索引位置

## 数据结构

```
financial/                                  <-- 数据库根目录
    ├── sh600000/                           <-- 股票代码目录
    │   ├── calendars/                           <-- 交易日历文件
    │   │   ├── 202001.bin                        <-- 2020Q1数据文件
    │   │   ├── feature_data/                    <-- 特征数据文件（浮点数）
    │   │   │   └── ...
    │   └── financial/                                 <-- 其他数据文件
```

## 类与函数

### P 类

**继承关系：** 无

**类说明：** Point-in-Time数据库提供者类。

#### 属性

| 属性 | 类型 | 说明 |
|------|------|------|------|
| `file_name` | str | 数据库名称 |

#### 方法

##### __init__(self, file_name)

**功能：** 初始化PIT数据库

**参数说明：**
| 参数 | 类型 | 说明 |
|------|------|-------|---| filename: str | 数据库名称，如"financial" |

**返回值：** 无

**说明：** 该类只负责数据库名称管理，实际操作由方法实现。

---

##### _get_record_type()

**功能：** 获取记录类型

**参数说明：**
| 参数 | 类型 | 说明 |
|------|-------|-------|
| 无 |

**返回值：**
| `str` - 返回PIT记录类型："date"/"period"

**说明：** 根据季度类型对应的数据记录类型。

---

##### _read_meta(file_path, record_type)

**功能：** 读取元数据

**参数说明：**
| 参数 | 类型 | 说明 |
|------|-------|-------|---| filename: file_path - str | 元数据文件完整路径 |
| record_type : str | 记录类型 |

**返回值：**
| `dict` - 元数据字典，包含date和period等信息。

**说明：** 从PIT数据文件中读取元数据。

---

##### write_meta(file_path, meta, record_type)

**功能：** 写入元数据

**参数说明：**
| 参数 | 类型 | 说明 |
|------|-------|-------|---| filename: file_path - str | 元数据文件完整路径 |
| meta : dict | 元数据字典 |
| record_type : str | 记录类型 |

**返回值：** 无

**说明：** 将元数据写入PIT数据文件。

---

##### _read_data(file_path, start_index, end_index)

**功能：** 读取数据值

**参数说明：**
| 参数 | 类型 | 说明 |
|------|-------|-------|---| filename: file_path - str | 元数据文件完整路径 |
| start_index : int | 开始索引，相对于cur_time |
| end_index : int | 结束索引，相对于cur_time |

**返回值：**
| `np.ndarray` - 数据值数组，形状为(数据量, 2)

**说明：** 读取指定索引范围的数据值，形状为(数据量, 2)。 |

---

##### _write_data(file_path, data)

**功能：** 写入数据值

**参数说明：**
| 参数 | 类型 | 说明 |
|------|-------|-------|---| filename: file_path : str | 元数据文件完整路径 |
| data : np.ndarray | 数据值数组 |

**返回值：** 无

**说明：** 将数据值写入PIT数据文件。

---

### 数据读取流程图

```
读取数据 → _read_meta() → 读取数据值 → 写入数据()
```

**示例：**
```python
from qlib.data.pit import P

# 读取季度营收数据
revenue = P.read_data(
    file_name="financial",
    record_type="date",
    start_index=0,
    end_index=4
)
# 返回值：形状为(数据量, 2)
```

## 使用场景

### 场景1：读取季度营收
```python
import qlib.data.pit as P

# 初始化PIT数据库
pit = P(file_name="financial")

# 读取2020Q1到2020Q4的营收数据
revenue = pit.read_data(
    file_name="financial",
    record_type="date",
    start_index=0,
    end_index=4,
)
print(f"营收数据形状: {revenue.shape}")
```

### 场景2：数据探索与筛选
```python
import qlib.data.pit as P

# 初始化PIT数据库
pit = P(file_name="financial")

# 读取所有时间戳
timestamps = pit.read_meta(
    file_name="financial",
    record_type="date",
)

# 过滤缺失值的时间戳
valid_timestamps = timestamps[timestamps.notna()]

# 对缺失值进行标记
pit.write_data(
    meta={"valid": True},
    record_type="date"
)

# 读取有效数据
data_values = pit.read_data(
    file_name="financial",
    start_index=0,
    end_index=len(timestamps),
    meta={"valid": True},
    record_type="date"
)

# 探索特定时间段的数据
specific_data = pit.read_data(
    file_name="financial",
    start_index=0,
    end_index=len(timestamps) // 只读取有效数据
)
```

## 设计模式

### 访问式缓存设计

**三级缓存策略：**
```
第一级：内存缓存（最快）
    ↓
数据请求 → 检查内存缓存
第二级：磁盘缓存（快速）
    ↓ P._read_data() → 数据库查询
第三级：原始数据源（最慢）
```

**数据格式：**
- `.bin` - 二进制浮点数，提供紧凑存储
- `date` - 元数据字典，包含date和period等
- 日期索引和记录类型

**索引结构：**
```
index: [0, 4, 8, 12, 16, 20, 24, 28, 32, 36]
    ↑   周度：记录类型索引位置
    ↑ 数据值数组：[数据量, 2]
  ↑ 数据值形状：[数据量, 2]
```

## 性能优化

**1. **内存映射**：** 使用 `Dict` 提供快速的时间戳查找

**2. **批量读取**：** 一次读取多个时间戳数据，提高I/O效率

**3. **索引优化**：** 预供高效的索引访问

## 与其他模块的关系

- `qlib.data.base` - 表达式基类
- `qlib.data.cache` - 缓存管理
- `qlib.data.data` - 数据访问接口
- `qlib.data.dataset` - 数据集模块