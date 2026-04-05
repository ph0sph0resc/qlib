"""
Task Manager for QLib Web
Handles background task execution using threading
"""
import threading
import uuid
import time
import queue
import logging
from typing import Dict, Optional, Callable
from datetime import datetime

logger = logging.getLogger(__name__)


class TaskStatus:
    PENDING = 'pending'
    RUNNING = 'running'
    COMPLETED = 'completed'
    FAILED = 'failed'
    CANCELLED = 'cancelled'


class Task:
    """Represents a background task"""

    def __init__(self, task_id: str, task_type: str, func: Callable, args: tuple = (), kwargs: dict = None):
        self.id = task_id
        self.type = task_type
        self.func = func
        self.args = args
        self.kwargs = kwargs or {}
        self.status = TaskStatus.PENDING
        self.progress = 0.0
        self.message = 'Task pending'
        self.result = None
        self.error = None
        self.created_at = datetime.now().isoformat()
        self.started_at = None
        self.completed_at = None
        self._thread = None
        self._stop_event = threading.Event()
        self._log_queue = queue.Queue()
        self._status_callbacks = []  # 状态变更回调列表

    def start(self):
        """Start the task in a background thread"""
        self.status = TaskStatus.RUNNING
        self.started_at = datetime.now().isoformat()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self):
        """Run the task function"""
        try:
            self._log_queue.put(('INFO', f'Task {self.id} started'))
            self.result = self.func(
                *self.args,
                task=self,
                **self.kwargs
            )
            self.status = TaskStatus.COMPLETED
            self.progress = 100.0
            self.message = 'Task completed'
            self._log_queue.put(('INFO', f'Task {self.id} completed'))
        except Exception as e:
            self.status = TaskStatus.FAILED
            self.error = str(e)
            self.message = f'Task failed: {str(e)}'
            logger.error(f'Task {self.id} failed: {e}', exc_info=True)
            self._log_queue.put(('ERROR', f'Task {self.id} failed: {str(e)}'))
        finally:
            self.completed_at = datetime.now().isoformat()
            # 触发状态变更回调 - 关键修复！任务完成时必须触发回调
            logger.info(f'Task {self.id} finished with status={self.status}, triggering callbacks')
            self._notify_status_change()

    def stop(self):
        """Stop the task"""
        if self.status == TaskStatus.RUNNING:
            self._stop_event.set()
            self.status = TaskStatus.CANCELLED
            self.message = 'Task cancelled'
            self._log_queue.put(('INFO', f'Task {self.id} cancelled'))

    def is_stopped(self) -> bool:
        """Check if task is stopped"""
        return self._stop_event.is_set()

    def update_progress(self, progress: float, message: str = None):
        """Update task progress"""
        self.progress = min(100.0, max(0.0, progress))
        if message:
            self.message = message
            self._log_queue.put(('INFO', message))
        # 触发进度更新回调
        self._notify_status_change()

    def get_logs(self) -> list:
        """Get all queued logs"""
        logs = []
        while not self._log_queue.empty():
            try:
                logs.append(self._log_queue.get_nowait())
            except queue.Empty:
                break
        return logs

    def add_status_callback(self, callback: Callable):
        """添加状态变更回调"""
        self._status_callbacks.append(callback)

    def _notify_status_change(self):
        """通知所有注册的回调"""
        for callback in self._status_callbacks:
            try:
                callback(self)
            except Exception as e:
                logger.error(f'Status callback error: {e}')

    def to_dict(self) -> dict:
        """Convert task to dictionary"""
        return {
            'id': self.id,
            'type': self.type,
            'status': self.status,
            'progress': self.progress,
            'message': self.message,
            'result': self.result,
            'error': self.error,
            'created_at': self.created_at,
            'started_at': self.started_at,
            'completed_at': self.completed_at
        }


class TaskManager:
    """Manages background tasks"""

    def __init__(self, max_concurrent_tasks: int = 3):
        self.tasks: Dict[str, Task] = {}
        self.max_concurrent_tasks = max_concurrent_tasks
        self._lock = threading.Lock()

    def create_task(self, task_type: str, func: Callable, args: tuple = (), kwargs: dict = None) -> str:
        """Create a new task"""
        task_id = str(uuid.uuid4())
        task = Task(task_id, task_type, func, args, kwargs)

        with self._lock:
            self.tasks[task_id] = task

        logger.info(f'Task {task_id} created of type {task_type}')
        return task_id

    def start_task(self, task_id: str) -> bool:
        """Start a task"""
        with self._lock:
            if task_id not in self.tasks:
                logger.error(f'Task {task_id} not found')
                return False

            task = self.tasks[task_id]

            # Check if too many tasks are running
            running_count = sum(1 for t in self.tasks.values() if t.status == TaskStatus.RUNNING)
            if running_count >= self.max_concurrent_tasks:
                logger.warning(f'Max concurrent tasks ({self.max_concurrent_tasks}) reached')
                return False

            if task.status != TaskStatus.PENDING:
                logger.warning(f'Task {task_id} is not pending')
                return False

            task.start()
            return True

    def stop_task(self, task_id: str) -> bool:
        """Stop a task"""
        with self._lock:
            if task_id not in self.tasks:
                return False

            self.tasks[task_id].stop()
            return True

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID"""
        with self._lock:
            return self.tasks.get(task_id)

    def get_task_status(self, task_id: str) -> Optional[dict]:
        """Get task status"""
        task = self.get_task(task_id)
        if task:
            return task.to_dict()
        return None

    def get_task_logs(self, task_id: str) -> list:
        """Get task logs"""
        task = self.get_task(task_id)
        if task:
            return task.get_logs()
        return []

    def list_tasks(self, filters: dict = None) -> list:
        """List all tasks"""
        with self._lock:
            tasks = list(self.tasks.values())

        if filters:
            # Apply filters
            if 'status' in filters:
                tasks = [t for t in tasks if t.status == filters['status']]
            if 'type' in filters:
                tasks = [t for t in tasks if t.type == filters['type']]

        return [t.to_dict() for t in tasks]

    def cleanup_old_tasks(self, max_age_hours: int = 24):
        """Remove old completed/failed tasks"""
        cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)

        with self._lock:
            to_remove = []
            for task_id, task in self.tasks.items():
                if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                    if task.completed_at:
                        completed_time = datetime.fromisoformat(task.completed_at).timestamp()
                        if completed_time < cutoff_time:
                            to_remove.append(task_id)

            for task_id in to_remove:
                del self.tasks[task_id]
                logger.info(f'Cleaned up old task {task_id}')

    def get_running_count(self) -> int:
        """Get count of currently running tasks"""
        with self._lock:
            return sum(1 for t in self.tasks.values() if t.status == TaskStatus.RUNNING)


# Global task manager instance
task_manager = TaskManager()
