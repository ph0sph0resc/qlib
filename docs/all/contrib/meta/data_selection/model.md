# model.py

## 模块概述

该模块实现了基于元学习的数据选择模型，包括：

- **TimeReweighter**: 时间重加权器，根据时间性能调整样本权重
- **MetaModelDS**: 元学习模型，学习数据选择策略

## 类定义

### TimeReweighter

时间重加权器，根据元学习模型输出的时间权重重新加权样本。

#### 构造方法参数

| 参数名 | 类型 | 必需 | 说明 |
|--------|------|------|------|
| time_weight | pd.Series | 是 | 时间权重序列 |

**time_weight 数据结构：**

索引为时间区间元组，值为该时间区间的权重。

```python
# 示例
{
    ("2009-01-05", "2009-02-06"): 1.2,
    ("2009-02-09", "2009-03-06"): 0.8,
    ...
}
```

#### 方法

##### reweight(data)

根据时间权重重新加权数据。

**参数说明：**

- **data**: `pd.DataFrame` 或 `pd.Series`，需要加权的数据

**返回值：**

- **pd.Series**: 权重序列，索引与输入数据相同

**逻辑说明：**

1. 初始化权重为 1.0
2. 根据时间区间应用对应权重
3. 返回加权后的权重序列

---

### MetaModelDS

元学习模型，通过学习历史数据性能来优化数据选择策略。

#### 构造方法参数

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|----------|------|
| step | int | - | 滚动窗口步长 |
| hist_step_n | int | - | 历史步数 |
| clip_method | str | "tanh" | 权重截断方法 |
| clip_weight | float | 2.0 | 权重截断阈值 |
| criterion | str | "ic_loss" | 损失函数类型 |
| lr | float | 0.0001 | 学习率 |
| max_epoch | int | 100 | 最大训练轮数 |
| seed | int | 43 | 随机种子 |
| alpha | float | 0.0 | L2正则化系数 |
| loss_skip_thresh | int | 50 | 损失计算跳过阈值 |

**criterion 选项：**

- `"mse"`: 均方误差损失
- `"ic_loss"`: 信息系数损失

**clip_method 选项：**

- `"tanh"`: 使用 tanh 函数截断
- `"clamp"`: 使用硬截断

#### 方法

##### fit(meta_dataset)

训练元学习模型。

**参数说明：**

- **meta_dataset** (`MetaDatasetDS`): 元学习数据集

**训练流程：**

1. 初始化预测网络（`PredNet`）
2. 准备训练和测试任务
3. 运行无权重基线测试
4. 初始化权重测试
5. 执行多轮训练：
   - 前向传播计算预测和权重
   - 计算损失（MSE 或 IC Loss）
   - 反向传播更新参数
   - 记录指标
6. 保存最佳模型

**日志指标：**

- `loss/train`: 训练损失
- `loss/test`: 测试损失
- `ic/train`: 训练 IC
- `ic/test`: 测试 IC

##### run_epoch(phase, task_list, epoch, opt, loss_l, ignore_weight=False)

运行一个训练/测试轮次。

**参数说明：**

- **phase**: "train" 或 "test"
- **task_list**: 任务列表
- **epoch**: 当前轮数
- **opt**: 优化器
- **loss_l**: 损失记录字典
- **ignore_weight**: 是否忽略权重

**功能说明：**

1. 设置训练/测试模式
2. 遍历所有任务
3. 前向传播计算预测和权重
   - 使用时间权重加权特征
   - 计算算术回归系数
   - 生成预测
4. 计算损失
5. 训练模式下反向传播
6. 计算并记录 IC 指标

##### inference(meta_dataset)

使用训练好的模型进行推理，生成重新加权的任务配置。

**参数说明：**

- **meta_dataset** (`MetaTaskDataset`): 元学习数据集

**返回值：**

- **List[dict]**: 重新加权的任务配置列表

**每个任务的修改：**

```python
{
    "reweighter": TimeReweighter(time_weight_series),
    ... # 原有配置
}
```

##### _prepare_task(task)

为单个任务准备重新加权的配置。

**参数说明：**

- **task** (`MetaTask`): 元学习任务

**返回值：**

- **dict**: 添加了重加权器的任务配置

**处理流程：**

1. 获取任务的元输入
2. 使用时间权重模块计算权重
3. 创建 `TimeReweighter` 实例
4. 将重加权器添加到任务配置中

## 使用示例

### 基本训练

```python
from qlib.contrib.meta.data_selection.dataset import MetaDatasetDS
from qlib.contrib.meta.data_selection.model import MetaModelDS

# 创建数据集
meta_dataset = MetaDatasetDS(
    task_tpl=task_tpl,
    step=20,
    exp_name="proxy_exp",
    segments=0.8,
    hist_step_n=10
)

# 创建模型
meta_model = MetaModelDS(
    step=20,
    hist_step_n=10,
    clip_method="tanh",
    clip_weight=2.0,
    criterion="ic_loss",
    lr=0.0001,
    max_epoch=100
)

# 训练模型
meta_model.fit(meta_dataset)
```

### 使用训练好的模型

```python
# 进行推理，获取重新加权的任务
reweighted_tasks = meta_model.inference(meta_dataset)

# 使用重新加权的任务进行训练
for task in reweighted_tasks:
    trainer.train([task])
```

### 查看学习的时间权重

```python
# 获取时间权重
time_weights = meta_model.tn.twm(
    time_perf_tensor,
    time_belong_tensor
)

# 转换为 Series
weight_series = pd.Series(
    time_weights.detach().cpu().numpy(),
    index=time_periods
)

print("学习到的数据段权重:")
print(weight_series)
```

## 训练流程监控

### 训练日志示例

```python
# 训练过程中的日志输出
Epoch 1/100:
  train_loss: 0.0453
  test_loss: 0.0482
  train_ic: 0.0532
  test_ic: 0.0481

Epoch 2/100:
  train_loss: 0.0412
  test_loss: 0.0445
  train_ic: 0.0567
  test_ic: 0.0521
...
```

### 使用 R 对象记录指标

```python
from qlib.workflow import R

# 在 run_epoch 中自动记录
R.log_metrics(loss=0.0453, step=0)
R.log_metrics(ic=0.0532, step=0)

# 记录参数
R.log_params(lr=0.0001, step=20,
             hist_step_n=10,
             clip_method="tanh")
```

## 算法原理

### 元学习框架

```mermaid
graph LR
    A[历史数据] --> B[代理模型]
    B --> C[性能矩阵 IC]
    C --> {Meta学习}
    D[当前任务] --> E[提取相关历史]
    E --> F[权重网络]
    F --> G[数据权重]
    G --> H[加权的子模型]
    H --> I[更好的预测]
```

### 时间权重学习

1. **输入**: 历史数据段的性能矩阵
2. **网络**: 线性层 + 截断函数
3. **输出**: 每个数据段的权重
4. **训练**: 通过优化 IC 或 MSE 学习权重

### 加权回归

```python
# 特征加权
X_w = X.T * weights

# 计算回归系数
theta = (X_w @ X + alpha * I)^(-1) @ X_w @ y

# 生成预测
pred = X_test @ theta
```

## 注意事项

1. **训练稳定性**:
   - IC Loss 在样本量少时可能不稳定
   - 使用 `loss_skip_thresh` 跳过样本量少的日期

2. **权重截断**:
   - 防止极端权重导致训练不稳定
   - `tanh` 方法提供平滑截断

3. **正则化**:
   - `alpha` 参数用于 L2 正则化
   - 特别适用于线性子模型

4. **内存管理**:
   - 训练过程会占用较多内存
   - 使用小批量训练可降低内存消耗

5. **计算成本**:
   - 每个任务需要前向传播
   - IC Loss 计算成本较高

## 相关文档

- [dataset.py 文档](./dataset.md) - 元学习数据集
- [net.py 文档](./net.md) - 神经网络结构
- [utils.py 文档](./utils.md) - 损失函数
