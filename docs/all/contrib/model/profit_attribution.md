# profit_attribution 模块详细文档

## 模块概述

`profit_attribution` 模块提供了投资组合利润归因分析的功能，主要用于分析投资组合相对于基准组合的超额收益来源。该模块实现了经典的 Brinson 归因分析方法kt。

### 主要功能

- 获取基准组合的股票权重分布
- 分解投资组合权重到不同分组（行业、市值等）
- Brinson 利润归因分析，将超额收益分解为：
  - RAA (Allocation Effect)：配置效应
  - RSS (Selection Effect)：选股效应
  - RIN (Interaction Effect)：交互效应
  - RTotal：总超额收益

### 注意

该模块当前**维护不佳**，使用时请注意。

---

## 函数文档

### get_benchmark_weight

获取基准组合的股票权重分布。

**函数签名：**
```python
def get_benchmark_weight(
    bench,
    start_date=None,
    end_date=None,
    path=None,
    freq="day",
)
```

**参数说明：**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `bench` | str | 必填 | 基准指数代码（如 'SH000905'） |
| `start_date` | str/datetime | None | 开始日期 |
| `end_date` | str/datetime | None | 结束日期 |
| `path` | str/Path | None | 权重文件路径。默认使用配置路径 |
| `freq` | str | "day" | 频率，默认为日线 |

**返回值：**
- 类型：`pandas.DataFrame`
- 说明：基准组合的权重分布
  - 每一行对应一个交易日
  - 每一列对应一个股票
  - 每个单元格表示该股票在该日的权重

**使用示例：**
```python
from qlib.backtest.profit_attribution import get_benchmark_weight

# 获取中证500基准的权重分布
bench_weight = get_benchmark_weight(
    bench="SH000905",
    start_date="2020-01-01",
    end_date="2020-12-31",
    freq="day"
)

print(bench_weight.head())
```

---

### get_stock_weight_df

从回测结果的 positions 中提取股票权重分布。

**函数签名：**
```python
def get_stock_weight_df(positions)
```

**参数说明：**

| 参数 | 类型 | 说明 |
|------|------|------|
| `positions` | dict | 回测结果产生的持仓字典，key为日期，value为Position对象或字典 |

**返回值：**
- 类型：`pandas.DataFrame`
- 说明：持仓的权重分布DataFrame
  - 索引为日期
  - 列为股票代码
  - 值为该股票在组合中的权重

**使用示例：**
```python
from qlib.backtest.profit_attribution import get_stock_weight_df

# 假设 positions 是回测产生的持仓字典
stock_weight_df = get_stock_weight_df(positions)

print(stock_weight_df.head())
```

---

### decompose_portofolio_weight

按分组分解投资组合的权重。

**函数签名：**
```python
def decompose_portofolio_weight(stock_weight_df, stock_group_df)
```

**参数说明：**

| 参数 | 类型 | 说明 |
|------|------|------|
| `stock_weight_df` | DataFrame | 投资组合的权重DataFrame<br>- 每行对应一个交易日<br>- 每列对应一个股票<br>- 值为权重 |
| `stock_group_df` | DataFrame | 肂票分组DataFrame<br>- 每行对应一个交易日<br>- 每列对应一个股票<br>- 值为分组ID（如行业代码） |

**返回值：**
- 类型：`(dict, dict)`
- 说明：返回两个字典
  - 第一个字典 `group_weight`：每个组的权重，key为分组ID，value为Series（按日期）
  - 第二个字典 `stock_weight_in_group`：组内股票的权重，key为分组ID，value为DataFrame

**数据示例：**

stock_weight_df 示例：
```
code        SH600004  SH600006  SH600017  SH600022
date
2016-01-05  0.001543  0.001570  0.002732  0.001320
2016-01-06  0.001538  0.001569  0.002770  0.001417
```

stock_group_df 示例（行业）：
```
instrument  SH600000  SH600004  SH600005
datetime
2016-01-05  801780.0  801170.0  801040.0
2016-01-06  801780.0  801170.0  801040.0
```

**使用示例：**
```python
from qlib.backtest.profit_attribution import decompose_portofolio_weight

# 分解组合权重到行业分组
group_weight, stock_weight_in_group = decompose_portofolio_weight(
    stock_weight_df,
    stock_group_df
)

# 查看每个行业的权重分布
for group_id, weight_series in group_weight.items():
    print(f"行业 {group_id}:")
    print(weight_series.head())
```

---

### decompose_portofolio

分解投资组合，计算分组权重和分组收益。

**函数签名：**
```python
def decompose_portofolio(stock_weight_df, stock_group_df, stock_ret_df)
```

**参数说明：**

| 参数 | 类型 | 说明 |
|------|------|------|
| `stock_weight_df` | DataFrame | 投资组合的权重DataFrame<br>- 每行对应一个交易日<br>- 每列对应一个股票<br>- 值为权重 |
| `stock_group_df` | DataFrame | 股票分组DataFrame<br>- 每行对应一个交易日<br>- 每列对应一个股票<br>- 值为分组ID |
| `stock_ret_df` | DataFrame | 股票收益DataFrame<br>- 每行对应一个交易日<br>- 每列对应一个股票<br>- 值为收益率 |

**返回值：**
- 类型：`(DataFrame, DataFrame)`
- 说明：返回两个DataFrame
  - `group_weight_df`：各分组的权重DataFrame（按日期）
  - `group_ret_df`：各分组的收益DataFrame（按日期）

**数据示例：**

stock_ret_df 示例：
```
instrument  SH600000  SH600004  SH600005
datetime
2016-01-05  0.007795  0.022070  0.099099
2016-01-06 -0.032597 -0.075205 -0.098361
```

**使用示例：**
```python
from qlib.backtest.profit_attribution import decompose_portofolio

# 分解组合，计算分组权重和收益
group_weight_df, group_ret_df = decompose_portofolio(
    stock_weight_df,
    stock_group_df,
    stock_ret_df
)

print("分组权重：")
print(group_weight_df.head())
print("\n分组收益：")
print(group_ret_df.head())
```

---

### get_daily_bin_group

在一天内将基准组合的股票按值分箱分组。

**函数签名：**
```python
def get_daily_bin_group(bench_values, stock_values, group_n)
```

**参数说明：**

| 参数 | 类型 | 说明 |
|------|------|------|
| `bench_values` | Series | 基准组合中股票的值（如市值、PE等），索引为股票代码 |
| `stock_values` | Series | 投资组合中股票的值，索引为股票代码 |
| `group_n` | int | 分箱数量 |

**返回值：**
- 类型：`pandas.Series`
- 说明：与 stock_values 大小和索引相同的Series
  - 值为分组ID（箱号）
  - 第1个分组包含最大的值

**分组逻辑：**
- 根据基准组合的值的百分位数确定分箱边界
- 将投资组合的股票放入对应的箱中
- 值最大的股票进入第1个箱

**使用示例：**
```python
from qlib.backtest.profit_attribution import get_daily_bin_group
import pandas as pd

# 创建示例数据
bench_values = pd.Series([100, 200, 300, 400, 500],
                         index=['SH600000', 'SH600004', 'SH600005', 'SH600006', 'SH600007'])
stock_values = pd.Series([150, 250, 350, 450, 550],
                         index=['SH600000', 'SH600004', 'SH600005', 'SH600006', 'SH600007'])

# 分成5个箱
stock_group = get_daily_bin_group(bench_values, stock_values, group_n=5)

print(stock_group)
```

---

### get_stock_group

获取股票分组信息。

**函数签名：**
```python
def get_stock_group(stock_group_field_df, bench_stock_weight_df, group_method, group_n=None)
```

**参数说明：**

| 参数 | 类型 | 说明 |
|------|------|------|
| `stock_group_field_df` | DataFrame | 股票分组字段DataFrame（如行业、市值） |
| `bench_stock_weight_df` | DataFrame | 基准组合的股票权重DataFrame |
| `group_method` | str | 分组方法：`'category'` 或 `'bins'` |
| `group_n` | int | None | 分箱数量，仅在 `group_method='bins'` 时使用 |

**返回值：**
- 类型：`pandas.DataFrame`
- 说明：股票分组DataFrame

**分组方法说明：**
- `'category'`：直接使用分组字段的值作为分组ID（如行业代码）
- `'bins'`：将分组字段的值分箱，每个箱作为一个分组

**使用示例：**
```python
from qlib.backtest.profit_attribution import get_stock_group

# 使用行业分类（category方法）
stock_group = get_stock_group(
    stock_group_field_df=industry_df,
    bench_stock_weight_df=bench_weight_df,
    group_method='category'
)

# 使用市值分箱（bins方法）
stock_group = get_stock_group(
    stock_group_field_df=market_value_df,
    bench_stock_weight_df=bench_weight_df,
    group_method='bins',
    group_n=5  # 分成5个箱
)
```

---

### brinson_pa

执行 Brinson 利润归因分析。

**函数签名：**
```python
def brinson_pa(
    positions,
    bench="SH000905",
    group_field="industry",
    group_method="category",
    group_n=None,
    deal_price="vwap",
    freq="day",
)
```

**参数说明：**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `positions` | dict | 必填 | 回测类产生的持仓字典 |
| `bench` | str | "SH000905" | 用于比较的基准指数代码 |
| `group_field` | str | "industry" | 用于资产配置分组的字段<br>常用：`'industry'`（行业）、`'market_value'`（市值） |
| `group_method` | str | "category" | 分组方法：`'category'` 或 `'bins'` |
| `group_n` | int | None | 分箱数量，仅在 `group_method='bins'` 时使用 |
| `deal_price` | str | "vwap" | 成交价字段，默认为成交量加权平均价 |
| `freq` | str | "day" | 频率，默认为日线 |

**返回值：**
- 类型：`(DataFrame, dict)`
- 说明：返回两个值
  1. **DataFrame**：包含四列的归因分析结果
     - `RAA`：配置效应（Allocation Effect）
     - `RSS`：选股效应（Selection Effect）
     - `RIN`：交互效应（Interaction Effect）
     - `RTotal`：总超额收益
     - 每一行对应一个交易日，值为该日的下一期收益率
  2. **dict**：中间信息，包含以下键：
     - `port_group_ret`：投资组合各分组收益
     - `port_group_weight`：投资组合各分组权重
     - `bench_group_ret`：基准各分组收益
     - `bench_group_weight`：基准各分组权重
     - `stock_group`：股票分组信息
     - `bench_stock_weight`：基准股票权重
     - `port_stock_weight`：投资组合股票权重
     - `stock_ret`：股票收益率

### Brinson 归因分析原理

Brinson 模型将超额收益分解为三个部分：

1. **配置效应（RAA）**
   - 度量投资组合在不同组别之间的配置偏离基准带来的收益

2. **选股效应（RSS）**
   - 度量在相同组别内，投资组合选股优于基准带来的收益

3. **交互效应（RIN）**
   - 度量配置和选股交互作用带来的收益

计算公式：
```
Q1 = Σ(基准组权重 × 基准组收益)
Q2 = Σ(投资组权重 × 基准组收益)
Q3 = Σ(基准组权重 × 投资组收益)
Q4 = Σ(投资组权重 × 投资组收益)

RAA = Q2 - Q1    (Asset Allocation)
RSS = Q3 - Q1    (Stock Selection)
RIN = Q4 - Q3 - Q2 + Q1  (Interaction)
RTotal = Q4 - Q1  (Total Excess Return)
```

**使用示例：**
```python
from qlib.backtest.profit_attribution import brinson_pa

# 假设 positions 是回测产生的持仓字典
result_df, info_dict = brinson_pa(
    positions=positions,
    bench="SH000905",           # 中证500作为基准
    group_field="industry",      # 按行业分组
    group_method="category",     # 使用分类方法
    deal_price="vwap",           # 使用成交量加权平均价
    freq="day"
)

# 查看归因分析结果
print("Brinson 归因分析结果：")
print(result_df.head())

# 计算累计归因
cumulative_result = result_df.add(1).cumprod() - 1
print("\n累计归因效果：")
print(cumulative_result.tail())

# 查看中间信息
print("\n投资组合各行业权重：")
print(info_dict['port_group_weight'].head())
```

**示例输出：**
```
Brinson 归因分析结果：
date        RAA       RSS       RIN    RTotal
2020-01-02  0.0001    0.0005   -0.0002   0.0004
2020-01-03  0.0002    0.0003   -0.0001   0.0004
...

累计归因效果：
date        RAA       RSS       RIN    RTotal
2020-12-31  0.0234    0.0567   -0.0123   0.0678
```

---

## 完整使用流程示例

```python
import qlib
from qlib.backtest.profit_attribution import brinson_pa

# 1. 初始化 QLib
qlib.init(provider_uri="~/.qlib/qlib_data/cn_data", region="cn")

# 2. 运行回测获得 positions
# ... (回测代码省略)

# 3. 执行 Brinson 利润归因分析
result_df, info_dict = brinson_pa(
    positions=positions,
    bench="SH000905",
    group_field="industry",
    group_method="category"
)

# 4. 分析结果
print("每日归因分析：")
print(result_df)

print("\n累计归因效果：")
print(result_df.add(1).cumprod() - 1)

# 5. 查看投资组合的行业配置
print("\n投资组合行业权重（最后一天）：")
last_date = result_df.index[-1]
print(info_dict['port_group_weight'].loc[last_date])
```

---

## 注意事项

1. **模块维护状态**：该模块目前维护不佳，使用时需要谨慎
2. **数据对齐**：确保 positions 的时间范围与基准数据一致
3. **停牌股票处理**：某些停牌股票的属性（如市值）可能为 NaN，代码中使用前向填充处理
4. **收益计算**：该模块中持仓在交易日收盘时调整，因此收益计算可能与回测报告略有差异
5. **基准数据**：需要预先准备基准指数的成分股权重数据

---

## 相关模块

- `qlib.backtest.position.Position`：持仓类
- `qlib.data.D`：数据访问接口
- `qlib.config.C`：配置Qlib
