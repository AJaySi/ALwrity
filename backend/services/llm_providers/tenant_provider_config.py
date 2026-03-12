"""Tenant-aware provider configuration and API key resolution for LLM providers."""

from __future__ import annotations

import os
import time
from typing import Dict, Optional

from loguru import logger

from services.database import get_session_for_user
from models.onboarding import APIKey, OnboardingSession

_PROVIDER_KEY_MAP = {
    "google": "gemini",
    "gemini": "gemini",
    "huggingface": "hf_token",
    "hf": "hf_token",
    "hf_response_api": "hf_token",
}

_PROVIDER_ENV_MAP = {
    "gemini": "GEMINI_API_KEY",
    "hf_token": "HF_TOKEN",
}

_CACHE_TTL_SECONDS = int(os.getenv("TENANT_PROVIDER_CACHE_TTL", "60"))
_cache: Dict[str, tuple[float, Optional[str]]] = {}


def _cache_key(user_id: Optional[str], provider_key: str) -> str:
    return f"{user_id or 'global'}::{provider_key}"


def _normalize_provider(provider: str) -> str:
    return _PROVIDER_KEY_MAP.get((provider or "").lower(), (provider or "").lower())


def get_tenant_api_key(user_id: Optional[str], provider: str) -> Optional[str]:
    provider_key = _normalize_provider(provider)
    ck = _cache_key(user_id, provider_key)
    cached = _cache.get(ck)
    now = time.time()
    if cached and (now - cached[0]) < _CACHE_TTL_SECONDS:
        return cached[1]

    key: Optional[str] = None
    if user_id:
        db = None
        try:
            db = get_session_for_user(user_id)
            if db:
                record = (
                    db.query(APIKey.key)
                    .join(OnboardingSession, APIKey.session_id == OnboardingSession.id)
                    .filter(OnboardingSession.user_id == user_id, APIKey.provider == provider_key)
                    .order_by(APIKey.updated_at.desc())
                    .first()
                )
                if record and record[0]:
                    key = record[0]
        except Exception as exc:
            logger.debug("tenant api-key lookup failed for user={}, provider={}: {}", user_id, provider_key, exc)
        finally:
            if db:
                db.close()

    if not key:
        env_var = _PROVIDER_ENV_MAP.get(provider_key)
        if env_var:
            key = os.getenv(env_var)

    _cache[ck] = (now, key)
    return key


def get_available_text_providers(user_id: Optional[str]) -> list[str]:
    providers = []
    if get_tenant_api_key(user_id, "gemini"):
        providers.append("google")
    if get_tenant_api_key(user_id, "huggingface"):
        providers.append("huggingface")
    return providers
