"""
SIF Indexing Executor
Executes SIF indexing tasks (Step 2 metadata and User Website Content).
"""

import time
from datetime import datetime, timedelta
from typing import Any, Optional

from sqlalchemy.orm import Session

from models.website_analysis_monitoring_models import (
    SIFIndexingTask,
    SIFIndexingExecutionLog
)
from services.scheduler.core.executor_interface import TaskExecutor, TaskExecutionResult
from services.scheduler.core.failure_detection_service import FailureDetectionService
from services.intelligence.sif_integration import SIFIntegrationService
from utils.logger_utils import get_service_logger

logger = get_service_logger("sif_indexing_executor")


class SIFIndexingExecutor(TaskExecutor):
    """
    Executor for SIF indexing tasks.
    
    Handles:
    - Indexing Step 2 Website Analysis Data (Metadata)
    - Harvesting and Indexing User Website Content (Deep Crawl)
    - Scheduling recurring updates (snapshot refresh)
    """
    
    def __init__(self):
        pass

    async def execute_task(self, task: Any, db: Session) -> TaskExecutionResult:
        start_time = time.time()

        if not isinstance(task, SIFIndexingTask):
            return TaskExecutionResult(
                success=False,
                error_message="Invalid task type for SIF indexing",
                retryable=False
            )

        task_log = SIFIndexingExecutionLog(
            task_id=task.id,
            status="running",
            execution_date=datetime.utcnow()
        )
        db.add(task_log)
        db.commit()

        user_id = str(task.user_id)
        website_url = task.website_url

        try:
            logger.info(f"Executing SIF indexing for user {user_id} ({website_url})")
            
            # Initialize SIF Service
            sif_service = SIFIntegrationService(user_id)
            
            # 1. Sync Step 2 Metadata (WebsiteAnalysis, CompetitorAnalysis)
            metadata_synced = await sif_service.sync_onboarding_data_to_sif()
            
            # 2. Sync User Website Content (Deep Crawl / Snapshot)
            content_synced = await sif_service.sync_user_website_content(website_url)
            
            # Determine overall success
            # We consider it a success if at least one operation worked, or if both were attempted without error
            # But ideally, content sync is the heavy lifter.
            success = metadata_synced or content_synced
            
            if not success:
                logger.warning(f"SIF indexing completed but no data was synced/indexed for {user_id}")

            task.last_executed = datetime.utcnow()
            task.last_success = datetime.utcnow()
            
            # Schedule next execution (Recurring)
            frequency_hours = task.frequency_hours or 48
            task.next_execution = datetime.utcnow() + timedelta(hours=frequency_hours)
            task.status = "active"

            task.consecutive_failures = 0
            task.failure_pattern = None
            task.failure_reason = None

            task_log.status = "success"
            task_log.result_data = {
                "metadata_synced": metadata_synced,
                "content_synced": content_synced,
                "website_url": website_url
            }
            task_log.execution_time_ms = int((time.time() - start_time) * 1000)

            db.commit()

            return TaskExecutionResult(
                success=True,
                result_data=task_log.result_data,
                execution_time_ms=task_log.execution_time_ms,
                retryable=False
            )

        except Exception as e:
            db.rollback()
            logger.warning(f"SIF indexing task failed for user {user_id}: {e}")

            failure_detection = FailureDetectionService(db)
            pattern = failure_detection.analyze_task_failures(task.id, "sif_indexing", user_id)

            task.last_executed = datetime.utcnow()
            task.last_failure = datetime.utcnow()
            task.failure_reason = str(e)
            task.consecutive_failures = (task.consecutive_failures or 0) + 1

            if pattern and pattern.should_cool_off:
                task.status = "needs_intervention"
                task.failure_pattern = {
                    "consecutive_failures": pattern.consecutive_failures,
                    "recent_failures": pattern.recent_failures,
                    "failure_reason": pattern.failure_reason.value,
                    "error_patterns": pattern.error_patterns,
                    "cool_off_until": (datetime.utcnow() + timedelta(days=7)).isoformat()
                }
                task.next_execution = None
            else:
                # Retry sooner if it's a transient failure
                task.status = "active" # Keep active for retry
                task.next_execution = datetime.utcnow() + timedelta(minutes=60)

            task_log.status = "failed"
            task_log.error_message = str(e)
            task_log.execution_time_ms = int((time.time() - start_time) * 1000)

            db.add(task_log)
            db.commit()

            return TaskExecutionResult(
                success=False,
                error_message=str(e),
                execution_time_ms=task_log.execution_time_ms,
                retryable=(task.status != "needs_intervention"),
                retry_delay=3600
            )

    def calculate_next_execution(self, task: Any, frequency: str, last_execution: datetime = None) -> datetime:
        # Not strictly used here as we handle logic in execute_task, but good for interface compliance
        base = last_execution or datetime.utcnow()
        hours = getattr(task, 'frequency_hours', 48) or 48
        return base + timedelta(hours=hours)
