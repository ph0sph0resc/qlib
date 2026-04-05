"""
Test script for real QLib training integration
Tests the web API's qlib_wrapper with actual QLib training
"""
import os
import sys
import yaml
import logging

# Add web module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'web'))

from web.api.qlib_wrapper import QLibWrapper
from web.api.task_manager import Task, TaskStatus

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_test_config():
    """
    Create a minimal test configuration for LightGBM training
    """
    config = {
        'qlib_init': {
            'provider_uri': os.path.expanduser('~/.qlib/qlib_data/cn_data'),
            'region': 'cn'
        },
        'experiment_name': 'test_web_training',
        'task': {
            'model': {
                'class': 'LGBModel',
                'module_path': 'qlib.contrib.model.gbdt',
                'kwargs': {
                    'loss': 'mse',
                    'colsample_bytree': 0.8,
                    'learning_rate': 0.05,
                    'subsample': 0.8,
                    'lambda_l1': 0.1,
                    'lambda_l2': 0.1,
                    'max_depth': 5,
                    'num_leaves': 31,
                    'num_boost_round': 50,  # Small number for testing
                    'early_ stop': 10
                }
            },
            'dataset': {
                'class': 'DatasetH',
                'module_path': 'qlib.data.dataset',
                'kwargs': {
                    'handler': {
                        'class': 'Alpha158',
                        'module_path': 'qlib.contrib.data.handler',
                        'kwargs': {
                            'start_time': '2018-01-01',
                            'end_time': '2020-08-01',
                            'fit_start_time': '2018-01-01',
                            'fit_end_time': '2019-12-31',
                            'instruments': 'csi300'
                        }
                    },
                    'segments': {
                        'train': ['2018-01-01', '2019-12-31'],
                        'valid': ['2020-01-01', '2020-06-30'],
                        'test': ['2020-07-01', '2020-08-01']
                    }
                }
            }
        },
        'record': [
            {
                'class': 'SignalRecord',
                'module_path': 'qlib.workflow.record_temp'
            },
            {
                'class': 'SigAnaRecord',
                'module_path': 'qlib.workflow.record_temp',
                'kwargs': {
                    'ana_long_short': False
                }
            }
        ]
    }
    return config


def test_basic_initialization():
    """Test QLibWrapper initialization"""
    print('\n' + '='*60)
    print('TEST 1: Basic Initialization')
    print('='*60)

    try:
        wrapper = QLibWrapper()
        result = wrapper.init()
        if result:
            print('✓ QLib initialized successfully')
            return True
        else:
            print('✗ QLib initialization failed')
            return False
    except Exception as e:
        print(f'✗ Error during initialization: {e}')
        return False


def test_real_training():
    """Test real QLib training"""
    print('\n' + '='*60)
    print('TEST 2: Real QLib Training')
    print('='*60)

    # Create a mock task for progress tracking
    class MockTask:
        def __init__(self):
            self.id = 'test_task_001'
            self.progress = 0
            self.message = ''
            self.logs = []

        def update_progress(self, progress, message=''):
            self.progress = min(100, max(0, progress))
            self.message = message
            if message:
                self.logs.append(message)
                if len(self.logs) <= 5 or self.progress % 20 == 0:
                    print(f'  Progress: {self.progress:.1f}% - {message}')

    try:
        wrapper = QLibWrapper()
        config = create_test_config()

        print('\nConfiguration:')
        print(f'  Model: {config["task"]["model"]["class"]}')
        print(f'  Dataset: {config["task"]["dataset"]["kwargs"]["handler"]["class"]}')
        print(f'  Experiment: {config["experiment_name"]}')
        print(f'  Boost rounds: {config["task"]["model"]["kwargs"]["num_boost_round"]}')

        print('\nStarting training...')
        mock_task = MockTask()
        results = wrapper.train_model(config, task=mock_task)

        print('\n✓ Training completed!')
        print(f'\nResults keys: {list(results.keys())}')

        # Check for expected results
        checks = []

        if 'model' in results:
            print(f'  Model ID: {results["model"]}')
            checks.append(('Model ID', True))
        else:
            checks.append(('Model ID', False))

        if 'model_class' in results:
            print(f'  Model class: {results["model_class"]}')
            checks.append(('Model class', True))
        else:
            checks.append(('Model class', False))

        if 'training_history' in results and results['training_history']:
            history = results['training_history']
            print(f'  Training epochs: {len(history.get("epochs", []))}')
            print(f'  Train loss values: {len(history.get("train_loss", []))}')
            print(f'  Valid loss values: {len(history.get("valid_loss", []))}')
            checks.append(('Training history', True))
        else:
            print('  No training history found')
            checks.append(('Training history', False))

        if 'feature_importance' in results and results['feature_importance']:
            print(f'  Feature importance: {len(results["feature_importance"])} features')
            if results['feature_importance']:
                top_5 = list(results['feature_importance'].items())[:5]
                print(f'  Top 5 features: {[f"{k}: {v:.4f}" for k, v in top_5]}')
            checks.append(('Feature importance', True))
        else:
            print('  No feature importance found')
            checks.append(('Feature importance', False))

        # Print summary
        print('\nSummary:')
        for check_name, passed in checks:
            symbol = '✓' if passed else '✗'
            print(f'  {symbol} {check_name}')

        all_passed = all(passed for _, passed in checks)
        if all_passed:
            print('\n✓ All tests passed!')
        else:
            print('\n✗ Some tests failed')

        return all_passed

    except Exception as e:
        print(f'\n✗ Training failed with error: {e}')
        import traceback
        traceback.print_exc()
        return False


def test_with_example_config():
    """Test with actual example config file"""
    print('\n' + '='*60)
    print('TEST 3: Training with Example Config')
    print('='*60)

    example_path = os.path.join(
        os.path.dirname(__file__),
        '..',
        'examples',
        'benchmarks',
        'LightGBM',
        'workflow_config_lightgbm_Alpha158.yaml'
    )

    if not os.path.exists(example_path):
        print(f'Example config not found: {example_path}')
        return False

    try:
        print(f'\nLoading example config from: {example_path}')
        with open(example_path, 'r') as f:
            config = yaml.safe_load(f)

        # Modify config for faster training
        config['task']['model']['kwargs']['num_boost_round'] = 50
        config['task']['model']['kwargs']['early_ stop'] = 10
        config['experiment_name'] = 'test_web_training_example'

        print('Modified config for faster training:')
        print(f'  Boost rounds: {config["task"]["model"]["kwargs"]["num_boost_round"]}')
        print(f'  Early stopping: {config["task"]["model"]["kwargs"]["early_ stop"]}')

        class MockTask:
            def __init__(self):
                self.id = 'test_task_002'
                self.progress = 0
                self.message = ''

            def update_progress(self, progress, message=''):
                self.progress = min(100, max(0, progress))
                self.message = message
                if message and self.progress % 25 == 0:
                    print(f'  Progress: {self.progress:.1f}% - {message}')

        wrapper = QLibWrapper()
        mock_task = MockTask()

        print('\nStarting training with example config...')
        results = wrapper.train_model(config, task=mock_task)

        print('\n✓ Training with example config completed!')
        print(f'Results: {list(results.keys())}')

        if 'training_history' in results:
            history = results['training_history']
            print(f'  Epochs: {len(history.get("epochs", []))}')
            print(f'  Train score final: {history.get("train_score", [])[-1] if history.get("train_score") else "N/A"}')
            print(f'  Valid score final: {history.get("valid_score", [])[-1] if history.get("valid_score") else "N/A"}')

        return True

    except Exception as e:
        print(f'✗ Test failed: {e}')
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print('='*60)
    print('QLib Real Training Integration Tests')
    print('='*60)

    # Check if QLib data exists
    data_path = os.path.expanduser('~/.qlib/qlib_data/cn_data')
    if not os.path.exists(data_path):
        print(f'\nWARNING: QLib data not found at {data_path}')
        print('Please run: python -m qlib.cli.data qlib_data --target_dir ~/.qlib/qlib_data/cn_data --region cn')
        print('\nTests will likely fail without QLib data.\n')

    results = []

    # Run tests
    results.append(('Initialization', test_basic_initialization()))
    results.append(('Real Training', test_real_training()))
    results.append(('Example Config', test_with_example_config()))

    # Summary
    print('\n' + '='*60)
    print('FINAL SUMMARY')
    print('='*60)

    for test_name, passed in results:
        symbol = '✓' if passed else '✗'
        print(f'{symbol} {test_name}')

    all_passed = all(passed for _, passed in results)
    if all_passed:
        print('\n✓ ALL TESTS PASSED!')
        return 0
    else:
        print('\n✗ SOME TESTS FAILED')
        return 1


if __name__ == '__main__':
    sys.exit(main())
