# -*- coding: utf-8 -*-
"""
测试训练功能修复
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'web'))

print("=" * 60)
print("测试训练功能修复")
print("=" * 60)

# 测试1: 检查配置解析器
print("\n1. 测试配置解析器...")
from api.config_parser import ConfigParser

lgb_params = ConfigParser.get_model_schema('LGBModel')
print(f"  LGBModel 参数数量: {len(lgb_params)}")
print(f"  包含 learning_rate: {'learning_rate' in lgb_params}")
print(f"  包含 max_depth: {'max_depth' in lgb_params}")

double_params = ConfigParser.get_model_schema('DoubleEnsemble')
print(f"  DoubleEnsemble 参数数量: {len(double_params)}")
print(f"  包含 base_model: {'base_model' in double_params}")
print(f"  包含 num_models: {'num_models' in double_params}")

# 测试2: 检查QLibWrapper
print("\n2. 测试QLibWrapper训练函数...")
from api.qlib_wrapper import QLibWrapper

print("  创建QLibWrapper实例")

# 模拟Task类
class MockTask:
    def update_progress(self, progress, message=None):
        if message:
            print(f"    进度: {progress}% - {message}")

# 模拟训练调用（不实际运行）
print("\n3. 模拟训练调用...")
mock_task = MockTask()

result = QLibWrapper.train_model(
    None,
    {'task': {'model': {'class': 'LGBModel'}}},
    task=mock_task
)

print("\n  训练结果:")
print(f"    model_id: {result.get('model_id')}")
print(f"    train_score: {result.get('train_score')}")
print(f"    valid_score: {result.get('valid_score')}")
print(f"    test_score: {result.get('test_score')}")
print(f"    feature_importance: {list(result.get('feature_importance', {}).keys())}")
print(f"    training_history: {'training_history' in result}")

if 'training_history' in result:
    history = result['training_history']
    print(f"    epochs 数量: {len(history.get('epochs', []))}")
    print(f"    train_loss 数量: {len(history.get('train_loss', []))}")
    print(f"    valid_loss 数量: {len(history.get('valid_loss', []))}")

print("\n" + "=" * 60)
print("测试完成！")
print("=" * 60)
