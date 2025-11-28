from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from pydantic import BaseModel, Field

from middleware.auth_middleware import get_current_user
from models.story_models import (
    StoryStartRequest,
    StoryContentResponse,
    StoryScene,
    StoryContinueRequest,
    StoryContinueResponse,
)
from services.story_writer.story_service import StoryWriterService

from ..utils.auth import require_authenticated_user


router = APIRouter()
story_service = StoryWriterService()
scene_approval_store: Dict[str, Dict[str, Dict[str, Dict[str, Any]]]] = {}
APPROVAL_TTL_SECONDS = 60 * 60 * 24
MAX_APPROVALS_PER_USER = 200


def _cleanup_user_approvals(user_id: str) -> None:
    user_store = scene_approval_store.get(user_id)
    if not user_store:
        return
    now = datetime.utcnow()
    for project_id in list(user_store.keys()):
        scenes = user_store.get(project_id, {})
        for scene_id in list(scenes.keys()):
            timestamp = scenes[scene_id].get("timestamp")
            if isinstance(timestamp, datetime):
                if (now - timestamp).total_seconds() > APPROVAL_TTL_SECONDS:
                    scenes.pop(scene_id, None)
        if not scenes:
            user_store.pop(project_id, None)
    if not user_store:
        scene_approval_store.pop(user_id, None)


def _enforce_capacity(user_id: str) -> None:
    user_store = scene_approval_store.get(user_id)
    if not user_store:
        return
    entries: List[tuple[datetime, str, str]] = []
    for project_id, scenes in user_store.items():
        for scene_id, meta in scenes.items():
            timestamp = meta.get("timestamp")
            if isinstance(timestamp, datetime):
                entries.append((timestamp, project_id, scene_id))
    if len(entries) <= MAX_APPROVALS_PER_USER:
        return
    entries.sort(key=lambda item: item[0])
    to_remove = len(entries) - MAX_APPROVALS_PER_USER
    for i in range(to_remove):
        _, project_id, scene_id = entries[i]
        scenes = user_store.get(project_id)
        if not scenes:
            continue
        scenes.pop(scene_id, None)
        if not scenes:
            user_store.pop(project_id, None)


def _get_user_store(user_id: str) -> Dict[str, Dict[str, Dict[str, Any]]]:
    _cleanup_user_approvals(user_id)
    return scene_approval_store.setdefault(user_id, {})


@router.post("/generate-start", response_model=StoryContentResponse)
async def generate_story_start(
    request: StoryStartRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> StoryContentResponse:
    """Generate the starting section of a story."""
    try:
        user_id = require_authenticated_user(current_user)

        if not request.premise or not request.premise.strip():
            raise HTTPException(status_code=400, detail="Premise is required")
        if not request.outline or (isinstance(request.outline, str) and not request.outline.strip()):
            raise HTTPException(status_code=400, detail="Outline is required")

        logger.info(f"[StoryWriter] Generating story start for user {user_id}")

        outline_data: Any = request.outline
        if isinstance(outline_data, list) and outline_data and isinstance(outline_data[0], StoryScene):
            outline_data = [scene.dict() for scene in outline_data]

        story_length = getattr(request, "story_length", "Medium")
        story_start = story_service.generate_story_start(
            premise=request.premise,
            outline=outline_data,
            persona=request.persona,
            story_setting=request.story_setting,
            character_input=request.character_input,
            plot_elements=request.plot_elements,
            writing_style=request.writing_style,
            story_tone=request.story_tone,
            narrative_pov=request.narrative_pov,
            audience_age_group=request.audience_age_group,
            content_rating=request.content_rating,
            ending_preference=request.ending_preference,
            story_length=story_length,
            user_id=user_id,
        )

        story_length_lower = story_length.lower()
        is_short_story = "short" in story_length_lower or "1000" in story_length_lower
        is_complete = False
        if is_short_story:
            word_count = len(story_start.split()) if story_start else 0
            if word_count >= 900:
                is_complete = True
                logger.info(
                    f"[StoryWriter] Short story generated with {word_count} words. Marking as complete."
                )
            else:
                logger.warning(
                    f"[StoryWriter] Short story generated with only {word_count} words. May need continuation."
                )

        outline_response = outline_data
        if isinstance(outline_response, list):
            outline_response = "\n".join(
                [
                    f"Scene {scene.get('scene_number', i + 1)}: "
                    f"{scene.get('title', 'Untitled')}\n  {scene.get('description', '')}"
                    for i, scene in enumerate(outline_response)
                ]
            )

        return StoryContentResponse(
            story=story_start,
            premise=request.premise,
            outline=str(outline_response),
            is_complete=is_complete,
            success=True,
        )

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"[StoryWriter] Failed to generate story start: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/continue", response_model=StoryContinueResponse)
async def continue_story(
    request: StoryContinueRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> StoryContinueResponse:
    """Continue writing a story."""
    try:
        user_id = require_authenticated_user(current_user)

        if not request.story_text or not request.story_text.strip():
            raise HTTPException(status_code=400, detail="Story text is required")

        logger.info(f"[StoryWriter] Continuing story for user {user_id}")

        outline_data: Any = request.outline
        if isinstance(outline_data, list) and outline_data and isinstance(outline_data[0], StoryScene):
            outline_data = [scene.dict() for scene in outline_data]

        story_length = getattr(request, "story_length", "Medium")
        story_length_lower = story_length.lower()
        is_short_story = "short" in story_length_lower or "1000" in story_length_lower
        if is_short_story:
            logger.warning(
                "[StoryWriter] Attempted to continue a short story. Short stories should be complete in one call."
            )
            raise HTTPException(
                status_code=400,
                detail="Short stories are generated in a single call and should be complete. "
                "If the story is incomplete, please regenerate it from the beginning.",
            )

        current_word_count = len(request.story_text.split()) if request.story_text else 0
        if "long" in story_length_lower or "10000" in story_length_lower:
            target_total_words = 10000
        else:
            target_total_words = 4500
        buffer_target = int(target_total_words * 1.05)

        if current_word_count >= buffer_target or (
            current_word_count >= target_total_words
            and (current_word_count - target_total_words) < 50
        ):
            logger.info(
                f"[StoryWriter] Word count ({current_word_count}) already at or near target ({target_total_words})."
            )
            return StoryContinueResponse(continuation="IAMDONE", is_complete=True, success=True)

        continuation = story_service.continue_story(
            premise=request.premise,
            outline=outline_data,
            story_text=request.story_text,
            persona=request.persona,
            story_setting=request.story_setting,
            character_input=request.character_input,
            plot_elements=request.plot_elements,
            writing_style=request.writing_style,
            story_tone=request.story_tone,
            narrative_pov=request.narrative_pov,
            audience_age_group=request.audience_age_group,
            content_rating=request.content_rating,
            ending_preference=request.ending_preference,
            story_length=story_length,
            user_id=user_id,
        )

        is_complete = "IAMDONE" in continuation.upper()
        if not is_complete and continuation:
            new_story_text = request.story_text + "\n\n" + continuation
            new_word_count = len(new_story_text.split())
            if new_word_count >= buffer_target:
                logger.info(
                    f"[StoryWriter] Word count ({new_word_count}) now exceeds buffer target ({buffer_target})."
                )
                if "IAMDONE" not in continuation.upper():
                    continuation = continuation.rstrip() + "\n\nIAMDONE"
                is_complete = True
            elif new_word_count >= target_total_words and (
                new_word_count - target_total_words
            ) < 100:
                logger.info(
                    f"[StoryWriter] Word count ({new_word_count}) is at or very close to target ({target_total_words})."
                )
                if "IAMDONE" not in continuation.upper():
                    continuation = continuation.rstrip() + "\n\nIAMDONE"
                is_complete = True

        return StoryContinueResponse(continuation=continuation, is_complete=is_complete, success=True)

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"[StoryWriter] Failed to continue story: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


class SceneApprovalRequest(BaseModel):
    project_id: str = Field(..., min_length=1)
    scene_id: str = Field(..., min_length=1)
    approved: bool = True
    notes: Optional[str] = None


@router.post("/script/approve")
async def approve_script_scene(
    request: SceneApprovalRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """Persist scene approval metadata for auditing."""
    try:
        user_id = require_authenticated_user(current_user)
        if not request.project_id.strip() or not request.scene_id.strip():
            raise HTTPException(status_code=400, detail="project_id and scene_id are required")

        notes = request.notes.strip() if request.notes else None
        user_store = _get_user_store(user_id)
        project_store = user_store.setdefault(request.project_id, {})
        timestamp = datetime.utcnow()
        project_store[request.scene_id] = {
            "approved": request.approved,
            "notes": notes,
            "user_id": user_id,
            "timestamp": timestamp,
        }
        _enforce_capacity(user_id)
        logger.info(
            "[StoryWriter] Scene approval recorded user=%s project=%s scene=%s approved=%s",
            user_id,
            request.project_id,
            request.scene_id,
            request.approved,
        )
        return {
            "success": True,
            "project_id": request.project_id,
            "scene_id": request.scene_id,
            "approved": request.approved,
            "timestamp": timestamp.isoformat(),
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"[StoryWriter] Failed to approve scene: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


