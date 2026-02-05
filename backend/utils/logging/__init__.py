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

# Simplified logging system - use working components only
from ..logger_utils import get_service_logger

# Import enhanced features that work
from .middleware_logging import log_api_call, MiddlewareLogger

# Re-export for backward compatibility
__all__ = [
    # Core functions from utils.logger_utils
    'get_service_logger',
    
    # Utility functions
    'log_api_call',
    'MiddlewareLogger'
]
