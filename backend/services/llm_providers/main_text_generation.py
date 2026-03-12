"""Main Text Generation Service for ALwrity Backend.

This service provides the main LLM text generation functionality,
migrated from the legacy lib/gpt_providers/text_generation/main_text_generation.py

This is a clean version that imports from modular components to avoid merge conflicts.
"""

import os
import json
from typing import Optional, Dict, Any, List
from datetime import datetime
from loguru import logger
from fastapi import HTTPException

# Import all functionality from our modular textgen_utils package
from .textgen_utils import (
    llm_text_gen,
    check_gpt_provider,
    get_api_key,
    _normalize_provider,
    _parse_csv_env,
    _resolve_provider_sequence,
    _map_logical_model_to_provider_model,
    _resolve_model_sequence,
)

# Re-export all the main functions for backward compatibility
__all__ = [
    "llm_text_gen",
    "check_gpt_provider", 
    "get_api_key",
    "_normalize_provider",
    "_parse_csv_env",
    "_resolve_provider_sequence",
    "_map_logical_model_to_provider_model",
    "_resolve_model_sequence",
]

# Maintain any additional constants or configurations that might be needed
PREMIUM_HF_MINIMAL_FALLBACK_MODELS = [
    "openai/gpt-oss-120b:groq",
]

# Legacy compatibility - any imports that other modules might expect
from .gemini_provider import gemini_text_response, gemini_structured_json_response
from .huggingface_provider import huggingface_text_response, huggingface_structured_json_response
from .tenant_provider_config import tenant_provider_config_resolver
from .routing_policy import (
    PREMIUM_DEFAULT_MODEL,
    SIF_LOW_COST_MODEL_DEFAULTS,
    resolve_text_provider_alias,
)
