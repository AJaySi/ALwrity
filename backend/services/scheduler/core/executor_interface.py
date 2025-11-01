"""
Task Executor Interface
Abstract base class for all task executors.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from sqlalchemy.orm import Session


@dataclass
class TaskExecutionResult:
    """Result of task execution."""
    success: bool
    error_message: Optional[str] = None
    result_data: Optional[Dict[str, Any]] = None
    execution_time_ms: Optional[int] = None
    retryable: bool = True
    retry_delay: int = 300  # seconds
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'success': self.success,
            'error_message': self.error_message,
            'result_data': self.result_data,
            'execution_time_ms': self.execution_time_ms,
            'retryable': self.retryable,
            'retry_delay': self.retry_delay
        }


class TaskExecutor(ABC):
    """
    Abstract base class for task executors.
    
    Each task type must implement this interface to be schedulable.
    """
    
    @abstractmethod
    async def execute_task(self, task: Any, db: Session) -> TaskExecutionResult:
        """
        Execute a task.
        
        Args:
            task: Task instance from database
            db: Database session
            
        Returns:
            TaskExecutionResult with execution details
        """
        pass
    
    @abstractmethod
    def calculate_next_execution(
        self,
        task: Any,
        frequency: str,
        last_execution: Optional[datetime] = None
    ) -> datetime:
        """
        Calculate next execution time based on frequency.
        
        Args:
            task: Task instance
            frequency: Task frequency (e.g., 'Daily', 'Weekly')
            last_execution: Last execution datetime
            
        Returns:
            Next execution datetime
        """
        pass

