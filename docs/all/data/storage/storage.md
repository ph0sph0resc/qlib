# data/storage/storage.py 模块文档

## 文件概述

此文件定义了数据存储后端的抽象接口（Abstract Storage Interface），包括CalendarStorage、InstrumentStorage和FeatureStorage。这些类定义了统一的数据访问接口，支持各种存储后端实现。

## 类与函数

### 类型定义

```python
CalVT = str  # 日历值类型
InstVT = List[Tuple[CalVT, CalVT]]  # 标的物值类型
InstKT = Text  # 标的物键类型
```

### BaseStorage 类

**继承关系**:
- 无直接父类

**说明**:
- 存储后端的基类
- 提供统一的接口和方法

**主要方法**:

```python
@property
def storage_name(self) -> str
```
- 返回存储名称
- 从类名自动提取（如FileCalendarStorage → "calendar"）

### CalendarStorage 类（抽象）

**继承关系**:
- 继承自 BaseStorage

**说明**:
- 日历数据存储的抽象接口
- 支持List-like接口和字典索引映射

**主要方法**:

```python
def __init__(self, freq: str, future: bool, **kwargs)
```
- 初始化日历存储
- 参数：
  - freq: 数据频率（year/quarter/month/week/day）
  - future: 是否包含未来交易日
  - kwargs: 扩展参数

```python
@property
@abstractmethod
def data(self) -> Iterable[CalVT]
```
- 获取所有日历数据
- 返回：可迭代的时间戳列表
- 子：抛出ValueError，如果数据不存在

```python
@abstractmethod
def clear(self) -> None
```
- 清空日历数据

```python
@abstractmethod
def extend(self, iterable: Iterable[CalVT]) -> None
```
- 扩展日历数据

```python
@abstractmethod
def index(self, value: CalVT) -> int
```
- 获取时间戳的索引位置
- 返回：时间戳在日历中的索引位置

```python
@abstractmethod
def insert(self, index: int, value: CalVT) -> None
```
- 在指定位置插入时间戳
- index：插入位置

```python
@abstractmethod
def remove(self, value: CalVT) -> None
```
- 移除指定的时间戳

```python
@abstractmethod
def __setitem__(self, i: int, value: CalVT) -> None
```
- 设置指定位置的值
- 支持单个元素和切片设置

```python
@abstractmethod
def __delitem__(self, i: Union[int, slice]) -> None
```
- 删除指定位置的值
- �持单个索引和切片删除

```python
@abstractmethod
def __getitem__(self, i: Union[int, slice]) -> Union[CalVT, Iterable[CalVT]]
```
- 获取指定位置的值
- 支持单个索引和切片访问

```python
@abstractmethod
def __len__(self) -> int
```
- 返回日历长度

### InstrumentStorage 类（抽象）

**继承关系**:
- 继承自 BaseStorage

**说明**:
- 标的物数据存储的抽象接口
- 支持字典接口（键为标的物，值为时间范围元组列表）

**主要方法**:

```python
def __init__(self, market: str, freq: str, **kwargs)
```
- 初始化标的物存储
- 参数：
  - market: 市场名称
  - freq: 数据频率
- kwargs: 扩展参数

```python
@property
@abstractmethod
def data(self) -> Dict[InstKT, InstVT]
```
- 获取所有标的物数据
- 返回：{标的物代码: [(开始时间, 结束时间), ...]}
- 子：抛出ValueError，如果数据不存在

```python
@abstractmethod
def clear(self) -> None
```
- 清空标的物数据

```python
@abstractmethod
def update(self, *args, **kwargs) -> None
```
- 更新标的物数据
- 类似于dict的update()方法

```python
@abstractmethod
def __setitem__(self, k: InstKT, v: InstVT) -> None
```
- 设置指定标的物的数据

```python
@abstractmethod
def __delitem__(self, k: InstKT) -> None
```
- 删除指定标的物

```python
@abstractmethod
def __getitem__(self, k: InstKT) -> InstVT
```
- 获取指定标的物的数据
- 返回：[(开始时间, 结束时间), ...]

```python
@abstractmethod
def __len__(self) -> int
```
- 返回标的物数量

### FeatureStorage 类（抽象）

**继承关系**:
- 继承自 BaseStorage

**说明**:
- 特征数据存储的抽象接口
- 支持二进制格式存储和范围访问

**主要方法**:

```python
def __init__(self, instrument: str, field: str, freq: str, **kwargs)
```
- 初始化特征存储
- 参数：
  - instrument: 标的物代码
  - field: 特征字段名
  - freq: 数据频率

```python
@property
@abstractmethod
def data(self) -> pd.Series
```
- 获取所有特征数据
- 返回：以日历索引的Series
- 如果数据不存在，返回空pd.Series(dtype=np.float32)

```python
@property
@abstractmethod
def start_index(self) -> Union[int, None]
```
- 获取特征的起始索引
- 返回：第一个数据点的索引
- 如果数据不存在，返回None

```python
@property
@abstractmethod
def end_index(self) -> Union[int, None]
```
- 获取特征的结束索引
- 返回：最后一个数据点的索引
- 注意：右侧索引是闭区间，下一个追加点的索引为end_index + 1
- 如果数据不存在，返回None

```python
@abstractmethod
def clear(self) -> None
```
- 清空特征数据

```python
@abstractmethod
def write(self, data_array: Union[List, np.ndarray, Tuple], index: int = None)
```
- 写入数据数组
- 参数：
  - data_array: 要写入的数据（列表、numpy数组或元组）
  - index: 起始索引（None表示追加）
- 行为：
  - index=None: 追加到末尾
  - index指定且 > 当前end_index: 0: 从end_index+1到index-1填充NaN
  - index指定且 > 当前start_index: 覫新数据

```python
@abstractmethod
def rebase(self, start_index: int = None, end_index: int = None)
```
- 重定位特征的起始和结束索引
- start_index和end_index是闭区间：[start_index, end_index]
- 如果start_index < 当前start_index：前导用NaN填充
- 如果end_index > 当前end_index：后导用NaN填充
- 如果end_index < start_index：忽略

```python
@abstractmethod
def rewrite(self, data: Union[List, np.ndarray, Tuple], index: int)
```
- 重写特征所有数据
- 清空旧数据后写入新数据

```python
@abstractmethod
def __getitem__(self, i: Union[int, slice]) -> Union[Tuple[int, float], pd.Series]
```
- 获取指定位置的特征值
- 支持：
  - 单个索引：返回 (索引, 值值)
  - 切片访问：返回Series
- 如果数据不存在：
  - 单个索引：返回 (None, None)
  - 切片访问：返回空Series

```python
@abstractmethod
def __len__(self) -> int
```
- 返回特征长度

## 与其他模块的关系

### 依赖模块
- **pandas/numpy**: 数据结构
- **pathlib**: 路径处理
- **qlib.log**: 日志记录

### 梫导出模块
- **qlib.data/file_storage.py**: 文件存储实现

## 设计模式

### 存储接口设计

采用List-like接口和字典索引映射：

```
CalendarStorage: List[timestamp]
    ↓
    索询: index(timestamp) → index
    ↓
    插入: insert(index, timestamp)
    ↓
    删除: remove(timestamp)
```

```

### 特征存储设计

```
FeatureStorage (二进制文件)
    ↓
    快速范围访问: getitem(slice) → np.array
    ↓
    索意填充： write支持NaN填充
    ↓
    定位重写： rebase/rewrite
```

### 索引管理

```
index: int (在日历中的位置)
    ↓
start_index: int (第一个数据点)
    ↓
end_index: int (最后一个数据点)
    ↓
长度: end_index - start_index + 1
```

## 使用示例

### 实现日历存储

```python
from qlib.data.storage import CalendarStorage

class MyCalendarStorage(CalendarStorage):
    def __init__(self, freq, future):
        super().__init__(freq, future)
        self._calendar = []

    @property
    def data(self):
        return self._calendar

    def clear(self):
        self._calendar.clear()

    def extend(self, values):
        self._calendar.extend(values)

    def index(self, value):
        return self._calendar.index(value)

    def __setitem__(self, index, value):
        if index >= len(self._calendar):
            self._calendar.extend([None] * (index - len(self._calendar)))
        self._calendar[index] = value

    def __getitem__(self, index):
        return self._calendar[index]

    def __delitem__(self, index):
        del self._calendar[index]

    def __len__(self):
        return len(self._calendar)
```

### 实现标的物存储

```python
from qlib.data.storage import InstrumentStorage
from pathlib import Path

class MyInstrumentStorage(InstrumentStorage):
    def __init__(self, market, freq):
        super().__init__(market, freq)
        self.file_path = Path(f"/path/to/instruments/{market.lower()}.txt")
        self._data = {}

    def load(self):
        if self.file_path.exists():
            with self.file_path.open('r') as f:
                for line in f:
                    parts = line.strip().split('\t')
                    if len(parts) >= 3:
                        inst = parts[0]
                        start = pd.Timestamp(parts[1])
                        end = pd.Timestamp(parts[2])
                        self._data.setdefault(inst, []).append((start, end))

    @property
    def data(self):
        return self._data

    def clear(self):
        self._data.clear()

    def update(self, *args, **kwargs):
        for inst, spans in kwargs.items():
            self._data[inst] = spans

    def __setitem__(self, k, v):
        self._data[k] = v

    def __getitem__(self, k):
        return self._data.get(k)

    def __delitem__(self, k):
        del self._data[k]

    def __len__(self):
        return len(self._data)
```

### 实现特征存储（二进制格式）

```python
from qlib.data.storage import FeatureStorage
import numpy as np
import pandas as pd
from pathlib import Path

class BinaryFeatureStorage(FeatureStorage):
    def __init__(self, instrument, field, freq):
        super().__init__(instrument, field, freq)
        self.file_path = Path(f"/path/to/features/{instrument.lower()}/{field.lower()}.{freq}.bin")
        self._dtype = np.float32

    def clear(self):
        self.file_path.write_bytes(b'')

    @property
    def data(self) -> pd.Series:
        if not self.file_path.exists():
            return pd.Series(dtype=self._dtype)
        with open(self.file_path, 'rb') as f:
            index = np.frombuffer(f.read(4), dtype='<f')[0]
            n_items = (self.file_path.stat().st_size // 4) - 1
            data = np.fromfile(self.file_path, dtype=self._dtype, offset=4, count=n_items)
            return pd.Series(data, index=pd.RangeIndex(index, index + len(data)), dtype=self._dtype)

    @property
    def start_index(self) -> int:
        if not self.file_path.exists():
            return None
        with open(self.file_path, 'rb') as f:
            return int(np.frombuffer(f.read(4), dtype='<f')[0])

    @property
    def end_index(self) -> int:
        if not self.file_path.exists():
            return None
        return self.start_index + len(self) - 1

    def write(self, data_array, index=None):
        if not data_array:
            return
        with open(self.file_path, 'ab') as f:
            data_array = np.asarray(data_array, dtype=self._dtype)
            if index is not None:
                current_end = self.end_index if self.file_path.exists() else -1
                index = max(0, current_end)
                if index <= current_end:
                    padding = np.zeros(current_end - index, dtype=self._dtype)
                    data_array = np.concatenate([padding, data_array])
                index = current_end - len(data_array)
            else:
                index = self.end_index + 1
            f.seek(index * 4, 0)
            f.write(data_array.tobytes())

    def __getitem__(self, i):
        if not self.file_path.exists():
            return (None, None)
        with open(self.file_path, 'rb') as f:
            f.seek(i * 4, 0)
            value = np.frombuffer(f.read(4), dtype='<f')[0]
            return (i, value)

    def __getitem__(self, slice):
        if not self.file_path.exists():
            return pd.Series(dtype=self._dtype)
        start, stop = slice.start, slice.stop
        length = stop - start
        f.seek(start * 4, 0)
        data = np.fromfile(f.read(4, dtype=self._dtype, count=length)
        return pd.Series(data, index=pd.RangeIndex(start, stop), dtype=self._dtype)

    def __len__(self):
        if not self.file_path.exists():
            return 0
        return self.file_path.stat().st_size // 4 - 1
```

## 扩展点

### 二进制特征存储格式

```
文件格式: {instrument}/{field}.{freq}.bin
结构: [index (int), values...] (float32)
```

- 索引：4字节float32，表示第一个数据点的索引
- 数据：连续的float32数组

### 写入流程

```python
# 1. 初始化缓冲
index = current_end_index + 1
data_array = np.array(values, dtype=np.float32)

# 2. 定位到文件起始位置
f.seek(index * 4, 0)

# 3. 写入数据
f.write(data_array.tobytes())
```

### 扩展点

### 自动扩容机制

```python
# 当index指定超出当前范围时自动填充NaN
if index <= current_end:
    padding = np.zeros(current_end - index, dtype=self._dtype)
    data_array = np.concatenate([padding, data_array])
```

## 注意事项

1. **接口一致性**: 所有存储类必须实现完整的接口方法
2. **类型安全**: 使用typing注解确保类型正确
3. **错误处理**: 数据不存在时抛出ValueError
4. **索引管理**: 特征存储使用索引而非时间戳，提高性能
5. **边界处理**: write方法会自动处理边界情况
6. **文件安全**: 使用pathlib.Path进行跨平台路径操作
7. **性能考虑**: 使用二进制格式和向量化操作
8. **线程安全**: 需要考虑多线程访问的并发安全

## 相关文件

- **qlib.data/storage/file_storage.py**: 文件存储实现
- **qlib.data**: 提供者使用存储
- **qlib.config**: 配置管理
- **pandas/numpy**: 数据处理
