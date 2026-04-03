# `highfreq_provider.py`

## 模块概述

`qlib.contrib.data.highfreq_provider` 模块提供了高频数据的统一提供者类 \`HighFreqProvider\`。该类封装了高频数据生成、预处理和缓存管理的完整流程。

高频数据（如 1分钟数据）相比日线数据具有以下特点：
- 数据量更大（每日约 240 个数据点）
- 包含更多细节信息
- 需要特殊的数据处理和存储策略

## 类说明

### HighFreqProvider

高频数据提供者，统一管理高频数据的生成和访问。

#### 构造方法

\`\`\`python
def __init__(
    self,
    start_time: str,            # 总数据开始时间
    end_time: str,              # 总数据结束时间
    train_end_time: str,         # 训练集结束时间
    valid_start_time: str,       # 验证集开始时间
    valid_end_time: str,         # 验证集结束时间
    test_start_time: str,         # 测试集开始时间
    qlib_conf: dict,            # Qlib 配置
    feature_conf: dict,           # 特征配置
    label_conf: Optional[dict] = None,    # 标签配置
    backtest_conf: dict = None,  # 回测配置
    freq: str = "1min",          # 数据频率
    **kwargs,
)
\`\`\`

**参数说明：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| \`start_time\` | str` | 是 | 总数据范围的开始时间 |
| \`end_time\` | str | 是 | 总数据范围的结束时间 |
| \`train_end_time\` | str | 是 | 训练集的结束时间 |
| \`valid_start_time\` | str | 是 | 验证集的开始时间 |
| \`valid_end_time\` | str | 是 | 验证集的结束时间 |
| \`test_start_time\` | str | 是 | 测试集的开始时间 |
| \`qlib_conf\` | dict | 是 | Qlib 初始化配置 |
| \`feature_conf\` | dict | 是 | 特征数据集配置 |
| \`label_conf\` | dict | 否 | 标签数据集配置 |
| \`backtest_conf\` | dict | 否 | 回测数据集配置 |
| \`freq\` | str | 否 | 数据频率，默认 "1min" |

**时间分割示例：**

\`\`\`python
{
    "start_time": "2020-01-01",    # 总开始
    "end_time": "2023-12-31",      # 总结束
    "train_end_time": "2021-12-31",  # 训练结束
    "valid_start_time": "2022-01-01", # 验证开始
    "valid_end_time": "2022-12-31",   # 验证结束
    "test_start_time": "2023-01-01",  # 测试开始
}
# 训练集: start_time ~ train_end_time
# 验证集: valid_start_time ~ valid_end_time
# 测试集: test_start_time ~ end_time
\`\`\`

#### 重要方法

##### \`get_pre_datasets()\`

生成用于预测的训练、验证和测试数据集。

**返回值：**

\`\`\`python
(
    {
        "train": "path/to/train_feature.pkl",
        "valid": "path/to/valid_feature.pkl",
        "test": "path/to/test_feature.pkl"
    },
    {
        "train": "path/to/train_label.pkl",
        "valid": "path/to/valid_label.pkl",
        "test": "path/to/test_label.pkl"
    }
)
\`\`\`

**功能：**
- 检查是否已存在缓存
- 如果不存在，生成数据集并保存
- 返回特征和标签的路径字典

##### \`get_backtest(**kwargs)\`

生成回测数据集。

**参数：**
- \`**kwargs\`：额外的回测参数

##### \`_init_qlib(qlib_conf)\`

初始化 Qlib 环境。

**功能：**
- 加载自定义操作符（高频相关）
- 配置缓存
- 设置区域参数

##### \`_prepare_calender_cache()\`

预加载交易日历缓存。

**功能：**
- 利用 Linux 的写时复制（copy-on-write）特性
- 避免在子进程中重复计算日历
- 加速数据处理流程

##### \`_gen_data(config, datasets)\`

生成数据集并缓存。

**参数：**
- \`config\`：数据集配置（包含 \`path\` 字段）
- \`datasets\`：要生成的数据集列表 ["train", "valid", "test"]

**流程：**
1. 检查缓存文件是否存在
2. 如果存在，从磁盘加载
3. 如果不存在，生成数据集并保存
4. 返回请求的数据集

##### \`_gen_dataset(config)\`

生成完整的数据集对象（包含所有分割）。

##### \`_gen_day_dataset(config, conf_type)\`

按天生成数据集。

**参数：**
- \`config\`：数据集配置
- \`conf_type\`：配置类型（"backtest" 或其他）

**功能：**
- 为每个交易日生成独立的数据集文件
- 使用并行处理加速生成
- 文件命名：\`{path}{date}.pkl\`

##### \`_gen_stock_dataset(config, conf_type)\`

按股票生成数据集。

**参数：**
- \`config\`：数据集配置
- \`conf_type\`：配置类型

**功能：**
- 为每只股票生成独立的数据集文件
- 使用并行处理加速生成
- 文件命名：\`{path}{stock_code}.pkl\`

## 使用示例

### 基本使用

\`\`\`python
from qlib.contrib.data.highfreq_provider import HighFreqProvider

# 配置数据提供者
provider = HighFreqProvider(
    start_time="2020-01-01",
    end_time="2023-12-31",
    train_end_time="2021-12-31",
    valid_start_time="2022-01-01",
    valid_end_time="2022-12-31",
    test_start_time="2023-01-01",
    qlib_conf={
        "provider_uri": "~/.qlib/qlib_data/cn_data_1min",
        "region": "cn",
    },
    feature_conf={
        "class": "HighFreqDataset",
        "module_path": "qlib.contrib.data.dataset",
        "kwargs": {
            # 高频数据集配置
        },
        "path": "data/hf_features.pkl"
    },
    label_conf={
        "class": "HighFreqDataset",
        "module_path": "qlib.contrib.data.dataset",
        "kwargs": {
            # 标签配置
        },
        "path": "data/hf_labels.pkl"
    },
    freq="1min"
)

# 获取训练、验证、测试数据集
feature_paths, label_paths = provider.get_pre_datasets()

print(f"特征数据路径: {feature_paths}")
print(f"标签数据路径: {label_paths}")

# 加载数据
import pickle
with open(feature_paths["train"], "rb") as f:
    train_features = pickle.load(f)
\`\`\`

### 生成回测数据

\`\`\`python
# 配置回测数据
provider = HighFreqProvider(
    # ... 其他配置
    backtest_conf={
        "class": "HighFreqDataset",
        "module_path": "qlib.contrib.data.dataset",
        "kwargs": {...},
        "path": "data/hf_backtest.pkl"
    }
)

# 生成回测数据
provider.get_backtest()
\`\`\`

### 按天生成数据集

\`\`\`python
# 配置数据集
config = {
    "class": "HighFreqDataset",
    "module_path": "qlib.contrib.data.dataset",
    "kwargs": {
        "handler": {...},
        "segments": {...},
    },
    "path": "data/hf_daily/"
}

provider = HighFreqProvider(...)

# 按天生成（并行处理）
provider._gen_day_dataset(config, conf_type="train")
# 生成文件：data/hf_daily/2020-01-01.pkl
#          data/hf_daily/2020-01-02.pkl
#          ...
\`\`\`

### 按股票生成数据集

\`\`\`python
# 按股票生成（并行处理）
provider._gen_stock_dataset(config, conf_type="train")
# 生成文件：data/hf_stock/000001.pkl
#          data/hf_stock/000002.pkl
#          ...
\`\`\`

## 数据流程图

\`\`\`mermaid
graph TD
    A[HighFreqProvider] --> B{检查缓存}
    B -->|缓存存在| C[从磁盘加载]
    B -->|缓存不存在| D[初始化 Qlib]
    D --> E[预加载日历]
    E --> F[创建数据集]
    F --> G[准备数据]
    G --> H[保存到磁盘]
    
    C --> I[返回数据]
    H --> I
    
    F --> F1[按天生成]
    F --> F2[按股票生成]
    
    F1 --> J[并行处理]
    F2 --> J
\`\`\`

## 性能优化

1. **缓存机制**：
   - 自动检测和利用已生成的数据
   - 避免重复计算

2. **并行处理**：
   - 使用 \`joblib.Parallel\` 实现多进程
- 按天或按股票并行生成
   - 默认 8 个进程（按天）或 32 个进程（按股票）

3. **日历缓存**：
   - 利用 Linux 写时复制特性
   - 子进程共享日历数据
   - 减少内存占用

4. **分片存储**：
   - 按天或按股票独立存储
   - 支持增量更新
   - 减少单文件大小

## 配置示例

### 完整配置示例

\`\`\`python
from qlib.contrib.data.highfreq_provider import HighFreqProvider

provider = HighFreqProvider(
    # 时间配置
    start_time="2020-01-01",
    end_time="2023-12-31",
    train_end_time="2021-12-31",
    valid_start_time="2022-01-01",
    valid_end_time="2022-12-31",
    test_start_time="2023-01-01",
    
    # Qlib 配置
    qlib_conf={
        "provider_uri": "~/.qlib/qlib_data/cn_data_1min",
        "region": "cn",
        "redis_port": None,
        "expression_cache": None,
    },
    
    # 特征配置
    feature_conf={
        "class": "HighFreqDataset",
        "module_path": "qlib.contrib.data.dataset",
        "kwargs": {
            "handler": {
                "class": "HighFreqHandler",
                "module_path": "qlib.contrib.data.highfreq_handler",
                "kwargs": {
                    "instruments": "csi300",
                    "start_time": "2020-01-01",
                    "end_time": "2023-12-31",
                }
            },
            "segments": {
                "train": ("2020-01-01", "2021-12-31"),
                "valid": ("2022-01-01", "2022-12-31"),
                "test": ("2023-01-01", "2023-12-31"),
            }
        },
        "path": "checkpoints/hf_features.pkl"
    },
    
    # 标签配置
    label_conf={
        "class": "HighFreqDataset",
        "module_path": "qlib.contrib.data.dataset",
        "kwargs": {
            "handler": {
                "class": "HighFreqHandler",
                "module_path": "qlib.contrib.data.highfreq_handler",
                "kwargs": {
                    "instruments": "csi300",
                    "start_time": "2020-01-01",
                    "end_time": "2023-12-31",
                }
            },
            "segments": {...}
        },
        "path": "checkpoints/hf_labels.pkl"
    },
    
    # 数据频率
    freq="1min"
)
\`\`\`

## 注意事项

1. **时间配置**：
   - 确保时间范围连续且合理
   - 训练集、验证集、测试集不应重叠
   - \`train_end_time\` 和 \`valid_start_time\` 之间可以有间隔

2. **内存管理**：
   - 高频数据量大，注意内存限制
   - 使用分片存储减少单文件大小
   - 考虑使用按天或按股票存储策略

3. **并行处理**：
   - 并行数根据 CPU 核心数调整
   - 注意文件 I/O 限制
   - Windows 和 macOS 不支持写时复制优化

4. **缓存策略**：
   - 首次生成耗时较长
   - 后续使用会很快（从缓存加载）
   - 清除缓存需要手动删除文件

5. **自定义操作符**：
   - 高频数据需要特殊操作符
   - 已内置：DayLast, FFillNan, BFillNan, Date, Select, IsNull, IsInf, Cut
   - 可通过 \`qlib_conf\` 添加自定义操作符

## 相关模块

- \`qlib.contrib.data.highfreq_handler\`：高频数据处理器
- \`qlib.contrib.data.highfreq_processor\`：高频数据处理器
- \`qlib.contrib.ops.high_freq\`：高频操作符

## 参考资源

- [Qlib 高频数据处理](https://qlib.readthedocs.io/en/latest/component/data.html#high-frequency-data)
- [高频数据示例](https://github.com/microsoft/qlib/tree/main/examples/high_freq)
