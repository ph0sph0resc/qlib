# cli/__init__.py 模块文档

## 文件概述
此文件是CLI模块的初始化文件，使用fire命令行框架来创建命令行接口。

## 功能
- 将`GetData`类注册为fire命令
- 提供命令行数据下载接口

## 使用方式
```bash
python -m qlib.cli.data <command> <args>
```

## 与其他模块的关系
- `qlib.tests.data`: 提供GetData类
- `fire`: Python命令行框架
