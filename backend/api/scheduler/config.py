"""Configuration for Scheduler API Facade"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class SchedulerConfig:
    """Configuration class for Scheduler API Facade."""

    # Environment settings
    environment: str = field(default_factory=lambda: os.getenv("ENVIRONMENT", "development"))
    version: str = "3.0.0"  # Refactored version

    # Feature flags for gradual rollout
    enable_dashboard: bool = True
    enable_monitoring: bool = True
    enable_tasks: bool = True
    enable_platform: bool = True

    # Performance settings
    max_concurrent_requests: int = 50
    request_timeout_seconds: int = 120  # 2 minutes for complex operations
    max_response_size_mb: int = 10

    # Database settings
    db_connection_pool_size: int = 10
    db_connection_timeout: int = 30

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
    rate_limit_requests_per_minute: int = 100
    enable_cors: bool = True

    @classmethod
    def from_env(cls) -> "SchedulerConfig":
        """Create configuration from environment variables."""
        return cls(
            environment=os.getenv("ENVIRONMENT", "development"),
            enable_dashboard=cls._get_bool_env("SCHEDULER_ENABLE_DASHBOARD", True),
            enable_monitoring=cls._get_bool_env("SCHEDULER_ENABLE_MONITORING", True),
            enable_tasks=cls._get_bool_env("SCHEDULER_ENABLE_TASKS", True),
            enable_platform=cls._get_bool_env("SCHEDULER_ENABLE_PLATFORM", True),
            max_concurrent_requests=int(os.getenv("SCHEDULER_MAX_CONCURRENT", "50")),
            request_timeout_seconds=int(os.getenv("SCHEDULER_TIMEOUT", "120")),
            max_response_size_mb=int(os.getenv("SCHEDULER_MAX_RESPONSE_SIZE_MB", "10")),
            enable_metrics=cls._get_bool_env("SCHEDULER_METRICS", True),
            metrics_retention_days=int(os.getenv("SCHEDULER_METRICS_RETENTION", "30")),
            enable_health_checks=cls._get_bool_env("SCHEDULER_HEALTH_CHECKS", True),
            health_check_interval_seconds=int(os.getenv("SCHEDULER_HEALTH_INTERVAL", "60")),
            log_level=os.getenv("SCHEDULER_LOG_LEVEL", "INFO"),
            enable_request_logging=cls._get_bool_env("SCHEDULER_REQUEST_LOGGING", True),
            enable_performance_logging=cls._get_bool_env("SCHEDULER_PERF_LOGGING", True),
            enable_rate_limiting=cls._get_bool_env("SCHEDULER_RATE_LIMITING", True),
            rate_limit_requests_per_minute=int(os.getenv("SCHEDULER_RATE_LIMIT", "100")),
            enable_cors=cls._get_bool_env("SCHEDULER_CORS", True),
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
            "dashboard": self.enable_dashboard,
            "monitoring": self.enable_monitoring,
            "tasks": self.enable_tasks,
            "platform": self.enable_platform,
        }

    @property
    def enabled_features(self) -> list[str]:
        """Get list of enabled features."""
        return [feature for feature, enabled in self.feature_flags.items() if enabled]

    @property
    def disabled_features(self) -> list[str]:
        """Get list of disabled features."""
        return [feature for feature, enabled in self.feature_flags.items() if not enabled]

    @property
    def total_enabled_endpoints(self) -> int:
        """Calculate total enabled endpoints based on feature flags."""
        base_counts = {
            "dashboard": 3,
            "monitoring": 5,
            "tasks": 4,
            "platform": 4
        }

        total = 0
        for feature, enabled in self.feature_flags.items():
            if enabled:
                total += base_counts.get(feature, 0)

        return total

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.environment.lower() == "development"

    def can_enable_feature(self, feature: str) -> bool:
        """Check if a feature can be safely enabled."""
        # In production, be more conservative
        if self.is_production and feature not in ["dashboard", "monitoring"]:
            return False
        return True

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "environment": self.environment,
            "version": self.version,
            "feature_flags": self.feature_flags,
            "enabled_features": self.enabled_features,
            "disabled_features": self.disabled_features,
            "total_enabled_endpoints": self.total_enabled_endpoints,
            "is_production": self.is_production,
            "is_development": self.is_development,
            "performance_settings": {
                "max_concurrent_requests": self.max_concurrent_requests,
                "request_timeout_seconds": self.request_timeout_seconds,
                "max_response_size_mb": self.max_response_size_mb,
            },
            "monitoring_settings": {
                "enable_metrics": self.enable_metrics,
                "metrics_retention_days": self.metrics_retention_days,
                "enable_health_checks": self.enable_health_checks,
                "health_check_interval_seconds": self.health_check_interval_seconds,
            },
            "security_settings": {
                "enable_rate_limiting": self.enable_rate_limiting,
                "rate_limit_requests_per_minute": self.rate_limit_requests_per_minute,
                "enable_cors": self.enable_cors,
            }
        }


# Global configuration instance
config = SchedulerConfig.from_env()