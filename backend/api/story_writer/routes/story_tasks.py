from typing import Any, Dict

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from loguru import logger

from middleware.auth_middleware import get_current_user
from models.story_models import (
    StoryGenerationRequest,
    TaskStatus,
)
from services.story_writer.story_service import StoryWriterService

from ..cache_manager import cache_manager
from ..task_manager import task_manager
from ..utils.auth import require_authenticated_user


router = APIRouter()
story_service = StoryWriterService()


@router.post("/generate-full", response_model=Dict[str, Any])
async def generate_full_story(
    request: StoryGenerationRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user),
    max_iterations: int = 10,
) -> Dict[str, Any]:
    """Generate a complete story asynchronously."""
    try:
        user_id = require_authenticated_user(current_user)

        cache_key = cache_manager.get_cache_key(request.dict())
        cached_result = cache_manager.get_cached_result(cache_key)
        if cached_result:
            logger.info(f"[StoryWriter] Returning cached result for user {user_id}")
            task_id = task_manager.create_task("story_generation")
            task_manager.update_task_status(
                task_id,
                "completed",
                progress=100.0,
                result=cached_result,
                message="Returned cached result",
            )
            return {"task_id": task_id, "cached": True}

        task_id = task_manager.create_task("story_generation")
        request_data = request.dict()
        request_data["max_iterations"] = max_iterations

        background_tasks.add_task(
            task_manager.execute_story_generation_task,
            task_id=task_id,
            request_data=request_data,
            user_id=user_id,
        )

        logger.info(f"[StoryWriter] Created task {task_id} for full story generation (user {user_id})")
        return {
            "task_id": task_id,
            "status": "pending",
            "message": "Story generation started. Use /task/{task_id}/status to check progress.",
        }

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"[StoryWriter] Failed to start story generation: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/task/{task_id}/status", response_model=TaskStatus)
async def get_task_status(
    task_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> TaskStatus:
    """Get the status of a story generation task."""
    try:
        require_authenticated_user(current_user)

        task_status = task_manager.get_task_status(task_id)
        if not task_status:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

        return TaskStatus(**task_status)

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"[StoryWriter] Failed to get task status: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/task/{task_id}/result")
async def get_task_result(
    task_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """Get the result of a completed story generation task."""
    try:
        require_authenticated_user(current_user)

        task_status = task_manager.get_task_status(task_id)
        if not task_status:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        if task_status["status"] != "completed":
            raise HTTPException(
                status_code=400,
                detail=f"Task {task_id} is not completed. Status: {task_status['status']}",
            )

        result = task_status.get("result")
        if not result:
            raise HTTPException(status_code=404, detail=f"No result found for task {task_id}")

        if isinstance(result, dict):
            payload = {**result}
            payload.setdefault("success", True)
            payload["task_id"] = task_id
            return payload

        return {"result": result, "success": True, "task_id": task_id}

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"[StoryWriter] Failed to get task result: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


