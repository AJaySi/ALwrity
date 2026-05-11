"""Backlink outreach router."""

from fastapi import APIRouter, Query

from services.backlink_outreach_models import BacklinkDiscoveryResponse, BacklinkKeywordInput, PolicyValidationRequest, PolicyValidationResponse
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


@router.post("/campaigns")
async def create_backlink_campaign(payload: BacklinkCampaignCreateRequest):
    storage = BacklinkOutreachStorageService()
    return storage.create_campaign(payload.user_id, payload.workspace_id, payload.name)


@router.get("/campaigns")
async def list_backlink_campaigns(user_id: str, workspace_id: str, limit: int = 50):
    storage = BacklinkOutreachStorageService()
    return {"campaigns": storage.list_campaigns(user_id, workspace_id, limit)}


@router.post("/policy-validate", response_model=PolicyValidationResponse)
async def validate_outreach_policy(payload: PolicyValidationRequest):
    return backlink_outreach_service.validate_send_policy(payload)


@router.get("/reporting")
async def get_backlink_reporting_snapshot():
    return backlink_outreach_service.get_reporting_snapshot()


@router.get("/migration-coverage")
async def get_backlink_migration_coverage():
    return backlink_outreach_service.get_migration_coverage()
