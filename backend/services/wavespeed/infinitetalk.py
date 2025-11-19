from __future__ import annotations

import base64
from typing import Any, Dict, Optional

import requests
from fastapi import HTTPException
from loguru import logger

from .client import WaveSpeedClient
from .kling_animation import generate_animation_prompt

INFINITALK_MODEL_PATH = "wavespeed-ai/infinitetalk"
INFINITALK_MODEL_NAME = "wavespeed-ai/infinitetalk"
INFINITALK_DEFAULT_COST = 0.30  # $0.30 per 5 seconds at 720p tier
MAX_IMAGE_BYTES = 10 * 1024 * 1024  # 10MB
MAX_AUDIO_BYTES = 50 * 1024 * 1024  # 50MB safety cap


def _as_data_uri(content_bytes: bytes, mime_type: str) -> str:
    encoded = base64.b64encode(content_bytes).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"


def animate_scene_with_voiceover(
    *,
    image_bytes: bytes,
    audio_bytes: bytes,
    scene_data: Dict[str, Any],
    story_context: Dict[str, Any],
    user_id: str,
    resolution: str = "720p",
    prompt_override: Optional[str] = None,
    image_mime: str = "image/png",
    audio_mime: str = "audio/mpeg",
    client: Optional[WaveSpeedClient] = None,
) -> Dict[str, Any]:
    """
    Animate a scene image with narration audio using WaveSpeed InfiniteTalk.
    Returns dict with video bytes, prompt used, model name, and cost.
    """

    if not image_bytes:
        raise HTTPException(status_code=404, detail="Scene image bytes missing for animation.")
    if not audio_bytes:
        raise HTTPException(status_code=404, detail="Scene audio bytes missing for animation.")

    if len(image_bytes) > MAX_IMAGE_BYTES:
        raise HTTPException(
            status_code=400,
            detail="Scene image exceeds 10MB limit required by WaveSpeed InfiniteTalk.",
        )
    if len(audio_bytes) > MAX_AUDIO_BYTES:
        raise HTTPException(
            status_code=400,
            detail="Scene audio exceeds 50MB limit allowed for InfiniteTalk requests.",
        )

    if resolution not in {"480p", "720p"}:
        raise HTTPException(status_code=400, detail="Resolution must be '480p' or '720p'.")

    animation_prompt = prompt_override or generate_animation_prompt(scene_data, story_context, user_id)

    payload = {
        "image": _as_data_uri(image_bytes, image_mime),
        "audio": _as_data_uri(audio_bytes, audio_mime),
        "resolution": resolution,
    }
    if animation_prompt:
        payload["prompt"] = animation_prompt

    client = client or WaveSpeedClient()
    prediction_id = client.submit_image_to_video(INFINITALK_MODEL_PATH, payload, timeout=60)

    try:
        result = client.poll_until_complete(prediction_id, timeout_seconds=600, interval_seconds=1.0)
    except HTTPException as exc:
        detail = exc.detail or {}
        if isinstance(detail, dict):
            detail.setdefault("prediction_id", prediction_id)
            detail.setdefault("resume_available", True)
        raise

    outputs = result.get("outputs") or []
    if not outputs:
        raise HTTPException(status_code=502, detail="WaveSpeed InfiniteTalk completed but returned no outputs.")

    video_url = outputs[0]
    video_response = requests.get(video_url, timeout=180)
    if video_response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail={
                "error": "Failed to download InfiniteTalk video",
                "status_code": video_response.status_code,
                "response": video_response.text[:200],
            },
        )

    metadata = result.get("metadata") or {}
    duration = metadata.get("duration_seconds") or metadata.get("duration") or 0

    logger.info(
        "[InfiniteTalk] Generated talking avatar video user=%s scene=%s resolution=%s size=%s bytes",
        user_id,
        scene_data.get("scene_number"),
        resolution,
        len(video_response.content),
    )

    return {
        "video_bytes": video_response.content,
        "prompt": animation_prompt,
        "duration": duration or 5,
        "model_name": INFINITALK_MODEL_NAME,
        "cost": INFINITALK_DEFAULT_COST,
        "provider": "wavespeed",
        "source_video_url": video_url,
        "prediction_id": prediction_id,
    }


