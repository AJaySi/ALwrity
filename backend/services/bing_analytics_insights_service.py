"""
Bing Analytics Insights Service

Generates meaningful insights and analytics from stored Bing Webmaster Tools data.
Provides actionable recommendations, trend analysis, and performance insights.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy import create_engine, func, desc, and_, or_, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from models.bing_analytics_models import (
    BingQueryStats, BingDailyMetrics, BingTrendAnalysis,
    BingAlertRules, BingAlertHistory, BingSitePerformance
)
from services.database import get_session_for_user

logger = logging.getLogger(__name__)


class BingAnalyticsInsightsService:
    """Service for generating insights from Bing analytics data"""
    
    def __init__(self, database_url: Optional[str] = None):
        """Initialize the insights service"""
        # Legacy support: database_url is ignored as we use per-user sessions
        pass
    
    def _get_db_session(self, user_id: str) -> Session:
        """Get database session for user"""
        return get_session_for_user(user_id)
    
    def _with_db_session(self, user_id: str, func):
        """Context manager for database sessions"""
        db = None
        try:
            db = self._get_db_session(user_id)
            return func(db)
        finally:
            if db:
                db.close()
    
    def get_comprehensive_insights(self, user_id: str, site_url: str, days: int = 30) -> Dict[str, Any]:
        """
        Generate comprehensive insights from Bing analytics data
        
        Args:
            user_id: User identifier
            site_url: Site URL
            days: Number of days to analyze (default 30)
            
        Returns:
            Dict containing comprehensive insights
        """
        return self._with_db_session(user_id, lambda db: self._generate_comprehensive_insights(db, user_id, site_url, days))
    
    def _generate_comprehensive_insights(self, db: Session, user_id: str, site_url: str, days: int) -> Dict[str, Any]:
        """Generate comprehensive insights from the database"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Get performance summary
            performance_summary = self._get_performance_summary(db, user_id, site_url, start_date, end_date)
            
            # Get trending queries
            trending_queries = self._get_trending_queries(db, user_id, site_url, start_date, end_date)
            
            # Get top performing content
            top_content = self._get_top_performing_content(db, user_id, site_url, start_date, end_date)
            
            # Get SEO opportunities
            seo_opportunities = self._get_seo_opportunities(db, user_id, site_url, start_date, end_date)
            
            # Get competitive insights
            competitive_insights = self._get_competitive_insights(db, user_id, site_url, start_date, end_date)
            
            # Get actionable recommendations
            recommendations = self._get_actionable_recommendations(
                performance_summary, trending_queries, top_content, seo_opportunities
            )
            
            return {
                "performance_summary": performance_summary,
                "trending_queries": trending_queries,
                "top_content": top_content,
                "seo_opportunities": seo_opportunities,
                "competitive_insights": competitive_insights,
                "recommendations": recommendations,
                "last_analyzed": datetime.now().isoformat(),
                "analysis_period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days": days
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating comprehensive insights: {e}")
            return {"error": str(e)}
    
    def _get_performance_summary(self, db: Session, user_id: str, site_url: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get overall performance summary"""
        try:
            # Get aggregated metrics
            metrics = db.query(
                func.sum(BingQueryStats.clicks).label('total_clicks'),
                func.sum(BingQueryStats.impressions).label('total_impressions'),
                func.count(BingQueryStats.query).label('total_queries'),
                func.avg(BingQueryStats.ctr).label('avg_ctr'),
                func.avg(BingQueryStats.avg_impression_position).label('avg_position')
            ).filter(
                and_(
                    BingQueryStats.user_id == user_id,
                    BingQueryStats.site_url == site_url,
                    BingQueryStats.query_date >= start_date,
                    BingQueryStats.query_date <= end_date
                )
            ).first()
            
            # Get daily trend data
            daily_trends = db.query(
                func.date(BingQueryStats.query_date).label('date'),
                func.sum(BingQueryStats.clicks).label('clicks'),
                func.sum(BingQueryStats.impressions).label('impressions'),
                func.avg(BingQueryStats.ctr).label('ctr')
            ).filter(
                and_(
                    BingQueryStats.user_id == user_id,
                    BingQueryStats.site_url == site_url,
                    BingQueryStats.query_date >= start_date,
                    BingQueryStats.query_date <= end_date
                )
            ).group_by(func.date(BingQueryStats.query_date)).order_by('date').all()
            
            # Calculate trends
            trend_analysis = self._calculate_trends(daily_trends)
            
            return {
                "total_clicks": metrics.total_clicks or 0,
                "total_impressions": metrics.total_impressions or 0,
                "total_queries": metrics.total_queries or 0,
                "avg_ctr": round(metrics.avg_ctr or 0, 2),
                "avg_position": round(metrics.avg_position or 0, 2),
                "daily_trends": [{"date": str(d.date), "clicks": d.clicks, "impressions": d.impressions, "ctr": round(d.ctr or 0, 2)} for d in daily_trends],
                "trend_analysis": trend_analysis
            }
            
        except Exception as e:
            logger.error(f"Error getting performance summary: {e}")
            return {"error": str(e)}
    
    def _get_trending_queries(self, db: Session, user_id: str, site_url: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get trending queries analysis"""
        try:
            # Get top queries by clicks
            top_clicks = db.query(
                BingQueryStats.query,
                func.sum(BingQueryStats.clicks).label('total_clicks'),
                func.sum(BingQueryStats.impressions).label('total_impressions'),
                func.avg(BingQueryStats.ctr).label('avg_ctr'),
                func.avg(BingQueryStats.avg_impression_position).label('avg_position')
            ).filter(
                and_(
                    BingQueryStats.user_id == user_id,
                    BingQueryStats.site_url == site_url,
                    BingQueryStats.query_date >= start_date,
                    BingQueryStats.query_date <= end_date
                )
            ).group_by(BingQueryStats.query).order_by(desc('total_clicks')).limit(10).all()
            
            # Get top queries by impressions
            top_impressions = db.query(
                BingQueryStats.query,
                func.sum(BingQueryStats.clicks).label('total_clicks'),
                func.sum(BingQueryStats.impressions).label('total_impressions'),
                func.avg(BingQueryStats.ctr).label('avg_ctr'),
                func.avg(BingQueryStats.avg_impression_position).label('avg_position')
            ).filter(
                and_(
                    BingQueryStats.user_id == user_id,
                    BingQueryStats.site_url == site_url,
                    BingQueryStats.query_date >= start_date,
                    BingQueryStats.query_date <= end_date
                )
            ).group_by(BingQueryStats.query).order_by(desc('total_impressions')).limit(10).all()
            
            # Get high CTR queries (opportunities)
            high_ctr_queries = db.query(
                BingQueryStats.query,
                func.sum(BingQueryStats.clicks).label('total_clicks'),
                func.sum(BingQueryStats.impressions).label('total_impressions'),
                func.avg(BingQueryStats.ctr).label('avg_ctr'),
                func.avg(BingQueryStats.avg_impression_position).label('avg_position')
            ).filter(
                and_(
                    BingQueryStats.user_id == user_id,
                    BingQueryStats.site_url == site_url,
                    BingQueryStats.query_date >= start_date,
                    BingQueryStats.query_date <= end_date,
                    BingQueryStats.impressions >= 10  # Minimum impressions for reliability
                )
            ).group_by(BingQueryStats.query).having(func.avg(BingQueryStats.ctr) > 5).order_by(desc(func.avg(BingQueryStats.ctr))).limit(10).all()
            
            return {
                "top_by_clicks": [{"query": q.query, "clicks": q.total_clicks, "impressions": q.total_impressions, "ctr": round(q.avg_ctr or 0, 2), "position": round(q.avg_position or 0, 2)} for q in top_clicks],
                "top_by_impressions": [{"query": q.query, "clicks": q.total_clicks, "impressions": q.total_impressions, "ctr": round(q.avg_ctr or 0, 2), "position": round(q.avg_position or 0, 2)} for q in top_impressions],
                "high_ctr_opportunities": [{"query": q.query, "clicks": q.total_clicks, "impressions": q.total_impressions, "ctr": round(q.avg_ctr or 0, 2), "position": round(q.avg_position or 0, 2)} for q in high_ctr_queries]
            }
            
        except Exception as e:
            logger.error(f"Error getting trending queries: {e}")
            return {"error": str(e)}
    
    def _get_top_performing_content(self, db: Session, user_id: str, site_url: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get top performing content categories"""
        try:
            # Get category performance
            category_performance = db.query(
                BingQueryStats.category,
                func.sum(BingQueryStats.clicks).label('total_clicks'),
                func.sum(BingQueryStats.impressions).label('total_impressions'),
                func.avg(BingQueryStats.ctr).label('avg_ctr'),
                func.count(BingQueryStats.query).label('query_count')
            ).filter(
                and_(
                    BingQueryStats.user_id == user_id,
                    BingQueryStats.site_url == site_url,
                    BingQueryStats.query_date >= start_date,
                    BingQueryStats.query_date <= end_date
                )
            ).group_by(BingQueryStats.category).order_by(desc('total_clicks')).all()
            
            # Get brand vs non-brand performance
            brand_performance = db.query(
                BingQueryStats.is_brand_query,
                func.sum(BingQueryStats.clicks).label('total_clicks'),
                func.sum(BingQueryStats.impressions).label('total_impressions'),
                func.avg(BingQueryStats.ctr).label('avg_ctr')
            ).filter(
                and_(
                    BingQueryStats.user_id == user_id,
                    BingQueryStats.site_url == site_url,
                    BingQueryStats.query_date >= start_date,
                    BingQueryStats.query_date <= end_date
                )
            ).group_by(BingQueryStats.is_brand_query).all()
            
            return {
                "category_performance": [{"category": c.category, "clicks": c.total_clicks, "impressions": c.total_impressions, "ctr": round(c.avg_ctr or 0, 2), "query_count": c.query_count} for c in category_performance],
                "brand_vs_nonbrand": [{"type": "Brand" if b.is_brand_query else "Non-Brand", "clicks": b.total_clicks, "impressions": b.total_impressions, "ctr": round(b.avg_ctr or 0, 2)} for b in brand_performance]
            }
            
        except Exception as e:
            logger.error(f"Error getting top performing content: {e}")
            return {"error": str(e)}
    
    def _get_seo_opportunities(self, db: Session, user_id: str, site_url: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get SEO opportunities and recommendations"""
        try:
            # Get queries with high impressions but low CTR (optimization opportunities)
            optimization_opportunities = db.query(
                BingQueryStats.query,
                func.sum(BingQueryStats.clicks).label('total_clicks'),
                func.sum(BingQueryStats.impressions).label('total_impressions'),
                func.avg(BingQueryStats.ctr).label('avg_ctr'),
                func.avg(BingQueryStats.avg_impression_position).label('avg_position')
            ).filter(
                and_(
                    BingQueryStats.user_id == user_id,
                    BingQueryStats.site_url == site_url,
                    BingQueryStats.query_date >= start_date,
                    BingQueryStats.query_date <= end_date,
                    BingQueryStats.impressions >= 20,  # Minimum impressions
                    BingQueryStats.avg_impression_position <= 10,  # Good position
                    BingQueryStats.ctr < 3  # Low CTR
                )
            ).group_by(BingQueryStats.query).order_by(desc('total_impressions')).limit(15).all()
            
            # Get queries ranking on page 2 (positions 11-20)
            page2_opportunities = db.query(
                BingQueryStats.query,
                func.sum(BingQueryStats.clicks).label('total_clicks'),
                func.sum(BingQueryStats.impressions).label('total_impressions'),
                func.avg(BingQueryStats.ctr).label('avg_ctr'),
                func.avg(BingQueryStats.avg_impression_position).label('avg_position')
            ).filter(
                and_(
                    BingQueryStats.user_id == user_id,
                    BingQueryStats.site_url == site_url,
                    BingQueryStats.query_date >= start_date,
                    BingQueryStats.query_date <= end_date,
                    BingQueryStats.avg_impression_position >= 11,
                    BingQueryStats.avg_impression_position <= 20
                )
            ).group_by(BingQueryStats.query).order_by(desc('total_impressions')).limit(10).all()
            
            return {
                "optimization_opportunities": [{"query": o.query, "clicks": o.total_clicks, "impressions": o.total_impressions, "ctr": round(o.avg_ctr or 0, 2), "position": round(o.avg_position or 0, 2), "opportunity": "Improve CTR with better titles/descriptions"} for o in optimization_opportunities],
                "page2_opportunities": [{"query": o.query, "clicks": o.total_clicks, "impressions": o.total_impressions, "ctr": round(o.avg_ctr or 0, 2), "position": round(o.avg_position or 0, 2), "opportunity": "Optimize to move to page 1"} for o in page2_opportunities]
            }
            
        except Exception as e:
            logger.error(f"Error getting SEO opportunities: {e}")
            return {"error": str(e)}
    
    def _get_competitive_insights(self, db: Session, user_id: str, site_url: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get competitive insights and market analysis"""
        try:
            # Get query length analysis
            query_length_analysis = db.query(
                BingQueryStats.query_length,
                func.count(BingQueryStats.query).label('query_count'),
                func.sum(BingQueryStats.clicks).label('total_clicks'),
                func.avg(BingQueryStats.ctr).label('avg_ctr')
            ).filter(
                and_(
                    BingQueryStats.user_id == user_id,
                    BingQueryStats.site_url == site_url,
                    BingQueryStats.query_date >= start_date,
                    BingQueryStats.query_date <= end_date
                )
            ).group_by(BingQueryStats.query_length).order_by(BingQueryStats.query_length).all()
            
            # Get position distribution
            position_distribution = db.query(
                func.case(
                    (BingQueryStats.avg_impression_position <= 3, "Top 3"),
                    (BingQueryStats.avg_impression_position <= 10, "Page 1"),
                    (BingQueryStats.avg_impression_position <= 20, "Page 2"),
                    else_="Page 3+"
                ).label('position_group'),
                func.count(BingQueryStats.query).label('query_count'),
                func.sum(BingQueryStats.clicks).label('total_clicks')
            ).filter(
                and_(
                    BingQueryStats.user_id == user_id,
                    BingQueryStats.site_url == site_url,
                    BingQueryStats.query_date >= start_date,
                    BingQueryStats.query_date <= end_date
                )
            ).group_by('position_group').all()
            
            return {
                "query_length_analysis": [{"length": q.query_length, "count": q.query_count, "clicks": q.total_clicks, "ctr": round(q.avg_ctr or 0, 2)} for q in query_length_analysis],
                "position_distribution": [{"position": p.position_group, "query_count": p.query_count, "clicks": p.total_clicks} for p in position_distribution]
            }
            
        except Exception as e:
            logger.error(f"Error getting competitive insights: {e}")
            return {"error": str(e)}
    
    def _calculate_trends(self, daily_trends: List) -> Dict[str, Any]:
        """Calculate trend analysis from daily data"""
        if len(daily_trends) < 2:
            return {"clicks_trend": "insufficient_data", "impressions_trend": "insufficient_data", "ctr_trend": "insufficient_data"}
        
        try:
            # Calculate trends (comparing first half vs second half)
            mid_point = len(daily_trends) // 2
            first_half = daily_trends[:mid_point]
            second_half = daily_trends[mid_point:]
            
            # Calculate averages for each half
            first_half_clicks = sum(d.clicks or 0 for d in first_half) / len(first_half)
            second_half_clicks = sum(d.clicks or 0 for d in second_half) / len(second_half)
            
            first_half_impressions = sum(d.impressions or 0 for d in first_half) / len(first_half)
            second_half_impressions = sum(d.impressions or 0 for d in second_half) / len(second_half)
            
            first_half_ctr = sum(d.ctr or 0 for d in first_half) / len(first_half)
            second_half_ctr = sum(d.ctr or 0 for d in second_half) / len(second_half)
            
            # Calculate percentage changes
            clicks_change = ((second_half_clicks - first_half_clicks) / first_half_clicks * 100) if first_half_clicks > 0 else 0
            impressions_change = ((second_half_impressions - first_half_impressions) / first_half_impressions * 100) if first_half_impressions > 0 else 0
            ctr_change = ((second_half_ctr - first_half_ctr) / first_half_ctr * 100) if first_half_ctr > 0 else 0
            
            return {
                "clicks_trend": {
                    "change_percent": round(clicks_change, 2),
                    "direction": "up" if clicks_change > 0 else "down" if clicks_change < 0 else "stable",
                    "current": round(second_half_clicks, 2),
                    "previous": round(first_half_clicks, 2)
                },
                "impressions_trend": {
                    "change_percent": round(impressions_change, 2),
                    "direction": "up" if impressions_change > 0 else "down" if impressions_change < 0 else "stable",
                    "current": round(second_half_impressions, 2),
                    "previous": round(first_half_impressions, 2)
                },
                "ctr_trend": {
                    "change_percent": round(ctr_change, 2),
                    "direction": "up" if ctr_change > 0 else "down" if ctr_change < 0 else "stable",
                    "current": round(second_half_ctr, 2),
                    "previous": round(first_half_ctr, 2)
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating trends: {e}")
            return {"error": str(e)}
    
    def _get_actionable_recommendations(self, performance_summary: Dict, trending_queries: Dict, top_content: Dict, seo_opportunities: Dict) -> Dict[str, Any]:
        """Generate actionable recommendations based on the analysis"""
        try:
            recommendations = {
                "immediate_actions": [],
                "content_optimization": [],
                "technical_improvements": [],
                "long_term_strategy": []
            }
            
            # Analyze performance summary for recommendations
            if performance_summary.get("avg_ctr", 0) < 3:
                recommendations["immediate_actions"].append({
                    "action": "Improve Meta Descriptions",
                    "priority": "high",
                    "description": f"Current CTR is {performance_summary.get('avg_ctr', 0)}%. Focus on creating compelling meta descriptions that encourage clicks."
                })
            
            if performance_summary.get("avg_position", 0) > 10:
                recommendations["immediate_actions"].append({
                    "action": "Improve Page Rankings",
                    "priority": "high",
                    "description": f"Average position is {performance_summary.get('avg_position', 0)}. Focus on on-page SEO and content quality."
                })
            
            # Analyze trending queries for content opportunities
            high_ctr_queries = trending_queries.get("high_ctr_opportunities", [])
            if high_ctr_queries:
                recommendations["content_optimization"].extend([
                    {
                        "query": q["query"],
                        "opportunity": f"Expand content around '{q['query']}' - high CTR of {q['ctr']}%",
                        "priority": "medium"
                    } for q in high_ctr_queries[:5]
                ])
            
            # Analyze SEO opportunities
            optimization_ops = seo_opportunities.get("optimization_opportunities", [])
            if optimization_ops:
                recommendations["technical_improvements"].extend([
                    {
                        "issue": f"Low CTR for '{op['query']}'",
                        "solution": f"Optimize title and meta description for '{op['query']}' to improve CTR from {op['ctr']}%",
                        "priority": "medium"
                    } for op in optimization_ops[:3]
                ])
            
            # Long-term strategy recommendations
            if performance_summary.get("total_queries", 0) < 100:
                recommendations["long_term_strategy"].append({
                    "strategy": "Expand Content Portfolio",
                    "timeline": "3-6 months",
                    "expected_impact": "Increase organic traffic by 50-100%"
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return {"error": str(e)}
    
    def get_quick_insights(self, user_id: str, site_url: str) -> Dict[str, Any]:
        """Get quick insights for dashboard display"""
        return self._with_db_session(lambda db: self._generate_quick_insights(db, user_id, site_url))
    
    def _generate_quick_insights(self, db: Session, user_id: str, site_url: str) -> Dict[str, Any]:
        """Generate quick insights for dashboard"""
        try:
            # Get last 7 days data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            
            # Get basic metrics
            metrics = db.query(
                func.sum(BingQueryStats.clicks).label('total_clicks'),
                func.sum(BingQueryStats.impressions).label('total_impressions'),
                func.count(BingQueryStats.query).label('total_queries'),
                func.avg(BingQueryStats.ctr).label('avg_ctr'),
                func.avg(BingQueryStats.avg_impression_position).label('avg_position')
            ).filter(
                and_(
                    BingQueryStats.user_id == user_id,
                    BingQueryStats.site_url == site_url,
                    BingQueryStats.query_date >= start_date,
                    BingQueryStats.query_date <= end_date
                )
            ).first()
            
            # Get top 3 queries
            top_queries = db.query(
                BingQueryStats.query,
                func.sum(BingQueryStats.clicks).label('total_clicks'),
                func.sum(BingQueryStats.impressions).label('total_impressions'),
                func.avg(BingQueryStats.ctr).label('avg_ctr')
            ).filter(
                and_(
                    BingQueryStats.user_id == user_id,
                    BingQueryStats.site_url == site_url,
                    BingQueryStats.query_date >= start_date,
                    BingQueryStats.query_date <= end_date
                )
            ).group_by(BingQueryStats.query).order_by(desc('total_clicks')).limit(3).all()
            
            return {
                "total_clicks": metrics.total_clicks or 0,
                "total_impressions": metrics.total_impressions or 0,
                "total_queries": metrics.total_queries or 0,
                "avg_ctr": round(metrics.avg_ctr or 0, 2),
                "avg_position": round(metrics.avg_position or 0, 2),
                "top_queries": [{"query": q.query, "clicks": q.total_clicks, "impressions": q.total_impressions, "ctr": round(q.avg_ctr or 0, 2)} for q in top_queries],
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating quick insights: {e}")
            return {"error": str(e)}
