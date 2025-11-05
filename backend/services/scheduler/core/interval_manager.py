"""
Interval Manager
Handles intelligent scheduling interval adjustment based on active strategies.
"""

from typing import TYPE_CHECKING
from datetime import datetime
from sqlalchemy.orm import Session

from services.database import get_db_session
from utils.logger_utils import get_service_logger
from models.scheduler_models import SchedulerEventLog

if TYPE_CHECKING:
    from .scheduler import TaskScheduler

logger = get_service_logger("interval_manager")


async def determine_optimal_interval(
    scheduler: 'TaskScheduler',
    min_interval: int,
    max_interval: int
) -> int:
    """
    Determine optimal check interval based on active strategies.
    
    Args:
        scheduler: TaskScheduler instance
        min_interval: Minimum check interval in minutes
        max_interval: Maximum check interval in minutes
        
    Returns:
        Optimal check interval in minutes
    """
    db = None
    try:
        db = get_db_session()
        if db:
            from services.active_strategy_service import ActiveStrategyService
            active_strategy_service = ActiveStrategyService(db_session=db)
            active_count = active_strategy_service.count_active_strategies_with_tasks()
            scheduler.stats['active_strategies_count'] = active_count
            
            if active_count > 0:
                logger.info(f"Found {active_count} active strategies with tasks - using {min_interval}min interval")
                return min_interval
            else:
                logger.info(f"No active strategies with tasks - using {max_interval}min interval")
                return max_interval
    except Exception as e:
        logger.warning(f"Error determining optimal interval: {e}, using default {min_interval}min")
    finally:
        if db:
            db.close()
    
    # Default to shorter interval on error (safer)
    return min_interval


async def adjust_check_interval_if_needed(
    scheduler: 'TaskScheduler',
    db: Session
):
    """
    Intelligently adjust check interval based on active strategies.
    
    If there are active strategies with tasks, check more frequently.
    If there are no active strategies, check less frequently.
    
    Args:
        scheduler: TaskScheduler instance
        db: Database session
    """
    try:
        from services.active_strategy_service import ActiveStrategyService
        
        active_strategy_service = ActiveStrategyService(db_session=db)
        active_count = active_strategy_service.count_active_strategies_with_tasks()
        scheduler.stats['active_strategies_count'] = active_count
        
        # Determine optimal interval
        if active_count > 0:
            optimal_interval = scheduler.min_check_interval_minutes
        else:
            optimal_interval = scheduler.max_check_interval_minutes
        
        # Only reschedule if interval needs to change
        if optimal_interval != scheduler.current_check_interval_minutes:
            interval_message = (
                f"[Scheduler] ⚙️ Adjusting Check Interval\n"
                f"   ├─ Current: {scheduler.current_check_interval_minutes}min\n"
                f"   ├─ Optimal: {optimal_interval}min\n"
                f"   ├─ Active Strategies: {active_count}\n"
                f"   └─ Reason: {'Active strategies detected' if active_count > 0 else 'No active strategies'}"
            )
            logger.warning(interval_message)
            
            # Reschedule the job with new interval
            scheduler.scheduler.modify_job(
                'check_due_tasks',
                trigger=scheduler._get_trigger_for_interval(optimal_interval)
            )
            
            # Save previous interval before updating
            previous_interval = scheduler.current_check_interval_minutes
            
            # Update current interval
            scheduler.current_check_interval_minutes = optimal_interval
            scheduler.stats['last_interval_adjustment'] = datetime.utcnow().isoformat()
            
            # Save interval adjustment event to database
            try:
                event_db = get_db_session()
                if event_db:
                    event_log = SchedulerEventLog(
                        event_type='interval_adjustment',
                        event_date=datetime.utcnow(),
                        previous_interval_minutes=previous_interval,
                        new_interval_minutes=optimal_interval,
                        check_interval_minutes=optimal_interval,
                        active_strategies_count=active_count,
                        event_data={
                            'reason': 'intelligent_scheduling',
                            'min_interval': scheduler.min_check_interval_minutes,
                            'max_interval': scheduler.max_check_interval_minutes
                        }
                    )
                    event_db.add(event_log)
                    event_db.commit()
                    event_db.close()
            except Exception as e:
                logger.warning(f"Failed to save interval adjustment event log: {e}")
            
            logger.warning(f"[Scheduler] ✅ Interval adjusted to {optimal_interval}min")
        
    except Exception as e:
        logger.warning(f"Error adjusting check interval: {e}")

