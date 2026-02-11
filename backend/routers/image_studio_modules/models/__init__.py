"""Image Studio API Models Package.

This package contains all Pydantic models used by the Image Studio API,
organized by functional area for better maintainability.
"""

# Generation models
from .generation import CreateImageRequest, CostEstimationRequest

# Editing models
from .editing import (
    EditImageRequest,
    EditModelsResponse,
    EditModelRecommendationRequest,
    EditModelRecommendationResponse,
    EditImageResponse,
    EditOperationsResponse,
    UpscaleImageRequest,
    UpscaleImageResponse,
    ControlImageRequest,
    ControlImageResponse,
    ControlOperationsResponse,
)

# Face swap models
from .face_swap import (
    FaceSwapRequest,
    FaceSwapResponse,
    FaceSwapModelsResponse,
    FaceSwapModelRecommendationRequest,
    FaceSwapModelRecommendationResponse,
)

# Social models
from .social import SocialOptimizeRequest, SocialOptimizeResponse, PlatformFormatsResponse

# Transform models
from .transform import (
    TransformImageToVideoRequestModel,
    TalkingAvatarRequestModel,
    TransformVideoResponse,
    TransformCostEstimateRequest,
    TransformCostEstimateResponse,
    TransformJobResponse,
    TransformJobStatusResponse,
    TransformCancelResponse,
)

# Compression models
from .compression import (
    CompressImageRequest,
    CompressImageResponse,
    CompressBatchRequest,
    CompressBatchResponse,
    CompressionEstimateRequest,
    CompressionEstimateResponse,
    CompressionFormatsResponse,
    CompressionPresetsResponse,
)

# Format conversion models
from .conversion import (
    ConvertFormatRequest,
    ConvertFormatResponse,
    ConvertFormatBatchRequest,
    ConvertFormatBatchResponse,
    SupportedFormatsResponse,
    FormatRecommendationsResponse,
)

# Shared models
from .shared import *

__all__ = [
    # Generation
    "CreateImageRequest",
    "CostEstimationRequest",

    # Editing
    "EditImageRequest",
    "EditModelsResponse",
    "EditModelRecommendationRequest",
    "EditModelRecommendationResponse",
    "EditImageResponse",
    "EditOperationsResponse",
    "UpscaleImageRequest",
    "UpscaleImageResponse",
    "ControlImageRequest",
    "ControlImageResponse",
    "ControlOperationsResponse",

    # Face swap
    "FaceSwapRequest",
    "FaceSwapResponse",
    "FaceSwapModelsResponse",
    "FaceSwapModelRecommendationRequest",
    "FaceSwapModelRecommendationResponse",

    # Social
    "SocialOptimizeRequest",
    "SocialOptimizeResponse",
    "PlatformFormatsResponse",

    # Transform
    "TransformImageToVideoRequestModel",
    "TalkingAvatarRequestModel",
    "TransformVideoResponse",
    "TransformCostEstimateRequest",
    "TransformCostEstimateResponse",
    "TransformJobResponse",
    "TransformJobStatusResponse",
    "TransformCancelResponse",

    # Compression
    "CompressImageRequest",
    "CompressImageResponse",
    "CompressBatchRequest",
    "CompressBatchResponse",
    "CompressionEstimateRequest",
    "CompressionEstimateResponse",
    "CompressionFormatsResponse",
    "CompressionPresetsResponse",

    # Format conversion
    "ConvertFormatRequest",
    "ConvertFormatResponse",
    "ConvertFormatBatchRequest",
    "ConvertFormatBatchResponse",
    "SupportedFormatsResponse",
    "FormatRecommendationsResponse",
]