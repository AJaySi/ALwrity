"""
Onboarding Data Service
Extracts real user data from onboarding to personalize AI inputs
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from loguru import logger
from datetime import datetime
import json

from services.database import get_db_session
from models.onboarding import OnboardingSession, WebsiteAnalysis, ResearchPreferences

class OnboardingDataService:
    """Service to extract and use real onboarding data for AI personalization."""
    
    def __init__(self, db: Optional[Session] = None):
        """Initialize the onboarding data service."""
        self.db = db
        logger.info("OnboardingDataService initialized")
    
    def get_user_website_analysis(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get website analysis data for a specific user.
        
        Args:
            user_id: User ID to get data for
            
        Returns:
            Website analysis data or None if not found
        """
        try:
            session = self.db or get_db_session()
            
            # Find onboarding session for user
            onboarding_session = session.query(OnboardingSession).filter(
                OnboardingSession.user_id == user_id
            ).first()
            
            if not onboarding_session:
                logger.warning(f"No onboarding session found for user {user_id}")
                return None
            
            # Get website analysis for this session
            website_analysis = session.query(WebsiteAnalysis).filter(
                WebsiteAnalysis.session_id == onboarding_session.id
            ).first()
            
            if not website_analysis:
                logger.warning(f"No website analysis found for user {user_id}")
                return None
            
            return website_analysis.to_dict()
            
        except Exception as e:
            logger.error(f"Error getting website analysis for user {user_id}: {str(e)}")
            return None
    
    def get_user_research_preferences(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get research preferences for a specific user.
        
        Args:
            user_id: User ID to get data for
            
        Returns:
            Research preferences data or None if not found
        """
        try:
            session = self.db or get_db_session()
            
            # Find onboarding session for user
            onboarding_session = session.query(OnboardingSession).filter(
                OnboardingSession.user_id == user_id
            ).first()
            
            if not onboarding_session:
                logger.warning(f"No onboarding session found for user {user_id}")
                return None
            
            # Get research preferences for this session
            research_prefs = session.query(ResearchPreferences).filter(
                ResearchPreferences.session_id == onboarding_session.id
            ).first()
            
            if not research_prefs:
                logger.warning(f"No research preferences found for user {user_id}")
                return None
            
            return research_prefs.to_dict()
            
        except Exception as e:
            logger.error(f"Error getting research preferences for user {user_id}: {str(e)}")
            return None
    
    def get_personalized_ai_inputs(self, user_id: int) -> Dict[str, Any]:
        """
        Get personalized AI inputs based on user's onboarding data.
        
        Args:
            user_id: User ID to get personalized data for
            
        Returns:
            Personalized data for AI analysis
        """
        try:
            logger.info(f"Getting personalized AI inputs for user {user_id}")
            
            # Get website analysis
            website_analysis = self.get_user_website_analysis(user_id)
            research_prefs = self.get_user_research_preferences(user_id)
            
            if not website_analysis:
                logger.warning(f"No onboarding data found for user {user_id}, using defaults")
                return self._get_default_ai_inputs()
            
            # Extract real data from website analysis
            writing_style = website_analysis.get('writing_style', {})
            target_audience = website_analysis.get('target_audience', {})
            content_type = website_analysis.get('content_type', {})
            recommended_settings = website_analysis.get('recommended_settings', {})
            
            # Build personalized AI inputs
            personalized_inputs = {
                "website_analysis": {
                    "website_url": website_analysis.get('website_url', ''),
                    "content_types": self._extract_content_types(content_type),
                    "writing_style": writing_style.get('tone', 'professional'),
                    "target_audience": target_audience.get('demographics', ['professionals']),
                    "industry_focus": target_audience.get('industry_focus', 'general'),
                    "expertise_level": target_audience.get('expertise_level', 'intermediate')
                },
                "competitor_analysis": {
                    "top_performers": self._generate_competitor_suggestions(target_audience),
                    "industry": target_audience.get('industry_focus', 'general'),
                    "target_demographics": target_audience.get('demographics', [])
                },
                "gap_analysis": {
                    "content_gaps": self._identify_content_gaps(content_type, writing_style),
                    "target_keywords": self._generate_target_keywords(target_audience),
                    "content_opportunities": self._identify_opportunities(content_type)
                },
                "keyword_analysis": {
                    "high_value_keywords": self._generate_high_value_keywords(target_audience),
                    "content_topics": self._generate_content_topics(content_type),
                    "search_intent": self._analyze_search_intent(target_audience)
                }
            }
            
            # Add research preferences if available
            if research_prefs:
                personalized_inputs["research_preferences"] = {
                    "research_depth": research_prefs.get('research_depth', 'Standard'),
                    "content_types": research_prefs.get('content_types', []),
                    "auto_research": research_prefs.get('auto_research', True),
                    "factual_content": research_prefs.get('factual_content', True)
                }
            
            logger.info(f"✅ Generated personalized AI inputs for user {user_id}")
            return personalized_inputs
            
        except Exception as e:
            logger.error(f"Error generating personalized AI inputs for user {user_id}: {str(e)}")
            return self._get_default_ai_inputs()
    
    def _extract_content_types(self, content_type: Dict[str, Any]) -> List[str]:
        """Extract content types from content type analysis."""
        types = []
        if content_type.get('primary_type'):
            types.append(content_type['primary_type'])
        if content_type.get('secondary_types'):
            types.extend(content_type['secondary_types'])
        return types if types else ['blog', 'article']
    
    def _generate_competitor_suggestions(self, target_audience: Dict[str, Any]) -> List[str]:
        """Generate competitor suggestions based on target audience."""
        industry = target_audience.get('industry_focus', 'general')
        demographics = target_audience.get('demographics', ['professionals'])
        
        # Generate industry-specific competitors
        if industry == 'technology':
            return ['techcrunch.com', 'wired.com', 'theverge.com']
        elif industry == 'marketing':
            return ['hubspot.com', 'marketingland.com', 'moz.com']
        else:
            return ['competitor1.com', 'competitor2.com', 'competitor3.com']
    
    def _identify_content_gaps(self, content_type: Dict[str, Any], writing_style: Dict[str, Any]) -> List[str]:
        """Identify content gaps based on current content type and style."""
        gaps = []
        primary_type = content_type.get('primary_type', 'blog')
        
        if primary_type == 'blog':
            gaps.extend(['Video tutorials', 'Case studies', 'Infographics'])
        elif primary_type == 'video':
            gaps.extend(['Blog posts', 'Whitepapers', 'Webinars'])
        
        # Add style-based gaps
        tone = writing_style.get('tone', 'professional')
        if tone == 'professional':
            gaps.append('Personal stories')
        elif tone == 'casual':
            gaps.append('Expert interviews')
        
        return gaps
    
    def _generate_target_keywords(self, target_audience: Dict[str, Any]) -> List[str]:
        """Generate target keywords based on audience analysis."""
        industry = target_audience.get('industry_focus', 'general')
        expertise = target_audience.get('expertise_level', 'intermediate')
        
        if industry == 'technology':
            return ['AI tools', 'Digital transformation', 'Tech trends']
        elif industry == 'marketing':
            return ['Content marketing', 'SEO strategies', 'Social media']
        else:
            return ['Industry insights', 'Best practices', 'Expert tips']
    
    def _identify_opportunities(self, content_type: Dict[str, Any]) -> List[str]:
        """Identify content opportunities based on current content type."""
        opportunities = []
        purpose = content_type.get('purpose', 'informational')
        
        if purpose == 'informational':
            opportunities.extend(['How-to guides', 'Tutorials', 'Educational content'])
        elif purpose == 'promotional':
            opportunities.extend(['Case studies', 'Testimonials', 'Success stories'])
        
        return opportunities
    
    def _generate_high_value_keywords(self, target_audience: Dict[str, Any]) -> List[str]:
        """Generate high-value keywords based on audience analysis."""
        industry = target_audience.get('industry_focus', 'general')
        
        if industry == 'technology':
            return ['AI marketing', 'Content automation', 'Digital strategy']
        elif industry == 'marketing':
            return ['Content marketing', 'SEO optimization', 'Social media strategy']
        else:
            return ['Industry trends', 'Best practices', 'Expert insights']
    
    def _generate_content_topics(self, content_type: Dict[str, Any]) -> List[str]:
        """Generate content topics based on content type analysis."""
        topics = []
        primary_type = content_type.get('primary_type', 'blog')
        
        if primary_type == 'blog':
            topics.extend(['Industry trends', 'How-to guides', 'Expert insights'])
        elif primary_type == 'video':
            topics.extend(['Tutorials', 'Product demos', 'Expert interviews'])
        
        return topics
    
    def _analyze_search_intent(self, target_audience: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze search intent based on target audience."""
        expertise = target_audience.get('expertise_level', 'intermediate')
        
        if expertise == 'beginner':
            return {'intent': 'educational', 'focus': 'basic concepts'}
        elif expertise == 'intermediate':
            return {'intent': 'practical', 'focus': 'implementation'}
        else:
            return {'intent': 'advanced', 'focus': 'strategic insights'}
    
    def _get_default_ai_inputs(self) -> Dict[str, Any]:
        """Get default AI inputs when no onboarding data is available."""
        return {
            "website_analysis": {
                "content_types": ["blog", "video", "social"],
                "writing_style": "professional",
                "target_audience": ["professionals"],
                "industry_focus": "general",
                "expertise_level": "intermediate"
            },
            "competitor_analysis": {
                "top_performers": ["competitor1.com", "competitor2.com"],
                "industry": "general",
                "target_demographics": ["professionals"]
            },
            "gap_analysis": {
                "content_gaps": ["AI content", "Video tutorials", "Case studies"],
                "target_keywords": ["Industry insights", "Best practices"],
                "content_opportunities": ["How-to guides", "Tutorials"]
            },
            "keyword_analysis": {
                "high_value_keywords": ["AI marketing", "Content automation", "Digital strategy"],
                "content_topics": ["Industry trends", "Expert insights"],
                "search_intent": {"intent": "practical", "focus": "implementation"}
            }
        }
