"""
Custom exceptions for the AI Backlinking service.

Provides specific exception types for different error scenarios
to enable better error handling and user feedback.
"""

from typing import Dict, Any, Optional


class BacklinkingError(Exception):
    """Base exception for all backlinking-related errors."""

    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "BACKLINKING_ERROR"
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses."""
        return {
            "error": self.error_code,
            "message": self.message,
            "details": self.details
        }


class CampaignError(BacklinkingError):
    """Base exception for campaign-related errors."""
    pass


class CampaignNotFoundError(CampaignError):
    """Raised when a requested campaign is not found."""

    def __init__(self, campaign_id: str):
        super().__init__(
            f"Campaign with ID '{campaign_id}' not found",
            "CAMPAIGN_NOT_FOUND",
            {"campaign_id": campaign_id}
        )


class CampaignValidationError(CampaignError):
    """Raised when campaign data validation fails."""

    def __init__(self, field: str, value: Any, reason: str):
        super().__init__(
            f"Invalid campaign data: {reason}",
            "CAMPAIGN_VALIDATION_ERROR",
            {"field": field, "value": value, "reason": reason}
        )


class OpportunityError(BacklinkingError):
    """Base exception for opportunity-related errors."""
    pass


class OpportunityNotFoundError(OpportunityError):
    """Raised when an opportunity is not found."""

    def __init__(self, opportunity_url: str):
        super().__init__(
            f"Opportunity with URL '{opportunity_url}' not found",
            "OPPORTUNITY_NOT_FOUND",
            {"opportunity_url": opportunity_url}
        )


class ScrapingError(BacklinkingError):
    """Base exception for web scraping errors."""
    pass


class ScrapingTimeoutError(ScrapingError):
    """Raised when web scraping times out."""

    def __init__(self, url: str, timeout: int):
        super().__init__(
            f"Scraping timeout for URL: {url}",
            "SCRAPING_TIMEOUT",
            {"url": url, "timeout_seconds": timeout}
        )


class ScrapingBlockedError(ScrapingError):
    """Raised when scraping is blocked by target website."""

    def __init__(self, url: str, status_code: int = None):
        message = f"Scraping blocked for URL: {url}"
        if status_code:
            message += f" (HTTP {status_code})"

        super().__init__(
            message,
            "SCRAPING_BLOCKED",
            {"url": url, "status_code": status_code}
        )


class EmailError(BacklinkingError):
    """Base exception for email-related errors."""
    pass


class EmailConnectionError(EmailError):
    """Raised when email server connection fails."""

    def __init__(self, server: str, port: int, reason: str = None):
        message = f"Failed to connect to email server {server}:{port}"
        if reason:
            message += f" - {reason}"

        super().__init__(
            message,
            "EMAIL_CONNECTION_ERROR",
            {"server": server, "port": port, "reason": reason}
        )


class EmailAuthenticationError(EmailError):
    """Raised when email authentication fails."""

    def __init__(self, server: str):
        super().__init__(
            f"Email authentication failed for server: {server}",
            "EMAIL_AUTHENTICATION_ERROR",
            {"server": server}
        )


class EmailSendError(EmailError):
    """Raised when sending an email fails."""

    def __init__(self, recipient: str, reason: str = None):
        message = f"Failed to send email to: {recipient}"
        if reason:
            message += f" - {reason}"

        super().__init__(
            message,
            "EMAIL_SEND_ERROR",
            {"recipient": recipient, "reason": reason}
        )


class AIError(BacklinkingError):
    """Base exception for AI/LLM-related errors."""
    pass


class AIServiceUnavailableError(AIError):
    """Raised when AI service is unavailable."""

    def __init__(self, service_name: str, reason: str = None):
        message = f"AI service '{service_name}' is unavailable"
        if reason:
            message += f" - {reason}"

        super().__init__(
            message,
            "AI_SERVICE_UNAVAILABLE",
            {"service_name": service_name, "reason": reason}
        )


class AIProcessingError(AIError):
    """Raised when AI processing fails."""

    def __init__(self, operation: str, reason: str = None):
        message = f"AI processing failed for operation: {operation}"
        if reason:
            message += f" - {reason}"

        super().__init__(
            message,
            "AI_PROCESSING_ERROR",
            {"operation": operation, "reason": reason}
        )


class RateLimitError(BacklinkingError):
    """Raised when rate limits are exceeded."""

    def __init__(self, service: str, limit: int, window_seconds: int):
        super().__init__(
            f"Rate limit exceeded for {service}: {limit} requests per {window_seconds} seconds",
            "RATE_LIMIT_EXCEEDED",
            {"service": service, "limit": limit, "window_seconds": window_seconds}
        )


class ConfigurationError(BacklinkingError):
    """Raised when configuration is invalid or missing."""

    def __init__(self, setting: str, reason: str = None):
        message = f"Configuration error for setting: {setting}"
        if reason:
            message += f" - {reason}"

        super().__init__(
            message,
            "CONFIGURATION_ERROR",
            {"setting": setting, "reason": reason}
        )


class ValidationError(BacklinkingError):
    """Raised when input validation fails."""

    def __init__(self, field: str, value: Any, rule: str):
        super().__init__(
            f"Validation failed for field '{field}': {rule}",
            "VALIDATION_ERROR",
            {"field": field, "value": value, "rule": rule}
        )


def handle_service_error(error: Exception) -> BacklinkingError:
    """
    Convert common exceptions to BacklinkingError types.

    Args:
        error: The original exception

    Returns:
        BacklinkingError: Converted exception with appropriate type
    """
    if isinstance(error, BacklinkingError):
        return error

    # Handle common Python exceptions
    if isinstance(error, ValueError):
        return ValidationError("unknown", str(error), "Invalid input value")

    if isinstance(error, ConnectionError):
        return EmailConnectionError("unknown", 0, str(error))

    if isinstance(error, TimeoutError):
        return ScrapingTimeoutError("unknown", 30)

    # Generic fallback
    return BacklinkingError(
        f"Unexpected error: {str(error)}",
        "UNEXPECTED_ERROR",
        {"original_error": type(error).__name__}
    )