#!/usr/bin/env python3
"""
全面的Qlib文档修复
将所有错误的API替换为正确的API
"""

import re
from pathlib import Path

# 读取文档
doc_path = Path("/home/firewind0/qlib/docs/QLib_Complete_Learning_Guide.md")

with open(doc_path, 'r', encoding='utf-8') as f:
    content = f.read()

print(f"读取文档: {doc_path}")
print(f"文档总长度: {len(content)}")

fixes = 0

# ============ 批量替换规则 ============

# 规则1: GBDTModel -> LGBModel（所有出现）
old1 = 'GBDTModel'
new1 = 'LGBModel'
if old1 in content:
    content = content.replace(old1, new1)
    count1 = content.count(new1)
    print(f"✓ 修复1: {old1} -> {new1} ({count1}处)")
    fixes += count1

# 规则2: GBDTModel -> LGBModel（在import语句中）
old2 = 'from qlib.contrib.model.gbdt import GBDTModel'
new2 = 'from qlib.contrib.model.gbdt import LGBModel'
if old2 in content:
    content = content.replace(old2, new2)
    print(f"✓ 修复2: {old2} -> {new2}")
    fixes += 1

# 规则3: 在from语句中的GBDTModel
old3 = 'from qlib.contrib.model.gbdt import'
new3 = 'from qlib.contrib.model.gbdt import LGBModel'
if old3 in content:
    content = re.sub(r'from qlib\.contrib\.model\.gbdt import \*', new3, content)
    print(f"✓ 修复3: 更新gbdt模块的import")
    fixes += 1

# 规则4: 修复回测部分的模型类名
old4 = '"class": "qlib.contrib.model.gbdt.GBDTModel"'
new4 = '"class": "qlib.contrib.model.gbdt.LGBModel"'
if old4 in content:
    content = content.replace(old4, new4)
    print(f"✓ 修复4: {old4} -> {new4}")
    fixes += 1

# ============ 插入注意说明 ============

# 在第一个代码示例后插入详细的API说明
first_code_marker = """```python
import qlib
from qlib.data import D
from qlib.contrib.model.gbdt import GBDTModel"""

if first_code_marker in content:
    # 找到代码块结束位置
    end_marker = '```'
    pos = content.find(first_code_marker)
    if pos > 0:
        end_pos = content.find(end_marker, pos + 100)
        if end_pos > 0:
            note = """

> **重要提示：本示例中的API调用在当前Qlib版本中可能需要调整**
>
> **正确的API使用方式请参考以下示例**：
>
> 1. **获取股票列表**：从文件直接读取
>    ```python
>    from pathlib import Path
>    def read_instruments(market="csi300"):
>        inst_file = Path("~/.qlib/qlib_data/cn_data/instruments").expanduser() / f"{market}.txt"
>        with open(inst_file) as f:
>            lines = f.read().strip().split("\\n")
>            instruments = [line.split("\\t")[0] for line in lines if line.strip()]
>        return instruments
>    instruments = read_instruments("csi300")
>    ```
>
> 2. **获取特征数据**：使用 `instruments` 字典参数
>    ```python
>    dataset = D.features(
>        instruments={"market": "csi300", "filter_pipe": []},
>        fields=fields,
>        start_time=start_time,
>        end_time=end_time,
>        freq="day"
>    )
>    ```
>
> 3. **创建数据集**：使用 `DatasetH` 和 `dataset.prepare()`
>    ```python
>    from qlib.contrib.data.handler import Alpha158
>    from qlib.data.dataset import DatasetH
>
>    dataset = DatasetH(
>        handler={
>            "class": "qlib.contrib.data.handler.Alpha158",
>            "module_path": "qlib.contrib.data.handler"
>        },
>        segments={
>            "train": ["2020-01-01", "2022-12-31"],
>            "valid": ["2023-01-01", "2023-06-30"],
>            "test": ["2023-07-01", "2023-12-31"]
>        }
>    )
>
>    # 准备数据
>    train_df = dataset.prepare("train", col_set=["feature", "label"], data_key="learn")
>    valid_df = dataset.prepare("valid", col_set=["feature", "label"], data_key="infer")
>    ```
>
> 4. **模型训练**：使用 `LGBModel` 而不是 `GBDTModel`
>    ```python
>    from qlib.contrib.model.gbdt import LGBModel
>
>    model = LGBModel(
>        loss="mse",
>        learning_rate=0.05,
>        num_leaves=100,
>        verbose=-1
>    )
>
>    # 训练
>    model.fit(dataset)
>    ```
>
> **完整可运行示例**：请查看 `working_correct_example.py` 文件。

"""
            content = content[:end_pos] + note + content[end_pos:]
            print("✓ 在第一个示例后插入了API说明")
            fixes += 1

# 保存修复后的文档
if fixes > 0:
    with open(doc_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"\n✓ 共修复 {fixes} 处问题")
    print("✓ 文档已保存")
else:
    print("\n没有发现需要修复的问题")

# 最终验证
print("\n最终验证:")
print(f"  LGBModel数量: {content.count('LGBModel')}")
print(f"  GBDTModel数量: {content.count('GBDTModel')}")
print(f"  read_instruments数量: {content.count('read_instruments')}")

# 检查问题
problems = []
if 'D.instruments(' in content:
    problems.append('D.instruments(')
if 'dataset.split(' in content:
    problems.append('dataset.split(')
if 'model.fit(dataset=train_df' in content:
    problems.append('model.fit(dataset=train_df')

if problems:
    print("\n⚠ 仍存在的问题:")
    for p in problems:
        print(f"  - {p}")
else:
    print("\n✓ 主要问题已修复")
