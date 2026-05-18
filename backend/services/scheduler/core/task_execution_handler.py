"""
Task Execution Handler
Handles asynchronous execution of individual tasks with proper session isolation.
"""

from typing import TYPE_CHECKING, Any, Dict, Optional
from datetime import datetime
from sqlalchemy.orm import object_session

from services.database import get_db_session
from services.intelligence.agents.market_signal_detector import get_market_signal_summary
from utils.logger_utils import get_service_logger
from ..utils.traffic_control import (
    apply_recalibrated_window_to_task,
    compute_recalibrated_deployment_window,
    upsert_deferral_metadata,
)
from .exception_handler import (
    SchedulerException, TaskExecutionError, DatabaseError, SchedulerConfigError
)

if TYPE_CHECKING:
    from .scheduler import TaskScheduler

logger = get_service_logger("task_execution_handler")

NCI_HIGH_THRESHOLD = 0.65
PUBLISH_TASK_TYPES = {"publish", "content_publish", "social_publish", "daily_publish_task"}


def _is_publish_capable_task(task_type: str, task: Any) -> bool:
    if task_type in PUBLISH_TASK_TYPES or "publish" in (task_type or ""):
        return True
    if getattr(task, "pillar_id", None) == "publish":
        return True
    if getattr(task, "action_type", None) == "publish":
        return True
    return bool(getattr(task, "can_publish", False))


def _extract_nci(summary: Dict[str, Any]) -> float:
    high_priority = float(summary.get("high_priority_signals", 0) or 0)
    total = float(summary.get("total_signals", 0) or 0)
    avg_impact = float(summary.get("average_impact_score", 0) or 0)
    urgency_ratio = (high_priority / total) if total > 0 else 0.0
    return min(1.0, max(0.0, (urgency_ratio * 0.7) + (avg_impact * 0.3)))


async def execute_task_async(
    scheduler: 'TaskScheduler',
    task_type: str,
    task: Any,
    summary: Optional[Dict[str, Any]] = None,
    execution_source: str = "scheduler",  # "scheduler" or "manual"
    user_id: Optional[str] = None
):
    """
    Execute a single task asynchronously with user isolation.
    
    Each task gets its own database session to prevent concurrent access issues,
    as SQLAlchemy sessions are not async-safe or concurrent-safe.
    
    User context is extracted and tracked for user isolation.
    
    Args:
        scheduler: TaskScheduler instance
        task_type: Type of task
        task: Task instance from database (detached from original session)
        summary: Optional summary dict to update with execution results
        user_id: Optional user ID for user isolation (overrides extraction from task)
    """
    task_id = f"{task_type}_{getattr(task, 'id', id(task))}"
    db = None
    
    try:
        # Extract user context if available (for user isolation tracking)
        if user_id is None:
            try:
                if hasattr(task, 'strategy') and task.strategy:
                    user_id = getattr(task.strategy, 'user_id', None)
                elif hasattr(task, 'strategy_id') and task.strategy_id:
                    # Will query user_id after we have db session
                    pass
                elif hasattr(task, 'user_id') and task.user_id:
                    # Direct user_id on task object
                    user_id = task.user_id
            except Exception as e:
                logger.debug(f"Could not extract user_id before execution for task {task_id}: {e}")
        
        # Log task execution start (detailed for important tasks)
        task_db_id = getattr(task, 'id', None)
        if task_db_id:
            logger.debug(f"[Scheduler] ▶️ Executing {task_type} task {task_db_id} | user_id: {user_id}")
        
        # Create a new database session for this async task
        # SQLAlchemy sessions are not async-safe and cannot be shared across concurrent tasks
        db = get_db_session(user_id)
        if db is None:
            error = DatabaseError(
                message=f"Failed to get database session for task {task_id}",
                user_id=user_id,
                task_id=getattr(task, 'id', None),
                task_type=task_type
            )
            scheduler.exception_handler.handle_exception(error, log_level="error")
            scheduler.stats['tasks_failed'] += 1
            scheduler._update_user_stats(user_id, success=False)
            return
        
        # Set database session for exception handler
        scheduler.exception_handler.db = db
        
        # Merge the detached task object into this session
        # The task object was loaded in a different session and is now detached
        from sqlalchemy.inspection import inspect
        is_model = False
        try:
            inspect(task)
            is_model = True
        except:
            pass

        if is_model and object_session(task) is None:
            # Task is detached, need to merge it into this session
            task = db.merge(task)
        
        # Extract user_id after merge if not already available
        if user_id is None and hasattr(task, 'strategy'):
            try:
                if task.strategy:
                    user_id = getattr(task.strategy, 'user_id', None)
                elif hasattr(task, 'strategy_id'):
                    # Query strategy if relationship not loaded
                    from models.enhanced_strategy_models import EnhancedContentStrategy
                    strategy = db.query(EnhancedContentStrategy).filter(
                        EnhancedContentStrategy.id == task.strategy_id
                    ).first()
                    if strategy:
                        user_id = strategy.user_id
            except Exception as e:
                logger.debug(f"Could not extract user_id after merge for task {task_id}: {e}")
        
        # Check if task is in cool-off (skip if scheduler-triggered, allow if manual)
        if execution_source == "scheduler":
            if hasattr(task, 'status') and task.status == "needs_intervention":
                logger.warning(
                    f"[Scheduler] ⏸️ Skipping task {task_id} - marked for human intervention. "
                    f"Use manual trigger to retry."
                )
                scheduler.stats['tasks_skipped'] += 1
                if summary:
                    summary.setdefault('skipped', 0)
                    summary['skipped'] += 1
                return
        
        # Get executor for this task type
        try:
            executor = scheduler.registry.get_executor(task_type)
        except Exception as e:
            error = SchedulerConfigError(
                message=f"Failed to get executor for task type {task_type}: {str(e)}",
                user_id=user_id,
                context={
                    "task_id": getattr(task, 'id', None),
                    "task_type": task_type
                },
                original_error=e
            )
            scheduler.exception_handler.handle_exception(error)
            scheduler.stats['tasks_failed'] += 1
            scheduler._update_user_stats(user_id, success=False)
            return
        
        # Pre-flight hook for publish-capable tasks:
        # evaluate market volatility/NCI before dispatching publish execution.
        if _is_publish_capable_task(task_type, task) and user_id:
            market_summary = await get_market_signal_summary(str(user_id))
            nci_score = _extract_nci(market_summary)
            if nci_score >= NCI_HIGH_THRESHOLD:
                task_db_id = getattr(task, "id", "unknown")
                reason_code = "high_nci"
                marker_epoch = datetime.utcnow().strftime("%Y%m%d%H")
                deferral_marker = f"{task_type}:{task_db_id}:{reason_code}:{marker_epoch}"

                recalibrated_window = compute_recalibrated_deployment_window()
                apply_recalibrated_window_to_task(task, recalibrated_window)

                metadata = {
                    "deferral_marker": deferral_marker,
                    "reason": reason_code,
                    "nci_score": nci_score,
                    "market_signal_summary": {
                        "total_signals": market_summary.get("total_signals", 0),
                        "high_priority_signals": market_summary.get("high_priority_signals", 0),
                        "average_impact_score": market_summary.get("average_impact_score", 0),
                    },
                    "recalibrated_window": recalibrated_window,
                    "deferred_at": datetime.utcnow().isoformat(),
                }
                upsert_deferral_metadata(task, metadata)

                if hasattr(task, "status"):
                    task.status = "deferred"
                db.commit()

                scheduler.stats['tasks_skipped'] += 1
                scheduler._update_user_stats(user_id, success=True)
                if summary:
                    summary.setdefault('skipped', 0)
                    summary['skipped'] += 1
                logger.info(
                    f"[Scheduler] ⏸️ Deferred publish task {task_type}_{task_db_id} due to high NCI "
                    f"(nci={nci_score:.3f}, threshold={NCI_HIGH_THRESHOLD})"
                )
                return

        # Execute task with its own session (with error handling)
        try:
            result = await executor.execute_task(task, db)
            
            # Handle result and update statistics
            if result.success:
                scheduler.stats['tasks_executed'] += 1
                scheduler._update_user_stats(user_id, success=True)
                if summary:
                    summary['executed'] += 1
                logger.debug(f"[Scheduler] ✅ Task {task_id} executed successfully | user_id: {user_id} | time: {result.execution_time_ms}ms")
            else:
                scheduler.stats['tasks_failed'] += 1
                scheduler._update_user_stats(user_id, success=False)
                if summary:
                    summary['failed'] += 1
                
                # Create structured error for failed execution
                error = TaskExecutionError(
                    message=result.error_message or "Task execution failed",
                    user_id=user_id,
                    task_id=getattr(task, 'id', None),
                    task_type=task_type,
                    execution_time_ms=result.execution_time_ms,
                    context={"result_data": result.result_data}
                )
                scheduler.exception_handler.handle_exception(error, log_level="warning")
                
                logger.warning(f"[Scheduler] ❌ Task {task_id} failed | user_id: {user_id} | error: {result.error_message}")
                
                # Retry logic if enabled
                if scheduler.enable_retries and result.retryable:
                    await scheduler._schedule_retry(task, result.retry_delay)
                    
        except SchedulerException as e:
            # Re-raise scheduler exceptions (they're already handled)
            raise
        except Exception as e:
            # Wrap unexpected exceptions
            error = TaskExecutionError(
                message=f"Unexpected error during task execution: {str(e)}",
                user_id=user_id,
                task_id=getattr(task, 'id', None),
                task_type=task_type,
                original_error=e
            )
            scheduler.exception_handler.handle_exception(error)
            scheduler.stats['tasks_failed'] += 1
            scheduler._update_user_stats(user_id, success=False)
        
    except SchedulerException as e:
        # Handle scheduler exceptions
        scheduler.exception_handler.handle_exception(e)
        scheduler.stats['tasks_failed'] += 1
        scheduler._update_user_stats(user_id, success=False)
    except Exception as e:
        # Handle any other unexpected errors
        error = TaskExecutionError(
            message=f"Unexpected error in task execution wrapper: {str(e)}",
            user_id=user_id,
            task_id=getattr(task, 'id', None),
            task_type=task_type,
            original_error=e
        )
        scheduler.exception_handler.handle_exception(error)
        scheduler.stats['tasks_failed'] += 1
        scheduler._update_user_stats(user_id, success=False)
    finally:
        # Clean up database session
        if db:
            try:
                db.close()
            except Exception as e:
                logger.error(f"Error closing database session for task {task_id}: {e}")
        
        # Remove from active executions
        if task_id in scheduler.active_executions:
            del scheduler.active_executions[task_id]
