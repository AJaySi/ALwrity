"""
Configuration management for the AI Backlinking service.

Provides centralized configuration management with environment variable support,
validation, and default values for all service settings.
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from loguru import logger

from .exceptions import ConfigurationError


@dataclass
class EmailConfig:
    """Email service configuration."""
    smtp_timeout: int = 30
    imap_timeout: int = 30
    max_follow_ups: int = 3
    max_bulk_send: int = 50
    rate_limit_per_hour: int = 100

    # Default email settings
    default_smtp_server: str = "smtp.gmail.com"
    default_smtp_port: int = 587
    default_imap_server: str = "imap.gmail.com"
    default_imap_port: int = 993


@dataclass
class ScrapingConfig:
    """Web scraping configuration."""
    max_concurrent_requests: int = 5
    request_timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    user_agent: str = "ALwrity-Backlinking/1.0"

    # Rate limiting
    requests_per_minute: int = 30
    domain_delay: float = 2.0

    # Content limits
    max_content_length: int = 5_000_000  # 5MB
    max_title_length: int = 200
    max_description_length: int = 500


@dataclass
class ProspectAnalysisConfig:
    """Configuration for enhanced prospect analysis features."""
    enable_enhanced_analysis: bool = True
    deep_analysis_threshold: int = 10  # Max prospects for deep analysis
    cache_analysis_results: bool = True
    analysis_cache_ttl_hours: int = 24
    max_competitors_for_analysis: int = 3
    analysis_timeout_seconds: int = 120
    enable_competitor_discovery: bool = False  # Disabled by default for performance


@dataclass
class AIConfig:
    """AI service configuration."""
    text_generation_timeout: int = 60
    max_tokens: int = 2000
    temperature: float = 0.7
    model_preference: str = "gemini"  # gemini, openai, or auto

    # Prompt templates
    email_prompt_template: str = ""
    analysis_prompt_template: str = ""


@dataclass
class CampaignConfig:
    """Campaign management configuration."""
    max_campaigns_per_user: int = 10
    max_opportunities_per_campaign: int = 100
    campaign_timeout_days: int = 30
    auto_archive_after_days: int = 90

    # Email tracking
    email_tracking_enabled: bool = True
    response_check_interval_hours: int = 24


@dataclass
class BacklinkingConfig:
    """Main configuration class for AI Backlinking service."""
    email: EmailConfig = field(default_factory=EmailConfig)
    scraping: ScrapingConfig = field(default_factory=ScrapingConfig)
    ai: AIConfig = field(default_factory=AIConfig)
    campaign: CampaignConfig = field(default_factory=CampaignConfig)
    prospect_analysis: ProspectAnalysisConfig = field(default_factory=ProspectAnalysisConfig)

    # Service-wide settings
    debug_mode: bool = False
    log_level: str = "INFO"
    enable_metrics: bool = True

    # External service integrations
    firecrawl_enabled: bool = False
    firecrawl_api_key: Optional[str] = None
    exa_enabled: bool = False
    exa_api_key: Optional[str] = None

    def __post_init__(self):
        """Load configuration from environment variables."""
        self._load_from_environment()

    def _load_from_environment(self) -> None:
        """Load configuration values from environment variables."""
        # Email configuration
        self.email.smtp_timeout = self._get_int_env("BACKLINKING_SMTP_TIMEOUT", self.email.smtp_timeout)
        self.email.imap_timeout = self._get_int_env("BACKLINKING_IMAP_TIMEOUT", self.email.imap_timeout)
        self.email.max_follow_ups = self._get_int_env("BACKLINKING_MAX_FOLLOW_UPS", self.email.max_follow_ups)
        self.email.max_bulk_send = self._get_int_env("BACKLINKING_MAX_BULK_SEND", self.email.max_bulk_send)
        self.email.rate_limit_per_hour = self._get_int_env("BACKLINKING_EMAIL_RATE_LIMIT", self.email.rate_limit_per_hour)

        # Scraping configuration
        self.scraping.max_concurrent_requests = self._get_int_env(
            "BACKLINKING_MAX_CONCURRENT_REQUESTS", self.scraping.max_concurrent_requests
        )
        self.scraping.request_timeout = self._get_int_env("BACKLINKING_REQUEST_TIMEOUT", self.scraping.request_timeout)
        self.scraping.max_retries = self._get_int_env("BACKLINKING_MAX_RETRIES", self.scraping.max_retries)
        self.scraping.retry_delay = self._get_float_env("BACKLINKING_RETRY_DELAY", self.scraping.retry_delay)
        self.scraping.requests_per_minute = self._get_int_env(
            "BACKLINKING_REQUESTS_PER_MINUTE", self.scraping.requests_per_minute
        )
        self.scraping.user_agent = os.getenv("BACKLINKING_USER_AGENT", self.scraping.user_agent)

        # AI configuration
        self.ai.text_generation_timeout = self._get_int_env(
            "BACKLINKING_AI_TIMEOUT", self.ai.text_generation_timeout
        )
        self.ai.max_tokens = self._get_int_env("BACKLINKING_MAX_TOKENS", self.ai.max_tokens)
        self.ai.temperature = self._get_float_env("BACKLINKING_AI_TEMPERATURE", self.ai.temperature)
        self.ai.model_preference = os.getenv("BACKLINKING_AI_MODEL", self.ai.model_preference)

        # Campaign configuration
        self.campaign.max_campaigns_per_user = self._get_int_env(
            "BACKLINKING_MAX_CAMPAIGNS_PER_USER", self.campaign.max_campaigns_per_user
        )
        self.campaign.max_opportunities_per_campaign = self._get_int_env(
            "BACKLINKING_MAX_OPPORTUNITIES_PER_CAMPAIGN", self.campaign.max_opportunities_per_campaign
        )
        self.campaign.campaign_timeout_days = self._get_int_env(
            "BACKLINKING_CAMPAIGN_TIMEOUT_DAYS", self.campaign.campaign_timeout_days
        )
        self.campaign.auto_archive_after_days = self._get_int_env(
            "BACKLINKING_AUTO_ARCHIVE_DAYS", self.campaign.auto_archive_after_days
        )

        # Service-wide settings
        self.debug_mode = self._get_bool_env("BACKLINKING_DEBUG_MODE", self.debug_mode)
        self.log_level = os.getenv("BACKLINKING_LOG_LEVEL", self.log_level)
        self.enable_metrics = self._get_bool_env("BACKLINKING_ENABLE_METRICS", self.enable_metrics)

        # External integrations
        self.firecrawl_enabled = self._get_bool_env("BACKLINKING_FIRECRAWL_ENABLED", self.firecrawl_enabled)
        self.firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY")
        self.exa_enabled = self._get_bool_env("BACKLINKING_EXA_ENABLED", self.exa_enabled)
        self.exa_api_key = os.getenv("EXA_API_KEY")

    def _get_int_env(self, key: str, default: int) -> int:
        """Get integer value from environment variable."""
        value = os.getenv(key)
        if value is not None:
            try:
                return int(value)
            except ValueError:
                logger.warning(f"Invalid integer value for {key}: {value}, using default {default}")
        return default

    def _get_float_env(self, key: str, default: float) -> float:
        """Get float value from environment variable."""
        value = os.getenv(key)
        if value is not None:
            try:
                return float(value)
            except ValueError:
                logger.warning(f"Invalid float value for {key}: {value}, using default {default}")
        return default

    def _get_bool_env(self, key: str, default: bool) -> bool:
        """Get boolean value from environment variable."""
        value = os.getenv(key, "").lower()
        if value in ("true", "1", "yes", "on"):
            return True
        if value in ("false", "0", "no", "off"):
            return False
        return default

    def validate(self) -> None:
        """
        Validate configuration values.

        Raises:
            ConfigurationError: If configuration is invalid
        """
        # Validate email settings
        if self.email.smtp_timeout <= 0:
            raise ConfigurationError("BACKLINKING_SMTP_TIMEOUT", "SMTP timeout must be positive")
        if self.email.imap_timeout <= 0:
            raise ConfigurationError("BACKLINKING_IMAP_TIMEOUT", "IMAP timeout must be positive")
        if self.email.max_follow_ups < 0:
            raise ConfigurationError("BACKLINKING_MAX_FOLLOW_UPS", "Max follow-ups cannot be negative")

        # Validate scraping settings
        if self.scraping.max_concurrent_requests <= 0:
            raise ConfigurationError("BACKLINKING_MAX_CONCURRENT_REQUESTS", "Max concurrent requests must be positive")
        if self.scraping.request_timeout <= 0:
            raise ConfigurationError("BACKLINKING_REQUEST_TIMEOUT", "Request timeout must be positive")

        # Validate AI settings
        if self.ai.text_generation_timeout <= 0:
            raise ConfigurationError("BACKLINKING_AI_TIMEOUT", "AI timeout must be positive")
        if not self.ai.model_preference in ["gemini", "openai", "auto"]:
            raise ConfigurationError("BACKLINKING_AI_MODEL", "AI model must be 'gemini', 'openai', or 'auto'")

        # Validate campaign settings
        if self.campaign.max_campaigns_per_user <= 0:
            raise ConfigurationError("BACKLINKING_MAX_CAMPAIGNS_PER_USER", "Max campaigns per user must be positive")

        # Validate external integrations
        if self.firecrawl_enabled and not self.firecrawl_api_key:
            raise ConfigurationError("FIRECRAWL_API_KEY", "Firecrawl API key required when enabled")
        if self.exa_enabled and not self.exa_api_key:
            raise ConfigurationError("EXA_API_KEY", "Exa API key required when enabled")

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary for logging/debugging."""
        return {
            "email": {
                "smtp_timeout": self.email.smtp_timeout,
                "imap_timeout": self.email.imap_timeout,
                "max_follow_ups": self.email.max_follow_ups,
                "max_bulk_send": self.email.max_bulk_send,
                "rate_limit_per_hour": self.email.rate_limit_per_hour,
            },
            "scraping": {
                "max_concurrent_requests": self.scraping.max_concurrent_requests,
                "request_timeout": self.scraping.request_timeout,
                "max_retries": self.scraping.max_retries,
                "requests_per_minute": self.scraping.requests_per_minute,
            },
            "ai": {
                "text_generation_timeout": self.ai.text_generation_timeout,
                "max_tokens": self.ai.max_tokens,
                "temperature": self.ai.temperature,
                "model_preference": self.ai.model_preference,
            },
            "campaign": {
                "max_campaigns_per_user": self.campaign.max_campaigns_per_user,
                "max_opportunities_per_campaign": self.campaign.max_opportunities_per_campaign,
                "campaign_timeout_days": self.campaign.campaign_timeout_days,
            },
            "integrations": {
                "firecrawl_enabled": self.firecrawl_enabled,
                "exa_enabled": self.exa_enabled,
            },
            "service": {
                "debug_mode": self.debug_mode,
                "log_level": self.log_level,
                "enable_metrics": self.enable_metrics,
            }
        }


# Global configuration instance
_config: Optional[BacklinkingConfig] = None


def get_config() -> BacklinkingConfig:
    """
    Get the global backlinking configuration instance.

    Returns:
        BacklinkingConfig: The configuration instance

    Raises:
        ConfigurationError: If configuration validation fails
    """
    global _config
    if _config is None:
        _config = BacklinkingConfig()
        _config.validate()
        logger.info("Backlinking configuration loaded and validated")
        if _config.debug_mode:
            logger.debug(f"Configuration: {_config.to_dict()}")
    return _config


def reload_config() -> BacklinkingConfig:
    """
    Reload configuration from environment variables.

    Returns:
        BacklinkingConfig: Fresh configuration instance
    """
    global _config
    _config = BacklinkingConfig()
    _config.validate()
    logger.info("Backlinking configuration reloaded")
    return _config