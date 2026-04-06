"""
清理有问题的旧回测任务
"""
import sqlite3

def cleanup_problematic_backtest():
    """清理包含无效数据的回测任务"""
    db_path = 'data/qlib_web.db'

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 查找包含无效数据的回测任务
        cursor.execute("""
            SELECT id, name, results
            FROM experiments
            WHERE task_type='backtest'
                AND (results LIKE '%Prototype%' OR results LIKE '%function%')
        """)

        problematic_tasks = cursor.fetchall()

        if not problematic_tasks:
            print("没有发现有问题的回测任务")
            return

        print(f"发现 {len(problematic_tasks)} 个有问题的回测任务:")
        print("-" * 80)

        for task in problematic_tasks:
            task_id, name, results_json = task
            print(f"  ID: {task_id}")
            print(f"  名称: {name}")
            print(f"  问题: 包含无效的函数引用")

            # 删除这些任务
            cursor.execute("DELETE FROM experiments WHERE id = ?", (task_id,))
            print(f"  已删除")

        conn.commit()
        print(f"\n已清理 {cursor.rowcount} 个有问题的回测任务")

        # 显示清理后的状态
        cursor.execute("SELECT COUNT(*) FROM experiments WHERE task_type='backtest' AND status='completed'")
        completed_count = cursor.fetchone()[0]
        print(f"\n清理后剩余的 completed 回测任务: {completed_count}")

        # 显示最新的回测任务
        cursor.execute("""
            SELECT id, name, task_type, status
            FROM experiments
            WHERE task_type='backtest'
            ORDER BY created_at DESC
            LIMIT 1
        """)
        latest = cursor.fetchone()
        if latest:
            print(f"\n最新的回测任务:")
            print(f"  ID: {latest[0]}")
            print(f"  名称: {latest[1]}")
            print(f"  状态: {latest[2]}")

        conn.close()

    except Exception as e:
        print(f"错误: {e}")


if __name__ == '__main__':
    cleanup_problematic_backtest()
