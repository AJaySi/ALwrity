"""
Link Search API — Internal & external link discovery and reword-with-links.

Endpoints:
  POST /api/links/search  — Search for internal or external links via Exa
  POST /api/links/reword  — Reword text to naturally incorporate selected links
  GET  /api/links/health   — Health check
"""

from typing import Dict, Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from loguru import logger

from middleware.auth_middleware import get_current_user
from api.story_writer.utils.auth import require_authenticated_user
from services.link_search_service import get_link_search_service


router = APIRouter(prefix="/api/links", tags=["Links"])


class LinkSearchRequest(BaseModel):
    """Request for link search (internal or external)."""
    query: str = Field(..., description="Search query (typically section heading or topic)")
    link_type: str = Field(
        ...,
        description="Type of links: 'internal' or 'external'",
    )
    site_url: Optional[str] = Field(
        default=None,
        description="User's website URL (required for internal links, optional for external to exclude own domain)",
    )
    num_results: int = Field(default=5, description="Number of results to return", ge=1, le=15)


class LinkSearchResult(BaseModel):
    """A single link search result."""
    title: str = ""
    url: str = ""
    text: str = ""
    publishedDate: str = ""
    author: str = ""
    score: float = 0.5


class LinkSearchResponse(BaseModel):
    """Response for link search."""
    results: List[LinkSearchResult] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class RewordRequest(BaseModel):
    """Request to reword text with selected links."""
    section_text: str = Field(..., description="Full section text")
    selected_text: Optional[str] = Field(
        default=None,
        description="If provided, only reword this portion of the text",
    )
    section_heading: Optional[str] = Field(default=None, description="Section heading for context")
    links: List[Dict[str, str]] = Field(
        ...,
        description="List of {'url': str, 'title': str} dicts to incorporate",
    )


class RewordResponse(BaseModel):
    """Response for reword-with-links."""
    reworded_text: str = ""
    warnings: List[str] = Field(default_factory=list)


@router.post("/search", response_model=LinkSearchResponse)
async def search_links(
    request: LinkSearchRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Search for internal or external links using Exa."""
    user_id = require_authenticated_user(current_user)

    if request.link_type not in ("internal", "external"):
        raise HTTPException(
            status_code=400,
            detail="link_type must be 'internal' or 'external'",
        )

    if request.link_type == "internal" and not request.site_url:
        raise HTTPException(
            status_code=400,
            detail="site_url is required for internal link search",
        )

    if len(request.query) > 500:
        raise HTTPException(
            status_code=400,
            detail="Query must be 500 characters or less",
        )

    service = get_link_search_service(user_id=user_id)

    try:
        if request.link_type == "internal":
            logger.info(f"[Links] Internal search: query='{request.query[:50]}', site='{request.site_url}', user={user_id}")
            result = await service.search_internal(
                query=request.query,
                site_url=request.site_url,
                user_id=user_id,
                num_results=request.num_results,
            )
        else:
            logger.info(f"[Links] External search: query='{request.query[:50]}', user={user_id}")
            result = await service.search_external(
                query=request.query,
                site_url=request.site_url,
                user_id=user_id,
                num_results=request.num_results,
            )

        return LinkSearchResponse(
            results=[LinkSearchResult(**r) for r in result.get("results", [])],
            warnings=result.get("warnings", []),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Links] Search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Link search failed: {str(e)}")


@router.post("/reword", response_model=RewordResponse)
async def reword_with_links(
    request: RewordRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Reword text to naturally incorporate selected links."""
    user_id = require_authenticated_user(current_user)

    if not request.links:
        raise HTTPException(
            status_code=400,
            detail="At least one link must be provided",
        )

    # Validate each link has a url
    for i, link in enumerate(request.links):
        if not link.get("url"):
            raise HTTPException(
                status_code=400,
                detail=f"Link at index {i} is missing a 'url' field",
            )

    if len(request.section_text) > 10000:
        raise HTTPException(
            status_code=400,
            detail="section_text must be 10000 characters or less",
        )

    service = get_link_search_service(user_id=user_id)

    try:
        logger.info(f"[Links] Reword: heading='{request.section_heading}', links={len(request.links)}, user={user_id}")
        result = service.reword_with_links(
            section_text=request.section_text,
            links=request.links,
            section_heading=request.section_heading,
            selected_text=request.selected_text,
            user_id=user_id,
        )

        return RewordResponse(
            reworded_text=result.get("reworded_text", request.section_text),
            warnings=result.get("warnings", []),
        )

    except Exception as e:
        logger.error(f"[Links] Reword failed: {e}")
        raise HTTPException(status_code=500, detail=f"Reword failed: {str(e)}")


@router.get("/health")
async def links_health():
    """Health check for Links service."""
    return {"status": "ok", "service": "links"}