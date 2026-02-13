"""YouTube Video Planning Router

Handles video planning and script generation endpoints.
Provides AI-powered video planning with persona integration and avatar generation.
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from middleware.auth_middleware import get_current_user
from services.database import get_db
from models.content_asset_models import AssetType, AssetSource

from .models import VideoPlanRequest, VideoPlanResponse
from .utils import require_authenticated_user
from .dependencies import get_youtube_planner_service, get_persona_data_service, get_content_asset_service

# Import avatar handler for auto-generation
from .handlers.avatar import _generate_avatar_from_context

from utils.logger_utils import get_service_logger

logger = get_service_logger("api.youtube.planning")

router = APIRouter(prefix="/planning", tags=["youtube-planning"])


@router.post("/plan", response_model=VideoPlanResponse)
async def create_video_plan(
    request: VideoPlanRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> VideoPlanResponse:
    """
    Generate a comprehensive video plan from user input.

    This endpoint uses AI to create a detailed plan including:
    - Video summary and target audience
    - Content outline with timing
    - Hook strategy and CTA
    - Visual style recommendations
    - SEO keywords
    """
    try:
        user_id = require_authenticated_user(current_user)

        logger.info(
            f"[YouTubePlanning] Planning video: idea={request.user_idea[:50]}..., "
            f"duration={request.duration_type}, user={user_id}"
        )

        # Note: Research subscription checks are handled by ResearchService internally
        # ResearchService validates limits before making API calls and raises HTTPException(429) if exceeded

        # Note: Subscription checks for LLM are handled by llm_text_gen internally
        # It validates limits before making API calls and raises HTTPException(429) if exceeded

        # Get persona data if available
        persona_data = None
        try:
            persona_service = get_persona_data_service()
            persona_data = persona_service.get_user_persona_data(user_id)
        except Exception as e:
            logger.warning(f"[YouTubePlanning] Could not load persona data: {e}")

        # Generate plan (optimized: for shorts, combine plan + scenes in one call)
        planner = get_youtube_planner_service()
        plan = await planner.generate_video_plan(
            user_idea=request.user_idea,
            duration_type=request.duration_type,
            video_type=request.video_type,
            target_audience=request.target_audience,
            video_goal=request.video_goal,
            brand_style=request.brand_style,
            persona_data=persona_data,
            reference_image_description=request.reference_image_description,
            source_content_id=request.source_content_id,
            source_content_type=request.source_content_type,
            user_id=user_id,
            include_scenes=(request.duration_type == "shorts"),  # Optimize shorts
            enable_research=getattr(request, 'enable_research', True),  # Research enabled by default
        )

        # Auto-generate avatar if user didn't upload one
        # Try to reuse existing avatar from asset library first to save on AI calls during testing
        auto_avatar_url = None
        if not request.avatar_url:
            try:
                import uuid
                import json
                from services.content_asset_service import ContentAssetService

                # Check for existing YouTube creator avatar in asset library
                asset_service = get_content_asset_service()
                existing_avatars, _ = asset_service.get_user_assets(
                    user_id=user_id,
                    asset_type=AssetType.IMAGE,
                    source_module=AssetSource.YOUTUBE_CREATOR,
                    limit=1,  # Get most recent one
                )

                if existing_avatars and len(existing_avatars) > 0:
                    # Reuse the most recent avatar
                    existing_avatar = existing_avatars[0]
                    auto_avatar_url = existing_avatar.file_url
                    plan["auto_generated_avatar_url"] = auto_avatar_url
                    plan["avatar_reused"] = True  # Flag to indicate avatar was reused
                    logger.info(
                        f"[YouTubePlanning] ♻️ Reusing existing avatar from asset library to save AI call: {auto_avatar_url} "
                        f"(asset_id: {existing_avatar.id}, created: {existing_avatar.created_at})"
                    )
                else:
                    # No existing avatar found, generate new one
                    logger.info(f"[YouTubePlanning] 🎨 No existing avatar found, generating new avatar...")
                    avatar_response = await _generate_avatar_from_context(
                        user_id=user_id,
                        project_id=f"plan_{user_id}_{uuid.uuid4().hex[:8]}",
                        audience=request.target_audience or plan.get("target_audience"),  # Prefer user input
                        content_type=request.video_type,  # User's video type selection
                        video_plan_json=json.dumps(plan),
                        brand_style=request.brand_style,  # User's brand style preference
                        db=db,
                    )
                    auto_avatar_url = avatar_response.get("avatar_url")
                    avatar_prompt = avatar_response.get("avatar_prompt")
                    plan["auto_generated_avatar_url"] = auto_avatar_url
                    plan["avatar_prompt"] = avatar_prompt  # Store the AI prompt used for generation
                    plan["avatar_reused"] = False  # Flag to indicate avatar was newly generated
                    logger.info(f"[YouTubePlanning] ✅ Auto-generated new avatar based on user inputs and plan: {auto_avatar_url}")
            except Exception as e:
                logger.warning(f"[YouTubePlanning] Avatar generation/reuse failed (non-critical): {e}")
                # Non-critical, continue without avatar

        return VideoPlanResponse(
            success=True,
            plan=plan,
            message="Video plan generated successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[YouTubePlanning] Error creating plan: {e}", exc_info=True)
        return VideoPlanResponse(
            success=False,
            message=f"Failed to create video plan: {str(e)}"
        )