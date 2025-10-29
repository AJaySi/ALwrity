"""
Structured Logging Configuration for Blog Writer

Configures structured JSON logging with correlation IDs, context tracking,
and performance metrics for the AI Blog Writer system.
"""

import json
import uuid
import time
import sys
from typing import Dict, Any, Optional
from contextvars import ContextVar
from loguru import logger
from datetime import datetime

# Context variables for request tracking
correlation_id: ContextVar[str] = ContextVar('correlation_id', default='')
user_id: ContextVar[str] = ContextVar('user_id', default='')
task_id: ContextVar[str] = ContextVar('task_id', default='')
operation: ContextVar[str] = ContextVar('operation', default='')


class BlogWriterLogger:
    """Enhanced logger for Blog Writer with structured logging and context tracking."""
    
    def __init__(self):
        self._setup_logger()
    
    def _setup_logger(self):
        """Configure loguru with structured JSON output."""
        from utils.logger_utils import get_service_logger
        return get_service_logger("blog_writer")
    
    def _json_formatter(self, record):
        """Format log record as structured JSON."""
        # Extract context variables
        correlation_id_val = correlation_id.get('')
        user_id_val = user_id.get('')
        task_id_val = task_id.get('')
        operation_val = operation.get('')
        
        # Build structured log entry
        log_entry = {
            "timestamp": datetime.fromtimestamp(record["time"].timestamp()).isoformat(),
            "level": record["level"].name,
            "logger": record["name"],
            "function": record["function"],
            "line": record["line"],
            "message": record["message"],
            "correlation_id": correlation_id_val,
            "user_id": user_id_val,
            "task_id": task_id_val,
            "operation": operation_val,
            "module": record["module"],
            "process_id": record["process"].id,
            "thread_id": record["thread"].id
        }
        
        # Add exception info if present
        if record["exception"]:
            log_entry["exception"] = {
                "type": record["exception"].type.__name__,
                "value": str(record["exception"].value),
                "traceback": record["exception"].traceback
            }
        
        # Add extra fields from record
        if record["extra"]:
            log_entry.update(record["extra"])
        
        return json.dumps(log_entry, default=str)
    
    def set_context(
        self, 
        correlation_id_val: Optional[str] = None,
        user_id_val: Optional[str] = None,
        task_id_val: Optional[str] = None,
        operation_val: Optional[str] = None
    ):
        """Set context variables for the current request."""
        if correlation_id_val:
            correlation_id.set(correlation_id_val)
        if user_id_val:
            user_id.set(user_id_val)
        if task_id_val:
            task_id.set(task_id_val)
        if operation_val:
            operation.set(operation_val)
    
    def clear_context(self):
        """Clear all context variables."""
        correlation_id.set('')
        user_id.set('')
        task_id.set('')
        operation.set('')
    
    def generate_correlation_id(self) -> str:
        """Generate a new correlation ID."""
        return str(uuid.uuid4())
    
    def log_operation_start(
        self, 
        operation_name: str, 
        **kwargs
    ):
        """Log the start of an operation with context."""
        logger.info(
            f"Starting {operation_name}",
            extra={
                "operation": operation_name,
                "event_type": "operation_start",
                **kwargs
            }
        )
    
    def log_operation_end(
        self, 
        operation_name: str, 
        duration_ms: float,
        success: bool = True,
        **kwargs
    ):
        """Log the end of an operation with performance metrics."""
        logger.info(
            f"Completed {operation_name} in {duration_ms:.2f}ms",
            extra={
                "operation": operation_name,
                "event_type": "operation_end",
                "duration_ms": duration_ms,
                "success": success,
                **kwargs
            }
        )
    
    def log_api_call(
        self,
        api_name: str,
        endpoint: str,
        duration_ms: float,
        status_code: Optional[int] = None,
        token_usage: Optional[Dict[str, int]] = None,
        **kwargs
    ):
        """Log API call with performance metrics."""
        logger.info(
            f"API call to {api_name}",
            extra={
                "event_type": "api_call",
                "api_name": api_name,
                "endpoint": endpoint,
                "duration_ms": duration_ms,
                "status_code": status_code,
                "token_usage": token_usage,
                **kwargs
            }
        )
    
    def log_error(
        self,
        error: Exception,
        operation: str,
        context: Optional[Dict[str, Any]] = None
    ):
        """Log error with full context."""
        logger.error(
            f"Error in {operation}: {str(error)}",
            extra={
                "event_type": "error",
                "operation": operation,
                "error_type": type(error).__name__,
                "error_message": str(error),
                "context": context or {}
            },
            exc_info=True
        )
    
    def log_performance(
        self,
        metric_name: str,
        value: float,
        unit: str = "ms",
        **kwargs
    ):
        """Log performance metrics."""
        logger.info(
            f"Performance metric: {metric_name} = {value} {unit}",
            extra={
                "event_type": "performance",
                "metric_name": metric_name,
                "value": value,
                "unit": unit,
                **kwargs
            }
        )


# Global logger instance
blog_writer_logger = BlogWriterLogger()


def get_logger(name: str = "blog_writer"):
    """Get a logger instance with the given name."""
    return logger.bind(name=name)


def log_function_call(func_name: str, **kwargs):
    """Decorator to log function calls with timing."""
    def decorator(func):
        async def async_wrapper(*args, **func_kwargs):
            start_time = time.time()
            correlation_id_val = correlation_id.get('')
            
            blog_writer_logger.log_operation_start(
                func_name,
                function=func.__name__,
                correlation_id=correlation_id_val,
                **kwargs
            )
            
            try:
                result = await func(*args, **func_kwargs)
                duration_ms = (time.time() - start_time) * 1000
                
                blog_writer_logger.log_operation_end(
                    func_name,
                    duration_ms,
                    success=True,
                    function=func.__name__,
                    correlation_id=correlation_id_val
                )
                
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                
                blog_writer_logger.log_error(
                    e,
                    func_name,
                    context={
                        "function": func.__name__,
                        "duration_ms": duration_ms,
                        "correlation_id": correlation_id_val
                    }
                )
                raise
        
        def sync_wrapper(*args, **func_kwargs):
            start_time = time.time()
            correlation_id_val = correlation_id.get('')
            
            blog_writer_logger.log_operation_start(
                func_name,
                function=func.__name__,
                correlation_id=correlation_id_val,
                **kwargs
            )
            
            try:
                result = func(*args, **func_kwargs)
                duration_ms = (time.time() - start_time) * 1000
                
                blog_writer_logger.log_operation_end(
                    func_name,
                    duration_ms,
                    success=True,
                    function=func.__name__,
                    correlation_id=correlation_id_val
                )
                
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                
                blog_writer_logger.log_error(
                    e,
                    func_name,
                    context={
                        "function": func.__name__,
                        "duration_ms": duration_ms,
                        "correlation_id": correlation_id_val
                    }
                )
                raise
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator
