#!/usr/bin/env python3
"""Qlib 完整可运行示例"""

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

# 读取股票列表（直接从文件读取）
def read_instruments(market="csi300"):
    """从文件读取股票列表"""
    inst_file = Path("~/.qlib/qlib_data/cn_data/instruments").expanduser() / f"{market}.txt"
    with open(inst_file) as f:
        lines = f.read().strip().split('\n')
        # 每行格式：股票代码\t开始日期\t结束日期
        instruments = [line.split('\t')[0] for line in lines if line.strip()]
    return instruments

# 获取股票列表
instruments = read_instruments("csi300")
print(f"✓ 可选资产数量: {len(instruments)}")
print(f"✓ 前10个股票: {instruments[:10]}")

# 加载因子（使用Alpha158 Handler）
handler = Alpha158()
handler.config = {
    "dropna": True,
    "drop_multi_day": True,
}

# 分段设置
segments = {
    "train": ["2020-01-01", "2022-12-31"],
    "valid": ["2023-01-01", "2023-06-30"],
    "test": ["2023-07-01", "2023-12-31"]
}

# 创建数据集
dataset = DatasetH(
    handler={
        "class": "qlib.contrib.data.handler.Alpha158",
        "module_path": "qlib.contrib.data.handler"
    },
    segments=segments
)

print("✓ 数据集创建成功")

# 准备训练数据
train_df = dataset.prepare("train", col_set=["feature", "label"], data_key="learn")
valid_df = dataset.prepare("valid", col_set=["feature", "label"], data_key="infer")

print(f"✓ 训练数据形状: {train_df.shape}")
print(f"✓ 验证数据形状: {valid_df.shape}")

# 创建LightGBM模型
model = LGBModel(
    loss="mse",
    learning_rate=0.05,
    num_leaves=100,
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

# 计算IC值
from scipy.stats import spearmanr

test_df = dataset.prepare("test", col_set=["feature", "label"], data_key="infer")
ic_values = []
for col in test_df["feature"].columns:
    if col in test_df.columns:
        ic = spearmanr(test_df[col].fillna(0), test_df["label"].fillna(0), nan_policy="omit")
        if not np.isnan(ic):
            ic_values.append((col, ic))

print(f"✓ IC值（前10个因子）:")
for name, ic in sorted(ic_values, key=lambda x: abs(x[1]), reverse=True)[:10]:
    print(f"  {name}: {ic:.4f}")
