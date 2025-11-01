"""
Monitoring Task Executor
Handles execution of content strategy monitoring tasks.
"""

import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from ..core.executor_interface import TaskExecutor, TaskExecutionResult
from ..core.exception_handler import TaskExecutionError, DatabaseError, SchedulerExceptionHandler
from ..utils.frequency_calculator import calculate_next_execution
from models.monitoring_models import MonitoringTask, TaskExecutionLog
from models.enhanced_strategy_models import EnhancedContentStrategy
from utils.logger_utils import get_service_logger

logger = get_service_logger("monitoring_task_executor")


class MonitoringTaskExecutor(TaskExecutor):
    """
    Executor for content strategy monitoring tasks.
    
    Handles:
    - ALwrity tasks (automated execution)
    - Human tasks (notifications/queuing)
    """
    
    def __init__(self):
        self.logger = logger
        self.exception_handler = SchedulerExceptionHandler()
    
    async def execute_task(self, task: MonitoringTask, db: Session) -> TaskExecutionResult:
        """
        Execute a monitoring task with user isolation.
        
        Args:
            task: MonitoringTask instance (with strategy relationship loaded)
            db: Database session
            
        Returns:
            TaskExecutionResult
        """
        start_time = time.time()
        
        # Extract user_id from strategy relationship for user isolation
        user_id = None
        try:
            if task.strategy and hasattr(task.strategy, 'user_id'):
                user_id = task.strategy.user_id
            elif task.strategy_id:
                # Fallback: query strategy if relationship not loaded
                strategy = db.query(EnhancedContentStrategy).filter(
                    EnhancedContentStrategy.id == task.strategy_id
                ).first()
                if strategy:
                    user_id = strategy.user_id
        except Exception as e:
            self.logger.warning(f"Could not extract user_id for task {task.id}: {e}")
        
        try:
            self.logger.info(
                f"Executing monitoring task: {task.id} | "
                f"user_id: {user_id} | "
                f"assignee: {task.assignee} | "
                f"frequency: {task.frequency}"
            )
            
            # Create execution log with user_id for user isolation tracking
            execution_log = TaskExecutionLog(
                task_id=task.id,
                user_id=user_id,
                execution_date=datetime.utcnow(),
                status='running'
            )
            db.add(execution_log)
            db.flush()
            
            # Execute based on assignee
            if task.assignee == 'ALwrity':
                result = await self._execute_alwrity_task(task, db)
            else:
                result = await self._execute_human_task(task, db)
            
            # Update execution log
            execution_time_ms = int((time.time() - start_time) * 1000)
            execution_log.status = 'success' if result.success else 'failed'
            execution_log.result_data = result.result_data
            execution_log.error_message = result.error_message
            execution_log.execution_time_ms = execution_time_ms
            
            # Update task
            task.last_executed = datetime.utcnow()
            task.next_execution = self.calculate_next_execution(
                task,
                task.frequency,
                task.last_executed
            )
            
            if result.success:
                task.status = 'completed'
            else:
                task.status = 'failed'
            
            db.commit()
            
            return result
            
        except Exception as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            # Set database session for exception handler
            self.exception_handler.db = db
            
            # Create structured error
            error = TaskExecutionError(
                message=f"Error executing monitoring task {task.id}: {str(e)}",
                user_id=user_id,
                task_id=task.id,
                task_type="monitoring_task",
                execution_time_ms=execution_time_ms,
                context={
                    "assignee": task.assignee,
                    "frequency": task.frequency,
                    "component": task.component_name
                },
                original_error=e
            )
            
            # Handle exception with structured logging
            self.exception_handler.handle_exception(error)
            
            # Update execution log with error (include user_id for isolation)
            try:
                execution_log = TaskExecutionLog(
                    task_id=task.id,
                    user_id=user_id,
                    execution_date=datetime.utcnow(),
                    status='failed',
                    error_message=str(e),
                    execution_time_ms=execution_time_ms,
                    result_data={
                        "error_type": error.error_type.value,
                        "severity": error.severity.value,
                        "context": error.context
                    }
                )
                db.add(execution_log)
                
                task.status = 'failed'
                task.last_executed = datetime.utcnow()
                
                db.commit()
            except Exception as commit_error:
                db_error = DatabaseError(
                    message=f"Error saving execution log: {str(commit_error)}",
                    user_id=user_id,
                    task_id=task.id,
                    original_error=commit_error
                )
                self.exception_handler.handle_exception(db_error)
                db.rollback()
            
            return TaskExecutionResult(
                success=False,
                error_message=str(e),
                execution_time_ms=execution_time_ms,
                retryable=True,
                retry_delay=300
            )
    
    async def _execute_alwrity_task(self, task: MonitoringTask, db: Session) -> TaskExecutionResult:
        """
        Execute an ALwrity (automated) monitoring task.
        
        This is where the actual monitoring logic would go.
        For now, we'll implement a placeholder that can be extended.
        """
        try:
            self.logger.info(f"Executing ALwrity task: {task.task_title}")
            
            # TODO: Implement actual monitoring logic based on:
            # - task.metric
            # - task.measurement_method
            # - task.success_criteria
            # - task.alert_threshold
            
            # Placeholder: Simulate task execution
            result_data = {
                'metric_value': 0,
                'status': 'measured',
                'message': f"Task {task.task_title} executed successfully",
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return TaskExecutionResult(
                success=True,
                result_data=result_data
            )
            
        except Exception as e:
            self.logger.error(f"Error in ALwrity task execution: {e}")
            return TaskExecutionResult(
                success=False,
                error_message=str(e),
                retryable=True
            )
    
    async def _execute_human_task(self, task: MonitoringTask, db: Session) -> TaskExecutionResult:
        """
        Execute a Human monitoring task (notification/queuing).
        
        For human tasks, we don't execute the task directly,
        but rather queue it for human review or send notifications.
        """
        try:
            self.logger.info(f"Queuing human task: {task.task_title}")
            
            # TODO: Implement notification/queuing system:
            # - Send email notification
            # - Add to user's task queue
            # - Create in-app notification
            
            result_data = {
                'status': 'queued',
                'message': f"Task {task.task_title} queued for human review",
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return TaskExecutionResult(
                success=True,
                result_data=result_data
            )
            
        except Exception as e:
            self.logger.error(f"Error queuing human task: {e}")
            return TaskExecutionResult(
                success=False,
                error_message=str(e),
                retryable=True
            )
    
    def calculate_next_execution(
        self,
        task: MonitoringTask,
        frequency: str,
        last_execution: Optional[datetime] = None
    ) -> datetime:
        """
        Calculate next execution time based on frequency.
        
        Args:
            task: MonitoringTask instance
            frequency: Frequency string (Daily, Weekly, Monthly, Quarterly)
            last_execution: Last execution datetime (defaults to now)
            
        Returns:
            Next execution datetime
        """
        return calculate_next_execution(
            frequency=frequency,
            base_time=last_execution or datetime.utcnow()
        )

