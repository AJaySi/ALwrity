"""Pydantic models for component logic requests and responses."""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, EmailStr, validator
import re

# AI Research Models

class UserInfoRequest(BaseModel):
    """Request model for user information validation."""
    full_name: str
    email: str
    company: str
    role: str
    
    @validator('full_name')
    def validate_full_name(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Full name must be at least 2 characters long')
        return v.strip()
    
    @validator('email')
    def validate_email(cls, v):
        # Basic email validation
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        if not email_pattern.match(v):
            raise ValueError('Invalid email format')
        return v.lower()
    
    @validator('company')
    def validate_company(cls, v):
        if not v or len(v.strip()) < 1:
            raise ValueError('Company name is required')
        return v.strip()
    
    @validator('role')
    def validate_role(cls, v):
        valid_roles = ["Content Creator", "Marketing Manager", "Business Owner", "Other"]
        if v not in valid_roles:
            raise ValueError(f'Role must be one of: {", ".join(valid_roles)}')
        return v

class ResearchPreferencesRequest(BaseModel):
    """Request model for research preferences configuration."""
    research_depth: str
    content_types: List[str]
    auto_research: bool
    factual_content: bool = True  # Default to True
    
    @validator('research_depth')
    def validate_research_depth(cls, v):
        valid_depths = ["Basic", "Standard", "Deep", "Comprehensive"]
        if v not in valid_depths:
            raise ValueError(f'Research depth must be one of: {", ".join(valid_depths)}')
        return v
    
    @validator('content_types')
    def validate_content_types(cls, v):
        valid_types = ["Blog Posts", "Social Media", "Technical Articles", "News", "Academic Papers"]
        if not v:
            raise ValueError('At least one content type must be selected')
        for content_type in v:
            if content_type not in valid_types:
                raise ValueError(f'Invalid content type: {content_type}')
        return v

class ResearchRequest(BaseModel):
    """Request model for research processing."""
    topic: str
    preferences: ResearchPreferencesRequest
    
    @validator('topic')
    def validate_topic(cls, v):
        if not v or len(v.strip()) < 3:
            raise ValueError('Topic must be at least 3 characters long')
        return v.strip()

class UserInfoResponse(BaseModel):
    """Response model for user information validation."""
    valid: bool
    user_info: Optional[Dict[str, Any]] = None
    errors: List[str] = []

class ResearchPreferencesResponse(BaseModel):
    """Response model for research preferences configuration."""
    valid: bool
    preferences: Optional[Dict[str, Any]] = None
    errors: List[str] = []

class ResearchResponse(BaseModel):
    """Response model for research processing."""
    success: bool
    topic: str
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# Personalization Models

class ContentStyleRequest(BaseModel):
    """Request model for content style configuration."""
    writing_style: str
    tone: str
    content_length: str
    
    @validator('writing_style')
    def validate_writing_style(cls, v):
        valid_styles = ["Professional", "Casual", "Technical", "Conversational", "Academic"]
        if v not in valid_styles:
            raise ValueError(f'Writing style must be one of: {", ".join(valid_styles)}')
        return v
    
    @validator('tone')
    def validate_tone(cls, v):
        valid_tones = ["Formal", "Semi-Formal", "Neutral", "Friendly", "Humorous"]
        if v not in valid_tones:
            raise ValueError(f'Tone must be one of: {", ".join(valid_tones)}')
        return v
    
    @validator('content_length')
    def validate_content_length(cls, v):
        valid_lengths = ["Concise", "Standard", "Detailed", "Comprehensive"]
        if v not in valid_lengths:
            raise ValueError(f'Content length must be one of: {", ".join(valid_lengths)}')
        return v

class BrandVoiceRequest(BaseModel):
    """Request model for brand voice configuration."""
    personality_traits: List[str]
    voice_description: Optional[str] = None
    keywords: Optional[str] = None
    
    @validator('personality_traits')
    def validate_personality_traits(cls, v):
        valid_traits = ["Professional", "Innovative", "Friendly", "Trustworthy", "Creative", "Expert"]
        if not v:
            raise ValueError('At least one personality trait must be selected')
        for trait in v:
            if trait not in valid_traits:
                raise ValueError(f'Invalid personality trait: {trait}')
        return v
    
    @validator('voice_description')
    def validate_voice_description(cls, v):
        if v and len(v.strip()) < 10:
            raise ValueError('Voice description must be at least 10 characters long')
        return v.strip() if v else None

class AdvancedSettingsRequest(BaseModel):
    """Request model for advanced content generation settings."""
    seo_optimization: bool
    readability_level: str
    content_structure: List[str]
    
    @validator('readability_level')
    def validate_readability_level(cls, v):
        valid_levels = ["Simple", "Standard", "Advanced", "Expert"]
        if v not in valid_levels:
            raise ValueError(f'Readability level must be one of: {", ".join(valid_levels)}')
        return v
    
    @validator('content_structure')
    def validate_content_structure(cls, v):
        valid_structures = ["Introduction", "Key Points", "Examples", "Conclusion", "Call-to-Action"]
        if not v:
            raise ValueError('At least one content structure element must be selected')
        for structure in v:
            if structure not in valid_structures:
                raise ValueError(f'Invalid content structure: {structure}')
        return v

class PersonalizationSettingsRequest(BaseModel):
    """Request model for complete personalization settings."""
    content_style: ContentStyleRequest
    brand_voice: BrandVoiceRequest
    advanced_settings: AdvancedSettingsRequest

class ContentStyleResponse(BaseModel):
    """Response model for content style validation."""
    valid: bool
    style_config: Optional[Dict[str, Any]] = None
    errors: List[str] = []

class BrandVoiceResponse(BaseModel):
    """Response model for brand voice configuration."""
    valid: bool
    brand_config: Optional[Dict[str, Any]] = None
    errors: List[str] = []

class PersonalizationSettingsResponse(BaseModel):
    """Response model for complete personalization settings."""
    valid: bool
    settings: Optional[Dict[str, Any]] = None
    errors: List[str] = []

# Research Utilities Models

class ResearchTopicRequest(BaseModel):
    """Request model for topic research."""
    topic: str
    api_keys: Dict[str, str]
    
    @validator('topic')
    def validate_topic(cls, v):
        if not v or len(v.strip()) < 3:
            raise ValueError('Topic must be at least 3 characters long')
        return v.strip()

class ResearchResultResponse(BaseModel):
    """Response model for research results."""
    success: bool
    topic: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None 

# Style Detection Models
class StyleAnalysisRequest(BaseModel):
    """Request model for style analysis."""
    content: Dict[str, Any]
    analysis_type: str = "comprehensive"  # comprehensive, patterns, guidelines

class StyleAnalysisResponse(BaseModel):
    """Response model for style analysis."""
    success: bool
    analysis: Optional[Dict[str, Any]] = None
    patterns: Optional[Dict[str, Any]] = None
    guidelines: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: str

class WebCrawlRequest(BaseModel):
    """Request model for web crawling."""
    url: Optional[str] = None
    text_sample: Optional[str] = None

class WebCrawlResponse(BaseModel):
    """Response model for web crawling."""
    success: bool
    content: Optional[Dict[str, Any]] = None
    metrics: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: str

class StyleDetectionRequest(BaseModel):
    """Request model for complete style detection workflow."""
    url: Optional[str] = None
    text_sample: Optional[str] = None
    include_patterns: bool = True
    include_guidelines: bool = True

class StyleDetectionResponse(BaseModel):
    """Response model for complete style detection workflow."""
    success: bool
    crawl_result: Optional[Dict[str, Any]] = None
    style_analysis: Optional[Dict[str, Any]] = None
    style_patterns: Optional[Dict[str, Any]] = None
    style_guidelines: Optional[Dict[str, Any]] = None
    seo_audit: Optional[Dict[str, Any]] = None
    sitemap_analysis: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    warning: Optional[str] = None
    timestamp: str 