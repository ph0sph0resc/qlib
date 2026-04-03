# analysis_model/__init__.py

## 模块概述

`qlib.contrib.report.analysis_model.__init__.py` 是模型分析模块的初始化文件，导出了模型性能分析的核心函数。

## 导出函数

```python
from .analysis_model_performance import model_performance_graph

__all__ = ["model_performance_graph"]
```

## 导出函数说明

### model_performance_graph

**位置**: `analysis_model.analysis_model_performance.model_performance_graph`

**说明**: 全面分析模型预测性能，生成分组收益分析、IC 分析、自相关分析、换手率分析等多种性能指标的可视化图表。

**主要用途**:
- 评估预测模型的准确性
- 分析分组收益情况
- 评估模型的时序特性
- 识别模型的交易特征

## 使用示例

### 基础导入

```python
from qlib.contrib.report import analysis_model as am
```

### 导入函数

```python
from qlib.contrib.report.analysis_model import model_performance_graph
```

### 完整分析流程

```python
import qlib
import pandas as pd
from qlib.data import D
from qlib.contrib.report import analysis_model as am

# 初始化 Qlib
qlib.init(provider_uri='~/.qlib/qlib_data/cn_data', region='cn')

# 准备数据
instruments = D.instruments('csi500')
fields = [
    'Ref($close, -2)/Ref($close, -1) - 1',  # 标签
    '$volume / Ref($volume, 1)',    # 特征
    'Ref($close, 1)/$close',      # 特征
]
dates = pd.date_range('2018-01-01', '2020-12-31')

data = D.features(instruments, fields, dates[0], dates[-1])

# 假设有预测得分 pred_score
# ... 获取预测得分 ...

# 准备分析数据
test_data = data.loc['2020-01-01':]
pred_label = pd.DataFrame({
    'score': pred_score.values,
    'label': test_data.iloc[:, 0].values
}, index=pred_score.index)

# 生成所有默认图表
am.model_performance_graph(pred_label)
```

### 自定义分析

```python
# 只生成分组收益和 IC 分析
am.model_performance_graph(
    pred_label,
    graph_names=["group_return", "pred_ic"]
)

# 使用 10 个分组
am.model_performance_graph(
    pred_label,
    N=10,
    graph_names=["group_return"]
)

# 反转预测得分
am.model_performance_graph(
    pred_label,
    reverse=True,
    graph_names=["group_return"]
)
```

### 返回图表对象

```python
# 返回图表对象
figures = am.model_performance_graph(
    pred_label,
    show_notebook=False
)

# 遍历所有图表
for i, fig in enumerate(figures):
    fig.update_layout(title=f'模型性能图表 {i+1}')
    fig.show()
```

## 函数快速参考

### 主要参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| pred_label | pd.DataFrame | 必需 | 预测得分和标签数据 |
| lag | int | 1 | 滞后期数，用于自相关计算 |
| N | int | 5 | 分组数量 |
| reverse | bool | False | 是否反转得分 |
| rank | bool | False | 是否计算 Rank IC |
| graph_names | list | ["group_return", "pred_ic", "pred_autocorr"] | 图表类型列表 |
| show_notebook | bool | True | 是否在 Notebook 中显示 |
| show_nature_day | bool | False | 是否显示非交易日 |

### 支持的图表类型

| 图表名称 | 说明 |
|---------|------|
| group_return | 分组收益分析 |
| pred_ic | 预测 IC 分析 |
| pred_autocorr | 自相关分析 |
| pred_turnover | 换手率分析 |

## 常见使用场景

### 场景 1: 快速评估模型

```python
# 生成所有默认图表
am.model_performance_graph(pred_label)
```

### 场景 2: 重点关注分组收益

```python
# 只生成分组收益分析
am.model_performance_graph(
    pred_label,
    graph_names=["group_return"]
)
```

### 场景 3: 评估预测能力

```python
# 生成分组收益和 IC 分析
am.model_performance_graph(
    pred_label,
    graph_names=["group_return", "pred_ic"]
)
```

### 场景 4: 分析交易特征

```python
# 生成自相关和换手率分析
am.model_performance_graph(
    pred_label,
    graph_names=["pred_autocorr", "pred_turnover"]
)
```

### 场景 5: 完整性能分析

```python
# 生成所有类型的图表
am.model_performance_graph(
    pred_label,
    graph_names=[
        "group_return",
        "pred_ic",
        "pred_autocorr",
        "pred_pred_turnover"
    ]
)
```

## 注意事项

1. **数据格式**: pred_label 必须包含 score 和 label 两列
2. **索引格式**: 索引必须是 MultiIndex，包含 instrument 和 datetime
3. **标签定义**: label 通常使用未来收益率，如 Ref($close, -1)/$close - 1
4. **分组数量**: N 值通常设置为 5、10 或 3
5. **反转得分**: 如果模型预测负向关系，使用 reverse=True
