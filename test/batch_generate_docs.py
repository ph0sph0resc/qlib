#!/usr/bin/env python3
"""
批量并行生成文档
"""

import os
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path


def process_file(file_info):
    """处理单个文件"""
    file_path, output_dir = file_info
    result = os.system(f"python3 generate_single_doc.py '{file_path}' '{output_dir}'")
    return file_path, result == 0


def batch_generate(pending_files, output_dir, num_workers=4):
    """批量生成文档"""
    print(f"开始并行生成 {len(pending_files)} 个文件，使用 {num_workers} 个进程...\n")

    file_pairs = [(f, output_dir) for f in pending_files]
    success_count = 0
    fail_count = 0
    failed_files = []

    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = {executor.submit(process_file, fp): fp[0] for fp in file_pairs}

        for i, future in enumerate(as_completed(futures), 1):
            file_path, success = future.result()
            if success:
                success_count += 1
                print(f"[{i}/{len(pending_files)}] 成功: {file_path}")
            else:
                fail_count += 1
                failed_files.append(file_path)
                print(f"[{i}/{len(pending_files)}] 失败: {file_path}")

    print(f"\n生成完成！")
    print(f"成功: {success_count}, 失败: {fail_count}")

    if failed_files:
        with open('docs/failed_files.txt', 'w', encoding='utf-8') as f:
            for file_path in failed_files:
                f.write(f"{file_path}\n")
        print(f"失败文件列表已保存到: docs/failed_files.txt")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python3 batch_generate_docs.py <module_prefix> [num_workers]")
        print("示例: python3 batch_generate_docs.py contrib/data 4")
        sys.exit(1)

    module_prefix = sys.argv[1]
    num_workers = int(sys.argv[2]) if len(sys.argv) > 2 else 4

    # 读取待处理文件
    pending_file = 'docs/pending_files.txt'
    if not os.path.exists(pending_file):
        print(f"待处理文件列表不存在: {pending_file}")
        sys.exit(1)

    with open(pending_file, 'r', encoding='utf-8') as f:
        all_pending = [line.strip() for line in f if line.strip()]

    # 过滤指定模块的文件
    filtered = [f for f in all_pending if module_prefix in f]

    if not filtered:
        print(f"没有找到匹配 '{module_prefix}' 的待处理文件")
        sys.exit(0)

    print(f"找到 {len(filtered)} 个匹配的文件")

    # 批量生成
    batch_generate(filtered, 'docs/all', num_workers)


if __name__ == '__main__':
    main()
