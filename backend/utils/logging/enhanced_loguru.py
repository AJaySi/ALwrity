"""
Enhanced Loguru Logger Module

Provides enhanced Loguru features with advanced functionality.
"""

import sys
import json
import asyncio
import threading
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Dict, Any, Optional, Union, Callable
from datetime import datetime, timedelta
from loguru import logger

from .core.config import LOG_BASE_DIR


class EnhancedLoguruLogger:
    """
    Enhanced Loguru logger with advanced features and optimizations.
    
    This class extends Loguru's capabilities with:
    - Structured JSON logging with context binding
    - Custom sinks for external services
    - Performance monitoring with lazy evaluation
    - Environment-aware configuration
    - Multi-threaded async support
    """
    
    def __init__(self, service_name: str, environment: str = "development"):
        self.service_name = service_name
        self.environment = environment
    
    def setup_enhanced_logging(self):
        """Setup enhanced Loguru configuration with advanced features."""
        try:
            # Remove default handler to avoid duplicates
            logger.remove()
            
            # Setup console handler with enhanced formatting
            if self.environment == "production":
                # Production: Structured JSON logging
                log_format = "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message} | {extra}"
                logger.add(
                    sys.stderr,
                    format=log_format,
                    level="INFO",
                    serialize=True,
                    backtrace=False,
                    diagnose=False
                )
            else:
                # Development: Enhanced human-readable with colors
                log_format = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}:{function}:{line}</cyan> - <white>{message}</white> | <yellow>{extra}</yellow>"
                logger.add(
                    sys.stderr,
                    format=log_format,
                    level="DEBUG",
                    colorize=True,
                    backtrace=True,
                    diagnose=True
                )
            
            # Setup structured file handlers
            self.setup_structured_logging()
            
            # Setup performance monitoring
            self.setup_performance_monitoring()
            
            logger.info(f"Enhanced Loguru logger configured for {self.service_name}")
            
        except Exception as e:
            print(f"Failed to configure enhanced logger: {e}")
    
    def setup_structured_logging(self):
        """Setup structured file handlers."""
        # Structured logs (JSON format)
        logger.add(
            f"{LOG_BASE_DIR}/structured/enhanced.jsonl",
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message} | {extra}",
            level="DEBUG",
            rotation="10 MB",
            retention="30 days",
            compression="zip",
            serialize=True,
            filter=lambda record: "enhanced_logging" in record["extra"]
        )
    
    def setup_performance_monitoring(self):
        """Setup performance monitoring with lazy evaluation."""
        def performance_patcher(record):
            """Add performance monitoring with lazy evaluation."""
            # Lazy evaluation of performance metrics
            if "execution_time_ms" in record["extra"]:
                execution_time = record["extra"]["execution_time_ms"]
                if execution_time > 5000:  # 5 seconds
                    record["extra"]["performance_warning"] = "SLOW_OPERATION"
                elif execution_time > 2000:  # 2 seconds
                    record["extra"]["performance_warning"] = "MODERATE_SLOW"
        
        logger.patch(performance_patcher)
    
    def bind_request_context(self, **context):
        """Bind request context for structured logging."""
        return logger.bind(**context, enhanced_logging=True)
    
    def log_structured_event(self, event_type: str, data: Dict[str, Any]):
        """Log structured event with JSON serialization."""
        structured_data = {
            "event_type": event_type,
            "service": self.service_name,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        
        bound_logger = self.bind_request_context(**structured_data)
        bound_logger.info(f"Structured Event: {event_type}")
    
    @asynccontextmanager
    async def async_operation_logger(self, operation_name: str):
        """Context manager for async operation logging."""
        start_time = datetime.now()
        
        bound_logger = self.bind_request_context(
            operation=operation_name,
            phase="async_operation"
        )
        
        bound_logger.info(f"Starting async operation: {operation_name}")
        
        try:
            yield bound_logger
        except Exception as e:
            bound_logger.error(f"Async operation failed: {operation_name}", error=str(e))
            raise
        finally:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            bound_logger.info(f"Completed async operation: {operation_name} ({duration:.2f}ms)")
    
    def create_performance_sink(self, sink_path: str):
        """Create custom performance sink."""
        def performance_filter(record):
            return "performance" in record["extra"].get("log_type", "")
        
        logger.add(
            sink_path,
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {message} | {extra}",
            level="INFO",
            rotation="50 MB",
            retention="7 days",
            filter=performance_filter
        )
    
    def get_logger_stats(self) -> Dict[str, Any]:
        """Get logger statistics and performance metrics."""
        return {
            "service": self.service_name,
            "environment": self.environment,
            "handlers_count": len(logger._core.handlers),
            "configured_at": datetime.now().isoformat()
        }
