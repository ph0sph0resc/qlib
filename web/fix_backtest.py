#!/usr/bin/env python3
"""
重置并清理回测任务
"""
import sqlite3
import json

def fix_backtest_data():
    """修复回测任务数据格式"""
    db_path = 'data/qlib_web.db'

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 获取所有回测任务
        cursor.execute("""
            SELECT id, name, task_type, status, progress, message, results, created_at, started_at, completed_at
            FROM experiments
            WHERE task_type='backtest'
            ORDER BY created_at DESC
        """)

        rows = cursor.fetchall()
        print(f"找到 {len(rows)} 个回测任务")

        for row in rows:
            task_id, name, task_type, status, progress, message, results_json, created_at, started_at, completed_at = row

            print(f"\n任务: {name}")
            print(f"  状态: {status}")
            print(f"  进度: {progress}")
            print(f"  消息: {message}")

            # 检查并修复 results JSON
            if results_json:
                try:
                    results = json.loads(results_json)
                    print(f" 修复前的结果键: {list(results.keys())}")

                    # 修复问题字段
                    fixed = False

                    # 确保 dates 是数组
                    if 'dates' in results:
                        if not isinstance(results['dates'], list):
                            print(f"  → dates 不是数组，修复为空数组")
                            results['dates'] = []
                            fixed = True
                        else:
                            # 清理无效日期数据
                            valid_dates = []
                            for d in results['dates']:
                                if isinstance(d, str) and (d.startswith('2') or d.startswith('20')):
                                    valid_dates.append(d)
                            results['dates'] = valid_dates
                            if len(valid_dates) != len(results['dates']):
                                fixed = True

                    # 确保 total_trades 是数组
                    if 'total_trades' in results:
                        if not isinstance(results['total_trades'], list):
                            print(f"  → total_trades 不是数组，修复为空数组")
                            results['total_trades'] = []
                            fixed = True

                    # 清理 benchmark_curve 中的 Prototype 字符串
                    if 'benchmark_curve' in results:
                        if isinstance(results['benchmark_curve'], str) and 'Prototype' in results['benchmark_curve']:
                            print(f"  → benchmark_curve 包含 'Prototype' 字符串，移除")
                            # 这可能是 Array.toString() 的输出
                            # 如果 portfolio_curve 正确，就用它
                            if 'portfolio_curve' in results and isinstance(results['portfolio_curve'], list) and len(results['portfolio_curve']) == len(results['benchmark_curve']):
                                results['benchmark_curve'] = results['portfolio_curve'].copy()
                                fixed = True
                            else:
                                # 创建空数组
                                results['benchmark_curve'] = []
                                fixed = True

                    # 如果有修复，更新数据库
                    if fixed:
                        new_results = json.dumps(results, ensure_ascii=False, indent=2)
                        cursor.execute(
                            "UPDATE experiments SET results = ? WHERE id = ?",
                            (new_results, task_id)
                        )
                        conn.commit()
                        print(f"  → 已更新数据库")
                except json.JSONDecodeError as e:
                    print(f"  → JSON 解析错误: {e}")
                    # 尝试修复：重置为空
                    cursor.execute(
                        "UPDATE experiments SET results = ? WHERE id = ?",
                        ('{"dates": [], "total_trades": [], "benchmark_curve": [], "portfolio_curve": []}', task_id)
                    )
                    conn.commit()
                    print(f"  → 已重置为空对象")

            else:
                print(f"  → results 为空，保持不变")

        conn.close()
        print("\n" + "=" * 80)
        print("修复完成！")

    except Exception as e:
        print(f"错误: {e}")


if __name__ == '__main__':
    fix_backtest_data()
