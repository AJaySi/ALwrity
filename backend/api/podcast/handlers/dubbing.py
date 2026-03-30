"""
Podcast Dubbing Handlers

Audio dubbing endpoints for translating podcast audio to different languages.
Supports both low-quality (DeepL) and high-quality (WaveSpeed) dubbing with voice cloning.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from services.database import get_db
from middleware.auth_middleware import get_current_user
from api.story_writer.utils.auth import require_authenticated_user
from api.story_writer.task_manager import task_manager
from loguru import logger

from ..models import (
    PodcastAudioDubRequest,
    PodcastAudioDubResponse,
    PodcastAudioDubResult,
    PodcastAudioDubEstimateRequest,
    PodcastAudioDubEstimateResponse,
    VoiceCloneRequest,
    VoiceCloneResponse,
    VoiceCloneResult,
)
from services.dubbing import AudioDubbingService
from ..constants import get_podcast_media_read_dirs, get_podcast_media_dir

router = APIRouter()

_dubbing_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="podcast_dubbing")

_DUBBED_AUDIO_SUBDIR = Path("dubbed_audio")
_LEGACY_DUBBED_AUDIO_DIR = Path(__file__).resolve().parents[3] / "data" / "media" / "dubbed_audio"


def _get_dubbed_audio_dir(user_id: str, *, ensure_exists: bool = False) -> Path:
    """Resolve tenant-scoped dubbed audio directory under podcast audio media."""
    base_dir = get_podcast_media_dir("audio", user_id, ensure_exists=ensure_exists)
    dubbed_dir = (base_dir / _DUBBED_AUDIO_SUBDIR).resolve()
    if ensure_exists:
        dubbed_dir.mkdir(parents=True, exist_ok=True)
    return dubbed_dir


def _resolve_dubbed_audio_file(filename: str, user_id: str) -> Path:
    """Resolve dubbed audio with traversal-safe checks (tenant first, then legacy fallback)."""
    clean_filename = filename.split("?", 1)[0].strip()
    if not clean_filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    candidate_dirs: list[Path] = []
    for base_dir in get_podcast_media_read_dirs("audio", user_id):
        candidate_dirs.append((base_dir / _DUBBED_AUDIO_SUBDIR).resolve())
    candidate_dirs.append(_LEGACY_DUBBED_AUDIO_DIR.resolve())

    for target_dir in candidate_dirs:
        candidate = (target_dir / clean_filename).resolve()
        if not str(candidate).startswith(str(target_dir)):
            logger.error(f"[Podcast][Dubbing] Attempted path traversal: {filename}")
            raise HTTPException(status_code=403, detail="Invalid audio path")
        if candidate.exists():
            return candidate

    raise HTTPException(status_code=404, detail="Audio file not found")


def _execute_dubbing_task(
    task_id: str,
    source_audio_url: str,
    source_language: Optional[str],
    target_language: str,
    quality: str,
    voice_id: str,
    speed: float,
    emotion: str,
    use_voice_clone: bool,
    custom_voice_id: Optional[str],
    voice_clone_accuracy: float,
    user_id: str,
):
    """Background task to dub audio."""
    try:
        task_manager.update_task_status(
            task_id, "processing", progress=5.0,
            message="Starting audio dubbing..."
        )
        
        dubbed_audio_dir = _get_dubbed_audio_dir(user_id, ensure_exists=True)
        service = AudioDubbingService(output_dir=dubbed_audio_dir)
        
        def progress_callback(progress: float, message: str):
            task_manager.update_task_status(
                task_id, "processing", progress=progress,
                message=message
            )
        
        logger.info(f"[Dubbing] Task {task_id}: Starting dubbing with voice_clone={use_voice_clone}")
        
        result = service.dub_audio(
            source_audio=source_audio_url,
            target_language=target_language,
            source_language=source_language,
            voice_id=voice_id,
            speed=speed,
            emotion=emotion,
            quality=quality,
            use_voice_clone=use_voice_clone,
            custom_voice_id=custom_voice_id,
            accuracy=voice_clone_accuracy,
            user_id=user_id,
            progress_callback=progress_callback,
        )
        
        task_manager.update_task_status(
            task_id, "completed", progress=100.0,
            result={
                "dubbed_audio_url": result.dubbed_audio_url,
                "dubbed_audio_filename": Path(result.dubbed_audio_path).name,
                "original_transcript": result.original_transcript,
                "translated_transcript": result.translated_transcript,
                "source_language": result.source_language,
                "target_language": result.target_language,
                "voice_id": result.voice_id,
                "quality": result.quality,
                "duration_seconds": result.duration_seconds,
                "file_size": result.file_size,
                "cost": result.cost,
                "status": "completed",
                "voice_clone_used": result.voice_clone_used,
                "cloned_voice_id": result.cloned_voice_id,
            },
            message="Audio dubbing completed!"
        )
        
        logger.info(f"[Dubbing] Task {task_id} completed successfully (voice_clone_used={result.voice_clone_used})")
        
    except Exception as e:
        logger.error(f"[Dubbing] Task {task_id} failed: {str(e)}")
        task_manager.update_task_status(
            task_id, "failed",
            error=str(e),
            message=f"Dubbing failed: {str(e)}"
        )


def _execute_voice_clone_task(
    task_id: str,
    source_audio_url: str,
    custom_voice_id: Optional[str],
    accuracy: float,
    language_boost: Optional[str],
    user_id: str,
):
    """Background task to clone voice from audio."""
    try:
        task_manager.update_task_status(
            task_id, "processing", progress=10.0,
            message="Starting voice cloning..."
        )
        
        dubbed_audio_dir = _get_dubbed_audio_dir(user_id, ensure_exists=True)
        service = AudioDubbingService(output_dir=dubbed_audio_dir)
        
        task_manager.update_task_status(
            task_id, "processing", progress=30.0,
            message="Processing audio..."
        )
        
        voice_info = service.clone_voice_from_audio(
            source_audio=source_audio_url,
            custom_voice_id=custom_voice_id,
            accuracy=accuracy,
            language_boost=language_boost,
            user_id=user_id,
        )
        
        task_manager.update_task_status(
            task_id, "completed", progress=100.0,
            result={
                "voice_id": voice_info.voice_id,
                "voice_url": voice_info.voice_url,
                "source_language": voice_info.source_language,
                "accuracy": voice_info.accuracy,
                "file_size": voice_info.file_size,
                "status": "completed",
            },
            message="Voice cloning completed!"
        )
        
        logger.info(f"[VoiceClone] Task {task_id} completed: {voice_info.voice_id}")
        
    except Exception as e:
        logger.error(f"[VoiceClone] Task {task_id} failed: {str(e)}")
        task_manager.update_task_status(
            task_id, "failed",
            error=str(e),
            message=f"Voice cloning failed: {str(e)}"
        )


@router.post("/dub/audio", response_model=PodcastAudioDubResponse)
async def create_audio_dubbing_task(
    request: PodcastAudioDubRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create an audio dubbing task.
    
    Translates podcast audio to a target language using STT → Translate → TTS pipeline.
    
    For high-quality dubbing with voice preservation, set use_voice_clone=True.
    
    - **source_audio_url**: URL or path to source audio file
    - **target_language**: Target language code (e.g., 'es', 'Spanish')
    - **source_language**: Source language (auto-detected if not provided)
    - **quality**: 'low' (DeepL, cheaper) or 'high' (WaveSpeed, better quality)
    - **voice_id**: Voice ID for TTS (default: 'Wise_Woman')
    - **speed**: Speech speed 0.5-2.0 (default: 1.0)
    - **use_voice_clone**: Use voice cloning to preserve original speaker's voice
    - **custom_voice_id**: Custom name for the cloned voice
    - **voice_clone_accuracy**: Voice cloning accuracy 0.1-1.0 (default: 0.7)
    """
    user_id = require_authenticated_user(current_user)
    
    task_id = task_manager.create_task(
        "audio_dubbing",
        metadata={"owner_user_id": user_id},
    )
    
    background_tasks.add_task(
        _execute_dubbing_task,
        task_id=task_id,
        source_audio_url=request.source_audio_url,
        source_language=request.source_language,
        target_language=request.target_language,
        quality=request.quality,
        voice_id=request.voice_id or "Wise_Woman",
        speed=request.speed or 1.0,
        emotion=request.emotion or "happy",
        use_voice_clone=request.use_voice_clone or False,
        custom_voice_id=request.custom_voice_id,
        voice_clone_accuracy=request.voice_clone_accuracy or 0.7,
        user_id=user_id,
    )
    
    logger.info(f"[Dubbing] Created task {task_id} for user {user_id} (voice_clone={request.use_voice_clone})")
    
    return PodcastAudioDubResponse(
        task_id=task_id,
        status="pending",
        message="Audio dubbing task created"
    )


@router.get("/dub/{task_id}/result", response_model=PodcastAudioDubResult)
async def get_dubbing_result(
    task_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Get the result of a completed dubbing task.
    """
    user_id = require_authenticated_user(current_user)
    
    task_status = task_manager.get_task_status(task_id, requester_user_id=user_id)
    
    if not task_status:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task_status.get("status") == "failed":
        raise HTTPException(
            status_code=500,
            detail=task_status.get("error", "Dubbing failed")
        )
    
    if task_status.get("status") != "completed":
        return PodcastAudioDubResult(
            task_id=task_id,
            status=task_status.get("status", "pending"),
            dubbed_audio_url="",
            dubbed_audio_filename="",
            original_transcript="",
            translated_transcript="",
            source_language="",
            target_language="",
            voice_id="",
            quality="",
            duration_seconds=0,
            file_size=0,
            cost=0.0,
            voice_clone_used=False,
            cloned_voice_id=None,
        )
    
    result_data = task_status.get("result", {})
    
    return PodcastAudioDubResult(
        task_id=task_id,
        status="completed",
        dubbed_audio_url=result_data.get("dubbed_audio_url", ""),
        dubbed_audio_filename=result_data.get("dubbed_audio_filename", ""),
        original_transcript=result_data.get("original_transcript", ""),
        translated_transcript=result_data.get("translated_transcript", ""),
        source_language=result_data.get("source_language", ""),
        target_language=result_data.get("target_language", ""),
        voice_id=result_data.get("voice_id", ""),
        quality=result_data.get("quality", ""),
        duration_seconds=result_data.get("duration_seconds", 0),
        file_size=result_data.get("file_size", 0),
        cost=result_data.get("cost", 0.0),
        voice_clone_used=result_data.get("voice_clone_used", False),
        cloned_voice_id=result_data.get("cloned_voice_id"),
    )


@router.get("/dub/audio/{filename}")
async def serve_dubbed_audio(
    filename: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Serve a dubbed audio file.
    """
    user_id = require_authenticated_user(current_user)
    
    audio_path = _resolve_dubbed_audio_file(filename, user_id)
    
    return FileResponse(
        path=audio_path,
        media_type="audio/mpeg",
        filename=filename,
    )


@router.post("/dub/estimate", response_model=PodcastAudioDubEstimateResponse)
async def estimate_dubbing_cost(
    request: PodcastAudioDubEstimateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Estimate the cost for audio dubbing.
    
    Set use_voice_clone=True to include voice cloning cost ($0.05).
    """
    user_id = require_authenticated_user(current_user)
    
    dubbed_audio_dir = _get_dubbed_audio_dir(user_id, ensure_exists=True)
    service = AudioDubbingService(output_dir=dubbed_audio_dir)
    
    cost_estimate = service.estimate_cost(
        audio_duration_seconds=request.audio_duration_seconds,
        target_language=request.target_language,
        quality=request.quality,
        use_voice_clone=request.use_voice_clone or False,
    )
    
    return PodcastAudioDubEstimateResponse(**cost_estimate)


@router.get("/dub/languages")
async def get_supported_dubbing_languages(
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Get list of supported languages for dubbing.
    """
    from services.translation import list_supported_languages
    
    languages = list_supported_languages()
    
    return {
        "languages": [
            {"code": code, "name": name}
            for code, name in sorted(languages.items(), key=lambda x: x[1])
        ],
        "count": len(languages),
    }


@router.get("/dub/voices")
async def get_available_voices(
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Get list of available TTS voices for dubbing.
    """
    return {
        "voices": [
            {"id": "Wise_Woman", "name": "Wise Woman", "gender": "female"},
            {"id": "Warm_Woman", "name": "Warm Woman", "gender": "female"},
            {"id": "Young_Woman", "name": "Young Woman", "gender": "female"},
            {"id": "Mature_Woman", "name": "Mature Woman", "gender": "female"},
            {"id": "Gentle_Woman", "name": "Gentle Woman", "gender": "female"},
            {"id": "Confident_Man", "name": "Confident Man", "gender": "male"},
            {"id": "Warm_Man", "name": "Warm Man", "gender": "male"},
            {"id": "Young_Man", "name": "Young Man", "gender": "male"},
            {"id": "Mature_Man", "name": "Mature Man", "gender": "male"},
            {"id": "Default", "name": "Default", "gender": "neutral"},
        ],
        "count": 10,
        "note": "Voice cloning creates custom voices from audio samples. Use /dub/voices/clone to create one."
    }


@router.post("/dub/voices/clone", response_model=VoiceCloneResponse)
async def create_voice_clone_task(
    request: VoiceCloneRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Clone a voice from an audio sample.
    
    Creates a custom voice that can be used for dubbing with preserved speaker identity.
    
    - **source_audio_url**: URL or path to source audio (10-60 seconds recommended)
    - **custom_voice_id**: Custom name for the cloned voice
    - **accuracy**: Cloning accuracy 0.1-1.0 (higher = better quality but more processing)
    - **language_boost**: Language to optimize the voice for
    """
    user_id = require_authenticated_user(current_user)
    
    task_id = task_manager.create_task(
        "voice_clone",
        metadata={"owner_user_id": user_id},
    )
    
    background_tasks.add_task(
        _execute_voice_clone_task,
        task_id=task_id,
        source_audio_url=request.source_audio_url,
        custom_voice_id=request.custom_voice_id,
        accuracy=request.accuracy or 0.7,
        language_boost=request.language_boost,
        user_id=user_id,
    )
    
    logger.info(f"[VoiceClone] Created task {task_id} for user {user_id}")
    
    return VoiceCloneResponse(
        task_id=task_id,
        status="pending",
        message="Voice cloning task created"
    )


@router.get("/dub/voices/{task_id}/result", response_model=VoiceCloneResult)
async def get_voice_clone_result(
    task_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Get the result of a completed voice cloning task.
    """
    user_id = require_authenticated_user(current_user)
    
    task_status = task_manager.get_task_status(task_id, requester_user_id=user_id)
    
    if not task_status:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task_status.get("status") == "failed":
        raise HTTPException(
            status_code=500,
            detail=task_status.get("error", "Voice cloning failed")
        )
    
    if task_status.get("status") != "completed":
        return VoiceCloneResult(
            task_id=task_id,
            voice_id="",
            voice_url="",
            source_language="",
            accuracy=0.0,
            file_size=0,
            status=task_status.get("status", "pending"),
        )
    
    result_data = task_status.get("result", {})
    
    return VoiceCloneResult(
        task_id=task_id,
        voice_id=result_data.get("voice_id", ""),
        voice_url=result_data.get("voice_url", ""),
        source_language=result_data.get("source_language", ""),
        accuracy=result_data.get("accuracy", 0.7),
        file_size=result_data.get("file_size", 0),
        status="completed",
    )


@router.get("/dub/voices/audio/{filename}")
async def serve_voice_audio(
    filename: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Serve a voice sample audio file.
    """
    user_id = require_authenticated_user(current_user)
    
    try:
        audio_path = _resolve_dubbed_audio_file(filename, user_id)
    except HTTPException as exc:
        if exc.status_code == 404:
            raise HTTPException(status_code=404, detail="Voice audio file not found") from exc
        raise
    
    return FileResponse(
        path=audio_path,
        media_type="audio/mpeg",
        filename=filename,
    )
