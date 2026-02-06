"""
Avatar Studio Service

Service for creating talking avatars using InfiniteTalk and Hunyuan Avatar.
Supports both models with automatic selection or explicit model choice.
"""

from typing import Dict, Any, Optional
from fastapi import HTTPException
from loguru import logger

from services.image_studio.infinitetalk_adapter import InfiniteTalkService
from services.video_studio.hunyuan_avatar_adapter import HunyuanAvatarService
from utils.logging import get_service_logger

logger = get_service_logger("video_studio.avatar")


class AvatarStudioService:
    """Service for Avatar Studio operations using InfiniteTalk and Hunyuan Avatar."""
    
    def __init__(self):
        """Initialize Avatar Studio service."""
        self.infinitetalk_service = InfiniteTalkService()
        self.hunyuan_avatar_service = HunyuanAvatarService()
        logger.info("[AvatarStudio] Service initialized with InfiniteTalk and Hunyuan Avatar")
    
    async def create_talking_avatar(
        self,
        image_base64: str,
        audio_base64: str,
        resolution: str = "720p",
        prompt: Optional[str] = None,
        mask_image_base64: Optional[str] = None,
        seed: Optional[int] = None,
        user_id: str = "video_studio",
        model: str = "infinitetalk",
        progress_callback: Optional[callable] = None,
    ) -> Dict[str, Any]:
        """
        Create talking avatar video using InfiniteTalk or Hunyuan Avatar.
        
        Args:
            image_base64: Person image in base64 or data URI
            audio_base64: Audio file in base64 or data URI
            resolution: Output resolution (480p or 720p)
            prompt: Optional prompt for expression/style
            mask_image_base64: Optional mask for animatable regions (InfiniteTalk only)
            seed: Optional random seed
            user_id: User ID for tracking
            model: Model to use - "infinitetalk" (default) or "hunyuan-avatar"
            progress_callback: Optional progress callback function
            
        Returns:
            Dictionary with video_bytes, metadata, cost, and file info
        """
        logger.info(
            f"[AvatarStudio] Creating talking avatar: user={user_id}, resolution={resolution}, model={model}"
        )
        
        try:
            if model == "hunyuan-avatar":
                # Use Hunyuan Avatar (doesn't support mask_image)
                result = await self.hunyuan_avatar_service.create_talking_avatar(
                    image_base64=image_base64,
                    audio_base64=audio_base64,
                    resolution=resolution,
                    prompt=prompt,
                    seed=seed,
                    user_id=user_id,
                    progress_callback=progress_callback,
                )
            else:
                # Default to InfiniteTalk
                result = await self.infinitetalk_service.create_talking_avatar(
                    image_base64=image_base64,
                    audio_base64=audio_base64,
                    resolution=resolution,
                    prompt=prompt,
                    mask_image_base64=mask_image_base64,
                    seed=seed,
                    user_id=user_id,
                )
            
            logger.info(
                f"[AvatarStudio] ✅ Talking avatar created: "
                f"model={model}, resolution={resolution}, duration={result.get('duration', 0)}s, "
                f"cost=${result.get('cost', 0):.2f}"
            )
            
            return result
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"[AvatarStudio] ❌ Error creating talking avatar: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create talking avatar: {str(e)}"
            )
    
    def calculate_cost_estimate(
        self,
        resolution: str,
        estimated_duration: float,
        model: str = "infinitetalk",
    ) -> float:
        """
        Calculate estimated cost for talking avatar generation.
        
        Args:
            resolution: Output resolution (480p or 720p)
            estimated_duration: Estimated video duration in seconds
            model: Model to use - "infinitetalk" (default) or "hunyuan-avatar"
            
        Returns:
            Estimated cost in USD
        """
        if model == "hunyuan-avatar":
            return self.hunyuan_avatar_service.calculate_cost(resolution, estimated_duration)
        else:
            return self.infinitetalk_service.calculate_cost(resolution, estimated_duration)
