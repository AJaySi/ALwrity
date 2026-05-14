"""
Category Research Handlers

Research endpoints using Tavily or Exa for category-based topic discovery.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from loguru import logger
from types import SimpleNamespace
from sqlalchemy import text

from middleware.auth_middleware import get_current_user
from api.story_writer.utils.auth import require_authenticated_user
from services.research.tavily_service import TavilyService
from services.subscription import PricingService
from models.subscription_models import APIProvider

router = APIRouter(prefix="/research", tags=["Podcast Category Research"])

CATEGORY_PROVIDER_MAP = {
    "news": "tavily",
    "finance": "tavily",
    "research-paper": "exa",
    "personal-site": "exa",
}

EXA_CATEGORY_MAP = {
    "research-paper": "research paper",
    "personal-site": "personal site",
}


def _preflight_check(user_id: str, provider: APIProvider, provider_name: str):
    """Check subscription limits before making a research API call."""
    from services.database import get_session_for_user

    db = get_session_for_user(user_id)
    if not db:
        return
    try:
        pricing_service = PricingService(db)
        can_proceed, message, usage_info = pricing_service.check_usage_limits(
            user_id=user_id,
            provider=provider,
            tokens_requested=0,
            actual_provider_name=provider_name,
        )
        if not can_proceed:
            raise HTTPException(status_code=429, detail={
                'error': message, 'message': message,
                'provider': provider_name, 'usage_info': usage_info or {}
            })
    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f"[CategoryResearch] Preflight check failed for {provider_name}: {e}")
    finally:
        db.close()


def _track_research_usage(user_id: str, provider_name: str, cost: float, calls_column: str, cost_column: str):
    """Track research API usage after successful call."""
    from services.database import get_session_for_user

    db = get_session_for_user(user_id)
    if not db:
        logger.warning(f"[CategoryResearch] Could not get DB session for user {user_id}")
        return
    try:
        pricing_service = PricingService(db)
        current_period = pricing_service.get_current_billing_period(user_id)

        update_query = text(f"""
            UPDATE usage_summaries 
            SET {calls_column} = COALESCE({calls_column}, 0) + 1,
                {cost_column} = COALESCE({cost_column}, 0) + :cost,
                total_calls = COALESCE(total_calls, 0) + 1,
                total_cost = COALESCE(total_cost, 0) + :cost
            WHERE user_id = :user_id AND billing_period = :period
        """)
        db.execute(update_query, {
            'cost': cost,
            'user_id': user_id,
            'period': current_period,
        })
        db.commit()
        logger.info(f"[CategoryResearch] Tracked {provider_name} usage: user={user_id}, cost=${cost}")

        # Clear dashboard cache so header stats update immediately
        try:
            from api.subscription.cache import clear_dashboard_cache
            clear_dashboard_cache(user_id)
        except Exception as cache_err:
            logger.warning(f"[CategoryResearch] Failed to clear dashboard cache: {cache_err}")
    except Exception as e:
        logger.error(f"[CategoryResearch] Failed to track {provider_name} usage: {e}")
        db.rollback()
    finally:
        db.close()


class CategoryResearchRequest(BaseModel):
    category: str
    keyword: Optional[str] = None
    max_results: Optional[int] = 8
    website_url: Optional[str] = None


class CategoryTopic(BaseModel):
    title: str
    url: str
    snippet: str
    score: float
    favicon: Optional[str] = None


class CategoryResearchResponse(BaseModel):
    success: bool
    category: str
    provider: str
    topics: List[CategoryTopic]
    query: Optional[str] = None
    error: Optional[str] = None


def _normalize_tavily_results(results: List[Dict]) -> List[CategoryTopic]:
    topics = []
    for item in results:
        topics.append(CategoryTopic(
            title=item.get("title", ""),
            url=item.get("url", ""),
            snippet=item.get("content", ""),
            score=item.get("score", 0.0),
            favicon=item.get("favicon"),
        ))
    return topics


def _normalize_exa_results(results: List[Dict], query: str) -> List[CategoryTopic]:
    topics = []
    for idx, item in enumerate(results):
        score = 1.0 - (idx * 0.1)
        topics.append(CategoryTopic(
            title=item.get("title", "") or f"Result {idx + 1}",
            url=item.get("url", ""),
            snippet=item.get("summary", "") or item.get("text", "") or "",
            score=max(0.5, score),
            favicon=None,
        ))
    return topics


async def _search_tavily(category: str, keyword: str, max_results: int, user_id: str) -> CategoryResearchResponse:
    logger.info(f"[CategoryResearch] Using Tavily for category={category}, keyword={keyword}")

    # Preflight subscription check
    _preflight_check(user_id, APIProvider.TAVILY, "tavily")

    try:
        tavily = TavilyService()
        result = await tavily.search(
            query=keyword,
            topic=category,
            search_depth="basic",
            max_results=max_results,
            include_favicon=True,
        )

        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Tavily search failed")
            )

        topics = _normalize_tavily_results(result.get("results", []))
        logger.info(f"[CategoryResearch] Tavily found {len(topics)} topics")

        # Track usage
        cost = 0.001  # basic search = 1 credit
        _track_research_usage(user_id, "tavily", cost, "tavily_calls", "tavily_cost")

        return CategoryResearchResponse(
            success=True,
            category=category,
            provider="tavily",
            topics=topics,
            query=keyword,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[CategoryResearch] Tavily error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


async def _search_exa(category: str, keyword: str, max_results: int, user_id: str, website_url: Optional[str] = None) -> CategoryResearchResponse:
    exa_category = EXA_CATEGORY_MAP.get(category, category)
    
    logger.info(f"[CategoryResearch] Exa: category={category}, exa_category={exa_category}, keyword={keyword}, website_url={website_url}")

    try:
        # Import exa directly for more control
        import os
        from urllib.parse import urlparse
        exa_api_key = os.getenv("EXA_API_KEY")
        if not exa_api_key:
            raise HTTPException(status_code=500, detail="EXA_API_KEY not configured")
        
        from exa_py import Exa
        exa = Exa(exa_api_key)
        logger.info(f"[CategoryResearch] Exa client initialized")

        # Preflight subscription check
        _preflight_check(user_id, APIProvider.EXA, "exa")
        
        # Build search parameters
        search_params = {
            "num_results": max_results,
            "category": exa_category,
        }
        
        # For personal-site, extract domain from URL if provided
        include_domains = None
        if category == "personal-site" and website_url:
            try:
                parsed = urlparse(website_url)
                if parsed.netloc:
                    include_domains = [parsed.netloc]
                    logger.info(f"[CategoryResearch] Personal site - limiting to domain: {parsed.netloc}")
                elif parsed.path and "." in parsed.path:
                    # Could be domain without protocol
                    include_domains = [parsed.path]
                    logger.info(f"[CategoryResearch] Personal site - using as domain: {parsed.path}")
            except Exception as url_err:
                logger.warning(f"[CategoryResearch] Failed to parse website_url: {url_err}")
        
        logger.info(f"[CategoryResearch] Calling Exa with params: {search_params}, include_domains={include_domains}")
        
        # Make the search call
        results = exa.search_and_contents(
            query=keyword,
            type="auto" if category != "personal-site" else "neural",
            num_results=max_results,
            category=exa_category,
            text=True,
            summary=True,
            include_domains=include_domains,
        )
        
        logger.info(f"[CategoryResearch] Exa search completed, got results")
        
        # Transform results to our format
        topics = []
        if results and hasattr(results, 'results'):
            for item in results.results:
                title = getattr(item, 'title', 'Untitled')
                url = getattr(item, 'url', '')
                snippet = getattr(item, 'summary', '') or getattr(item, 'text', '') or ''
                score = 0.8  # Default score for Exa results
                
                topics.append(CategoryTopic(
                    title=title,
                    url=url,
                    snippet=snippet[:300] if snippet else '',
                    score=score,
                    favicon=None,
                ))
        
        logger.info(f"[CategoryResearch] Exa found {len(topics)} topics")

        # Track usage
        cost = 0.005  # Default Exa cost for 1-25 results
        _track_research_usage(user_id, "exa", cost, "exa_calls", "exa_cost")

        return CategoryResearchResponse(
            success=True,
            category=category,
            provider="exa",
            topics=topics,
            query=keyword,
        )

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        logger.error(f"[CategoryResearch] Exa error: {type(e).__name__}: {e}")
        logger.error(f"[CategoryResearch] Stack: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Exa search failed: {str(e)}")


@router.post("/tavily-category", response_model=CategoryResearchResponse)
async def research_by_category(
    request: CategoryResearchRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Research topics by category using Tavily or Exa.
    
    Categories:
    - news, finance: Uses Tavily
    - research-paper, personal-site: Uses Exa
    """
    user_id = require_authenticated_user(current_user)
    category = request.category.lower()
    valid_categories = list(CATEGORY_PROVIDER_MAP.keys())
    
    logger.info(f"[CategoryResearch] Full request payload: category={request.category}, keyword={request.keyword}, website_url={request.website_url}")
    
    if category not in valid_categories:
        logger.error(f"[CategoryResearch] Invalid category: {category}, valid: {valid_categories}")
        raise HTTPException(
            status_code=400,
            detail=f"Category must be one of: {', '.join(valid_categories)}"
        )

    keyword = request.keyword or category
    max_results = min(max(request.max_results or 8, 5), 10)
    website_url = request.website_url

    logger.info(f"[CategoryResearch] Processing: category={category}, keyword={keyword}, max_results={max_results}, website_url={website_url}")

    provider = CATEGORY_PROVIDER_MAP.get(category, "tavily")
    logger.info(f"[CategoryResearch] Selected provider: {provider} for category: {category}")

    try:
        if provider == "tavily":
            return await _search_tavily(category, keyword, max_results, user_id)
        elif provider == "exa":
            return await _search_exa(category, keyword, max_results, user_id, website_url)
        else:
            raise HTTPException(status_code=500, detail="Unknown provider")
    except Exception as e:
        logger.error(f"[CategoryResearch] Outer error: {type(e).__name__}: {e}", exc_info=True)
        raise