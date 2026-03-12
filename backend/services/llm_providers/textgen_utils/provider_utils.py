"""
Provider Utilities Module

This module contains provider-related utility functions extracted from main_text_generation.py
to resolve merge conflicts and improve maintainability.
"""

import os
from typing import Optional, List

from ..routing_policy import resolve_text_provider_alias


def _normalize_provider(provider: Optional[str]) -> Optional[str]:
    """Normalize provider name to canonical form."""
    if not provider:
        return None
    provider_aliases = {
        "gemini": "google",
        "google": "google",
        "hf": "huggingface",
        "hf_response_api": "huggingface",
        "huggingface": "huggingface",
        "wavespeed": "huggingface",
    }
    value = str(provider).strip().lower()
    return provider_aliases.get(value, value)


def _parse_csv_env(value: Optional[str]) -> List[str]:
    """Parse CSV environment variable into list of values."""
    if not value:
        return []
    return [v.strip() for v in str(value).split(",") if v.strip()]


def _resolve_provider_sequence(
    preferred_provider: Optional[str],
    env_provider_raw: str,
    available_providers: List[str],
) -> List[str]:
    """Resolve provider sequence based on preferences and availability."""
    configured = _parse_csv_env(preferred_provider) if preferred_provider else _parse_csv_env(env_provider_raw)
    normalized = [_normalize_provider(p) for p in configured if _normalize_provider(p)]

    if not normalized:
        if "google" in available_providers:
            return ["google"]
        if "huggingface" in available_providers:
            return ["huggingface"]
        return []

    # preserve order and keep only available providers
    sequence = []
    for provider in normalized:
        if provider in available_providers:
            sequence.append(provider)

    # strict mode for single configured provider: no silent remap
    if len(normalized) == 1:
        return sequence

    # multi-provider mode: append any other available providers as tail only if none configured are available
    if not sequence:
        return [p for p in ["huggingface", "google"] if p in available_providers]

    return sequence


def check_gpt_provider(gpt_provider: str) -> bool:
    """Check if the specified GPT provider is supported."""
    supported_providers = ["google", "huggingface"]
    resolved_provider = resolve_text_provider_alias(gpt_provider) or gpt_provider
    return resolved_provider in supported_providers
