"""
Task Scheduler Package
Modular, pluggable scheduler for ALwrity tasks.
"""

from sqlalchemy.orm import Session

from .core.scheduler import TaskScheduler
from .core.executor_interface import TaskExecutor, TaskExecutionResult
from .core.exception_handler import (
    SchedulerExceptionHandler, SchedulerException, SchedulerErrorType, SchedulerErrorSeverity,
    TaskExecutionError, DatabaseError, TaskLoaderError, SchedulerConfigError
)
from .executors.monitoring_task_executor import MonitoringTaskExecutor
from .executors.oauth_token_monitoring_executor import OAuthTokenMonitoringExecutor
from .executors.website_analysis_executor import WebsiteAnalysisExecutor
from .executors.gsc_insights_executor import GSCInsightsExecutor
from .executors.bing_insights_executor import BingInsightsExecutor
from .utils.task_loader import load_due_monitoring_tasks
from .utils.oauth_token_task_loader import load_due_oauth_token_monitoring_tasks
from .utils.website_analysis_task_loader import load_due_website_analysis_tasks
from .utils.platform_insights_task_loader import load_due_platform_insights_tasks

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
        
        # Register OAuth token monitoring executor
        oauth_token_executor = OAuthTokenMonitoringExecutor()
        _scheduler_instance.register_executor(
            'oauth_token_monitoring',
            oauth_token_executor,
            load_due_oauth_token_monitoring_tasks
        )
        
        # Register website analysis executor
        website_analysis_executor = WebsiteAnalysisExecutor()
        _scheduler_instance.register_executor(
            'website_analysis',
            website_analysis_executor,
            load_due_website_analysis_tasks
        )
        
        # Register platform insights executors
        # GSC insights executor
        def load_due_gsc_insights_tasks(db: Session, user_id=None):
            return load_due_platform_insights_tasks(db, user_id, platform='gsc')
        
        gsc_insights_executor = GSCInsightsExecutor()
        _scheduler_instance.register_executor(
            'gsc_insights',
            gsc_insights_executor,
            load_due_gsc_insights_tasks
        )
        
        # Bing insights executor
        def load_due_bing_insights_tasks(db: Session, user_id=None):
            return load_due_platform_insights_tasks(db, user_id, platform='bing')
        
        bing_insights_executor = BingInsightsExecutor()
        _scheduler_instance.register_executor(
            'bing_insights',
            bing_insights_executor,
            load_due_bing_insights_tasks
        )
    
    return _scheduler_instance


__all__ = [
    'TaskScheduler',
    'TaskExecutor',
    'TaskExecutionResult',
    'MonitoringTaskExecutor',
    'OAuthTokenMonitoringExecutor',
    'WebsiteAnalysisExecutor',
    'GSCInsightsExecutor',
    'BingInsightsExecutor',
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
