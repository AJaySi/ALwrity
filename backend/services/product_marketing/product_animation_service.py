"""
Product Animation Service
Handles product animation workflows using Transform Studio (WAN 2.5 Image-to-Video).
"""

from typing import Dict, Any, Optional
from loguru import logger
from dataclasses import dataclass

from services.image_studio.transform_service import TransformStudioService, TransformImageToVideoRequest
from services.image_studio.studio_manager import ImageStudioManager
from utils.logging import get_service_logger
from utils.asset_tracker import save_asset_to_library
from services.database import SessionLocal

logger = get_service_logger("product_marketing.animation")


@dataclass
class ProductAnimationRequest:
    """Request for product animation."""
    product_image_base64: str
    animation_type: str  # "reveal", "rotation", "demo", "lifestyle"
    product_name: str
    product_description: Optional[str] = None
    resolution: str = "720p"  # 480p, 720p, 1080p
    duration: int = 5  # 5 or 10 seconds
    audio_base64: Optional[str] = None
    brand_context: Optional[Dict[str, Any]] = None
    additional_context: Optional[str] = None


class ProductAnimationService:
    """Service for product animation workflows."""
    
    def __init__(self):
        """Initialize Product Animation Service."""
        self.transform_service = TransformStudioService()
        self.image_studio = ImageStudioManager()
        logger.info("[Product Animation Service] Initialized")
    
    def _build_animation_prompt(
        self,
        animation_type: str,
        product_name: str,
        product_description: Optional[str],
        brand_context: Optional[Dict[str, Any]],
        additional_context: Optional[str]
    ) -> str:
        """
        Build animation prompt based on animation type and product context.
        
        Args:
            animation_type: Type of animation (reveal, rotation, demo, lifestyle)
            product_name: Product name
            product_description: Product description
            brand_context: Brand DNA context
            additional_context: Additional context
            
        Returns:
            Animation prompt
        """
        base_prompt = f"{product_name}"
        if product_description:
            base_prompt += f": {product_description}"
        
        # Animation-specific prompts
        animation_prompts = {
            "reveal": f"{base_prompt} elegantly revealing, smooth camera movement, professional product showcase, cinematic lighting",
            "rotation": f"{base_prompt} slowly rotating 360 degrees, smooth rotation, professional product photography, studio lighting, clean background",
            "demo": f"{base_prompt} in use, demonstrating features, dynamic movement, engaging presentation, professional product demo",
            "lifestyle": f"{base_prompt} in realistic lifestyle setting, natural environment, authentic use case, relatable scenario",
        }
        
        prompt = animation_prompts.get(animation_type, base_prompt)
        
        # Add brand context if available
        if brand_context:
            visual_identity = brand_context.get("visual_identity", {})
            if visual_identity.get("color_palette"):
                colors = ", ".join(visual_identity["color_palette"][:3])  # First 3 colors
                prompt += f", {colors} color scheme"
            
            if visual_identity.get("style_guidelines"):
                style = visual_identity["style_guidelines"].get("aesthetic", "")
                if style:
                    prompt += f", {style} style"
        
        # Add additional context
        if additional_context:
            prompt += f", {additional_context}"
        
        return prompt
    
    async def animate_product(
        self,
        request: ProductAnimationRequest,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Animate a product image into a video.
        
        Args:
            request: Product animation request
            user_id: User ID for tracking
            
        Returns:
            Animation result with video URL and metadata
        """
        try:
            logger.info(
                f"[Product Animation] Animating product '{request.product_name}' "
                f"with type '{request.animation_type}' for user {user_id}"
            )
            
            # Build animation prompt
            animation_prompt = self._build_animation_prompt(
                animation_type=request.animation_type,
                product_name=request.product_name,
                product_description=request.product_description,
                brand_context=request.brand_context,
                additional_context=request.additional_context
            )
            
            # Create transform request
            transform_request = TransformImageToVideoRequest(
                image_base64=request.product_image_base64,
                prompt=animation_prompt,
                audio_base64=request.audio_base64,
                resolution=request.resolution,
                duration=request.duration,
                enable_prompt_expansion=True,  # Expand prompt for better results
            )
            
            # Generate video using Transform Studio
            result = await self.transform_service.transform_image_to_video(
                request=transform_request,
                user_id=user_id
            )
            
            # Add product-specific metadata
            result["product_name"] = request.product_name
            result["animation_type"] = request.animation_type
            result["source_module"] = "product_marketing"
            
            # Save to Asset Library
            if result.get("file_url") and result.get("filename"):
                db = SessionLocal()
                try:
                    # Build animation prompt for metadata
                    animation_prompt = self._build_animation_prompt(
                        animation_type=request.animation_type,
                        product_name=request.product_name,
                        product_description=request.product_description,
                        brand_context=request.brand_context,
                        additional_context=request.additional_context
                    )
                    
                    asset_id = save_asset_to_library(
                        db=db,
                        user_id=user_id,
                        asset_type="video",
                        source_module="product_marketing",
                        filename=result.get("filename"),
                        file_url=result.get("file_url"),
                        file_path=result.get("file_path"),
                        file_size=result.get("file_size"),
                        mime_type="video/mp4",
                        title=f"{request.product_name} - {request.animation_type.title()} Animation",
                        description=f"Product animation: {request.product_description or request.product_name}",
                        prompt=animation_prompt,
                        tags=["product_marketing", "product_animation", request.animation_type, request.resolution],
                        provider=result.get("provider", "wavespeed"),
                        model=result.get("model_name", "alibaba/wan-2.5/image-to-video"),
                        cost=result.get("cost", 0.0),
                        generation_time=result.get("generation_time"),
                        asset_metadata={
                            "product_name": request.product_name,
                            "product_description": request.product_description,
                            "animation_type": request.animation_type,
                            "resolution": request.resolution,
                            "duration": request.duration,
                            "width": result.get("width"),
                            "height": result.get("height"),
                        },
                    )
                    
                    if asset_id:
                        logger.info(f"[Product Animation] ✅ Saved animation to Asset Library: ID={asset_id}")
                    else:
                        logger.warning(f"[Product Animation] ⚠️ Asset Library save returned None")
                        
                except Exception as db_error:
                    logger.error(f"[Product Animation] Database error saving to Asset Library: {str(db_error)}", exc_info=True)
                    # Video is saved, but database tracking failed - not critical
                finally:
                    if db:
                        try:
                            db.close()
                        except Exception:
                            pass
            
            logger.info(
                f"[Product Animation] ✅ Product animation completed: "
                f"cost=${result.get('cost', 0):.2f}, video_url={result.get('video_url', 'N/A')}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"[Product Animation] ❌ Error animating product: {str(e)}", exc_info=True)
            raise
    
    async def create_product_reveal(
        self,
        product_image_base64: str,
        product_name: str,
        product_description: Optional[str],
        user_id: str,
        resolution: str = "720p",
        duration: int = 5,
        brand_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create product reveal animation."""
        request = ProductAnimationRequest(
            product_image_base64=product_image_base64,
            animation_type="reveal",
            product_name=product_name,
            product_description=product_description,
            resolution=resolution,
            duration=duration,
            brand_context=brand_context
        )
        return await self.animate_product(request, user_id)
    
    async def create_product_rotation(
        self,
        product_image_base64: str,
        product_name: str,
        product_description: Optional[str],
        user_id: str,
        resolution: str = "720p",
        duration: int = 10,  # Longer for full rotation
        brand_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create 360° product rotation animation."""
        request = ProductAnimationRequest(
            product_image_base64=product_image_base64,
            animation_type="rotation",
            product_name=product_name,
            product_description=product_description,
            resolution=resolution,
            duration=duration,
            brand_context=brand_context
        )
        return await self.animate_product(request, user_id)
    
    async def create_product_demo(
        self,
        product_image_base64: str,
        product_name: str,
        product_description: Optional[str],
        user_id: str,
        resolution: str = "720p",
        duration: int = 10,
        audio_base64: Optional[str] = None,
        brand_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create product demo video."""
        request = ProductAnimationRequest(
            product_image_base64=product_image_base64,
            animation_type="demo",
            product_name=product_name,
            product_description=product_description,
            resolution=resolution,
            duration=duration,
            audio_base64=audio_base64,
            brand_context=brand_context
        )
        return await self.animate_product(request, user_id)
