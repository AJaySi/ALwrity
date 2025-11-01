"""
Task Scheduler Package
Modular, pluggable scheduler for ALwrity tasks.
"""

from .core.scheduler import TaskScheduler
from .core.executor_interface import TaskExecutor, TaskExecutionResult
from .core.exception_handler import (
    SchedulerExceptionHandler, SchedulerException, SchedulerErrorType, SchedulerErrorSeverity,
    TaskExecutionError, DatabaseError, TaskLoaderError, SchedulerConfigError
)
from .executors.monitoring_task_executor import MonitoringTaskExecutor
from .utils.task_loader import load_due_monitoring_tasks

# Global scheduler instance (initialized on first access)
_scheduler_instance: TaskScheduler = None


def get_scheduler() -> TaskScheduler:
    """
    Get global scheduler instance (singleton pattern).
    
    Returns:
        TaskScheduler instance
    """
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = TaskScheduler(
            check_interval_minutes=15,
            max_concurrent_executions=10
        )
        
        # Register monitoring task executor
        monitoring_executor = MonitoringTaskExecutor()
        _scheduler_instance.register_executor(
            'monitoring_task',
            monitoring_executor,
            load_due_monitoring_tasks
        )
    
    return _scheduler_instance


__all__ = [
    'TaskScheduler',
    'TaskExecutor',
    'TaskExecutionResult',
    'MonitoringTaskExecutor',
    'get_scheduler',
    # Exception handling
    'SchedulerExceptionHandler',
    'SchedulerException',
    'SchedulerErrorType',
    'SchedulerErrorSeverity',
    'TaskExecutionError',
    'DatabaseError',
    'TaskLoaderError',
    'SchedulerConfigError'
]
