"""
Video Studio Router (Legacy Import)

This file is kept for backward compatibility.
All functionality has been moved to backend/routers/video_studio/ module.
"""

# Re-export from the new modular structure
from routers.video_studio import router

__all__ = ["router"]
