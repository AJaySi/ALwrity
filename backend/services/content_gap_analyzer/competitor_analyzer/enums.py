"""
Enums for Competitor Analyzer Service

This module contains type-safe enumerations for all categorical data
used across the competitor analyzer services.
"""

from enum import Enum


class AnalysisStatus(str, Enum):
    """Analysis status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PriorityLevel(str, Enum):
    """Priority level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class ImpactLevel(str, Enum):
    """Impact level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class OpportunityLevel(str, Enum):
    """Opportunity level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CompetitorSize(str, Enum):
    """Competitor size enumeration."""
    STARTUP = "startup"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    ENTERPRISE = "enterprise"


class CompetitorType(str, Enum):
    """Competitor type enumeration."""
    DIRECT = "direct"
    INDIRECT = "indirect"
    SUBSTITUTE = "substitute"
    POTENTIAL = "potential"


class ContentType(str, Enum):
    """Content type enumeration."""
    BLOG_POST = "blog_post"
    ARTICLE = "article"
    CASE_STUDY = "case_study"
    WHITEPAPER = "whitepaper"
    EBOOK = "ebook"
    VIDEO = "video"
    PODCAST = "podcast"
    WEBINAR = "webinar"
    INFOGRAPHIC = "infographic"
    PRESS_RELEASE = "press_release"
    CHECKLIST = "checklist"
    TEMPLATE = "template"
    TOOL = "tool"
    CALCULATOR = "calculator"
    QUIZ = "quiz"
    SURVEY = "survey"
    RESEARCH_REPORT = "research_report"


class PublishingFrequency(str, Enum):
    """Publishing frequency enumeration."""
    DAILY = "daily"
    WEEKLY = "weekly"
    BI_WEEKLY = "bi_weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    IRREGULAR = "irregular"


class MarketPosition(str, Enum):
    """Market position enumeration."""
    LEADER = "leader"
    CHALLENGER = "challenger"
    FOLLOWER = "follower"
    NICHE = "niche"
    EMERGING = "emerging"


class MarketShareType(str, Enum):
    """Market share type enumeration."""
    REVENUE = "revenue"
    CUSTOMER_BASE = "customer_base"
    TRAFFIC = "traffic"
    CONTENT_VOLUME = "content_volume"
    BRAND_AWARENESS = "brand_awareness"


class CompetitiveIntensity(str, Enum):
    """Competitive intensity enumeration."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


class GapType(str, Enum):
    """Content gap type enumeration."""
    TOPIC_GAP = "topic_gap"
    FORMAT_GAP = "format_gap"
    QUALITY_GAP = "quality_gap"
    FREQUENCY_GAP = "frequency_gap"
    AUDIENCE_GAP = "audience_gap"
    KEYWORD_GAP = "keyword_gap"
    INTENT_GAP = "intent_gap"
    TIMELINESS_GAP = "timeliness_gap"


class ContentFormat(str, Enum):
    """Content format enumeration."""
    BLOG_POST = "blog_post"
    ARTICLE = "article"
    CASE_STUDY = "case_study"
    WHITEPAPER = "whitepaper"
    EBOOK = "ebook"
    VIDEO = "video"
    PODCAST = "podcast"
    WEBINAR = "webinar"
    INFOGRAPHIC = "infographic"
    CHECKLIST = "checklist"
    TEMPLATE = "template"
    TOOL = "tool"
    CALCULATOR = "calculator"
    QUIZ = "quiz"
    SURVEY = "survey"
    RESEARCH_REPORT = "research_report"


class SEOGapType(str, Enum):
    """SEO gap type enumeration."""
    KEYWORD_GAP = "keyword_gap"
    TECHNICAL_SEO_GAP = "technical_seo_gap"
    CONTENT_SEO_GAP = "content_seo_gap"
    BACKLINK_GAP = "backlink_gap"
    LOCAL_SEO_GAP = "local_seo_gap"
    MOBILE_SEO_GAP = "mobile_seo_gap"
    SPEED_GAP = "speed_gap"
    STRUCTURED_DATA_GAP = "structured_data_gap"


class KeywordDifficulty(str, Enum):
    """Keyword difficulty enumeration."""
    VERY_EASY = "very_easy"
    EASY = "easy"
    MODERATE = "moderate"
    DIFFICULT = "difficult"
    VERY_DIFFICULT = "very_difficult"


class SearchIntent(str, Enum):
    """Search intent enumeration."""
    INFORMATIONAL = "informational"
    COMMERCIAL = "commercial"
    TRANSACTIONAL = "transactional"
    NAVIGATIONAL = "navigational"


class AIProviderType(str, Enum):
    """AI provider type enumeration."""
    OPENAI = "openai"
    GEMINI = "gemini"
    CLAUDE = "claude"
    LLAMA = "llama"
    CUSTOM = "custom"
    LLM_TEXT_GEN = "llm_text_gen"


class AnalysisDepth(str, Enum):
    """Analysis depth enumeration."""
    BASIC = "basic"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"
    DEEP_DIVE = "deep_dive"


class ConfidenceLevel(str, Enum):
    """Confidence level enumeration."""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class TrendDirection(str, Enum):
    """Trend direction enumeration."""
    UP = "up"
    DOWN = "down"
    STABLE = "stable"
    VOLATILE = "volatile"


class ImplementationComplexity(str, Enum):
    """Implementation complexity enumeration."""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class RiskLevel(str, Enum):
    """Risk level enumeration."""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class MarketMaturity(str, Enum):
    """Market maturity enumeration."""
    EMERGING = "emerging"
    GROWING = "growing"
    MATURE = "mature"
    DECLINING = "declining"


class SeasonalPattern(str, Enum):
    """Seasonal pattern enumeration."""
    NONE = "none"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


class AlertSeverity(str, Enum):
    """Alert severity enumeration."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ServiceStatus(str, Enum):
    """Service status enumeration."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"


class LogLevel(str, Enum):
    """Log level enumeration."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Environment(str, Enum):
    """Environment enumeration."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class DataFreshness(str, Enum):
    """Data freshness enumeration."""
    REAL_TIME = "real_time"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"


class ValidationStatus(str, Enum):
    """Validation status enumeration."""
    PENDING = "pending"
    VALID = "valid"
    INVALID = "invalid"
    ERROR = "error"


class ProcessingStatus(str, Enum):
    """Processing status enumeration."""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class CacheStatus(str, Enum):
    """Cache status enumeration."""
    HIT = "hit"
    MISS = "miss"
    STALE = "stale"
    INVALID = "invalid"
    EXPIRED = "expired"


class MetricType(str, Enum):
    """Metric type enumeration."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


class ComparisonOperator(str, Enum):
    """Comparison operator enumeration."""
    EQUAL = "equal"
    NOT_EQUAL = "not_equal"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    GREATER_EQUAL = "greater_equal"
    LESS_EQUAL = "less_equal"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"


class AggregationType(str, Enum):
    """Aggregation type enumeration."""
    SUM = "sum"
    AVERAGE = "average"
    MIN = "min"
    MAX = "max"
    COUNT = "count"
    MEDIAN = "median"
    MODE = "mode"
    STD_DEV = "std_dev"


class TimePeriod(str, Enum):
    """Time period enumeration."""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class TimeUnit(str, Enum):
    """Time unit enumeration."""
    SECONDS = "seconds"
    MINUTES = "minutes"
    HOURS = "hours"
    DAYS = "days"
    WEEKS = "weeks"
    MONTHS = "months"
    YEARS = "years"


class Currency(str, Enum):
    """Currency enumeration."""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"
    CNY = "CNY"
    INR = "INR"
    AUD = "AUD"
    CAD = "CAD"


class Language(str, Enum):
    """Language enumeration."""
    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    ITALIAN = "it"
    PORTUGUESE = "pt"
    RUSSIAN = "ru"
    CHINESE = "zh"
    JAPANESE = "ja"
    KOREAN = "ko"


class Region(str, Enum):
    """Region enumeration."""
    NORTH_AMERICA = "north_america"
    SOUTH_AMERICA = "south_america"
    EUROPE = "europe"
    ASIA = "asia"
    AFRICA = "africa"
    OCEANIA = "oceania"
    MIDDLE_EAST = "middle_east"


class Industry(str, Enum):
    """Industry enumeration."""
    TECHNOLOGY = "technology"
    HEALTHCARE = "healthcare"
    FINANCE = "finance"
    EDUCATION = "education"
    RETAIL = "retail"
    MANUFACTURING = "manufacturing"
    REAL_ESTATE = "real_estate"
    ENTERTAINMENT = "entertainment"
    TRAVEL = "travel"
    FOOD_BEVERAGE = "food_beverage"
    AUTOMOTIVE = "automotive"
    ENERGY = "energy"
    AGRICULTURE = "agriculture"
    CONSTRUCTION = "construction"
    TRANSPORTATION = "transportation"
    MEDIA = "media"
    TELECOMMUNICATIONS = "telecommunications"
    CONSULTING = "consulting"
    LEGAL = "legal"
    INSURANCE = "insurance"


class BusinessModel(str, Enum):
    """Business model enumeration."""
    B2B = "b2b"
    B2C = "b2c"
    B2B2C = "b2b2c"
    C2C = "c2c"
    C2B = "c2b"
    MARKETPLACE = "marketplace"
    SUBSCRIPTION = "subscription"
    FREEMIUM = "freemium"
    ADVERTISING = "advertising"
    COMMISSION = "commission"


class TargetAudience(str, Enum):
    """Target audience enumeration."""
    ENTERPRISE = "enterprise"
    SMALL_BUSINESS = "small_business"
    CONSUMER = "consumer"
    DEVELOPER = "developer"
    STUDENT = "student"
    PROFESSIONAL = "professional"
    CREATIVE = "creative"
    ANALYST = "analyst"
    EXECUTIVE = "executive"
    ENTREPRENEUR = "entrepreneur"


class ContentTypeCategory(str, Enum):
    """Content type category enumeration."""
    EDUCATIONAL = "educational"
    INFORMATIONAL = "informational"
    ENTERTAINMENT = "entertainment"
    PROMOTIONAL = "promotional"
    TRANSACTIONAL = "transactional"
    INTERACTIVE = "interactive"
    REFERENCE = "reference"
    NEWS = "news"
    OPINION = "opinion"
    RESEARCH = "research"


class ContentPurpose(str, Enum):
    """Content purpose enumeration."""
    AWARENESS = "awareness"
    CONSIDERATION = "consideration"
    CONVERSION = "conversion"
    RETENTION = "retention"
    ADVOCACY = "advocacy"
    EDUCATION = "education"
    ENTERTAINMENT = "entertainment"
    INSPIRATION = "inspiration"
    PERSUASION = "persuasion"
    INFORMATION = "information"


class DistributionChannel(str, Enum):
    """Distribution channel enumeration."""
    WEBSITE = "website"
    BLOG = "blog"
    SOCIAL_MEDIA = "social_media"
    EMAIL = "email"
    SEARCH_ENGINES = "search_engines"
    PAID_ADVERTISING = "paid_advertising"
    ORGANIC_SEARCH = "organic_search"
    REFERRAL = "referral"
    DIRECT = "direct"
    PARTNERS = "partners"


class MeasurementMetric(str, Enum):
    """Measurement metric enumeration."""
    TRAFFIC = "traffic"
    ENGAGEMENT = "engagement"
    CONVERSIONS = "conversions"
    REVENUE = "revenue"
    LEADS = "leads"
    SIGNUPS = "signups"
    DOWNLOADS = "downloads"
    SHARES = "shares"
    COMMENTS = "comments"
    LIKES = "likes"
    VIEWS = "views"
    CLICKS = "clicks"
    IMPRESSIONS = "impressions"
    REACH = "reach"
    FREQUENCY = "frequency"
    RECENCY = "recency"


class AnalysisType(str, Enum):
    """Analysis type enumeration."""
    COMPETITOR_ANALYSIS = "competitor_analysis"
    MARKET_ANALYSIS = "market_analysis"
    CONTENT_ANALYSIS = "content_analysis"
    SEO_ANALYSIS = "seo_analysis"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    TREND_ANALYSIS = "trend_analysis"
    GAP_ANALYSIS = "gap_analysis"
    OPPORTUNITY_ANALYSIS = "opportunity_analysis"
    THREAT_ANALYSIS = "threat_analysis"
    STRENGTH_ANALYSIS = "strength_analysis"
    WEAKNESS_ANALYSIS = "weakness_analysis"


class ReportType(str, Enum):
    """Report type enumeration."""
    SUMMARY = "summary"
    DETAILED = "detailed"
    EXECUTIVE = "executive"
    TECHNICAL = "technical"
    COMPARATIVE = "comparative"
    HISTORICAL = "historical"
    FORECAST = "forecast"
    REAL_TIME = "real_time"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"


class ExportFormat(str, Enum):
    """Export format enumeration."""
    JSON = "json"
    CSV = "csv"
    EXCEL = "excel"
    PDF = "pdf"
    XML = "xml"
    YAML = "yaml"


class NotificationType(str, Enum):
    """Notification type enumeration."""
    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"
    SLACK = "slack"
    TEAMS = "teams"
    IN_APP = "in_app"
    PUSH = "push"
    BROWSER = "browser"


class IntegrationType(str, Enum):
    """Integration type enumeration."""
    API = "api"
    WEBHOOK = "webhook"
    DATABASE = "database"
    FILE = "file"
    STREAM = "stream"
    QUEUE = "queue"
    CACHE = "cache"
    STORAGE = "storage"


class SecurityLevel(str, Enum):
    """Security level enumeration."""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    SECRET = "secret"


class ComplianceStandard(str, Enum):
    """Compliance standard enumeration."""
    GDPR = "gdpr"
    CCPA = "ccpa"
    HIPAA = "hipaa"
    SOX = "sox"
    ISO_27001 = "iso_27001"
    SOC_2 = "soc_2"
    PCI_DSS = "pci_dss"


# Utility functions for enums
def get_enum_values(enum_class: type) -> list:
    """Get all values from an enum class."""
    return [value.value for value in enum_class]


def get_enum_names(enum_class: type) -> list:
    """Get all names from an enum class."""
    return [value.name for value in enum_class]


def is_valid_enum_value(enum_class: type, value: str) -> bool:
    """Check if a value is valid for an enum class."""
    try:
        enum_class(value)
        return True
    except ValueError:
        return False


def get_enum_by_value(enum_class: type, value: str, default=None):
    """Get enum instance by value, with optional default."""
    try:
        return enum_class(value)
    except ValueError:
        return default


# Common enum collections
CONTENT_TYPE_ENUMS = [ContentType, ContentFormat, ContentTypeCategory, ContentPurpose]
ANALYSIS_ENUMS = [AnalysisType, AnalysisDepth, AnalysisStatus]
PRIORITY_ENUMS = [PriorityLevel, ImpactLevel, OpportunityLevel, RiskLevel]
MARKET_ENUMS = [MarketPosition, MarketShareType, CompetitiveIntensity, MarketMaturity]
SEO_ENUMS = [SEOGapType, KeywordDifficulty, SearchIntent]
COMPETITOR_ENUMS = [CompetitorType, CompetitorSize]
MONITORING_ENUMS = [ServiceStatus, AlertSeverity, LogLevel, ProcessingStatus]
