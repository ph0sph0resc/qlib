# QLib量化投资可视化平台

QLib量化投资平台是一个基于Web的QLib可视化工具，提供因子测试、模型训练、回测和记录分析的完整功能。

## 功能特性

- **因子测试**：分析因子的IC值、Rank IC等指标
- **模型训练**：支持20+种机器学习和深度学习模型
- **策略回测**：完整的回测功能和结果可视化
- **记录分析**：历史实验记录管理和对比
- **可视化**：基于Chart.js的交互式图表

## 技术栈

- **前端**：HTML + Chart.js + Bootstrap 5
- **后端**：Flask (Python)
- **任务处理**：Python后台线程
- **数据存储**：SQLite + QLib原生存储

## 安装

### 前置要求

- Python 3.8+
- QLib 已安装
- 现代浏览器（Chrome、Firefox、Safari、Edge）

### 安装步骤

1. 克隆仓库或进入web目录：
```bash
cd /path/to/qlib/web
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. （可选）下载Chart.js和Bootstrap：
```bash
# 脚本会自动下载缺失的库
python3 download_libs.py
```

## 使用

### 启动服务

使用启动脚本：
```bash
./start.sh
```

或直接运行：
```bash
python3 app.py
```

服务默认运行在 `http://localhost:5000`

### 访问页面

- 首页：http://localhost:5000/
- 因子测试：http://localhost:5000/factor_test
- 模型训练：http://localhost:5000/model_train
- 回测：http://localhost:5000/backtest
- 记录分析：http://localhost:5000/analysis

## 配置

### 环境变量

可以在启动时设置以下环境变量：

- `QLIB_WEB_HOST`：服务监听地址（默认：0.0.0.0）
- `QLIB_WEB_PORT`：服务端口（默认：5000）
- `QLIB_WEB_DEBUG`：调试模式（默认：True）
- `QLIB_WEB_SECRET_KEY`：Flask密钥（生产环境必须设置）

### 配置文件

`config.py` 包含主要的配置选项：

```python
# 数据目录
DATA_DIR = 'data'
LOGS_DIR = 'logs'

# 数据库
DATABASE_PATH = 'data/qlib_web.db'

# 任务设置
MAX_CONCURRENT_TASKS = 3
TASK_TIMEOUT = 3600
```

## 支持的模型

### 传统机器学习模型
- LGBModel (LightGBM)
- XGBModel (XGBoost)
- CatModel (CatBoost)
- Linear (线性回归)

### 深度学习模型
- LSTM
- GRU
- Transformer
- ALSTM (Attention LSTM)
- TCN (Time Convolutional Network)
- TFT (Temporal Fusion Transformer)
- GATs (Graph Attention Networks)
- Localformer

### 高级模型
- DoubleEnsemble
- TRA (Time Recurrent Attention)
- TabNet
- IGMTF
- KRNN (Kernel RNN)
- ADARNN
- HIST

### 高频模型
- HFLGBModel

## API文档

### 系统API

- `GET /api/status` - 获取系统状态
- `GET /api/examples` - 获取所有示例配置
- `GET /api/models` - 获取可用模型列表
- `GET /api/markets` - 获取可用市场列表

### 配置API

- `GET /api/config/template/<category>/<template_name>` - 获取YAML模板
- `GET /api/config/schema/<model_name>` - 获取模型参数schema
- `POST /api/config/validate` - 验证YAML配置
- `POST /api/config/generate` - 根据表单生成YAML

### 任务API

- `POST /api/task` - 创建新任务
- `POST /api/task/<id>/start` - 启动任务
- `POST /api/task/<id>/stop` - 停止任务
- `GET /api/task/<id>/status` - 获取任务状态
- `GET /api/task/<id>/log` - 获取任务日志
- `GET /api/tasks` - 列出所有任务

### 分析API

- `GET /api/analysis/list` - 获取实验列表
- `GET /api/analysis/detail/<id>` - 获取实验详情

## 数据目录结构

```
web/
├── app.py                 # Flask主应用
├── config.py              # 配置文件
├── requirements.txt       # 依赖
├── static/                # 静态资源
│   ├── css/
│   ├── js/
│   └── img/
├── templates/             # HTML模板
├── api/                  # API模块
│   ├── qlib_wrapper.py
│   ├── config_parser.py
│   ├── task_manager.py
│   └── models.py
├── data/                 # 数据目录
│   └── qlib_web.db      # SQLite数据库
└── logs/                 # 日志目录
```

## 故障排除

### 端口已被占用

如果5000端口已被占用，可以通过环境变量指定其他端口：

```bash
QLIB_WEB_PORT=8000 python3 app.py
```

### 数据库错误

删除数据库文件重新创建：

```bash
rm data/qlib_web.db
```

### QLib初始化失败

确保QLib已正确安装并配置了数据目录：

```bash
python3 -c "from qlib import init; init()"
```

## 开发

### 运行调试模式

```bash
python3 app.py
# 或
FLASK_ENV=development python3 app.py
```

### 添加新的模型

1. 在 `api/config_parser.py` 的 `MODEL_SCHEMAS` 中添加模型参数schema
2. 在 `api/qlib_wrapper.py` 中实现模型训练逻辑（如果需要特殊处理）
3. 在前端页面中添加模型选项

## 许可证

与QLib主项目保持一致。

## 贡献

欢迎提交问题和拉取请求！

## 联系

如有问题，请提交GitHub Issue。
