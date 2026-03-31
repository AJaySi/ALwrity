"""Feature profile parsing and expansion logic."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Iterable, Tuple

from .feature_registry import FEATURE_GROUPS, PROFILE_GROUP_MAP


ENV_FEATURE_PROFILE = "ALWRITY_FEATURE_TO_ENABLE"
DEFAULT_PROFILE = "all"


@dataclass(frozen=True)
class ExpandedFeatureProfile:
    """Expanded profile data used by runtime helpers."""
    
    profiles: Tuple[str, ...]
    groups: Tuple[str, ...]


class UnknownFeatureProfileError(ValueError):
    """Raised when ALWRITY_FEATURE_TO_ENABLE contains unknown profile values."""


def _normalize_values(raw_value: str | None) -> Tuple[str, ...]:
    if not raw_value or not raw_value.strip():
        return (DEFAULT_PROFILE,)
    
    normalized = tuple(
        value.strip().lower()
        for value in raw_value.split(",")
        if value.strip()
    )
    return normalized or (DEFAULT_PROFILE,)


def parse_feature_profiles(raw_value: str | None = None) -> Tuple[str, ...]:
    """Parse and validate profile names from env/raw input.
    
    Supports comma-separated profile names, e.g. `core,podcast`.
    Raises UnknownFeatureProfileError when any profile is not registered.
    """
    
    selected_profiles = _normalize_values(raw_value if raw_value is not None else os.getenv(ENV_FEATURE_PROFILE))
    
    unknown = sorted({profile for profile in selected_profiles if profile not in PROFILE_GROUP_MAP})
    if unknown:
        supported = ", ".join(sorted(PROFILE_GROUP_MAP))
        unknown_display = ", ".join(unknown)
        raise UnknownFeatureProfileError(
            f"Unknown {ENV_FEATURE_PROFILE} value(s): {unknown_display}. Supported profiles: {supported}."
        )
    
    return selected_profiles


def _dedupe_stable(items: Iterable[str]) -> Tuple[str, ...]:
    return tuple(dict.fromkeys(items))


def expand_profiles(profiles: Tuple[str, ...]) -> ExpandedFeatureProfile:
    """Expand profile names into a deduplicated group list."""
    
    groups = _dedupe_stable(
        group
        for profile in profiles
        for group in PROFILE_GROUP_MAP[profile]
    )
    
    missing_groups = sorted({group for group in groups if group not in FEATURE_GROUPS})
    if missing_groups:
        raise RuntimeError(f"Profile mapping references unknown groups: {', '.join(missing_groups)}")
    
    return ExpandedFeatureProfile(profiles=profiles, groups=groups)
