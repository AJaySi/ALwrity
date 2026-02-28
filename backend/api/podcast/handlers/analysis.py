"""
Podcast Analysis Handlers

Analysis endpoint for podcast ideas.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
import json
import uuid
from sqlalchemy.orm import Session

from services.database import get_db
from middleware.auth_middleware import get_current_user
from api.story_writer.utils.auth import require_authenticated_user
from services.llm_providers.main_text_generation import llm_text_gen
from services.llm_providers.main_image_generation import generate_image
from services.podcast_bible_service import PodcastBibleService
from utils.asset_tracker import save_asset_to_library
from loguru import logger
from ..constants import PODCAST_IMAGES_DIR
from ..models import (
    PodcastAnalyzeRequest, 
    PodcastAnalyzeResponse,
    PodcastEnhanceIdeaRequest,
    PodcastEnhanceIdeaResponse
)

router = APIRouter()


@router.post("/idea/enhance", response_model=PodcastEnhanceIdeaResponse)
async def enhance_podcast_idea(
    request: PodcastEnhanceIdeaRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Take raw keywords/topic and use AI to craft a presentable, detailed podcast idea.
    Uses the user's Podcast Bible for hyper-personalization if available.
    """
    user_id = require_authenticated_user(current_user)
    
    # Serialize Bible context if provided or generate from onboarding
    bible_context = ""
    try:
        bible_service = PodcastBibleService()
        if request.bible:
            from models.podcast_bible_models import PodcastBible
            bible_data = PodcastBible(**request.bible)
            bible_context = bible_service.serialize_bible(bible_data)
        else:
            # Generate from onboarding data directly
            bible_obj = bible_service.generate_bible(user_id, "temp_enhance")
            bible_context = bible_service.serialize_bible(bible_obj)
    except Exception as exc:
        logger.warning(f"[Podcast Enhance] Failed to parse or generate bible context: {exc}")

    prompt = f"""
You are a creative podcast producer. Your goal is to take a simple podcast idea or keywords
and transform it into a compelling, professional, and detailed episode concept.

{f"USER PERSONALIZATION CONTEXT (Podcast Bible):\n{bible_context}\n" if bible_context else ""}

RAW IDEA/KEYWORDS: "{request.idea}"

TASK:
1. Rewrite the idea into a professional, presentable 2-3 sentence episode pitch.
2. Focus on making it sound expert-led and audience-focused.
3. Ensure it aligns with the host's persona and target audience interests if context was provided.
4. Keep it concise but information-rich.

Return JSON with:
- enhanced_idea: the rewritten, professional episode pitch
- rationale: 1 sentence explaining why this version works better for the target audience
"""

    try:
        raw = llm_text_gen(prompt=prompt, user_id=user_id, json_struct=None)
        
        # Normalize response
        if isinstance(raw, str):
            data = json.loads(raw)
        else:
            data = raw
            
        return PodcastEnhanceIdeaResponse(
            enhanced_idea=data.get("enhanced_idea", request.idea),
            rationale=data.get("rationale", "Made it more professional and listener-focused.")
        )
    except Exception as exc:
        logger.error(f"[Podcast Enhance] Failed for user {user_id}: {exc}")
        return PodcastEnhanceIdeaResponse(
            enhanced_idea=request.idea,
            rationale="Failed to enhance idea with AI, using original."
        )


@router.post("/analyze", response_model=PodcastAnalyzeResponse)
async def analyze_podcast_idea(
    request: PodcastAnalyzeRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Analyze a podcast idea and return podcast-oriented outlines, keywords, and titles.
    If no avatar_url is provided, it generates one automatically based on the host's look.
    """
    user_id = require_authenticated_user(current_user)

    # Serialize Bible context if provided or generate from onboarding
    bible_context = ""
    bible_obj = None
    try:
        bible_service = PodcastBibleService()
        if request.bible:
            from models.podcast_bible_models import PodcastBible
            bible_data = PodcastBible(**request.bible)
            bible_context = bible_service.serialize_bible(bible_data)
            bible_obj = bible_data
        else:
            # Generate from onboarding data directly
            bible_obj = bible_service.generate_bible(user_id, "temp_analyze")
            bible_context = bible_service.serialize_bible(bible_obj)
            bible_obj = bible_obj
    except Exception as exc:
        logger.warning(f"[Podcast Analyze] Failed to parse or generate bible context: {exc}")

    # --- NEW: Generate Presenter Avatar if missing ---
    final_avatar_url = request.avatar_url
    final_avatar_prompt = None
    
    if not final_avatar_url:
        logger.info(f"[Podcast Analyze] No avatar_url provided, generating one for user {user_id}")
        try:
            # 1. PRE-FLIGHT VALIDATION: Check subscription limits for image generation
            from services.subscription import PricingService
            from services.subscription.preflight_validator import validate_image_generation_operations
            pricing_service = PricingService(db)
            validate_image_generation_operations(
                pricing_service=pricing_service,
                user_id=user_id,
                num_images=1
            )
            
            # 2. Build avatar prompt from Bible host look or fallback
            host_look = bible_obj.host.look if bible_obj and bible_obj.host.look else "A professional podcast host"
            visual_style = bible_obj.visual_style.style_preset if bible_obj else "Realistic Photography"
            
            final_avatar_prompt = f"Professional headshot of a podcast host, {host_look}, {visual_style} style, clean background, soft studio lighting, center-focused, high resolution, sharp focus, professional photography quality, 16:9 aspect ratio."
            
            # 3. Generate the image
            logger.info(f"[Podcast Analyze] Generating avatar with prompt: {final_avatar_prompt}")
            image_result = generate_image(
                prompt=final_avatar_prompt,
                user_id=user_id,
                width=1024,
                height=1024
            )
            
            # 4. Save to disk and library
            if image_result and image_result.image_bytes:
                img_id = str(uuid.uuid4())[:8]
                filename = f"presenter_podcast_{user_id}_{img_id}.png"
                output_path = PODCAST_IMAGES_DIR / filename
                PODCAST_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
                
                with open(output_path, "wb") as f:
                    f.write(image_result.image_bytes)
                
                final_avatar_url = f"/api/podcast/images/avatars/{filename}"
                
                # Save to asset library for reuse
                save_asset_to_library(
                    db=db,
                    user_id=user_id,
                    asset_type="image",
                    file_url=final_avatar_url,
                    filename=filename,
                    title=f"Presenter Avatar - {request.idea[:40]}",
                    description=f"AI-generated podcast presenter for: {request.idea}",
                    provider=image_result.provider,
                    model=image_result.model,
                    cost=image_result.cost
                )
                logger.info(f"[Podcast Analyze] ✅ Generated and saved avatar to {final_avatar_url}")
        except Exception as e:
            logger.error(f"[Podcast Analyze] ❌ Failed to generate avatar: {e}")
            # Non-fatal: continue analysis even if avatar generation fails
    
    # --- END: Avatar Generation ---

    # Incorporate user feedback if provided
    feedback_context = ""
    if request.feedback:
        feedback_context = f"""
USER REGENERATION FEEDBACK:
The user was not satisfied with the previous analysis. They provided the following instructions for improvement:
"{request.feedback}"
Please prioritize this feedback and adjust the analysis accordingly.
"""

    prompt = f"""
You are an expert podcast producer and research strategist. Given a podcast idea, craft concise podcast-ready assets
that sound like episode plans (not fiction stories).

{f"USER PERSONALIZATION CONTEXT (Podcast Bible):\n{bible_context}\n" if bible_context else ""}
{feedback_context}

Podcast Idea: "{request.idea}"
Duration: ~{request.duration} minutes
Speakers: {request.speakers} (host + optional guest)

TASK:
1. Define the target audience and content type aligned with the Bible's "Audience DNA" and "Brand DNA".
2. Identify 5 high-impact keywords.
3. Propose 2 episode outlines with factual segments.
4. Suggest 3 titles.
5. IMPORTANT: Generate 4-6 specific research queries for Exa. These queries MUST be highly targeted to the episode's topic, the host's expertise level, and the audience's interests as defined in the Bible.
   * Do NOT use generic queries like "latest trends in X".
   * DO use queries that look for case studies, specific data points, expert opinions, or contrasting viewpoints that would make for a deep, insightful podcast conversation.

Return JSON with:
- audience: short target audience description
- content_type: podcast style/format
- top_keywords: 5 podcast-relevant keywords/phrases
- suggested_outlines: 2 items, each with title (<=60 chars) and 4-6 short segments (bullet-friendly, factual)
- title_suggestions: 3 concise episode titles
- research_queries: array of {{"query": "string", "rationale": "string"}}
- exa_suggested_config: suggested Exa search options with:
  - exa_search_type: "auto" | "neural" | "keyword"
  - exa_category: one of ["research paper","news","company","github","tweet","personal site","pdf","financial report","linkedin profile"]
  - exa_include_domains: up to 3 reputable domains
  - exa_exclude_domains: up to 3 domains
  - max_sources: 6-10
  - include_statistics: boolean
  - date_range: one of ["last_month","last_3_months","last_year","all_time"]

Requirements:
- Keep language factual, actionable, and suited for spoken audio.
- Avoid narrative fiction tone.
- Prefer 2024-2025 context.
"""

    try:
        raw = llm_text_gen(prompt=prompt, user_id=user_id, json_struct=None)
    except HTTPException:
        # Re-raise HTTPExceptions (e.g., 429 subscription limit) - preserve error details
        raise
    except Exception as exc:
        logger.error(f"[Podcast Analyze] Analysis failed for user {user_id}: {exc}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}")

    # Normalize response (accept dict or JSON string)
    if isinstance(raw, str):
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="LLM returned non-JSON output")
    elif isinstance(raw, dict):
        data = raw
    else:
        raise HTTPException(status_code=500, detail="Unexpected LLM response format")

    audience = data.get("audience") or "Growth-focused professionals"
    content_type = data.get("content_type") or "Interview + insights"
    top_keywords = data.get("top_keywords") or []
    suggested_outlines = data.get("suggested_outlines") or []
    title_suggestions = data.get("title_suggestions") or []
    research_queries = data.get("research_queries") or []
    exa_suggested_config = data.get("exa_suggested_config") or None

    return PodcastAnalyzeResponse(
        audience=audience,
        content_type=content_type,
        top_keywords=top_keywords,
        suggested_outlines=suggested_outlines,
        title_suggestions=title_suggestions,
        research_queries=research_queries,
        exa_suggested_config=exa_suggested_config,
        bible=bible_obj.model_dump() if bible_obj else None,
        avatar_url=final_avatar_url,
        avatar_prompt=final_avatar_prompt,
    )

