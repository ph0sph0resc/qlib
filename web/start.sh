#!/bin/bash
# QLib Web启动脚本

echo "===================================="
echo "  QLib可视化Web平台"
echo "===================================="
echo

# 检查Python版本
python3 --version

# 进入web目录
cd "$(dirname "$0")"

# 安装依赖
echo "安装依赖..."
pip install -r requirements.txt

# 启动Flask应用
echo "启动Flask应用..."
python3 app.py
