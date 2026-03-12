<<<<<<< HEAD
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
=======
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from utils.logger_utils import get_service_logger

logger = get_service_logger("tenant_provider_config")


@dataclass
class TenantProviderConfig:
    selected_providers: List[str]
    model_policy: Dict[str, Optional[str]]
    credential_source: Dict[str, str]
    provider_keys: Dict[str, str] = field(default_factory=dict)


class TenantProviderConfigResolver:
    """Resolves per-request provider, model policy, and credential source.

    Priority: tenant-scoped DB key (future vault hook) -> environment defaults.
    """

    _PROVIDER_ALIASES: Dict[str, Tuple[str, ...]] = {
        "gemini": ("gemini", "google", "google_api_key", "gemini_api_key"),
        "google": ("gemini", "google", "google_api_key", "gemini_api_key"),
        "huggingface": ("huggingface", "hf", "hf_token"),
        "hf": ("huggingface", "hf", "hf_token"),
        "stability": ("stability", "stability_api_key"),
        "wavespeed": ("wavespeed", "wavespeed_api_key"),
        "openai": ("openai", "openai_api_key"),
    }

    _ENV_VARS: Dict[str, Tuple[str, ...]] = {
        "gemini": ("GEMINI_API_KEY", "GOOGLE_API_KEY"),
        "huggingface": ("HF_TOKEN",),
        "stability": ("STABILITY_API_KEY",),
        "wavespeed": ("WAVESPEED_API_KEY",),
        "openai": ("OPENAI_API_KEY",),
    }

    _ENV_PROVIDER_DEFAULTS: Dict[str, str] = {
        "text": "GPT_PROVIDER",
        "image": "GPT_PROVIDER",
        "video": "VIDEO_PROVIDER",
        "audio": "AUDIO_PROVIDER",
    }

    _DEFAULT_MODELS: Dict[Tuple[str, str], str] = {
        ("text", "google"): "gemini-2.0-flash-001",
        ("text", "huggingface"): "mistralai/Mistral-7B-Instruct-v0.3:groq",
        ("image", "wavespeed"): "qwen-image",
        ("image", "huggingface"): "black-forest-labs/FLUX.1-Krea-dev",
        ("video", "huggingface"): "tencent/HunyuanVideo",
        ("video", "wavespeed"): "hunyuan-video-1.5",
        ("audio", "wavespeed"): "minimax-speech-02-hd",
    }

    def resolve(self, modality: str, user_id: Optional[str], explicit_provider: Optional[str] = None) -> TenantProviderConfig:
        provider_candidates = self._resolve_providers(modality=modality, explicit_provider=explicit_provider)
        provider_keys: Dict[str, str] = {}
        credential_source: Dict[str, str] = {}

        for provider in provider_candidates:
            key, source = self.resolve_provider_key(provider=provider, user_id=user_id)
            if key:
                provider_keys[provider] = key
            credential_source[provider] = source

        selected_providers = [p for p in provider_candidates if p in provider_keys]
        if not selected_providers and provider_candidates:
            selected_providers = [provider_candidates[0]]

        model_policy = {
            "modality": modality,
            "default_model": self._DEFAULT_MODELS.get((modality, selected_providers[0]), None) if selected_providers else None,
            "allow_fallback": True,
        }
        return TenantProviderConfig(
            selected_providers=selected_providers,
            model_policy=model_policy,
            credential_source=credential_source,
            provider_keys=provider_keys,
        )

    def resolve_provider_key(self, provider: str, user_id: Optional[str]) -> Tuple[Optional[str], str]:
        normalized = self._normalize_provider(provider)

        tenant_key = self._get_tenant_key_from_db(user_id=user_id, provider=normalized)
        if tenant_key:
            return tenant_key, "tenant_db"

        env_key = self._get_key_from_env(normalized)
        if env_key:
            return env_key, "env_default"

        return None, "missing"

    def _resolve_providers(self, modality: str, explicit_provider: Optional[str]) -> List[str]:
        if explicit_provider:
            return [self._normalize_provider(explicit_provider)]

        env_provider = os.getenv(self._ENV_PROVIDER_DEFAULTS.get(modality, ""), "").strip().lower()
        if env_provider:
            normalized = self._normalize_provider(env_provider)
            return [normalized]

        defaults = {
            "text": ["google", "huggingface"],
            "image": ["wavespeed", "gemini", "huggingface", "stability"],
            "video": ["huggingface", "wavespeed"],
            "audio": ["wavespeed"],
        }
        return defaults.get(modality, ["google"])

    def _normalize_provider(self, provider: str) -> str:
        provider_l = (provider or "").strip().lower()
        if provider_l in ("gemini", "google"):
            return "gemini"
        if provider_l in ("hf", "huggingface", "hf_response_api"):
            return "huggingface"
        return provider_l

    def _get_tenant_key_from_db(self, user_id: Optional[str], provider: str) -> Optional[str]:
        if not user_id:
            return None
        try:
            from services.database import get_session_for_user
            from models.onboarding import OnboardingSession, APIKey

            db = get_session_for_user(user_id)
            if not db:
                return None
            try:
                session = (
                    db.query(OnboardingSession)
                    .filter(OnboardingSession.user_id == user_id)
                    .order_by(OnboardingSession.updated_at.desc())
                    .first()
                )
                if not session:
                    return None

                aliases = self._PROVIDER_ALIASES.get(provider, (provider,))
                rec = (
                    db.query(APIKey)
                    .filter(APIKey.session_id == session.id, APIKey.provider.in_(aliases))
                    .order_by(APIKey.updated_at.desc())
                    .first()
                )
                return rec.key if rec and rec.key else None
            finally:
                db.close()
        except Exception as exc:
            logger.debug("Tenant DB key lookup failed for provider=%s user_id=%s: %s", provider, user_id, exc)
            return None

    def _get_key_from_env(self, provider: str) -> Optional[str]:
        for env_var in self._ENV_VARS.get(provider, ()):  # pragma: no branch
            value = os.getenv(env_var)
            if value:
                return value
        return None


tenant_provider_config_resolver = TenantProviderConfigResolver()
>>>>>>> pr-420
