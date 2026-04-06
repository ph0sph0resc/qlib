#!/usr/bin/env python3
"""
清理有问题的旧回测任务
"""
import sqlite3

def main():
    db_path = 'data/qlib_web.db'

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 查找所有回测任务
    cursor.execute("SELECT id, name, task_type, status, results FROM experiments WHERE task_type='backtest'")
    rows = cursor.fetchall()

    print(f"找到 {len(rows)} 个回测任务")
    print("=" * 80)

    cleaned = 0

    for row in rows:
        task_id, name, task_type, status, results_json = row

        # 检查 results 是否包含无效的 JavaScript 代码
        if results_json:
            if any(x in results_json for x in ['function', '=>', '{', '}', 'Array()', 'Object()']):
                print(f"\n清理任务: {name} (ID: {task_id[:8]})")
                cursor.execute("DELETE FROM experiments WHERE id = ?", (task_id,))
                cleaned += 1
            else:
                print(f"\n保留任务: {name} (ID: {task_id[:8]}) - 数据正常")

    conn.commit()
    print("=" * 80)
    print(f"已清理 {cleaned} 个有问题的任务")

    # 显示清理后的状态
    cursor.execute("SELECT COUNT(*) FROM experiments WHERE task_type='backtest'")
    remaining = cursor.fetchone()[0]
    print(f"剩余回测任务: {remaining}")

    conn.close()

if __name__ == '__main__':
    main()
