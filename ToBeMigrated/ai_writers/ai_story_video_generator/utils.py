"""
Utility functions for the AI Story Video Generator.
"""

import os
import tempfile
import uuid
from pathlib import Path
from typing import Optional

# Constants
TEMP_DIR = Path(tempfile.gettempdir()) / "alwrity_story_generator"

def ensure_temp_dir() -> Path:
    """Ensure the temporary directory exists and return its path."""
    os.makedirs(TEMP_DIR, exist_ok=True)
    return TEMP_DIR

def get_temp_filepath(prefix: str, extension: str) -> str:
    """Generate a temporary file path with the given prefix and extension."""
    temp_dir = ensure_temp_dir()
    return str(temp_dir / f"{prefix}_{uuid.uuid4()}.{extension}")

def clean_temp_files(older_than_hours: int = 24) -> int:
    """
    Clean temporary files older than the specified number of hours.
    
    Args:
        older_than_hours: Remove files older than this many hours
        
    Returns:
        Number of files removed
    """
    import time
    from datetime import datetime, timedelta
    
    temp_dir = ensure_temp_dir()
    cutoff_time = time.time() - (older_than_hours * 3600)
    count = 0
    
    for file_path in temp_dir.glob("*"):
        if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
            try:
                file_path.unlink()
                count += 1
            except Exception:
                pass
    
    return count

def format_duration(seconds: float) -> str:
    """Format seconds into a MM:SS string."""
    minutes = int(seconds // 60)
    remaining_seconds = int(seconds % 60)
    return f"{minutes}:{remaining_seconds:02d}"

def sanitize_filename(filename: str) -> str:
    """Sanitize a string to be used as a filename."""
    import re
    # Remove invalid characters
    sanitized = re.sub(r'[^\w\s-]', '', filename)
    # Replace spaces with underscores
    sanitized = sanitized.strip().replace(' ', '_')
    return sanitized