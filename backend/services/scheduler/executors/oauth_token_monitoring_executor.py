"""
OAuth Token Monitoring Task Executor
Handles execution of OAuth token monitoring tasks for connected platforms.
"""

import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from ..core.executor_interface import TaskExecutor, TaskExecutionResult
from ..core.exception_handler import TaskExecutionError, DatabaseError, SchedulerExceptionHandler
from models.oauth_token_monitoring_models import OAuthTokenMonitoringTask, OAuthTokenExecutionLog
from models.subscription_models import UsageAlert
from utils.logger_utils import get_service_logger

from services.integrations.registry import get_provider

logger = get_service_logger("oauth_token_monitoring_executor")


class OAuthTokenMonitoringExecutor(TaskExecutor):
    """
    Executor for OAuth token monitoring tasks.
    
    Handles:
    - Checking token validity and expiration
    - Attempting automatic token refresh
    - Logging results and updating task status
    - One-time refresh attempt (no automatic retries on failure)
    """
    
    def __init__(self):
        self.logger = logger
        self.exception_handler = SchedulerExceptionHandler()
        # Expiration warning window (7 days before expiration)
        self.expiration_warning_days = 7
    
    async def execute_task(self, task: OAuthTokenMonitoringTask, db: Session) -> TaskExecutionResult:
        """
        Execute an OAuth token monitoring task.
        
        This checks token status and attempts refresh if needed.
        If refresh fails, marks task as failed and does not retry automatically.
        
        Args:
            task: OAuthTokenMonitoringTask instance
            db: Database session
            
        Returns:
            TaskExecutionResult
        """
        start_time = time.time()
        user_id = task.user_id
        platform = task.platform
        
        try:
            self.logger.info(
                f"Executing OAuth token monitoring: task_id={task.id} | "
                f"user_id={user_id} | platform={platform}"
            )
            
            # Create execution log
            execution_log = OAuthTokenExecutionLog(
                task_id=task.id,
                execution_date=datetime.utcnow(),
                status='running'
            )
            db.add(execution_log)
            db.flush()
            
            # Check and refresh token
            result = await self._check_and_refresh_token(task, db)

            if result.success:
                self.logger.info(
                    f"OAuth token monitoring succeeded: task_id={task.id} | "
                    f"platform={platform} | status={result.result_data.get('status') if result.result_data else 'unknown'}"
                )
            else:
                self.logger.warning(
                    f"OAuth token monitoring failed: task_id={task.id} | "
                    f"platform={platform} | error={result.error_message}"
                )
            
            # Update execution log
            execution_time_ms = int((time.time() - start_time) * 1000)
            execution_log.status = 'success' if result.success else 'failed'
            execution_log.result_data = result.result_data
            execution_log.error_message = result.error_message
            execution_log.execution_time_ms = execution_time_ms
            
            # Update task based on result
            task.last_check = datetime.utcnow()
            
            if result.success:
                task.last_success = datetime.utcnow()
                task.status = 'active'
                task.failure_reason = None
                # Reset failure tracking on success
                task.consecutive_failures = 0
                task.failure_pattern = None
                # Schedule next check (7 days from now)
                task.next_check = self.calculate_next_execution(
                    task=task,
                    frequency='Weekly',
                    last_execution=task.last_check
                )
            else:
                # Analyze failure pattern
                from services.scheduler.core.failure_detection_service import FailureDetectionService
                failure_detection = FailureDetectionService(db)
                pattern = failure_detection.analyze_task_failures(
                    task.id, "oauth_token_monitoring", task.user_id
                )
                
                task.last_failure = datetime.utcnow()
                task.failure_reason = result.error_message
                
                if pattern and pattern.should_cool_off:
                    # Mark task for human intervention
                    task.status = "needs_intervention"
                    task.consecutive_failures = pattern.consecutive_failures
                    task.failure_pattern = {
                        "consecutive_failures": pattern.consecutive_failures,
                        "recent_failures": pattern.recent_failures,
                        "failure_reason": pattern.failure_reason.value,
                        "error_patterns": pattern.error_patterns,
                        "cool_off_until": (datetime.utcnow() + timedelta(days=7)).isoformat()
                    }
                    # Clear next_check - task won't run automatically
                    task.next_check = None
                    
                    self.logger.warning(
                        f"Task {task.id} marked for human intervention: "
                        f"{pattern.consecutive_failures} consecutive failures, "
                        f"reason: {pattern.failure_reason.value}"
                    )
                else:
                    # Normal failure handling
                    task.status = 'failed'
                    task.consecutive_failures = (task.consecutive_failures or 0) + 1
                    # Do NOT update next_check - wait for manual trigger
                
                self.logger.warning(
                    f"OAuth token refresh failed for user {user_id}, platform {platform}. "
                    f"{'Task marked for human intervention' if pattern and pattern.should_cool_off else 'Task marked as failed. No automatic retry will be scheduled.'}"
                )
                
                # Create UsageAlert notification for the user
                self._create_failure_alert(user_id, platform, result.error_message, result.result_data, db)
            
            task.updated_at = datetime.utcnow()
            db.commit()
            
            return result
            
        except Exception as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            # Set database session for exception handler
            self.exception_handler.db = db
            
            # Create structured error
            error = TaskExecutionError(
                message=f"Error executing OAuth token monitoring task {task.id}: {str(e)}",
                user_id=user_id,
                task_id=task.id,
                task_type="oauth_token_monitoring",
                execution_time_ms=execution_time_ms,
                context={
                    "platform": platform,
                    "user_id": user_id
                },
                original_error=e
            )
            
            # Handle exception with structured logging
            self.exception_handler.handle_exception(error)
            
            # Update execution log with error
            try:
                execution_log = OAuthTokenExecutionLog(
                    task_id=task.id,
                    execution_date=datetime.utcnow(),
                    status='failed',
                    error_message=str(e),
                    execution_time_ms=execution_time_ms,
                    result_data={
                        "error_type": error.error_type.value,
                        "severity": error.severity.value,
                        "context": error.context
                    }
                )
                db.add(execution_log)
                
                task.last_failure = datetime.utcnow()
                task.failure_reason = str(e)
                task.status = 'failed'
                task.last_check = datetime.utcnow()
                task.updated_at = datetime.utcnow()
                # Do NOT update next_check - wait for manual trigger
                
                # Create UsageAlert notification for the user
                self._create_failure_alert(user_id, task.platform, str(e), None, db)
                
                db.commit()
            except Exception as commit_error:
                db_error = DatabaseError(
                    message=f"Error saving execution log: {str(commit_error)}",
                    user_id=user_id,
                    task_id=task.id,
                    original_error=commit_error
                )
                self.exception_handler.handle_exception(db_error)
                db.rollback()
            
            return TaskExecutionResult(
                success=False,
                error_message=str(e),
                execution_time_ms=execution_time_ms,
                retryable=False,  # Do not retry automatically
                retry_delay=0
            )
    
    async def _check_and_refresh_token(
        self,
        task: OAuthTokenMonitoringTask,
        db: Session
    ) -> TaskExecutionResult:
        """Check token status and attempt refresh if needed using the integration registry."""
        platform = task.platform
        user_id = task.user_id

        try:
            self.logger.info(f"Checking token for platform: {platform}, user: {user_id}")
            provider = get_provider(platform)
            if not provider:
                return TaskExecutionResult(
                    success=False,
                    error_message=f"Unsupported platform: {platform}",
                    result_data={
                        'platform': platform,
                        'user_id': user_id,
                        'error': 'Unsupported platform'
                    },
                    retryable=False
                )

            status = provider.get_connection_status(user_id)
            now = datetime.utcnow()

            if not status.connected:
                return TaskExecutionResult(
                    success=False,
                    error_message="OAuth connection not found",
                    result_data={
                        'platform': platform,
                        'user_id': user_id,
                        'status': 'not_connected',
                        'check_time': now.isoformat(),
                        'details': status.details,
                        'warnings': status.warnings,
                    },
                    retryable=False,
                )

            needs_refresh = False
            if status.expires_at:
                try:
                    days_until_expiry = (status.expires_at - now).days
                    needs_refresh = days_until_expiry < self.expiration_warning_days
                except Exception:
                    needs_refresh = False

            if status.refreshable and needs_refresh:
                refresh_result = provider.refresh_token(user_id)
                if refresh_result and refresh_result.success:
                    return TaskExecutionResult(
                        success=True,
                        result_data={
                            'platform': platform,
                            'user_id': user_id,
                            'status': 'refreshed',
                            'check_time': now.isoformat(),
                            'message': 'Token refreshed successfully',
                            'expires_at': refresh_result.expires_at.isoformat() if refresh_result.expires_at else None,
                        },
                    )
                return TaskExecutionResult(
                    success=False,
                    error_message="Token refresh failed",
                    result_data={
                        'platform': platform,
                        'user_id': user_id,
                        'status': 'refresh_failed',
                        'check_time': now.isoformat(),
                    },
                    retryable=False,
                )

            return TaskExecutionResult(
                success=True,
                result_data={
                    'platform': platform,
                    'user_id': user_id,
                    'status': 'valid',
                    'check_time': now.isoformat(),
                    'message': 'Token is valid',
                },
            )

        except Exception as e:
            self.logger.error(
                f"Error checking/refreshing token for platform {platform}, user {user_id}: {e}",
                exc_info=True
            )
            return TaskExecutionResult(
                success=False,
                error_message=f"Token check failed: {str(e)}",
                result_data={
                    'platform': platform,
                    'user_id': user_id,
                    'error': str(e)
                },
                retryable=False  # Do not retry automatically
            )
    
    def _create_failure_alert(
        self,
        user_id: str,
        platform: str,
        error_message: str,
        result_data: Optional[Dict[str, Any]],
        db: Session
    ):
        """
        Create a UsageAlert notification when OAuth token refresh fails.
        
        Args:
            user_id: User ID
            platform: Platform identifier (gsc, bing, wordpress, wix)
            error_message: Error message from token check
            result_data: Optional result data from token check
            db: Database session
        """
        try:
            result_data = result_data or {}
            # Determine severity based on error type
            status = result_data.get('status', 'unknown')
            
            if status in ['expired', 'refresh_failed']:
                severity = 'error'
                alert_type = 'oauth_token_failure'
            elif status in ['expiring_soon', 'not_found']:
                severity = 'warning'
                alert_type = 'oauth_token_warning'
            else:
                severity = 'error'
                alert_type = 'oauth_token_failure'
            
            # Format platform name for display
            platform_names = {
                'gsc': 'Google Search Console',
                'bing': 'Bing Webmaster Tools',
                'wordpress': 'WordPress',
                'wix': 'Wix'
            }
            platform_display = platform_names.get(platform, platform.upper())
            
            # Create alert title and message
            if status == 'expired':
                title = f"{platform_display} Token Expired"
                message = (
                    f"Your {platform_display} access token has expired and could not be automatically renewed. "
                    f"Please reconnect your {platform_display} account to continue using this integration."
                )
            elif status == 'expiring_soon':
                title = f"{platform_display} Token Expiring Soon"
                message = (
                    f"Your {platform_display} access token will expire soon. "
                    f"Please reconnect your {platform_display} account to avoid interruption."
                )
            elif status == 'refresh_failed':
                title = f"{platform_display} Token Renewal Failed"
                message = (
                    f"Failed to automatically renew your {platform_display} access token. "
                    f"Please reconnect your {platform_display} account. "
                    f"Error: {error_message}"
                )
            elif status == 'not_found':
                title = f"{platform_display} Token Not Found"
                message = (
                    f"No {platform_display} access token found. "
                    f"Please connect your {platform_display} account in the onboarding settings."
                )
            else:
                title = f"{platform_display} Token Error"
                message = (
                    f"An error occurred while checking your {platform_display} access token. "
                    f"Please reconnect your {platform_display} account. "
                    f"Error: {error_message}"
                )
            
            # Get current billing period (YYYY-MM format)
            from datetime import datetime
            billing_period = datetime.utcnow().strftime("%Y-%m")
            
            # Create UsageAlert
            alert = UsageAlert(
                user_id=user_id,
                alert_type=alert_type,
                threshold_percentage=0,  # Not applicable for OAuth alerts
                provider=None,  # Not applicable for OAuth alerts
                title=title,
                message=message,
                severity=severity,
                is_sent=False,  # Will be marked as sent when frontend polls
                is_read=False,
                billing_period=billing_period
            )
            
            db.add(alert)
            # Note: We don't commit here - let the caller commit
            # This allows the alert to be created atomically with the task update

            self.logger.info(
                f"Created UsageAlert for OAuth token failure: user={user_id}, "
                f"platform={platform}, severity={severity}, status={status}"
            )
            
        except Exception as e:
            # Don't fail the entire task execution if alert creation fails
            self.logger.error(
                f"Failed to create UsageAlert for OAuth token failure: {e}",
                exc_info=True
            )
    
    def calculate_next_execution(
        self,
        task: OAuthTokenMonitoringTask,
        frequency: str,
        last_execution: Optional[datetime] = None
    ) -> datetime:
        """
        Calculate next execution time based on frequency.
        
        For OAuth token monitoring, frequency is always 'Weekly' (7 days).
        
        Args:
            task: OAuthTokenMonitoringTask instance
            frequency: Frequency string (should be 'Weekly' for token monitoring)
            last_execution: Last execution datetime (defaults to task.last_check or now)
            
        Returns:
            Next execution datetime
        """
        if last_execution is None:
            last_execution = task.last_check if task.last_check else datetime.utcnow()
        
        # OAuth token monitoring is always weekly (7 days)
        if frequency == 'Weekly':
            return last_execution + timedelta(days=7)
        else:
            # Default to weekly if frequency is not recognized
            self.logger.warning(
                f"Unknown frequency '{frequency}' for OAuth token monitoring task {task.id}. "
                f"Defaulting to Weekly (7 days)."
            )
            return last_execution + timedelta(days=7)
