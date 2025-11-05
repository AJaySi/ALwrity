"""
Research Persona Models
Pydantic models for AI-generated research personas.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class ResearchPreset(BaseModel):
    """Research preset configuration."""
    name: str
    keywords: str
    industry: str
    target_audience: str
    research_mode: str = Field(..., description="basic, comprehensive, or targeted")
    config: Dict[str, Any] = Field(default_factory=dict, description="Complete ResearchConfig object")
    description: Optional[str] = None
    icon: Optional[str] = None
    gradient: Optional[str] = None


class ResearchPersona(BaseModel):
    """AI-generated research persona providing personalized defaults and suggestions."""
    
    # Smart Defaults
    default_industry: str = Field(..., description="Default industry from onboarding data")
    default_target_audience: str = Field(..., description="Default target audience from onboarding data")
    default_research_mode: str = Field(..., description="basic, comprehensive, or targeted")
    default_provider: str = Field(..., description="google or exa")
    
    # Keyword Intelligence
    suggested_keywords: List[str] = Field(default_factory=list, description="8-12 relevant keywords")
    keyword_expansion_patterns: Dict[str, List[str]] = Field(
        default_factory=dict, 
        description="Mapping of keywords to expanded, industry-specific terms"
    )
    
    # Domain & Source Intelligence
    suggested_exa_domains: List[str] = Field(
        default_factory=list, 
        description="4-6 authoritative domains for the industry"
    )
    suggested_exa_category: Optional[str] = Field(
        None, 
        description="Suggested Exa category based on industry"
    )
    
    # Query Enhancement Intelligence
    research_angles: List[str] = Field(
        default_factory=list, 
        description="5-8 alternative research angles/focuses"
    )
    query_enhancement_rules: Dict[str, str] = Field(
        default_factory=dict, 
        description="Templates for improving vague user queries"
    )
    
    # Research History Insights
    recommended_presets: List[ResearchPreset] = Field(
        default_factory=list, 
        description="3-5 personalized research preset templates"
    )
    
    # Research Preferences
    research_preferences: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Structured research preferences from onboarding"
    )
    
    # Metadata
    generated_at: Optional[str] = Field(None, description="ISO timestamp of generation")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence score 0-1")
    version: Optional[str] = Field(None, description="Schema version")
    
    class Config:
        json_schema_extra = {
            "example": {
                "default_industry": "Healthcare",
                "default_target_audience": "Medical professionals and healthcare administrators",
                "default_research_mode": "comprehensive",
                "default_provider": "exa",
                "suggested_keywords": ["telemedicine", "patient care", "healthcare technology"],
                "keyword_expansion_patterns": {
                    "AI": ["healthcare AI", "medical AI", "clinical AI"],
                    "tools": ["medical devices", "clinical tools"]
                },
                "suggested_exa_domains": ["pubmed.gov", "nejm.org", "thelancet.com"],
                "suggested_exa_category": "research paper",
                "research_angles": [
                    "Compare telemedicine platforms",
                    "Telemedicine ROI analysis",
                    "Latest telemedicine trends"
                ],
                "query_enhancement_rules": {
                    "vague_ai": "Research: AI applications in Healthcare for Medical professionals",
                    "vague_tools": "Compare top Healthcare tools"
                },
                "recommended_presets": [],
                "research_preferences": {
                    "research_depth": "comprehensive",
                    "content_types": ["blog", "article"]
                },
                "generated_at": "2024-01-01T00:00:00Z",
                "confidence_score": 0.85,
                "version": "1.0"
            }
        }

