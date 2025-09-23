"""
Task Management System for Blog Writer API

Handles background task execution, status tracking, and progress updates
for research and outline generation operations.
"""

import asyncio
import uuid
from datetime import datetime
from typing import Any, Dict, List
from loguru import logger

from models.blog_models import (
    BlogResearchRequest,
    BlogOutlineRequest,
    MediumBlogGenerateRequest,
    MediumBlogGenerateResult,
)
from services.blog_writer.blog_service import BlogWriterService


class TaskManager:
    """Manages background tasks for research and outline generation."""
    
    def __init__(self):
        self.task_storage: Dict[str, Dict[str, Any]] = {}
        self.service = BlogWriterService()
    
    def cleanup_old_tasks(self):
        """Remove tasks older than 1 hour to prevent memory leaks."""
        current_time = datetime.now()
        tasks_to_remove = []
        
        for task_id, task_data in self.task_storage.items():
            if (current_time - task_data["created_at"]).total_seconds() > 3600:  # 1 hour
                tasks_to_remove.append(task_id)
        
        for task_id in tasks_to_remove:
            del self.task_storage[task_id]
    
    def create_task(self, task_type: str = "general") -> str:
        """Create a new task and return its ID."""
        task_id = str(uuid.uuid4())
        
        self.task_storage[task_id] = {
            "status": "pending",
            "created_at": datetime.now(),
            "result": None,
            "error": None,
            "progress_messages": [],
            "task_type": task_type
        }
        
        return task_id
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get the status of a task."""
        self.cleanup_old_tasks()
        
        if task_id not in self.task_storage:
            return None
        
        task = self.task_storage[task_id]
        response = {
            "task_id": task_id,
            "status": task["status"],
            "created_at": task["created_at"].isoformat(),
            "progress_messages": task.get("progress_messages", [])
        }
        
        if task["status"] == "completed":
            response["result"] = task["result"]
        elif task["status"] == "failed":
            response["error"] = task["error"]
        
        return response
    
    async def update_progress(self, task_id: str, message: str):
        """Update progress message for a task."""
        if task_id in self.task_storage:
            if "progress_messages" not in self.task_storage[task_id]:
                self.task_storage[task_id]["progress_messages"] = []
            
            progress_entry = {
                "timestamp": datetime.now().isoformat(),
                "message": message
            }
            self.task_storage[task_id]["progress_messages"].append(progress_entry)
            
            # Keep only last 10 progress messages to prevent memory bloat
            if len(self.task_storage[task_id]["progress_messages"]) > 10:
                self.task_storage[task_id]["progress_messages"] = self.task_storage[task_id]["progress_messages"][-10:]
            
            logger.info(f"Progress update for task {task_id}: {message}")
    
    def start_research_task(self, request: BlogResearchRequest) -> str:
        """Start a research operation and return a task ID."""
        task_id = self.create_task("research")
        
        # Start the research operation in the background
        asyncio.create_task(self._run_research_task(task_id, request))
        
        return task_id
    
    def start_outline_task(self, request: BlogOutlineRequest) -> str:
        """Start an outline generation operation and return a task ID."""
        task_id = self.create_task("outline")
        
        # Start the outline generation operation in the background
        asyncio.create_task(self._run_outline_generation_task(task_id, request))
        
        return task_id

    def start_medium_generation_task(self, request: MediumBlogGenerateRequest) -> str:
        """Start a medium (≤1000 words) full-blog generation task."""
        task_id = self.create_task("medium_generation")
        asyncio.create_task(self._run_medium_generation_task(task_id, request))
        return task_id
    
    async def _run_research_task(self, task_id: str, request: BlogResearchRequest):
        """Background task to run research and update status with progress messages."""
        try:
            # Update status to running
            self.task_storage[task_id]["status"] = "running"
            self.task_storage[task_id]["progress_messages"] = []
            
            # Send initial progress message
            await self.update_progress(task_id, "🔍 Starting research operation...")
            
            # Check cache first
            await self.update_progress(task_id, "📋 Checking cache for existing research...")
            
            # Run the actual research with progress updates
            result = await self.service.research_with_progress(request, task_id)
            
            # Check if research failed gracefully
            if not result.success:
                await self.update_progress(task_id, f"❌ Research failed: {result.error_message or 'Unknown error'}")
                self.task_storage[task_id]["status"] = "failed"
                self.task_storage[task_id]["error"] = result.error_message or "Research failed"
            else:
                await self.update_progress(task_id, f"✅ Research completed successfully! Found {len(result.sources)} sources and {len(result.search_queries or [])} search queries.")
                # Update status to completed
                self.task_storage[task_id]["status"] = "completed"
                self.task_storage[task_id]["result"] = result.dict()
            
        except Exception as e:
            await self.update_progress(task_id, f"❌ Research failed with error: {str(e)}")
            # Update status to failed
            self.task_storage[task_id]["status"] = "failed"
            self.task_storage[task_id]["error"] = str(e)
        
        # Ensure we always send a final completion message
        finally:
            if task_id in self.task_storage:
                current_status = self.task_storage[task_id]["status"]
                if current_status not in ["completed", "failed"]:
                    # Force completion if somehow we didn't set a final status
                    await self.update_progress(task_id, "⚠️ Research operation completed with unknown status")
                    self.task_storage[task_id]["status"] = "failed"
                    self.task_storage[task_id]["error"] = "Research completed with unknown status"
    
    async def _run_outline_generation_task(self, task_id: str, request: BlogOutlineRequest):
        """Background task to run outline generation and update status with progress messages."""
        try:
            # Update status to running
            self.task_storage[task_id]["status"] = "running"
            self.task_storage[task_id]["progress_messages"] = []
            
            # Send initial progress message
            await self.update_progress(task_id, "🧩 Starting outline generation...")
            
            # Run the actual outline generation with progress updates
            result = await self.service.generate_outline_with_progress(request, task_id)
            
            # Update status to completed
            await self.update_progress(task_id, f"✅ Outline generated successfully! Created {len(result.outline)} sections with {len(result.title_options)} title options.")
            self.task_storage[task_id]["status"] = "completed"
            self.task_storage[task_id]["result"] = result.dict()
            
        except Exception as e:
            await self.update_progress(task_id, f"❌ Outline generation failed: {str(e)}")
            # Update status to failed
            self.task_storage[task_id]["status"] = "failed"
            self.task_storage[task_id]["error"] = str(e)

    async def _run_medium_generation_task(self, task_id: str, request: MediumBlogGenerateRequest):
        """Background task to generate a medium blog using a single structured JSON call."""
        try:
            self.task_storage[task_id]["status"] = "running"
            self.task_storage[task_id]["progress_messages"] = []

            await self.update_progress(task_id, "📦 Packaging outline and metadata...")

            # Basic guard: respect global target words
            total_target = int(request.globalTargetWords or 1000)
            if total_target > 1000:
                raise ValueError("Global target words exceed 1000; medium generation not allowed")

            result: MediumBlogGenerateResult = await self.service.generate_medium_blog_with_progress(
                request,
                task_id,
            )

            if not result or not getattr(result, "sections", None):
                raise ValueError("Empty generation result from model")

            # Check if result came from cache
            cache_hit = getattr(result, 'cache_hit', False)
            if cache_hit:
                await self.update_progress(task_id, "⚡ Found cached content - loading instantly!")
            else:
                await self.update_progress(task_id, "🤖 Generated fresh content with AI...")
                await self.update_progress(task_id, "✨ Post-processing and assembling sections...")

            # Mark completed
            self.task_storage[task_id]["status"] = "completed"
            self.task_storage[task_id]["result"] = result.dict()
            await self.update_progress(task_id, f"✅ Generated {len(result.sections)} sections successfully.")

        except Exception as e:
            await self.update_progress(task_id, f"❌ Medium generation failed: {str(e)}")
            self.task_storage[task_id]["status"] = "failed"
            self.task_storage[task_id]["error"] = str(e)


# Global task manager instance
task_manager = TaskManager()
