"""OAuth Token Monitoring Models for Scheduler API"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class OAuthTokenTask(BaseModel):
    """OAuth token monitoring task information."""
    task_id: str = Field(..., description="Task identifier")
    user_id: str = Field(..., description="User ID associated with task")
    platform: str = Field(..., description="Platform (e.g., 'google', 'facebook', 'twitter')")
    token_type: str = Field(..., description="Type of token (access, refresh, api_key)")
    status: str = Field(..., description="Task status (active, paused, failed)")
    created_at: datetime = Field(..., description="Task creation timestamp")
    last_run_at: Optional[datetime] = Field(None, description="Last validation timestamp")
    next_run_at: Optional[datetime] = Field(None, description="Next scheduled validation timestamp")
    frequency_hours: int = Field(..., description="Validation frequency in hours")
    error_count: int = Field(default=0, description="Number of consecutive validation errors")
    last_error: Optional[str] = Field(None, description="Last validation error message")
    expires_at: Optional[datetime] = Field(None, description="Token expiration timestamp")
    days_until_expiry: Optional[int] = Field(None, description="Days until token expires")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional token metadata")


class OAuthTokenStatusResponse(BaseModel):
    """Response model for OAuth token monitoring status endpoint."""
    tasks: List[OAuthTokenTask] = Field(default_factory=list, description="List of OAuth token monitoring tasks")
    total_tasks: int = Field(default=0, description="Total number of token monitoring tasks")
    active_tasks: int = Field(default=0, description="Number of active token validations")
    expiring_soon: int = Field(default=0, description="Number of tokens expiring within 7 days")
    expired_tokens: int = Field(default=0, description="Number of expired tokens")
    failed_validations: int = Field(default=0, description="Number of failed token validations")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class OAuthTokenLogEntry(BaseModel):
    """Entry in OAuth token validation logs."""
    id: int = Field(..., description="Log entry ID")
    task_id: str = Field(..., description="Task identifier")
    user_id: str = Field(..., description="User ID")
    platform: str = Field(..., description="Platform monitored")
    token_type: str = Field(..., description="Type of token validated")
    validated_at: datetime = Field(..., description="Validation timestamp")
    status: str = Field(..., description="Validation status (valid, invalid, expired, error)")
    is_valid: bool = Field(..., description="Whether token is currently valid")
    expires_at: Optional[datetime] = Field(None, description="Token expiration timestamp")
    days_until_expiry: Optional[int] = Field(None, description="Days until token expires")
    error_message: Optional[str] = Field(None, description="Error message if validation failed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional validation metadata")