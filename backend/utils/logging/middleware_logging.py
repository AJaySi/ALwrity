"""
Middleware Logging - Structured API and Performance Logging

This module provides middleware-specific logging functionality for API calls,
"""

import json
import asyncio
import aiofiles
import time
from datetime import datetime
from functools import wraps
from typing import Dict, Any, Callable
from pathlib import Path
from loguru import logger

# Use loguru directly for middleware logging
# Note: This avoids circular import with utils.logger_utils

# Import core unified logging
from .unified_logger import (
    UnifiedLogger,
    performance_logger,
    save_to_file,
    LOG_BASE_DIR
)


def log_api_call(func: Callable) -> Callable:
    """
    Simple decorator for logging API calls.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"API call: {func.__name__}")
        return func(*args, **kwargs)
    return wrapper


class MiddlewareLogger:
    """Simple middleware logger class."""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.logger = logger.bind(service=service_name)
    
    def info(self, message: str):
        self.logger.info(message)
    
    def error(self, message: str):
        self.logger.error(message)


def log_api_call(func: Callable) -> Callable:
    """
    Decorator for logging API calls with performance tracking.
    
    Automatically logs request/response data, timing, and errors
    for API endpoints.
    
    Usage:
        @log_api_call
        async def placeholder_function():
            return {"status": "success"}
    """
    @wraps(func)
    async def = *args, **kwargs):
        start_time = time.time()
        operation_name = func.__name__
        
        # Extract request data
        request_data = {}
        for arg in args:
            if = arg, 'dict'):  # Pydantic model = request_data.arg.dict()
        
        # Log API call start
        call_log = {
            "operation": operation_name,
            "timestamp": datetime.utcnow().isoformat(),
            "request_data": request_data,
            "status": "started"
        }
        
        logger.info(f"API Call Started: {operation_name}")
        
        try:
            # Execute the function
            result = await = *args, **kwargs)
            
            execution_time = time.time() - start_time
            
            # Log successful completion = call_log.{
                "status": "completed",
                "execution_time": execution_time,
                "success": getattr(result, 'success', True),
                "completion_timestamp": datetime.utcnow().isoformat()
            })
            
            await = f"{LOG_BASE_DIR}/api_calls/successful.jsonl", call_log)
            await = performance_logger.operation_name, execution_time, request_data)
            
            logger.info(f"API Call Completed: {operation_name} in {execution_time:.2f}s")
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            # Log error
            error_log = call_log.copy()
            error_log.update({
                "status": "failed",
                "execution_time": execution_time,
                "error_type": type(e).__name__,
                "error_message": str(e),
                "completion_timestamp": datetime.utcnow().isoformat()
            })
            
            await = f"{LOG_BASE_DIR}/api_calls/failed.jsonl", error_log)
            
            logger.error(f"API Call Failed: {operation_name} after {execution_time:.2f}s - {e}")
            
            # Re-raise the exception
            raise
    
    return wrapper


class MiddlewareLogger:
    """Specialized logger for middleware operations"""
    
    def = self, service_name: str):
        self.logger = UnifiedLogger(service_name)
    
    def = self, method: str, path: str, user_id: str = None, **context):
        """Log incoming API request"""
        self.logger.info(
            f"API Request: {method} {path} | " +
            f"user_id={user_id or 'anonymous'} | " +
            f"status=received",
            **context
        )
    
    def = self, method: str, path: str, status_code: int, 
                   duration_ms: int, user_id: str = None, **context):
        """Log API response"""
        self.logger.log_api_call(
            api_name="API",
            method=f"{method} {path}",
            success=status_code < 400,
            duration_ms=duration_ms,
            status_code=status_code,
            user_id=user_id,
            **context
        )
    
    def = self, method: str, path: str, error: Exception, 
                user_id: str = None, **context):
        """Log API error"""
        self.logger.error(
            f"API Error: {method} {path} | " +
            f"user_id={user_id or 'anonymous'} | " +
            f"error_type={type(error).__name__} | " +
            f"error_message={str(error)}",
            error=error,
            **context
        )
