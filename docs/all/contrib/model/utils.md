# utils 模块详细文档

## 模块概述

`utils` 模块提供了回测框架的核心工具类和辅助函数，主要包括：

1. **TradeCalendarManager**：交易日历管理器，用于管理交易时间范围和步进
2. **BaseInfrastructure****CommonInfrastructure****LevelInfrastructure**：基础设施类，用于在不同层级之间共享资源和对象
3. **get_start_end_idx**：辅助函数，用于获取决策级别的索引范围

这些工具类构成了 QLib 回测框架的基础架构，支持多层级策略执行。

---

## 类文档

### TradeCalendarManager

交易日历管理器，用于管理交易日历和交易步进。被 `BaseStrategy` 和 `BaseExecutor` 使用。

#### 初始化方法

**函数签名：**
```python
def __init__(
    self,
    freq: str,
    start_time: Union[str, pd.Timestamp] = None,
    end_time: Union[str, pd.Timestamp] = None,
    level_infra: LevelInfrastructure | None = None,
) -> None
```

**参数说明：**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `freq` | str | 必填 | 交易频率（如 'day', '1min'），也是每个交易步骤的交易时间 |
| `start_time` | str/pd.Timestamp | None | 交易日历的闭区间开始时间。如果为 None，必须在交易前调用 `reset()` |
| `end_time` | str/pd.Timestamp | None | 交易时间范围的闭区间结束时间。如果为 None，必须在交易前调用 `reset()` |
| `level_infra` | LevelInfrastructure | None | 级别基础设施对象 |

**使用示例：**
```python
import pandas as pd
from qlib.backtest.utils import TradeCalendarManager

# 创建日历管理器
calendar = TradeCalendarManager(
    freq="day",
    start_time="2020-01-01",
    end_time="2020-12-31"
)

print(f"交易步数: {calendar.get_trade_len()}")
print(f"当前步: {calendar.get_trade_step()}")
```

---

#### 主要方法

##### reset

重置交易日历。

**函数签名：**
```python
def reset(
    self,
    freq: str,
    start_time: Union[str, pd.Timestamp] = None,
    end_time: Union[str, pd.Timestamp] = None,
) -> None
```

**参数说明：** 同 `__init__` 方法

**功能说明：**
- 设置交易频率和时间范围
- 获取完整的交易日历
- 定位开始和结束索引
- 初始化交易步数：
  - `self.trade_len`：总交易步数
  - `self.trade_step`：已完成的交易步数（初始为 0）
  - `trade_step` 的取值范围：`[0, 1, 2, ..., trade_len - 1]`

**使用示例：**
```python
# 重置日历
calendar.reset(
    freq="1min",
    start_time="2020-01-01 09:30:00",
    end_time="2020-01-01 15:00:00"
)
```

##### finished

检查交易是否完成。

**函数签名：**
```python
def finished(self) -> bool
```

**返回值：**
- `True`：交易已完成（`trade_step >= trade_len`）
- `False`：交易未完成

**使用场景：**
- 在调用 `strategy.generate_decisions()` 和 `executor.execute()` 之前应该检查

**使用示例：**
```python
while not calendar.finished():
    # 执行交易逻辑
    current_start, current_end = calendar.get_step_time()
    execute_trade(current_start, current_end)
    calendar.step()
```

##### step

推进到下一个交易步。

**函数签名：**
```python
def step(self) -> None
```

**异常：**
- 如果日历已完成，抛出 `RuntimeError`

**使用示例：**
```python
# 推进到下一步
calendar.step()

# 检查是否完成
if calendar.finished():
    print("交易完成的所有步骤")
```

##### get_freq

获取交易频率。

**函数签名：**
```python
def get_freq(self) -> str
```

**返回值：**
- 类型：`str`
- 说明：交易频率（如 'day', '1min'）

##### get_trade_len

获取总交易步数。

**函数签名：**
```python
def get_trade_len(self) -> int
```

**返回值：**
- 类型：`int`
- 说明：总交易步数

##### get_trade_step

获取当前已完成的交易步数。

**函数签名：：**
```python
def get_trade_step(self) -> int
```

**返回值：**
- 类型：`int`
- 说明：当前已完成的交易步数

##### get_step_time

获取指定交易步的时间范围。

**函数签名：**
```python
def get_step_time(self, trade_step: int | None = None, shift: int = 0) -> Tuple[pd.Timestamp, pd.Timestamp]
```

**参数说明：**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `trade_step` | int | None | 交易步数。如果为 None，使用当前步 |
| `shift` | int | 0 | 时间偏移<br>- `shift == 0`：返回当前步的时间范围<br>- `shift > 0`：返回前 shift 步的时间范围<br>- `shift < 0`：返回后 |shift| 步的时间范围 |

**返回值：**
- 类型：`Tuple[pd.Timestamp, pd.Timestamp]`
- 说明：交易时间范围的（开始时间，结束时间）

**关于时间端点：**
- QLib 使用闭区间表示时间序列数据
- 返回的结束时间点会减去 1 秒（使用 `epsilon_change`）
- QLib 支持到分钟级别的决策执行，所以 1 秒小于任何交易时间间隔

**使用示例：**
```python
# 获取当前步的时间范围
start, end = calendar.get_step_time()
print(f"当前步: {start} 到 {end}")

# 获取前一步的时间范围
prev_start, prev_end = calendar.get_step_time(shift=1)
print(f"前一步: {prev_start} 到 {prev_end}")

# 获取第 5 步的时间范围
step5_start, step5_end = calendar.get_step_time(trade_step=5)
print(f"第5步: {step5_start} 到 {step5_end}")
```

##### get_data_cal_range

获取数据日历的范围索引。

**函数签名：**
```python
def get_data_cal_range(self, rtype: str = "full") -> Tuple[int, int]
```

**参数说明：**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `rtype` | str | "full" | 范围类型<br>- `"full"`：返回当天的完整决策范围<br>- `"step"`：返回当前步的范围 |

**返回值：**
- 类型：`Tuple[int, int]`
- 说明：相对于当天开始的（开始索引，结束索引）

**假设条件：**
1. `common_infra` 中 exchange 的频率与数据日历相同
2. 用户希望数据索引按天取模（即 240 分钟）

**使用示例：**
```python
# 获取当天的完整决策范围
day_start_idx, day_end_idx = calendar.get_data_cal_range(rtype="full")
print(f"当天范围: {day_start_idx} 到 {day_end_idx}")

# 获取当前步的范围
step_start_idx, step_end_idx = calendar.get_data_cal_range(rtype="step")
print(f"当前步范围: {step_start_idx} 到 {step_end_idx}")
```

##### get_all_time

获取交易的开始时间和结束时间。

**函数签名：**
```python
def get_all_time(self) -> Tuple[pd.Timestamp, pd.Timestamp]
```

**返回值：**
- 类型：`Tuple[pd.Timestamp, pd.Timestamp]`
- 说明：（start_time, end_time）

##### get_range_idx

获取涉及指定时间范围的索引（两端闭区间）。

**函数签名：**
```python
def get_range_idx(self, start_time: pd.Timestamp, end_time: pd.Timestamp) -> Tuple[int, int]
```

**参数说明：**

| 参数 | 类型 | 说明 |
|------|------|------|
| `start_time` | pd.Timestamp | 开始时间 |
| `end_time` | pd.Timestamp | 结束时间 |

**返回值：**
- 类型：`Tuple[int, int]`
- 说明：范围索引（左索引，右索引），两端都是闭区间

**使用示例：**
```python
# 获取 2020年1月的交易步索引范围
month_start = pd.Timestamp('2020-01-01')
month_end = pd.Timestamp('2020-01-31')
start_idx, end_idx = calendar.get_range_idx(month_start, month_end)
print(f"2020年1月对应步索引: {start_idx} 到 {end_idx}")
```

##### __repr__

字符串表示。

**函数签名：**
```python
def __repr__(self) -> str
```

**返回格式：**
```
class: TradeCalendarManager; start_time[start_index]~end_time[end_index]: [trade_step/trade_len]
```

---

### BaseInfrastructure

基础设施基类，用于在不同层级之间共享资源。

#### 初始化方法

**函数签名：**
```python
def __init__(self, **kwargs: Any) -> None
```

**参数说明：**
- `**kwargs`：任意关键字参数，传递给 `reset_infra()`

---

#### 主要方法

##### get_support_infra

获取支持的基础设施名称集合（抽象方法）。

**函数签名：**
```python
@abstractmethod
def get_support_infra(self) -> Set[str]
```

**返回值：**
- 类型：`Set[str]`
- 说明：支持的基础设施名称集合

**异常：**
- 必须由子类实现

##### reset_infra

重置基础设施属性。

**函数签名：**
```python
def reset_infra(self, **kwargs: Any) -> None
```

**参数说明：**
- `**kwargs`：键值对，设置基础设施属性

**功能说明：**
- 只设置在 `get_support_infra()` 中声明的属性
- 如果传入不支持的属性名称，发出警告

**使用示例：**
```python
infra = CommonInfrastructure()
infra.reset_infra(
    trade_account=account,
    trade_exchange=exchange
)
```

##### get

获取指定的基础设施对象。

**函数签名：**
```python
def get(self, infra_name: str) -> Any
```

**参数说明：**
- `infra_name`：基础设施名称

**返回值：**
- 类型：`Any`
- 说明：基础设施对象，如果不存在则发出警告

**使用示例：**
```python
exchange = infra.get("trade_exchange")
account = infra.get("trade_account")
```

##### has

检查是否包含指定的基础设施。

**函数签名：**
```python
def has(self, infra_name: str) -> bool
```

**参数说明：**
- `infra_name`：基础设施名称

**返回值：**
- 类型：`bool`
- 说明：是否包含该基础设施

**使用示例：**
```python
if infra.has("trade_calendar"):
    calendar = infra.get("trade_calendar")
```

##### update

从另一个基础设施对象更新当前对象。

**函数签名：**
```python
def update(self, other: BaseInfrastructure) -> None
```

**参数说明：**
- `other`：另一个基础设施对象

**功能说明：**
- `other` 支持的属性中存在的值会更新到当前对象

**使用示例：**
```python
common_infra = CommonInfrastructure()
common_infra.reset_infra(trade_account=account)

level_infra = LevelInfrastructure()
level_infra.reset_infra(trade_calendar=calendar)

# 用 common_infra 更新 level_infra
level_infra.update(common_infra)
```

---

### CommonInfrastructure

公共基础设施类，继承自 `BaseInfrastructure`。

#### 支持的基础设施

| 名称 | 说明 |
|------|------|
| `trade_account` | 交易账户对象 |
| `trade_exchange` | 交易交易所对象 |

**使用示例：**
```python
from qlib.backtest.utils import CommonInfrastructure

# 创建公共基础设施
common_infra = CommonInfrastructure()
common_infra.reset_infra(
    trade_account=account,
    trade_exchange=exchange
)

# 获取对象
account = common_infra.get("trade_account")
exchange = common_infra.get("trade_exchange")
```

---

### LevelInfrastructure

级别基础设施类，继承自 `BaseInfrastructure`。由执行器创建，然后共享给同一层级的策略。

#### 支持的基础设施

| 名称 | 说明 |
|------|------|
| `trade_calendar` | 交易日历管理器 |
| `sub_level_infra` | 子级别基础设施<br>**注意**：仅在 `_init_sub_trading` 之后可用 |
| `common_infra` | 公共基础设施对象 |
| `executor` | 执行器对象 |

#### 方法

##### reset_cal

重置交易日历管理器。

**函数签名：**
```python
def reset_cal(
    self,
    freq: str,
    start_time: Union[str, pd.Timestamp, None],
    end_time: Union[str, pd.Timestamp, None],
) -> None
```

**参数说明：**

| 参数 | 类型 | 说明 |
|------|------|------|
| `freq` | str | 交易频率 |
| `start_time` | str/pd.Timestamp | None | 开始时间 |
| `end_time` | str/pd.Timestamp | None | 结束时间 |

**功能说明：**
- 如果已存在 `trade_calendar`，则重置它
- 否则，创建新的 `TradeCalendarManager`

**使用示例：**
```python
from qlib.backtest.utils import LevelInfrastructure

level_infra = LevelInfrastructure()
level_infra.reset_cal(
    freq="day",
    start_time="2020-01-01",
    end_time="2020-12-31"
)
```

##### set_sub_level_infra

设置子级别基础设施，使跨多层级访问日历更方便。

**函数签名：**
```python
def set_sub_level_infra(self, sub_level_infra: LevelInfrastructure) -> None
```

**参数说明：**
- `sub_level_infra`：子级别基础设施对象

**使用示例：**
```python
# 父级别基础设施
parent_infra = LevelInfrastructure()

# 子级别基础设施
child_infra = LevelInfrastructure()

# 设置子级别
parent_infra.set_sub_level_infra(child_infra)
```

---

## 函数文档

### get_start_end_idx

获取内部策略的决策级别索引范围限制的辅助函数。

**函数签名：**
```python
def get_start_end_idx(trade_calendar: TradeCalendarManager, outer_trade_decision: BaseTradeDecision) -> Tuple[int, int]
```

**参数说明：**

| 参数 | 类型 | 说明 |
|------|------|------|
| `trade_calendar` | TradeCalendarManager | 交易日历管理器 |
| `outer_trade_decision` | BaseTradeDecision | 外部策略的交易决策 |

**返回值：**
- 类型：`Tuple[int, int]`
- 说明：（开始索引，结束索引）

**功能说明：**
- 首先尝试调用 `outer_trade_decision.get_range_limit(inner_calendar=trade_calendar)`
- 如果抛出 `NotImplementedError`，则返回整个日历范围 `(0, trade_calendar.get_trade_len() - 1)`

**注意：**
- 此函数不适用于订单级别（order-level）
- 仅适用于决策级别（decision-level）

**使用示例：**
```python
from qlib.backtest.utils import get_start_end_idx

# 获取内部策略的索引范围
start_idx, end_idx = get_start_end_idx(
    trade_calendar=calendar,
    outer_trade_decision=outer_decision
)

# 限制内部策略的执行范围
for step in range(start_idx, end_idx + 1):
    # 执行内部策略
    execute_inner_strategy(step)
```

---

## 完整使用流程示例

### 示例 1：使用 TradeCalendarManager 进行回测循环

```python
import pandas as pd
from qlib.backtest.utils import TradeCalendarManager

# 创建日历管理器
calendar = TradeCalendarManager(
    freq="day",
    start_time="2020-01-01",
    end_time="2020-12-31"
)

print(f"总交易步数: {calendar.get_trade_len()}")
print(f"日历信息: {calendar}")

# 回测循环
step_count = 0
while not calendar.finished():
    # 获取当前步的时间范围
    start_time, end_time = calendar.get_step_time()

    print(f"\n步骤 {step_count}:")
    print(f"  时间范围: {start_time} 到 {end_time}")

    # 执行交易逻辑
    # execute_strategy(start_time, end_time)

    # 推进到下一步
    calendar.step()
    step_count += 1

print(f"\n回测完成，共执行 {step_count} 步")
```

### 示例 2：使用基础设施类管理共享资源

```python
from qlib.backtest.utils import CommonInfrastructure, LevelInfrastructure

# 创建交易账户和交易所（假设已有）
# account = ...
# exchange = ...

# 创建公共基础设施
common_infra = CommonInfrastructure()
common_infra.reset_infra(
    trade_account=account,
    trade_exchange=exchange
    )

print("公共基础设施:")
print(f"  包含 trade_account: {common_infra.has('trade_account')}")
print(f"  包含 trade_exchange: {common_infra.has('trade_exchange')}")

# 获取对象
account_obj = common_infra.get("trade_account")
exchange_obj = common_infra.get("trade_exchange")

# 创建级别基础设施
level_infra = LevelInfrastructure()
level_infra.reset_cal(
    freq="day",
    start_time="2020-01-01",
    end_time="2020-12-31"
)

# 添加公共基础设施
level_infra.update(common_infra)

print("\n级别基础设施:")
print(f"  包含 trade_calendar: {level_infra.has('trade_calendar')}")
print(f"  包含 common_infra: {level_infra.has('common_infra')}")
print(f"  包含 trade_account: {level_infra.has('trade_account')}")
```

### 示例 3：多层级日历管理

```python
import pandas as pd
from qlib.backtest.utils import TradeCalendarManager, LevelInfrastructure

# 创建父级基础设施
parent_infra = LevelInfrastructure()
parent_infra.reset_cal(
    freq="day",
    start_time="2020-01-01",
    end_time="2020-12-31"
)

# 创建子级基础设施
child_infra = LevelInfrastructure()
child_infra.reset_cal(
    freq="1min",
    start_time="2020-01-01 09:30:00",
    end_time="2020-01-01 15:00:00"
)

# 设置子级别
parent_infra.set_sub_level_infra(child_infra)

# 获取各级日历
parent_calendar = parent_infra.get("trade_calendar")
child_calendar = child_infra.get("trade_calendar")

print(f"父级日历: {parent_calendar}")
print(f"子级日历: {child_calendar}")
```

### 示例 4：时间范围查询和索引转换

```python
import pandas as pd
from qlib.backtest.utils import TradeCalendarManager

# 创建日历
calendar = TradeCalendarManager(
    freq="day",
    start_time="2020-01-01",
    end_time="2020-12-31"
)

# 获取特定日期范围的步索引
date1 = pd.Timestamp('2020-01-15')
date2 = pd.Timestamp('2020-01-31')
idx1, idx2 = calendar.get_range_idx(date1, date2)
print(f"日期范围 {date1.date()} 到 {date2.date()} 对应步索引: {idx1} 到 {idx2}")

# 获取步的时间范围
start, end = calendar.get_step_time(trade_step=10)
print(f"第10步的时间范围: {start.date()} 到 {end.date()}")

# 获取前一步的时间范围
prev_start, prev_end = calendar.get_step_time(trade_step=10, shift=1)
print(f"第9步的时间范围: {prev_start.date()} 到 {prev_end.date()}")
```

### 示例 5：在策略中使用基础设施

```python
from qlib.backtest.utils import LevelInfrastructure

class MyStrategy:
    """自定义策略类"""

    def __init__(self, level_infra: LevelInfrastructure):
        self.level_infra = level_infra

    def execute(self):
        # 获取交易日历
        calendar = self.level_infra.get("trade_calendar")

        # 获取交易所
        common_infra = self.level_infra.get("common_infra")
        exchange = common_infra.get("trade)exchange")

        # 获取账户
        account = common_infra.get("trade_account")

        # 执行策略逻辑
        while not calendar.finished():
            start, end = calendar.get_step_time()

            # 获取当前价格
            price = exchange.get_deal_price("SH600000", start, end)

            # 根据价格做出决策
            if price > 100:
                # 买入逻辑
                pass

            calendar.step()

# 使用策略
# level_infra = ...  # 预先创建
# strategy = MyStrategy(level_infra)
# strategy.execute()
```

### 示例 6：外部决策限制内部策略的范围

```python
from qlib.backtest.utils import get_start_end_idx, TradeCalendarManager
import pandas as pd

# 创建日历
calendar = TradeCalendarManager(
    freq="1min",
    start_time="2020-01-01 09:30:00",
    end_time="2020-01-01 15:00:00"
)

# 假设有一个外部决策
# outer_decision = ...

# 获取内部策略的执行范围
start_idx, end_idx = get_start_end_idx(
    trade_calendar=calendar,
    outer_trade_decision=outer_decision
)

print(f"内部策略执行范围: {start_idx} 到 {end_idx}")

# 限制内部策略的执行
for step in range(start_idx, end_idx + 1):
    step_start, step_end = calendar.get_step_time(trade_step=step)
    # 执行内部策略
    execute_inner_step(step_start, step_end)
```

---

## 架构说明

### 层级关系

```
LevelInfrastructure (父级)
├── trade_calendar: TradeCalendarManager
├── common_infra: CommonInfrastructure
│   ├── trade_account
│   └── trade_exchange
├── executor
└── sub_level_infra: LevelInfrastructure (子级)
    ├── trade_calendar: TradeCalendarManager
    ├── common_infra: CommonInfrastructure (共享)
    ├── executor
    └── sub_level_infra: ... (可以继续嵌套)
```

### 数据流

1. **Executor** 创建 `LevelInfrastructure`
2. `LevelInfrastructure` 包含：
   - `TradeCalendarManager`：管理时间
   - `CommonInfrastructure`：共享账户和交易所
   - `executor`：引用回溯
3. **Strategy** 通过 `LevelInfrastructure` 访问：
   - 日历信息
   - 交易所和账户
   - 子级别的日历（如果有多层级策略）

---

## 注意事项

1. **时间端点**：QLib 使用闭区间表示时间，`get_step_time()` 返回的结束时间会减去 1 秒
2. `trade_step`：表示已完成的步数，初始为 0，范围是 `[0, trade_len - 1]`
3. **基础设施属性**：只有在 `get_support_infra()` 中声明的属性才会被接受
4. **跨层级访问**：`set_sub_level_infra()` 使跨多层级访问日历更方便
5. **索引范围**：`get_start_end_idx()` 仅适用于决策级别，不适用于订单级别

---

## 相关模块

- `qlib.data.data.Cal`：日历类
- `qlib.utils.time.epsilon_change`：时间微调函数
- `qlib.backtest.decision.BaseTradeDecision`：交易决策基类
