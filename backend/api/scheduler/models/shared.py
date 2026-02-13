"""Shared Models for Scheduler API"""

from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """Enumeration of possible task statuses."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"


class TaskType(str, Enum):
    """Enumeration of possible task types."""
    OAUTH_TOKEN_MONITORING = "oauth_token_monitoring"
    PLATFORM_INSIGHTS = "platform_insights"
    WEBSITE_ANALYSIS = "website_analysis"
    GENERAL = "general"


class TaskInterventionInfo(BaseModel):
    """Information about a task that needs intervention."""
    task_id: str = Field(..., description="Task identifier")
    task_type: TaskType = Field(..., description="Type of task")
    user_id: str = Field(..., description="User ID associated with task")
    status: TaskStatus = Field(..., description="Current task status")
    created_at: str = Field(..., description="Task creation timestamp")
    last_attempt: Optional[str] = Field(None, description="Last execution attempt timestamp")
    failure_count: int = Field(default=0, description="Number of failed attempts")
    error_message: Optional[str] = Field(None, description="Last error message")
    next_retry_at: Optional[str] = Field(None, description="Next scheduled retry timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional task metadata")


class ManualTriggerRequest(BaseModel):
    """Request model for manual task triggering."""
    task_type: TaskType = Field(..., description="Type of task to trigger")
    task_id: str = Field(..., description="Specific task ID to trigger")
    user_id: Optional[str] = Field(None, description="User ID (if not in path)")
    force: bool = Field(default=False, description="Force execution even if conditions not met")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Additional parameters for task execution")


class ManualTriggerResponse(BaseModel):
    """Response model for manual task triggering."""
    success: bool = Field(..., description="Whether trigger was successful")
    task_id: str = Field(..., description="Task ID that was triggered")
    execution_id: Optional[str] = Field(None, description="Execution ID for tracking")
    message: str = Field(..., description="Status message")
    estimated_duration_seconds: Optional[int] = Field(None, description="Estimated execution time")


class TaskRetryRequest(BaseModel):
    """Request model for task retry operations."""
    task_id: str = Field(..., description="Task ID to retry")
    reset_failure_count: bool = Field(default=False, description="Reset failure count to 0")
    force_retry: bool = Field(default=False, description="Force retry even if not eligible")
    custom_parameters: Dict[str, Any] = Field(default_factory=dict, description="Custom parameters for retry")


class TaskRetryResponse(BaseModel):
    """Response model for task retry operations."""
    success: bool = Field(..., description="Whether retry was initiated successfully")
    task_id: str = Field(..., description="Task ID being retried")
    retry_scheduled_at: Optional[str] = Field(None, description="When retry is scheduled")
    message: str = Field(..., description="Status message")
    failure_count_reset: bool = Field(default=False, description="Whether failure count was reset")