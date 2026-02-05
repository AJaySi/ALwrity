"""
Logging configuration management.
"""

import os
from pathlib import Path

# Base directory for all log files
LOG_BASE_DIR = os.getenv("LOG_BASE_DIR", "logs")

# Environment detection
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Check if scheduler event log is available
SCHEDULER_EVENT_LOG_AVAILABLE = True
