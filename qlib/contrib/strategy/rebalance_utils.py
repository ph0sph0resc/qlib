# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""
Helper class for detecting portfolio rebalance events
This helper provides functionality to detect when and how a strategy rebalances its portfolio
by analyzing position changes before and after trading decisions.
"""

from typing import Dict, List, Optional


def detect_rebalance(
    position_before: Dict[str, float],
    position_after: Dict[str, float],
    threshold: float = 0.1
) -> Optional[Dict]:
    """
    Detect if a rebalance occurred by comparing positions before and after.

    Parameters
    ----------
    position_before : Dict[str, float]
        Position snapshot before rebalancing, mapping stock_id to amount
    position_after : Dict[str, float]
        Position snapshot after rebalancing, mapping stock_id to amount
    threshold : float
        Minimum percentage change to consider as a rebalance (default 0.1 = 10%)

    Returns
    -------
    Optional[Dict]
        Rebalance event information if detected, None otherwise
    """
    if not position_before or not position_after:
        return None

    # Get list of stocks in both positions
    stocks_before = set(position_before.keys())
    stocks_after = set(position_after.keys())
    all_stocks = stocks_before.union(stocks_after)

    stocks_bought = []
    stocks_sold = []
    total_buy_value = 0.0
    total_sell_value = 0.0

    for stock_id in all_stocks:
        # Skip cash in position comparison
        if stock_id == 'cash':
            continue

        amount_before = position_before.get(stock_id, 0)
        amount_after = position_after.get(stock_id, 0)

        # Check if this stock's position changed significantly
        if amount_before > 0 and amount_after == 0:
            stocks_sold.append(stock_id)
            total_sell_value += amount_before
        elif amount_before == 0 and amount_after > 0:
            stocks_bought.append(stock_id)
            total_buy_value += amount_after

    # Calculate total value change
    cash_before = position_before.get('cash', 0)
    cash_after = position_after.get('cash', 0)

    total_value_before = cash_before + sum(
        amount for stock, amount in position_before.items() if stock != 'cash'
    )
    total_value_after = cash_after + sum(
        amount for stock, amount in position_after.items() if stock != 'cash'
    )

    # Check if change exceeds threshold
    total_change_ratio = abs(total_value_after - total_value_before) / total_value_before if total_value_before > 0 else 0

    if total_change_ratio < threshold:
        return None

    return {
        'total_value_before': total_value_before,
        'total_value_after': total_value_after,
        'change_ratio': total_change_ratio,
        'stocks_bought': stocks_bought,
        'stocks_sold': stocks_sold,
        'total_buy_value': total_buy_value,
        'total_sell_value': total_sell_value,
        'cash_before': cash_before,
        'cash_after': cash_after
    }
