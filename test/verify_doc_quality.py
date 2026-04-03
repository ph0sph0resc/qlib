#!/usr/bin/env python3
"""
验证文档质量
"""

import os
import re
from pathlib import Path
from collections import defaultdict


def check_doc_quality(doc_path):
    """检查单个文档质量"""
    with open(doc_path, 'r', encoding='utf-8') as f:
        content = f.read()

    issues = []

    # 检查1: 是否包含中文
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', content))
    if chinese_chars < 10:
        issues.append("中文内容不足")

    # 检查2: 是否有函数级别的细节
    if '## 函数定义' not in content and '#### 方法' not in content:
        issues.append("缺少函数/方法级别文档")

    # 检查3: 是否有类定义
    if '###' not in content:
        issues.append("缺少类定义")

    # 检查4: 是否有参数说明
    if '**参数**:' not in content and '**参数**' not in content:
        issues.append("缺少参数说明")

    return issues


def main():
    """主函数"""
    docs_dir = Path('docs/all')

    # 统计信息
    total_docs = 0
    good_docs = 0
    issues_by_type = defaultdict(int)
    docs_with_issues = []

    # 遍历所有文档
    for md_file in docs_dir.rglob('*.md'):
        total_docs += 1
        issues = check_doc_quality(md_file)

        if not issues:
            good_docs += 1
        else:
            for issue in issues:
                issues_by_type[issue] += 1
            docs_with_issues.append((str(md_file), issues))

    # 输出统计结果
    print("=" * 60)
    print("文档质量验证报告")
    print("=" * 60)
    print(f"总文档数: {total_docs}")
    print(f"质量良好: {good_docs} ({good_docs/total_docs*100:.1f}%)")
    print(f"存在问题: {total_docs - good_docs} ({(total_docs - good_docs)/total_docs*100:.1f}%)")
    print()

    print("问题类型统计:")
    for issue, count in sorted(issues_by_type.items(), key=lambda x: -x[1]):
        print(f"  - {issue}: {count}")

    if docs_with_issues:
        print()
        print(f"存在问题的文档 (前20个):")
        for doc_path, issues in docs_with_issues[:20]:
            rel_path = doc_path.replace('docs/all/', '')
            print(f"  - {rel_path}: {', '.join(issues)}")

        print()
        print(f"完整问题列表已保存到: docs/doc_quality_report.txt")

        with open('docs/doc_quality_report.txt', 'w', encoding='utf-8') as f:
            for doc_path, issues in docs_with_issues:
                rel_path = doc_path.replace('docs/all/', '')
                f.write(f"{rel_path}: {', '.join(issues)}\n")


if __name__ == '__main__':
    main()
