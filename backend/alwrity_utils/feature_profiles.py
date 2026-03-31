"""Feature profile parsing and expansion logic."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Iterable, Tuple

from .feature_registry import FEATURE_GROUPS, PROFILE_GROUP_MAP


ENV_ENABLED_FEATURES = "ALWRITY_ENABLED_FEATURES"
DEFAULT_FEATURES = "all"


@dataclass(frozen=True)
class ExpandedFeatureProfile:
    """Expanded profile data used by runtime helpers."""
    
    profiles: Tuple[str, ...]
    groups: Tuple[str, ...]


class UnknownFeatureProfileError(ValueError):
    """Raised when ALWRITY_ENABLED_FEATURES contains unknown feature values."""


def _get_env_value() -> str:
    """Get the enabled features value from environment."""
    return os.getenv(ENV_ENABLED_FEATURES) or DEFAULT_FEATURES


def _normalize_values(raw_value: str | None) -> Tuple[str, ...]:
    if not raw_value or not raw_value.strip():
        return (DEFAULT_FEATURES,)
    
    normalized = tuple(
        value.strip().lower()
        for value in raw_value.split(",")
        if value.strip()
    )
    return normalized or (DEFAULT_FEATURES,)


def parse_feature_profiles(raw_value: str | None = None) -> Tuple[str, ...]:
    """Parse and validate feature names from env/raw input.
    
    Supports comma-separated feature names, e.g. `podcast,core`.
    Raises UnknownFeatureProfileError when any feature is not registered.
    """
    
    selected_profiles = _normalize_values(raw_value if raw_value is not None else _get_env_value())
    
    unknown = sorted({profile for profile in selected_profiles if profile not in PROFILE_GROUP_MAP and profile not in FEATURE_GROUPS})
    if unknown:
        supported = ", ".join(sorted(set(PROFILE_GROUP_MAP.keys()) | set(FEATURE_GROUPS.keys())))
        unknown_display = ", ".join(unknown)
        raise UnknownFeatureProfileError(
            f"Unknown {ENV_ENABLED_FEATURES} value(s): {unknown_display}. Supported: {supported}."
        )
    
    return selected_profiles


def _dedupe_stable(items: Iterable[str]) -> Tuple[str, ...]:
    return tuple(dict.fromkeys(items))


def expand_profiles(profiles: Tuple[str, ...]) -> ExpandedFeatureProfile:
    """Expand profile names into a deduplicated group list."""
    
    # Handle "all" specially - include all groups
    if "all" in profiles:
        return ExpandedFeatureProfile(profiles=("all",), groups=tuple(FEATURE_GROUPS.keys()))
    
    # Otherwise expand via PROFILE_GROUP_MAP
    groups = _dedupe_stable(
        group
        for profile in profiles
        for group in PROFILE_GROUP_MAP.get(profile, (profile,))
    )
    
    # Include FEATURE_GROUPS keys directly
    all_groups = _dedupe_stable(list(groups) + [g for g in groups if g in FEATURE_GROUPS])
    
    return ExpandedFeatureProfile(profiles=profiles, groups=all_groups)
