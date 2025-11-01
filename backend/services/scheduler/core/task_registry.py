"""
Task Registry
Manages registration of task executors and loaders.
"""

import logging
from typing import Dict, Callable, List, Any
from sqlalchemy.orm import Session

from .executor_interface import TaskExecutor

logger = logging.getLogger(__name__)


class TaskRegistry:
    """Registry for task executors and loaders."""
    
    def __init__(self):
        self.executors: Dict[str, TaskExecutor] = {}
        self.task_loaders: Dict[str, Callable[[Session], List[Any]]] = {}
    
    def register(
        self,
        task_type: str,
        executor: TaskExecutor,
        task_loader: Callable[[Session], List[Any]]
    ):
        """
        Register a task executor and loader.
        
        Args:
            task_type: Unique identifier for task type
            executor: TaskExecutor instance
            task_loader: Function that loads due tasks from database
        """
        if task_type in self.executors:
            logger.warning(f"Overwriting existing executor for task type: {task_type}")
        
        self.executors[task_type] = executor
        self.task_loaders[task_type] = task_loader
        
        logger.info(f"Registered task type: {task_type}")
    
    def get_executor(self, task_type: str) -> TaskExecutor:
        """Get executor for task type."""
        if task_type not in self.executors:
            raise ValueError(f"No executor registered for task type: {task_type}")
        return self.executors[task_type]
    
    def get_task_loader(self, task_type: str) -> Callable[[Session], List[Any]]:
        """Get task loader for task type."""
        if task_type not in self.task_loaders:
            raise ValueError(f"No task loader registered for task type: {task_type}")
        return self.task_loaders[task_type]
    
    def get_registered_types(self) -> List[str]:
        """Get list of registered task types."""
        return list(self.executors.keys())

