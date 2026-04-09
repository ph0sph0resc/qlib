"""
Database Models for QLib Web
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import json
import logging

logger = logging.getLogger(__name__)

db = SQLAlchemy()


class Experiment(db.Model):
    """Experiment record for tracking all runs"""
    __tablename__ = 'experiments'

    id = db.Column(db.String(64), primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    task_type = db.Column(db.String(50), nullable=False)  # factor_test, model_train, backtest
    status = db.Column(db.String(20), default='pending')  # pending, running, completed, failed, cancelled
    config = db.Column(db.Text)  # YAML config as text
    config_hash = db.Column(db.String(64))  # Hash of config for deduplication

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)

    # Results (stored as JSON)
    results = db.Column(db.Text)  # JSON string of results

    # Progress
    progress = db.Column(db.Float, default=0.0)  # 0.0 to 100.0
    message = db.Column(db.String(500))

    # Error info
    error = db.Column(db.Text)

    # Related IDs
    parent_id = db.Column(db.String(64))  # For linked experiments (train -> backtest)

    def to_dict(self):
        # Parse results JSON safely
        results = None
        if self.results:
            try:
                results = json.loads(self.results)
            except json.JSONDecodeError as e:
                logger.error(f'Failed to parse results JSON for experiment {self.id}: {e}')
                results = None

        return {
            'id': self.id,
            'name': self.name,
            'task_type': self.task_type,
            'status': self.status,
            'config': self.config,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'progress': self.progress,
            'message': self.message,
            'error': self.error,
            'parent_id': self.parent_id,
            'results': results
        }

    def get_results(self):
        """Parse and return results as dict"""
        if self.results:
            return json.loads(self.results)
        return {}


class TaskLog(db.Model):
    """Log entries for tasks"""
    __tablename__ = 'task_logs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    experiment_id = db.Column(db.String(64), db.ForeignKey('experiments.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    level = db.Column(db.String(10), default='INFO')  # DEBUG, INFO, WARNING, ERROR
    message = db.Column(db.Text, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'experiment_id': self.experiment_id,
            'timestamp': self.timestamp.isoformat(),
            'level': self.level,
            'message': self.message
        }


class ModelRecord(db.Model):
    """Trained model records"""
    __tablename__ = 'model_records'

    id = db.Column(db.String(64), primary_key=True)
    experiment_id = db.Column(db.String(64), db.ForeignKey('experiments.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    model_type = db.Column(db.String(50), nullable=False)
    model_path = db.Column(db.String(500))  # Path to saved model

    # Metrics
    train_score = db.Column(db.Float)
    valid_score = db.Column(db.Float)
    test_score = db.Column(db.Float)

    # Feature importance (JSON)
    feature_importance = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'experiment_id': self.experiment_id,
            'name': self.name,
            'model_type': self.model_type,
            'model_path': self.model_path,
            'train_score': self.train_score,
            'valid_score': self.valid_score,
            'test_score': self.test_score,
            'feature_importance': json.loads(self.feature_importance) if self.feature_importance else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class BacktestRecord(db.Model):
    """Backtest results records"""
    __tablename__ = 'backtest_records'

    id = db.Column(db.String(64), primary_key=True)
    experiment_id = db.Column(db.String(64), db.ForeignKey('experiments.id'), nullable=False)
    model_id = db.Column(db.String(64), db.ForeignKey('model_records.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)

    # Backtest parameters
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    initial_cash = db.Column(db.Float)
    benchmark = db.Column(db.String(50))

    # Performance metrics
    total_return = db.Column(db.Float)
    annual_return = db.Column(db.Float)
    sharpe_ratio = db.Column(db.Float)
    max_drawdown = db.Column(db.Float)
    win_rate = db.Column(db.Float)
    turnover = db.Column(db.Float)

    # Trade statistics
    total_trades = db.Column(db.Integer)
    avg_trade_duration = db.Column(db.Float)

    # PnL series (JSON)
    pnl_series = db.Column(db.Text)
    drawdown_series = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'experiment_id': self.experiment_id,
            'model_id': self.model_id,
            'name': self.name,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'initial_cash': self.initial_cash,
            'benchmark': self.benchmark,
            'total_return': self.total_return,
            'annual_return': self.annual_return,
            'sharpe_ratio': self.sharpe_ratio,
            'max_drawdown': self.max_drawdown,
            'win_rate': self.win_rate,
            'turnover': self.turnover,
            'total_trades': self.total_trades,
            'avg_trade_duration': self.avg_trade_duration,
            'pnl_series': json.loads(self.pnl_series) if self.pnl_series else None,
            'drawdown_series': json.loads(self.drawdown_series) if self.drawdown_series else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
