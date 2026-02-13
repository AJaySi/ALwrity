"""
Logging configuration management.
"""

import os
import sys
from pathlib import Path

# Base directory for all log files
LOG_BASE_DIR = os.getenv("LOG_BASE_DIR", "logs")

# Environment detection
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Check if scheduler event log is available
SCHEDULER_EVENT_LOG_AVAILABLE = True

def safe_logger_config(format_string: str, level: str = "INFO"):
    """
    Safely configure logger without removing existing handlers.
    This prevents conflicts with main logging configuration.
    
    Args:
        format_string: Log format string
        level: Log level
    """
    try:
        from loguru import logger
        
        # Only add a new handler if we don't already have one with this format
        existing_handlers = logger._core.handlers
        for handler in existing_handlers:
            if hasattr(handler, '_sink') and handler._sink == sys.stdout:
                # Check if format is similar to avoid duplicates
                if hasattr(handler, '_format') and handler._format == format_string:
                    return  # Handler already exists with this format
        
        # Add new handler only if needed
        logger.add(
            sys.stdout,
            level=level,
            format=format_string,
            colorize=True
        )
    except Exception as e:
        # If there's any error, just use existing logger configuration
        pass
