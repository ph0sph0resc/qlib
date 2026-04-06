#!/usr/bin/env python3
"""
Script to generate class design documentation for qlib/contrib modules using AST.
"""

import os
import sys
import ast
from pathlib import Path

# Add qlib to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

def is_valid_python_file(file_path):
    """Check if a file is a valid Python file (not __init__.py or __pycache__)."""
    if not file_path.endswith('.py'):
        return False
    if file_path.endswith('__init__.py'):
        return False
    if '__pycache__' in file_path:
        return False
    return True

def get_class_docstring(node):
    """Get the docstring of a class node."""
    if not node.body:
        return ""
    first_stmt = node.body[0]
    if isinstance(first_stmt, ast.Expr) and isinstance(first_stmt.value, ast.Constant):
        return first_stmt.value.value.strip()
    elif isinstance(first_stmt, ast.Expr) and isinstance(first_stmt.value, ast.Str):
        return first_stmt.value.s.strip()
    return ""

def generate_class_doc(file_path, cls_node):
    """Generate documentation for a single class."""
    doc = []
    doc.append(f"### {cls_node.name}\n")
    
    # Class docstring
    cls_docstring = get_class_docstring(cls_node)
    if cls_docstring:
        first_line = cls_docstring.split('\n')[0].strip()
        doc.append(f"{first_line}\n")
    
    # Inheritance
    if cls_node.bases:
        base_names = []
        for base in cls_node.bases:
            if isinstance(base, ast.Name):
                base_names.append(f"`{base.id}`")
            elif isinstance(base, ast.Attribute):
                # Handle qualified names like torch.nn.Module
                attr = []
                node = base
                while isinstance(node, ast.Attribute):
                    attr.append(node.attr)
                    node = node.value
                if isinstance(node, ast.Name):
                    attr.append(node.id)
                base_names.append(f"`{'::'.join(reversed(attr))}`")
            elif isinstance(base, ast.Subscript):
                # Handle generic types like List[int]
                if isinstance(base.value, ast.Name):
                    base_names.append(f"`{base.value.id}[...]`")
        if base_names:
            doc.append(f"**Inherits from**: {', '.join(base_names)}\n")
    
    # Methods
    methods = []
    for stmt in cls_node.body:
        if isinstance(stmt, ast.FunctionDef) or isinstance(stmt, ast.AsyncFunctionDef):
            methods.append(stmt)
    
    if methods:
        doc.append(f"**Methods**:\n")
        for method in methods:
            # Method signature
            param_names = []
            for arg in method.args.args:
                param_names.append(arg.arg)
            signature = f"{method.name}({', '.join(param_names)})"
            doc.append(f"- `{signature}`")
            
            # Method docstring
            method_doc = get_class_docstring(method)
            if method_doc:
                first_line = method_doc.split('\n')[0].strip()
                doc[-1] += f" - {first_line}"
            
            doc[-1] += '\n'
    
    doc.append("\n")
    return '\n'.join(doc)

def scan_module(module_name, module_path, output_file):
    """Scan a module and generate documentation for all classes using AST."""
    print(f"Scanning module: {module_name}")
    output_file.write(f"## {module_name.split('.')[-1].capitalize()} Module\n\n")
    
    # Get all Python files in the module directory
    python_files = []
    for root, _, files in os.walk(module_path):
        for file in files:
            if is_valid_python_file(file):
                python_files.append(os.path.join(root, file))
    
    # Sort files for consistent output
    python_files.sort()
    
    # Parse files and scan for classes
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Find all class definitions
            classes = []
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append(node)
            
            # Write classes documentation
            for cls in classes:
                output_file.write(generate_class_doc(file_path, cls))
                
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            continue
    
    output_file.write("---\n\n")

def main():
    # Define modules to scan
    modules = [
        {
            "name": "qlib.contrib.model",
            "path": "/home/firewind0/qlib/qlib/contrib/model"
        },
        {
            "name": "qlib.contrib.strategy",
            "path": "/home/firewind0/qlib/qlib/contrib/strategy"
        },
        {
            "name": "qlib.contrib.data",
            "path": "/home/firewind0/qlib/qlib/contrib/data"
        },
        {
            "name": "qlib.contrib.report",
            "path": "/home/firewind0/qlib/qlib/contrib/report"
        },
        {
            "name": "qlib.contrib.workflow",
            "path": "/home/firewind0/qlib/qlib/contrib/workflow"
        }
    ]
    
    output_path = "/home/firewind0/qlib/docs/api/classes_contrib.md"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Qlib Contrib Modules Class Design Documentation\n\n")
        f.write("This document provides class design documentation for all modules in qlib/contrib/ directory.\n\n")
        f.write("## Table of Contents\n")
        for module in modules:
            title = module['name'].split('.')[-1].capitalize()
            f.write(f"1. [{title} Classes](#{title.lower()}-classes)\n")
        f.write("\n---\n\n")
        
        for module in modules:
            scan_module(module['name'], module['path'], f)
    
    print(f"\nDocumentation generated successfully: {output_path}")

if __name__ == "__main__":
    main()
