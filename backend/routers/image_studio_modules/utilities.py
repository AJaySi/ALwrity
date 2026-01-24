"""Utility operations API endpoints for Image Studio."""

from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException

from routers.image_studio_modules.models import (
    CompressImageRequest, CompressImageResponse, CompressBatchRequest,
    CompressBatchResponse, CompressionEstimateRequest, CompressionEstimateResponse,
    CompressionFormatsResponse, CompressionPresetsResponse,
    ConvertFormatRequest, ConvertFormatResponse, ConvertFormatBatchRequest,
    ConvertFormatBatchResponse, SupportedFormatsResponse, FormatRecommendationsResponse
)
from routers.image_studio_modules.utils import _require_user_id
from routers.image_studio_modules.dependencies import get_studio_manager

from services.image_studio import ImageStudioManager
from middleware.auth_middleware import get_current_user
from utils.logger_utils import get_service_logger

logger = get_service_logger("api.image_studio.utilities")
router = APIRouter()


# ====================
# COMPRESSION STUDIO ENDPOINTS
# ====================

@router.post("/compress", response_model=CompressImageResponse, summary="Compress an image")
async def compress_image(
    request: CompressImageRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    studio_manager: ImageStudioManager = Depends(get_studio_manager),
):
    """Compress an image with specified quality and format settings.

    Features:
    - Quality control (1-100)
    - Format conversion (JPEG, PNG, WebP)
    - Target size compression
    - Metadata stripping
    - Progressive JPEG support
    """
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
    try:
        formats = studio_manager.get_compression_formats()
        return CompressionFormatsResponse(formats=formats)
    except Exception as e:
        logger.error(f"[Compression Formats] ❌ Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to load compression formats")


@router.get("/compress/presets", response_model=CompressionPresetsResponse, summary="Get compression presets")
async def get_compression_presets(
    studio_manager: ImageStudioManager = Depends(get_studio_manager),
):
    """Get list of predefined compression presets."""
    try:
        presets = studio_manager.get_compression_presets()
        return CompressionPresetsResponse(presets=presets)
    except Exception as e:
        logger.error(f"[Compression Presets] ❌ Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to load compression presets")


# ====================
# FORMAT CONVERTER ENDPOINTS
# ====================

@router.post("/convert-format", response_model=ConvertFormatResponse, summary="Convert image format")
async def convert_format(
    request: ConvertFormatRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    studio_manager: ImageStudioManager = Depends(get_studio_manager),
):
    """Convert an image to a different format.

    Features:
    - Multi-format support (PNG, JPEG, WebP, GIF, BMP, TIFF)
    - Transparency preservation
    - Color space conversion
    - Metadata handling
    """
    try:
        user_id = _require_user_id(current_user, "format conversion")
        logger.info(f"[Format Converter] Request from user {user_id}: {request.target_format}")

        from services.image_studio.format_converter_service import FormatConversionRequest as ServiceRequest

        conversion_request = ServiceRequest(
            image_base64=request.image_base64,
            target_format=request.target_format,
            preserve_transparency=request.preserve_transparency,
            quality=request.quality,
            color_space=request.color_space,
            strip_metadata=request.strip_metadata,
            optimize=request.optimize,
            progressive=request.progressive,
        )

        result = await studio_manager.convert_format(conversion_request, user_id=user_id)

        return ConvertFormatResponse(
            success=result.success,
            image_base64=result.image_base64,
            original_format=result.original_format,
            target_format=result.target_format,
            original_size_kb=result.original_size_kb,
            converted_size_kb=result.converted_size_kb,
            width=result.width,
            height=result.height,
            transparency_preserved=result.transparency_preserved,
            metadata_preserved=result.metadata_preserved,
            color_space=result.color_space,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Format Converter] ❌ Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Format conversion failed: {e}")


@router.post("/convert-format/batch", response_model=ConvertFormatBatchResponse, summary="Convert multiple images")
async def convert_format_batch(
    request: ConvertFormatBatchRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    studio_manager: ImageStudioManager = Depends(get_studio_manager),
):
    """Convert multiple images to different formats."""
    try:
        user_id = _require_user_id(current_user, "batch format conversion")
        logger.info(f"[Format Converter] Batch request from user {user_id}: {len(request.images)} images")

        from services.image_studio.format_converter_service import FormatConversionRequest as ServiceRequest

        conversion_requests = [
            ServiceRequest(
                image_base64=img.image_base64,
                target_format=img.target_format,
                preserve_transparency=img.preserve_transparency,
                quality=img.quality,
                color_space=img.color_space,
                strip_metadata=img.strip_metadata,
                optimize=img.optimize,
                progressive=img.progressive,
            )
            for img in request.images
        ]

        results = await studio_manager.convert_format_batch(conversion_requests, user_id=user_id)

        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful

        return ConvertFormatBatchResponse(
            success=failed == 0,
            results=[
                ConvertFormatResponse(
                    success=r.success,
                    image_base64=r.image_base64,
                    original_format=r.original_format,
                    target_format=r.target_format,
                    original_size_kb=r.original_size_kb,
                    converted_size_kb=r.converted_size_kb,
                    width=r.width,
                    height=r.height,
                    transparency_preserved=r.transparency_preserved,
                    metadata_preserved=r.metadata_preserved,
                    color_space=r.color_space,
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
        logger.error(f"[Format Converter] ❌ Batch error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch format conversion failed: {e}")


@router.get("/convert-format/supported", response_model=SupportedFormatsResponse, summary="Get supported formats")
async def get_supported_formats(
    studio_manager: ImageStudioManager = Depends(get_studio_manager),
):
    """Get list of supported conversion formats with their capabilities."""
    try:
        formats = studio_manager.get_supported_formats()
        return SupportedFormatsResponse(formats=formats)
    except Exception as e:
        logger.error(f"[Supported Formats] ❌ Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to load supported formats")


@router.get("/convert-format/recommendations", response_model=FormatRecommendationsResponse, summary="Get format recommendations")
async def get_format_recommendations(
    source_format: str,
    studio_manager: ImageStudioManager = Depends(get_studio_manager),
):
    """Get format recommendations based on source format."""
    try:
        recommendations = studio_manager.get_format_recommendations(source_format)
        return FormatRecommendationsResponse(recommendations=recommendations)
    except Exception as e:
        logger.error(f"[Format Recommendations] ❌ Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to load format recommendations")


# ====================
# HEALTH CHECK
# ====================

@router.get("/health", summary="Health Check")
async def health_check():
    """Health check endpoint for Image Studio.

    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "service": "image_studio",
        "version": "1.0.0",
        "modules": {
            "generation": "active",
            "editing": "active",
            "advanced": "active",
            "utilities": "active",
        },
    }