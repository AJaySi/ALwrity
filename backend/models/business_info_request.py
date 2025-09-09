"""Business Information Request Models for ALwrity backend."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class BusinessInfoRequest(BaseModel):
    user_id: Optional[int] = None
    business_description: str = Field(..., min_length=10, max_length=1000, description="Description of the business")
    industry: Optional[str] = Field(None, max_length=100, description="Industry sector")
    target_audience: Optional[str] = Field(None, max_length=500, description="Target audience description")
    business_goals: Optional[str] = Field(None, max_length=1000, description="Business goals and objectives")

class BusinessInfoResponse(BaseModel):
    id: int
    user_id: Optional[int]
    business_description: str
    industry: Optional[str]
    target_audience: Optional[str]
    business_goals: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
