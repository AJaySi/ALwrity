from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks, HTTPException, Depends
from fastapi.responses import FileResponse
from typing import Optional, Dict, Any
import shutil
import os
from pathlib import Path
from services.wavespeed.infinitetalk import animate_scene_with_voiceover
from ..task_manager import task_manager
from middleware.auth_middleware import get_current_user
from loguru import logger
from services.database import get_engine_for_user
from sqlalchemy.orm import sessionmaker
from utils.asset_tracker import save_asset_to_library

router = APIRouter()

# Define storage directory
UPLOAD_DIR = Path("backend/data/video_studio/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def _process_avatar_generation(task_id: str, image_path: Path, audio_path: Path, user_id: str, resolution: str, model: str):
    """
    Background task to process avatar generation using shared InfiniteTalk service.
    """
    try:
        task_manager.update_task(task_id, "processing", user_id=user_id)
        
        # Read file bytes
        with open(image_path, "rb") as f:
            image_bytes = f.read()
        with open(audio_path, "rb") as f:
            audio_bytes = f.read()
            
        # Dummy scene data required by the service (used for prompt generation)
        scene_data = {
            "title": "Test Persona", 
            "description": "A talking avatar video generated via Video Studio."
        }
        story_context = {}
        
        # Call the common interface function
        logger.info(f"[VideoStudio] Starting InfiniteTalk generation for task {task_id}")
        result = animate_scene_with_voiceover(
            image_bytes=image_bytes,
            audio_bytes=audio_bytes,
            scene_data=scene_data,
            story_context=story_context,
            user_id=user_id,
            resolution=resolution
        )
        
        # Save the resulting video bytes to a file
        video_filename = f"video_{task_id}.mp4"
        video_path = UPLOAD_DIR / video_filename
        with open(video_path, "wb") as f:
            f.write(result["video_bytes"])
            
        # Prepare result for frontend (remove raw bytes)
        result.pop("video_bytes", None)
        
        # Add local download URL
        video_url = f"/api/video-studio/download/{video_filename}"
        result["video_url"] = video_url
        
        # Save asset to library
        try:
            engine = get_engine_for_user(user_id)
            SessionLocal = sessionmaker(bind=engine)
            db = SessionLocal()
            try:
                save_asset_to_library(
                    db=db,
                    user_id=user_id,
                    asset_type="video",
                    source_module="video_studio",
                    filename=video_filename,
                    file_url=video_url,
                    file_path=str(video_path),
                    file_size=video_path.stat().st_size,
                    mime_type="video/mp4",
                    title=f"Avatar Video {task_id}",
                    description=f"Generated avatar video using {model}",
                    model=model,
                    cost=result.get("cost", 0.0),
                    generation_time=result.get("generation_time", 0.0)
                )
            finally:
                db.close()
        except Exception as e:
            logger.error(f"[VideoStudio] Failed to save asset to library: {e}")

        logger.info(f"[VideoStudio] Task {task_id} completed successfully")
        task_manager.update_task(task_id, "completed", result=result, user_id=user_id)
        
    except Exception as e:
        logger.error(f"[VideoStudio] Avatar generation failed for task {task_id}: {e}", exc_info=True)
        task_manager.update_task(task_id, "failed", error=str(e), user_id=user_id)
    finally:
        # Cleanup temp upload files
        try:
            if image_path.exists(): image_path.unlink()
            if audio_path.exists(): audio_path.unlink()
        except Exception as e:
            logger.warning(f"[VideoStudio] Failed to cleanup temp files: {e}")

@router.post("/avatar/create-async")
async def create_avatar_video(
    background_tasks: BackgroundTasks,
    image: UploadFile = File(...),
    audio: UploadFile = File(...),
    resolution: str = Form("720p"),
    model: str = Form("infinitetalk"),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a talking avatar video using InfiniteTalk (WaveSpeed).
    Directly uses the common backend service without Podcast Maker dependencies.
    """
    user_id = current_user.get("id", "anonymous")
    
    # Validate file types roughly
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid image file type")
    
    task_id = task_manager.create_task("avatar_generation", user_id=user_id)
    
    # Generate temp paths
    image_ext = Path(image.filename).suffix or ".png"
    audio_ext = Path(audio.filename).suffix or ".mp3"
    image_path = UPLOAD_DIR / f"img_{task_id}{image_ext}"
    audio_path = UPLOAD_DIR / f"aud_{task_id}{audio_ext}"
    
    try:
        # Save uploaded files
        with open(image_path, "wb") as f:
            shutil.copyfileobj(image.file, f)
        with open(audio_path, "wb") as f:
            shutil.copyfileobj(audio.file, f)
            
        # Start background task
        background_tasks.add_task(
            _process_avatar_generation,
            task_id,
            image_path,
            audio_path,
            user_id,
            resolution,
            model
        )
        
        return {"task_id": task_id, "status": "pending", "message": "Video generation started successfully."}
        
    except Exception as e:
        # Cleanup if immediate failure
        if image_path.exists(): image_path.unlink()
        if audio_path.exists(): audio_path.unlink()
        logger.error(f"[VideoStudio] Failed to start generation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start generation: {str(e)}")

@router.get("/task/{task_id}")
async def get_task_status(task_id: str, current_user: dict = Depends(get_current_user)):
    user_id = current_user.get("id", "anonymous")
    task = task_manager.get_task(task_id, user_id=user_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.get("/download/{filename}")
async def download_video(filename: str):
    file_path = UPLOAD_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)
