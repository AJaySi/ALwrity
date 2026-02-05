"""
Context-based logging functionality.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger


class ContextLogger:
    """Context-aware logger for request tracing."""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.logger = logger.bind(service=f"{service_name}-context")
        self.context = {}
    
    def set_context(self, **kwargs):
        """Set logging context."""
        self.context.update(kwargs)
        self.logger = self.logger.bind(**self.context)
    
    def clear_context(self):
        """Clear logging context."""
        self.context.clear()
        self.logger = logger.bind(service=self.service_name)
    
    def log_with_context(self, message: str, level: str = "info"):
        """Log message with current context."""
        log_method = getattr(self.logger, level)
        if self.context:
            log_method(f"{message} | Context: {self.context}")
        else:
            log_method(message)
    
    def get_context(self) -> Dict[str, Any]:
        """Get current context."""
        return self.context.copy()
