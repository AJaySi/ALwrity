"""Transform Studio service for image-to-video and talking avatar generation."""

import os
import uuid
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass
from fastapi import HTTPException
from loguru import logger

from .wan25_service import WAN25Service
from .infinitetalk_adapter import InfiniteTalkService
from services.llm_providers.main_video_generation import ai_video_generate
from utils.logger_utils import get_service_logger
from utils.file_storage import save_file_safely, sanitize_filename

logger = get_service_logger("image_studio.transform")


@dataclass
class TransformImageToVideoRequest:
    """Request for WAN 2.5 image-to-video."""
    image_base64: str
    prompt: str
    audio_base64: Optional[str] = None
    resolution: str = "720p"  # 480p, 720p, 1080p
    duration: int = 5  # 5 or 10 seconds
    negative_prompt: Optional[str] = None
    seed: Optional[int] = None
    enable_prompt_expansion: bool = True


@dataclass
class TalkingAvatarRequest:
    """Request for InfiniteTalk talking avatar."""
    image_base64: str
    audio_base64: str
    resolution: str = "720p"  # 480p or 720p
    prompt: Optional[str] = None
    mask_image_base64: Optional[str] = None
    seed: Optional[int] = None


class TransformStudioService:
    """Service for Transform Studio operations."""
    
    def __init__(self):
        """Initialize Transform Studio service."""
        self.wan25_service = WAN25Service()
        self.infinitetalk_service = InfiniteTalkService()
        
        # Video output directory
        # __file__ is: backend/services/image_studio/transform_service.py
        # We need: backend/transform_videos
        base_dir = Path(__file__).parent.parent.parent.parent
        self.output_dir = base_dir / "transform_videos"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Verify directory was created
        if not self.output_dir.exists():
            raise RuntimeError(f"Failed to create transform_videos directory: {self.output_dir}")
        
        logger.info(f"[Transform Studio] Initialized with output directory: {self.output_dir}")
    
    def _save_video_file(
        self,
        video_bytes: bytes,
        operation_type: str,
        user_id: str,
    ) -> Dict[str, Any]:
        """Save video file to disk.
        
        Args:
            video_bytes: Video content as bytes
            operation_type: Type of operation (e.g., "image-to-video", "talking-avatar")
            user_id: User ID for directory organization
            
        Returns:
            Dictionary with filename, file_path, and file_url
        """
        # Create user-specific directory
        user_dir = self.output_dir / user_id
        user_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        filename = f"{operation_type}_{uuid.uuid4().hex[:8]}.mp4"
        filename = sanitize_filename(filename)
        
        # Save file
        file_path, error = save_file_safely(
            content=video_bytes,
            directory=user_dir,
            filename=filename,
            max_file_size=500 * 1024 * 1024  # 500MB max for videos
        )
        
        if error:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save video file: {error}"
            )
        
        file_url = f"/api/image-studio/videos/{user_id}/{filename}"
        
        return {
            "filename": filename,
            "file_path": str(file_path),
            "file_url": file_url,
            "file_size": len(video_bytes),
        }
    
    async def transform_image_to_video(
        self,
        request: TransformImageToVideoRequest,
        user_id: str,
    ) -> Dict[str, Any]:
        """Transform image to video using unified video generation entry point.
        
        Args:
            request: Transform request
            user_id: User ID for tracking and file organization
            
        Returns:
            Dictionary with video URL, metadata, and cost
        """
        logger.info(
            f"[Transform Studio] Image-to-video request from user {user_id}: "
            f"resolution={request.resolution}, duration={request.duration}s"
        )
        
        # Use unified video generation entry point
        # This handles pre-flight validation, generation, and usage tracking
        # Returns dict with video_bytes and full metadata
        result = ai_video_generate(
            image_base64=request.image_base64,
            prompt=request.prompt,
            operation_type="image-to-video",
            provider="wavespeed",
            user_id=user_id,
            duration=request.duration,
            resolution=request.resolution,
            negative_prompt=request.negative_prompt,
            seed=request.seed,
            audio_base64=request.audio_base64,
            enable_prompt_expansion=request.enable_prompt_expansion,
            model="alibaba/wan-2.5/image-to-video",
        )
        
        # Extract video bytes and metadata from result
        video_bytes = result["video_bytes"]
        
        # Save video to disk
        save_result = self._save_video_file(
            video_bytes=video_bytes,
            operation_type="image-to-video",
            user_id=user_id,
        )
        
        # Save to asset library
        try:
            from services.database import get_db
            from utils.asset_tracker import save_asset_to_library
            
            db = next(get_db())
            try:
                save_asset_to_library(
                    db=db,
                    user_id=user_id,
                    asset_type="video",
                    source_module="image_studio",
                    filename=save_result["filename"],
                    file_url=save_result["file_url"],
                    file_path=save_result["file_path"],
                    file_size=save_result["file_size"],
                    mime_type="video/mp4",
                    title=f"Transform: Image-to-Video ({request.resolution})",
                    description=f"Generated video using WAN 2.5: {request.prompt[:100]}",
                    prompt=result.get("prompt", request.prompt),
                    tags=["image_studio", "transform", "video", "image-to-video", request.resolution],
                    provider=result.get("provider", "wavespeed"),
                    model=result.get("model_name", "alibaba/wan-2.5/image-to-video"),
                    cost=result.get("cost", 0.0),
                    asset_metadata={
                        "resolution": request.resolution,
                        "duration": result.get("duration", float(request.duration)),
                        "operation": "image-to-video",
                        "width": result.get("width", 1280),
                        "height": result.get("height", 720),
                    }
                )
                logger.info(f"[Transform Studio] Video saved to asset library")
            finally:
                db.close()
        except Exception as e:
            logger.warning(f"[Transform Studio] Failed to save to asset library: {e}")
        
        return {
            "success": True,
            "video_url": save_result["file_url"],
            "video_base64": None,  # Don't include base64 for large videos
            "duration": result.get("duration", float(request.duration)),
            "resolution": result.get("resolution", request.resolution),
            "width": result.get("width", 1280),
            "height": result.get("height", 720),
            "file_size": save_result["file_size"],
            "cost": result.get("cost", 0.0),
            "provider": result.get("provider", "wavespeed"),
            "model": result.get("model_name", "alibaba/wan-2.5/image-to-video"),
            "metadata": result.get("metadata", {}),
        }
    
    async def create_talking_avatar(
        self,
        request: TalkingAvatarRequest,
        user_id: str,
    ) -> Dict[str, Any]:
        """Create talking avatar using InfiniteTalk.
        
        Args:
            request: Talking avatar request
            user_id: User ID for tracking and file organization
            
        Returns:
            Dictionary with video URL, metadata, and cost
        """
        logger.info(
            f"[Transform Studio] Talking avatar request from user {user_id}: "
            f"resolution={request.resolution}"
        )
        
        # Generate video using InfiniteTalk
        result = await self.infinitetalk_service.create_talking_avatar(
            image_base64=request.image_base64,
            audio_base64=request.audio_base64,
            resolution=request.resolution,
            prompt=request.prompt,
            mask_image_base64=request.mask_image_base64,
            seed=request.seed,
            user_id=user_id,
        )
        
        # Save video to disk
        save_result = self._save_video_file(
            video_bytes=result["video_bytes"],
            operation_type="talking-avatar",
            user_id=user_id,
        )
        
        # Track usage
        try:
            usage_info = track_video_usage(
                user_id=user_id,
                provider=result["provider"],
                model_name=result["model_name"],
                prompt=result.get("prompt", ""),
                video_bytes=result["video_bytes"],
                cost_override=result["cost"],
            )
            logger.info(
                f"[Transform Studio] Usage tracked: {usage_info.get('current_calls', 0)} / "
                f"{usage_info.get('video_limit_display', '∞')} videos, "
                f"cost=${result['cost']:.2f}"
            )
        except Exception as e:
            logger.warning(f"[Transform Studio] Failed to track usage: {e}")
        
        # Save to asset library
        try:
            from services.database import get_db
            from utils.asset_tracker import save_asset_to_library
            
            db = next(get_db())
            try:
                save_asset_to_library(
                    db=db,
                    user_id=user_id,
                    asset_type="video",
                    source_module="image_studio",
                    filename=save_result["filename"],
                    file_url=save_result["file_url"],
                    file_path=save_result["file_path"],
                    file_size=save_result["file_size"],
                    mime_type="video/mp4",
                    title=f"Transform: Talking Avatar ({request.resolution})",
                    description="Generated talking avatar video using InfiniteTalk",
                    prompt=result.get("prompt", ""),
                    tags=["image_studio", "transform", "video", "talking-avatar", request.resolution],
                    provider=result["provider"],
                    model=result["model_name"],
                    cost=result["cost"],
                    asset_metadata={
                        "resolution": request.resolution,
                        "duration": result.get("duration", 5.0),
                        "operation": "talking-avatar",
                        "width": result.get("width", 1280),
                        "height": result.get("height", 720),
                    }
                )
                logger.info(f"[Transform Studio] Video saved to asset library")
            finally:
                db.close()
        except Exception as e:
            logger.warning(f"[Transform Studio] Failed to save to asset library: {e}")
        
        return {
            "success": True,
            "video_url": save_result["file_url"],
            "video_base64": None,  # Don't include base64 for large videos
            "duration": result.get("duration", 5.0),
            "resolution": result.get("resolution", request.resolution),
            "width": result.get("width", 1280),
            "height": result.get("height", 720),
            "file_size": save_result["file_size"],
            "cost": result["cost"],
            "provider": result["provider"],
            "model": result["model_name"],
            "metadata": result.get("metadata", {}),
        }
    
    def estimate_cost(
        self,
        operation: str,
        resolution: str,
        duration: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Estimate cost for transform operation.
        
        Args:
            operation: Operation type ("image-to-video" or "talking-avatar")
            resolution: Output resolution
            duration: Video duration in seconds (for image-to-video)
            
        Returns:
            Cost estimation details
        """
        if operation == "image-to-video":
            if duration is None:
                duration = 5
            cost = self.wan25_service.calculate_cost(resolution, duration)
            return {
                "estimated_cost": cost,
                "breakdown": {
                    "base_cost": 0.0,
                    "per_second": self.wan25_service.calculate_cost(resolution, 1),
                    "duration": duration,
                    "total": cost,
                },
                "currency": "USD",
                "provider": "wavespeed",
                "model": "alibaba/wan-2.5/image-to-video",
            }
        elif operation == "talking-avatar":
            # InfiniteTalk minimum is 5 seconds
            estimated_duration = duration or 5.0
            cost = self.infinitetalk_service.calculate_cost(resolution, estimated_duration)
            return {
                "estimated_cost": cost,
                "breakdown": {
                    "base_cost": 0.0,
                    "per_second": self.infinitetalk_service.calculate_cost(resolution, 1.0),
                    "duration": estimated_duration,
                    "total": cost,
                },
                "currency": "USD",
                "provider": "wavespeed",
                "model": "wavespeed-ai/infinitetalk",
            }
        else:
            raise ValueError(f"Unknown operation: {operation}")

