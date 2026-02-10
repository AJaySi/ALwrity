"""Monitoring and Logs Router for Scheduler API"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from datetime import datetime
from loguru import logger

# Import models and utilities
from .models.monitoring import ExecutionLogsResponse, EventHistoryResponse, EventLogStats, EventLogCleanupResponse
from .aggregations import aggregate_execution_logs, aggregate_event_history
from .statistics import calculate_event_log_statistics
from .utils import extract_user_id_from_current_user
from .validators import validate_pagination_params, validate_user_access, validate_event_log_cleanup_params

# Import existing services and models
from services.database import get_db
from middleware.auth_middleware import get_current_user
from models.monitoring_models import TaskExecutionLog
from models.scheduler_models import SchedulerEventLog
from models.platform_insights_monitoring_models import PlatformInsightsExecutionLog, PlatformInsightsTask

router = APIRouter(prefix="/api/scheduler", tags=["scheduler-monitoring"])


@router.get("/execution-logs", response_model=ExecutionLogsResponse)
async def get_execution_logs(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    status: Optional[str] = Query(None, pattern="^(success|failed|running|skipped)$"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get task execution logs from database.

    Query Params:
        - limit: Number of logs to return (1-500, default: 50)
        - offset: Pagination offset (default: 0)
        - status: Filter by status (success, failed, running, skipped)

    Returns:
        - List of execution logs with task details
        - Total count for pagination
    """
    try:
        # Validate pagination parameters
        validate_pagination_params(limit, offset)

        # Extract user ID for potential future user isolation
        user_id = extract_user_id_from_current_user(current_user)

        # Use the aggregation function from Phase 1B
        result = aggregate_execution_logs(
            db=db,
            limit=limit,
            offset=offset,
            status_filter=status,
            user_id=user_id
        )

        return ExecutionLogsResponse(**result)

    except Exception as e:
        logger.error(f"[Monitoring] Error getting execution logs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get execution logs: {str(e)}")


@router.get("/event-history", response_model=EventHistoryResponse)
async def get_event_history(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get scheduler event history for monitoring and debugging.

    Query Params:
        - limit: Number of events to return (1-500, default: 50)
        - offset: Pagination offset (default: 0)

    Returns:
        - List of scheduler events with details
        - Pagination information
    """
    try:
        # Validate pagination parameters
        validate_pagination_params(limit, offset)

        # Extract user ID for potential future user isolation
        user_id = extract_user_id_from_current_user(current_user)

        # Use the aggregation function from Phase 1B
        result = aggregate_event_history(
            db=db,
            limit=limit,
            offset=offset,
            user_id=user_id
        )

        return EventHistoryResponse(**result)

    except Exception as e:
        logger.error(f"[Monitoring] Error getting event history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get event history: {str(e)}")


@router.get("/event-logs/stats", response_model=EventLogStats)
async def get_event_logs_stats(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive statistics for event logs.

    Returns:
        - Total events count
        - Events by type breakdown
        - Date range information
        - Performance metrics
    """
    try:
        # Extract user ID for potential future user isolation
        user_id = extract_user_id_from_current_user(current_user)

        # Use the statistics function from Phase 1B
        stats = calculate_event_log_statistics(db)

        return EventLogStats(**stats)

    except Exception as e:
        logger.error(f"[Monitoring] Error getting event log statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get event log statistics: {str(e)}")


@router.post("/cleanup-event-logs", response_model=EventLogCleanupResponse)
async def cleanup_event_logs(
    older_than_days: Optional[int] = Query(None, ge=1, le=365),
    days_to_keep: Optional[int] = Query(None, ge=1, le=365),
    dry_run: bool = Query(True, description="Perform dry run without actual deletion"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Clean up old event logs to maintain database performance.

    Query Params:
        - older_than_days: Delete events older than this many days (1-365)
        - dry_run: If true, only count what would be deleted (default: true)

    Returns:
        - Number of events deleted/would be deleted
        - Oldest event timestamp kept
    """
    try:
        # Backward-compatible parameter handling
        effective_days = older_than_days if older_than_days is not None else days_to_keep
        if effective_days is None:
            raise HTTPException(status_code=422, detail="Either older_than_days or days_to_keep is required")

        # Validate cleanup parameters
        validate_event_log_cleanup_params(effective_days)

        # Extract user ID for potential future user isolation
        user_id = extract_user_id_from_current_user(current_user)

        # Calculate cutoff date
        from .utils import calculate_event_log_cleanup_cutoff
        cutoff_date = calculate_event_log_cleanup_cutoff(effective_days)

        # Count events that would be deleted
        delete_query = db.query(SchedulerEventLog).filter(
            SchedulerEventLog.created_at < cutoff_date
        )

        # Apply user filter if needed (for future multi-tenant support)
        if user_id:
            delete_query = delete_query.filter(SchedulerEventLog.user_id == user_id)

        would_delete_count = delete_query.count()

        deleted_count = 0
        oldest_kept_event = None

        if not dry_run:
            # Perform actual deletion
            deleted_count = delete_query.delete()

            # Commit the changes
            db.commit()

            # Find the oldest remaining event
            oldest_event = db.query(SchedulerEventLog.created_at).order_by(
                SchedulerEventLog.created_at.asc()
            ).first()

            if oldest_event:
                oldest_kept_event = oldest_event[0]

            logger.info(f"[Monitoring] Cleaned up {deleted_count} event logs older than {effective_days} days")

        return EventLogCleanupResponse(
            deleted_count=deleted_count,
            would_delete_count=would_delete_count,
            oldest_kept_event=oldest_kept_event,
            dry_run=dry_run
        )

    except Exception as e:
        logger.error(f"[Monitoring] Error cleaning up event logs: {e}")
        db.rollback()  # Rollback in case of error
        raise HTTPException(status_code=500, detail=f"Failed to cleanup event logs: {str(e)}")


@router.get("/platform-insights/logs/{user_id}")
async def get_platform_insights_logs(
    user_id: str,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    task_id: Optional[int] = Query(None, ge=1),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get platform insights execution logs for a specific user.

    Path Params:
        - user_id: User identifier

    Query Params:
        - limit: Number of logs to return (1-100, default: 50)
        - offset: Pagination offset (default: 0)

    Returns:
        - List of platform insights execution logs
        - Pagination information
    """
    try:
        # Validate user access (user can only access their own logs)
        authenticated_user_id = validate_user_access(user_id, current_user, require_ownership=True)

        # Validate pagination parameters
        validate_pagination_params(limit, offset, max_limit=100)

        # Query platform insights logs by joining through tasks (execution logs table has no user_id)
        query = db.query(PlatformInsightsExecutionLog).join(
            PlatformInsightsTask,
            PlatformInsightsExecutionLog.task_id == PlatformInsightsTask.id
        ).filter(PlatformInsightsTask.user_id == user_id)

        if task_id:
            query = query.filter(PlatformInsightsExecutionLog.task_id == task_id)

        # Get total count for pagination
        total = query.count()

        # Apply pagination and ordering
        logs = query.order_by(desc(PlatformInsightsExecutionLog.execution_date)).offset(offset).limit(limit).all()

        # Format logs for response (frontend-compatible)
        formatted_logs = []
        for log in logs:
            formatted_logs.append({
                'id': log.id,
                'task_id': log.task_id,
                'execution_date': log.execution_date.isoformat() if log.execution_date else None,
                'status': log.status,
                'result_data': log.result_data,
                'error_message': log.error_message,
                'execution_time_ms': log.execution_time_ms,
                'data_source': log.data_source,
                'created_at': log.created_at.isoformat() if log.created_at else None
            })

        return {
            'success': True,
            'logs': formatted_logs,
            'total_count': total,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Monitoring] Error getting platform insights logs for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get platform insights logs: {str(e)}")