"""
Enhanced Unified Logging System - Modular Architecture

This package provides a comprehensive, modular logging system that integrates
with Loguru while maintaining backward compatibility and providing enhanced features.

Key Features:
- Modular architecture for maintainability
- Loguru integration with bind(), patch(), and contextualize()
- Unified log format with service context
- Dashboard compatibility with SchedulerEventLog
- Performance monitoring with automatic thresholds
- Context-based operations grouping
- Structured file logging for analysis
- Backward compatibility with existing code
- Gradual migration support from direct loguru imports

Architecture:
- core/: Core logging components
  - unified_logger.py: Main UnifiedLogger class
  - context_logger.py: Context-based operations logging
  - performance_logger.py: Performance monitoring
  - structured_logger.py: Structured file logging
  - config.py: Configuration management
  - utils.py: Utility functions and decorators
  - enhanced_loguru.py: Enhanced Loguru features
  - migration_helpers.py: Migration support utilities
- logger_utils.py: Backward compatibility layer
- middleware_logging.py: Middleware-specific logging
"""

# Core unified logging system
from .core.unified_logger import get_logger as _get_unified_logger, get_service_logger as _get_service_logger
from .enhanced_loguru import EnhancedLoguruLogger

# Migration support
import os
from typing import Dict, Any

def get_migration_status() -> Dict[str, Any]:
    """Get current migration status across all modules"""
    return {
        "migration_enabled": os.getenv("LOGGING_MIGRATION_ENABLED", "false").lower() == "true",
        "migration_mode": os.getenv("LOGGING_MIGRATION_MODE", "gradual"),
        "migration_target": os.getenv("LOGGING_MIGRATION_TARGET", ""),
    }

def log_migration_progress(module: str, status: str, details: str = None):
    """Log migration progress for monitoring"""
    from loguru import logger
    logger.info(f"🔄 Migration [{module}]: {status} - {details}")

# Main entry point with migration support
def get_logger(service_name: str, migration_mode: bool = False):
    """
    Main entry point with migration support.
    
    Args:
        service_name: Name of the service
        migration_mode: Whether to use unified logging system
        
    Returns:
        Logger instance (unified or fallback)
    """
    migration_status = get_migration_status()
    
    if migration_mode or migration_status["migration_enabled"]:
        # Use unified logging system
        return _get_unified_logger(service_name)
    else:
        # Fall back to direct loguru for existing code
        from loguru import logger
        return logger.bind(service=service_name)

# Service logger function (backward compatibility)
def get_service_logger(service_name: str, format_string: str = None):
    """Get service logger with backward compatibility."""
    return _get_service_logger(service_name, None, format_string)

# Enhanced features
def get_enhanced_logger(service_name: str):
    """Get enhanced logger with advanced features"""
    return EnhancedLoguruLogger(service_name)

# Re-export for backward compatibility
__all__ = [
    # Core functions
    'get_logger',
    'get_service_logger',
    'get_enhanced_logger',
    
    # Migration support
    'get_migration_status',
    'log_migration_progress',
    
    # Enhanced classes
    'EnhancedLoguruLogger',
]
