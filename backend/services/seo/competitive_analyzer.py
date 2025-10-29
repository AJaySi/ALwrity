"""
Competitive Analyzer Service

Leverages onboarding step 3 research data and combines it with GSC/Bing
query data to provide competitive insights. Superior to SEMrush/Ahrefs
because it uses actual user data and personalized content strategy.
"""

from typing import Dict, Any, List, Optional, Set, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from loguru import logger

from utils.logger_utils import get_service_logger
from services.onboarding.data_service import OnboardingDataService
from services.calendar_generation_datasource_framework.data_processing.comprehensive_user_data import ComprehensiveUserDataProcessor

logger = get_service_logger("competitive_analyzer")

class CompetitiveAnalyzer:
    """Analyzes competitive landscape using onboarding research data and analytics."""
    
    def __init__(self, db: Session):
        """Initialize the competitive analyzer."""
        self.db = db
        self.user_data_service = OnboardingDataService(db)
        self.comprehensive_processor = ComprehensiveUserDataProcessor(db)
    
    async def get_competitive_insights(self, user_id: str) -> Dict[str, Any]:
        """
        Get comprehensive competitive insights for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary containing competitive insights
        """
        try:
            # Get user's research preferences and competitor data
            research_prefs = self.user_data_service.get_user_research_preferences(user_id)
            competitors = research_prefs.get('competitors', []) if research_prefs else []
            
            if not competitors:
                logger.info(f"No competitors found for user {user_id}")
                return {
                    "competitor_keywords": [],
                    "content_gaps": [],
                    "opportunity_score": 0,
                    "competitors_analyzed": 0,
                    "last_updated": datetime.now().isoformat()
                }
            
            # Get comprehensive user data including competitor analysis
            comprehensive_data = self.comprehensive_processor.get_comprehensive_user_data(user_id)
            competitor_analysis = comprehensive_data.get('competitor_analysis', {})
            
            # Extract competitor keywords and content topics
            competitor_keywords = self._extract_competitor_keywords(competitor_analysis, competitors)
            
            # Get user's current keywords from GSC/Bing (would be passed in real implementation)
            user_keywords = self._get_user_keywords(user_id)
            
            # Find content gaps
            content_gaps = self._find_content_gaps(user_keywords, competitor_keywords)
            
            # Calculate opportunity score
            opportunity_score = self._calculate_opportunity_score(content_gaps, competitor_keywords)
            
            # Generate actionable insights
            insights = self._generate_insights(content_gaps, competitor_keywords, opportunity_score)
            
            return {
                "competitor_keywords": competitor_keywords,
                "content_gaps": content_gaps,
                "opportunity_score": opportunity_score,
                "competitors_analyzed": len(competitors),
                "insights": insights,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting competitive insights for user {user_id}: {e}")
            return {
                "competitor_keywords": [],
                "content_gaps": [],
                "opportunity_score": 0,
                "competitors_analyzed": 0,
                "insights": [],
                "last_updated": datetime.now().isoformat()
            }
    
    def _extract_competitor_keywords(self, competitor_analysis: Dict[str, Any], competitors: List[str]) -> List[Dict[str, Any]]:
        """Extract keywords from competitor analysis."""
        try:
            keywords = []
            
            # Extract from competitor analysis data
            for competitor_url in competitors:
                competitor_data = competitor_analysis.get(competitor_url, {})
                
                # Extract keywords from various sources
                competitor_keywords = competitor_data.get('keywords', [])
                content_topics = competitor_data.get('content_topics', [])
                meta_keywords = competitor_data.get('meta_keywords', [])
                
                # Combine all keyword sources
                all_keywords = set()
                all_keywords.update(competitor_keywords)
                all_keywords.update(content_topics)
                all_keywords.update(meta_keywords)
                
                # Add to keywords list with competitor attribution
                for keyword in all_keywords:
                    if keyword and len(keyword.strip()) > 0:
                        keywords.append({
                            "keyword": keyword.strip(),
                            "competitor": competitor_url,
                            "source": "analysis",
                            "volume_estimate": competitor_data.get('keyword_volume', {}).get(keyword, 0),
                            "difficulty_estimate": competitor_data.get('keyword_difficulty', {}).get(keyword, 0),
                            "relevance_score": self._calculate_relevance_score(keyword, competitor_data)
                        })
            
            # Remove duplicates and sort by relevance
            unique_keywords = self._deduplicate_keywords(keywords)
            sorted_keywords = sorted(unique_keywords, key=lambda x: x['relevance_score'], reverse=True)
            
            logger.debug(f"Extracted {len(sorted_keywords)} unique competitor keywords")
            return sorted_keywords[:100]  # Limit to top 100
            
        except Exception as e:
            logger.error(f"Error extracting competitor keywords: {e}")
            return []
    
    def _get_user_keywords(self, user_id: str) -> Set[str]:
        """Get user's current keywords from GSC/Bing data."""
        try:
            # In a real implementation, this would fetch from GSC/Bing APIs
            # For now, return empty set as placeholder
            # This would be called from the dashboard service with actual query data
            return set()
        except Exception as e:
            logger.error(f"Error getting user keywords: {e}")
            return set()
    
    def _find_content_gaps(self, user_keywords: Set[str], competitor_keywords: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find content gaps between user and competitors."""
        try:
            content_gaps = []
            user_keywords_lower = {kw.lower() for kw in user_keywords}
            
            for comp_keyword in competitor_keywords:
                keyword = comp_keyword['keyword'].lower()
                
                # Check if user doesn't have this keyword
                if keyword not in user_keywords_lower:
                    # Check for partial matches (related keywords)
                    is_related = any(
                        self._are_keywords_related(keyword, user_kw) 
                        for user_kw in user_keywords_lower
                    )
                    
                    if not is_related:
                        content_gaps.append({
                            "keyword": comp_keyword['keyword'],
                            "competitor": comp_keyword['competitor'],
                            "volume_estimate": comp_keyword.get('volume_estimate', 0),
                            "difficulty_estimate": comp_keyword.get('difficulty_estimate', 0),
                            "relevance_score": comp_keyword['relevance_score'],
                            "opportunity_type": self._classify_opportunity_type(comp_keyword),
                            "content_suggestion": self._generate_content_suggestion(comp_keyword)
                        })
            
            # Sort by opportunity score (volume * relevance / difficulty)
            sorted_gaps = sorted(
                content_gaps,
                key=lambda x: (x['volume_estimate'] * x['relevance_score']) / max(x['difficulty_estimate'], 1),
                reverse=True
            )
            
            logger.debug(f"Found {len(sorted_gaps)} content gaps")
            return sorted_gaps[:50]  # Limit to top 50
            
        except Exception as e:
            logger.error(f"Error finding content gaps: {e}")
            return []
    
    def _calculate_opportunity_score(self, content_gaps: List[Dict[str, Any]], competitor_keywords: List[Dict[str, Any]]) -> int:
        """Calculate overall opportunity score (0-100)."""
        try:
            if not content_gaps:
                return 0
            
            # Calculate average opportunity metrics
            avg_volume = sum(gap['volume_estimate'] for gap in content_gaps) / len(content_gaps)
            avg_relevance = sum(gap['relevance_score'] for gap in content_gaps) / len(content_gaps)
            avg_difficulty = sum(gap['difficulty_estimate'] for gap in content_gaps) / len(content_gaps)
            
            # Calculate opportunity score
            # Higher volume and relevance = higher score
            # Lower difficulty = higher score
            volume_score = min(avg_volume / 1000, 1.0) * 40  # Max 40 points for volume
            relevance_score = avg_relevance * 30  # Max 30 points for relevance
            difficulty_score = max(0, (10 - avg_difficulty) / 10) * 30  # Max 30 points for low difficulty
            
            total_score = volume_score + relevance_score + difficulty_score
            opportunity_score = min(int(total_score), 100)
            
            logger.debug(f"Calculated opportunity score: {opportunity_score}")
            return opportunity_score
            
        except Exception as e:
            logger.error(f"Error calculating opportunity score: {e}")
            return 0
    
    def _generate_insights(self, content_gaps: List[Dict[str, Any]], competitor_keywords: List[Dict[str, Any]], opportunity_score: int) -> List[Dict[str, Any]]:
        """Generate actionable insights from competitive analysis."""
        try:
            insights = []
            
            # High opportunity score insight
            if opportunity_score > 70:
                insights.append({
                    "type": "opportunity",
                    "priority": "high",
                    "title": "High Competitive Opportunity",
                    "description": f"Your opportunity score is {opportunity_score}% - competitors are ranking for many keywords you're not targeting.",
                    "action": "Create content for the identified keyword gaps to capture more organic traffic."
                })
            elif opportunity_score > 40:
                insights.append({
                    "type": "opportunity",
                    "priority": "medium",
                    "title": "Moderate Competitive Opportunity",
                    "description": f"Your opportunity score is {opportunity_score}% - there are some keyword gaps you could target.",
                    "action": "Review the content gaps and prioritize high-volume, low-difficulty keywords."
                })
            
            # Content gap insights
            if content_gaps:
                high_volume_gaps = [gap for gap in content_gaps if gap['volume_estimate'] > 500]
                if high_volume_gaps:
                    insights.append({
                        "type": "content",
                        "priority": "high",
                        "title": "High-Volume Content Gaps",
                        "description": f"Found {len(high_volume_gaps)} high-volume keywords that competitors rank for but you don't.",
                        "action": "Create comprehensive content targeting these high-volume keywords."
                    })
                
                low_difficulty_gaps = [gap for gap in content_gaps if gap['difficulty_estimate'] < 3]
                if low_difficulty_gaps:
                    insights.append({
                        "type": "content",
                        "priority": "medium",
                        "title": "Low-Difficulty Content Gaps",
                        "description": f"Found {len(low_difficulty_gaps)} low-difficulty keywords that would be easy to rank for.",
                        "action": "Quick wins: Create content for these low-difficulty keywords first."
                    })
            
            # Competitor analysis insights
            if competitor_keywords:
                top_competitors = {}
                for kw in competitor_keywords:
                    competitor = kw['competitor']
                    if competitor not in top_competitors:
                        top_competitors[competitor] = 0
                    top_competitors[competitor] += 1
                
                top_competitor = max(top_competitors.items(), key=lambda x: x[1]) if top_competitors else None
                if top_competitor:
                    insights.append({
                        "type": "competitive",
                        "priority": "medium",
                        "title": "Top Competitor Analysis",
                        "description": f"{top_competitor[0]} has the most keyword overlap with your content strategy.",
                        "action": f"Analyze {top_competitor[0]}'s content strategy for additional keyword opportunities."
                    })
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return []
    
    def _deduplicate_keywords(self, keywords: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate keywords and merge data."""
        try:
            keyword_map = {}
            
            for kw in keywords:
                keyword = kw['keyword'].lower()
                if keyword in keyword_map:
                    # Merge data from multiple competitors
                    existing = keyword_map[keyword]
                    existing['competitors'].append(kw['competitor'])
                    existing['volume_estimate'] = max(existing['volume_estimate'], kw['volume_estimate'])
                    existing['relevance_score'] = max(existing['relevance_score'], kw['relevance_score'])
                else:
                    keyword_map[keyword] = {
                        'keyword': kw['keyword'],
                        'competitors': [kw['competitor']],
                        'source': kw['source'],
                        'volume_estimate': kw['volume_estimate'],
                        'difficulty_estimate': kw['difficulty_estimate'],
                        'relevance_score': kw['relevance_score']
                    }
            
            return list(keyword_map.values())
            
        except Exception as e:
            logger.error(f"Error deduplicating keywords: {e}")
            return []
    
    def _calculate_relevance_score(self, keyword: str, competitor_data: Dict[str, Any]) -> float:
        """Calculate relevance score for a keyword based on competitor data."""
        try:
            # Base relevance score
            relevance = 0.5
            
            # Increase relevance based on keyword frequency in competitor content
            content_frequency = competitor_data.get('content_frequency', {})
            if keyword in content_frequency:
                relevance += min(content_frequency[keyword] / 10, 0.3)
            
            # Increase relevance based on meta keyword presence
            meta_keywords = competitor_data.get('meta_keywords', [])
            if keyword in meta_keywords:
                relevance += 0.2
            
            # Increase relevance based on title presence
            titles = competitor_data.get('titles', [])
            if any(keyword.lower() in title.lower() for title in titles):
                relevance += 0.2
            
            # Normalize to 0-1 range
            return min(relevance, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating relevance score: {e}")
            return 0.5
    
    def _are_keywords_related(self, keyword1: str, keyword2: str) -> bool:
        """Check if two keywords are related."""
        try:
            # Simple similarity check - can be enhanced with NLP
            words1 = set(keyword1.lower().split())
            words2 = set(keyword2.lower().split())
            
            # Check for word overlap
            overlap = len(words1.intersection(words2))
            total_words = len(words1.union(words2))
            
            if total_words == 0:
                return False
            
            similarity = overlap / total_words
            return similarity > 0.3  # 30% word overlap threshold
            
        except Exception as e:
            logger.error(f"Error checking keyword relatedness: {e}")
            return False
    
    def _classify_opportunity_type(self, keyword_data: Dict[str, Any]) -> str:
        """Classify the type of opportunity for a keyword."""
        try:
            volume = keyword_data.get('volume_estimate', 0)
            difficulty = keyword_data.get('difficulty_estimate', 0)
            relevance = keyword_data.get('relevance_score', 0)
            
            if volume > 1000 and difficulty < 5 and relevance > 0.7:
                return "high_priority"
            elif volume > 500 and difficulty < 7 and relevance > 0.5:
                return "medium_priority"
            elif volume > 100 and difficulty < 8:
                return "low_priority"
            else:
                return "long_term"
                
        except Exception as e:
            logger.error(f"Error classifying opportunity type: {e}")
            return "unknown"
    
    def _generate_content_suggestion(self, keyword_data: Dict[str, Any]) -> str:
        """Generate content suggestion for a keyword."""
        try:
            keyword = keyword_data['keyword']
            opportunity_type = self._classify_opportunity_type(keyword_data)
            
            suggestions = {
                "high_priority": f"Create comprehensive, in-depth content targeting '{keyword}' - high volume, low difficulty opportunity.",
                "medium_priority": f"Consider creating content around '{keyword}' - good volume with moderate competition.",
                "low_priority": f"'{keyword}' could be a good long-tail keyword to target in future content.",
                "long_term": f"'{keyword}' might be worth monitoring for future content opportunities."
            }
            
            return suggestions.get(opportunity_type, f"Consider creating content around '{keyword}'.")
            
        except Exception as e:
            logger.error(f"Error generating content suggestion: {e}")
            return f"Consider creating content around '{keyword_data.get('keyword', 'this keyword')}'."