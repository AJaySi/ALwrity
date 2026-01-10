"""
Personalization Service
Extracts ALL onboarding data and provides personalized defaults for forms and recommendations.
"""

from typing import Dict, Any, Optional, List
from loguru import logger

from services.onboarding.database_service import OnboardingDatabaseService
from services.database import SessionLocal


class PersonalizationService:
    """
    Service for extracting user preferences from onboarding data
    and providing personalized defaults and recommendations.
    """
    
    def __init__(self):
        """Initialize Personalization Service."""
        self.logger = logger
        logger.info("[Personalization Service] Initialized")
    
    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """
        Get comprehensive user preferences from ALL onboarding data.
        
        Returns:
            Dictionary with personalized preferences:
            - industry: User's industry
            - target_audience: Demographics, expertise level
            - platform_preferences: Preferred platforms from persona data
            - content_preferences: Preferred content types
            - style_preferences: Visual style, tone, voice
            - brand_colors: Brand color palette
            - templates: Recommended templates for user's industry
            - channels: Recommended channels based on platform personas
        """
        db = SessionLocal()
        try:
            onboarding_db = OnboardingDatabaseService(db)
            website_analysis = onboarding_db.get_website_analysis(user_id, db)
            persona_data = onboarding_db.get_persona_data(user_id, db)
            competitor_analyses = onboarding_db.get_competitor_analysis(user_id, db)
            
            preferences = {
                "industry": None,
                "target_audience": {},
                "platform_preferences": [],
                "content_preferences": [],
                "style_preferences": {},
                "brand_colors": [],
                "recommended_templates": [],
                "recommended_channels": [],
                "writing_style": {},
                "brand_values": [],
            }
            
            # Extract from website_analysis
            if website_analysis:
                # Industry
                target_audience = website_analysis.get("target_audience", {})
                preferences["industry"] = target_audience.get("industry_focus")
                
                # Target audience
                preferences["target_audience"] = {
                    "demographics": target_audience.get("demographics", []),
                    "expertise_level": target_audience.get("expertise_level", "intermediate"),
                    "industry_focus": target_audience.get("industry_focus"),
                }
                
                # Writing style
                writing_style = website_analysis.get("writing_style", {})
                preferences["writing_style"] = {
                    "tone": writing_style.get("tone", "professional"),
                    "voice": writing_style.get("voice", "authoritative"),
                    "complexity": writing_style.get("complexity", "intermediate"),
                    "engagement_level": writing_style.get("engagement_level", "moderate"),
                }
                
                # Brand colors
                brand_analysis = website_analysis.get("brand_analysis", {})
                if brand_analysis:
                    preferences["brand_colors"] = brand_analysis.get("color_palette", [])
                    preferences["brand_values"] = brand_analysis.get("brand_values", [])
                
                # Style preferences
                style_guidelines = website_analysis.get("style_guidelines", {})
                if style_guidelines:
                    preferences["style_preferences"] = {
                        "aesthetic": style_guidelines.get("aesthetic", "modern"),
                        "visual_style": style_guidelines.get("visual_style", "clean"),
                    }
            
            # Extract from persona_data
            if persona_data:
                core_persona = persona_data.get("corePersona", {})
                platform_personas = persona_data.get("platformPersonas", {})
                selected_platforms = persona_data.get("selectedPlatforms", [])
                
                # Platform preferences from selected platforms
                if selected_platforms:
                    preferences["platform_preferences"] = selected_platforms
                elif platform_personas:
                    # Extract platforms from platform personas
                    preferences["platform_preferences"] = list(platform_personas.keys())
                
                # Recommended channels based on platform personas
                if platform_personas:
                    # Prioritize platforms with active personas
                    preferences["recommended_channels"] = list(platform_personas.keys())[:5]  # Top 5
                
                # Content preferences from persona
                if core_persona:
                    content_format_rules = core_persona.get("content_format_rules", {})
                    if content_format_rules:
                        preferred_formats = content_format_rules.get("preferred_formats", [])
                        preferences["content_preferences"] = preferred_formats
            
            # Infer content preferences from industry
            if preferences["industry"]:
                industry_content_map = {
                    "ecommerce": ["product_images", "product_videos", "lifestyle_content"],
                    "saas": ["feature_highlights", "tutorials", "demo_videos"],
                    "education": ["tutorials", "educational_content", "explainer_videos"],
                    "healthcare": ["informational_content", "patient_stories", "educational_videos"],
                    "finance": ["informational_content", "trust_building", "expert_content"],
                    "fashion": ["lifestyle_images", "fashion_shows", "style_guides"],
                    "food": ["food_photography", "recipe_videos", "lifestyle_content"],
                }
                industry_lower = preferences["industry"].lower()
                for key, content_types in industry_content_map.items():
                    if key in industry_lower:
                        preferences["content_preferences"] = content_types
                        break
            
            # Recommend templates based on industry
            preferences["recommended_templates"] = self._get_recommended_templates(
                preferences.get("industry"),
                preferences.get("style_preferences", {}).get("aesthetic")
            )
            
            # Recommend channels if not already set
            if not preferences["recommended_channels"]:
                preferences["recommended_channels"] = self._get_recommended_channels(
                    preferences.get("industry"),
                    preferences.get("target_audience", {}).get("demographics", [])
                )
            
            logger.info(f"[Personalization] Extracted preferences for user {user_id}: industry={preferences.get('industry')}")
            return preferences
            
        except Exception as e:
            logger.error(f"[Personalization] Error getting user preferences: {str(e)}", exc_info=True)
            return self._get_default_preferences()
        finally:
            db.close()
    
    def get_personalized_defaults(
        self,
        user_id: str,
        form_type: str = "product_photoshoot"
    ) -> Dict[str, Any]:
        """
        Get personalized defaults for a specific form.
        
        Args:
            user_id: User ID
            form_type: Type of form (product_photoshoot, campaign_creator, product_video, etc.)
            
        Returns:
            Dictionary with pre-filled form values
        """
        preferences = self.get_user_preferences(user_id)
        defaults = {}
        
        if form_type == "product_photoshoot":
            defaults = {
                "environment": self._infer_environment(preferences),
                "background_style": self._infer_background_style(preferences),
                "lighting": self._infer_lighting(preferences),
                "style": self._infer_style(preferences),
                "resolution": "1024x1024",
                "num_variations": 1,
                "brand_colors": preferences.get("brand_colors", []),
            }
        
        elif form_type == "campaign_creator":
            defaults = {
                "channels": preferences.get("recommended_channels", ["instagram", "linkedin"]),
                "goal": self._infer_campaign_goal(preferences),
            }
        
        elif form_type == "product_video":
            defaults = {
                "video_type": self._infer_video_type(preferences),
                "resolution": "720p",
                "duration": 10,
            }
        
        elif form_type == "product_avatar":
            defaults = {
                "explainer_type": self._infer_explainer_type(preferences),
                "resolution": "720p",
            }
        
        return defaults
    
    def get_recommendations(self, user_id: str) -> Dict[str, Any]:
        """
        Get personalized recommendations for user.
        
        Returns:
            Dictionary with:
            - recommended_templates: Templates matching user's industry
            - recommended_channels: Channels matching user's platform personas
            - recommended_asset_types: Asset types matching user's content preferences
        """
        preferences = self.get_user_preferences(user_id)
        
        return {
            "templates": preferences.get("recommended_templates", []),
            "channels": preferences.get("recommended_channels", []),
            "asset_types": preferences.get("content_preferences", []),
            "industry": preferences.get("industry"),
            "reasoning": self._generate_recommendation_reasoning(preferences),
        }
    
    def _get_recommended_templates(
        self,
        industry: Optional[str],
        aesthetic: Optional[str] = None
    ) -> List[str]:
        """Get recommended template IDs based on industry and aesthetic."""
        templates = []
        
        if not industry:
            return ["ecommerce_product_shot", "lifestyle_product"]
        
        industry_lower = industry.lower() if industry else ""
        
        # Industry-based template recommendations
        if "ecommerce" in industry_lower or "retail" in industry_lower:
            templates.extend(["ecommerce_product_shot", "lifestyle_product"])
        elif "saas" in industry_lower or "tech" in industry_lower:
            templates.extend(["technical_product_detail", "lifestyle_product"])
        elif "luxury" in industry_lower or "premium" in industry_lower:
            templates.extend(["luxury_product_showcase", "lifestyle_product"])
        else:
            templates.extend(["ecommerce_product_shot", "lifestyle_product"])
        
        # Aesthetic-based adjustments
        if aesthetic:
            aesthetic_lower = aesthetic.lower()
            if "luxury" in aesthetic_lower or "premium" in aesthetic_lower:
                templates.insert(0, "luxury_product_showcase")
            elif "minimalist" in aesthetic_lower or "clean" in aesthetic_lower:
                templates.insert(0, "ecommerce_product_shot")
        
        return templates[:3]  # Return top 3
    
    def _get_recommended_channels(
        self,
        industry: Optional[str],
        demographics: List[str]
    ) -> List[str]:
        """Get recommended channels based on industry and demographics."""
        channels = []
        
        if not industry:
            return ["instagram", "linkedin"]
        
        industry_lower = industry.lower() if industry else ""
        
        # Industry-based channel recommendations
        if "b2b" in industry_lower or "saas" in industry_lower or "enterprise" in industry_lower:
            channels.extend(["linkedin", "twitter", "youtube"])
        elif "b2c" in industry_lower or "ecommerce" in industry_lower or "retail" in industry_lower:
            channels.extend(["instagram", "facebook", "pinterest", "tiktok"])
        elif "fashion" in industry_lower or "lifestyle" in industry_lower:
            channels.extend(["instagram", "pinterest", "tiktok"])
        elif "education" in industry_lower:
            channels.extend(["youtube", "linkedin", "facebook"])
        else:
            channels.extend(["instagram", "linkedin", "facebook"])
        
        # Demographics-based adjustments
        if demographics:
            demographics_str = " ".join(demographics).lower()
            if "young" in demographics_str or "millennial" in demographics_str or "gen z" in demographics_str:
                if "tiktok" not in channels:
                    channels.insert(0, "tiktok")
            if "professional" in demographics_str or "business" in demographics_str:
                if "linkedin" not in channels:
                    channels.insert(0, "linkedin")
        
        return channels[:5]  # Return top 5
    
    def _infer_environment(self, preferences: Dict[str, Any]) -> str:
        """Infer environment setting from preferences."""
        industry = preferences.get("industry", "").lower() if preferences.get("industry") else ""
        aesthetic = preferences.get("style_preferences", {}).get("aesthetic", "").lower()
        
        if "luxury" in aesthetic or "premium" in industry:
            return "studio"
        elif "ecommerce" in industry or "retail" in industry:
            return "studio"
        elif "lifestyle" in aesthetic:
            return "lifestyle"
        else:
            return "studio"
    
    def _infer_background_style(self, preferences: Dict[str, Any]) -> str:
        """Infer background style from preferences."""
        industry = preferences.get("industry", "").lower() if preferences.get("industry") else ""
        aesthetic = preferences.get("style_preferences", {}).get("aesthetic", "").lower()
        
        if "ecommerce" in industry or "retail" in industry:
            return "white"
        elif "luxury" in aesthetic:
            return "minimalist"
        elif "lifestyle" in aesthetic:
            return "lifestyle"
        else:
            return "white"
    
    def _infer_lighting(self, preferences: Dict[str, Any]) -> str:
        """Infer lighting style from preferences."""
        aesthetic = preferences.get("style_preferences", {}).get("aesthetic", "").lower()
        
        if "luxury" in aesthetic or "dramatic" in aesthetic:
            return "dramatic"
        elif "natural" in aesthetic:
            return "natural"
        else:
            return "studio"
    
    def _infer_style(self, preferences: Dict[str, Any]) -> str:
        """Infer image style from preferences."""
        aesthetic = preferences.get("style_preferences", {}).get("aesthetic", "").lower()
        industry = preferences.get("industry", "").lower() if preferences.get("industry") else ""
        
        if "luxury" in aesthetic or "premium" in industry:
            return "luxury"
        elif "minimalist" in aesthetic:
            return "minimalist"
        elif "technical" in industry or "saas" in industry:
            return "technical"
        else:
            return "photorealistic"
    
    def _infer_campaign_goal(self, preferences: Dict[str, Any]) -> str:
        """Infer campaign goal from preferences."""
        industry = preferences.get("industry", "").lower() if preferences.get("industry") else ""
        
        if "saas" in industry or "tech" in industry:
            return "conversion"
        elif "ecommerce" in industry or "retail" in industry:
            return "conversion"
        else:
            return "awareness"
    
    def _infer_video_type(self, preferences: Dict[str, Any]) -> str:
        """Infer video type from preferences."""
        content_prefs = preferences.get("content_preferences", [])
        
        if "demo" in str(content_prefs).lower():
            return "demo"
        elif "tutorial" in str(content_prefs).lower():
            return "feature_highlight"
        else:
            return "demo"
    
    def _infer_explainer_type(self, preferences: Dict[str, Any]) -> str:
        """Infer explainer type from preferences."""
        content_prefs = preferences.get("content_preferences", [])
        
        if "tutorial" in str(content_prefs).lower():
            return "tutorial"
        elif "feature" in str(content_prefs).lower():
            return "feature_explainer"
        else:
            return "product_overview"
    
    def _generate_recommendation_reasoning(self, preferences: Dict[str, Any]) -> str:
        """Generate human-readable reasoning for recommendations."""
        industry = preferences.get("industry", "your industry")
        channels = preferences.get("recommended_channels", [])
        
        reasoning = f"Based on your {industry} industry"
        if channels:
            reasoning += f" and platform preferences, we recommend focusing on {', '.join(channels[:3])}"
        reasoning += "."
        
        return reasoning
    
    def _get_default_preferences(self) -> Dict[str, Any]:
        """Get default preferences when onboarding data is unavailable."""
        return {
            "industry": None,
            "target_audience": {},
            "platform_preferences": ["instagram", "linkedin"],
            "content_preferences": [],
            "style_preferences": {},
            "brand_colors": [],
            "recommended_templates": ["ecommerce_product_shot", "lifestyle_product"],
            "recommended_channels": ["instagram", "linkedin", "facebook"],
            "writing_style": {
                "tone": "professional",
                "voice": "authoritative",
            },
            "brand_values": [],
        }
