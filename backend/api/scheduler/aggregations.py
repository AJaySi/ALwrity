"""Data aggregation utilities for Scheduler API"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from loguru import logger

from models.monitoring_models import TaskExecutionLog, MonitoringTask
from models.scheduler_models import SchedulerEventLog
from models.oauth_token_monitoring_models import OAuthTokenMonitoringTask
from models.platform_insights_monitoring_models import PlatformInsightsTask, PlatformInsightsExecutionLog
from models.website_analysis_monitoring_models import WebsiteAnalysisTask, WebsiteAnalysisExecutionLog


def aggregate_execution_logs(
    db: Session,
    limit: int = 50,
    offset: int = 0,
    status_filter: Optional[str] = None,
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Aggregate execution logs with pagination and filtering.

    Args:
        db: Database session
        limit: Maximum number of logs to return
        offset: Pagination offset
        status_filter: Optional status filter
        user_id: Optional user ID filter

    Returns:
        Dictionary with logs and pagination info
    """
    try:
        query = db.query(TaskExecutionLog)

        # Apply filters
        if status_filter:
            query = query.filter(TaskExecutionLog.status == status_filter)
        if user_id:
            query = query.filter(TaskExecutionLog.user_id == user_id)

        # Get total count for pagination
        total = query.count()

        # Apply pagination and ordering
        logs = query.order_by(desc(TaskExecutionLog.started_at)).offset(offset).limit(limit).all()

        # Convert to response format
        log_entries = []
        for log in logs:
            log_entries.append({
                'id': log.id,
                'task_id': log.task_id,
                'task_type': log.task_type,
                'status': log.status,
                'started_at': log.started_at.isoformat() if log.started_at else None,
                'completed_at': log.completed_at.isoformat() if log.completed_at else None,
                'duration_seconds': log.duration_seconds,
                'error_message': log.error_message,
                'user_id': log.user_id,
                'metadata': log.metadata or {}
            })

        return {
            'logs': log_entries,
            'pagination': {
                'limit': limit,
                'offset': offset,
                'total': total,
                'has_more': offset + limit < total
            }
        }

    except Exception as e:
        logger.error(f"[Aggregation] Error aggregating execution logs: {e}", exc_info=True)
        return {
            'logs': [],
            'pagination': {
                'limit': limit,
                'offset': offset,
                'total': 0,
                'has_more': False
            }
        }


def aggregate_event_history(
    db: Session,
    limit: int = 50,
    offset: int = 0,
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Aggregate scheduler event history.

    Args:
        db: Database session
        limit: Maximum number of events to return
        offset: Pagination offset
        user_id: Optional user ID filter

    Returns:
        Dictionary with events and pagination info
    """
    try:
        query = db.query(SchedulerEventLog)

        if user_id:
            query = query.filter(SchedulerEventLog.user_id == user_id)

        total = query.count()
        events = query.order_by(desc(SchedulerEventLog.timestamp)).offset(offset).limit(limit).all()

        event_entries = []
        for event in events:
            event_entries.append({
                'id': event.id,
                'event_type': event.event_type,
                'timestamp': event.timestamp.isoformat(),
                'user_id': event.user_id,
                'details': event.details or {},
                'tasks_found': event.tasks_found,
                'tasks_executed': event.tasks_executed,
                'tasks_failed': event.tasks_failed,
                'tasks_skipped': getattr(event, 'tasks_skipped', None),  # May not exist in older versions
                'duration_seconds': event.duration_seconds
            })

        return {
            'events': event_entries,
            'pagination': {
                'limit': limit,
                'offset': offset,
                'total': total,
                'has_more': offset + limit < total
            }
        }

    except Exception as e:
        logger.error(f"[Aggregation] Error aggregating event history: {e}", exc_info=True)
        return {
            'events': [],
            'pagination': {
                'limit': limit,
                'offset': offset,
                'total': 0,
                'has_more': False
            }
        }


def aggregate_platform_insights_status(db: Session, user_id: str) -> Dict[str, Any]:
    """
    Aggregate platform insights monitoring status for a user.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        Dictionary with platform insights status
    """
    try:
        tasks = db.query(PlatformInsightsTask).filter(
            PlatformInsightsTask.user_id == user_id
        ).all()

        task_list = []
        active_count = 0
        paused_count = 0
        failed_count = 0

        for task in tasks:
            task_dict = {
                'task_id': task.task_id,
                'user_id': task.user_id,
                'platform': task.platform,
                'property_url': task.property_url,
                'status': task.status,
                'created_at': task.created_at.isoformat(),
                'last_run_at': task.last_run_at.isoformat() if task.last_run_at else None,
                'next_run_at': task.next_run_at.isoformat() if task.next_run_at else None,
                'frequency_hours': task.frequency_hours,
                'error_count': task.error_count,
                'last_error': task.last_error,
                'metadata': task.metadata or {}
            }
            task_list.append(task_dict)

            # Count by status
            if task.status == 'active':
                active_count += 1
            elif task.status == 'paused':
                paused_count += 1
            elif task.status == 'failed':
                failed_count += 1

        return {
            'tasks': task_list,
            'total_tasks': len(tasks),
            'active_tasks': active_count,
            'paused_tasks': paused_count,
            'failed_tasks': failed_count,
            'last_updated': None  # Will be set by calling function
        }

    except Exception as e:
        logger.error(f"[Aggregation] Error aggregating platform insights status: {e}", exc_info=True)
        return {
            'tasks': [],
            'total_tasks': 0,
            'active_tasks': 0,
            'paused_tasks': 0,
            'failed_tasks': 0,
            'last_updated': None
        }


def aggregate_website_analysis_status(db: Session, user_id: str) -> Dict[str, Any]:
    """
    Aggregate website analysis monitoring status for a user.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        Dictionary with website analysis status
    """
    try:
        tasks = db.query(WebsiteAnalysisTask).filter(
            WebsiteAnalysisTask.user_id == user_id
        ).all()

        task_list = []
        active_count = 0
        paused_count = 0
        failed_count = 0

        for task in tasks:
            task_dict = {
                'task_id': task.task_id,
                'user_id': task.user_id,
                'website_url': task.website_url,
                'analysis_type': task.analysis_type,
                'status': task.status,
                'created_at': task.created_at.isoformat(),
                'last_run_at': task.last_run_at.isoformat() if task.last_run_at else None,
                'next_run_at': task.next_run_at.isoformat() if task.next_run_at else None,
                'frequency_hours': task.frequency_hours,
                'error_count': task.error_count,
                'last_error': task.last_error,
                'metadata': task.metadata or {}
            }
            task_list.append(task_dict)

            # Count by status
            if task.status == 'active':
                active_count += 1
            elif task.status == 'paused':
                paused_count += 1
            elif task.status == 'failed':
                failed_count += 1

        return {
            'tasks': task_list,
            'total_tasks': len(tasks),
            'active_tasks': active_count,
            'paused_tasks': paused_count,
            'failed_tasks': failed_count,
            'last_updated': None  # Will be set by calling function
        }

    except Exception as e:
        logger.error(f"[Aggregation] Error aggregating website analysis status: {e}", exc_info=True)
        return {
            'tasks': [],
            'total_tasks': 0,
            'active_tasks': 0,
            'paused_tasks': 0,
            'failed_tasks': 0,
            'last_updated': None
        }