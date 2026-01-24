"""Configuration for YouTube API Facade"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class YouTubeConfig:
    """Configuration class for YouTube API Facade."""

    # Environment settings
    environment: str = field(default_factory=lambda: os.getenv("ENVIRONMENT", "development"))
    version: str = "2.0.0"  # Refactored version

    # Feature flags for gradual rollout
    enable_planning: bool = True
    enable_scenes: bool = True
    enable_rendering: bool = True
    enable_assets: bool = True

    # Performance settings
    max_concurrent_requests: int = 20
    request_timeout_seconds: int = 300  # 5 minutes for video operations
    max_video_size_mb: int = 500

    # Video processing settings
    max_scenes_per_video: int = 20
    max_video_duration_seconds: int = 600  # 10 minutes
    supported_resolutions: list = field(default_factory=lambda: ["480p", "720p", "1080p"])
    default_resolution: str = "720p"

    # AI and generation settings
    enable_ai_enhancement: bool = True
    enable_trend_analysis: bool = False
    enable_enhanced_analysis: bool = True
    max_ai_retries: int = 3

    # Cost and billing settings
    enable_cost_tracking: bool = True
    enable_cost_estimation: bool = True
    max_cost_per_video: float = 50.0

    # Storage settings
    enable_asset_library: bool = True
    asset_retention_days: int = 365
    max_assets_per_user: int = 1000

    # Monitoring settings
    enable_metrics: bool = True
    metrics_retention_days: int = 30
    enable_health_checks: bool = True
    health_check_interval_seconds: int = 60

    # Logging settings
    log_level: str = "INFO"
    enable_request_logging: bool = True
    enable_performance_logging: bool = True

    # Security settings
    enable_rate_limiting: bool = True
    rate_limit_requests_per_minute: int = 30
    enable_cors: bool = True

    @classmethod
    def _get_bool_env(cls, key: str, default: bool = False) -> bool:
        """Get boolean value from environment variable."""
        value = os.getenv(key, str(default)).lower()
        return value in ("true", "1", "yes", "on")

    @classmethod
    def from_env(cls) -> "YouTubeConfig":
        """Create configuration from environment variables."""
        return cls(
            environment=os.getenv("ENVIRONMENT", "development"),
            enable_planning=cls._get_bool_env("YOUTUBE_ENABLE_PLANNING", True),
            enable_scenes=cls._get_bool_env("YOUTUBE_ENABLE_SCENES", True),
            enable_rendering=cls._get_bool_env("YOUTUBE_ENABLE_RENDERING", True),
            enable_assets=cls._get_bool_env("YOUTUBE_ENABLE_ASSETS", True),
            max_concurrent_requests=int(os.getenv("YOUTUBE_MAX_CONCURRENT", "20")),
            request_timeout_seconds=int(os.getenv("YOUTUBE_TIMEOUT", "300")),
            max_video_size_mb=int(os.getenv("YOUTUBE_MAX_VIDEO_SIZE_MB", "500")),
            max_scenes_per_video=int(os.getenv("YOUTUBE_MAX_SCENES", "20")),
            max_video_duration_seconds=int(os.getenv("YOUTUBE_MAX_DURATION", "600")),
            default_resolution=os.getenv("YOUTUBE_DEFAULT_RESOLUTION", "720p"),
            enable_ai_enhancement=cls._get_bool_env("YOUTUBE_AI_ENHANCEMENT", True),
            enable_trend_analysis=cls._get_bool_env("YOUTUBE_TREND_ANALYSIS", False),
            enable_enhanced_analysis=cls._get_bool_env("YOUTUBE_ENHANCED_ANALYSIS", True),
            max_ai_retries=int(os.getenv("YOUTUBE_MAX_AI_RETRIES", "3")),
            enable_cost_tracking=cls._get_bool_env("YOUTUBE_COST_TRACKING", True),
            enable_cost_estimation=cls._get_bool_env("YOUTUBE_COST_ESTIMATION", True),
            max_cost_per_video=float(os.getenv("YOUTUBE_MAX_COST_PER_VIDEO", "50.0")),
            enable_asset_library=cls._get_bool_env("YOUTUBE_ASSET_LIBRARY", True),
            asset_retention_days=int(os.getenv("YOUTUBE_ASSET_RETENTION", "365")),
            max_assets_per_user=int(os.getenv("YOUTUBE_MAX_ASSETS_PER_USER", "1000")),
            enable_metrics=cls._get_bool_env("YOUTUBE_METRICS", True),
            metrics_retention_days=int(os.getenv("YOUTUBE_METRICS_RETENTION", "30")),
            enable_health_checks=cls._get_bool_env("YOUTUBE_HEALTH_CHECKS", True),
            health_check_interval_seconds=int(os.getenv("YOUTUBE_HEALTH_INTERVAL", "60")),
            log_level=os.getenv("YOUTUBE_LOG_LEVEL", "INFO"),
            enable_request_logging=cls._get_bool_env("YOUTUBE_REQUEST_LOGGING", True),
            enable_performance_logging=cls._get_bool_env("YOUTUBE_PERFORMANCE_LOGGING", True),
            enable_rate_limiting=cls._get_bool_env("YOUTUBE_RATE_LIMITING", True),
            rate_limit_requests_per_minute=int(os.getenv("YOUTUBE_RATE_LIMIT", "30")),
            enable_cors=cls._get_bool_env("YOUTUBE_CORS", True),
        )

    @property
    def enabled_features(self) -> list:
        """Get list of enabled features."""
        features = []
        if self.enable_planning:
            features.append("planning")
        if self.enable_scenes:
            features.append("scenes")
        if self.enable_rendering:
            features.append("rendering")
        if self.enable_assets:
            features.append("assets")
        return features

    @property
    def disabled_features(self) -> list:
        """Get list of disabled features."""
        features = []
        if not self.enable_planning:
            features.append("planning")
        if not self.enable_scenes:
            features.append("scenes")
        if not self.enable_rendering:
            features.append("rendering")
        if not self.enable_assets:
            features.append("assets")
        return features

    @property
    def total_enabled_endpoints(self) -> int:
        """Calculate total enabled endpoints across all features."""
        count = 0
        if self.enable_planning:
            count += 2  # plan, scenes endpoint
        if self.enable_scenes:
            count += 2  # scenes, update_scene
        if self.enable_rendering:
            count += 4  # render, scene, status, combine
        if self.enable_assets:
            count += 3  # videos, estimate-cost, serve_video
        return count

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "version": self.version,
            "environment": self.environment,
            "features": {
                "planning": {
                    "enabled": self.enable_planning,
                    "description": "Video planning and AI-enhanced content generation"
                },
                "scenes": {
                    "enabled": self.enable_scenes,
                    "description": "Scene building and management"
                },
                "rendering": {
                    "enabled": self.enable_rendering,
                    "description": "Video rendering and processing"
                },
                "assets": {
                    "enabled": self.enable_assets,
                    "description": "Asset management and file serving"
                }
            },
            "performance": {
                "max_concurrent_requests": self.max_concurrent_requests,
                "request_timeout_seconds": self.request_timeout_seconds,
                "max_video_size_mb": self.max_video_size_mb,
                "max_scenes_per_video": self.max_scenes_per_video,
                "max_video_duration_seconds": self.max_video_duration_seconds,
                "supported_resolutions": self.supported_resolutions,
                "default_resolution": self.default_resolution
            },
            "ai_settings": {
                "enable_ai_enhancement": self.enable_ai_enhancement,
                "enable_trend_analysis": self.enable_trend_analysis,
                "enable_enhanced_analysis": self.enable_enhanced_analysis,
                "max_ai_retries": self.max_ai_retries
            },
            "cost_settings": {
                "enable_cost_tracking": self.enable_cost_tracking,
                "enable_cost_estimation": self.enable_cost_estimation,
                "max_cost_per_video": self.max_cost_per_video
            },
            "storage_settings": {
                "enable_asset_library": self.enable_asset_library,
                "asset_retention_days": self.asset_retention_days,
                "max_assets_per_user": self.max_assets_per_user
            },
            "monitoring": {
                "enable_metrics": self.enable_metrics,
                "metrics_retention_days": self.metrics_retention_days,
                "enable_health_checks": self.enable_health_checks,
                "health_check_interval_seconds": self.health_check_interval_seconds
            },
            "logging": {
                "log_level": self.log_level,
                "enable_request_logging": self.enable_request_logging,
                "enable_performance_logging": self.enable_performance_logging
            },
            "security": {
                "enable_rate_limiting": self.enable_rate_limiting,
                "rate_limit_requests_per_minute": self.rate_limit_requests_per_minute,
                "enable_cors": self.enable_cors
            },
            "summary": {
                "enabled_features": self.enabled_features,
                "disabled_features": self.disabled_features,
                "total_enabled_endpoints": self.total_enabled_endpoints
            }
        }


# Create global configuration instance
config = YouTubeConfig.from_env()