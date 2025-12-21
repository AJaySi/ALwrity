"""YouTube Creator scene image generation handlers."""

from pathlib import Path
from typing import Dict, Any, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from middleware.auth_middleware import get_current_user
from services.database import get_db
from services.subscription import PricingService
from services.subscription.preflight_validator import validate_image_generation_operations
from services.llm_providers.main_image_generation import generate_image
from services.wavespeed.client import WaveSpeedClient
from utils.asset_tracker import save_asset_to_library
from utils.logger_utils import get_service_logger

router = APIRouter(tags=["youtube-image"])
logger = get_service_logger("api.youtube.image")

# Directories
base_dir = Path(__file__).parent.parent.parent.parent
YOUTUBE_IMAGES_DIR = base_dir / "youtube_images"
YOUTUBE_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
YOUTUBE_AVATARS_DIR = base_dir / "youtube_avatars"


class YouTubeImageRequest(BaseModel):
    scene_id: str
    scene_title: Optional[str] = None
    scene_content: Optional[str] = None
    base_avatar_url: Optional[str] = None
    idea: Optional[str] = None
    width: Optional[int] = 1024
    height: Optional[int] = 1024
    custom_prompt: Optional[str] = None
    style: Optional[str] = None  # e.g., "Realistic", "Fiction"
    rendering_speed: Optional[str] = None  # e.g., "Quality", "Turbo"
    aspect_ratio: Optional[str] = None  # e.g., "16:9"


def require_authenticated_user(current_user: Dict[str, Any]) -> str:
    """Extract and validate user ID from current user."""
    user_id = current_user.get("id") if current_user else None
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    return str(user_id)


def _load_base_avatar_bytes(avatar_url: str) -> bytes:
    """Load base avatar bytes for character consistency."""
    filename = avatar_url.split("/")[-1].split("?")[0]
    avatar_path = YOUTUBE_AVATARS_DIR / filename
    if not avatar_path.exists() or not avatar_path.is_file():
        raise HTTPException(status_code=404, detail="Base avatar image not found")
    return avatar_path.read_bytes()


def _save_scene_image(image_bytes: bytes, scene_id: str) -> Dict[str, str]:
    """Persist generated scene image and return file/url info."""
    unique_id = str(uuid.uuid4())[:8]
    image_filename = f"yt_scene_{scene_id}_{unique_id}.png"
    image_path = YOUTUBE_IMAGES_DIR / image_filename
    with open(image_path, "wb") as f:
        f.write(image_bytes)

    image_url = f"/api/youtube/images/scenes/{image_filename}"
    return {
        "image_filename": image_filename,
        "image_path": str(image_path),
        "image_url": image_url,
    }


@router.post("/image")
async def generate_youtube_scene_image(
    request: YouTubeImageRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate a YouTube scene image, with optional avatar consistency."""
    user_id = require_authenticated_user(current_user)

    if not request.scene_title:
        raise HTTPException(status_code=400, detail="Scene title is required")

    try:
        # Pre-flight subscription validation
        pricing_service = PricingService(db)
        validate_image_generation_operations(
            pricing_service=pricing_service,
            user_id=user_id,
            num_images=1,
        )
        logger.info(f"[YouTube] ✅ Pre-flight validation passed for user {user_id}")

        base_avatar_bytes = None
        if request.base_avatar_url:
            try:
                base_avatar_bytes = _load_base_avatar_bytes(request.base_avatar_url)
                logger.info(f"[YouTube] Loaded base avatar for scene {request.scene_id}")
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"[YouTube] Failed to load base avatar: {e}", exc_info=True)
                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": "Failed to load base avatar",
                        "message": f"Could not load the base avatar image: {str(e)}",
                    },
                )

        # Build prompt
        image_prompt = ""
        if base_avatar_bytes:
            prompt_parts = []
            if request.scene_title:
                prompt_parts.append(f"Scene: {request.scene_title}")
            if request.scene_content:
                content_preview = request.scene_content[:200].replace("\n", " ").strip()
                prompt_parts.append(f"Context: {content_preview}")
            if request.idea:
                prompt_parts.append(f"Video idea: {request.idea[:80].strip()}")
            prompt_parts.append("YouTube creator on camera, engaging and dynamic framing")
            prompt_parts.append("Clean background, good lighting, thumbnail-friendly composition")
            image_prompt = ", ".join(prompt_parts)
        else:
            prompt_parts = [
                "YouTube creator scene",
                "clean, modern background",
                "good lighting, high contrast for thumbnail clarity",
            ]
            if request.scene_title:
                prompt_parts.append(f"Scene theme: {request.scene_title}")
            if request.scene_content:
                prompt_parts.append(f"Context: {request.scene_content[:120].replace(chr(10), ' ')}")
            if request.idea:
                prompt_parts.append(f"Topic: {request.idea[:80]}")
            prompt_parts.append("video-optimized composition, 16:9 aspect ratio")
            image_prompt = ", ".join(prompt_parts)

        # Generate image
        provider = "wavespeed"
        model = "ideogram-v3-turbo"
        if base_avatar_bytes:
            logger.info(f"[YouTube] Using character-consistent generation for scene {request.scene_id}")
            style = request.style or "Realistic"
            rendering_speed = request.rendering_speed or "Quality"
            aspect_ratio = request.aspect_ratio or "16:9"
            width = request.width or 1024
            height = request.height or 576

            wavespeed_client = WaveSpeedClient()
            image_bytes = wavespeed_client.generate_character_image(
                prompt=image_prompt,
                reference_image_bytes=base_avatar_bytes,
                style=style,
                aspect_ratio=aspect_ratio,
                rendering_speed=rendering_speed,
                timeout=None,
            )
            model = "ideogram-character"
        else:
            logger.info(f"[YouTube] Generating scene {request.scene_id} from scratch")
            image_options = {
                "provider": "wavespeed",
                "model": "ideogram-v3-turbo",
                "width": request.width or 1024,
                "height": request.height or 576,
            }
            result = generate_image(
                prompt=request.custom_prompt or image_prompt,
                options=image_options,
                user_id=user_id,
            )
            image_bytes = result.image_bytes
            provider = result.provider
            model = result.model

        # Save image
        saved = _save_scene_image(image_bytes, request.scene_id)

        # Save to asset library
        try:
            save_asset_to_library(
                db=db,
                user_id=user_id,
                asset_type="image",
                source_module="youtube_creator",
                filename=saved["image_filename"],
                file_url=saved["image_url"],
                file_path=saved["image_path"],
                file_size=len(image_bytes),
                mime_type="image/png",
                title=f"YouTube Scene: {request.scene_title or request.scene_id}",
                description=request.scene_content or f"Scene image for {request.scene_id}",
                prompt=image_prompt,
                tags=["youtube_creator", "scene", request.scene_id],
                provider=provider,
                model=model,
                asset_metadata={
                    "scene_id": request.scene_id,
                    "scene_title": request.scene_title,
                    "has_base_avatar": bool(base_avatar_bytes),
                    "width": request.width or 1024,
                    "height": request.height or 576,
                },
            )
        except Exception as e:
            logger.warning(f"[YouTube] Failed to save scene image to asset library: {e}")

        return {
            "scene_id": request.scene_id,
            "scene_title": request.scene_title,
            "image_filename": saved["image_filename"],
            "image_url": saved["image_url"],
            "width": request.width or 1024,
            "height": request.height or 576,
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"[YouTube] Scene image generation failed: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate scene image: {str(exc)}")


@router.get("/images/{category}/{filename}")
async def serve_youtube_image(
    category: str,
    filename: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Serve stored YouTube images (avatars or scenes).
    Unified endpoint for both avatar and scene images.
    """
    require_authenticated_user(current_user)

    if category not in {"avatars", "scenes"}:
        raise HTTPException(status_code=400, detail="Invalid image category. Must be 'avatars' or 'scenes'")

    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    directory = YOUTUBE_AVATARS_DIR if category == "avatars" else YOUTUBE_IMAGES_DIR
    image_path = directory / filename
    
    if not image_path.exists() or not image_path.is_file():
        raise HTTPException(status_code=404, detail="Image not found")

    return FileResponse(
        path=str(image_path),
        media_type="image/png",
        filename=filename,
    )
