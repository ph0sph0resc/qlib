"""
Rebalance Analysis API
API endpoints for rebalance rebalance analysis
"""
import logging
from flask import request

from api.qlib_wrapper import qlib

logger = logging.getLogger(__name__)


def get_rebalance_history(task_id: str) -> dict:
    """
    Get rebalance history for a backtest task.

    Args:
        task_id: Experiment ID

    Returns:
        dict: API response with events and summary
    """
    try:
        from api.models import Experiment
        import pickle
        from pathlib import Path
        import json
        import yaml
        experiment = Experiment.query.get(task_id)
        data = yaml.safe_load(experiment.config)  # Ensure config is valid YAML
        model_id = data['model_id']

        logger.info(f'Fetching rebalance history for task_id={task_id}, experiment found: {model_id}')
        if not experiment:
            return {'success': False, 'error': 'Experiment not found'}

        # Get filters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        stock_code = request.args.get('stock_code')
        min_turnover = request.args.get('min_turnover', type=float)

        # Try to load rebalance history
        # First check if it's in results
        events = []
        if experiment.results:
            results = json.loads(experiment.results) if isinstance(experiment.results, str) else experiment.results

            # Check if results have rebalance data
            if 'rebalance_events' in results:
                events = results['rebalance_events']

        # If not in results, try to load from pickle file
        if not events:
            exp_dir = qlib.get_experiment_dir(model_id)
            
            rebalance_file = Path(exp_dir)/'artifacts'/ 'portfolio_analysis' / 'rebalance_history.pkl'
            logger.info(f'Looking for rebalance history in {rebalance_file}')
            if rebalance_file.exists():
                with open(rebalance_file, 'rb') as f:
                    history = pickle.load(f)
                    events = []
                    for e in history:
                        # Convert numpy types to native Python types for JSON serialization
                        buy_amounts = {k: float(v) for k, v in e.buy_amounts.items()}
                        sell_amounts = {k: float(v) for k, v in e.sell_amounts.items()}
                        position_before = {k: float(v) for k, v in e.position_before.items()}
                        position_after = {k: float(v) for k, v in e.position_after.items()}

                        events.append({
                            'date': e.date,
                            'trade_step': e.trade_step,
                            'stocks_to_buy': e.stocks_to_buy,
                            'stocks_to_sell': e.stocks_to_sell,
                            'buy_amounts': buy_amounts,
                            'sell_amounts': sell_amounts,
                            'turnover': float(e.turnover),
                            'cash_before': float(e.cash_before),
                            'cash_after': float(e.cash_after),
                            'total_value': float(e.total_value),
                            'position_before': position_before,
                            'position_after': position_after
                        })

        # Apply filters
        if start_date:
            events = [e for e in events if e['date'] >= start_date]
        if end_date:
            events = [e for e in events if e['date'] <= end_date]
        if stock_code:
            events = [
                e for e in events
                if stock_code in e['stocks_to_buy'] or stock_code in e['stocks_to_sell']
            ]
        if min_turnover:
            events = [e for e in events if e['turnover'] >= min_turnover]

        # Calculate summary
        if events:
            summary = {
                'total_rebalances': len(events),
                'avg_turnover': sum(e['turnover'] for e in events) / len(events),
                'max_turnover': max(e['turnover'] for e in events),
                'min_turnover': min(e['turnover'] for e in events),
                'total_buy_amount': sum(sum(e['buy_amounts'].values()) for e in events),
                'total_sell_amount': sum(sum(e['sell_amounts'].values()) for e in events)
            }
        else:
            summary = {
                'total_rebalances': 0,
            'avg_turnover': 0,
            'max_turnover': 0,
            'min_turnover': 0,
            'total_buy_amount': 0,
            'total_sell_amount': 0
            }    
        logger.info(f'No rebalance events found for this experiment.{events[0:3]}')
        return {
            'success': True,
            'events': events,
            'summary': summary
        }

    except Exception as e:
        logger.error(f'Rebalance history error: {e}', exc_info=True)
        return {'success': False, 'error': str(e)}


def export_rebalance_history(task_id: str, export_format: str = 'csv'):
    """
    Export rebalance history as CSV or Excel.

    Args:
        task_id: Experiment ID
        export_format: 'csv' or 'xlsx'

    Returns:
        tuple: (data, filename, mimetype)
    """
    history_response = get_rebalance_history(task_id)

    if not history_response.get('success'):
        return None

    events = history_response.get('events', [])

    if export_format == 'csv':
        import io
        import csv

        # Generate CSV
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow([
            '日期', '交易步骤', '买入股票', '卖出股票',
            '买入金额', '卖出金额', '周转率',
            '调仓前现金', '调仓后现金', '组合价值'
        ])

        # Write data
        for e in events:
            writer.writerow([
                e['date'],
                e['trade_step'],
                ','.join(e['stocks_to_buy']),
                ','.join(e['stocks_to_sell']),
                sum(e['buy_amounts'].values()),
                sum(e['sell_amounts'].values()),
                e['turnover'],
                e['cash_before'],
                e['cash_after'],
                e['total_value']
            ])

        return output.getvalue(), f'rebalance_history_{task_id}.csv', 'text/csv'

    elif export_format == 'xlsx':
        import io
        import csv

        # Generate CSV (using basic approach since we may not have openpyxl)
        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow([
            '日期', '交易步骤', '买入股票', '卖出股票',
            '买入金额', '卖出金额', '周转率',
            '调仓前现金', '调仓后现金', '组合价值'
        ])

        for e in events:
            writer.writerow([
                e['date'],
                e['trade_step'],
                ','.join(e['stocks_to_buy']),
                ','.join(e['stocks_to_sell']),
                sum(e['buy_amounts'].values()),
                sum(e['sell_amounts'].values()),
                e['turnover'],
                e['cash_before'],
                e['cash_after'],
                e['total_value']
            ])

        return output.getvalue(), f'rebalance_history_{task_id}.xlsx', 'text/csv'

    return None
