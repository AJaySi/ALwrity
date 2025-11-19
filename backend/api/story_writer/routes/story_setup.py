from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from middleware.auth_middleware import get_current_user
from models.story_models import (
    StorySetupGenerationRequest,
    StorySetupGenerationResponse,
    StorySetupOption,
    StoryGenerationRequest,
    StoryOutlineResponse,
    StoryScene,
    StoryStartRequest,
    StoryPremiseResponse,
)
from services.story_writer.story_service import StoryWriterService

from ..utils.auth import require_authenticated_user


router = APIRouter()
story_service = StoryWriterService()


@router.post("/generate-setup", response_model=StorySetupGenerationResponse)
async def generate_story_setup(
    request: StorySetupGenerationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> StorySetupGenerationResponse:
    """Generate 3 story setup options from a user's story idea."""
    try:
        user_id = require_authenticated_user(current_user)

        if not request.story_idea or not request.story_idea.strip():
            raise HTTPException(status_code=400, detail="Story idea is required")

        logger.info(f"[StoryWriter] Generating story setup options for user {user_id}")

        options = story_service.generate_story_setup_options(
            story_idea=request.story_idea,
            user_id=user_id,
        )

        setup_options = [StorySetupOption(**option) for option in options]
        return StorySetupGenerationResponse(options=setup_options, success=True)

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"[StoryWriter] Failed to generate story setup options: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/generate-premise", response_model=StoryPremiseResponse)
async def generate_premise(
    request: StoryGenerationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> StoryPremiseResponse:
    """Generate a story premise."""
    try:
        user_id = require_authenticated_user(current_user)
        logger.info(f"[StoryWriter] Generating premise for user {user_id}")

        premise = story_service.generate_premise(
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
            user_id=user_id,
        )

        return StoryPremiseResponse(premise=premise, success=True)

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"[StoryWriter] Failed to generate premise: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/generate-outline", response_model=StoryOutlineResponse)
async def generate_outline(
    request: StoryStartRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    use_structured: bool = True,
) -> StoryOutlineResponse:
    """Generate a story outline from a premise."""
    try:
        user_id = require_authenticated_user(current_user)

        if not request.premise or not request.premise.strip():
            raise HTTPException(status_code=400, detail="Premise is required")

        logger.info(
            f"[StoryWriter] Generating outline for user {user_id} (structured={use_structured})"
        )
        logger.info(
            "[StoryWriter] Outline params: audience_age_group=%s, writing_style=%s, story_tone=%s",
            request.audience_age_group,
            request.writing_style,
            request.story_tone,
        )

        outline = story_service.generate_outline(
            premise=request.premise,
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
            user_id=user_id,
            use_structured_output=use_structured,
        )

        if isinstance(outline, list):
            scenes: List[StoryScene] = [
                StoryScene(**scene) if isinstance(scene, dict) else scene for scene in outline
            ]
            return StoryOutlineResponse(outline=scenes, success=True, is_structured=True)

        return StoryOutlineResponse(outline=str(outline), success=True, is_structured=False)

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"[StoryWriter] Failed to generate outline: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


