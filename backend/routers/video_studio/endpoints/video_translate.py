"""
Video Translate endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import uuid

from ...database import get_db
from ...models.content_asset_models import AssetSource, AssetType
from ...services.video_studio import VideoStudioService
from ...services.video_studio.video_translate_service import VideoTranslateService
from ...services.asset_service import ContentAssetService
from ...utils.auth import get_current_user, require_authenticated_user
from utils.logger_utils import get_service_logger

logger = get_service_logger("video_studio.endpoints.video_translate")

router = APIRouter()


@router.post("/video-translate")
async def translate_video(
    background_tasks: BackgroundTasks,
    video_file: UploadFile = File(..., description="Source video to translate"),
    output_language: str = Form("English", description="Target language for translation"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Translate video to target language using HeyGen Video Translate.
    
    Supports 70+ languages and 175+ dialects. Translates both audio and video
    with lip-sync preservation.
    
    Requirements:
    - Video: Source video file (MP4, WebM, etc.)
    - Output Language: Target language (default: "English")
    - Pricing: $0.0375/second
    
    Supported languages include:
    - English, Spanish, French, Hindi, Italian, German, Polish, Portuguese
    - Chinese, Japanese, Korean, Arabic, Russian, and many more
    - Regional variants (e.g., "English (United States)", "Spanish (Mexico)")
    """
    try:
        user_id = require_authenticated_user(current_user)

        # Validate file type
        if not video_file.content_type.startswith('video/'):
            raise HTTPException(status_code=400, detail="File must be a video")

        # Initialize services
        video_translate_service = VideoTranslateService()
        asset_service = ContentAssetService(db)

        logger.info(
            f"[VideoTranslate] Video translate request: user={user_id}, "
            f"output_language={output_language}"
        )

        # Read file
        video_data = await video_file.read()

        # Validate file size (reasonable limit)
        if len(video_data) > 500 * 1024 * 1024:  # 500MB
            raise HTTPException(status_code=400, detail="Video file must be less than 500MB")

        # Perform video translation
        result = await video_translate_service.translate_video(
            video_data=video_data,
            output_language=output_language,
            user_id=user_id,
        )

        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=f"Video translation failed: {result.get('error', 'Unknown error')}"
            )

        # Store in asset library
        video_url = result.get("video_url")
        if video_url:
            asset_metadata = {
                "video_file": video_file.filename,
                "output_language": output_language,
                "operation_type": "video_translate",
                "model": "heygen/video-translate",
            }

            asset_service.create_asset(
                user_id=user_id,
                filename=f"video_translate_{uuid.uuid4().hex[:8]}.mp4",
                file_url=video_url,
                asset_type=AssetType.VIDEO,
                source_module=AssetSource.VIDEO_STUDIO,
                asset_metadata=asset_metadata,
                cost=result.get("cost", 0),
                tags=["video_studio", "video_translate", "ai-generated"],
            )

        logger.info(f"[VideoTranslate] Video translate successful: user={user_id}, url={video_url}")

        return {
            "success": True,
            "video_url": video_url,
            "cost": result.get("cost", 0),
            "output_language": output_language,
            "metadata": result.get("metadata", {}),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[VideoTranslate] Video translate error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Video translation failed: {str(e)}")


@router.post("/video-translate/estimate-cost")
async def estimate_video_translate_cost(
    estimated_duration: float = Form(10.0, description="Estimated video duration in seconds", ge=1.0),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Estimate cost for video translation operation.
    
    Returns estimated cost based on duration.
    """
    try:
        require_authenticated_user(current_user)
        
        video_translate_service = VideoTranslateService()
        estimated_cost = video_translate_service.calculate_cost(estimated_duration)
        
        return {
            "estimated_cost": estimated_cost,
            "estimated_duration": estimated_duration,
            "cost_per_second": 0.0375,
            "pricing_model": "per_second",
            "min_duration": 1.0,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[VideoTranslate] Failed to estimate cost: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to estimate cost: {str(e)}")


@router.get("/video-translate/languages")
async def get_supported_languages(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get list of supported languages for video translation.
    
    Returns a categorized list of 70+ languages and 175+ dialects.
    """
    try:
        require_authenticated_user(current_user)
        
        # Common languages (simplified list - full list has 175+ dialects)
        languages = [
            "English",
            "English (United States)",
            "English (UK)",
            "English (Australia)",
            "English (Canada)",
            "Spanish",
            "Spanish (Spain)",
            "Spanish (Mexico)",
            "Spanish (Argentina)",
            "French",
            "French (France)",
            "French (Canada)",
            "German",
            "German (Germany)",
            "Italian",
            "Italian (Italy)",
            "Portuguese",
            "Portuguese (Brazil)",
            "Portuguese (Portugal)",
            "Chinese",
            "Chinese (Mandarin, Simplified)",
            "Chinese (Cantonese, Traditional)",
            "Japanese",
            "Japanese (Japan)",
            "Korean",
            "Korean (Korea)",
            "Hindi",
            "Hindi (India)",
            "Arabic",
            "Arabic (Saudi Arabia)",
            "Arabic (Egypt)",
            "Russian",
            "Russian (Russia)",
            "Polish",
            "Polish (Poland)",
            "Dutch",
            "Dutch (Netherlands)",
            "Turkish",
            "Turkish (Türkiye)",
            "Thai",
            "Thai (Thailand)",
            "Vietnamese",
            "Vietnamese (Vietnam)",
            "Indonesian",
            "Indonesian (Indonesia)",
            "Malay",
            "Malay (Malaysia)",
            "Filipino",
            "Filipino (Philippines)",
            "Bengali (India)",
            "Tamil (India)",
            "Telugu (India)",
            "Marathi (India)",
            "Gujarati (India)",
            "Kannada (India)",
            "Malayalam (India)",
            "Urdu (India)",
            "Urdu (Pakistan)",
            "Swedish",
            "Swedish (Sweden)",
            "Norwegian Bokmål (Norway)",
            "Danish",
            "Danish (Denmark)",
            "Finnish",
            "Finnish (Finland)",
            "Greek",
            "Greek (Greece)",
            "Hebrew (Israel)",
            "Czech",
            "Czech (Czechia)",
            "Romanian",
            "Romanian (Romania)",
            "Hungarian",
            "Hungarian (Hungary)",
            "Bulgarian",
            "Bulgarian (Bulgaria)",
            "Croatian",
            "Croatian (Croatia)",
            "Ukrainian",
            "Ukrainian (Ukraine)",
            "English - Your Accent",
            "English - American Accent",
        ]
        
        return {
            "languages": sorted(languages),
            "total_count": len(languages),
            "note": "This is a simplified list. Full API supports 70+ languages and 175+ dialects. See documentation for complete list.",
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[VideoTranslate] Failed to get languages: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get languages: {str(e)}")
