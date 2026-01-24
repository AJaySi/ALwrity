"""Dashboard Statistics Router for Scheduler API"""

from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from datetime import datetime
from loguru import logger

# Import models and utilities
from .models.dashboard import SchedulerDashboardResponse, JobInfo, UserIsolationInfo
from .statistics import rebuild_cumulative_stats_from_events, validate_cumulative_stats
from .utils import format_job_for_response, extract_user_id_from_current_user
from .validators import validate_user_access

# Import existing services and models
from services.scheduler import get_scheduler
from services.scheduler.utils.user_job_store import get_user_job_store_name
from services.database import get_db
from middleware.auth_middleware import get_current_user
from models.oauth_token_monitoring_models import OAuthTokenMonitoringTask
from models.platform_insights_monitoring_models import PlatformInsightsTask
from models.website_analysis_monitoring_models import WebsiteAnalysisTask

router = APIRouter(prefix="/api/scheduler", tags=["scheduler-dashboard"])


@router.get("/dashboard", response_model=SchedulerDashboardResponse)
async def get_scheduler_dashboard(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get scheduler dashboard statistics and current state.

    Returns:
        - Scheduler stats (total checks, tasks executed, failed, etc.)
        - Current scheduled jobs
        - Active strategies count
        - Check interval
        - User isolation status
        - Last check timestamp
    """
    try:
        scheduler = get_scheduler()

        # Get user_id from current_user (Clerk format)
        user_id_str = extract_user_id_from_current_user(current_user)

        # Get scheduler stats
        stats = scheduler.get_stats(user_id=None)  # Get all stats for dashboard

        # Get cumulative stats from database
        cumulative_stats = _get_cumulative_stats(db)

        # Get all scheduled jobs
        formatted_jobs = _get_formatted_jobs(db, user_id_str)

        # Get active strategies count
        active_strategies = stats.get('active_strategies_count', 0)

        # Get last_update from stats (added by scheduler for frontend polling)
        last_update = stats.get('last_update')

        # Build response stats
        response_stats = {
            'total_checks': stats.get('total_checks', 0),
            'tasks_found': stats.get('tasks_found', 0),
            'tasks_executed': stats.get('tasks_executed', 0),
            'tasks_failed': stats.get('tasks_failed', 0),
            'tasks_skipped': stats.get('tasks_skipped', 0),
            'last_check': stats.get('last_check'),
            'last_update': last_update,
            'active_executions': stats.get('active_executions', 0),
            'running': stats.get('running', False),
            'check_interval_minutes': stats.get('check_interval_minutes', 60),
            'min_check_interval_minutes': stats.get('min_check_interval_minutes', 15),
            'max_check_interval_minutes': stats.get('max_check_interval_minutes', 60),
            'intelligent_scheduling': stats.get('intelligent_scheduling', True),
            'active_strategies_count': active_strategies,
            'last_interval_adjustment': stats.get('last_interval_adjustment'),
            'registered_types': stats.get('registered_types', []),
            'cumulative_total_check_cycles': cumulative_stats.get('total_check_cycles', 0),
            'cumulative_tasks_found': cumulative_stats.get('cumulative_tasks_found', 0),
            'cumulative_tasks_executed': cumulative_stats.get('cumulative_tasks_executed', 0),
            'cumulative_tasks_failed': cumulative_stats.get('cumulative_tasks_failed', 0)
        }

        # Calculate job statistics
        job_count = len(formatted_jobs)
        recurring_jobs = 1 + len([j for j in formatted_jobs if j.get('is_database_task')])  # check_due_tasks + all DB tasks
        one_time_jobs = len([j for j in formatted_jobs if not j.get('is_database_task') and j.get('trigger_type') == 'DateTrigger'])
        registered_task_types = stats.get('registered_types', [])

        # Build user isolation info
        user_isolation = UserIsolationInfo(
            enabled=True,
            current_user_id=user_id_str
        )

        return SchedulerDashboardResponse(
            stats=response_stats,
            jobs=formatted_jobs,
            job_count=job_count,
            recurring_jobs=recurring_jobs,
            one_time_jobs=one_time_jobs,
            registered_task_types=registered_task_types,
            user_isolation=user_isolation,
            last_updated=datetime.utcnow()
        )

    except Exception as e:
        logger.error(f"[Dashboard] Error getting scheduler dashboard: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get scheduler dashboard: {str(e)}")


@router.get("/jobs")
async def get_scheduler_jobs(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about all scheduled jobs.

    Returns:
        - List of jobs with detailed information
        - Job ID, trigger type, next run time
        - User context (extracted from job ID/kwargs)
        - Job store name (from user's website root)
    """
    try:
        scheduler = get_scheduler()
        all_jobs = scheduler.scheduler.get_jobs()

        formatted_jobs = []
        for job in all_jobs:
            job_dict = {
                'id': job.id,
                'trigger': type(job.trigger).__name__,
                'trigger_type': type(job.trigger).__name__,
                'next_run_time': job.next_run_time,
                'jobstore': getattr(job, 'jobstore', 'default'),
                'user_id': None,
                'user_job_store': 'default',
                'function_name': None,
                'is_database_task': False
            }

            # Extract user_id from job
            user_id_from_job = None
            if hasattr(job, 'kwargs') and job.kwargs and job.kwargs.get('user_id'):
                user_id_from_job = job.kwargs.get('user_id')
            elif job.id and ('research_persona_' in job.id or 'facebook_persona_' in job.id):
                parts = job.id.split('_')
                if len(parts) >= 3:
                    user_id_from_job = parts[2]

            if user_id_from_job:
                job_dict['user_id'] = user_id_from_job
                try:
                    user_job_store = get_user_job_store_name(user_id_from_job, db)
                    job_dict['user_job_store'] = user_job_store
                except Exception as e:
                    logger.debug(f"Could not get job store for user {user_id_from_job}: {e}")

            # Extract function name
            if hasattr(job, 'func') and hasattr(job.func, '__name__'):
                job_dict['function_name'] = job.func.__name__
            elif hasattr(job, 'func') and hasattr(job.func, '__module__'):
                job_dict['function_name'] = f"{job.func.__module__}.{job.func.__name__}"

            formatted_jobs.append(format_job_for_response(job_dict))

        return {
            'jobs': formatted_jobs,
            'total_count': len(formatted_jobs),
            'last_updated': datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"[Dashboard] Error getting scheduler jobs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get scheduler jobs: {str(e)}")


@router.get("/recent-scheduler-logs")
async def get_recent_scheduler_logs(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get recent scheduler logs (restoration, job scheduling, etc.) for display in Execution Logs.
    These are informational logs that show scheduler activity when actual execution logs are not available.

    Returns only the latest 5 logs (rolling window, not accumulating).

    Returns:
        - List of latest 5 scheduler events (job_scheduled, job_completed, job_failed)
        - Formatted as execution log-like entries for display
    """
    try:
        # Get only the latest 5 scheduler events - simple rolling window
        # Focus on job-related events that indicate scheduler activity
        query = db.query(SchedulerEventLog).filter(
            SchedulerEventLog.event_type.in_(['job_scheduled', 'job_completed', 'job_failed'])
        ).order_by(desc(SchedulerEventLog.event_date)).limit(5)

        events = query.all()

        # Only log if there are issues (no events when expected)
        if not events:
            total_count = db.query(func.count(SchedulerEventLog.id)).filter(
                SchedulerEventLog.event_type.in_(['job_scheduled', 'job_completed', 'job_failed'])
            ).scalar() or 0
            if total_count > 0:  # Only log if there should be events
                logger.debug(f"[Dashboard] No recent scheduler events found (expected {total_count})")

        # Format as execution log-like entries
        formatted_logs = []
        for event in events:
            event_data = event.event_data or {}

            # Determine status based on event type
            status = 'running'
            if event.event_type == 'job_completed':
                status = 'success'
            elif event.event_type == 'job_failed':
                status = 'failed'

            # Extract job function name
            job_function = event_data.get('job_function') or event_data.get('function_name') or 'unknown'

            # Extract execution time if available
            execution_time_ms = None
            if event_data.get('execution_time_seconds'):
                execution_time_ms = int(event_data.get('execution_time_seconds', 0) * 1000)

            log_entry = {
                'id': f"scheduler_event_{event.id}",
                'task_id': None,
                'user_id': event.user_id,
                'execution_date': event.event_date.isoformat() if event.event_date else None,
                'status': status,
                'error_message': event.error_message,
                'execution_time_ms': execution_time_ms,
                'result_data': None,
                'created_at': event.created_at.isoformat() if event.created_at else None,
                'task': {
                    'id': None,
                    'task_title': f"{event.event_type.replace('_', ' ').title()}: {event.job_id or 'N/A'}",
                    'component_name': 'Scheduler',
                    'metric': job_function,
                    'tags': ['scheduler', 'system'],
                    'type': 'scheduler_event'
                }
            }

            formatted_logs.append(log_entry)

        return {
            'logs': formatted_logs,
            'total_count': len(formatted_logs),
            'limit': 5,
            'offset': 0,
            'has_more': False,
            'is_scheduler_logs': True  # Indicate these are scheduler logs, not execution logs
        }

    except Exception as e:
        logger.error(f"[Dashboard] Error getting recent scheduler logs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get recent scheduler logs: {str(e)}")


def _get_cumulative_stats(db: Session) -> Dict[str, int]:
    """Get cumulative statistics from database with fallback logic."""
    try:
        # Try to get from persistent table first
        from models.monitoring_models import TaskExecutionLog
        cumulative_stats = None

        try:
            # Try to import and use SchedulerCumulativeStats if it exists
            from models.scheduler_cumulative_stats import SchedulerCumulativeStats
            cumulative_stats_row = SchedulerCumulativeStats.get_or_none(db)

            if cumulative_stats_row:
                cumulative_stats = {
                    'total_check_cycles': cumulative_stats_row.total_check_cycles or 0,
                    'cumulative_tasks_found': cumulative_stats_row.cumulative_tasks_found or 0,
                    'cumulative_tasks_executed': cumulative_stats_row.cumulative_tasks_executed or 0,
                    'cumulative_tasks_failed': cumulative_stats_row.cumulative_tasks_failed or 0,
                    'cumulative_tasks_skipped': cumulative_stats_row.cumulative_tasks_skipped or 0
                }

                # Validate stats against actual event count
                cumulative_stats = validate_cumulative_stats(cumulative_stats, db)

                # Update the persistent table with validated stats
                cumulative_stats_row.total_check_cycles = cumulative_stats['total_check_cycles']
                cumulative_stats_row.cumulative_tasks_found = cumulative_stats['cumulative_tasks_found']
                cumulative_stats_row.cumulative_tasks_executed = cumulative_stats['cumulative_tasks_executed']
                cumulative_stats_row.cumulative_tasks_failed = cumulative_stats['cumulative_tasks_failed']
                cumulative_stats_row.cumulative_tasks_skipped = cumulative_stats.get('cumulative_tasks_skipped', 0)
                db.commit()

                return cumulative_stats

        except ImportError:
            # Cumulative stats model doesn't exist yet (migration not run)
            logger.warning(
                "[Dashboard] Cumulative stats model not found. "
                "Falling back to event logs aggregation. "
                "Run migration: create_scheduler_cumulative_stats.sql"
            )
        except Exception as e:
            logger.error(f"[Dashboard] Error getting cumulative stats: {e}", exc_info=True)

        # Fallback to event logs aggregation
        return rebuild_cumulative_stats_from_events(db)

    except Exception as e:
        logger.error(f"[Dashboard] Error in _get_cumulative_stats: {e}", exc_info=True)
        # Return safe defaults
        return {
            'total_check_cycles': 0,
            'cumulative_tasks_found': 0,
            'cumulative_tasks_executed': 0,
            'cumulative_tasks_failed': 0,
            'cumulative_tasks_skipped': 0
        }


def _get_formatted_jobs(db: Session, user_id_str: str = None) -> List[Dict[str, Any]]:
    """Get formatted jobs including database-backed tasks."""
    scheduler = get_scheduler()
    all_jobs = scheduler.scheduler.get_jobs()

    formatted_jobs = []

    # Add APScheduler jobs
    for job in all_jobs:
        job_info = {
            'id': job.id,
            'trigger_type': type(job.trigger).__name__,
            'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
            'user_id': None,
            'job_store': 'default',
            'user_job_store': 'default',
            'is_database_task': False
        }

        # Extract user_id from job
        user_id_from_job = None
        if hasattr(job, 'kwargs') and job.kwargs and job.kwargs.get('user_id'):
            user_id_from_job = job.kwargs.get('user_id')
        elif job.id and ('research_persona_' in job.id or 'facebook_persona_' in job.id):
            parts = job.id.split('_')
            if len(parts) >= 3:
                user_id_from_job = parts[2]

        if user_id_from_job:
            job_info['user_id'] = user_id_from_job
            try:
                user_job_store = get_user_job_store_name(user_id_from_job, db)
                job_info['user_job_store'] = user_job_store
            except Exception as e:
                logger.debug(f"Could not get job store for user {user_id_from_job}: {e}")

        formatted_jobs.append(job_info)

    # Add OAuth token monitoring tasks
    _add_oauth_monitoring_tasks(db, formatted_jobs, user_id_str)

    # Add website analysis tasks
    _add_website_analysis_tasks(db, formatted_jobs, user_id_str)

    # Add platform insights tasks
    _add_platform_insights_tasks(db, formatted_jobs, user_id_str)

    return formatted_jobs


def _add_oauth_monitoring_tasks(db: Session, formatted_jobs: List[Dict[str, Any]], user_id_str: str = None):
    """Add OAuth token monitoring tasks to formatted jobs."""
    try:
        oauth_tasks = db.query(OAuthTokenMonitoringTask).filter(
            OAuthTokenMonitoringTask.status == 'active'
        ).all()

        # Consolidated OAuth logging - only log if there are issues
        oauth_tasks_count = len(oauth_tasks)
        if oauth_tasks_count == 0:
            # Check if there are failed tasks that need attention
            all_oauth_tasks = db.query(OAuthTokenMonitoringTask).all()
            failed_count = sum(1 for task in all_oauth_tasks if task.status == 'failed')
            if failed_count > 0:
                logger.warning(f"[Dashboard] OAuth: {failed_count} failed tasks need attention")
        elif oauth_tasks_count > 0 and len(oauth_tasks) > 10:  # Only log if unusually high count
            logger.info(f"[Dashboard] OAuth: {oauth_tasks_count} active monitoring tasks")

        for task in oauth_tasks:
            try:
                user_job_store = get_user_job_store_name(task.user_id, db)
            except Exception as e:
                user_job_store = 'default'
                logger.debug(f"Could not get job store for user {task.user_id}: {e}")

            # Format as recurring weekly job
            job_info = {
                'id': f"oauth_token_monitoring_{task.platform}_{task.user_id}",
                'trigger_type': 'CronTrigger',  # Weekly recurring
                'next_run_time': task.next_check.isoformat() if task.next_check else None,
                'user_id': task.user_id,
                'job_store': 'default',
                'user_job_store': user_job_store,
                'function_name': 'oauth_token_monitoring_executor.execute_task',
                'platform': task.platform,
                'task_id': task.id,
                'is_database_task': True,  # Flag to indicate this is a DB task, not APScheduler job
                'frequency': 'Weekly'
            }

            formatted_jobs.append(job_info)
    except Exception as e:
        logger.error(f"[Dashboard] Error loading OAuth token monitoring tasks: {e}", exc_info=True)


def _add_website_analysis_tasks(db: Session, formatted_jobs: List[Dict[str, Any]], user_id_str: str = None):
    """Add website analysis tasks to formatted jobs."""
    try:
        website_analysis_tasks = db.query(WebsiteAnalysisTask).filter(
            WebsiteAnalysisTask.status == 'active'
        ).all()

        # Filter by user if user_id_str is provided
        if user_id_str:
            website_analysis_tasks = [t for t in website_analysis_tasks if t.user_id == user_id_str]

        for task in website_analysis_tasks:
            try:
                user_job_store = get_user_job_store_name(task.user_id, db)
            except Exception as e:
                user_job_store = 'default'
                logger.debug(f"Could not get job store for user {task.user_id}: {e}")

            # Format as recurring job
            job_info = {
                'id': f"website_analysis_{task.task_type}_{task.user_id}_{task.id}",
                'trigger_type': 'CronTrigger',  # Recurring based on frequency_days
                'next_run_time': task.next_check.isoformat() if task.next_check else None,
                'user_id': task.user_id,
                'job_store': 'default',
                'user_job_store': user_job_store,
                'function_name': 'website_analysis_executor.execute_task',
                'task_type': task.task_type,  # 'user_website' or 'competitor'
                'website_url': task.website_url,
                'competitor_id': task.competitor_id,
                'task_id': task.id,
                'is_database_task': True,
                'frequency': f'Every {task.frequency_days} days',
                'task_category': 'website_analysis'
            }

            formatted_jobs.append(job_info)
    except Exception as e:
        logger.error(f"[Dashboard] Error loading website analysis tasks: {e}", exc_info=True)


def _add_platform_insights_tasks(db: Session, formatted_jobs: List[Dict[str, Any]], user_id_str: str = None):
    """Add platform insights tasks to formatted jobs."""
    try:
        insights_tasks = db.query(PlatformInsightsTask).filter(
            PlatformInsightsTask.status == 'active'
        ).all()

        # Filter by user if user_id_str is provided
        if user_id_str:
            insights_tasks = [t for t in insights_tasks if t.user_id == user_id_str]

        for task in insights_tasks:
            try:
                user_job_store = get_user_job_store_name(task.user_id, db)
            except Exception as e:
                user_job_store = 'default'
                logger.debug(f"Could not get job store for user {task.user_id}: {e}")

            # Format as recurring weekly job
            job_info = {
                'id': f"platform_insights_{task.platform}_{task.user_id}",
                'trigger_type': 'CronTrigger',  # Weekly recurring
                'next_run_time': task.next_check.isoformat() if task.next_check else None,
                'user_id': task.user_id,
                'job_store': 'default',
                'user_job_store': user_job_store,
                'function_name': f'{task.platform}_insights_executor.execute_task',
                'platform': task.platform,
                'task_id': task.id,
                'is_database_task': True,
                'frequency': 'Weekly',
                'task_category': 'platform_insights'
            }

            formatted_jobs.append(job_info)
    except Exception as e:
        logger.error(f"[Dashboard] Error loading platform insights tasks: {e}", exc_info=True)