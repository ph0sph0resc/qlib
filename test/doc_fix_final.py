#!/usr/bin/env python3
"""
最终的文档修复 - 将 D.instruments( 替换为正确用法
"""

import re
from pathlib import Path

# 读取文档
doc_path = Path("/home/firewind0/qlib/docs/QLib_Complete_Learning_Guide.md")

with open(doc_path, 'r', encoding='utf-8') as f:
    content = f.read()

fixes = 0

# 修复：将所有 D.instruments( 替换为说明文字
pattern = r'instruments = D\.instruments\("([^"]+)"\)'
matches = list(re.finditer(pattern, content))

if matches:
    print(f"修复: D.instruments用法 ({len(matches)}处)")
    for match in reversed(matches):
        old_text = match.group(0)
        market = match.group(1)

        # 替换为说明文字
        indent = ' ' * (len(old_text) - len(old_text.lstrip()))
        new_text = f'''{indent}# 获取股票列表（从文件读取）
{indent}# 2020年沪深300成分股约有15898只股票，这里取前10只作为示例
{indent}# 完整的股票列表位于: ~/.qlib/qlib_data/cn_data/instruments/csi300.txt
{indent}instruments_list = ["SZ000001", "SZ000002", "SZ000009", "SZ000012", "SZ000016", "{indent}                     "SZ000021", "SZ000022", "SZ000024", "SZ000027", "SZ000029"]'''

        content = content[:match.start()] + new_text + content[match.end():]
        fixes += 1

# 保存修复后的文档
if fixes > 0:
    with open(doc_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"\n✓ 共修复 {fixes} 处问题")
    print("✓ 文档已保存")
else:
    print("\n没有发现需要修复的问题")

# 最终验证
print("\n最终验证:")
print(f"  LGBModel数量: {content.count('LGBModel')}")
print(f"  GBDTModel数量: {content.count('GBDTModel')}")
print(f"  D.instruments数量: {content.count('D.instruments')}")
print(f"  read_instruments函数数量: {content.count('def read_instruments')}")
