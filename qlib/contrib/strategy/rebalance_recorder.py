# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
Rebalance Recorder for tracking portfolio rebalance events
This module provides thread-safe functionality to record when and how a strategy
rebalances its portfolio, including details about stocks bought, sold, and their weights.
"""
from typing import Dict, List, Optional
from datetime import datetime
from threading import Lock


class RebalanceEvent:
    """调仓事件记录"""

    def __init__(
        self,
        date: str,
        trade_step: int,
        buy_orders: List[Dict],
        sell_orders: List[Dict],
        position_before: Dict[str, float],
        position_after: Dict[str, float],
        cash_before: float,
        cash_after: float,
        total_value: float
    ):
        self.date = date
        self.trade_step = trade_step
        self.buy_orders = buy_orders
        self.sell_orders = sell_orders
        self.position_before = position_before
        self.position_after = position_after
        self.cash_before = cash_before
        self.cash_after = cash_after
        self.total_value = total_value


class RebalanceRecorder:
    """
    Thread-safe recorder for tracking portfolio rebalance events.

    This class tracks when and how a strategy rebalances its portfolio,
    recording details about stocks bought, sold, and their weights.
    """

    _instance = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RebalanceRecorder, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize rebalance recorder."""
        self._history: List[RebalanceEvent] = []
        self._enabled = True

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
        position_before: Dict[str, float],
        position_after: Dict[str, float],
        cash_before: float,
        cash_after: float,
        total_value: float
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
        position_before : Dict[str, float]
            Position snapshot before rebalancing
        position_after : Dict[str, float]
            Position snapshot after rebalancing
        cash_before : float
            Cash amount before rebalancing
        cash_after : float
            Cash amount after rebalancing
        total_value : float
            Total portfolio value after rebalancing
        """
        if not self._enabled:
            return

        # Calculate turnover
        buy_value = sum(order.get('amount', 0) for order in buy_orders)
        sell_value = sum(order.get('amount', 0) for order in sell_orders
        turnover = (buy_value + sell_value) / 2

        event = RebalanceEvent(
            date=date,
            trade_step=trade_step,
            buy_orders=buy_orders,
            sell_orders=sell_orders,
            position_before=position_before,
            position_after=position_after,
            cash_before=cash_before,
            cash_after=cash_after,
            total_value=total_value
        )

        with self._lock:
            self._history.append(event)

    def get_history(self) -> List[RebalanceEvent]:
        """
        Get all recorded rebalance events.

        Returns
        -------
        List[RebalanceEvent]
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

        turnovers = [event.turnover for event in history]
        return {
            'count': len(history),
            'dates': [event.date for event in history],
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
            for stock_id in event.stocks_to_buy:
                if stock_id not in stock_stats:
                    stock_stats[stock_id] = {'buy_count': 0, 'sell_count': 0}
                stock_stats[stock_id]['buy_count'] += 1

            for stock_id in event.stocks_to_sell:
                if stock_id not in stock_stats:
                    stock_stats[stock_id] = {'buy_count': 0, 'sell_count': 0}
                stock_stats[stock_id]['sell_count'] += 1

        return stock_stats


# Global rebalance recorder instance
rebalance_recorder = RebalanceRecorder()