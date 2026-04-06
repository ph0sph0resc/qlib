# qlib/rl/contrib/naive_config_parser.md 模块文档

## 文件概述
配置文件解析工具，支持多种配置格式（YAML、JSON、Python）和配置继承机制。

## 主要函数

### merge_a_into_b

```python
def merge_a_into_b(a: dict, b: dict) -> dict
```

将字典a合并到字典b中，支持嵌套合并和删除标记。

**特殊处理**：
- 如果值包含`_delete_`键，则删除b中的对应键
- 支持嵌套字典的递归合并

### check_file_exist

```python
def check_file_exist(filename: str, msg_tmpl: str = 'file "{}" does not exist') -> None
```

检查文件是否存在，不存在则抛出FileNotFoundError。

### parse_backtest_config

```python
def parse_backtest_config(path: str) -> dict
```

解析配置文件，支持多种格式和继承机制。

**支持的格式**：
- `.py`: Python配置文件
- `.yaml`, `.yml`: YAML配置文件
- `.json`: JSON配置文件

**配置继承**：
- 使用`_base_`字段指定基础配置文件
- 支持多个基础配置（列表形式）
- 递归继承和合并

### _convert_all_list_to_tuple

```python
def _convert_all_list_to_tuple(config: dict) -> dict
```

递归将配置中的所有列表转换为元组。用于保持配置不可变性。

### get_backtest_config_fromfile

```python
def get_backtest_config_fromfile(path: str) -> dict
```

从文件加载配置并应用默认值。

**默认配置**：

```python
# 交易所默认配置
exchange_config_default = {
    "open_cost": 0.0005,
    "close_cost": 0.0015,
    "min_cost": 5.0,
    "trade_unit": 100.0,
    "cash_limit": None,
}

# 回测默认配置
backtest_config_default = {
    "debug_single_stock": None,
    "debug_single_day": None,
    "concurrency": -1,
    "multiplier": 1.0,
    "output_dir": "outputs_backtest/",
    "generate_report": False,
    "data_granularity": "1min",
}
```

## 配置继承示例

### 基础配置（base.yaml）
```yaml
# base.yaml
exchange:
    open_cost: 0.0005
    close_cost: 0.0015

executor:
    time_per_step: 1day
```

### 派生配置
```yaml
# derived.yaml
_base_: base.yaml  # 继承基础配置

exchange:
    min_cost: 5.0  # 覆盖或添加新配置

executor:
    track_data: true  # 新增配置
```

### 合并后结果
```python
{
    "exchange": {
        "open_cost": 0.0005,  # 来自base
        "close_cost": 0.0015,  # 来自base
        "min_cost": 5.0,      # 来自derived
    },
    "executor": {
        "time_per_step": "1day",  # 来自base
        "track_data": true,         # 来自derived
    },
}
```

## 多重继承

```yaml
# level3.yaml
_base_:
  - level1.yaml
  - level2.yaml  # 按顺序继承
```

## 删除标记

使用`_delete_`标记删除不需要的配置：

```yaml
_base_: base.yaml

exchange:
    _delete_: true  # 删除整个exchange配置
```

## 配置加载流程

```
配置文件路径
    │
    ▼
parse_backtest_config()
    │
    ├─▶ 检查文件存在性
    │     │
    │     ├─▶ 读取文件内容
    │     │     │
    │     │     ├─▶ .py → import为模块，提取非__属性
    │     │     ├─▶ .yaml/.yml → 使用ruamel.yaml加载
    │     │     └─▶ .json → 使用json加载
    │     │
    │     └─▶ 返回配置字典
    │
    ├─▶ 检查_base_字段
    │     │
    │     ├─▶ 如果存在：
    │     │     │
    │     │     ├─▶ 递归加载基础配置
    │     │     ├─▶ 合并配置（merge_a_into_b）
    │     │     └─▶ 处理_delete_标记
    │     │
    │     └─▶ 否则：直接使用当前配置
    │
    ├─▶ 应用默认值（get_backtest_config_fromfile）
    │     │
    │     ├─▶ 交易所默认配置
    │     └─▶ 回测默认配置
    │
    └─▶ 返回完整配置
```

## 使用示例

### 基本使用
```python
from qlib.rl.contrib.naive_config_parser import get_backtest_config_fromfile

config = get_backtest_config_fromfile("config.yaml")
print(config)
```

### 动态加载配置
```python
# 可以在运行时动态加载不同的配置
def run_backtest(config_path: str):
    config = get_backtest_config_fromfile(config_path)
    # 使用config进行回测
```

## 平台兼容性

### Windows平台
- 使用临时目录处理文件复制
- 关闭临时文件以避免锁问题

### 跨平台
- 使用标准库（os, pathlib）
- 不依赖平台特定功能

## 注意事项

1. **路径处理**：
   - 支持相对路径和绝对路径
   - `_base_`中的路径相对于当前配置文件

2. **类型转换**：
   - 列表转换为元组
   - 保持配置的不可变性

3. **默认值**：
   - 确保必要的配置项有默认值
   - 避免KeyError

4. **配置验证**：
   - 当前不做严格验证
   - 依赖下游模块验证

## 安全考虑

- **Python配置**：使用临时目录导入模块，清理临时路径
- **YAML加载**：使用`safe`模式和`typ='safe'`防止代码注入
