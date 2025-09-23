"""
Brainstorming endpoints for generating Google search prompts and running a
single grounded search to surface topic ideas. Built for reusability across
editors. Uses the existing Gemini provider modules.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from loguru import logger

from services.llm_providers.gemini_provider import gemini_structured_json_response

try:
    from services.llm_providers.gemini_grounded_provider import GeminiGroundedProvider
    GROUNDED_AVAILABLE = True
except Exception:
    GROUNDED_AVAILABLE = False


router = APIRouter(prefix="/api/brainstorm", tags=["Brainstorming"])


class PersonaPayload(BaseModel):
    persona_name: Optional[str] = None
    archetype: Optional[str] = None
    core_belief: Optional[str] = None
    tonal_range: Optional[Dict[str, Any]] = None
    linguistic_fingerprint: Optional[Dict[str, Any]] = None


class PlatformPersonaPayload(BaseModel):
    content_format_rules: Optional[Dict[str, Any]] = None
    engagement_patterns: Optional[Dict[str, Any]] = None
    content_types: Optional[Dict[str, Any]] = None
    tonal_range: Optional[Dict[str, Any]] = None


class PromptRequest(BaseModel):
    seed: str = Field(..., description="Idea seed provided by end user")
    persona: Optional[PersonaPayload] = None
    platformPersona: Optional[PlatformPersonaPayload] = None
    count: int = Field(5, ge=3, le=10, description="Number of prompts to generate (default 5)")


class PromptResponse(BaseModel):
    prompts: List[str]


@router.post("/prompts", response_model=PromptResponse)
async def generate_prompts(req: PromptRequest) -> PromptResponse:
    """Generate N high-signal Google search prompts using Gemini structured output."""
    try:
        persona_line = ""
        if req.persona:
            parts = []
            if req.persona.persona_name:
                parts.append(req.persona.persona_name)
            if req.persona.archetype:
                parts.append(f"({req.persona.archetype})")
            persona_line = " ".join(parts)

        platform_hints = []
        if req.platformPersona and req.platformPersona.content_format_rules:
            limit = req.platformPersona.content_format_rules.get("character_limit")
            if limit:
                platform_hints.append(f"respect LinkedIn character limit {limit}")

        sys_prompt = (
            "You are an expert LinkedIn strategist who crafts precise Google search prompts "
            "to ideate content topics. Follow Google grounding best-practices: be specific, "
            "time-bound (2024-2025), include entities, and prefer intent-rich phrasing."
        )

        prompt = f"""
Seed: {req.seed}
Persona: {persona_line or 'N/A'}
Guidelines:
- Generate {req.count} distinct, high-signal Google search prompts.
- Each prompt should include concrete entities (companies, tools, frameworks) when possible.
- Prefer phrasing that yields recent, authoritative sources.
- Avoid generic phrasing ("latest trends") unless combined with concrete qualifiers.
- Optimize for LinkedIn thought leadership and practicality.
{('Platform hints: ' + ', '.join(platform_hints)) if platform_hints else ''}

Return only the list of prompts.
""".strip()

        schema = {
            "type": "object",
            "properties": {
                "prompts": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            }
        }

        result = gemini_structured_json_response(
            prompt=prompt,
            schema=schema,
            temperature=0.2,
            top_p=0.9,
            top_k=40,
            max_tokens=2048,
            system_prompt=sys_prompt,
        )

        prompts = []
        if isinstance(result, dict) and isinstance(result.get("prompts"), list):
            prompts = [str(p).strip() for p in result["prompts"] if str(p).strip()]

        if not prompts:
            # Minimal fallback: derive simple variations
            base = req.seed.strip()
            prompts = [
                f"Recent data-backed insights about {base}",
                f"Case studies and benchmarks on {base}",
                f"Implementation playbooks for {base}",
                f"Common pitfalls and solutions in {base}",
                f"Industry leader perspectives on {base}",
            ]

        return PromptResponse(prompts=prompts[: req.count])
    except Exception as e:
        logger.error(f"Error generating brainstorm prompts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class SearchRequest(BaseModel):
    prompt: str = Field(..., description="Selected search prompt to run with grounding")
    max_tokens: int = Field(1024, ge=256, le=4096)


class SearchResult(BaseModel):
    title: Optional[str] = None
    url: Optional[str] = None
    snippet: Optional[str] = None


class SearchResponse(BaseModel):
    results: List[SearchResult] = []


@router.post("/search", response_model=SearchResponse)
async def run_grounded_search(req: SearchRequest) -> SearchResponse:
    """Run a single grounded Google search via GeminiGroundedProvider and return normalized results."""
    if not GROUNDED_AVAILABLE:
        raise HTTPException(status_code=503, detail="Grounded provider not available")

    try:
        provider = GeminiGroundedProvider()
        resp = await provider.generate_grounded_content(
            prompt=req.prompt,
            content_type="linkedin_post",
            temperature=0.3,
            max_tokens=req.max_tokens,
        )

        items: List[SearchResult] = []
        # Normalize 'sources' if present
        for s in (resp.get("sources") or []):
            items.append(SearchResult(
                title=s.get("title") or "Source",
                url=s.get("url") or s.get("link"),
                snippet=s.get("content") or s.get("snippet")
            ))

        # Provide minimal fallback if no structured sources are returned
        if not items and resp.get("content"):
            items.append(SearchResult(title="Generated overview", url=None, snippet=resp.get("content")[:400]))

        return SearchResponse(results=items[:10])
    except Exception as e:
        logger.error(f"Error in grounded search: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class IdeasRequest(BaseModel):
    seed: str
    persona: Optional[PersonaPayload] = None
    platformPersona: Optional[PlatformPersonaPayload] = None
    results: List[SearchResult] = []
    count: int = 5


class IdeaItem(BaseModel):
    prompt: str
    rationale: Optional[str] = None


class IdeasResponse(BaseModel):
    ideas: List[IdeaItem]


@router.post("/ideas", response_model=IdeasResponse)
async def generate_brainstorm_ideas(req: IdeasRequest) -> IdeasResponse:
    """
    Create brainstorm ideas by combining persona, seed, and Google search results.
    Uses gemini_structured_json_response for consistent output.
    """
    try:
        # Build compact search context
        top_results = req.results[:5]
        sources_block = "\n".join(
            [
                f"- {r.title or 'Source'} | {r.url or ''} | {r.snippet or ''}"
                for r in top_results
            ]
        ) or "(no sources)"

        persona_block = ""
        if req.persona:
            persona_block = (
                f"Persona: {req.persona.persona_name or ''} {('(' + req.persona.archetype + ')') if req.persona.archetype else ''}\n"
            )

        platform_block = ""
        if req.platformPersona and req.platformPersona.content_format_rules:
            limit = req.platformPersona.content_format_rules.get("character_limit")
            platform_block = f"LinkedIn character limit: {limit}" if limit else ""

        sys_prompt = (
            "You are an enterprise-grade LinkedIn strategist. Generate specific, non-generic "
            "brainstorm prompts suitable for LinkedIn posts or carousels. Use the provided web "
            "sources to ground ideas and the persona to align tone and style."
        )

        prompt = f"""
SEED IDEA: {req.seed}
{persona_block}
{platform_block}

RECENT WEB SOURCES (top {len(top_results)}):
{sources_block}

TASK:
- Propose {req.count} LinkedIn-ready brainstorm prompts tailored to the persona and grounded in the sources.
- Each prompt should be specific and actionable for 2024–2025.
- Prefer thought-leadership angles, contrarian takes with evidence, or practical playbooks.
- Avoid generic phrases like "latest trends" unless qualified by entities.

Return JSON with an array named ideas where each item has:
- prompt: the exact text the user can use to generate a post
- rationale: 1–2 sentence why this works for the audience/persona
""".strip()

        schema = {
            "type": "object",
            "properties": {
                "ideas": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "prompt": {"type": "string"},
                            "rationale": {"type": "string"},
                        },
                    },
                }
            },
        }

        result = gemini_structured_json_response(
            prompt=prompt,
            schema=schema,
            temperature=0.2,
            top_p=0.9,
            top_k=40,
            max_tokens=2048,
            system_prompt=sys_prompt,
        )

        ideas: List[IdeaItem] = []
        if isinstance(result, dict) and isinstance(result.get("ideas"), list):
            for item in result["ideas"]:
                if isinstance(item, dict) and item.get("prompt"):
                    ideas.append(IdeaItem(prompt=item["prompt"], rationale=item.get("rationale")))

        if not ideas:
            # Fallback basic ideas from seed if model returns nothing
            ideas = [
                IdeaItem(prompt=f"Explain why {req.seed} matters now with 2 recent stats", rationale="Timely and data-backed."),
                IdeaItem(prompt=f"Common pitfalls in {req.seed} and how to avoid them", rationale="Actionable and experience-based."),
                IdeaItem(prompt=f"A step-by-step playbook to implement {req.seed}", rationale="Practical value."),
                IdeaItem(prompt=f"Case study: measurable impact of {req.seed}", rationale="Story + ROI."),
                IdeaItem(prompt=f"Contrarian take: what most get wrong about {req.seed}", rationale="Thought leadership.")
            ]

        return IdeasResponse(ideas=ideas[: req.count])
    except Exception as e:
        logger.error(f"Error generating brainstorm ideas: {e}")
        raise HTTPException(status_code=500, detail=str(e))


