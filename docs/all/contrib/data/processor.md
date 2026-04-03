# `processor.py`

## 模块概述

`qlib.contrib.data.processor` 模块提供了 Qlib 中用于数据预处理的处理器类。该模块主要包含 `ConfigSectionProcessor` 类，这是专门为 Alpha158 数据集设计的配置化数据处理器。

该处理器能够对特征和标签进行各种标准化、异常值处理等操作，是 Qlib 数据处理流程中的重要组件。

## 类说明

### ConfigSectionProcessor

`ConfigSectionProcessor` 是一个专门为 Alpha158 数据集设计的数据处理器。它提供了丰富的数据预处理功能，。

#### 构造方法

\`\`\`python
def __init__(self, fields_group=None, **kwargs)
\`\`\`

**参数说明：**

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| \`fields_group\` | str | None | 字段分组名称 |
| \`fillna_feature\` | bool | True | 是否填充特征中的缺失值 |
| \`fillna_label\` | bool | True | 是否填充标签中的缺失值 |
| \`clip_feature_outlier\` | bool | False | 是否裁剪特征异常值 |
| \`shrink_feature_outlier\` | bool | True | 是否收缩特征异常值 |
| \`clip_label_outlier\` | bool | False | 是否裁剪标签异常值 |

#### 数据处理逻辑

不同类型特征的处理策略：

- **标签标准化**: 去均值 -> 除以标准差 -> 可选裁剪 -> 可选填充
- **K线特征（长度）**: 开0.25次方 -> 去中位数 -> 除以MAD*1.4826
- **K线特征（位置）**: 开0.5次方 -> 去中位数 -> 除以MAD*1.4826
- **常规特征**: 去中位数 -> 除以MAD*1.4826
- **波动率特征**: 取对数 -> 去中位数 -> 除以MAD*1.4826
- **R平方特征**: 填充0 -> 去中位数 -> 除以MAD*1.4826
- **最大值特征**: (x-1)开0.5次方 -> 去中位数 -> 除以MAD*1.4826
- **最小值特征**: (1-x)开0.5次方 -> 去中位数 -> 除以MAD*1.4826
- **相关性特征**: 取指数 -> 去中位数 -> 除以MAD*1.4826
- **加权波动率**: 取log1p -> 去中位数 -> 除以MAD*1.4826

## 使用示例

\`\`\`python
from qlib.contrib.data.processor import ConfigSectionProcessor

processor = ConfigSectionProcessor(
    fields_group="feature",
    fillna_feature=True,
    shrink_feature_outlier=True
)

processed_data = processor(data)
\`\`\`

## 注意事项

1. 专门为 Alpha158 数据集设计
2. 未来计划用更简单的处理器组合替换
3. 标准化按日期分组进行，避免数据泄露
