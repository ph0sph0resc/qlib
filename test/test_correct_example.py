#!/usr/bin/env python3
"""测试正确的Qlib API示例"""

import qlib
from qlib.data import D
import pandas as pd
import numpy as np

# 初始化
qlib.init(provider_uri="~/.qlib/qlib_data/cn_data", region="cn")

# 获取股票池
instruments = D.instruments("csi300")
print(f"可选资产数量: {len(instruments)}")

# 加载因子（使用基础特征）
fields = ["Ref($close, 1)", "Ref($close, 2)", "Ref($close, 3)",
          "Ref($close, 4)", "Ref($close, 5)"]

# 创建数据集
start_time = "2020-01-01"
end_time = "2020-12-31"

# 取部分股票进行测试
test_instruments = instruments[:10]

dataset = D.features(
    instruments=test_instruments,
    fields=fields,
    start_time=start_time,
    end_time=end_time,
    freq="day"
)

print(f"数据集形状: {dataset.shape}")
print(f"数据集列: {dataset.columns.tolist()}")
print(f"数据集前5行:")
print(dataset.head())
