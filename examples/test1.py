import qlib
from qlib.data import D
from qlib.contrib.model.gbdt import LGBModel
from qlib.contrib.evaluate import risk_analysis
from pathlib import Path
# 初始化
qlib.init(provider_uri="~/.qlib/qlib_data/cn_data", region="cn")

# 获取数据
# 读取股票列表（从文件读取）
def read_instruments(market="csi300"):
    inst_file = Path("~/.qlib/qlib_data/cn_data/instruments").expanduser() / f"{market}.txt"
    with open(inst_file) as f:
        lines = f.read().strip().split("\n")
        instruments = [line.split("\t")[0] for line in lines if line.strip()]
    return instruments

instruments = read_instruments("csi300")  # 沪深300只
print(f"可选资产数量: {len(instruments)}")

# 加载因子（这里使用基础特征）
fields = ["Ref($close, 1)", "Ref($close, 2)", "Ref($close, 3)",
          "Ref($close, 4)", "Ref($close, 5)"]

# 创建数据集
start_time = "2020-01-01"
end_time = "2023-12-31"
dataset = D.features(
    instruments={"market": "csi300", "filter_pipe": []},
    fields=fields,
    start_time=start_time,
    end_time=end_time,
    freq="day"
)

# 分割数据
train_df = dataset.prepare("2020-01-01", col_set=["feature", "label"], data_key="infer")
test_df = dataset.prepare("2023-01-01", col_set=["feature", "label"], data_key="infer")

print(f"训练数据形状: {train_df.shape}")
print(f"测试数据形状: {test_df.shape}")

# 准备标签（假设使用未来收益率作为标签）
label_field = "Ref($close, 1)"  # 下日收盘价
  # 计算收益率

# 训练模型
model = LGBModel(
    loss="mse",         # 均方误差损失
    eval_metric="mean", # 使用平均绝对误差作为评估指标
    col_sample_weight="label"  # 按标签列加权样本
)

# 训练
model.fit(dataset,
    segment="train"  # 训练段
)

# 预测
predictions = model.predict(dataset, segment="test")

# 计算IC（信息系数）
import pandas as pd
from scipy.stats import spearmanr

for col in fields:
    ic = spearmanr.corr(predictions[col], test_df[col])
    print(f"{col} IC: {ic:.4f}")