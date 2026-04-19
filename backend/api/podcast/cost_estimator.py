"""
Podcast cost estimation helpers.

Builds user-facing podcast estimates from the subscription pricing catalog
instead of hard-coded frontend heuristics.
"""

from __future__ import annotations

from typing import Any, Dict, Optional
from sqlalchemy.orm import Session

from models.subscription_models import APIProvider
from services.subscription.pricing_service import PricingService


def _round_money(value: float) -> float:
    return round(float(value), 4)


def _load_pricing(
    pricing_service: PricingService,
    provider: APIProvider,
    preferred_model: str,
) -> Optional[Dict[str, Any]]:
    pricing = pricing_service.get_pricing_for_provider_model(provider, preferred_model)
    if pricing:
        return pricing
    # Fallback to provider default model row (if configured).
    return pricing_service.get_pricing_for_provider_model(provider, "default")


def estimate_podcast_cost(
    *,
    db: Session,
    duration_minutes: int,
    speakers: int,
    query_count: int,
    include_avatar_phase: bool = True,
) -> Optional[Dict[str, Any]]:
    """
    Compute a backend estimate for podcast creation.

    Returns None when pricing rows are unavailable so UI can display "Unavailable".
    """
    pricing_service = PricingService(db)

    gemini_pricing = _load_pricing(pricing_service, APIProvider.GEMINI, "gemini-2.5-flash")
    exa_pricing = _load_pricing(pricing_service, APIProvider.EXA, "exa-search")
    audio_pricing = _load_pricing(pricing_service, APIProvider.AUDIO, "minimax/speech-02-hd")
    video_pricing = _load_pricing(pricing_service, APIProvider.VIDEO, "default")
    image_pricing = _load_pricing(pricing_service, APIProvider.STABILITY, "qwen-image")

    if not gemini_pricing:
        return None

    minutes = max(1, int(duration_minutes or 1))
    speaker_count = max(1, int(speakers or 1))
    research_queries = max(1, int(query_count or 1))

    # Phase-level usage assumptions (token/request proxies for pre-creation estimate).
    analysis_input_tokens = 1800
    analysis_output_tokens = 1000
    research_synthesis_input_tokens = 2200
    research_synthesis_output_tokens = 900
    script_input_tokens = max(1800, minutes * 300)
    script_output_tokens = max(2200, minutes * 700)

    # TTS token proxy: ~900 chars per minute per speaker.
    estimated_tts_tokens = max(900, minutes * 900 * speaker_count)

    analysis_cost = (
        analysis_input_tokens * float(gemini_pricing.get("cost_per_input_token") or 0.0)
        + analysis_output_tokens * float(gemini_pricing.get("cost_per_output_token") or 0.0)
        + float(gemini_pricing.get("cost_per_request") or 0.0)
    )
    research_llm_cost = (
        research_synthesis_input_tokens * float(gemini_pricing.get("cost_per_input_token") or 0.0)
        + research_synthesis_output_tokens * float(gemini_pricing.get("cost_per_output_token") or 0.0)
        + float(gemini_pricing.get("cost_per_request") or 0.0)
    )
    script_cost = (
        script_input_tokens * float(gemini_pricing.get("cost_per_input_token") or 0.0)
        + script_output_tokens * float(gemini_pricing.get("cost_per_output_token") or 0.0)
        + float(gemini_pricing.get("cost_per_request") or 0.0)
    )

    research_search_cost = 0.0
    if exa_pricing:
        research_search_cost = research_queries * float(exa_pricing.get("cost_per_request") or 0.0)

    tts_cost = 0.0
    if audio_pricing:
        tts_cost = (
            estimated_tts_tokens * float(audio_pricing.get("cost_per_input_token") or 0.0)
            + float(audio_pricing.get("cost_per_request") or 0.0)
        )

    # Assume one video render request per minute (upper-bound planning estimate).
    video_cost = 0.0
    if video_pricing:
        video_cost = minutes * float(video_pricing.get("cost_per_request") or 0.0)

    avatar_cost = 0.0
    if include_avatar_phase and image_pricing:
        image_unit = float(image_pricing.get("cost_per_image") or image_pricing.get("cost_per_request") or 0.0)
        avatar_cost = speaker_count * image_unit

    research_cost = research_search_cost + research_llm_cost
    total = analysis_cost + research_cost + script_cost + tts_cost + video_cost + avatar_cost

    return {
        "ttsCost": _round_money(tts_cost),
        "avatarCost": _round_money(avatar_cost),
        "videoCost": _round_money(video_cost),
        "researchCost": _round_money(research_cost),
        "analysisCost": _round_money(analysis_cost),
        "scriptCost": _round_money(script_cost),
        "total": _round_money(total),
        "currency": "USD",
        "source": "pricing_catalog",
        "assumptions": {
            "analysis_input_tokens": analysis_input_tokens,
            "analysis_output_tokens": analysis_output_tokens,
            "research_synthesis_input_tokens": research_synthesis_input_tokens,
            "research_synthesis_output_tokens": research_synthesis_output_tokens,
            "script_input_tokens": script_input_tokens,
            "script_output_tokens": script_output_tokens,
            "estimated_tts_tokens": estimated_tts_tokens,
            "research_queries": research_queries,
            "video_requests": minutes,
        },
    }
