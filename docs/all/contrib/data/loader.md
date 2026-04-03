# `loader.py`

## 模块概述

`qlib.contrib.data.loader` 模块提供了 Qlib 中常用的数据加载器类。数据加载器负责定义如何从原始数据中提取特征和标签，是数据管道的起点。

该模块主要包含两个经典的数据加载器：
- `Alpha360DL`：Alpha360 数据加载器，提供60天的历史价格序列
- `Alpha158DL`：Alpha158 数据加载器，提供丰富的技术指标特征

## 类说明

### Alpha360DL

Alpha360 数据加载器，用于获取包含过去60天历史价格数据的特征序列。

#### 特征说明

Alpha360 提供了过去60天的原始价格序列，包括：
- **价格数据**：Close, Open, High, Low
- **成交量**：Volume
- **成交均价**：VWAP

#### 数据标准化

所有价格和成交量数据都进行了归一化处理：
- 价格除以当天的收盘价
- 成交量除以当天的成交量（加小常数防止除零）

归一化后的数据：
- \`CLOSE0\` = 1（当天收盘价归一化）
- \`VOLUME0\` = 1（当天成交量归一化）

#### 特征配置

| 特征名称 | 数量 | 说明 |
|----------|------|------|
| \`CLOSE0-59\` | 60 | 收盘价序列（CLOSE0=1） |
| \`OPEN0-59\` | 60 | 开盘价序列 |
| \`HIGH0-59\` | 60 | 最高价序列 |
| \`LOW0-59\` | 60 | 最低价序列 |
| \`VWAP0-59\` | 60 | 成交均价序列 |
| \`VOLUME0-59\` | 60 | 成交量序列（VOLUME0=1） |

**总特征数：360**

### Alpha158DL

Alpha158 数据加载器，用于获取丰富的技术指标特征。

#### 特征配置方法

\`\`\`python
def get_feature_config(
    config={
        "kbar": {},
        "price": {"windows": [0], "feature": ["OPEN", "HIGH", "LOW", "VWAP"]},
        "rolling": {},
    }
)
\`\`\`

**配置参数：**

| 参数 | 说明 |
|------|------|
| \`kbar\` | 是否使用硬编码的K线特征 |
| \`price.windows\` | 使用的滞后期（如 [0, 1, 2]） |
| \`price.feature\` | 使用的价格字段 |
| \`volume.windows\` | 成交量滞后期 |
| \`rolling.windows\` | 滚动窗口大小 |
| \`rolling.include\` | 包含的操作符 |
| \`rolling.exclude\` | 排除的操作符 |

#### 技术指标分类

1. **K线特征**（9个）：KMID, KLEN, KMID2, KUP, KUP2, KLOW, KLOW2, KSFT, KSFT2
2. **价格变化率**（ROC）：N日变化率
3. **移动平均**（MA）：N日移动平均
4. **统计特征**：STD, BETA, RSQR, RESI
5. **极值特征**：MAX, MIN, QTLU, QTLD, RSV
6. **动量特征**（Aroon）：IMAX, IMIN, IMXD
7. **相关性特征**：CORR, CORD
8. **方向统计**：CNTP, CNTN, CNTD
9. **累计涨跌**（类似RSI）：SUMP, SUMN, SUMD
10. **成交量特征**：VMA, VSTD, WVMA
11. **成交量方向**：VSUMP, VSUMN, VSUMD

## 使用示例

\`\`\`python
from qlib.contrib.data.loader import Alpha158DL, Alpha360DL

# Alpha360 加载器
loader360 = Alpha360DL()
fields, names = loader360.get_feature_config()

# Alpha158 加载器
loader158 = Alpha158DL()
fields, names = loader158.get_feature_config()
\`\`\`

## 参考资源

- [ROC 指标](https://www.investopedia.com/terms/r/rateofchange.asp)
- [MA 指标](https://www.investopedia.com/ask/answers/071414/whats-difference-between-moving-average-and-weighted-moving-average.asp)
- [RSI 指标](https://www.investopedia.com/terms/r/rsi.asp)
- [Aroon 指标](https://www.investopedia.com/terms/a/aroon.asp)
