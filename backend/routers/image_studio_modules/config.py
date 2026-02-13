"""Configuration for Image Studio API."""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class ImageStudioConfig:
    """Configuration class for Image Studio API."""

    # Feature flags for gradual rollout
    enable_generation: bool = True
    enable_editing: bool = True
    enable_advanced: bool = True
    enable_utilities: bool = True

    # Performance settings
    max_concurrent_requests: int = 10
    request_timeout_seconds: int = 300  # 5 minutes
    max_image_size_mb: int = 50

    # Monitoring settings
    enable_metrics: bool = False
    metrics_retention_days: int = 30

    # Deployment settings
    environment: str = "development"
    version: str = "2.0.0"

    @classmethod
    def from_env(cls) -> "ImageStudioConfig":
        """Create configuration from environment variables."""
        return cls(
            enable_generation=cls._get_bool_env("IMAGE_STUDIO_ENABLE_GENERATION", True),
            enable_editing=cls._get_bool_env("IMAGE_STUDIO_ENABLE_EDITING", True),
            enable_advanced=cls._get_bool_env("IMAGE_STUDIO_ENABLE_ADVANCED", True),
            enable_utilities=cls._get_bool_env("IMAGE_STUDIO_ENABLE_UTILITIES", True),
            max_concurrent_requests=int(os.getenv("IMAGE_STUDIO_MAX_CONCURRENT", "10")),
            request_timeout_seconds=int(os.getenv("IMAGE_STUDIO_TIMEOUT", "300")),
            max_image_size_mb=int(os.getenv("IMAGE_STUDIO_MAX_SIZE_MB", "50")),
            enable_metrics=cls._get_bool_env("IMAGE_STUDIO_METRICS", False),
            metrics_retention_days=int(os.getenv("IMAGE_STUDIO_METRICS_RETENTION", "30")),
            environment=os.getenv("ENVIRONMENT", "development"),
        )

    @staticmethod
    def _get_bool_env(key: str, default: bool = False) -> bool:
        """Get boolean value from environment variable."""
        value = os.getenv(key, str(default)).lower()
        return value in ("true", "1", "yes", "on")

    @property
    def feature_flags(self) -> Dict[str, bool]:
        """Get feature flags as dictionary."""
        return {
            "generation": self.enable_generation,
            "editing": self.enable_editing,
            "advanced": self.enable_advanced,
            "utilities": self.enable_utilities,
        }

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment.lower() == "production"

    @property
    def total_enabled_endpoints(self) -> int:
        """Calculate total enabled endpoints based on feature flags."""
        base_counts = {
            "generation": 6,
            "editing": 7,
            "advanced": 10,
            "utilities": 10,
        }

        total = 0
        for feature, enabled in self.feature_flags.items():
            if enabled:
                total += base_counts.get(feature, 0)

        return total

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "enable_generation": self.enable_generation,
            "enable_editing": self.enable_editing,
            "enable_advanced": self.enable_advanced,
            "enable_utilities": self.enable_utilities,
            "max_concurrent_requests": self.max_concurrent_requests,
            "request_timeout_seconds": self.request_timeout_seconds,
            "max_image_size_mb": self.max_image_size_mb,
            "enable_metrics": self.enable_metrics,
            "metrics_retention_days": self.metrics_retention_days,
            "environment": self.environment,
            "version": self.version,
            "feature_flags": self.feature_flags,
            "total_enabled_endpoints": self.total_enabled_endpoints,
            "is_production": self.is_production,
        }


# Global configuration instance
config = ImageStudioConfig.from_env()