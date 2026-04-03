# `highfreq_processor.py`

## 模块概述

`qlib.contrib.data.highfreq_processor` 模块提供了高频数据的专用处理器类。这些处理器专门用于处理分钟级别的市场数据，包括数据类型转换和标准化。

该模块主要包含：
- \`HighFreqTrans\`：高频数据类型转换处理器
- \`HighFreqNorm\`：高频数据标准化处理器

## 类说明

### HighFreqTrans

高频数据类型转换处理器，将高频数据转换为指定的数据类型。

#### 构造方法

\`\`\`python
def __'init__'(self, dtype: str = "bool")
\`\`\`

**参数说明：**

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| \`dtype\` | str | "bool" | 目标数据类型（"bool" 或 "float"） |

#### 方法

##### \`fit(df_features)\`

拟合处理器（无操作）。

**参数：**
- \`df_features\`：特征数据

##### \`__call__(df_features)\`

转换数据类型。

**参数：**
- \`df_features\`：特征数据

**返回：**
- 转换后的特征数据

**转换规则：**

\`\`\`python
if dtype == "bool":
    return df_features.astype(np.int8)  # 布尔型转为 int8
else:
    return df_features.astype(np.float32)  # 其他转为 float32
\`\`\`

**使用场景：**
- 将布尔标志转换为整数类型（节省内存）
- 确保所有数据为统一类型（float32）

### HighFreqNorm

高频数据标准化处理器，支持分组标准化和日志转换。

#### 构造方法

\`\`\`python
def __'init__'(
    self,
    fit_start_time: pd.Timestamp,      # 拟合开始时间
    fit_end_time: pd.Timestamp,        # 拟合结束时间
    feature_save_dir: str,            # 统计量保存目录
    norm_groups: Dict[str, int],       # 标准化分组
)
\`\`\`

**参数说明：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| \`fit_start_time\` | pd.Timestamp | 是 | 计算统计量的开始时间 |
| \`fit_end_time\` | pd.Timestamp | 是 | 计算统计量的结束时间 |
| \`feature_save_dir\` | str | 是 | 统计量保存目录 |
| \`norm_groups\` | Dict[str, int] | 是 | 标准化分组配置（特征名: 维度） |

**norm_groups 示例：**

\`\`\`python
norm_groups = {
    "price": 5,      # 5维价格特征
    "volume": 1,     # 1维成交量特征
    "vwap": 1,        # 1维 VWAP 特征
    "bid": 4,         # 4维买盘特征
    "ask": 4,         # 4维卖盘特征
}
\`\`\`

#### 方法

##### \`fit(df_features)\`

拟合处理器，计算并保存统计量。

**参数：**
- \`df_features\`：特征数据

**流程：**

1. 检查是否已存在统计量文件
2. 如果存在，直接返回
3. 提取拟合时间段的数据
4. 对每个特征分组：
   - 如果是成交量特征，先取 \`log1p\`
   - 计算均值并保存
   - 计算标准差并保存
   - 标准化后计算最大值并保存
   - 标准化后计算最小值并保存

**保存的文件：**

- \`{feature}_mean.npy\`：均值
- \`{feature}_std.npy\`：标准差
- \`{feature}_vmax.npy\`：标准化后的最大值
- \`{feature}_vmin.npy\`：标准化后的最小值

##### \`__call__(df_features)\`

应用标准化转换。

**参数：**
- \`df_features\`：特征数据

**返回：**
- 标准化后的特征数据

**流程：**

1. 删除 "date" 索引层级（如果存在）
2. 对每个特征分组：
   - 加载保存的均值和标准差
   - 如果是成交量特征，先取 \`log1p\`
   - 减去均值
   - 除以标准差
3. 填充缺失值为 0

**标准化公式：**

\`\`\`python
# 成交量特征
x = log1p(x)  # x = log(x + 1)
x = (x - mean) / std

# 其他特征
x = (x - mean) / std
\`\`\`

## 使用示例

### 基本使用（HighFreqTrans）

\`\`\`python
from qlib.contrib.data.highfreq_processor import HighFreqTrans
import pandas as pd

# 创建数据
data = pd.DataFrame({
    'feature1': [True, False, True],
    'feature2': [False, False, True],
})

# 转换为 int8
processor = HighFreqTrans(dtype="bool")
processed = processor(data)
print(processed.dtypes)  # int8

# 转换为 float32
processor = HighFreqTrans(dtype="float")
processed = processor(data)
print(processed.dtypes)  # float32
\`\`\`

### 基本使用（HighFreqNorm）

\`\`\`python
from qlib.contrib.data.highfreq_processor import HighFreqNorm
import pandas as pd

# 创建数据
data = pd.DataFrame({
    'price_1': [1.0, 2.0, 3.0, 4.0, 5.0],
    'price_2': [2.0, 4.0, 6.0, 8.0, 10.0],
    'volume_1': [1000, 2000, 3000, 4000, 5000],
}, index=pd.MultiIndex.from_tuples([
    ('stock1', '2020-01-01'),
    ('stock1', '2020-01-02'),
    ('stock1', '2020-01-03'),
    ('stock1', '2020-01-04'),
    ('stock1', '2020-01-05'),
], names=['instrument', 'datetime']))

# 配置标准化分组
norm_groups = {
    'price': 2,     # 2个价格特征
    'volume': 1,    # 1个成交量特征
}

# 创建处理器
processor = HighFreqNorm(
    fit_start_time=pd.Timestamp('2020-01-01'),
    fit_end_time=pd.Timestamp('2020-01-05'),
    feature_save_dir='./norm_stats/',
    norm_groups=norm_groups
)

# 拟合（计算统计量）
processor.fit(data)

# 应用标准化
normalized = processor(data)
print(normalized)
\`\`\`

### 在 DataHandler 中使用

\`\`\`python
from qlib.contrib.data.highfreq_handler import HighFreqHandler
from qlib.contrib.data.highfreq_processor import HighFreqTrans, HighFreqNorm

# 创建数据处理器
handler = HighFreqHandler(
    instruments="csi300",
    start_time="2023-01-01",
    end_time="2023-12-31",
    learn_processors=[
        HighFreqTrans(dtype="float"),           # 类型转换
        HighFreqNorm(
            fit_start_time=pd.Timestamp('2023-01-01'),
            fit_end_time=pd.Timestamp('2023-06-30'),
            feature_save_dir='./norm_stats/',
            norm_groups={
                'price': 5,
                'volume': 1,
            }
        ),                              # 标准化
    ],
)
\`\`\`

### 配置文件中使用

\`\`\`yaml
# workflow_config.yaml
data_handler:
  class: HighFreqHandler
  module_path: qlib.contrib.data.highfreq_handler
  kwargs:
    instruments: csi300
    start_time: 2023-01-01
    end_time: 2023-12-31
    learn_processors:
      - class: HighFreqTrans
        module_path: qlib.contrib.data.highfreq_processor
        kwargs:
          dtype: "float"
      - class: HighFreqNorm
        module_path: qlib.contrib.data.highfreq_processor
        kwargs:
          fit_start_time: 2023-01-01
          fit_end_time: 2023-06-30
          feature_save_dir: ./norm_stats/
          norm_groups:
            price: 5
            volume: 1
\`\`\`

## 处理流程图

\`\`\`mermaid
graph TD
    A[原始高频数据] --> B[HighFreqTrans]
    B --> C[类型转换]
    C --> D[HighFreqNorm]
    D --> E{首次运行?}
    E -->|是| F[fit: 计算统计量]
    E -->|否| G[加载保存的统计量]
    F --> H[保存统计量到文件]
    H --> I[__call__: 应用标准化]
    G --> I
    I --> J[标准化后的数据]
    
    F --> F1[提取拟合时间段数据]
    F1 --> F2[遍历特征分组]
    F2 --> F3[成交量: log1p]
    F2 --> F4[计算均值]
    F2 --> F5[计算标准差]
    F2 --> F6[计算标准化后的极值]
    F3 --> F7[(x - mean) / std]
    F4 --> F7
    F5 --> F7
    F6 --> F7
\`\`\`

## 性能优化

1. **统计量缓存**：
   - 首次拟合后保存到文件
   - 后续直接加载，无需重新计算
   - 显著加速数据加载

2. **分组处理**：
   - 支持多个特征分组独立标准化
   - 不同特征可以有不同的统计特性
   - 便于管理多源数据

3. **内存高效**：
   - 使用 numpy 数组操作
   - 原地修改减少内存复制

4. **对数变换**：
   - 对成交量取 \`log1p\` 减少量级差异
   - 提高数值稳定性

## 注意事项

1. **拟合时间范围**：
   - \`fit_start_time\` 和 \`fit_end_time\` 应在训练集范围内
   - 避免使用未来数据统计量
   - 防止数据泄露

2. **特征分组配置**：
   - 确保所有特征维度总和等于特征总数
   - 特征名称应与实际数据匹配
   - 组内特征共享统计量

3. **统计量保存**：
   - \`feature_save_dir\` 目录需要写权限
   - 统计量文件会覆盖同名文件
   - 更新数据后需重新拟合

4. **数据类型**：
   - \`HighFreqTrans\` 支持 "bool" 和 "float"
   - 布尔型转换为 int8 节省空间
   - 浮点型使用 float32 保持精度

5. **缺失值处理**：
   - 标准化后填充为 0
   - 保持数据维度一致
   - 避免后续计算错误

## 相关模块

- \`qlib.contrib.data.highfreq_handler\`：高频数据处理器
- \`qlib.contrib.data.dataset.processor\`：基础数据处理器

## 参考资源

- [Qlib 数据处理文档](https://qlib.readthedocs.io/en/latest/component/data.html#data-processing)
- [数据标准化方法](https://scikit-learn.org/stable/modules/preprocessing.html)
