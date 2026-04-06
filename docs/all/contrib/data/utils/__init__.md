# qlib.contrib.data.utils 模块

## 模块概述

`qlib.contrib.data.utils` 模块提供了一些数据处理的工具类和函数，特别是用于优化数据处理性能的工具。该模块主要包括：

- `SepDataFrame`：分离式数据框类，用于避免多个数据框拼接和分离的性能开销
- `SDFLoc`：`SepDataFrame` 的定位器类
- `align_index()`：对齐索引的辅助函数

## 核心类和函数

### 1. SepDataFrame 类

```python
class SepDataFrame:
    def __init__(self, df_dict: Dict[str, pd.DataFrame], join: str, skip_align=False)
```

**功能说明**：
分离式数据框（Separate DataFrame）。通常我们会将多个数据框拼接在一起进行处理（如特征、标签、权重、过滤器）。然而，它们通常在最后会被分开使用。这会导致拼接和分离数据的额外成本（内存中的重塑和数据复制非常昂贵）。

`SepDataFrame` 试图像一个具有多索引列的 DataFrame 一样工作，但避免了数据拼接的开销。

**参数说明**：

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `df_dict` | Dict[str, pd.DataFrame] | - | 数据框字典，键为数据框名称，值为数据框对象 |
| `join` | str | - | 连接方式，用于对齐数据框的索引。如果 join 为 None，则跳过重新索引步骤 |
| `skip_align` | bool | False | 是否跳过索引对齐步骤。对于某些情况，跳过对齐可以提高性能 |

**属性**：

| 属性 | 类型 | 说明 |
|------|------|------|
| `loc` | SDFLoc | 定位器，用于索引操作 |
| `index` | pd.Index | 返回 join 指定的数据框的索引 |
| `columns` | pd.MultiIndex | 返回所有数据框的列名，格式为多级索引 |

**主要方法**：

| 方法 | 说明 |
|------|------|
| `apply_each(method, *args, **kwargs)` | 对每个数据框应用指定方法 |
| `sort_index(*args, **kwargs)` | 对每个数据框的索引进行排序 |
| `copy(*args, **kwargs)` | 复制每个数据框 |
| `__getitem__(item)` | 获取指定的数据框 |
| `__setitem__(item, df)` | 设置或更新数据框 |
| `__delitem__(item)` | 删除指定的数据框 |
| `__contains__(item)` | 检查是否包含指定的数据框 |
| `__len__()` | 返回数据框的长度 |

**使用示例**：

```python
import pandas as pd
from qlib.contrib.data.utils import SepDataFrame

# 创建多个数据框
df1 = pd.DataFrame({
    'A': [1, 2, 3],
    'B': [4, 5, 6]
}, index=['2020-01-01', '2020-01-02', '2020-01-03'])

df2 = pd.DataFrame({
    'C': [7, 8, 9],
    'D': [10, 11, 12]
}, index=['20202020-01-01', '2020-01-02', '2020-01-03'])

# 创建 SepDataFrame
sdf = SepDataFrame(
    df_dict={
        'feature': df1,
        'label': df2
    },
    join='feature'
)

# 访问数据框
feature_df = sdf['feature']
label_df = sdf['label']

# 添加新数据框
sdf['weight'] = pd.DataFrame({
    'W': [1, 1, 1]
}, index=df1.index)

# 获取索引
index = sdf.index

# 获取列名
columns = sdf.columns
print(columns)  # MultiIndex([('feature', 'A'), ('feature', 'B'), ('label', 'C'), ('label', 'D'), ('weight', 'W')])

# 使用 loc 进行索引
subset = sdf.loc[['2020-01-01', '2020-01-02']]
```

---

### 2. SDFLoc 类

```python
class SDFLoc:
    def __init__(self, sdf: SepDataFrame, join)
```

**功能说明**：
`SepDataFrame` 的定位器类，用于支持类似 pandas 的索引操作。

**参数说明**：

| 参数 | 类型 | 说明 |
|------|------|------|
| `sdf` | SepDataFrame | 要定位的分离式数据框 |
| `join` | str | 连接方式 |

**使用示例**：

```python
from qlib.contrib.data.utils import SepDataFrame

sdf = SepDataFrame(
    df_dict={
        'feature': df1,
        'label': df2
    },
    join='feature'
)

# 按行索引
subset_rows = sdf.loc[['2020-01-01', '2020-01-02']]

# 按列名选择
subset_cols = sdf.loc(axis=1)[['feature', 'label']]

# 按行和列选择
subset = sdf.loc[['2020-01-01', '2020-01-02'], ['feature', 'label']]
```

---

### 3. align_index() 函数

```python
def align_index(df_dict, join)
```

**功能说明**：
对齐数据框字典中所有数据框的索引。

**参数说明**：

| 参数 | 类型 | 说明 |
|------|------|------|
| `df_dict` | dict | 数据框字典 |
| `join` | str | 用于作为基准索引的键名 |

**返回值**：
- 对齐后的数据框字典

**使用示例**：

```python
from qlib.contrib.data.utils import align_index

df1 = pd.DataFrame({
    'A': [1, 2, 3]
}, index=['2020-01-01', '2020-01-02', '2020-01-03'])

df2 = pd.DataFrame({
    'B': [4, 5, 6]
}, index=['2020-01-01', '2020-01-02', '2020-01-03'])

# 对齐索引（实际上索引已经对齐，此示例演示用法）
df_dict = {
    'feature': df1,
    'label': df2
}

aligned_dict = align_index(df_dict, join='feature')
```

---

## 特性说明

### 1. 性能优化

`SepDataFrame` 的主要设计目标是避免多个数据框拼接和分离的性能开销：

- **避免数据复制**：每个数据框保持独立，不需要复制数据
- **避免拼接开销**：不需要将多个数据框拼接成一个大数据框
- **按需访问**：只访问需要的数据框，减少内存使用

### 2. 类似 pandas 的接口

`SepDataFrame` 提供了类似 pandas 的接口，使其易于使用：

- 支持 `loc` 索引
- 支持 `columns` 和 `index` 属性
- 支持字典式的访问和修改
- 支持一些常用的 DataFrame 方法

### 3. isinstance 欺骗

模块中通过重写 `builtins.isinstance` 函数，使得 `isinstance(SepDataFrame(), pd.DataFrame)` 返回 `True`。这使得 `SepDataFrame` 可以被当作 `pd.DataFrame` 使用，兼容大多数接受 DataFrame 的代码。

---

## 完整示例

### 示例 1：基本使用

```python
import pandas as pd
from qlib.contrib.data.utils import SepDataFrame

# 创建数据框
features_df = pd.DataFrame({
    'feature1': [1.0, 2.0, 3.0],
    'feature2': [4.0, 5.0, 6.0],
}, index=['2020-01-01', '2020-01-02', '2020-01-03'])

labels_df = pd.DataFrame({
    'label': [0, 1, 0],
}, index=['2020-01-01', '2020-01-02', '2020-01-03'])

weights_df = pd.DataFrame({
    'weight': [1.0, 0.8, 1.0],
}, index=['2020-01-01', '2020-01-02', '2020-01-03'])

# 创建 SepDataFrame
sdf = SepDataFrame(
    df_dict={
        'features': features_df,
        'labels': labels_df,
        'weights': weights_df
    },
    join='features'
)

# 访问数据
print("Features:", sdf['features'])
print("Labels:", sdf['labels'])
print("Weights:", sdf['weights'])

# 获取信息
print("Index:", sdf.index)
print("Columns:", sdf.columns)
print("Length:", len(sdf))
```

### 示例 2：索引操作

```python
from qlib.contrib.data.utils import SepDataFrame

# 创建 SepDataFrame
sdf = SepDataFrame(
    df_dict={
        'features': features_df,
        'labels': labels_df
    },
    join='features'
)

# 按行索引选择
subset = sdf.loc[['2020-01-01', '2020-01-02']]
print("Subset by rows:")
print(subset)

# 按列名选择
subset = sdf.loc(axis=1)['features']
print("Subset by columns:")
print(subset)

# 组合选择
subset = sdf.loc[['2020-01-01', '2020-01-02'], ['features']]
print("Combined selection:")
print(subset)
```

### 示例 3：数据框操作

```python
from qlib.contrib.data.utils import SepDataFrame

# 创建 SepDataFrame
sdf = SepDataFrame(
    df_dict={
        'features': features_df,
        'labels': labels_df
    },
    join='features'
)

# 排序索引
sdf_sorted = sdf.sort_index()
print("Sorted index:")
print(sdf_sorted.index)

# 复制
sdf_copy = sdf.copy()

# 应用方法
sdf_filled = sdf.apply_each('fillna', value=0)
```

### 示例 4：动态添加和删除

```python
from qlib.contrib.data.utils import SepDataFrame

# 创建初始 SepDataFrame
sdf = SepDataFrame(
    df_dict={
        'features': features_df
    },
    join='features'
)

# 添加新的数据框
sdf['labels'] = labels_df
sdf['weights'] = weights_df

# 检查是否存在
print("'features' in sdf:", 'features' in sdf)
print("'labels' in sdf:", 'labels' in sdf)

# 删除数据框
del sdf['weights']
print("'weights' in sdf:", 'weights' in sdf)
```

---

## 注意事项

1. **索引对齐**：在创建 `SepDataFrame` 时，如果指定了 `join` 参数，所有其他数据框会根据 join 指定的数据框的索引进行重新索引
2. **性能考虑**：对于已知索引已经对齐的情况，可以使用 `skip_align=True` 来跳过索引对齐步骤以提高性能
3. **接口限制**：`SepDataFrame` 试图模仿 pandas DataFrame，但并不完全相同。某些高级功能可能尚未实现
4. **isinstance 行为**：由于重写了 `builtins.isinstance`，`isinstance(SepDataFrame(), pd.DataFrame)` 会返回 `True`
5. **多列索引**：`columns` 属性返回多级索引，第一级是数据框名称，第二级是列名

---

## 相关模块

- [qlib.data.dataset](../dataset/README.md) - 数据集模块
- [qlib.contrib.data.handler](../handler.md) - 数据处理器模块
