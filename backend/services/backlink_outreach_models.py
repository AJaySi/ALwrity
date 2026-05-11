from __future__ import annotations

from pydantic import BaseModel, Field, HttpUrl, EmailStr
from typing import Dict, List, Optional


class BacklinkKeywordInput(BaseModel):
    keyword: str = Field(..., min_length=2, max_length=120)
    max_results: int = Field(default=10, ge=1, le=50)


class OpportunityContactInfo(BaseModel):
    email: Optional[EmailStr] = None
    contact_page: Optional[HttpUrl] = None


class OpportunityRecord(BaseModel):
    url: HttpUrl
    title: str
    snippet: str
    metadata: Dict[str, str] = Field(default_factory=dict)
    contact_info: OpportunityContactInfo = Field(default_factory=OpportunityContactInfo)
    confidence_score: float = Field(..., ge=0.0, le=1.0)


class BacklinkDiscoveryResponse(BaseModel):
    keyword: str
    queries: List[str]
    opportunities: List[OpportunityRecord]


class GeneratedEmailResponse(BaseModel):
    subject: str
    body: str


class OutreachStatusRecord(BaseModel):
    opportunity_url: HttpUrl
    status: str
    notes: Optional[str] = None


class PolicyValidationRequest(BaseModel):
    user_id: str = Field(..., min_length=1)
    workspace_id: str = Field(..., min_length=1)
    campaign_id: str = Field(..., min_length=1)
    recipient_email: EmailStr
    recipient_domain: str
    recipient_region: str = Field(default="unknown")
    legal_basis: str = Field(..., min_length=2)
    approved_by_human: bool = False
    unsubscribe_url: Optional[HttpUrl] = None
    sender_identity: str = Field(..., min_length=3)
    idempotency_key: str = Field(..., min_length=8)


class PolicyValidationResponse(BaseModel):
    allowed: bool
    reasons: List[str] = Field(default_factory=list)
    final_status: str
