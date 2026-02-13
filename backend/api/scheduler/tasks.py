"""Task Management Router for Scheduler API"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from loguru import logger

# Import models and utilities
from .models.shared import TaskInterventionInfo, ManualTriggerRequest, ManualTriggerResponse, TaskRetryRequest, TaskRetryResponse
from .utils import extract_user_id_from_current_user
from .validators import validate_user_access

# Import existing services and models
from services.scheduler import get_scheduler
from services.database import get_db
from middleware.auth_middleware import get_current_user
from models.oauth_token_monitoring_models import OAuthTokenMonitoringTask
from models.platform_insights_monitoring_models import PlatformInsightsTask
from models.website_analysis_monitoring_models import WebsiteAnalysisTask

router = APIRouter(prefix="/api/scheduler", tags=["scheduler-tasks"])


@router.get("/tasks-needing-intervention/{user_id}")
async def get_tasks_needing_intervention(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get all tasks that need human intervention.

    Tasks enter this state when they have failed multiple times and are in cool-off.
    This allows users to manually intervene, fix issues, and retry tasks.

    Args:
        user_id: User ID

    Returns:
        List of tasks needing intervention with failure pattern details
    """
    try:
        # Verify user access - users can only see their own tasks
        validated_user_id = validate_user_access(user_id, current_user, require_ownership=True)

        from services.scheduler.core.failure_detection_service import FailureDetectionService
        detection_service = FailureDetectionService(db)

        tasks = detection_service.get_tasks_needing_intervention(user_id=validated_user_id)

        # Convert to response format
        intervention_tasks = []
        for task in tasks:
            intervention_info = TaskInterventionInfo(
                task_id=task.get('task_id', ''),
                task_type=task.get('task_type', ''),
                user_id=task.get('user_id', ''),
                status=task.get('status', 'needs_intervention'),
                created_at=task.get('created_at', ''),
                last_attempt=task.get('last_attempt'),
                failure_count=task.get('failure_count', 0),
                error_message=task.get('error_message'),
                next_retry_at=task.get('next_retry_at'),
                metadata=task.get('metadata', {})
            )
            intervention_tasks.append(intervention_info)

        return {
            "success": True,
            "tasks": intervention_tasks,
            "count": len(intervention_tasks),
            "user_id": validated_user_id,
            "last_updated": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Tasks] Error getting tasks needing intervention for user {user_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get tasks needing intervention: {str(e)}")


@router.post("/tasks/{task_type}/{task_id}/manual-trigger", response_model=ManualTriggerResponse)
async def manual_trigger_task(
    task_type: str,
    task_id: int,
    request: ManualTriggerRequest = None,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Manually trigger a task that is in cool-off or needs intervention.
    This bypasses the cool-off check and executes the task immediately.

    Useful for:
    - Tasks stuck in cool-off due to temporary issues
    - Manual intervention after fixing underlying problems
    - Testing task execution with custom parameters

    Args:
        task_type: Task type (oauth_token_monitoring, website_analysis, gsc_insights, bing_insights)
        task_id: Task ID
        request: Optional manual trigger parameters

    Returns:
        Success status and execution result
    """
    try:
        from services.scheduler.core.task_execution_handler import execute_task_async
        scheduler = get_scheduler()

        # Load task based on type
        task = None
        if task_type == "oauth_token_monitoring":
            task = db.query(OAuthTokenMonitoringTask).filter(
                OAuthTokenMonitoringTask.id == task_id
            ).first()
        elif task_type == "website_analysis":
            task = db.query(WebsiteAnalysisTask).filter(
                WebsiteAnalysisTask.id == task_id
            ).first()
        elif task_type in ["gsc_insights", "bing_insights"]:
            task = db.query(PlatformInsightsTask).filter(
                PlatformInsightsTask.id == task_id
            ).first()
        else:
            raise HTTPException(status_code=400, detail=f"Unknown task type: {task_type}")

        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        # Verify user access - users can only trigger their own tasks
        authenticated_user_id = extract_user_id_from_current_user(current_user)
        if authenticated_user_id != task.user_id:
            raise HTTPException(status_code=403, detail="Access denied: You can only trigger your own tasks")

        # Clear cool-off status and reset failure count
        task.status = "active"
        task.consecutive_failures = 0
        task.failure_pattern = None

        # Apply custom parameters if provided
        if request and request.parameters:
            for key, value in request.parameters.items():
                if hasattr(task, key):
                    setattr(task, key, value)

        # Execute task manually (bypasses cool-off check)
        await execute_task_async(scheduler, task_type, task, execution_source="manual")

        db.commit()

        logger.info(f"[Tasks] Manually triggered task {task_id} ({task_type}) for user {task.user_id}")

        return ManualTriggerResponse(
            success=True,
            task_id=str(task_id),
            execution_id=f"manual_{task_type}_{task_id}_{datetime.utcnow().isoformat()}",
            message="Task triggered successfully",
            estimated_duration_seconds=300  # 5 minutes default estimate
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Tasks] Error manually triggering task {task_id} ({task_type}): {e}", exc_info=True)
        db.rollback()  # Rollback on error
        raise HTTPException(status_code=500, detail=f"Failed to trigger task: {str(e)}")


@router.post("/website-analysis/retry/{task_id}", response_model=TaskRetryResponse)
async def retry_website_analysis(
    task_id: int,
    request: TaskRetryRequest = None,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Manually retry a failed website analysis task.

    This endpoint allows users to retry website analysis tasks that have failed,
    with options to reset failure count and schedule immediate execution.

    Args:
        task_id: Task ID to retry
        request: Optional retry parameters

    Returns:
        Success status and updated task details
    """
    try:
        # Get task
        task = db.query(WebsiteAnalysisTask).filter(WebsiteAnalysisTask.id == task_id).first()

        if not task:
            raise HTTPException(status_code=404, detail="Website analysis task not found")

        # Verify user access - users can only retry their own tasks
        authenticated_user_id = extract_user_id_from_current_user(current_user)
        if authenticated_user_id != task.user_id:
            raise HTTPException(status_code=403, detail="Access denied: You can only retry your own tasks")

        # Reset task status and failure tracking
        task.status = 'active'
        task.failure_reason = None

        # Reset failure count if requested
        reset_count = False
        if request and request.reset_failure_count:
            task.consecutive_failures = 0
            task.failure_pattern = None
            reset_count = True

        # Apply custom parameters if provided
        if request and request.custom_parameters:
            for key, value in request.custom_parameters.items():
                if hasattr(task, key):
                    setattr(task, key, value)

        # Schedule immediate execution unless custom schedule provided
        if not (request and request.custom_parameters and 'next_check' in request.custom_parameters):
            task.next_check = datetime.utcnow()  # Schedule immediately

        task.updated_at = datetime.utcnow()

        db.commit()

        # Calculate retry schedule
        retry_scheduled_at = task.next_check.isoformat() if task.next_check else None

        logger.info(f"[Tasks] Manually retried website analysis task {task_id} for user {task.user_id}")

        return TaskRetryResponse(
            success=True,
            task_id=str(task_id),
            retry_scheduled_at=retry_scheduled_at,
            message=f'Website analysis task {task_id} scheduled for retry',
            failure_count_reset=reset_count
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Tasks] Error retrying website analysis task {task_id}: {e}", exc_info=True)
        db.rollback()  # Rollback on error
        raise HTTPException(status_code=500, detail=f"Failed to retry website analysis task: {str(e)}")


@router.get("/task-intervention/summary/{user_id}")
async def get_task_intervention_summary(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get a summary of tasks needing intervention for a user.

    This provides a quick overview without full task details,
    useful for dashboard widgets and notifications.

    Args:
        user_id: User ID

    Returns:
        Summary statistics of tasks needing intervention
    """
    try:
        # Verify user access
        validated_user_id = validate_user_access(user_id, current_user, require_ownership=True)

        from services.scheduler.core.failure_detection_service import FailureDetectionService
        detection_service = FailureDetectionService(db)

        tasks = detection_service.get_tasks_needing_intervention(user_id=validated_user_id)

        # Calculate summary statistics
        total_needing_attention = len(tasks)

        # Group by task type
        by_type = {}
        critical_failures = 0
        oldest_failure = None

        for task in tasks:
            task_type = task.get('task_type', 'unknown')
            by_type[task_type] = by_type.get(task_type, 0) + 1

            # Count critical failures (5+ consecutive failures)
            if task.get('failure_count', 0) >= 5:
                critical_failures += 1

            # Track oldest failure
            created_at = task.get('created_at')
            if created_at:
                try:
                    task_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    if oldest_failure is None or task_date < oldest_failure:
                        oldest_failure = task_date
                except:
                    pass

        return {
            "user_id": validated_user_id,
            "total_needing_attention": total_needing_attention,
            "by_task_type": by_type,
            "critical_failures": critical_failures,
            "oldest_failure_hours": (datetime.utcnow() - oldest_failure).total_seconds() / 3600 if oldest_failure else None,
            "requires_immediate_attention": total_needing_attention > 0,
            "last_updated": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Tasks] Error getting task intervention summary for user {user_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get task intervention summary: {str(e)}")