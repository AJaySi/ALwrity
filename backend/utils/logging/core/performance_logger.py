"""
Performance monitoring functionality.
"""

from typing import Dict, Any
from datetime import datetime
from loguru import logger


class PerformanceLogger:
    """Performance monitoring logger."""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.logger = logger.bind(service=f"{service_name}-performance")
    
    def log_slow_query(self, query: str, execution_time: float):
        """Log slow database queries."""
        if execution_time > 1000:  # 1 second
            self.logger.warning(f"🐌 Slow query ({execution_time:.2f}ms): {query[:100]}...")
    
    def log_memory_usage(self, usage_mb: float):
        """Log memory usage."""
        if usage_mb > 500:  # 500MB
            self.logger.warning(f"🧠 High memory usage: {usage_mb:.1f}MB")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        return {
            "service": self.service_name,
            "timestamp": datetime.now().isoformat(),
            "status": "monitoring"
        }


# Global performance logger instance
performance_logger = PerformanceLogger("system")
