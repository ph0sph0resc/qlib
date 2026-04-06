"""
清理卡在 running 状态的任务
用于修复状态同步问题
"""
import sqlite3
import sys

def cleanup_stuck_tasks():
    """清理卡在 running 状态的任务"""
    db_path = 'data/qlib_web.db'

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 查找所有卡在 running 状态的任务
        cursor.execute("""
            SELECT id, name, task_type, progress, message, created_at
            FROM experiments
            WHERE status = 'running'
        """)

        stuck_tasks = cursor.fetchall()

        if not stuck_tasks:
            print("没有发现卡在 running 状态的任务")
            return

        print(f"发现 {len(stuck_tasks)} 个卡在 running 状态的任务:")
        print("-" * 80)

        for task in stuck_tasks:
            task_id, name, task_type, progress, message, created_at = task
            print(f"  ID: {task_id}")
            print(f"  名称: {name}")
            print(f"  类型: {task_type}")
            print(f"  进度: {progress}")
            print(f"  消息: {message}")
            print(f"  创建时间: {created_at}")
            print("-" * 80)

        # 确认后清理
        print("\n请确认是否要将这些任务重置为 pending 状态？(y/n)")
        response = input().strip().lower()

        if response == 'y':
            cursor.execute("""
                UPDATE experiments
                SET status = 'pending', progress = 0, message = 'Task reset'
                WHERE status = 'running'
            """)

            conn.commit()
            print(f"已重置 {cursor.rowcount} 个任务为 pending 状态")

            # 显示清理后的状态
            cursor.execute("SELECT COUNT(*) FROM experiments WHERE status = 'running'")
            running_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM experiments WHERE status = 'pending'")
            pending_count = cursor.fetchone()[0]

            print(f"\n清理后:")
            print(f"  running 任务: {running_count}")
            print(f"  pending 任务: {pending_count}")
        else:
            print("操作已取消")

        conn.close()

    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == '__main__':
    cleanup_stuck_tasks()
