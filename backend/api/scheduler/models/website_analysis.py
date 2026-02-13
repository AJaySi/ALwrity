"""Website Analysis Models for Scheduler API"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class WebsiteAnalysisTask(BaseModel):
    """Website analysis monitoring task information."""
    task_id: str = Field(..., description="Task identifier")
    user_id: str = Field(..., description="User ID associated with task")
    website_url: str = Field(..., description="Website URL being analyzed")
    analysis_type: str = Field(..., description="Type of analysis (e.g., 'seo', 'performance', 'accessibility')")
    status: str = Field(..., description="Task status (active, paused, failed)")
    created_at: datetime = Field(..., description="Task creation timestamp")
    last_run_at: Optional[datetime] = Field(None, description="Last execution timestamp")
    next_run_at: Optional[datetime] = Field(None, description="Next scheduled run timestamp")
    frequency_hours: int = Field(..., description="Execution frequency in hours")
    error_count: int = Field(default=0, description="Number of consecutive errors")
    last_error: Optional[str] = Field(None, description="Last error message")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional task metadata")


class WebsiteAnalysisStatusResponse(BaseModel):
    """Response model for website analysis status endpoint."""
    tasks: List[WebsiteAnalysisTask] = Field(default_factory=list, description="List of website analysis tasks")
    total_tasks: int = Field(default=0, description="Total number of tasks")
    active_tasks: int = Field(default=0, description="Number of active tasks")
    paused_tasks: int = Field(default=0, description="Number of paused tasks")
    failed_tasks: int = Field(default=0, description="Number of failed tasks")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class WebsiteAnalysisLogEntry(BaseModel):
    """Entry in website analysis execution logs."""
    id: int = Field(..., description="Log entry ID")
    task_id: str = Field(..., description="Task identifier")
    user_id: str = Field(..., description="User ID")
    website_url: str = Field(..., description="Website URL analyzed")
    analysis_type: str = Field(..., description="Type of analysis performed")
    executed_at: datetime = Field(..., description="Execution timestamp")
    status: str = Field(..., description="Execution status")
    analysis_completed: bool = Field(..., description="Whether analysis was completed successfully")
    issues_found: Optional[int] = Field(None, description="Number of issues found")
    recommendations_count: Optional[int] = Field(None, description="Number of recommendations generated")
    duration_seconds: Optional[float] = Field(None, description="Execution duration")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    results_summary: Dict[str, Any] = Field(default_factory=dict, description="Summary of analysis results")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional execution metadata")