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


# -- Deep Discovery Models --

class DeepKeywordInput(BaseModel):
    keyword: str = Field(..., min_length=2, max_length=120)
    max_results: int = Field(default=15, ge=1, le=50)
    campaign_id: Optional[str] = Field(default=None, description="If set, auto-saves leads to this campaign")


class EnrichedOpportunity(BaseModel):
    url: str
    domain: str
    page_title: str = ""
    snippet: str = ""
    full_text: str = ""
    email: Optional[str] = None
    contact_page: Optional[str] = None
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    quality_score: float = Field(default=0.0, ge=0.0, le=1.0)
    word_count: int = 0
    has_guest_post_guidelines: bool = False
    discovery_source: str = "duckduckgo"


class DeepDiscoveryResponse(BaseModel):
    keyword: str
    source: str
    total_found: int
    opportunities: List[EnrichedOpportunity]


# -- Lead Models --

class LeadCreateRequest(BaseModel):
    campaign_id: str = Field(..., min_length=1)
    url: str = Field(..., min_length=1)
    domain: str = Field(..., min_length=1)
    email: Optional[str] = None
    page_title: Optional[str] = None
    snippet: Optional[str] = None
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    notes: Optional[str] = None


class LeadRecord(BaseModel):
    lead_id: str
    campaign_id: str
    url: Optional[str]
    domain: str
    page_title: Optional[str] = ""
    snippet: Optional[str] = ""
    email: Optional[str] = None
    confidence_score: float = 0.0
    discovery_source: Optional[str] = "duckduckgo"
    status: str = "discovered"
    notes: Optional[str] = None
    created_at: Optional[str] = None


class LeadListResponse(BaseModel):
    leads: List[LeadRecord]
    total: int


class LeadStatusUpdateRequest(BaseModel):
    status: str = Field(..., min_length=1)
    notes: Optional[str] = None


class CampaignDetailResponse(BaseModel):
    campaign_id: str
    name: str
    status: str
    created_at: Optional[str] = None
    lead_count: int = 0
    leads: List[LeadRecord] = Field(default_factory=list)


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
