"""
Check Cycle Handler
Handles the main scheduler check cycle that finds and executes due tasks.
"""

from typing import TYPE_CHECKING, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

from services.database import get_db_session
from utils.logger_utils import get_service_logger
from models.scheduler_models import SchedulerEventLog
from .exception_handler import DatabaseError
from .interval_manager import adjust_check_interval_if_needed

if TYPE_CHECKING:
    from .scheduler import TaskScheduler

logger = get_service_logger("check_cycle_handler")


async def check_and_execute_due_tasks(scheduler: 'TaskScheduler'):
    """
    Main scheduler loop: check for due tasks and execute them.
    This runs periodically with intelligent interval adjustment based on active strategies.
    
    Args:
        scheduler: TaskScheduler instance
    """
    scheduler.stats['total_checks'] += 1
    check_start_time = datetime.utcnow()
    scheduler.stats['last_check'] = check_start_time.isoformat()
    
    # Track execution summary for this check cycle
    cycle_summary = {
        'tasks_found_by_type': {},
        'tasks_executed_by_type': {},
        'tasks_failed_by_type': {},
        'total_found': 0,
        'total_executed': 0,
        'total_failed': 0
    }
    
    db = None
    try:
        db = get_db_session()
        if db is None:
            logger.error("[Scheduler Check] ❌ Failed to get database session")
            return
        
        # Check for active strategies and adjust interval intelligently
        await adjust_check_interval_if_needed(scheduler, db)
        
        # Check each registered task type
        registered_types = scheduler.registry.get_registered_types()
        for task_type in registered_types:
            type_summary = await scheduler._process_task_type(task_type, db, cycle_summary)
            if type_summary:
                cycle_summary['tasks_found_by_type'][task_type] = type_summary.get('found', 0)
                cycle_summary['tasks_executed_by_type'][task_type] = type_summary.get('executed', 0)
                cycle_summary['tasks_failed_by_type'][task_type] = type_summary.get('failed', 0)
        
        # Calculate totals
        cycle_summary['total_found'] = sum(cycle_summary['tasks_found_by_type'].values())
        cycle_summary['total_executed'] = sum(cycle_summary['tasks_executed_by_type'].values())
        cycle_summary['total_failed'] = sum(cycle_summary['tasks_failed_by_type'].values())
        
        # Log comprehensive check cycle summary
        check_duration = (datetime.utcnow() - check_start_time).total_seconds()
        active_strategies = scheduler.stats.get('active_strategies_count', 0)
        active_executions = len(scheduler.active_executions)
        
        # Build comprehensive check cycle summary log message
        check_lines = [
            f"[Scheduler Check] 🔍 Check Cycle #{scheduler.stats['total_checks']} Completed",
            f"   ├─ Duration: {check_duration:.2f}s",
            f"   ├─ Active Strategies: {active_strategies}",
            f"   ├─ Check Interval: {scheduler.current_check_interval_minutes}min",
            f"   ├─ User Isolation: Enabled (tasks filtered by user_id)",
            f"   ├─ Tasks Found: {cycle_summary['total_found']} total"
        ]
        
        if cycle_summary['tasks_found_by_type']:
            task_types_list = list(cycle_summary['tasks_found_by_type'].items())
            for idx, (task_type, count) in enumerate(task_types_list):
                executed = cycle_summary['tasks_executed_by_type'].get(task_type, 0)
                failed = cycle_summary['tasks_failed_by_type'].get(task_type, 0)
                is_last_task_type = idx == len(task_types_list) - 1 and cycle_summary['total_executed'] == 0 and cycle_summary['total_failed'] == 0
                prefix = "   └─" if is_last_task_type else "   ├─"
                check_lines.append(f"{prefix} {task_type}: {count} found, {executed} executed, {failed} failed")
        
        if cycle_summary['total_found'] > 0:
            check_lines.append(f"   ├─ Total Executed: {cycle_summary['total_executed']}")
            check_lines.append(f"   ├─ Total Failed: {cycle_summary['total_failed']}")
            check_lines.append(f"   └─ Active Executions: {active_executions}/{scheduler.max_concurrent_executions}")
        else:
            check_lines.append(f"   └─ No tasks found - scheduler idle")
        
        # Log comprehensive check cycle summary in single message
        logger.warning("\n".join(check_lines))
        
        # Save check cycle event to database for historical tracking
        try:
            event_log = SchedulerEventLog(
                event_type='check_cycle',
                event_date=check_start_time,
                check_cycle_number=scheduler.stats['total_checks'],
                check_interval_minutes=scheduler.current_check_interval_minutes,
                tasks_found=cycle_summary.get('total_found', 0),
                tasks_executed=cycle_summary.get('total_executed', 0),
                tasks_failed=cycle_summary.get('total_failed', 0),
                tasks_by_type=cycle_summary.get('tasks_found_by_type', {}),
                check_duration_seconds=check_duration,
                active_strategies_count=active_strategies,
                active_executions=active_executions,
                event_data={
                    'executed_by_type': cycle_summary.get('tasks_executed_by_type', {}),
                    'failed_by_type': cycle_summary.get('tasks_failed_by_type', {})
                }
            )
            db.add(event_log)
            db.commit()
        except Exception as e:
            logger.warning(f"Failed to save check cycle event log: {e}")
            if db:
                db.rollback()
        
        # Update last_update timestamp for frontend polling
        scheduler.stats['last_update'] = datetime.utcnow().isoformat()
        
    except Exception as e:
        error = DatabaseError(
            message=f"Error checking for due tasks: {str(e)}",
            original_error=e
        )
        scheduler.exception_handler.handle_exception(error)
        logger.error(f"[Scheduler Check] ❌ Error in check cycle: {str(e)}")
    finally:
        if db:
            db.close()

