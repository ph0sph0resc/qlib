"""
Web应用基础功能测试
"""
import sys
import os

# 添加web目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'web'))


def test_config_module():
    """测试配置模块"""
    print("测试配置模块...")
    from config import MODEL_CATEGORIES, ALPHA_FACTORS, STRATEGY_TYPES

    assert 'ML' in MODEL_CATEGORIES
    assert 'DL' in MODEL_CATEGORIES
    assert 'LGBModel' in MODEL_CATEGORIES['ML']
    assert 'Alpha158' in ALPHA_FACTORS
    assert 'TopkDropoutStrategy' in STRATEGY_TYPES
    print("✓ 配置模块测试通过")


def test_config_parser():
    """测试配置解析器"""
    print("\n测试配置解析器...")
    from api.config_parser import ConfigParser

    # 测试获取模型schema
    schema = ConfigParser.get_model_schema('LGBModel')
    assert 'learning_rate' in schema
    assert 'max_depth' in schema
    print("✓ 模型schema获取测试通过")

    # 测试获取所有模型
    models = ConfigParser.get_all_models()
    assert 'ML' in models
    assert 'DL' in models
    print("✓ 获取所有模型测试通过")


def test_task_manager():
    """测试任务管理器"""
    print("\n测试任务管理器...")
    from api.task_manager import TaskManager, TaskStatus

    manager = TaskManager()

    # 创建模拟任务
    def mock_task(task=None):
        return {'result': 'success'}

    task_id = manager.create_task('test_task', mock_task)
    assert task_id is not None
    print("✓ 任务创建测试通过")

    # 启动任务
    result = manager.start_task(task_id)
    assert result is True
    print("✓ 任务启动测试通过")

    # 获取任务状态
    task = manager.get_task(task_id)
    assert task is not None
    print("✓ 获取任务状态测试通过")


def test_database_models():
    """测试数据库模型"""
    print("\n测试数据库模型...")
    from api.models import Experiment, TaskLog, ModelRecord, BacktestRecord

    # 验证模型可以正常创建
    exp = Experiment(
        id='test_exp_1',
        name='Test Experiment',
        task_type='test',
        status='pending'
    )
    assert exp.id == 'test_exp_1'
    print("✓ 数据库模型测试通过")


def test_qlib_wrapper():
    """测试QLib封装"""
    print("\n测试QLib封装...")
    from api.qlib_wrapper import QLibWrapper

    wrapper = QLibWrapper()
    # 注意：不实际初始化QLib，只测试导入和基本功能
    assert wrapper.region == 'cn'
    print("✓ QLib封装测试通过")


def main():
    """运行所有测试"""
    print("=" * 50)
    print("QLib Web基础功能测试")
    print("=" * 50)

    try:
        test_config_module()
        test_config_parser()
        test_task_manager()
        test_database_models()
        test_qlib_wrapper()

        print("\n" + "=" * 50)
        print("✓ 所有测试通过!")
        print("=" * 50)
        return 0

    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
