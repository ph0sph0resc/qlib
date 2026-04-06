#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为 utils 和 workflow 目录生成中文函数级详细文档
"""

import os
import ast
import inspect
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
import re

# 设置源码根目录
SRC_ROOT = Path("/home/firewind0/qlib")
DOC_ROOT = Path("/home/firewind0/qlib/docs/all")


def ensure_output_dir(file_path: Path):
    """确保输出目录存在"""
    output_path = DOC_ROOT / file_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    return output_path


def get_docstring(node) -> Optional[str]:
    """获取节点的docstring"""
    return ast.get_docstring(node)


def format_type_annotation(annotation) -> str:
    """格式化类型注解"""
    if annotation is None:
        return ""
    if isinstance(annotation, ast.Name):
        return annotation.id
    elif isinstance(annotation, ast.Subscript):
        base = format_type_annotation(annotation.value)
        if isinstance(annotation.slice, ast.Tuple):
            slice_str = ", ".join(format_type_annotation(elt) for elt in annotation.slice.elts)
        else:
            slice_str = format_type_annotation(annotation.slice)
        return f"{base}[{slice_str}]"
    elif isinstance(annotation, ast.Attribute):
        return f"{format_type_annotation(annotation.value)}.{annotation.attr}"
    elif isinstance(annotation, ast.Constant):
        return str(annotation.value)
    return str(annotation)


def parse_function_args(node: ast.FunctionDef) -> List[Dict[str, Any]]:
    """解析函数参数"""
    args = []

    # 处理位置参数和关键字参数
    all_args = node.args.args + node.args.kwonlyargs
    defaults_offset = len(all_args) - len(node.args.defaults) if node.args.defaults else len(all_args)

    for i, arg in enumerate(all_args):
        arg_info = {
            "name": arg.arg,
            "type": format_type_annotation(arg.annotation) if arg.annotation else "Any",
            "default": None,
            "is_vararg": False,
            "is_kwarg": False,
        }

        # 检查默认值
        if node.args.defaults and i >= defaults_offset:
            default_idx = i - defaults_offset
            if default_idx < len(node.args.defaults):
                default = node.args.defaults[default_idx]
                if isinstance(default, ast.Constant):
                    arg_info["default"] = str(default.value)
                elif isinstance(default, ast.NameConstant):
                    arg_info["default"] = str(default.value)
                elif isinstance(default, ast.Name):
                    arg_info["default"] = default.id
                elif isinstance(default, (ast.List, ast.Dict)):
                    arg_info["default"] = "[]"
                else:
                    arg_info["default"] = "..."

        args.append(arg_info)

    # 处理 *args
    if node.args.vararg:
        args.append({
            "name": f"*{node.args.vararg.arg}",
            "type": format_type_annotation(node.args.vararg.annotation) if node.args.vararg.annotation else "Any",
            "default": None,
            "is_vararg": True,
            "is_kwarg": False,
        })

    # 处理 **kwargs
    if node.args.kwarg:
        args.append({
            "name": f"**{node.args.kwarg.arg}",
            "type": format_type_annotation(node.args.kwarg.annotation) if node.args.kwarg.annotation else "Any",
            "default": None,
            "is_vararg": False,
            "is_kwarg": True,
        })

    return args


def parse_decorators(node: ast.AST) -> List[str]:
    """解析装饰器"""
    decorators = []
    if hasattr(node, "decorator_list"):
        for dec in node.decorator_list:
            if isinstance(dec, ast.Name):
                decorators.append(f"@{dec.id}")
            elif isinstance(dec, ast.Attribute):
                decorators.append(f"@{format_type_annotation(dec)}")
            elif isinstance(dec, ast.Call):
                func = format_type_annotation(dec.func)
                args = []
                for arg in dec.args:
                    if isinstance(arg, ast.Str):
                        args.append(f'"{arg.s}"')
                    elif isinstance(arg, ast.Constant):
                        args.append(f'"{arg.value}"' if isinstance(arg.value, str) else str(arg.value))
                decorators.append(f"@{func}({', '.join(args)})")
    return decorators


def translate_common_terms(text: str) -> str:
    """翻译常见术语"""
    translations = {
        "Initialize": "初始化",
        "Constructor": "构造函数",
        "Parameters": "参数",
        "Returns": "返回值",
        "Raises": "抛出异常",
        "Examples": "示例",
        "Note": "注意",
        "Warning": "警告",
        "See Also": "参考",
        "Attributes": "属性",
        "Methods": "方法",
        "Args": "参数",
        "kwargs": "关键字参数",
        "args": "可变参数",
        "Returns:": "返回值：",
        "Args:": "参数：",
        "Raises:": "异常：",
    }
    for en, cn in translations.items():
        text = text.replace(en, cn)
    return text


def generate_class_doc(class_node: ast.ClassDef, module_name: str) -> str:
    """生成类文档"""
    class_name = class_node.name
    class_doc = get_docstring(class_node) or "暂无文档"

    doc = f"\n### 类：{class_name}\n\n"
    doc += f"**说明：**\n\n{class_doc}\n\n"

    # 解析基类
    if class_node.bases:
        base_classes = [format_type_annotation(base) for base in class_node.bases]
        doc += f"**继承自：** {', '.join(base_classes)}\n\n"

    # 获取装饰器
    decorators = parse_decorators(class_node)
    if decorators:
        doc += f"**装饰器：**\n"
        for dec in decorators:
            doc += f"- `{dec}`\n"
        doc += "\n"

    # 分析类内容
    methods = []
    properties = []
    attributes = []
    class_vars = []

    for item in class_node.body:
        if isinstance(item, ast.FunctionDef):
            if item.name in ["__init__", "__new__"]:
                methods.append((item, True))  # 构造函数
            elif item.name.startswith("__") and item.name.endswith("__"):
                methods.append((item, False))  # 魔术方法
            else:
                methods.append((item, False))  # 普通方法
        elif isinstance(item, ast.AsyncFunctionDef):
            methods.append((item, False))  # 异步方法
        elif isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
            properties.append(item)
        elif isinstance(item, ast.Assign):
            for target in item.targets:
                if isinstance(target, ast.Name):
                    class_vars.append((target.id, item))

    # 输出类变量
    if class_vars:
        doc += "#### 类变量\n\n"
        doc += "| 变量名 | 类型 | 说明 |\n"
        doc += "|--------|------|------|\n"
        for var_name, item in class_vars:
            doc += f"| {var_name} | - | 类级变量 |\n"
        doc += "\n"

    # 输出构造方法
    init_method = None
    for method, is_init in methods:
        if is_init:
            init_method = method
            break

    if init_method:
        doc += "#### 构造方法\n\n"
        args = parse_function_args(init_method)
        init_doc = get_docstring(init_method) or "初始化类实例"

        # 构建参数签名
        sig_parts = []
        for arg in args:
            sig = f'{arg["name"]}'
            if arg["type"] and arg["type"] != "Any":
                sig += f': {arg["type"]}'
            if arg["default"]:
                sig += f' = {arg["default"]}'
            sig_parts.append(sig)

        doc += f"```python\ndef __init__({', '.join(sig_parts)}):\n```\n\n"
        doc += f"**说明：**\n\n{init_doc}\n\n"

        if args and not (args[0]["name"] == "self"):
            doc += "**参数：**\n\n"
            doc += "| 参数名 | 类型 | 必填 | 默认值 | 说明 |\n"
            doc += "|--------|------|------|--------|------|\n"
            for arg in args:
                if arg["name"] in ["self", "cls"]:
                    continue
                is_required = "是" if arg["default"] is None else "否"
                default_val = arg["default"] if arg["default"] is not None else "-"
                doc += f"| {arg['name']} | {arg['type']} | {is_required} | {default_val} | - |\n"
            doc += "\n"

    # 输出属性
    if properties:
        doc += "#### 属性\n\n"
        doc += "| 属性名 | 类型 | 说明 |\n"
        doc += "|--------|------|------|\n"
        for prop in properties:
            prop_name = prop.target.id
            prop_type = format_type_annotation(prop.annotation) if prop.annotation else "Any"
            doc += f"| {prop_name} | {prop_type} | - |\n"
        doc += "\n"

    # 输出方法
    regular_methods = [(m, is_init) for m, is_init in methods if not is_init]
    if regular_methods:
        doc += "#### 方法\n\n"
        for method, is_init in regular_methods:
            method_name = method.name
            method_doc = get_docstring(method) or "暂无文档"
            args = parse_function_args(method)
            decorators = parse_decorators(method)

            doc += f"**{method_name}**\n\n"

            if decorators:
                doc += "装饰器：\n"
                for dec in decorators:
                    doc += f"- `{dec}`\n"
                doc += "\n"

            # 函数签名
            sig_args = []
            for arg in args:
                if arg["name"] in ["self", "cls"]:
                    continue
                sig = f"{arg['name']}"
                if arg['type'] and arg['type'] != 'Any':
                    sig += f": {arg['type']}"
                if arg['default']:
                    sig += f" = {arg['default']}"
                sig_args.append(sig)

            return_type = ""
            if hasattr(method, "returns") and method.returns:
                return_type = f" -> {format_type_annotation(method.returns)}"

            doc += f"```python\n{method_name}({', '.join(sig_args)}){return_type}\n```\n\n"

            doc += f"**说明：**\n\n{method_doc}\n\n"

            # 参数表
            non_self_args = [arg for arg in args if arg["name"] not in ["self", "cls"]]
            if non_self_args:
                doc += "**参数：**\n\n"
                doc += "| 参数名 | 类型 | 必填 | 默认值 | 说明 |\n"
                doc += "|--------|------|------|--------|------|\n"
                for arg in non_self_args:
                    is_required = "是" if arg["default"] is None else "否"
                    default_val = arg["default"] if arg["default"] is not None else "-"
                    name_suffix = "..." if arg.get('is_vararg') or arg.get('is_kwarg') else ""
                    doc += f"| {arg['name']}{name_suffix} | {arg['type']} | {is_required} | {default_val} | - |\n"
                doc += "\n"

            # 返回值
            if method.returns:
                return_type_str = format_type_annotation(method.returns)
                doc += f"**返回值：** {return_type_str}\n\n"
            elif "Returns:" in method_doc or "返回" in method_doc:
                doc += "**返回值：** 见函数说明\n\n"

    return doc


def generate_function_doc(func_node: ast.FunctionDef, module_name: str, is_method: bool = False) -> str:
    """生成函数文档"""
    func_name = func_node.name
    func_doc = get_docstring(func_node) or "暂无文档"
    args = parse_function_args(func_node)
    decorators = parse_decorators(func_node)

    doc = f"\n### {'方法' if is_method else '函数'}：{func_name}\n\n"

    if decorators:
        doc += "装饰器：\n"
        for dec in decorators:
            doc += f"- `{dec}`\n"
        doc += "\n"

    # 函数签名
    sig_args = []
    for arg in args:
        if is_method and arg["name"] in ["self", "cls"]:
            continue
        sig = f"{arg['name']}"
        if arg['type'] and arg['type'] != 'Any':
            sig += f": {arg['type']}"
        if arg['default']:
            sig += f" = {arg['default']}"
        sig_args.append(sig)

    return_type = ""
    if hasattr(func_node, "returns") and func_node.returns:
        return_type = f" -> {format_type_annotation(func_node.returns)}"

    doc += f"```python\n{func_name}({', '.join(sig_args)}){return_type}\n```\n\n"

    doc += f"**说明：**\n\n{func_doc}\n\n"

    # 参数表
    non_self_args = [arg for arg in args if not (is_method and arg["name"] in ["self", "cls"])]
    if non_self_args:
        doc += "**参数：**\n\n"
        doc += "| 参数名 | 类型 | 必填 | 默认值 | 说明 |\n"
        doc += "|--------|------|------|--------|------|\n"
        for arg in non_self_args:
            is_required = "是" if arg["default"] is None else "否"
            default_val = arg["default"] if arg["default"] is not None else "-"
            name_suffix = "..." if arg.get('is_vararg') or arg.get('is_kwarg') else ""
            doc += f"| {arg['name']}{name_suffix} | {arg['type']} | {is_required} | {default_val} | - |\n"
        doc += "\n"

    # 返回值
    if func_node.returns:
        return_type_str = format_type_annotation(func_node.returns)
        doc += f"**返回值：** {return_type_str}\n\n"
    elif "Returns:" in func_doc or "返回" in func_doc:
        doc += "**返回值：** 见函数说明\n\n"

    return doc


def generate_module_doc(file_path: Path, module_name: str) -> str:
    """生成模块文档"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source_code = f.read()
    except Exception as e:
        return f"无法读取文件: {e}\n"

    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        return f"语法错误: {e}\n"
    module_doc = get_docstring(tree) or "暂无模块说明"

    doc = f"# {module_name}\n\n"
    doc += f"**源文件：** `{file_path}`\n\n"
    doc += f"**模块说明：**\n\n{module_doc}\n\n"

    # 分析AST
    classes = []
    functions = []
    constants = []
    imports = []

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            classes.append(node)
        elif isinstance(node, ast.FunctionDef):
            functions.append(node)
        elif isinstance(node, ast.AsyncFunctionDef):
            functions.append(node)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id.isupper():
                    constants.append((target.id, node))
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            imports.append(node)

    # 输出导入
    if imports:
        doc += "## 导入依赖\n\n"
        doc += "```python\n"
        for imp in imports:
            if isinstance(imp, ast.Import):
                for name in imp.names:
                    alias = f" as {name.asname}" if name.asname else ""
                    doc += f"import {name.name}{alias}\n"
            elif isinstance(imp, ast.ImportFrom):
                module = imp.module or ""
                names = ", ".join(f"{name.name} as {name.asname}" if name.asname else name.name for name in imp.names)
                doc += f"from {module} import {names}\n"
        doc += "```\n\n"

    # 输出常量
    if constants:
        doc += "## 常量\n\n"
        doc += "| 常量名 | 说明 |\n"
        doc += "|--------|------|\n"
        for const_name, node in constants:
            doc += f"| `{const_name}` | 模块常量 |\n"
        doc += "\n"

    # 目录
    if classes or functions:
        doc += "## 目录\n\n"
        if classes:
            doc += "### 类\n\n"
            for cls in classes:
                doc += f"- [{cls.name}](#类{cls.name.lower()})\n"
            doc += "\n"
        if functions:
            doc += "### 函数\n\n"
            for func in functions:
                doc += f"- [{func.name}](#函数{func.name.lower()})\n"
            doc += "\n"

    # 输出类
    if classes:
        doc += "## 类定义\n\n"
        for class_node in classes:
            doc += generate_class_doc(class_node, module_name)

    # 输出函数
    if functions:
        doc += "## 函数定义\n\n"
        for func_node in functions:
            if not func_node.name.startswith("_") or func_node.name.startswith("__") and func_node.name.endswith("__"):
                doc += generate_function_doc(func_node, module_name)

    return doc


def process_file(file_path: Path):
    """处理单个文件"""
    rel_path = file_path.relative_to(SRC_ROOT)
    module_name = str(rel_path.with_suffix("")).replace("/", ".")

    print(f"处理文件: {rel_path}")

    # 生成文档
    doc_content = generate_module_doc(file_path, module_name)

    # 确定输出路径
    output_path = ensure_output_dir(rel_path.with_suffix(".md"))

    # 保存文档
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(doc_content)

    print(f"  保存到: {output_path}")


def main():
    """主函数"""
    target_dirs = [
        "qlib/utils/",
        "qlib/workflow/",
    ]

    total_files = 0
    for target_dir in target_dirs:
        dir_path = SRC_ROOT / target_dir
        if not dir_path.exists():
            print(f"警告: 目录不存在: {dir_path}")
            continue

        # 查找所有Python文件
        for py_file in dir_path.rglob("*.py"):
            try:
                process_file(py_file)
                total_files += 1
            except Exception as e:
                print(f"错误: 处理 {py_file} 失败: {e}")
                import traceback
                traceback.print_exc()

    print(f"\n完成! 共处理 {total_files} 个文件")
    print(f"文档输出到: {DOC_ROOT}")


if __name__ == "__main__":
    main()
