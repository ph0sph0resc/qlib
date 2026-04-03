# contrib.data.utils

**文件路径**: `qlib/contrib/data/utils/__init__.py`

## 模块概述

该模块提供了数据处理的辅助工具，主要用于优化DataFrame的内存使用和性能。

**核心组件**:
- `align_index`: 对齐多个DataFrame的索引
- `SepDataFrame`: 分离式DataFrame，避免不必要的拼接和拆分

## 函数定义

### `align_index(df_dict, join)`

**功能**: 对齐多个DataFrame的索引

**参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| df_dict | dict | DataFrame字典 |
| join | str | 用于对齐的键名 |

**返回值**:
- `dict` - 对齐后的DataFrame字典

**说明**:
1. 遍历字典中的所有DataFrame
2. 对于非join键的DataFrame，使用join键对应的索引进行reindex
3. 返回对齐后的字典

**示例**:
```python
df1 = pd.DataFrame({"A": [1, 2, 3]}, index=[0, 1, 2])
df2 = pd.DataFrame({"B": [4, 5]}, index=[0, 1])

# 对齐索引
aligned = align_index({"df1": df1, "df2": df2}, join="df1")
# df2现在索引为[0, 1, 2]，填充NaN
```

## 类定义

### `SepDataFrame`

**说明**: 分离式DataFrame（Mock DataFrame类）

**设计理念**:
通常我们会拼接多个DataFrame一起处理（如特征、标签、权重、过滤器）。但是最后它们通常会被分开使用。这会导致拼接和拆分数据的额外成本（重塑和内存复制非常昂贵）。

SepDataFrame尝试表现得像一个列具有多级索引的DataFrame，但实际上保持数据分离。

#### 构造方法

```python
__init__(self, df_dict: Dict[str, pd.DataFrame], join: str, skip_align=False)
```

**功能**: 初始化分离式DataFrame

**参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| df_dict | Dict[str, pd.DataFrame] | DataFrame字典 |
| join | str | 数据拼接方式 |
| skip_align | bool | 是否跳过索引对齐（某些情况下可提高性能）|

**说明**:
- 如果skip_align=False，使用align_index对齐所有DataFrame的索引
- join键指定了用于对齐的基准DataFrame

---

#### 属性

##### `loc`

**类型**: `SDFLoc` 属性

**功能**: 返回位置索引对象

**说明**: 提供类似pandas DataFrame的loc索引访问。

##### `index`

**类型**: `pd.Index` 属性

**功能**: 返回join键对应的索引

**说明**: 返回基准DataFrame的索引。

---

#### 方法

##### `apply_each(method: str, skip_align=True, *args, **kwargs)`

**功能**: 对每个DataFrame应用方法

**参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| method | str | 方法名 |
| skip_align | bool | 是否跳过索引对齐 |
| *args | any | 位置参数 |
| **kwargs | dict | 关键字参数 |

**返回值**:
- `SepDataFrame` 或 `None` - 应用方法后的对象

**说明**:
- 假设：inplace方法返回None
- 对每个DataFrame应用指定的方法
- 如果所有方法都返回None（inplace操作），返回None
- 否则返回新的SepDataFrame

**示例**:
```python
sdf = SepDataFrame({"f1": df1, "f2": df2}, join="f1")

# 应用dropna
cleaned_sdf = sdf.apply_each("dropna")

# inplace操作
sdf.apply_each("fillna", 0, skip_align=True)  # 返回None
```

##### `sort_index(*args, **kwargs)`

**功能**: 对每个DataFrame排序索引

**参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| *args | any | sort_index的位置参数 |
| **kwargs | dict | sort_index的关键字参数 |

**返回值**:
- `SepDataFrame` - 排序后的对象

**说明**: 应用sort_index方法到所有DataFrame，返回新的SepDataFrame。

##### `copy(*args, **kwargs)`

**功能**: 复制每个DataFrame

**参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| *args | any | copy的位置参数 |
| **kwargs | dict | copy的关键字参数 |

**返回值**:
- `SepDataFrame` - 复制后的对象

**说明**: 应用copy方法到所有DataFrame，返回新的SepDataFrame。

##### `_update_join()`

**功能**: 更新join键

**说明**:
- 如果join键不在字典中，更新为第一个键
- 如果字典为空，设置join为None

##### `__getitem__(item)`

**功能**: 获取指定键的DataFrame

**参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| item | str | 键名 |

**返回值**:
- `pd.DataFrame` - 指定键的DataFrame

##### `__setitem__(item: str, df: Union[pd.DataFrame, pd.Series])`

**功能**: 设置指定键的DataFrame

**参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| item | str/tuple | 键名 |
| df | pd.DataFrame/pd.Series | 要设置的DataFrame或Series |

**说明**:
- 支持简单的键名设置
- 支持元组形式的MultiIndex键

## 使用示例

### 基本使用

```python
from qlib.contrib.data.utils.sepdf import SepDataFrame
import pandas as pd

# 创建多个DataFrame
feature_df = pd.DataFrame({"f1": [1, 2, 3]})
label_df = pd.DataFrame({"l1": [4, 5, 6]})

# 创建分离式DataFrame
sdf = SepDataFrame(
    df_dict={"feature": feature_df, "label": label_df},
    join="feature"
)

# 访问数据
features = sdf["feature"]
labels = sdf["label"]

# 使用loc索引
sliced = sdf.loc[0:2]
```

### 应用方法

```python
# 对所有DataFrame应用dropna
cleaned = sdf.apply_each("dropna")

# 排序索引
sorted_sdf = sdf.sort_index()

# 复制
copied = sdf.copy()

# inplace操作
sdf.apply_each("fillna", 0, skip_align=True)
```

### 性能对比

```python
import pandas as pd
import time
from qlib.contrib.data.utils.sepdf import SepDataFrame

# 创建大数据
df1 = pd.DataFrame({f"f{i}": np.random.randn(10000) for i in range(10)})
df2 = pd.DataFrame({f"l{i}": np.random.randn(10000) for i in range(5)})

# 传统方式：拼接
start = time.time()
combined = pd.concat([df1, df2], axis=1)
# ... 处理
result1, result2 = combined.iloc[:, :10], combined.iloc[:, 10:]
print(f"Concat方式: {time.time() - start:.3f}s")

# SepDataFrame方式
start = time.time()
sdf = SepDataFrame({"df1": df1, "df2": df2}, join="df1")
# ... 处理
result1, result2 = sdf["df1"], sdf["df2"]
print(f"SepDataFrame方式: {time.time() - start:.3f}s")
```

## 数据流程对比

```mermaid
graph TD
    subgraph "传统方式"
        A1[多个DataFrame] --> B1[pd.concat]
        B1 --> C1[处理数据]
        C1 --> D1[拆分数据]
        D1 --> E1[使用分离数据]
    end

    subgraph "SepDataFrame方式"
        A2[多个DataFrame] --> B2[SepDataFrame]
        B2 --> C2[处理数据]
        C2 --> D2[直接访问]
        D2 --> E2[使用分离数据]
    end
```

## 性能优势

| 场景 | 传统方式 | SepDataFrame |
|--------|----------|--------------|
| 内存使用 | 拼接时复制 | 无额外复制 |
| CPU使用 | 拆分时复制 | 直接访问 |
| 代码简洁 | 需要管理索引 | 类似DataFrame API |
| 灵活性 | 较好 | 较差（限制操作） |

## 注意事项

1. **不完整实现**: 文档指出SepDataFrame不完全等同于pandas DataFrame
2. **贡献欢迎**: 欢迎贡献完善SepDataFrame的DataFrame-like行为
3. **MultiIndex支持**: 当前MultiIndex支持有限
4. **join行为**: 设置新DataFrame时，join行为可能需要调整
5. **性能权衡**: 在少量数据时，传统方式可能更快

## 相关模块

- `pandas.DataFrame` - 模仿的基类
- `qlib.data.dataset` - 数据集模块
- `qlib.data.dataset.handler` - 数据处理器

## 未来改进

根据代码中的TODO注释：

1. **完善DataFrame API**: 使SepDataFrame更接近pandas DataFrame的行为
2. **MultiIndex处理**: 改进MultiIndex列名的处理
3. **join行为优化**: 完善设置新DataFrame时的join键行为
