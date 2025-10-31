from __future__ import annotations

import base64
import os
from typing import Optional, Dict, Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services.llm_providers.main_image_generation import generate_image
from services.llm_providers.main_text_generation import llm_text_gen
from utils.logger_utils import get_service_logger


router = APIRouter(prefix="/api/images", tags=["images"])
logger = get_service_logger("api.images")


class ImageGenerateRequest(BaseModel):
    prompt: str
    negative_prompt: Optional[str] = None
    provider: Optional[str] = Field(None, pattern="^(gemini|huggingface|stability)$")
    model: Optional[str] = None
    width: Optional[int] = Field(default=1024, ge=64, le=2048)
    height: Optional[int] = Field(default=1024, ge=64, le=2048)
    guidance_scale: Optional[float] = None
    steps: Optional[int] = None
    seed: Optional[int] = None


class ImageGenerateResponse(BaseModel):
    success: bool = True
    image_base64: str
    width: int
    height: int
    provider: str
    model: Optional[str] = None
    seed: Optional[int] = None


@router.post("/generate", response_model=ImageGenerateResponse)
def generate(req: ImageGenerateRequest) -> ImageGenerateResponse:
    try:
        last_error: Optional[Exception] = None
        for attempt in range(2):  # simple single retry
            try:
                result = generate_image(
                    prompt=req.prompt,
                    options={
                        "negative_prompt": req.negative_prompt,
                        "provider": req.provider,
                        "model": req.model,
                        "width": req.width,
                        "height": req.height,
                        "guidance_scale": req.guidance_scale,
                        "steps": req.steps,
                        "seed": req.seed,
                    },
                )
                image_b64 = base64.b64encode(result.image_bytes).decode("utf-8")
                return ImageGenerateResponse(
                    image_base64=image_b64,
                    width=result.width,
                    height=result.height,
                    provider=result.provider,
                    model=result.model,
                    seed=result.seed,
                )
            except Exception as inner:
                last_error = inner
                logger.error(f"Image generation attempt {attempt+1} failed: {inner}")
                # On first failure, try provider auto-remap by clearing provider to let facade decide
                if attempt == 0 and req.provider:
                    req.provider = None
                    continue
                break
        raise last_error or RuntimeError("Unknown image generation error")
    except Exception as e:
        logger.error(f"Image generation failed: {e}")
        # Provide a clean, actionable message to the client
        raise HTTPException(
            status_code=500,
            detail="Image generation service is temporarily unavailable or the connection was reset. Please try again."
        )


class PromptSuggestion(BaseModel):
    prompt: str
    negative_prompt: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    overlay_text: Optional[str] = None


class ImagePromptSuggestRequest(BaseModel):
    provider: Optional[str] = Field(None, pattern="^(gemini|huggingface|stability)$")
    title: Optional[str] = None
    section: Optional[Dict[str, Any]] = None
    research: Optional[Dict[str, Any]] = None
    persona: Optional[Dict[str, Any]] = None
    include_overlay: Optional[bool] = True


class ImagePromptSuggestResponse(BaseModel):
    suggestions: list[PromptSuggestion]


@router.post("/suggest-prompts", response_model=ImagePromptSuggestResponse)
def suggest_prompts(req: ImagePromptSuggestRequest) -> ImagePromptSuggestResponse:
    try:
        provider = (req.provider or ("gemini" if (os.getenv("GPT_PROVIDER") or "").lower().startswith("gemini") else "huggingface")).lower()
        section = req.section or {}
        title = (req.title or section.get("heading") or "").strip()
        subheads = section.get("subheadings", []) or []
        key_points = section.get("key_points", []) or []
        keywords = section.get("keywords", []) or []
        if not keywords and req.research:
            keywords = (
                req.research.get("keywords", {}).get("primary_keywords")
                or req.research.get("keywords", {}).get("primary")
                or []
            )

        persona = req.persona or {}
        audience = persona.get("audience", "content creators and digital marketers")
        industry = persona.get("industry", req.research.get("domain") if req.research else "your industry")
        tone = persona.get("tone", "professional, trustworthy")

        schema = {
            "type": "object",
            "properties": {
                "suggestions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "prompt": {"type": "string"},
                            "negative_prompt": {"type": "string"},
                            "width": {"type": "number"},
                            "height": {"type": "number"},
                            "overlay_text": {"type": "string"},
                        },
                        "required": ["prompt"]
                    },
                    "minItems": 3,
                    "maxItems": 5
                }
            },
            "required": ["suggestions"]
        }

        system = (
            "You are an expert image prompt engineer for text-to-image models. "
            "Given blog section context, craft 3-5 hyper-personalized prompts optimized for the specified provider. "
            "Return STRICT JSON matching the provided schema, no extra text."
        )

        provider_guidance = {
            "huggingface": "Photorealistic Flux 1 Krea Dev; include camera/lighting cues (e.g., 50mm, f/2.8, rim light).",
            "gemini": "Editorial, brand-safe, crisp edges, balanced lighting; avoid artifacts.",
            "stability": "SDXL coherent details, sharp focus, cinematic contrast; readable text if present."
        }.get(provider, "")

        best_practices = (
            "Best Practices: one clear focal subject; clean, uncluttered background; rule-of-thirds or center-weighted composition; "
            "text-safe margins if overlay text is included; neutral lighting if unsure; realistic skin tones; avoid busy patterns; "
            "no brand logos or watermarks; no copyrighted characters; avoid low-res, blur, noise, banding, oversaturation, over-sharpening; "
            "ensure hands and text are coherent if present; prefer 1024px+ on shortest side for quality."
        )

        # Harvest a few concise facts from research if available
        facts: list[str] = []
        try:
            if req.research:
                # try common shapes used in research service
                top_stats = req.research.get("key_facts") or req.research.get("highlights") or []
                if isinstance(top_stats, list):
                    facts = [str(x) for x in top_stats[:3]]
                elif isinstance(top_stats, dict):
                    facts = [f"{k}: {v}" for k, v in list(top_stats.items())[:3]]
        except Exception:
            facts = []

        facts_line = ", ".join(facts) if facts else ""

        overlay_hint = "Include an on-image short title or fact if it improves communication; ensure clean, high-contrast safe area for text." if (req.include_overlay is None or req.include_overlay) else "Do not include on-image text."

        prompt = f"""
        Provider: {provider}
        Title: {title}
        Subheadings: {', '.join(subheads[:5])}
        Key Points: {', '.join(key_points[:5])}
        Keywords: {', '.join([str(k) for k in keywords[:8]])}
        Research Facts: {facts_line}
        Audience: {audience}
        Industry: {industry}
        Tone: {tone}

        Craft prompts that visually reflect this exact section (not generic blog topic). {provider_guidance}
        {best_practices}
        {overlay_hint}
        Include a suitable negative_prompt where helpful. Suggest width/height when relevant (e.g., 1024x1024 or 1920x1080).
        If including on-image text, return it in overlay_text (short: <= 8 words).
        """

        raw = llm_text_gen(prompt=prompt, system_prompt=system, json_struct=schema)
        data = raw if isinstance(raw, dict) else {}
        suggestions = data.get("suggestions") or []
        # basic fallback if provider returns string
        if not suggestions and isinstance(raw, str):
            suggestions = [{"prompt": raw}]

        return ImagePromptSuggestResponse(suggestions=[PromptSuggestion(**s) for s in suggestions])
    except Exception as e:
        logger.error(f"Prompt suggestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

