"""Monitoring Models for Scheduler API."""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class TaskInfo(BaseModel):
    """Execution task metadata for dashboard table rows."""
    id: Optional[int] = None
    task_title: Optional[str] = None
    component_name: Optional[str] = None
    metric: Optional[str] = None
    frequency: Optional[str] = None


class ExecutionLogEntry(BaseModel):
    """Entry in execution logs compatible with dashboard frontend."""
    id: int
    task_id: Optional[int] = None
    user_id: Optional[str] = None
    execution_date: Optional[datetime] = None
    status: str
    error_message: Optional[str] = None
    execution_time_ms: Optional[int] = None
    result_data: Optional[Any] = None
    created_at: Optional[datetime] = None
    task: Optional[TaskInfo] = None


class ExecutionLogsResponse(BaseModel):
    """Response model for execution logs endpoint."""
    logs: List[ExecutionLogEntry] = Field(default_factory=list)
    total_count: int = 0
    limit: int = 50
    offset: int = 0
    has_more: bool = False
    is_scheduler_logs: bool = False


class EventLogEntry(BaseModel):
    """Entry in scheduler event logs."""
    id: int
    event_type: str
    event_date: Optional[datetime] = None
    check_cycle_number: Optional[int] = None
    check_interval_minutes: Optional[int] = None
    previous_interval_minutes: Optional[int] = None
    new_interval_minutes: Optional[int] = None
    tasks_found: Optional[int] = None
    tasks_executed: Optional[int] = None
    tasks_failed: Optional[int] = None
    tasks_by_type: Optional[Dict[str, int]] = None
    check_duration_seconds: Optional[float] = None
    active_strategies_count: Optional[int] = None
    active_executions: Optional[int] = None
    job_id: Optional[str] = None
    job_type: Optional[str] = None
    user_id: Optional[str] = None
    event_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None


class EventHistoryResponse(BaseModel):
    """Response model for event history endpoint."""
    events: List[EventLogEntry] = Field(default_factory=list)
    total_count: int = 0
    limit: int = 50
    offset: int = 0
    has_more: bool = False
    date_filter: Optional[Dict[str, Any]] = None


class EventLogStats(BaseModel):
    """Statistics for event logs."""
    total_events: int
    events_by_type: Dict[str, int] = Field(default_factory=dict)
    oldest_event: Optional[datetime] = None
    newest_event: Optional[datetime] = None
    average_duration_seconds: Optional[float] = None
    total_tasks_found: int = 0
    total_tasks_executed: int = 0
    total_tasks_failed: int = 0
    total_tasks_skipped: int = 0


class EventLogCleanupRequest(BaseModel):
    """Request model for event log cleanup."""
    older_than_days: int = Field(..., ge=1, le=365)
    dry_run: bool = Field(default=True)


class EventLogCleanupResponse(BaseModel):
    """Response model for event log cleanup."""
    deleted_count: int
    would_delete_count: int
    oldest_kept_event: Optional[datetime] = None
    dry_run: bool
