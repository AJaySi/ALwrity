"""
Step 3 Research Service for Onboarding

This service handles the research phase of onboarding (Step 3), including
competitor discovery using Exa API and research data management.

Key Features:
- Competitor discovery using Exa API
- Research progress tracking
- Data storage and retrieval
- Integration with onboarding workflow

Author: ALwrity Team
Version: 1.0
Last Updated: January 2025
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from loguru import logger
from services.research.exa_service import ExaService
from services.database import get_db_session
from models.onboarding import OnboardingSession
from sqlalchemy.orm import Session

class Step3ResearchService:
    """
    Service for managing Step 3 research phase of onboarding.
    
    This service handles competitor discovery, research data storage,
    and integration with the onboarding workflow.
    """
    
    def __init__(self):
        """Initialize the Step 3 Research Service."""
        self.exa_service = ExaService()
        self.service_name = "step3_research"
        logger.info(f"Initialized {self.service_name}")
    
    async def discover_competitors_for_onboarding(
        self,
        user_url: str,
        session_id: str,
        industry_context: Optional[str] = None,
        num_results: int = 25,
        website_analysis_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Discover competitors for onboarding Step 3.
        
        Args:
            user_url: The user's website URL
            session_id: Onboarding session ID
            industry_context: Industry context for better discovery
            num_results: Number of competitors to discover
            
        Returns:
            Dictionary containing competitor discovery results
        """
        try:
            logger.info(f"Starting research analysis for session {session_id}, URL: {user_url}")
            
            # Step 1: Discover social media accounts
            logger.info("Step 1: Discovering social media accounts...")
            social_media_results = await self.exa_service.discover_social_media_accounts(user_url)
            
            if not social_media_results["success"]:
                logger.warning(f"Social media discovery failed: {social_media_results.get('error')}")
                # Continue with competitor discovery even if social media fails
                social_media_results = {"success": False, "social_media_accounts": {}, "citations": []}
            
            # Step 2: Discover competitors using Exa API
            logger.info("Step 2: Discovering competitors...")
            competitor_results = await self.exa_service.discover_competitors(
                user_url=user_url,
                num_results=num_results,
                exclude_domains=None,  # Let ExaService handle domain exclusion
                industry_context=industry_context,
                website_analysis_data=website_analysis_data
            )
            
            if not competitor_results["success"]:
                logger.error(f"Competitor discovery failed: {competitor_results.get('error')}")
                return competitor_results
            
            # Process and enhance competitor data
            enhanced_competitors = await self._enhance_competitor_data(
                competitor_results["competitors"],
                user_url,
                industry_context
            )
            
            # Store research data in database
            await self._store_research_data(
                session_id=session_id,
                user_url=user_url,
                competitors=enhanced_competitors,
                industry_context=industry_context,
                analysis_metadata={
                    **competitor_results,
                    "social_media_data": social_media_results
                }
            )
            
            # Generate research summary
            research_summary = self._generate_research_summary(
                enhanced_competitors,
                industry_context
            )
            
            logger.info(f"Successfully discovered {len(enhanced_competitors)} competitors for session {session_id}")
            
            return {
                "success": True,
                "session_id": session_id,
                "user_url": user_url,
                "competitors": enhanced_competitors,
                "social_media_accounts": social_media_results.get("social_media_accounts", {}),
                "social_media_citations": social_media_results.get("citations", []),
                "research_summary": research_summary,
                "total_competitors": len(enhanced_competitors),
                "industry_context": industry_context,
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "api_cost": competitor_results.get("api_cost", 0) + social_media_results.get("api_cost", 0)
            }
            
        except Exception as e:
            logger.error(f"Error in competitor discovery for onboarding: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "session_id": session_id,
                "user_url": user_url
            }
    
    async def _enhance_competitor_data(
        self,
        competitors: List[Dict[str, Any]],
        user_url: str,
        industry_context: Optional[str]
    ) -> List[Dict[str, Any]]:
        """
        Enhance competitor data with additional analysis.
        
        Args:
            competitors: Raw competitor data from Exa API
            user_url: User's website URL for comparison
            industry_context: Industry context
            
        Returns:
            List of enhanced competitor data
        """
        enhanced_competitors = []
        
        for competitor in competitors:
            try:
                # Add competitive analysis
                competitive_analysis = self._analyze_competitor_competitiveness(
                    competitor,
                    user_url,
                    industry_context
                )
                
                # Add content strategy insights
                content_insights = self._analyze_content_strategy(competitor)
                
                # Add market positioning
                market_positioning = self._analyze_market_positioning(competitor)
                
                enhanced_competitor = {
                    **competitor,
                    "competitive_analysis": competitive_analysis,
                    "content_insights": content_insights,
                    "market_positioning": market_positioning,
                    "enhanced_timestamp": datetime.utcnow().isoformat()
                }
                
                enhanced_competitors.append(enhanced_competitor)
                
            except Exception as e:
                logger.warning(f"Error enhancing competitor data: {str(e)}")
                enhanced_competitors.append(competitor)
        
        return enhanced_competitors
    
    def _analyze_competitor_competitiveness(
        self,
        competitor: Dict[str, Any],
        user_url: str,
        industry_context: Optional[str]
    ) -> Dict[str, Any]:
        """
        Analyze competitor competitiveness.
        
        Args:
            competitor: Competitor data
            user_url: User's website URL
            industry_context: Industry context
            
        Returns:
            Dictionary of competitive analysis
        """
        analysis = {
            "threat_level": "medium",
            "competitive_strengths": [],
            "competitive_weaknesses": [],
            "market_share_estimate": "unknown",
            "differentiation_opportunities": []
        }
        
        # Analyze threat level based on relevance score
        relevance_score = competitor.get("relevance_score", 0)
        if relevance_score > 0.8:
            analysis["threat_level"] = "high"
        elif relevance_score < 0.4:
            analysis["threat_level"] = "low"
        
        # Analyze competitive strengths from content
        summary = competitor.get("summary", "").lower()
        highlights = competitor.get("highlights", [])
        
        # Extract strengths from content analysis
        if "innovative" in summary or "cutting-edge" in summary:
            analysis["competitive_strengths"].append("Innovation leadership")
        
        if "comprehensive" in summary or "complete" in summary:
            analysis["competitive_strengths"].append("Comprehensive solution")
        
        if any("enterprise" in highlight.lower() for highlight in highlights):
            analysis["competitive_strengths"].append("Enterprise focus")
        
        # Generate differentiation opportunities
        if not any("saas" in summary for summary in [summary]):
            analysis["differentiation_opportunities"].append("SaaS platform differentiation")
        
        return analysis
    
    def _analyze_content_strategy(self, competitor: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze competitor's content strategy.
        
        Args:
            competitor: Competitor data
            
        Returns:
            Dictionary of content strategy analysis
        """
        strategy = {
            "content_focus": "general",
            "target_audience": "unknown",
            "content_types": [],
            "publishing_frequency": "unknown",
            "content_quality": "medium"
        }
        
        summary = competitor.get("summary", "").lower()
        title = competitor.get("title", "").lower()
        
        # Analyze content focus
        if "technical" in summary or "developer" in summary:
            strategy["content_focus"] = "technical"
        elif "business" in summary or "enterprise" in summary:
            strategy["content_focus"] = "business"
        elif "marketing" in summary or "seo" in summary:
            strategy["content_focus"] = "marketing"
        
        # Analyze target audience
        if "startup" in summary or "small business" in summary:
            strategy["target_audience"] = "startups_small_business"
        elif "enterprise" in summary or "large" in summary:
            strategy["target_audience"] = "enterprise"
        elif "developer" in summary or "technical" in summary:
            strategy["target_audience"] = "developers"
        
        # Analyze content quality
        if len(summary) > 300:
            strategy["content_quality"] = "high"
        elif len(summary) < 100:
            strategy["content_quality"] = "low"
        
        return strategy
    
    def _analyze_market_positioning(self, competitor: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze competitor's market positioning.
        
        Args:
            competitor: Competitor data
            
        Returns:
            Dictionary of market positioning analysis
        """
        positioning = {
            "market_tier": "unknown",
            "pricing_position": "unknown",
            "brand_positioning": "unknown",
            "competitive_advantage": "unknown"
        }
        
        summary = competitor.get("summary", "").lower()
        title = competitor.get("title", "").lower()
        
        # Analyze market tier
        if "enterprise" in summary or "enterprise" in title:
            positioning["market_tier"] = "enterprise"
        elif "startup" in summary or "small" in summary:
            positioning["market_tier"] = "startup_small_business"
        elif "premium" in summary or "professional" in summary:
            positioning["market_tier"] = "premium"
        
        # Analyze brand positioning
        if "innovative" in summary or "cutting-edge" in summary:
            positioning["brand_positioning"] = "innovator"
        elif "reliable" in summary or "trusted" in summary:
            positioning["brand_positioning"] = "trusted_leader"
        elif "affordable" in summary or "cost-effective" in summary:
            positioning["brand_positioning"] = "value_leader"
        
        return positioning
    
    def _generate_research_summary(
        self,
        competitors: List[Dict[str, Any]],
        industry_context: Optional[str]
    ) -> Dict[str, Any]:
        """
        Generate a summary of the research findings.
        
        Args:
            competitors: List of enhanced competitor data
            industry_context: Industry context
            
        Returns:
            Dictionary containing research summary
        """
        if not competitors:
            return {
                "total_competitors": 0,
                "market_insights": "No competitors found",
                "key_findings": [],
                "recommendations": []
            }
        
        # Analyze market landscape
        threat_levels = [comp.get("competitive_analysis", {}).get("threat_level", "medium") for comp in competitors]
        high_threat_count = threat_levels.count("high")
        
        # Extract common themes
        content_focuses = [comp.get("content_insights", {}).get("content_focus", "general") for comp in competitors]
        content_focus_distribution = {focus: content_focuses.count(focus) for focus in set(content_focuses)}
        
        # Generate key findings
        key_findings = []
        if high_threat_count > len(competitors) * 0.3:
            key_findings.append("Highly competitive market with multiple strong players")
        
        if "technical" in content_focus_distribution:
            key_findings.append("Technical content is a key differentiator in this market")
        
        # Generate recommendations
        recommendations = []
        if high_threat_count > 0:
            recommendations.append("Focus on unique value proposition to differentiate from strong competitors")
        
        if "technical" in content_focus_distribution and content_focus_distribution["technical"] > 2:
            recommendations.append("Consider developing technical content strategy")
        
        return {
            "total_competitors": len(competitors),
            "high_threat_competitors": high_threat_count,
            "content_focus_distribution": content_focus_distribution,
            "market_insights": f"Found {len(competitors)} competitors in {industry_context or 'the market'}",
            "key_findings": key_findings,
            "recommendations": recommendations,
            "competitive_landscape": "moderate" if high_threat_count < len(competitors) * 0.5 else "high"
        }
    
    async def _store_research_data(
        self,
        session_id: str,
        user_url: str,
        competitors: List[Dict[str, Any]],
        industry_context: Optional[str],
        analysis_metadata: Dict[str, Any]
    ) -> bool:
        """
        Store research data in the database.
        
        Args:
            session_id: Onboarding session ID
            user_url: User's website URL
            competitors: Competitor data
            industry_context: Industry context
            analysis_metadata: Analysis metadata
            
        Returns:
            Boolean indicating success
        """
        try:
            with get_db_session() as db:
                # Get or create onboarding session
                session = db.query(OnboardingSession).filter(
                    OnboardingSession.id == session_id
                ).first()
                
                if not session:
                    logger.error(f"Onboarding session {session_id} not found")
                    return False
                
                # Update session with research data
                research_data = {
                    "step3_research_data": {
                        "user_url": user_url,
                        "competitors": competitors,
                        "industry_context": industry_context,
                        "analysis_metadata": analysis_metadata,
                        "completed_at": datetime.utcnow().isoformat()
                    }
                }
                
                # Merge with existing data
                if session.step_data:
                    session.step_data.update(research_data)
                else:
                    session.step_data = research_data
                
                db.commit()
                logger.info(f"Research data stored for session {session_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error storing research data: {str(e)}")
            return False
    
    async def get_research_data(self, session_id: str) -> Dict[str, Any]:
        """
        Retrieve research data for a session.
        
        Args:
            session_id: Onboarding session ID
            
        Returns:
            Dictionary containing research data
        """
        try:
            with get_db_session() as db:
                session = db.query(OnboardingSession).filter(
                    OnboardingSession.id == session_id
                ).first()
                
                if not session:
                    return {
                        "success": False,
                        "error": "Session not found"
                    }
                
                research_data = session.step_data.get("step3_research_data") if session.step_data else None
                
                if not research_data:
                    return {
                        "success": False,
                        "error": "No research data found for this session"
                    }
                
                return {
                    "success": True,
                    "research_data": research_data,
                    "session_id": session_id
                }
                
        except Exception as e:
            logger.error(f"Error retrieving research data: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _extract_domain(self, url: str) -> str:
        """
        Extract domain from URL.
        
        Args:
            url: Website URL
            
        Returns:
            Domain name
        """
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc
        except Exception:
            return url
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check the health of the Step 3 Research Service.
        
        Returns:
            Dictionary containing service health status
        """
        try:
            exa_health = await self.exa_service.health_check()
            
            return {
                "status": "healthy" if exa_health["status"] == "healthy" else "degraded",
                "service": self.service_name,
                "exa_service_status": exa_health["status"],
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "service": self.service_name,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
