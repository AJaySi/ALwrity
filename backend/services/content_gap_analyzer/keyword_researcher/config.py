"""
Keyword Researcher Configuration

Configuration management for keyword researcher services.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import os
from enum import Enum


class Environment(str, Enum):
    """Environment types."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class AIProviderConfig(BaseModel):
    """Configuration for AI providers."""
    
    provider_name: str = Field(..., description="AI provider name")
    enabled: bool = Field(default=True, description="Whether provider is enabled")
    timeout: int = Field(default=30, description="Request timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    api_key: Optional[str] = Field(default=None, description="API key if required")
    model: Optional[str] = Field(default=None, description="Model name to use")
    temperature: float = Field(default=0.7, description="AI model temperature")
    max_tokens: Optional[int] = Field(default=None, description="Maximum tokens per response")


class AnalysisConfig(BaseModel):
    """Configuration for analysis parameters."""
    
    max_keywords_per_request: int = Field(default=50, description="Maximum keywords per analysis request")
    default_analysis_depth: str = Field(default="standard", description="Default analysis depth")
    enable_caching: bool = Field(default=True, description="Enable result caching")
    cache_ttl_seconds: int = Field(default=3600, description="Cache TTL in seconds")
    parallel_processing: bool = Field(default=True, description="Enable parallel processing")
    max_concurrent_requests: int = Field(default=5, description="Maximum concurrent requests")


class ScoringConfig(BaseModel):
    """Configuration for scoring algorithms."""
    
    opportunity_weight_volume: float = Field(default=0.3, description="Weight for search volume in opportunity scoring")
    opportunity_weight_competition: float = Field(default=0.25, description="Weight for competition in opportunity scoring")
    opportunity_weight_trend: float = Field(default=0.2, description="Weight for trend in opportunity scoring")
    opportunity_weight_relevance: float = Field(default=0.25, description="Weight for relevance in opportunity scoring")
    
    min_opportunity_score: float = Field(default=50.0, description="Minimum opportunity score threshold")
    max_difficulty_score: float = Field(default=70.0, description="Maximum difficulty score threshold")
    high_volume_threshold: int = Field(default=5000, description="High volume keyword threshold")
    low_competition_threshold: int = Field(default=30, description="Low competition threshold")


class ContentConfig(BaseModel):
    """Configuration for content recommendations."""
    
    optimal_title_length: int = Field(default=60, description="Optimal title length in characters")
    optimal_meta_length: int = Field(default=155, description="Optimal meta description length")
    target_word_count: int = Field(default=1500, description="Target word count for content")
    keyword_density_target: float = Field(default=0.02, description="Target keyword density")
    
    enable_content_format_suggestions: bool = Field(default=True, description="Enable content format suggestions")
    enable_topic_clustering: bool = Field(default=True, description="Enable topic clustering")
    enable_performance_prediction: bool = Field(default=True, description="Enable performance predictions")


class ExpansionConfig(BaseModel):
    """Configuration for keyword expansion."""
    
    max_variations_per_keyword: int = Field(default=15, description="Maximum variations per seed keyword")
    max_long_tail_per_keyword: int = Field(default=10, description="Maximum long-tail keywords per seed")
    max_semantic_per_keyword: int = Field(default=10, description="Maximum semantic variations per seed")
    max_related_per_keyword: int = Field(default=10, description="Maximum related keywords per seed")
    
    enable_variations: bool = Field(default=True, description="Enable keyword variations")
    enable_long_tail: bool = Field(default=True, description="Enable long-tail generation")
    enable_semantic: bool = Field(default=True, description="Enable semantic variations")
    enable_related: bool = Field(default=True, description="Enable related keywords")


class MonitoringConfig(BaseModel):
    """Configuration for monitoring and logging."""
    
    enable_detailed_logging: bool = Field(default=True, description="Enable detailed logging")
    log_level: str = Field(default="INFO", description="Log level")
    enable_metrics: bool = Field(default=True, description="Enable metrics collection")
    health_check_interval: int = Field(default=300, description="Health check interval in seconds")
    
    enable_performance_tracking: bool = Field(default=True, description="Enable performance tracking")
    enable_error_tracking: bool = Field(default=True, description="Enable error tracking")
    max_log_entries: int = Field(default=10000, description="Maximum log entries to keep")


class KeywordResearcherConfig(BaseModel):
    """Main configuration for keyword researcher service."""
    
    environment: Environment = Field(default=Environment.DEVELOPMENT, description="Environment")
    service_name: str = Field(default="KeywordResearcher", description="Service name")
    version: str = Field(default="1.0.0", description="Service version")
    
    # AI providers configuration
    ai_providers: List[AIProviderConfig] = Field(default_factory=list, description="AI providers configuration")
    
    # Analysis configuration
    analysis: AnalysisConfig = Field(default_factory=AnalysisConfig, description="Analysis configuration")
    
    # Scoring configuration
    scoring: ScoringConfig = Field(default_factory=ScoringConfig, description="Scoring configuration")
    
    # Content configuration
    content: ContentConfig = Field(default_factory=ContentConfig, description="Content configuration")
    
    # Expansion configuration
    expansion: ExpansionConfig = Field(default_factory=ExpansionConfig, description="Expansion configuration")
    
    # Monitoring configuration
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig, description="Monitoring configuration")
    
    # Feature flags
    enable_trend_analysis: bool = Field(default=True, description="Enable trend analysis")
    enable_intent_analysis: bool = Field(default=True, description="Enable intent analysis")
    enable_opportunity_discovery: bool = Field(default=True, description="Enable opportunity discovery")
    enable_content_recommendations: bool = Field(default=True, description="Enable content recommendations")
    enable_keyword_expansion: bool = Field(default=True, description="Enable keyword expansion")
    
    # Rate limiting
    requests_per_minute: int = Field(default=60, description="Requests per minute limit")
    requests_per_hour: int = Field(default=1000, description="Requests per hour limit")
    requests_per_day: int = Field(default=10000, description="Requests per day limit")
    
    class Config:
        env_prefix = "KEYWORD_RESEARCHER_"
        case_sensitive = False


def get_default_config() -> KeywordResearcherConfig:
    """Get default configuration."""
    
    # Default AI providers
    default_ai_providers = [
        AIProviderConfig(
            provider_name="gemini",
            enabled=True,
            timeout=30,
            max_retries=3,
            temperature=0.7,
            model="gemini-pro"
        ),
        AIProviderConfig(
            provider_name="main_text_generation",
            enabled=True,
            timeout=30,
            max_retries=3,
            temperature=0.7
        )
    ]
    
    return KeywordResearcherConfig(
        environment=Environment(os.getenv("ENVIRONMENT", "development")),
        ai_providers=default_ai_providers,
        analysis=AnalysisConfig(
            max_keywords_per_request=int(os.getenv("MAX_KEYWORDS_PER_REQUEST", "50")),
            enable_caching=os.getenv("ENABLE_CACHING", "true").lower() == "true",
            cache_ttl_seconds=int(os.getenv("CACHE_TTL_SECONDS", "3600"))
        ),
        scoring=ScoringConfig(
            min_opportunity_score=float(os.getenv("MIN_OPPORTUNITY_SCORE", "50.0")),
            max_difficulty_score=float(os.getenv("MAX_DIFFICULTY_SCORE", "70.0")),
            high_volume_threshold=int(os.getenv("HIGH_VOLUME_THRESHOLD", "5000"))
        ),
        content=ContentConfig(
            optimal_title_length=int(os.getenv("OPTIMAL_TITLE_LENGTH", "60")),
            optimal_meta_length=int(os.getenv("OPTIMAL_META_LENGTH", "155")),
            target_word_count=int(os.getenv("TARGET_WORD_COUNT", "1500"))
        ),
        monitoring=MonitoringConfig(
            enable_detailed_logging=os.getenv("ENABLE_DETAILED_LOGGING", "true").lower() == "true",
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            health_check_interval=int(os.getenv("HEALTH_CHECK_INTERVAL", "300"))
        ),
        requests_per_minute=int(os.getenv("REQUESTS_PER_MINUTE", "60")),
        requests_per_hour=int(os.getenv("REQUESTS_PER_HOUR", "1000")),
        requests_per_day=int(os.getenv("REQUESTS_PER_DAY", "10000"))
    )


def get_config() -> KeywordResearcherConfig:
    """Get configuration from environment or defaults."""
    return get_default_config()


# Global configuration instance
config = get_config()
