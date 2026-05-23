"""Backlink outreach router."""

from fastapi import APIRouter, Query, HTTPException

from services.backlink_outreach_models import (
    BacklinkDiscoveryResponse, BacklinkKeywordInput, DeepKeywordInput,
    LeadCreateRequest, LeadStatusUpdateRequest,
    PolicyValidationRequest, PolicyValidationResponse,
)
from services.backlink_outreach_service import backlink_outreach_service
from services.backlink_outreach_storage import BacklinkOutreachStorageService
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/backlink-outreach", tags=["backlink-outreach"])


class BacklinkCampaignCreateRequest(BaseModel):
    user_id: str = Field(..., min_length=1)
    workspace_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=3)


@router.get("/modules")
async def get_backlink_module_registry():
    return {"feature": "backlink_outreach", "modules": backlink_outreach_service.list_backlink_modules()}


@router.get("/query-templates")
async def get_backlink_query_templates(keyword: str = Query(..., min_length=1)):
    return {"keyword": keyword, "queries": backlink_outreach_service.generate_guest_post_queries(keyword)}


@router.post("/discover", response_model=BacklinkDiscoveryResponse)
async def discover_backlink_opportunities(payload: BacklinkKeywordInput):
    return backlink_outreach_service.discover_opportunities(payload.keyword, payload.max_results)


@router.post("/discover/deep")
async def discover_deep_backlink_opportunities(payload: DeepKeywordInput):
    """Enhanced discovery using Exa neural search + DuckDuckGo with full-page scraping."""
    result = await backlink_outreach_service.deep_discover(payload.keyword, payload.max_results)
    if payload.campaign_id:
        storage = BacklinkOutreachStorageService()
        user_id = "default"
        for opp in result.get("opportunities", []):
            try:
                storage.add_lead(
                    campaign_id=payload.campaign_id,
                    user_id=user_id,
                    url=opp["url"],
                    domain=opp["domain"],
                    page_title=opp.get("page_title", ""),
                    snippet=opp.get("snippet", ""),
                    email=opp.get("email"),
                    confidence_score=opp.get("confidence_score", 0.0),
                    discovery_source=opp.get("discovery_source", "duckduckgo"),
                )
            except Exception:
                continue
    return result


@router.post("/campaigns")
async def create_backlink_campaign(payload: BacklinkCampaignCreateRequest):
    storage = BacklinkOutreachStorageService()
    return storage.create_campaign(payload.user_id, payload.workspace_id, payload.name)


@router.get("/campaigns")
async def list_backlink_campaigns(user_id: str, workspace_id: str, limit: int = 50):
    storage = BacklinkOutreachStorageService()
    return {"campaigns": storage.list_campaigns(user_id, workspace_id, limit)}


@router.get("/campaigns/{campaign_id}")
async def get_backlink_campaign(campaign_id: str, user_id: str = Query(...)):
    """Get campaign detail with leads."""
    storage = BacklinkOutreachStorageService()
    campaign = storage.get_campaign(campaign_id, user_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


@router.get("/campaigns/{campaign_id}/leads")
async def list_campaign_leads(
    campaign_id: str, user_id: str = Query(...), status: str = Query(None)
):
    """List leads for a campaign, optionally filtered by status."""
    storage = BacklinkOutreachStorageService()
    leads = storage.list_leads(campaign_id, user_id, status=status or None)
    return {"leads": leads, "total": len(leads)}


@router.post("/campaigns/{campaign_id}/leads")
async def add_campaign_lead(campaign_id: str, payload: LeadCreateRequest):
    """Add a single lead to a campaign."""
    storage = BacklinkOutreachStorageService()
    try:
        lead = storage.add_lead(
            campaign_id=payload.campaign_id,
            user_id="default",
            url=payload.url,
            domain=payload.domain,
            page_title=payload.page_title or "",
            snippet=payload.snippet or "",
            email=payload.email,
            confidence_score=payload.confidence_score,
            notes=payload.notes,
        )
        return lead
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/leads/{lead_id}/status")
async def update_lead_status(lead_id: str, payload: LeadStatusUpdateRequest):
    """Update lead status (discovered -> contacted -> replied -> placed)."""
    storage = BacklinkOutreachStorageService()
    lead = storage.update_lead_status(lead_id, "default", payload.status, payload.notes)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.post("/policy-validate", response_model=PolicyValidationResponse)
async def validate_outreach_policy(payload: PolicyValidationRequest):
    return backlink_outreach_service.validate_send_policy(payload)


@router.get("/reporting")
async def get_backlink_reporting_snapshot():
    return backlink_outreach_service.get_reporting_snapshot()


@router.get("/migration-coverage")
async def get_backlink_migration_coverage():
    return backlink_outreach_service.get_migration_coverage()
