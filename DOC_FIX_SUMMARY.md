# Qlib 文档修复总结

## 修复时间
2026-03-31

## 修复内容

### 1. 已修复的代码问题

| 问题 | 修复方法 | 影响 |
|------|----------|------|
| `GDBTModel` 类名错误 | 替换为 `LGBModel` | 11处 |
| `from qlib.contrib.model.gbdt import GBDTModel` | 替换为 `from qlib.contrib.model.gbdt import LGBModel` | 模块导入 |
| YAML配置中的模型类名 | `qlib.contrib.model.gbdt.GBDTModel` → `qlib.contrib.model.gbdt.LGBModel` | 回测配置 |

### 2. 新增的内容

在第一个代码示例后添加了详细的API使用说明，包括：
- 获取股票列表的正确方法（从文件读取）
. 使用 `D.calendar()` 获取交易日历
- 使用 `D.features(instruments={...})` 的正确格式
- 使用 `DatasetH` 和 `dataset.prepare()` 获取各段数据
- 使用 `LGBModel` 进行模型训练

### 3. 验证结果

**运行测试脚本**：`working_correct_example.py` 可成功运行

**测试输出**：
```
✓ Qlib初始化成功
✓ 可选资产数量: 15898
✓ 前10个股票: ['SZ000001', 'SZ000002', ...]
✓ 2020年交易日历: 183个交易日
✓ DatasetH创建成功
✓ 训练数据形状: (91280, 159)
✓ 验证数据形状: (18500, 159)
✓ 测试数据形状: (11500, 159)
✓ 模型创建成功
开始训练...
Training until validation scores don't improve for 50 rounds
[20]	train's l2: 0.969821	valid's l2: 0.997767
[40]	train's l2: 0.942856	valid's l2: 0.999756
Early stopping, best iteration is:
[20]	train's l2: 0.969821	valid's l2: 0.997767
✓ 训练完成
✓ 预测完成，共11500个预测
✓ 示例执行完成！
```

### 4. 关键API纠正

| 错误用法 | 正确用法 | 说明 |
|----------|----------|------|
| `instruments = D.instruments("csi300")` | 从文件读取或使用 `instruments={"market": "csi300"}` | `D.instruments()` 在当前版本中API不同 |
| `dataset.split(("2020-01-01", "2022-12-31"))` | `dataset.prepare("train", col_set=["feature", "label"], data_key="learn")` | `DatasetH` 不支持 `split()` 方法 |
| `model.fit(dataset=train_df, segment="train")` | `model.fit(dataset)` | 传入整个 `dataset` 对象 |
| `model.predict(dataset=test_df, segment="test")` | `model.predict(dataset, segment="test")` | 传入整个 `dataset` 对象 |

## 测试方式

在 `/home/firewind0/qlib/venv0` 虚拟环境中运行以下命令：

```bash
# 激活虚拟环境
source /home/firewind0/qlib/venv0/bin/activate

# 运行修复后的示例
python3 working_correct_example.py
```

## 相关文件

- `/home/firewind0/qlib/docs/QLib_Complete_Learning_Guide.md` - 已修复的学习指南
- `/home/firewind0/qlib/working_correct_example.py` - 可运行的完整示例
- `/home/firewind0/qlib/doc_complete_fix.py` - 文档修复脚本

## 总结

✓ **所有代码示例已修复**
✓ **关键API已验证正确**
✓ **创建了可运行的完整示例**
✓ **添加了详细的API使用说明**
