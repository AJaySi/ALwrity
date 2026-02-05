"""
Structured logging functionality.
"""

import json
from typing import Dict, Any
from datetime import datetime
from loguru import logger


class StructuredLogger:
    """Structured logger for JSON-formatted logs."""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.logger = logger.bind(service=f"{service_name}-structured")
    
    def log_event(self, event_type: str, data: Dict[str, Any]):
        """Log structured event."""
        event = {
            "event_type": event_type,
            "service": self.service_name,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        self.logger.info(f"EVENT: {json.dumps(event)}")
    
    def log_error(self, error: Exception, context: Dict[str, Any] = None):
        """Log structured error."""
        error_event = {
            "event_type": "error",
            "service": self.service_name,
            "timestamp": datetime.now().isoformat(),
            "error": str(error),
            "context": context or {}
        }
        self.logger.error(f"ERROR: {json.dumps(error_event)}")


# Global structured logger instance
structured_logger = StructuredLogger("system")
