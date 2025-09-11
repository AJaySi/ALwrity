"""Configuration settings for Stability AI integration."""

import os
from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum


class StabilityEndpoint(Enum):
    """Stability AI API endpoints."""
    # Generate endpoints
    GENERATE_ULTRA = "/v2beta/stable-image/generate/ultra"
    GENERATE_CORE = "/v2beta/stable-image/generate/core"
    GENERATE_SD3 = "/v2beta/stable-image/generate/sd3"
    
    # Edit endpoints
    EDIT_ERASE = "/v2beta/stable-image/edit/erase"
    EDIT_INPAINT = "/v2beta/stable-image/edit/inpaint"
    EDIT_OUTPAINT = "/v2beta/stable-image/edit/outpaint"
    EDIT_SEARCH_REPLACE = "/v2beta/stable-image/edit/search-and-replace"
    EDIT_SEARCH_RECOLOR = "/v2beta/stable-image/edit/search-and-recolor"
    EDIT_REMOVE_BACKGROUND = "/v2beta/stable-image/edit/remove-background"
    EDIT_REPLACE_BACKGROUND = "/v2beta/stable-image/edit/replace-background-and-relight"
    
    # Upscale endpoints
    UPSCALE_FAST = "/v2beta/stable-image/upscale/fast"
    UPSCALE_CONSERVATIVE = "/v2beta/stable-image/upscale/conservative"
    UPSCALE_CREATIVE = "/v2beta/stable-image/upscale/creative"
    
    # Control endpoints
    CONTROL_SKETCH = "/v2beta/stable-image/control/sketch"
    CONTROL_STRUCTURE = "/v2beta/stable-image/control/structure"
    CONTROL_STYLE = "/v2beta/stable-image/control/style"
    CONTROL_STYLE_TRANSFER = "/v2beta/stable-image/control/style-transfer"
    
    # 3D endpoints
    STABLE_FAST_3D = "/v2beta/3d/stable-fast-3d"
    STABLE_POINT_AWARE_3D = "/v2beta/3d/stable-point-aware-3d"
    
    # Audio endpoints
    AUDIO_TEXT_TO_AUDIO = "/v2beta/audio/stable-audio-2/text-to-audio"
    AUDIO_AUDIO_TO_AUDIO = "/v2beta/audio/stable-audio-2/audio-to-audio"
    AUDIO_INPAINT = "/v2beta/audio/stable-audio-2/inpaint"
    
    # Results endpoint
    RESULTS = "/v2beta/results/{id}"
    
    # Legacy V1 endpoints
    V1_TEXT_TO_IMAGE = "/v1/generation/{engine_id}/text-to-image"
    V1_IMAGE_TO_IMAGE = "/v1/generation/{engine_id}/image-to-image"
    V1_MASKING = "/v1/generation/{engine_id}/image-to-image/masking"
    
    # User endpoints
    USER_ACCOUNT = "/v1/user/account"
    USER_BALANCE = "/v1/user/balance"
    ENGINES_LIST = "/v1/engines/list"


@dataclass
class StabilityConfig:
    """Configuration for Stability AI service."""
    api_key: str
    base_url: str = "https://api.stability.ai"
    timeout: int = 300
    max_retries: int = 3
    rate_limit_requests: int = 150
    rate_limit_window: int = 10  # seconds
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    supported_image_formats: List[str] = None
    supported_audio_formats: List[str] = None
    
    def __post_init__(self):
        if self.supported_image_formats is None:
            self.supported_image_formats = ["jpeg", "jpg", "png", "webp"]
        if self.supported_audio_formats is None:
            self.supported_audio_formats = ["mp3", "wav"]


# Model pricing information
MODEL_PRICING = {
    "generate": {
        "ultra": 8,
        "core": 3,
        "sd3.5-large": 6.5,
        "sd3.5-large-turbo": 4,
        "sd3.5-medium": 3.5,
        "sd3.5-flash": 2.5
    },
    "edit": {
        "erase": 5,
        "inpaint": 5,
        "outpaint": 4,
        "search_and_replace": 5,
        "search_and_recolor": 5,
        "remove_background": 5,
        "replace_background_and_relight": 8
    },
    "upscale": {
        "fast": 2,
        "conservative": 40,
        "creative": 60
    },
    "control": {
        "sketch": 5,
        "structure": 5,
        "style": 5,
        "style_transfer": 8
    },
    "3d": {
        "stable_fast_3d": 10,
        "stable_point_aware_3d": 4
    },
    "audio": {
        "text_to_audio": 20,
        "audio_to_audio": 20,
        "inpaint": 20
    }
}

# Image dimension limits
IMAGE_LIMITS = {
    "generate": {
        "min_pixels": 4096,
        "max_pixels": 16777216,  # 16MP
        "min_dimension": 64,
        "max_dimension": 16384
    },
    "edit": {
        "min_pixels": 4096,
        "max_pixels": 9437184,  # ~9.4MP
        "min_dimension": 64,
        "aspect_ratio_min": 0.4,  # 1:2.5
        "aspect_ratio_max": 2.5   # 2.5:1
    },
    "upscale": {
        "fast": {
            "min_width": 32,
            "max_width": 1536,
            "min_height": 32,
            "max_height": 1536,
            "min_pixels": 1024,
            "max_pixels": 1048576
        },
        "conservative": {
            "min_pixels": 4096,
            "max_pixels": 9437184,
            "min_dimension": 64
        },
        "creative": {
            "min_pixels": 4096,
            "max_pixels": 1048576,
            "min_dimension": 64
        }
    },
    "control": {
        "min_pixels": 4096,
        "max_pixels": 9437184,
        "min_dimension": 64,
        "aspect_ratio_min": 0.4,
        "aspect_ratio_max": 2.5
    },
    "3d": {
        "min_pixels": 4096,
        "max_pixels": 4194304,  # 4MP
        "min_dimension": 64
    }
}

# Audio limits
AUDIO_LIMITS = {
    "min_duration": 6,
    "max_duration": 190,
    "max_file_size": 50 * 1024 * 1024,  # 50MB
    "supported_formats": ["mp3", "wav"]
}

# Style preset descriptions
STYLE_PRESET_DESCRIPTIONS = {
    "enhance": "Enhance the natural qualities of the image",
    "anime": "Japanese animation style",
    "photographic": "Realistic photographic style",
    "digital-art": "Digital artwork style",
    "comic-book": "Comic book illustration style",
    "fantasy-art": "Fantasy and magical themes",
    "line-art": "Clean line art style",
    "analog-film": "Vintage film photography style",
    "neon-punk": "Cyberpunk with neon lighting",
    "isometric": "Isometric 3D perspective",
    "low-poly": "Low polygon 3D style",
    "origami": "Paper folding art style",
    "modeling-compound": "Clay or modeling compound style",
    "cinematic": "Movie-like cinematic style",
    "3d-model": "3D rendered model style",
    "pixel-art": "Retro pixel art style",
    "tile-texture": "Seamless tile texture style"
}

# Default parameters for different operations
DEFAULT_PARAMETERS = {
    "generate": {
        "ultra": {
            "aspect_ratio": "1:1",
            "output_format": "png"
        },
        "core": {
            "aspect_ratio": "1:1",
            "output_format": "png"
        },
        "sd3": {
            "model": "sd3.5-large",
            "mode": "text-to-image",
            "aspect_ratio": "1:1",
            "output_format": "png"
        }
    },
    "edit": {
        "erase": {
            "grow_mask": 5,
            "output_format": "png"
        },
        "inpaint": {
            "grow_mask": 5,
            "output_format": "png"
        },
        "outpaint": {
            "creativity": 0.5,
            "output_format": "png"
        }
    },
    "upscale": {
        "fast": {
            "output_format": "png"
        },
        "conservative": {
            "creativity": 0.35,
            "output_format": "png"
        },
        "creative": {
            "creativity": 0.3,
            "output_format": "png"
        }
    },
    "control": {
        "sketch": {
            "control_strength": 0.7,
            "output_format": "png"
        },
        "structure": {
            "control_strength": 0.7,
            "output_format": "png"
        },
        "style": {
            "aspect_ratio": "1:1",
            "fidelity": 0.5,
            "output_format": "png"
        }
    },
    "3d": {
        "stable_fast_3d": {
            "texture_resolution": "1024",
            "foreground_ratio": 0.85,
            "remesh": "none",
            "vertex_count": -1
        },
        "stable_point_aware_3d": {
            "texture_resolution": "1024",
            "foreground_ratio": 1.3,
            "remesh": "none",
            "target_type": "none",
            "target_count": 1000,
            "guidance_scale": 3
        }
    },
    "audio": {
        "text_to_audio": {
            "duration": 190,
            "model": "stable-audio-2",
            "output_format": "mp3"
        },
        "audio_to_audio": {
            "duration": 190,
            "model": "stable-audio-2",
            "output_format": "mp3",
            "strength": 1
        },
        "inpaint": {
            "duration": 190,
            "steps": 8,
            "output_format": "mp3",
            "mask_start": 30,
            "mask_end": 190
        }
    }
}

# Rate limiting configuration
RATE_LIMIT_CONFIG = {
    "requests_per_window": 150,
    "window_seconds": 10,
    "timeout_seconds": 60,
    "burst_allowance": 10  # Allow brief bursts above limit
}

# Content moderation settings
CONTENT_MODERATION = {
    "enabled": True,
    "blocked_keywords": [
        # This would contain actual blocked keywords in production
    ],
    "warning_keywords": [
        # Keywords that trigger warnings but don't block
    ]
}

# Quality settings for different use cases
QUALITY_PRESETS = {
    "draft": {
        "model": "core",
        "steps": None,  # Use model defaults
        "cfg_scale": None,
        "description": "Fast generation for drafts and iterations"
    },
    "standard": {
        "model": "sd3.5-medium",
        "steps": None,
        "cfg_scale": 4,
        "description": "Balanced quality and speed"
    },
    "premium": {
        "model": "ultra",
        "steps": None,
        "cfg_scale": None,
        "description": "Highest quality for final outputs"
    },
    "professional": {
        "model": "sd3.5-large",
        "steps": None,
        "cfg_scale": 4,
        "style_preset": "photographic",
        "description": "Professional photography style"
    }
}

# Workflow templates
WORKFLOW_TEMPLATES = {
    "portrait_enhancement": {
        "description": "Enhance portrait photos with professional quality",
        "steps": [
            {"operation": "upscale_conservative", "params": {"creativity": 0.2}},
            {"operation": "inpaint", "params": {"prompt": "professional portrait, high quality"}}
        ]
    },
    "art_creation": {
        "description": "Create artistic images from sketches",
        "steps": [
            {"operation": "control_sketch", "params": {"control_strength": 0.8}},
            {"operation": "upscale_fast", "params": {}}
        ]
    },
    "product_photography": {
        "description": "Create professional product images",
        "steps": [
            {"operation": "remove_background", "params": {}},
            {"operation": "replace_background_and_relight", "params": {"background_prompt": "professional studio lighting, white background"}}
        ]
    },
    "creative_exploration": {
        "description": "Explore different creative interpretations",
        "steps": [
            {"operation": "generate_core", "params": {}},
            {"operation": "control_style", "params": {"fidelity": 0.7}},
            {"operation": "upscale_creative", "params": {"creativity": 0.4}}
        ]
    }
}


def get_stability_config() -> StabilityConfig:
    """Get Stability AI configuration from environment variables.
    
    Returns:
        StabilityConfig instance
    """
    api_key = os.getenv("STABILITY_API_KEY")
    if not api_key:
        raise ValueError("STABILITY_API_KEY environment variable is required")
    
    return StabilityConfig(
        api_key=api_key,
        base_url=os.getenv("STABILITY_BASE_URL", "https://api.stability.ai"),
        timeout=int(os.getenv("STABILITY_TIMEOUT", "300")),
        max_retries=int(os.getenv("STABILITY_MAX_RETRIES", "3")),
        max_file_size=int(os.getenv("STABILITY_MAX_FILE_SIZE", str(10 * 1024 * 1024)))
    )


def validate_image_requirements(
    width: int, 
    height: int, 
    operation: str
) -> Dict[str, Any]:
    """Validate image requirements for specific operations.
    
    Args:
        width: Image width
        height: Image height
        operation: Operation type (generate, edit, upscale, etc.)
        
    Returns:
        Validation result with success status and any issues
    """
    issues = []
    
    limits = IMAGE_LIMITS.get(operation, IMAGE_LIMITS["generate"])
    total_pixels = width * height
    
    # Check minimum requirements
    if "min_pixels" in limits and total_pixels < limits["min_pixels"]:
        issues.append(f"Image must have at least {limits['min_pixels']} pixels")
    
    if "max_pixels" in limits and total_pixels > limits["max_pixels"]:
        issues.append(f"Image must have at most {limits['max_pixels']} pixels")
    
    if "min_dimension" in limits:
        if width < limits["min_dimension"] or height < limits["min_dimension"]:
            issues.append(f"Both dimensions must be at least {limits['min_dimension']} pixels")
    
    # Check aspect ratio for operations that require it
    if "aspect_ratio_min" in limits and "aspect_ratio_max" in limits:
        aspect_ratio = width / height
        if aspect_ratio < limits["aspect_ratio_min"] or aspect_ratio > limits["aspect_ratio_max"]:
            issues.append(f"Aspect ratio must be between {limits['aspect_ratio_min']}:1 and {limits['aspect_ratio_max']}:1")
    
    return {
        "is_valid": len(issues) == 0,
        "issues": issues,
        "total_pixels": total_pixels,
        "aspect_ratio": round(width / height, 3)
    }


def get_model_recommendations(
    use_case: str,
    quality_preference: str = "standard",
    speed_preference: str = "balanced"
) -> Dict[str, Any]:
    """Get model recommendations based on use case and preferences.
    
    Args:
        use_case: Type of use case (portrait, landscape, art, product, etc.)
        quality_preference: Quality preference (draft, standard, premium)
        speed_preference: Speed preference (fast, balanced, quality)
        
    Returns:
        Model recommendations with explanations
    """
    recommendations = {}
    
    # Base recommendations by use case
    if use_case == "portrait":
        recommendations["primary"] = "ultra"
        recommendations["alternative"] = "sd3.5-large"
        recommendations["style_preset"] = "photographic"
    elif use_case == "art":
        recommendations["primary"] = "sd3.5-large"
        recommendations["alternative"] = "ultra"
        recommendations["style_preset"] = "digital-art"
    elif use_case == "product":
        recommendations["primary"] = "ultra"
        recommendations["alternative"] = "sd3.5-large"
        recommendations["style_preset"] = "photographic"
    elif use_case == "concept":
        recommendations["primary"] = "core"
        recommendations["alternative"] = "sd3.5-medium"
        recommendations["style_preset"] = "enhance"
    else:
        recommendations["primary"] = "core"
        recommendations["alternative"] = "sd3.5-medium"
    
    # Adjust based on preferences
    if speed_preference == "fast":
        if recommendations["primary"] == "ultra":
            recommendations["primary"] = "core"
        elif recommendations["primary"] == "sd3.5-large":
            recommendations["primary"] = "sd3.5-medium"
    elif speed_preference == "quality":
        if recommendations["primary"] == "core":
            recommendations["primary"] = "ultra"
        elif recommendations["primary"] == "sd3.5-medium":
            recommendations["primary"] = "sd3.5-large"
    
    # Add quality preset
    if quality_preference in QUALITY_PRESETS:
        recommendations.update(QUALITY_PRESETS[quality_preference])
    
    return recommendations


def get_optimal_parameters(
    operation: str,
    image_info: Optional[Dict[str, Any]] = None,
    user_preferences: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Get optimal parameters for a specific operation.
    
    Args:
        operation: Operation type
        image_info: Information about input image
        user_preferences: User preferences
        
    Returns:
        Optimal parameters for the operation
    """
    # Start with defaults
    params = DEFAULT_PARAMETERS.get(operation, {}).copy()
    
    # Adjust based on image characteristics
    if image_info:
        total_pixels = image_info.get("total_pixels", 0)
        
        # Adjust creativity based on image quality
        if "creativity" in params:
            if total_pixels < 100000:  # Very low res
                params["creativity"] = min(params["creativity"] + 0.1, 0.5)
            elif total_pixels > 2000000:  # High res
                params["creativity"] = max(params["creativity"] - 0.1, 0.1)
    
    # Apply user preferences
    if user_preferences:
        for key, value in user_preferences.items():
            if key in params:
                params[key] = value
    
    return params


def calculate_estimated_cost(
    operation: str,
    model: Optional[str] = None,
    steps: Optional[int] = None
) -> float:
    """Calculate estimated cost in credits for an operation.
    
    Args:
        operation: Operation type
        model: Model name (if applicable)
        steps: Number of steps (for step-based pricing)
        
    Returns:
        Estimated cost in credits
    """
    if operation in MODEL_PRICING:
        if isinstance(MODEL_PRICING[operation], dict):
            if model and model in MODEL_PRICING[operation]:
                base_cost = MODEL_PRICING[operation][model]
            else:
                # Use default model cost
                base_cost = list(MODEL_PRICING[operation].values())[0]
        else:
            base_cost = MODEL_PRICING[operation]
    else:
        base_cost = 5  # Default cost
    
    # Adjust for steps if applicable (mainly for audio)
    if steps and operation.startswith("audio") and model == "stable-audio-2":
        # Audio 2.0 uses formula: 17 + 0.06 * steps
        return 17 + 0.06 * steps
    
    return base_cost


def get_operation_limits(operation: str) -> Dict[str, Any]:
    """Get limits and constraints for a specific operation.
    
    Args:
        operation: Operation type
        
    Returns:
        Limits and constraints
    """
    limits = {
        "file_size_limit": 10 * 1024 * 1024,  # 10MB default
        "timeout": 300,
        "rate_limit": True
    }
    
    # Add operation-specific limits
    if operation in IMAGE_LIMITS:
        limits.update(IMAGE_LIMITS[operation])
    
    if operation.startswith("audio"):
        limits.update(AUDIO_LIMITS)
        limits["file_size_limit"] = 50 * 1024 * 1024  # 50MB for audio
    
    if operation.startswith("3d"):
        limits["file_size_limit"] = 10 * 1024 * 1024  # 10MB for 3D
    
    return limits


# Environment-specific configurations
def get_environment_config() -> Dict[str, Any]:
    """Get environment-specific configuration.
    
    Returns:
        Environment configuration
    """
    env = os.getenv("ENVIRONMENT", "development")
    
    configs = {
        "development": {
            "debug_mode": True,
            "log_level": "DEBUG",
            "cache_results": False,
            "mock_responses": False
        },
        "staging": {
            "debug_mode": True,
            "log_level": "INFO",
            "cache_results": True,
            "mock_responses": False
        },
        "production": {
            "debug_mode": False,
            "log_level": "WARNING",
            "cache_results": True,
            "mock_responses": False
        }
    }
    
    return configs.get(env, configs["development"])


# Feature flags
FEATURE_FLAGS = {
    "enable_batch_processing": True,
    "enable_webhooks": True,
    "enable_caching": True,
    "enable_analytics": True,
    "enable_experimental_endpoints": True,
    "enable_quality_analysis": True,
    "enable_prompt_optimization": True,
    "enable_workflow_templates": True
}


def is_feature_enabled(feature: str) -> bool:
    """Check if a feature is enabled.
    
    Args:
        feature: Feature name
        
    Returns:
        True if feature is enabled
    """
    return FEATURE_FLAGS.get(feature, False)