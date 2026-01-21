"""
AI Backlinking Service

This service provides AI-powered backlinking capabilities including:
- Automated guest post opportunity discovery
- Website scraping and contact extraction
- Personalized outreach email generation
- Email automation and tracking
- Campaign management and analytics
"""

from .backlinking_service import BacklinkingService
from .email_service import EmailAutomationService
from .scraping_service import WebScrapingService
from .campaign_service import CampaignManagementService
from .research_service import BacklinkingResearchService
from .query_generator import BacklinkingQueryGenerator
from .dual_api_executor import DualAPISearchExecutor
from .cost_optimizer import BacklinkingCostOptimizer
from .email_extraction import EmailExtractionService
from .config import get_config, reload_config, BacklinkingConfig
from .logging_utils import (
    BacklinkingLogger,
    create_service_logger,
    backlinking_logger,
    scraping_logger,
    email_logger,
    campaign_logger,
    log_operation,
    log_campaign_action,
    log_email_action,
    log_scraping_action,
    log_performance_metric,
)
from .security_utils import (
    InputSanitizer,
    SecurityValidator,
    ContentSecurity,
    input_sanitizer,
    security_validator,
    content_security,
    sanitize_user_input,
    validate_content_for_email,
)
from .cache_utils import (
    MemoryCache,
    CacheManager,
    AsyncOperationManager,
    get_cache_manager,
    get_async_manager,
    timed_operation,
    cached_async,
)
from .exceptions import (
    BacklinkingError,
    CampaignError,
    CampaignNotFoundError,
    CampaignValidationError,
    OpportunityError,
    OpportunityNotFoundError,
    ScrapingError,
    ScrapingTimeoutError,
    ScrapingBlockedError,
    EmailError,
    EmailConnectionError,
    EmailAuthenticationError,
    EmailSendError,
    AIError,
    AIServiceUnavailableError,
    AIProcessingError,
    RateLimitError,
    ConfigurationError,
    ValidationError,
    handle_service_error,
)

__all__ = [
    # Main services
    'BacklinkingService',
    'EmailAutomationService',
    'WebScrapingService',
    'CampaignManagementService',
    'BacklinkingResearchService',
    'BacklinkingQueryGenerator',
    'DualAPISearchExecutor',
    'BacklinkingCostOptimizer',
    'EmailExtractionService',

    # Configuration
    'get_config',
    'reload_config',
    'BacklinkingConfig',

    # Logging
    'BacklinkingLogger',
    'create_service_logger',
    'backlinking_logger',
    'scraping_logger',
    'email_logger',
    'campaign_logger',
    'log_operation',
    'log_campaign_action',
    'log_email_action',
    'log_scraping_action',
    'log_performance_metric',

    # Security
    'InputSanitizer',
    'SecurityValidator',
    'ContentSecurity',
    'input_sanitizer',
    'security_validator',
    'content_security',
    'sanitize_user_input',
    'validate_content_for_email',

    # Caching
    'MemoryCache',
    'CacheManager',
    'AsyncOperationManager',
    'get_cache_manager',
    'get_async_manager',
    'timed_operation',
    'cached_async',

    # Exceptions
    'BacklinkingError',
    'CampaignError',
    'CampaignNotFoundError',
    'CampaignValidationError',
    'OpportunityError',
    'OpportunityNotFoundError',
    'ScrapingError',
    'ScrapingTimeoutError',
    'ScrapingBlockedError',
    'EmailError',
    'EmailConnectionError',
    'EmailAuthenticationError',
    'EmailSendError',
    'AIError',
    'AIServiceUnavailableError',
    'AIProcessingError',
    'RateLimitError',
    'ConfigurationError',
    'ValidationError',
    'handle_service_error',
]