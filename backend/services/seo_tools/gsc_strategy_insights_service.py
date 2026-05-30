"""
GSC Strategy Insights Service for SEO Dashboard

Transforms Google Search Console data into strategic insights optimized for
SEO Dashboard (not blog topic suggestions). Focuses on:
- Trend analysis and performance monitoring
- ROI-weighted opportunity prioritization
- Competitive positioning insights
- Impact forecasting and recommendations

This service builds upon GSCBrainstormService but focuses on dashboard needs:
- Broader SEO strategy context
- Historical trend analysis
- Competitive benchmarking
- Multi-metric ranking and scoring
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import asyncio
from dataclasses import dataclass
from enum import Enum
from loguru import logger
import json

from services.gsc_service import GSCService
from services.gsc_brainstorm_service import GSCBrainstormService
from services.llm_providers.main_text_generation import llm_text_gen


# Enums for strategy types
class StrategyType(str, Enum):
    """Types of strategic insights"""
    QUICK_WIN = "quick_win"
    KEYWORD_GAP = "keyword_gap"
    CONTENT_OPPORTUNITY = "content_opportunity"
    PAGE_OPTIMIZATION = "page_optimization"
    COMPETITIVE_GAP = "competitive_gap"
    MARKET_INSIGHT = "market_insight"
    TREND_ALERT = "trend_alert"
    SEASONAL_PATTERN = "seasonal_pattern"


class OpportunitySeverity(str, Enum):
    """Severity levels for opportunities"""
    CRITICAL = "critical"      # 80-100 ROI score
    HIGH = "high"              # 60-79 ROI score
    MEDIUM = "medium"          # 40-59 ROI score
    LOW = "low"                # 20-39 ROI score
    WATCH = "watch"            # <20 ROI score


# Data classes for structured responses
@dataclass
class StrategyOpportunity:
    """Represents a single strategic opportunity"""
    type: StrategyType
    keyword: str
    description: str
    roi_score: float  # 0-100
    priority: int  # 1-10
    effort_hours: float
    timeline_weeks: int
    current_position: float
    impressions: int
    current_ctr: float
    estimated_impact: float  # Monthly clicks gained
    severity: OpportunitySeverity
    recommendations: List[str]
    related_keywords: List[str]
    timestamp: datetime


@dataclass
class TrendMetric:
    """Represents a performance trend"""
    keyword: str
    metric: str  # 'position', 'impressions', 'clicks', 'ctr'
    current_value: float
    value_30d_ago: float
    value_90d_ago: float
    trend: str  # 'up', 'down', 'stable'
    trend_percentage: float  # -100 to +100
    momentum: float  # Acceleration of trend
    seasonal: bool
    anomaly: bool


@dataclass
class HealthMetrics:
    """Overall dashboard health metrics"""
    health_score: int  # 0-100
    score_trend: str  # 'up', 'down', 'stable'
    score_change: float  # Percentage change
    total_keywords: int
    page_1_keywords: int
    avg_position: float
    avg_ctr: float
    total_impressions: int
    total_clicks: int
    opportunities_count: int
    quick_wins_count: int
    keyword_gaps_count: int
    competitive_gaps_count: int
    timestamp: datetime
    period: str  # 'daily', 'weekly', 'monthly'


class GSCStrategyInsightsService:
    """
    Service for generating strategic SEO dashboard insights from GSC data.
    
    Key differences from GSCBrainstormService:
    1. Dashboard-focused context (not blog-specific)
    2. Trend analysis with historical data
    3. ROI-weighted scoring
    4. Competitive positioning
    5. Impact forecasting
    6. Multi-metric health scoring
    """
    
    def __init__(self, gsc_service: Optional[GSCService] = None):
        """
        Initialize the strategy insights service.
        
        Args:
            gsc_service: Optional GSCService instance (uses default if not provided)
        """
        self.service_name = "gsc_strategy_insights"
        self.gsc_service = gsc_service or GSCService()
        self.brainstorm_service = GSCBrainstormService(gsc_service)
        logger.info(f"Initialized {self.service_name}")
    
    async def get_dashboard_strategy(
        self,
        user_id: str,
        site_url: str,
        include_trends: bool = True,
        include_competitive: bool = True,
        top_n: int = 20
    ) -> Dict[str, Any]:
        """
        Get comprehensive strategy insights for dashboard display.
        
        Args:
            user_id: User ID for context
            site_url: Website URL
            include_trends: Include trend analysis
            include_competitive: Include competitive analysis
            top_n: Number of top opportunities to return
            
        Returns:
            Comprehensive strategy insights
        """
        try:
            logger.info(f"Generating dashboard strategy for {site_url}")
            start_time = datetime.utcnow()
            
            # Execute parallel analysis tasks
            tasks = {
                'opportunities': self._get_ranked_opportunities(site_url, top_n),
                'health_metrics': self._calculate_health_metrics(site_url),
                'quick_summary': self._generate_quick_summary(site_url),
            }
            
            # Conditional tasks
            if include_trends:
                tasks['trends'] = self._analyze_performance_trends(site_url)
            if include_competitive:
                tasks['competitive'] = self._analyze_competitive_positioning(site_url)
            
            # Execute all tasks concurrently
            results = await asyncio.gather(*tasks.values(), return_exceptions=True)
            
            # Aggregate results
            strategy_data = {}
            for task_name, result in zip(tasks.keys(), results):
                if isinstance(result, Exception):
                    logger.error(f"Strategy task {task_name} failed: {str(result)}")
                    strategy_data[task_name] = {'status': 'failed', 'error': str(result)}
                else:
                    strategy_data[task_name] = result
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return {
                'status': 'success',
                'data': strategy_data,
                'generated_at': datetime.utcnow().isoformat(),
                'execution_time_seconds': execution_time,
                'site_url': site_url,
            }
            
        except Exception as e:
            logger.error(f"Error generating dashboard strategy: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'generated_at': datetime.utcnow().isoformat(),
            }
    
    async def _get_ranked_opportunities(
        self,
        site_url: str,
        top_n: int = 20
    ) -> Dict[str, Any]:
        """
        Get ROI-weighted ranked opportunities.
        
        Scoring formula (0-100):
        ROI = 0.40 × (traffic_impact) + 
              0.30 × (ease_of_implementation) + 
              0.20 × (competitive_advantage) +
              0.10 × (momentum_score)
        
        Args:
            site_url: Website URL
            top_n: Number of top opportunities
            
        Returns:
            Ranked opportunities with ROI scores
        """
        try:
            # Get brainstorm opportunities (reuse existing analysis)
            brainstorm_result = await self.brainstorm_service.brainstorm_topics(
                user_id="dashboard",
                keywords="all",  # Special case: all keywords
                site_url=site_url
            )
            
            if not brainstorm_result or 'error' in brainstorm_result:
                return {'status': 'no_data', 'error': 'Could not fetch brainstorm data'}
            
            # Extract all opportunities
            all_opportunities = []
            
            # Quick wins (positions 4-10)
            for win in brainstorm_result.get('quick_wins', []):
                roi = self._calculate_roi_score(
                    traffic_impact=min(100, (win['impressions'] / 1000) * 10),
                    ease=80,  # Positions 4-10 are relatively easy
                    competitive=50,
                    momentum=60
                )
                opportunity = StrategyOpportunity(
                    type=StrategyType.QUICK_WIN,
                    keyword=win['keyword'],
                    description=f"Position {win['position']} → page 1 ranking",
                    roi_score=roi,
                    priority=1,
                    effort_hours=2,
                    timeline_weeks=1,
                    current_position=win['position'],
                    impressions=win['impressions'],
                    current_ctr=win['current_ctr'],
                    estimated_impact=win.get('estimated_traffic_gain', 0),
                    severity=self._get_severity(roi),
                    recommendations=[
                        "Update title and meta description",
                        "Improve content quality and depth",
                        "Add internal links from authority pages"
                    ],
                    related_keywords=self._find_related_keywords(win['keyword']),
                    timestamp=datetime.utcnow()
                )
                all_opportunities.append(opportunity)
            
            # Content opportunities (high volume, low CTR)
            for opp in brainstorm_result.get('content_opportunities', []):
                roi = self._calculate_roi_score(
                    traffic_impact=min(100, (opp['impressions'] / 2000) * 10),
                    ease=70,  # Meta updates are easy
                    competitive=40,
                    momentum=50
                )
                opportunity = StrategyOpportunity(
                    type=StrategyType.CONTENT_OPPORTUNITY,
                    keyword=opp['keyword'],
                    description=f"{opp['impressions']} impressions at position {opp['current_position']}",
                    roi_score=roi,
                    priority=2,
                    effort_hours=3,
                    timeline_weeks=1,
                    current_position=opp['current_position'],
                    impressions=opp['impressions'],
                    current_ctr=opp['current_ctr'],
                    estimated_impact=opp.get('estimated_traffic_gain', 0),
                    severity=self._get_severity(roi),
                    recommendations=[
                        f"Improve CTR from {opp['current_ctr']}% to 5%+",
                        "A/B test meta descriptions",
                        "Review SERP position and update title angle"
                    ],
                    related_keywords=self._find_related_keywords(opp['keyword']),
                    timestamp=datetime.utcnow()
                )
                all_opportunities.append(opportunity)
            
            # Keyword gaps (positions 11-20)
            for gap in brainstorm_result.get('keyword_gaps', []):
                roi = self._calculate_roi_score(
                    traffic_impact=min(100, (gap['estimated_traffic_if_page1'] / 500) * 10),
                    ease=50,  # Requires content improvements
                    competitive=70,
                    momentum=60
                )
                opportunity = StrategyOpportunity(
                    type=StrategyType.KEYWORD_GAP,
                    keyword=gap['keyword'],
                    description=f"Position {gap['position']} → large traffic opportunity",
                    roi_score=roi,
                    priority=2,
                    effort_hours=8,
                    timeline_weeks=4,
                    current_position=gap['position'],
                    impressions=gap['impressions'],
                    current_ctr=gap['current_ctr'],
                    estimated_impact=gap.get('estimated_traffic_if_page1', 0),
                    severity=self._get_severity(roi),
                    recommendations=[
                        "Create comprehensive guide on this topic",
                        "Increase content depth and topical coverage",
                        "Build topical authority in this space"
                    ],
                    related_keywords=self._find_related_keywords(gap['keyword']),
                    timestamp=datetime.utcnow()
                )
                all_opportunities.append(opportunity)
            
            # Sort by ROI score descending
            ranked = sorted(all_opportunities, key=lambda x: x.roi_score, reverse=True)
            
            # Convert to dictionaries and return top N
            return {
                'status': 'success',
                'opportunities': [
                    {
                        'type': opp.type.value,
                        'keyword': opp.keyword,
                        'roi_score': round(opp.roi_score, 1),
                        'priority': opp.priority,
                        'effort_hours': opp.effort_hours,
                        'timeline_weeks': opp.timeline_weeks,
                        'current_position': opp.current_position,
                        'impressions': opp.impressions,
                        'estimated_impact': round(opp.estimated_impact, 1),
                        'severity': opp.severity.value,
                        'recommendations': opp.recommendations,
                        'related_keywords': opp.related_keywords,
                    }
                    for opp in ranked[:top_n]
                ],
                'total_opportunities': len(ranked),
            }
            
        except Exception as e:
            logger.error(f"Error ranking opportunities: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    async def _calculate_health_metrics(self, site_url: str) -> Dict[str, Any]:
        """
        Calculate comprehensive health metrics for dashboard.
        
        Metrics include:
        - Health score (0-100)
        - Keyword position distribution
        - Average CTR vs benchmark
        - Growth trends
        - Overall assessment
        """
        try:
            # Get brainstorm summary (has health score)
            brainstorm_result = await self.brainstorm_service.brainstorm_topics(
                user_id="dashboard",
                keywords="all",
                site_url=site_url
            )
            
            summary = brainstorm_result.get('summary', {})
            
            return {
                'status': 'success',
                'health_score': summary.get('health_score', 0),
                'health_trend': 'stable',  # TODO: Compare with historical
                'total_keywords': summary.get('total_keywords_analyzed', 0),
                'page_1_keywords': summary.get('keyword_distribution', {}).get('positions_1_3', 0),
                'avg_position': summary.get('avg_position', 0),
                'avg_ctr': summary.get('avg_ctr', 0),
                'ctr_vs_benchmark': summary.get('ctr_vs_benchmark', 0),
                'total_impressions': summary.get('total_impressions', 0),
                'total_clicks': summary.get('total_clicks', 0),
                'timestamp': datetime.utcnow().isoformat(),
            }
            
        except Exception as e:
            logger.error(f"Error calculating health metrics: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    async def _generate_quick_summary(self, site_url: str) -> Dict[str, Any]:
        """Generate a quick text summary of key insights."""
        try:
            brainstorm_result = await self.brainstorm_service.brainstorm_topics(
                user_id="dashboard",
                keywords="all",
                site_url=site_url
            )
            
            summary = brainstorm_result.get('summary', {})
            quick_wins_count = len(brainstorm_result.get('quick_wins', []))
            opportunities_count = len(brainstorm_result.get('content_opportunities', []))
            gaps_count = len(brainstorm_result.get('keyword_gaps', []))
            
            # Generate summary text
            summary_text = (
                f"Found {quick_wins_count} quick wins (positions 4-10), "
                f"{opportunities_count} content optimization opportunities (high volume, low CTR), "
                f"and {gaps_count} keyword gaps on page 2+ that could boost traffic. "
                f"Overall SEO health: {summary.get('health_score', 0)}/100. "
            )
            
            return {
                'status': 'success',
                'summary': summary_text,
                'key_metrics': {
                    'quick_wins': quick_wins_count,
                    'opportunities': opportunities_count,
                    'gaps': gaps_count,
                    'health_score': summary.get('health_score', 0),
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating quick summary: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    async def _analyze_performance_trends(self, site_url: str) -> Dict[str, Any]:
        """Analyze performance trends over time."""
        # TODO: Implement historical trend analysis
        # This would require storing historical GSC snapshots
        return {
            'status': 'pending',
            'message': 'Trend analysis requires historical data collection',
            'note': 'To be implemented in Phase 2'
        }
    
    async def _analyze_competitive_positioning(self, site_url: str) -> Dict[str, Any]:
        """Analyze competitive positioning."""
        # TODO: Implement competitive analysis
        # This would require competitor keyword data
        return {
            'status': 'pending',
            'message': 'Competitive analysis requires competitor data integration',
            'note': 'To be implemented in Phase 2'
        }
    
    def _calculate_roi_score(
        self,
        traffic_impact: float,
        ease: float,
        competitive: float,
        momentum: float
    ) -> float:
        """
        Calculate ROI score (0-100).
        
        Formula:
        ROI = 0.40 × traffic_impact + 
              0.30 × ease +
              0.20 × competitive +
              0.10 × momentum
        """
        roi = (
            0.40 * min(100, traffic_impact) +
            0.30 * min(100, ease) +
            0.20 * min(100, competitive) +
            0.10 * min(100, momentum)
        )
        return min(100, max(0, roi))
    
    def _get_severity(self, roi_score: float) -> OpportunitySeverity:
        """Get severity level based on ROI score."""
        if roi_score >= 80:
            return OpportunitySeverity.CRITICAL
        elif roi_score >= 60:
            return OpportunitySeverity.HIGH
        elif roi_score >= 40:
            return OpportunitySeverity.MEDIUM
        elif roi_score >= 20:
            return OpportunitySeverity.LOW
        else:
            return OpportunitySeverity.WATCH
    
    def _find_related_keywords(self, keyword: str) -> List[str]:
        """Find related keywords (placeholder)."""
        # TODO: Implement semantic similarity search
        # For now, return empty list
        return []


# Export for router usage
__all__ = [
    'GSCStrategyInsightsService',
    'StrategyOpportunity',
    'StrategyType',
    'OpportunitySeverity',
    'HealthMetrics',
    'TrendMetric',
]
