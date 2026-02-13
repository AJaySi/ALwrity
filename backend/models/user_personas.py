"""
User Persona Models - User Data Database
AI writing personas for content creation with multi-tenant isolation.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, Text, Float
from models.ssot_bases import UserDataBase
from datetime import datetime
from typing import Optional
import uuid

Base = UserDataBase

class UserPersona(Base):
    """
    AI writing personas for content creation.
    User data database table with multi-tenant isolation by user_id.
    """
    __tablename__ = "user_personas"
    
    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Multi-tenant isolation
    user_id = Column(String, nullable=False, index=True)  # Foreign key to users table (platform DB)
    
    # Persona information
    persona_name = Column(String, nullable=False)
    persona_description = Column(Text, nullable=True)
    
    # Persona characteristics
    characteristics = Column(JSON, default={})  # Core personality traits
    
    # Writing style and tone
    writing_style = Column(String, nullable=True)  # formal, casual, professional, creative
    tone = Column(String, nullable=True)  # friendly, authoritative, humorous, serious
    voice_characteristics = Column(JSON, default={})  # Detailed voice attributes
    
    # Content preferences
    preferred_content_types = Column(JSON, default=[])  # blog, social, email, etc.
    target_audience = Column(JSON, default={})  # Intended audience
    content_goals = Column(JSON, default={})  # Inform, persuade, entertain, etc.
    
    # Language and communication
    language = Column(String, default="english")
    complexity_level = Column(String, default="medium")  # simple, medium, complex
    vocabulary_level = Column(String, default="professional")  # basic, professional, academic
    
    # AI generation parameters
    ai_parameters = Column(JSON, default={})  # Temperature, top_p, frequency_penalty, etc.
    preferred_ai_models = Column(JSON, default=[])  # GPT-4, Claude, etc.
    creativity_level = Column(Integer, default=5)  # 1-10 scale
    formality_level = Column(Integer, default=5)  # 1-10 scale
    
    # Brand and business alignment
    brand_guidelines = Column(JSON, default={})  # Brand voice guidelines
    industry_focus = Column(String, nullable=True)  # Specific industry expertise
    niche_specialization = Column(JSON, default=[])  # Specialized knowledge areas
    
    # Emotional and psychological traits
    personality_traits = Column(JSON, default={})  # Big Five traits, MBTI, etc.
    emotional_tone = Column(JSON, default={})  # Emotional expression patterns
    communication_style = Column(JSON, default={})  # Direct, indirect, supportive, etc.
    
    # Content structure preferences
    content_structure = Column(JSON, default={})  # Preferred content formats
    paragraph_style = Column(JSON, default={})  # Length, flow, transitions
    heading_preferences = Column(JSON, default={})  # H1, H2, H3 usage patterns
    
    # SEO and marketing focus
    seo_approach = Column(JSON, default={})  # SEO writing style preferences
    keyword_integration = Column(JSON, default={})  # How to use keywords
    call_to_action_style = Column(JSON, default={})  # CTA preferences
    
    # Cultural and regional considerations
    cultural_context = Column(JSON, default={})  # Cultural sensitivity and context
    regional_variations = Column(JSON, default={})  # Regional language preferences
    
    # Performance and usage metrics
    usage_count = Column(Integer, default=0)  # How many times used
    success_rate = Column(Float, default=0.0)  # Content performance metrics
    user_feedback_score = Column(Float, nullable=True)  # User ratings
    
    # Template and sharing
    is_template = Column(Boolean, default=False)  # Can be shared as template
    template_category = Column(String, nullable=True)  # Template category
    template_tags = Column(JSON, default=[])  # Template tags
    shared_with_users = Column(JSON, default=[])  # Users it's shared with
    
    # Version control
    version = Column(Integer, default=1)
    parent_persona_id = Column(String, nullable=True)  # For persona variations
    is_latest_version = Column(Boolean, default=True)
    
    # Status and workflow
    status = Column(String, default="active")  # active, archived, deleted
    is_favorite = Column(Boolean, default=False)  # User's favorite persona
    
    # Quality metrics
    coherence_score = Column(Float, nullable=True)  # Writing coherence
    consistency_score = Column(Float, nullable=True)  # Brand consistency
    engagement_prediction = Column(Float, nullable=True)  # Predicted engagement
    
    # Integration data
    integration_data = Column(JSON, default={})  # Platform-specific data
    external_references = Column(JSON, default=[])  # External style guides
    
    # Metadata
    persona_metadata = Column(JSON, default={})
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_used_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<UserPersona(id={self.id}, user_id={self.user_id}, persona_name={self.persona_name})>"
    
    @property
    def is_active(self) -> bool:
        """Check if persona is active"""
        return self.status == "active"
    
    @property
    def is_archived(self) -> bool:
        """Check if persona is archived"""
        return self.status == "archived"
    
    @property
    def days_since_created(self) -> int:
        """Get days since persona was created"""
        delta = datetime.utcnow() - self.created_at
        return delta.days
    
    @property
    def days_since_used(self) -> Optional[int]:
        """Get days since persona was last used"""
        if not self.last_used_at:
            return None
        delta = datetime.utcnow() - self.last_used_at
        return delta.days
    
    @property
    def effectiveness_score(self) -> Optional[float]:
        """Calculate overall effectiveness score"""
        if self.success_rate and self.user_feedback_score:
            return (self.success_rate + self.user_feedback_score) / 2
        return self.success_rate or self.user_feedback_score
    
    def use_persona(self):
        """Record persona usage"""
        self.usage_count += 1
        self.last_used_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def archive(self):
        """Archive the persona"""
        self.status = "archived"
        self.updated_at = datetime.utcnow()
    
    def favorite(self):
        """Mark as favorite"""
        self.is_favorite = True
        self.updated_at = datetime.utcnow()
    
    def unfavorite(self):
        """Remove from favorites"""
        self.is_favorite = False
        self.updated_at = datetime.utcnow()
    
    def update_performance_metrics(self, success_rate: float, feedback_score: Optional[float] = None):
        """Update performance metrics"""
        self.success_rate = success_rate
        if feedback_score is not None:
            self.user_feedback_score = feedback_score
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> dict:
        """Convert persona to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "persona_name": self.persona_name,
            "persona_description": self.persona_description,
            "characteristics": self.characteristics or {},
            "writing_style": self.writing_style,
            "tone": self.tone,
            "voice_characteristics": self.voice_characteristics or {},
            "preferred_content_types": self.preferred_content_types or [],
            "target_audience": self.target_audience or {},
            "content_goals": self.content_goals or {},
            "language": self.language,
            "complexity_level": self.complexity_level,
            "vocabulary_level": self.vocabulary_level,
            "ai_parameters": self.ai_parameters or {},
            "preferred_ai_models": self.preferred_ai_models or [],
            "creativity_level": self.creativity_level,
            "formality_level": self.formality_level,
            "brand_guidelines": self.brand_guidelines or {},
            "industry_focus": self.industry_focus,
            "niche_specialization": self.niche_specialization or [],
            "personality_traits": self.personality_traits or {},
            "emotional_tone": self.emotional_tone or {},
            "communication_style": self.communication_style or {},
            "content_structure": self.content_structure or {},
            "paragraph_style": self.paragraph_style or {},
            "heading_preferences": self.heading_preferences or {},
            "seo_approach": self.seo_approach or {},
            "keyword_integration": self.keyword_integration or {},
            "call_to_action_style": self.call_to_action_style or {},
            "cultural_context": self.cultural_context or {},
            "regional_variations": self.regional_variations or {},
            "usage_count": self.usage_count,
            "success_rate": self.success_rate,
            "user_feedback_score": self.user_feedback_score,
            "is_template": self.is_template,
            "template_category": self.template_category,
            "template_tags": self.template_tags or [],
            "shared_with_users": self.shared_with_users or [],
            "version": self.version,
            "parent_persona_id": self.parent_persona_id,
            "is_latest_version": self.is_latest_version,
            "status": self.status,
            "is_favorite": self.is_favorite,
            "coherence_score": self.coherence_score,
            "consistency_score": self.consistency_score,
            "engagement_prediction": self.engagement_prediction,
            "integration_data": self.integration_data or {},
            "external_references": self.external_references or [],
            "persona_metadata": self.persona_metadata or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_used_at": self.last_used_at.isoformat() if self.last_used_at else None,
            "is_active": self.is_active,
            "is_archived": self.is_archived,
            "days_since_created": self.days_since_created,
            "days_since_used": self.days_since_used,
            "effectiveness_score": self.effectiveness_score
        }
