"""Data aggregation utilities for Scheduler API."""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from loguru import logger
from datetime import datetime, timedelta

from models.monitoring_models import TaskExecutionLog
from models.scheduler_models import SchedulerEventLog
from models.platform_insights_monitoring_models import PlatformInsightsTask
from models.website_analysis_monitoring_models import WebsiteAnalysisTask


def aggregate_execution_logs(
    db: Session,
    limit: int = 50,
    offset: int = 0,
    status_filter: Optional[str] = None,
    user_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Aggregate task execution logs for dashboard-compatible responses."""
    try:
        query = db.query(TaskExecutionLog).options(joinedload(TaskExecutionLog.task))

        if status_filter:
            query = query.filter(TaskExecutionLog.status == status_filter)
        if user_id:
            query = query.filter(TaskExecutionLog.user_id == user_id)

        total = query.count()
        logs = query.order_by(desc(TaskExecutionLog.execution_date)).offset(offset).limit(limit).all()

        log_entries = []
        for log in logs:
            task = getattr(log, 'task', None)
            log_entries.append({
                'id': log.id,
                'task_id': log.task_id,
                'user_id': str(log.user_id) if log.user_id is not None else None,
                'execution_date': log.execution_date.isoformat() if log.execution_date else None,
                'status': log.status,
                'error_message': log.error_message,
                'execution_time_ms': log.execution_time_ms,
                'result_data': log.result_data,
                'created_at': log.created_at.isoformat() if log.created_at else None,
                'task': {
                    'id': task.id if task else log.task_id,
                    'task_title': task.task_title if task else f'Task {log.task_id}',
                    'component_name': task.component_name if task else 'Unknown',
                    'metric': task.metric if task else 'unknown',
                    'frequency': task.frequency if task else 'Unknown',
                }
            })

        return {
            'logs': log_entries,
            'total_count': total,
            'limit': limit,
            'offset': offset,
            'has_more': offset + limit < total,
            'is_scheduler_logs': False,
        }

    except Exception as e:
        logger.error(f"[Aggregation] Error aggregating execution logs: {e}", exc_info=True)
        return {
            'logs': [],
            'total_count': 0,
            'limit': limit,
            'offset': offset,
            'has_more': False,
            'is_scheduler_logs': False,
        }


def aggregate_event_history(
    db: Session,
    limit: int = 50,
    offset: int = 0,
    user_id: Optional[str] = None,
    event_type: Optional[str] = None,
    days: Optional[int] = None,
) -> Dict[str, Any]:
    """Aggregate scheduler event history in frontend-compatible shape."""
    try:
        query = db.query(SchedulerEventLog)

        if user_id:
            query = query.filter(SchedulerEventLog.user_id == user_id)

        if event_type:
            query = query.filter(SchedulerEventLog.event_type == event_type)

        date_filter = None
        if days:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            query = query.filter(SchedulerEventLog.event_date >= cutoff_date)
            date_filter = {
                'days': days,
                'cutoff_date': cutoff_date.isoformat(),
                'showing_events_since': cutoff_date.isoformat()
            }

        total = query.count()
        events = query.order_by(desc(SchedulerEventLog.event_date)).offset(offset).limit(limit).all()

        event_entries = []
        for event in events:
            event_entries.append({
                'id': event.id,
                'event_type': event.event_type,
                'event_date': event.event_date.isoformat() if event.event_date else None,
                'check_cycle_number': event.check_cycle_number,
                'check_interval_minutes': event.check_interval_minutes,
                'previous_interval_minutes': event.previous_interval_minutes,
                'new_interval_minutes': event.new_interval_minutes,
                'tasks_found': event.tasks_found,
                'tasks_executed': event.tasks_executed,
                'tasks_failed': event.tasks_failed,
                'tasks_by_type': event.tasks_by_type,
                'check_duration_seconds': event.check_duration_seconds,
                'active_strategies_count': event.active_strategies_count,
                'active_executions': event.active_executions,
                'job_id': event.job_id,
                'job_type': event.job_type,
                'user_id': event.user_id,
                'event_data': event.event_data,
                'error_message': event.error_message,
                'created_at': event.created_at.isoformat() if event.created_at else None,
            })

        response = {
            'events': event_entries,
            'total_count': total,
            'limit': limit,
            'offset': offset,
            'has_more': offset + limit < total,
        }

        if date_filter:
            response['date_filter'] = date_filter

        return response

    except Exception as e:
        logger.error(f"[Aggregation] Error aggregating event history: {e}", exc_info=True)
        return {
            'events': [],
            'total_count': 0,
            'limit': limit,
            'offset': offset,
            'has_more': False,
        }


def aggregate_platform_insights_status(db: Session, user_id: str) -> Dict[str, Any]:
    """Aggregate platform insights monitoring status for a user."""
    try:
        tasks = db.query(PlatformInsightsTask).filter(PlatformInsightsTask.user_id == user_id).all()

        task_list = []
        active_count = 0
        paused_count = 0
        failed_count = 0

        for task in tasks:
            task_dict = {
                'id': task.id,
                'user_id': task.user_id,
                'platform': task.platform,
                'site_url': task.site_url,
                'status': task.status,
                'created_at': task.created_at.isoformat() if task.created_at else None,
                'last_check': task.last_check.isoformat() if task.last_check else None,
                'next_check': task.next_check.isoformat() if task.next_check else None,
                'failure_reason': task.failure_reason,
                'metadata': getattr(task, 'metadata', None) or {}
            }
            task_list.append(task_dict)

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
            'last_updated': None,
        }

    except Exception as e:
        logger.error(f"[Aggregation] Error aggregating platform insights status: {e}", exc_info=True)
        return {
            'tasks': [],
            'total_tasks': 0,
            'active_tasks': 0,
            'paused_tasks': 0,
            'failed_tasks': 0,
            'last_updated': None,
        }


def aggregate_website_analysis_status(db: Session, user_id: str) -> Dict[str, Any]:
    """Aggregate website analysis monitoring status for a user."""
    try:
        tasks = db.query(WebsiteAnalysisTask).filter(WebsiteAnalysisTask.user_id == user_id).all()

        task_list = []
        active_count = 0
        paused_count = 0
        failed_count = 0

        for task in tasks:
            task_dict = {
                'id': task.id,
                'user_id': task.user_id,
                'website_url': task.website_url,
                'task_type': task.task_type,
                'status': task.status,
                'created_at': task.created_at.isoformat() if task.created_at else None,
                'last_check': task.last_check.isoformat() if task.last_check else None,
                'next_check': task.next_check.isoformat() if task.next_check else None,
                'failure_reason': task.failure_reason,
                'metadata': getattr(task, 'metadata', None) or {}
            }
            task_list.append(task_dict)

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
            'last_updated': None,
        }

    except Exception as e:
        logger.error(f"[Aggregation] Error aggregating website analysis status: {e}", exc_info=True)
        return {
            'tasks': [],
            'total_tasks': 0,
            'active_tasks': 0,
            'paused_tasks': 0,
            'failed_tasks': 0,
            'last_updated': None,
        }
