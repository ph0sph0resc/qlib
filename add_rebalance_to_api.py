# Read the original backup file
with open("/home/firewind0/qlib/web/api/qlib_wrapper_backup.py", "r", encoding="utf-8") as f:
    original_content = f.read()

# Read the current file
with open("/home/firewind0/qlib/web/api/qlib_wrapper.py", "r", encoding="utf-8") as f:
    current_content = f.read()

# The rebalance code to insert (without the extra closing brace from error)
rebalance_code = '''
        # Load rebalance history if available
        try:
            rebalance_history = backtest_results.get('rebalance_history.pkl')
            if rebalance_history:
                # Convert rebalance events to frontend format
                rebalance_events = []
                for event in rebalance_history:
                    event_dict = {
                        'date': event.date,
                        'trade_step': event.trade_step,
                        'stocks_to_buy': event.stocks_to_buy,
                        'stocks_to_sell': event.stocks_to_sell,
                        'buy_amounts': event.buy_amounts,
                        'sell_amounts': event.sell_amounts,
                        'turnover': event.turnover,
                        'cash_before': event.cash_before,
                        'cash_after': event.cash_after,
                        'total_value': event.total_value
                    }
                    rebalance_events.append(event_dict)

                results['rebalance_events'] = rebalance_events
                logger.info(f"Loaded {len(rebalance_events)} rebalance events")
        except Exception as e:
            logger.warning(f"Failed to load rebalance history: {e}")
'''

# Check if rebalance code already exists
if "# Load rebalance history if available" in current_content:
    # Rebalance code already added
    print("Rebalance history extraction code already exists in the file")
else:
    # Find the insertion point
    # Looking for: 'backtest_id': f'bt_...\n            'total_return': ...\n            # Format dates
    pattern_start = "'backtest_id':"
    pattern_end = "            # Format dates"

    if pattern_start in original_content and pattern_end in original_content:
        # Find the position in original content
        start_pos = original_content.find(pattern_start)
        end_pos = original_content.find(pattern_end, start_pos)

        if start_pos != -1 and end_pos != -1:
            # Find the corresponding position in current content
            current_start_pos = current_content.find(pattern_start)

            if current_start_pos != -1:
                # Build new content
                before = current_content[:current_start_pos]
                after = current_content[current_start_pos + len(pattern_start):]

                new_content = before + rebalance_code + '\n' + after

                # Write new content
                with open("/home/firewind0/qlib/web/api/qlib_wrapper.py", "w", encoding="utf-8") as f:
                    f.write(new_content)

                print("Rebalance history extraction code added successfully")
            else:
                print("Could not find insertion point in current content")
    else:
        print("Could not find insertion point in original content")
