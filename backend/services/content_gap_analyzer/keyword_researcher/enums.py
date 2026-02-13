"""
Keyword Researcher Enums

Enumerations used across keyword researcher services.
"""

from enum import Enum


class AnalysisStatus(str, Enum):
    """Analysis status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class IntentType(str, Enum):
    """Search intent types."""
    INFORMATIONAL = "informational"
    TRANSACTIONAL = "transactional"
    NAVIGATIONAL = "navigational"
    COMMERCIAL = "commercial"
    LOCAL = "local"


class IntentSubtype(str, Enum):
    """Search intent subtypes."""
    # Informational subtypes
    EDUCATIONAL = "educational"
    DEFINITIONAL = "definition"
    TUTORIAL = "tutorial"
    COMPARISON = "comparison"
    HOW_TO = "how_to"
    NEWS = "news"
    GUIDE = "guide"
    TIPS = "tips"
    
    # Transactional subtypes
    PURCHASE = "purchase"
    COST_INQUIRY = "cost_inquiry"
    PRICING = "pricing"
    BUY_NOW = "buy_now"
    QUOTE_REQUEST = "quote_request"
    ORDER = "order"
    BOOKING = "booking"
    
    # Navigational subtypes
    BRAND_SEARCH = "brand_search"
    WEBSITE_VISIT = "website_visit"
    LOGIN = "login"
    CONTACT = "contact"
    ABOUT = "about"
    DIRECTIONS = "directions"
    
    # Commercial subtypes
    REVIEW = "review"
    BEST_OF = "best_of"
    COMPARISON_SHOPPING = "comparison_shopping"
    ALTERNATIVE = "alternative"
    DEALS = "deals"
    DISCOUNT = "discount"
    COUPON = "coupon"


class UserJourneyStage(str, Enum):
    """User journey stages."""
    AWARENESS = "awareness"
    CONSIDERATION = "consideration"
    DECISION = "decision"
    PURCHASE = "purchase"
    RETENTION = "retention"
    ADVOCACY = "advocacy"


class TrendDirection(str, Enum):
    """Trend direction types."""
    RISING = "rising"
    STABLE = "stable"
    DECLINING = "declining"
    SEASONAL = "seasonal"
    VOLATILE = "volatile"
    EMERGING = "emerging"


class CompetitionLevel(str, Enum):
    """Competition levels."""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"
    EXTREME = "extreme"


class PriorityLevel(str, Enum):
    """Priority levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    CRITICAL = "critical"
    OPTIONAL = "optional"


class DifficultyLevel(str, Enum):
    """Difficulty levels."""
    VERY_EASY = "very_easy"
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    VERY_HARD = "very_hard"
    EXPERT = "expert"


class OpportunityType(str, Enum):
    """Opportunity types."""
    CONTENT_GAP = "content_gap"
    TRENDING = "trending"
    LONG_TAIL = "long_tail"
    LOW_COMPETITION = "low_competition"
    HIGH_VOLUME = "high_volume"
    SEASONAL = "seasonal"
    COMPETITIVE_ADVANTAGE = "competitive_advantage"
    LOCAL_SEO = "local_seo"
    VOICE_SEARCH = "voice_search"
    FEATURED_SNIPPET = "featured_snippet"


class ContentType(str, Enum):
    """Content types."""
    BLOG_POST = "blog_post"
    ARTICLE = "article"
    GUIDE = "guide"
    TUTORIAL = "tutorial"
    LANDING_PAGE = "landing_page"
    PRODUCT_PAGE = "product_page"
    CATEGORY_PAGE = "category_page"
    FAQ = "faq"
    CASE_STUDY = "case_study"
    INFOGRAPHIC = "infographic"
    VIDEO = "video"
    PODCAST = "podcast"
    WEBINAR = "webinar"
    WHITEPAPER = "whitepaper"
    EBOOK = "ebook"
    CHECKLIST = "checklist"
    TEMPLATE = "template"
    TOOL = "tool"
    CALCULATOR = "calculator"
    QUIZ = "quiz"
    SURVEY = "survey"


class ContentFormat(str, Enum):
    """Content formats."""
    LONG_FORM = "long_form"
    SHORT_FORM = "short_form"
    LISTICLE = "listicle"
    HOW_TO = "how_to"
    COMPARISON = "comparison"
    REVIEW = "review"
    INTERVIEW = "interview"
    ROUNDUP = "roundup"
    NEWS = "news"
    OPINION = "opinion"
    TUTORIAL = "tutorial"
    GUIDE = "guide"
    CHECKLIST = "checklist"
    TEMPLATE = "template"
    CASE_STUDY = "case_study"
    FAQ = "faq"
    Q_AND_A = "q_and_a"


class SeasonalPattern(str, Enum):
    """Seasonal patterns."""
    NONE = "none"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"
    HOLIDAY_BASED = "holiday_based"
    WEATHER_RELATED = "weather_related"
    SCHOOL_YEAR = "school_year"
    FISCAL_YEAR = "fiscal_year"


class AnalysisDepth(str, Enum):
    """Analysis depth levels."""
    BASIC = "basic"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"
    ADVANCED = "advanced"
    ENTERPRISE = "enterprise"


class AIProvider(str, Enum):
    """AI provider names."""
    GEMINI = "gemini"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    MAIN_TEXT_GENERATION = "main_text_generation"
    CUSTOM = "custom"


class ServiceStatus(str, Enum):
    """Service status types."""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"


class ErrorType(str, Enum):
    """Error types."""
    VALIDATION_ERROR = "validation_error"
    AI_PROVIDER_ERROR = "ai_provider_error"
    TIMEOUT_ERROR = "timeout_error"
    RATE_LIMIT_ERROR = "rate_limit_error"
    DATABASE_ERROR = "database_error"
    NETWORK_ERROR = "network_error"
    CONFIGURATION_ERROR = "configuration_error"
    UNKNOWN_ERROR = "unknown_error"


class LogLevel(str, Enum):
    """Log levels."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class MetricType(str, Enum):
    """Metric types."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


class CacheStrategy(str, Enum):
    """Cache strategies."""
    NO_CACHE = "no_cache"
    LRU = "lru"
    LFU = "lfu"
    TTL = "ttl"
    WRITE_THROUGH = "write_through"
    WRITE_BEHIND = "write_behind"


class Environment(str, Enum):
    """Environment types."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class FeatureFlag(str, Enum):
    """Feature flags."""
    TREND_ANALYSIS = "trend_analysis"
    INTENT_ANALYSIS = "intent_analysis"
    OPPORTUNITY_DISCOVERY = "opportunity_discovery"
    CONTENT_RECOMMENDATIONS = "content_recommendations"
    KEYWORD_EXPANSION = "keyword_expansion"
    TOPIC_CLUSTERING = "topic_clustering"
    PERFORMANCE_PREDICTION = "performance_prediction"
    AI_ENHANCEMENT = "ai_enhancement"
    CACHE_RESULTS = "cache_results"
    DETAILED_LOGGING = "detailed_logging"
    METRICS_COLLECTION = "metrics_collection"
    ERROR_TRACKING = "error_tracking"
    HEALTH_CHECKS = "health_checks"
