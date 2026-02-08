"""
Step 4 Brand Asset Routes
Handles brand avatar generation, enhancement, and variation.
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from loguru import logger
from .step4_persona_routes import _extract_user_id
import base64
import os
from pathlib import Path
from utils.file_storage import save_file_safely, generate_unique_filename
from services.database import get_db, WORKSPACE_DIR
from utils.asset_tracker import save_asset_to_library

from services.llm_providers.main_image_generation import (
    generate_image_with_provider,
    enhance_image_prompt,
    generate_image_variation
)

router = APIRouter()

# --- Models ---
class AvatarPromptRequest(BaseModel):
    user_id: Optional[str] = None
    prompt: str
    aspect_ratio: str = "1:1"
    style_preset: Optional[str] = None
    negative_prompt: Optional[str] = None
    num_inference_steps: int = 30
    guidance_scale: float = 7.5

class AvatarEnhanceRequest(BaseModel):
    user_id: Optional[str] = None
    prompt: str

class VoiceCloneRequest(BaseModel):
    user_id: Optional[str] = None
    voice_name: str
    description: Optional[str] = None
    engine: str = "qwen3" # qwen3 or minimax

# --- Routes ---

@router.post("/generate-avatar")
async def generate_avatar(
    request: AvatarPromptRequest,
    db: Session = Depends(get_db)
):
    """Generate a brand avatar using available image providers."""
    try:
        user_id = _extract_user_id(request.user_id)
        
        logger.info(f"Generating avatar for user {user_id} with prompt: {request.prompt}")
        
        # 1. Generate Image
        result = await generate_image_with_provider(
            prompt=request.prompt,
            aspect_ratio=request.aspect_ratio,
            negative_prompt=request.negative_prompt,
            num_inference_steps=request.num_inference_steps,
            guidance_scale=request.guidance_scale,
            style_preset=request.style_preset,
            user_id=user_id
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "Generation failed"))
            
        # 2. Save to local storage and Asset Library
        # The result typically contains image_base64 or image_url
        # For simplicity, we assume image_base64 is returned or we download the URL
        
        image_data = result.get("image_base64")
        if not image_data and result.get("image_url"):
            # TODO: Download image from URL if needed, or just store URL
            pass
            
        if image_data:
            # Decode if needed (usually it's already base64 string)
            # Save file
            filename = generate_unique_filename("avatar", "png")
            file_path = save_file_safely(
                base64.b64decode(image_data) if isinstance(image_data, str) else image_data,
                user_id,
                "avatars",
                filename
            )
            
            # Save to Asset Library
            asset_id = save_asset_to_library(
                db=db,
                user_id=user_id,
                file_path=file_path,
                asset_type="image",
                category="brand_avatar",
                meta_data={
                    "prompt": request.prompt,
                    "provider": result.get("provider", "unknown"),
                    "style": request.style_preset
                }
            )
            
            # Construct public URL (this depends on your static file serving setup)
            # Assuming /api/assets/{user_id}/avatars/{filename}
            image_url = f"/api/assets/{user_id}/avatars/{filename}"
            
            return {
                "success": True,
                "image_url": image_url,
                "image_base64": image_data, # Optional: return base64 for immediate display
                "asset_id": asset_id
            }
            
        return {"success": False, "error": "No image data returned"}

    except Exception as e:
        logger.error(f"Avatar generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/enhance-prompt")
async def enhance_prompt_route(
    request: AvatarEnhanceRequest
):
    """Enhance a simple prompt into a detailed midjourney-style prompt."""
    try:
        user_id = _extract_user_id(request.user_id)
        logger.info(f"Enhancing prompt for user {user_id}: {request.prompt}")
        
        enhanced_prompt = await enhance_image_prompt(request.prompt)
        
        return {
            "success": True,
            "original_prompt": request.prompt,
            "optimized_prompt": enhanced_prompt
        }
    except Exception as e:
        logger.error(f"Prompt enhancement failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create-voice-clone")
async def create_voice_clone(
    voice_name: str = Form(...),
    description: str = Form(None),
    engine: str = Form("qwen3"),
    file: UploadFile = File(...),
    user_id: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Create a voice clone from an audio file."""
    try:
        user_id = _extract_user_id(user_id)
        logger.info(f"Creating voice clone '{voice_name}' for user {user_id}")
        
        # 1. Save uploaded audio file
        file_content = await file.read()
        filename = generate_unique_filename("voice_sample", Path(file.filename).suffix.lstrip("."))
        file_path = save_file_safely(file_content, user_id, "voice_samples", filename)
        
        # 2. Call Voice Cloning API (Placeholder for actual implementation)
        # TODO: Integrate with Minimax or CosyVoice API
        # For now, we simulate success
        
        # 3. Save to Asset Library
        asset_id = save_asset_to_library(
            db=db,
            user_id=user_id,
            file_path=file_path,
            asset_type="audio",
            category="voice_clone",
            meta_data={
                "voice_name": voice_name,
                "engine": engine,
                "description": description,
                "original_filename": file.filename
            }
        )
        
        return {
            "success": True,
            "custom_voice_id": f"vc_{asset_id}", # Mock ID
            "preview_audio_url": f"/api/assets/{user_id}/voice_samples/{filename}",
            "asset_id": asset_id,
            "message": "Voice clone created successfully (simulated)"
        }
        
    except Exception as e:
        logger.error(f"Voice cloning failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
