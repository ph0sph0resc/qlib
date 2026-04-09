"""
Configuration Parser for QLib YAML configs
Handles parsing, validation, and form schema generation
"""
import yaml
import hashlib
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class ConfigParser:
    """Parser for QLib YAML configurations"""

    # backtest strategy module paths
    BACKTEST_MODULE_PATHS ={
        'TopkDropoutStrategy':'qlib.contrib.strategy',
        'SoftTopkStrategy':'qlib.contrib.strategy.cost_control',
        'EnhancedIndexingStrategy':'qlib.contrib.strategy',
    }

    # Strategy types
    STRATEGY_TYPES = ['TopkDropoutStrategy', 'SoftTopkStrategy', 'EnhancedIndexingStrategy']

    # Strategy parameter schemas
    STRATEGY_SCHEMAS = {
        'TopkDropoutStrategy': {
            'topk': {'type': 'int', 'default': 50, 'min': 1, 'label': '持仓股票数量'},
            'n_drop': {'type': 'int', 'default': 5, 'min': 1, 'label': '每次更换数量'},
            'method_sell': {'type': 'select', 'default': 'bottom', 'options': ['bottom', 'random'], 'label': '卖出策略'},
            'method_buy': {'type': 'select', 'default': 'top', 'options': ['top', 'random'], 'label': '买入策略'},
            'hold_thresh': {'type': 'int', 'default': 1, 'min': 1, 'label': '最小持有天数'},
        },
        'SoftTopkStrategy': {
            'topk': {'type': 'int', 'default': 50, 'min': 1, 'label': '持仓股票数量'},
            'risk_degree': {'type': 'float', 'default': 0.95, 'min': 0.0, 'max': 1.0, 'label': '风险度'},
            'trade_impact_limit': {'type': 'float', 'default': None, 'min': 0.0, 'max': 1.0, 'label': '交易影响限制'},
            'max_sold_weight': {'type': 'float', 'default': 1.0, 'min': 0.0, 'max': 1.0, 'label': '最大卖出权重'},
            'buy_method': {'type': 'select', 'default': 'first_fill', 'options': ['first_fill', 'random', 'top'], 'label': '买入方式'},
        },
        'EnhancedIndexingStrategy': {
            'riskmodel_root': {'type': 'text', 'required': True, 'label': '风险模型路径'},
            'market': {'type': 'select', 'default': 'csi500', 'options': ['csi300', 'csi500', 'all'], 'label': '市场'},
            'turn_limit': {'type': 'float', 'default': None, 'min': 0.0, 'max': 1.0, 'label': '换手率限制'},
        }
    }

    # Model module paths
    MODEL_MODULE_PATHS = {
        'LGBModel': 'qlib.contrib.model.gbdt',
        'XGBModel': 'qlib.contrib.model.xgboost',
        'CatBoostModel': 'qlib.contrib.model.catboost_model',
        'LinearModel': 'qlib.contrib.model.linear',
        'LSTM': 'qlib.contrib.model.pytorch_lstm_ts',
        'GRU': 'qlib.contrib.model.pytorch_gru_ts',
        'Transformer': 'qlib.contrib.model.pytorch_transformer_ts',
        'ALSTM': 'qlib.contrib.model.pytorch_alstm_ts',
        'TCN': 'qlib.contrib.model.pytorch_tcn_ts',
        'TFT': 'qlib.contrib.model.pytorch_tfts',
        'GATs': 'qlib.contrib.model.pytorch_gats_ts',
        'Localformer': 'qlib.contrib.model.pytorch_localformer_ts',
        'DEnsembleModel': 'qlib.contrib.model.double_ensemble',
        'TRA': 'qlib.contrib.model.pytorch_tra',
        'TabNet': 'qlib.contrib.model.pytorch_tabnet',
        'IGMTF': 'qlib.contrib.model.pytorch_igmtf',
        'KRNN': 'qlib.contrib.model.pytorch_krnn',
        'ADARNN': 'qlib.contrib.model.pytorch_adarnn',
        'HIST': 'qlib.contrib.model.pytorch_hist',
        'HFLGBModel': 'qlib.contrib.model.highfreq_gdbt_model',
    }

    # Model parameter schemas
    MODEL_SCHEMAS = {
        'LGBModel': {
            'loss': {'type': 'select', 'default': 'mse', 'options': ['mse', 'mae', 'huber']},
            'learning_rate': {'type': 'float', 'default': 0.2, 'min': 0.001, 'max': 1.0},
            'max_depth': {'type': 'int', 'default': 8, 'min': 1, 'max': 20},
            'num_leaves': {'type': 'int', 'default': 210, 'min': 10, 'max': 1000},
            'subsample': {'type': 'float', 'default': 0.8789, 'min': 0.1, 'max': 1.0},
            'colsample_bytree': {'type': 'float', 'default': 0.8879, 'min': 0.1, 'max': 1.0},
            'lambda_l1': {'type': 'float', 'default': 205.7, 'min': 0.0, 'max': 1000.0},
            'lambda_l2': {'type': 'float', 'default': 580.98, 'min': 0.0, 'max': 1000.0},
        },
        'XGBModel': {
            'objective': {'type': 'select', 'default': 'reg:squarederror',
                         'options': ['reg:squarederror', 'reg:squaredlogerror']},
            'learning_rate': {'type': 'float', 'default': 0.2, 'min': 0.001, 'max': 1.0},
            'max_depth': {'type': 'int', 'default': 8, 'min': 1, 'max': 20},
            'subsample': {'type': 'float', 'default': 0.8, 'min': 0.1, 'max': 1.0},
        },
        'CatBoostModel': {
            'learning_rate': {'type': 'float', 'default': 0.2, 'min': 0.001, 'max': 1.0},
            'depth': {'type': 'int', 'default': 8, 'min': 1, 'max': 20},
        },
        'LinearModel': {
            'fit_intercept': {'type': 'bool', 'default': True},
        },
        'LSTM': {
            'hidden_size': {'type': 'int', 'default': 64, 'min': 8, 'max': 512},
            'num_layers': {'type': 'int', 'default': 2, 'min': 1, 'max': 5},
            'dropout': {'type': 'float', 'default': 0.0, 'min': 0.0, 'max': 0.9},
        },
        'GRU': {
            'hidden_size': {'type': 'int', 'default': 64, 'min': 8, 'max': 512},
            'num_layers': {'type': 'int', 'default': 2, 'min': 1, 'max': 5},
            'dropout': {'type': 'float', 'default': 0.0, 'min': 0.0, 'max': 0.9},
        },
        'Transformer': {
            'd_model': {'type': 'int', 'default': 64, 'min': 8, 'max': 512},
            'nhead': {'type': 'int', 'default': 4, 'min': 1, 'max': 16},
            'num_layers': {'type': 'int', 'default': 2, 'min': 1, 'max': 8},
        },
        'ALSTM': {
            'hidden_size': {'type': 'int', 'default': 64, 'min': 8, 'max': 512},
            'attention_dim': {'type': 'int', 'default': 64, 'min': 8, 'max': 512},
        },
        'TCN': {
            'num_channels': {'type': 'list', 'default': [64, 64, 64]},
            'kernel_size': {'type': 'int', 'default': 3, 'min': 1, 'max': 10},
        },
        'TFT': {
            'hidden_size': {'type': 'int', 'default': 64, 'min': 8, 'max': 512},
            'num_heads': {'type': 'int', 'default': 4, 'min': 1, 'max': 16},
        },
        'GATs': {
            'hidden_size': {'type': 'int', 'default': 64, 'min': 8, 'max': 512},
            'num_layers': {'type': 'int', 'default': 2, 'min': 1, 'max': 5},
            'heads': {'type': 'int', 'default': 4, 'min': 1, 'max': 16},
        },
        'Localformer': {
            'hidden_size': {'type': 'int', 'default': 64, 'min': 8, 'max': 512},
            'window_size': {'type': 'int', 'default': 5, 'min': 1, 'max': 20},
        },
        'DEnsembleModel': {
            'base_model': {'type': 'select', 'default': 'gbm', 'options': ['gbm', 'lgb']},
            'loss': {'type': 'select', 'default': 'mse', 'options': ['mse', 'mae', 'huber']},
            'num_models': {'type': 'int', 'default': 6, 'min': 1, 'max': 20},
            'enable_sr': {'type': 'bool', 'default': True},
            'enable_fs': {'type': 'bool', 'default': True},
            'alpha1': {'type': 'float', 'default': 1.0, 'min': 0.1, 'max': 10.0},
            'alpha2': {'type': 'float', 'default': 1.0, 'min': 0.1, 'max': 10.0},
            'bins_sr': {'type': 'int', 'default': 10, 'min': 5, 'max': 50},
            'bins_fs': {'type': 'int', 'default': 5, 'min': 2, 'max': 20},
            'decay': {'type': 'float', 'default': 0.5, 'min': 0.1, 'max': 1.0},
            'sample_ratios': {'type': 'list', 'default': [0.8, 0.7, 0.6, 0.5, 0.4]},
            'sub_weights': {'type': 'list', 'default': [1.0, 0.2, 0.2, 0.2, 0.2, 0.2]},
            'epochs': {'type': 'int', 'default': 28, 'min': 1, 'max': 100},
            'learning_rate': {'type': 'float', 'default': 0.2, 'min': 0.001, 'max': 1.0},
            'max_depth': {'type': 'int', 'default': 8, 'min': 1, 'max': 20},
            'num_leaves': {'type': 'int', 'default': 210, 'min': 10, 'max': 1000},
            'num_threads': {'type': 'int', 'default': 20, 'min': 1, 'max': 50},
        },
        'TRA': {
            'sequence_length': {'type': 'int', 'default': 20, 'min': 5, 'max': 100},
            'hidden_size': {'type': 'int', 'default': 64, 'min': 8, 'max': 512},
        },
        'TabNet': {
            'n_d': {'type': 'int', 'default': 8, 'min': 1, 'max': 64},
            'n_a': {'type': 'int', 'default': 8, 'min': 1, 'max': 64},
            'n_steps': {'type': 'int', 'default': 3, 'min': 1, 'max': 10},
        },
        'IGMTF': {
            'd_feat': {'type': 'int', 'default': 6, 'min': 1, 'max': 20},
            'hidden_size': {'type': 'int', 'default': 64, 'min': 8, 'max': 512},
            'num_layers': {'type': 'int', 'default': 2, 'min': 1, 'max': 5},
            'dropout': {'type': 'float', 'default': 0.0, 'min': 0.0, 'max': 0.9},
            'n_epochs': {'type': 'int', 'default': 200, 'min': 10, 'max': 1000},
            'lr': {'type': 'float', 'default': 1e-4, 'min': 1e-6, 'max': 1e-2},
            'early_stop': {'type': 'int', 'default': 20, 'min': 5, 'max': 100},
            'metric': {'type': 'select', 'default': 'ic', 'options': ['ic', 'rank_ic', 'pearson']},
            'loss': {'type': 'select', 'default': 'mse', 'options': ['mse', 'mae']},
            'base_model': {'type': 'select', 'default': 'LSTM', 'options': ['LSTM', 'GRU', 'Transformer']},
            'GPU': {'type': 'int', 'default': 0, 'min': 0, 'max': 1},
        },
        'HIST': {
            'd_feat': {'type': 'int', 'default': 6, 'min': 1, 'max': 20},
            'hidden_size': {'type': 'int', 'default': 64, 'min': 8, 'max': 512},
            'num_layers': {'type': 'int', 'default': 2, 'min': 1, 'max': 5},
            'dropout': {'type': 'float', 'default': 0.0, 'min': 0.0, 'max': 0.9},
            'n_epochs': {'type': 'int', 'default': 200, 'min': 10, 'max': 1000},
            'lr': {'type': 'float', 'default': 1e-4, 'min': 1e-6, 'max': 1e-2},
            'early_stop': {'type': 'int', 'default': 20, 'min': 5, 'max': 100},
            'metric': {'type': 'select', 'default': 'ic', 'options': ['ic', 'rank_ic', 'pearson']},
            'loss': {'type': 'select', 'default': 'mse', 'options': ['mse', 'mae']},
            'base_model': {'type': 'select', 'default': 'LSTM', 'options': ['LSTM', 'GRU', 'Transformer']},
            'GPU': {'type': 'int', 'default': 0, 'min': 0, 'max': 1},
        },
        'KRNN': {
            'd_feat': {'type': 'int', 'default': 6, 'min': 1, 'max': 20},
            'hidden_size': {'type': 'int', 'default': 64, 'min': 8, 'max': 512},
            'num_layers': {'type': 'int', 'default': 2, 'min': 1, 'max': 5},
            'dropout': {'type': 'float', 'default': 0.0, 'min': 0.0, 'max': 0.9},
            'n_epochs': {'type': 'int', 'default': 200, 'min': 10, 'max': 1000},
            'lr': {'type': 'float', 'default': 1e-4, 'min': 1e-6, 'max': 1e-2},
            'early_stop': {'type': 'int', 'default': 20, 'min': 5, 'max': 100},
            'metric': {'type': 'select', 'default': 'ic', 'options': ['ic', 'rank_ic', 'pearson']},
            'loss': {'type': 'select', 'default': 'mse', 'options': ['mse', 'mae']},
            'GPU': {'type': 'int', 'default': 0, 'min': 0, 'max': 1},
        },
        'ADARNN': {
            'd_feat': {'type': 'int', 'default': 6, 'min': 1, 'max': 20},
            'hidden_size': {'type': 'int', 'default': 64, 'min': 8, 'max': 512},
            'num_layers': {'type': 'int', 'default': 2, 'min': 1, 'max': 5},
            'dropout': {'type': 'float', 'default': 0.0, 'min': 0.0, 'max': 0.9},
            'n_epochs': {'type': 'int', 'default': 200, 'min': 10, 'max': 1000},
            'lr': {'type': 'float', 'default': 1e-4, 'min': 1e-6, 'max': 1e-2},
            'early_stop': {'type': 'int', 'default': 20, 'min': 5, 'max': 100},
            'metric': {'type': 'select', 'default': 'ic', 'options': ['ic', 'rank_ic', 'pearson']},
            'loss': {'type': 'select', 'default': 'mse', 'options': ['mse', 'mae']},
            'GPU': {'type': 'int', 'default': 0, 'min': 0, 'max': 1},
        },
        'HFLGBModel': {
            'objective': {'type': 'select', 'default': 'binary', 'options': ['binary', 'regression']},
            'learning_rate': {'type': 'float', 'default': 0.01, 'min': 0.001, 'max': 1.0},
            'max_depth': {'type': 'int', 'default': 8, 'min': 1, 'max': 20},
        },
    }

    @staticmethod
    def parse_yaml(yaml_path: str) -> Optional[Dict]:
        """
        Parse YAML configuration file

        Args:
            yaml_path: Path to YAML file

        Returns:
            Configuration dictionary or None
        """
        try:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f'Failed to parse YAML {yaml_path}: {e}')
            return None

    @staticmethod
    def parse_yaml_string(yaml_string: str) -> Optional[Dict]:
        """
        Parse YAML string

        Args:
            yaml_string: YAML content as string

        Returns:
            Configuration dictionary or None
        """
        try:
            return yaml.safe_load(yaml_string)
        except Exception as e:
            logger.error(f'Failed to parse YAML string: {e}')
            return None

    @staticmethod
    def yaml_to_string(config: Dict) -> str:
        """
        Convert configuration dictionary to YAML string

        Args:
            config: Configuration dictionary

        Returns:
            YAML string
        """
        return yaml.dump(config, default_flow_style=False, allow_unicode=True)

    @staticmethod
    def get_config_hash(config: Dict) -> str:
        """
        Get hash of configuration

        Args:
            config: Configuration dictionary

        Returns:
            MD5 hash string
        """
        yaml_string = ConfigParser.yaml_to_string(config)
        return hashlib.md5(yaml_string.encode()).hexdigest()

    @staticmethod
    def validate_config(config: Dict) -> tuple[bool, List[str]]:
        """
        Validate configuration

        Args:
            config: Configuration dictionary

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        # Check for required sections
        required_sections = ['task']
        for section in required_sections:
            if section not in config:
                errors.append(f'Missing required section: {section}')

        # Validate task section
        if 'task' in config:
            task = config['task']
            if 'model' not in task:
                errors.append('Missing model in task')
            if 'dataset' not in task:
                errors.append('Missing dataset in task')

        return (len(errors) == 0, errors)

    @staticmethod
    def get_model_schema(model_name: str) -> Dict:
        """
        Get parameter schema for a model

        Args:
            model_name: Name of the model

        Returns:
            Parameter schema dictionary
        """
        return ConfigParser.MODEL_SCHEMAS.get(model_name, {})

    @staticmethod
    def get_all_models() -> Dict[str, List[str]]:
        """
        Get all available models by category

        Returns:
            Dictionary of model categories
        """
        return {
            'ML': ['LGBModel', 'XGBModel', 'CatBoostModel', 'LinearModel'],
            'DL': ['LSTM', 'GRU', 'Transformer', 'ALSTM', 'TCN', 'TFT', 'GATs', 'Localformer'],
            'Advanced': ['DEnsembleModel', 'TRA', 'TabNet', 'IGMTF', 'KRNN', 'ADARNN', 'HIST'],
            'HF': ['HFLGBModel']
        }

    @staticmethod
    def yaml_to_form_schema(config: Dict) -> Dict:
        """
        Convert YAML config to form schema

        Args:
            config: Configuration dictionary

        Returns:
            Form schema for frontend
        """
        schema = {
            'qlib_init': ConfigParser._extract_qlib_init_schema(config),
            'data_handler': ConfigParser._extract_data_handler_schema(config),
            'model': ConfigParser._extract_model_schema(config),
            'backtest': ConfigParser._extract_backtest_schema(config),
        }
        return schema

    @staticmethod
    def _extract_qlib_init_schema(config: Dict) -> Dict:
        """Extract qlib_init schema"""
        qlib_init = config.get('qlib_init', {})
        return {
            'provider_uri': {
                'type': 'text',
                'default': qlib_init.get('provider_uri', '~/.qlib/qlib_data/cn_data'),
                'label': 'Data Provider URI'
            },
            'region': {
                'type': 'select',
                'default': 'cn',
                'options': ['cn', 'us'],
                'label': 'Region'
            }
        }

    @staticmethod
    def _extract_data_handler_schema(config: Dict) -> Dict:
        """Extract data_handler_config schema"""
        data_handler = config.get('data_handler_config', {})
        return {
            'start_time': {
                'type': 'date',
                'default': data_handler.get('start_time', '2008-01-01'),
                'label': 'Start Time'
            },
            'end_time': {
                'type': 'date',
                'default': data_handler.get('end_time', '2020-08-01'),
                'label': 'End Time'
            },
            'fit_start_time': {
                'type': 'date',
                'default': data_handler.get('fit_start_time', '2008-01-01'),
                'label': 'Train Start Time'
            },
            'fit_end_time': {
                'type': 'date',
                'default': data_handler.get('fit_end_time', '2014-12-31'),
                'label': 'Train End Time'
            },
            'market': {
                'type': 'select',
                'default': 'csi300',
                'options': ['csi300', 'csi500', 'all'],
                'label': 'Market'
            }
        }

    @staticmethod
    def _extract_model_schema(config: Dict) -> Dict:
        """Extract model schema"""
        task = config.get('task', {})
        model = task.get('model', {})

        model_class = model.get('class', 'LGBModel')
        model_kwargs = model.get('kwargs', {})

        # Get module path from mapping or use existing value in config
        default_module_path = ConfigParser.MODEL_MODULE_PATHS.get(model_class, 'qlib.contrib.model.gbdt')
        module_path = model.get('module_path', default_module_path)

        schema = {
            'model_class': {
                'type': 'select',
                'default': model_class,
                'options': ConfigParser._get_all_model_names(),
                'label': 'Model Class'
            },
            'module_path': {
                'type': 'text',
                'default': module_path,
                'label': 'Module Path'
            },
            'kwargs': ConfigParser.get_model_schema(model_class)
        }

        # Update kwargs with current values
        for key, value in model_kwargs.items():
            if key in schema['kwargs']:
                schema['kwargs'][key]['default'] = value

        return schema

    @staticmethod
    def _get_all_model_names() -> List[str]:
        """Get flat list of all model names"""
        all_models = []
        models = ConfigParser.get_all_models()
        for category_models in models.values():
            all_models.extend(category_models)
        return all_models

    @staticmethod
    def _extract_backtest_schema(config: Dict) -> Dict:
        """Extract backtest schema"""
        port_analysis = config.get('port_analysis_config', {})
        backtest = port_analysis.get('backtest', {})
        strategy_config = backtest.get('strategy', {})
        strategy_type = strategy_config.get('type', 'TopkDropoutStrategy')

        return {
            'start_time': {
                'type': 'date',
                'default': backtest.get('start_time', '2017-01-01'),
                'label': 'Backtest Start Time'
            },
            'end_time': {
                'type': 'date',
                'default': backtest.get('end_time', '2020-08-01'),
                'label': 'Backtest End Time'
            },
            'account': {
                'type': 'float',
                'default': backtest.get('account', 100000000),
                'label': 'Initial Account (RMB)'
            },
            'benchmark': {
                'type': 'text',
                'default': backtest.get('benchmark', 'SH000300'),
                'label': 'Benchmark'
            },
            'strategy': {
                'type': 'object',
                'label': 'Strategy Configuration',
                'properties': {
                    'type': {
                        'type': 'select',
                        'default': strategy_type,
                        'options': ConfigParser.STRATEGY_TYPES,
                        'label': 'Strategy Type'
                    },
                    **ConfigParser.STRATEGY_SCHEMAS.get(strategy_type, {})
                }
            }
        }

    @staticmethod
    def form_to_yaml(form_data: Dict, template_config: Dict = None) -> str:
        """
        Convert form data to YAML

        Args:
            form_data: Form data from frontend
            template_config: Optional template config to merge with

        Returns:
            YAML string
        """
        if template_config:
            config = template_config.copy()
        else:
            config = {}

        # Update qlib_init
        if 'qlib_init' in form_data:
            config['qlib_init'] = form_data['qlib_init']

        # Update data_handler_config
        if 'data_handler' in form_data:
            config.setdefault('data_handler_config', {}).update(form_data['data_handler'])

        # Update model
        if 'model' in form_data:
            model_data = form_data['model'].copy()
            # Ensure module_path is set correctly based on model_class
            if 'model_class' in model_data:
                model_class = model_data['model_class']
                if model_class in ConfigParser.MODEL_MODULE_PATHS:
                    model_data['module_path'] = ConfigParser.MODEL_MODULE_PATHS[model_class]
                else:
                    # If not in mapping, keep existing module_path or use default
                    if 'module_path' not in model_data:
                        model_data['module_path'] = 'qlib.contrib.model.gbdt'
            config.setdefault('task', {}).setdefault('model', {}).update(model_data)

        # Update backtest
        if 'backtest' in form_data:
            config.setdefault('port_analysis_config', {}).setdefault('backtest', {}).update(form_data['backtest'])

        return ConfigParser.yaml_to_string(config)
