#!/usr/bin/env python3
"""
为单个 Python 文件生成详细的中文设计文档
"""

import os
import sys
import ast
from pathlib import Path


def parse_python_file(file_path):
    """解析 Python 文件，提取类和函数信息"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        tree = ast.parse(content)

        classes = []
        functions = []
        imports = []
        docstring = None

        # 提取模块文档字符串
        module_doc = ast.get_docstring(tree)
        if module_doc:
            docstring = module_doc

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = []
                properties = []
                class_vars = []
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        # 检查是否是 property
                        is_property = any(
                            dec.id == 'property' if isinstance(dec, ast.Name) else False
                            for dec in item.decorator_list
                        )
                        method_info = {
                            'name': item.name,
                            'lineno': item.lineno,
                            'docstring': ast.get_docstring(item),
                            'args': [arg.arg for arg in item.args.args],
                            'is_property': is_property,
                            'is_async': isinstance(item, ast.AsyncFunctionDef),
                        }
                        methods.append(method_info)
                    elif isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name):
                                class_vars.append(target.id)

                bases = []
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        bases.append(base.id)
                    elif isinstance(base, ast.Attribute):
                        bases.append(f"{base.value.id}.{base.attr}")
                    elif isinstance(base, ast.Subscript):
                        # 处理 typing.Generic 等复杂继承
                        if isinstance(base.value, ast.Name):
                            bases.append(base.value.id)

                classes.append({
                    'name': node.name,
                    'lineno': node.lineno,
                    'docstring': ast.get_docstring(node),
                    'bases': bases,
                    'methods': methods,
                    'class_vars': class_vars,
                })
            elif isinstance(node, ast.FunctionDef) and node.col_offset == 0:
                # 顶层函数
                args = [arg.arg for arg in node.args.args]
                defaults = [ast.unparse(d) for d in node.args.defaults] if hasattr(ast, 'unparse') else []

                functions.append({
                    'name': node.name,
                    'lineno': node.lineno,
                    'docstring': ast.get_docstring(node),
                    'args': args,
                    'defaults': defaults,
                    'returns': ast.unparse(node.returns) if hasattr(ast, 'unparse') and node.returns else None,
                    'is_async': isinstance(node, ast.AsyncFunctionDef),
                })
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append({'type': 'import', 'name': alias.name, 'as': alias.asname})
                else:
                    module = node.module if node.module else ''
                    for alias in node.names:
                        imports.append({
                            'type': 'from',
                            'module': module,
                            'name': alias.name,
                            'as': alias.asname
                        })

        return {
            'content': content,
            'classes': classes,
            'functions': functions,
            'imports': imports,
            'docstring': docstring,
        }
    except Exception as e:
        return {
            'content': '',
            'classes': [],
            'functions': [],
            'imports': [],
            'docstring': None,
            'error': str(e)
        }


def generate_markdown_doc(file_path, parsed):
    """生成 Markdown 文档"""
    rel_path = file_path.replace('qlib/', '')
    module_name = rel_path.replace('.py', '').replace('/', '.')
    file_name = os.path.basename(file_path)

    doc = f"# {module_name}\n\n"
    doc += f"**文件路径**: `{file_path}`\n\n"
    doc += f"**模块名**: `{module_name}`\n\n"

    # 模块概述
    doc += "## 模块概述\n\n"
    if parsed.get('docstring'):
        doc += f"{parsed['docstring']}\n\n"
    else:
        doc += "本模块是 Qlib 框架的组成部分，提供相关功能实现。\n\n"

    if 'error' in parsed:
        doc += f"**注意**: 文件解析时出错: {parsed['error']}\n\n"

    # 导入
    imports = parsed.get('imports', [])
    if imports:
        doc += "## 导入模块\n\n"
        for imp in imports:
            if imp['type'] == 'import':
                if imp['as']:
                    doc += f"- `import {imp['name']} as {imp['as']}`\n"
                else:
                    doc += f"- `import {imp['name']}`\n"
            else:
                if imp['name'] == '*':
                    doc += f"- `from {imp['module']} import *`\n"
                elif imp['as']:
                    doc += f"- `from {imp['module']} import {imp['name']} as {imp['as']}`\n"
                else:
                    doc += f"- `from {imp['module']} import {imp['name']}`\n"
        doc += "\n"

    # 类
    classes = parsed.get('classes', [])
    if classes:
        doc += "## 类定义\n\n"
        for cls in classes:
            doc += f"### {cls['name']}\n\n"

            # 继承关系
            if cls['bases']:
                doc += "#### 继承关系\n\n"
                for base in cls['bases']:
                    doc += f"- 继承自 `{base}`\n"
                doc += "\n"

            # 类说明
            if cls['docstring']:
                doc += "#### 说明\n\n"
                doc += f"{cls['docstring']}\n\n"

            # 类变量
            if cls['class_vars']:
                doc += "#### 类属性\n\n"
                for var in cls['class_vars']:
                    doc += f"- `{var}`\n"
                doc += "\n"

            # 方法
            if cls['methods']:
                doc += "#### 方法\n\n"
                for method in cls['methods']:
                    # 方法签名
                    prefix = "async " if method['is_async'] else ""
                    if method['is_property']:
                        doc += f"**{prefix}@property `{method['name']}`**\n\n"
                    else:
                        args_str = ', '.join(method['args'])
                        doc += f"**{prefix}`{method['name']}({args_str})`**\n\n"

                    # 方法说明
                    if method['docstring']:
                        doc += f"{method['docstring']}\n\n"

                    doc += "---\n\n"

    # 函数
    functions = parsed.get('functions', [])
    if functions:
        doc += "## 函数定义\n\n"
        for func in functions:
            # 函数签名
            prefix = "async " if func['is_async'] else ""
            args_str = ', '.join(func['args'])
            doc += f"### {prefix}`{func['name']}({args_str})`\n\n"

            # 返回类型
            if func.get('returns'):
                doc += f"**返回类型**: `{func['returns']}`\n\n"

            # 函数说明
            if func['docstring']:
                doc += f"**说明**:\n\n{func['docstring']}\n\n"

            doc += "---\n\n"

    doc += "\n---\n\n"
    doc += "*本文档由 Qlib 文档生成器自动生成*"

    return doc


def generate_doc_for_file(file_path, output_dir):
    """为单个文件生成文档"""
    try:
        # 解析文件
        parsed = parse_python_file(file_path)

        # 构建输出路径
        rel_path = file_path.replace('qlib/', '')
        # 将 .py 替换为 .md
        output_path = Path(output_dir) / rel_path.replace('.py', '.md')

        # 确保父目录存在
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # 生成文档内容
        doc_content = generate_markdown_doc(file_path, parsed)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(doc_content)

        return True, str(output_path)
    except Exception as e:
        import traceback
        return False, f"{file_path}: {str(e)}\n{traceback.format_exc()}"


def main():
    """主函数"""
    if len(sys.argv) < 3:
        print("用法: python3 generate_single_doc.py <input_file> <output_dir>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_dir = sys.argv[2]

    success, result = generate_doc_for_file(input_file, output_dir)

    if success:
        print(f"成功生成: {result}")
    else:
        print(f"失败: {result}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
