"""API endpoints for Product Marketing Suite."""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from services.product_marketing import (
    ProductMarketingOrchestrator,
    BrandDNASyncService,
    AssetAuditService,
    ChannelPackService,
    ProductAnimationService,
    ProductAnimationRequest,
    ProductVideoService,
    ProductVideoRequest,
    ProductAvatarService,
    ProductAvatarRequest,
)
from services.product_marketing.campaign_storage import CampaignStorageService
from services.product_marketing.product_image_service import ProductImageService, ProductImageRequest
from middleware.auth_middleware import get_current_user
from utils.logger_utils import get_service_logger
from services.database import get_db
from sqlalchemy.orm import Session


logger = get_service_logger("api.product_marketing")
router = APIRouter(prefix="/api/product-marketing", tags=["product-marketing"])


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

def get_orchestrator() -> ProductMarketingOrchestrator:
    """Get Product Marketing Orchestrator instance."""
    return ProductMarketingOrchestrator()


def get_campaign_storage() -> CampaignStorageService:
    """Get Campaign Storage Service instance."""
    return CampaignStorageService()


def _require_user_id(current_user: Dict[str, Any], operation: str) -> str:
    """Ensure user_id is available for protected operations."""
    user_id = current_user.get("sub") or current_user.get("user_id") or current_user.get("id")
    if not user_id:
        logger.error(
            "[Product Marketing] ❌ Missing user_id for %s operation - blocking request",
            operation,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authenticated user required for product marketing operations.",
        )
    return str(user_id)


# ====================
# CAMPAIGN ENDPOINTS
# ====================

@router.post("/campaigns/validate-preflight", summary="Validate Campaign Pre-flight")
async def validate_campaign_preflight(
    request: CampaignCreateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    orchestrator: ProductMarketingOrchestrator = Depends(get_orchestrator)
):
    """Validate campaign blueprint against subscription limits before creation.
    
    This endpoint:
    - Creates a temporary blueprint to estimate costs
    - Validates subscription limits
    - Returns cost estimates and validation results
    - Does NOT save anything to database
    """
    try:
        user_id = _require_user_id(current_user, "campaign pre-flight validation")
        logger.info(f"[Product Marketing] Pre-flight validation for user {user_id}")
        
        # Create temporary blueprint for validation (not saved)
        campaign_data = {
            "campaign_name": request.campaign_name or "Temporary Campaign",
            "goal": request.goal,
            "kpi": request.kpi,
            "channels": request.channels,
        }
        
        blueprint = orchestrator.create_campaign_blueprint(user_id, campaign_data)
        
        # Run pre-flight validation
        validation_result = orchestrator.validate_campaign_preflight(user_id, blueprint)
        
        logger.info(f"[Product Marketing] ✅ Pre-flight validation completed: can_proceed={validation_result.get('can_proceed')}")
        return validation_result
        
    except Exception as e:
        logger.error(f"[Product Marketing] ❌ Error in pre-flight validation: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Pre-flight validation failed: {str(e)}")


@router.post("/campaigns/create-blueprint", summary="Create Campaign Blueprint")
async def create_campaign_blueprint(
    request: CampaignCreateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    orchestrator: ProductMarketingOrchestrator = Depends(get_orchestrator)
):
    """Create a campaign blueprint with personalized asset nodes.
    
    This endpoint:
    - Uses onboarding data to personalize the blueprint
    - Generates campaign phases (teaser, launch, nurture)
    - Creates asset nodes for each phase and channel
    - Returns blueprint ready for AI proposal generation
    """
    try:
        user_id = _require_user_id(current_user, "campaign blueprint creation")
        logger.info(f"[Product Marketing] Creating blueprint for user {user_id}: {request.campaign_name}")
        
        campaign_data = {
            "campaign_name": request.campaign_name,
            "goal": request.goal,
            "kpi": request.kpi,
            "channels": request.channels,
        }
        
        blueprint = orchestrator.create_campaign_blueprint(user_id, campaign_data)
        
        # Convert blueprint to dict for JSON response
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
        
        # Save to database
        campaign_storage = get_campaign_storage()
        campaign_storage.save_campaign(user_id, blueprint_dict)
        
        logger.info(f"[Product Marketing] ✅ Blueprint created and saved: {blueprint.campaign_id}")
        return blueprint_dict
        
    except Exception as e:
        logger.error(f"[Product Marketing] ❌ Error creating blueprint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Campaign blueprint creation failed: {str(e)}")


@router.post("/campaigns/{campaign_id}/generate-proposals", summary="Generate Asset Proposals")
async def generate_asset_proposals(
    campaign_id: str,
    request: AssetProposalRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    orchestrator: ProductMarketingOrchestrator = Depends(get_orchestrator)
):
    """Generate AI proposals for all assets in a campaign blueprint.
    
    This endpoint:
    - Uses specialized marketing prompts with brand DNA
    - Recommends templates, providers, and settings
    - Provides cost estimates
    - Returns proposals ready for user approval
    """
    try:
        user_id = _require_user_id(current_user, "asset proposal generation")
        logger.info(f"[Product Marketing] Generating proposals for campaign {campaign_id}")
        
        # Fetch blueprint from database
        campaign_storage = get_campaign_storage()
        campaign = campaign_storage.get_campaign(user_id, campaign_id)
        
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Reconstruct blueprint from database
        from services.product_marketing.orchestrator import CampaignBlueprint, CampaignAssetNode
        
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
        
        # Save proposals to database
        try:
            campaign_storage.save_proposals(user_id, campaign_id, proposals)
            logger.info(f"[Product Marketing] ✅ Saved {proposals['total_assets']} proposals to database")
        except Exception as save_error:
            logger.error(f"[Product Marketing] ⚠️ Failed to save proposals to database: {str(save_error)}")
            # Continue even if save fails - proposals are still returned to user
            # This allows the workflow to continue, but proposals won't persist
        
        logger.info(f"[Product Marketing] ✅ Generated {proposals['total_assets']} proposals")
        return proposals
        
    except Exception as e:
        logger.error(f"[Product Marketing] ❌ Error generating proposals: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Asset proposal generation failed: {str(e)}")


@router.post("/assets/generate", summary="Generate Asset")
async def generate_asset(
    request: AssetGenerateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    orchestrator: ProductMarketingOrchestrator = Depends(get_orchestrator)
):
    """Generate a single asset using Image Studio APIs.
    
    This endpoint:
    - Reuses existing Image Studio APIs
    - Applies specialized marketing prompts
    - Automatically tracks assets in Asset Library
    - Validates subscription limits
    - Updates campaign status after generation
    """
    try:
        user_id = _require_user_id(current_user, "asset generation")
        logger.info(f"[Product Marketing] Generating asset for user {user_id}")
        
        result = await orchestrator.generate_asset(
            user_id=user_id,
            asset_proposal=request.asset_proposal,
            product_context=request.product_context,
        )
        
        # Update campaign status if asset was generated successfully
        if result.get('success'):
            campaign_id = request.asset_proposal.get('campaign_id')
            if not campaign_id:
                # Try to extract from asset_id
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
                        # Update proposal status to 'generating' or 'ready'
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
                                    logger.info(f"[Product Marketing] ✅ Updated proposal status for {asset_node_id}")
                            finally:
                                db.close()
                        
                        # Check if all assets are ready and update campaign status
                        # (This could be enhanced to check all proposals)
                        logger.info(f"[Product Marketing] ✅ Asset generated for campaign {campaign_id}")
                except Exception as update_error:
                    logger.warning(f"[Product Marketing] ⚠️ Could not update campaign status: {str(update_error)}")
                    # Don't fail the request if status update fails
        
        logger.info(f"[Product Marketing] ✅ Asset generated successfully")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Product Marketing] ❌ Error generating asset: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Asset generation failed: {str(e)}")


# ====================
# BRAND DNA ENDPOINTS
# ====================

@router.get("/brand-dna", summary="Get Brand DNA Tokens")
async def get_brand_dna(
    current_user: Dict[str, Any] = Depends(get_current_user),
    brand_dna_sync: BrandDNASyncService = Depends(lambda: BrandDNASyncService())
):
    """Get brand DNA tokens for the authenticated user.
    
    Returns normalized brand DNA from onboarding and persona data.
    """
    try:
        user_id = _require_user_id(current_user, "brand DNA retrieval")
        brand_tokens = brand_dna_sync.get_brand_dna_tokens(user_id)
        
        return {"brand_dna": brand_tokens}
        
    except Exception as e:
        logger.error(f"[Product Marketing] ❌ Error getting brand DNA: {str(e)}", exc_info=True)
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
        logger.error(f"[Product Marketing] ❌ Error getting channel DNA: {str(e)}", exc_info=True)
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
        logger.error(f"[Product Marketing] ❌ Error auditing asset: {str(e)}", exc_info=True)
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
        logger.error(f"[Product Marketing] ❌ Error getting channel pack: {str(e)}", exc_info=True)
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
        logger.error(f"[Product Marketing] ❌ Error listing campaigns: {str(e)}", exc_info=True)
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
        logger.error(f"[Product Marketing] ❌ Error getting campaign: {str(e)}", exc_info=True)
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
        logger.error(f"[Product Marketing] ❌ Error getting proposals: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ====================
# PRODUCT ASSET ENDPOINTS (Product Marketing Suite - Product Assets)
# ====================

class ProductPhotoshootRequest(BaseModel):
    """Request for product image photoshoot generation."""
    product_name: str = Field(..., description="Product name")
    product_description: str = Field(..., description="Product description")
    environment: str = Field(default="studio", description="Environment: studio, lifestyle, outdoor, minimalist, luxury")
    background_style: str = Field(default="white", description="Background: white, transparent, lifestyle, branded")
    lighting: str = Field(default="natural", description="Lighting: natural, studio, dramatic, soft")
    product_variant: Optional[str] = Field(None, description="Product variant (color, size, etc.)")
    angle: Optional[str] = Field(None, description="Product angle: front, side, top, 360")
    style: str = Field(default="photorealistic", description="Style: photorealistic, minimalist, luxury, technical")
    resolution: str = Field(default="1024x1024", description="Resolution (e.g., 1024x1024, 1280x720)")
    num_variations: int = Field(default=1, description="Number of variations to generate")
    brand_colors: Optional[List[str]] = Field(None, description="Brand color palette")
    additional_context: Optional[str] = Field(None, description="Additional context for generation")


def get_product_image_service() -> ProductImageService:
    """Get Product Image Service instance."""
    return ProductImageService()


@router.post("/products/photoshoot", summary="Generate Product Image")
async def generate_product_image(
    request: ProductPhotoshootRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    product_image_service: ProductImageService = Depends(get_product_image_service),
    brand_dna_sync: BrandDNASyncService = Depends(lambda: BrandDNASyncService())
):
    """Generate professional product images using AI.
    
    This endpoint:
    - Generates product images optimized for e-commerce
    - Supports multiple environments and styles
    - Integrates with brand DNA for personalization
    - Automatically saves to Asset Library
    """
    try:
        user_id = _require_user_id(current_user, "product image generation")
        logger.info(f"[Product Marketing] Generating product image for '{request.product_name}'")
        
        # Get brand DNA for personalization
        brand_context = None
        try:
            brand_dna = brand_dna_sync.get_brand_dna_tokens(user_id)
            brand_context = {
                "visual_identity": brand_dna.get("visual_identity", {}),
                "persona": brand_dna.get("persona", {}),
            }
        except Exception as brand_error:
            logger.warning(f"[Product Marketing] Could not load brand DNA: {str(brand_error)}")
        
        # Convert request to service request
        service_request = ProductImageRequest(
            product_name=request.product_name,
            product_description=request.product_description,
            environment=request.environment,
            background_style=request.background_style,
            lighting=request.lighting,
            product_variant=request.product_variant,
            angle=request.angle,
            style=request.style,
            resolution=request.resolution,
            num_variations=request.num_variations,
            brand_colors=request.brand_colors,
            additional_context=request.additional_context,
        )
        
        # Generate product image
        result = await product_image_service.generate_product_image(
            request=service_request,
            user_id=user_id,
            brand_context=brand_context,
        )
        
        if not result.success:
            raise HTTPException(status_code=500, detail=result.error or "Product image generation failed")
        
        logger.info(f"[Product Marketing] ✅ Generated product image: {result.asset_id}")
        
        # Return result (image_bytes will be served via separate endpoint)
        return {
            "success": True,
            "product_name": result.product_name,
            "image_url": result.image_url,
            "asset_id": result.asset_id,
            "provider": result.provider,
            "model": result.model,
            "cost": result.cost,
            "generation_time": result.generation_time,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Product Marketing] ❌ Error generating product image: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Product image generation failed: {str(e)}")


@router.get("/products/images/{filename}", summary="Serve Product Image")
async def serve_product_image(
    filename: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Serve generated product images."""
    try:
        from fastapi.responses import FileResponse
        from pathlib import Path
        
        _require_user_id(current_user, "serving product image")
        
        # Locate image file
        base_dir = Path(__file__).parent.parent.parent
        image_path = base_dir / "product_images" / filename
        
        if not image_path.exists():
            raise HTTPException(status_code=404, detail="Image not found")
        
        return FileResponse(
            path=str(image_path),
            media_type="image/png",
            filename=filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Product Marketing] ❌ Error serving product image: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ====================
# PRODUCT ANIMATION ENDPOINTS
# ====================

class ProductAnimationRequestModel(BaseModel):
    """Request for product animation."""
    product_image_base64: str = Field(..., description="Base64 encoded product image")
    animation_type: str = Field(..., description="Animation type: reveal, rotation, demo, lifestyle")
    product_name: str = Field(..., description="Product name")
    product_description: Optional[str] = Field(None, description="Product description")
    resolution: str = Field(default="720p", description="Video resolution: 480p, 720p, 1080p")
    duration: int = Field(default=5, description="Video duration: 5 or 10 seconds")
    audio_base64: Optional[str] = Field(None, description="Optional audio for synchronization")
    additional_context: Optional[str] = Field(None, description="Additional context for animation")


def get_product_animation_service() -> ProductAnimationService:
    """Get Product Animation Service instance."""
    return ProductAnimationService()


@router.post("/products/animate", summary="Animate Product Image")
async def animate_product(
    request: ProductAnimationRequestModel,
    current_user: Dict[str, Any] = Depends(get_current_user),
    animation_service: ProductAnimationService = Depends(get_product_animation_service),
    brand_dna_sync: BrandDNASyncService = Depends(lambda: BrandDNASyncService())
):
    """Animate a product image into a video.
    
    This endpoint:
    - Uses WAN 2.5 Image-to-Video via Transform Studio
    - Supports multiple animation types (reveal, rotation, demo, lifestyle)
    - Applies brand DNA for consistent styling
    - Returns video URL and metadata
    """
    try:
        user_id = _require_user_id(current_user, "product animation")
        logger.info(f"[Product Marketing] Animating product '{request.product_name}' with type '{request.animation_type}'")
        
        # Get brand DNA for personalization
        brand_context = None
        try:
            brand_dna = brand_dna_sync.get_brand_dna_tokens(user_id)
            brand_context = {
                "visual_identity": brand_dna.get("visual_identity", {}),
                "persona": brand_dna.get("persona", {}),
            }
        except Exception as brand_error:
            logger.warning(f"[Product Marketing] Could not load brand DNA: {str(brand_error)}")
        
        # Create animation request
        animation_request = ProductAnimationRequest(
            product_image_base64=request.product_image_base64,
            animation_type=request.animation_type,
            product_name=request.product_name,
            product_description=request.product_description,
            resolution=request.resolution,
            duration=request.duration,
            audio_base64=request.audio_base64,
            brand_context=brand_context,
            additional_context=request.additional_context,
        )
        
        # Generate animation
        result = await animation_service.animate_product(animation_request, user_id)
        
        logger.info(f"[Product Marketing] ✅ Product animation completed: cost=${result.get('cost', 0):.2f}")
        
        return {
            "success": True,
            "product_name": result.get("product_name"),
            "animation_type": result.get("animation_type"),
            "video_url": result.get("video_url"),
            "video_filename": result.get("filename"),
            "cost": result.get("cost", 0.0),
            "resolution": request.resolution,
            "duration": request.duration,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Product Marketing] ❌ Error animating product: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Product animation failed: {str(e)}")


@router.post("/products/animate/reveal", summary="Create Product Reveal Animation")
async def create_product_reveal(
    request: ProductAnimationRequestModel,
    current_user: Dict[str, Any] = Depends(get_current_user),
    animation_service: ProductAnimationService = Depends(get_product_animation_service),
    brand_dna_sync: BrandDNASyncService = Depends(lambda: BrandDNASyncService())
):
    """Create product reveal animation (elegant product unveiling)."""
    try:
        user_id = _require_user_id(current_user, "product reveal animation")
        
        # Get brand DNA
        brand_context = None
        try:
            brand_dna = brand_dna_sync.get_brand_dna_tokens(user_id)
            brand_context = {
                "visual_identity": brand_dna.get("visual_identity", {}),
                "persona": brand_dna.get("persona", {}),
            }
        except Exception:
            pass
        
        result = await animation_service.create_product_reveal(
            product_image_base64=request.product_image_base64,
            product_name=request.product_name,
            product_description=request.product_description,
            user_id=user_id,
            resolution=request.resolution,
            duration=request.duration,
            brand_context=brand_context
        )
        
        return {
            "success": True,
            "animation_type": "reveal",
            "video_url": result.get("video_url"),
            "cost": result.get("cost", 0.0),
        }
    except Exception as e:
        logger.error(f"[Product Marketing] ❌ Error creating reveal: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/products/animate/rotation", summary="Create Product Rotation Animation")
async def create_product_rotation(
    request: ProductAnimationRequestModel,
    current_user: Dict[str, Any] = Depends(get_current_user),
    animation_service: ProductAnimationService = Depends(get_product_animation_service),
    brand_dna_sync: BrandDNASyncService = Depends(lambda: BrandDNASyncService())
):
    """Create 360° product rotation animation."""
    try:
        user_id = _require_user_id(current_user, "product rotation animation")
        
        # Get brand DNA
        brand_context = None
        try:
            brand_dna = brand_dna_sync.get_brand_dna_tokens(user_id)
            brand_context = {
                "visual_identity": brand_dna.get("visual_identity", {}),
                "persona": brand_dna.get("persona", {}),
            }
        except Exception:
            pass
        
        result = await animation_service.create_product_rotation(
            product_image_base64=request.product_image_base64,
            product_name=request.product_name,
            product_description=request.product_description,
            user_id=user_id,
            resolution=request.resolution,
            duration=request.duration or 10,  # Default 10s for rotation
            brand_context=brand_context
        )
        
        return {
            "success": True,
            "animation_type": "rotation",
            "video_url": result.get("video_url"),
            "cost": result.get("cost", 0.0),
        }
    except Exception as e:
        logger.error(f"[Product Marketing] ❌ Error creating rotation: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/products/animate/demo", summary="Create Product Demo Animation")
async def create_product_demo_animation(
    request: ProductAnimationRequestModel,
    current_user: Dict[str, Any] = Depends(get_current_user),
    animation_service: ProductAnimationService = Depends(get_product_animation_service),
    brand_dna_sync: BrandDNASyncService = Depends(lambda: BrandDNASyncService())
):
    """Create product demo animation (image-to-video: product in use, demonstrating features)."""
    try:
        user_id = _require_user_id(current_user, "product demo animation")
        
        # Get brand DNA
        brand_context = None
        try:
            brand_dna = brand_dna_sync.get_brand_dna_tokens(user_id)
            brand_context = {
                "visual_identity": brand_dna.get("visual_identity", {}),
                "persona": brand_dna.get("persona", {}),
            }
        except Exception:
            pass
        
        result = await animation_service.create_product_demo(
            product_image_base64=request.product_image_base64,
            product_name=request.product_name,
            product_description=request.product_description,
            user_id=user_id,
            resolution=request.resolution,
            duration=request.duration or 10,  # Default 10s for demo
            audio_base64=request.audio_base64,
            brand_context=brand_context
        )
        
        return {
            "success": True,
            "animation_type": "demo",
            "video_subtype": "animation",  # Image-to-video
            "video_url": result.get("video_url"),
            "cost": result.get("cost", 0.0),
        }
    except Exception as e:
        logger.error(f"[Product Marketing] ❌ Error creating demo animation: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ====================
# PRODUCT VIDEO ENDPOINTS (Text-to-Video)
# ====================

class ProductVideoRequestModel(BaseModel):
    """Request for product demo video (text-to-video)."""
    product_name: str = Field(..., description="Product name")
    product_description: str = Field(..., description="Product description")
    video_type: str = Field(default="demo", description="Video type: demo, storytelling, feature_highlight, launch")
    resolution: str = Field(default="720p", description="Video resolution: 480p, 720p, 1080p")
    duration: int = Field(default=10, description="Video duration: 5 or 10 seconds")
    audio_base64: Optional[str] = Field(None, description="Optional audio for synchronization")
    additional_context: Optional[str] = Field(None, description="Additional context for video")


def get_product_video_service() -> ProductVideoService:
    """Get Product Video Service instance."""
    return ProductVideoService()


@router.post("/products/video/demo", summary="Create Product Demo Video (Text-to-Video)")
async def create_product_demo_video(
    request: ProductVideoRequestModel,
    current_user: Dict[str, Any] = Depends(get_current_user),
    video_service: ProductVideoService = Depends(get_product_video_service),
    brand_dna_sync: BrandDNASyncService = Depends(lambda: BrandDNASyncService())
):
    """Create product demo video using WAN 2.5 Text-to-Video.
    
    This endpoint:
    - Uses WAN 2.5 Text-to-Video via main_video_generation
    - Generates video from product description (no image required)
    - Applies brand DNA for consistent styling
    - Returns video URL and metadata
    """
    try:
        user_id = _require_user_id(current_user, "product demo video")
        logger.info(f"[Product Marketing] Creating {request.video_type} video for product '{request.product_name}'")
        
        # Get brand DNA for personalization
        brand_context = None
        try:
            brand_dna = brand_dna_sync.get_brand_dna_tokens(user_id)
            brand_context = {
                "visual_identity": brand_dna.get("visual_identity", {}),
                "persona": brand_dna.get("persona", {}),
            }
        except Exception as brand_error:
            logger.warning(f"[Product Marketing] Could not load brand DNA: {str(brand_error)}")
        
        # Create video request
        video_request = ProductVideoRequest(
            product_name=request.product_name,
            product_description=request.product_description,
            video_type=request.video_type,
            resolution=request.resolution,
            duration=request.duration,
            audio_base64=request.audio_base64,
            brand_context=brand_context,
            additional_context=request.additional_context,
        )
        
        # Generate video using unified ai_video_generate()
        result = await video_service.generate_product_video(video_request, user_id)
        
        logger.info(f"[Product Marketing] ✅ Product demo video completed: cost=${result.get('cost', 0):.2f}")
        
        return {
            "success": True,
            "product_name": result.get("product_name"),
            "video_type": result.get("video_type"),
            "video_url": result.get("file_url"),
            "video_filename": result.get("filename"),
            "cost": result.get("cost", 0.0),
            "resolution": request.resolution,
            "duration": request.duration,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Product Marketing] ❌ Error creating product demo video: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Product demo video generation failed: {str(e)}")


@router.post("/products/video/storytelling", summary="Create Product Storytelling Video")
async def create_product_storytelling(
    request: ProductVideoRequestModel,
    current_user: Dict[str, Any] = Depends(get_current_user),
    video_service: ProductVideoService = Depends(get_product_video_service),
    brand_dna_sync: BrandDNASyncService = Depends(lambda: BrandDNASyncService())
):
    """Create product storytelling video (narrative-driven product showcase)."""
    try:
        user_id = _require_user_id(current_user, "product storytelling video")
        
        # Get brand DNA
        brand_context = None
        try:
            brand_dna = brand_dna_sync.get_brand_dna_tokens(user_id)
            brand_context = {
                "visual_identity": brand_dna.get("visual_identity", {}),
                "persona": brand_dna.get("persona", {}),
            }
        except Exception:
            pass
        
        result = await video_service.create_product_storytelling(
            product_name=request.product_name,
            product_description=request.product_description,
            user_id=user_id,
            resolution=request.resolution,
            duration=request.duration,
            audio_base64=request.audio_base64,
            brand_context=brand_context
        )
        
        return {
            "success": True,
            "video_type": "storytelling",
            "video_url": result.get("file_url"),
            "cost": result.get("cost", 0.0),
        }
    except Exception as e:
        logger.error(f"[Product Marketing] ❌ Error creating storytelling video: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/products/video/feature-highlight", summary="Create Product Feature Highlight Video")
async def create_product_feature_highlight(
    request: ProductVideoRequestModel,
    current_user: Dict[str, Any] = Depends(get_current_user),
    video_service: ProductVideoService = Depends(get_product_video_service),
    brand_dna_sync: BrandDNASyncService = Depends(lambda: BrandDNASyncService())
):
    """Create product feature highlight video (close-up shots of key features)."""
    try:
        user_id = _require_user_id(current_user, "product feature highlight video")
        
        # Get brand DNA
        brand_context = None
        try:
            brand_dna = brand_dna_sync.get_brand_dna_tokens(user_id)
            brand_context = {
                "visual_identity": brand_dna.get("visual_identity", {}),
                "persona": brand_dna.get("persona", {}),
            }
        except Exception:
            pass
        
        result = await video_service.create_product_feature_highlight(
            product_name=request.product_name,
            product_description=request.product_description,
            user_id=user_id,
            resolution=request.resolution,
            duration=request.duration,
            audio_base64=request.audio_base64,
            brand_context=brand_context
        )
        
        return {
            "success": True,
            "video_type": "feature_highlight",
            "video_url": result.get("file_url"),
            "cost": result.get("cost", 0.0),
        }
    except Exception as e:
        logger.error(f"[Product Marketing] ❌ Error creating feature highlight video: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/products/video/launch", summary="Create Product Launch Video")
async def create_product_launch(
    request: ProductVideoRequestModel,
    current_user: Dict[str, Any] = Depends(get_current_user),
    video_service: ProductVideoService = Depends(get_product_video_service),
    brand_dna_sync: BrandDNASyncService = Depends(lambda: BrandDNASyncService())
):
    """Create product launch video (exciting unveiling, launch event aesthetic)."""
    try:
        user_id = _require_user_id(current_user, "product launch video")
        
        # Get brand DNA
        brand_context = None
        try:
            brand_dna = brand_dna_sync.get_brand_dna_tokens(user_id)
            brand_context = {
                "visual_identity": brand_dna.get("visual_identity", {}),
                "persona": brand_dna.get("persona", {}),
            }
        except Exception:
            pass
        
        result = await video_service.create_product_launch(
            product_name=request.product_name,
            product_description=request.product_description,
            user_id=user_id,
            resolution=request.resolution or "1080p",  # Higher quality for launch
            duration=request.duration,
            audio_base64=request.audio_base64,
            brand_context=brand_context
        )
        
        return {
            "success": True,
            "video_type": "launch",
            "video_url": result.get("file_url"),
            "cost": result.get("cost", 0.0),
        }
    except Exception as e:
        logger.error(f"[Product Marketing] ❌ Error creating launch video: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/products/videos/{user_id}/{filename}", summary="Serve Product Video")
async def serve_product_video(
    user_id: str,
    filename: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Serve generated product videos."""
    try:
        from fastapi.responses import FileResponse
        from pathlib import Path
        
        # Verify user owns the video
        current_user_id = _require_user_id(current_user, "serving product video")
        if current_user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Locate video file
        base_dir = Path(__file__).parent.parent.parent
        video_path = base_dir / "product_videos" / user_id / filename
        
        if not video_path.exists():
            raise HTTPException(status_code=404, detail="Video not found")
        
        return FileResponse(
            path=str(video_path),
            media_type="video/mp4",
            filename=filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Product Marketing] ❌ Error serving product video: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ====================
# HEALTH CHECK
# ====================

@router.get("/health", summary="Health Check")
async def health_check():
    """Health check endpoint for Product Marketing Suite."""
    return {
        "status": "healthy",
        "service": "product_marketing",
        "version": "1.0.0",
        "modules": {
            "orchestrator": "available",
            "prompt_builder": "available",
            "brand_dna_sync": "available",
            "asset_audit": "available",
            "channel_pack": "available",
            "product_image_service": "available",
            "product_animation_service": "available",
            "product_video_service": "available",
        }
    }

