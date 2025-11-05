"""
Scheduler Dashboard API
Provides endpoints for scheduler dashboard UI.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, func
from datetime import datetime
from loguru import logger

from services.scheduler import get_scheduler
from services.scheduler.utils.user_job_store import get_user_job_store_name
from services.monitoring_data_service import MonitoringDataService
from services.database import get_db
from middleware.auth_middleware import get_current_user
from models.monitoring_models import TaskExecutionLog, MonitoringTask
from models.scheduler_models import SchedulerEventLog
from models.oauth_token_monitoring_models import OAuthTokenMonitoringTask
from sqlalchemy import func

router = APIRouter(prefix="/api/scheduler", tags=["scheduler-dashboard"])


@router.get("/dashboard")
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
        user_id_str = str(current_user.get('id', '')) if current_user else None
        
        # Get scheduler stats
        stats = scheduler.get_stats(user_id=None)  # Get all stats for dashboard
        
        # Get all scheduled jobs
        all_jobs = scheduler.scheduler.get_jobs()
        
        # Format jobs with user context
        formatted_jobs = []
        for job in all_jobs:
            job_info = {
                'id': job.id,
                'trigger_type': type(job.trigger).__name__,
                'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
                'user_id': None,
                'job_store': 'default',
                'user_job_store': 'default'
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
        
        # Add OAuth token monitoring tasks from database (these are recurring weekly tasks)
        try:
            oauth_tasks = db.query(OAuthTokenMonitoringTask).filter(
                OAuthTokenMonitoringTask.status == 'active'
            ).all()
            
            oauth_tasks_count = len(oauth_tasks)
            if oauth_tasks_count > 0:
                # Log platform breakdown for debugging
                platforms = {}
                for task in oauth_tasks:
                    platforms[task.platform] = platforms.get(task.platform, 0) + 1
                
                platform_summary = ", ".join([f"{platform}: {count}" for platform, count in platforms.items()])
                logger.warning(
                    f"[Dashboard] OAuth Monitoring: Found {oauth_tasks_count} active OAuth token monitoring tasks "
                    f"({platform_summary})"
                )
            else:
                # Check if there are any inactive tasks
                all_oauth_tasks = db.query(OAuthTokenMonitoringTask).all()
                if all_oauth_tasks:
                    inactive_by_status = {}
                    for task in all_oauth_tasks:
                        status = task.status
                        inactive_by_status[status] = inactive_by_status.get(status, 0) + 1
                    logger.warning(
                        f"[Dashboard] OAuth Monitoring: Found {len(all_oauth_tasks)} total OAuth tasks, "
                        f"but {oauth_tasks_count} are active. Status breakdown: {inactive_by_status}"
                    )
            
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
            logger.error(f"Error loading OAuth token monitoring tasks: {e}", exc_info=True)
        
        # Get active strategies count
        active_strategies = stats.get('active_strategies_count', 0)
        
        # Get last_update from stats (added by scheduler for frontend polling)
        last_update = stats.get('last_update')
        
        # Calculate cumulative/historical values from scheduler_event_logs
        cumulative_stats = {}
        try:
            # First, check total events in database for debugging
            total_events = db.query(func.count(SchedulerEventLog.id)).scalar() or 0
            
            # Check for check_cycle events specifically
            check_cycle_count = db.query(func.count(SchedulerEventLog.id)).filter(
                SchedulerEventLog.event_type == 'check_cycle'
            ).scalar() or 0
            
            # Also check for other event types that might have task counts
            job_failed_count = db.query(func.count(SchedulerEventLog.id)).filter(
                SchedulerEventLog.event_type == 'job_failed'
            ).scalar() or 0
            job_completed_count = db.query(func.count(SchedulerEventLog.id)).filter(
                SchedulerEventLog.event_type == 'job_completed'
            ).scalar() or 0
            
            logger.warning(
                f"[Dashboard] Database stats: {total_events} total events, "
                f"{check_cycle_count} check_cycles, {job_failed_count} job_failed, "
                f"{job_completed_count} job_completed"
            )
            
            if check_cycle_count > 0:
                logger.warning(f"[Dashboard] Found {check_cycle_count} check cycle events in database")
                # Aggregate check cycle events for cumulative totals
                result = db.query(
                    func.count(SchedulerEventLog.id),
                    func.sum(SchedulerEventLog.tasks_found),
                    func.sum(SchedulerEventLog.tasks_executed),
                    func.sum(SchedulerEventLog.tasks_failed)
                ).filter(
                    SchedulerEventLog.event_type == 'check_cycle'
                ).first()
                
                if result:
                    # SQLAlchemy returns tuple for multi-column queries
                    # SUM returns NULL when no rows, handle that
                    total_cycles = result[0] if result[0] is not None else 0
                    total_found = result[1] if result[1] is not None else 0
                    total_executed = result[2] if result[2] is not None else 0
                    total_failed = result[3] if result[3] is not None else 0
                    
                    cumulative_stats = {
                        'total_check_cycles': int(total_cycles),
                        'cumulative_tasks_found': int(total_found),
                        'cumulative_tasks_executed': int(total_executed),
                        'cumulative_tasks_failed': int(total_failed)
                    }
                    
                    logger.warning(f"[Dashboard] Cumulative stats from check_cycles: {cumulative_stats}")
                else:
                    # No results (shouldn't happen with COUNT, but handle it)
                    cumulative_stats = {
                        'total_check_cycles': 0,
                        'cumulative_tasks_found': 0,
                        'cumulative_tasks_executed': 0,
                        'cumulative_tasks_failed': 0
                    }
                    logger.warning("[Dashboard] Query returned None (no check cycle events)")
            else:
                # No check cycles yet, but we can still show job counts
                # Log detailed info about why cumulative stats are 0
                if stats.get('total_checks', 0) > 0:
                    logger.warning(
                        f"[Dashboard] ⚠️ Scheduler shows {stats.get('total_checks', 0)} checks in memory, "
                        f"but NO check_cycle events found in database. "
                        f"This suggests check_cycle events are not being saved properly."
                    )
                else:
                    logger.warning(
                        f"[Dashboard] No check_cycle events yet. "
                        f"Scheduler interval: {stats.get('check_interval_minutes', 60)}min. "
                        f"First check cycle will run after interval expires. "
                        f"One-time jobs: {job_completed_count} completed, {job_failed_count} failed"
                    )
        except Exception as e:
            logger.error(f"Error calculating cumulative stats: {e}", exc_info=True)
            cumulative_stats = {
                'total_check_cycles': 0,
                'cumulative_tasks_found': 0,
                'cumulative_tasks_executed': 0,
                'cumulative_tasks_failed': 0
            }
        
        return {
            'stats': {
                # Current session stats (from scheduler memory)
                'total_checks': stats.get('total_checks', 0),
                'tasks_found': stats.get('tasks_found', 0),
                'tasks_executed': stats.get('tasks_executed', 0),
                'tasks_failed': stats.get('tasks_failed', 0),
                'tasks_skipped': stats.get('tasks_skipped', 0),
                'last_check': stats.get('last_check'),
                'last_update': last_update,  # Include for frontend polling
                'active_executions': stats.get('active_executions', 0),
                'running': stats.get('running', False),
                'check_interval_minutes': stats.get('check_interval_minutes', 60),
                'min_check_interval_minutes': stats.get('min_check_interval_minutes', 15),
                'max_check_interval_minutes': stats.get('max_check_interval_minutes', 60),
                'intelligent_scheduling': stats.get('intelligent_scheduling', True),
                'active_strategies_count': active_strategies,
                'last_interval_adjustment': stats.get('last_interval_adjustment'),
                'registered_types': stats.get('registered_types', []),
                # Cumulative/historical stats (from database)
                'cumulative_total_check_cycles': cumulative_stats.get('total_check_cycles', 0),
                'cumulative_tasks_found': cumulative_stats.get('cumulative_tasks_found', 0),
                'cumulative_tasks_executed': cumulative_stats.get('cumulative_tasks_executed', 0),
                'cumulative_tasks_failed': cumulative_stats.get('cumulative_tasks_failed', 0)
            },
            'jobs': formatted_jobs,
            'job_count': len(formatted_jobs),
            'recurring_jobs': 1 + len([j for j in formatted_jobs if j.get('is_database_task')]),  # check_due_tasks + OAuth tasks
            'one_time_jobs': len([j for j in formatted_jobs if not j.get('is_database_task') and j.get('trigger_type') == 'DateTrigger']),
            'user_isolation': {
                'enabled': True,
                'current_user_id': user_id_str
            },
            'last_updated': datetime.utcnow().isoformat()  # Keep for backward compatibility
        }
        
    except Exception as e:
        logger.error(f"Error getting scheduler dashboard: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get scheduler dashboard: {str(e)}")


@router.get("/execution-logs")
async def get_execution_logs(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    status: Optional[str] = Query(None, regex="^(success|failed|running|skipped)$"),
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
        # Get user_id from current_user (Clerk format - convert to int if needed)
        user_id_str = str(current_user.get('id', '')) if current_user else None
        
        # Check if user_id column exists in the database
        from sqlalchemy import inspect
        inspector = inspect(db.bind)
        columns = [col['name'] for col in inspector.get_columns('task_execution_logs')]
        has_user_id_column = 'user_id' in columns
        
        # If user_id column doesn't exist, we need to handle the query differently
        # to avoid SQLAlchemy trying to access a non-existent column
        if not has_user_id_column:
            # Query without user_id column - use explicit column selection
            from sqlalchemy import func
            
            # Build query for count
            count_query = db.query(func.count(TaskExecutionLog.id)).join(
                MonitoringTask,
                TaskExecutionLog.task_id == MonitoringTask.id
            )
            
            # Filter by status if provided
            if status:
                count_query = count_query.filter(TaskExecutionLog.status == status)
            
            total_count = count_query.scalar() or 0
            
            # Build query for data - select specific columns to avoid user_id
            query = db.query(
                TaskExecutionLog.id,
                TaskExecutionLog.task_id,
                TaskExecutionLog.execution_date,
                TaskExecutionLog.status,
                TaskExecutionLog.result_data,
                TaskExecutionLog.error_message,
                TaskExecutionLog.execution_time_ms,
                TaskExecutionLog.created_at,
                MonitoringTask
            ).join(
                MonitoringTask,
                TaskExecutionLog.task_id == MonitoringTask.id
            )
            
            # Filter by status if provided
            if status:
                query = query.filter(TaskExecutionLog.status == status)
            
            # Get paginated results
            logs = query.order_by(TaskExecutionLog.execution_date.desc()).offset(offset).limit(limit).all()
            
            # Format results for compatibility
            formatted_logs = []
            for log_tuple in logs:
                # Unpack the tuple
                log_id, task_id, execution_date, log_status, result_data, error_message, execution_time_ms, created_at, task = log_tuple
                
                log_data = {
                    'id': log_id,
                    'task_id': task_id,
                    'user_id': None,  # No user_id column in database
                    'execution_date': execution_date.isoformat() if execution_date else None,
                    'status': log_status,
                    'error_message': error_message,
                    'execution_time_ms': execution_time_ms,
                    'result_data': result_data,
                    'created_at': created_at.isoformat() if created_at else None
                }
                
                # Add task details
                if task:
                    log_data['task'] = {
                        'id': task.id,
                        'task_title': task.task_title,
                        'component_name': task.component_name,
                        'metric': task.metric,
                        'frequency': task.frequency
                    }
                
                formatted_logs.append(log_data)
            
            return {
                'logs': formatted_logs,
                'total_count': total_count,
                'limit': limit,
                'offset': offset,
                'has_more': (offset + limit) < total_count,
                'is_scheduler_logs': False  # Explicitly mark as execution logs, not scheduler logs
            }
        
        # If user_id column exists, use the normal query path
        # Build query with eager loading of task relationship
        query = db.query(TaskExecutionLog).join(
            MonitoringTask,
            TaskExecutionLog.task_id == MonitoringTask.id
        ).options(
            joinedload(TaskExecutionLog.task)
        )
        
        # Filter by status if provided
        if status:
            query = query.filter(TaskExecutionLog.status == status)
        
        # Filter by user_id if provided (for user isolation)
        if user_id_str and has_user_id_column:
            # Note: user_id in TaskExecutionLog is Integer, but we have Clerk string
            # For now, get all logs - can enhance later with user_id mapping
            pass
        
        # Get total count
        total_count = query.count()
        
        # Get paginated results
        logs = query.order_by(desc(TaskExecutionLog.execution_date)).offset(offset).limit(limit).all()
        
        # Format results
        formatted_logs = []
        for log in logs:
            log_data = {
                'id': log.id,
                'task_id': log.task_id,
                'user_id': log.user_id if has_user_id_column else None,
                'execution_date': log.execution_date.isoformat() if log.execution_date else None,
                'status': log.status,
                'error_message': log.error_message,
                'execution_time_ms': log.execution_time_ms,
                'result_data': log.result_data,
                'created_at': log.created_at.isoformat() if log.created_at else None
            }
            
            # Add task details if available
            if log.task:
                log_data['task'] = {
                    'id': log.task.id,
                    'task_title': log.task.task_title,
                    'component_name': log.task.component_name,
                    'metric': log.task.metric,
                    'frequency': log.task.frequency
                }
            
            formatted_logs.append(log_data)
        
        return {
            'logs': formatted_logs,
            'total_count': total_count,
            'limit': limit,
            'offset': offset,
            'has_more': (offset + limit) < total_count,
            'is_scheduler_logs': False  # Explicitly mark as execution logs, not scheduler logs
        }
        
    except Exception as e:
        logger.error(f"Error getting execution logs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get execution logs: {str(e)}")


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
            job_info = {
                'id': job.id,
                'trigger_type': type(job.trigger).__name__,
                'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
                'jobstore': getattr(job, 'jobstore', 'default'),
                'user_id': None,
                'user_job_store': 'default',
                'function_name': None
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
            
            # Get function name if available
            if hasattr(job, 'func') and hasattr(job.func, '__name__'):
                job_info['function_name'] = job.func.__name__
            elif hasattr(job, 'func_ref'):
                job_info['function_name'] = str(job.func_ref)
            
            formatted_jobs.append(job_info)
        
        return {
            'jobs': formatted_jobs,
            'total_jobs': len(formatted_jobs),
            'recurring_jobs': 1,  # check_due_tasks
            'one_time_jobs': len(formatted_jobs) - 1
        }
        
    except Exception as e:
        logger.error(f"Error getting scheduler jobs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get scheduler jobs: {str(e)}")


@router.get("/event-history")
async def get_scheduler_event_history(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    event_type: Optional[str] = Query(None, regex="^(check_cycle|interval_adjustment|start|stop|job_scheduled|job_cancelled|job_completed|job_failed)$"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get scheduler event history from database.
    
    This endpoint returns historical scheduler events such as:
    - Check cycles (when scheduler runs and checks for due tasks)
    - Interval adjustments (when check interval changes)
    - Scheduler start/stop events
    - Job scheduled/cancelled events
    
    Query Params:
        - limit: Number of events to return (1-1000, default: 100)
        - offset: Pagination offset (default: 0)
        - event_type: Filter by event type (check_cycle, interval_adjustment, start, stop, etc.)
    
    Returns:
        - List of scheduler events with details
        - Total count for pagination
    """
    try:
        # Build query
        query = db.query(SchedulerEventLog)
        
        # Filter by event type if provided
        if event_type:
            query = query.filter(SchedulerEventLog.event_type == event_type)
        
        # Get total count
        total_count = query.count()
        
        # Get paginated results (most recent first)
        events = query.order_by(desc(SchedulerEventLog.event_date)).offset(offset).limit(limit).all()
        
        # Format results
        formatted_events = []
        for event in events:
            event_data = {
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
                'created_at': event.created_at.isoformat() if event.created_at else None
            }
            formatted_events.append(event_data)
        
        return {
            'events': formatted_events,
            'total_count': total_count,
            'limit': limit,
            'offset': offset,
            'has_more': (offset + limit) < total_count
        }
        
    except Exception as e:
        logger.error(f"Error getting scheduler event history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get scheduler event history: {str(e)}")


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
        
        # Log for debugging - show more details
        logger.warning(
            f"[Dashboard] Recent scheduler logs query: found {len(events)} events"
        )
        if events:
            for e in events:
                logger.warning(
                    f"[Dashboard]   - Event: {e.event_type} | "
                    f"Job ID: {e.job_id} | User: {e.user_id} | "
                    f"Date: {e.event_date} | Error: {bool(e.error_message)}"
                )
        else:
            # Check if there are ANY events of these types
            total_count = db.query(func.count(SchedulerEventLog.id)).filter(
                SchedulerEventLog.event_type.in_(['job_scheduled', 'job_completed', 'job_failed'])
            ).scalar() or 0
            logger.warning(
                f"[Dashboard] No recent scheduler logs found (query returned 0). "
                f"Total events of these types in DB: {total_count}"
            )
        
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
                    'frequency': 'one-time'
                },
                'is_scheduler_log': True,  # Flag to indicate this is a scheduler log, not execution log
                'event_type': event.event_type,
                'job_id': event.job_id
            }
            
            formatted_logs.append(log_entry)
        
        # Log the formatted response for debugging
        logger.warning(
            f"[Dashboard] Formatted {len(formatted_logs)} scheduler logs for response. "
            f"Sample log entry keys: {list(formatted_logs[0].keys()) if formatted_logs else 'none'}"
        )
        
        return {
            'logs': formatted_logs,
            'total_count': len(formatted_logs),
            'limit': 5,
            'offset': 0,
            'has_more': False,
            'is_scheduler_logs': True  # Indicate these are scheduler logs, not execution logs
        }
        
    except Exception as e:
        logger.error(f"Error getting recent scheduler logs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get recent scheduler logs: {str(e)}")

