# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
Rebalance Tracker for recording portfolio rebalance events
"""
from typing import Dict, List, Optional
from datetime import datetime
from threading import Lock


class RebalanceTracker:
    """
    Thread-safe tracker for recording portfolio rebalance events.

    This class tracks when and how a strategy rebalances its portfolio,
    recording details about stocks bought, sold, and their weights.
    """

    _instance = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RebalanceTracker, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the rebalance tracker."""
        self._history: List[Dict] = []
        self._enabled = False

    def enable(self):
        """Enable rebalance tracking."""
        self._enabled = True

    def disable(self):
        """Disable rebalance tracking."""
        self._enabled = False

    def is_enabled(self) -> bool:
        """Check if tracking is enabled."""
        return self._enabled

    def reset(self):
        """Clear all rebalance history."""
        with self._lock:
            self._history = []

    def record_rebalance(
        self,
        date: str,
        trade_step: int,
        buy_orders: List[Dict],
        sell_orders: List[Dict],
        position_before: Dict,
        position_after: Dict
    ) -> None:
        """
        Record a rebalance event.

        Parameters
        ----------
        date : str
            The trading date
        trade_step : int
            The trading step number
        buy_orders : List[Dict]
            List of buy orders in this rebalance
        sell_orders : List[Dict]
            List of sell orders in this rebalance
        position_before : Dict
            Position snapshot before rebalancing
        position_after : Dict
            Position snapshot after rebalancing
        """
        if not self._enabled:
            return

        # Calculate turnover
        buy_value = sum(order.get('amount', 0) for order in buy_orders)
        sell_value = sum(order.get('amount', 0) for order in sell_orders)
        turnover = (buy_value + sell_value) / 2

        event = {
            'date': date,
            'trade_step': trade_step,
            'buy_orders': buy_orders,
            'sell_orders': sell_orders,
            'stocks_to_buy': [order['stock_id'] for order in buy_orders],
            'stocks_to_sell': [order['stock_id'] for order in sell_orders],
            'buy_amounts': {order['stock_id']: order.get('amount', 0) for order in buy_orders},
            'sell_amounts': {order['stock_id']: order.get('amount', 0) for order in sell_orders},
            'buy_weights': {},  # Will be filled if available
            'sell_weights': {},  # Will be filled if available
            'turnover': turnover,
            'position_before': position_before,
            'position_after': position_after,
            'total_value': sum(pos_after.get('amount', 0) for pos_after in position_after.values()),
            'cash': position_after.get('cash', 0)
        }

        with self._lock:
            self._history.append(event)

    def get_history(self) -> List[Dict]:
        """
        Get all recorded rebalance events.

        Returns
        -------
        List[Dict]
            List of rebalance event dictionaries
        """
        with self._lock:
            return self._history.copy()

    def get_summary(self) -> Dict:
        """
        Get a summary of all rebalance events.

        Returns
        -------
        Dict
            Summary statistics
        """
        history = self.get_history()
        if not history:
            return {
                'count': 0,
                'dates': [],
                'avg_turnover': 0,
                'max_turnover': 0,
                'min_turnover': 0,
                'total_turnover': 0
            }

        turnovers = [event['turnover'] for event in history]
        return {
            'count': len(history),
            'dates': [event['date'] for event in history],
            'avg_turnover': sum(turnovers) / len(turnovers),
            'max_turnover': max(turnovers) if turnovers else 0,
            'min_turnover': min(turnovers) if turnovers else 0,
            'total_turnover': sum(turnovers)
        }

    def get_stock_frequency(self) -> Dict[str, Dict]:
        """
        Get rebalance frequency for each stock.

        Returns
        -------
        Dict[str, Dict]
            Dictionary mapping stock_id to frequency statistics
        """
        history = self.get_history()
        stock_stats = {}

        for event in history:
            for stock_id in event['stocks_to_buy']:
                if stock_id not in stock_stats:
                    stock_stats[stock_id] = {'buy_count': 0, 'sell_count': 0}
                stock_stats[stock_id]['buy_count'] += 1

            for stock_id in event['stocks_to_sell']:
                if stock_id not in stock_stats:
                    stock_stats[stock_id] = {'buy_count': 0, 'sell_count': 0}
                stock_stats[stock_id]['sell_count'] += 1

        return stock_stats
