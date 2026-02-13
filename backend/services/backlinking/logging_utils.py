"""
Logging utilities for the AI Backlinking service.

Provides structured logging with context, performance monitoring,
and configurable log levels for different components.
"""

import time
from typing import Dict, Any, Optional, Callable
from contextlib import contextmanager
from functools import wraps
from loguru import logger

from .config import get_config


class BacklinkingLogger:
    """
    Structured logger for backlinking service operations.

    Provides contextual logging with performance metrics,
    error tracking, and configurable verbosity.
    """

    def __init__(self, service_name: str):
        self.service_name = service_name
        self.config = get_config()

    def _get_log_level(self) -> str:
        """Get the appropriate log level based on configuration."""
        return self.config.log_level.upper()

    def _should_log(self, level: str) -> bool:
        """Check if a log level should be output based on configuration."""
        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        config_level = self._get_log_level()

        if config_level not in levels:
            return True  # Default to logging everything

        return levels.index(level) >= levels.index(config_level)

    def debug(self, message: str, **context: Any) -> None:
        """Log debug message with context."""
        if self._should_log("DEBUG"):
            logger.debug(f"[{self.service_name}] {message}", **context)

    def info(self, message: str, **context: Any) -> None:
        """Log info message with context."""
        if self._should_log("INFO"):
            logger.info(f"[{self.service_name}] {message}", **context)

    def warning(self, message: str, **context: Any) -> None:
        """Log warning message with context."""
        if self._should_log("WARNING"):
            logger.warning(f"[{self.service_name}] {message}", **context)

    def error(self, message: str, error: Optional[Exception] = None, **context: Any) -> None:
        """Log error message with context and exception details."""
        if self._should_log("ERROR"):
            if error:
                context["error_type"] = type(error).__name__
                context["error_message"] = str(error)
            logger.error(f"[{self.service_name}] {message}", **context)

    def critical(self, message: str, error: Optional[Exception] = None, **context: Any) -> None:
        """Log critical message with context and exception details."""
        if self._should_log("CRITICAL"):
            if error:
                context["error_type"] = type(error).__name__
                context["error_message"] = str(error)
            logger.critical(f"[{self.service_name}] {message}", **context)

    def operation_start(self, operation: str, **context: Any) -> None:
        """Log the start of an operation."""
        self.info(f"Starting operation: {operation}", operation=operation, **context)

    def operation_end(self, operation: str, duration: Optional[float] = None, **context: Any) -> None:
        """Log the end of an operation."""
        if duration is not None:
            context["duration_seconds"] = round(duration, 3)
        self.info(f"Completed operation: {operation}", operation=operation, **context)

    def operation_error(self, operation: str, error: Exception, **context: Any) -> None:
        """Log an operation error."""
        self.error(
            f"Operation failed: {operation}",
            error=error,
            operation=operation,
            **context
        )

    def metric(self, name: str, value: Any, **context: Any) -> None:
        """Log a metric value."""
        if self.config.enable_metrics:
            self.info(f"Metric: {name} = {value}", metric=name, value=value, **context)

    @contextmanager
    def operation_context(self, operation: str, **context: Any):
        """
        Context manager for logging operation start/end with timing.

        Usage:
            with logger.operation_context("create_campaign", user_id=123):
                # Do work here
                pass
        """
        start_time = time.time()
        self.operation_start(operation, **context)

        try:
            yield
            duration = time.time() - start_time
            self.operation_end(operation, duration, **context)
        except Exception as e:
            duration = time.time() - start_time
            self.operation_error(operation, e, duration=duration, **context)
            raise


def log_operation(operation_name: Optional[str] = None, service_name: str = "backlinking"):
    """
    Decorator for logging method operations with timing.

    Usage:
        @log_operation("create_campaign")
        async def create_campaign(self, ...):
            pass
    """
    def decorator(func: Callable) -> Callable:
        nonlocal operation_name
        if operation_name is None:
            operation_name = func.__name__

        logger_instance = BacklinkingLogger(service_name)

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            method_name = f"{args[0].__class__.__name__}.{operation_name}" if args else operation_name

            with logger_instance.operation_context(method_name):
                return await func(*args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            method_name = f"{args[0].__class__.__name__}.{operation_name}" if args else operation_name

            with logger_instance.operation_context(method_name):
                return func(*args, **kwargs)

        if hasattr(func, '__call__'):
            import inspect
            if inspect.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
        else:
            return func

    return decorator


def create_service_logger(service_name: str) -> BacklinkingLogger:
    """
    Create a logger instance for a specific service.

    Args:
        service_name: Name of the service (e.g., "backlinking", "scraping", "email")

    Returns:
        BacklinkingLogger: Configured logger instance
    """
    return BacklinkingLogger(service_name)


# Global logger instances for each service
backlinking_logger = create_service_logger("backlinking")
scraping_logger = create_service_logger("scraping")
email_logger = create_service_logger("email")
campaign_logger = create_service_logger("campaign")


def log_campaign_action(campaign_id: str, action: str, **context: Any) -> None:
    """Log a campaign-related action."""
    campaign_logger.info(
        f"Campaign action: {action}",
        campaign_id=campaign_id,
        action=action,
        **context
    )


def log_email_action(email_address: str, action: str, campaign_id: str = None, **context: Any) -> None:
    """Log an email-related action."""
    email_logger.info(
        f"Email action: {action}",
        email=email_address,
        campaign_id=campaign_id,
        action=action,
        **context
    )


def log_scraping_action(url: str, action: str, **context: Any) -> None:
    """Log a scraping-related action."""
    scraping_logger.info(
        f"Scraping action: {action}",
        url=url,
        action=action,
        **context
    )


def log_performance_metric(metric_name: str, value: Any, **context: Any) -> None:
    """Log a performance metric."""
    backlinking_logger.metric(metric_name, value, **context)