"""
Product Marketing Orchestrator
Main service that orchestrates campaign workflows and asset generation.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from loguru import logger

from services.image_studio import ImageStudioManager, CreateStudioRequest
from .prompt_builder import ProductMarketingPromptBuilder
from .brand_dna_sync import BrandDNASyncService
from .asset_audit import AssetAuditService
from .channel_pack import ChannelPackService
from services.database import SessionLocal
from services.subscription import PricingService
from services.subscription.preflight_validator import validate_image_generation_operations


@dataclass
class CampaignAssetNode:
    """Represents an asset node in the campaign graph."""
    asset_id: str
    asset_type: str  # image, video, text, audio
    channel: str
    status: str  # draft, generating, ready, approved
    prompt: Optional[str] = None
    template_id: Optional[str] = None
    provider: Optional[str] = None
    cost_estimate: Optional[float] = None
    generated_asset_id: Optional[int] = None  # Asset Library ID


@dataclass
class CampaignBlueprint:
    """Campaign blueprint with phases and asset nodes."""
    campaign_id: str
    campaign_name: str
    goal: str
    kpi: Optional[str] = None
    phases: List[Dict[str, Any]] = None  # teaser, launch, nurture
    asset_nodes: List[CampaignAssetNode] = None
    channels: List[str] = None
    status: str = "draft"  # draft, generating, ready, published


class ProductMarketingOrchestrator:
    """Main orchestrator for Product Marketing Suite."""
    
    def __init__(self):
        """Initialize Product Marketing Orchestrator."""
        self.image_studio = ImageStudioManager()
        self.prompt_builder = ProductMarketingPromptBuilder()
        self.brand_dna_sync = BrandDNASyncService()
        self.asset_audit = AssetAuditService()
        self.channel_pack = ChannelPackService()
        self.logger = logger
        logger.info("[Product Marketing Orchestrator] Initialized")
    
    def create_campaign_blueprint(
        self,
        user_id: str,
        campaign_data: Dict[str, Any]
    ) -> CampaignBlueprint:
        """
        Create campaign blueprint from user input and onboarding data.
        
        Args:
            user_id: User ID
            campaign_data: Campaign information (name, goal, channels, etc.)
            
        Returns:
            Campaign blueprint with asset nodes
        """
        try:
            import time
            campaign_id = campaign_data.get('campaign_id') or f"campaign_{user_id}_{int(time.time())}"
            campaign_name = campaign_data.get('campaign_name', 'New Campaign')
            goal = campaign_data.get('goal', 'product_launch')
            channels = campaign_data.get('channels', [])
            
            # Get brand DNA for personalization
            brand_dna = self.brand_dna_sync.get_brand_dna_tokens(user_id)
            
            # Build campaign phases
            phases = self._build_campaign_phases(goal, channels)
            
            # Generate asset nodes for each phase and channel
            asset_nodes = []
            for phase in phases:
                phase_name = phase.get('name')
                for channel in channels:
                    # Determine required assets for this phase + channel
                    required_assets = self._get_required_assets(phase_name, channel)
                    
                    for asset_type in required_assets:
                        asset_node = CampaignAssetNode(
                            asset_id=f"{campaign_id}_{phase_name}_{channel}_{asset_type}",
                            asset_type=asset_type,
                            channel=channel,
                            status="draft",
                        )
                        asset_nodes.append(asset_node)
            
            blueprint = CampaignBlueprint(
                campaign_id=campaign_id,
                campaign_name=campaign_name,
                goal=goal,
                kpi=campaign_data.get('kpi'),
                phases=phases,
                asset_nodes=asset_nodes,
                channels=channels,
                status="draft",
            )
            
            logger.info(f"[Orchestrator] Created blueprint for campaign {campaign_id} with {len(asset_nodes)} assets")
            return blueprint
            
        except Exception as e:
            logger.error(f"[Orchestrator] Error creating blueprint: {str(e)}")
            raise
    
    def generate_asset_proposals(
        self,
        user_id: str,
        blueprint: CampaignBlueprint,
        product_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate AI proposals for each asset node in the blueprint.
        
        Args:
            user_id: User ID
            blueprint: Campaign blueprint
            product_context: Product information
            
        Returns:
            Dictionary with proposals for each asset node
        """
        try:
            proposals = {}
            
            for asset_node in blueprint.asset_nodes:
                # Build specialized prompt based on asset type and channel
                if asset_node.asset_type == "image":
                    base_prompt = product_context.get('product_description', 'Product image') if product_context else 'Marketing image'
                    enhanced_prompt = self.prompt_builder.build_marketing_image_prompt(
                        base_prompt=base_prompt,
                        user_id=user_id,
                        channel=asset_node.channel,
                        asset_type="hero_image",
                        product_context=product_context,
                    )
                    
                    # Get channel pack for template recommendations
                    channel_pack = self.channel_pack.get_channel_pack(asset_node.channel)
                    recommended_template = channel_pack.get('templates', [{}])[0] if channel_pack.get('templates') else None
                    
                    # Estimate cost
                    cost_estimate = self._estimate_asset_cost("image", asset_node.channel)
                    
                    proposals[asset_node.asset_id] = {
                        "asset_id": asset_node.asset_id,
                        "asset_type": asset_node.asset_type,
                        "channel": asset_node.channel,
                        "campaign_id": blueprint.campaign_id,  # Include campaign_id for tracking
                        "proposed_prompt": enhanced_prompt,
                        "recommended_template": recommended_template.get('id') if recommended_template else None,
                        "recommended_provider": recommended_template.get('recommended_provider', 'wavespeed') if recommended_template else 'wavespeed',
                        "cost_estimate": cost_estimate,
                        "concept_summary": self._generate_concept_summary(enhanced_prompt),
                    }
                
                elif asset_node.asset_type == "video":
                    # Video asset proposals - determine if animation (image-to-video) or demo (text-to-video)
                    # Default to animation if we have product image, otherwise demo
                    video_subtype = asset_proposal.get('video_subtype', 'animation') if 'asset_proposal' in locals() else 'demo'
                    
                    # For demo videos (text-to-video), we need product description
                    if video_subtype == "demo" or not product_context or not product_context.get('product_image_base64'):
                        # Text-to-video demo video
                        video_type = "demo"  # Default, can be customized
                        if asset_node.channel in ["tiktok", "instagram"]:
                            video_type = "storytelling"  # Storytelling for social media
                        elif asset_node.channel in ["linkedin", "youtube"]:
                            video_type = "feature_highlight"  # Feature highlights for professional
                        
                        # Estimate cost for text-to-video (WAN 2.5: $0.05-$0.15/second)
                        duration = 10  # Default 10s for demo videos
                        resolution = "720p"  # Default
                        cost_per_second = 0.10 if resolution == "720p" else (0.15 if resolution == "1080p" else 0.05)
                        cost_estimate = duration * cost_per_second
                        
                        proposals[asset_node.asset_id] = {
                            "asset_id": asset_node.asset_id,
                            "asset_type": asset_node.asset_type,
                            "video_subtype": "demo",  # Text-to-video
                            "channel": asset_node.channel,
                            "campaign_id": blueprint.campaign_id,
                            "video_type": video_type,
                            "duration": duration,
                            "resolution": resolution,
                            "cost_estimate": cost_estimate,
                            "concept_summary": f"Product {video_type} video optimized for {asset_node.channel}",
                            "note": "Text-to-video demo - requires product description",
                        }
                    else:
                        # Image-to-video animation
                        animation_type = "reveal"  # Default
                        if asset_node.channel in ["tiktok", "instagram", "youtube"]:
                            animation_type = "demo"  # Demo animations for social media
                        elif asset_node.channel in ["linkedin", "facebook"]:
                            animation_type = "reveal"  # Professional reveal for B2B
                        
                        # Estimate cost for image-to-video (WAN 2.5: $0.05-$0.15/second)
                        duration = 5  # Default 5s for animations
                        resolution = "720p"  # Default
                        cost_per_second = 0.10 if resolution == "720p" else (0.15 if resolution == "1080p" else 0.05)
                        cost_estimate = duration * cost_per_second
                        
                        proposals[asset_node.asset_id] = {
                            "asset_id": asset_node.asset_id,
                            "asset_type": asset_node.asset_type,
                            "video_subtype": "animation",  # Image-to-video
                            "channel": asset_node.channel,
                            "campaign_id": blueprint.campaign_id,
                            "animation_type": animation_type,
                            "duration": duration,
                            "resolution": resolution,
                            "cost_estimate": cost_estimate,
                            "concept_summary": f"Product {animation_type} animation optimized for {asset_node.channel}",
                            "note": "Requires product image - will be provided during generation",
                        }
                
                elif asset_node.asset_type == "text":
                    base_request = f"Write {asset_node.channel} {asset_node.asset_type} for product launch"
                    enhanced_prompt = self.prompt_builder.build_marketing_copy_prompt(
                        base_request=base_request,
                        user_id=user_id,
                        channel=asset_node.channel,
                        content_type="caption",
                        product_context=product_context,
                    )
                    
                    proposals[asset_node.asset_id] = {
                        "asset_id": asset_node.asset_id,
                        "asset_type": asset_node.asset_type,
                        "channel": asset_node.channel,
                        "campaign_id": blueprint.campaign_id,  # Include campaign_id for tracking
                        "proposed_prompt": enhanced_prompt,
                        "cost_estimate": 0.0,  # Text generation cost is minimal
                        "concept_summary": "Marketing copy optimized for channel and persona",
                    }
            
            logger.info(f"[Orchestrator] Generated {len(proposals)} asset proposals")
            return {"proposals": proposals, "total_assets": len(proposals)}
            
        except Exception as e:
            logger.error(f"[Orchestrator] Error generating proposals: {str(e)}")
            raise
    
    async def generate_asset(
        self,
        user_id: str,
        asset_proposal: Dict[str, Any],
        product_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a single asset using Image Studio APIs.
        
        Args:
            user_id: User ID
            asset_proposal: Asset proposal from generate_asset_proposals
            product_context: Product information
            
        Returns:
            Generated asset result
        """
        try:
            asset_type = asset_proposal.get('asset_type')
            
            if asset_type == "image":
                # Build CreateStudioRequest
                create_request = CreateStudioRequest(
                    prompt=asset_proposal.get('proposed_prompt'),
                    template_id=asset_proposal.get('recommended_template'),
                    provider=asset_proposal.get('recommended_provider', 'wavespeed'),
                    quality="premium",
                    enhance_prompt=True,
                    use_persona=True,
                    num_variations=1,
                )
                
                # Generate image using Image Studio
                result = await self.image_studio.create_image(create_request, user_id=user_id)
                
                # Asset is automatically tracked in Asset Library via Image Studio
                return {
                    "success": True,
                    "asset_type": "image",
                    "result": result,
                    "asset_library_ids": [
                        r.get('asset_id') for r in result.get('results', [])
                        if r.get('asset_id')
                    ],
                }
            
            elif asset_type == "video":
                # Check video subtype: "animation" (image-to-video) or "demo" (text-to-video)
                video_subtype = asset_proposal.get('video_subtype', 'animation')
                
                if video_subtype == "demo":
                    # Text-to-video: Product demo video from description
                    from .product_video_service import ProductVideoService, ProductVideoRequest
                    
                    # Get product info from context
                    product_name = product_context.get('product_name', 'Product') if product_context else 'Product'
                    product_description = product_context.get('product_description', '') if product_context else ''
                    
                    if not product_description:
                        raise ValueError("Product description required for text-to-video demo generation")
                    
                    # Get brand context
                    brand_dna = self.brand_dna_sync.get_brand_dna_tokens(user_id)
                    brand_context = {
                        "visual_identity": brand_dna.get("visual_identity", {}),
                        "persona": brand_dna.get("persona", {}),
                    }
                    
                    # Get video type from proposal or default
                    video_type = asset_proposal.get('video_type', 'demo')
                    
                    # Create video service
                    video_service = ProductVideoService()
                    
                    # Create video request
                    video_request = ProductVideoRequest(
                        product_name=product_name,
                        product_description=product_description,
                        video_type=video_type,
                        resolution=asset_proposal.get('resolution', '720p'),
                        duration=asset_proposal.get('duration', 10),
                        audio_base64=asset_proposal.get('audio_base64'),
                        brand_context=brand_context,
                        additional_context=asset_proposal.get('additional_context'),
                    )
                    
                    # Generate video using unified ai_video_generate()
                    result = await video_service.generate_product_video(video_request, user_id)
                    
                    # Extract campaign_id for metadata
                    campaign_id = asset_proposal.get('campaign_id')
                    asset_id = asset_proposal.get('asset_id', '')
                    
                    return {
                        "success": True,
                        "asset_type": "video",
                        "video_subtype": "demo",
                        "video_url": result.get('file_url'),
                        "video_filename": result.get('filename'),
                        "cost": result.get('cost', 0.0),
                        "video_type": video_type,
                        "campaign_id": campaign_id,
                        "asset_id": asset_id,
                    }
                
                else:
                    # Image-to-video: Product animation
                    from .product_animation_service import ProductAnimationService, ProductAnimationRequest
                    
                    # Get product image from proposal or product context
                    product_image_base64 = asset_proposal.get('product_image_base64')
                    if not product_image_base64 and product_context:
                        product_image_base64 = product_context.get('product_image_base64')
                    
                    if not product_image_base64:
                        raise ValueError("Product image required for image-to-video animation generation")
                    
                    # Get animation type from proposal or default to "reveal"
                    animation_type = asset_proposal.get('animation_type', 'reveal')
                    product_name = product_context.get('product_name', 'Product') if product_context else 'Product'
                    product_description = product_context.get('product_description') if product_context else None
                    
                    # Get brand context
                    brand_dna = self.brand_dna_sync.get_brand_dna_tokens(user_id)
                    brand_context = {
                        "visual_identity": brand_dna.get("visual_identity", {}),
                        "persona": brand_dna.get("persona", {}),
                    }
                    
                    # Create animation service
                    animation_service = ProductAnimationService()
                    
                    # Create animation request
                    animation_request = ProductAnimationRequest(
                        product_image_base64=product_image_base64,
                        animation_type=animation_type,
                        product_name=product_name,
                        product_description=product_description,
                        resolution=asset_proposal.get('resolution', '720p'),
                        duration=asset_proposal.get('duration', 5),
                        audio_base64=asset_proposal.get('audio_base64'),
                        brand_context=brand_context,
                        additional_context=asset_proposal.get('additional_context'),
                    )
                    
                    # Generate video
                    result = await animation_service.animate_product(animation_request, user_id)
                    
                    # Extract campaign_id for metadata
                    campaign_id = asset_proposal.get('campaign_id')
                    asset_id = asset_proposal.get('asset_id', '')
                    
                    return {
                        "success": True,
                        "asset_type": "video",
                        "video_subtype": "animation",
                        "video_url": result.get('video_url'),
                        "video_filename": result.get('filename'),
                        "cost": result.get('cost', 0.0),
                        "animation_type": animation_type,
                        "campaign_id": campaign_id,
                        "asset_id": asset_id,
                    }
            
            elif asset_type == "text":
                # Import text generation service and tracker
                import asyncio
                from services.llm_providers.main_text_generation import llm_text_gen
                from utils.text_asset_tracker import save_and_track_text_content
                from services.database import SessionLocal
                
                # Get enhanced prompt from proposal
                text_prompt = asset_proposal.get('proposed_prompt', '')
                channel = asset_proposal.get('channel', 'social')
                asset_id = asset_proposal.get('asset_id', '')
                
                # Extract campaign_id - try from asset_proposal first, then from asset_id
                # asset_id format: {campaign_id}_{phase}_{channel}_{type}
                campaign_id = asset_proposal.get('campaign_id')
                if not campaign_id and asset_id and '_' in asset_id:
                    # Try to extract: asset_id might be "campaign_user123_1234567890_teaser_instagram_text"
                    # We need to find where phase_name starts (common phases: teaser, launch, nurture)
                    parts = asset_id.split('_')
                    # Find phase indicator (usually one of: teaser, launch, nurture)
                    phase_indicators = ['teaser', 'launch', 'nurture', 'prelaunch', 'postlaunch']
                    phase_idx = None
                    for i, part in enumerate(parts):
                        if part.lower() in phase_indicators:
                            phase_idx = i
                            break
                    if phase_idx and phase_idx > 0:
                        # Campaign ID is everything before the phase
                        campaign_id = '_'.join(parts[:phase_idx])
                
                # If still not found, use None (metadata will work without it)
                if not campaign_id:
                    logger.warning(f"[Orchestrator] Could not extract campaign_id from asset_id: {asset_id}")
                
                # Build system prompt for marketing copy
                system_prompt = f"""You are an expert marketing copywriter specializing in {channel} content.
Generate compelling, on-brand marketing copy that:
- Is optimized for {channel} platform best practices
- Includes a clear call-to-action
- Uses appropriate tone and style for the platform
- Is concise and engaging
- Aligns with the product marketing context provided

Return only the final copy text without explanations or markdown formatting."""
                
                # Run synchronous llm_text_gen in thread pool
                logger.info(f"[Orchestrator] Generating text asset for channel: {channel}")
                generated_text = await asyncio.to_thread(
                    llm_text_gen,
                    prompt=text_prompt,
                    system_prompt=system_prompt,
                    user_id=user_id
                )
                
                if not generated_text or not generated_text.strip():
                    raise ValueError("Text generation returned empty content")
                
                # Save to Asset Library
                db = SessionLocal()
                asset_library_id = None
                try:
                    asset_library_id = save_and_track_text_content(
                        db=db,
                        user_id=user_id,
                        content=generated_text.strip(),
                        source_module="product_marketing",
                        title=f"{channel.title()} Copy: {asset_id.split('_')[-1] if '_' in asset_id else 'Marketing Copy'}",
                        description=f"Marketing copy for {channel} platform generated from campaign proposal",
                        prompt=text_prompt,
                        tags=["product_marketing", channel.lower(), "text", "copy"],
                        asset_metadata={
                            "campaign_id": campaign_id,
                            "asset_id": asset_id,
                            "asset_type": "text",
                            "channel": channel,
                            "concept_summary": asset_proposal.get('concept_summary'),
                        },
                        subdirectory="campaigns",
                        file_extension=".txt"
                    )
                    
                    if asset_library_id:
                        logger.info(f"[Orchestrator] ✅ Text asset saved to library: ID={asset_library_id}")
                    else:
                        logger.warning(f"[Orchestrator] ⚠️ Text asset tracking returned None")
                        
                except Exception as save_error:
                    logger.error(f"[Orchestrator] ⚠️ Failed to save text asset to library: {str(save_error)}")
                    # Continue even if save fails - text is still generated
                finally:
                    db.close()
                
                return {
                    "success": True,
                    "asset_type": "text",
                    "content": generated_text.strip(),
                    "asset_library_id": asset_library_id,
                    "channel": channel,
                }
            
            else:
                raise ValueError(f"Unsupported asset type: {asset_type}")
                
        except Exception as e:
            logger.error(f"[Orchestrator] Error generating asset: {str(e)}")
            raise
    
    def validate_campaign_preflight(
        self,
        user_id: str,
        blueprint: CampaignBlueprint
    ) -> Dict[str, Any]:
        """
        Validate campaign blueprint against subscription limits before generation.
        
        Args:
            user_id: User ID
            blueprint: Campaign blueprint
            
        Returns:
            Pre-flight validation results
        """
        try:
            db = SessionLocal()
            try:
                pricing_service = PricingService(db)
                
                # Count operations needed
                image_count = sum(1 for node in blueprint.asset_nodes if node.asset_type == "image")
                text_count = sum(1 for node in blueprint.asset_nodes if node.asset_type == "text")
                
                # Estimate total cost
                total_cost = 0.0
                for node in blueprint.asset_nodes:
                    if node.cost_estimate:
                        total_cost += node.cost_estimate
                
                # Validate image generation limits
                operations = []
                if image_count > 0:
                    operations.append({
                        'provider': 'stability',  # Default provider
                        'tokens_requested': 0,
                        'actual_provider_name': 'wavespeed',
                        'operation_type': 'image_generation',
                    })
                
                can_proceed, message, error_details = pricing_service.check_comprehensive_limits(
                    user_id=user_id,
                    operations=operations * image_count if operations else []
                )
                
                return {
                    "can_proceed": can_proceed,
                    "message": message,
                    "error_details": error_details,
                    "summary": {
                        "total_assets": len(blueprint.asset_nodes),
                        "image_count": image_count,
                        "text_count": text_count,
                        "estimated_cost": total_cost,
                    },
                }
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"[Orchestrator] Error in pre-flight validation: {str(e)}")
            return {
                "can_proceed": False,
                "message": f"Validation error: {str(e)}",
                "error_details": {},
            }
    
    def _build_campaign_phases(
        self,
        goal: str,
        channels: List[str]
    ) -> List[Dict[str, Any]]:
        """Build campaign phases based on goal."""
        if goal == "product_launch":
            return [
                {"name": "teaser", "duration_days": 7, "purpose": "Build anticipation"},
                {"name": "launch", "duration_days": 3, "purpose": "Official launch"},
                {"name": "nurture", "duration_days": 14, "purpose": "Sustain engagement"},
            ]
        else:
            return [
                {"name": "campaign", "duration_days": 30, "purpose": "Campaign execution"},
            ]
    
    def _get_required_assets(
        self,
        phase: str,
        channel: str
    ) -> List[str]:
        """Get required asset types for phase and channel."""
        # Default: image for all phases and channels
        assets = ["image"]
        
        # Add text/copy for social channels
        if channel in ["instagram", "linkedin", "facebook", "twitter"]:
            assets.append("text")
        
        return assets
    
    def _estimate_asset_cost(
        self,
        asset_type: str,
        channel: str
    ) -> float:
        """Estimate cost for asset generation."""
        if asset_type == "image":
            # Premium quality image: ~5-6 credits
            return 5.0
        elif asset_type == "video":
            # WAN 2.5 Image-to-Video: $0.05-$0.15/second
            # Default: 5 seconds at 720p = $0.50
            return 0.50
        elif asset_type == "text":
            return 0.0  # Text generation is typically included
        else:
            return 0.0
    
    def _generate_concept_summary(self, prompt: str) -> str:
        """Generate a brief concept summary from prompt."""
        # Simple extraction: take first 100 chars
        return prompt[:100] + "..." if len(prompt) > 100 else prompt

