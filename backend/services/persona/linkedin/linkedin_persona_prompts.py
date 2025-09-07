"""
LinkedIn Persona Prompts
Contains LinkedIn-specific prompt generation for persona analysis.
"""

from typing import Dict, Any
import json
from loguru import logger


class LinkedInPersonaPrompts:
    """Handles LinkedIn-specific persona prompt generation."""
    
    @staticmethod
    def build_enhanced_linkedin_prompt(core_persona: Dict[str, Any], onboarding_data: Dict[str, Any]) -> str:
        """Build enhanced LinkedIn-specific persona prompt with professional optimization."""
        
        # Extract comprehensive professional context
        professional_context = LinkedInPersonaPrompts._extract_professional_context(onboarding_data)
        
        website_analysis = onboarding_data.get("website_analysis", {}) or {}
        target_audience = website_analysis.get("target_audience", {})
        industry_focus = professional_context.get("industry_focus", "general")
        expertise_level = professional_context.get("expertise_level", "intermediate")
        
        prompt = f"""
LINKEDIN PROFESSIONAL PERSONA OPTIMIZATION TASK: Create a comprehensive LinkedIn-optimized writing persona for professional networking and thought leadership.

CORE PERSONA FOUNDATION:
{json.dumps(core_persona, indent=2)}

PROFESSIONAL CONTEXT:
- Industry: {industry_focus}
- Expertise Level: {expertise_level}
- Company Size: {professional_context.get('company_size', 'Not specified')}
- Business Model: {professional_context.get('business_model', 'Not specified')}
- Professional Role: {professional_context.get('professional_role', 'Not specified')}
- Demographics: {professional_context.get('target_demographics', [])}
- Psychographic: {professional_context.get('psychographic_profile', 'Not specified')}

LINKEDIN PLATFORM SPECIFICATIONS:
- Character Limit: 3,000 characters
- Optimal Post Length: 150-300 words for maximum engagement
- Professional Network: B2B focused, career-oriented audience
- Algorithm Priority: Engagement, relevance, professional value
- Content Types: Posts, Articles, Polls, Videos, Carousels, Events
- Hashtag Limit: 3-5 hashtags for optimal reach
- Link Strategy: Place external links in first comment for algorithm optimization

LINKEDIN PROFESSIONAL OPTIMIZATION REQUIREMENTS:

1. PROFESSIONAL TONE & VOICE:
   - Maintain authoritative yet approachable professional tone
   - Use industry-specific terminology appropriately
   - Balance expertise with accessibility for {expertise_level} audience
   - Incorporate thought leadership elements
   - Include professional storytelling and case studies

2. CONTENT STRATEGY FOR {industry_focus.upper()}:
   - Industry insights for {expertise_level} professionals
   - Professional development content for {professional_context.get('target_demographics', [])}
   - Business strategy discussions for {professional_context.get('business_model', 'general business')}
   - Networking focus for {professional_context.get('company_size', 'all company sizes')}
   - Thought leadership positioning as {professional_context.get('professional_role', 'professional')}

3. ENGAGEMENT OPTIMIZATION:
   - Professional question frameworks for discussion
   - Industry-relevant polling strategies
   - Professional networking call-to-actions
   - Thought leadership positioning
   - Community building through professional value

4. LINKEDIN-SPECIFIC FEATURES:
   - Native video optimization for professional content
   - LinkedIn Articles for long-form thought leadership
   - LinkedIn Polls for industry insights and engagement
   - LinkedIn Events for professional networking
   - LinkedIn Carousels for educational content
   - LinkedIn Live for professional discussions

5. PROFESSIONAL NETWORKING ELEMENTS:
   - Industry-specific hashtag strategy
   - Professional mention and tagging etiquette
   - Thought leadership positioning
   - Professional relationship building
   - Career advancement focus

6. CONTENT FORMAT OPTIMIZATION:
   - Hook strategies for professional feed
   - "See More" optimization for longer posts
   - Professional call-to-action frameworks
   - Industry-specific content structures
   - Professional storytelling techniques

7. LINKEDIN ALGORITHM OPTIMIZATION:
   - Professional engagement patterns
   - Industry-relevant content timing
   - Professional network interaction strategies
   - Thought leadership content performance
   - Professional community building

8. INDUSTRY-SPECIFIC ADAPTATIONS FOR {industry_focus.upper()}:
   - Terminology appropriate for {expertise_level} level
   - Professional development for {professional_context.get('target_demographics', [])}
   - Trend discussions for {professional_context.get('business_model', 'general business')}
   - Networking strategies for {professional_context.get('company_size', 'all company sizes')}
   - Thought leadership as {professional_context.get('professional_role', 'professional')}
   - Content addressing {professional_context.get('psychographic_profile', 'professional needs')}
   - Business insights for {professional_context.get('conversion_focus', 'business growth')}

PROFESSIONAL EXCELLENCE STANDARDS:
- Maintain high professional standards
- Focus on value-driven content
- Emphasize thought leadership and expertise
- Build professional credibility and authority
- Foster meaningful professional relationships
- Provide actionable business insights
- Support professional development and growth

Generate a comprehensive LinkedIn-optimized persona that positions the user as a thought leader in {industry_focus} while maintaining professional excellence and maximizing LinkedIn's professional networking potential.
"""
        
        return prompt
    
    @staticmethod
    def get_linkedin_platform_constraints() -> Dict[str, Any]:
        """Get LinkedIn-specific platform constraints and best practices."""
        return {
            "character_limit": 3000,
            "optimal_length": "150-300 words",
            "professional_tone": True,
            "hashtag_limit": 5,
            "rich_media": True,
            "long_form": True,
            "thought_leadership": True,
            "networking_focus": True,
            "career_development": True,
            "industry_insights": True,
            "professional_storytelling": True,
            "b2b_optimized": True,
            "algorithm_engagement": True,
            "native_video": True,
            "linkedin_articles": True,
            "linkedin_polls": True,
            "linkedin_events": True,
            "linkedin_carousels": True,
            "linkedin_live": True
        }
    
    @staticmethod
    def _extract_professional_context(onboarding_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract comprehensive professional context from onboarding data."""
        
        professional_context = {
            "industry_focus": "general",
            "expertise_level": "intermediate", 
            "company_size": "Not specified",
            "business_model": "Not specified",
            "professional_role": "Not specified",
            "geographic_focus": "global",
            "target_demographics": [],
            "psychographic_profile": "",
            "content_purpose": "",
            "conversion_focus": "",
            "research_depth": "",
            "content_types": []
        }
        
        # Extract from website analysis
        website_analysis = onboarding_data.get("website_analysis", {}) or {}
        
        # Target audience information
        target_audience = website_analysis.get("target_audience", {})
        if target_audience:
            professional_context["industry_focus"] = target_audience.get("industry_focus", "general")
            professional_context["expertise_level"] = target_audience.get("expertise_level", "intermediate")
            professional_context["geographic_focus"] = target_audience.get("geographic_focus", "global")
            professional_context["target_demographics"] = target_audience.get("demographics", [])
            professional_context["psychographic_profile"] = target_audience.get("psychographic_profile", "")
        
        # Content type and business context
        content_type = website_analysis.get("content_type", {})
        if content_type:
            professional_context["content_purpose"] = content_type.get("purpose", "")
            professional_context["conversion_focus"] = content_type.get("conversion_focus", "")
        
        # Company and business information from crawl results
        crawl_result = website_analysis.get("crawl_result", {})
        if crawl_result:
            domain_info = crawl_result.get("domain_info", {})
            if domain_info:
                professional_context["company_size"] = domain_info.get("company_size", "Not specified")
                professional_context["business_model"] = domain_info.get("business_model", "Not specified")
            
            brand_info = crawl_result.get("brand_info", {})
            if brand_info:
                professional_context["professional_role"] = brand_info.get("professional_role", "Not specified")
        
        # Research preferences
        research_prefs = onboarding_data.get("research_preferences", {})
        if research_prefs:
            professional_context["research_depth"] = research_prefs.get("research_depth", "")
            professional_context["content_types"] = research_prefs.get("content_types", [])
        
        # Enhanced analysis data
        enhanced_analysis = onboarding_data.get("enhanced_analysis", {})
        if enhanced_analysis:
            audience_intel = enhanced_analysis.get("audience_intelligence", {})
            if audience_intel:
                # Override with more detailed information if available
                if audience_intel.get("industry_focus"):
                    professional_context["industry_focus"] = audience_intel["industry_focus"]
                if audience_intel.get("expertise_level"):
                    professional_context["expertise_level"] = audience_intel["expertise_level"]
                if audience_intel.get("psychographic_profile"):
                    professional_context["psychographic_profile"] = audience_intel["psychographic_profile"]
            
            brand_voice = enhanced_analysis.get("brand_voice_analysis", {})
            if brand_voice:
                if brand_voice.get("primary_content_type"):
                    professional_context["content_purpose"] = brand_voice["primary_content_type"]
                if brand_voice.get("conversion_focus"):
                    professional_context["conversion_focus"] = brand_voice["conversion_focus"]
        
        return professional_context
    
    @staticmethod
    def build_linkedin_system_prompt(core_persona: Dict[str, Any]) -> str:
        """
        Build system prompt with core persona for LinkedIn generation.
        This moves the core persona to system prompt to free up context window.
        """
        import json
        
        return f"""You are an expert LinkedIn content strategist and professional networking specialist.

CORE PERSONA FOUNDATION:
{json.dumps(core_persona, indent=2)}

Your task is to create LinkedIn-optimized persona adaptations that maintain the core persona's identity while optimizing for professional networking, thought leadership, and B2B engagement on LinkedIn.

Focus on:
- Professional tone and authority
- Industry-specific optimization
- LinkedIn algorithm best practices
- B2B engagement strategies
- Professional networking optimization"""
    
    @staticmethod
    def build_focused_linkedin_prompt(onboarding_data: Dict[str, Any]) -> str:
        """
        Build focused LinkedIn prompt without core persona JSON to optimize context usage.
        """
        # Extract professional context
        professional_context = LinkedInPersonaPrompts._extract_professional_context(onboarding_data)
        
        industry_focus = professional_context.get("industry_focus", "general")
        expertise_level = professional_context.get("expertise_level", "intermediate")
        
        return f"""LINKEDIN PROFESSIONAL OPTIMIZATION TASK: Create LinkedIn-specific adaptations for the core persona.

PROFESSIONAL CONTEXT:
- Industry: {industry_focus}
- Expertise Level: {expertise_level}
- Company Size: {professional_context.get('company_size', 'Not specified')}
- Business Model: {professional_context.get('business_model', 'Not specified')}
- Professional Role: {professional_context.get('professional_role', 'Not specified')}
- Demographics: {professional_context.get('target_demographics', [])}
- Psychographic: {professional_context.get('psychographic_profile', 'Not specified')}

LINKEDIN PLATFORM SPECIFICATIONS:
- Character Limit: 3,000 characters
- Optimal Post Length: 150-300 words for maximum engagement
- Professional Network: B2B focused, career-oriented audience
- Algorithm Priority: Engagement, relevance, professional value
- Content Types: Posts, Articles, Polls, Videos, Carousels, Events
- Hashtag Limit: 3-5 hashtags for optimal reach
- Link Strategy: Place external links in first comment for algorithm optimization

LINKEDIN OPTIMIZATION REQUIREMENTS:

1. PROFESSIONAL TONE & VOICE:
   - Maintain authoritative yet approachable professional tone
   - Use industry-specific terminology appropriately
   - Balance expertise with accessibility for {expertise_level} audience
   - Incorporate thought leadership elements
   - Include professional storytelling and case studies

2. CONTENT STRATEGY FOR {industry_focus.upper()}:
   - Industry insights for {expertise_level} professionals
   - Professional development content for {professional_context.get('target_demographics', [])}
   - Business strategy discussions for {professional_context.get('business_model', 'general business')}
   - Networking focus for {professional_context.get('company_size', 'all company sizes')}
   - Thought leadership positioning as {professional_context.get('professional_role', 'professional')}

3. LINKEDIN-SPECIFIC ADAPTATIONS:
   - Optimize sentence structure for professional readability
   - Create platform-specific vocabulary and terminology
   - Define engagement patterns for B2B audience
   - Establish professional networking strategies
   - Include LinkedIn feature optimization (Articles, Polls, Events, etc.)

4. ALGORITHM OPTIMIZATION:
   - Engagement patterns for professional audience
   - Content timing for maximum reach
   - Professional value metrics
   - Network interaction strategies

5. PROFESSIONAL CONTEXT OPTIMIZATION:
   - Industry-specific positioning
   - Expertise level adaptation
   - Company size considerations
   - Business model alignment
   - Professional role authority
   - Demographic targeting
   - Psychographic engagement
   - Conversion optimization

Generate a comprehensive LinkedIn-optimized persona that maintains the core persona's identity while maximizing professional networking and thought leadership potential on LinkedIn."""
