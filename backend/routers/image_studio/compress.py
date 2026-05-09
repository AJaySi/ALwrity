"""Compression Studio endpoints."""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException

from .models import (
    CompressImageRequest, CompressImageResponse,
    CompressBatchRequest, CompressBatchResponse,
    CompressionEstimateRequest, CompressionEstimateResponse,
    CompressionFormatsResponse, CompressionPresetsResponse,
)
from .deps import get_studio_manager, _require_user_id
from services.image_studio import ImageStudioManager
from middleware.auth_middleware import get_current_user
from utils.logger_utils import get_service_logger

logger = get_service_logger("api.image_studio")
router = APIRouter(tags=["image-studio"])


@router.post("/compress", response_model=CompressImageResponse, summary="Compress an image")
async def compress_image(
    request: CompressImageRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    studio_manager: ImageStudioManager = Depends(get_studio_manager),
):
    """Compress an image with specified quality and format settings."""
    try:
        user_id = _require_user_id(current_user, "image compression")
        logger.info(f"[Compression] Request from user {user_id}: format={request.format}, quality={request.quality}")

        from services.image_studio.compression_service import CompressionRequest as ServiceRequest

        compression_request = ServiceRequest(
            image_base64=request.image_base64,
            quality=request.quality,
            format=request.format,
            target_size_kb=request.target_size_kb,
            strip_metadata=request.strip_metadata,
            progressive=request.progressive,
            optimize=request.optimize,
        )

        result = await studio_manager.compress_image(compression_request, user_id=user_id)

        return CompressImageResponse(
            success=result.success,
            image_base64=result.image_base64,
            original_size_kb=result.original_size_kb,
            compressed_size_kb=result.compressed_size_kb,
            compression_ratio=result.compression_ratio,
            format=result.format,
            width=result.width,
            height=result.height,
            quality_used=result.quality_used,
            metadata_stripped=result.metadata_stripped,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Compression] ❌ Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Image compression failed: {e}")


@router.post("/compress/batch", response_model=CompressBatchResponse, summary="Compress multiple images")
async def compress_batch(
    request: CompressBatchRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    studio_manager: ImageStudioManager = Depends(get_studio_manager),
):
    """Compress multiple images with the same or individual settings."""
    try:
        user_id = _require_user_id(current_user, "batch compression")
        logger.info(f"[Compression] Batch request from user {user_id}: {len(request.images)} images")

        from services.image_studio.compression_service import CompressionRequest as ServiceRequest

        compression_requests = [
            ServiceRequest(
                image_base64=img.image_base64,
                quality=img.quality,
                format=img.format,
                target_size_kb=img.target_size_kb,
                strip_metadata=img.strip_metadata,
                progressive=img.progressive,
                optimize=img.optimize,
            )
            for img in request.images
        ]

        results = await studio_manager.compress_batch(compression_requests, user_id=user_id)

        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful

        return CompressBatchResponse(
            success=failed == 0,
            results=[
                CompressImageResponse(
                    success=r.success,
                    image_base64=r.image_base64,
                    original_size_kb=r.original_size_kb,
                    compressed_size_kb=r.compressed_size_kb,
                    compression_ratio=r.compression_ratio,
                    format=r.format,
                    width=r.width,
                    height=r.height,
                    quality_used=r.quality_used,
                    metadata_stripped=r.metadata_stripped,
                )
                for r in results
            ],
            total_images=len(results),
            successful=successful,
            failed=failed,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Compression] ❌ Batch error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch compression failed: {e}")


@router.post("/compress/estimate", response_model=CompressionEstimateResponse, summary="Estimate compression results")
async def estimate_compression(
    request: CompressionEstimateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    studio_manager: ImageStudioManager = Depends(get_studio_manager),
):
    """Estimate compression results without actually compressing the image."""
    try:
        result = await studio_manager.estimate_compression(
            request.image_base64,
            request.format,
            request.quality,
        )
        return CompressionEstimateResponse(**result)
    except Exception as e:
        logger.error(f"[Compression] ❌ Estimate error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Compression estimation failed: {e}")


@router.get("/compress/formats", response_model=CompressionFormatsResponse, summary="Get supported compression formats")
async def get_compression_formats(
    studio_manager: ImageStudioManager = Depends(get_studio_manager),
):
    """Get list of supported compression formats with their capabilities."""
    formats = studio_manager.get_compression_formats()
    return CompressionFormatsResponse(formats=formats)


@router.get("/compress/presets", response_model=CompressionPresetsResponse, summary="Get compression presets")
async def get_compression_presets(
    studio_manager: ImageStudioManager = Depends(get_studio_manager),
):
    """Get predefined compression presets for common use cases."""
    presets = studio_manager.get_compression_presets()
    return CompressionPresetsResponse(presets=presets)
