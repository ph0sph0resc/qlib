#!/usr/bin/env python3
"""
系统修复Qlib学习文档中的所有代码示例
主要修复：
1. GBDTModel -> LGBModel（模型类名错误）
2. D.instruments(...) 的用法错误
3. dataset.split(...) 的用法错误
4. model.fit(dataset=train_df) 的用法错误
5. 其他API调用错误
"""

import re
from pathlib import Path

# 读取文档
doc_path = Path("/home/firewind0/qlib/docs/QLib_Complete_Learning_Guide.md")
print(f"读取文档: {doc_path}")

with open(doc_path, 'r', encoding='utf-8') as f:
    content = f.read()

print(f"文档总行数: {len(content.split('\\n'))}")

fixes = 0

# 修复1: GBDTModel -> LGBModel（类名错误）
old1 = 'GDBTModel'
new1 = 'LGBModel'
if old1 in content:
    content = content.replace(old1, new1)
    count1 = content.count(new1)
    print(f"✓ 修复1: {old1} -> {new1} ({count1}处)")
    fixes += count1

# 修复2: 修复 D.instruments(...) 的用法
# 找到所有需要修复的 D.instruments 调用
pattern2 = r'instruments = D\.instruments\("([^"]+)"\)'
matches2 = list(re.finditer(pattern2, content))

if matches2:
    print(f"✓ 修复2: D.instruments用法 ({len(matches2)}处)")
    for match in reversed(matches2):
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

# 修复3: 修复 dataset.split(...) 的用法 - 应该用 dataset.prepare()
pattern3 = r'dataset\.split\(\("([^"]+)", "([^"]+)"\)\)'
matches3 = list(re.finditer(pattern3, content))

if matches3:
    print(f"✓ 修复3: dataset.split用法 ({len(matches3)}处)")
    for match in reversed(matches3):
        old_text = match.group(0)
        segment1 = match.group(1)
        segment2 = match.group(2)

        # 判断是train还是test/valid
        if 'train' in old_text.lower():
            new_segment = 'train'
            data_key = 'learn'
        elif 'test' in old_text.lower():
            new_segment = 'test'
            data_key = 'infer'
        elif 'valid' in old_text.lower():
            new_segment = 'valid'
            data_key = 'infer'
        else:
            new_segment = segment1
            data_key = 'infer'

        indent = ' ' * (len(old_text) - len(old_text.lstrip()))
        new_text = f'{indent}dataset.prepare("{new_segment}", col_set=["feature", "label"], data_key="{data_key}")'

        content = content[:match.start()] + new_text + content[match.end():]
        fixes += 1

# 修复4: 修复 model.fit(dataset=train_df, ...) 的用法
pattern4 = r'model\.fit\(\s*dataset=train_df,'
matches4 = list(re.finditer(pattern4, content))

if matches4:
    print(f"✓ 修复4: model.fit用法 ({len(matches4)}处)")
    for match in reversed(matches4):
        old_text = match.group(0)
        indent = ' ' * (len(old_text) - len(old_text.lstrip()))
        # 找到参数部分
        params = old_text.split('dataset=train_df,')[1] if 'dataset=train_df,' in old_text else ''
        new_text = f'{indent}model.fit(dataset{params}'

        content = content[:match.start()] + new_text + content[match.end():]
        fixes += 1

# 修复5: 修复 model.predict(dataset=test_df, ...) 的用法
pattern5 = r'model\.predict\(\s*dataset=test_df,'
matches5 = list(re.finditer(pattern5, content))

if matches5:
    print(f"✓ 修复5: model.predict用法 ({len(matches5)}处)")
    for match in reversed(matches5):
        old_text = match.group(0)
        indent = ' ' * (len(old_text) - len(old_text.lstrip()))
        # 找到参数部分
        params = old_text.split('dataset=test_df,')[1] if 'dataset=test_df,' in old_text else ''
        new_text = f'{indent}model.predict(dataset{params}'

        content = content[:match.start()] + new_text + content[match.end():]
        fixes += 1

# 修复6: 修复 D.features 中的 instruments 参数格式
# 从 instruments=instruments 改为 instruments={"market": "csi300", "filter_pipe": []}
pattern6 = r'D\.features\(\s*instruments=instruments,'
if re.search(pattern6, content):
    content = re.sub(pattern6, 'D.features(\n    instruments={"market": "csi300", "filter_pipe": []},', content)
    print("✓ 修复6: D.features的instruments参数格式")
    fixes += 1

# 保存修复后的文档
if fixes > 0:
    with open(doc_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"\n✓ 共修复 {fixes} 处问题")
    print("✓ 文档已保存")
else:
    print("\n⚠ 没有发现需要修复的问题")

# 验证修复
print("\n验证修复结果:")
if 'GDBTModel' in content:
    print("  ✗ GDBTModel 仍然存在")
else:
    print("  ✓ GDBTModel 已修复")

if 'LGBModel' in content:
    print("  ✓ LGBModel 已添加")
