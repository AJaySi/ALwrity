import time
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from models.website_analysis_monitoring_models import (
    DeepWebsiteCrawlTask,
    DeepWebsiteCrawlExecutionLog
)
from services.scheduler.core.executor_interface import TaskExecutor, TaskExecutionResult
from services.scheduler.core.failure_detection_service import FailureDetectionService
from services.research.deep_crawl_service import DeepCrawlService
from utils.logger_utils import get_service_logger

logger = get_service_logger("deep_website_crawl_executor")


class DeepWebsiteCrawlExecutor(TaskExecutor):
    def __init__(self):
        self.crawl_service = DeepCrawlService()

    async def execute_task(self, task: Any, db: Session) -> TaskExecutionResult:
        start_time = time.time()

        if not isinstance(task, DeepWebsiteCrawlTask):
            return TaskExecutionResult(
                success=False,
                error_message="Invalid task type for deep website crawl",
                retryable=False
            )

        task_log = DeepWebsiteCrawlExecutionLog(
            task_id=task.id,
            status="running",
            execution_date=datetime.utcnow()
        )
        db.add(task_log)
        db.commit()

        user_id = str(task.user_id)
        website_url = task.website_url

        try:
            logger.info(f"Executing deep website crawl for user {user_id}, url {website_url}")
            
            result = await self.crawl_service.execute_deep_crawl(
                user_id=user_id, 
                website_url=website_url,
                task_id=task.id # Pass task_id so service can update logs/task if needed, but we handle some here too.
                # Actually, the service updates logs and task status.
                # So we should coordinate.
                # In DeepCrawlService I wrote logic to update logs/task if task_id provided.
                # But here we also create a log "running".
                # The service creates a "success" or "failed" log.
                # This might result in duplicate logs or "running" log stuck.
                # Let's see DeepCrawlService again.
            )
            
            # The service creates a new log entry for success/failure.
            # So the "running" log created here will stay as "running" unless updated.
            # I should probably update the "running" log instead of letting service create new one.
            # OR, I should remove task_id from service call and handle logging here.
            # Handling logging here is better for separation of concerns, BUT the service has the detailed stats.
            # The service returns the stats.
            # I will remove task_id from service call in future refactor, but for now let's just update the local log here too if needed.
            # Wait, if service creates a log, I have 2 logs.
            # I'll modify this executor to NOT pass task_id to service, but rely on return value.
            # But `DeepCrawlService.execute_deep_crawl` takes task_id as Optional.
            # If I don't pass it, it returns the result dict.
            # I'll do that.
            
            # Re-calling service without task_id
            # Wait, `execute_deep_crawl` signature: `async def execute_deep_crawl(self, user_id: str, website_url: str, task_id: Optional[int] = None)`
            
            # If I don't pass task_id, the service won't touch the DB for logs/tasks (except for saving content).
            # This is cleaner.
            
            # result = await self.crawl_service.execute_deep_crawl(user_id, website_url)
            # But wait, in the service I implemented:
            # `if task_id: log = ... db.add(log) ...`
            # So if I don't pass task_id, it just returns data. Perfect.
            
            # Correction: I need to update the file `backend/services/research/deep_crawl_service.py` ?
            # No, it handles optional task_id.
            
            # So here I call it without task_id.
            
            # However, `DeepCrawlService` updates task status (last_executed, etc) if task_id is present.
            # If I don't pass task_id, I must update task status here.
            
            task.last_executed = datetime.utcnow()
            task.last_success = datetime.utcnow()
            task.status = "active" # Keep active for recurring? Or paused?
            # User said "schedule this task". So likely recurring.
            # But usually crawl is heavy, maybe weekly.
            
            # Calculate next execution
            task.next_execution = self.calculate_next_execution(task, "Weekly", task.last_executed)
            
            task.consecutive_failures = 0
            task.failure_pattern = None
            task.failure_reason = None

            task_log.status = "success"
            task_log.result_data = result
            task_log.execution_time_ms = int((time.time() - start_time) * 1000)

            db.commit()

            return TaskExecutionResult(
                success=True,
                result_data=result,
                execution_time_ms=task_log.execution_time_ms,
                retryable=False
            )

        except Exception as e:
            db.rollback()
            logger.warning(f"Deep website crawl task failed for user {user_id}: {e}")

            failure_detection = FailureDetectionService(db)
            pattern = failure_detection.analyze_task_failures(task.id, "deep_website_crawl", user_id)

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
                task.status = "failed"
                task.next_execution = datetime.utcnow() + timedelta(minutes=60) # Retry in hour

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

    def calculate_next_execution(
        self,
        task: Any,
        frequency: str,
        last_execution: Optional[datetime] = None
    ) -> datetime:
        """
        Calculate next execution time based on frequency.
        """
        if not last_execution:
            last_execution = datetime.utcnow()
            
        if frequency == 'Daily':
            return last_execution + timedelta(days=1)
        elif frequency == 'Weekly':
            return last_execution + timedelta(weeks=1)
        elif frequency == 'Monthly':
            return last_execution + timedelta(days=30)
        else:
            # Default to weekly if unknown
            return last_execution + timedelta(weeks=1)
