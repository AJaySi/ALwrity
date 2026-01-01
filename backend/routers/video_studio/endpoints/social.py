"""
Social Optimizer endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
import json

from ...database import get_db
from ...models.content_asset_models import AssetSource, AssetType
from ...services.video_studio import VideoStudioService
from ...services.video_studio.social_optimizer_service import (
    SocialOptimizerService,
    OptimizationOptions,
)
from ...services.asset_service import ContentAssetService
from ...utils.auth import get_current_user, require_authenticated_user
from ...utils.logger_utils import get_service_logger

logger = get_service_logger("video_studio.endpoints.social")

router = APIRouter()


@router.post("/social/optimize")
async def optimize_for_social(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="Source video file"),
    platforms: str = Form(..., description="Comma-separated list of platforms (instagram,tiktok,youtube,linkedin,facebook,twitter)"),
    auto_crop: bool = Form(True, description="Auto-crop to platform aspect ratio"),
    generate_thumbnails: bool = Form(True, description="Generate thumbnails"),
    compress: bool = Form(True, description="Compress for file size limits"),
    trim_mode: str = Form("beginning", description="Trim mode if video exceeds duration (beginning, middle, end)"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Optimize video for multiple social media platforms.
    
    Creates platform-optimized versions with:
    - Aspect ratio conversion
    - Duration trimming
    - File size compression
    - Thumbnail generation
    
    Returns optimized videos for each selected platform.
    """
    try:
        user_id = require_authenticated_user(current_user)

        if not file.content_type.startswith('video/'):
            raise HTTPException(status_code=400, detail="File must be a video")

        # Parse platforms
        platform_list = [p.strip().lower() for p in platforms.split(",") if p.strip()]
        if not platform_list:
            raise HTTPException(status_code=400, detail="At least one platform must be specified")

        # Validate platforms
        valid_platforms = ["instagram", "tiktok", "youtube", "linkedin", "facebook", "twitter"]
        invalid_platforms = [p for p in platform_list if p not in valid_platforms]
        if invalid_platforms:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid platforms: {', '.join(invalid_platforms)}. Valid platforms: {', '.join(valid_platforms)}"
            )

        # Validate trim_mode
        valid_trim_modes = ["beginning", "middle", "end"]
        if trim_mode not in valid_trim_modes:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid trim_mode. Must be one of: {', '.join(valid_trim_modes)}"
            )

        # Initialize services
        video_service = VideoStudioService()
        social_optimizer = SocialOptimizerService()
        asset_service = ContentAssetService(db)

        logger.info(
            f"[SocialOptimizer] Optimization request: "
            f"user={user_id}, platforms={platform_list}"
        )

        # Read video file
        video_data = await file.read()

        # Create optimization options
        options = OptimizationOptions(
            auto_crop=auto_crop,
            generate_thumbnails=generate_thumbnails,
            compress=compress,
            trim_mode=trim_mode,
        )

        # Optimize for platforms
        result = await social_optimizer.optimize_for_platforms(
            video_bytes=video_data,
            platforms=platform_list,
            options=options,
            user_id=user_id,
            video_studio_service=video_service,
        )

        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=f"Optimization failed: {result.get('errors', 'Unknown error')}"
            )

        # Store results in asset library
        for platform_result in result.get("results", []):
            asset_metadata = {
                "platform": platform_result["platform"],
                "name": platform_result["name"],
                "aspect_ratio": platform_result["aspect_ratio"],
                "duration": platform_result["duration"],
                "file_size": platform_result["file_size"],
                "width": platform_result["width"],
                "height": platform_result["height"],
                "optimization_type": "social_optimizer",
            }

            asset_service.create_asset(
                user_id=user_id,
                filename=f"social_{platform_result['platform']}_{platform_result['name'].replace(' ', '_').lower()}.mp4",
                file_url=platform_result["video_url"],
                asset_type=AssetType.VIDEO,
                source_module=AssetSource.VIDEO_STUDIO,
                asset_metadata=asset_metadata,
                cost=0.0,  # Free (FFmpeg processing)
                tags=["video_studio", "social_optimizer", platform_result["platform"]],
            )

        logger.info(
            f"[SocialOptimizer] Optimization successful: "
            f"user={user_id}, platforms={len(result.get('results', []))}"
        )

        return {
            "success": True,
            "results": result.get("results", []),
            "errors": result.get("errors", []),
            "cost": result.get("cost", 0.0),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[SocialOptimizer] Optimization error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")


@router.get("/social/platforms")
async def get_platforms(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get list of available platforms and their specifications.
    """
    try:
        require_authenticated_user(current_user)

        from ...services.video_studio.platform_specs import (
            PLATFORM_SPECS,
            Platform,
        )

        platforms_data = {}
        for platform in Platform:
            specs = [spec for spec in PLATFORM_SPECS if spec.platform == platform]
            platforms_data[platform.value] = [
                {
                    "name": spec.name,
                    "aspect_ratio": spec.aspect_ratio,
                    "width": spec.width,
                    "height": spec.height,
                    "max_duration": spec.max_duration,
                    "max_file_size_mb": spec.max_file_size_mb,
                    "formats": spec.formats,
                    "description": spec.description,
                }
                for spec in specs
            ]

        return {
            "success": True,
            "platforms": platforms_data,
        }

    except Exception as e:
        logger.error(f"[SocialOptimizer] Failed to get platforms: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get platforms: {str(e)}")
