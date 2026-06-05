"""
Task Manager for YouTube Creator Studio

Delegates to the hybrid DB-backed + in-memory YouTubeTaskManager.
Maintains backward compatibility with the Story Writer TaskManager API.
"""

from services.youtube.youtube_task_manager import task_manager

__all__ = ["task_manager"]