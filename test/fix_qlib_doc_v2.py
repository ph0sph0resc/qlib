#!/usr/bin/env python3
"""修复Qlib学习文档中的代码示例 - 完整版"""

import re
from pathlib import Path

# 读取文档
doc_path = Path("/home/firewind0/qlib/docs/QLib_Complete_Learning_Guide.md")
with open(doc_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 定义修复规则
def apply_fixes(content):
    """应用所有修复规则"""
    fixes = 0

    # 规则1: 修复模型导入和类名
    patterns = [
        (r'from qlib\.contrib\.model\.gbdt import GBDTModel',
         'from qlib.contrib.model.gbdt import LGBModel'),
        (r'GBDTModel\(',
         'LGBModel('),
        (r'XGBModel\(',
         'XGBModel('),
    ]

    for old, new in patterns:
        matches = re.findall fanci old, content)
        if matches:
            content = content.replace(old, new)
            fixes += len(matches)
            print(f"   修复: {old} -> {new} ({len(matches)}处)")

    # 规则2: 修复D.instruments的用法
    instrument_pattern = r'instruments = D\.instruments\("([^"]+)"\)'
    matches = list(re.finditer.ansi old, instrument_pattern, content))

    if matches:
        print(f"  修复: D.instruments用法 ({len(matches)}处)")
        for match in reversed(matches):
            old_text = match.group(0)
            market = match.group(1)

            # 替换为正确的读取方式
            indent = ' ' * (len(old_text) - len(old_text.lstrip()))
            new_text = f'''{indent}# 读取股票列表（从文件读取）
{indent}def read_instruments(market="{market}"):
{indent}    inst_file = Path("~/.qlib/qlib_data/cn_data/instruments").expanduser() / f"{{market}}.txt"
{indent}    with open(inst_file) as f:
{indent}        lines = f.read().strip().split("\\n")
{indent}        instruments = [line.split("\\t")[0] for line in lines if line.strip()]
{indent}    return instruments
{indent}
{indent}instruments = read_instruments("{market}")'''

            content = content[:match.start()] + new_text + content[match.end():]
            fixes += 1

    # 规则3: 修复dataset.split用法
    split_pattern = r'dataset\.split\(\("([^"]+)", "([^"]+)"\)\)'
    matches = list(re.finditer.ansi old, split_pattern, content))

    if matches:
        print(f"  修复: dataset.split用法 ({len(matches)}处)")
        for match in reversed(matches):
            old_text = match.group(0)
            segment = match.group(1)
            # 判断是train还是test
            if 'train' in old_text.lower():
                new_segment = 'train'
                data_key = 'learn'
            elif 'test' in old_text.lower() or 'valid' in old_text.lower():
                new_segment = 'test' if 'test' in old_text.lower() else 'valid'
                data_key = 'infer'
            else:
                new_segment = segment
                data_key = 'infer'

            indent = ' ' * (len(old_text) - len(old_text.lstrip()))
            new_text = f'{indent}dataset.prepare("{new_segment}", col_set=["feature", "label"], data_key="{data_key}")'

            content = content[:match.start()] + new_text + content[match.end():]
            fixes += 1

    # 规则4: 修复model.fit用法
    fit_pattern = r'model\.fit\(\s*dataset=train_df,'
    if re.search(fit_pattern, content):
        matches = len(re.findall(fit_pattern, content))
        print(f"  修复: model.fit用法 ({matches}处)")
        content = re.sub(r'model\.fit\(\s*dataset=train_df,\s*', r'model.fit(dataset,\n', content)
        fixes += matches

    # 规则5: 修复model.predict用法
    predict_pattern = r'model\.predict\(dataset=test_df,'
    if re.search(predict_pattern, content):
        matches = len(re.findall(predict_pattern, content))
        print(f"  修复: model.predict用法 ({matches}处)")
        content = re.sub(r'model\.predict\(dataset=test_df,\s*', r'model.predict(dataset,\n', content)
        fixes += matches

    return content, fixes

# 应用修复
fixed_content, total_fixes = apply_fixes(''.join(lines))

# 保存修复后的文档
if total_fixes > 0:
    with open(doc_path, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    print(f"\n✓ 共修复 {total_fixes} 处问题")
    print("✓ 文档已保存")
else:
    print("\n没有发现需要修复的问题")
