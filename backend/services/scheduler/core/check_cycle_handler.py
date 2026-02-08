"""
Check Cycle Handler
Handles the main scheduler check cycle that finds and executes due tasks.
"""

from typing import TYPE_CHECKING, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

from services.database import get_all_user_ids, get_session_for_user
from utils.logger_utils import get_service_logger
from .interval_manager import adjust_check_interval_if_needed

# Import semantic monitoring for Phase 2B integration
from services.intelligence.monitoring.semantic_dashboard import RealTimeSemanticMonitor

if TYPE_CHECKING:
    from .scheduler import TaskScheduler

logger = get_service_logger("check_cycle_handler")

# Track last semantic check per user to enforce 24-hour interval
# In-memory cache is sufficient as it resets on restart (which is fine)
LAST_SEMANTIC_CHECKS: Dict[str, datetime] = {}

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
    
    # Iterate through all users (Multi-tenancy support)
    user_ids = get_all_user_ids()
    total_active_strategies = 0
    
    for user_id in user_ids:
        db = get_session_for_user(user_id)
        if not db:
            logger.warning(f"[Scheduler Check] Could not get database session for user {user_id}")
            continue
            
        try:
            # Check active strategies for this user (for interval adjustment)
            try:
                from services.active_strategy_service import ActiveStrategyService
                active_strategy_service = ActiveStrategyService(db_session=db)
                user_active_strategies = active_strategy_service.count_active_strategies_with_tasks()
                total_active_strategies += user_active_strategies
            except Exception as e:
                logger.warning(f"Error counting active strategies for user {user_id}: {e}")

            # Phase 2B: Real-time semantic health monitoring (runs every 24 hours)
            # Check if 24 hours have passed since last check
            should_run_semantic = False
            now = datetime.utcnow()
            last_check = LAST_SEMANTIC_CHECKS.get(user_id)
            
            if not last_check or (now - last_check).total_seconds() > 86400:  # 24 hours
                should_run_semantic = True
            
            if should_run_semantic:
                try:
                    semantic_monitor = RealTimeSemanticMonitor(user_id)
                    # Use public wrapper method which aggregates metrics
                    # Note: semantic_monitor instantiation loads heavy models, so we limit frequency to 24h
                    semantic_health = await semantic_monitor.check_semantic_health(user_id)
                    logger.info(f"[Semantic Monitor] User {user_id} health check: {semantic_health.status} (score: {semantic_health.value:.2f})")
                    
                    # Update timestamp only on success/attempt to prevent spamming retries
                    LAST_SEMANTIC_CHECKS[user_id] = now
                         
                except Exception as e:
                    logger.warning(f"[Semantic Monitor] Error checking semantic health for user {user_id}: {e}")
            else:
                pass


            # Check each registered task type for this user
            registered_types = scheduler.registry.get_registered_types()
            for task_type in registered_types:
                # Pass the user-specific session
                type_summary = await scheduler._process_task_type(task_type, db, cycle_summary, user_id=user_id)
                if type_summary:
                    cycle_summary['tasks_found_by_type'][task_type] = cycle_summary['tasks_found_by_type'].get(task_type, 0) + type_summary.get('found', 0)
                    cycle_summary['tasks_executed_by_type'][task_type] = cycle_summary['tasks_executed_by_type'].get(task_type, 0) + type_summary.get('executed', 0)
                    cycle_summary['tasks_failed_by_type'][task_type] = cycle_summary['tasks_failed_by_type'].get(task_type, 0) + type_summary.get('failed', 0)
        
        except Exception as e:
            logger.error(f"[Scheduler Check] Error processing user {user_id}: {e}")
        finally:
            db.close()
    
    # Adjust interval based on TOTAL active strategies across all users
    # We manually update the stats and check interval, skipping adjust_check_interval_if_needed 
    # because it's not multi-tenant aware yet.
    scheduler.stats['active_strategies_count'] = total_active_strategies
    
    if total_active_strategies > 0:
        optimal_interval = scheduler.min_check_interval_minutes
    else:
        optimal_interval = scheduler.max_check_interval_minutes
    
    if optimal_interval != scheduler.current_check_interval_minutes:
        interval_message = (
            f"[Scheduler] ⚙️ Adjusting Check Interval\n"
            f"   ├─ Current: {scheduler.current_check_interval_minutes}min\n"
            f"   ├─ Optimal: {optimal_interval}min\n"
            f"   ├─ Active Strategies: {total_active_strategies}\n"
            f"   └─ Reason: {'Active strategies detected' if total_active_strategies > 0 else 'No active strategies'}"
        )
        logger.warning(interval_message)
        
        # Reschedule the job with new interval
        scheduler.scheduler.modify_job(
            job_id='check_due_tasks',
            trigger=scheduler._get_trigger_for_interval(optimal_interval)
        )
        scheduler.current_check_interval_minutes = optimal_interval

    # Calculate totals
    cycle_summary['total_found'] = sum(cycle_summary['tasks_found_by_type'].values())
    cycle_summary['total_executed'] = sum(cycle_summary['tasks_executed_by_type'].values())
    cycle_summary['total_failed'] = sum(cycle_summary['tasks_failed_by_type'].values())
    
    # Log comprehensive check cycle summary
    check_duration = (datetime.utcnow() - check_start_time).total_seconds()
    active_executions = len(scheduler.active_executions)
    
    # Build comprehensive check cycle summary log message
    check_lines = [
        f"[Scheduler Check] 🔍 Check Cycle #{scheduler.stats['total_checks']} Completed",
        f"   ├─ Duration: {check_duration:.2f}s",
        f"   ├─ Active Strategies: {total_active_strategies}",
        f"   ├─ Check Interval: {scheduler.current_check_interval_minutes}min",
        f"   ├─ User Isolation: Enabled (Scanned {len(user_ids)} users)",
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
    
    # Update last_update timestamp for frontend polling
    scheduler.stats['last_update'] = datetime.utcnow().isoformat()


