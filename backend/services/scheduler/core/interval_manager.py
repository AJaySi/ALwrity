"""
Interval Manager
Handles intelligent scheduling interval adjustment based on active strategies.
"""

from typing import TYPE_CHECKING
from datetime import datetime
from sqlalchemy.orm import Session

from services.database import get_all_user_ids, get_session_for_user
from utils.logger_utils import get_service_logger

if TYPE_CHECKING:
    from .scheduler import TaskScheduler

logger = get_service_logger("interval_manager")


async def determine_optimal_interval(
    scheduler: 'TaskScheduler',
    min_interval: int,
    max_interval: int
) -> int:
    """
    Determine optimal check interval based on active strategies across all users.
    
    Args:
        scheduler: TaskScheduler instance
        min_interval: Minimum check interval in minutes
        max_interval: Maximum check interval in minutes
        
    Returns:
        Optimal check interval in minutes
    """
    total_active_count = 0
    user_ids = get_all_user_ids()
    
    for user_id in user_ids:
        db = None
        try:
            db = get_session_for_user(user_id)
            if db:
                try:
                    from services.active_strategy_service import ActiveStrategyService
                    active_strategy_service = ActiveStrategyService(db_session=db)
                    user_active_count = active_strategy_service.count_active_strategies_with_tasks()
                    total_active_count += user_active_count
                    
                    # Optimization: If we found at least one active strategy, we can stop and return min_interval
                    # (unless we want accurate stats)
                    # For stats accuracy, we should continue.
                except Exception as e:
                    logger.warning(f"Error counting active strategies for user {user_id}: {e}")
        except Exception as e:
            logger.warning(f"Error checking user {user_id} for strategies: {e}")
        finally:
            if db:
                db.close()
                
    scheduler.stats['active_strategies_count'] = total_active_count
    
    if total_active_count > 0:
        logger.info(f"Found {total_active_count} active strategies across users - using {min_interval}min interval")
        return min_interval
    else:
        logger.info(f"No active strategies found - using {max_interval}min interval")
        return max_interval


async def adjust_check_interval_if_needed(
    scheduler: 'TaskScheduler',
    db: Session = None  # Deprecated parameter, ignored
):
    """
    Intelligently adjust check interval based on active strategies across all users.
    
    If there are active strategies with tasks, check more frequently.
    If there are no active strategies, check less frequently.
    
    Args:
        scheduler: TaskScheduler instance
        db: Deprecated/Ignored
    """
    total_active_count = 0
    user_ids = get_all_user_ids()
    
    for user_id in user_ids:
        user_db = None
        try:
            user_db = get_session_for_user(user_id)
            if user_db:
                try:
                    from services.active_strategy_service import ActiveStrategyService
                    active_strategy_service = ActiveStrategyService(db_session=user_db)
                    user_active_count = active_strategy_service.count_active_strategies_with_tasks()
                    total_active_count += user_active_count
                except Exception as e:
                    logger.warning(f"Error counting active strategies for user {user_id}: {e}")
        except Exception as e:
            logger.warning(f"Error checking user {user_id} for strategies: {e}")
        finally:
            if user_db:
                user_db.close()
    
    scheduler.stats['active_strategies_count'] = total_active_count
    
    # Determine optimal interval
    if total_active_count > 0:
        optimal_interval = scheduler.min_check_interval_minutes
    else:
        optimal_interval = scheduler.max_check_interval_minutes
    
    # Only reschedule if interval needs to change
    if optimal_interval != scheduler.current_check_interval_minutes:
        interval_message = (
            f"[Scheduler] ⚙️ Adjusting Check Interval\n"
            f"   ├─ Current: {scheduler.current_check_interval_minutes}min\n"
            f"   ├─ Optimal: {optimal_interval}min\n"
            f"   ├─ Active Strategies: {total_active_count}\n"
            f"   └─ Reason: {'Active strategies detected' if total_active_count > 0 else 'No active strategies'}"
        )
        logger.warning(interval_message)
        
        # Reschedule the job with new interval
        scheduler.scheduler.modify_job(
            job_id='check_due_tasks',  # Fixed job_id from check_cycle to check_due_tasks to match scheduler.py
            trigger=scheduler._get_trigger_for_interval(optimal_interval)
        )
        scheduler.current_check_interval_minutes = optimal_interval
        scheduler.stats['last_interval_adjustment'] = datetime.utcnow().isoformat()

