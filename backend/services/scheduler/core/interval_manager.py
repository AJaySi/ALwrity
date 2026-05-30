"""
Interval Manager
Determines optimal scheduling interval at startup based on active strategies.
"""

from typing import TYPE_CHECKING
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

    Only one strategy can be active per user at a time, so this is a simple
    exists/not-exists check: does any user have an active strategy?

    Args:
        scheduler: TaskScheduler instance
        min_interval: Minimum check interval in minutes
        max_interval: Maximum check interval in minutes

    Returns:
        Optimal check interval in minutes
    """
    has_active = False
    user_ids = get_all_user_ids()

    for user_id in user_ids:
        db = None
        try:
            db = get_session_for_user(user_id)
            if db:
                from services.active_strategy_service import ActiveStrategyService
                active_strategy_service = ActiveStrategyService(db_session=db)
                if active_strategy_service.has_active_strategies_with_tasks():
                    has_active = True
                    break
        except Exception as e:
            logger.warning(f"Error checking active strategies for user {user_id}: {e}")
        finally:
            if db:
                db.close()

    # Note: stats['active_strategies_count'] is set by check_cycle_handler
    # with the actual per-user count for accurate logging.

    if has_active:
        logger.info(f"Active strategies found - using {min_interval}min interval")
        return min_interval
    else:
        logger.info(f"No active strategies found - using {max_interval}min interval")
        return max_interval
