"""Feature registry for profile-based capability toggles.

This module stores normalized feature-group definitions used by the
feature profile runtime.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Tuple


@dataclass(frozen=True)
class FeatureGroup:
    """Single feature group and the capabilities it enables."""

    routers: Tuple[str, ...] = ()
    startup_hooks: Tuple[str, ...] = ()
    optional_services: Tuple[str, ...] = ()
    features: Tuple[str, ...] = field(default_factory=tuple)


FEATURE_GROUPS: Dict[str, FeatureGroup] = {
    # Baseline platform capabilities expected for most deployments.
    "core": FeatureGroup(
        features=("core", "health", "onboarding", "research"),
        routers=(
            "api.component_logic:router",
            "api.subscription:router",
            "api.onboarding_utils.step3_routes:router",
            "api.research.router:router",
        ),
        startup_hooks=(
            "services.database:init_database",
        ),
        optional_services=(
            "services.scheduler:get_scheduler",
        ),
    ),
    # Podcast maker capability set.
    "podcast": FeatureGroup(
        features=("podcast",),
        routers=("api.podcast.router:router",),
    ),
    # YouTube creator studio capability set.
    "youtube": FeatureGroup(
        features=("youtube",),
        routers=("api.youtube.router:router",),
    ),
    # Content planning and strategy copilot capability set.
    "content_planning": FeatureGroup(
        features=("content_planning", "strategy_copilot"),
        routers=(
            "api.content_planning.api.router:router",
            "api.content_planning.strategy_copilot:router",
        ),
    ),
}


# Profile-to-group mapping.
PROFILE_GROUP_MAP: Dict[str, Tuple[str, ...]] = {
    # Default / full-feature deployment.
    "all": tuple(FEATURE_GROUPS.keys()),
    # Lightweight deployment.
    "core": ("core",),
    # Focused profile for podcast-only experiences (+ core infra).
    "podcast": ("core", "podcast"),
    # Focused profile for YouTube-only experiences (+ core infra).
    "youtube": ("core", "youtube"),
    # Planning-only setup (+ core infra).
    "planning": ("core", "content_planning"),
}
