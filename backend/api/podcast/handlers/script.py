"""
Podcast Script Handlers

Script generation endpoint.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
import json

from middleware.auth_middleware import get_current_user
from api.story_writer.utils.auth import require_authenticated_user
from services.llm_providers.main_text_generation import llm_text_gen
from loguru import logger
from ..models import (
    PodcastScriptRequest,
    PodcastScriptResponse,
    PodcastScene,
    PodcastSceneLine,
)

router = APIRouter()


@router.post("/script", response_model=PodcastScriptResponse)
async def generate_podcast_script(
    request: PodcastScriptRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Generate a podcast script outline (scenes + lines) using podcast-oriented prompting.
    """
    user_id = require_authenticated_user(current_user)

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

    prompt = f"""You are an expert podcast script planner. Create natural, conversational podcast scenes.

Podcast Idea: "{request.idea}"
Duration: ~{request.duration_minutes} minutes
Speakers: {request.speakers} (Host + optional Guest)

{f"RESEARCH CONTEXT:\n{research_context}\n" if research_context else ""}

Return JSON with:
- scenes: array of scenes. Each scene has:
  - id: string
  - title: short scene title (<= 60 chars)
  - duration: duration in seconds (evenly split across total duration)
  - emotion: string (one of: "neutral", "happy", "excited", "serious", "curious", "confident")
  - lines: array of {{"speaker": "...", "text": "...", "emphasis": boolean}}
    * Write natural, conversational dialogue
    * Each line can be a sentence or a few sentences that flow together
    * Use plain text only - no markdown formatting (no asterisks, underscores, etc.)
    * Mark "emphasis": true for key statistics or important points

Guidelines:
- Write for spoken delivery: conversational, natural, with contractions
- Use research insights naturally - weave statistics into dialogue, don't just list them
- Vary emotion per scene based on content
- Ensure scenes match target duration: aim for ~2.5 words per second of audio
- Keep it engaging and informative, like a real podcast conversation
"""

    try:
        raw = llm_text_gen(prompt=prompt, user_id=user_id, json_struct=None)
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

