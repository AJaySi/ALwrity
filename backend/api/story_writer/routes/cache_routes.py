from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from middleware.auth_middleware import get_current_user

from ..cache_manager import cache_manager
from ..utils.auth import require_authenticated_user


router = APIRouter()


@router.get("/cache/stats")
async def get_cache_stats(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """Get cache statistics."""
    try:
        require_authenticated_user(current_user)
        stats = cache_manager.get_cache_stats()
        return {"success": True, "stats": stats}
    except Exception as exc:
        logger.error(f"[StoryWriter] Failed to get cache stats: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/cache/clear")
async def clear_cache(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """Clear the story generation cache."""
    try:
        require_authenticated_user(current_user)
        result = cache_manager.clear_cache()
        return {"success": True, **result}
    except Exception as exc:
        logger.error(f"[StoryWriter] Failed to clear cache: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


