"""
Platform specifications for Social Optimizer.

Defines aspect ratios, duration limits, file size limits, and other requirements
for each social media platform.
"""

from dataclasses import dataclass
from typing import List, Optional
from enum import Enum


class Platform(Enum):
    """Social media platforms."""
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    LINKEDIN = "linkedin"
    FACEBOOK = "facebook"
    TWITTER = "twitter"


@dataclass
class PlatformSpec:
    """Platform specification for video optimization."""
    platform: Platform
    name: str
    aspect_ratio: str  # e.g., "9:16", "16:9", "1:1"
    width: int
    height: int
    max_duration: float  # seconds
    max_file_size_mb: float  # MB
    formats: List[str]  # e.g., ["mp4", "mov"]
    description: str


# Platform specifications
PLATFORM_SPECS: List[PlatformSpec] = [
    PlatformSpec(
        platform=Platform.INSTAGRAM,
        name="Instagram Reels",
        aspect_ratio="9:16",
        width=1080,
        height=1920,
        max_duration=90.0,  # 90 seconds
        max_file_size_mb=4000.0,  # 4GB
        formats=["mp4"],
        description="Vertical video format for Instagram Reels",
    ),
    PlatformSpec(
        platform=Platform.TIKTOK,
        name="TikTok",
        aspect_ratio="9:16",
        width=1080,
        height=1920,
        max_duration=60.0,  # 60 seconds
        max_file_size_mb=287.0,  # 287MB
        formats=["mp4", "mov"],
        description="Vertical video format for TikTok",
    ),
    PlatformSpec(
        platform=Platform.YOUTUBE,
        name="YouTube Shorts",
        aspect_ratio="9:16",
        width=1080,
        height=1920,
        max_duration=60.0,  # 60 seconds
        max_file_size_mb=256000.0,  # 256GB (very high limit)
        formats=["mp4", "mov", "webm"],
        description="Vertical video format for YouTube Shorts",
    ),
    PlatformSpec(
        platform=Platform.LINKEDIN,
        name="LinkedIn Video",
        aspect_ratio="16:9",
        width=1920,
        height=1080,
        max_duration=600.0,  # 10 minutes
        max_file_size_mb=5000.0,  # 5GB
        formats=["mp4"],
        description="Horizontal video format for LinkedIn",
    ),
    PlatformSpec(
        platform=Platform.LINKEDIN,
        name="LinkedIn Video (Square)",
        aspect_ratio="1:1",
        width=1080,
        height=1080,
        max_duration=600.0,  # 10 minutes
        max_file_size_mb=5000.0,  # 5GB
        formats=["mp4"],
        description="Square video format for LinkedIn",
    ),
    PlatformSpec(
        platform=Platform.FACEBOOK,
        name="Facebook Video",
        aspect_ratio="16:9",
        width=1920,
        height=1080,
        max_duration=240.0,  # 240 seconds (4 minutes)
        max_file_size_mb=4000.0,  # 4GB
        formats=["mp4", "mov"],
        description="Horizontal video format for Facebook",
    ),
    PlatformSpec(
        platform=Platform.FACEBOOK,
        name="Facebook Video (Square)",
        aspect_ratio="1:1",
        width=1080,
        height=1080,
        max_duration=240.0,  # 240 seconds
        max_file_size_mb=4000.0,  # 4GB
        formats=["mp4", "mov"],
        description="Square video format for Facebook",
    ),
    PlatformSpec(
        platform=Platform.TWITTER,
        name="Twitter/X Video",
        aspect_ratio="16:9",
        width=1920,
        height=1080,
        max_duration=140.0,  # 140 seconds (2:20)
        max_file_size_mb=512.0,  # 512MB
        formats=["mp4"],
        description="Horizontal video format for Twitter/X",
    ),
]


def get_platform_specs(platform: Platform) -> List[PlatformSpec]:
    """Get all specifications for a platform."""
    return [spec for spec in PLATFORM_SPECS if spec.platform == platform]


def get_platform_spec(platform: Platform, aspect_ratio: Optional[str] = None) -> Optional[PlatformSpec]:
    """Get a specific platform specification."""
    specs = get_platform_specs(platform)
    if aspect_ratio:
        for spec in specs:
            if spec.aspect_ratio == aspect_ratio:
                return spec
    return specs[0] if specs else None


def get_all_platforms() -> List[Platform]:
    """Get all available platforms."""
    return list(Platform)


def get_platform_by_name(name: str) -> Optional[Platform]:
    """Get platform enum by name."""
    name_lower = name.lower()
    for platform in Platform:
        if platform.value == name_lower:
            return platform
    return None
