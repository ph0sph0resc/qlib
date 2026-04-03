# utils/index_data.py 模块文档

## 文件概述
提供高性能的索引数据结构，作为Pandas Series/DataFrame的轻量级替代品。目标是在保持简单索引功能的同时提供接近NumPy的性能。

## 设计理念
- Pandas提供了用户友好的接口，但集成了太多功能导致性能开销
- `index_data`尝试模拟Pandas的API，但不妥协性能
- 提供基本的NumPy数据和简单索引功能
- 如果调用可能损害性能的API，会抛出Error

## 核心类

### Index 类
**功能：** 索引类（用于行或列索引）

**设计原则：**
- 只读操作优先级高于写操作
- 设计为只读方式以共享数据查询
- 修改会创建新的Index

**限制：**
- 不支持重复索引值（只考虑第一次出现）
- 不考虑索引顺序（切片行为与Pandas不一致）

**主要属性：**
- `idx_list`: np.ndarray类型，存储索引列表
- `index_map`: dict类型，索引值到位置的映射
- `_is_sorted`: bool类型，标识是否已排序

**主要方法：**

1. `__init__(idx_list)`
   - 接受list、pd.Index、Index或int
   - int类型时创建指定长度的arange索引

2. `__getitem__(i: int)`
   - 按位置获取索引值

3. `index(item) -> int`
   - 根据索引值获取整数位置
   - 支持类型转换（pd.Timestamp、np.datetime64）
   - 如果不存在则抛出KeyError

4. `__or__(other) -> Index`
   - 合并两个索引（并集）

5. `__eq__(other) -> bool`
   - 比较两个索引是否相等

6. `sort() -> Tuple[Index, np.ndarray]`
   - 对索引进行排序
   - 返回：(排序后的Index, 排序索引数组)

7. `tolist()`
   - 转换为Python list

**内部方法：**
- `_convert_type(item)`: 类型转换处理

---

### LocIndexer 类
**功能：** 类似Pandas的loc索引器

**设计原则：**
- 只读操作优先级高于写操作
- 设计为只读方式以共享数据查询
- 修改会创建新的Index

**主要方法：**

1. `__init__(index_data, indices, int_loc=False)`
   - `index_data`: 绑定的IndexData
   - `indices`: 索引列表
   - `int_loc`: 是否为整数位置模式

2. `__getitem__(indexing)`
   - 支持多种索引方式：
     - 单值：`loc[value]`
     - 切片：`loc[start:stop]`
     - 列表/数组：`loc[[v1, v2, ...]]`
     - 布尔数组：`loc[bool_array]`
   - 自动处理值索引到位置索引的转换
   - 返回SingleData或MultiData

**索引转换流程：**
```
值索引 → 位置索引 → 选择数据 → 选择索引 → 压缩维度 → 返回
```

---

### IndexData 类（基类）
**功能：** SingleData和MultiData的基类

**设计原则：**
- 底层数据只支持np.floating类型
- 支持基于np.floating的布尔值

**主要属性：**
- `data`: np.ndarray，存储实际数据
- `indices`: List[Index]，存储索引
- `ndim`: 数据维度

**主要方法：**

1. 数据访问：
   - `loc`: 类似Pandas的loc索引器
   - `iloc`: 整数位置索引器
   - `index`: 行索引
   - `columns`: 列索引（仅2D）
   - `__getitem__`: 支持[...]语法

2. 数据操作：
   - `_align_indices(other)`: 对齐索引
   - `sort_index(axis=0, inplace=True)`: 排序索引
   - `__invert__`: 取反操作
   - `abs()`: 绝对值（忽略NaN）
   - `replace(to_replace)`: 替换值
   - `apply(func)`: 应用函数

3. 聚合运算：
   - `sum(axis=None)`: 求和（支持NaN）
   - `mean(axis=None)`: 求平均值（支持NaN）

4. 数据清理：
   - `isna()`: 检查NaN
   - `fillna(value=0, inplace=False)`: 填充NaN
   - `count()`: 非NaN值计数
   - `all()`: 全部为真

5. 属性：
   - `empty`: 是否为空
   - `values`: 返回data数组

**元类：方法运算的自动生成**
- `index_data_ops_creator`: 自动生成`__add__`, `__sub__`, `__mul__`, `__truediv__`等方法

---

### SingleData 类
**功能：** 1D数据结构（替代pd.Series）

**继承关系：**
- 继承自 `IndexData`

**构造方式：**
- 从list/array创建
- 从dict创建（自动提取keys和values）
- 从pd.Series创建
- 从单个数值创建（转为list）

**主要方法：**

1. `_align_indices(other)`
   - 对齐索引进行算术运算
   - 如果索引集合相同则直接返回
   - 否则通过reindex对齐

2. `reindex(index, fill_value=np.nan) -> SingleData`
   - 重新索引数据
   - 缺失值用fill_value填充

3. `add(other, fill_value=0)`
   - 加法操作（支持不同索引）
   - 先reindex到并集索引，然后相加

4. `to_dict() -> dict`
   - 转换为字典

5. `to_series() -> pd.Series`
   - 转换为pd.Series

**使用示例：**
```python
# 从dict创建
sd = SingleData({"a": 1, "b": 2, "c": 3})

# 重新索引
sd2 = sd.reindex(["a", "c", "d"])  # {"a": 1, "c": 3, "d": nan}

# 加法
sd3 = sd + SingleData({"a": 10, "d": 4})
```

---

### MultiData 类
**功能：** 2D数据结构（替代pd.DataFrame）

**继承关系：**
- 继承自 `IndexData`

**构造方式：**
- 从2D list/array创建
- 从pd.DataFrame创建

**主要方法：**
- `_align_indices(other)`: 对齐索引

**使用示例：**
```python
# 从DataFrame创建
import pandas as pd
df = pd.DataFrame({"a": [1, 2], "b": [3, 4]}, index=["x", "y"])
md = MultiData(df)

# 访问数据
print(md.loc["x", "a"])  # 1
print(md.loc["x", :])   # SingleData({"a": 1, "b": 3})
```

## 辅助函数

### concat(data_list, axis=1) -> MultiData
**功能：** 按索引连接多个SingleData

**参数：**
- `data_list`: SingleData列表
- `axis`: 连接轴（目前只支持axis=1）

**返回：** MultiData（ndim=2）

---

### sum_by_index(data_list, new_index, fill_value=0) -> SingleData
**功能：** 按新索引求和

**参数：**
- `data_list`: SingleData列表
- `new_index`: 新索引列表
- `fill_value`: 缺失值的填充值

**返回：** 求和后的SingleData

## 性能优化点

1. **使用NumPy数组**
   - 底层数据存储为np.ndarray
   - 避免Pandas的包装开销

2. **只读设计**
   - 修改操作返回新对象
   - 支持数据共享

3. **索引缓存**
   - 使用dict进行O(1)查找
   - 避免线性搜索

4. **批量操作**
   - 算术运算使用向量化操作
   - 聚合函数使用NumPy的nansum、nanmean

## 与其他模块的关系
- `numpy`: 底层数据结构
- `pandas`: 兼容性支持
