"""
Bing Analytics Storage Service

Handles storage, retrieval, and analysis of Bing Webmaster Tools analytics data.
Provides methods for data persistence, trend analysis, and alert management.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy import create_engine, func, desc, and_, or_
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from models.bing_analytics_models import (
    BingQueryStats, BingDailyMetrics, BingTrendAnalysis,
    BingAlertRules, BingAlertHistory, BingSitePerformance
)
from services.integrations.bing_oauth import BingOAuthService
from services.database import get_session_for_user

logger = logging.getLogger(__name__)


class BingAnalyticsStorageService:
    """Service for managing Bing analytics data storage and analysis"""
    
    def __init__(self, database_url: Optional[str] = None):
        """Initialize the storage service"""
        # Legacy support: database_url is ignored
        self.bing_service = BingOAuthService()
    
    def _create_tables(self):
        """Create database tables if they don't exist"""
        # Handled by services.database.init_user_database
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
    
    def store_raw_query_data(self, user_id: str, site_url: str, query_data: List[Dict[str, Any]]) -> bool:
        """
        Store raw query statistics data from Bing API
        
        Args:
            user_id: User identifier
            site_url: Site URL
            query_data: List of query statistics from Bing API
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            db = self._get_db_session(user_id)
            
            # Process and store each query
            stored_count = 0
            for query_item in query_data:
                try:
                    # Parse date from Bing format
                    query_date = self._parse_bing_date(query_item.get('Date', ''))
                    
                    # Calculate CTR
                    clicks = query_item.get('Clicks', 0)
                    impressions = query_item.get('Impressions', 0)
                    ctr = (clicks / impressions * 100) if impressions > 0 else 0
                    
                    # Determine if brand query
                    is_brand = self._is_brand_query(query_item.get('Query', ''), site_url)
                    
                    # Categorize query
                    category = self._categorize_query(query_item.get('Query', ''))
                    
                    # Create query stats record
                    query_stats = BingQueryStats(
                        user_id=user_id,
                        site_url=site_url,
                        query=query_item.get('Query', ''),
                        clicks=clicks,
                        impressions=impressions,
                        avg_click_position=query_item.get('AvgClickPosition', -1),
                        avg_impression_position=query_item.get('AvgImpressionPosition', -1),
                        ctr=ctr,
                        query_date=query_date,
                        query_length=len(query_item.get('Query', '')),
                        is_brand_query=is_brand,
                        category=category
                    )
                    
                    db.add(query_stats)
                    stored_count += 1
                    
                except Exception as e:
                    logger.error(f"Error processing individual query: {e}")
                    continue
            
            db.commit()
            db.close()
            
            logger.info(f"Successfully stored {stored_count} Bing query records for {site_url}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing Bing query data: {e}")
            if 'db' in locals():
                db.rollback()
                db.close()
            return False
    
    def generate_daily_metrics(self, user_id: str, site_url: str, target_date: datetime = None) -> bool:
        """
        Generate and store daily aggregated metrics
        
        Args:
            user_id: User identifier
            site_url: Site URL
            target_date: Date to generate metrics for (defaults to yesterday)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if target_date is None:
                target_date = datetime.now() - timedelta(days=1)
            
            # Get date range for the day
            start_date = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)
            
            db = self._get_db_session(user_id)
            
            # Get raw data for the day
            daily_queries = db.query(BingQueryStats).filter(
                and_(
                    BingQueryStats.user_id == user_id,
                    BingQueryStats.site_url == site_url,
                    BingQueryStats.query_date >= start_date,
                    BingQueryStats.query_date < end_date
                )
            ).all()
            
            if not daily_queries:
                logger.warning(f"No query data found for {site_url} on {target_date.date()}")
                db.close()
                return False
            
            # Calculate aggregated metrics
            total_clicks = sum(q.clicks for q in daily_queries)
            total_impressions = sum(q.impressions for q in daily_queries)
            total_queries = len(daily_queries)
            avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
            avg_position = sum(q.avg_click_position for q in daily_queries if q.avg_click_position > 0) / len([q for q in daily_queries if q.avg_click_position > 0]) if any(q.avg_click_position > 0 for q in daily_queries) else 0
            
            # Get top performing queries
            top_queries = sorted(daily_queries, key=lambda x: x.clicks, reverse=True)[:10]
            top_clicks = [{'query': q.query, 'clicks': q.clicks, 'impressions': q.impressions, 'ctr': q.ctr} for q in top_queries]
            top_impressions = sorted(daily_queries, key=lambda x: x.impressions, reverse=True)[:10]
            top_impressions_data = [{'query': q.query, 'clicks': q.clicks, 'impressions': q.impressions, 'ctr': q.ctr} for q in top_impressions]
            
            # Calculate changes from previous day
            prev_day_metrics = self._get_previous_day_metrics(db, user_id, site_url, target_date)
            clicks_change = self._calculate_percentage_change(total_clicks, prev_day_metrics.get('total_clicks', 0))
            impressions_change = self._calculate_percentage_change(total_impressions, prev_day_metrics.get('total_impressions', 0))
            ctr_change = self._calculate_percentage_change(avg_ctr, prev_day_metrics.get('avg_ctr', 0))
            
            # Create daily metrics record
            daily_metrics = BingDailyMetrics(
                user_id=user_id,
                site_url=site_url,
                metric_date=start_date,
                total_clicks=total_clicks,
                total_impressions=total_impressions,
                total_queries=total_queries,
                avg_ctr=avg_ctr,
                avg_position=avg_position,
                top_queries=json.dumps(top_clicks),
                top_clicks=json.dumps(top_clicks),
                top_impressions=json.dumps(top_impressions_data),
                clicks_change=clicks_change,
                impressions_change=impressions_change,
                ctr_change=ctr_change
            )
            
            # Check if record already exists and update or create
            existing = db.query(BingDailyMetrics).filter(
                and_(
                    BingDailyMetrics.user_id == user_id,
                    BingDailyMetrics.site_url == site_url,
                    BingDailyMetrics.metric_date == start_date
                )
            ).first()
            
            if existing:
                # Update existing record
                for key, value in daily_metrics.__dict__.items():
                    if not key.startswith('_') and key != 'id':
                        setattr(existing, key, value)
            else:
                # Create new record
                db.add(daily_metrics)
            
            db.commit()
            db.close()
            
            logger.info(f"Successfully generated daily metrics for {site_url} on {target_date.date()}")
            return True
            
        except Exception as e:
            logger.error(f"Error generating daily metrics: {e}")
            if 'db' in locals():
                db.rollback()
                db.close()
            return False
    
    def get_analytics_summary(self, user_id: str, site_url: str, days: int = 30) -> Dict[str, Any]:
        """
        Get analytics summary for a site over a specified period
        
        Args:
            user_id: User identifier
            site_url: Site URL
            days: Number of days to include in summary
            
        Returns:
            Dict containing analytics summary
        """
        try:
            db = self._get_db_session()
            
            # Date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Get daily metrics for the period
            daily_metrics = db.query(BingDailyMetrics).filter(
                and_(
                    BingDailyMetrics.user_id == user_id,
                    BingDailyMetrics.site_url == site_url,
                    BingDailyMetrics.metric_date >= start_date,
                    BingDailyMetrics.metric_date <= end_date
                )
            ).order_by(BingDailyMetrics.metric_date).all()
            
            if not daily_metrics:
                return {'error': 'No analytics data found for the specified period'}
            
            # Calculate summary statistics
            total_clicks = sum(m.total_clicks for m in daily_metrics)
            total_impressions = sum(m.total_impressions for m in daily_metrics)
            total_queries = sum(m.total_queries for m in daily_metrics)
            avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
            
            # Get top performing queries for the period
            top_queries = []
            for metric in daily_metrics:
                if metric.top_queries:
                    try:
                        queries = json.loads(metric.top_queries)
                        top_queries.extend(queries)
                    except:
                        continue
            
            # Aggregate and sort top queries
            query_aggregates = {}
            for query in top_queries:
                q = query['query']
                if q not in query_aggregates:
                    query_aggregates[q] = {'clicks': 0, 'impressions': 0, 'count': 0}
                query_aggregates[q]['clicks'] += query['clicks']
                query_aggregates[q]['impressions'] += query['impressions']
                query_aggregates[q]['count'] += 1
            
            # Sort by clicks and get top 10
            top_performing = sorted(
                [{'query': k, **v} for k, v in query_aggregates.items()],
                key=lambda x: x['clicks'],
                reverse=True
            )[:10]
            
            # Calculate trends
            recent_metrics = daily_metrics[-7:] if len(daily_metrics) >= 7 else daily_metrics
            older_metrics = daily_metrics[:-7] if len(daily_metrics) >= 14 else daily_metrics
            
            recent_avg_ctr = sum(m.avg_ctr for m in recent_metrics) / len(recent_metrics) if recent_metrics else 0
            older_avg_ctr = sum(m.avg_ctr for m in older_metrics) / len(older_metrics) if older_metrics else 0
            ctr_trend = self._calculate_percentage_change(recent_avg_ctr, older_avg_ctr)
            
            db.close()
            
            return {
                'period_days': days,
                'total_clicks': total_clicks,
                'total_impressions': total_impressions,
                'total_queries': total_queries,
                'avg_ctr': round(avg_ctr, 2),
                'ctr_trend': round(ctr_trend, 2),
                'top_queries': top_performing,
                'daily_metrics_count': len(daily_metrics),
                'data_quality': 'good' if len(daily_metrics) >= days * 0.8 else 'partial'
            }
            
        except Exception as e:
            logger.error(f"Error getting analytics summary: {e}")
            if 'db' in locals():
                db.close()
            return {'error': str(e)}
    
    def get_top_queries(self, user_id: str, site_url: str, days: int = 30, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get top performing queries for a site over a specified period
        
        Args:
            user_id: User identifier
            site_url: Site URL
            days: Number of days to analyze
            limit: Maximum number of queries to return
            
        Returns:
            List of top queries with performance data
        """
        try:
            db = self._get_db_session()
            
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Query top queries from the database
            query_stats = db.query(BingQueryStats).filter(
                BingQueryStats.user_id == user_id,
                BingQueryStats.site_url == site_url,
                BingQueryStats.query_date >= start_date,
                BingQueryStats.query_date <= end_date
            ).order_by(BingQueryStats.clicks.desc()).limit(limit).all()
            
            # Convert to list of dictionaries
            top_queries = []
            for stat in query_stats:
                top_queries.append({
                    'query': stat.query,
                    'clicks': stat.clicks,
                    'impressions': stat.impressions,
                    'ctr': stat.ctr,
                    'position': stat.avg_click_position,
                    'date': stat.query_date.isoformat()
                })
            
            db.close()
            return top_queries
            
        except Exception as e:
            logger.error(f"Error getting top queries: {e}")
            if 'db' in locals():
                db.close()
            return []

    def get_daily_metrics(self, user_id: str, site_url: str, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get daily metrics for a site over a specified period
        """
        try:
            db = self._get_db_session(user_id)
            
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            daily_metrics = db.query(BingDailyMetrics).filter(
                BingDailyMetrics.user_id == user_id,
                BingDailyMetrics.site_url == site_url,
                BingDailyMetrics.metric_date >= start_date,
                BingDailyMetrics.metric_date <= end_date
            ).order_by(BingDailyMetrics.metric_date.desc()).all()
            
            metrics_list = []
            for metric in daily_metrics:
                metrics_list.append({
                    'date': metric.metric_date.isoformat(),
                    'total_clicks': metric.total_clicks,
                    'total_impressions': metric.total_impressions,
                    'total_queries': metric.total_queries,
                    'avg_ctr': metric.avg_ctr,
                    'avg_position': metric.avg_position,
                    'clicks_change': metric.clicks_change,
                    'impressions_change': metric.impressions_change,
                    'ctr_change': metric.ctr_change
                })
            
            db.close()
            return metrics_list
            
        except Exception as e:
            logger.error(f"Error getting daily metrics: {e}")
            if 'db' in locals():
                db.close()
            return []
    
    def collect_and_store_data(self, user_id: str, site_url: str, days_back: int = 30) -> bool:
        """
        Collect fresh data from Bing API and store it
        
        Args:
            user_id: User identifier
            site_url: Site URL
            days_back: How many days back to collect data for
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            # Get query stats from Bing API
            query_data = self.bing_service.get_query_stats(
                user_id=user_id,
                site_url=site_url,
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d'),
                page=0
            )
            
            if 'error' in query_data:
                logger.error(f"Bing API error: {query_data['error']}")
                return False
            
            # Extract queries from response
            queries = self._extract_queries_from_response(query_data)
            if not queries:
                logger.warning(f"No queries found in Bing API response for {site_url}")
                return False
            
            # Store raw data
            if not self.store_raw_query_data(user_id, site_url, queries):
                logger.error("Failed to store raw query data")
                return False
            
            # Generate daily metrics for each day
            current_date = start_date
            while current_date < end_date:
                if not self.generate_daily_metrics(user_id, site_url, current_date):
                    logger.warning(f"Failed to generate daily metrics for {current_date.date()}")
                current_date += timedelta(days=1)
            
            logger.info(f"Successfully collected and stored Bing data for {site_url}")
            return True
            
        except Exception as e:
            logger.error(f"Error collecting and storing Bing data: {e}")
            return False
    
    def _parse_bing_date(self, date_str: str) -> datetime:
        """Parse Bing API date format"""
        try:
            # Bing uses /Date(timestamp-0700)/ format
            if date_str.startswith('/Date(') and date_str.endswith(')/'):
                timestamp_str = date_str[6:-2].split('-')[0]
                timestamp = int(timestamp_str) / 1000  # Convert from milliseconds
                return datetime.fromtimestamp(timestamp)
            else:
                return datetime.now()
        except:
            return datetime.now()
    
    def _is_brand_query(self, query: str, site_url: str) -> bool:
        """Determine if a query is a brand query"""
        # Extract domain from site URL
        domain = site_url.replace('https://', '').replace('http://', '').split('/')[0]
        brand_terms = domain.split('.')
        
        # Check if query contains brand terms
        query_lower = query.lower()
        for term in brand_terms:
            if len(term) > 3 and term in query_lower:
                return True
        return False
    
    def _categorize_query(self, query: str) -> str:
        """Categorize a query based on keywords"""
        query_lower = query.lower()
        
        if any(term in query_lower for term in ['ai', 'artificial intelligence', 'machine learning']):
            return 'ai'
        elif any(term in query_lower for term in ['story', 'narrative', 'tale', 'fiction']):
            return 'story_writing'
        elif any(term in query_lower for term in ['business', 'plan', 'strategy', 'company']):
            return 'business'
        elif any(term in query_lower for term in ['letter', 'email', 'correspondence']):
            return 'letter_writing'
        elif any(term in query_lower for term in ['blog', 'article', 'content', 'post']):
            return 'content_writing'
        elif any(term in query_lower for term in ['free', 'generator', 'tool', 'online']):
            return 'tools'
        else:
            return 'general'
    
    def _extract_queries_from_response(self, response_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract queries from Bing API response"""
        try:
            if isinstance(response_data, dict) and 'd' in response_data:
                d_data = response_data['d']
                if isinstance(d_data, dict) and 'results' in d_data:
                    return d_data['results']
                elif isinstance(d_data, list):
                    return d_data
            elif isinstance(response_data, list):
                return response_data
            return []
        except Exception as e:
            logger.error(f"Error extracting queries from response: {e}")
            return []
    
    def _get_previous_day_metrics(self, db: Session, user_id: str, site_url: str, current_date: datetime) -> Dict[str, float]:
        """Get metrics from the previous day for comparison"""
        try:
            prev_date = current_date - timedelta(days=1)
            prev_metrics = db.query(BingDailyMetrics).filter(
                and_(
                    BingDailyMetrics.user_id == user_id,
                    BingDailyMetrics.site_url == site_url,
                    BingDailyMetrics.metric_date == prev_date.replace(hour=0, minute=0, second=0, microsecond=0)
                )
            ).first()
            
            if prev_metrics:
                return {
                    'total_clicks': prev_metrics.total_clicks,
                    'total_impressions': prev_metrics.total_impressions,
                    'avg_ctr': prev_metrics.avg_ctr
                }
            return {}
        except Exception as e:
            logger.error(f"Error getting previous day metrics: {e}")
            return {}
    
    def _calculate_percentage_change(self, current: float, previous: float) -> float:
        """Calculate percentage change between two values"""
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        return ((current - previous) / previous) * 100
