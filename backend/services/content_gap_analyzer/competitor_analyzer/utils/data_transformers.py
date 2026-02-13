"""
Data Transformers for Competitor Analyzer Service

This module contains utility functions for data transformation,
format conversion, and validation between different data formats.
"""

from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import json
from loguru import logger

from ..models.competitor_models import (
    CompetitorProfile,
    CompetitorMetrics,
    CompetitorAnalysis,
    EngagementMetrics,
    SEOMetrics,
    ContentAnalysis,
    ContentType,
    PublishingFrequency,
)
from ..models.market_analysis import (
    MarketPositioning,
    CompetitiveLandscape,
    MarketShare,
    MarketTrend,
)
from ..models.content_gap_models import (
    ContentGap,
    ContentGapAnalysis,
    GapType,
    PriorityLevel,
    ImpactLevel,
)
from ..models.seo_analysis import (
    SEOGap,
    SEOAnalysis,
    SEOGapType,
)
from ..models.shared import (
    AnalysisStatus,
    APIResponse,
    ValidationError,
)


def transform_legacy_competitor_data(legacy_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform legacy competitor data to modern format.
    
    Args:
        legacy_data: Legacy competitor data
        
    Returns:
        Dict[str, Any]: Transformed data
    """
    try:
        transformed = {
            'url': legacy_data.get('url', ''),
            'name': legacy_data.get('name', ''),
            'analysis_timestamp': datetime.utcnow().isoformat(),
            'data_version': '2.0',
            'transformed_from_legacy': True
        }
        
        # Transform engagement metrics
        if 'engagement_metrics' in legacy_data:
            transformed['engagement_metrics'] = transform_engagement_metrics(
                legacy_data['engagement_metrics']
            )
        
        # Transform SEO metrics
        if 'seo_metrics' in legacy_data:
            transformed['seo_metrics'] = transform_seo_metrics(
                legacy_data['seo_metrics']
            )
        
        # Transform content analysis
        if 'content_analysis' in legacy_data:
            transformed['content_analysis'] = transform_content_analysis(
                legacy_data['content_analysis']
            )
        
        # Transform market data
        if 'market_data' in legacy_data:
            transformed['market_data'] = transform_market_data(
                legacy_data['market_data']
            )
        
        # Add validation metadata
        transformed['validation'] = {
            'validated_at': datetime.utcnow().isoformat(),
            'validation_status': 'transformed',
            'warnings': []
        }
        
        return transformed
        
    except Exception as e:
        logger.error(f"Error transforming legacy competitor data: {e}")
        return {'error': f'Transformation failed: {str(e)}'}


def transform_engagement_metrics(legacy_metrics: Dict[str, Any]) -> EngagementMetrics:
    """
    Transform legacy engagement metrics to modern format.
    
    Args:
        legacy_metrics: Legacy engagement metrics
        
    Returns:
        EngagementMetrics: Transformed metrics
    """
    try:
        return EngagementMetrics(
            avg_time_on_page=legacy_metrics.get('avg_time_on_page', 180),
            bounce_rate=legacy_metrics.get('bounce_rate', 0.35),
            social_shares=legacy_metrics.get('social_shares', 0),
            comments_count=legacy_metrics.get('comments_count', 0),
            page_views=legacy_metrics.get('page_views', 0),
            unique_visitors=legacy_metrics.get('unique_visitors', 0),
            conversion_rate=legacy_metrics.get('conversion_rate', 0.0),
        )
        
    except Exception as e:
        logger.error(f"Error transforming engagement metrics: {e}")
        raise


def transform_seo_metrics(legacy_metrics: Dict[str, Any]) -> SEOMetrics:
    """
    Transform legacy SEO metrics to modern format.
    
    Args:
        legacy_metrics: Legacy SEO metrics
        
    Returns:
        SEOMetrics: Transformed metrics
    """
    try:
        return SEOMetrics(
            domain_authority=legacy_metrics.get('domain_authority', 50),
            page_authority=legacy_metrics.get('page_authority', 0),
            page_speed=legacy_metrics.get('page_speed', 75),
            mobile_friendly=legacy_metrics.get('mobile_friendly', True),
            ssl_certificate=legacy_metrics.get('ssl_certificate', True),
            indexed_pages=legacy_metrics.get('indexed_pages', 0),
            backlinks_count=legacy_metrics.get('backlinks_count', 0),
            organic_traffic=legacy_metrics.get('organic_traffic', 0),
            keyword_rankings=legacy_metrics.get('keyword_rankings', 0),
        )
        
    except Exception as e:
        logger.error(f"Error transforming SEO metrics: {e}")
        raise


def transform_content_analysis(legacy_analysis: Dict[str, Any]) -> ContentAnalysis:
    """
    Transform legacy content analysis to modern format.
    
    Args:
        legacy_analysis: Legacy content analysis
        
    Returns:
        ContentAnalysis: Transformed analysis
    """
    try:
        # Transform content types
        content_types = legacy_analysis.get('content_types', ['blog'])
        transformed_types = []
        for content_type in content_types:
            try:
                transformed_types.append(ContentType(content_type))
            except ValueError:
                # Handle unknown content types
                transformed_types.append(ContentType.BLOG_POST)
        
        return ContentAnalysis(
            content_count=legacy_analysis.get('content_count', 0),
            avg_quality_score=legacy_analysis.get('avg_quality_score', 5.0),
            top_keywords=legacy_analysis.get('top_keywords', []),
            content_types=transformed_types,
            publishing_frequency=PublishingFrequency(
                legacy_analysis.get('publishing_frequency', 'weekly')
            ),
            avg_word_count=legacy_analysis.get('avg_word_count', 1000),
            content_depth_score=legacy_analysis.get('content_depth_score', 5.0),
            freshness_score=legacy_analysis.get('freshness_score', 5.0),
            topic_diversity=legacy_analysis.get('topic_diversity', 5.0),
        )
        
    except Exception as e:
        logger.error(f"Error transforming content analysis: {e}")
        raise


def transform_market_data(legacy_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform legacy market data to modern format.
    
    Args:
        legacy_data: Legacy market data
        
    Returns:
        Dict[str, Any]: Transformed market data
    """
    try:
        transformed = {
            'market_share': legacy_data.get('market_share', 0.0),
            'growth_rate': legacy_data.get('growth_rate', 0.0),
            'market_position': legacy_data.get('market_position', 'follower'),
            'competitor_type': legacy_data.get('competitor_type', 'indirect'),
            'industry_focus': legacy_data.get('industry_focus', []),
            'target_audience': legacy_data.get('target_audience', []),
        }
        
        # Transform market positioning if available
        if 'market_positioning' in legacy_data:
            transformed['market_positioning'] = transform_market_positioning(
                legacy_data['market_positioning']
            )
        
        return transformed
        
    except Exception as e:
        logger.error(f"Error transforming market data: {e}")
        return {}


def transform_market_positioning(legacy_positioning: Dict[str, Any]) -> MarketPositioning:
    """
    Transform legacy market positioning to modern format.
    
    Args:
        legacy_positioning: Legacy market positioning data
        
    Returns:
        MarketPositioning: Transformed positioning
    """
    try:
        return MarketPositioning(
            market_leader=legacy_positioning.get('market_leader', ''),
            content_leader=legacy_positioning.get('content_leader', ''),
            quality_leader=legacy_positioning.get('quality_leader', ''),
            market_gaps=legacy_positioning.get('market_gaps', []),
            opportunities=legacy_positioning.get('opportunities', []),
            competitive_advantages=legacy_positioning.get('competitive_advantages', []),
            strategic_recommendations=[],  # Would be transformed from legacy format
            positioning_map=legacy_positioning.get('positioning_map', {}),
            market_maturity=legacy_positioning.get('market_maturity', 'developing'),
            growth_potential=legacy_positioning.get('growth_potential', 'medium'),
        )
        
    except Exception as e:
        logger.error(f"Error transforming market positioning: {e}")
        raise


def transform_to_api_response(data: Any, success: bool = True, 
                           message: str = "", request_id: str = "") -> APIResponse:
    """
    Transform data to API response format.
    
    Args:
        data: Data to include in response
        success: Whether the request was successful
        message: Response message
        request_id: Request identifier
        
    Returns:
        APIResponse: Formatted API response
    """
    try:
        return APIResponse(
            success=success,
            data=data if isinstance(data, dict) else {'result': data},
            message=message or ('Success' if success else 'Failed'),
            timestamp=datetime.utcnow(),
            request_id=request_id,
            errors=None if success else [ValidationError(
                field='general',
                message='Request failed',
                value=None,
                error_code='REQUEST_FAILED'
            )]
        )
        
    except Exception as e:
        logger.error(f"Error transforming to API response: {e}")
        return APIResponse(
            success=False,
            data=None,
            message=f"Response transformation error: {str(e)}",
            timestamp=datetime.utcnow(),
            request_id=request_id,
            errors=[ValidationError(
                field='transformation',
                message=str(e),
                value=None,
                error_code='TRANSFORMATION_ERROR'
            )]
        )


def transform_analysis_summary(analysis_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform analysis data to summary format.
    
    Args:
        analysis_data: Raw analysis data
        
    Returns:
        Dict[str, Any]: Analysis summary
    """
    try:
        summary = {
            'analysis_id': analysis_data.get('analysis_id', ''),
            'status': analysis_data.get('status', 'completed'),
            'industry': analysis_data.get('industry', ''),
            'competitors_analyzed': len(analysis_data.get('competitors', [])),
            'analysis_timestamp': analysis_data.get('analysis_timestamp', datetime.utcnow().isoformat()),
            'key_metrics': {},
            'insights': [],
            'recommendations': []
        }
        
        # Extract key metrics
        competitors = analysis_data.get('competitors', [])
        if competitors:
            # Calculate average metrics
            avg_domain_authority = sum(c.get('seo_metrics', {}).get('domain_authority', 0) for c in competitors) / len(competitors)
            avg_content_quality = sum(c.get('content_analysis', {}).get('avg_quality_score', 0) for c in competitors) / len(competitors)
            total_content_pieces = sum(c.get('content_analysis', {}).get('content_count', 0) for c in competitors)
            
            summary['key_metrics'] = {
                'avg_domain_authority': round(avg_domain_authority, 1),
                'avg_content_quality': round(avg_content_quality, 1),
                'total_content_pieces': total_content_pieces,
                'market_leaders': identify_market_leaders(competitors),
                'content_gaps': len(analysis_data.get('content_gaps', [])),
                'seo_gaps': len(analysis_data.get('seo_gaps', []))
            }
        
        # Extract insights
        summary['insights'] = analysis_data.get('insights', [])
        
        # Extract recommendations
        summary['recommendations'] = analysis_data.get('recommendations', [])
        
        return summary
        
    except Exception as e:
        logger.error(f"Error transforming analysis summary: {e}")
        return {'error': f'Summary transformation failed: {str(e)}'}


def identify_market_leaders(competitors: List[Dict[str, Any]]) -> List[str]:
    """
    Identify market leaders from competitor data.
    
    Args:
        competitors: List of competitor data
        
    Returns:
        List[str]: List of market leader URLs
    """
    try:
        if not competitors:
            return []
        
        # Sort by market share or domain authority
        sorted_competitors = sorted(
            competitors,
            key=lambda x: (
                x.get('market_data', {}).get('market_share', 0),
                x.get('seo_metrics', {}).get('domain_authority', 0)
            ),
            reverse=True
        )
        
        # Return top 3 as market leaders
        return [comp.get('url', '') for comp in sorted_competitors[:3] if comp.get('url')]
        
    except Exception as e:
        logger.error(f"Error identifying market leaders: {e}")
        return []


def transform_content_gaps_to_analysis(gaps: List[Dict[str, Any]]) -> ContentGapAnalysis:
    """
    Transform content gaps to analysis format.
    
    Args:
        gaps: List of content gap data
        
    Returns:
        ContentGapAnalysis: Formatted content gap analysis
    """
    try:
        # Transform individual gaps
        transformed_gaps = []
        gap_counts = {gap_type: 0 for gap_type in GapType}
        
        for gap_data in gaps:
            gap_type = GapType(gap_data.get('gap_type', 'topic_gap'))
            gap_counts[gap_type] += 1
            
            transformed_gap = ContentGap(
                gap_type=gap_type,
                description=gap_data.get('description', ''),
                opportunity_level=gap_data.get('opportunity_level', 'medium'),
                estimated_impact=gap_data.get('estimated_impact', 'medium'),
                content_suggestions=gap_data.get('content_suggestions', []),
                priority=PriorityLevel(gap_data.get('priority', 'medium')),
                implementation_time=gap_data.get('implementation_time', '1-3 months'),
                resources_required=gap_data.get('resources_required', []),
                success_metrics=gap_data.get('success_metrics', []),
                competitor_coverage=gap_data.get('competitor_coverage', {}),
                search_volume=gap_data.get('search_volume'),
                difficulty_score=gap_data.get('difficulty_score'),
            )
            transformed_gaps.append(transformed_gap)
        
        # Separate high priority gaps
        high_priority_gaps = [gap for gap in transformed_gaps if gap.priority == PriorityLevel.HIGH]
        
        return ContentGapAnalysis(
            industry=gaps[0].get('industry', '') if gaps else '',
            competitor_urls=gaps[0].get('competitor_urls', []) if gaps else [],
            total_gaps_identified=len(transformed_gaps),
            gaps_by_type=gap_counts,
            high_priority_gaps=high_priority_gaps,
            topic_gaps=[gap for gap in transformed_gaps if gap.gap_type == GapType.TOPIC_GAP],
            format_gaps=[gap for gap in transformed_gaps if gap.gap_type == GapType.FORMAT_GAP],
            quality_gaps=[gap for gap in transformed_gaps if gap.gap_type == GapType.QUALITY_GAP],
            frequency_gaps=[gap for gap in transformed_gaps if gap.gap_type == GapType.FREQUENCY_GAP],
            gap_summary={
                'total_gaps': len(transformed_gaps),
                'high_priority': len(high_priority_gaps),
                'by_type': dict(gap_counts)
            },
            recommendations=[],  # Would be generated from gaps
            implementation_roadmap=[],  # Would be generated from gaps
            expected_impact='High' if high_priority_gaps else 'Medium',
            analysis_date=datetime.utcnow(),
            confidence_score=0.8
        )
        
    except Exception as e:
        logger.error(f"Error transforming content gaps to analysis: {e}")
        raise


def transform_seo_gaps_to_analysis(gaps: List[Dict[str, Any]]) -> SEOAnalysis:
    """
    Transform SEO gaps to analysis format.
    
    Args:
        gaps: List of SEO gap data
        
    Returns:
        SEOAnalysis: Formatted SEO analysis
    """
    try:
        # Transform individual gaps
        transformed_gaps = []
        gap_counts = {gap_type: 0 for gap_type in SEOGapType}
        
        for gap_data in gaps:
            gap_type = SEOGapType(gap_data.get('gap_type', 'keyword_gap'))
            gap_counts[gap_type] += 1
            
            transformed_gap = SEOGap(
                gap_type=gap_type,
                description=gap_data.get('description', ''),
                impact_level=ImpactLevel(gap_data.get('impact_level', 'medium')),
                opportunity_level=PriorityLevel(gap_data.get('opportunity_level', 'medium')),
                current_performance=gap_data.get('current_performance', {}),
                competitor_performance=gap_data.get('competitor_performance', {}),
                improvement_potential=gap_data.get('improvement_potential', 5.0),
                implementation_complexity=PriorityLevel(gap_data.get('implementation_complexity', 'medium')),
                estimated_time_to_impact=gap_data.get('estimated_time_to_impact', '1-3 months'),
                resource_requirements=gap_data.get('resource_requirements', []),
                success_metrics=gap_data.get('success_metrics', []),
                recommendations=[],  # Would be generated from gap
                related_gaps=gap_data.get('related_gaps', []),
                priority_score=gap_data.get('priority_score', 5.0),
                confidence_level=gap_data.get('confidence_level', 0.8),
            )
            transformed_gaps.append(transformed_gap)
        
        # Separate high priority gaps
        high_priority_gaps = [gap for gap in transformed_gaps if gap.priority == PriorityLevel.HIGH]
        
        return SEOAnalysis(
            industry=gaps[0].get('industry', '') if gaps else '',
            competitor_urls=gaps[0].get('competitor_urls', []) if gaps else [],
            analysis_date=datetime.utcnow(),
            total_gaps_identified=len(transformed_gaps),
            gaps_by_type=gap_counts,
            keyword_gaps=[gap for gap in transformed_gaps if gap.gap_type == SEOGapType.KEYWORD_GAP],
            technical_seo_gaps=[gap for gap in transformed_gaps if gap.gap_type == SEOGapType.TECHNICAL_SEO_GAP],
            backlink_gaps=[gap for gap in transformed_gaps if gap.gap_type == SEOGapType.BACKLINK_GAP],
            seo_comparisons=[],  # Would be generated from gap analysis
            overall_seo_scores={},  # Would be calculated from gaps
            high_priority_gaps=high_priority_gaps,
            recommendations=[],  # Would be generated from gaps
            implementation_roadmap=[],  # Would be generated from gaps
            expected_impact_timeline='3-6 months',
            confidence_score=0.8
        )
        
    except Exception as e:
        logger.error(f"Error transforming SEO gaps to analysis: {e}")
        raise


def transform_health_check_results(results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform health check results to standard format.
    
    Args:
        results: Raw health check results
        
    Returns:
        Dict[str, Any]: Transformed health check results
    """
    try:
        transformed = {
            'service': results.get('service', 'CompetitorAnalyzer'),
            'status': results.get('status', 'healthy'),
            'timestamp': results.get('timestamp', datetime.utcnow().isoformat()),
            'checks': {},
            'overall_score': 0,
            'issues': [],
            'recommendations': []
        }
        
        # Transform individual checks
        checks = results.get('checks', {})
        total_score = 0
        check_count = 0
        
        for check_name, check_result in checks.items():
            check_status = check_result.get('status', 'unknown')
            check_score = check_result.get('score', 0)
            
            transformed['checks'][check_name] = {
                'status': check_status,
                'score': check_score,
                'message': check_result.get('message', ''),
                'details': check_result.get('details', {}),
                'last_checked': check_result.get('last_checked', datetime.utcnow().isoformat())
            }
            
            total_score += check_score
            check_count += 1
            
            # Add issues for failed checks
            if check_status in ['error', 'failed', 'unhealthy']:
                transformed['issues'].append({
                    'check': check_name,
                    'severity': 'high' if check_status == 'error' else 'medium',
                    'message': check_result.get('message', ''),
                    'recommendation': check_result.get('recommendation', '')
                })
        
        # Calculate overall score
        if check_count > 0:
            transformed['overall_score'] = round(total_score / check_count, 1)
        
        # Determine overall status
        if transformed['overall_score'] >= 90:
            transformed['status'] = 'healthy'
        elif transformed['overall_score'] >= 70:
            transformed['status'] = 'degraded'
        else:
            transformed['status'] = 'unhealthy'
        
        return transformed
        
    except Exception as e:
        logger.error(f"Error transforming health check results: {e}")
        return {
            'service': 'CompetitorAnalyzer',
            'status': 'error',
            'timestamp': datetime.utcnow().isoformat(),
            'error': f'Health check transformation failed: {str(e)}'
        }


def validate_analysis_results(analysis_data: Dict[str, Any]) -> List[ValidationError]:
    """
    Validate analysis results and return validation errors.
    
    Args:
        analysis_data: Analysis data to validate
        
    Returns:
        List[ValidationError]: List of validation errors
    """
    errors = []
    
    try:
        # Validate required fields
        required_fields = ['industry', 'competitors', 'analysis_timestamp']
        for field in required_fields:
            if field not in analysis_data:
                errors.append(ValidationError(
                    field=field,
                    message=f'Required field {field} is missing',
                    value=None,
                    error_code='MISSING_REQUIRED_FIELD'
                ))
        
        # Validate competitors data
        competitors = analysis_data.get('competitors', [])
        if not isinstance(competitors, list):
            errors.append(ValidationError(
                field='competitors',
                message='Competitors must be a list',
                value=competitors,
                error_code='INVALID_COMPETITORS_FORMAT'
            ))
        else:
            for i, competitor in enumerate(competitors):
                if not isinstance(competitor, dict):
                    errors.append(ValidationError(
                        field=f'competitors[{i}]',
                        message='Each competitor must be a dictionary',
                        value=competitor,
                        error_code='INVALID_COMPETITOR_FORMAT'
                    ))
                elif 'url' not in competitor:
                    errors.append(ValidationError(
                        field=f'competitors[{i}].url',
                        message='Competitor URL is required',
                        value=None,
                        error_code='MISSING_COMPETITOR_URL'
                    ))
        
        # Validate timestamp format
        timestamp = analysis_data.get('analysis_timestamp')
        if timestamp:
            try:
                # Try to parse timestamp
                if isinstance(timestamp, str):
                    datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                elif isinstance(timestamp, datetime):
                    pass  # Valid datetime object
                else:
                    errors.append(ValidationError(
                        field='analysis_timestamp',
                        message='Invalid timestamp format',
                        value=timestamp,
                        error_code='INVALID_TIMESTAMP_FORMAT'
                    ))
            except (ValueError, AttributeError):
                errors.append(ValidationError(
                    field='analysis_timestamp',
                    message='Invalid timestamp format',
                    value=timestamp,
                    error_code='INVALID_TIMESTAMP_FORMAT'
                ))
        
    except Exception as e:
        logger.error(f"Error validating analysis results: {e}")
        errors.append(ValidationError(
            field='validation',
            message=f'Validation error: {str(e)}',
            value=analysis_data,
            error_code='VALIDATION_ERROR'
        ))
    
    return errors


def transform_to_export_format(data: Dict[str, Any], 
                           export_format: str = 'json') -> Union[str, bytes]:
    """
    Transform data to export format.
    
    Args:
        data: Data to export
        export_format: Export format ('json', 'csv', 'excel')
        
    Returns:
        Union[str, bytes]: Exported data
    """
    try:
        if export_format.lower() == 'json':
            return json.dumps(data, indent=2, default=str)
        
        elif export_format.lower() == 'csv':
            # Simplified CSV export (would use pandas in production)
            if isinstance(data, dict) and 'competitors' in data:
                csv_lines = []
                competitors = data['competitors']
                if competitors:
                    # Header
                    headers = list(competitors[0].keys())
                    csv_lines.append(','.join(headers))
                    
                    # Data rows
                    for competitor in competitors:
                        row = []
                        for header in headers:
                            value = competitor.get(header, '')
                            if isinstance(value, (dict, list)):
                                value = json.dumps(value)
                            elif isinstance(value, str):
                                value = f'"{value}"'  # Quote strings
                            else:
                                value = str(value)
                            row.append(value)
                        csv_lines.append(','.join(row))
                
                return '\n'.join(csv_lines)
        
        else:
            raise ValueError(f"Unsupported export format: {export_format}")
        
    except Exception as e:
        logger.error(f"Error transforming to export format: {e}")
        return f"Export failed: {str(e)}"


def merge_analysis_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Merge multiple analysis results into a single result.
    
    Args:
        results: List of analysis results
        
    Returns:
        Dict[str, Any]: Merged analysis results
    """
    try:
        if not results:
            return {}
        
        merged = {
            'merged_at': datetime.utcnow().isoformat(),
            'source_analyses': len(results),
            'industry': results[0].get('industry', ''),
            'competitors': [],
            'content_gaps': [],
            'seo_gaps': [],
            'market_analysis': {},
            'insights': [],
            'recommendations': []
        }
        
        # Merge competitors
        all_competitors = {}
        for result in results:
            for competitor in result.get('competitors', []):
                url = competitor.get('url', '')
                if url and url not in all_competitors:
                    all_competitors[url] = competitor
        
        merged['competitors'] = list(all_competitors.values())
        
        # Merge content gaps
        all_gaps = []
        for result in results:
            all_gaps.extend(result.get('content_gaps', []))
        
        # Remove duplicates based on description
        seen_descriptions = set()
        unique_gaps = []
        for gap in all_gaps:
            description = gap.get('description', '')
            if description not in seen_descriptions:
                seen_descriptions.add(description)
                unique_gaps.append(gap)
        
        merged['content_gaps'] = unique_gaps
        
        # Merge SEO gaps
        all_seo_gaps = []
        for result in results:
            all_seo_gaps.extend(result.get('seo_gaps', []))
        
        # Remove duplicates
        seen_seo_descriptions = set()
        unique_seo_gaps = []
        for gap in all_seo_gaps:
            description = gap.get('description', '')
            if description not in seen_seo_descriptions:
                seen_seo_descriptions.add(description)
                unique_seo_gaps.append(gap)
        
        merged['seo_gaps'] = unique_seo_gaps
        
        # Merge insights and recommendations
        for result in results:
            merged['insights'].extend(result.get('insights', []))
            merged['recommendations'].extend(result.get('recommendations', []))
        
        # Update summary statistics
        merged['summary'] = {
            'total_competitors': len(merged['competitors']),
            'total_content_gaps': len(merged['content_gaps']),
            'total_seo_gaps': len(merged['seo_gaps']),
            'total_insights': len(merged['insights']),
            'total_recommendations': len(merged['recommendations'])
        }
        
        return merged
        
    except Exception as e:
        logger.error(f"Error merging analysis results: {e}")
        return {'error': f'Merge failed: {str(e)}'}


def filter_analysis_by_criteria(analysis_data: Dict[str, Any],
                              filters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Filter analysis data based on specified criteria.
    
    Args:
        analysis_data: Analysis data to filter
        filters: Filter criteria
        
    Returns:
        Dict[str, Any]: Filtered analysis data
    """
    try:
        filtered = analysis_data.copy()
        
        # Filter competitors
        if 'competitors' in filtered and 'competitor_filters' in filters:
            competitor_filters = filters['competitor_filters']
            filtered_competitors = []
            
            for competitor in filtered['competitors']:
                include = True
                
                # Filter by domain authority
                if 'min_domain_authority' in competitor_filters:
                    da = competitor.get('seo_metrics', {}).get('domain_authority', 0)
                    if da < competitor_filters['min_domain_authority']:
                        include = False
                
                # Filter by content quality
                if 'min_quality_score' in competitor_filters:
                    quality = competitor.get('content_analysis', {}).get('avg_quality_score', 0)
                    if quality < competitor_filters['min_quality_score']:
                        include = False
                
                # Filter by competitor type
                if 'competitor_types' in competitor_filters:
                    comp_type = competitor.get('market_data', {}).get('competitor_type', '')
                    if comp_type not in competitor_filters['competitor_types']:
                        include = False
                
                if include:
                    filtered_competitors.append(competitor)
            
            filtered['competitors'] = filtered_competitors
        
        # Filter content gaps
        if 'content_gaps' in filtered and 'gap_filters' in filters:
            gap_filters = filters['gap_filters']
            filtered_gaps = []
            
            for gap in filtered['content_gaps']:
                include = True
                
                # Filter by gap type
                if 'gap_types' in gap_filters:
                    if gap.get('gap_type') not in gap_filters['gap_types']:
                        include = False
                
                # Filter by priority
                if 'priorities' in gap_filters:
                    if gap.get('priority') not in gap_filters['priorities']:
                        include = False
                
                # Filter by opportunity level
                if 'opportunity_levels' in gap_filters:
                    if gap.get('opportunity_level') not in gap_filters['opportunity_levels']:
                        include = False
                
                if include:
                    filtered_gaps.append(gap)
            
            filtered['content_gaps'] = filtered_gaps
        
        # Update filtered metadata
        filtered['filtered_at'] = datetime.utcnow().isoformat()
        filtered['applied_filters'] = filters
        filtered['original_counts'] = {
            'competitors': len(analysis_data.get('competitors', [])),
            'content_gaps': len(analysis_data.get('content_gaps', [])),
            'seo_gaps': len(analysis_data.get('seo_gaps', []))
        }
        filtered['filtered_counts'] = {
            'competitors': len(filtered.get('competitors', [])),
            'content_gaps': len(filtered.get('content_gaps', [])),
            'seo_gaps': len(filtered.get('seo_gaps', []))
        }
        
        return filtered
        
    except Exception as e:
        logger.error(f"Error filtering analysis by criteria: {e}")
        return {'error': f'Filtering failed: {str(e)}'}
