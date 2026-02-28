"""
Podcast Bible Models

Pydantic models for the structured Podcast Bible, used for hyper-personalization.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class HostPersona(BaseModel):
    """Details about the podcast host persona."""
    name: str = Field(..., description="Name of the podcast host")
    background: str = Field(..., description="Professional background and expertise")
    expertise_level: str = Field(..., description="Level of expertise (e.g., Expert, Practitioner, Enthusiast)")
    personality_traits: List[str] = Field(default_factory=list, description="Personality traits (e.g., Witty, Authoritative, Empathetic)")
    vocal_style: str = Field(..., description="Description of the vocal style and delivery")
    vocal_characteristics: List[str] = Field(default_factory=list, description="Specific vocal traits (e.g., Deep, Raspy, Energetic, Calm)")
    look: Optional[str] = Field(None, description="Visual description of the host (for avatar generation)")
    catchphrases: List[str] = Field(default_factory=list, description="Commonly used phrases or sign-offs")

class VisualStyle(BaseModel):
    """Visual aesthetic for the podcast videos and avatars."""
    style_preset: str = Field(default="Professional Studio", description="Visual style (e.g., 3D Cartoon, Cinematic, Minimalist)")
    environment: str = Field(..., description="The studio or setting where the podcast takes place")
    lighting: str = Field(default="Soft Studio Lighting", description="Lighting mood and setup")
    color_palette: List[str] = Field(default_factory=list, description="Primary brand colors for the visual elements")
    camera_style: str = Field(default="Static Mid-shot", description="Preferred camera framing and movement")

class AudioEnvironment(BaseModel):
    """The soundscape and audio characteristics of the podcast."""
    soundscape: str = Field(default="Quiet Studio", description="Acoustics and ambient noise level")
    music_mood: str = Field(default="Professional & Subtle", description="Genre and mood of background music")
    sfx_style: str = Field(default="Minimalist", description="Style of sound effects used (e.g., tech-inspired, natural)")

class ShowRules(BaseModel):
    """Consistency rules for the podcast narrative and structure."""
    intro_format: str = Field(..., description="Standard way to start the episode")
    outro_format: str = Field(..., description="Standard way to end the episode")
    interaction_tone: str = Field(default="Conversational", description="Tone between hosts or with audience")
    constraints: List[str] = Field(default_factory=list, description="Specific things to always do or avoid")

class AudienceDNA(BaseModel):
    """Details about the target audience."""
    expertise_level: str = Field(..., description="Target audience expertise level (Beginner, Intermediate, Expert)")
    interests: List[str] = Field(default_factory=list, description="Primary interests of the audience")
    pain_points: List[str] = Field(default_factory=list, description="Common challenges or problems the audience faces")
    demographics: Optional[str] = Field(None, description="General demographic information")

class BrandDNA(BaseModel):
    """Details about the brand and industry context."""
    industry: str = Field(..., description="Primary industry or niche")
    tone: str = Field(..., description="Overall brand tone (e.g., Professional, Casual, Inspirational)")
    communication_style: str = Field(..., description="Preferred communication style (e.g., Socratic, Storytelling, Analytical)")
    key_messages: List[str] = Field(default_factory=list, description="Core messages the brand wants to convey")
    competitor_context: Optional[str] = Field(None, description="Context on how to differentiate from competitors")

class PodcastBible(BaseModel):
    """The complete structured Podcast Bible SSOT."""
    project_id: Optional[str] = Field(default=None, description="Associated project ID")
    host: HostPersona = Field(..., description="Host persona details")
    audience: AudienceDNA = Field(..., description="Target audience details")
    brand: BrandDNA = Field(..., description="Brand and industry context")
    visual_style: VisualStyle = Field(..., description="Visual aesthetic and environment")
    audio_environment: AudioEnvironment = Field(..., description="Soundscape and music details")
    show_rules: ShowRules = Field(..., description="Consistency and structural rules")
