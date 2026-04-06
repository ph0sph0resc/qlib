#!/usr/bin/env python3
"""
完整的文档修复脚本
修复所有API调用问题
"""

import re
from pathlib import Path

# 读取文档
doc_path = Path("/home/firewind0/qlib/docs/QLib_Complete_Learning_Guide.md")

with open(doc_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"读取文档: {doc_path}")
print(f"文档总行数: {len(lines)}")

fixes = 0

# ============ 批量替换规则 ============

# 规则1: GBDTModel -> LGBModel（所有出现）
old1 = 'GBDTModel'
new1 = 'LGBModel'
if old1 in ''.join(lines):
    lines = [line.replace(old1, new1) for line in lines]
    count1 = ''.join(lines).count(new1)
    print(f"✓ 修复1: {old1} -> {new1} ({count1}处)")
    fixes += count1

# 规则2: 修复from导入中的GBDTModel
old2 = 'from qlib.contrib.model.gbdt import GBDTModel'
new2 = 'from qlib.contrib.model.gbdt import LGBModel'
if old2 in ''.join(lines):
    lines = [line.replace(old2, new2) for line in lines]
    print(f"✓ 修复2: 更新gbdt模块的import")
    fixes += 1

# 规则3: 修复YAML中的模型类名
old3 = '"class": "qlib.contrib.model.gbdt.GBDTModel"'
new3 = '"class": "qlib.contrib.model.gbdt.LGBModel"'
if old3 in ''.join(lines):
    lines = [line.replace(old3, new3) for line in lines]
    print(f"✓ 修复3: YAML中的模型类名")
    fixes += 1

# 规则4: 修复 D.instruments(region="cn") 的用法
# 替换为从文件读取
pattern4 = r'instruments = D\.instruments\([^)]+\)'
matches4 = []
for i, line in enumerate(lines):
    if 'D.instruments(' in line and '= ' not in line and ')' in line:
        matches4.append(i)

if matches4:
    print(f"✓ 修复4: D.instruments用法 ({len(matches4)}处)")
    for i in reversed(matches4):
        # 找到行并替换
        old_text = lines[i].strip()
        if 'region=' in old_text:
            market = old_text.split('region="')[1].strip(')').strip()
            indent = ' ' * (len(lines[i]) - len(lines[i].lstrip()))
            new_text = f'''{indent}# 获取股票列表
{indent}def read_instruments(market="{market}"):
{indent}    inst_file = Path("~/.qlib/qlib_data/cn_data/instruments").expanduser() / f"{{market}}.txt"
{indent}    with open(inst_file) as f:
{indent}        lines = f.read().strip().split("\\n")
{indent}        instruments = [line.split("\\t")[0] for line in lines if line.strip()]
{indent}    return instruments
{indent}
{indent}instruments = read_instruments("{market}")'''
            lines[i] = new_text
            fixes += 1

# 保存修复后的文档
if fixes > 0:
    with open(doc_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print(f"\n✓ 共修复 {fixes} 处问题")
    print("✓ 文档已保存")
else:
    print("\n没有发现需要修复的问题")

# 最终验证
print("\n最终验证:")
content = ''.join(lines)
print(f"  LGBModel数量: {content.count('LGBModel')}")
print(f"  GBDTModel数量: {content.count('GBDTModel')}")
print(f"  D.instruments(数量: {content.count('D.instruments(')}")
print(f"  read_instruments数量: {content.count('def read_instruments')}")
print(f"  dataset.prepare数量: {content.count('dataset.prepare')}")
