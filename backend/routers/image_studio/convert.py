"""Format Converter endpoints."""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query

from .models import (
    ConvertFormatRequest, ConvertFormatResponse,
    ConvertFormatBatchRequest, ConvertFormatBatchResponse,
    SupportedFormatsResponse, FormatRecommendationsResponse,
)
from .deps import get_studio_manager, _require_user_id
from services.image_studio import ImageStudioManager
from middleware.auth_middleware import get_current_user
from utils.logger_utils import get_service_logger

logger = get_service_logger("api.image_studio")
router = APIRouter(tags=["image-studio"])


@router.post("/convert-format", response_model=ConvertFormatResponse, summary="Convert image format")
async def convert_format(
    request: ConvertFormatRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    studio_manager: ImageStudioManager = Depends(get_studio_manager),
):
    """Convert an image to a different format."""
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
    formats = studio_manager.get_supported_formats()
    return SupportedFormatsResponse(formats=formats)


@router.get("/convert-format/recommendations", response_model=FormatRecommendationsResponse, summary="Get format recommendations")
async def get_format_recommendations(
    source_format: str = Query(..., description="Source format"),
    studio_manager: ImageStudioManager = Depends(get_studio_manager),
):
    """Get format recommendations based on source format."""
    recommendations = studio_manager.get_format_recommendations(source_format)
    return FormatRecommendationsResponse(recommendations=recommendations)
