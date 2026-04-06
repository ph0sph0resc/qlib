#!/usr/bin/env python3
"""修复Qlib学习文档中的代码示例"""

import re
import sys
from pathlib import Path

# 读取文档
doc_path = Path("/home/firewind0/qlib/docs/QLib_Complete_Learning_Guide.md")
with open(doc_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 修复规则
fixes = [
    # 1. 修复错误的模型导入
    (r'from qlib\.contrib\.model\.gbdt import GBDTModel',
     'from qlib.contrib.model.gbdt import LGBModel'),

    # 2. 修复模型类名
    (r'GBDTModel\(',
     'LGBModel('),

    # 3. 修复D.instruments用法 - 不能直接作为列表使用
    (r'instruments = D\.instruments\("(.*?)"\)',
     """# 读取股票列表（从文件读取）
def read_instruments(market="\\1"):
    inst_file = Path("~/.qlib/qlib_data/cn_data/instruments").expanduser() / f"{market}.txt"
    with open(inst_file) as f:
        lines = f.read().strip().split('\\n')
        instruments = [line.split('\\t')[0] for line in lines if line.strip()]
    return instruments

instruments = read_instruments("\\1")"""),

    # 4. 修复dataset.split用法 - 应该用dataset.prepare
    (r'train_df = dataset\.split\(("(.*?)", "(.*?)""\))',
     r'train_df = dataset.prepare("train", col_set=["feature", "label"], data_key="learn")'),

    (r'test_df = dataset\.split\(("(.*?)", "(.*?)""\))',
     r'test_df = dataset.prepare("test", col_set=["feature", "label"], data_key="infer")'),

    # 5. 修复model.fit用法 - 应该用dataset而不是train_df
    (r'model\.fit\(\s*dataset=train_df,\s*segment="train"\s*\)',
     r'model.fit(dataset)'),

    # 6. 修复model.predict用法
    (r'predictions = model\.predict\(dataset=test_df, segment="test"\)',
     r'predictions = model.predict(dataset, segment="test")'),

    # 7. 修复dataset在D.features中的instruments参数
    (r'D\.features\(\s*instruments=instruments,',
     r'D.features(\n    instruments={"market": "csi300", "filter_pipe": []},'),
]

# 应用修复
for pattern, replacement in fixes:
    count = len(re.findall(pattern, content))
    if count > 0:
        continue
    new_content = re.sub(pattern, replacement, content)
    if new_content != content:
        content = new_content
        print(f"修复: {pattern[:50]}... (替换{count}处)")
    else:
        print(f"无变化: {pattern[:50]}...")

# 保存修复后的文档
with open(doc_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ 文档修复完成")
