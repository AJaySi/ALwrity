"""
AI-First Backlinking Database Models

This module defines the database models for the AI Backlinking feature,
designed specifically for an AI-first approach to guest posting and link building.

Key AI-First Considerations:
- Store AI-generated content and decisions
- Track AI performance and learning
- Cache AI responses for efficiency
- Enable AI personalization and optimization
- Support AI-driven analytics and insights
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, Float,
    ForeignKey, JSON, Enum, Index, UniqueConstraint
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.dialects.postgresql import JSONB, ARRAY, UUID
import uuid

Base = declarative_base()


class BacklinkingCampaign(Base):
    """
    AI-Driven Backlinking Campaign

    Represents a user's outreach campaign for building backlinks through guest posting.
    Designed for AI-first approach with personalization and optimization.
    """
    __tablename__ = "backlinking_campaigns"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Basic campaign info
    name = Column(String(100), nullable=False)
    description = Column(Text)

    # Campaign configuration (AI-driven)
    keywords = Column(ARRAY(String), nullable=False)
    target_industries = Column(ARRAY(String))
    content_pillars = Column(ARRAY(String))

    # AI personalization settings
    ai_model_preference = Column(String(50), default="gemini")  # gemini, openai, auto
    tone_preference = Column(String(50), default="professional")  # professional, friendly, authoritative
    personalization_level = Column(String(20), default="high")  # low, medium, high

    # Status and lifecycle
    status = Column(Enum("draft", "active", "paused", "completed", "cancelled", name="campaign_status"),
                   default="draft", index=True)
    priority = Column(Enum("low", "medium", "high", name="campaign_priority"), default="medium")

    # Dates
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    paused_at = Column(DateTime)

    # AI learning and optimization
    ai_performance_score = Column(Float, default=0.0)  # 0-1 scale based on success rate
    ai_learning_data = Column(JSONB)  # Store AI learning insights and preferences

    # Campaign limits and constraints
    max_opportunities = Column(Integer, default=100)
    max_emails_per_day = Column(Integer, default=10)
    max_follow_ups = Column(Integer, default=3)

    # Success metrics
    total_opportunities = Column(Integer, default=0)
    contacted_opportunities = Column(Integer, default=0)
    responded_opportunities = Column(Integer, default=0)
    successful_links = Column(Integer, default=0)

    # Financial tracking
    estimated_cost = Column(Float, default=0.0)  # AI API costs
    actual_cost = Column(Float, default=0.0)

    # Relationships
    opportunities = relationship("BacklinkOpportunity", back_populates="campaign",
                               cascade="all, delete-orphan")
    emails = relationship("BacklinkingEmail", back_populates="campaign",
                         cascade="all, delete-orphan")
    analytics = relationship("BacklinkingAnalytics", back_populates="campaign",
                           cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('idx_campaign_user_status', 'user_id', 'status'),
        Index('idx_campaign_created', 'created_at'),
        Index('idx_campaign_ai_performance', 'ai_performance_score'),
    )

    def __repr__(self):
        return f"<BacklinkingCampaign(id='{self.id}', name='{self.name}', status='{self.status}')>"


class BacklinkOpportunity(Base):
    """
    AI-Analyzed Backlinking Opportunity

    Represents a discovered website that accepts guest posts.
    Includes comprehensive AI analysis and scoring.
    """
    __tablename__ = "backlinking_opportunities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    campaign_id = Column(String(36), ForeignKey("backlinking_campaigns.id"), nullable=False, index=True)

    # Website information
    url = Column(String(2048), nullable=False, index=True)
    domain = Column(String(253), nullable=False, index=True)
    title = Column(String(500))
    description = Column(Text)

    # Contact information (AI-extracted)
    contact_email = Column(String(254))
    contact_email_quality = Column(Float, default=0.0)  # 0-1 email quality score
    all_contact_emails = Column(ARRAY(String))  # List of all extracted emails
    email_extraction_method = Column(String(50))  # direct, contact_page, alternative, none_found
    email_extraction_confidence = Column(String(20))  # high, medium, low
    contact_name = Column(String(200))
    contact_page_url = Column(String(2048))

    # AI analysis results
    ai_content_analysis = Column(JSONB)  # AI-generated content analysis
    ai_relevance_score = Column(Float, default=0.0)  # 0-1 relevance to campaign keywords
    ai_authority_score = Column(Float, default=0.0)  # 0-1 domain authority estimation
    ai_content_quality_score = Column(Float, default=0.0)  # 0-1 content quality assessment
    ai_spam_risk_score = Column(Float, default=0.0)  # 0-1 spam/risk assessment

    # Content topics and focus (AI-detected)
    primary_topics = Column(ARRAY(String))
    content_categories = Column(ARRAY(String))
    writing_tone = Column(String(50))  # formal, casual, technical, etc.

    # Guest posting requirements (AI-extracted)
    submission_guidelines = Column(Text)
    word_count_min = Column(Integer)
    word_count_max = Column(Integer)
    requires_images = Column(Boolean, default=False)
    allows_links = Column(Boolean, default=True)
    submission_deadline = Column(String(100))

    # Status and lifecycle
    status = Column(Enum("discovered", "analyzing", "qualified", "contacted", "responded",
                        "published", "rejected", "expired", name="opportunity_status"),
                   default="discovered", index=True)

    # Discovery and analysis metadata
    discovered_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    analyzed_at = Column(DateTime)
    contacted_at = Column(DateTime)
    responded_at = Column(DateTime)
    published_at = Column(DateTime)

    # AI decision tracking
    ai_contact_recommendation = Column(String(20))  # contact, skip, research_more
    ai_email_template_suggestion = Column(String(100))
    ai_follow_up_strategy = Column(String(50))

    # Quality and risk assessment
    domain_authority = Column(Integer)  # 0-100 Moz DA equivalent
    spam_score = Column(Float, default=0.0)  # 0-1 spam likelihood
    quality_score = Column(Float, default=0.0)  # 0-1 overall quality

    # User feedback and overrides
    user_rating = Column(Integer)  # 1-5 user quality rating
    user_notes = Column(Text)
    user_override_decision = Column(String(20))  # approve, reject, research

    # Performance tracking
    email_open_rate = Column(Float, default=0.0)
    response_time_hours = Column(Float)  # Hours to first response
    link_acquired = Column(Boolean, default=False)
    link_url = Column(String(2048))
    link_placement_date = Column(DateTime)

    # Relationships
    campaign = relationship("BacklinkingCampaign", back_populates="opportunities")
    emails = relationship("BacklinkingEmail", back_populates="opportunity",
                         cascade="all, delete-orphan")
    responses = relationship("BacklinkingResponse", back_populates="opportunity",
                           cascade="all, delete-orphan")

    # Indexes and constraints
    __table_args__ = (
        Index('idx_opportunity_campaign_status', 'campaign_id', 'status'),
        Index('idx_opportunity_url', 'url'),
        Index('idx_opportunity_domain', 'domain'),
        Index('idx_opportunity_ai_scores', 'ai_relevance_score', 'ai_authority_score'),
        Index('idx_opportunity_discovered', 'discovered_at'),
        UniqueConstraint('campaign_id', 'url', name='uq_campaign_opportunity_url'),
    )

    @property
    def overall_score(self) -> float:
        """Calculate overall opportunity score based on AI analysis."""
        if self.ai_relevance_score and self.ai_authority_score and self.ai_content_quality_score:
            # Weighted average favoring relevance and authority
            return (self.ai_relevance_score * 0.4 +
                   self.ai_authority_score * 0.4 +
                   self.ai_content_quality_score * 0.2)
        return 0.0

    def __repr__(self):
        return f"<BacklinkOpportunity(id={self.id}, url='{self.url}', status='{self.status}', score={self.overall_score:.2f})>"


class BacklinkingEmail(Base):
    """
    AI-Generated Outreach Email

    Stores AI-generated, personalized outreach emails sent to opportunities.
    Tracks email performance and AI optimization.
    """
    __tablename__ = "backlinking_emails"

    id = Column(Integer, primary_key=True, autoincrement=True)
    campaign_id = Column(String(36), ForeignKey("backlinking_campaigns.id"), nullable=False, index=True)
    opportunity_id = Column(Integer, ForeignKey("backlinking_opportunities.id"), nullable=False, index=True)

    # Email content (AI-generated)
    subject = Column(String(200), nullable=False)
    body_html = Column(Text, nullable=False)
    body_text = Column(Text)  # Plain text version

    # AI generation metadata
    ai_model_used = Column(String(50))  # gemini-pro, gpt-4, etc.
    ai_prompt_used = Column(Text)  # Store the prompt for debugging
    ai_generation_time = Column(Float)  # Seconds to generate
    ai_temperature = Column(Float, default=0.7)
    ai_confidence_score = Column(Float, default=0.0)  # AI's confidence in email quality

    # Email personalization data
    personalization_data = Column(JSONB)  # Website analysis, user preferences, etc.
    template_used = Column(String(100))  # Email template identifier

    # Email metadata
    from_email = Column(String(254), nullable=False)
    to_email = Column(String(254), nullable=False)
    reply_to_email = Column(String(254))

    # Status and delivery
    status = Column(Enum("draft", "queued", "sending", "sent", "delivered", "bounced",
                        "failed", name="email_status"), default="draft", index=True)
    email_type = Column(Enum("initial", "follow_up", "reminder", "negotiation",
                           name="email_type"), default="initial")

    # Timing
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    sent_at = Column(DateTime)
    delivered_at = Column(DateTime)
    bounced_at = Column(DateTime)
    failed_at = Column(DateTime)

    # Delivery tracking
    smtp_provider = Column(String(50))  # gmail, sendgrid, etc.
    smtp_response = Column(Text)  # SMTP server response
    message_id = Column(String(200))  # Email message ID for tracking

    # Performance metrics
    open_count = Column(Integer, default=0)
    click_count = Column(Integer, default=0)
    open_rate = Column(Float, default=0.0)
    click_rate = Column(Float, default=0.0)

    # User feedback and edits
    user_edited = Column(Boolean, default=False)
    user_approved = Column(Boolean, default=True)  # Auto-approved for AI-generated
    user_feedback_rating = Column(Integer)  # 1-5 rating of AI email quality

    # Follow-up tracking
    follow_up_number = Column(Integer, default=1)
    parent_email_id = Column(Integer, ForeignKey("backlinking_emails.id"))  # For follow-ups

    # Relationships
    campaign = relationship("BacklinkingCampaign", back_populates="emails")
    opportunity = relationship("BacklinkOpportunity", back_populates="emails")
    parent_email = relationship("BacklinkingEmail", remote_side=[id])
    follow_ups = relationship("BacklinkingEmail",
                            backref="parent_email_obj",
                            remote_side=[parent_email_id])

    # Indexes
    __table_args__ = (
        Index('idx_email_campaign_opportunity', 'campaign_id', 'opportunity_id'),
        Index('idx_email_status_sent', 'status', 'sent_at'),
        Index('idx_email_type', 'email_type'),
        Index('idx_email_created', 'created_at'),
    )

    def __repr__(self):
        return f"<BacklinkingEmail(id={self.id}, to='{self.to_email}', status='{self.status}')>"


class BacklinkingResponse(Base):
    """
    Email Response Tracking and AI Analysis

    Tracks responses to outreach emails and includes AI analysis
    of response sentiment, intent, and recommended actions.
    """
    __tablename__ = "backlinking_responses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    campaign_id = Column(String(36), ForeignKey("backlinking_campaigns.id"), nullable=False, index=True)
    opportunity_id = Column(Integer, ForeignKey("backlinking_opportunities.id"), nullable=False, index=True)
    email_id = Column(Integer, ForeignKey("backlinking_emails.id"), nullable=False, index=True)

    # Response content
    from_email = Column(String(254), nullable=False)
    subject = Column(String(200), nullable=False)
    body_html = Column(Text)
    body_text = Column(Text, nullable=False)

    # Response metadata
    received_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    message_id = Column(String(200))
    in_reply_to = Column(String(200))  # References original email

    # AI analysis of response
    ai_sentiment_analysis = Column(JSONB)  # positive, negative, neutral with confidence
    ai_intent_classification = Column(String(50))  # interested, rejected, negotiate, etc.
    ai_urgency_level = Column(String(20))  # high, medium, low
    ai_response_quality = Column(Float, default=0.0)  # 0-1 quality assessment

    # AI recommendations
    ai_recommended_action = Column(String(50))  # reply, follow_up, negotiate, accept, reject
    ai_suggested_reply = Column(Text)  # AI-generated reply suggestion
    ai_follow_up_delay = Column(Integer)  # Suggested delay in hours

    # Manual processing
    user_reviewed = Column(Boolean, default=False)
    user_response_sent = Column(Boolean, default=False)
    user_notes = Column(Text)
    user_sentiment_override = Column(String(20))  # positive, negative, neutral

    # Response categorization
    response_type = Column(Enum("positive", "negative", "neutral", "auto_reply", "bounce",
                               "unsubscribe", "spam", name="response_type"), default="neutral")
    is_opportunity = Column(Boolean, default=False)  # Indicates genuine opportunity
    requires_action = Column(Boolean, default=False)  # Needs user attention

    # Success tracking
    led_to_publication = Column(Boolean, default=False)
    link_acquired = Column(Boolean, default=False)
    link_url = Column(String(2048))
    publication_date = Column(DateTime)

    # Relationships
    campaign = relationship("BacklinkingCampaign")
    opportunity = relationship("BacklinkOpportunity", back_populates="responses")
    email = relationship("BacklinkingEmail")

    # Indexes
    __table_args__ = (
        Index('idx_response_campaign_received', 'campaign_id', 'received_at'),
        Index('idx_response_opportunity', 'opportunity_id'),
        Index('idx_response_email', 'email_id'),
        Index('idx_response_type', 'response_type'),
        Index('idx_response_received', 'received_at'),
    )

    @property
    def sentiment_score(self) -> float:
        """Get sentiment score from AI analysis."""
        if self.ai_sentiment_analysis:
            return self.ai_sentiment_analysis.get('score', 0.5)
        return 0.5

    def __repr__(self):
        return f"<BacklinkingResponse(id={self.id}, from='{self.from_email}', sentiment={self.sentiment_score:.2f})>"


class BacklinkingAnalytics(Base):
    """
    AI-Driven Analytics and Performance Tracking

    Stores comprehensive analytics data for campaigns, AI performance,
    and user success metrics to enable continuous optimization.
    """
    __tablename__ = "backlinking_analytics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    campaign_id = Column(String(36), ForeignKey("backlinking_campaigns.id"), nullable=False, index=True)

    # Time period
    date = Column(DateTime, nullable=False, index=True)
    period_type = Column(Enum("daily", "weekly", "monthly", name="analytics_period"), default="daily")

    # Campaign metrics
    opportunities_discovered = Column(Integer, default=0)
    opportunities_contacted = Column(Integer, default=0)
    opportunities_responded = Column(Integer, default=0)
    opportunities_published = Column(Integer, default=0)
    links_acquired = Column(Integer, default=0)

    # Email performance
    emails_sent = Column(Integer, default=0)
    emails_delivered = Column(Integer, default=0)
    emails_bounced = Column(Integer, default=0)
    emails_opened = Column(Integer, default=0)
    emails_clicked = Column(Integer, default=0)

    # Response metrics
    responses_received = Column(Integer, default=0)
    positive_responses = Column(Integer, default=0)
    negative_responses = Column(Integer, default=0)
    auto_replies = Column(Integer, default=0)

    # AI performance metrics
    ai_emails_generated = Column(Integer, default=0)
    ai_responses_analyzed = Column(Integer, default=0)
    ai_accuracy_score = Column(Float, default=0.0)  # Overall AI performance
    ai_cost_incurred = Column(Float, default=0.0)  # API costs

    # User engagement metrics
    user_reviews_provided = Column(Integer, default=0)
    user_satisfaction_score = Column(Float, default=0.0)  # Average user ratings

    # Success rates (calculated fields)
    @property
    def response_rate(self) -> float:
        """Calculate response rate percentage."""
        if self.emails_delivered > 0:
            return (self.responses_received / self.emails_delivered) * 100
        return 0.0

    @property
    def conversion_rate(self) -> float:
        """Calculate conversion rate (responses to publications)."""
        if self.responses_received > 0:
            return (self.opportunities_published / self.responses_received) * 100
        return 0.0

    @property
    def success_rate(self) -> float:
        """Calculate overall success rate (links acquired)."""
        if self.opportunities_contacted > 0:
            return (self.links_acquired / self.opportunities_contacted) * 100
        return 0.0

    # AI insights and recommendations
    ai_insights = Column(JSONB)  # AI-generated insights and recommendations
    performance_trends = Column(JSONB)  # Trend analysis data
    optimization_suggestions = Column(JSONB)  # AI suggestions for improvement

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    campaign = relationship("BacklinkingCampaign", back_populates="analytics")

    # Indexes
    __table_args__ = (
        Index('idx_analytics_campaign_date', 'campaign_id', 'date'),
        Index('idx_analytics_period', 'period_type', 'date'),
        Index('idx_analytics_created', 'created_at'),
    )

    def __repr__(self):
        return f"<BacklinkingAnalytics(id={self.id}, campaign='{self.campaign_id}', date='{self.date}', success_rate={self.success_rate:.1f}%)>"


class AILearningData(Base):
    """
    AI Learning and Personalization Data

    Stores data to improve AI performance and personalization
    based on user feedback and successful campaigns.
    """
    __tablename__ = "ai_learning_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Learning data type
    data_type = Column(Enum("email_template", "keyword_performance", "tone_preference",
                           "response_pattern", "success_factor", name="learning_data_type"),
                      nullable=False, index=True)

    # Content and metadata
    data_key = Column(String(200), nullable=False)  # Identifier for the learning data
    data_value = Column(JSONB, nullable=False)  # The actual learning data

    # Performance metrics
    success_score = Column(Float, default=0.0)  # 0-1 success rate
    usage_count = Column(Integer, default=0)
    last_used = Column(DateTime, default=datetime.utcnow)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Source tracking
    source_campaign_id = Column(String(36), ForeignKey("backlinking_campaigns.id"))
    source_opportunity_id = Column(Integer, ForeignKey("backlinking_opportunities.id"))

    # Indexes
    __table_args__ = (
        Index('idx_learning_user_type', 'user_id', 'data_type'),
        Index('idx_learning_key', 'data_key'),
        Index('idx_learning_success', 'success_score'),
        UniqueConstraint('user_id', 'data_type', 'data_key', name='uq_user_learning_data'),
    )

    def __repr__(self):
        return f"<AILearningData(id={self.id}, user={self.user_id}, type='{self.data_type}', key='{self.data_key}')>"


class BacklinkingTemplate(Base):
    """
    Email Template Library for AI Customization

    Stores reusable email templates that can be customized by AI
    based on opportunity analysis and user preferences.
    """
    __tablename__ = "backlinking_templates"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Template metadata
    name = Column(String(100), nullable=False)
    description = Column(Text)
    category = Column(String(50), default="general")  # initial, follow_up, negotiation, etc.

    # Template content
    subject_template = Column(String(200), nullable=False)
    body_template_html = Column(Text, nullable=False)
    body_template_text = Column(Text)

    # AI customization metadata
    ai_variables = Column(ARRAY(String))  # Available variables for AI customization
    ai_tone_suggestions = Column(ARRAY(String))  # Suggested tones for this template
    ai_context_requirements = Column(JSONB)  # Required context for AI to use this template

    # Usage statistics
    usage_count = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    average_response_time = Column(Float)  # Hours

    # Template metadata
    is_active = Column(Boolean, default=True)
    is_system_template = Column(Boolean, default=False)  # Built-in vs user-created
    created_by_user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Indexes
    __table_args__ = (
        Index('idx_template_category', 'category'),
        Index('idx_template_active', 'is_active'),
        Index('idx_template_usage', 'usage_count', 'success_rate'),
    )

    def __repr__(self):
        return f"<BacklinkingTemplate(id={self.id}, name='{self.name}', category='{self.category}')>"


# Create all tables
def create_all_tables(engine):
    """Create all backlinking tables in the database."""
    Base.metadata.create_all(engine)


def drop_all_tables(engine):
    """Drop all backlinking tables from the database."""
    Base.metadata.drop_all(engine)


# Export all models
__all__ = [
    'BacklinkingCampaign',
    'BacklinkOpportunity',
    'BacklinkingEmail',
    'BacklinkingResponse',
    'BacklinkingAnalytics',
    'AILearningData',
    'BacklinkingTemplate',
    'create_all_tables',
    'drop_all_tables',
]