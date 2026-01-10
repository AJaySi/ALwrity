"""
Product Video Service
Handles product demo video generation using WAN 2.5 Text-to-Video via main_video_generation.
"""

from typing import Dict, Any, Optional
from loguru import logger
from dataclasses import dataclass

from services.llm_providers.main_video_generation import ai_video_generate
from utils.logger_utils import get_service_logger
from utils.asset_tracker import save_asset_to_library
from services.database import SessionLocal

logger = get_service_logger("product_marketing.video")


@dataclass
class ProductVideoRequest:
    """Request for product demo video generation."""
    product_name: str
    product_description: str
    video_type: str  # "demo", "storytelling", "feature_highlight", "launch"
    resolution: str = "720p"  # 480p, 720p, 1080p
    duration: int = 10  # 5 or 10 seconds
    audio_base64: Optional[str] = None
    brand_context: Optional[Dict[str, Any]] = None
    additional_context: Optional[str] = None
    negative_prompt: Optional[str] = None
    seed: Optional[int] = None


class ProductVideoService:
    """Service for product demo video generation using WAN 2.5 Text-to-Video."""
    
    def __init__(self):
        """Initialize Product Video Service."""
        logger.info("[Product Video Service] Initialized")
    
    def _build_video_prompt(
        self,
        video_type: str,
        product_name: str,
        product_description: str,
        brand_context: Optional[Dict[str, Any]],
        additional_context: Optional[str]
    ) -> str:
        """
        Build video prompt based on video type and product context.
        
        Args:
            video_type: Type of video (demo, storytelling, feature_highlight, launch)
            product_name: Product name
            product_description: Product description
            brand_context: Brand DNA context
            additional_context: Additional context
            
        Returns:
            Video generation prompt
        """
        base_description = f"{product_name}"
        if product_description:
            base_description += f": {product_description}"
        
        # Video type-specific prompts
        video_prompts = {
            "demo": (
                f"{base_description} being demonstrated in use, showcasing key features and benefits, "
                f"professional product demonstration, dynamic camera movement, engaging presentation, "
                f"clear product visibility, modern and clean aesthetic"
            ),
            "storytelling": (
                f"Story of {base_description}, narrative-driven product showcase, emotional connection, "
                f"cinematic storytelling, compelling visual narrative, professional cinematography, "
                f"engaging product story"
            ),
            "feature_highlight": (
                f"{base_description} highlighting key features, close-up shots of important details, "
                f"feature-focused presentation, professional product photography, clear feature visibility, "
                f"modern and sleek aesthetic"
            ),
            "launch": (
                f"{base_description} product launch reveal, exciting unveiling, dynamic presentation, "
                f"professional product showcase, launch event aesthetic, engaging and energetic, "
                f"modern and premium feel"
            ),
        }
        
        prompt = video_prompts.get(video_type, base_description)
        
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
            
            # Add brand values if available
            if visual_identity.get("brand_values"):
                values = ", ".join(visual_identity["brand_values"][:2])  # First 2 values
                prompt += f", embodying {values}"
        
        # Add additional context
        if additional_context:
            prompt += f", {additional_context}"
        
        return prompt
    
    async def generate_product_video(
        self,
        request: ProductVideoRequest,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Generate product demo video using WAN 2.5 Text-to-Video.
        
        This method uses the unified ai_video_generate() entry point which handles:
        - Pre-flight validation
        - Usage tracking
        - Cost tracking
        - Error handling
        
        Args:
            request: Product video request
            user_id: User ID for tracking
            
        Returns:
            Video generation result with video URL and metadata
        """
        try:
            logger.info(
                f"[Product Video] Generating {request.video_type} video for product '{request.product_name}' "
                f"for user {user_id}"
            )
            
            # Build video prompt
            video_prompt = self._build_video_prompt(
                video_type=request.video_type,
                product_name=request.product_name,
                product_description=request.product_description,
                brand_context=request.brand_context,
                additional_context=request.additional_context
            )
            
            # Build negative prompt (default to avoid common issues)
            negative_prompt = request.negative_prompt or (
                "blurry, low quality, distorted, deformed, ugly, bad anatomy, "
                "watermark, text overlay, logo, signature"
            )
            
            # Generate video using unified entry point
            # This handles pre-flight validation, usage tracking, and cost tracking automatically
            result = await ai_video_generate(
                prompt=video_prompt,
                operation_type="text-to-video",
                provider="wavespeed",
                user_id=user_id,
                model="alibaba/wan-2.5/text-to-video",  # WAN 2.5 Text-to-Video
                duration=request.duration,
                resolution=request.resolution,
                audio_base64=request.audio_base64,
                negative_prompt=negative_prompt,
                seed=request.seed,
                enable_prompt_expansion=True,  # Enable prompt optimization
            )
            
            # Extract video bytes and save to user directory
            video_bytes = result.get("video_bytes")
            if not video_bytes:
                raise ValueError("Video generation returned no video bytes")
            
            # Save video file (similar to Transform Studio)
            from pathlib import Path
            import uuid
            import os
            
            base_dir = Path(__file__).parent.parent.parent.parent
            output_dir = base_dir / "product_videos"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Create user-specific directory
            user_dir = output_dir / user_id
            user_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename (sanitize to avoid issues)
            safe_product_name = "".join(c for c in request.product_name if c.isalnum() or c in (' ', '-', '_')).strip()[:30]
            filename = f"product_{safe_product_name}_{request.video_type}_{uuid.uuid4().hex[:8]}.mp4"
            filename = filename.replace(" ", "_").replace("/", "_").replace("\\", "_")
            
            # Save file
            file_path = user_dir / filename
            with open(file_path, 'wb') as f:
                f.write(video_bytes)
            
            # Check file size (500MB max)
            file_size = os.path.getsize(file_path)
            if file_size > 500 * 1024 * 1024:
                os.remove(file_path)
                raise RuntimeError(f"Video file too large: {file_size / (1024*1024):.2f}MB (max 500MB)")
            
            file_url = f"/api/product-marketing/videos/{user_id}/{filename}"
            
            # Add product-specific metadata
            result["product_name"] = request.product_name
            result["video_type"] = request.video_type
            result["source_module"] = "product_marketing"
            result["filename"] = filename
            result["file_path"] = str(file_path)
            result["file_url"] = file_url
            result["file_size"] = len(video_bytes)
            
            # Save to Asset Library
            db = SessionLocal()
            try:
                # Build video prompt for metadata
                video_prompt = self._build_video_prompt(
                    video_type=request.video_type,
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
                    filename=filename,
                    file_url=file_url,
                    file_path=str(file_path),
                    file_size=len(video_bytes),
                    mime_type="video/mp4",
                    title=f"{request.product_name} - {request.video_type.replace('_', ' ').title()} Video",
                    description=f"Product video: {request.product_description or request.product_name}",
                    prompt=video_prompt,
                    tags=["product_marketing", "product_video", request.video_type, request.resolution],
                    provider=result.get("provider", "wavespeed"),
                    model=result.get("model_name", "alibaba/wan-2.5/text-to-video"),
                    cost=result.get("cost", 0.0),
                    generation_time=result.get("generation_time"),
                    asset_metadata={
                        "product_name": request.product_name,
                        "product_description": request.product_description,
                        "video_type": request.video_type,
                        "resolution": request.resolution,
                        "duration": request.duration,
                        "width": result.get("width"),
                        "height": result.get("height"),
                    },
                )
                
                if asset_id:
                    logger.info(f"[Product Video] ✅ Saved video to Asset Library: ID={asset_id}")
                else:
                    logger.warning(f"[Product Video] ⚠️ Asset Library save returned None")
                    
            except Exception as db_error:
                logger.error(f"[Product Video] Database error saving to Asset Library: {str(db_error)}", exc_info=True)
                # Video is saved, but database tracking failed - not critical
            finally:
                if db:
                    try:
                        db.close()
                    except Exception:
                        pass
            
            logger.info(
                f"[Product Video] ✅ Product video generated successfully: "
                f"cost=${result.get('cost', 0):.2f}, video_url={file_url}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"[Product Video] ❌ Error generating product video: {str(e)}", exc_info=True)
            raise
    
    async def create_product_demo(
        self,
        product_name: str,
        product_description: str,
        user_id: str,
        resolution: str = "720p",
        duration: int = 10,
        audio_base64: Optional[str] = None,
        brand_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create product demo video (product in use, demonstrating features)."""
        request = ProductVideoRequest(
            product_name=product_name,
            product_description=product_description,
            video_type="demo",
            resolution=resolution,
            duration=duration,
            audio_base64=audio_base64,
            brand_context=brand_context
        )
        return await self.generate_product_video(request, user_id)
    
    async def create_product_storytelling(
        self,
        product_name: str,
        product_description: str,
        user_id: str,
        resolution: str = "720p",
        duration: int = 10,
        audio_base64: Optional[str] = None,
        brand_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create product storytelling video (narrative-driven product showcase)."""
        request = ProductVideoRequest(
            product_name=product_name,
            product_description=product_description,
            video_type="storytelling",
            resolution=resolution,
            duration=duration,
            audio_base64=audio_base64,
            brand_context=brand_context
        )
        return await self.generate_product_video(request, user_id)
    
    async def create_product_feature_highlight(
        self,
        product_name: str,
        product_description: str,
        user_id: str,
        resolution: str = "720p",
        duration: int = 10,
        audio_base64: Optional[str] = None,
        brand_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create product feature highlight video (close-up shots of key features)."""
        request = ProductVideoRequest(
            product_name=product_name,
            product_description=product_description,
            video_type="feature_highlight",
            resolution=resolution,
            duration=duration,
            audio_base64=audio_base64,
            brand_context=brand_context
        )
        return await self.generate_product_video(request, user_id)
    
    async def create_product_launch(
        self,
        product_name: str,
        product_description: str,
        user_id: str,
        resolution: str = "1080p",  # Higher quality for launch
        duration: int = 10,
        audio_base64: Optional[str] = None,
        brand_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create product launch video (exciting unveiling, launch event aesthetic)."""
        request = ProductVideoRequest(
            product_name=product_name,
            product_description=product_description,
            video_type="launch",
            resolution=resolution,
            duration=duration,
            audio_base64=audio_base64,
            brand_context=brand_context
        )
        return await self.generate_product_video(request, user_id)
