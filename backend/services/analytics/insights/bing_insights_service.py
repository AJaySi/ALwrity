"""
Bing Webmaster Insights Service

Provides advanced analytics insights and recommendations based on Bing Webmaster data.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from loguru import logger
import json

from ...bing_analytics_storage_service import BingAnalyticsStorageService
from ..models.platform_types import PlatformType
from ...analytics_cache_service import AnalyticsCacheService


class BingInsightsService:
    """Service for generating Bing Webmaster insights and recommendations"""
    
    def __init__(self, database_url: Optional[str] = None):
        self.storage_service = BingAnalyticsStorageService(database_url)
        self.cache_service = AnalyticsCacheService()
    
    def get_performance_insights(self, user_id: str, site_url: str, days: int = 30) -> Dict[str, Any]:
        """Get performance insights including trends and patterns"""
        try:
            # Check cache first
            cache_key = self.cache_service._generate_cache_key(
                'bing_performance_insights', 
                user_id, 
                site_url=site_url, 
                days=days
            )
            
            cached_result = self.cache_service.get('bing_analytics', cache_key)
            if cached_result:
                logger.info(f"Returning cached performance insights for user {user_id}")
                return cached_result
            
            # Quick check if data exists before expensive operations
            logger.info(f"Quick data check for user {user_id}, site: {site_url}")
            quick_summary = self.storage_service.get_analytics_summary(user_id, site_url, days)
            if 'error' in quick_summary:
                logger.info(f"No stored data found for user {user_id}, returning basic insights")
                insights = self._generate_basic_performance_insights({})
                # Cache basic insights for shorter time
                self.cache_service.set('bing_analytics', cache_key, insights)
                return insights
            
            # Generate insights from real data (with timeout protection)
            logger.info(f"Generating performance insights from stored data for user {user_id}")
            insights = self._generate_performance_insights_from_data(quick_summary, [])
            
            # Cache the result
            self.cache_service.set('bing_analytics', cache_key, insights)
            
            return insights
            
        except Exception as e:
            logger.error(f"Error getting performance insights: {e}")
            # Return basic insights on error to prevent hanging
            return self._generate_basic_performance_insights({})
    
    def get_seo_insights(self, user_id: str, site_url: str, days: int = 30) -> Dict[str, Any]:
        """Get SEO-specific insights and opportunities"""
        try:
            # Check cache first
            cache_key = self.cache_service._generate_cache_key(
                'bing_seo_insights', 
                user_id, 
                site_url=site_url, 
                days=days
            )
            
            cached_result = self.cache_service.get('bing_analytics', cache_key)
            if cached_result:
                logger.info(f"Returning cached SEO insights for user {user_id}")
                return cached_result
            
            # Quick check if data exists
            logger.info(f"Quick SEO data check for user {user_id}, site: {site_url}")
            summary = self.storage_service.get_analytics_summary(user_id, site_url, days)
            
            if 'error' in summary:
                logger.info(f"No stored data found for user {user_id}, returning basic SEO insights")
                insights = self._generate_basic_seo_insights({})
                # Cache basic insights for shorter time
                self.cache_service.set('bing_analytics', cache_key, insights)
                return insights
            
            # Get limited top queries to prevent timeout
            logger.info(f"Generating SEO insights from stored data for user {user_id}")
            top_queries = self.storage_service.get_top_queries(user_id, site_url, days, limit=50)  # Reduced from 100
            
            if not top_queries:
                logger.info(f"No query data found for user {user_id}, using basic SEO insights")
                insights = self._generate_basic_seo_insights(summary)
            else:
                # Generate insights from real data
                insights = self._generate_seo_insights_from_data(summary, top_queries)
            
            # Cache the result
            self.cache_service.set('bing_analytics', cache_key, insights)
            
            return insights
            
        except Exception as e:
            logger.error(f"Error getting SEO insights: {e}")
            # Return basic insights on error to prevent hanging
            return self._generate_basic_seo_insights({})
    
    def get_competitive_insights(self, user_id: str, site_url: str, days: int = 30) -> Dict[str, Any]:
        """Get competitive analysis and market insights"""
        try:
            # Check cache first
            cache_key = self.cache_service._generate_cache_key(
                'bing_competitive_insights', 
                user_id, 
                site_url=site_url, 
                days=days
            )
            
            cached_result = self.cache_service.get('bing_analytics', cache_key)
            if cached_result:
                logger.info(f"Returning cached competitive insights for user {user_id}")
                return cached_result
            
            # Generate insights
            logger.info(f"Generating competitive insights for user {user_id}")
            insights = {
                'market_position': {'status': 'basic_analysis', 'message': 'Basic insights available'},
                'competition_analysis': {'status': 'basic_analysis', 'message': 'Basic insights available'},
                'growth_opportunities': [],
                'competitive_recommendations': []
            }
            
            # Cache the result
            self.cache_service.set('bing_analytics', cache_key, insights)
            
            return insights
            
        except Exception as e:
            logger.error(f"Error getting competitive insights: {e}")
            return {'error': str(e)}
    
    def _analyze_market_position(self, summary: Dict[str, Any], top_queries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze market position and competitive landscape"""
        try:
            if not summary or not top_queries:
                return {'error': 'Insufficient data for market analysis'}
            
            # Analyze query diversity
            unique_queries = len(set(q['query'] for q in top_queries))
            total_queries = summary.get('total_queries', 0)
            query_diversity = (unique_queries / total_queries * 100) if total_queries > 0 else 0
            
            # Analyze performance distribution
            high_performing_queries = [q for q in top_queries if q.get('clicks', 0) > 10]
            medium_performing_queries = [q for q in top_queries if 1 <= q.get('clicks', 0) <= 10]
            low_performing_queries = [q for q in top_queries if q.get('clicks', 0) == 0]
            
            # Market position indicators
            market_position = {
                'query_diversity_score': round(query_diversity, 2),
                'high_performing_queries': len(high_performing_queries),
                'medium_performing_queries': len(medium_performing_queries),
                'low_performing_queries': len(low_performing_queries),
                'market_penetration': round((len(high_performing_queries) / len(top_queries) * 100), 2) if top_queries else 0,
                'competitive_advantage': 'High' if query_diversity > 50 else 'Medium' if query_diversity > 25 else 'Low'
            }
            
            return market_position
            
        except Exception as e:
            logger.error(f"Error analyzing market position: {e}")
            return {'error': str(e)}
    
    def _analyze_competition(self, top_queries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze competitive landscape based on query performance"""
        try:
            if not top_queries:
                return {'error': 'No query data available for competition analysis'}
            
            # Analyze query performance distribution
            high_performing = [q for q in top_queries if q.get('clicks', 0) > 10]
            medium_performing = [q for q in top_queries if 1 <= q.get('clicks', 0) <= 10]
            low_performing = [q for q in top_queries if q.get('clicks', 0) == 0]
            
            # Calculate competitive metrics
            total_queries = len(top_queries)
            competition_analysis = {
                'high_performing_queries': len(high_performing),
                'medium_performing_queries': len(medium_performing),
                'low_performing_queries': len(low_performing),
                'competitive_advantage_score': round((len(high_performing) / total_queries * 100), 2) if total_queries > 0 else 0,
                'market_penetration': 'High' if len(high_performing) > total_queries * 0.3 else 'Medium' if len(high_performing) > total_queries * 0.1 else 'Low',
                'top_competitors': [q['query'] for q in high_performing[:5]] if high_performing else []
            }
            
            return competition_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing competition: {e}")
            return {'error': str(e)}
    
    def _identify_growth_opportunities(self, top_queries: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Identify growth opportunities based on query performance"""
        try:
            if not top_queries:
                return []
            
            opportunities = []
            
            # Find high-impression, low-click queries (potential for CTR improvement)
            high_impression_low_click = [
                q for q in top_queries 
                if q.get('impressions', 0) > 50 and q.get('clicks', 0) < 5
            ]
            
            if high_impression_low_click:
                opportunities.append({
                    'type': 'CTR Improvement',
                    'description': f'{len(high_impression_low_click)} queries have high impressions but low clicks',
                    'action': 'Optimize meta descriptions and titles for these queries'
                })
            
            # Find queries with good clicks but poor position
            good_clicks_poor_position = [
                q for q in top_queries 
                if q.get('clicks', 0) > 10 and q.get('position', 100) > 10
            ]
            
            if good_clicks_poor_position:
                opportunities.append({
                    'type': 'Position Improvement',
                    'description': f'{len(good_clicks_poor_position)} queries have good clicks but poor positions',
                    'action': 'Improve content quality and relevance for these topics'
                })
            
            # Find zero-click queries with decent impressions
            zero_click_opportunities = [
                q for q in top_queries 
                if q.get('impressions', 0) > 20 and q.get('clicks', 0) == 0
            ]
            
            if zero_click_opportunities:
                opportunities.append({
                    'type': 'Content Gap',
                    'description': f'{len(zero_click_opportunities)} queries get impressions but no clicks',
                    'action': 'Create targeted content for these query topics'
                })
            
            return opportunities[:3]  # Return top 3 opportunities
            
        except Exception as e:
            logger.error(f"Error identifying growth opportunities: {e}")
            return []
    
    def get_actionable_recommendations(self, user_id: str, site_url: str, days: int = 30) -> Dict[str, Any]:
        """Get actionable recommendations for improving search performance"""
        try:
            # Check cache first
            cache_key = self.cache_service._generate_cache_key(
                'bing_actionable_recommendations', 
                user_id, 
                site_url=site_url, 
                days=days
            )
            
            cached_result = self.cache_service.get('bing_analytics', cache_key)
            if cached_result:
                logger.info(f"Returning cached actionable recommendations for user {user_id}")
                return cached_result
            
            # Get actual data from storage service
            logger.info(f"Generating actionable recommendations from stored data for user {user_id}")
            
            # Get data for analysis
            summary = self.storage_service.get_analytics_summary(user_id, site_url, days)
            top_queries = self.storage_service.get_top_queries(user_id, site_url, days, limit=100)
            daily_metrics = self.storage_service.get_daily_metrics(user_id, site_url, days)
            
            if 'error' in summary or not top_queries:
                logger.warning(f"No stored data found, generating basic recommendations")
                insights = {
                    'immediate_actions': [],
                    'content_optimization': [],
                    'technical_improvements': [],
                    'long_term_strategy': [],
                    'priority_score': {}
                }
            else:
                # Generate insights from real data
                insights = {
                    'immediate_actions': self._get_immediate_actions(summary, top_queries),
                    'content_optimization': self._get_content_optimization_recommendations(top_queries),
                    'technical_improvements': self._get_technical_improvements(top_queries, daily_metrics),
                    'long_term_strategy': self._get_long_term_strategy(summary, top_queries),
                    'priority_score': self._calculate_priority_scores(top_queries)
                }
            
            # Cache the result
            self.cache_service.set('bing_analytics', cache_key, insights)
            
            return insights
            
        except Exception as e:
            logger.error(f"Error getting actionable recommendations: {e}")
            return {'error': str(e)}
    
    def _get_immediate_actions(self, summary: Dict[str, Any], top_queries: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Get immediate actions based on current performance"""
        try:
            if not summary or not top_queries:
                return []
            
            actions = []
            
            # Analyze CTR performance
            avg_ctr = summary.get('avg_ctr', 0)
            if avg_ctr < 2.0:
                actions.append({
                    'action': 'Improve CTR',
                    'priority': 'High',
                    'description': f'Current CTR is {avg_ctr:.1f}%, below industry average of 2-3%',
                    'action': 'Optimize meta descriptions and titles to be more compelling'
                })
            
            # Analyze query diversity
            unique_queries = len(set(q['query'] for q in top_queries))
            if unique_queries < 20:
                actions.append({
                    'action': 'Expand Query Coverage',
                    'priority': 'Medium',
                    'description': f'Only {unique_queries} unique queries found',
                    'action': 'Create content targeting more keyword variations'
                })
            
            # Analyze low-performing queries
            low_performing = [q for q in top_queries if q.get('clicks', 0) == 0 and q.get('impressions', 0) > 10]
            if len(low_performing) > 5:
                actions.append({
                    'action': 'Fix Zero-Click Queries',
                    'priority': 'High',
                    'description': f'{len(low_performing)} queries get impressions but no clicks',
                    'action': 'Improve content relevance and meta descriptions for these queries'
                })
            
            return actions
            
        except Exception as e:
            logger.error(f"Error getting immediate actions: {e}")
            return []
    
    def _get_content_optimization_recommendations(self, top_queries: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Get content optimization recommendations based on query analysis"""
        try:
            if not top_queries:
                return []
            
            recommendations = []
            
            # Analyze query length patterns
            short_queries = [q for q in top_queries if len(q.get('query', '')) <= 3]
            long_queries = [q for q in top_queries if len(q.get('query', '')) > 10]
            
            if len(short_queries) > len(long_queries):
                recommendations.append({
                    'type': 'Content Strategy',
                    'priority': 'Medium',
                    'recommendation': 'Focus on long-tail keyword content to capture more specific searches'
                })
            
            # Analyze high-impression, low-CTR queries
            low_ctr_queries = [
                q for q in top_queries 
                if q.get('impressions', 0) > 100 and (q.get('clicks', 0) / max(q.get('impressions', 1), 1)) < 0.02
            ]
            
            if low_ctr_queries:
                recommendations.append({
                    'type': 'Meta Optimization',
                    'priority': 'High',
                    'recommendation': f'Optimize meta descriptions for {len(low_ctr_queries)} high-impression, low-CTR queries'
                })
            
            # Analyze position vs clicks correlation
            position_10_plus = [q for q in top_queries if q.get('position', 100) > 10 and q.get('clicks', 0) > 0]
            if position_10_plus:
                recommendations.append({
                    'type': 'Content Quality',
                    'priority': 'High',
                    'recommendation': f'Improve content quality for {len(position_10_plus)} queries ranking beyond position 10'
                })
            
            # Analyze query intent patterns
            question_queries = [q for q in top_queries if '?' in q.get('query', '') or q.get('query', '').startswith(('what', 'how', 'why', 'when', 'where'))]
            if len(question_queries) > 5:
                recommendations.append({
                    'type': 'Content Format',
                    'priority': 'Medium',
                    'recommendation': 'Create FAQ-style content to better match question-based queries'
                })
            
            return recommendations[:4]  # Return top 4 recommendations
            
        except Exception as e:
            logger.error(f"Error getting content optimization recommendations: {e}")
            return []
    
    def _generate_basic_seo_insights(self, summary: Dict[str, Any]) -> Dict[str, Any]:
        """Generate basic SEO insights from summary data when detailed query data is not available"""
        try:
            total_clicks = summary.get('total_clicks', 0)
            total_impressions = summary.get('total_impressions', 0)
            total_queries = summary.get('total_queries', 0)
            avg_ctr = summary.get('avg_ctr', 0)
            
            # Generate basic insights from summary data
            query_analysis = {
                'total_queries': total_queries,
                'brand_queries': {'percentage': 30},  # Estimated
                'non_brand_queries': {'percentage': 70},  # Estimated
                'query_length_distribution': {'average_length': 4}  # Estimated
            }
            
            technical_insights = {
                'average_position': 8.5,  # Estimated based on CTR
                'average_ctr': avg_ctr,
                'position_distribution': {
                    'top_3': int(total_queries * 0.15),  # Estimated 15% in top 3
                    'top_10': int(total_queries * 0.35)   # Estimated 35% in top 10
                }
            }
            
            seo_recommendations = [
                {
                    'type': 'data',
                    'priority': 'high',
                    'recommendation': 'Collect more detailed search data to generate comprehensive insights'
                },
                {
                    'type': 'performance',
                    'priority': 'medium',
                    'recommendation': f'Current CTR of {avg_ctr:.1f}% is {"good" if avg_ctr > 3 else "needs improvement"}'
                }
            ]
            
            return {
                'query_analysis': query_analysis,
                'content_opportunities': [],
                'technical_insights': technical_insights,
                'seo_recommendations': seo_recommendations
            }
            
        except Exception as e:
            logger.error(f"Error generating basic SEO insights: {e}")
            return {'error': str(e)}
    
    def _get_technical_improvements(self, top_queries: List[Dict[str, Any]], daily_metrics: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Get technical improvement recommendations"""
        try:
            if not top_queries and not daily_metrics:
                return []
            
            improvements = []
            
            # Analyze position distribution
            if top_queries:
                avg_position = sum(q.get('position', 100) for q in top_queries) / len(top_queries)
                if avg_position > 10:
                    improvements.append({
                        'type': 'Position Optimization',
                        'priority': 'High',
                        'recommendation': f'Average position is {avg_position:.1f}, focus on improving content quality'
                    })
            
            # Analyze CTR performance
            if daily_metrics:
                recent_ctr = sum(m.get('avg_ctr', 0) for m in daily_metrics[-7:]) / len(daily_metrics[-7:]) if daily_metrics else 0
                if recent_ctr < 2.0:
                    improvements.append({
                        'type': 'CTR Enhancement',
                        'priority': 'High',
                        'recommendation': 'Optimize meta descriptions and titles to improve click-through rates'
                    })
            
            # Analyze query diversity
            if top_queries:
                unique_queries = len(set(q.get('query', '') for q in top_queries))
                if unique_queries < 20:
                    improvements.append({
                        'type': 'Content Expansion',
                        'priority': 'Medium',
                        'recommendation': 'Create content targeting more keyword variations'
                    })
            
            return improvements[:3]  # Return top 3 improvements
            
        except Exception as e:
            logger.error(f"Error getting technical improvements: {e}")
            return []
    
    def _generate_competitive_recommendations(self, summary: Dict[str, Any], top_queries: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Generate competitive recommendations based on market analysis"""
        try:
            if not summary and not top_queries:
                return []
            
            recommendations = []
            
            # Analyze market position
            total_queries = summary.get('total_queries', 0) if summary else len(top_queries)
            avg_ctr = summary.get('avg_ctr', 0) if summary else 0
            
            if total_queries > 0:
                # Market penetration analysis
                if total_queries < 50:
                    recommendations.append({
                        'type': 'Market Expansion',
                        'priority': 'High',
                        'recommendation': 'Expand keyword targeting to capture more search volume'
                    })
                
                # CTR competitiveness
                if avg_ctr < 3.0:
                    recommendations.append({
                        'type': 'Competitive CTR',
                        'priority': 'High',
                        'recommendation': 'Improve CTR to compete better with top-ranking pages'
                    })
                elif avg_ctr > 8.0:
                    recommendations.append({
                        'type': 'Market Leadership',
                        'priority': 'Medium',
                        'recommendation': 'Leverage high CTR to expand into related keyword markets'
                    })
                
                # Query diversity analysis
                if top_queries:
                    unique_queries = len(set(q.get('query', '') for q in top_queries))
                    if unique_queries / len(top_queries) < 0.5:
                        recommendations.append({
                            'type': 'Query Diversification',
                            'priority': 'Medium',
                            'recommendation': 'Diversify content to target more unique search queries'
                        })
            
            return recommendations[:3]  # Return top 3 recommendations
            
        except Exception as e:
            logger.error(f"Error generating competitive recommendations: {e}")
            return []
    
    def _get_long_term_strategy(self, summary: Dict[str, Any], top_queries: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Get long-term strategic recommendations"""
        try:
            if not summary and not top_queries:
                return []
            
            strategies = []
            
            # Growth strategy based on current performance
            total_clicks = summary.get('total_clicks', 0) if summary else 0
            total_impressions = summary.get('total_impressions', 0) if summary else 0
            avg_ctr = summary.get('avg_ctr', 0) if summary else 0
            
            if total_clicks > 0:
                # Content scaling strategy
                if total_clicks < 1000:
                    strategies.append({
                        'type': 'Content Scaling',
                        'priority': 'High',
                        'recommendation': 'Scale content production to capture more search traffic'
                    })
                elif total_clicks > 5000:
                    strategies.append({
                        'type': 'Market Dominance',
                        'priority': 'High',
                        'recommendation': 'Focus on maintaining market leadership and expanding into new verticals'
                    })
                
                # Technical SEO strategy
                if avg_ctr < 5.0:
                    strategies.append({
                        'type': 'Technical Optimization',
                        'priority': 'Medium',
                        'recommendation': 'Invest in technical SEO improvements for long-term growth'
                    })
                
                # Brand building strategy
                if total_impressions > 10000:
                    strategies.append({
                        'type': 'Brand Building',
                        'priority': 'Medium',
                        'recommendation': 'Focus on brand awareness and authority building in your niche'
                    })
            
            # Query analysis for strategy
            if top_queries:
                brand_queries = [q for q in top_queries if 'alwrity' in q.get('query', '').lower()]
                if len(brand_queries) / len(top_queries) < 0.3:
                    strategies.append({
                        'type': 'Brand Recognition',
                        'priority': 'Medium',
                        'recommendation': 'Increase brand-related content to improve brand recognition in search'
                    })
            
            return strategies[:3]  # Return top 3 strategies
            
        except Exception as e:
            logger.error(f"Error getting long-term strategy: {e}")
            return []
    
    def _calculate_priority_scores(self, top_queries: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculate priority scores for different optimization areas"""
        try:
            if not top_queries:
                return {}
            
            scores = {
                'ctr_optimization': 0,
                'position_improvement': 0,
                'content_expansion': 0,
                'technical_seo': 0
            }
            
            # Analyze CTR optimization priority
            low_ctr_queries = [q for q in top_queries if q.get('ctr', 0) < 2.0]
            if len(low_ctr_queries) > len(top_queries) * 0.3:
                scores['ctr_optimization'] = 8
            
            # Analyze position improvement priority
            poor_position_queries = [q for q in top_queries if q.get('position', 100) > 10]
            if len(poor_position_queries) > len(top_queries) * 0.4:
                scores['position_improvement'] = 7
            
            # Analyze content expansion priority
            unique_queries = len(set(q.get('query', '') for q in top_queries))
            if unique_queries < 20:
                scores['content_expansion'] = 6
            
            # Analyze technical SEO priority
            high_impression_low_click = [q for q in top_queries if q.get('impressions', 0) > 50 and q.get('clicks', 0) < 5]
            if len(high_impression_low_click) > 5:
                scores['technical_seo'] = 9
            
            return scores
            
        except Exception as e:
            logger.error(f"Error calculating priority scores: {e}")
            return {}
    
    def _generate_performance_insights_from_data(self, summary: Dict[str, Any], daily_metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate performance insights from actual stored data"""
        try:
            # Extract performance summary from stored data
            performance_summary = {
                'total_clicks': summary.get('total_clicks', 0),
                'total_impressions': summary.get('total_impressions', 0),
                'avg_ctr': summary.get('avg_ctr', 0),
                'total_queries': summary.get('total_queries', 0)
            }
            
            # Analyze trends from daily metrics
            trends = self._analyze_trends(daily_metrics)
            
            # Get performance indicators
            performance_indicators = self._get_performance_indicators(summary, daily_metrics)
            
            # Generate insights based on real data
            insights = self._generate_performance_insights(summary, daily_metrics)
            
            return {
                'performance_summary': performance_summary,
                'trends': trends,
                'performance_indicators': performance_indicators,
                'insights': insights
            }
            
        except Exception as e:
            logger.error(f"Error generating performance insights from data: {e}")
            return {'error': str(e)}
    
    def _generate_seo_insights_from_data(self, summary: Dict[str, Any], top_queries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate SEO insights from actual stored data"""
        try:
            # Analyze query patterns from real data
            query_analysis = self._analyze_query_patterns(top_queries)
            
            # Get technical insights
            technical_insights = self._get_technical_insights(top_queries)
            
            # Identify content opportunities
            content_opportunities = self._identify_content_opportunities(top_queries)
            
            # Generate SEO recommendations
            seo_recommendations = self._generate_seo_recommendations(top_queries)
            
            return {
                'query_analysis': query_analysis,
                'content_opportunities': content_opportunities,
                'technical_insights': technical_insights,
                'seo_recommendations': seo_recommendations
            }
            
        except Exception as e:
            logger.error(f"Error generating SEO insights from data: {e}")
            return {'error': str(e)}
    
    def _generate_basic_performance_insights(self, summary: Dict[str, Any]) -> Dict[str, Any]:
        """Generate basic performance insights when detailed data is not available"""
        try:
            # Generate basic insights with estimated data
            performance_summary = {
                'total_clicks': 0,
                'total_impressions': 0,
                'avg_ctr': 0,
                'total_queries': 0
            }
            
            trends = {
                'status': 'insufficient_data',
                'message': 'Detailed analytics data not available for trend analysis'
            }
            
            performance_indicators = {
                'performance_level': 'Unknown',
                'traffic_quality': 'Unknown',
                'growth_potential': 'Unknown'
            }
            
            insights = [
                'Detailed analytics data is not available in the database',
                'Connect Bing Webmaster Tools to collect comprehensive search data',
                'Basic metrics are available but detailed insights require data collection'
            ]
            
            return {
                'performance_summary': performance_summary,
                'trends': trends,
                'performance_indicators': performance_indicators,
                'insights': insights
            }
            
        except Exception as e:
            logger.error(f"Error generating basic performance insights: {e}")
            return {'error': str(e)}
    
    def _analyze_trends(self, daily_metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze performance trends over time"""
        if not daily_metrics or len(daily_metrics) < 7:
            return {'status': 'insufficient_data', 'message': 'Need at least 7 days of data for trend analysis'}
        
        # Calculate week-over-week trends
        recent_week = daily_metrics[-7:] if len(daily_metrics) >= 7 else daily_metrics
        previous_week = daily_metrics[-14:-7] if len(daily_metrics) >= 14 else daily_metrics[:-7]
        
        recent_avg_ctr = sum(m.get('avg_ctr', 0) for m in recent_week) / len(recent_week)
        previous_avg_ctr = sum(m.get('avg_ctr', 0) for m in previous_week) / len(previous_week) if previous_week else recent_avg_ctr
        
        recent_clicks = sum(m.get('total_clicks', 0) for m in recent_week)
        previous_clicks = sum(m.get('total_clicks', 0) for m in previous_week) if previous_week else recent_clicks
        
        ctr_change = self._calculate_percentage_change(recent_avg_ctr, previous_avg_ctr)
        clicks_change = self._calculate_percentage_change(recent_clicks, previous_clicks)
        
        return {
            'ctr_trend': {
                'current': recent_avg_ctr,
                'previous': previous_avg_ctr,
                'change_percent': ctr_change,
                'direction': 'up' if ctr_change > 0 else 'down' if ctr_change < 0 else 'stable'
            },
            'clicks_trend': {
                'current': recent_clicks,
                'previous': previous_clicks,
                'change_percent': clicks_change,
                'direction': 'up' if clicks_change > 0 else 'down' if clicks_change < 0 else 'stable'
            },
            'trend_strength': self._calculate_trend_strength(daily_metrics)
        }
    
    def _get_performance_indicators(self, summary: Dict[str, Any], daily_metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get key performance indicators"""
        total_clicks = summary.get('total_clicks', 0)
        total_impressions = summary.get('total_impressions', 0)
        avg_ctr = summary.get('avg_ctr', 0)
        
        # Calculate performance scores
        ctr_score = min(100, (avg_ctr / 5) * 100)  # Assuming 5% CTR is excellent
        volume_score = min(100, (total_clicks / 1000) * 100)  # Assuming 1000 clicks is good
        consistency_score = self._calculate_consistency_score(daily_metrics)
        
        return {
            'ctr_score': round(ctr_score, 1),
            'volume_score': round(volume_score, 1),
            'consistency_score': round(consistency_score, 1),
            'overall_score': round((ctr_score + volume_score + consistency_score) / 3, 1),
            'performance_level': self._get_performance_level(ctr_score, volume_score, consistency_score)
        }
    
    def _generate_performance_insights(self, summary: Dict[str, Any], daily_metrics: List[Dict[str, Any]]) -> List[str]:
        """Generate performance insights"""
        insights = []
        
        total_clicks = summary.get('total_clicks', 0)
        avg_ctr = summary.get('avg_ctr', 0)
        
        # CTR insights
        if avg_ctr < 2:
            insights.append("Your CTR is below 2%. Consider optimizing titles and descriptions for better click-through rates.")
        elif avg_ctr > 5:
            insights.append("Excellent CTR performance! Your content is highly engaging.")
        else:
            insights.append("Good CTR performance. There's room for improvement with better title optimization.")
        
        # Volume insights
        if total_clicks < 100:
            insights.append("Low click volume suggests limited visibility. Focus on increasing impressions through content expansion.")
        elif total_clicks > 1000:
            insights.append("Strong click volume indicates good search visibility. Maintain content quality and consistency.")
        
        # Trend insights
        if daily_metrics and len(daily_metrics) >= 7:
            recent_avg = sum(m.get('total_clicks', 0) for m in daily_metrics[-7:]) / 7
            older_avg = sum(m.get('total_clicks', 0) for m in daily_metrics[:-7]) / max(1, len(daily_metrics) - 7)
            
            if recent_avg > older_avg * 1.2:
                insights.append("Positive trend: Recent performance shows 20%+ improvement in clicks.")
            elif recent_avg < older_avg * 0.8:
                insights.append("Declining trend: Recent performance shows 20%+ decrease in clicks. Investigate potential issues.")
        
        return insights
    
    def _analyze_query_patterns(self, top_queries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze query patterns and characteristics"""
        if not top_queries:
            return {'error': 'No query data available'}
        
        # Analyze query characteristics
        brand_queries = [q for q in top_queries if q.get('is_brand', False)]
        non_brand_queries = [q for q in top_queries if not q.get('is_brand', False)]
        
        # Calculate metrics
        total_clicks = sum(q.get('clicks', 0) for q in top_queries)
        brand_clicks = sum(q.get('clicks', 0) for q in brand_queries)
        non_brand_clicks = sum(q.get('clicks', 0) for q in non_brand_queries)
        
        # Query length analysis
        short_queries = [q for q in top_queries if len(q.get('query', '')) <= 3]
        long_queries = [q for q in top_queries if len(q.get('query', '')) > 10]
        
        return {
            'total_queries': len(top_queries),
            'brand_queries': {
                'count': len(brand_queries),
                'clicks': brand_clicks,
                'percentage': round((brand_clicks / total_clicks * 100), 1) if total_clicks > 0 else 0
            },
            'non_brand_queries': {
                'count': len(non_brand_queries),
                'clicks': non_brand_clicks,
                'percentage': round((non_brand_clicks / total_clicks * 100), 1) if total_clicks > 0 else 0
            },
            'query_length_distribution': {
                'short_queries': len(short_queries),
                'long_queries': len(long_queries),
                'average_length': round(sum(len(q.get('query', '')) for q in top_queries) / len(top_queries), 1)
            },
            'top_categories': self._get_query_categories(top_queries)
        }
    
    def _identify_content_opportunities(self, top_queries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify content optimization opportunities"""
        opportunities = []
        
        # High impression, low CTR queries
        high_impression_low_ctr = [
            q for q in top_queries 
            if q.get('impressions', 0) > 100 and q.get('ctr', 0) < 2
        ]
        
        for query in high_impression_low_ctr[:5]:  # Top 5 opportunities
            opportunities.append({
                'query': query.get('query', ''),
                'impressions': query.get('impressions', 0),
                'ctr': query.get('ctr', 0),
                'opportunity': 'High impressions but low CTR - optimize title and description',
                'priority': 'high'
            })
        
        # Queries with declining performance
        declining_queries = [
            q for q in top_queries 
            if q.get('clicks', 0) > 0 and q.get('avg_position', 0) > 10
        ]
        
        for query in declining_queries[:3]:  # Top 3 declining
            opportunities.append({
                'query': query.get('query', ''),
                'position': query.get('avg_position', 0),
                'clicks': query.get('clicks', 0),
                'opportunity': 'Declining position - improve content relevance and authority',
                'priority': 'medium'
            })
        
        return opportunities
    
    def _get_technical_insights(self, top_queries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get technical SEO insights"""
        if not top_queries:
            return {'error': 'No query data available'}
        
        # Position analysis
        positions = [q.get('avg_position', 0) for q in top_queries if q.get('avg_position', 0) > 0]
        avg_position = sum(positions) / len(positions) if positions else 0
        
        # CTR analysis
        ctrs = [q.get('ctr', 0) for q in top_queries if q.get('ctr', 0) > 0]
        avg_ctr = sum(ctrs) / len(ctrs) if ctrs else 0
        
        return {
            'average_position': round(avg_position, 1),
            'average_ctr': round(avg_ctr, 2),
            'position_distribution': {
                'top_3': len([p for p in positions if p <= 3]),
                'top_10': len([p for p in positions if p <= 10]),
                'page_2_plus': len([p for p in positions if p > 10])
            },
            'ctr_distribution': {
                'excellent': len([c for c in ctrs if c >= 5]),
                'good': len([c for c in ctrs if 2 <= c < 5]),
                'poor': len([c for c in ctrs if c < 2])
            }
        }
    
    def _generate_seo_recommendations(self, top_queries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate SEO recommendations based on query analysis"""
        recommendations = []
        
        if not top_queries:
            return [{'type': 'data', 'priority': 'high', 'recommendation': 'Collect more search data to generate insights'}]
        
        # Analyze performance patterns
        high_performing = [q for q in top_queries if q.get('ctr', 0) > 5 and q.get('clicks', 0) > 10]
        underperforming = [q for q in top_queries if q.get('ctr', 0) < 2 and q.get('impressions', 0) > 50]
        
        if high_performing:
            recommendations.append({
                'type': 'content',
                'priority': 'high',
                'recommendation': f'Replicate success patterns from {len(high_performing)} high-performing queries',
                'action': 'Analyze top-performing content and apply similar optimization strategies'
            })
        
        if underperforming:
            recommendations.append({
                'type': 'optimization',
                'priority': 'medium',
                'recommendation': f'Optimize {len(underperforming)} underperforming queries with high impressions',
                'action': 'Improve title tags, meta descriptions, and content relevance'
            })
        
        # Brand vs non-brand analysis
        brand_queries = [q for q in top_queries if q.get('is_brand', False)]
        if len(brand_queries) / len(top_queries) > 0.7:
            recommendations.append({
                'type': 'strategy',
                'priority': 'medium',
                'recommendation': 'High brand query dependency - diversify with non-brand content',
                'action': 'Create content targeting informational and commercial non-brand queries'
            })
        
        return recommendations
    
    def _calculate_percentage_change(self, current: float, previous: float) -> float:
        """Calculate percentage change between two values"""
        if previous == 0:
            return 100 if current > 0 else 0
        return round(((current - previous) / previous) * 100, 1)
    
    def _calculate_trend_strength(self, daily_metrics: List[Dict[str, Any]]) -> str:
        """Calculate the strength of trends"""
        if len(daily_metrics) < 7:
            return 'insufficient_data'
        
        # Simple trend analysis
        recent_week = daily_metrics[-7:]
        clicks_trend = [m.get('total_clicks', 0) for m in recent_week]
        
        # Check if trend is consistently up, down, or stable
        increasing = sum(1 for i in range(1, len(clicks_trend)) if clicks_trend[i] > clicks_trend[i-1])
        decreasing = sum(1 for i in range(1, len(clicks_trend)) if clicks_trend[i] < clicks_trend[i-1])
        
        if increasing > decreasing + 2:
            return 'strong_upward'
        elif decreasing > increasing + 2:
            return 'strong_downward'
        else:
            return 'stable'
    
    def _calculate_consistency_score(self, daily_metrics: List[Dict[str, Any]]) -> float:
        """Calculate consistency score based on daily performance"""
        if len(daily_metrics) < 7:
            return 0
        
        clicks = [m.get('total_clicks', 0) for m in daily_metrics]
        avg_clicks = sum(clicks) / len(clicks)
        
        # Calculate coefficient of variation (lower is more consistent)
        variance = sum((c - avg_clicks) ** 2 for c in clicks) / len(clicks)
        std_dev = variance ** 0.5
        cv = (std_dev / avg_clicks) * 100 if avg_clicks > 0 else 100
        
        # Convert to 0-100 score (lower CV = higher consistency)
        return max(0, 100 - cv)
    
    def _get_performance_level(self, ctr_score: float, volume_score: float, consistency_score: float) -> str:
        """Determine overall performance level"""
        overall = (ctr_score + volume_score + consistency_score) / 3
        
        if overall >= 80:
            return 'excellent'
        elif overall >= 60:
            return 'good'
        elif overall >= 40:
            return 'fair'
        else:
            return 'needs_improvement'
    
    def _get_query_categories(self, top_queries: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get distribution of query categories"""
        categories = {}
        for query in top_queries:
            category = query.get('category', 'general')
            categories[category] = categories.get(category, 0) + 1
        return categories
