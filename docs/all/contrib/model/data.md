# data 模块详细文档

## 模块概述

`data` 模块提供了数据准备的命令行接口（CLI），用于下载和准备 QLib 所需的市场数据。该模块使用 Google Fire 库将 `GetData` 类暴露为命令行工具。

通过这个命令行工具，用户可以方便地下载市场数据、准备数据集等操作，无需编写 Python 代码。

---

## 文件结构

```python
# Copyright (c) Microsoft Corporation.
# Licensed under MIT License.

import fire
from qlib.tests.data import GetData

if __name__ == "__main__":
    fire.Fire(GetData)
```

**核心逻辑：**
- 使用 `fire.Fire()` 将 `GetData` 类转换为命令行接口
- 当直接运行该文件时，会解析命令行参数并调用 `GetData` 类的相应方法

---

## 使用说明

### 基本用法

```bash
# 使用 Python 运行
python -m qlib.cli.data [command] [options]

# 或者直接运行文件
python qlib/cli/data.py [command] [options]
```

### 常用命令

由于该模块通过 `fire.Fire(GetData)` 暴露 `GetData` 类的所有方法作为命令，具体可用命令取决于 `qlib.tests.data.GetData` 类的实现。

#### 1. 下载数据

```bash
# 下载默认数据集
python -m qlib.cli.data qlib_data

# 下载到指定目录
python -m qlib.cli.data qlib_data --target_dir ~/.qlib/qlib_data/cn_data

# 指定地区
python -m qlib.cli.data qlib_data --region cn
python -m qlib.cli.data qlib_data --region us

# 指定时间间隔
python -m qlib.cli.data qlib_data --interval 1day
python -m qlib.cli.data qlib_data --interval 1min
```

#### 2. 查看帮助信息

```bash
# 查看所有可用命令
python -m qlib.cli.data --help

# 查看特定命令的帮助
python -m qlib.cli.data qlib_data --help
```

---

## 完整使用流程示例

### 示例 1：下载中国A股日线数据

```bash
# 下载中国A股日线数据到默认目录
python -m qlib.cli.data qlib_data \
    --target_dir ~/.qlib/qlib_data/cn_data \
    --region cn \
    --interval 1day
```

**输出示例：**
```
Downloading data for region: cn
Interval: 1day
Target directory: /home/user/.qlib/qlib_data/cn_data
[████████████████████] 100%
Data download completed successfully.
```

### 示例 2：下载中国A股分钟线数据

```bash
# 下载中国A股1分钟数据（用于高频回测）
python -m qlib.cli.data qlib_data \
    --target_dir ~/.qlib/qlib_data/cn_data_1min \
    --region cn \
    --interval 1min
```

### 示例 3：下载美国股市数据

```bash
# 下载美国股市日线数据
python -m qlib.cli.data qlib_data \
    --target_dir ~/.qlib/qlib_data/us_data \
    --region us \
    --interval 1day
```

### 示例 4：在脚本中使用

```python
#!/bin/bash

# 数据准备脚本
# prepare_data.sh

echo "=== QLib 数据准备脚本 ==="

# 设置数据目录
DATA_DIR=~/.qlib/qlib_data/cn_data

# 创建目录
mkdir -p $DATA_DIR

# 下载日线数据
echo "下载日线数据..."
python -m qlib.cli.data qlib_data \
    --target_dir $DATA_DIR \
    --region cn \
    --interval 1day

# 下载数据
echo "下载1分钟数据..."
MIN_DIR=~/.qlib/qlib_data/cn_data_1min
mkdir -p $MIN_DIR
python -m qlib.cli.data qlib_data \
    --target_dir $MIN_DIR \
    --region cn \
    --interval 1min

echo "数据准备完成！"
```

### 示例 5：Python 脚本中调用

虽然该模块主要设计为命令行使用，但也可以在 Python 代码中直接调用 `GetData` 类：

```python
from qlib.tests.data import GetData

# 创建 GetData 实例
data_getter = GetData()

# 调用方法（假设有这些方法）
# data_getter.qlib_data(
#     target_dir="~/.qlib/qlib_data/cn_data",
#     region="cn",
#     interval="1day"
# )
```

---

## 数据目录结构

下载的数据通常存储在以下目录结构中：

```
~/.qlib/qlib_data/
├── cn_data/              # 中国A股日线数据
│   ├── calendars/        # 交易日历
│   ├── instruments/      # 股票列表和分类
│   ├── features/         # 特征数据
│   └── raw/             # 原始数据
├── cn_data_1min/        # 中国A股分钟数据
│   └── ...
└── us_data/             # 美股数据
    └── ...
```

---

## 常见参数说明

由于该模块封装了 `GetData` 类，常见参数可能包括：

| 参数 | 类型 | 说明 |
|------|------|------|
| `target_dir` | str | 数据存储目录路径 |
| `region` | str | 数据地区（cn, us 等） |
| `interval` | str | 数据间隔（1day, 1min 等） |
| `start_date` | str | 数据开始日期 |
| `end_date` | str | 数据结束日期 |
| `skip_download` | bool | 跳过下载，仅处理已有数据 |
| `skip_prepare` | bool | 跳过数据处理 |
| `force_update` | bool | 强制更新已有数据 |

---

## 使用场景

### 场景 1：初次安装 QLib

首次安装 QLib 后，需要下载和准备数据：

```bash
# 1. 安装 QLib
pip install pyqlib

# 2. 下载中国A股数据
python -m qlib.cli.data qlib_data \
    --target_dir ~/.qlib/qlib_data/cn_data \
    --region cn

# 3. 验证数据
python -c "import qlib; qlib.init(provider_uri='~/.qlib/qlib_data/cn_data', region='cn')"
```

### 场景 2：更新数据

定期更新市场数据以获取最新的行情：

```bash
# 更新到最新日期
python -m qlib.cli.data qlib_data \
    --target_dir ~/.qlib/qlib_data/cn_data \
    --region cn \
    --interval 1day \
    --force_update
```

### 场景 3：多数据源准备

为不同的回测策略准备不同频率的数据：

```bash
#!/bin/bash

# 准备所有数据源
prepare_all_data() {
    # 日线数据（用于中低频策略）
    echo "准备日线数据..."
    python -m qlib.cli.data qlib_data \
        --target_dir ~/.qlib/qlib_data/cn_data_1day \
        --region cn \
        --interval 1day

    # 分钟数据（用于中高频策略）
    echo "准备分钟数据..."
    python -m qlib.cli.data qlib_data \
        --target_dir ~/.qlib/qlib_data/cn_data_1min \
        --region cn \
        --interval 1min
}

# 执行
prepare_all_data
```

### 场景 4：在 Docker 中准备数据

在 Docker 容器中准备数据，用于生产环境：

```dockerfile
# Dockerfile
FROM python:3.9-slim

# 安装依赖
RUN pip install pyqlib

# 准备数据
RUN python -m qlib.cli.data qlib_data \
    --target_dir /data/qlib_data \
    --region cn \
    --interval 1day

# 设置环境变量
ENV QLIB_DATA_DIR=/data/qlib_data

# 启动应用
CMD ["python", "app.py"]
```

### 场景 5：CI/CD 集成

在 CI/CD 流程中自动准备测试数据：

```yaml
# .github/workflows/test.yml
name: QLib Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: |
          pip install pyqlib

      - name: Prepare test data
        run: |
          python -m qlib.cli.data qlib_data \
            --target_dir ~/.qlib/qlib_data/test_data \
            --region cn \
            --interval 1day

      - name: Run tests
        run: |
          pytest tests/
```

---

## 故障排查

### 问题 1：权限错误

**错误信息：**
```
PermissionError: [Errno 13] Permission denied: '/path/to/data'
```

**解决方法：**
```bash
# 检查目录权限
ls -la ~/.qlib/

# 修复权限
chmod -R 755 ~/.qlib/
```

### 问题 2：网络连接失败

**错误信息：**
```
ConnectionError: Failed to download data
```

**解决方法：**
```bash
# 检查网络连接
ping -c 4 api.example.com

# 如果需要使用代理
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080

# 重新下载
python -m qlib.cli.data qlib_data --target_dir ...
```

### 问题 3：磁盘空间不足

**错误信息：**
```
OSError: [Errno 28] No space left on device
```

**解决方法：**
```bash
# 检查磁盘空间
df -h

# 清理不必要的文件
rm -rf ~/.qlib/qlib_data/old_data

# 重新下载
python -m qlib.cli.data qlib_data --target_dir ...
```

---

## 性能优化建议

### 1. 使用 SSD 存储数据

将数据存储在 SSD 上可以显著提高读取速度：

```bash
# 使用 SSD 目录
python -m qlib.cli.data qlib_data \
    --target_dir /mnt/ssd/qlib_data \
    --region cn
```

### 2. 批量下载

如果需要多个地区或频率的数据，可以并行下载：

```bash
# 使用 GNU parallel
parallel python -m qlib.cli.data qlib_data \
    --target_dir ~/.qlib/qlib_data/{} \
    --region {} ::: cn_data us_data

# 或者使用后台任务
python -m qlib.cli.data qlib_data --target_dir cn --region cn &
python -m qlib.cli.data qlib_data --target_dir us --region us &
wait
```

### 3. 增量更新

使用 `force_update=false` 只下载新增的数据：

```bash
python -m qlib.cli.data qlib_data \
    --target_dir ~/.qlib/qlib_data/cn_data \
    --region cn \
    --force_update=false
```

---

## 注意事项

1. **数据下载时间**：首次下载可能需要较长时间，取决于数据量和网络速度
2. **存储空间**：完整的数据集可能占用数 GB 的磁盘空间
3. **网络稳定性**：确保下载过程中网络连接稳定，避免下载中断
4. **数据更新**：市场数据定期更新，建议定期运行更新脚本
5. **地区设置**：确保 `region` 参数与实际需要的数据地区匹配
6. **路径权限**：确保对目标目录有读写权限
7. **依赖版本**：保持 QLib 版本更新，以获取最新的数据处理功能

---

## 相关模块

- `qlib.tests.data.GetData`：数据下载和处理的核心类
- `qlib.data.D`：数据访问接口
- `qlib.contrib.data.handler`：数据处理器
- `fire`：Google Fire 命令行工具库

---

## 扩展阅读

- [QLib 官方文档](https://qlib.readthedocs.io/)
- [数据准备指南](https://qlib.readthedocs.io/en/latest/component/data.html)
- [Qlib 使用示例](https://github.com/microsoft/qlib/tree/main/examples)
