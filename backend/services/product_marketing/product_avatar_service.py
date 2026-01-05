"""
Product Avatar Service
Handles product explainer video generation using InfiniteTalk (talking avatars).
"""

from typing import Dict, Any, Optional
from loguru import logger
from dataclasses import dataclass
from pathlib import Path
import uuid
import os
import base64

from services.image_studio.infinitetalk_adapter import InfiniteTalkService
from services.story_writer.audio_generation_service import StoryAudioGenerationService
from utils.logger_utils import get_service_logger

logger = get_service_logger("product_marketing.avatar")


@dataclass
class ProductAvatarRequest:
    """Request for product explainer video with talking avatar."""
    avatar_image_base64: str  # Product image, brand spokesperson, or brand mascot
    script_text: Optional[str] = None  # Text script to convert to audio
    audio_base64: Optional[str] = None  # Pre-generated audio (alternative to script_text)
    product_name: str = "Product"
    product_description: Optional[str] = None
    explainer_type: str = "product_overview"  # product_overview, feature_explainer, tutorial, brand_message
    resolution: str = "720p"  # 480p or 720p
    prompt: Optional[str] = None  # Optional prompt for expression/style
    mask_image_base64: Optional[str] = None  # Optional mask for animatable regions
    seed: Optional[int] = None
    brand_context: Optional[Dict[str, Any]] = None
    additional_context: Optional[str] = None


class ProductAvatarService:
    """Service for product explainer video generation using InfiniteTalk."""
    
    def __init__(self):
        """Initialize Product Avatar Service."""
        self.infinitetalk_service = InfiniteTalkService()
        self.audio_service = StoryAudioGenerationService()
        logger.info("[Product Avatar Service] Initialized")
    
    def _build_avatar_prompt(
        self,
        explainer_type: str,
        product_name: str,
        product_description: Optional[str],
        brand_context: Optional[Dict[str, Any]],
        additional_context: Optional[str]
    ) -> str:
        """
        Build avatar prompt based on explainer type and product context.
        
        Args:
            explainer_type: Type of explainer (product_overview, feature_explainer, tutorial, brand_message)
            product_name: Product name
            product_description: Product description
            brand_context: Brand DNA context
            additional_context: Additional context
            
        Returns:
            Avatar animation prompt
        """
        base_description = f"{product_name}"
        if product_description:
            base_description += f": {product_description}"
        
        # Explainer type-specific prompts
        explainer_prompts = {
            "product_overview": (
                f"Professional product presentation of {base_description}, "
                f"engaging and informative, clear communication, confident expression, "
                f"professional setting, modern and clean aesthetic"
            ),
            "feature_explainer": (
                f"Demonstrating features of {base_description}, "
                f"detailed explanation, pointing gestures, clear visual communication, "
                f"educational and informative, professional presentation"
            ),
            "tutorial": (
                f"Tutorial presentation for {base_description}, "
                f"step-by-step explanation, instructional and clear, "
                f"friendly and approachable, educational setting"
            ),
            "brand_message": (
                f"Brand message delivery for {base_description}, "
                f"authentic and compelling, brand storytelling, "
                f"emotional connection, professional brand representation"
            ),
        }
        
        prompt = explainer_prompts.get(explainer_type, base_description)
        
        # Add brand context if available
        if brand_context:
            visual_identity = brand_context.get("visual_identity", {})
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
    
    def _generate_audio_from_script(
        self,
        script_text: str,
        user_id: str,
        output_dir: Path
    ) -> bytes:
        """
        Generate audio from script text using TTS.
        
        Args:
            script_text: Text to convert to speech
            user_id: User ID for tracking
            output_dir: Directory to save temporary audio file
            
        Returns:
            Audio bytes
        """
        try:
            # Create temporary audio file
            audio_filename = f"avatar_audio_{uuid.uuid4().hex[:8]}.mp3"
            audio_path = output_dir / audio_filename
            
            # Generate audio using gTTS (free, always available)
            # Note: For premium voices, we could integrate Minimax voice clone here
            success = self.audio_service._generate_audio_gtts(
                text=script_text,
                output_path=audio_path,
                lang="en",
                slow=False
            )
            
            if not success:
                raise RuntimeError("Failed to generate audio from script")
            
            # Read audio bytes
            with open(audio_path, 'rb') as f:
                audio_bytes = f.read()
            
            # Clean up temporary file
            try:
                os.remove(audio_path)
            except Exception:
                pass
            
            logger.info(f"[Product Avatar] Generated audio from script: {len(audio_bytes)} bytes")
            return audio_bytes
            
        except Exception as e:
            logger.error(f"[Product Avatar] Error generating audio: {str(e)}", exc_info=True)
            raise
    
    async def generate_product_explainer(
        self,
        request: ProductAvatarRequest,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Generate product explainer video using InfiniteTalk.
        
        Args:
            request: Product avatar request
            user_id: User ID for tracking
            
        Returns:
            Explainer video result with video URL and metadata
        """
        try:
            logger.info(
                f"[Product Avatar] Generating {request.explainer_type} explainer for product '{request.product_name}' "
                f"for user {user_id}"
            )
            
            # Prepare audio
            audio_base64 = request.audio_base64
            if not audio_base64 and request.script_text:
                # Generate audio from script
                base_dir = Path(__file__).parent.parent.parent.parent
                temp_dir = base_dir / "temp_audio"
                temp_dir.mkdir(parents=True, exist_ok=True)
                
                audio_bytes = self._generate_audio_from_script(
                    script_text=request.script_text,
                    user_id=user_id,
                    output_dir=temp_dir
                )
                
                # Convert to base64
                audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
                audio_base64 = f"data:audio/mpeg;base64,{audio_base64}"
            
            if not audio_base64:
                raise ValueError("Either audio_base64 or script_text must be provided")
            
            # Build avatar prompt
            avatar_prompt = request.prompt
            if not avatar_prompt:
                avatar_prompt = self._build_avatar_prompt(
                    explainer_type=request.explainer_type,
                    product_name=request.product_name,
                    product_description=request.product_description,
                    brand_context=request.brand_context,
                    additional_context=request.additional_context
                )
            
            # Generate video using InfiniteTalk
            result = await self.infinitetalk_service.create_talking_avatar(
                image_base64=request.avatar_image_base64,
                audio_base64=audio_base64,
                resolution=request.resolution,
                prompt=avatar_prompt,
                mask_image_base64=request.mask_image_base64,
                seed=request.seed,
                user_id=user_id,
            )
            
            # Extract video bytes and save to user directory
            video_bytes = result.get("video_bytes")
            if not video_bytes:
                raise ValueError("Avatar generation returned no video bytes")
            
            # Save video file
            base_dir = Path(__file__).parent.parent.parent.parent
            output_dir = base_dir / "product_avatars"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Create user-specific directory
            user_dir = output_dir / user_id
            user_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename
            safe_product_name = "".join(c for c in request.product_name if c.isalnum() or c in (' ', '-', '_')).strip()[:30]
            filename = f"explainer_{safe_product_name}_{request.explainer_type}_{uuid.uuid4().hex[:8]}.mp4"
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
            
            file_url = f"/api/product-marketing/avatars/{user_id}/{filename}"
            
            # Add product-specific metadata
            result["product_name"] = request.product_name
            result["explainer_type"] = request.explainer_type
            result["source_module"] = "product_marketing"
            result["filename"] = filename
            result["file_path"] = str(file_path)
            result["file_url"] = file_url
            result["file_size"] = file_size
            result["duration"] = result.get("duration", 0.0)
            
            logger.info(
                f"[Product Avatar] ✅ Product explainer video generated successfully: "
                f"cost=${result.get('cost', 0):.2f}, duration={result.get('duration', 0):.1f}s, "
                f"video_url={file_url}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"[Product Avatar] ❌ Error generating product explainer: {str(e)}", exc_info=True)
            raise
    
    async def create_product_overview(
        self,
        avatar_image_base64: str,
        script_text: str,
        product_name: str,
        product_description: Optional[str],
        user_id: str,
        resolution: str = "720p",
        audio_base64: Optional[str] = None,
        brand_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create product overview explainer video."""
        request = ProductAvatarRequest(
            avatar_image_base64=avatar_image_base64,
            script_text=script_text,
            audio_base64=audio_base64,
            product_name=product_name,
            product_description=product_description,
            explainer_type="product_overview",
            resolution=resolution,
            brand_context=brand_context
        )
        return await self.generate_product_explainer(request, user_id)
    
    async def create_feature_explainer(
        self,
        avatar_image_base64: str,
        script_text: str,
        product_name: str,
        product_description: Optional[str],
        user_id: str,
        resolution: str = "720p",
        audio_base64: Optional[str] = None,
        brand_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create product feature explainer video."""
        request = ProductAvatarRequest(
            avatar_image_base64=avatar_image_base64,
            script_text=script_text,
            audio_base64=audio_base64,
            product_name=product_name,
            product_description=product_description,
            explainer_type="feature_explainer",
            resolution=resolution,
            brand_context=brand_context
        )
        return await self.generate_product_explainer(request, user_id)
    
    async def create_tutorial(
        self,
        avatar_image_base64: str,
        script_text: str,
        product_name: str,
        product_description: Optional[str],
        user_id: str,
        resolution: str = "720p",
        audio_base64: Optional[str] = None,
        brand_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create product tutorial video."""
        request = ProductAvatarRequest(
            avatar_image_base64=avatar_image_base64,
            script_text=script_text,
            audio_base64=audio_base64,
            product_name=product_name,
            product_description=product_description,
            explainer_type="tutorial",
            resolution=resolution,
            brand_context=brand_context
        )
        return await self.generate_product_explainer(request, user_id)
    
    async def create_brand_message(
        self,
        avatar_image_base64: str,
        script_text: str,
        product_name: str,
        product_description: Optional[str],
        user_id: str,
        resolution: str = "720p",
        audio_base64: Optional[str] = None,
        brand_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create brand message video."""
        request = ProductAvatarRequest(
            avatar_image_base64=avatar_image_base64,
            script_text=script_text,
            audio_base64=audio_base64,
            product_name=product_name,
            product_description=product_description,
            explainer_type="brand_message",
            resolution=resolution,
            brand_context=brand_context
        )
        return await self.generate_product_explainer(request, user_id)
