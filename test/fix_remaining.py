#!/usr/bin/env python3
"""
修复剩余的文档问题
"""

import re
from pathlib import Path

# 读取文档
doc_path = Path("/home/firewind0/qlib/docs/QLib_Complete_Learning_Guide.md")

with open(doc_path, 'r', encoding='utf-8') as f:
    content = f.read()

fixes = 0

# 修复: 将 train_df[label_field].pct_change(1) 这类代码删除
# 因为DatasetH已经处理了标签
pattern = r'train_df\["label"\] = train_df\[.*?\]\.pct_change\(1\)'
matches = list(re.finditer(pattern, content))

if matches:
    print(f"✓ 修复: 手动计算标签 ({len(matches)}处)")
    for match in reversed(matches):
        old_text = match.group(0)
        # 找到该行并删除
        content = content[:match.start()] + content[match.end():]
        fixes += 1

# 保存修复后的文档
if fixes > 0:
    with open(doc_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"\n✓ 共修复 {fixes} 处问题")
    print("✓ 文档已保存")
else:
    print("\n没有发现需要修复的问题")

# 验证
if 'D.instruments(' in content:
    print("⚠ D.instruments( 仍然存在")
