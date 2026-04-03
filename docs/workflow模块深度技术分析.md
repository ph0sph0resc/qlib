# QLib Workflow 模块深度技术分析

## 目录

1. [模块概览](#模块概览)
2. [核心架构](#核心架构)
3. [R API 和上下文管理](#r-api-和上下文管理)
4. [Recorder 系统](#recorder-系统)
5. [Experiment 管理](#experiment-管理)
6. [任务管理系统](#任务管理系统)
7. [在线学习工作流](#在线学习工作流)
8. [记录模板系统](#记录模板系统)
9. [完整代码示例](#完整代码示例)

---

## 模块概览

QLib的workflow模块是一个强大的实验管理和工作流执行系统，它提供了比直接使用MLflow更高级的抽象和功能。

### 设计动机

根据`__init__.py`中的注释，该模块的设计动机包括：

1. **更直观的接口**：提供Recorder对象，有丰富的方法，而不是每次都使用run_id
2. **更丰富的特性**：
   - 自动记录代码差异
   - 直接log_object和load_object，而不是log_artifact和download_artifact
3. **多样化的后端支持**

### 模块结构

```
qlib/workflow/
├── __init__.py          # 核心API (R)
├── exp.py               # Experiment抽象基类和MLflow实现
├── expm.py              # Experiment管理器
├── recorder.py          # Recorder抽象基类和MLflow实现
├── record_temp.py       # 记录模板系统
├── utils.py             # 工具函数
├── online/              # 在线学习模块
│   ├── __init__.py
│   ├── manager.py       # OnlineManager
│   ├── strategy.py      # OnlineStrategy
│   ├── update.py        # 更新机制
│   └── utils.py
└── task/                # 任务管理模块
    ├── __init__.py
    ├── collect.py       # 任务收集器
    ├── gen.py           # 任务生成器
    ├── manage.py        # TaskManager
    └── utils.py
```

---

## 核心架构

### 类层次结构

```
QlibRecorder (全局R对象)
    ├── ExpManager (实验管理器)
    │   └── MLflowExpManager (MLflow实现)
    └── Experiment (实验)
        └── MLflowExperiment (MLflow实现)
            └── Recorder (记录器)
                └── MLflowRecorder (MLflow实现)

TaskManager (任务管理)
OnlineManager (在线学习管理)
    └── OnlineStrategy (在线策略)
        └── RollingStrategy (滚动策略)
```

### 数据流

```
用户代码 → R.start() → 创建Experiment → 创建Recorder
    ↓
记录参数、指标、对象
    ↓
R.end() → 保存状态
    ↓
后续可查询、分析、重用
```

---

## R API 和上下文管理

### 全局 R 对象

`R`是workflow模块的核心入口点，是一个全局的`QlibRecorder`实例，通过`RecorderWrapper`包装。

```python
# 全局记录器
R: QlibRecorderWrapper = RecorderWrapper()
```

### R.start() 上下文管理器

`R.start()`是最常用的接口，使用Python的`with`语句进行上下文管理：

```python
@contextmanager
def start(
    self,
    *,
    experiment_id: Optional[Text] = None,
    experiment_name: Optional[Text] = None,
    recorder_id: Optional[Text] = None,
    recorder_name: Optional[Text] = None,
    uri: Optional[Text] = None,
    resume: bool = False,
):
    # ... 实现细节
```

**使用示例：**

```python
# 启动新实验和记录器
with R.start(experiment_name='test', recorder_name='recorder_1'):
    model.fit(dataset)
    R.log_params(learning_rate=0.01)
    R.log_metrics(train_loss=0.33)
    R.save_objects(model=model)

# 恢复之前的实验和记录器
with R.start(experiment_name='test', recorder_name='recorder_1', resume=True):
    # 继续操作
```

**生命周期：**
1. 进入`with`块：调用`start_exp()`，激活实验和记录器
2. 执行块内代码：可以记录各种信息
3. 正常退出：调用`end_exp(Recorder.STATUS_FI)`，标记为FINISHED
4. 异常退出：调用`end_exp(Recorder.STATUS_FA)`，标记为FAILED

### R 的主要方法

| 方法 | 描述 |
|------|------|
| `start()` | 上下文管理器，启动实验 |
| `start_exp()` / `end_exp()` | 低级方法，手动管理实验生命周期 |
| `log_params()` | 记录参数 |
| `log_metrics()` | 记录指标 |
| `save_objects()` / `load_object()` | 保存/加载Python对象 |
| `set_tags()` | 设置标签 |
| `get_exp()` / `get_recorder()` | 获取实验/记录器 |
| `list_experiments()` / `list_recorders()` | 列出实验/记录器 |
| `search_records()` | 搜索记录 |
| `delete_exp()` / `delete_recorder()` | 删除实验/记录器 |

### URI 管理

```python
# 获取当前URI
uri = R.get_uri()

# 设置默认URI
R.set_uri("file:///path/to/mlruns")

# 临时使用不同的URI
with R.uri_context("file:///other/path"):
    # 在这个上下文中使用新URI
    with R.start():
        pass
```

---

## Recorder 系统

### Recorder 基类

`Recorder`是一个抽象基类，定义了记录器的接口：

```python
class Recorder:
    # 状态类型
    STATUS_S = "SCHEDULED"
    STATUS_R = "RUNNING"
    STATUS_FI = "FINISHED"
    STATUS_FA = "FAILED"

    # 主要方法
    def start_run(self): ...
    def end_run(self): ...
    def log_params(self, **kwargs): ...
    def log_metrics(self, step=None, **kwargs): ...
    def save_objects(self, local_path=None, artifact_path=None, **kwargs): ...
    def load_object(self, name): ...
    def set_tags(self, **kwargs): ...
    def list_artifacts(self, artifact_path=None): ...
    def list_metrics(self): ...
    def list_params(self): ...
    def list_tags(self): ...
```

### MLflowRecorder 实现

`MLflowRecorder`是基于MLflow的具体实现：

```python
class MLflowRecorder(Recorder):
    def __init__(self, experiment_id, uri, name=None, mlflow_run=None):
        super().__init__(experiment_id, name)
        self._uri = uri
        self.client = mlflow.tracking.MlflowClient(tracking_uri=self._uri)
        # ...
```

**核心特性：**

1. **异步日志记录**：使用`AsyncCaller`进行异步日志记录，提高性能
   ```python
   @AsyncCaller.async_dec(ac_attr="async_log")
   def log_params(self, **kwargs):
       for name, data in kwargs.items():
           self.client.log_param(self.id, name, data)
   ```

2. **自动记录未提交代码**：
   ```python
   def _log_uncommitted_code(self):
       for cmd, fname in [
           ("git diff", "code_diff.txt"),
           ("git status", "code_status.txt"),
           ("git diff --cached", "code_cached.txt"),
       ]:
           # 执行命令并记录
   ```

3. **自动记录命令和环境变量**：
   ```python
   self.log_params(**{"cmd-sys.argv": " ".join(sys.argv)})
   self.log_params(**{k: v for k, v in os.environ.items() if k.startswith("_QLIB_")})
   ```

4. **对象序列化**：使用`Serializable.general_dump`和`restricted_pickle_loads`
   ```python
   def save_objects(self, local_path=None, artifact_path=None, **kwargs):
       temp_dir = Path(tempfile.mkdtemp()).resolve()
       for name, data in kwargs.items():
           path = temp_dir / name
           Serializable.general_dump(data, path)
           self.client.log_artifact(self.id, temp_dir / name, artifact_path)
   ```

---

## Experiment 管理

### Experiment 基类

```python
class Experiment:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.active_recorder = None  # 每次只能有一个活动的recorder

    def start(self, *, recorder_id=None, recorder_name=None, resume=False):
        # 启动实验和recorder
    def end(self, recorder_status=Recorder.STATUS_S):
        # 结束实验
    def create_recorder(self, recorder_name=None):
        # 创建recorder
    def get_recorder(self, recorder_id=None, recorder_name=None, create: bool = True, start: bool = False):
        # 获取或创建recorder
    def list_recorders(self, rtype: Literal["dict", "list"] = RT_D):
        # 列出所有recorders
```

### MLflowExperiment 实现

```python
class MLflowExperiment(Experiment):
    def __init__(self, id, name, uri):
        super().__init__(id, name)
        self._uri = uri
        self._client = mlflow.tracking.MlflowClient(tracking_uri=self._uri)
```

**关键方法：**

1. **get_recorder() - 智能获取/创建recorder**：
   - 如果有活动的recorder且未指定id/name，返回活动的recorder
   - 如果指定了id/name，尝试获取，不存在则创建（如果create=True）
   - 支持自动启动recorder

2. **list_recorders() - 过滤和列出recorders**：
   ```python
   def list_recorders(
       self,
       rtype: Literal["dict", "list"] = Experiment.RT_D,
       max_results: int = UNLIMITED,
       status: Union[str, None] = None,
       filter_string: str = "",
   ):
       # 支持按状态过滤、自定义过滤字符串
   ```

### ExpManager 实验管理器

`ExpManager`管理多个Experiment：

```python
class ExpManager:
    def __init__(self, uri: Text, default_exp_name: Optional[Text]):
        self.default_uri = uri
        self._active_exp_uri = None
        self._default_exp_name = default_exp_name
        self.active_experiment = None  # 每次只能有一个活动的experiment
```

**URI 管理机制：**
- `default_uri`：从配置`C.exp_manager["kwargs"]["uri"]`获取
- `_active_exp_uri`：当前活动的URI，临时覆盖default_uri
- `uri`属性：返回`_active_exp_uri or default_uri`

**关键方法：**
- `start_exp()` / `end_exp()`：启动/结束实验
- `get_exp()`：智能获取/创建实验
- `create_exp()` / `delete_exp()`：创建/删除实验
- `list_experiments()`：列出所有实验
- `search_records()`：跨实验搜索记录

---

## 任务管理系统

### TaskManager

`TaskManager`使用MongoDB存储和管理任务，支持分布式任务执行。

**任务结构：**
```python
{
    'def': pickle序列化的任务定义,
    'filter': JSON-like数据用于过滤任务,
    'status': 'waiting' | 'running' | 'done' | 'part_done',
    'res': pickle序列化的任务结果,
    'priority': 优先级 (可选),
}
```

**状态类型：**
- `STATUS_WAITING = "waiting"`：等待执行
- `STATUS_RUNNING = "running"`：正在执行
- `STATUS_DONE = "done"`：完成
- `STATUS_PART_DONE = "part_done"`：部分完成

**核心方法：**

1. **任务创建：**
   ```python
   def create_task(self, task_def_l, dry_run=False, print_nt=False) -> List[str]:
       # 检查任务是否已存在
       # 插入新任务
       # 返回任务ID列表
   ```

2. **安全获取任务（上下文管理器）：**
   ```python
   @contextmanager
   def safe_fetch_task(self, query={}, status=STATUS_WAITING):
       task = self.fetch_task(query=query, status=status)
       try:
           yield task
       except Exception:
           if task is not None:
               self.return_task(task, status=status)  # 异常时返回任务
           raise
   ```

3. **提交结果：**
   ```python
   def commit_task_res(self, task, res, status=STATUS_DONE):
       # 保存结果并更新状态
   ```

4. **任务状态统计：**
   ```python
   def task_stat(self, query={}) -> dict:
       # 统计各状态的任务数量
   ```

5. **等待所有任务完成：**
   ```python
   def wait(self, query={}):
       # 等待直到所有任务完成
       # 显示进度条
   ```

**使用示例 - run_task()：**
```python
def run_task(
    task_func: Callable,
    task_pool: str,
    query: dict = {},
    force_release: bool = False,
    before_status: str = TaskManager.STATUS_WAITING,
    after_status: str = TaskManager.STATUS_DONE,
    **kwargs,
):
    # 循环获取任务并执行
    # 支持多阶段任务（WAITING → PART_DONE → DONE）
```

**命令行使用：**
```bash
# 列出所有任务池
python -m qlib.workflow.task.manage list

# 查看任务统计
python -m qlib.workflow.task.manage -t <pool_name> task_stat

# 等待任务完成
python -m qlib.workflow.task.manage -t <pool_name> wait

# 重置运行中的任务为等待状态
python -m qlib.workflow.task.manage -t <pool_name> reset_waiting
```

### 任务生成器 (TaskGen)

```python
class TaskGen(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def generate(self, task: dict) -> List[dict]:
        # 基于任务模板生成多个任务
```

#### RollingGen - 滚动任务生成

```python
class RollingGen(TaskGen):
    ROLL_EX = TimeAdjuster.SHIFT_EX  # 扩展窗口（固定开始日期）
    ROLL_SD = TimeAdjuster.SHIFT_SD  # 滑动窗口（固定窗口大小）

    def __init__(
        self,
        step: int = 40,
        rtype: str = ROLL_EX,
        ds_extra_mod_func: Union[None, Callable] = handler_mod,
        test_key="test",
        train_key="train",
        trunc_days: int = None,  # 避免未来信息泄露
    ):
        # ...
```

**使用示例：**
```python
task_generator(
    tasks=[task_template],
    generators=RollingGen(step=20, rtype=RollingGen.ROLL_SD)
)
```

#### 多视角任务生成

```python
class MultiHorizonGenBase(TaskGen):
    def __init__(self, horizon: List[int] = [5], label_leak_n=2):
        # 为不同预测 horizon 生成任务
```

### 任务收集器 (Collector)

```python
class Collector(Serializable):
    def __init__(self, process_list=[]):
        self.process_list = process_list

    def collect(self) -> dict:
        # 收集结果
        raise NotImplementedError

    def __call__(self, *args, **kwargs) -> dict:
        collected = self.collect()
        return self.process_collect(collected, self.process_list, *args, **kwargs)
```

#### RecorderCollector

从Recorder中收集结果：

```python
class RecorderCollector(Collector):
    def __init__(
        self,
        experiment,  # Experiment对象或名称
        process_list=[],
        rec_key_func=None,  # 如何从recorder获取key
        rec_filter_func=None,  # 如何过滤recorder
        artifacts_path={"pred": "pred.pkl"},  # artifact名称和路径
        artifacts_key=None,
        status: Iterable = {Recorder.STATUS_FI},
    ):
        # ...
```

**使用示例：**
```python
collector = RecorderCollector(
    experiment="my_experiment",
    artifacts_path={"pred": "pred.pkl", "ic": "sig_analysis/ic.pkl"},
    process_list=[RollingGroup(), AverageEnsemble()]
)
results = collector()
```

#### MergeCollector

合并多个Collector的结果：

```python
class MergeCollector(Collector):
    def __init__(
        self,
        collector_dict: Dict[str, Collector],
        process_list: List[Callable] = [],
        merge_func=None,
    ):
        # ...
```

---

## 在线学习工作流

### OnlineManager

`OnlineManager`管理在线策略的执行，支持真实在线交易和历史模拟。

```python
class OnlineManager(Serializable):
    STATUS_SIMULATING = "simulating"
    STATUS_ONLINE = "online"

    def __init__(
        self,
        strategies: Union[OnlineStrategy, List[OnlineStrategy]],
        trainer: Trainer = None,
        begin_time: Union[str, pd.Timestamp] = None,
        freq="day",
    ):
        # ...
```

**核心流程：**

1. **first_train() - 首次训练：**
   ```python
   def first_train(self, strategies: List[OnlineStrategy] = None, model_kwargs: dict = {}):
       # 对每个策略：
       #   1. 获取首次任务
       #   2. 训练模型
       #   3. 准备在线模型
       #   4. 记录历史
   ```

2. **routine() - 例行更新：**
   ```python
   def routine(
       self,
       cur_time: Union[str, pd.Timestamp] = None,
       task_kwargs: dict = {},
       model_kwargs: dict = {},
       signal_kwargs: dict = {},
   ):
       # 对每个策略：
       #   1. 准备新任务
       #   2. 训练模型
       #   3. 更新在线模型
       #   4. 更新预测（仅在线模式）
       #   5. 准备信号
   ```

3. **simulate() - 历史模拟：**
   ```python
   def simulate(
       self, end_time=None, frequency="day",
       task_kwargs={}, model_kwargs={}, signal_kwargs={}
   ):
       # 设置状态为SIMULATING
       # 对每个时间点执行routine()
       # 支持DelayTrainer进行延迟训练（并行化）
   ```

**四种使用场景：**

| 场景 | 描述 |
|------|------|
| Online + Trainer | 真实在线交易，逐次训练 |
| Online + DelayTrainer | 真实在线交易，批量训练 |
| Simulation + Trainer | 历史模拟，逐次训练 |
| Simulation + DelayTrainer | 历史模拟，批量训练（无时间依赖时） |

### OnlineStrategy

```python
class OnlineStrategy:
    def __init__(self, name_id: str):
        self.name_id = name_id
        self.tool = OnlineTool()

    def first_tasks(self) -> List[dict]:
        # 生成首批任务
        raise NotImplementedError

    def prepare_tasks(self, cur_time, **kwargs) -> List[dict]:
        # 基于当前时间准备新任务
        raise NotImplementedError

    def prepare_online_models(self, trained_models, cur_time=None) -> List[object]:
        # 从训练好的模型中选择在线模型
        # 默认实现：使用所有训练好的模型
        if not trained_models:
            return self.tool.online_models()
        self.tool.reset_online_tag(trained_models)
        return trained_models

    def get_collector(self) -> Collector:
        # 获取Collector用于收集结果
        raise NotImplementedError
```

#### RollingStrategy

```python
class RollingStrategy(OnlineStrategy):
    def __init__(
        self,
        name_id: str,
        task_template: Union[dict, List[dict]],
        rolling_gen: RollingGen,
    ):
        super().__init__(name_id=name_id)
        self.task_template = task_template
        self.rg = rolling_gen
        self.tool = OnlineToolR(self.exp_name)
```

**关键方法：**
- `first_tasks()`：使用rolling_gen生成首批滚动任务
- `prepare_tasks()`：检查是否需要生成新的滚动任务
- `_list_latest()`：列出最新的recorders
- `get_collector()`：获取RecorderCollector，按模型和滚动时段分组

---

## 记录模板系统

### RecordTemp 基类

```python
class RecordTemp:
    artifact_path = None  # artifact存储路径
    depend_cls = None     # 依赖的RecordTemp类

    def __init__(self, recorder):
        self._recorder = recorder

    def generate(self, **kwargs):
        # 生成记录并保存
        raise NotImplementedError

    def save(self, **kwargs):
        # 保存到recorder，自动处理artifact_path
        art_path = self.get_path()
        self.recorder.save_objects(artifact_path=art_path, **kwargs)

    def load(self, name: str, parents: bool = True):
        # 从recorder加载
        try:
            return self.recorder.load_object(self.get_path(name))
        except LoadObjectError:
            if parents and self.depend_cls:
                with class_casting(self, self.depend_cls):
                    return self.load(name, parents=True)
            raise
```

### 内置记录模板

#### SignalRecord - 信号记录

```python
class SignalRecord(RecordTemp):
    def __init__(self, model=None, dataset=None, recorder=None):
        super().__init__(recorder=recorder)
        self.model = model
        self.dataset = dataset

    def generate(self, **kwargs):
        # 生成预测
        pred = self.model.predict(self.dataset)
        self.save(**{"pred.pkl": pred})

        # 生成标签（如果可用）
        if isinstance(self.dataset, DatasetH):
            raw_label = self.generate_label(self.dataset)
            self.save(**{"label.pkl": raw_label})
```

#### SigAnaRecord - 信号分析记录

```python
class SigAnaRecord(ACRecordTemp):
    artifact_path = "sig_analysis"
    depend_cls = SignalRecord

    def _generate(self, label: Optional[pd.DataFrame] = None, **kwargs):
        pred = self.load("pred.pkl")
        label = self.load("label.pkl") if label is None else label

        # 计算IC、Rank IC
        ic, ric = calc_ic(pred.iloc[:, 0], label.iloc[:, self.label_col])
        metrics = {
            "IC": ic.mean(),
            "ICIR": ic.mean() / ic.std(),
            "Rank IC": ric.mean(),
            "Rank ICIR": ric.mean() / ric.std(),
        }

        # 记录指标
        self.recorder.log_metrics(**metrics)

        return {"ic.pkl": ic, "ric.pkl": ric}
```

#### PortAnaRecord - 投资组合分析记录

```python
class PortAnaRecord(ACRecordTemp):
    artifact_path = "portfolio_analysis"
    depend_cls = SignalRecord

    def __init__(
        self,
        recorder,
        config=None,  # 包含strategy、executor、backtest配置
        risk_analysis_freq: Union[List, str] = None,
        indicator_analysis_freq: Union[List, str] = None,
        skip_existing=False,
    ):
        # ...

    def _generate(self, **kwargs):
        pred = self.load("pred.pkl")

        # 替换配置中的<PRED>占位符
        placeholder_value = {"<PRED>": pred}

        # 执行回测
        portfolio_metric_dict, indicator_dict = normal_backtest(
            executor=self.executor_config,
            strategy=self.strategy_config,
            **self.backtest_config
        )

        # 风险分析
        for _analysis_freq in self.risk_analysis_freq:
            report_normal, _ = portfolio_metric_dict.get(_analysis_freq)
            analysis = {
                "excess_return_without_cost": risk_analysis(report_normal["return"] - report_normal["bench"]),
                "excess_return_with_cost": risk_analysis(report_normal["return"] - report_normal["bench"] - report_normal["cost"]),
            }
            # 记录指标
            # ...

        return artifact_objects
```

#### MultiPassPortAnaRecord - 多遍回测

```python
class MultiPassPortAnaRecord(PortAnaRecord):
    def __init__(self, recorder, pass_num=10, shuffle_init_score=True, **kwargs):
        self.pass_num = pass_num
        self.shuffle_init_score = shuffle_init_score
        # ...

    def _generate(self, **kwargs):
        # 运行多遍回测
        # 每遍打乱初始信号（如果shuffle_init_score=True）
        # 统计年化收益率和信息比率的均值、标准差
```

### ACRecordTemp - 自动检查模板

```python
class ACRecordTemp(RecordTemp):
    def __init__(self, recorder, skip_existing=False):
        self.skip_existing = skip_existing
        super().__init__(recorder=recorder)

    def generate(self, *args, **kwargs):
        # 1. 如果skip_existing=True，检查是否已生成，是则跳过
        # 2. 检查依赖的文件是否存在
        # 3. 调用_generate()
        # 4. 保存结果
        artifact_dict = self._generate(*args, **kwargs)
        if isinstance(artifact_dict, dict):
            self.save(**artifact_dict)
        return artifact_dict
```

---

## 完整代码示例

### 示例1：基础工作流

```python
import qlib
from qlib.constant import REG_CN
from qlib.utils import init_instance_by_config, flatten_dict
from qlib.workflow import R
from qlib.workflow.record_temp import SignalRecord, PortAnaRecord, SigAnaRecord
from qlib.tests.data import GetData
from qlib.tests.config import CSI300_BENCH, CSI300_GBDT_TASK

# 初始化QLib
provider_uri = "~/.qlib/qlib_data/cn_data"
GetData().qlib_data(target_dir=provider_uri, region=REG_CN, exists_skip=True)
qlib.init(provider_uri=provider_uri, region=REG_CN)

# 初始化模型和数据集
model = init_instance_by_config(CSI300_GBDT_TASK["model"])
dataset = init_instance_by_config(CSI300_GBDT_TASK["dataset"])

# 配置回测
port_analysis_config = {
    "executor": {
        "class": "SimulatorExecutor",
        "module_path": "qlib.backtest.executor",
        "kwargs": {
            "time_per_step": "day",
            "generate_portfolio_metrics": True,
        },
    },
    "strategy": {
        "class": "TopkDropoutStrategy",
        "module_path": "qlib.contrib.strategy.signal_strategy",
        "kwargs": {
            "signal": (model, dataset),
            "topk": 50,
            "n_drop": 5,
        },
    },
    "backtest": {
        "start_time": "2017-01-01",
        "end_time": "2020-08-01",
        "account": 100000000,
        "benchmark": CSI300_BENCH,
        "exchange_kwargs": {
            "freq": "day",
            "limit_threshold": 0.095,
            "deal_price": "close",
            "open_cost": 0.0005,
            "close_cost": 0.0015,
            "min_cost": 5,
        },
    },
}

# 启动实验
with R.start(experiment_name="workflow"):
    # 记录参数
    R.log_params(**flatten_dict(CSI300_GBDT_TASK))

    # 训练模型
    model.fit(dataset)

    # 保存模型
    R.save_objects(**{"params.pkl": model})

    # 生成信号记录
    recorder = R.get_recorder()
    sr = SignalRecord(model, dataset, recorder)
    sr.generate()

    # 信号分析
    sar = SigAnaRecord(recorder)
    sar.generate()

    # 回测和投资组合分析
    par = PortAnaRecord(recorder, port_analysis_config, "day")
    par.generate()
```

### 示例2：任务管理

```python
from qlib.workflow.task.manage import TaskManager, run_task
from qlib.workflow.task.gen import RollingGen, task_generator

# 任务模板
task_template = {
    "model": {
        "class": "LGBModel",
        "module_path": "qlib.contrib.model.gbdt",
    },
    "dataset": {
        "class": "DatasetH",
        "module_path": "qlib.data.dataset",
        "kwargs": {
            "handler": {
                "class": "Alpha158",
                "module_path": "qlib.contrib.data.handler",
                "kwargs": {
                    "start_time": "2008-01-01",
                    "end_time": "2020-08-01",
                },
            },
            "segments": {
                "train": ("2008-01-01", "2014-12-31"),
                "valid": ("2015-01-01", "2016-12-31"),
                "test": ("2017-01-01", "2020-08-01"),
            },
        },
    },
}

# 生成滚动任务
tasks = task_generator(
    tasks=task_template,
    generators=RollingGen(step=60, rtype=RollingGen.ROLL_SD)
)

# 创建TaskManager
tm = TaskManager(task_pool="my_tasks")

# 插入任务
task_ids = tm.create_task(tasks)

# 定义任务执行函数
def train_and_evaluate(task_def):
    model = init_instance_by_config(task_def["model"])
    dataset = init_instance_by_config(task_def["dataset"])
    model.fit(dataset)
    pred = model.predict(dataset)
    return {"model": model, "pred": pred}

# 运行任务（单进程）
run_task(
    task_func=train_and_evaluate,
    task_pool="my_tasks"
)

# 或者在多个进程/机器上并行运行
# run_task(task_func=train_and_evaluate, task_pool="my_tasks")
```

### 示例3：在线学习

```python
from qlib.workflow.online.manager import OnlineManager
from qlib.workflow.online.strategy import RollingStrategy
from qlib.workflow.task.gen import RollingGen
from qlib.model.trainer import TrainerR

# 创建滚动策略
strategy = RollingStrategy(
    name_id="rolling_strategy",
    task_template=task_template,
    rolling_gen=RollingGen(step=20)
)

# 创建OnlineManager
online_mgr = OnlineManager(
    strategies=strategy,
    trainer=TrainerR(),
    begin_time="2019-01-01"
)

# 方式1：历史模拟
signals = online_mgr.simulate(
    end_time="2020-08-01",
    frequency="day"
)

# 方式2：真实在线交易
# 首次训练
online_mgr.first_train()

# 每日例行更新
for cur_time in pd.date_range("2019-01-01", "2020-08-01", freq="B"):
    online_mgr.routine(cur_time=cur_time)
    signals = online_mgr.get_signals()
    # 使用signals进行交易
```

### 示例4：结果收集和分析

```python
from qlib.workflow import R
from qlib.workflow.task.collect import RecorderCollector, MergeCollector
from qlib.model.ens.group import RollingGroup
from qlib.model.ens.ensemble import AverageEnsemble

# 方式1：直接使用R
with R.uri_context(uri="file:///path/to/mlruns"):
    # 列出实验
    exps = R.list_experiments()

    # 获取实验
    exp = R.get_exp(experiment_name="my_experiment")

    # 列出recorders
    recorders = exp.list_recorders(status=Recorder.STATUS_FI)

    # 获取特定recorder
    rec = R.get_recorder(recorder_name="best_run", experiment_name="my_experiment")

    # 加载对象
    model = rec.load_object("params.pkl")
    pred = rec.load_object("pred.pkl")

    # 查看指标
    metrics = rec.list_metrics()
    print(f"IC: {metrics.get('IC', 'N/A')}")

# 方式2：使用Collector收集结果
collector = RecorderCollector(
    experiment="my_experiment",
    artifacts_path={
        "pred": "pred.pkl",
        "ic": "sig_analysis/ic.pkl"
    },
    process_list=[
        RollingGroup(),  # 按滚动时段分组
        AverageEnsemble()  # 平均集成
    ]
)

results = collector()
# results = {
#     "pred": 平均后的预测,
#     "ic": 平均后的IC
# }

# 方式3：合并多个Collector
collector1 = RecorderCollector(experiment="exp1", artifacts_path={"pred": "pred.pkl"})
collector2 = RecorderCollector(experiment="exp2", artifacts_path={"pred": "pred.pkl"})

merge_collector = MergeCollector({
    "exp1": collector1,
    "exp2": collector2
})

results = merge_collector()
# results = {
#     ("exp1", "pred"): ...,
#     ("exp2", "pred"): ...
# }
```

### 示例5：搜索和比较实验

```python
from qlib.workflow import R
import pandas as pd

# 搜索记录
with R.uri_context(uri="file:///path/to/mlruns"):
    exp = R.get_exp(experiment_name="my_experiment")

    # 方式1：使用search_records
    records = R.search_records(
        [exp.id],
        filter_string="metrics.IC > 0.05",
        order_by=["metrics.IC DESC"],
        max_results=10
    )

    # 方式2：手动遍历和比较
    recorders = exp.list_recorders()
    data = []
    for rid, rec in recorders.items():
        metrics = rec.list_metrics()
        params = rec.list_params()
        data.append({
            "id": rid,
            "name": rec.name,
            "IC": metrics.get("IC"),
            "ICIR": metrics.get("ICIR"),
            "learning_rate": params.get("model kwargs learning_rate"),
            "start_time": rec.start_time,
        })

    df = pd.DataFrame(data)
    df = df.sort_values("IC", ascending=False)
    print(df.head(10))

    # 获取最佳运行
    best_rec = recorders[df.iloc[0]["id"]]
    best_pred = best_rec.load_object("pred.pkl")
    best_model = best_rec.load_object("params.pkl")
```

---

## 总结

QLib的workflow模块提供了一个完整的实验管理和工作流执行系统，其核心优势包括：

1. **直观的API**：通过`R`全局对象和上下文管理器简化使用
2. **完整的实验追踪**：自动记录参数、指标、模型、代码差异等
3. **灵活的任务管理**：支持分布式任务执行、滚动任务生成
4. **在线学习支持**：提供完整的在线策略管理和模拟框架
5. **模块化设计**：易于扩展和自定义各个组件

该模块是QLib量化研究 pipeline 的核心，为研究人员提供了从数据处理、模型训练、回测分析到实盘部署的完整工作流支持。
