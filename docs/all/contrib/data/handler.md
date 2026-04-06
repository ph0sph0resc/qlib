# `handler.py`

## 模块概述

`qlib.contrib.data.handler` 模块提供了 Qlib 中常用的数据处理器类。数据处理器负责协调整个数据管道，包括数据加载、处理和分割。

该模块主要包含以下处理器：
- \`Alpha360\`：Alpha360 数据处理器
- \`Alpha158\`：Alpha158 数据处理器（最常用）
- \`Alpha360vwap\`：基于 VWAP 的 Alpha360 处理器
- \`Alpha158vwap\`：基于 VWAP 的 Alpha158 处理器

## 类说明

### Alpha360

Alpha360 数据处理器，用于管理 Alpha360 数据集的加载和处理流程。

#### 构造方法

\`\`\`python
def __init__(
    self,
    instruments="csi500",          # 股票池
    start_time=None,              # 开始时间
    end_time=None,                # 结束时间
    freq="day",                  # 数据频率
    infer_processors=[],            # 推理处理器
    learn_processors=[],            # 训练处理器
    fit_start_time=None,           # 拟合开始时间
    fit_end_time=None,             # 拟合结束时间
    filter_pipe=None,             # 过滤管道
    inst_processors=None,           # 仪器处理器
    **kwargs,
)
\`\`\`

**参数说明：**

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| \`instruments\` | str/list | "csi500" | 股票池或股票列表 |
| \`start_time\` | str | None | 数据开始时间 |
| \`end_time\` | str | None | 数据结束时间 |
| \`freq\` | str | "day" | 数据频率（day/1min/5min等） |
| \`infer_processors\` | list | [] | 推理阶段的数据处理器 |
| \`learn_processors\` | list | [] | 训练阶段的数据处理器 |
| \`fit_start_time\` | str | None | 处理器拟合的开始时间 |
| \`fit_end_time\` | str | None | 处理器拟合的结束时间 |
| \`filter_pipe\` | list | None | 数据过滤器管道 |
| \`inst_processors\` | list | None | 仪器级别的处理器 |

#### 默认标签配置

Alpha360 的默认标签：

\`\`\`python
# 预测第二天的收益率相对于第一天的收益率
label = Ref($close, -2)/Ref($close, -1) - 1
\`\`\`

### Alpha158

Alpha158 数据处理器，Qlib 最常用的数据处理器之一。

#### 构造方法

\`\`\`python
def __init__(
    self,
    instruments="csi500",
    start_time=None,
    end_time=None,
    freq="day",
    infer_processors=[],
    learn_processors=_DEFAULT_LEARN_PROCESSORS,  # 默认包含 DropnaLabel 和 CSZScoreNorm
    fit_start_time=None,
    fit_end_time=None,
    process_type=DataHandlerLP.PTYPE_A,  # 处理类型
    filter_pipe=None,
    inst_processors=None,
    **kwargs,
)
\`\`\`

**参数说明：**

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| \`process_type\` | str | PTYPE_A | 处理类型 |

#### 默认处理器

**训练阶段默认处理器：**

\`\`\`python
_DEFAULT_LEARN_PROCESSORS = [
    {"class": "DropnaLabel"},              # 删除标签为空的行
    {"class": "CSZScoreNorm",             # 按日期对标签标准化
     "kwargs": {"fields_group": "label"}}
]
\`\`\`

**推理阶段默认处理器：**

\`\`\`python
_DEFAULT_INFER_PROCESSORS = [
    {"class": "ProcessInf", "kwargs": {}},  # 推理处理
    {"class": "ZScoreNorm", "kwargs": {}},   # Z-score 标准化
    {"class": "Fillna", "kwargs": {}},       # 填充缺失值
]
\`\`\`

#### 特征配置方法

\`\`\`python
def get_feature_config(self):
    conf = {
        "kbar": {},
        "price": {
            "windows": [0],
            "feature": ["OPEN", "HIGH", "LOW", "VWAP"],
        },
        "rolling": {},
    }
    return Alpha158DL.get_feature_config(conf)
\`\`\`

默认生成约 158 个特征。

### Alpha360vwap / Alpha158vwap

基于 VWAP（成交量加权平均价）的标签定义。

#### 标签配置

\`\`\`python
# 使用 VWAP 计算收益率
label = Ref($vwap, -2)/Ref($vwap, -1) - 1
\`\`\`

相较于使用收盘价的版本，VWAP 版本更能反映实际交易价格。

## 使用示例

### 基本使用（Alpha158）

\`\`\`python
from qlib.contrib.data.handler import Alpha158

# 创建数据处理器
handler = Alpha158(
    instruments="csi500",
    start_time="2020-01-01",
    end_time="2023-12-31",
)

# 获取训练数据
train_data = handler.fetch(
    segment="train",
    col_set=["feature", "label"],
)
\`\`\`

### 自定义处理器

\`\`\`python
from qlib.contrib.data.handler import Alpha158
from qlib.contrib.data.processor import ConfigSectionProcessor

# 使用自定义处理器
handler = Alpha158(
    instruments="csi500",
    start_time="2020-01-01",
    end_time="2023-12-31",
    learn_processors=[
        {"class": "DropnaLabel"},
        {"class": "CSZScoreNorm", 
         "kwargs": {"fields_group": "label"}},
        ConfigSectionProcessor(fillna_feature=True),
    ],
)
\`\`\`

### 使用 VWAP 标签

\`\`\`python
from qlib.contrib.data.handler import Alpha158vwap

# 使用 VWAP 标签
handler = Alpha158vwap(
    instruments="csi300",
    start_time="2020-01-01",
    end_time="2023-12-31",
)
\`\`\`

### 在配置文件中使用

\`\`\`yaml
# workflow_config.yaml
data_handler:
  class: Alpha158
  module_path: qlib.contrib.data.handler
  kwargs:
    instruments: csi500
    start_time: 2020-01-01
    end_time: 2023-12-31
    learn_processors:
      - class: DropnaLabel
      - class: CSZScoreNorm
        kwargs:
          fields_group: label
\`\`\`

### 数据分割

\`\`\`python
from qlib import init
from qlib.workflow import R

# 初始化 Qlib
init(provider_uri="~/.qlib/qlib_data/cn_data", region="cn")

# 配置数据处理器
config = {
    "class": "Alpha158",
    "module_path": "qlib.contrib.data.handler",
    "kwargs": {
        "instruments": "csi500",
        "start_time": "2020-01-01",
        "end_time": "2023-12-31",
    }
}

# 准备数据
handler = R.get_data_handler(**config)
handler.setup_data(
    config(
        {
            "train": ("2020-01-01", "2021-12-31"),
            "valid": ("2022-01-01", "2022-12-31"),
            "test": ("2023-01-01", "2023-12-31"),
        },
        dump_all=True,
    )
)

# 获取数据
train_data = handler.fetch(col_set=["feature", "label"], segment="train")
\`\`\`

## 数据处理流程

\`\`\`mermaid
graph TD
    A[原始市场数据] --> B[DataLoader]
    B --> C[特征工程]
    C --> D[标签计算]
    D --> E[学习处理器]
    E --> F[推理处理器]
    F --> G[训练数据]
    F --> H[推理数据]
    
    E --> E1[DropnaLabel]
    E --> E2[CSZScoreNorm]
    
    F --> F1[ProcessInf]
    F --> F2[ZScoreNorm]
    F --> F3[Fillna]
\`\`\`

## Alpha360 vs Alpha158 对比

| 特性 | Alpha360 | Alpha158 |
|------|----------|----------|
| 特征数量 | 360 | ~158 |
| 特征类型 | 原始价格序列 | 技术指标 |
| 适用模型面 | LSTM、GRU 等序列模型 | GBDT、MLP 等非序列模型 |
| 数据量 | 较小 | 较大 |
| 计算复杂度 | 低 | 高 |
| 解释性 | 较强 | 较强 |

## 注意事项

1. **数据时间范围**：
   - 确保时间范围在交易日历内
   - 训练集、验证集、测试集不应有时间重叠

2. **处理器拟合**：
   - 如果使用需要拟合的处理器，需指定 \`fit_start_time\` 和 \`fit_end_time\`
   - 避免数据泄露，拟合时间应在训练时间范围内

3. **内存使用**：
   - Alpha158 特征较多，注意内存占用
   - 可以使用 \`fit_start_time\` 和 \`fit_end_time\` 分批加载

4. **标签定义**：
   - 确保标签表达式与模型预测目标一致
   - VWAP 版本适合实际交易场景

## 相关模块

- \`qlib.data.dataset.handler\`：基础数据处理器
- \`qlib.contrib.data.loader\`：数据加载器
- \`qlib.contrib.data.processor\`：数据预处理器

## 参考资源

- [Qlib 数据处理文档](https://qlib.readthedocs.io/en/latest/component/data.html#data-handling)
- [Alpha158 示例](https://github.com/microsoft/qlib/tree/main/examples/benchmarks/LightGBM)
- [Alpha360 示例](https://github.com/microsoft/qlib/tree/main/examples/benchmarks/Alpha360)
