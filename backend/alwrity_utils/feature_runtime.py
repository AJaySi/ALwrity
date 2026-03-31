"""Runtime helpers for profile-driven feature toggles."""

from __future__ import annotations

from functools import lru_cache
from typing import Tuple

from .feature_profiles import expand_profiles, parse_feature_profiles
from .feature_registry import FEATURE_GROUPS


@lru_cache(maxsize=1)
def _runtime_state() -> dict[str, Tuple[str, ...]]:
    profiles = parse_feature_profiles()
    expanded = expand_profiles(profiles)
    
    routers = []
    startup_hooks = []
    optional_services = []
    enabled_features = set(expanded.groups)
    
    for group in expanded.groups:
        feature_group = FEATURE_GROUPS[group]
        routers.extend(feature_group.routers)
        startup_hooks.extend(feature_group.startup_hooks)
        optional_services.extend(feature_group.optional_services)
        enabled_features.update(feature_group.features)
    
    return {
        "profiles": expanded.profiles,
        "groups": expanded.groups,
        "routers": tuple(dict.fromkeys(routers)),
        "startup_hooks": tuple(dict.fromkeys(startup_hooks)),
        "optional_services": tuple(dict.fromkeys(optional_services)),
        "features": tuple(sorted(enabled_features)),
    }


def get_active_profiles() -> Tuple[str, ...]:
    """Return validated active profile names."""
    return _runtime_state()["profiles"]


def get_enabled_groups() -> Tuple[str, ...]:
    """Return resolved feature-group names."""
    return _runtime_state()["groups"]


def get_enabled_routers() -> Tuple[str, ...]:
    """Return enabled router import targets in `module:attribute` format."""
    return _runtime_state()["routers"]


def get_enabled_startup_hooks() -> Tuple[str, ...]:
    """Return enabled startup hook import targets in `module:attribute` format."""
    return _runtime_state()["startup_hooks"]


def get_enabled_optional_services() -> Tuple[str, ...]:
    """Return enabled optional service import targets in `module:attribute` format."""
    return _runtime_state()["optional_services"]


def is_enabled(feature: str) -> bool:
    """Return True when a feature/group name is enabled by active profiles."""
    return feature.strip().lower() in _runtime_state()["features"]


def reset_feature_runtime_cache() -> None:
    """Clear runtime cache (useful for tests)."""
    _runtime_state.cache_clear()
