"""
Podcast Script Handlers

Script generation and approval endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import json

from middleware.auth_middleware import get_current_user
from api.story_writer.utils.auth import require_authenticated_user
from services.llm_providers.main_text_generation import llm_text_gen
from services.podcast_bible_service import PodcastBibleService
from models.podcast_bible_models import PodcastBible
from loguru import logger
from ..models import (
    PodcastScriptRequest,
    PodcastScriptResponse,
    PodcastScene,
    PodcastSceneLine,
)

router = APIRouter()


class SceneApprovalRequest(BaseModel):
    project_id: str = Field(..., min_length=1)
    scene_id: str = Field(..., min_length=1)
    approved: bool = True
    notes: Optional[str] = None


@router.post("/script/approve")
async def approve_podcast_scene(
    request: SceneApprovalRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """Persist scene approval metadata for auditing (podcast-specific)."""
    user_id = require_authenticated_user(current_user)
    logger.warning(f"[Podcast] Scene approval recorded user={user_id} project={request.project_id} scene={request.scene_id} approved={request.approved}")
    return {
        "success": True,
        "project_id": request.project_id,
        "scene_id": request.scene_id,
        "approved": request.approved,
    }


@router.post("/script", response_model=PodcastScriptResponse)
async def generate_podcast_script(
    request: PodcastScriptRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Generate a podcast script outline (scenes + lines) using podcast-oriented prompting.
    """
    user_id = require_authenticated_user(current_user)
    logger.warning(f"[ScriptGen] ========== SCRIPT GENERATION START ==========")
    logger.warning(f"[ScriptGen] Topic: {request.idea[:60]}...")
    logger.warning(f"[ScriptGen] Duration: {request.duration_minutes} min, Speakers: {request.speakers}")
    logger.warning(f"[ScriptGen] Has research: {bool(request.research)}, Has bible: {bool(request.bible)}, Has analysis: {bool(request.analysis)}")

    # Build comprehensive research context for higher-quality scripts
    research_context = ""
    if request.research:
        try:
            key_insights = request.research.get("keyword_analysis", {}).get("key_insights") or []
            fact_cards = request.research.get("factCards", []) or []
            mapped_angles = request.research.get("mappedAngles", []) or []
            sources = request.research.get("sources", []) or []

            top_facts = [f.get("quote", "") for f in fact_cards[:5] if f.get("quote")]
            angles_summary = [
                f"{a.get('title', '')}: {a.get('why', '')}" for a in mapped_angles[:3] if a.get("title") or a.get("why")
            ]
            top_sources = [s.get("url") for s in sources[:3] if s.get("url")]

            research_parts = []
            if key_insights:
                research_parts.append(f"Key Insights: {', '.join(key_insights[:5])}")
            if top_facts:
                research_parts.append(f"Key Facts: {', '.join(top_facts)}")
            if angles_summary:
                research_parts.append(f"Research Angles: {' | '.join(angles_summary)}")
            if top_sources:
                research_parts.append(f"Top Sources: {', '.join(top_sources)}")

            research_context = "\n".join(research_parts)
        except Exception as exc:
            logger.warning(f"Failed to parse research context: {exc}")
            research_context = ""

    # Extract Podcast Bible context for hyper-personalization
    bible_context = ""
    if request.bible:
        try:
            bible_service = PodcastBibleService()
            bible_obj = PodcastBible(**request.bible)
            bible_context = bible_service.serialize_bible(bible_obj)
        except Exception as exc:
            logger.warning(f"Failed to serialize podcast bible: {exc}")

    # Extract Analysis and Outline context for grounding
    analysis_context = ""
    if request.analysis:
        try:
            audience = request.analysis.get('audience', '') or ''
            content_type = request.analysis.get('contentType', '') or ''
            keywords = request.analysis.get('topKeywords', []) or []
            analysis_context = f"ANALYSIS: Audience={audience} | Type={content_type} | Keywords={', '.join(keywords[:8])}"
        except:
            pass

    outline_context = ""
    if request.outline:
        try:
            title = request.outline.get('title', '') or ''
            segments = request.outline.get('segments', []) or []
            outline_context = f"OUTLINE: {title} - {' | '.join(segments[:5])}"
        except:
            pass

    prompt = f"""Create a podcast script with scenes and dialogue.

{f"BIBLE: {bible_context[:1500]}" if bible_context else ""}
{f"{analysis_context}" if analysis_context else ""}
{f"{outline_context}" if outline_context else ""}
{f"RESEARCH: {research_context[:1200]}" if research_context else ""}

Topic: "{request.idea}"
Duration: {request.duration_minutes} min | Speakers: {request.speakers}

Return JSON with scenes array. Each scene:
- id: string
- title: short title (<=50 chars)
- duration: seconds (total/5)
- emotion: neutral|happy|excited|serious|curious|confident
- lines: array of {{speaker, text, emphasis}}
  - Use 2-4 LINES PER SCENE (shorter script = lower TTS costs)
  - Each line: 1-3 sentences, conversational
  - Plain text only, no markdown

COST OPTIMIZATION:
- 5-6 scenes max for {request.duration_minutes} min episode
- Concise, information-dense dialogue
- Skip filler words and redundant phrases
- Focus on unique insights from research
- Make every line count toward value delivery
"""

    try:
        logger.warning(f"[ScriptGen] Calling LLM to generate script (prompt length: {len(prompt)})...")
        raw = llm_text_gen(
            prompt=prompt,
            user_id=user_id,
            json_struct=None,
            preferred_provider=None,
            flow_type="premium_tool",
        )
        logger.warning(f"[ScriptGen] LLM response received, length: {len(raw) if raw else 0}")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Script generation failed: {exc}")

    if isinstance(raw, str):
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="LLM returned non-JSON output")
    elif isinstance(raw, dict):
        data = raw
    else:
        raise HTTPException(status_code=500, detail="Unexpected LLM response format")

    scenes_data = data.get("scenes") or []
    if not isinstance(scenes_data, list):
        raise HTTPException(status_code=500, detail="LLM response missing scenes array")

    valid_emotions = {"neutral", "happy", "excited", "serious", "curious", "confident"}

    # Normalize scenes
    scenes: list[PodcastScene] = []
    for idx, scene in enumerate(scenes_data):
        title = scene.get("title") or f"Scene {idx + 1}"
        duration = int(scene.get("duration") or max(30, (request.duration_minutes * 60) // max(1, len(scenes_data))))
        emotion = scene.get("emotion") or "neutral"
        if emotion not in valid_emotions:
            emotion = "neutral"
        lines_raw = scene.get("lines") or []
        lines: list[PodcastSceneLine] = []
        for line in lines_raw:
            speaker = line.get("speaker") or ("Host" if len(lines) % request.speakers == 0 else "Guest")
            text = line.get("text") or ""
            emphasis = line.get("emphasis", False)
            if text:
                lines.append(PodcastSceneLine(speaker=speaker, text=text, emphasis=emphasis))
        scenes.append(
            PodcastScene(
                id=scene.get("id") or f"scene-{idx + 1}",
                title=title,
                duration=duration,
                lines=lines,
                approved=False,
                emotion=emotion,
            )
        )

    return PodcastScriptResponse(scenes=scenes)

