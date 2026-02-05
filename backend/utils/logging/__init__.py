"""
Enhanced Unified Logging System - Modular Architecture

This package provides a comprehensive, modular logging system that integrates
with Loguru while maintaining backward compatibility and providing enhanced features.

Key Features:
- Modular architecture for maintainability
- Loguru integration with = ), patch(), and = )
- Unified log format with service context
- Dashboard compatibility with SchedulerEventLog
- Performance monitoring with automatic thresholds
- Context-based operations grouping
- Structured file logging for analysis
- Backward compatibility with existing code

Architecture:
- core/: Core logging components
  - unified_logger.py: Main UnifiedLogger class
  - context_logger.py: Context-based operations logging
  - performance_logger.py: Performance monitoring
  - structured_logger.py: Structured file logging
  - config.py: Configuration management
  - utils.py: Utility functions and decorators
- logger_utils.py: Backward compatibility layer
- enhanced_loguru.py: Enhanced Loguru features
- middleware_logging.py: Middleware-specific logging
"""

# Import core components
from .core import (
    UnifiedLogger,
    get_logger,
    get_service_logger,
    ContextLogger,
    PerformanceLogger,
    StructuredLogger,
    safe_logger_config,
    log_execution_time,
    save_to_file,
    performance_logger,
    structured_logger
)

# Import enhanced features
from .enhanced_loguru import EnhancedLoguruLogger
from .middleware_logging import log_api_call, MiddlewareLogger

# Re-export for backward compatibility
__all__ = [
    # Core functions
    'get_logger',
    'get_service_logger',
    'safe_logger_config',
    'log_execution_time',
    
    # Core classes
    'UnifiedLogger',
    'ContextLogger',
    'PerformanceLogger',
    'StructuredLogger',
    'EnhancedLoguruLogger',
    'MiddlewareLogger',
    
    # Global instances
    'performance_logger',
    'structured_logger',
    
    # Utility functions
    'save_to_file',
    'log_api_call'
]
