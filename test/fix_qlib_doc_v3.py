#!/usr/bin/env python3
"""修复Qlib学习文档中的代码示例 - 简化版"""

import re
from pathlib import Path

# 读取文档
doc_path = Path("/home/firewind0/qlib/docs/QLib_Complete_Learning_Guide.md")
with open(doc_path, 'r', encoding='utf-8') as f:
    content = f.read()

print("开始修复文档...")

fixes = 0

# 修复1: GBDTModel -> LGBModel
if 'GBDTModel' in content:
    content = content.replace('GBDTModel', 'LGBModel')
    print("  修复: GBDTModel -> LGBModel")
    fixes += 1

# 保存修复后的文档
if fixes > 0:
    with open(doc_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"\n✓ 共修复 {fixes} 处问题")
    print("✓ 文档已保存")
else:
    print("\n没有发现需要修复的问题")
