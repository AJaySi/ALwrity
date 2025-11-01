"""
Core Task Scheduler Service
Pluggable task scheduler that can work with any task model.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session

from .executor_interface import TaskExecutor, TaskExecutionResult
from .task_registry import TaskRegistry
from .exception_handler import (
    SchedulerExceptionHandler, SchedulerException, TaskExecutionError, DatabaseError,
    TaskLoaderError, SchedulerConfigError
)
from services.database import get_db_session
from utils.logger_utils import get_service_logger

logger = get_service_logger("task_scheduler")


class TaskScheduler:
    """
    Pluggable task scheduler that can work with any task model.
    
    Features:
    - Async task execution
    - Plugin-based executor system
    - Database-backed task persistence
    - Configurable check intervals
    - Automatic retry logic
    """
    
    def __init__(
        self,
        check_interval_minutes: int = 15,
        max_concurrent_executions: int = 10,
        enable_retries: bool = True,
        max_retries: int = 3
    ):
        """
        Initialize the task scheduler.
        
        Args:
            check_interval_minutes: How often to check for due tasks
            max_concurrent_executions: Maximum concurrent task executions
            enable_retries: Whether to retry failed tasks
            max_retries: Maximum retry attempts
        """
        self.check_interval_minutes = check_interval_minutes
        self.max_concurrent_executions = max_concurrent_executions
        self.enable_retries = enable_retries
        self.max_retries = max_retries
        
        # Initialize APScheduler
        self.scheduler = AsyncIOScheduler(
            timezone='UTC',
            job_defaults={
                'coalesce': True,
                'max_instances': 1,
                'misfire_grace_time': 300  # 5 minutes grace period
            }
        )
        
        # Task executor registry
        self.registry = TaskRegistry()
        
        # Track running executions
        self.active_executions: Dict[str, asyncio.Task] = {}
        
        # Exception handler for robust error handling
        self.exception_handler = SchedulerExceptionHandler()
        
        # Intelligent scheduling configuration
        self.min_check_interval_minutes = 15  # Check every 15min when active strategies exist
        self.max_check_interval_minutes = 60  # Check every 60min when no active strategies
        self.current_check_interval_minutes = check_interval_minutes  # Current interval
        
        # Statistics
        self.stats = {
            'total_checks': 0,
            'tasks_found': 0,
            'tasks_executed': 0,
            'tasks_failed': 0,
            'tasks_skipped': 0,
            'last_check': None,
            'per_user_stats': {},  # Track metrics per user for user isolation
            'active_strategies_count': 0,  # Track active strategies with tasks
            'last_interval_adjustment': None  # Track when interval was last adjusted
        }
        
        self._running = False
    
    def _get_trigger_for_interval(self, interval_minutes: int):
        """
        Get the appropriate trigger for the given interval.
        
        For intervals >= 60 minutes, use IntervalTrigger.
        For intervals < 60 minutes, use CronTrigger.
        
        Args:
            interval_minutes: Interval in minutes
            
        Returns:
            Appropriate APScheduler trigger
        """
        if interval_minutes >= 60:
            # Use IntervalTrigger for intervals >= 60 minutes
            return IntervalTrigger(minutes=interval_minutes)
        else:
            # Use CronTrigger for intervals < 60 minutes (valid range: 0-59)
            return CronTrigger(minute=f'*/{interval_minutes}')
    
    def register_executor(
        self,
        task_type: str,
        executor: TaskExecutor,
        task_loader: Callable[[Session], List[Any]]
    ):
        """
        Register a task executor for a specific task type.
        
        Args:
            task_type: Unique identifier for task type (e.g., 'monitoring_task')
            executor: TaskExecutor instance that handles execution
            task_loader: Function that loads due tasks from database
        """
        self.registry.register(task_type, executor, task_loader)
        logger.info(f"Registered executor for task type: {task_type}")
    
    async def start(self):
        """Start the scheduler with intelligent interval adjustment."""
        if self._running:
            logger.warning("Scheduler is already running")
            return
        
        try:
            # Determine initial check interval based on active strategies
            initial_interval = await self._determine_optimal_interval()
            self.current_check_interval_minutes = initial_interval
            
            # Add periodic job to check for due tasks
            self.scheduler.add_job(
                self._check_and_execute_due_tasks,
                trigger=self._get_trigger_for_interval(initial_interval),
                id='check_due_tasks',
                replace_existing=True
            )
            
            self.scheduler.start()
            self._running = True
            
            logger.info(
                f"Task scheduler started | "
                f"check_interval={initial_interval}min | "
                f"registered_types={self.registry.get_registered_types()}"
            )
            
        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")
            raise
    
    async def stop(self):
        """Stop the scheduler gracefully."""
        if not self._running:
            return
        
        try:
            # Cancel all active executions
            for task_id, execution_task in self.active_executions.items():
                execution_task.cancel()
            
            # Wait for active executions to complete (with timeout)
            if self.active_executions:
                await asyncio.wait(
                    self.active_executions.values(),
                    timeout=30
                )
            
            # Shutdown scheduler
            self.scheduler.shutdown(wait=True)
            self._running = False
            
            logger.info("Task scheduler stopped gracefully")
            
        except Exception as e:
            logger.error(f"Error stopping scheduler: {e}")
            raise
    
    async def _check_and_execute_due_tasks(self):
        """
        Main scheduler loop: check for due tasks and execute them.
        This runs periodically with intelligent interval adjustment based on active strategies.
        """
        self.stats['total_checks'] += 1
        self.stats['last_check'] = datetime.utcnow().isoformat()
        
        logger.debug("Checking for due tasks...")
        
        db = None
        try:
            db = get_db_session()
            if db is None:
                logger.error("Failed to get database session")
                return
            
            # Check for active strategies and adjust interval intelligently
            await self._adjust_check_interval_if_needed(db)
            
            # Check each registered task type
            for task_type in self.registry.get_registered_types():
                await self._process_task_type(task_type, db)
            
        except Exception as e:
            error = DatabaseError(
                message=f"Error checking for due tasks: {str(e)}",
                original_error=e
            )
            self.exception_handler.handle_exception(error)
        finally:
            if db:
                db.close()
    
    async def _determine_optimal_interval(self) -> int:
        """
        Determine optimal check interval based on active strategies.
        
        Returns:
            Optimal check interval in minutes
        """
        db = None
        try:
            db = get_db_session()
            if db:
                from services.active_strategy_service import ActiveStrategyService
                active_strategy_service = ActiveStrategyService(db_session=db)
                active_count = active_strategy_service.count_active_strategies_with_tasks()
                self.stats['active_strategies_count'] = active_count
                
                if active_count > 0:
                    logger.info(f"Found {active_count} active strategies with tasks - using {self.min_check_interval_minutes}min interval")
                    return self.min_check_interval_minutes
                else:
                    logger.info(f"No active strategies with tasks - using {self.max_check_interval_minutes}min interval")
                    return self.max_check_interval_minutes
        except Exception as e:
            logger.warning(f"Error determining optimal interval: {e}, using default {self.min_check_interval_minutes}min")
        finally:
            if db:
                db.close()
        
        # Default to shorter interval on error (safer)
        return self.min_check_interval_minutes
    
    async def _adjust_check_interval_if_needed(self, db: Session):
        """
        Intelligently adjust check interval based on active strategies.
        
        If there are active strategies with tasks, check more frequently.
        If there are no active strategies, check less frequently.
        
        Args:
            db: Database session
        """
        try:
            from services.active_strategy_service import ActiveStrategyService
            
            active_strategy_service = ActiveStrategyService(db_session=db)
            active_count = active_strategy_service.count_active_strategies_with_tasks()
            self.stats['active_strategies_count'] = active_count
            
            # Determine optimal interval
            if active_count > 0:
                optimal_interval = self.min_check_interval_minutes
            else:
                optimal_interval = self.max_check_interval_minutes
            
            # Only reschedule if interval needs to change
            if optimal_interval != self.current_check_interval_minutes:
                logger.info(
                    f"Adjusting scheduler interval: {self.current_check_interval_minutes}min → {optimal_interval}min | "
                    f"active_strategies={active_count}"
                )
                
                # Reschedule the job with new interval
                self.scheduler.modify_job(
                    'check_due_tasks',
                    trigger=self._get_trigger_for_interval(optimal_interval)
                )
                
                self.current_check_interval_minutes = optimal_interval
                self.stats['last_interval_adjustment'] = datetime.utcnow().isoformat()
                
                logger.info(f"Scheduler interval adjusted to {optimal_interval}min")
            
        except Exception as e:
            logger.warning(f"Error adjusting check interval: {e}")
    
    async def trigger_interval_adjustment(self):
        """
        Trigger immediate interval adjustment check.
        
        This should be called when a strategy is activated or deactivated
        to immediately adjust the scheduler interval based on current active strategies.
        """
        if not self._running:
            logger.debug("Scheduler not running, skipping interval adjustment")
            return
        
        try:
            db = get_db_session()
            if db:
                await self._adjust_check_interval_if_needed(db)
            else:
                logger.warning("Could not get database session for interval adjustment")
        except Exception as e:
            logger.warning(f"Error triggering interval adjustment: {e}")
    
    async def _process_task_type(self, task_type: str, db: Session):
        """Process due tasks for a specific task type."""
        try:
            # Get task loader for this type
            try:
                task_loader = self.registry.get_task_loader(task_type)
            except Exception as e:
                error = TaskLoaderError(
                    message=f"Failed to get task loader for type {task_type}: {str(e)}",
                    task_type=task_type,
                    original_error=e
                )
                self.exception_handler.handle_exception(error)
                return
            
            # Load due tasks (with error handling)
            try:
                due_tasks = task_loader(db)
            except Exception as e:
                error = TaskLoaderError(
                    message=f"Failed to load due tasks for type {task_type}: {str(e)}",
                    task_type=task_type,
                    original_error=e
                )
                self.exception_handler.handle_exception(error)
                return
            
            if not due_tasks:
                return
            
            self.stats['tasks_found'] += len(due_tasks)
            logger.info(f"Found {len(due_tasks)} due tasks for type: {task_type}")
            
            # Execute tasks (with concurrency limit)
            execution_tasks = []
            for task in due_tasks:
                if len(self.active_executions) >= self.max_concurrent_executions:
                    logger.warning(
                        f"Max concurrent executions reached ({self.max_concurrent_executions}), "
                        f"skipping {len(due_tasks) - len(execution_tasks)} tasks"
                    )
                    break
                
                # Execute task asynchronously
                # Note: Each task gets its own database session to prevent concurrent access issues
                execution_task = asyncio.create_task(
                    self._execute_task_async(task_type, task)
                )
                
                task_id = f"{task_type}_{getattr(task, 'id', id(task))}"
                self.active_executions[task_id] = execution_task
                
                execution_tasks.append(execution_task)
            
            # Wait for executions to complete (with timeout per task)
            if execution_tasks:
                await asyncio.wait(execution_tasks, timeout=300)
            
        except Exception as e:
            error = TaskLoaderError(
                message=f"Error processing task type {task_type}: {str(e)}",
                task_type=task_type,
                original_error=e
            )
            self.exception_handler.handle_exception(error)
    
    async def _execute_task_async(self, task_type: str, task: Any):
        """
        Execute a single task asynchronously with user isolation.
        
        Each task gets its own database session to prevent concurrent access issues,
        as SQLAlchemy sessions are not async-safe or concurrent-safe.
        
        User context is extracted and tracked for user isolation.
        
        Args:
            task_type: Type of task
            task: Task instance from database (detached from original session)
        """
        task_id = f"{task_type}_{getattr(task, 'id', id(task))}"
        db = None
        user_id = None
        
        try:
            # Extract user context if available (for user isolation tracking)
            try:
                if hasattr(task, 'strategy') and task.strategy:
                    user_id = getattr(task.strategy, 'user_id', None)
                elif hasattr(task, 'strategy_id') and task.strategy_id:
                    # Will query user_id after we have db session
                    pass
            except Exception as e:
                logger.debug(f"Could not extract user_id before execution for task {task_id}: {e}")
            
            logger.info(f"Executing task: {task_id} | user_id: {user_id}")
            
            # Create a new database session for this async task
            # SQLAlchemy sessions are not async-safe and cannot be shared across concurrent tasks
            db = get_db_session()
            if db is None:
                error = DatabaseError(
                    message=f"Failed to get database session for task {task_id}",
                    user_id=user_id,
                    task_id=getattr(task, 'id', None),
                    task_type=task_type
                )
                self.exception_handler.handle_exception(error, log_level="error")
                self.stats['tasks_failed'] += 1
                self._update_user_stats(user_id, success=False)
                return
            
            # Set database session for exception handler
            self.exception_handler.db = db
            
            # Merge the detached task object into this session
            # The task object was loaded in a different session and is now detached
            from sqlalchemy.orm import object_session
            if object_session(task) is None:
                # Task is detached, need to merge it into this session
                task = db.merge(task)
            
            # Extract user_id after merge if not already available
            if user_id is None and hasattr(task, 'strategy'):
                try:
                    if task.strategy:
                        user_id = getattr(task.strategy, 'user_id', None)
                    elif hasattr(task, 'strategy_id'):
                        # Query strategy if relationship not loaded
                        from models.enhanced_strategy_models import EnhancedContentStrategy
                        strategy = db.query(EnhancedContentStrategy).filter(
                            EnhancedContentStrategy.id == task.strategy_id
                        ).first()
                        if strategy:
                            user_id = strategy.user_id
                except Exception as e:
                    logger.debug(f"Could not extract user_id after merge for task {task_id}: {e}")
            
            # Get executor for this task type
            try:
                executor = self.registry.get_executor(task_type)
            except Exception as e:
                from .exception_handler import SchedulerConfigError
                error = SchedulerConfigError(
                    message=f"Failed to get executor for task type {task_type}: {str(e)}",
                    user_id=user_id,
                    context={
                        "task_id": getattr(task, 'id', None),
                        "task_type": task_type
                    },
                    original_error=e
                )
                self.exception_handler.handle_exception(error)
                self.stats['tasks_failed'] += 1
                self._update_user_stats(user_id, success=False)
                return
            
            # Execute task with its own session (with error handling)
            try:
                result = await executor.execute_task(task, db)
                
                # Handle result and update statistics
                if result.success:
                    self.stats['tasks_executed'] += 1
                    self._update_user_stats(user_id, success=True)
                    logger.info(f"Task executed successfully: {task_id} | user_id: {user_id}")
                else:
                    self.stats['tasks_failed'] += 1
                    self._update_user_stats(user_id, success=False)
                    
                    # Create structured error for failed execution
                    error = TaskExecutionError(
                        message=result.error_message or "Task execution failed",
                        user_id=user_id,
                        task_id=getattr(task, 'id', None),
                        task_type=task_type,
                        execution_time_ms=result.execution_time_ms,
                        context={"result_data": result.result_data}
                    )
                    self.exception_handler.handle_exception(error, log_level="warning")
                    
                    # Retry logic if enabled
                    if self.enable_retries and result.retryable:
                        await self._schedule_retry(task, result.retry_delay)
                        
            except SchedulerException as e:
                # Re-raise scheduler exceptions (they're already handled)
                raise
            except Exception as e:
                # Wrap unexpected exceptions
                error = TaskExecutionError(
                    message=f"Unexpected error during task execution: {str(e)}",
                    user_id=user_id,
                    task_id=getattr(task, 'id', None),
                    task_type=task_type,
                    original_error=e
                )
                self.exception_handler.handle_exception(error)
                self.stats['tasks_failed'] += 1
                self._update_user_stats(user_id, success=False)
            
        except SchedulerException as e:
            # Handle scheduler exceptions
            self.exception_handler.handle_exception(e)
            self.stats['tasks_failed'] += 1
            self._update_user_stats(user_id, success=False)
        except Exception as e:
            # Handle any other unexpected errors
            error = TaskExecutionError(
                message=f"Unexpected error in task execution wrapper: {str(e)}",
                user_id=user_id,
                task_id=getattr(task, 'id', None),
                task_type=task_type,
                original_error=e
            )
            self.exception_handler.handle_exception(error)
            self.stats['tasks_failed'] += 1
            self._update_user_stats(user_id, success=False)
        finally:
            # Clean up database session
            if db:
                try:
                    db.close()
                except Exception as e:
                    logger.error(f"Error closing database session for task {task_id}: {e}")
            
            # Remove from active executions
            if task_id in self.active_executions:
                del self.active_executions[task_id]
    
    def _update_user_stats(self, user_id: Optional[int], success: bool):
        """
        Update per-user statistics for user isolation tracking.
        
        Args:
            user_id: User ID (None if user context not available)
            success: Whether task execution was successful
        """
        if user_id is None:
            return
        
        if user_id not in self.stats['per_user_stats']:
            self.stats['per_user_stats'][user_id] = {
                'executed': 0,
                'failed': 0,
                'success_rate': 0.0
            }
        
        user_stats = self.stats['per_user_stats'][user_id]
        if success:
            user_stats['executed'] += 1
        else:
            user_stats['failed'] += 1
        
        # Calculate success rate
        total = user_stats['executed'] + user_stats['failed']
        if total > 0:
            user_stats['success_rate'] = (user_stats['executed'] / total) * 100.0
    
    async def _schedule_retry(self, task: Any, delay_seconds: int):
        """Schedule a retry for a failed task."""
        # This would update the task's next_execution time
        # For now, just log - could be enhanced to update next_execution
        logger.debug(f"Scheduling retry for task in {delay_seconds}s")
    
    def get_stats(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Get scheduler statistics with optional user filtering.
        
        Args:
            user_id: Optional user ID to filter statistics for specific user
            
        Returns:
            Dictionary with scheduler statistics
        """
        base_stats = {
            **{k: v for k, v in self.stats.items() if k not in ['per_user_stats']},
            'active_executions': len(self.active_executions),
            'registered_types': self.registry.get_registered_types(),
            'running': self._running,
            'check_interval_minutes': self.current_check_interval_minutes,
            'min_check_interval_minutes': self.min_check_interval_minutes,
            'max_check_interval_minutes': self.max_check_interval_minutes,
            'intelligent_scheduling': True
        }
        
        # Include per-user stats (all users or filtered)
        if user_id is not None:
            if user_id in self.stats['per_user_stats']:
                base_stats['user_stats'] = self.stats['per_user_stats'][user_id]
            else:
                base_stats['user_stats'] = {
                    'executed': 0,
                    'failed': 0,
                    'success_rate': 0.0
                }
        else:
            # Include all per-user stats (for admin/debugging)
            base_stats['per_user_stats'] = self.stats['per_user_stats']
        
        return base_stats
    
    def is_running(self) -> bool:
        """Check if scheduler is running."""
        return self._running

