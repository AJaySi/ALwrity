"""
Model Utilities Module

This module contains model-related utility functions extracted from main_text_generation.py
to resolve merge conflicts and improve maintainability.
"""

import os
from typing import Optional, List

from ..routing_policy import PREMIUM_DEFAULT_MODEL


def _map_logical_model_to_provider_model(provider: str, model_name: str) -> str:
    """Map logical model aliases/full names to provider-specific model IDs."""
    raw = (model_name or "").strip()
    if not raw:
        return raw

    # Full provider path supplied explicitly; use as-is.
    if "/" in raw:
        return raw

    key = raw.lower()

    hf_map = {
        "gpt-oss": "openai/gpt-oss-120b:cerebras",
        "gpt-oss-120b": "openai/gpt-oss-120b:cerebras",
        "gpt-oss-20b": "openai/gpt-oss-20b:cerebras",
        "mistral": "mistralai/Mistral-7B-Instruct-v0.3:cerebras",
        "mistral-7b": "mistralai/Mistral-7B-Instruct-v0.3:cerebras",
        "llama": "meta-llama/Llama-3.1-8B-Instruct:groq",
        "llama-8b": "meta-llama/Llama-3.1-8B-Instruct:groq",
        "llama-70b": "meta-llama/Llama-3.1-70B-Instruct:groq",
    }

    wavespeed_map = {
        "gpt-oss": "openai/gpt-oss-120b",
        "gpt-oss-120b": "openai/gpt-oss-120b",
        "gpt-oss-20b": "openai/gpt-oss-20b",
        "mistral": "mistralai/Mistral-7B-Instruct-v0.3",
        "mistral-7b": "mistralai/Mistral-7B-Instruct-v0.3",
        "llama": "meta-llama/Llama-3.1-8B-Instruct",
        "llama-8b": "meta-llama/Llama-3.1-8B-Instruct",
        "llama-70b": "meta-llama/Llama-3.1-70B-Instruct",
    }

    if provider in {"huggingface", "hf", "hf_response_api"}:
        return hf_map.get(key, raw)
    if provider == "wavespeed":
        return wavespeed_map.get(key, raw)

    return raw


def _resolve_model_sequence(provider: str, preferred_hf_models: Optional[List[str]] = None) -> List[str]:
    """Resolve model sequence for a given provider."""
    models_env = _parse_csv_env(os.getenv("TEXTGEN_AI_MODELS", ""))

    if provider == "google":
        return ["gemini-2.0-flash-001"]

    if preferred_hf_models:
        return [_map_logical_model_to_provider_model(provider, m) for m in preferred_hf_models if m]

    if not models_env:
        return [PREMIUM_DEFAULT_MODEL]

    resolved = [_map_logical_model_to_provider_model(provider, m) for m in models_env if m.strip()]
    return resolved or [PREMIUM_DEFAULT_MODEL]


def _parse_csv_env(value: Optional[str]) -> List[str]:
    """Parse CSV environment variable into list of values."""
    if not value:
        return []
    return [v.strip() for v in str(value).split(",") if v.strip()]
