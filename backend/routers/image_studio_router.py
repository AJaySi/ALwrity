"""API endpoints for Image Studio operations."""

import base64
from pathlib import Path
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import FileResponse

from .image_studio.models import (
    CreateImageRequest, CostEstimationRequest,
    EditImageRequest, EditImageResponse, EditOperationsResponse,
    EditModelsResponse, EditModelRecommendationRequest, EditModelRecommendationResponse,
    UpscaleImageRequest, UpscaleImageResponse,
    FaceSwapRequest, FaceSwapResponse, FaceSwapModelsResponse,
    FaceSwapModelRecommendationRequest, FaceSwapModelRecommendationResponse,
    ControlImageRequest, ControlImageResponse, ControlOperationsResponse,
    SocialOptimizeRequest, SocialOptimizeResponse, PlatformFormatsResponse,
    TransformImageToVideoRequestModel, TalkingAvatarRequestModel,
    TransformVideoResponse, TransformCostEstimateRequest, TransformCostEstimateResponse,
    CompressImageRequest, CompressImageResponse, CompressBatchRequest, CompressBatchResponse,
    CompressionEstimateRequest, CompressionEstimateResponse,
    CompressionFormatsResponse, CompressionPresetsResponse,
    ConvertFormatRequest, ConvertFormatResponse, ConvertFormatBatchRequest, ConvertFormatBatchResponse,
    SupportedFormatsResponse, FormatRecommendationsResponse,
)
from .image_studio.deps import get_studio_manager, _require_user_id
from services.image_studio import (
    ImageStudioManager,
    CreateStudioRequest,
    EditStudioRequest,
    ControlStudioRequest,
    SocialOptimizerRequest,
    TransformImageToVideoRequest,
    TalkingAvatarRequest,
)
from services.image_studio.face_swap_service import FaceSwapStudioRequest
from services.image_studio.upscale_service import UpscaleStudioRequest
from services.image_studio.templates import Platform, TemplateCategory
from middleware.auth_middleware import get_current_user, get_current_user_with_query_token
from utils.logger_utils import get_service_logger


logger = get_service_logger("api.image_studio")
router = APIRouter(prefix="/api/image-studio", tags=["image-studio"])




