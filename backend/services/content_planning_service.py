"""
Content Planning Service
Handles content strategy development, calendar management, and gap analysis.
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from loguru import logger
from datetime import datetime

from services.database import get_session_for_user
from services.content_planning_db import ContentPlanningDBService
from services.ai_service_manager import AIServiceManager
from models.content_planning import ContentStrategy, CalendarEvent, ContentAnalytics

class ContentPlanningService:
    """Service for managing content planning operations with database integration."""
    
    def __init__(self):
        self.ai_manager = AIServiceManager()
    
    def _get_db_session(self, user_id: int) -> Session:
        """Get database session."""
        return get_session_for_user(str(user_id))
    
    def _get_db_service(self, user_id: int) -> ContentPlanningDBService:
        """Get database service."""
        return ContentPlanningDBService(self._get_db_session(user_id))
    
    async def analyze_content_strategy_with_ai(self, industry: str, target_audience: Dict[str, Any], 
                                             business_goals: List[str], content_preferences: Dict[str, Any],
                                             user_id: int) -> Optional[ContentStrategy]:
        """
        Analyze and create content strategy with AI recommendations and database storage.
        
        Args:
            industry: Target industry
            target_audience: Audience demographics and preferences
            business_goals: List of business objectives
            content_preferences: Content type and platform preferences
            user_id: User ID for database storage
            
        Returns:
            Created content strategy with AI recommendations
        """
        try:
            logger.info(f"Analyzing content strategy with AI for industry: {industry}")
            
            # Generate AI recommendations using AI Service Manager
            ai_analysis_data = {
                'industry': industry,
                'target_audience': target_audience,
                'business_goals': business_goals,
                'content_preferences': content_preferences
            }
            
            # Get AI recommendations
            ai_recommendations = await self.ai_manager.generate_content_gap_analysis(ai_analysis_data)
            
            # Prepare strategy data for database
            strategy_data = {
                'user_id': user_id,
                'name': f"Content Strategy for {industry}",
                'industry': industry,
                'target_audience': target_audience,
                'content_pillars': ai_recommendations.get('content_pillars', []),
                'ai_recommendations': ai_recommendations
            }
            
            # Create strategy in database
            db_service = self._get_db_service(user_id)
            if db_service:
                strategy = await db_service.create_content_strategy(strategy_data)
                
                if strategy:
                    logger.info(f"Content strategy created with AI recommendations: {strategy.id}")
                    
                    # Store AI analytics
                    await self._store_ai_analytics(user_id, strategy.id, ai_recommendations, 'strategy_analysis')
                    
                    return strategy
                else:
                    logger.error("Failed to create content strategy in database")
                    return None
            else:
                logger.error("Database service not available")
                return None
                
        except Exception as e:
            logger.error(f"Error analyzing content strategy with AI: {str(e)}")
            return None
    
    async def create_content_strategy_with_ai(self, user_id: int, strategy_data: Dict[str, Any]) -> Optional[ContentStrategy]:
        """
        Create content strategy with AI recommendations and database storage.
        
        Args:
            user_id: User ID
            strategy_data: Strategy configuration data
            
        Returns:
            Created content strategy or None if failed
        """
        try:
            logger.info(f"Creating content strategy with AI for user: {user_id}")
            
            # Generate AI recommendations
            ai_recommendations = await self._generate_ai_recommendations(strategy_data)
            strategy_data['ai_recommendations'] = ai_recommendations
            
            # Create strategy in database
            db_service = self._get_db_service(user_id)
            if db_service:
                strategy = await db_service.create_content_strategy(strategy_data)
                
                if strategy:
                    logger.info(f"Content strategy created with AI recommendations: {strategy.id}")
                    
                    # Store AI analytics
                    await self._store_ai_analytics(user_id, strategy.id, ai_recommendations, 'strategy_creation')
                    
                    return strategy
                else:
                    logger.error("Failed to create content strategy in database")
                    return None
            else:
                logger.error("Database service not available")
                return None
                
        except Exception as e:
            logger.error(f"Error creating content strategy with AI: {str(e)}")
            return None
    
    async def get_content_strategy(self, user_id: int, strategy_id: Optional[int] = None) -> Optional[ContentStrategy]:
        """
        Get user's content strategy from database.
        
        Args:
            user_id: User ID
            strategy_id: Optional specific strategy ID
            
        Returns:
            Content strategy or None if not found
        """
        try:
            logger.info(f"Getting content strategy for user: {user_id}")
            
            db_service = self._get_db_service(user_id)
            if db_service:
                if strategy_id:
                    strategy = await db_service.get_content_strategy(strategy_id)
                else:
                    strategies = await db_service.get_user_content_strategies(user_id)
                    strategy = strategies[0] if strategies else None
                
                if strategy:
                    logger.info(f"Content strategy retrieved: {strategy.id}")
                    return strategy
                else:
                    logger.info(f"No content strategy found for user: {user_id}")
                    return None
            else:
                logger.error("Database service not available")
                return None
                
        except Exception as e:
            logger.error(f"Error getting content strategy: {str(e)}")
            return None
    
    async def create_calendar_event_with_ai(self, user_id: int, event_data: Dict[str, Any]) -> Optional[CalendarEvent]:
        """
        Create calendar event with AI recommendations and database storage.
        
        Args:
            user_id: User ID
            event_data: Event configuration data
            
        Returns:
            Created calendar event or None if failed
        """
        try:
            logger.info(f"Creating calendar event with AI: {event_data.get('title', 'Untitled')} (user {user_id})")
            
            # Generate AI recommendations for the event
            ai_recommendations = await self._generate_event_ai_recommendations(event_data)
            event_data['ai_recommendations'] = ai_recommendations
            
            # Create event in database
            db_service = self._get_db_service(user_id)
            if db_service:
                event = await db_service.create_calendar_event(event_data)
                
                if event:
                    logger.info(f"Calendar event created with AI recommendations: {event.id}")
                    
                    # Store AI analytics
                    await self._store_ai_analytics(user_id, event.strategy_id, ai_recommendations, 'event_creation', event.id)
                    
                    return event
                else:
                    logger.error("Failed to create calendar event in database")
                    return None
            else:
                logger.error("Database service not available")
                return None
                
        except Exception as e:
            logger.error(f"Error creating calendar event with AI: {str(e)}")
            return None
    
    async def get_calendar_events(self, user_id: int, strategy_id: Optional[int] = None) -> List[CalendarEvent]:
        """
        Get calendar events from database.
        
        Args:
            user_id: User ID
            strategy_id: Optional strategy ID to filter events
            
        Returns:
            List of calendar events
        """
        try:
            logger.info(f"Getting calendar events from database for user {user_id}")
            
            db_service = self._get_db_service(user_id)
            if db_service:
                if strategy_id:
                    events = await db_service.get_strategy_calendar_events(strategy_id)
                else:
                    # TODO: Implement get_all_calendar_events method
                    events = []
                
                logger.info(f"Retrieved {len(events)} calendar events")
                return events
            else:
                logger.error("Database service not available")
                return []
                
        except Exception as e:
            logger.error(f"Error getting calendar events: {str(e)}")
            return []
    
    async def analyze_content_gaps_with_ai(self, website_url: str, competitor_urls: List[str], 
                                         user_id: int, target_keywords: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """
        Analyze content gaps with AI and store results in database.
        
        Args:
            website_url: Target website URL
            competitor_urls: List of competitor URLs
            user_id: User ID for database storage
            target_keywords: Optional target keywords
            
        Returns:
            Content gap analysis results
        """
        try:
            logger.info(f"Analyzing content gaps with AI for: {website_url}")
            
            # Generate AI analysis
            ai_analysis_data = {
                'website_url': website_url,
                'competitor_urls': competitor_urls,
                'target_keywords': target_keywords or []
            }
            
            ai_analysis = await self.ai_manager.generate_content_gap_analysis(ai_analysis_data)
            
            # Store analysis in database
            analysis_data = {
                'user_id': user_id,
                'website_url': website_url,
                'competitor_urls': competitor_urls,
                'target_keywords': target_keywords,
                'analysis_results': ai_analysis.get('analysis_results', {}),
                'recommendations': ai_analysis.get('recommendations', {}),
                'opportunities': ai_analysis.get('opportunities', {})
            }
            
            db_service = self._get_db_service(user_id)
            if db_service:
                analysis = await db_service.create_content_gap_analysis(analysis_data)
                
                if analysis:
                    logger.info(f"Content gap analysis stored in database: {analysis.id}")
                    
                    # Store AI analytics
                    await self._store_ai_analytics(user_id, user_id, ai_analysis, 'gap_analysis')
                    
                    return {
                        'analysis_id': analysis.id,
                        'results': ai_analysis,
                        'stored_at': analysis.created_at.isoformat()
                    }
                else:
                    logger.error("Failed to store content gap analysis in database")
                    return None
            else:
                logger.error("Database service not available")
                return None
                
        except Exception as e:
            logger.error(f"Error analyzing content gaps with AI: {str(e)}")
            return None
    
    async def generate_content_recommendations_with_ai(self, strategy_id: int) -> List[Dict[str, Any]]:
        """
        Generate content recommendations with AI and store in database.
        
        Args:
            strategy_id: Strategy ID
            
        Returns:
            List of content recommendations
        """
        try:
            logger.info(f"Generating content recommendations with AI for strategy: {strategy_id}")
            
            # Get strategy data
            db_service = self._get_db_service()
            if not db_service:
                logger.error("Database service not available")
                return []
            
            strategy = await db_service.get_content_strategy(strategy_id)
            if not strategy:
                logger.error(f"Strategy not found: {strategy_id}")
                return []
            
            # Generate AI recommendations
            recommendation_data = {
                'strategy_id': strategy_id,
                'industry': strategy.industry,
                'target_audience': strategy.target_audience,
                'content_pillars': strategy.content_pillars
            }
            
            ai_recommendations = await self.ai_manager.generate_content_gap_analysis(recommendation_data)
            
            # Store recommendations in database
            for rec in ai_recommendations.get('recommendations', []):
                rec_data = {
                    'user_id': strategy.user_id,
                    'strategy_id': strategy_id,
                    'recommendation_type': rec.get('type', 'content'),
                    'title': rec.get('title', ''),
                    'description': rec.get('description', ''),
                    'priority': rec.get('priority', 'medium'),
                    'estimated_impact': rec.get('estimated_impact', 'medium'),
                    'ai_recommendations': rec
                }
                
                await db_service.create_content_recommendation(rec_data)
            
            # Store AI analytics
            await self._store_ai_analytics(strategy_id, ai_recommendations, 'recommendation_generation')
            
            logger.info(f"Generated and stored {len(ai_recommendations.get('recommendations', []))} recommendations")
            return ai_recommendations.get('recommendations', [])
            
        except Exception as e:
            logger.error(f"Error generating content recommendations with AI: {str(e)}")
            return []
    
    async def track_content_performance_with_ai(self, event_id: int) -> Optional[Dict[str, Any]]:
        """
        Track content performance with AI predictions and store in database.
        
        Args:
            event_id: Calendar event ID
            
        Returns:
            Performance tracking results
        """
        try:
            logger.info(f"Tracking content performance with AI for event: {event_id}")
            
            # Get event data
            db_service = self._get_db_service()
            if not db_service:
                logger.error("Database service not available")
                return None
            
            event = await db_service.get_calendar_event(event_id)
            if not event:
                logger.error(f"Event not found: {event_id}")
                return None
            
            # Generate AI performance prediction
            performance_data = {
                'event_id': event_id,
                'title': event.title,
                'content_type': event.content_type,
                'platform': event.platform,
                'ai_recommendations': event.ai_recommendations
            }
            
            ai_prediction = await self.ai_manager.generate_content_gap_analysis(performance_data)
            
            # Store analytics in database
            analytics_data = {
                'event_id': event_id,
                'strategy_id': event.strategy_id,
                'platform': event.platform,
                'content_type': event.content_type,
                'performance_score': ai_prediction.get('performance_score', 0),
                'engagement_prediction': ai_prediction.get('engagement_prediction', 'medium'),
                'ai_insights': ai_prediction.get('insights', {}),
                'recommendations': ai_prediction.get('optimization_recommendations', [])
            }
            
            analytics = await db_service.create_content_analytics(analytics_data)
            
            if analytics:
                logger.info(f"Performance tracking stored in database: {analytics.id}")
                
                # Store AI analytics
                await self._store_ai_analytics(event.strategy_id, ai_prediction, 'performance_tracking', event_id)
                
                return {
                    'analytics_id': analytics.id,
                    'performance_score': analytics.performance_score,
                    'engagement_prediction': analytics.engagement_prediction,
                    'ai_insights': analytics.ai_insights,
                    'recommendations': analytics.recommendations
                }
            else:
                logger.error("Failed to store performance tracking in database")
                return None
                
        except Exception as e:
            logger.error(f"Error tracking content performance with AI: {str(e)}")
            return None
    
    async def _generate_ai_recommendations(self, strategy_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI recommendations for content strategy."""
        try:
            ai_analysis_data = {
                'industry': strategy_data.get('industry', ''),
                'target_audience': strategy_data.get('target_audience', {}),
                'content_preferences': strategy_data.get('content_preferences', {})
            }
            
            return await self.ai_manager.generate_content_gap_analysis(ai_analysis_data)
            
        except Exception as e:
            logger.error(f"Error generating AI recommendations: {str(e)}")
            return {}
    
    async def _generate_event_ai_recommendations(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI recommendations for calendar event."""
        try:
            ai_analysis_data = {
                'content_type': event_data.get('content_type', ''),
                'platform': event_data.get('platform', ''),
                'title': event_data.get('title', ''),
                'description': event_data.get('description', '')
            }
            
            return await self.ai_manager.generate_content_gap_analysis(ai_analysis_data)
            
        except Exception as e:
            logger.error(f"Error generating event AI recommendations: {str(e)}")
            return {}
    
    async def _store_ai_analytics(self, user_id: int, strategy_id: int, ai_results: Dict[str, Any], 
                                 analysis_type: str, event_id: Optional[int] = None) -> None:
        """Store AI analytics results in database."""
        try:
            db_service = self._get_db_service(user_id)
            if not db_service:
                return
            
            analytics_data = {
                'strategy_id': strategy_id,
                'event_id': event_id,
                'analysis_type': analysis_type,
                'ai_results': ai_results,
                'performance_score': ai_results.get('performance_score', 0),
                'confidence_score': ai_results.get('confidence_score', 0.5),
                'recommendations': ai_results.get('recommendations', [])
            }
            
            await db_service.create_content_analytics(analytics_data)
            logger.info(f"AI analytics stored for {analysis_type}")
            
        except Exception as e:
            logger.error(f"Error storing AI analytics: {str(e)}")
    
    def __del__(self):
        """Cleanup database session."""
        # No explicit session cleanup needed as sessions are managed per request
        pass 