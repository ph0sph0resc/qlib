# profit_attribution.py 模块文档

> **注意**: 该模块未得到良好维护。

## 模块概述

`profit_attribution.py` 模块实现了Brinson收益归因分析，用于分解投资组合的超额收益来源。

该模块主要功能：
- 获取基准指数的权重分布
- 计算投资组合的股票权重
- 将投资组合按行业/市值等分组进行分解
- 实现Brinson收益归因模型

## 主要函数

### 1. get_benchmark_weight()

获取基准指数的股票权重分布。

```python
def get_benchmark_weight(
    bench,
    start_date=None,
    end_date=None,
    path=None,
    freq="day"
)
```

**参数说明：**

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| bench | str | 是 | - | 基准指数代码 |
| start_date | datetime | 否 | None | 开始日期 |
| end_date | datetime | 否 | None | 结束日期 |
| path | Path | 否 | None | 权重文件路径 |
| freq | str | 否 | "day" | 频率 |

**返回值：**
- `pd.DataFrame`: 基准指数的权重分布
  - 每一行对应一个交易日
  - 每一列对应一只股票
  - 每个单元格表示该股票的权重

**数据格式：**
```
code        SH600004  SH600006  SH600017  ...
date
2016-01-05  0.001543  0.001570  0.002732  ...
2016-01-06  0.001538  0.001569  0.002770  ...
...
```

---

### 2. get_stock_weight_df()

将持仓位置转换为股票权重DataFrame。

```python
def get_stock_weight_df(positions)
```

**参数说明：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| positions | dict | 是 | 回测结果的持仓位置 |

**返回值：**
- `pd.DataFrame`: 股票权重分布DataFrame

---

### 3. decompose_portofolio_weight()

将投资组合按分组分解权重。

```python
def decompose_portofolio_weight(
    stock_weight_df,
    stock_group_df
)
```

**参数说明：**

| 参数名 | 类型 | 说明 |
|--------|------|------|
| stock_weight_df | pd.DataFrame | 股票权重DataFrame |
| stock_group_df | pd.DataFrame | 股票分组DataFrame |

**返回值：**
- `group_weight`: dict，每个组的权重Series
- `stock_weight_in_group`: dict，每个组内股票的权重DataFrame

---

### 4. decompose_portofolio()

将投资组合按分组分解，并计算组收益。

```python
def decompose_portofolio(
    stock_weight_df,
    stock_group_df,
    stock_ret_df
)
```

**参数说明：**

| 参数名 | 类型 | 说明 |
|--------|------|------|
| stock_weight_df | pd.DataFrame | 股票权重DataFrame |
| stock_group_df | pd.DataFrame | 股票分组DataFrame |
| stock_ret_df | pd.DataFrame | 股票收益DataFrame |

**返回值：**
- `group_weight_df`: DataFrame，每个组的权重
- `group_ret_df`: DataFrame，每个组的收益

---

### 5. get_daily_bin_group()

将基准股票的值分组到多个分箱中。

```python
def get_daily_bin_group(
    bench_values,
    stock_values,
    group_n
)
```

**参数说明：**

| 参数名 | 类型 | 说明 |
|--------|------|------|
| bench_values | pd.Series | 基准股票的值，index为股票代码 |
| stock_values | pd.Series | 投资组合股票的值，index为股票代码 |
| group_n | int | 分箱数量 |

**返回值：**
- `pd.Series`: 与stock_value相同大小和索引的Series

---

### 6. get_stock_group()

根据指定方法获取股票分组。

```python
def get_stock_group(
    stock_group_field_df,
    bench_stock_weight_df,
    group_method,
    group_n=None
)
```

**参数说明：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| stock_group_field_df | pd.DataFrame | 是 | 股票分组字段DataFrame |
| bench_stock_weight_df | pd.DataFrame | 是 | 基准股票权重DataFrame |
| group_method | str | 是 | 分组方法："category" 或 "bins" |
| group_n | int | 否 | 分箱数量，仅当group_method="bins"时使用。

---

### 7. brinson_pa()

Brinson收益归因分析主函数。

```python
def brinson_pa(
    positions,
    bench="SH000905",
    group_field="industry",
    group_method="category",
    group_n=None,
    deal_price="vwap",
    freq="day"
)
```

**参数说明：**

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| positions | dict | 是 | - | 回测类产生的持仓位置 |
| bench | str | 否 | "SH000905" | 用于比较的基准指数 |
| group_field | str | 否 | "industry" | 用于资产分配的分组字段 |
| group_method | str | 否 | "category" | 分组方法："category" 或 "bins" |
| group_n | int | 否 | None | 分箱数量，仅group_method="bins"时使用 |
| deal_price | str | 否 | "vwap" | 交易价格字段 |
| freq | str | 否 | "day" | 频率 |

**返回值：**
返回两个值：

1. **归因结果DataFrame**，包含以下列：
   - `RAA`: 资产配置超额收益
   - `RSS`: 股票选择超额收益
   - `RIN`: 交互效应超额收益
   - `RTotal`: 总超额收益

2. **中间信息字典**，包含：
   - `port_group_ret`: 投资组合组收益
   - `port_group_weight`: 投资组合组权重
   - `bench_group_ret`: 基准组收益
   - `bench_group_weight`: 基准组权重
   - `stock_group`: 股票分组
   - `bench_stock_weight`: 基准股票权重
   - `port_stock_weight`: 投资组合股票权重
   - `stock_ret`: 股票收益

---

## Brinson收益归因模型

### 原理

Brinson模型将超额收益分解为以下四个部分：

1. **资产配置收益 (RAA)**: 配置权重相对于基准的差异带来的收益
2. **股票选择收益 (RSS)**: 选择股票差异带来的收益
3. **交互收益 (RIN)**: 配置和选择的交互效应
4. **总超额收益 (RTotal)**: 以上三部分的总和

### 计算公式

```
Q1 = Σ(基准组权重 × 基准组收益)
Q2 = Σ(投资组权重 × 基准组收益)
Q3 = Σ(基准组权重 × 投资组收益)
Q4 = Σ(投资组权重 × 投资组收益)

RAA   = Q2 - Q1  # 资产配置超额收益
RSS   = Q3 - Q1  # 股票选择超额收益
RIN   = Q4 - Q3 - Q2 + Q1  # 交互效应
RTotal = Q4 - Q1  # 总超额收益
```

---

## 使用示例

```python
import pandas as pd
from qlib.backtest.profit_attribution import brinson_pa

# 假设 positions 是回测结果
positions = {
    pd.Timestamp("2020-01-01"): {
        "SH600000": 1000,
        "SH600001": 500
    },
    ...
}

# 执行Brinson归因分析
result, info = brinson_pa(
    positions=positions,
    bench="SH000905",  # 中证500
    group_field="industry",
    group_method="category",
    freq="day"
)

# 查看归因结果
print(result.head())
print("\n累计收益:")
print(result.sum())
```

---

##相关模块

- `qlib.backtest.report.py`: 提供回测报告和持仓位置
- `qlib.data.data.Cal`: 提供交易日历功能
- `qlib.data.D`: 提供数据访问接口
