"""Health check endpoint."""

from fastapi import APIRouter

router = APIRouter(tags=["image-studio"])


@router.get("/health", summary="Health Check")
async def health_check():
    """Health check endpoint for Image Studio."""
    return {
        "status": "healthy",
        "service": "image_studio",
        "version": "1.0.0",
        "modules": {
            "create_studio": "available",
            "templates": "available",
            "providers": "available",
            "compression": "available",
        }
    }
