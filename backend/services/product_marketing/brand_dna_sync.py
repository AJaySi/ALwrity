"""
Brand DNA Sync Service
Normalizes persona data and onboarding information into reusable brand tokens.
"""

from typing import Dict, Any, Optional
from loguru import logger

from services.onboarding import OnboardingDatabaseService
from services.database import SessionLocal


class BrandDNASyncService:
    """Service to sync and normalize brand DNA from onboarding and persona data."""
    
    def __init__(self):
        """Initialize Brand DNA Sync Service."""
        self.logger = logger
        logger.info("[Brand DNA Sync] Service initialized")
    
    def get_brand_dna_tokens(self, user_id: str) -> Dict[str, Any]:
        """
        Extract and normalize brand DNA tokens from onboarding and persona data.
        
        Args:
            user_id: User ID to fetch data for
            
        Returns:
            Dictionary of brand DNA tokens ready for prompt injection
        """
        try:
            db = SessionLocal()
            try:
                onboarding_db = OnboardingDatabaseService(db)
                website_analysis = onboarding_db.get_website_analysis(user_id, db)
                persona_data = onboarding_db.get_persona_data(user_id, db)
                competitor_analyses = onboarding_db.get_competitor_analysis(user_id, db)
            finally:
                db.close()
            
            brand_tokens = {
                "writing_style": {},
                "target_audience": {},
                "visual_identity": {},
                "persona": {},
                "competitive_positioning": {},
            }
            
            # Extract writing style from website analysis
            if website_analysis:
                writing_style = website_analysis.get('writing_style') or {}
                target_audience = website_analysis.get('target_audience') or {}
                brand_analysis = website_analysis.get('brand_analysis') or {}
                style_guidelines = website_analysis.get('style_guidelines') or {}
                
                # Ensure writing_style is a dict before accessing
                if isinstance(writing_style, dict):
                    brand_tokens["writing_style"] = {
                        "tone": writing_style.get('tone', 'professional'),
                        "voice": writing_style.get('voice', 'authoritative'),
                        "complexity": writing_style.get('complexity', 'intermediate'),
                        "engagement_level": writing_style.get('engagement_level', 'moderate'),
                    }
                
                # Ensure target_audience is a dict before accessing
                if isinstance(target_audience, dict):
                    brand_tokens["target_audience"] = {
                        "demographics": target_audience.get('demographics', []),
                        "industry_focus": target_audience.get('industry_focus', 'general'),
                        "expertise_level": target_audience.get('expertise_level', 'intermediate'),
                    }
                
                # Ensure brand_analysis is a dict before accessing
                if isinstance(brand_analysis, dict) and brand_analysis:
                    brand_tokens["visual_identity"] = {
                        "color_palette": brand_analysis.get('color_palette', []),
                        "brand_values": brand_analysis.get('brand_values', []),
                        "positioning": brand_analysis.get('positioning', ''),
                    }
                
                # Add style_guidelines if available and visual_identity exists
                if style_guidelines and isinstance(style_guidelines, dict):
                    if "visual_identity" not in brand_tokens:
                        brand_tokens["visual_identity"] = {}
                    brand_tokens["visual_identity"]["style_guidelines"] = style_guidelines
            
            # Extract persona data
            if persona_data:
                core_persona = persona_data.get('corePersona') or {}
                platform_personas = persona_data.get('platformPersonas') or {}
                
                # Ensure core_persona is a dict before accessing
                if isinstance(core_persona, dict) and core_persona:
                    brand_tokens["persona"] = {
                        "persona_name": core_persona.get('persona_name', ''),
                        "archetype": core_persona.get('archetype', ''),
                        "core_belief": core_persona.get('core_belief', ''),
                        "linguistic_fingerprint": core_persona.get('linguistic_fingerprint', {}),
                    }
                
                # Ensure persona dict exists before setting platform_personas
                if "persona" not in brand_tokens:
                    brand_tokens["persona"] = {}
                
                # Only set platform_personas if it's a valid dict
                if isinstance(platform_personas, dict):
                    brand_tokens["persona"]["platform_personas"] = platform_personas
            
            # Extract competitive positioning
            if competitor_analyses and isinstance(competitor_analyses, list) and len(competitor_analyses) > 0:
                # Extract differentiation points
                brand_tokens["competitive_positioning"] = {
                    "differentiators": [],
                    "unique_value_props": [],
                }
                
                for competitor in competitor_analyses[:3]:  # Top 3 competitors
                    if not isinstance(competitor, dict):
                        continue
                    
                    analysis_data = competitor.get('analysis_data') or {}
                    if isinstance(analysis_data, dict) and analysis_data:
                        competitive_insights = analysis_data.get('competitive_analysis') or {}
                        if isinstance(competitive_insights, dict) and competitive_insights:
                            differentiators = competitive_insights.get('differentiators', [])
                            if isinstance(differentiators, list) and differentiators:
                                brand_tokens["competitive_positioning"]["differentiators"].extend(
                                    differentiators[:2]
                                )
            
            logger.info(f"[Brand DNA Sync] Extracted brand tokens for user {user_id}")
            return brand_tokens
            
        except Exception as e:
            logger.error(f"[Brand DNA Sync] Error extracting brand tokens: {str(e)}")
            return {
                "writing_style": {"tone": "professional", "voice": "authoritative"},
                "target_audience": {"demographics": [], "expertise_level": "intermediate"},
                "visual_identity": {},
                "persona": {},
                "competitive_positioning": {},
            }
    
    def get_channel_specific_dna(
        self,
        user_id: str,
        channel: str
    ) -> Dict[str, Any]:
        """
        Get channel-specific brand DNA adaptations.
        
        Args:
            user_id: User ID
            channel: Target channel (instagram, linkedin, tiktok, etc.)
            
        Returns:
            Channel-specific brand DNA tokens
        """
        brand_tokens = self.get_brand_dna_tokens(user_id)
        channel_dna = brand_tokens.copy()
        
        # Get platform-specific persona if available
        persona = brand_tokens.get("persona") or {}
        platform_personas = persona.get("platform_personas") or {}
        
        if isinstance(platform_personas, dict) and channel in platform_personas:
            platform_persona = platform_personas[channel]
            if isinstance(platform_persona, dict):
                channel_dna["platform_adaptation"] = {
                    "content_format_rules": platform_persona.get('content_format_rules') or {},
                    "engagement_patterns": platform_persona.get('engagement_patterns') or {},
                    "visual_identity": platform_persona.get('visual_identity') or {},
                }
        
        return channel_dna

