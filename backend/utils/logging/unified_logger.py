"""
Unified Logging System - Modular Interface

This module provides a clean interface to the modular logging system.
All functionality is now organized in the core/ subdirectory for better maintainability.

Architecture:
- core/unified_logger.py: Main UnifiedLogger class
- core/context_logger.py: Context-based operations logging
- core/performance_logger.py: Performance monitoring
- core/structured_logger.py: Structured file logging
- core/config.py: Configuration management
- core/utils.py: Utility functions and decorators
"""

# Import all functionality from the modular core
from .core.unified_logger import (
    UnifiedLogger,
    get_logger,
    get_service_logger
)

from .core.context_logger import ContextLogger
from .core.performance_logger import PerformanceLogger, performance_logger
from .core.structured_logger import StructuredLogger, structured_logger
from .core.config import safe_logger_config, LOG_BASE_DIR, ENVIRONMENT, SCHEDULER_EVENT_LOG_AVAILABLE
from .core.utils import log_execution_time, save_to_file

# Import enhanced features
from .enhanced_loguru import EnhancedLoguruLogger

# Export all public symbols
__all__ = [
    # Core classes
    'UnifiedLogger',
    'ContextLogger', 
    'PerformanceLogger',
    'StructuredLogger',
    'EnhancedLoguruLogger',
    
    # Core functions
    'get_logger',
    'get_service_logger',
    'safe_logger_config',
    'log_execution_time',
    'save_to_file',
    
    # Global instances
    'performance_logger',
    'structured_logger',
    
    # Configuration
    'LOG_BASE_DIR',
    'ENVIRONMENT',
    'SCHEDULER_EVENT_LOG_AVAILABLE'
]
