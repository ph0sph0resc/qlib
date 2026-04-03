# qlib/rl/contrib/backtest.py 模块文档

## 文件概述
基于训练好的强化学习策略进行回测的工具模块。支持并行回测和详细的执行报告生成。

## 主要函数

### _get_multi_level_executor_config

```python
def _get_multi_level_executor_config(
    strategy_config: dict,
    cash_limit: float | None = None,
    generate_report: bool = False,
    data_granularity: str = "1min",
) -> dict
```

生成多级执行器配置。
- **参数**：
  - `strategy_config`: 策略配置字典
  - `cash_limit`: 现金限制
  - `generate_report`: 是否生成报告
  - `data_granularity`: 数据粒度
- **返回**: 执行器配置字典

### _convert_indicator_to_dataframe

```python
def _convert_indicator_to_dataframe(indicator: dict) -> Optional[pd.DataFrame]
```

将指标字典转换为DataFrame。
- **参数**: `indicator`: 指标字典
- **返回**: 转换后的DataFrame

### _generate_report

```python
def _generate_report(
    decisions: List[BaseTradeDecision],
    report_indicators: List[INDICATOR_METRIC],
) -> Dict[str, Tuple[pd.DataFrame, pd.DataFrame]]
```

生成回测报告。
- **参数**：
  - `decisions`: 交易决策列表
  - `report_indicators`: 指标报告列表
- **返回**: 报告字典

### single_with_simulator

```python
def single_with_simulator(
    backtest_config: dict,
    orders: pd.DataFrame,
    split: Literal["stock", "day"] = "stock",
    cash_limit: float | None = None,
    generate_report: bool = False,
) -> Union[Tuple[pd.DataFrame, dict], pd.DataFrame]
```

使用SingleAssetOrderExecution模拟器在单线程中运行回测。
订单将逐日执行。每天订单创建一个新的模拟器。

**执行流程**：
```
对于每个订单：
    1. 创建SingleAssetOrderExecution模拟器
    2. 使用Qlib Executor和Exchange执行
    3. 收集执行记录
    4. 累计指标
```

- **参数**：
  - `backtest_config`: 回测配置
  - `orders`: 要执行的订单DataFrame
  - `split`: 订单分割方式（"stock"或"day"）
  - `cash_limit`: 现金限制
  - `generate_report`: 是否生成报告
- **返回**:
  - 如果`generate_report=True`: 返回（执行记录，生成的报告）
  - 否则：只返回执行记录

### single_with_collect_data_loop

```python
def single_with_collect_data_loop(
    backtest_config: dict,
    orders: pd.DataFrame,
    split: Literal["stock", "day"] = "stock",
    cash_limit: float | None = None,
    generate_report: bool = False,
) -> Union[Tuple[pd.DataFrame, dict], pd.DataFrame]
```

使用collect_data_loop在单线程中运行回测。
不使用模拟器包装，直接使用Qlib的回测循环。

- **参数**：
  - `backtest_config`: 回测配置
  - `orders`: 要执行的订单DataFrame
  - `split`: 订单分割方式
  - `cash_limit`: 现金限制
  - `generate_report`: 是否生成报告
- **返回**:
  - 如果`generate_report=True`: 返回（执行记录，生成的报告）
  - 否则：只返回执行记录

### backtest

```python
def backtest(backtest_config: dict, with_simulator: bool = False) -> pd.DataFrame
```

主回测函数，支持并行执行。

**执行流程**：
```
1. 读取订单文件
2. 按股票分割订单
3. 使用joblib并行执行每个股票的回测
4. 合并所有结果
5. 保存到CSV文件
```

- **参数**：
  - `backtest_config`: 回测配置字典
  - `with_simulator`: 是否使用模拟器作为后端
- **返回**: 执行记录DataFrame

## 回测架构

```
┌─────────────────────────────────────────────────┐
│                   backtest()                    │
│  (主回测函数，并行管理)                       │
└──────────────┬──────────────────────────────────┘
               │
               ├──────────────────────────┬─────────────────┐
               │                      │                 │
               ▼                      ▼                 │
    ┌────────────────────┐  ┌─────────────────────┐ │
    │ single_with_...   │  │ single_with_...     │ │
    │ (simulator)      │  │ (collect_data_loop)│ │
    └────────┬─────────┘  └────────┬───────────┘ │
             │                      │             │
             ▼                      ▼             │
    ┌──────────────────────────────────────────────┐    │
    │  SingleAssetOrderExecution   │  │  Qlib Executor/Exchange  │
    │  (模拟器)                 │  │  (原生回测)            │
    └────────┬─────────────────┘  └────────┬─────────┘    │
             │                      │             │
             ▼                      ▼             │
    ┌──────────────────────────────────────────────────────┐
    │         Qlib Backend                          │
    │  - Exchange: 交易所模拟                      │
    │  - Executor: 执行器                         │
    │  - Strategy: 策略（如FileOrderStrategy）    │
    └──────────────────────────────────────────────────────┘
```

## 订单格式

输入订单DataFrame应包含以下列：

```python
# 格式示例
orders = pd.DataFrame({
    "datetime": ["2020-01-01", "2020-01-02", ...],  # 交易日期
    "instrument": ["SH600000", "SH600001", ...],  # 股票代码
    "amount": [1000, 2000, ...],                # 交易数量
    "direction": [1, 0, ...],                    # 方向（1=买，0=卖）
})
```

## 配置示例

### 基本配置

```python
config = {
    # Qlib配置
    "qlib": {
        "provider_uri_1min": "/path/to/1min_data",
        "provider_uri_day": "/path/to/day_data",
    },

    # 订单文件
    "order_file": "/path/to/orders.pkl",

    # 执行器配置
    "executor": {
        "time_per_step": "1day",
    },

    # 交易所配置
    "exchange": {
        "open_cost": 0.0005,
        "close_cost": 0.0015,
        "min_cost": 5.0,
        "trade_unit": 100.0,
        "cash_limit": None,
    },

    # 策略配置
    "strategies": {
        "1day": {
            "class": "SomeStrategy",
            "module_path": "some.module",
            "kwargs": {...},
        },
    },

    # 回测参数
    "start_time": "09:30:00",
    "end_time": "14:59:00",
    "data_granularity": "1min",
    "concurrency": -1,
    "generate_report": False,
}
```

### 使用示例

```python
from qlib.rl.contrib import backtest

# 方式1：使用模拟器
results_simulator = backtest(config, with_simulator=True)

# 方式2：使用原生回测
results_native = backtest(config, with_simulator=False)
```

## 命令行使用

```bash
python -m qlib.rl.contrib.backtest \
    --config_path config.yaml \
    --use_simulator \
    --n_jobs 4
```

## 报告输出

### CSV文件
输出`backtest_result.csv`包含以下列：
- `instrument`: 股票代码
- `datetime`: 时间戳
- `amount`: 交易数量
- `direction`: 方向
- `deal_price`: 成交价格
- `deal_amount`: 成交数量
- `ffr`: 成交比例
- `pa`: 价格优势（BP）

### 详细报告
如果`generate_report=True`，额外输出`report.pkl`：
- 包含每个股票或日期的详细指标
- 包含交易明细

## 与其他模块的关系

### qlib.backtest
- **Exchange**: 交易所模拟核心
- **Executor**: 交易执行器
- **Strategy**: 交易策略基类
- **collect_data_loop**: 回测循环函数

### qlib.rl.order_execution
- **SingleAssetOrderExecution**: 订单执行模拟器
- 封装Qlib回测组件成RL模拟器接口

### qlib.rl.data
- **数据加载**: 提供回测所需的市场数据
- **特征计算**: 使用Qlib的特征系统

## 性能优化

### 1. 并行执行
- 使用joblib.Parallel进行并行
- 设置合适的worker数量
- 避免GIL限制

### 2. 内存管理
- 按股票分割订单
- 每个worker处理一个股票的所有订单
- 及时释放不需要的数据

### 3. 数据缓存
- 使用cachetools缓存频繁访问的数据
- 避免重复加载相同的数据

## 注意事项

1. **线程安全**: PyTorch设置单线程模式以避免问题
2. **数据格式**: 订单文件格式需要严格匹配
3. **时间对齐**: 确保时间戳正确对齐
4. **内存限制**: 大规模回测可能需要大量内存
