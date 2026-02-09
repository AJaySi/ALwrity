"""
Unified Logger Module - Core Component

The main UnifiedLogger class with Loguru integration.
This is the core logging component that provides the interface
for all enhanced logging functionality.
"""

import json
import time
import traceback
import functools
from datetime import datetime
from typing import Dict, Any, Optional, Union, List
from loguru import logger

from .config import SCHEDULER_EVENT_LOG_AVAILABLE, LOG_BASE_DIR


class UnifiedLogger:
    """
    Enhanced unified logger with Loguru integration and dashboard compatibility.
    
    This class provides:
    - Loguru integration with bind(), patch(), and contextualize()
    - Unified log format with service context
    - Dashboard compatibility with SchedulerEventLog
    - Performance monitoring with automatic thresholds
    - Context-based operations grouping
    - Structured file logging for analysis
    """
    
    def __init__(self, service_name: str, db_session=None):
        """
        Initialize unified logger with Loguru integration.
        
        Args:
            service_name: Name of the service (e.g., "Scheduler", "GSCInsights")
            db_session: Database session for SchedulerEventLog compatibility
        """
        self.service_name = service_name
        self.db_session = db_session
        
        # Use Loguru's bind() to add service context to all log records
        self.logger = logger.bind(service=service_name)
        
        # Apply performance monitoring patch to this logger instance
        self.apply_performance_patch()
    
    def apply_performance_patch(self):
        """Apply performance monitoring patch to this logger instance."""
        def performance_patcher(record):
            """Add performance monitoring to log records."""
            # Add performance warnings for slow operations
            execution_time = record["extra"].get("execution_time_ms", 0)
            if execution_time > 5000:  # 5 seconds
                record["extra"]["performance_warning"] = "SLOW_OPERATION"
            elif execution_time > 2000:  # 2 seconds
                record["extra"]["performance_warning"] = "MODERATE_SLOW"
        
        # Apply patch only to this logger instance
        self.logger = self.logger.patch(performance_patcher)
    
    def debug(self, message: str, **context):
        """Debug level logging (only in verbose mode) using Loguru"""
        # Use Loguru's bind() to add context to this specific call
        bound_logger = self.logger.bind(**context, structured_logging=False)
        bound_logger.debug(message)
    
    def info(self, message: str, create_event_log: bool = False, event_type: str = None, **context):
        """Info level logging with optional SchedulerEventLog creation using Loguru"""
        # Use Loguru's bind() to add context to this specific call
        bound_logger = self.logger.bind(**context, structured_logging=False)
        bound_logger.info(message)
        
        if create_event_log and event_type and SCHEDULER_EVENT_LOG_AVAILABLE:
            self._create_scheduler_event_log(event_type, **context)
    
    def warning(self, message: str, **context):
        """Warning level logging using Loguru with automatic multi-line preservation"""
        bound_logger = self.logger.bind(**context, structured_logging=False)
        
        # Check if message contains multiple lines or tree structure
        if '\n' in message or any(char in message for char in ['├', '└', '│', '─']):
            # Multi-line message - log each line separately to preserve formatting
            lines = message.split('\n') if isinstance(message, str) else message
            for line in lines:
                if line.strip():  # Only log non-empty lines
                    bound_logger.warning(line)
        else:
            # Single line message - log normally
            bound_logger.warning(message)
    
    def error(self, message: str, exc_info: bool = True, **context):
        """Error level logging with exception details using Loguru"""
        bound_logger = self.logger.bind(**context, structured_logging=False)
        bound_logger.error(message, exc_info=exc_info)
    
    def critical(self, message: str, create_event_log: bool = False, event_type: str = None, **context):
        """Critical level logging with optional SchedulerEventLog creation using Loguru"""
        bound_logger = self.logger.bind(**context, structured_logging=False)
        bound_logger.critical(message)
        
        if create_event_log and event_type and SCHEDULER_EVENT_LOG_AVAILABLE:
            self._create_scheduler_event_log(event_type, **context)
    
    def log_critical_alert(self, message: str, error_details: Dict[str, Any] = None):
        """Log critical alerts with enhanced context and alerting."""
        alert_context = {
            "alert_type": "critical_error",
            "service": self.service_name,
            "timestamp": datetime.now().isoformat(),
            "error_details": error_details or {}
        }
        
        self.critical(
            f"🚨 CRITICAL ALERT: {message}",
            **alert_context
        )
        
        # Additional alerting mechanisms could be added here
        # (email, Slack, PagerDuty, etc.)
    
    def _create_scheduler_event_log(self, event_type: str, **context):
        """Create SchedulerEventLog entry for dashboard compatibility."""
        if not SCHEDULER_EVENT_LOG_AVAILABLE or not self.db_session:
            return
            
        try:
            from models.scheduler_models import SchedulerEventLog
            
            event_log = SchedulerEventLog(
                event_type=event_type,
                status="completed",
                details=json.dumps({
                    "service": self.service_name,
                    "timestamp": datetime.now().isoformat(),
                    "context": context
                })
            )
            
            self.db_session.add(event_log)
            self.db_session.commit()
            
        except Exception as e:
            # Don't let logging errors break the application
            logger.error(f"Failed to create SchedulerEventLog: {e}", exc_info=False)
    
    def log_api_call(self, method: str, endpoint: str, status_code: int, 
                    duration_ms: int, user_id: str = None, **context):
        """Log API call with structured context."""
        api_context = {
            "log_type": "api",
            "method": method,
            "endpoint": endpoint,
            "status_code": status_code,
            "duration_ms": duration_ms,
            "user_id": user_id,
            **context
        }
        
        self.info(
            f"API {method} {endpoint} - {status_code} ({duration_ms}ms)",
            **api_context
        )
    
    def log_performance(self, operation: str, duration_ms: int, **context):
        """Log performance metrics with automatic threshold warnings."""
        perf_context = {
            "operation": operation,
            "duration_ms": duration_ms,
            **context
        }
        
        # Add performance warnings
        if duration_ms > 5000:  # 5 seconds
            perf_warning = "SLOW_OPERATION"
        elif duration_ms > 2000:  # 2 seconds
            perf_warning = "MODERATE_SLOW"
        else:
            perf_warning = None
            
        if perf_warning:
            perf_context["performance_warning"] = perf_warning
            self.warning(
                f"Performance: {operation} took {duration_ms}ms",
                **perf_context
            )
        else:
            self.info(
                f"Performance: {operation} took {duration_ms}ms",
                **perf_context
            )
    
    def bind_context(self, **context):
        """Return a new logger bound with additional context."""
        return self.logger.bind(**context)
    
    def context(self, **context):
        """Context manager for temporary context binding."""
        return _ContextManager(self, context)


class _ContextManager:
    """Context manager for temporary logger context binding."""
    
    def __init__(self, unified_logger: UnifiedLogger, context: Dict[str, Any]):
        self.unified_logger = unified_logger
        self.context = context
        self.bound_logger = None
    
    def __enter__(self):
        self.bound_logger = self.unified_logger.bind_context(**self.context)
        return self.bound_logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Context is automatically cleaned up when exiting
        pass


def get_logger(service_name: str, db_session=None, format_string: str = None):
    """
    Get a configured unified logger instance.
    
    Args:
        service_name: Name of the service
        db_session: Database session for SchedulerEventLog compatibility
        format_string: Custom format string (optional)
        
    Returns:
        UnifiedLogger instance
    """
    from .config import safe_logger_config
    
    if format_string:
        safe_logger_config(format_string)
    
    return UnifiedLogger(service_name, db_session)


def get_service_logger(service_name: str, format_string: str = None):
    """Backward compatibility function"""
    return get_logger(service_name, None, format_string)
