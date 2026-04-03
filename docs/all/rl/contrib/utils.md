# qlib/rl/contrib/utils.md 模块文档

## 文件概述
contrib模块的辅助工具函数，主要用于订单文件的读取和处理。

## 主要函数

### read_order_file

```python
def read_order_file(order_file: Path | pd.DataFrame) -> pd.DataFrame
```

读取订单文件并转换为标准格式。

**支持格式**：
- `.pkl`: Pickle文件
- `.csv`: CSV文件
- `pd.DataFrame`: 直接传入DataFrame

**列名映射**：
- `date` → `datetime`（兼容旧格式）
- `order_type` → `direction`（兼容旧格式）

**输出格式**：
```python
{
    "datetime": str,      # 交易日期时间
    "instrument": str,    # 股票代码
    "amount": float,      # 交易数量
    "direction": int,     # 方向（0=卖，1=买）
}
```

## 使用示例

### 从文件读取

```python
from qlib.rl.contrib.utils import read_order_file
from pathlib import Path

# 读取pickle文件
orders = read_order_file(Path("/path/to/orders.pkl"))

# 读取CSV文件
orders = read_order_file(Path("/path/to/orders.csv"))

# 直接传入DataFrame
import pandas as pd
df = pd.DataFrame({...})
orders = read_order_file(df)
```

### 在回测中使用

```python
from qlib.rl.contrib import backtest, utils

config = {...}
config["order_file"] = "/path/to/orders.pkl"

# 内部会调用read_order_file
results = backtest(config)
```

## 兼容性设计

### 支持多种输入
```python
# 可以接受路径
read_order_file("orders.pkl")

# 可以接受Path对象
read_order_file(Path("orders.pkl"))

# 可以接受DataFrame
read_order_file(df)
```

### 自动列名转换
- 处理旧格式的列名
- 确保输出格式一致

## 数据流程

```
订单文件/数据源
    │
    ▼
read_order_file()
    │
    ├─▶ 检查输入类型
    │     │
    │     ├─▶ Path → 根据扩展名读取
    │     │     │   ├─▶ .pkl → pd.read_pickle()
    │     │     │   └─▶ .csv → pd.read_csv()
    │     │     │
    │     │     └─▶ 转换列名
    │     │         ├─▶ date → datetime
    │     │         └─▶ order_type → direction
    │     │
    │     └─▶ DataFrame → 直接使用
    │         └─▶ 同样的列名转换
    │
    └─▶ 返回标准格式DataFrame
```

## 与其他模块的关系

### qlib.rl.contrib.backtest
- **使用**: 读取订单文件进行回测
- **集成**: 作为配置的一部分

### qlib.backtest.decision
- **输出格式**: 与Order对象兼容
- **类型转换**: 字符串时间戳转pd.Timestamp

## 错误处理

### 不支持的文件类型
```python
TypeError: Unsupported order file type: .txt
```

### 文件不存在
```python
FileNotFoundError: [Errno 2] No such file or directory: 'nonexistent.pkl'
```

## 最佳实践

1. **统一格式**：
   - 始终使用标准格式
   - 避免依赖列名转换

2. **类型一致性**：
   - datetime转换为字符串
   - direction使用整数类型

3. **路径处理**：
   - 使用Path对象
   - 支持相对和绝对路径

4. **验证输入**：
   - 检查必要列是否存在
   - 验证数据类型
