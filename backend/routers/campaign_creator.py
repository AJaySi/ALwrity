"""API endpoints for Campaign Creator - Multi-channel campaign management."""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from services.campaign_creator import (
    CampaignOrchestrator,
    CampaignStorageService,
    AssetAuditService,
    ChannelPackService,
)
from services.product_marketing import BrandDNASyncService
from middleware.auth_middleware import get_current_user
from utils.logger_utils import get_service_logger

logger = get_service_logger("api.campaign_creator")
router = APIRouter(prefix="/api/campaign-creator", tags=["campaign-creator"])


# ====================
# REQUEST MODELS
# ====================

class CampaignCreateRequest(BaseModel):
    """Request to create a new campaign blueprint."""
    campaign_name: str = Field(..., description="Campaign name")
    goal: str = Field(..., description="Campaign goal (product_launch, awareness, conversion, etc.)")
    kpi: Optional[str] = Field(None, description="Key performance indicator")
    channels: List[str] = Field(..., description="Target channels (instagram, linkedin, tiktok, etc.)")
    product_context: Optional[Dict[str, Any]] = Field(None, description="Product information")


class AssetProposalRequest(BaseModel):
    """Request to generate asset proposals."""
    campaign_id: str = Field(..., description="Campaign ID")
    product_context: Optional[Dict[str, Any]] = Field(None, description="Product information")


class AssetGenerateRequest(BaseModel):
    """Request to generate a specific asset."""
    asset_proposal: Dict[str, Any] = Field(..., description="Asset proposal from generate_proposals")
    product_context: Optional[Dict[str, Any]] = Field(None, description="Product information")


class AssetAuditRequest(BaseModel):
    """Request to audit uploaded assets."""
    image_base64: str = Field(..., description="Base64 encoded image")
    asset_metadata: Optional[Dict[str, Any]] = Field(None, description="Asset metadata")


# ====================
# DEPENDENCY
# ====================

def get_orchestrator() -> CampaignOrchestrator:
    """Get Campaign Orchestrator instance."""
    return CampaignOrchestrator()


def get_campaign_storage() -> CampaignStorageService:
    """Get Campaign Storage Service instance."""
    return CampaignStorageService()


def _require_user_id(current_user: Dict[str, Any], operation: str) -> str:
    """Ensure user_id is available for protected operations."""
    user_id = current_user.get("sub") or current_user.get("user_id") or current_user.get("id")
    if not user_id:
        logger.error(
            "[Campaign Creator] ❌ Missing user_id for %s operation - blocking request",
            operation,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authenticated user required for campaign creator operations.",
        )
    return str(user_id)


# ====================
# CAMPAIGN ENDPOINTS
# ====================

@router.post("/campaigns/validate-preflight", summary="Validate Campaign Pre-flight")
async def validate_campaign_preflight(
    request: CampaignCreateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    orchestrator: CampaignOrchestrator = Depends(get_orchestrator)
):
    """Validate campaign blueprint against subscription limits before creation."""
    try:
        user_id = _require_user_id(current_user, "campaign pre-flight validation")
        logger.info(f"[Campaign Creator] Pre-flight validation for user {user_id}")
        
        campaign_data = {
            "campaign_name": request.campaign_name or "Temporary Campaign",
            "goal": request.goal,
            "kpi": request.kpi,
            "channels": request.channels,
        }
        
        blueprint = orchestrator.create_campaign_blueprint(user_id, campaign_data)
        validation_result = orchestrator.validate_campaign_preflight(user_id, blueprint)
        
        logger.info(f"[Campaign Creator] ✅ Pre-flight validation completed: can_proceed={validation_result.get('can_proceed')}")
        return validation_result
        
    except Exception as e:
        logger.error(f"[Campaign Creator] ❌ Error in pre-flight validation: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Pre-flight validation failed: {str(e)}")


@router.post("/campaigns/create-blueprint", summary="Create Campaign Blueprint")
async def create_campaign_blueprint(
    request: CampaignCreateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    orchestrator: CampaignOrchestrator = Depends(get_orchestrator)
):
    """Create a campaign blueprint with personalized asset nodes."""
    try:
        user_id = _require_user_id(current_user, "campaign blueprint creation")
        logger.info(f"[Campaign Creator] Creating blueprint for user {user_id}: {request.campaign_name}")
        
        campaign_data = {
            "campaign_name": request.campaign_name,
            "goal": request.goal,
            "kpi": request.kpi,
            "channels": request.channels,
        }
        
        blueprint = orchestrator.create_campaign_blueprint(user_id, campaign_data)
        
        blueprint_dict = {
            "campaign_id": blueprint.campaign_id,
            "campaign_name": blueprint.campaign_name,
            "goal": blueprint.goal,
            "kpi": blueprint.kpi,
            "phases": blueprint.phases,
            "asset_nodes": [
                {
                    "asset_id": node.asset_id,
                    "asset_type": node.asset_type,
                    "channel": node.channel,
                    "status": node.status,
                }
                for node in blueprint.asset_nodes
            ],
            "channels": blueprint.channels,
            "status": blueprint.status,
        }
        
        campaign_storage = get_campaign_storage()
        campaign_storage.save_campaign(user_id, blueprint_dict)
        
        logger.info(f"[Campaign Creator] ✅ Blueprint created and saved: {blueprint.campaign_id}")
        return blueprint_dict
        
    except Exception as e:
        logger.error(f"[Campaign Creator] ❌ Error creating blueprint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Campaign blueprint creation failed: {str(e)}")


@router.post("/campaigns/{campaign_id}/generate-proposals", summary="Generate Asset Proposals")
async def generate_asset_proposals(
    campaign_id: str,
    request: AssetProposalRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    orchestrator: CampaignOrchestrator = Depends(get_orchestrator)
):
    """Generate AI proposals for all assets in a campaign blueprint."""
    try:
        user_id = _require_user_id(current_user, "asset proposal generation")
        logger.info(f"[Campaign Creator] Generating proposals for campaign {campaign_id}")
        
        campaign_storage = get_campaign_storage()
        campaign = campaign_storage.get_campaign(user_id, campaign_id)
        
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        from services.campaign_creator.orchestrator import CampaignBlueprint, CampaignAssetNode
        
        asset_nodes = []
        if campaign.asset_nodes:
            for node_data in campaign.asset_nodes:
                asset_nodes.append(CampaignAssetNode(
                    asset_id=node_data.get('asset_id'),
                    asset_type=node_data.get('asset_type'),
                    channel=node_data.get('channel'),
                    status=node_data.get('status', 'draft'),
                ))
        
        blueprint = CampaignBlueprint(
            campaign_id=campaign.campaign_id,
            campaign_name=campaign.campaign_name,
            goal=campaign.goal,
            kpi=campaign.kpi,
            channels=campaign.channels or [],
            asset_nodes=asset_nodes,
        )
        
        proposals = orchestrator.generate_asset_proposals(
            user_id=user_id,
            blueprint=blueprint,
            product_context=request.product_context,
        )
        
        try:
            campaign_storage.save_proposals(user_id, campaign_id, proposals)
            logger.info(f"[Campaign Creator] ✅ Saved {proposals['total_assets']} proposals to database")
        except Exception as save_error:
            logger.error(f"[Campaign Creator] ⚠️ Failed to save proposals to database: {str(save_error)}")
        
        logger.info(f"[Campaign Creator] ✅ Generated {proposals['total_assets']} proposals")
        return proposals
        
    except Exception as e:
        logger.error(f"[Campaign Creator] ❌ Error generating proposals: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Asset proposal generation failed: {str(e)}")


@router.post("/assets/generate", summary="Generate Asset")
async def generate_asset(
    request: AssetGenerateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    orchestrator: CampaignOrchestrator = Depends(get_orchestrator)
):
    """Generate a single asset using Image Studio APIs."""
    try:
        user_id = _require_user_id(current_user, "asset generation")
        logger.info(f"[Campaign Creator] Generating asset for user {user_id}")
        
        result = await orchestrator.generate_asset(
            user_id=user_id,
            asset_proposal=request.asset_proposal,
            product_context=request.product_context,
        )
        
        if result.get('success'):
            campaign_id = request.asset_proposal.get('campaign_id')
            if not campaign_id:
                asset_id = request.asset_proposal.get('asset_id', '')
                if asset_id and '_' in asset_id:
                    parts = asset_id.split('_')
                    phase_indicators = ['teaser', 'launch', 'nurture', 'prelaunch', 'postlaunch']
                    for i, part in enumerate(parts):
                        if part.lower() in phase_indicators and i > 0:
                            campaign_id = '_'.join(parts[:i])
                            break
            
            if campaign_id:
                try:
                    campaign_storage = get_campaign_storage()
                    campaign = campaign_storage.get_campaign(user_id, campaign_id)
                    if campaign:
                        asset_node_id = request.asset_proposal.get('asset_id', '')
                        if asset_node_id:
                            from models.product_marketing_models import CampaignProposal
                            from services.database import SessionLocal
                            db = SessionLocal()
                            try:
                                proposal = db.query(CampaignProposal).filter(
                                    CampaignProposal.campaign_id == campaign_id,
                                    CampaignProposal.asset_node_id == asset_node_id,
                                    CampaignProposal.user_id == user_id
                                ).first()
                                if proposal:
                                    proposal.status = 'ready'
                                    db.commit()
                                    logger.info(f"[Campaign Creator] ✅ Updated proposal status for {asset_node_id}")
                            finally:
                                db.close()
                        
                        logger.info(f"[Campaign Creator] ✅ Asset generated for campaign {campaign_id}")
                except Exception as update_error:
                    logger.warning(f"[Campaign Creator] ⚠️ Could not update campaign status: {str(update_error)}")
        
        logger.info(f"[Campaign Creator] ✅ Asset generated successfully")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Campaign Creator] ❌ Error generating asset: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Asset generation failed: {str(e)}")


# ====================
# BRAND DNA ENDPOINTS
# ====================

@router.get("/brand-dna", summary="Get Brand DNA Tokens")
async def get_brand_dna(
    current_user: Dict[str, Any] = Depends(get_current_user),
    brand_dna_sync: BrandDNASyncService = Depends(lambda: BrandDNASyncService())
):
    """Get brand DNA tokens for the authenticated user."""
    try:
        user_id = _require_user_id(current_user, "brand DNA retrieval")
        brand_tokens = brand_dna_sync.get_brand_dna_tokens(user_id)
        
        return {"brand_dna": brand_tokens}
        
    except Exception as e:
        logger.error(f"[Campaign Creator] ❌ Error getting brand DNA: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/brand-dna/channel/{channel}", summary="Get Channel-Specific Brand DNA")
async def get_channel_brand_dna(
    channel: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    brand_dna_sync: BrandDNASyncService = Depends(lambda: BrandDNASyncService())
):
    """Get channel-specific brand DNA adaptations."""
    try:
        user_id = _require_user_id(current_user, "channel brand DNA retrieval")
        channel_dna = brand_dna_sync.get_channel_specific_dna(user_id, channel)
        
        return {"channel": channel, "brand_dna": channel_dna}
        
    except Exception as e:
        logger.error(f"[Campaign Creator] ❌ Error getting channel DNA: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ====================
# ASSET AUDIT ENDPOINTS
# ====================

@router.post("/assets/audit", summary="Audit Asset")
async def audit_asset(
    request: AssetAuditRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    asset_audit: AssetAuditService = Depends(lambda: AssetAuditService())
):
    """Audit an uploaded asset and get enhancement recommendations."""
    try:
        user_id = _require_user_id(current_user, "asset audit")
        audit_result = asset_audit.audit_asset(
            request.image_base64,
            request.asset_metadata,
        )
        
        return audit_result
        
    except Exception as e:
        logger.error(f"[Campaign Creator] ❌ Error auditing asset: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ====================
# CHANNEL PACK ENDPOINTS
# ====================

@router.get("/channels/{channel}/pack", summary="Get Channel Pack")
async def get_channel_pack(
    channel: str,
    asset_type: str = "social_post",
    current_user: Dict[str, Any] = Depends(get_current_user),
    channel_pack: ChannelPackService = Depends(lambda: ChannelPackService())
):
    """Get channel-specific pack configuration with templates and optimization tips."""
    try:
        pack = channel_pack.get_channel_pack(channel, asset_type)
        return pack
        
    except Exception as e:
        logger.error(f"[Campaign Creator] ❌ Error getting channel pack: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ====================
# CAMPAIGN LISTING & RETRIEVAL
# ====================

@router.get("/campaigns", summary="List Campaigns")
async def list_campaigns(
    status: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
    campaign_storage: CampaignStorageService = Depends(get_campaign_storage)
):
    """List all campaigns for the authenticated user."""
    try:
        user_id = _require_user_id(current_user, "list campaigns")
        campaigns = campaign_storage.list_campaigns(user_id, status=status)
        
        return {
            "campaigns": [
                {
                    "campaign_id": c.campaign_id,
                    "campaign_name": c.campaign_name,
                    "goal": c.goal,
                    "kpi": c.kpi,
                    "status": c.status,
                    "channels": c.channels,
                    "phases": c.phases,
                    "asset_nodes": c.asset_nodes,
                    "created_at": c.created_at.isoformat() if c.created_at else None,
                    "updated_at": c.updated_at.isoformat() if c.updated_at else None,
                }
                for c in campaigns
            ],
            "total": len(campaigns),
        }
    except Exception as e:
        logger.error(f"[Campaign Creator] ❌ Error listing campaigns: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/campaigns/{campaign_id}", summary="Get Campaign")
async def get_campaign(
    campaign_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    campaign_storage: CampaignStorageService = Depends(get_campaign_storage)
):
    """Get a specific campaign by ID."""
    try:
        user_id = _require_user_id(current_user, "get campaign")
        campaign = campaign_storage.get_campaign(user_id, campaign_id)
        
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        return {
            "campaign_id": campaign.campaign_id,
            "campaign_name": campaign.campaign_name,
            "goal": campaign.goal,
            "kpi": campaign.kpi,
            "status": campaign.status,
            "channels": campaign.channels,
            "phases": campaign.phases,
            "asset_nodes": campaign.asset_nodes,
            "product_context": campaign.product_context,
            "created_at": campaign.created_at.isoformat() if campaign.created_at else None,
            "updated_at": campaign.updated_at.isoformat() if campaign.updated_at else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Campaign Creator] ❌ Error getting campaign: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/campaigns/{campaign_id}/proposals", summary="Get Campaign Proposals")
async def get_campaign_proposals(
    campaign_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    campaign_storage: CampaignStorageService = Depends(get_campaign_storage)
):
    """Get proposals for a campaign."""
    try:
        user_id = _require_user_id(current_user, "get proposals")
        proposals = campaign_storage.get_proposals(user_id, campaign_id)
        
        proposals_dict = {}
        for proposal in proposals:
            proposals_dict[proposal.asset_node_id] = {
                "asset_id": proposal.asset_node_id,
                "asset_type": proposal.asset_type,
                "channel": proposal.channel,
                "proposed_prompt": proposal.proposed_prompt,
                "recommended_template": proposal.recommended_template,
                "recommended_provider": proposal.recommended_provider,
                "cost_estimate": proposal.cost_estimate,
                "concept_summary": proposal.concept_summary,
                "status": proposal.status,
            }
        
        return {
            "proposals": proposals_dict,
            "total_assets": len(proposals),
        }
    except Exception as e:
        logger.error(f"[Campaign Creator] ❌ Error getting proposals: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ====================
# HEALTH CHECK
# ====================

@router.get("/health", summary="Health Check")
async def health_check():
    """Health check endpoint for Campaign Creator."""
    return {
        "status": "healthy",
        "service": "campaign_creator",
        "version": "1.0.0",
        "modules": {
            "orchestrator": "available",
            "prompt_builder": "available",
            "brand_dna_sync": "available",
            "asset_audit": "available",
            "channel_pack": "available",
            "campaign_storage": "available",
        }
    }
