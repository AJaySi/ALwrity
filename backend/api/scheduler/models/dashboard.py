"""Dashboard Models for Scheduler API"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class SchedulerStats(BaseModel):
    """Statistics for scheduler dashboard."""
    # Current session stats
    total_checks: int = Field(default=0, description="Total checks performed in current session")
    tasks_found: int = Field(default=0, description="Tasks found in current session")
    tasks_executed: int = Field(default=0, description="Tasks executed in current session")
    tasks_failed: int = Field(default=0, description="Tasks failed in current session")
    tasks_skipped: int = Field(default=0, description="Tasks skipped in current session")
    last_check: Optional[datetime] = Field(None, description="Timestamp of last check")
    last_update: Optional[datetime] = Field(None, description="Timestamp of last update")
    active_executions: int = Field(default=0, description="Currently active task executions")
    running: bool = Field(default=False, description="Whether scheduler is currently running")
    check_interval_minutes: int = Field(default=60, description="Current check interval in minutes")
    min_check_interval_minutes: int = Field(default=15, description="Minimum check interval")
    max_check_interval_minutes: int = Field(default=60, description="Maximum check interval")
    intelligent_scheduling: bool = Field(default=True, description="Whether intelligent scheduling is enabled")
    active_strategies_count: int = Field(default=0, description="Number of active strategies")
    last_interval_adjustment: Optional[datetime] = Field(None, description="Last interval adjustment")
    registered_types: List[str] = Field(default_factory=list, description="Registered task types")

    # Cumulative/historical stats
    cumulative_total_check_cycles: int = Field(default=0, description="Total check cycles across all sessions")
    cumulative_tasks_found: int = Field(default=0, description="Total tasks found across all sessions")
    cumulative_tasks_executed: int = Field(default=0, description="Total tasks executed across all sessions")
    cumulative_tasks_failed: int = Field(default=0, description="Total tasks failed across all sessions")


class JobInfo(BaseModel):
    """Information about a scheduled job."""
    id: str = Field(..., description="Job ID")
    name: str = Field(..., description="Job name")
    func: str = Field(..., description="Function to execute")
    args: List[Any] = Field(default_factory=list, description="Positional arguments")
    kwargs: Dict[str, Any] = Field(default_factory=dict, description="Keyword arguments")
    trigger: str = Field(..., description="Trigger type (e.g., 'interval', 'date')")
    trigger_type: str = Field(..., description="Specific trigger type")
    next_run_time: Optional[datetime] = Field(None, description="Next scheduled run time")
    is_paused: bool = Field(default=False, description="Whether job is paused")
    is_database_task: bool = Field(default=False, description="Whether this is a database-backed task")
    task_type: Optional[str] = Field(None, description="Type of task")
    user_id: Optional[str] = Field(None, description="User ID for user-specific tasks")
    created_at: Optional[datetime] = Field(None, description="Job creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Job last update timestamp")


class UserIsolationInfo(BaseModel):
    """Information about user isolation settings."""
    enabled: bool = Field(default=True, description="Whether user isolation is enabled")
    current_user_id: str = Field(..., description="Current user's ID")


class SchedulerDashboardResponse(BaseModel):
    """Response model for scheduler dashboard endpoint."""
    stats: SchedulerStats = Field(..., description="Scheduler statistics")
    jobs: List[JobInfo] = Field(default_factory=list, description="List of scheduled jobs")
    job_count: int = Field(default=0, description="Total number of jobs")
    recurring_jobs: int = Field(default=0, description="Number of recurring jobs")
    one_time_jobs: int = Field(default=0, description="Number of one-time jobs")
    registered_task_types: List[str] = Field(default_factory=list, description="Registered task types")
    user_isolation: UserIsolationInfo = Field(..., description="User isolation information")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")