"""
Facebook Persona Prompts
Contains Facebook-specific persona prompt generation logic.
"""

from typing import Dict, Any
from loguru import logger


class FacebookPersonaPrompts:
    """Facebook-specific persona prompt generation."""
    
    @staticmethod
    def build_facebook_system_prompt(core_persona: Dict[str, Any]) -> str:
        """
        Build optimized system prompt with core persona for Facebook generation.
        This moves the core persona to system prompt to free up context window.
        """
        import json

        return f"""You are an expert Facebook content strategist specializing in community engagement and social sharing optimization.

CORE PERSONA FOUNDATION:
{json.dumps(core_persona, indent=2)}

TASK: Create Facebook-optimized persona adaptations that maintain core identity while maximizing community engagement and Facebook algorithm performance.

FOCUS AREAS:
- Community-focused tone and engagement strategies
- Facebook algorithm optimization (engagement, reach, timing)
- Social sharing and viral content potential
- Facebook-specific features (Stories, Reels, Live, Groups, Events)
- Audience interaction and community building"""

    @staticmethod
    def build_focused_facebook_prompt(onboarding_data: Dict[str, Any]) -> str:
        """
        Build focused Facebook prompt without core persona JSON to optimize context usage.
        """
        # Extract audience context
        audience_context = FacebookPersonaPrompts._extract_audience_context(onboarding_data)

        target_audience = audience_context.get("target_audience", "general")
        content_goals = audience_context.get("content_goals", "engagement")
        business_type = audience_context.get("business_type", "general")

        return f"""FACEBOOK OPTIMIZATION TASK: Create Facebook-specific adaptations for the core persona.

AUDIENCE CONTEXT:
- Target: {target_audience} | Goals: {content_goals} | Business: {business_type}
- Demographics: {audience_context.get('demographics', [])}
- Interests: {audience_context.get('interests', [])}
- Behaviors: {audience_context.get('behaviors', [])}

FACEBOOK SPECS:
- Character Limit: 63,206 | Optimal Length: 40-80 words
- Algorithm Priority: Engagement, meaningful interactions, community building
- Content Types: Posts, Stories, Reels, Live, Events, Groups, Carousels, Polls
- Hashtag Strategy: 1-2 recommended (max 30)
- Link Strategy: Native content performs better

OPTIMIZATION REQUIREMENTS:

1. COMMUNITY-FOCUSED TONE:
   - Authentic, conversational, approachable language
   - Balance professionalism with relatability
   - Incorporate storytelling and personal anecdotes
   - Community-building elements

2. CONTENT STRATEGY FOR {business_type.upper()}:
   - Community engagement content for {target_audience}
   - Social sharing optimization for {content_goals}
   - Facebook-specific content formats
   - Audience interaction strategies
   - Viral content potential

3. FACEBOOK-SPECIFIC ADAPTATIONS:
   - Algorithm optimization (engagement, reach, timing)
   - Platform-specific vocabulary and terminology
   - Engagement patterns for Facebook audience
   - Community interaction strategies
   - Facebook feature optimization (Stories, Reels, Live, Events, Groups)

4. AUDIENCE TARGETING:
   - Demographic-specific positioning
   - Interest-based content adaptation
   - Behavioral targeting considerations
   - Community building strategies
   - Engagement optimization tactics

Generate comprehensive Facebook-optimized persona maintaining core identity while maximizing community engagement and social sharing potential."""

    @staticmethod
    def _extract_audience_context(onboarding_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract audience context from onboarding data."""
        try:
            # Get enhanced analysis data
            enhanced_analysis = onboarding_data.get("enhanced_analysis", {})
            website_analysis = onboarding_data.get("website_analysis", {}) or {}
            research_prefs = onboarding_data.get("research_preferences", {}) or {}
            
            # Extract audience intelligence
            audience_intel = enhanced_analysis.get("audience_intelligence", {})
            
            # Extract target audience from website analysis
            target_audience_data = website_analysis.get("target_audience", {}) or {}
            
            # Build audience context
            audience_context = {
                "target_audience": target_audience_data.get("primary_audience", "general"),
                "content_goals": research_prefs.get("content_goals", "engagement"),
                "business_type": website_analysis.get("business_type", "general"),
                "demographics": audience_intel.get("demographics", []),
                "interests": audience_intel.get("interests", []),
                "behaviors": audience_intel.get("behaviors", []),
                "psychographic_profile": audience_intel.get("psychographic_profile", "general"),
                "pain_points": audience_intel.get("pain_points", []),
                "engagement_level": audience_intel.get("engagement_level", "moderate")
            }
            
            return audience_context
            
        except Exception as e:
            logger.warning(f"Error extracting audience context: {str(e)}")
            return {
                "target_audience": "general",
                "content_goals": "engagement",
                "business_type": "general",
                "demographics": [],
                "interests": [],
                "behaviors": [],
                "psychographic_profile": "general",
                "pain_points": [],
                "engagement_level": "moderate"
            }

    @staticmethod
    def build_facebook_validation_prompt(persona_data: Dict[str, Any]) -> str:
        """Build optimized prompt for validating Facebook persona data."""
        return f"""FACEBOOK PERSONA VALIDATION TASK: Validate Facebook persona data for completeness and quality.

PERSONA DATA:
{persona_data}

VALIDATION REQUIREMENTS:

1. COMPLETENESS CHECK:
   - Verify all required Facebook-specific fields are present
   - Check for missing algorithm optimization strategies
   - Validate engagement strategy completeness
   - Ensure content format rules are defined

2. QUALITY ASSESSMENT:
   - Evaluate Facebook algorithm optimization quality
   - Assess engagement strategy effectiveness
   - Check content format optimization
   - Validate audience targeting strategies

3. FACEBOOK-SPECIFIC VALIDATION:
   - Verify Facebook platform constraints are respected
   - Check for Facebook-specific best practices
   - Validate community building strategies
   - Ensure Facebook feature optimization

4. RECOMMENDATIONS:
   - Provide specific improvement suggestions
   - Identify missing optimization opportunities
   - Suggest Facebook-specific enhancements
   - Recommend engagement strategy improvements

Generate comprehensive validation report with scores, recommendations, and specific improvement suggestions for Facebook optimization."""

    @staticmethod
    def build_facebook_optimization_prompt(persona_data: Dict[str, Any]) -> str:
        """Build optimized prompt for optimizing Facebook persona data."""
        return f"""FACEBOOK PERSONA OPTIMIZATION TASK: Optimize Facebook persona data for maximum algorithm performance and community engagement.

CURRENT PERSONA DATA:
{persona_data}

OPTIMIZATION REQUIREMENTS:

1. ALGORITHM OPTIMIZATION:
   - Enhance Facebook algorithm performance strategies
   - Optimize for Facebook's engagement metrics
   - Improve content timing and frequency
   - Enhance audience targeting precision

2. ENGAGEMENT OPTIMIZATION:
   - Strengthen community building strategies
   - Enhance social sharing potential
   - Improve audience interaction tactics
   - Optimize content for viral potential

3. CONTENT FORMAT OPTIMIZATION:
   - Optimize for Facebook's content formats
   - Enhance visual content strategies
   - Improve video content optimization
   - Optimize for Facebook Stories and Reels

4. AUDIENCE TARGETING OPTIMIZATION:
   - Refine demographic targeting
   - Enhance interest-based targeting
   - Improve behavioral targeting
   - Optimize for Facebook's audience insights

5. COMMUNITY BUILDING OPTIMIZATION:
   - Enhance group management strategies
   - Improve event management tactics
   - Optimize live streaming strategies
   - Enhance community interaction methods

Generate optimized Facebook persona data with enhanced algorithm performance, engagement strategies, and community building tactics."""
