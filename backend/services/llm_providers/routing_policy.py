"""Routing policy for LLM provider aliases and model defaults."""

from typing import Dict, List


# Premium text generation defaults
PREMIUM_DEFAULT_PROVIDER = "huggingface"
PREMIUM_DEFAULT_MODEL = "openai/gpt-oss-120b:groq"

# SIF low-cost defaults for text generation
SIF_LOW_COST_MODEL_DEFAULTS: List[str] = [
    "mistralai/Mistral-7B-Instruct-v0.3:groq",
]

# Canonical provider aliases for text routing
PROVIDER_ALIAS_MAPPING: Dict[str, str] = {
    "gemini": "google",
    "google": "google",
    "hf_response_api": "huggingface",
    "huggingface": "huggingface",
    "hf": "huggingface",
    # Text-only alias: route wavespeed GPT_PROVIDER to premium HF text route.
    "wavespeed": PREMIUM_DEFAULT_PROVIDER,
}


def resolve_text_provider_alias(provider: str) -> str:
    """Resolve a GPT provider alias into a canonical text provider."""
    return PROVIDER_ALIAS_MAPPING.get((provider or "").lower(), "")

