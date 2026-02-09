"""
OAuth redirect URI helpers and validations.

Ensures redirect URIs are environment-driven and aligned with the expected
deployment environment (dev/stage/prod).
"""

from __future__ import annotations

import os
from typing import Optional
from urllib.parse import urlparse


def _origin_from_url(url: str) -> str:
    # We only care about the scheme + host for redirect origin validation.
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError(f"Invalid URL for redirect URI: {url}")
    return f"{parsed.scheme}://{parsed.netloc}"


def _infer_origin_environment(origin: str) -> str:
    # Heuristic mapping used to catch common prod/stage/dev mismatches.
    host = urlparse(origin).hostname or ""
    host = host.lower()

    if host in {"localhost", "127.0.0.1"} or host.endswith(".local") or "ngrok" in host:
        return "dev"

    if "staging" in host or "stage" in host:
        return "stage"

    return "prod"


def _expected_environment() -> Optional[str]:
    # Normalize DEPLOY_ENV to our internal dev/stage/prod buckets.
    deploy_env = os.getenv("DEPLOY_ENV", "").lower()
    mapping = {
        "local": "dev",
        "development": "dev",
        "dev": "dev",
        "staging": "stage",
        "stage": "stage",
        "production": "prod",
        "prod": "prod",
    }
    return mapping.get(deploy_env)


def validate_redirect_uri(provider: str, redirect_uri: str) -> str:
    """
    Validate redirect URI for a provider and return its origin.
    """
    origin = _origin_from_url(redirect_uri)

    frontend_url = os.getenv("FRONTEND_URL")
    if frontend_url:
        # Enforce a single trusted origin for OAuth redirects to avoid mixups.
        frontend_origin = _origin_from_url(frontend_url)
        if frontend_origin != origin:
            raise ValueError(
                f"{provider} redirect origin {origin} does not match FRONTEND_URL origin {frontend_origin}."
            )

    expected_env = _expected_environment()
    if expected_env:
        # Catch accidental prod/stage/dev crossovers early during config load.
        origin_env = _infer_origin_environment(origin)
        if origin_env != expected_env:
            raise ValueError(
                f"{provider} redirect origin {origin} looks like {origin_env}, but DEPLOY_ENV expects {expected_env}."
            )

    return origin


def get_redirect_uri(provider: str, env_var: str) -> str:
    """
    Fetch and validate redirect URI for a provider.
    """
    # We intentionally require environment configuration to avoid hardcoded fallbacks.
    redirect_uri = os.getenv(env_var)
    if not redirect_uri:
        raise ValueError(f"{env_var} must be set for {provider} OAuth.")
    validate_redirect_uri(provider, redirect_uri)
    return redirect_uri
