#!/usr/bin/env python3
"""
生成待处理文件列表并启动多个进程并行生成文档
"""

import os
import re
import ast
from pathlib import Path


def extract_files_from_file_all(file_all_path):
    """从 file_all.md 提取所有 qlib/*.py 文件路径"""
    files = []
    with open(file_all_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('- ') and line.endswith('.py'):
                file_path = line[2:].strip()
                if file_path.startswith('qlib/'):
                    files.append(file_path)
    return files


def get_existing_docs(docs_dir):
    """获取已生成的文档路径（相对于 docs/all/）"""
    existing = set()
    if not os.path.exists(docs_dir):
        return existing

    for md_file in Path(docs_dir).rglob('*.md'):
        rel_path = md_file.relative_to(docs_dir)
        existing.add(str(rel_path))
    return existing


def get_pending_files(file_all_path, docs_dir):
    """获取待处理的文件列表"""
    all_files = extract_files_from_file_all(file_all_path)
    existing_docs = get_existing_docs(docs_dir)

    pending = []
    for file_path in all_files:
        # 构建对应的文档路径
        rel_path = file_path.replace('qlib/', '').replace('.py', '.md')
        # 处理 __init__.py 的情况
        if '__init__.py' in rel_path:
            rel_path = rel_path.replace('__init__.py', '__init__.md')

        # 检查文档是否已存在
        if rel_path not in existing_docs:
            # 检查实际的文件是否存在
            if os.path.exists(file_path):
                pending.append(file_path)

    return pending


def group_files_by_module(files):
    """按模块分组文件"""
    groups = {
        'contrib/data': [],
        'contrib/model': [],
        'contrib/report': [],
        'contrib/strategy': [],
        'contrib/meta': [],
        'contrib/online': [],
        'contrib/ops': [],
        'contrib/eva': [],
        'contrib/rolling': [],
        'contrib/tuner': [],
        'contrib/workflow': [],
        'data/dataset': [],
        'data/storage': [],
        'rl/order_execution': [],
        'rl/contrib': [],
        'rl/data': [],
        'rl/trainer': [],
        'rl/utils': [],
        'rl/strategy': [],
        'workflow/task': [],
        'workflow/online': [],
        'other': [],
    }

    for file_path in files:
        grouped = False
        for group_name in groups:
            if group_name != 'other' and f'qlib/{group_name}/' in file_path:
                groups[group_name].append(file_path)
                grouped = True
                break
        if not grouped:
            groups['other'].append(file_path)

    return groups


def main():
    """主函数"""
    file_all_path = 'docs/file_all.md'
    docs_dir = 'docs/all'

    print("生成待处理文件列表...")
    pending_files = all_files = extract_files_from_file_all(file_all_path)
    existing_docs = get_existing_docs(docs_dir)
    pending_files = get_pending_files(file_all_path, docs_dir)
    print(f"所有文件数量: {len(all_files)}")
    print(f"已生成文档数量: {len(existing_docs)}")
    print(f"待处理文件数量: {len(pending_files)}")

    if not pending_files:
        print("所有文档已生成完成！")
        return

    # 按模块分组
    groups = group_files_by_module(pending_files)

    print("\n按模块分组统计:")
    for group_name, files in groups.items():
        if files:
            print(f"  {group_name}: {len(files)}")

    # 输出待处理文件列表
    output_file = 'docs/pending_files.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        for file_path in pending_files:
            f.write(f"{file_path}\n")

    print(f"\n待处理文件列表已保存到: {output_file}")


if __name__ == '__main__':
    main()
