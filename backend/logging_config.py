"""
Logging Configuration Module - Moved to Unified Logging System
DEPRECATED: This file is moved to utils/logging/config.py
Use: from utils.logging import setup_clean_logging, get_uvicorn_log_level
"""

# Backward compatibility import
from utils.logging import setup_clean_logging, get_uvicorn_log_level

# Re-export for backward compatibility
__all__ = [
    'setup_clean_logging',
    'get_uvicorn_log_level',
]
