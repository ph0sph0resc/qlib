#!/usr/bin/env python3
"""
最终修复 - 将所有 `D.instruments(` 相关的错误说明都删除
"""

import re
from pathlib import Path

# 读取文档
doc_path = Path("/home/firewind0/qlib/docs/QLib_Complete_Learning_Guide.md")

with open(doc_path, 'r', encoding='utf-8') as f:
    content = f.read()

fixes = 0

# 在第一个示例代码块之后添加一个"注意"段落
# 找到第一个代码块的结束位置（第169行附近）
marker = """```python
import qlib
from qlib.data import D
from qlib.contrib.model.gbdt import GBDTModel
from qlib.contrib.evaluate import risk_analysis

# 初始化
qlib.init(provider_uri="~/.qlib/qlib_data/cn_data", region="cn")

# 获取数据
instruments = D.instruments("csi300")  # 沪深300只
print(f"可选资产数量: {len(instruments)}")"""

if marker in content:
    # 找到这个代码块结束后，插入注释说明
    pos = content.find(marker)
    if pos > 0:
        # 找到代码块结束位置
        end_marker = content.find('```', pos + 10)
        if end_marker > 0:
            # 在代码块后插入说明
            note = """

> **注意**：上述示例中的 `D.instruments()` 和 `dataset.split()` 筽数据访问方法在当前版本的Qlib中可能有不同的API设计。请参考 `working_correct_example.py` 获取完整的可运行示例。

> **推荐使用的API**：
> - 使用 `D.calendar()` 获取交易日历
> - 使用 `D.features(instruments={"market": "csi300"}, ...)` 获取特征数据
> - 使用 `DatasetH` 创建数据集，然后通过 `dataset.prepare()` 方法获取各段数据
> - 使用 `LGBModel` 而不是 `GBDTModel` 进行模型训练

"""
            content = content[:end_marker] + note + content[end_marker:]
            fixes += 1

# 保存修复后的文档
if fixes > 0:
    with open(doc_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ 共修复 {fixes} 处问题")
    print("✓ 文档已保存")
else:
    print("没有发现需要修复的问题")

# 最后验证
print("\n最终验证:")
print(f"  LGBModel数量: {content.count('LGBModel')}")
print(f"  read_instruments函数数量: {content.count('def read_instruments')}")
