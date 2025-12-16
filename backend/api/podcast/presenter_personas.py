"""
Podcast Presenter Personas

Lightweight, podcast-specific presenter persona presets used to steer avatar generation.

Design goals:
- Market-fit + style consistency without asking end-users to choose sensitive traits.
- Deterministic persona selection using analysis hints (audience/content type/keywords).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, List


@dataclass(frozen=True)
class PresenterPersona:
    id: str
    label: str
    target_market: str  # e.g. "global", "us_canada", "uk_eu", "india", "latam"
    style: str  # e.g. "corporate", "tech_modern", "creator"
    prompt: str  # prompt fragment to inject


# NOTE: Avoid encoding/guessing ethnicity. Keep personas about market-fit + style.
PERSONAS: Dict[str, PresenterPersona] = {
    "global_corporate": PresenterPersona(
        id="global_corporate",
        label="Global — Corporate Host",
        target_market="global",
        style="corporate",
        prompt=(
            "professional podcast presenter, business professional attire (white shirt and light gray blazer), "
            "confident, friendly, camera-ready, neutral background, studio lighting"
        ),
    ),
    "global_tech_modern": PresenterPersona(
        id="global_tech_modern",
        label="Global — Tech Modern Host",
        target_market="global",
        style="tech_modern",
        prompt=(
            "modern professional podcast presenter, contemporary tech-forward style, "
            "clean minimal studio background, soft studio lighting, friendly and energetic expression"
        ),
    ),
    "global_news_anchor": PresenterPersona(
        id="global_news_anchor",
        label="Global — News Anchor",
        target_market="global",
        style="news_anchor",
        prompt=(
            "professional news-style presenter, polished on-camera appearance, "
            "formal attire, authoritative yet approachable expression, studio lighting, neutral background"
        ),
    ),
    "india_corporate": PresenterPersona(
        id="india_corporate",
        label="India — Corporate Host",
        target_market="india",
        style="corporate",
        prompt=(
            "professional podcast presenter for the Indian market, business professional attire, "
            "polished and confident on-camera presence, clean studio background, soft studio lighting"
        ),
    ),
    "us_canada_creator": PresenterPersona(
        id="us_canada_creator",
        label="US/Canada — Creator Host",
        target_market="us_canada",
        style="creator",
        prompt=(
            "professional podcast creator host, business casual style, approachable and conversational expression, "
            "clean studio background, soft studio lighting"
        ),
    ),
}


def get_persona(persona_id: Optional[str]) -> Optional[PresenterPersona]:
    if not persona_id:
        return None
    return PERSONAS.get(persona_id)


def list_personas() -> List[PresenterPersona]:
    return list(PERSONAS.values())


def choose_persona_id(
    audience: Optional[str] = None,
    content_type: Optional[str] = None,
    top_keywords: Optional[List[str]] = None,
) -> str:
    """
    Choose a persona id using non-sensitive heuristics from analysis.

    - Uses explicit market hints if present (e.g. "India", "US", "UK", etc.)
    - Uses content_type / keywords to pick a style
    - Falls back to global corporate
    """
    audience_l = (audience or "").lower()
    content_l = (content_type or "").lower()
    keywords_l = [k.lower() for k in (top_keywords or [])]

    # Market hints (explicit only)
    if any(x in audience_l for x in ["india", "indian"]):
        market = "india"
    elif any(x in audience_l for x in ["us", "usa", "united states", "canada", "north america"]):
        market = "us_canada"
    elif any(x in audience_l for x in ["uk", "united kingdom", "europe", "eu", "european"]):
        market = "uk_eu"
    elif any(x in audience_l for x in ["latam", "latin america", "south america"]):
        market = "latam"
    else:
        market = "global"

    # Style hints
    style = "corporate"
    if "news" in content_l or "analysis" in content_l:
        style = "news_anchor"
    if any(x in content_l for x in ["tech", "technology", "ai", "software"]) or any(
        kw in ["ai", "technology", "tech", "software"] for kw in keywords_l
    ):
        style = "tech_modern"
    if any(x in content_l for x in ["casual", "creator", "conversational"]) or any(
        kw in ["creator", "youtube", "tiktok", "instagram"] for kw in keywords_l
    ):
        style = "creator"

    # Map market+style to a concrete persona id
    if market == "india" and style == "corporate":
        return "india_corporate"
    if market == "us_canada" and style == "creator":
        return "us_canada_creator"
    if style == "news_anchor":
        return "global_news_anchor"
    if style == "tech_modern":
        return "global_tech_modern"
    return "global_corporate"


