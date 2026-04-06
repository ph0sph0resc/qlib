#!/usr/bin/env python3
"""
清理自动生成的低质量文档
"""

import os
from pathlib import Path


def main():
    """主函数"""
    docs_dir = Path("docs/all")

    if not docs_dir.exists():
        print("docs/all 目录不存在")
        return

    marker_text = "本文档由 Qlib 文档生成器自动生成"
    deleted_count = 0
    kept_count = 0

    for md_file in docs_dir.rglob("*.md"):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

            if marker_text in content:
                # 删除文件
                md_file.unlink()
                deleted_count += 1
                print(f"删除: {md_file}")
            else:
                kept_count += 1

    print(f"\n完成!")
    print(f"删除文件数: {deleted_count}")
    print(f"保留文件数: {kept_count}")


if __name__ == '__main__':
    main()
