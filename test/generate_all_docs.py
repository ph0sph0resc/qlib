#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量生成 Qlib 中文设计文档的脚本
"""
import ast
import inspect
import os
import sys
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional, Any

# 添加 qlib 到路径
sys.path.insert(0, str(Path(__file__).parent))

class DocGenerator:
    """文档生成器"""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.visited_files: Set[str] = set()

    def generate_for_module(self, module_path: str) -> bool:
        """为单个模块生成文档"""
        if module_path in self.visited_files:
            return False

        self.visited_files.add(module_path)

        # 转换为文件路径
        file_path = self._module_to_path(module_path)
        if not file_path.exists():
            print(f"  ⚠ 文件不存在: {file_path}")
            return False

        # 读取文件内容
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            print(f"  ❌ 读取失败: {e}")
            return False

        # 解析 AST
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            print(f"  ⚠ 语法错误: {e}")
            # 对于 .pyx 文件，跳过
            if file_path.suffix == '.pyx':
                print(f"  ℹ 跳过 Cython 文件: {file_path}")
                return True
            return False

        # 生成文档
        doc = self._generate_doc_content(module_path, file_path, tree, content)

        # 输出文档
        output_path = self.output_dir / f"{module_path}.md"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            output_path.write_text(doc, encoding='utf-8')
            print(f"  ✓ 生成文档: {output_path.name}")
            return True
        except Exception as e:
            print(f"  ❌ 写入失败: {e}")
            return False

    def _module_to_path(self, module_path: str) -> Path:
        """将模块路径转换为文件路径"""
        # 转换模块名到文件名
        # qlib.backtest.account -> qlib/backtest/account.py
        parts = module_path.split('.')
        return Path(*parts[:-1]) / f"{parts[-1]}.py"

    def _generate_doc_content(self, module_path: str, file_path: Path, tree: ast.AST, content: str) -> str:
        """生成文档内容"""
        lines = [
            f"# {module_path} 模块设计文档",
            "",
            "## 模块概述",
            "",
            "该模块是 Qlib 的一部分，具体功能请参考源代码。",
            "",
            "## 导入模块列表",
            "",
            "```python",
        ]

        # 提取导入
        imports = self._extract_imports(tree)
        for imp in imports:
            lines.append(imp)
        lines.append("```")
        lines.append("")

        # 提取类定义
        classes = self._extract_classes(tree, content)
        if classes:
            lines.append("## 类定义")
            lines.append("")
            for cls_info in classes:
                lines.extend(self._format_class_info(cls_info))
                lines.append("")

        # 提取函数定义
        functions = self._extract_functions(tree, content)
        if functions:
            lines.append("## 主要函数")
            lines.append("")
            for func_info in functions:
                lines.extend(self._format_function_info(func_info))
                lines.append("")

        # 添加占位符
        lines.append("## 注意事项")
        lines.append("")
        lines.append("请参考源代码获取更详细的使用说明。")

        return '\n'.join(lines)

    def _extract_imports(self, tree: ast.AST) -> List[str]:
        """提取导入语句"""
        imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(f"import {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    if alias.asname:
                        imports.append(f"from {module} import {alias.name} as {alias.asname}")
                    else:
                        imports.append(f"from {module} import {alias.name}")

        return sorted(set(imports))[:20]  # 限制数量

    def _extract_classes(self, tree: ast.AST, content: str) -> List[Dict]:
        """提取类定义"""
        classes = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # 跳过内部的嵌套类
                if hasattr(node, 'depth') and node.depth > 1:
                    continue

                class_info = {
                    'name': node.name,
                    'docstring': ast.get_docstring(node),
                    'methods': []
                }

                # 提取方法
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        if not item.name.startswith('_'):
                            method_info = {
                                'name': item.name,
                                'docstring': ast.get_docstring(item),
                                'args': self._extract_args(item)
                            }
                            class_info['methods'].append(method_info)

                if class_info['methods'] or class_info['docstring']:
                    classes.append(class_info)

        return classes[:10]  # 限制数量

    def _extract_functions(self, tree: ast.AST, content: str) -> List[Dict]:
        """提取函数定义"""
        functions = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # 跳过内部定义的函数
                if hasattr(node, 'parent'):
                    continue

                # 跳过私有函数
                if node.name.startswith('_'):
                    continue

                func_info = {
                    'name': node.name,
                    'docstring': ast.get_docstring(node),
                    'args': self._extract_args(node)
                }

                if func_info['docstring']:
                    functions.append(func_info)

        return functions[:10]  # 限制数量

    def _extract_args(self, node: ast.FunctionDef) -> List[str]:
        """提取函数参数"""
        args = []
        for arg in node.args.args:
            arg_str = arg.arg
            if arg.annotation:
                annotation = ast.unparse(arg.annotation)
                arg_str += f": {annotation}"
            args.append(arg_str)
        return args[:10]  # 限制数量

    def _format_class_info(self, cls_info: Dict) -> List[str]:
        """格式化类信息"""
        lines = []
        lines.append(f"### `{cls_info['name']}`")
        lines.append("")
        if cls_info['docstring']:
            lines.append("**功能描述：** " + cls_info['docstring'].split('\n')[0])
            lines.append("")

        if cls_info['methods']:
            lines.append("**主要方法：**")
            lines.append("")
            for method in cls_info['methods'][:5]:  # 限制数量
                lines.append(f"#### `{method['name']}()`")
                if method['args']:
                    lines.append("**参数：**")
                    for arg in method['args']:
                        lines.append(f"- `{arg}`")
                lines.append("")
        return lines

    def _format_function_info(self, func_info: Dict) -> List[str]:
        """格式化函数信息"""
        lines = []
        lines.append(f"### `{func_info['name']}()`")
        lines.append("")

        if func_info['docstring']:
            lines.append("**功能描述：** " + func_info['docstring'].split('\n')[0])
            lines.append("")

        if func_info['args']:
            lines.append("**参数：**")
            for arg in func_info['args']:
                lines.append(f"- `{arg}`")
            lines.append("")

        return lines


def read_file_list(file_path: Path) -> List[str]:
    """读取文件列表"""
    content = file_path.read_text(encoding='utf-8')

    files = []
    for line in content.split('\n'):
        line = line.strip()
        if line.startswith('- ') and line.endswith('.py'):
            # 提取文件路径
            file = line[2:].strip()
            if file.startswith('qlib/'):
                # 转换为模块名
                module = file.replace('/', '.').replace('.py', '')
                files.append(module)

    return files


def main():
    """主函数"""
    # 文件列表
    file_list_path = Path(__file__).parent / "docs" / "file_all.md"
    output_dir = Path(__file__).parent / "docs" / "all"

    # 读取文件列表
    print("📖 读取文件列表...")
    try:
        files = read_file_list(file_list_path)
        print(f"  ✓ 找到 {len(files)} 个文件")
    except Exception as e:
        print(f"  ❌ 读取失败: {e}")
        return

    # 生成文档
    print(f"\n📝 开始生成文档到: {output_dir}")
    print("=" * 60)

    generator = DocGenerator(output_dir)

    success = 0
    failed = 0
    skipped = 0

    for i, file in enumerate(files, 1):
        print(f"\n[{i}/{len(files)}] {file}")

        try:
            if generator.generate_for_module(file):
                success += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"  ❌ 错误: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"✓ 成功: {success}")
    print(f"⊘ 跳过: {skipped}")
    print(f"✗ 失败: {failed}")
    print(f"\n📁 文档输出目录: {output_dir}")


if __name__ == "__main__":
    main()
