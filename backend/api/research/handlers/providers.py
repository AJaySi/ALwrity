"""
Provider Status Handler

Handles provider availability and status endpoints.
"""

from fastapi import APIRouter
from loguru import logger

from services.research.core import ResearchEngine
from ..models import ProviderStatusResponse

router = APIRouter()


@router.get("/providers/status", response_model=ProviderStatusResponse)
async def get_provider_status():
    """
    Get status of available research providers.
    
    Returns availability and priority of Exa, Tavily, and Google providers.
    """
    try:
        engine = ResearchEngine()
        return engine.get_provider_status()
    except Exception as e:
        logger.error(f"[Provider Status] Failed: {e}")
        # Return default status on error
        return ProviderStatusResponse(
            exa={"available": False, "error": str(e)},
            tavily={"available": False, "error": str(e)},
            google={"available": False, "error": str(e)},
        )
