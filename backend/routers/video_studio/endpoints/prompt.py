"""
Prompt optimization endpoints for Video Studio.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

from ...utils.auth import get_current_user, require_authenticated_user
from utils.logger_utils import get_service_logger
from services.wavespeed.client import WaveSpeedClient

logger = get_service_logger("video_studio.endpoints.prompt")

router = APIRouter()


class PromptOptimizeRequest(BaseModel):
    text: str = Field(..., description="The prompt text to optimize")
    mode: Optional[str] = Field(
        default="video",
        pattern="^(image|video)$",
        description="Optimization mode: 'image' or 'video' (default: 'video' for Video Studio)"
    )
    style: Optional[str] = Field(
        default="default",
        pattern="^(default|artistic|photographic|technical|anime|realistic)$",
        description="Style: 'default', 'artistic', 'photographic', 'technical', 'anime', or 'realistic'"
    )
    image: Optional[str] = Field(None, description="Base64-encoded image for context (optional)")


class PromptOptimizeResponse(BaseModel):
    optimized_prompt: str
    success: bool


@router.post("/optimize-prompt")
async def optimize_prompt(
    request: PromptOptimizeRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> PromptOptimizeResponse:
    """
    Optimize a prompt using WaveSpeed prompt optimizer.
    
    The WaveSpeedAI Prompt Optimizer enhances prompts specifically for image and video 
    generation workflows. It restructures and enriches your input prompt to improve:
    - Visual clarity and composition
    - Cinematic framing and lighting
    - Camera movement and style consistency
    - Motion dynamics for video generation
    
    Produces significantly better outputs across video generation models like FLUX, Wan, 
    Kling, Veo, Seedance, and more.
    """
    try:
        user_id = require_authenticated_user(current_user)

        if not request.text or not request.text.strip():
            raise HTTPException(status_code=400, detail="Prompt text is required")

        # Default to "video" mode for Video Studio
        mode = request.mode or "video"
        style = request.style or "default"

        logger.info(f"[VideoStudio] Optimizing prompt for user {user_id} (mode={mode}, style={style})")

        client = WaveSpeedClient()
        optimized_prompt = client.optimize_prompt(
            text=request.text.strip(),
            mode=mode,
            style=style,
            image=request.image,  # Optional base64 image
            enable_sync_mode=True,
            timeout=30
        )

        logger.info(f"[VideoStudio] Prompt optimized successfully for user {user_id}")

        return PromptOptimizeResponse(
            optimized_prompt=optimized_prompt,
            success=True
        )

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"[VideoStudio] Failed to optimize prompt: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to optimize prompt: {str(exc)}")
