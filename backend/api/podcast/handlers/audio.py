"""
Podcast Audio Handlers

Audio generation, combining, and serving endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Dict, Any
from pathlib import Path
from urllib.parse import urlparse
import tempfile
import uuid
import shutil

from services.database import get_db
from middleware.auth_middleware import get_current_user, get_current_user_with_query_token
from api.story_writer.utils.auth import require_authenticated_user
from utils.asset_tracker import save_asset_to_library
from models.story_models import StoryAudioResult
from loguru import logger
from ..constants import PODCAST_AUDIO_DIR, audio_service
from ..models import (
    PodcastAudioRequest,
    PodcastAudioResponse,
    PodcastCombineAudioRequest,
    PodcastCombineAudioResponse,
)

router = APIRouter()


@router.post("/audio", response_model=PodcastAudioResponse)
async def generate_podcast_audio(
    request: PodcastAudioRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generate AI audio for a podcast scene using shared audio service.
    """
    user_id = require_authenticated_user(current_user)

    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Text is required")

    try:
        result: StoryAudioResult = audio_service.generate_ai_audio(
            scene_number=0,
            scene_title=request.scene_title,
            text=request.text.strip(),
            user_id=user_id,
            voice_id=request.voice_id or "Wise_Woman",
            speed=request.speed or 1.0,  # Normal speed (was 0.9, but too slow - causing duration issues)
            volume=request.volume or 1.0,
            pitch=request.pitch or 0.0,  # Normal pitch (0.0 = neutral)
            emotion=request.emotion or "neutral",
            english_normalization=request.english_normalization or False,
            sample_rate=request.sample_rate,
            bitrate=request.bitrate,
            channel=request.channel,
            format=request.format,
            language_boost=request.language_boost,
            enable_sync_mode=request.enable_sync_mode,
        )
        
        # Override URL to use podcast endpoint instead of story endpoint
        if result.get("audio_url") and "/api/story/audio/" in result.get("audio_url", ""):
            audio_filename = result.get("audio_filename", "")
            result["audio_url"] = f"/api/podcast/audio/{audio_filename}"
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Audio generation failed: {exc}")

    # Save to asset library (podcast module)
    try:
        if result.get("audio_url"):
            asset_id = save_asset_to_library(
                db=db,
                user_id=user_id,
                asset_type="audio",
                source_module="podcast_maker",
                filename=result.get("audio_filename", ""),
                file_url=result.get("audio_url", ""),
                file_path=result.get("audio_path"),
                file_size=result.get("file_size"),
                mime_type="audio/mpeg",
                title=f"{request.scene_title} - Podcast",
                description="Podcast scene narration",
                tags=["podcast", "audio", request.scene_id],
                provider=result.get("provider"),
                model=result.get("model"),
                cost=result.get("cost"),
                asset_metadata={
                    "scene_id": request.scene_id,
                    "scene_title": request.scene_title,
                    "status": "completed",
                },
            )
            if asset_id is None:
                logger.warning(
                    "[Podcast] Audio generated but asset tracking failed",
                    extra={"user_id": user_id, "filename": result.get("audio_filename", "")},
                )
    except Exception as e:
        logger.warning(f"[Podcast] Failed to save audio asset: {e}")

    return PodcastAudioResponse(
        scene_id=request.scene_id,
        scene_title=request.scene_title,
        audio_filename=result.get("audio_filename", ""),
        audio_url=result.get("audio_url", ""),
        provider=result.get("provider", "wavespeed"),
        model=result.get("model", "minimax/speech-02-hd"),
        voice_id=result.get("voice_id", request.voice_id or "Wise_Woman"),
        text_length=result.get("text_length", len(request.text)),
        file_size=result.get("file_size", 0),
        cost=result.get("cost", 0.0),
    )


@router.post("/combine-audio", response_model=PodcastCombineAudioResponse)
async def combine_podcast_audio(
    request: PodcastCombineAudioRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Combine multiple scene audio files into a single podcast audio file.
    """
    user_id = require_authenticated_user(current_user)
    
    if not request.scene_ids or not request.scene_audio_urls:
        raise HTTPException(status_code=400, detail="Scene IDs and audio URLs are required")
    
    if len(request.scene_ids) != len(request.scene_audio_urls):
        raise HTTPException(status_code=400, detail="Scene IDs and audio URLs count must match")
    
    try:
        # Import moviepy for audio concatenation
        try:
            from moviepy import AudioFileClip, concatenate_audioclips
        except ImportError:
            logger.error("[Podcast] MoviePy not available for audio combination")
            raise HTTPException(
                status_code=500,
                detail="Audio combination requires MoviePy. Please install: pip install moviepy"
            )
        
        # Create temporary directory for audio processing
        temp_dir = Path(tempfile.gettempdir()) / f"podcast_combine_{uuid.uuid4().hex[:8]}"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        audio_clips = []
        total_duration = 0.0
        
        try:
            # Log incoming request for debugging
            logger.info(f"[Podcast] Combining audio: {len(request.scene_audio_urls)} URLs received")
            for idx, url in enumerate(request.scene_audio_urls):
                logger.info(f"[Podcast] URL {idx+1}: {url}")
            
            # Download and load each audio file from podcast_audio directory
            for idx, audio_url in enumerate(request.scene_audio_urls):
                try:
                    # Normalize audio URL - handle both absolute and relative paths
                    if audio_url.startswith("http"):
                        # External URL - would need to download
                        logger.error(f"[Podcast] External URLs not supported: {audio_url}")
                        raise HTTPException(
                            status_code=400,
                            detail=f"External URLs not supported. Please use local file paths."
                        )
                    
                    # Handle relative paths - only /api/podcast/audio/... URLs are supported
                    audio_path = None
                    if audio_url.startswith("/api/"):
                        # Extract filename from URL
                        parsed = urlparse(audio_url)
                        path = parsed.path if parsed.scheme else audio_url
                        
                        # Handle both /api/podcast/audio/ and /api/story/audio/ URLs (for backward compatibility)
                        if "/api/podcast/audio/" in path:
                            filename = path.split("/api/podcast/audio/", 1)[1].split("?", 1)[0].strip()
                        elif "/api/story/audio/" in path:
                            # Convert story audio URLs to podcast audio (they're in the same directory now)
                            filename = path.split("/api/story/audio/", 1)[1].split("?", 1)[0].strip()
                            logger.info(f"[Podcast] Converting story audio URL to podcast: {audio_url} -> {filename}")
                        else:
                            logger.error(f"[Podcast] Unsupported audio URL format: {audio_url}. Expected /api/podcast/audio/ or /api/story/audio/ URLs.")
                            continue
                        
                        if not filename:
                            logger.error(f"[Podcast] Could not extract filename from URL: {audio_url}")
                            continue
                        
                        # Podcast audio files are stored in podcast_audio directory
                        audio_path = (PODCAST_AUDIO_DIR / filename).resolve()
                        
                        # Security check: ensure path is within PODCAST_AUDIO_DIR
                        if not str(audio_path).startswith(str(PODCAST_AUDIO_DIR)):
                            logger.error(f"[Podcast] Attempted path traversal when resolving audio: {audio_url}")
                            continue
                    else:
                        logger.warning(f"[Podcast] Non-API URL format, treating as direct path: {audio_url}")
                        audio_path = Path(audio_url)
                    
                    if not audio_path or not audio_path.exists():
                        logger.error(f"[Podcast] Audio file not found: {audio_path} (from URL: {audio_url})")
                        continue
                    
                    # Load audio clip
                    audio_clip = AudioFileClip(str(audio_path))
                    audio_clips.append(audio_clip)
                    total_duration += audio_clip.duration
                    logger.info(f"[Podcast] Loaded audio {idx+1}/{len(request.scene_audio_urls)}: {audio_path.name} ({audio_clip.duration:.2f}s)")
                    
                except HTTPException:
                    raise
                except Exception as e:
                    logger.error(f"[Podcast] Failed to load audio {idx+1}: {e}", exc_info=True)
                    # Continue with other audio files
                    continue
            
            if not audio_clips:
                raise HTTPException(status_code=400, detail="No valid audio files found to combine")
            
            # Concatenate all audio clips
            logger.info(f"[Podcast] Combining {len(audio_clips)} audio clips (total duration: {total_duration:.2f}s)")
            combined_audio = concatenate_audioclips(audio_clips)
            
            # Generate output filename
            output_filename = f"podcast_combined_{request.project_id}_{uuid.uuid4().hex[:8]}.mp3"
            output_path = PODCAST_AUDIO_DIR / output_filename
            
            # Write combined audio file
            combined_audio.write_audiofile(
                str(output_path),
                codec="mp3",
                bitrate="192k",
                logger=None,  # Suppress moviepy logging
            )
            
            # Close audio clips to free resources
            for clip in audio_clips:
                clip.close()
            combined_audio.close()
            
            file_size = output_path.stat().st_size
            audio_url = f"/api/podcast/audio/{output_filename}"
            
            logger.info(f"[Podcast] Combined audio saved: {output_path} ({file_size} bytes)")
            
            # Save to asset library
            try:
                asset_id = save_asset_to_library(
                    db=db,
                    user_id=user_id,
                    asset_type="audio",
                    source_module="podcast_maker",
                    filename=output_filename,
                    file_url=audio_url,
                    file_path=str(output_path),
                    file_size=file_size,
                    mime_type="audio/mpeg",
                    title=f"Combined Podcast - {request.project_id}",
                    description=f"Combined podcast audio from {len(request.scene_ids)} scenes",
                    tags=["podcast", "audio", "combined", request.project_id],
                    asset_metadata={
                        "project_id": request.project_id,
                        "scene_ids": request.scene_ids,
                        "scene_count": len(request.scene_ids),
                        "total_duration": total_duration,
                        "status": "completed",
                    },
                )
                if asset_id is None:
                    logger.warning(
                        "[Podcast] Combined audio generated but asset tracking failed",
                        extra={"user_id": user_id, "filename": output_filename},
                    )
            except Exception as e:
                logger.warning(f"[Podcast] Failed to save combined audio asset: {e}")
            
            return PodcastCombineAudioResponse(
                combined_audio_url=audio_url,
                combined_audio_filename=output_filename,
                total_duration=total_duration,
                file_size=file_size,
                scene_count=len(request.scene_ids),
            )
            
        finally:
            # Cleanup temporary directory
            try:
                if temp_dir.exists():
                    shutil.rmtree(temp_dir)
            except Exception as e:
                logger.warning(f"[Podcast] Failed to cleanup temp directory: {e}")
                
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"[Podcast] Audio combination failed: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Audio combination failed: {exc}")


@router.get("/audio/{filename}")
async def serve_podcast_audio(
    filename: str,
    current_user: Dict[str, Any] = Depends(get_current_user_with_query_token),
):
    """Serve generated podcast scene audio files.
    
    Supports authentication via Authorization header or token query parameter.
    Query parameter is useful for HTML elements like <audio> that cannot send custom headers.
    """
    require_authenticated_user(current_user)
    
    # Security check: ensure filename doesn't contain path traversal
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    audio_path = (PODCAST_AUDIO_DIR / filename).resolve()
    
    # Security check: ensure path is within PODCAST_AUDIO_DIR
    if not str(audio_path).startswith(str(PODCAST_AUDIO_DIR)):
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    return FileResponse(audio_path, media_type="audio/mpeg")

