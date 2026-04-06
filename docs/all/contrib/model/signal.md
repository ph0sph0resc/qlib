# signal 模块详细文档

## 模块概述

`signal` 模块提供了统一的交易信号接口，用于支持基于不同来源的交易决策。信号可以来自：
- 预先准备的数据
- 模型和数据集的在线预测
- 其他自定义来源

该模块的核心是一个抽象接口 `Signal`，以及几个具体实现类，用于统一处理不同来源的交易信号。

---

## 类文档

### Signal

抽象基类，定义了交易信号的统一接口。

#### 抽象方法

##### get_signal

获取指定时间段内的交易信号。

**函数签名：**
```python
@abc.abstractmethod
def get_signal(self, start_time: pd.Timestamp, end_time: pd.Timestamp) -> Union[pd.Series, pd.DataFrame, None]
```

**参数说明：**

| 参数 | 类型 | 说明 |
|------|------|------|
| `start_time` | pd.Timestamp | 决策步骤的开始时间 |
| `end_time` | pd.Timestamp | 决策步骤的结束时间 |

**返回值：**
- 类型：`Union[pd.Series, pd.DataFrame, None]`
- 说明：
  - `pd.Series`：单个预测值序列
  - `pd.DataFrame`：多个预测值的DataFrame
  - `None`：该时间段没有信号

**使用示例：**
```python
from qlib.backtest.signal import Signal

class MyCustomSignal(Signal):
    def get_signal(self, start_time, end_time):
        # 实现自定义信号逻辑
        # ...
        return signal_series
```

---

### SignalWCache

带缓存功能的信号实现类，使用 pandas DataFrame/Series 作为缓存存储预先准备好的信号数据。

#### 初始化方法

**函数签名：**
```python
def __init__(self, signal: Union[pd.Series, pd.DataFrame]) -> None
```

**参数说明：**

| 参数 | 类型 | 说明 |
|------|------|------|
| `signal` | Union[pd.Series, pd.DataFrame] | 预先准备好的信号数据 |

**信号数据格式要求：**

数据应具有双重索引（multi-index），格式如下：

```
                datetime
instrument
SH600000   2008-01-02  0.079704
           2008-01-03  0.120125
           2008-01-04  0.878860
           2008-01-07  0.505539
           2008-01-08  0.395004
```

- 外层索引：股票代码（instrument）
- 内层索引：时间戳（datetime）
- 值：预测分数或信号值

**注意：** 索引的顺序不重要，会自动调整。

#### 主要方法

##### get_signal

获取指定时间段内的信号。

**函数签名：**
```python
def get_signal(self, start_time: pd.Timestamp, end_time: pd.Timestamp) -> Union[pd.Series, pd.DataFrame]
```

**参数说明：**

| 参数 | 类型 | 说明 |
|------|------|------|
| `start_time` | pd.Timestamp | 开始时间 |
| `end_time` | pd.Timestamp | 结束时间 |

**返回值：**
- 类型：`Union[pd.Series, pd.DataFrame]`
- 说明：该时间段内的信号

**重采样逻辑：**
由于信号的频率可能与策略的决策频率不一致，因此需要进行重采样。使用 `"last"` 方法重采样，表示使用最近的信号值。

**使用示例：**
```python
import pandas as pd
from qlib.backtest.signal import SignalWCache

# 准备信号数据
data = {
    ('SH600000', pd.Timestamp('2020-01-02')): 0.5,
    ('SH600000', pd.Timestamp('2020-01-03')): 0.6,
    ('SH600004', pd.Timestamp('2020-01-02')): 0.3,
    ('SH600004', pd.Timestamp('2020-01-03')): 0.4,
}
index = pd.MultiIndex.from_tuples(data.keys(), names=['instrument', 'datetime'])
signal_series = pd.Series(data, index=index)

# 创建信号对象
signal = SignalWCache(signal_series)

# 获取信号
signal_data = signal.get_signal(
    pd.Timestamp('2020-01-02'),
    pd.Timestamp('2020-01-03
)
print(signal_data)
```

---

### ModelSignal

基于模型和数据集的信号实现类，继承自 `SignalWCache`。

该类使用训练好的模型对数据集进行预测，生成的预测分数作为信号。

#### 初始化方法

**函数签名：**
```python
def __init__(self, model: BaseModel, dataset: Dataset) -> None
```

**参数说明：**

| 参数 | 类型 | 说明 |
|------|------|------|
| `model` | BaseModel | 训练好的模型对象 |
| `dataset` | Dataset | 数据集对象 |

**初始化流程：**
1. 调用模型的 `predict()` 方法对数据集进行预测
2. 如果返回的是 DataFrame，提取第一列
3. 将预测结果传递给父类 `SignalWCache` 进行缓存

**使用示例：**
```python
from qlib.backtest.signal import ModelSignal
from qlib.model.base import BaseModel
from qlib.data.dataset import Dataset

# 假设已有训练好的模型和数据集
# model = ...
# dataset = ...

# 创建信号对象
signal = ModelSignal(model=model, dataset=dataset)

# 获取信号
signal_data = signal.get_signal(
    pd.Timestamp('2020-01-01'),
    pd.Timestamp('2020-01-31')
)
```

#### 方法

##### _update_model

更新模型（未实现）。

**函数签名：**
```python
def _update_model(self) -> None
```

**说明：**
该方法设计用于在线数据场景，在每个时间步更新模型：
1. 使用在线数据更新数据集（数据集需要支持在线更新）
2. 对新时间步进行预测
3. 更新到最新预测结果

**注意：** 当前未实现，抛出 `NotImplementedError`。

---

## 函数文档

### create_signal_from

根据不同类型的输入对象创建信号对象。

**函数签名：**
```python
def create_signal_from(
    obj: Union[Signal, Tuple[BaseModel, Dataset], List, Dict, Text, pd.Series, pd.DataFrame],
) -> Signal
```

**参数说明：**

| 参数 | 类型 | 说明 |
|------|------|------|
| `obj` | Union[Signal, Tuple, List, Dict, str, pd.Series, pd.DataFrame] | 用于创建信号的对象 |

**支持的输入类型及其处理方式：**

| 输入类型 | 处理方式 | 示例 |
|----------|----------|------|
| `Signal` | 直接返回 | `Signal` 对象 |
| `Tuple` 或 `List` | 创建 `ModelSignal` | `(model, dataset)` |
| `Dict` 或 `str` | 通过配置初始化 | `{"class": "SignalWCache", "signal": ...}` |
| `pd.Series``pandas.DataFrame` | 创建 `SignalWCache` | 预测分数 Series 或 DataFrame |

**返回值：**
- 类型：`Signal`
- 说明：创建的信号对象

**使用示例：**

```python
import pandas as pd
from qlib.backtest.signal import create_signal_from, SignalWCache, ModelSignal

# 方式 1：从 pandas Series 创建
signal_series = pd.Series(...)
signal1 = create_signal_from(signal_series)

# 方式 2：从 pandas DataFrame 创建
signal_df = pd.DataFrame(...)
signal2 = create_signal_from(signal_df)

# 方式 3：从元组 (model, dataset) 创建
signal3 = create_signal_from((model, dataset))

# 方式 4：从列表创建
signal4 = create_signal_from([model, dataset])

# 方式 5：从字典配置创建
signal_config = {
    "class": "SignalWCache",
    "module_path": "qlib.backtest.signal",
    "signal": signal_series
}
signal5 = create_signal_from(signal_config)

# 方式 6：从字符串配置创建
signal6 = create_signal_from("qlib.backtest.signal.SignalWCache")  # 需要配合配置

# 方式 7：直接传递 Signal 对象
signal7 = create_signal_from(SignalWCache(signal_series))
```

---

## 完整使用流程示例

### 示例 1：使用预先准备的信号数据

```python
import pandas as pd
from qlib.backtest.signal import SignalWCache

# 准备信号数据
# 假设我们有一份预测分数文件
predictions_df = pd.read_csv("predictions.csv", index_col=['instrument', 'datetime'])
predictions_df.index = pd.MultiIndex.from_tuples(
    [(inst, pd.Timestamp(date)) for inst, date in predictions_df.index],
    names=['instrument', 'datetime']
)

# 创建信号对象
signal = SignalWCache(predictions_df)

# 在回测中使用
def on_trading_day(start_time, end_time):
    # 获取当前时间段的信号
    current_signal = signal.get_signal(start_time, end_time)

    if current_signal is None:
        print(f"{start_time}: 无信号")
        return

    # 根据信号进行交易决策
    # 假设信号值 > 0.5 表示买入
    buy_signals = current_signal[current_signal > 0.5]
    for instrument, score in buy_signals.items():
        print(f"{start_time}: 买入 {instrument}, 信号分数 {score:.3f}")

# 模拟回测
trading_days = pd.date_range('2020-01-01', '2020-12-31', freq='B')
for i, day in enumerate(trading_days[:-1]):
    start_time = day
    end_time = trading_days[i + 1]
    on_trading_day(start_time, end_time)
```

### 示例 2：使用模型预测生成信号

```python
import qlib
from qlib.workflow import R
from qlib.backtest.signal import ModelSignal

# 初始化 QLib
qlib.init(provider_uri="~/.qlib/qlib_data/cn_data", region="cn")

# 使用工作流训练模型
config = "path/to/config.yaml"
model, dataset = R.run(config)

# 创建信号对象
signal = ModelSignal(model=model, dataset=dataset)

# 在回测中使用
def on_trading_day(start_time, end_time):
    # 获取当前时间段的信号
    current_signal = signal.get_signal(start_time, end_time)

    if current_signal is None:
        return

    # 选择信号最高的前10只股票
    top_n = 10
    top_stocks = current_signal.nlargest(top_n)

    print(f"\n{start_time}: 选股结果")
    for rank, (instrument, score) in enumerate(top_stocks.items(), 1):
        print(f"  {rank}. {instrument}: {score:.3f}")

    # 生成投资组合权重
    # 例如：等权配置
    target_weight = {inst: 1.0 / top_n for inst in top_stocks.index}

    # 执行交易
    # execute_trade(target_weight)
```

### 示例 3：使用 create_signal_from 灵活创建信号

```python
import pandas as pd
from qlib.backtest.signal import create_signal_from

# 场景 1：从 CSV 文件加载信号
csv_signal = pd.read_csv("predictions.csv")
signal1 = create_signal_from(csv_signal)

# 场景 2：从 Excel 文件加载信号
excel_signal = pd.read_excel("predictions.xlsx")
signal2 = create_signal_from(excel_signal)

# 场景 3：使用配置字典创建
signal_config = {
    "class": "SignalWCache",
    "module_path": "qlib.backtest.signal",
    "signal": csv_signal
}
signal3 = create_signal_from(signal_config)

# 场景 4：动态选择信号来源
def get_signal_by_type(signal_type, data):
    """
    根据类型创建信号对象

    Args:
        signal_type: 'precomputed', 'model', 'config'
        data: 对应的数据或配置

    Returns:
        Signal 对象
    """
    if signal_type == 'precomputed':
        return create_signal_from(data)
    elif signal_type == 'model':
        model, dataset = data
        return create_signal_from((model, dataset))
    elif signal_type == 'config':
        return create_signal_from(data)
    else:
        raise ValueError(f"未知的信号类型: {signal_type}")

# 使用
signal = get_signal_by_type('precomputed', csv_signal)
```

### 示例 4：结合策略使用

```python
import qlib
from qlib.backtest.signal import SignalWCache, create_signal_from
from qlib.backtest.executor import Executor
from qlib.backtest.strategy import BaseStrategy

class SignalBasedStrategy(BaseStrategy):
    """基于信号的交易策略"""

    def __init__(self, signal, top_n=10):
        super().__init__()
        self.signal = create_signal_from(signal)
        self.top_n = top_n

    def generate_trade_decision(self, execute_result=None):
        # 获取当前时间段
        start_time = self.trade_calendar.get_trade_start()
        end_time = self.trade_calendar.get_trade_end()

        # 获取信号
        signal_data = self.signal.get_signal(start_time, end_time)

        if signal_data is None or len(signal_data) == 0:
            return self.get_default_trade_decision()

        # 选择信号最高的股票
        top_stocks = signal_data.nlargest(self.top_n)

        # 生成等权配置
        target_weight = {inst: 1.0 / self.top_n for inst in top_stocks.index}

        # 返回交易决策
        return self._generate_order_from_target(target_weight)

# 使用示例
if __name__ == "__main__":
    import pandas as pd

    # 初始化 QLib
    qlib.init(provider_uri="~/.qlib/qlib_data/cn_data", region="cn")

    # 准备信号数据
    signal_data = pd.Series(...)  # 你的预测数据

    # 创建策略
    strategy = SignalBasedStrategy(signal=signal_data, top_n=20)

    # 创建执行器
    executor = Executor(
        time_range="2020-01-01 -- 2020-12-31",
        execute_strategy=strategy
    )

    # 运行回测
    portfolio = executor.run()
```

### 示例 5：多策略信号组合

```python
import pandas as pd
from qlib.backtest.signal import SignalWCache

class CombinedSignal:
    """组合多个信号源"""

    def __init__(self, signals, weights):
        """
        Args:
            signals: Signal 对象列表
            weights: 权重列表，和 signals 长度相同
        """
        self.signals = signals
        self.weights = weights
        assert len(signals) == len(weights)
        assert abs(sum(weights) - 1.0) < 1e-6

    def get_signal(self, start_time, end_time):
        """获取组合信号"""
        combined_signal = None

        for signal, weight in zip(self.signals, self.weights):
            # 获取单个信号
            signal_data = signal.get_signal(start_time, end_time)

            if signal_data is None:
                continue

            # 加权
            weighted_signal = signal_data * weight

            # 累加
            if combined_signal is None:
                combined_signal = weighted_signal
            else:
                combined_signal = combined_signal.add(weighted_signal, fill_value=0)

        return combined_signal

# 使用示例
signal1 = SignalWCache(signal_data1)  # 动量信号
signal2 = SignalWCache(signal_data2)  # 价值信号
signal3 = SignalWCache(signal_data3)  # 质量信号

# 组合信号：40%动量 + 30%价值 + 30%质量
combined_signal = CombinedSignal(
    signals=[signal1, signal2, signal3],
    weights=[0.4, 0.3, 0.3]
)

# 在策略中使用
def on_trading_day(start_time, end_time):
    current_signal = combined_signal.get_signal(start_time, end_time)
    # 根据组合信号进行决策
    ...
```

---

## 信号频率处理

### 重采样机制

`SignalWCache` 使用 `"last"` 方法进行信号重采样，这意味着：

1. **信号频率高于决策频率**：如果信号每分钟更新一次，而策略每天决策一次，则使用当天的最后一条信号
2. **信号频率低于决策频率**：如果信号每天更新一次，而策略每小时决策一次，则所有小时的决策都使用该天的同一条信号

**示例：**

```python
from qlib.backtest.signal import SignalWCache
import pandas as pd

# 创建每分钟频率的信号
minute_signals = pd.Series(...)
signal = SignalWCache(minute_signals)

# 策略每天决策
# 获取 2020-01-01 的信号（会使用当天最后一条分钟信号）
daily_signal = signal.get_signal(
    pd.Timestamp('2020-01-01 09:30:00'),
    pd.Timestamp('2020-01-01 15:00:00')
)
```

---

## 注意事项

1. **数据格式**：确保信号数据使用正确的双重索引格式（instrument, datetime）
2. **时间对齐**：信号的时间索引应与交易日历对齐
3. **空值处理**：如果没有信号，`get_signal()` 返回 None，需要在策略中处理
4. **在线更新**：`ModelSignal._update_model()` 方法尚未实现，需要在线更新时需要自行实现
5. **信号频率**：注意信号频率与决策频率的匹配问题

---

## 相关模块

- `qlib.model.base.BaseModel`：模型基类
- `qlib.data.dataset.Dataset`：数据集类
- `qlib.data.dataset.utils.convert_index_format`：索引格式转换
- `qlib.utils.resam.resam_ts_data`：时间序列重采样
