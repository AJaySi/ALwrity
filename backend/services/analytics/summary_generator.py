"""
Analytics Summary Generator

Generates comprehensive summaries and aggregations of analytics data across platforms.
"""

from typing import Dict, Any, List
from datetime import datetime
from utils.logging import get_logger
logger = get_logger("analytics_summary_generator", migration_mode=True)

from .models.analytics_data import AnalyticsData
from .models.platform_types import PlatformType


class AnalyticsSummaryGenerator:
    """Generates analytics summaries and insights"""
    
    def __init__(self):
        self.supported_metrics = [
            'total_clicks',
            'total_impressions',
            'avg_ctr',
            'avg_position',
            'total_queries',
            'connected_sites'
        ]
    
    def get_analytics_summary(self, analytics_data: Dict[str, AnalyticsData]) -> Dict[str, Any]:
        """
        Generate a summary of analytics data across all platforms
        
        Args:
            analytics_data: Dictionary of platform analytics data
            
        Returns:
            Summary statistics and insights
        """
        summary = {
            'total_platforms': len(analytics_data),
            'connected_platforms': 0,
            'successful_data': 0,
            'partial_data': 0,
            'failed_data': 0,
            'total_clicks': 0,
            'total_impressions': 0,
            'total_queries': 0,
            'total_sites': 0,
            'platforms': {},
            'insights': [],
            'last_updated': datetime.now().isoformat()
        }
        
        # Process each platform's data
        for platform_name, data in analytics_data.items():
            platform_summary = self._process_platform_data(platform_name, data)
            summary['platforms'][platform_name] = platform_summary
            
            # Aggregate counts
            if data.status == 'success':
                summary['connected_platforms'] += 1
                summary['successful_data'] += 1
            elif data.status == 'partial':
                summary['partial_data'] += 1
            else:
                summary['failed_data'] += 1
            
            # Aggregate metrics if successful
            if data.is_successful():
                summary['total_clicks'] += data.get_total_clicks()
                summary['total_impressions'] += data.get_total_impressions()
                summary['total_queries'] += data.get_metric('total_queries', 0)
                summary['total_sites'] += data.get_metric('connected_sites', 0)
        
        # Calculate derived metrics
        summary['overall_ctr'] = self._calculate_ctr(summary['total_clicks'], summary['total_impressions'])
        summary['avg_position'] = self._calculate_avg_position(analytics_data)
        summary['insights'] = self._generate_insights(summary, analytics_data)
        
        return summary
    
    def _process_platform_data(self, platform_name: str, data: AnalyticsData) -> Dict[str, Any]:
        """Process individual platform data for summary"""
        platform_summary = {
            'status': data.status,
            'last_updated': data.last_updated,
            'metrics_count': len(data.metrics),
            'has_data': data.is_successful() or data.is_partial()
        }
        
        if data.has_error():
            platform_summary['error'] = data.error_message
        
        if data.is_successful():
            # Add key metrics for successful platforms
            platform_summary.update({
                'clicks': data.get_total_clicks(),
                'impressions': data.get_total_impressions(),
                'ctr': data.get_avg_ctr(),
                'position': data.get_avg_position(),
                'queries': data.get_metric('total_queries', 0),
                'sites': data.get_metric('connected_sites', 0)
            })
        
        return platform_summary
    
    def _calculate_ctr(self, total_clicks: int, total_impressions: int) -> float:
        """Calculate overall click-through rate"""
        if total_impressions > 0:
            return round(total_clicks / total_impressions * 100, 2)
        return 0.0
    
    def _calculate_avg_position(self, analytics_data: Dict[str, AnalyticsData]) -> float:
        """Calculate average position across all platforms"""
        total_position = 0
        platform_count = 0
        
        for data in analytics_data.values():
            if data.is_successful():
                position = data.get_avg_position()
                if position > 0:
                    total_position += position
                    platform_count += 1
        
        if platform_count > 0:
            return round(total_position / platform_count, 2)
        return 0.0
    
    def _generate_insights(self, summary: Dict[str, Any], analytics_data: Dict[str, AnalyticsData]) -> List[str]:
        """Generate actionable insights from analytics data"""
        insights = []
        
        # Connection insights
        if summary['connected_platforms'] == 0:
            insights.append("No platforms are currently connected. Connect platforms to start collecting analytics data.")
        elif summary['connected_platforms'] < summary['total_platforms']:
            insights.append(f"Only {summary['connected_platforms']} of {summary['total_platforms']} platforms are connected.")
        
        # Performance insights
        if summary['total_clicks'] > 0:
            insights.append(f"Total traffic across all platforms: {summary['total_clicks']:,} clicks from {summary['total_impressions']:,} impressions.")
            
            if summary['overall_ctr'] < 2.0:
                insights.append("Overall CTR is below 2%. Consider optimizing titles and descriptions for better click-through rates.")
            elif summary['overall_ctr'] > 5.0:
                insights.append("Excellent CTR performance! Your content is highly engaging.")
        
        # Platform-specific insights
        for platform_name, data in analytics_data.items():
            if data.is_successful():
                if data.get_avg_position() > 10:
                    insights.append(f"{platform_name.title()} average position is {data.get_avg_position()}. Consider SEO optimization.")
                elif data.get_avg_position() < 5:
                    insights.append(f"Great {platform_name.title()} performance! Average position is {data.get_avg_position()}.")
        
        # Data freshness insights
        for platform_name, data in analytics_data.items():
            if data.is_successful():
                try:
                    last_updated = datetime.fromisoformat(data.last_updated.replace('Z', '+00:00'))
                    hours_old = (datetime.now().replace(tzinfo=last_updated.tzinfo) - last_updated).total_seconds() / 3600
                    
                    if hours_old > 24:
                        insights.append(f"{platform_name.title()} data is {hours_old:.1f} hours old. Consider refreshing for latest insights.")
                except:
                    pass
        
        return insights
    
    def get_platform_comparison(self, analytics_data: Dict[str, AnalyticsData]) -> Dict[str, Any]:
        """Generate platform comparison metrics"""
        comparison = {
            'platforms': {},
            'top_performer': None,
            'needs_attention': []
        }
        
        max_clicks = 0
        top_platform = None
        
        for platform_name, data in analytics_data.items():
            if data.is_successful():
                platform_metrics = {
                    'clicks': data.get_total_clicks(),
                    'impressions': data.get_total_impressions(),
                    'ctr': data.get_avg_ctr(),
                    'position': data.get_avg_position(),
                    'queries': data.get_metric('total_queries', 0)
                }
                
                comparison['platforms'][platform_name] = platform_metrics
                
                # Track top performer
                if platform_metrics['clicks'] > max_clicks:
                    max_clicks = platform_metrics['clicks']
                    top_platform = platform_name
                
                # Identify platforms needing attention
                if platform_metrics['ctr'] < 1.0 or platform_metrics['position'] > 20:
                    comparison['needs_attention'].append(platform_name)
        
        comparison['top_performer'] = top_platform
        return comparison
    
    def get_trend_analysis(self, analytics_data: Dict[str, AnalyticsData]) -> Dict[str, Any]:
        """Generate trend analysis (placeholder for future implementation)"""
        # TODO: Implement trend analysis when historical data is available
        return {
            'status': 'not_implemented',
            'message': 'Trend analysis requires historical data collection',
            'suggestions': [
                'Enable data storage to track trends over time',
                'Implement daily metrics collection',
                'Add time-series analysis capabilities'
            ]
        }
