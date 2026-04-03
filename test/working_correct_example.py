#!/usr/bin/env python3
# Qlib完整可运行示例 - 修复版
# 这个示例可以在venv0环境中正确运行

import qlib
from qlib.data import D
from qlib.contrib.data.handler import Alpha158
from qlib.data.dataset import DatasetH
from qlib.contrib.model.gbdt import LGBModel
import pandas as pd
import numpy as np
from pathlib import Path

# 初始化Qlib
qlib.init(provider_uri="~/.qlib/qlib_data/cn_data", region="cn")
print("✓ Qlib初始化成功")

# 读取股票列表（从文件读取）
def read_instruments(market="csi300"):
    inst_file = Path("~/.qlib/qlib_data/cn_data/instruments").expanduser() / f"{market}.txt"
    with open(inst_file) as f:
        lines = f.read().strip().split('\n')
        instruments = [line.split('\t')[0] for line in lines if line.strip()]
    return instruments

# 获取股票列表
instruments = read_instruments("csi300")
print(f"✓ 可选资产数量: {len(instruments)}")
print(f"✓ 前10个股票: {instruments[:10]}")

# 检查交易日历
calendar = D.calendar(start_time="2020-01-01", end_time="2020-09-30")
print(f"✓ 2020年交易日历: {len(calendar)}个交易日")
print(f"✓ 前5个交易日: {calendar[:5]}")

# 创建数据集用于模型训练（使用Alpha158 Handler）
segments = {
    "train": ["2024-01-01", "2024-09-30"],
    "valid": ["2024-10-01", "2024-11-30"],
    "test": ["2024-12-01", "2024-12-31"]
}

dataset = DatasetH(
    handler={
        "class": "qlib.contrib.data.handler.Alpha158",
        "module_path": "qlib.contrib.data.handler"
    },
    segments=segments
)

print("✓ DatasetH创建成功")

# 准备训练数据
train_df = dataset.prepare("train", col_set=["feature", "label"], data_key="learn")
valid_df = dataset.prepare("valid", col_set=["feature", "label"], data_key="infer")
test_df = dataset.prepare("test", col_set=["feature", "label"], data_key="infer")

print(f"✓ 训练数据形状: {train_df.shape}")
print(f"✓ 验证数据形状: {valid_df.shape}")
print(f"✓ 测试数据形状: {test_df.shape}")

# 创建LightGBM模型
model = LGBModel(
    loss="mse",
    learning_rate=0.05,
    num_leaves=50,  # 减少树的数量以加快测试
    verbose=-1
)

print("✓ 模型创建成功")

# 训练模型
print("开始训练...")
model.fit(dataset)
print("✓ 训练完成")

# 预测
predictions = model.predict(dataset, segment="test")
print(f"✓ 预测完成，共{len(predictions)}个预测")

# 计算IC值（信息系数）
from scipy.stats import spearmanr
import warnings
warnings.filterwarnings('ignore')

ic_values = []

# 获取特征列名（从多级索引中提取）
feature_cols = test_df.columns.get_level_values(0).unique()
feature_cols = [col for col in feature_cols if col != 'label']

# 只计算前10个因子的IC
for i, col in enumerate(feature_cols[:10]):
    try:
        # 从多级索引中获取特征列数据
        feature_data = test_df[col].iloc[:, 0] if isinstance(test_df[col], pd.DataFrame) else test_df[col]
        label_data = test_df['label'].iloc[:, 0] if isinstance(test_df['label'], pd.DataFrame) else test_df['label']

        # 计算spearman相关系数，返回的是correlation对象
        result = spearmanr(feature_data.fillna(0), label_data.fillna(0), nan_policy="omit")

        # spearmanr返回的是一个namedtuple，correlation是第一个元素
        ic_value = result.correlation

        if not np.isnan(ic_value):
            ic_values.append((col, ic_value))
    except Exception as e:
        print(f"  计算{col}的IC时出错: {e}")
        continue

if ic_values:
    print(f"\n✓ IC值（已计算的因子）：")
    for name, ic in sorted(ic_values, key=lambda x: abs(x[1]), reverse=True):
        print(f"  {name}: {ic:.4f}")
else:
    print("\n⚠ 未能计算IC值")

print("\n✓ 示例执行完成！")
