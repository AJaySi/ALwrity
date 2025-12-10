"""
Task Manager for YouTube Creator Studio

Reuses the Story Writer task manager pattern for async video rendering.
"""

from api.story_writer.task_manager import TaskManager

# Shared task manager instance
task_manager = TaskManager()

