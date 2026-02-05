"""
Utility functions for logging system.
"""

import functools
import time
from datetime import datetime
from typing import Callable, Any


def log_execution_time(func: Callable) -> Callable:
    """
    Decorator to log function execution time.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = (time.time() - start_time) * 1000
            print(f"⏱️ {func.__name__} executed in {execution_time:.2f}ms")
            return result
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            print(f"❌ {func.__name__} failed after {execution_time:.2f}ms: {e}")
            raise
    return wrapper


def save_to_file(data: Any, filename: str, directory: str = None):
    """
    Save data to a file in the log directory.
    """
    from .config import LOG_BASE_DIR
    
    if directory is None:
        directory = LOG_BASE_DIR
    
    filepath = Path(directory) / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        if isinstance(data, dict):
            import json
            json.dump(data, f, indent=2, default=str)
        else:
            f.write(str(data))
    
    print(f"💾 Saved data to {filepath}")
