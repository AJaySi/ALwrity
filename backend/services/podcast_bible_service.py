from typing import Dict, Any, Optional
from loguru import logger
from services.product_marketing.personalization_service import PersonalizationService
from models.podcast_bible_models import (
    PodcastBible, 
    HostPersona, 
    AudienceDNA, 
    BrandDNA, 
    VisualStyle, 
    AudioEnvironment, 
    ShowRules
)

class PodcastBibleService:
    """Service for generating and managing the Podcast Bible."""

    def __init__(self):
        self.personalization_service = PersonalizationService()

    def generate_bible(self, user_id: str, project_id: str) -> PodcastBible:
        """Generate a Podcast Bible from onboarding data."""
        logger.info(f"Generating Podcast Bible for user {user_id}")
        
        try:
            preferences = self.personalization_service.get_user_preferences(user_id)
            writing_style = preferences.get("writing_style", {})
            style_prefs = preferences.get("style_preferences", {})
            target_audience = preferences.get("target_audience", {})
            industry = preferences.get("industry", "General Business")
            
            # 1. Map Host Persona
            host = HostPersona(
                name="Your AI Host",
                background=f"Expert in {industry}",
                expertise_level=writing_style.get("complexity", "Expert").capitalize(),
                personality_traits=[
                    writing_style.get("tone", "Professional").capitalize(),
                    writing_style.get("engagement_level", "Informative").capitalize()
                ],
                vocal_style=writing_style.get("voice", "Authoritative").capitalize(),
                vocal_characteristics=["Clear", "Articulate", writing_style.get("voice", "Steady")],
                look=f"A professional individual dressed in business-casual attire, fitting the {industry} industry aesthetic.",
                catchphrases=[]
            )
            
            # 2. Map Audience DNA
            audience = AudienceDNA(
                expertise_level=target_audience.get("expertise_level", "Intermediate").capitalize(),
                interests=target_audience.get("interests", ["Industry Trends", "Innovation"]),
                pain_points=target_audience.get("pain_points", ["Staying ahead of competition", "Efficiency"]),
                demographics=None
            )
            
            # 3. Map Brand DNA
            brand = BrandDNA(
                industry=industry,
                tone=writing_style.get("tone", "Professional").capitalize(),
                communication_style=writing_style.get("engagement_level", "Informative").capitalize(),
                key_messages=preferences.get("brand_values", []),
                competitor_context=None
            )

            # 4. Map Visual Style
            visual = VisualStyle(
                style_preset=style_prefs.get("aesthetic", "Professional Studio").capitalize(),
                environment=f"A modern {industry}-themed podcast studio with professional equipment.",
                lighting="Soft, warm studio lighting with subtle rim lights.",
                color_palette=preferences.get("brand_colors", ["#1e293b", "#3b82f6"]),
                camera_style="Dynamic mid-shots with occasional close-ups for emphasis."
            )

            # 5. Map Audio Environment
            audio_env = AudioEnvironment(
                soundscape="Pristine studio environment with deep, warm acoustics.",
                music_mood=f"{writing_style.get('tone', 'Professional').capitalize()} & {writing_style.get('engagement_level', 'Upbeat').capitalize()}",
                sfx_style="Modern, clean interface-inspired sounds."
            )

            # 6. Map Show Rules
            show_rules = ShowRules(
                intro_format=f"Start with a high-energy hook about the episode topic, followed by a warm welcome and an overview of the {industry} insights to be shared.",
                outro_format="Summarize the key takeaways, provide a clear call to action, and sign off with a professional closing.",
                interaction_tone=writing_style.get("engagement_level", "Conversational").capitalize(),
                constraints=[
                    "Avoid overly technical jargon unless defined",
                    "Keep segments concise and factual",
                    f"Maintain a {writing_style.get('tone', 'Professional')} tone at all times"
                ]
            )
            
            bible = PodcastBible(
                project_id=project_id,
                host=host,
                audience=audience,
                brand=brand,
                visual_style=visual,
                audio_environment=audio_env,
                show_rules=show_rules
            )
            
            logger.info(f"Podcast Bible generated successfully for project {project_id}")
            return bible
            
        except Exception as e:
            logger.error(f"Error generating Podcast Bible: {str(e)}")
            # Return a default bible if something goes wrong to ensure project creation doesn't fail
            return self._get_default_bible(project_id)

    def _get_default_bible(self, project_id: str) -> PodcastBible:
        """Return a sensible default Bible."""
        return PodcastBible(
            project_id=project_id,
            host=HostPersona(
                name="AI Host",
                background="Industry Professional",
                expertise_level="Expert",
                vocal_style="Authoritative",
                vocal_characteristics=["Deep", "Steady"]
            ),
            audience=AudienceDNA(
                expertise_level="Intermediate",
                interests=["Industry Trends", "Technology"],
                pain_points=["Staying Competitive", "Operational Efficiency"]
            ),
            brand=BrandDNA(
                industry="General Business",
                tone="Professional",
                communication_style="Analytical"
            ),
            visual_style=VisualStyle(
                environment="Professional modern office studio",
                color_palette=["#000000", "#FFFFFF"]
            ),
            audio_environment=AudioEnvironment(),
            show_rules=ShowRules(
                intro_format="Standard welcome and topic introduction.",
                outro_format="Summary and sign-off."
            )
        )

    def serialize_bible(self, bible: PodcastBible) -> str:
        """Serialize the Bible into a prompt-friendly text block."""
        return f"""
<podcast_bible>
HOST PERSONA:
- Name: {bible.host.name}
- Background: {bible.host.background}
- Expertise Level: {bible.host.expertise_level}
- Personality: {', '.join(bible.host.personality_traits)}
- Vocal Style: {bible.host.vocal_style}
- Vocal Characteristics: {', '.join(bible.host.vocal_characteristics)}
- Visual Look: {bible.host.look}

TARGET AUDIENCE:
- Expertise: {bible.audience.expertise_level}
- Interests: {', '.join(bible.audience.interests)}
- Pain Points: {', '.join(bible.audience.pain_points)}

BRAND & STYLE:
- Industry: {bible.brand.industry}
- Tone: {bible.brand.tone}
- Communication Style: {bible.brand.communication_style}
- Visual Style Preset: {bible.visual_style.style_preset}
- Environment: {bible.visual_style.environment}
- Lighting: {bible.visual_style.lighting}

AUDIO ENVIRONMENT:
- Soundscape: {bible.audio_environment.soundscape}
- Music Mood: {bible.audio_environment.music_mood}

SHOW RULES & STRUCTURE:
- Intro Format: {bible.show_rules.intro_format}
- Outro Format: {bible.show_rules.outro_format}
- Interaction Tone: {bible.show_rules.interaction_tone}
- Constraints: {', '.join(bible.show_rules.constraints)}
</podcast_bible>
"""
