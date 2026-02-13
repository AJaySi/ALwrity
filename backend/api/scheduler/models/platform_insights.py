"""Platform Insights Models for Scheduler API"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class PlatformInsightsTask(BaseModel):
    """Platform insights monitoring task information."""
    task_id: str = Field(..., description="Task identifier")
    user_id: str = Field(..., description="User ID associated with task")
    platform: str = Field(..., description="Platform being monitored (e.g., 'google_search_console')")
    property_url: str = Field(..., description="Property URL being monitored")
    status: str = Field(..., description="Task status (active, paused, failed)")
    created_at: datetime = Field(..., description="Task creation timestamp")
    last_run_at: Optional[datetime] = Field(None, description="Last execution timestamp")
    next_run_at: Optional[datetime] = Field(None, description="Next scheduled run timestamp")
    frequency_hours: int = Field(..., description="Execution frequency in hours")
    error_count: int = Field(default=0, description="Number of consecutive errors")
    last_error: Optional[str] = Field(None, description="Last error message")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional task metadata")


class PlatformInsightsStatusResponse(BaseModel):
    """Response model for platform insights status endpoint."""
    tasks: List[PlatformInsightsTask] = Field(default_factory=list, description="List of platform insights tasks")
    total_tasks: int = Field(default=0, description="Total number of tasks")
    active_tasks: int = Field(default=0, description="Number of active tasks")
    paused_tasks: int = Field(default=0, description="Number of paused tasks")
    failed_tasks: int = Field(default=0, description="Number of failed tasks")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class PlatformInsightsLogEntry(BaseModel):
    """Entry in platform insights execution logs."""
    id: int = Field(..., description="Log entry ID")
    task_id: str = Field(..., description="Task identifier")
    user_id: str = Field(..., description="User ID")
    platform: str = Field(..., description="Platform monitored")
    property_url: str = Field(..., description="Property URL")
    executed_at: datetime = Field(..., description="Execution timestamp")
    status: str = Field(..., description="Execution status")
    data_retrieved: bool = Field(..., description="Whether data was successfully retrieved")
    records_found: Optional[int] = Field(None, description="Number of records found")
    records_processed: Optional[int] = Field(None, description="Number of records processed")
    duration_seconds: Optional[float] = Field(None, description="Execution duration")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional execution metadata")