# Qlib 项目说明

## 项目概览

Qlib是Microsoft开源的AI导向量化投资平台，覆盖数据预处理、模型训练、回测、投资组合优化和订单执行的完整流程。

## 技术栈

- Python 3.8-3.12
- NumPy, Pandas
- PyTorch, LightGBM, XGBoost, CatBoost
- MLflow, Redis, MongoDB
- Cython (用于性能关键操作)

## 代码风格

- 使用 **Black** 格式化（行长度 120）
- 使用 **Pylint** 进行静态分析
- 使用 **Flake8** 进行 linting
- 使用 **mypy** 进行类型检查
- 函数命名：snake_case
- 类命名：PascalCase

## 测试

```bash
# 安装测试依赖
make test

# 运行测试
cd tests
pytest . -m "not slow"  # 排除慢速测试
```
测试环境是venv0，执行source /venv0/bin/activate 后执行python脚本

## 构建与运行

### 开发环境
```bash
make dev              # 安装所有开发依赖
make install           # 编译Cython扩展并安装
```

### 数据准备
```bash
# 获取1d数据
python -m qlib.cli.data qlib_data --target_dir ~/.qlib/qlib_data/cn_data --region cn

# 获取1min数据
python -m qlib.cli.data qlib_data --target_dir ~/.qlib/qlib_data/cn_data_1min --region cn --interval 1min
```

### 运行示例
```bash
cd examples
qrun benchmarks/LightGBM/workflow_config_lightgbm_Alpha158.yaml
```

### 代码质量检查
```bash
make lint  # 运行所有检查
make black  # 检查格式
make pylint  # 静态分析
make flake8  # linting
make mypy  # 类型检查
```

## 项目结构

```
qlib/
├── data/           # 数据管理层：存储、操作、数据集
│   ├── _libs/       # Cython扩展（rolling, expanding）需编译
│   ├── dataset/     # 数据集加载、处理
│   └── storage/     # 存储后端
├── model/          # 模型接口
├── workflow/       # ML工作流管理
├── backtest/       # 回测引擎
├── strategy/       # 交易策略
├── rl/            # 强化学习
├── contrib/        # 社区贡献
│   ├── model/       # 各种模型实现（LightGBM, XGBoost, PyTorch模型等）
│   ├── strategy/    # 策略优化器
│   ├── data/        # 数据处理器和handler
│   └── report/      # 分析报告
├── cli/            # 命令行工具 (qrun)
└── utils/          # 工具函数
```


## Project Rules (项目规则)

在开发qlib项目时，必须遵守以下规则：

1. **文档索引** (`docs/project_index.md`):
   - `docs/` 目录下必须有一个 `project_index.md` 文件作为项目所有文档的索引
   - 新增或修改文档后，必须更新 `project_index.md`

2. **版本号规范**:
   - 所有的更新方案都要有对应的更新版本号
   - 版本号格式: `v[主版本].[次版本].[修订号]`
     - 主版本: 重大架构变更
     - 次版本: 新功能模块添加
     - 修订号: Bug修复和优化

3. **优化计划文档** (`docs/xxx_v.aaa_optimize.md`):
   - 每次优化前需要把优化计划方案写到 `docs/` 目录下
   - 文档命名格式: `xxx_v.aaa_optimize.md`
     - `xxx`: 模块名（如: backtest_visualization, data_service）
     - `aaa`: 版本号（如: 1.1.0）
   - 优化完成后需要把结果更新到对应文档里
   - 每次完成后必须更新 `project_index.md`

4. **测试要求**:
   - 所有的优化、新功能开发都要有对应的测试方案
   - 测试文档必须覆盖所有的功能和模块
   - 特别注意以下测试覆盖:
     - Web端API接口测试
     - Web端界面交互测试
     - 数据加载和验证测试
     - 策略执行测试

## 约定

### Git Commit 风格

遵循 conventional commits 格式：

- `fix: <description>` - bug修复
- `feat: <description>` - 新功能
- `refactor: <description>` - 重构
- `docs: <description>` - 文档
- `test: <description>` - 测试
- `chore: <description>` - 杂项
- `perf: <description>` - 性能优化
- `ci: <description>` - CI配置

示例：
```
fix(security): use RestrictedUnpickler in load_instance
refactor(data_collector): use akshare to build unified trade calendar
```

### Pre-commit Hooks

项目配置了 pre-commit hooks，会自动运行：
- Black 格式化检查
- Flake8 linting

## 常见任务

| 任务 | 位置 |
|------|------|
| 添加新模型 | `qlib/contrib/model/` |
| 添加数据处理器 | `qlib/contrib/data/handler.py` |
| 添加策略 | `qlib/contrib/strategy/` |
| 查看示例 | `examples/benchmarks/` |
| 理解数据API | `qlib/data/__init__.py` |
| 配置QLib | `qlib/config.py` |

## 特殊注意事项

1. **Cython编译**：`qlib/data/_libs/` 中的 .pyx 文件需要编译
2. **macOS多线程**：限制OpenMP线程数以避免段错误
3. **Pandas版本**：某些功能需要pandas>=1.1
4. **数据缓存**：QLib有缓存机制，初始化时可配置
