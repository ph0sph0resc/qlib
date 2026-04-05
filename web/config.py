"""
QLib Web Configuration
"""
import os

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Data directories
DATA_DIR = os.path.join(BASE_DIR, 'data')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# Database
DATABASE_PATH = os.path.join(DATA_DIR, 'qlib_web.db')
DATABASE_URI = f'sqlite:///{DATABASE_PATH}'

# QLib default settings
QLIB_DEFAULT_PROVIDER = os.path.expanduser('~/.qlib/qlib_data/cn_data')
QLIB_DEFAULT_REGION = 'cn'

# Flask settings
SECRET_KEY = os.environ.get('QLIB_WEB_SECRET_KEY', 'dev-secret-key-change-in-production')
DEBUG = os.environ.get('QLIB_WEB_DEBUG', 'True').lower() == 'true'
HOST = os.environ.get('QLIB_WEB_HOST', '0.0.0.0')
PORT = int(os.environ.get('QLIB_WEB_PORT', '5000'))

# Task settings
MAX_CONCURRENT_TASKS = 3
TASK_TIMEOUT = 3600  # 1 hour default timeout

# Pagination
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Available markets
AVAILABLE_MARKETS = ['csi300', 'csi500', 'all', 'custom']

# Available regions
AVAILABLE_REGIONS = ['cn', 'us']

# Model categories
MODEL_CATEGORIES = {
    'ML': ['LGBModel', 'XGBModel', 'CatModel', 'Linear'],
    'DL': ['LSTM', 'GRU', 'Transformer', 'ALSTM', 'TCN', 'TFT', 'GATs', 'Localformer'],
    'Advanced': ['DoubleEnsemble', 'TRA', 'TabNet', 'IGMTF', 'KRNN', 'ADARNN', 'HIST'],
    'HF': ['HFLGBModel']
}

# Alpha factor sets
ALPHA_FACTORS = ['Alpha158', 'Alpha360', 'Alpha191', 'custom']

# Strategy types
STRATEGY_TYPES = ['TopkDropoutStrategy', 'SoftTopkStrategy', 'EnhancedIndexingStrategy']

# Task status
TASK_STATUS = {
    'PENDING': 'pending',
    'RUNNING': 'running',
    'COMPLETED': 'completed',
    'FAILED': 'failed',
    'CANCELLED': 'cancelled'
}

# Task types
TASK_TYPES = {
    'FACTOR_TEST': 'factor_test',
    'MODEL_TRAIN': 'model_train',
    'BACKTEST': 'backtest'
}
