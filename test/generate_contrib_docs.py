#!/usr/bin/env python3
"""
Script to generate class design documentation for qlib/contrib modules.
"""

import os
import sys
import inspect
import importlib
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

def get_all_classes(module):
    """Get all classes defined in a module."""
    classes = []
    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj):
            # Only include classes defined in the module (not imported)
            if obj.__module__ == module.__name__:
                classes.append(obj)
    return classes

def generate_class_doc(cls):
    """Generate documentation for a single class."""
    doc = []
    doc.append(f"### {cls.__name__}\n")
    
    # Class docstring
    if cls.__doc__:
        first_line = cls.__doc__.split('\n')[0].strip()
        doc.append(f"{first_line}\n")
    
    # Inheritance
    bases = cls.__bases__
    if bases and not (len(bases) == 1 and bases[0] == object):
        base_names = [f"`{base.__name__}`" for base in bases]
        doc.append(f"**Inherits from**: {', '.join(base_names)}\n")
    
    # Class signature
    try:
        signature = inspect.signature(cls.__init__)
        if str(signature) != "(*args, **kwargs)":
            doc.append(f"**Signature**: `{cls.__name__}{signature}`\n")
    except:
        pass
    
    # Methods
    methods = []
    for name, obj in inspect.getmembers(cls):
        if inspect.isfunction(obj) or inspect.ismethod(obj):
            if obj.__name__ != '__init_subclass__':
                # Only include methods defined in this class (not inherited)
                if hasattr(obj, '__module__') and obj.__module__ == cls.__module__:
                    methods.append(obj)
    
    if methods:
        doc.append(f"**Methods**:\n")
        for method in methods:
            try:
                sig = inspect.signature(method)
                doc.append(f"- `{method.__name__}{sig}`")
                # Add method docstring first line
                if method.__doc__:
                    mdoc = method.__doc__.split('\n')[0].strip()
                    if mdoc:
                        doc[-1] += f" - {mdoc}"
                doc[-1] += '\n'
            except:
                pass
    
    doc.append("\n")
    return '\n'.join(doc)

def scan_module(module_name, module_path, output_file):
    """Scan a module and generate documentation for all classes."""
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
    
    # Import modules and scan for classes
    for file_path in python_files:
        rel_path = os.path.relpath(file_path, module_path).replace(os.sep, '.')[:-3]
        full_module_name = f"{module_name}.{rel_path}"
        
        try:
            module = importlib.import_module(full_module_name)
            
            # Get all classes in the module
            classes = get_all_classes(module)
            
            if classes:
                # Write classes documentation
                for cls in classes:
                    output_file.write(generate_class_doc(cls))
                    
        except Exception as e:
            print(f"Error importing {full_module_name}: {e}")
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
