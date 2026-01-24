"""Statistics calculation utilities for Scheduler API"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from loguru import logger

from models.scheduler_models import SchedulerEventLog


def rebuild_cumulative_stats_from_events(db: Session) -> Dict[str, int]:
    """
    Rebuild cumulative stats by aggregating all check_cycle events from event logs.
    This is used as a fallback when the cumulative stats table doesn't exist or is invalid.

    Args:
        db: Database session

    Returns:
        Dictionary with cumulative stats
    """
    try:
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
            total_check_cycles, cumulative_tasks_found, cumulative_tasks_executed, cumulative_tasks_failed = result

            # Handle None values from SUM operations
            cumulative_stats = {
                'total_check_cycles': total_check_cycles or 0,
                'cumulative_tasks_found': cumulative_tasks_found or 0,
                'cumulative_tasks_executed': cumulative_tasks_executed or 0,
                'cumulative_tasks_failed': cumulative_tasks_failed or 0,
                'cumulative_tasks_skipped': 0  # This field may not exist in older versions
            }

            logger.debug(f"[Stats] Rebuilt cumulative stats from {total_check_cycles} events: {cumulative_stats}")
            return cumulative_stats
        else:
            logger.warning("[Stats] No check_cycle events found, returning zeros")
            return {
                'total_check_cycles': 0,
                'cumulative_tasks_found': 0,
                'cumulative_tasks_executed': 0,
                'cumulative_tasks_failed': 0,
                'cumulative_tasks_skipped': 0
            }

    except Exception as e:
        logger.error(f"[Stats] Error rebuilding cumulative stats from events: {e}", exc_info=True)
        # Return safe defaults
        return {
            'total_check_cycles': 0,
            'cumulative_tasks_found': 0,
            'cumulative_tasks_executed': 0,
            'cumulative_tasks_failed': 0,
            'cumulative_tasks_skipped': 0
        }


def validate_cumulative_stats(cumulative_stats: Dict[str, int], db: Session) -> Dict[str, int]:
    """
    Validate cumulative stats against event logs and rebuild if necessary.

    Args:
        cumulative_stats: Current cumulative stats
        db: Database session

    Returns:
        Validated or rebuilt cumulative stats
    """
    try:
        # Count actual check_cycle events
        check_cycle_count = db.query(
            func.count(SchedulerEventLog.id)
        ).filter(
            SchedulerEventLog.event_type == 'check_cycle'
        ).scalar() or 0

        if cumulative_stats['total_check_cycles'] != check_cycle_count:
            logger.warning(
                f"[Stats] Validation mismatch: cumulative_stats.total_check_cycles="
                f"{cumulative_stats['total_check_cycles']} vs event_logs.count={check_cycle_count}. "
                "Rebuilding cumulative stats from event logs..."
            )
            return rebuild_cumulative_stats_from_events(db)
        else:
            logger.debug(f"[Stats] Cumulative stats validated: {cumulative_stats['total_check_cycles']} check cycles")
            return cumulative_stats

    except Exception as e:
        logger.error(f"[Stats] Error validating cumulative stats: {e}", exc_info=True)
        return rebuild_cumulative_stats_from_events(db)


def calculate_event_log_statistics(db: Session) -> Dict[str, Any]:
    """
    Calculate comprehensive statistics for event logs.

    Args:
        db: Database session

    Returns:
        Dictionary with event log statistics
    """
    try:
        # Basic counts
        total_events = db.query(func.count(SchedulerEventLog.id)).scalar() or 0

        # Events by type
        events_by_type_result = db.query(
            SchedulerEventLog.event_type,
            func.count(SchedulerEventLog.id)
        ).group_by(SchedulerEventLog.event_type).all()

        events_by_type = {event_type: count for event_type, count in events_by_type_result}

        # Date range
        oldest_event = db.query(func.min(SchedulerEventLog.timestamp)).scalar()
        newest_event = db.query(func.max(SchedulerEventLog.timestamp)).scalar()

        # Aggregations
        total_tasks_found = db.query(func.sum(SchedulerEventLog.tasks_found)).scalar() or 0
        total_tasks_executed = db.query(func.sum(SchedulerEventLog.tasks_executed)).scalar() or 0
        total_tasks_failed = db.query(func.sum(SchedulerEventLog.tasks_failed)).scalar() or 0

        # Calculate average duration for completed events
        avg_duration_result = db.query(func.avg(SchedulerEventLog.duration_seconds)).filter(
            SchedulerEventLog.duration_seconds.isnot(None)
        ).scalar()

        return {
            'total_events': total_events,
            'events_by_type': events_by_type,
            'oldest_event': oldest_event,
            'newest_event': newest_event,
            'average_duration_seconds': float(avg_duration_result) if avg_duration_result else None,
            'total_tasks_found': total_tasks_found,
            'total_tasks_executed': total_tasks_executed,
            'total_tasks_failed': total_tasks_failed,
            'total_tasks_skipped': 0  # May not be tracked in all versions
        }

    except Exception as e:
        logger.error(f"[Stats] Error calculating event log statistics: {e}", exc_info=True)
        return {
            'total_events': 0,
            'events_by_type': {},
            'oldest_event': None,
            'newest_event': None,
            'average_duration_seconds': None,
            'total_tasks_found': 0,
            'total_tasks_executed': 0,
            'total_tasks_failed': 0,
            'total_tasks_skipped': 0
        }