"""
Enhanced Strategy Database Service
Handles database operations for enhanced content strategy models.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

# Import enhanced strategy models
from models.enhanced_strategy_models import EnhancedContentStrategy, EnhancedAIAnalysisResult, OnboardingDataIntegration

class EnhancedStrategyDBService:
    """Database service for enhanced content strategy operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_enhanced_strategy(self, strategy_data: Dict[str, Any]) -> EnhancedContentStrategy:
        """Create a new enhanced content strategy."""
        try:
            logger.info(f"Creating enhanced strategy: {strategy_data.get('name', 'Unknown')}")
            
            # Create the enhanced strategy
            enhanced_strategy = EnhancedContentStrategy(**strategy_data)
            
            # Calculate completion percentage
            enhanced_strategy.calculate_completion_percentage()
            
            # Add to database
            self.db.add(enhanced_strategy)
            self.db.commit()
            self.db.refresh(enhanced_strategy)
            
            logger.info(f"Enhanced strategy created successfully: {enhanced_strategy.id}")
            return enhanced_strategy
            
        except Exception as e:
            logger.error(f"Error creating enhanced strategy: {str(e)}")
            self.db.rollback()
            raise
    
    async def get_enhanced_strategy(self, strategy_id: int) -> Optional[EnhancedContentStrategy]:
        """Get an enhanced content strategy by ID."""
        try:
            strategy = self.db.query(EnhancedContentStrategy).filter(
                EnhancedContentStrategy.id == strategy_id
            ).first()
            
            if strategy:
                strategy.calculate_completion_percentage()
            
            return strategy
            
        except Exception as e:
            logger.error(f"Error getting enhanced strategy: {str(e)}")
            raise
    
    async def get_enhanced_strategies_by_user(self, user_id: str) -> List[EnhancedContentStrategy]:
        """Get all enhanced strategies for a user."""
        try:
            strategies = self.db.query(EnhancedContentStrategy).filter(
                EnhancedContentStrategy.user_id == str(user_id)
            ).order_by(desc(EnhancedContentStrategy.created_at)).all()
            
            # Calculate completion percentage for each strategy
            for strategy in strategies:
                strategy.calculate_completion_percentage()
            
            return strategies
            
        except Exception as e:
            logger.error(f"Error getting enhanced strategies for user: {str(e)}")
            raise
    
    async def update_enhanced_strategy(self, strategy_id: int, update_data: Dict[str, Any]) -> Optional[EnhancedContentStrategy]:
        """Update an enhanced content strategy."""
        try:
            strategy = await self.get_enhanced_strategy(strategy_id)
            
            if not strategy:
                return None
            
            # Update fields
            for field, value in update_data.items():
                if hasattr(strategy, field):
                    setattr(strategy, field, value)
            
            # Update timestamp
            strategy.updated_at = datetime.utcnow()
            
            # Recalculate completion percentage
            strategy.calculate_completion_percentage()
            
            self.db.commit()
            self.db.refresh(strategy)
            
            logger.info(f"Enhanced strategy updated successfully: {strategy_id}")
            return strategy
            
        except Exception as e:
            logger.error(f"Error updating enhanced strategy: {str(e)}")
            self.db.rollback()
            raise
    
    async def delete_enhanced_strategy(self, strategy_id: int) -> bool:
        """Delete an enhanced content strategy."""
        try:
            strategy = await self.get_enhanced_strategy(strategy_id)
            
            if not strategy:
                return False
            
            self.db.delete(strategy)
            self.db.commit()
            
            logger.info(f"Enhanced strategy deleted successfully: {strategy_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting enhanced strategy: {str(e)}")
            self.db.rollback()
            raise
    
    async def get_enhanced_strategies_with_analytics(self, user_id: Optional[str] = None, strategy_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get enhanced strategies with comprehensive analytics and AI analysis."""
        try:
            # Build base query
            query = self.db.query(EnhancedContentStrategy)
            
            if user_id:
                query = query.filter(EnhancedContentStrategy.user_id == str(user_id))
            
            if strategy_id:
                query = query.filter(EnhancedContentStrategy.id == strategy_id)
            
            strategies = query.order_by(desc(EnhancedContentStrategy.created_at)).all()
            
            enhanced_strategies = []
            
            for strategy in strategies:
                # Calculate completion percentage
                strategy.calculate_completion_percentage()
                
                # Get latest AI analysis
                latest_analysis = await self.get_latest_ai_analysis(strategy.id)
                
                # Get onboarding integration
                onboarding_integration = await self.get_onboarding_integration(strategy.id)
                
                # Build comprehensive strategy data
                strategy_data = strategy.to_dict()
                strategy_data.update({
                    'ai_analysis': latest_analysis,
                    'onboarding_integration': onboarding_integration,
                    'completion_percentage': strategy.completion_percentage,
                    'strategic_insights': self._extract_strategic_insights(strategy),
                    'market_positioning': strategy.market_positioning,
                    'strategic_scores': strategy.strategic_scores,
                    'competitive_advantages': strategy.competitive_advantages,
                    'strategic_risks': strategy.strategic_risks,
                    'opportunity_analysis': strategy.opportunity_analysis
                })
                
                enhanced_strategies.append(strategy_data)
            
            return enhanced_strategies
            
        except Exception as e:
            logger.error(f"Error getting enhanced strategies with analytics: {str(e)}")
            raise
    
    async def get_latest_ai_analysis(self, strategy_id: int) -> Optional[Dict[str, Any]]:
        """Get the latest AI analysis for a strategy."""
        try:
            analysis = self.db.query(EnhancedAIAnalysisResult).filter(
                EnhancedAIAnalysisResult.strategy_id == strategy_id
            ).order_by(desc(EnhancedAIAnalysisResult.created_at)).first()
            
            return analysis.to_dict() if analysis else None
            
        except Exception as e:
            logger.error(f"Error getting latest AI analysis: {str(e)}")
            return None
    
    async def get_onboarding_integration(self, strategy_id: int) -> Optional[Dict[str, Any]]:
        """Get onboarding data integration for a strategy."""
        try:
            integration = self.db.query(OnboardingDataIntegration).filter(
                OnboardingDataIntegration.strategy_id == strategy_id
            ).first()
            
            return integration.to_dict() if integration else None
            
        except Exception as e:
            logger.error(f"Error getting onboarding integration: {str(e)}")
            return None
    
    async def create_ai_analysis_result(self, analysis_data: Dict[str, Any]) -> EnhancedAIAnalysisResult:
        """Create a new AI analysis result."""
        try:
            analysis_result = EnhancedAIAnalysisResult(**analysis_data)
            
            self.db.add(analysis_result)
            self.db.commit()
            self.db.refresh(analysis_result)
            
            logger.info(f"AI analysis result created successfully: {analysis_result.id}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error creating AI analysis result: {str(e)}")
            self.db.rollback()
            raise
    
    async def create_onboarding_integration(self, integration_data: Dict[str, Any]) -> OnboardingDataIntegration:
        """Create a new onboarding data integration."""
        try:
            integration = OnboardingDataIntegration(**integration_data)
            
            self.db.add(integration)
            self.db.commit()
            self.db.refresh(integration)
            
            logger.info(f"Onboarding integration created successfully: {integration.id}")
            return integration
            
        except Exception as e:
            logger.error(f"Error creating onboarding integration: {str(e)}")
            self.db.rollback()
            raise
    
    async def get_strategy_completion_stats(self, user_id: int) -> Dict[str, Any]:
        """Get completion statistics for a user's strategies."""
        try:
            strategies = await self.get_enhanced_strategies_by_user(user_id)
            
            if not strategies:
                return {
                    'total_strategies': 0,
                    'average_completion': 0.0,
                    'completion_distribution': {},
                    'recent_strategies': []
                }
            
            # Calculate statistics
            total_strategies = len(strategies)
            average_completion = sum(s.completion_percentage for s in strategies) / total_strategies
            
            # Completion distribution
            completion_distribution = {
                '0-25%': len([s for s in strategies if s.completion_percentage <= 25]),
                '26-50%': len([s for s in strategies if 25 < s.completion_percentage <= 50]),
                '51-75%': len([s for s in strategies if 50 < s.completion_percentage <= 75]),
                '76-100%': len([s for s in strategies if s.completion_percentage > 75])
            }
            
            # Recent strategies (last 5)
            recent_strategies = [
                {
                    'id': s.id,
                    'name': s.name,
                    'completion_percentage': s.completion_percentage,
                    'created_at': s.created_at.isoformat() if s.created_at else None
                }
                for s in strategies[:5]
            ]
            
            return {
                'total_strategies': total_strategies,
                'average_completion': round(average_completion, 2),
                'completion_distribution': completion_distribution,
                'recent_strategies': recent_strategies
            }
            
        except Exception as e:
            logger.error(f"Error getting strategy completion stats: {str(e)}")
            raise
    
    async def get_ai_analysis_history(self, strategy_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get AI analysis history for a strategy."""
        try:
            analyses = self.db.query(EnhancedAIAnalysisResult).filter(
                EnhancedAIAnalysisResult.strategy_id == strategy_id
            ).order_by(desc(EnhancedAIAnalysisResult.created_at)).limit(limit).all()
            
            return [analysis.to_dict() for analysis in analyses]
            
        except Exception as e:
            logger.error(f"Error getting AI analysis history: {str(e)}")
            raise
    
    async def update_strategy_ai_analysis(self, strategy_id: int, ai_analysis_data: Dict[str, Any]) -> bool:
        """Update strategy with new AI analysis data."""
        try:
            strategy = await self.get_enhanced_strategy(strategy_id)
            
            if not strategy:
                return False
            
            # Update AI analysis fields
            strategy.comprehensive_ai_analysis = ai_analysis_data.get('comprehensive_ai_analysis')
            strategy.strategic_scores = ai_analysis_data.get('strategic_scores')
            strategy.market_positioning = ai_analysis_data.get('market_positioning')
            strategy.competitive_advantages = ai_analysis_data.get('competitive_advantages')
            strategy.strategic_risks = ai_analysis_data.get('strategic_risks')
            strategy.opportunity_analysis = ai_analysis_data.get('opportunity_analysis')
            
            strategy.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            logger.info(f"Strategy AI analysis updated successfully: {strategy_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating strategy AI analysis: {str(e)}")
            self.db.rollback()
            raise
    
    def _extract_strategic_insights(self, strategy: EnhancedContentStrategy) -> List[str]:
        """Extract strategic insights from strategy data."""
        insights = []
        
        # Extract insights from business context
        if strategy.business_objectives:
            insights.append(f"Business objectives: {strategy.business_objectives}")
        
        if strategy.target_metrics:
            insights.append(f"Target metrics: {strategy.target_metrics}")
        
        # Extract insights from audience intelligence
        if strategy.content_preferences:
            insights.append(f"Content preferences identified")
        
        if strategy.audience_pain_points:
            insights.append(f"Audience pain points mapped")
        
        # Extract insights from competitive intelligence
        if strategy.top_competitors:
            insights.append(f"Competitor analysis completed")
        
        if strategy.market_gaps:
            insights.append(f"Market gaps identified")
        
        # Extract insights from content strategy
        if strategy.preferred_formats:
            insights.append(f"Content formats selected")
        
        if strategy.content_frequency:
            insights.append(f"Publishing frequency defined")
        
        # Extract insights from performance analytics
        if strategy.traffic_sources:
            insights.append(f"Traffic sources analyzed")
        
        if strategy.conversion_rates:
            insights.append(f"Conversion tracking established")
        
        return insights
    
    async def search_enhanced_strategies(self, user_id: int, search_term: str) -> List[EnhancedContentStrategy]:
        """Search enhanced strategies by name or content."""
        try:
            search_filter = or_(
                EnhancedContentStrategy.name.ilike(f"%{search_term}%"),
                EnhancedContentStrategy.industry.ilike(f"%{search_term}%")
            )
            
            strategies = self.db.query(EnhancedContentStrategy).filter(
                and_(
                    EnhancedContentStrategy.user_id == user_id,
                    search_filter
                )
            ).order_by(desc(EnhancedContentStrategy.created_at)).all()
            
            # Calculate completion percentage for each strategy
            for strategy in strategies:
                strategy.calculate_completion_percentage()
            
            return strategies
            
        except Exception as e:
            logger.error(f"Error searching enhanced strategies: {str(e)}")
            raise
    
    async def get_strategy_export_data(self, strategy_id: int) -> Dict[str, Any]:
        """Get comprehensive export data for a strategy."""
        try:
            strategy = await self.get_enhanced_strategy(strategy_id)
            
            if not strategy:
                return {}
            
            # Get AI analysis history
            ai_history = await self.get_ai_analysis_history(strategy_id)
            
            # Get onboarding integration
            onboarding_integration = await self.get_onboarding_integration(strategy_id)
            
            export_data = {
                'strategy': strategy.to_dict(),
                'ai_analysis_history': ai_history,
                'onboarding_integration': onboarding_integration,
                'export_timestamp': datetime.utcnow().isoformat(),
                'completion_percentage': strategy.completion_percentage,
                'strategic_insights': self._extract_strategic_insights(strategy)
            }
            
            return export_data
            
        except Exception as e:
            logger.error(f"Error getting strategy export data: {str(e)}")
            raise 
