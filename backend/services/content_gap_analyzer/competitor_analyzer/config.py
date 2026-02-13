"""
Configuration Management for Competitor Analyzer Service

This module provides configuration management with environment support
and AI provider integration using the existing llm_text_gen service.
"""

import os
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from functools import lru_cache
from loguru import logger

from .constants import (
    DEFAULT_AI_CONFIDENCE_SCORE,
    AI_RETRY_ATTEMPTS,
    AI_TIMEOUT_SECONDS,
    AI_MAX_TOKENS,
    DEFAULT_PROCESSING_TIMEOUT,
    BATCH_PROCESSING_SIZE,
    CONCURRENT_ANALYSIS_LIMIT,
    DEFAULT_CACHE_TTL,
    HEALTH_CHECK_TIMEOUT,
    MAX_RESPONSE_TIME_THRESHOLD,
    ERROR_RATE_THRESHOLD,
)


class AIProviderConfig(BaseModel):
    """Configuration for AI providers."""
    
    name: str = Field(..., description="AI provider name")
    enabled: bool = Field(default=True, description="Whether provider is enabled")
    priority: int = Field(default=1, description="Provider priority (1 = highest)")
    max_tokens: int = Field(default=AI_MAX_TOKENS, description="Maximum tokens per request")
    timeout_seconds: int = Field(default=AI_TIMEOUT_SECONDS, description="Request timeout")
    retry_attempts: int = Field(default=AI_RETRY_ATTEMPTS, description="Number of retry attempts")
    confidence_threshold: float = Field(default=DEFAULT_AI_CONFIDENCE_SCORE, description="Minimum confidence score")
    rate_limit_per_minute: int = Field(default=60, description="Rate limit per minute")
    cost_per_request: float = Field(default=0.0, description="Cost per request")
    supports_structured_output: bool = Field(default=True, description="Supports structured JSON output")
    
    class Config:
        extra = "allow"


class AnalysisConfig(BaseModel):
    """Configuration for analysis parameters."""
    
    max_competitors_per_analysis: int = Field(default=50, description="Maximum competitors per analysis")
    max_urls_per_batch: int = Field(default=10, description="Maximum URLs processed per batch")
    max_content_pieces_per_competitor: int = Field(default=1000, description="Maximum content pieces to analyze")
    max_keywords_per_analysis: int = Field(default=100, description="Maximum keywords to analyze")
    max_recommendations_per_analysis: int = Field(default=20, description="Maximum recommendations to generate")
    processing_timeout_seconds: int = Field(default=DEFAULT_PROCESSING_TIMEOUT, description="Processing timeout")
    batch_processing_size: int = Field(default=BATCH_PROCESSING_SIZE, description="Batch processing size")
    concurrent_analysis_limit: int = Field(default=CONCURRENT_ANALYSIS_LIMIT, description="Concurrent analysis limit")
    enable_caching: bool = Field(default=True, description="Enable result caching")
    cache_ttl_seconds: int = Field(default=DEFAULT_CACHE_TTL, description="Cache TTL in seconds")
    enable_parallel_processing: bool = Field(default=True, description="Enable parallel processing")
    
    class Config:
        extra = "allow"


class QualityThresholdsConfig(BaseModel):
    """Configuration for quality thresholds."""
    
    min_quality_score: float = Field(default=0.0, description="Minimum quality score")
    max_quality_score: float = Field(default=10.0, description="Maximum quality score")
    high_quality_threshold: float = Field(default=8.0, description="High quality threshold")
    medium_quality_threshold: float = Field(default=6.0, description="Medium quality threshold")
    low_quality_threshold: float = Field(default=4.0, description="Low quality threshold")
    
    min_domain_authority: int = Field(default=0, description="Minimum domain authority")
    max_domain_authority: int = Field(default=100, description="Maximum domain authority")
    high_domain_authority_threshold: int = Field(default=70, description="High domain authority threshold")
    medium_domain_authority_threshold: int = Field(default=40, description="Medium domain authority threshold")
    low_domain_authority_threshold: int = Field(default=20, description="Low domain authority threshold")
    
    good_page_speed_threshold: int = Field(default=85, description="Good page speed threshold")
    fair_page_speed_threshold: int = Field(default=70, description="Fair page speed threshold")
    poor_page_speed_threshold: int = Field(default=50, description="Poor page speed threshold")
    
    class Config:
        extra = "allow"


class ContentConfig(BaseModel):
    """Configuration for content analysis."""
    
    default_content_count: int = Field(default=150, description="Default content count")
    high_content_volume_threshold: int = Field(default=500, description="High content volume threshold")
    medium_content_volume_threshold: int = Field(default=200, description="Medium content volume threshold")
    low_content_volume_threshold: int = Field(default=50, description="Low content volume threshold")
    
    default_avg_word_count: int = Field(default=1000, description="Default average word count")
    long_form_content_threshold: int = Field(default=2000, description="Long form content threshold")
    short_form_content_threshold: int = Field(default=500, description="Short form content threshold")
    
    optimal_title_length: int = Field(default=55, description="Optimal title length")
    max_title_length: int = Field(default=60, description="Maximum title length")
    min_title_length: int = Field(default=30, description="Minimum title length")
    
    optimal_meta_description_length: int = Field(default=155, description="Optimal meta description length")
    max_meta_description_length: int = Field(default=160, description="Maximum meta description length")
    min_meta_description_length: int = Field(default=120, description="Minimum meta description length")
    
    optimal_keyword_density_min: float = Field(default=0.01, description="Minimum optimal keyword density")
    optimal_keyword_density_max: float = Field(default=0.05, description="Maximum optimal keyword density")
    default_keyword_density: float = Field(default=0.025, description="Default keyword density")
    
    class Config:
        extra = "allow"


class MarketConfig(BaseModel):
    """Configuration for market analysis."""
    
    default_market_share: float = Field(default=0.0, description="Default market share")
    high_market_share_threshold: float = Field(default=30.0, description="High market share threshold")
    medium_market_share_threshold: float = Field(default=10.0, description="Medium market share threshold")
    low_market_share_threshold: float = Field(default=5.0, description="Low market share threshold")
    
    default_growth_rate: float = Field(default=0.0, description="Default growth rate")
    high_growth_rate_threshold: float = Field(default=20.0, description="High growth rate threshold")
    medium_growth_rate_threshold: float = Field(default=10.0, description="Medium growth rate threshold")
    low_growth_rate_threshold: float = Field(default=5.0, description="Low growth rate threshold")
    
    class Config:
        extra = "allow"


class MonitoringConfig(BaseModel):
    """Configuration for monitoring and health checks."""
    
    health_check_timeout: int = Field(default=HEALTH_CHECK_TIMEOUT, description="Health check timeout")
    max_response_time_threshold: int = Field(default=MAX_RESPONSE_TIME_THRESHOLD, description="Max response time threshold")
    error_rate_threshold: float = Field(default=ERROR_RATE_THRESHOLD, description="Error rate threshold")
    enable_metrics_collection: bool = Field(default=True, description="Enable metrics collection")
    enable_performance_monitoring: bool = Field(default=True, description="Enable performance monitoring")
    enable_error_tracking: bool = Field(default=True, description="Enable error tracking")
    log_level: str = Field(default="INFO", description="Log level")
    
    class Config:
        extra = "allow"


class FeatureFlags(BaseModel):
    """Feature flags for gradual rollout."""
    
    enable_advanced_ai_insights: bool = Field(default=True, description="Enable advanced AI insights")
    enable_real_time_analysis: bool = Field(default=True, description="Enable real-time analysis")
    enable_predictive_analytics: bool = Field(default=False, description="Enable predictive analytics")
    enable_custom_algorithms: bool = Field(default=False, description="Enable custom algorithms")
    enable_experimental_features: bool = Field(default=False, description="Enable experimental features")
    enable_beta_features: bool = Field(default=False, description="Enable beta features")
    
    class Config:
        extra = "allow"


class CompetitorAnalyzerConfig(BaseModel):
    """Main configuration for Competitor Analyzer Service."""
    
    service_name: str = Field(default="CompetitorAnalyzer", description="Service name")
    version: str = Field(default="1.0.0", description="Service version")
    environment: str = Field(default="development", description="Environment")
    debug: bool = Field(default=False, description="Debug mode")
    
    # AI Configuration
    ai_providers: List[AIProviderConfig] = Field(default_factory=list, description="AI provider configurations")
    primary_ai_provider: str = Field(default="llm_text_gen", description="Primary AI provider")
    
    # Analysis Configuration
    analysis: AnalysisConfig = Field(default_factory=AnalysisConfig, description="Analysis configuration")
    
    # Quality Thresholds
    quality_thresholds: QualityThresholdsConfig = Field(default_factory=QualityThresholdsConfig, description="Quality thresholds")
    
    # Content Configuration
    content: ContentConfig = Field(default_factory=ContentConfig, description="Content configuration")
    
    # Market Configuration
    market: MarketConfig = Field(default_factory=MarketConfig, description="Market configuration")
    
    # Monitoring Configuration
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig, description="Monitoring configuration")
    
    # Feature Flags
    feature_flags: FeatureFlags = Field(default_factory=FeatureFlags, description="Feature flags")
    
    # Database Configuration
    database_url: Optional[str] = Field(default=None, description="Database URL")
    enable_database_caching: bool = Field(default=True, description="Enable database caching")
    
    # External Services
    enable_website_analyzer: bool = Field(default=True, description="Enable website analyzer integration")
    enable_ai_engine_service: bool = Field(default=True, description="Enable AI engine service integration")
    
    class Config:
        extra = "allow"
        env_file = ".env"
        env_prefix = "COMPETITOR_ANALYZER_"
        case_sensitive = False


@lru_cache()
def get_config() -> CompetitorAnalyzerConfig:
    """
    Get the configuration for the Competitor Analyzer Service.
    
    Returns:
        CompetitorAnalyzerConfig: The configuration object
    """
    try:
        # Load configuration from environment and defaults
        config = CompetitorAnalyzerConfig()
        
        # Set up default AI providers if none configured
        if not config.ai_providers:
            config.ai_providers = [
                AIProviderConfig(
                    name="llm_text_gen",
                    enabled=True,
                    priority=1,
                    supports_structured_output=True,
                    confidence_threshold=DEFAULT_AI_CONFIDENCE_SCORE
                ),
                AIProviderConfig(
                    name="gemini",
                    enabled=True,
                    priority=2,
                    supports_structured_output=True,
                    confidence_threshold=DEFAULT_AI_CONFIDENCE_SCORE
                )
            ]
        
        # Validate primary AI provider
        provider_names = [provider.name for provider in config.ai_providers if provider.enabled]
        if config.primary_ai_provider not in provider_names:
            if provider_names:
                config.primary_ai_provider = provider_names[0]
                logger.warning(f"Primary AI provider not found, using: {config.primary_ai_provider}")
            else:
                logger.error("No enabled AI providers found")
        
        logger.info(f"Configuration loaded for {config.service_name} v{config.version}")
        logger.info(f"Environment: {config.environment}")
        logger.info(f"Primary AI Provider: {config.primary_ai_provider}")
        logger.info(f"Enabled AI Providers: {provider_names}")
        
        return config
        
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        # Return default configuration
        return CompetitorAnalyzerConfig()


def get_ai_provider_config(provider_name: str) -> Optional[AIProviderConfig]:
    """
    Get configuration for a specific AI provider.
    
    Args:
        provider_name: Name of the AI provider
        
    Returns:
        AIProviderConfig: Provider configuration or None if not found
    """
    config = get_config()
    for provider in config.ai_providers:
        if provider.name == provider_name:
            return provider
    return None


def get_enabled_ai_providers() -> List[str]:
    """
    Get list of enabled AI providers.
    
    Returns:
        List[str]: List of enabled provider names
    """
    config = get_config()
    return [provider.name for provider in config.ai_providers if provider.enabled]


def is_feature_enabled(feature_name: str) -> bool:
    """
    Check if a feature is enabled.
    
    Args:
        feature_name: Name of the feature
        
    Returns:
        bool: Whether the feature is enabled
    """
    config = get_config()
    feature_flags = config.feature_flags.dict()
    return feature_flags.get(feature_name, False)


def update_config(updates: Dict[str, Any]) -> CompetitorAnalyzerConfig:
    """
    Update configuration with new values.
    
    Args:
        updates: Dictionary of configuration updates
        
    Returns:
        CompetitorAnalyzerConfig: Updated configuration
    """
    config = get_config()
    
    # Clear the cache to force reload
    get_config.cache_clear()
    
    # Apply updates
    for key, value in updates.items():
        if hasattr(config, key):
            setattr(config, key, value)
        else:
            logger.warning(f"Unknown configuration key: {key}")
    
    logger.info("Configuration updated")
    return config


def validate_config(config: CompetitorAnalyzerConfig) -> bool:
    """
    Validate configuration values.
    
    Args:
        config: Configuration to validate
        
    Returns:
        bool: Whether configuration is valid
    """
    try:
        # Validate AI providers
        if not config.ai_providers:
            logger.error("No AI providers configured")
            return False
        
        enabled_providers = [p for p in config.ai_providers if p.enabled]
        if not enabled_providers:
            logger.error("No enabled AI providers")
            return False
        
        # Validate primary provider
        if config.primary_ai_provider not in [p.name for p in enabled_providers]:
            logger.error("Primary AI provider not in enabled providers")
            return False
        
        # Validate thresholds
        if config.quality_thresholds.min_quality_score > config.quality_thresholds.max_quality_score:
            logger.error("Invalid quality score range")
            return False
        
        if config.analysis.max_competitors_per_analysis <= 0:
            logger.error("Invalid max competitors per analysis")
            return False
        
        logger.info("Configuration validation passed")
        return True
        
    except Exception as e:
        logger.error(f"Configuration validation error: {e}")
        return False


def get_environment_config() -> Dict[str, Any]:
    """
    Get configuration from environment variables.
    
    Returns:
        Dict[str, Any]: Environment configuration
    """
    env_config = {}
    
    # Map environment variables to configuration keys
    env_mappings = {
        'COMPETITOR_ANALYZER_ENVIRONMENT': 'environment',
        'COMPETITOR_ANALYZER_DEBUG': 'debug',
        'COMPETITOR_ANALYZER_PRIMARY_AI_PROVIDER': 'primary_ai_provider',
        'COMPETITOR_ANALYZER_DATABASE_URL': 'database_url',
        'COMPETITOR_ANALYZER_LOG_LEVEL': 'monitoring.log_level',
    }
    
    for env_var, config_key in env_mappings.items():
        value = os.getenv(env_var)
        if value is not None:
            # Convert string values to appropriate types
            if config_key == 'debug':
                value = value.lower() in ('true', '1', 'yes', 'on')
            elif config_key in ['monitoring.log_level']:
                value = value.upper()
            
            # Handle nested keys
            if '.' in config_key:
                keys = config_key.split('.')
                current = env_config
                for key in keys[:-1]:
                    if key not in current:
                        current[key] = {}
                    current = current[key]
                current[keys[-1]] = value
            else:
                env_config[config_key] = value
    
    return env_config


# Initialize configuration on import
try:
    config = get_config()
    if validate_config(config):
        logger.info("✅ Competitor Analyzer configuration initialized successfully")
    else:
        logger.warning("⚠️ Competitor Analyzer configuration validation failed")
except Exception as e:
    logger.error(f"❌ Failed to initialize Competitor Analyzer configuration: {e}")
    # Use default configuration as fallback
    config = CompetitorAnalyzerConfig()
