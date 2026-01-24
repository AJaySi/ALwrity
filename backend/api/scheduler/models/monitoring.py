"""Monitoring Models for Scheduler API"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class PaginationInfo(BaseModel):
    """Pagination information for list responses."""
    limit: int = Field(..., description="Items per page")
    offset: int = Field(..., description="Offset from start")
    total: int = Field(..., description="Total items available")
    has_more: bool = Field(..., description="Whether more items are available")


class ExecutionLogEntry(BaseModel):
    """Entry in execution logs."""
    id: int = Field(..., description="Log entry ID")
    task_id: str = Field(..., description="Task identifier")
    task_type: str = Field(..., description="Type of task executed")
    status: str = Field(..., description="Execution status (success, failed, running, skipped)")
    started_at: Optional[datetime] = Field(None, description="Execution start time")
    completed_at: Optional[datetime] = Field(None, description="Execution completion time")
    duration_seconds: Optional[float] = Field(None, description="Execution duration in seconds")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    user_id: Optional[str] = Field(None, description="User ID associated with task")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ExecutionLogsResponse(BaseModel):
    """Response model for execution logs endpoint."""
    logs: List[ExecutionLogEntry] = Field(default_factory=list, description="List of execution log entries")
    pagination: PaginationInfo = Field(..., description="Pagination information")


class EventLogEntry(BaseModel):
    """Entry in scheduler event logs."""
    id: int = Field(..., description="Event log entry ID")
    event_type: str = Field(..., description="Type of event")
    timestamp: datetime = Field(..., description="Event timestamp")
    user_id: Optional[str] = Field(None, description="User ID associated with event")
    details: Dict[str, Any] = Field(default_factory=dict, description="Event details")
    tasks_found: Optional[int] = Field(None, description="Tasks found in this cycle")
    tasks_executed: Optional[int] = Field(None, description="Tasks executed in this cycle")
    tasks_failed: Optional[int] = Field(None, description="Tasks failed in this cycle")
    tasks_skipped: Optional[int] = Field(None, description="Tasks skipped in this cycle")
    duration_seconds: Optional[float] = Field(None, description="Event duration")


class EventHistoryResponse(BaseModel):
    """Response model for event history endpoint."""
    events: List[EventLogEntry] = Field(default_factory=list, description="List of event log entries")
    pagination: PaginationInfo = Field(..., description="Pagination information")


class EventLogStats(BaseModel):
    """Statistics for event logs."""
    total_events: int = Field(..., description="Total number of events")
    events_by_type: Dict[str, int] = Field(default_factory=dict, description="Events grouped by type")
    oldest_event: Optional[datetime] = Field(None, description="Oldest event timestamp")
    newest_event: Optional[datetime] = Field(None, description="Newest event timestamp")
    average_duration_seconds: Optional[float] = Field(None, description="Average event duration")
    total_tasks_found: int = Field(default=0, description="Total tasks found across all events")
    total_tasks_executed: int = Field(default=0, description="Total tasks executed across all events")
    total_tasks_failed: int = Field(default=0, description="Total tasks failed across all events")
    total_tasks_skipped: int = Field(default=0, description="Total tasks skipped across all events")


class EventLogCleanupRequest(BaseModel):
    """Request model for event log cleanup."""
    older_than_days: int = Field(..., ge=1, le=365, description="Delete events older than this many days")
    dry_run: bool = Field(default=True, description="Whether to perform dry run (no actual deletion)")


class EventLogCleanupResponse(BaseModel):
    """Response model for event log cleanup."""
    deleted_count: int = Field(..., description="Number of events deleted")
    would_delete_count: int = Field(..., description="Number of events that would be deleted (dry run)")
    oldest_kept_event: Optional[datetime] = Field(None, description="Oldest event kept after cleanup")
    dry_run: bool = Field(..., description="Whether this was a dry run")