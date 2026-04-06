# qlib.rl.data.integration 模块文档

## 模块概述

`qlib.rl.data.integration` 模块用于将 NeuTrader 与 Qlib 集成，以运行现有项目。

**注意**：
- 此处的实现是临时的（adhoc）
- 未来应该设计更统一通用的实现

## 主要函数

### init_qlib

```python
def init_qlib(qlib_config: dict) -> None
```

**说明**：初始化 Qlib 所需的资源，包括数据目录、特征列等。

**参数**：
- `qlib_config`: Qlib 配置字典

**配置参数**：

| 键 | 说明 | 示例 |
|----|------|------|
| `provider_uri_day` | 日线数据目录 | `Path("data/qlib_1d")` |
| `provider_uri_1min` | 1分钟线数据目录 | `Path("data/qlib_1min")` |
| `provider_uri_5min` | 5分钟线数据目录（可选） | `Path("data/qlib_5min")` |
| `feature_root_dir` | 特征根目录 | `Path("data/qlib_handler_stock")` |
| `feature_columns_today` | 今天的特征列 | `["$open", "$high", "$low", ...]` |
| `feature_columns_yesterday` | 昨天的特征列 | `["$open_1", "$high_1", "$low_1", ...]` |

**配置示例**：

```python
qlib_config = {
    "provider_uri_day": DATA_ROOT_DIR / "qlib_1d",
    "provider_uri_1min": DATA_ROOT_DIR / "qlib_1min",
    "feature_root_dir": DATA_ROOT_DIR / "qlib_handler_stock",
    "feature_columns_today": [
        "$open", "$high", "$low", "$close", "$vwap",
        "$bid", "$ask", "$volume",
        "$bidV", "$bidV1", "$bidV3", "$bidV5",
        "$askV", "$askV1", "$askV3", "$askV5",
    ],
    "feature_columns_yesterday": [
        "$open_1", "$high_1", "$low_1", "$close_1", "$vwap_1",
        "$bid_1", "$ask_1", "$volume_1",
        "$bidV_1", "$bidV1_1", "$bidV3_1", "$bidV5_1",
        "$askV_1", "$askV1_1", "$askV3_1", "$askV5_1",
    ],
}

init_qlib(qlib_config)
```

**实现逻辑**：
1. 构建 `provider_uri_map`，包含所有粒度的数据目录
2. 调用 `qlib.init()` 初始化 Qlib
3. 配置日历提供者和特征提供者
4. 使用本地的 FileCalendarStorage 和 FileFeatureStorage
5. 注册自定义算子（DayLast, FFillNan, BFillNan, Date, Select, IsNull, IsInf, Cut, DayCumsum）

## 使用示例

### 基本初始化

```python
import qlib
from pathlib import Path
from qlib.rl.data.integration import init_qlib

# 定义数据根目录
DATA_ROOT_DIR = Path("/path/to/data")

# 配置 Qlib
qlib_config = {
    "provider_uri_day": DATA_ROOT_DIR / "qlib_1d",
    "provider_uri_1min": DATA_ROOT_DIR / "qlib_1min",
    "feature_root_dir": DATA_ROOT_DIR / "qlib_handler_stock",
    "feature_columns_today": [
        "$open", "$high", "$low", "$close", "$vwap", "$volume"
    ],
    "feature_columns_yesterday": [
        "$open_1", "$high_1", "$low_1", "$close_1", "$vwap_1", "$volume_1"
    ],
}

# 初始化 Qlib
init_qlib(qlib_config)
```

### 完整工作流

```python
import qlib
from pathlib import Path
from qlib.rl.data.integration import init_qlib
from qlib.data.dataset import Dataset
from qlib.data.dataset.loader import QlibDataLoader

# 1. 初始化 Qlib
init_qlib(qlib_config)

# 2. 创建数据集
config = {
    "class": "DatasetH",
    "module_path": "qlib.data.dataset",
    "kwargs": {
        "handler": {
            "class": "Alpha360",
            "module_path": "qlib.contrib.data.handler",
            "kwargs": {
                "fit_start": "2010-01-01",
                "fit_end": "2015-12-31",
                "instruments": "all",
            },
        },
        "segments": {
            "train": ("2010-01-01", "2014-12-31"),
            "valid": ("2015-01-01", "2015-12-31"),
            "test": ("2016-01-01", "2016-12-31"),
        },
    },
}

dataset = Dataset(config)

# 3. 使用数据集
for segment in dataset.segments:
    data_loader = QlibDataLoader(config, segment)
    for data in data_loader:
        # 处理数据
        pass
```

### 与 NeuTrader 集成

```python
from qlib.rl.data.integration import init_qlib

# NeuTrader 配置
neutrader_config = {
    "qlib_config": {
        "provider_uri_day": "/path/to/qlib_1d",
        "provider_uri_1min": "/path/to/qlib_1min",
        "feature_columns_today": [...],
        "feature_columns_yesterday": [...],
    },
    "model_config": {...},
    "training_config": {...},
}

# 初始化 Qlib
init_qlib(neutrader_config["qlib_config"])

# 运行 NeuTrader 工作流
# ...
```

## 自定义算子

该模块注册了以下自定义算子：

| 算子 | 说明 |
|------|------|
| `DayLast` | 获取每天的最后值 |
| `FFillNan` | 前向填充 NaN |
| `BFillNan` | 后向填充 NaN |
| `Date` | 提取日期 |
| `Select` | 选择特定值 |
| `IsNull` | 检查是否为 null |
| `IsInf` | 检查是否为 inf |
| `Cut` | 数据分箱 |
| `DayCumsum` | 每日累加 |

这些算子来自 `qlib.contrib.ops.high_freq` 模块。

## Qlib 初始化参数

| 参数 | 说明 |
|------|------|
| `region` | 区域，默认为 REG_CN |
| `auto_mount` | 是否自动挂载，设置为 False |
| `custom_ops` | 自定义算子列表 |
| `expression_cache` | 表达式缓存，设置为 None |
| `calendar_provider` | 日历提供者配置 |
| `feature_provider` | 特征提供者配置 |
| `provider_uri` | 数据提供者 URI 映射 |
| `kernels` | 内核数，设置为 1 |
| `redis_port` | Redis 端口，设置为 -1（禁用） |
| `clear_mem_cache` | 是否清除内存缓存，设置为 False（保留缓存以提高性能） |

## 注意事项

1. **临时实现**：此模块是临时的实现，未来可能会重构
2. **配置完整性**：确保所有必需的配置参数都已提供
3. **路径处理**：路径可以是 `str` 或 `Path` 对象
4. **缓存保留**：`clear_mem_cache=False` 是为了在多次调用 `init_qlib` 时保留缓存
5. **算子依赖**：确保所有自定义算子都已正确导入

## 相关文档

- [base.md](./base.md) - 基类定义
- [native.md](./native.md) - 原生数据处理
- [pickle_styled.md](./pickle_styled.md) - Pickle 格式数据处理
