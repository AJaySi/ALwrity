"""
Core Task Scheduler Service
Pluggable task scheduler that can work with any task model.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
from sqlalchemy.orm import Session

from .executor_interface import TaskExecutor, TaskExecutionResult
from .task_registry import TaskRegistry
from .exception_handler import (
    SchedulerExceptionHandler, SchedulerException, TaskExecutionError, DatabaseError,
    TaskLoaderError, SchedulerConfigError
)
from services.database import get_db_session
from utils.logger_utils import get_service_logger
from ..utils.user_job_store import get_user_job_store_name
from models.scheduler_models import SchedulerEventLog
from .interval_manager import determine_optimal_interval, adjust_check_interval_if_needed
from .job_restoration import restore_persona_jobs
from .oauth_task_restoration import restore_oauth_monitoring_tasks
from .website_analysis_task_restoration import restore_website_analysis_tasks
from .platform_insights_task_restoration import restore_platform_insights_tasks
from .check_cycle_handler import check_and_execute_due_tasks
from .task_execution_handler import execute_task_async

logger = get_service_logger("task_scheduler")


class TaskScheduler:
    """
    Pluggable task scheduler that can work with any task model.
    
    Features:
    - Async task execution
    - Plugin-based executor system
    - Database-backed task persistence
    - Configurable check intervals
    - Automatic retry logic
    - User isolation: All tasks are filtered by user_id for isolation
    - Per-user job store context: Logs show user's website root for debugging
    
    User Isolation:
    - Tasks are filtered by user_id in task loaders
    - Execution logs include user_id for tracking
    - Per-user statistics are maintained
    - Job store names (based on website root) are logged for debugging
    """
    
    def __init__(
        self,
        check_interval_minutes: int = 15,
        max_concurrent_executions: int = 10,
        enable_retries: bool = True,
        max_retries: int = 3
    ):
        """
        Initialize the task scheduler.
        
        Args:
            check_interval_minutes: How often to check for due tasks
            max_concurrent_executions: Maximum concurrent task executions
            enable_retries: Whether to retry failed tasks
            max_retries: Maximum retry attempts
        """
        self.check_interval_minutes = check_interval_minutes
        self.max_concurrent_executions = max_concurrent_executions
        self.enable_retries = enable_retries
        self.max_retries = max_retries
        
        # Initialize APScheduler
        self.scheduler = AsyncIOScheduler(
            timezone='UTC',
            job_defaults={
                'coalesce': True,
                'max_instances': 1,
                'misfire_grace_time': 3600  # 1 hour grace period for missed jobs
            }
        )
        
        # Task executor registry
        self.registry = TaskRegistry()
        
        # Track running executions
        self.active_executions: Dict[str, asyncio.Task] = {}
        
        # Exception handler for robust error handling
        self.exception_handler = SchedulerExceptionHandler()
        
        # Intelligent scheduling configuration
        self.min_check_interval_minutes = 15  # Check every 15min when active strategies exist
        self.max_check_interval_minutes = 60  # Check every 60min when no active strategies
        self.current_check_interval_minutes = check_interval_minutes  # Current interval
        
        # Statistics
        self.stats = {
            'total_checks': 0,
            'tasks_found': 0,
            'tasks_executed': 0,
            'tasks_failed': 0,
            'tasks_skipped': 0,
            'last_check': None,
            'last_update': datetime.utcnow().isoformat(),  # Timestamp for frontend polling
            'per_user_stats': {},  # Track metrics per user for user isolation
            'active_strategies_count': 0,  # Track active strategies with tasks
            'last_interval_adjustment': None  # Track when interval was last adjusted
        }
        
        self._running = False
    
    def _get_trigger_for_interval(self, interval_minutes: int):
        """
        Get the appropriate trigger for the given interval.
        
        For intervals >= 60 minutes, use IntervalTrigger.
        For intervals < 60 minutes, use CronTrigger.
        
        Args:
            interval_minutes: Interval in minutes
            
        Returns:
            Appropriate APScheduler trigger
        """
        if interval_minutes >= 60:
            # Use IntervalTrigger for intervals >= 60 minutes
            return IntervalTrigger(minutes=interval_minutes)
        else:
            # Use CronTrigger for intervals < 60 minutes (valid range: 0-59)
            return CronTrigger(minute=f'*/{interval_minutes}')
    
    def register_executor(
        self,
        task_type: str,
        executor: TaskExecutor,
        task_loader: Callable[[Session], List[Any]]
    ):
        """
        Register a task executor for a specific task type.
        
        Args:
            task_type: Unique identifier for task type (e.g., 'monitoring_task')
            executor: TaskExecutor instance that handles execution
            task_loader: Function that loads due tasks from database
        """
        self.registry.register(task_type, executor, task_loader)
        logger.info(f"Registered executor for task type: {task_type}")
    
    async def start(self):
        """Start the scheduler with intelligent interval adjustment."""
        if self._running:
            logger.warning("Scheduler is already running")
            return
        
        try:
            # Determine initial check interval based on active strategies
            initial_interval = await determine_optimal_interval(
                self,
                self.min_check_interval_minutes,
                self.max_check_interval_minutes
            )
            self.current_check_interval_minutes = initial_interval
            
            # Add periodic job to check for due tasks
            self.scheduler.add_job(
                self._check_and_execute_due_tasks,
                trigger=self._get_trigger_for_interval(initial_interval),
                id='check_due_tasks',
                replace_existing=True
            )
            
            self.scheduler.start()
            self._running = True
            
            # Check for and execute any missed jobs that are still within grace period
            await self._execute_missed_jobs()
            
            # Restore one-time persona generation jobs for users who completed onboarding
            await restore_persona_jobs(self)
            
            # Restore/create missing OAuth token monitoring tasks for connected platforms
            await restore_oauth_monitoring_tasks(self)
            
            # Restore/create missing website analysis tasks for users who completed onboarding
            await restore_website_analysis_tasks(self)
            
            # Restore/create missing platform insights tasks for users with connected GSC/Bing
            await restore_platform_insights_tasks(self)
            
            # Validate and rebuild cumulative stats if needed
            await self._validate_and_rebuild_cumulative_stats()
            
            # Get all scheduled APScheduler jobs (including one-time tasks)
            all_jobs = self.scheduler.get_jobs()
            registered_types = self.registry.get_registered_types()
            active_strategies = self.stats.get('active_strategies_count', 0)
            
            # Count OAuth token monitoring tasks from database (recurring weekly tasks)
            oauth_tasks_count = 0
            oauth_tasks_details = []
            try:
                db = get_db_session()
                if db:
                    from models.oauth_token_monitoring_models import OAuthTokenMonitoringTask
                    # Count active tasks
                    oauth_tasks_count = db.query(OAuthTokenMonitoringTask).filter(
                        OAuthTokenMonitoringTask.status == 'active'
                    ).count()
                    
                    # Get all tasks (for detailed logging)
                    all_oauth_tasks = db.query(OAuthTokenMonitoringTask).all()
                    total_oauth_tasks = len(all_oauth_tasks)
                    
                    # Show platform breakdown for ALL tasks (active and inactive)
                    all_platforms = {}
                    active_platforms = {}
                    for task in all_oauth_tasks:
                        all_platforms[task.platform] = all_platforms.get(task.platform, 0) + 1
                        if task.status == 'active':
                            active_platforms[task.platform] = active_platforms.get(task.platform, 0) + 1
                    
                    if total_oauth_tasks > 0:
                        # Log details about all tasks (not just active)
                        for task in all_oauth_tasks:
                            oauth_tasks_details.append(
                                f"user={task.user_id}, platform={task.platform}, status={task.status}"
                            )
                    
                    if total_oauth_tasks > 0 and oauth_tasks_count == 0:
                        all_platform_summary = ", ".join([f"{p}: {c}" for p, c in sorted(all_platforms.items())])
                        logger.warning(
                            f"[Scheduler] Found {total_oauth_tasks} OAuth monitoring tasks in database, "
                            f"but {oauth_tasks_count} are active. "
                            f"All platforms: {all_platform_summary}. "
                            f"Task details: {', '.join(oauth_tasks_details[:5])}"  # Limit to first 5 for readability
                        )
                    elif oauth_tasks_count > 0:
                        # Show platform breakdown for active tasks
                        active_platform_summary = ", ".join([f"{platform}: {count}" for platform, count in sorted(active_platforms.items())])
                        all_platform_summary = ", ".join([f"{p}: {c}" for p, c in sorted(all_platforms.items())])
                        
                        # Check for missing platforms (expected: gsc, bing, wordpress, wix)
                        expected_platforms = ['gsc', 'bing', 'wordpress', 'wix']
                        missing_in_db = [p for p in expected_platforms if p not in all_platforms]
                        
                        if missing_in_db:
                            logger.warning(
                                f"[Scheduler] Found {oauth_tasks_count} active OAuth monitoring tasks "
                                f"(total: {total_oauth_tasks}). Active platforms: {active_platform_summary}. "
                                f"All platforms: {all_platform_summary}. "
                                f"⚠️ Missing platforms (not connected or no tasks): {', '.join(missing_in_db)}"
                            )
                        else:
                            logger.warning(
                                f"[Scheduler] Found {oauth_tasks_count} active OAuth monitoring tasks "
                                f"(total: {total_oauth_tasks}). Active platforms: {active_platform_summary}. "
                                f"All platforms: {all_platform_summary}"
                            )
                    
                    db.close()
            except Exception as e:
                logger.warning(
                    f"[Scheduler] Could not get OAuth token monitoring tasks count: {e}. "
                    f"This may indicate the oauth_token_monitoring_tasks table doesn't exist yet or "
                    f"tasks haven't been created. Error type: {type(e).__name__}"
                )
            
            # Get website analysis tasks count
            website_analysis_tasks_count = 0
            try:
                from models.website_analysis_monitoring_models import WebsiteAnalysisTask
                website_analysis_tasks_count = db.query(WebsiteAnalysisTask).filter(
                    WebsiteAnalysisTask.status == 'active'
                ).count()
            except Exception as e:
                logger.debug(f"Could not get website analysis tasks count: {e}")
            
            # Get platform insights tasks count
            platform_insights_tasks_count = 0
            try:
                from models.platform_insights_monitoring_models import PlatformInsightsTask
                platform_insights_tasks_count = db.query(PlatformInsightsTask).filter(
                    PlatformInsightsTask.status == 'active'
                ).count()
            except Exception as e:
                logger.debug(f"Could not get platform insights tasks count: {e}")
            
            # Calculate job counts
            apscheduler_recurring = 1  # check_due_tasks
            apscheduler_one_time = len(all_jobs) - 1
            total_recurring = apscheduler_recurring + oauth_tasks_count + website_analysis_tasks_count + platform_insights_tasks_count
            total_jobs = len(all_jobs) + oauth_tasks_count + website_analysis_tasks_count + platform_insights_tasks_count
            
            # Build comprehensive startup log message
            recurring_breakdown = f"check_due_tasks: {apscheduler_recurring}"
            if oauth_tasks_count > 0:
                recurring_breakdown += f", OAuth monitoring: {oauth_tasks_count}"
            if website_analysis_tasks_count > 0:
                recurring_breakdown += f", Website analysis: {website_analysis_tasks_count}"
            if platform_insights_tasks_count > 0:
                recurring_breakdown += f", Platform insights: {platform_insights_tasks_count}"
            
            startup_lines = [
                f"[Scheduler] ✅ Task Scheduler Started",
                f"   ├─ Check Interval: {initial_interval} minutes",
                f"   ├─ Registered Task Types: {len(registered_types)} ({', '.join(registered_types) if registered_types else 'none'})",
                f"   ├─ Active Strategies: {active_strategies}",
                f"   ├─ Total Scheduled Jobs: {total_jobs}",
                f"   ├─ Recurring Jobs: {total_recurring} ({recurring_breakdown})",
                f"   └─ One-Time Jobs: {apscheduler_one_time}"
            ]
            
            # Add APScheduler job details
            if all_jobs:
                for idx, job in enumerate(all_jobs):
                    is_last = idx == len(all_jobs) - 1 and oauth_tasks_count == 0 and website_analysis_tasks_count == 0 and platform_insights_tasks_count == 0
                    prefix = "   └─" if is_last else "   ├─"
                    next_run = job.next_run_time
                    trigger_type = type(job.trigger).__name__
                    
                    # Try to extract user_id from job ID or kwargs for context
                    user_context = ""
                    user_id_from_job = None
                    
                    # First try to get from kwargs
                    if hasattr(job, 'kwargs') and job.kwargs and job.kwargs.get('user_id'):
                        user_id_from_job = job.kwargs.get('user_id')
                    # Otherwise, try to extract from job ID (e.g., "research_persona_user_123..." or "research_persona_user123")
                    elif job.id and ('research_persona_' in job.id or 'facebook_persona_' in job.id):
                        # Job ID format: research_persona_{user_id} or facebook_persona_{user_id}
                        # where user_id is Clerk format (e.g., "user_33Gz1FPI86VDXhRY8QN4ragRFGN")
                        if job.id.startswith('research_persona_'):
                            user_id_from_job = job.id.replace('research_persona_', '')
                        elif job.id.startswith('facebook_persona_'):
                            user_id_from_job = job.id.replace('facebook_persona_', '')
                        else:
                            # Fallback: try to extract from parts (old format with timestamp)
                            parts = job.id.split('_')
                            if len(parts) >= 3:
                                user_id_from_job = parts[2]  # Extract user_id from job ID
                    
                    if user_id_from_job:
                        try:
                            db = get_db_session()
                            if db:
                                user_job_store = get_user_job_store_name(user_id_from_job, db)
                                if user_job_store == 'default':
                                    logger.debug(
                                        f"[Scheduler] Job store extraction returned 'default' for user {user_id_from_job}. "
                                        f"This may indicate no onboarding data or website URL not found."
                                    )
                                user_context = f" | User: {user_id_from_job} | Store: {user_job_store}"
                                db.close()
                        except Exception as e:
                            logger.warning(
                                f"[Scheduler] Could not extract job store name for user {user_id_from_job}: {e}. "
                                f"Error type: {type(e).__name__}"
                            )
                            user_context = f" | User: {user_id_from_job}"
                    
                    startup_lines.append(f"{prefix} Job: {job.id} | Trigger: {trigger_type} | Next Run: {next_run}{user_context}")
            
            # Add OAuth token monitoring tasks details
            # Show ALL OAuth tasks (active and inactive) for complete visibility
            if total_oauth_tasks > 0:
                try:
                    db = get_db_session()
                    if db:
                        from models.oauth_token_monitoring_models import OAuthTokenMonitoringTask
                        # Get ALL tasks, not just active ones
                        oauth_tasks = db.query(OAuthTokenMonitoringTask).all()
                        
                        for idx, task in enumerate(oauth_tasks):
                            is_last = idx == len(oauth_tasks) - 1 and website_analysis_tasks_count == 0 and platform_insights_tasks_count == 0 and len(all_jobs) == 0
                            prefix = "   └─" if is_last else "   ├─"
                            
                            try:
                                user_job_store = get_user_job_store_name(task.user_id, db)
                                if user_job_store == 'default':
                                    logger.debug(
                                        f"[Scheduler] Job store extraction returned 'default' for user {task.user_id}. "
                                        f"This may indicate no onboarding data or website URL not found."
                                    )
                            except Exception as e:
                                logger.warning(
                                    f"[Scheduler] Could not extract job store name for user {task.user_id}: {e}. "
                                    f"Using 'default'. Error type: {type(e).__name__}"
                                )
                                user_job_store = 'default'
                            
                            next_check = task.next_check.isoformat() if task.next_check else 'Not scheduled'
                            # Include status in the log line for visibility
                            status_indicator = "✅" if task.status == 'active' else f"[{task.status}]"
                            startup_lines.append(
                                f"{prefix} Job: oauth_token_monitoring_{task.platform}_{task.user_id} | "
                                f"Trigger: CronTrigger (Weekly) | Next Run: {next_check} | "
                                f"User: {task.user_id} | Store: {user_job_store} | Platform: {task.platform} {status_indicator}"
                            )
                        db.close()
                except Exception as e:
                    logger.debug(f"Could not get OAuth token monitoring task details: {e}")
            
            # Add website analysis tasks details
            if website_analysis_tasks_count > 0:
                try:
                    db = get_db_session()
                    if db:
                        from models.website_analysis_monitoring_models import WebsiteAnalysisTask
                        website_analysis_tasks = db.query(WebsiteAnalysisTask).all()
                        
                        for idx, task in enumerate(website_analysis_tasks):
                            is_last = idx == len(website_analysis_tasks) - 1 and platform_insights_tasks_count == 0 and len(all_jobs) == 0 and total_oauth_tasks == 0
                            prefix = "   └─" if is_last else "   ├─"
                            
                            try:
                                user_job_store = get_user_job_store_name(task.user_id, db)
                            except Exception as e:
                                logger.debug(f"Could not extract job store name for user {task.user_id}: {e}")
                                user_job_store = 'default'
                            
                            next_check = task.next_check.isoformat() if task.next_check else 'Not scheduled'
                            frequency = f"Every {task.frequency_days} days"
                            task_type_label = "User Website" if task.task_type == 'user_website' else "Competitor"
                            status_indicator = "✅" if task.status == 'active' else f"[{task.status}]"
                            website_display = task.website_url[:50] + "..." if task.website_url and len(task.website_url) > 50 else (task.website_url or 'N/A')
                            
                            startup_lines.append(
                                f"{prefix} Job: website_analysis_{task.task_type}_{task.user_id}_{task.id} | "
                                f"Trigger: CronTrigger ({frequency}) | Next Run: {next_check} | "
                                f"User: {task.user_id} | Store: {user_job_store} | Type: {task_type_label} | URL: {website_display} {status_indicator}"
                            )
                        db.close()
                except Exception as e:
                    logger.debug(f"Could not get website analysis task details: {e}")
            
            # Add platform insights tasks details
            if platform_insights_tasks_count > 0:
                try:
                    db = get_db_session()
                    if db:
                        from models.platform_insights_monitoring_models import PlatformInsightsTask
                        platform_insights_tasks = db.query(PlatformInsightsTask).all()
                        
                        for idx, task in enumerate(platform_insights_tasks):
                            is_last = idx == len(platform_insights_tasks) - 1 and len(all_jobs) == 0 and total_oauth_tasks == 0 and website_analysis_tasks_count == 0
                            prefix = "   └─" if is_last else "   ├─"
                            
                            try:
                                user_job_store = get_user_job_store_name(task.user_id, db)
                            except Exception as e:
                                logger.debug(f"Could not extract job store name for user {task.user_id}: {e}")
                                user_job_store = 'default'
                            
                            next_check = task.next_check.isoformat() if task.next_check else 'Not scheduled'
                            platform_label = task.platform.upper() if task.platform else 'Unknown'
                            site_display = task.site_url[:50] + "..." if task.site_url and len(task.site_url) > 50 else (task.site_url or 'N/A')
                            status_indicator = "✅" if task.status == 'active' else f"[{task.status}]"
                            
                            startup_lines.append(
                                f"{prefix} Job: platform_insights_{task.platform}_{task.user_id} | "
                                f"Trigger: CronTrigger (Weekly) | Next Run: {next_check} | "
                                f"User: {task.user_id} | Store: {user_job_store} | Platform: {platform_label} | Site: {site_display} {status_indicator}"
                            )
                        db.close()
                except Exception as e:
                    logger.debug(f"Could not get platform insights task details: {e}")
            
            # Log comprehensive startup information in single message
            logger.warning("\n".join(startup_lines))
            
            # Save scheduler start event to database
            try:
                db = get_db_session()
                if db:
                    event_log = SchedulerEventLog(
                        event_type='start',
                        event_date=datetime.utcnow(),
                        check_interval_minutes=initial_interval,
                        active_strategies_count=active_strategies,
                        event_data={
                            'registered_types': registered_types,
                            'total_jobs': total_jobs,
                            'recurring_jobs': total_recurring,
                            'one_time_jobs': apscheduler_one_time,
                            'oauth_monitoring_tasks': oauth_tasks_count,
                            'website_analysis_tasks': website_analysis_tasks_count,
                            'platform_insights_tasks': platform_insights_tasks_count
                        }
                    )
                    db.add(event_log)
                    db.commit()
                    db.close()
            except Exception as e:
                logger.warning(f"Failed to save scheduler start event log: {e}")
            
        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")
            raise
    
    
    async def stop(self):
        """Stop the scheduler gracefully."""
        if not self._running:
            return
        
        try:
            # Cancel all active executions
            for task_id, execution_task in self.active_executions.items():
                execution_task.cancel()
            
            # Wait for active executions to complete (with timeout)
            if self.active_executions:
                await asyncio.wait(
                    self.active_executions.values(),
                    timeout=30
                )
            
            # Get final job count before shutdown
            all_jobs_before = self.scheduler.get_jobs()
            
            # Shutdown scheduler
            self.scheduler.shutdown(wait=True)
            self._running = False
            
            # Log comprehensive shutdown information (use WARNING level for visibility)
            total_checks = self.stats.get('total_checks', 0)
            total_executed = self.stats.get('tasks_executed', 0)
            total_failed = self.stats.get('tasks_failed', 0)
            
            shutdown_message = (
                f"[Scheduler] 🛑 Task Scheduler Stopped\n"
                f"   ├─ Total Check Cycles: {total_checks}\n"
                f"   ├─ Total Tasks Executed: {total_executed}\n"
                f"   ├─ Total Tasks Failed: {total_failed}\n"
                f"   ├─ Jobs Cancelled: {len(all_jobs_before)}\n"
                f"   └─ Shutdown: Graceful"
            )
            logger.warning(shutdown_message)
            
            # Save scheduler stop event to database
            try:
                db = get_db_session()
                if db:
                    event_log = SchedulerEventLog(
                        event_type='stop',
                        event_date=datetime.utcnow(),
                        check_interval_minutes=self.current_check_interval_minutes,
                        event_data={
                            'total_checks': total_checks,
                            'total_executed': total_executed,
                            'total_failed': total_failed,
                            'jobs_cancelled': len(all_jobs_before)
                        }
                    )
                    db.add(event_log)
                    db.commit()
                    db.close()
            except Exception as e:
                logger.warning(f"Failed to save scheduler stop event log: {e}")
            
        except Exception as e:
            logger.error(f"Error stopping scheduler: {e}")
            raise
    
    async def _check_and_execute_due_tasks(self):
        """
        Main scheduler loop: check for due tasks and execute them.
        This runs periodically with intelligent interval adjustment based on active strategies.
        """
        await check_and_execute_due_tasks(self)
    
    async def _adjust_check_interval_if_needed(self, db: Session):
        """
        Intelligently adjust check interval based on active strategies.
        
        Args:
            db: Database session
        """
        await adjust_check_interval_if_needed(self, db)
    
    async def _execute_missed_jobs(self):
        """
        Check for and execute any missed DateTrigger jobs that are still within grace period.
        APScheduler marks jobs as 'missed' if they were scheduled to run while the scheduler wasn't running.
        """
        try:
            all_jobs = self.scheduler.get_jobs()
            now = datetime.utcnow().replace(tzinfo=self.scheduler.timezone)
            
            missed_jobs = []
            for job in all_jobs:
                # Only check DateTrigger jobs (one-time tasks)
                if hasattr(job, 'trigger') and isinstance(job.trigger, DateTrigger):
                    if job.next_run_time and job.next_run_time < now:
                        # Job's scheduled time has passed
                        time_since_scheduled = (now - job.next_run_time).total_seconds()
                        # Check if still within grace period (1 hour = 3600 seconds)
                        if time_since_scheduled <= 3600:
                            missed_jobs.append(job)
            
            if missed_jobs:
                logger.warning(
                    f"[Scheduler] Found {len(missed_jobs)} missed job(s) within grace period, executing now..."
                )
                for job in missed_jobs:
                    try:
                        # Execute the job immediately
                        logger.info(f"[Scheduler] Executing missed job: {job.id}")
                        await job.func(*job.args, **job.kwargs)
                    except Exception as e:
                        logger.error(f"[Scheduler] Error executing missed job {job.id}: {e}")
        except Exception as e:
            logger.warning(f"[Scheduler] Error checking for missed jobs: {e}")
    
    async def trigger_interval_adjustment(self):
        """
        Trigger immediate interval adjustment check.
        
        This should be called when a strategy is activated or deactivated
        to immediately adjust the scheduler interval based on current active strategies.
        """
        if not self._running:
            logger.debug("Scheduler not running, skipping interval adjustment")
            return
        
        try:
            db = get_db_session()
            if db:
                await adjust_check_interval_if_needed(self, db)
                db.close()
            else:
                logger.warning("Could not get database session for interval adjustment")
        except Exception as e:
            logger.warning(f"Error triggering interval adjustment: {e}")
    
    async def _validate_and_rebuild_cumulative_stats(self):
        """
        Validate cumulative stats on scheduler startup and rebuild if needed.
        This ensures cumulative stats are accurate after restarts.
        """
        db = None
        try:
            db = get_db_session()
            if not db:
                logger.warning("[Scheduler] Could not get database session for cumulative stats validation")
                return
            
            try:
                from models.scheduler_cumulative_stats_model import SchedulerCumulativeStats
                from models.scheduler_models import SchedulerEventLog
                from sqlalchemy import func
                
                # Get cumulative stats from persistent table
                cumulative_stats = db.query(SchedulerCumulativeStats).filter(
                    SchedulerCumulativeStats.id == 1
                ).first()
                
                # Count check_cycle events in database
                check_cycle_count = db.query(func.count(SchedulerEventLog.id)).filter(
                    SchedulerEventLog.event_type == 'check_cycle'
                ).scalar() or 0
                
                if cumulative_stats:
                    # Validate: cumulative stats should match event log count
                    if cumulative_stats.total_check_cycles != check_cycle_count:
                        logger.warning(
                            f"[Scheduler] ⚠️ Cumulative stats validation failed on startup: "
                            f"cumulative_stats.total_check_cycles={cumulative_stats.total_check_cycles} "
                            f"vs event_logs.count={check_cycle_count}. "
                            f"Rebuilding cumulative stats from event logs..."
                        )
                        
                        # Rebuild from event logs
                        result = db.query(
                            func.count(SchedulerEventLog.id),
                            func.sum(SchedulerEventLog.tasks_found),
                            func.sum(SchedulerEventLog.tasks_executed),
                            func.sum(SchedulerEventLog.tasks_failed)
                        ).filter(
                            SchedulerEventLog.event_type == 'check_cycle'
                        ).first()
                        
                        if result:
                            total_cycles = result[0] if result[0] is not None else 0
                            total_found = result[1] if result[1] is not None else 0
                            total_executed = result[2] if result[2] is not None else 0
                            total_failed = result[3] if result[3] is not None else 0
                            
                            # Update cumulative stats
                            cumulative_stats.total_check_cycles = int(total_cycles)
                            cumulative_stats.cumulative_tasks_found = int(total_found)
                            cumulative_stats.cumulative_tasks_executed = int(total_executed)
                            cumulative_stats.cumulative_tasks_failed = int(total_failed)
                            cumulative_stats.last_updated = datetime.utcnow()
                            cumulative_stats.updated_at = datetime.utcnow()
                            
                            db.commit()
                            logger.warning(
                                f"[Scheduler] ✅ Rebuilt cumulative stats on startup: "
                                f"cycles={total_cycles}, found={total_found}, "
                                f"executed={total_executed}, failed={total_failed}"
                            )
                        else:
                            logger.warning("[Scheduler] No check_cycle events found to rebuild from")
                    else:
                        logger.warning(
                            f"[Scheduler] ✅ Cumulative stats validated: "
                            f"{cumulative_stats.total_check_cycles} check cycles match event logs"
                        )
                else:
                    # Cumulative stats table doesn't exist, create it from event logs
                    logger.warning(
                        "[Scheduler] Cumulative stats table not found. "
                        "Creating from event logs..."
                    )
                    
                    result = db.query(
                        func.count(SchedulerEventLog.id),
                        func.sum(SchedulerEventLog.tasks_found),
                        func.sum(SchedulerEventLog.tasks_executed),
                        func.sum(SchedulerEventLog.tasks_failed)
                    ).filter(
                        SchedulerEventLog.event_type == 'check_cycle'
                    ).first()
                    
                    if result:
                        total_cycles = result[0] if result[0] is not None else 0
                        total_found = result[1] if result[1] is not None else 0
                        total_executed = result[2] if result[2] is not None else 0
                        total_failed = result[3] if result[3] is not None else 0
                        
                        cumulative_stats = SchedulerCumulativeStats.get_or_create(db)
                        cumulative_stats.total_check_cycles = int(total_cycles)
                        cumulative_stats.cumulative_tasks_found = int(total_found)
                        cumulative_stats.cumulative_tasks_executed = int(total_executed)
                        cumulative_stats.cumulative_tasks_failed = int(total_failed)
                        cumulative_stats.last_updated = datetime.utcnow()
                        cumulative_stats.updated_at = datetime.utcnow()
                        
                        db.commit()
                        logger.warning(
                            f"[Scheduler] ✅ Created cumulative stats from event logs: "
                            f"cycles={total_cycles}, found={total_found}, "
                            f"executed={total_executed}, failed={total_failed}"
                        )
            except ImportError:
                logger.warning(
                    "[Scheduler] Cumulative stats model not available. "
                    "Migration may not have been run yet. "
                    "Run: python backend/scripts/run_cumulative_stats_migration.py"
                )
        except Exception as e:
            logger.error(f"[Scheduler] Error validating cumulative stats: {e}", exc_info=True)
        finally:
            if db:
                db.close()
    
    async def _process_task_type(self, task_type: str, db: Session, cycle_summary: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """
        Process due tasks for a specific task type.
        
        Returns:
            Summary dict with 'found', 'executed', 'failed' counts, or None if no tasks
        """
        summary = {'found': 0, 'executed': 0, 'failed': 0}
        
        try:
            # Get task loader for this type
            try:
                task_loader = self.registry.get_task_loader(task_type)
            except Exception as e:
                error = TaskLoaderError(
                    message=f"Failed to get task loader for type {task_type}: {str(e)}",
                    task_type=task_type,
                    original_error=e
                )
                self.exception_handler.handle_exception(error)
                return None
            
            # Load due tasks (with error handling)
            try:
                due_tasks = task_loader(db)
            except Exception as e:
                error = TaskLoaderError(
                    message=f"Failed to load due tasks for type {task_type}: {str(e)}",
                    task_type=task_type,
                    original_error=e
                )
                self.exception_handler.handle_exception(error)
                return None
            
            if not due_tasks:
                return None
            
            summary['found'] = len(due_tasks)
            self.stats['tasks_found'] += len(due_tasks)
            
            # Execute tasks (with concurrency limit)
            execution_tasks = []
            skipped_count = 0
            for task in due_tasks:
                if len(self.active_executions) >= self.max_concurrent_executions:
                    skipped_count = len(due_tasks) - len(execution_tasks)
                    logger.warning(
                        f"[Scheduler] ⚠️ Max concurrent executions reached ({self.max_concurrent_executions}), "
                        f"skipping {skipped_count} tasks for {task_type}"
                    )
                    break
                
                # Execute task asynchronously
                # Note: Each task gets its own database session to prevent concurrent access issues
                execution_task = asyncio.create_task(
                    execute_task_async(self, task_type, task, summary)
                )
                
                task_id = f"{task_type}_{getattr(task, 'id', id(task))}"
                self.active_executions[task_id] = execution_task
                
                execution_tasks.append(execution_task)
            
            # Wait for executions to complete (with timeout per task)
            if execution_tasks:
                await asyncio.wait(execution_tasks, timeout=300)
            
            return summary
            
        except Exception as e:
            error = TaskLoaderError(
                message=f"Error processing task type {task_type}: {str(e)}",
                task_type=task_type,
                original_error=e
            )
            self.exception_handler.handle_exception(error)
            return summary
    
    
    def _update_user_stats(self, user_id: Optional[int], success: bool):
        """
        Update per-user statistics for user isolation tracking.
        
        Args:
            user_id: User ID (None if user context not available)
            success: Whether task execution was successful
        """
        if user_id is None:
            return
        
        if user_id not in self.stats['per_user_stats']:
            self.stats['per_user_stats'][user_id] = {
                'executed': 0,
                'failed': 0,
                'success_rate': 0.0
            }
        
        user_stats = self.stats['per_user_stats'][user_id]
        if success:
            user_stats['executed'] += 1
        else:
            user_stats['failed'] += 1
        
        # Calculate success rate
        total = user_stats['executed'] + user_stats['failed']
        if total > 0:
            user_stats['success_rate'] = (user_stats['executed'] / total) * 100.0
    
    async def _schedule_retry(self, task: Any, delay_seconds: int):
        """Schedule a retry for a failed task."""
        # This would update the task's next_execution time
        # For now, just log - could be enhanced to update next_execution
        logger.debug(f"Scheduling retry for task in {delay_seconds}s")
    
    def get_stats(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Get scheduler statistics with optional user filtering.
        
        Args:
            user_id: Optional user ID to filter statistics for specific user
            
        Returns:
            Dictionary with scheduler statistics
        """
        base_stats = {
            **{k: v for k, v in self.stats.items() if k not in ['per_user_stats']},
            'active_executions': len(self.active_executions),
            'registered_types': self.registry.get_registered_types(),
            'running': self._running,
            'check_interval_minutes': self.current_check_interval_minutes,
            'min_check_interval_minutes': self.min_check_interval_minutes,
            'max_check_interval_minutes': self.max_check_interval_minutes,
            'intelligent_scheduling': True
        }
        
        # Include per-user stats (all users or filtered)
        if user_id is not None:
            if user_id in self.stats['per_user_stats']:
                base_stats['user_stats'] = self.stats['per_user_stats'][user_id]
            else:
                base_stats['user_stats'] = {
                    'executed': 0,
                    'failed': 0,
                    'success_rate': 0.0
                }
        else:
            # Include all per-user stats (for admin/debugging)
            base_stats['per_user_stats'] = self.stats['per_user_stats']
        
        return base_stats
    
    def schedule_one_time_task(
        self,
        func: Callable,
        run_date: datetime,
        job_id: str,
        args: tuple = (),
        kwargs: Dict[str, Any] = None,
        replace_existing: bool = True
    ) -> str:
        """
        Schedule a one-time task to run at a specific datetime.
        
        Args:
            func: Async function to execute
            run_date: Datetime when the task should run (must be timezone-aware UTC)
            job_id: Unique identifier for this job
            args: Positional arguments to pass to func
            kwargs: Keyword arguments to pass to func
            replace_existing: If True, replace existing job with same ID
            
        Returns:
            Job ID
        """
        if not self._running:
            logger.warning(
                f"Scheduler not running, but scheduling job {job_id} anyway. "
                "APScheduler will start automatically when needed."
            )
        
        try:
            # Ensure run_date is timezone-aware (UTC)
            if run_date.tzinfo is None:
                from datetime import timezone
                run_date = run_date.replace(tzinfo=timezone.utc)
                logger.debug(f"Added UTC timezone to run_date: {run_date}")
            
            self.scheduler.add_job(
                func,
                trigger=DateTrigger(run_date=run_date),
                args=args,
                kwargs=kwargs or {},
                id=job_id,
                replace_existing=replace_existing,
                misfire_grace_time=3600  # 1 hour grace period for missed jobs
            )
            
            # Get updated job count
            all_jobs = self.scheduler.get_jobs()
            one_time_jobs = [j for j in all_jobs if j.id != 'check_due_tasks']
            
            # Extract user_id from kwargs if available for logging and job store
            user_id = kwargs.get('user_id', None) if kwargs else None
            func_name = func.__name__ if hasattr(func, '__name__') else str(func)
            
            # Get job store name for user (if user_id provided)
            job_store_name = 'default'
            if user_id:
                try:
                    db = get_db_session()
                    if db:
                        job_store_name = get_user_job_store_name(user_id, db)
                        db.close()
                except Exception as e:
                    logger.warning(f"Could not determine job store for user {user_id}: {e}")
            
            # Note: APScheduler doesn't support dynamic job store creation
            # We use 'default' for all jobs but log the user's job store name for debugging
            # The actual user isolation is handled through task filtering by user_id
            
            # Log detailed one-time task scheduling information (use WARNING level for visibility)
            log_message = (
                f"[Scheduler] 📅 Scheduled One-Time Task\n"
                f"   ├─ Job ID: {job_id}\n"
                f"   ├─ Function: {func_name}\n"
                f"   ├─ User ID: {user_id or 'system'}\n"
                f"   ├─ Job Store: {job_store_name} (user context)\n"
                f"   ├─ Scheduled For: {run_date}\n"
                f"   ├─ Replace Existing: {replace_existing}\n"
                f"   ├─ Total One-Time Jobs: {len(one_time_jobs)}\n"
                f"   └─ Total Scheduled Jobs: {len(all_jobs)}"
            )
            logger.warning(log_message)
            
            # Log job scheduling to event log for dashboard
            try:
                event_db = get_db_session()
                if event_db:
                    event_log = SchedulerEventLog(
                        event_type='job_scheduled',
                        event_date=datetime.utcnow(),
                        job_id=job_id,
                        job_type='one_time',
                        user_id=user_id,
                        event_data={
                            'function_name': func_name,
                            'job_store': job_store_name,
                            'scheduled_for': run_date.isoformat(),
                            'replace_existing': replace_existing
                        }
                    )
                    event_db.add(event_log)
                    event_db.commit()
                    event_db.close()
            except Exception as e:
                logger.debug(f"Failed to log job scheduling event: {e}")
            
            return job_id
        except Exception as e:
            logger.error(f"Failed to schedule one-time task {job_id}: {e}")
            raise
    
    def is_running(self) -> bool:
        """Check if scheduler is running."""
        return self._running

