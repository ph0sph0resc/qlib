# Read the file and fix the rebalance history extraction
with open("/home/firewind0/qlib/web/api/qlib_wrapper.py", "r", encoding="utf-8") as f:
    content = f.read()

# Find the line with "'backtest_id':" and the closing brace after it
pattern_to_find = "'backtest_id':"
pattern_closing = '        }'
pattern_end = '        return results'

# Split the content at key points
parts = content.split(pattern_to_find)
if len(parts) < 2:
    print(f"Could not find '{pattern_to_find}' in file")
    exit(1)

# Find the closing brace position
second_part = parts[1]
closing_pos = second_part.find(pattern_closing)
if closing_pos == -1:
    print(f"Could not find closing brace after '{pattern_to_find}'")
    exit(1)

# Prepare the rebalance extraction code
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

# Reconstruct the content
before_rebalance = parts[0] + pattern_to_find
closing_brace = second_part[:closing_pos + len(pattern_closing)] + pattern_closing
after_rebalance = second_part[closing_pos + len(pattern_closing):]

# Find and insert before the 'return results'
end_pos = before_rebalance.find(pattern_end)
if end_pos == -1:
    print(f"Could not find '{pattern_end}'")
    exit(1)

# Insert the rebalance code
new_content = before_rebalance + rebalance_code + '\n' + closing_brace + '\n' + after_rebalance

# Write the modified content
with open("/home/firewind0/qlib/web/api/qlib_wrapper.py", "w", encoding="utf-8") as f:
    f.write(new_content)

print("Rebalance history extraction code added successfully")
