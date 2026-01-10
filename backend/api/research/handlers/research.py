"""
Research Execution Handler

Handles research execution endpoints (execute, start, status, cancel).
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Dict, Any
from loguru import logger
import uuid

from services.database import get_db
from services.research.core import ResearchEngine, ResearchContext
from middleware.auth_middleware import get_current_user
from ..models import ResearchRequest, ResearchResponse
from ..utils import convert_to_research_context

router = APIRouter()

# In-memory task storage for async research
# TODO: In production, use Redis or database for persistence
_research_tasks: Dict[str, Dict[str, Any]] = {}


@router.post("/execute", response_model=ResearchResponse)
async def execute_research(
    request: ResearchRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Execute research synchronously.
    
    For quick research needs. For longer research, use /start endpoint.
    """
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        user_id = str(current_user.get('id', ''))
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid user ID in authentication token")
        
        logger.info(f"[Research API] Execute request: {request.query[:50]}...")
        
        engine = ResearchEngine()
        context = convert_to_research_context(request, user_id)
        
        result = await engine.research(context)
        
        return ResearchResponse(
            success=result.success,
            sources=result.sources,
            keyword_analysis=result.keyword_analysis,
            competitor_analysis=result.competitor_analysis,
            suggested_angles=result.suggested_angles,
            provider_used=result.provider_used,
            search_queries=result.search_queries,
            error_message=result.error_message,
            error_code=result.error_code,
        )
        
    except Exception as e:
        logger.error(f"[Research API] Execute failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/start", response_model=ResearchResponse)
async def start_research(
    request: ResearchRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Start research asynchronously.
    
    Returns a task_id that can be used to poll for status.
    Use this for comprehensive research that may take longer.
    """
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        user_id = str(current_user.get('id', ''))
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid user ID in authentication token")
        
        logger.info(f"[Research API] Start async request: {request.query[:50]}...")
        
        task_id = str(uuid.uuid4())
        
        # Initialize task
        _research_tasks[task_id] = {
            "status": "pending",
            "progress_messages": [],
            "result": None,
            "error": None,
        }
        
        # Start background task
        context = convert_to_research_context(request, user_id)
        background_tasks.add_task(_run_research_task, task_id, context)
        
        return ResearchResponse(
            success=True,
            task_id=task_id,
        )
        
    except Exception as e:
        logger.error(f"[Research API] Start failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def _run_research_task(task_id: str, context: ResearchContext):
    """Background task to run research."""
    try:
        _research_tasks[task_id]["status"] = "running"
        
        def progress_callback(message: str):
            _research_tasks[task_id]["progress_messages"].append(message)
        
        engine = ResearchEngine()
        result = await engine.research(context, progress_callback=progress_callback)
        
        _research_tasks[task_id]["status"] = "completed"
        _research_tasks[task_id]["result"] = result
        
    except Exception as e:
        logger.error(f"[Research API] Task {task_id} failed: {e}")
        _research_tasks[task_id]["status"] = "failed"
        _research_tasks[task_id]["error"] = str(e)


@router.get("/status/{task_id}")
async def get_research_status(task_id: str):
    """
    Get status of an async research task.
    
    Poll this endpoint to get progress updates and final results.
    """
    if task_id not in _research_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = _research_tasks[task_id]
    
    response = {
        "task_id": task_id,
        "status": task["status"],
        "progress_messages": task["progress_messages"],
    }
    
    if task["status"] == "completed" and task["result"]:
        result = task["result"]
        response["result"] = {
            "success": result.success,
            "sources": result.sources,
            "keyword_analysis": result.keyword_analysis,
            "competitor_analysis": result.competitor_analysis,
            "suggested_angles": result.suggested_angles,
            "provider_used": result.provider_used,
            "search_queries": result.search_queries,
        }
        
        # Clean up completed task after returning
        # In production, use Redis or database for persistence
        
    elif task["status"] == "failed":
        response["error"] = task["error"]
    
    return response


@router.delete("/status/{task_id}")
async def cancel_research(task_id: str):
    """
    Cancel a running research task.
    """
    if task_id not in _research_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = _research_tasks[task_id]
    
    if task["status"] in ["pending", "running"]:
        task["status"] = "cancelled"
        return {"message": "Task cancelled", "task_id": task_id}
    
    return {"message": f"Task already {task['status']}", "task_id": task_id}
