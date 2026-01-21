"""
Pydantic models for AI Backlinking service input validation.

Provides type-safe data models with validation for all API inputs
and internal data structures.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, EmailStr, validator, root_validator
from datetime import datetime
import re

from .security_utils import input_sanitizer


class UserProposalModel(BaseModel):
    """Model for user guest post proposal."""
    user_name: str = Field(..., min_length=1, max_length=100, description="User's full name")
    user_email: EmailStr = Field(..., description="User's email address")
    topic: str = Field(..., min_length=1, max_length=200, description="Guest post topic")
    description: Optional[str] = Field(None, max_length=1000, description="Optional topic description")

    @validator('user_name')
    def validate_user_name(cls, v):
        """Validate and sanitize user name format."""
        if not v.strip():
            raise ValueError('User name cannot be empty')
        # Sanitize input first
        sanitized = input_sanitizer.sanitize_text_input(v, max_length=100)
        # Remove extra whitespace
        return ' '.join(sanitized.split())

    @validator('topic')
    def validate_topic(cls, v):
        """Validate and sanitize topic format."""
        if not v.strip():
            raise ValueError('Topic cannot be empty')
        # Sanitize input first
        return input_sanitizer.sanitize_text_input(v, max_length=200)


class CreateCampaignRequestModel(BaseModel):
    """Model for campaign creation requests."""
    name: str = Field(..., min_length=3, max_length=100, description="Campaign name")
    keywords: List[str] = Field(..., min_items=1, max_items=10, description="Target keywords")
    user_proposal: UserProposalModel = Field(..., description="User's guest post proposal")

    @validator('name')
    def validate_name(cls, v):
        """Validate campaign name."""
        if not v.strip():
            raise ValueError('Campaign name cannot be empty')
        # Remove extra whitespace and capitalize
        cleaned = ' '.join(v.split())
        return cleaned

    @validator('keywords')
    def validate_keywords(cls, v):
        """Validate keywords list."""
        if not v:
            raise ValueError('At least one keyword is required')

        cleaned_keywords = []
        for keyword in v:
            if not keyword or not keyword.strip():
                raise ValueError('Keywords cannot be empty')
            cleaned = keyword.strip()
            if len(cleaned) > 50:
                raise ValueError(f'Keyword too long: {cleaned[:50]}...')
            cleaned_keywords.append(cleaned)

        # Check for duplicates
        if len(cleaned_keywords) != len(set(cleaned_keywords)):
            raise ValueError('Duplicate keywords are not allowed')

        return cleaned_keywords

    @root_validator
    def validate_campaign_data(cls, values):
        """Cross-field validation."""
        name = values.get('name', '')
        keywords = values.get('keywords', [])

        # Check if name contains keywords (basic relevance check)
        name_lower = name.lower()
        keyword_matches = sum(1 for keyword in keywords if keyword.lower() in name_lower)

        if keyword_matches == 0:
            from ..logging_utils import backlinking_logger
            backlinking_logger.warning(
                "Campaign name may not be relevant to keywords",
                campaign_name=name,
                keywords=keywords
            )

        return values


class EmailConfigModel(BaseModel):
    """Model for email server configuration."""

class BacklinkData(BaseModel):
    """Model for backlink information."""
    source_url: str
    target_url: str
    anchor_text: str = ""
    link_type: str = "external"  # external, internal, social, forum
    domain_authority: int = 0
    page_authority: int = 0
    spam_score: float = 0.0
    discovered_date: datetime = None
    last_seen: datetime = None
    is_active: bool = True

class ContentGap(BaseModel):
    """Model for content gap analysis."""
    gap_type: str  # keyword_gap, topic_gap, trend_gap, competitor_gap
    topic: str
    keywords: List[str] = []
    priority_score: float = 0.0
    opportunity_score: float = 0.0
    rationale: str = ""
    suggested_content: str = ""

class ContentSuggestion(BaseModel):
    """Model for AI-generated content suggestions."""
    title: str
    description: str
    target_keywords: List[str] = []
    content_type: str = "blog_post"  # blog_post, guide, case_study, etc.
    seo_score: float = 0.0
    readability_score: float = 0.0
    competitor_analysis: Dict[str, Any] = {}
    prospect_fit_score: float = 0.0
    estimated_traffic_potential: int = 0
    server: str = Field(..., min_length=1, max_length=255, description="SMTP/IMAP server address")
    port: int = Field(..., ge=1, le=65535, description="Server port")
    user: EmailStr = Field(..., description="Email username")
    password: str = Field(..., min_length=1, description="Email password or app password")

    @validator('server')
    def validate_server(cls, v):
        """Validate server address format."""
        if not v.strip():
            raise ValueError('Server address cannot be empty')

        # Basic domain validation
        domain_pattern = r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
        if not re.match(domain_pattern, v):
            raise ValueError('Invalid server address format')

        return v.strip()

    @validator('password')
    def validate_password(cls, v):
        """Validate password strength."""
        if len(v) < 4:
            raise ValueError('Password must be at least 4 characters long')

        # Check for common weak passwords
        weak_passwords = ['password', '123456', 'qwerty', 'admin']
        if v.lower() in weak_passwords:
            raise ValueError('Please use a stronger password')

        return v


class OpportunityResponseModel(BaseModel):
    """Model for backlinking opportunity data."""
    url: str = Field(..., description="Website URL")
    title: str = Field(..., description="Page title")
    description: str = Field(..., description="Page description")
    contact_email: Optional[EmailStr] = Field(None, description="Contact email")
    contact_name: Optional[str] = Field(None, max_length=100, description="Contact name")
    domain_authority: Optional[int] = Field(None, ge=0, le=100, description="Domain authority score")
    content_topics: List[str] = Field(default_factory=list, description="Content topics")
    submission_guidelines: Optional[str] = Field(None, max_length=2000, description="Submission guidelines")
    status: str = Field("discovered", description="Opportunity status")

    @validator('url')
    def validate_url(cls, v):
        """Validate URL format."""
        if not v.strip():
            raise ValueError('URL cannot be empty')

        # Basic URL validation
        url_pattern = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w)*)?)?$'
        if not re.match(url_pattern, v, re.IGNORECASE):
            raise ValueError('Invalid URL format')

        return v.strip()

    @validator('content_topics')
    def validate_topics(cls, v):
        """Validate content topics."""
        if len(v) > 10:
            raise ValueError('Cannot have more than 10 content topics')

        cleaned_topics = []
        for topic in v:
            cleaned = topic.strip()
            if len(cleaned) > 50:
                cleaned = cleaned[:47] + "..."
            cleaned_topics.append(cleaned)

        return cleaned_topics


class CampaignAnalyticsModel(BaseModel):
    """Model for campaign analytics data."""
    total_opportunities: int = Field(..., ge=0, description="Total opportunities found")
    opportunities_by_status: Dict[str, int] = Field(..., description="Opportunities grouped by status")
    email_stats: Dict[str, Any] = Field(..., description="Email performance statistics")
    top_performing_opportunities: List[Dict[str, Any]] = Field(default_factory=list, description="Top opportunities")
    campaign_progress: Dict[str, bool] = Field(..., description="Campaign progress indicators")

    @validator('email_stats')
    def validate_email_stats(cls, v):
        """Validate email statistics structure."""
        required_keys = ['sent', 'replied', 'bounced']
        for key in required_keys:
            if key not in v:
                raise ValueError(f'Missing required email stat: {key}')
            if not isinstance(v[key], (int, float)) or v[key] < 0:
                raise ValueError(f'Invalid value for {key}: {v[key]}')

        return v


class EmailGenerationRequestModel(BaseModel):
    """Model for email generation requests."""
    user_proposal: UserProposalModel = Field(..., description="User's proposal data")

    @validator('user_proposal')
    def validate_proposal(cls, v):
        """Validate user proposal for email generation."""
        if not v.topic or len(v.topic.strip()) < 5:
            raise ValueError('Topic must be at least 5 characters for email generation')

        return v


class BulkEmailRequestModel(BaseModel):
    """Model for bulk email sending requests."""
    email_records: List[Dict[str, Any]] = Field(..., min_items=1, max_items=50, description="Email records to send")
    smtp_config: EmailConfigModel = Field(..., description="SMTP configuration")

    @validator('email_records')
    def validate_email_records(cls, v):
        """Validate email records structure."""
        for i, record in enumerate(v):
            required_keys = ['recipient_email', 'subject', 'body']
            for key in required_keys:
                if key not in record:
                    raise ValueError(f'Email record {i} missing required field: {key}')

            # Validate email format
            email = record.get('recipient_email', '')
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                raise ValueError(f'Invalid email address in record {i}: {email}')

        return v


# Internal data models for service operations

class ScrapingResultModel(BaseModel):
    """Internal model for scraping results."""
    url: str
    title: str
    description: str
    has_guest_post_section: bool
    contact_email: Optional[str] = None
    contact_name: Optional[str] = None
    content_topics: List[str] = None
    submission_guidelines: Optional[str] = None
    domain_authority: Optional[int] = None


class EmailRecordModel(BaseModel):
    """Internal model for email records."""
    id: int
    campaign_id: str
    opportunity_id: str
    recipient_email: str
    subject: str
    body: str
    status: str
    sent_at: Optional[datetime] = None
    follow_up_count: int = 0


class CampaignModel(BaseModel):
    """Internal model for campaign data."""
    campaign_id: str
    user_id: str
    name: str
    keywords: List[str]
    status: str
    created_at: datetime
    email_stats: Dict[str, int]


# Response models for API endpoints

class CampaignResponseModel(BaseModel):
    """Response model for campaign data."""
    campaign_id: str
    user_id: str
    name: str
    keywords: List[str]
    status: str
    created_at: datetime
    email_stats: Dict[str, int]


class EmailGenerationResponseModel(BaseModel):
    """Response model for generated emails."""
    opportunity: OpportunityResponseModel
    email_subject: str
    email_body: str
    record_id: int


def validate_api_input(data: Dict[str, Any], model_class) -> BaseModel:
    """
    Validate API input data against a Pydantic model.

    Args:
        data: Input data dictionary
        model_class: Pydantic model class

    Returns:
        Validated model instance

    Raises:
        ValidationError: If validation fails
    """
    try:
        return model_class(**data)
    except Exception as e:
        from ..exceptions import ValidationError
        from ..logging_utils import backlinking_logger

        backlinking_logger.error(
            f"Input validation failed for {model_class.__name__}",
            error=str(e),
            input_data=data
        )
        raise ValidationError("input_data", data, f"Validation failed: {str(e)}")


def sanitize_string_input(value: str, max_length: int = 1000) -> str:
    """
    Sanitize string input by removing potentially harmful content.

    Args:
        value: Input string
        max_length: Maximum allowed length

    Returns:
        Sanitized string
    """
    if not value:
        return ""

    # Remove null bytes and other control characters
    cleaned = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', value)

    # Trim whitespace
    cleaned = cleaned.strip()

    # Limit length
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length - 3] + "..."

    return cleaned


def sanitize_url_input(url: str) -> str:
    """
    Sanitize URL input.

    Args:
        url: Input URL

    Returns:
        Sanitized URL
    """
    if not url:
        return ""

    # Remove potentially dangerous characters
    cleaned = re.sub(r'[<>]', '', url.strip())

    # Ensure it starts with http:// or https://
    if cleaned and not cleaned.startswith(('http://', 'https://')):
        cleaned = 'https://' + cleaned

    return cleaned