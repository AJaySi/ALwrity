"""
Competitor Utilities for Competitor Analyzer Service

This module contains utility functions for competitor analysis,
data extraction, validation, and processing.
"""

from typing import Dict, Any, List, Optional, Tuple, Union
from urllib.parse import urlparse
import re
import json
from collections import Counter, defaultdict
from loguru import logger

from ..constants import (
    DEFAULT_COMPETITOR_ANALYSIS,
    MAX_COMPETITORS_PER_ANALYSIS,
    MAX_URLS_PER_BATCH,
    HIGH_DOMAIN_AUTHORITY_THRESHOLD,
    MEDIUM_DOMAIN_AUTHORITY_THRESHOLD,
    LOW_DOMAIN_AUTHORITY_THRESHOLD,
    GOOD_PAGE_SPEED_THRESHOLD,
    FAIR_PAGE_SPEED_THRESHOLD,
    POOR_PAGE_SPEED_THRESHOLD,
    HIGH_QUALITY_THRESHOLD,
    MEDIUM_QUALITY_THRESHOLD,
    LOW_QUALITY_THRESHOLD,
)
from ..models.competitor_models import (
    CompetitorProfile,
    CompetitorMetrics,
    CompetitorAnalysis,
    CompetitorType,
    CompetitorSize,
    EngagementMetrics,
    SEOMetrics,
    ContentAnalysis,
    ContentType,
    PublishingFrequency,
)
from ..models.shared import ValidationError


def validate_competitor_url(url: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a competitor URL.
    
    Args:
        url: URL to validate
        
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    try:
        if not url or not isinstance(url, str):
            return False, "URL is required and must be a string"
        
        # Remove whitespace and check if empty
        url = url.strip()
        if not url:
            return False, "URL cannot be empty"
        
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Parse URL
        parsed = urlparse(url)
        if not parsed.netloc:
            return False, "Invalid URL format"
        
        # Check for valid domain
        domain = parsed.netloc.lower()
        if not re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', domain):
            return False, "Invalid domain format"
        
        # Check for common invalid patterns
        if domain.startswith(('localhost', '127.0.0.1', '192.168.', '10.')):
            return False, "Local or private IP addresses not allowed"
        
        return True, None
        
    except Exception as e:
        logger.error(f"Error validating URL {url}: {e}")
        return False, f"URL validation error: {str(e)}"


def normalize_competitor_urls(urls: List[str]) -> List[str]:
    """
    Normalize and validate a list of competitor URLs.
    
    Args:
        urls: List of URLs to normalize
        
    Returns:
        List[str]: List of normalized and valid URLs
    """
    normalized_urls = []
    
    for url in urls:
        is_valid, error = validate_competitor_url(url)
        if is_valid:
            # Normalize URL format
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            # Remove trailing slash
            url = url.rstrip('/')
            
            # Convert to lowercase
            url = url.lower()
            
            if url not in normalized_urls:  # Remove duplicates
                normalized_urls.append(url)
        else:
            logger.warning(f"Invalid URL skipped: {url} - {error}")
    
    return normalized_urls


def extract_domain_from_url(url: str) -> Optional[str]:
    """
    Extract domain from URL.
    
    Args:
        url: URL to extract domain from
        
    Returns:
        Optional[str]: Domain name or None if invalid
    """
    try:
        parsed = urlparse(url)
        return parsed.netloc.lower()
    except Exception as e:
        logger.error(f"Error extracting domain from {url}: {e}")
        return None


def categorize_competitor_size(employee_count: Optional[int] = None,
                             estimated_revenue: Optional[float] = None,
                             market_share: Optional[float] = None) -> CompetitorSize:
    """
    Categorize competitor size based on available metrics.
    
    Args:
        employee_count: Number of employees
        estimated_revenue: Estimated annual revenue
        market_share: Market share percentage
        
    Returns:
        CompetitorSize: Categorized size
    """
    try:
        # Prioritize employee count if available
        if employee_count:
            if employee_count >= 10000:
                return CompetitorSize.ENTERPRISE
            elif employee_count >= 1000:
                return CompetitorSize.LARGE
            elif employee_count >= 50:
                return CompetitorSize.MEDIUM
            elif employee_count >= 10:
                return CompetitorSize.SMALL
            else:
                return CompetitorSize.STARTUP
        
        # Use revenue as secondary metric
        if estimated_revenue:
            if estimated_revenue >= 1000000000:  # $1B+
                return CompetitorSize.ENTERPRISE
            elif estimated_revenue >= 100000000:  # $100M+
                return CompetitorSize.LARGE
            elif estimated_revenue >= 10000000:  # $10M+
                return CompetitorSize.MEDIUM
            elif estimated_revenue >= 1000000:  # $1M+
                return CompetitorSize.SMALL
            else:
                return CompetitorSize.STARTUP
        
        # Use market share as tertiary metric
        if market_share:
            if market_share >= 20.0:
                return CompetitorSize.ENTERPRISE
            elif market_share >= 10.0:
                return CompetitorSize.LARGE
            elif market_share >= 5.0:
                return CompetitorSize.MEDIUM
            elif market_share >= 1.0:
                return CompetitorSize.SMALL
            else:
                return CompetitorSize.STARTUP
        
        # Default to medium if no metrics available
        return CompetitorSize.MEDIUM
        
    except Exception as e:
        logger.error(f"Error categorizing competitor size: {e}")
        return CompetitorSize.MEDIUM


def determine_competitor_type(url: str, industry: str, target_keywords: List[str]) -> CompetitorType:
    """
    Determine competitor type based on URL, industry, and keywords.
    
    Args:
        url: Competitor URL
        industry: Industry category
        target_keywords: Target keywords
        
    Returns:
        CompetitorType: Determined competitor type
    """
    try:
        domain = extract_domain_from_url(url)
        if not domain:
            return CompetitorType.INDIRECT
        
        # Check for direct competitor indicators
        industry_keywords = [industry.lower(), f"{industry} solutions", f"{industry} services"]
        domain_lower = domain.lower()
        
        # Direct competitor: Same industry and similar keywords
        if any(keyword in domain_lower for keyword in industry_keywords):
            return CompetitorType.DIRECT
        
        # Check for keyword overlap
        if target_keywords:
            keyword_overlap = sum(1 for keyword in target_keywords if keyword.lower() in domain_lower)
            if keyword_overlap >= 2:
                return CompetitorType.DIRECT
            elif keyword_overlap == 1:
                return CompetitorType.INDIRECT
        
        # Substitute competitor: Similar target audience but different industry
        if any(term in domain_lower for term in ['alternative', 'vs', 'compare', 'review']):
            return CompetitorType.SUBSTITUTE
        
        # Default to indirect
        return CompetitorType.INDIRECT
        
    except Exception as e:
        logger.error(f"Error determining competitor type for {url}: {e}")
        return CompetitorType.INDIRECT


def calculate_competition_score(domain_authority: int,
                             content_count: int,
                             quality_score: float,
                             market_share: float = 0.0) -> float:
    """
    Calculate overall competition score based on multiple metrics.
    
    Args:
        domain_authority: Domain authority score (0-100)
        content_count: Number of content pieces
        quality_score: Average content quality score (0-10)
        market_share: Market share percentage
        
    Returns:
        float: Competition score (0-10)
    """
    try:
        # Normalize metrics to 0-1 scale
        da_score = domain_authority / 100.0
        
        # Normalize content count (logarithmic scale)
        content_score = min(1.0, (content_count / 1000.0) ** 0.5)
        
        # Normalize quality score
        quality_norm = quality_score / 10.0
        
        # Normalize market share
        market_score = min(1.0, market_share / 20.0)
        
        # Weighted average (adjust weights as needed)
        weights = {
            'domain_authority': 0.3,
            'content_volume': 0.2,
            'content_quality': 0.3,
            'market_share': 0.2
        }
        
        competition_score = (
            da_score * weights['domain_authority'] +
            content_score * weights['content_volume'] +
            quality_norm * weights['content_quality'] +
            market_score * weights['market_share']
        )
        
        return round(competition_score * 10, 2)  # Scale to 0-10
        
    except Exception as e:
        logger.error(f"Error calculating competition score: {e}")
        return 5.0  # Default to medium competition


def assess_domain_authority_tier(domain_authority: int) -> str:
    """
    Assess domain authority tier.
    
    Args:
        domain_authority: Domain authority score (0-100)
        
    Returns:
        str: Authority tier (high/medium/low)
    """
    try:
        if domain_authority >= HIGH_DOMAIN_AUTHORITY_THRESHOLD:
            return "high"
        elif domain_authority >= MEDIUM_DOMAIN_AUTHORITY_THRESHOLD:
            return "medium"
        else:
            return "low"
    except Exception as e:
        logger.error(f"Error assessing domain authority tier: {e}")
        return "medium"


def assess_page_speed_tier(page_speed: int) -> str:
    """
    Assess page speed tier.
    
    Args:
        page_speed: Page speed score (0-100)
        
    Returns:
        str: Speed tier (good/fair/poor)
    """
    try:
        if page_speed >= GOOD_PAGE_SPEED_THRESHOLD:
            return "good"
        elif page_speed >= FAIR_PAGE_SPEED_THRESHOLD:
            return "fair"
        else:
            return "poor"
    except Exception as e:
        logger.error(f"Error assessing page speed tier: {e}")
        return "fair"


def assess_content_quality_tier(quality_score: float) -> str:
    """
    Assess content quality tier.
    
    Args:
        quality_score: Content quality score (0-10)
        
    Returns:
        str: Quality tier (high/medium/low)
    """
    try:
        if quality_score >= HIGH_QUALITY_THRESHOLD:
            return "high"
        elif quality_score >= MEDIUM_QUALITY_THRESHOLD:
            return "medium"
        else:
            return "low"
    except Exception as e:
        logger.error(f"Error assessing content quality tier: {e}")
        return "medium"


def extract_competitor_insights(analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract key insights from competitor analysis.
    
    Args:
        analysis: Competitor analysis data
        
    Returns:
        Dict[str, Any]: Extracted insights
    """
    try:
        insights = {
            'strengths': [],
            'weaknesses': [],
            'opportunities': [],
            'threats': []
        }
        
        # Extract strengths
        if analysis.get('domain_authority', 0) >= HIGH_DOMAIN_AUTHORITY_THRESHOLD:
            insights['strengths'].append("High domain authority")
        
        if analysis.get('avg_quality_score', 0) >= HIGH_QUALITY_THRESHOLD:
            insights['strengths'].append("High content quality")
        
        if analysis.get('content_count', 0) >= 500:
            insights['strengths'].append("Large content volume")
        
        # Extract weaknesses
        if analysis.get('domain_authority', 0) < LOW_DOMAIN_AUTHORITY_THRESHOLD:
            insights['weaknesses'].append("Low domain authority")
        
        if analysis.get('avg_quality_score', 0) < LOW_QUALITY_THRESHOLD:
            insights['weaknesses'].append("Low content quality")
        
        if analysis.get('page_speed', 0) < POOR_PAGE_SPEED_THRESHOLD:
            insights['weaknesses'].append("Poor page speed")
        
        # Extract opportunities
        if analysis.get('mobile_friendly', False) == False:
            insights['opportunities'].append("Mobile optimization gap")
        
        if analysis.get('content_count', 0) < 100:
            insights['opportunities'].append("Content volume opportunity")
        
        # Extract threats
        if analysis.get('social_shares', 0) > 1000:
            insights['threats'].append("Strong social presence")
        
        if analysis.get('backlinks_count', 0) > 10000:
            insights['threats'].append("Extensive backlink profile")
        
        return insights
        
    except Exception as e:
        logger.error(f"Error extracting competitor insights: {e}")
        return {'strengths': [], 'weaknesses': [], 'opportunities': [], 'threats': []}


def create_competitor_profile(url: str,
                            name: Optional[str] = None,
                            industry: str = "",
                            description: Optional[str] = None,
                            **kwargs) -> CompetitorProfile:
    """
    Create a competitor profile from basic information.
    
    Args:
        url: Competitor URL
        name: Competitor name
        industry: Industry category
        description: Competitor description
        **kwargs: Additional profile information
        
    Returns:
        CompetitorProfile: Created competitor profile
    """
    try:
        domain = extract_domain_from_url(url)
        if not domain:
            raise ValueError(f"Invalid URL: {url}")
        
        # Generate name from domain if not provided
        if not name:
            name = domain.replace('www.', '').title()
        
        # Determine competitor type
        target_keywords = kwargs.get('target_keywords', [])
        competitor_type = determine_competitor_type(url, industry, target_keywords)
        
        # Categorize size
        employee_count = kwargs.get('employee_count')
        estimated_revenue = kwargs.get('estimated_revenue')
        market_share = kwargs.get('market_share', 0.0)
        competitor_size = categorize_competitor_size(employee_count, estimated_revenue, market_share)
        
        return CompetitorProfile(
            url=url,
            name=name,
            description=description,
            founded_year=kwargs.get('founded_year'),
            company_size=competitor_size,
            competitor_type=competitor_type,
            industry_focus=kwargs.get('industry_focus', [industry]),
            target_audience=kwargs.get('target_audience', []),
            unique_selling_proposition=kwargs.get('unique_selling_proposition'),
            market_position=kwargs.get('market_position'),
        )
        
    except Exception as e:
        logger.error(f"Error creating competitor profile: {e}")
        raise


def create_competitor_metrics(engagement_data: Dict[str, Any],
                           seo_data: Dict[str, Any],
                           content_data: Dict[str, Any],
                           **kwargs) -> CompetitorMetrics:
    """
    Create competitor metrics from analysis data.
    
    Args:
        engagement_data: Engagement metrics data
        seo_data: SEO metrics data
        content_data: Content analysis data
        **kwargs: Additional metrics
        
    Returns:
        CompetitorMetrics: Created competitor metrics
    """
    try:
        # Create engagement metrics
        engagement_metrics = EngagementMetrics(
            avg_time_on_page=engagement_data.get('avg_time_on_page', 180),
            bounce_rate=engagement_data.get('bounce_rate', 0.35),
            social_shares=engagement_data.get('social_shares', 45),
            comments_count=engagement_data.get('comments_count', 0),
            page_views=engagement_data.get('page_views', 0),
            unique_visitors=engagement_data.get('unique_visitors', 0),
            conversion_rate=engagement_data.get('conversion_rate', 0.0),
        )
        
        # Create SEO metrics
        seo_metrics = SEOMetrics(
            domain_authority=seo_data.get('domain_authority', 50),
            page_authority=seo_data.get('page_authority', 0),
            page_speed=seo_data.get('page_speed', 75),
            mobile_friendly=seo_data.get('mobile_friendly', True),
            ssl_certificate=seo_data.get('ssl_certificate', True),
            indexed_pages=seo_data.get('indexed_pages', 0),
            backlinks_count=seo_data.get('backlinks_count', 0),
            organic_traffic=seo_data.get('organic_traffic', 0),
            keyword_rankings=seo_data.get('keyword_rankings', 0),
        )
        
        # Create content analysis
        content_types = [ContentType(ct) for ct in content_data.get('content_types', ['blog'])]
        content_analysis = ContentAnalysis(
            content_count=content_data.get('content_count', 150),
            avg_quality_score=content_data.get('avg_quality_score', 5.0),
            top_keywords=content_data.get('top_keywords', []),
            content_types=content_types,
            publishing_frequency=PublishingFrequency(content_data.get('publishing_frequency', 'weekly')),
            avg_word_count=content_data.get('avg_word_count', 1000),
            content_depth_score=content_data.get('content_depth_score', 5.0),
            freshness_score=content_data.get('freshness_score', 5.0),
            topic_diversity=content_data.get('topic_diversity', 5.0),
        )
        
        return CompetitorMetrics(
            engagement_metrics=engagement_metrics,
            seo_metrics=seo_metrics,
            content_analysis=content_analysis,
            estimated_monthly_traffic=kwargs.get('estimated_monthly_traffic', 0),
            estimated_revenue=kwargs.get('estimated_revenue'),
            employee_count=kwargs.get('employee_count'),
            market_share_percentage=kwargs.get('market_share_percentage', 0.0),
            growth_rate=kwargs.get('growth_rate'),
            customer_satisfaction=kwargs.get('customer_satisfaction'),
        )
        
    except Exception as e:
        logger.error(f"Error creating competitor metrics: {e}")
        raise


def validate_competitor_data(data: Dict[str, Any]) -> List[ValidationError]:
    """
    Validate competitor analysis data.
    
    Args:
        data: Competitor data to validate
        
    Returns:
        List[ValidationError]: List of validation errors
    """
    errors = []
    
    try:
        # Validate required fields
        if 'url' not in data or not data['url']:
            errors.append(ValidationError(
                field='url',
                message='URL is required',
                value=data.get('url'),
                error_code='REQUIRED_FIELD'
            ))
        
        # Validate URL format
        if 'url' in data:
            is_valid, error_msg = validate_competitor_url(data['url'])
            if not is_valid:
                errors.append(ValidationError(
                    field='url',
                    message=error_msg,
                    value=data['url'],
                    error_code='INVALID_URL'
                ))
        
        # Validate numeric fields
        numeric_fields = {
            'domain_authority': (0, 100),
            'page_speed': (0, 100),
            'avg_quality_score': (0, 10),
            'content_count': (0, None),
            'bounce_rate': (0, 1),
            'social_shares': (0, None),
        }
        
        for field, (min_val, max_val) in numeric_fields.items():
            if field in data and data[field] is not None:
                try:
                    value = float(data[field])
                    if value < min_val:
                        errors.append(ValidationError(
                            field=field,
                            message=f'Value must be at least {min_val}',
                            value=value,
                            error_code='MIN_VALUE'
                        ))
                    elif max_val is not None and value > max_val:
                        errors.append(ValidationError(
                            field=field,
                            message=f'Value must be at most {max_val}',
                            value=value,
                            error_code='MAX_VALUE'
                        ))
                except (ValueError, TypeError):
                    errors.append(ValidationError(
                        field=field,
                        message='Must be a valid number',
                        value=data[field],
                        error_code='INVALID_NUMBER'
                    ))
        
        # Validate boolean fields
        boolean_fields = ['mobile_friendly', 'ssl_certificate']
        for field in boolean_fields:
            if field in data and data[field] is not None:
                if not isinstance(data[field], bool):
                    errors.append(ValidationError(
                        field=field,
                        message='Must be a boolean value',
                        value=data[field],
                        error_code='INVALID_BOOLEAN'
                    ))
        
    except Exception as e:
        logger.error(f"Error validating competitor data: {e}")
        errors.append(ValidationError(
            field='validation',
            message=f'Validation error: {str(e)}',
            value=data,
            error_code='VALIDATION_ERROR'
        ))
    
    return errors


def merge_competitor_analyses(analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Merge multiple competitor analyses into aggregated data.
    
    Args:
        analyses: List of competitor analyses
        
    Returns:
        Dict[str, Any]: Merged analysis data
    """
    try:
        if not analyses:
            return {}
        
        merged = {
            'total_competitors': len(analyses),
            'averages': {},
            'ranges': {},
            'top_performers': {},
            'common_elements': {},
        }
        
        # Calculate averages
        numeric_fields = [
            'domain_authority', 'page_speed', 'avg_quality_score',
            'content_count', 'bounce_rate', 'social_shares',
            'avg_time_on_page', 'backlinks_count'
        ]
        
        for field in numeric_fields:
            values = [analysis.get(field, 0) for analysis in analyses if analysis.get(field) is not None]
            if values:
                merged['averages'][field] = sum(values) / len(values)
                merged['ranges'][field] = {
                    'min': min(values),
                    'max': max(values),
                    'median': sorted(values)[len(values) // 2]
                }
        
        # Find top performers
        for field in numeric_fields:
            if field in merged['averages']:
                best_analysis = max(analyses, key=lambda x: x.get(field, 0))
                merged['top_performers'][field] = {
                    'url': best_analysis.get('url', ''),
                    'value': best_analysis.get(field, 0)
                }
        
        # Find common elements
        content_types = []
        for analysis in analyses:
            content_types.extend(analysis.get('content_types', []))
        
        if content_types:
            type_counter = Counter(content_types)
            merged['common_elements']['content_types'] = dict(type_counter.most_common())
        
        # Find common keywords
        all_keywords = []
        for analysis in analyses:
            all_keywords.extend(analysis.get('top_keywords', []))
        
        if all_keywords:
            keyword_counter = Counter(all_keywords)
            merged['common_elements']['top_keywords'] = dict(keyword_counter.most_common(10))
        
        return merged
        
    except Exception as e:
        logger.error(f"Error merging competitor analyses: {e}")
        return {}


def create_fallback_competitor_analysis(url: str) -> Dict[str, Any]:
    """
    Create fallback competitor analysis when real analysis fails.
    
    Args:
        url: Competitor URL
        
    Returns:
        Dict[str, Any]: Fallback analysis data
    """
    try:
        domain = extract_domain_from_url(url)
        if not domain:
            return {}
        
        # Use default values from constants
        fallback_data = DEFAULT_COMPETITOR_ANALYSIS.copy()
        fallback_data['url'] = url
        fallback_data['domain'] = domain
        fallback_data['analysis_source'] = 'fallback'
        fallback_data['confidence_score'] = 0.3  # Low confidence for fallback
        
        return fallback_data
        
    except Exception as e:
        logger.error(f"Error creating fallback analysis for {url}: {e}")
        return {}


def batch_process_urls(urls: List[str], batch_size: int = MAX_URLS_PER_BATCH) -> List[List[str]]:
    """
    Split URLs into batches for processing.
    
    Args:
        urls: List of URLs to batch
        batch_size: Size of each batch
        
    Returns:
        List[List[str]]: List of URL batches
    """
    try:
        batches = []
        for i in range(0, len(urls), batch_size):
            batch = urls[i:i + batch_size]
            if batch:  # Only add non-empty batches
                batches.append(batch)
        return batches
    except Exception as e:
        logger.error(f"Error batching URLs: {e}")
        return [urls]  # Return single batch if batching fails


def calculate_similarity_score(url1: str, url2: str, analysis1: Dict[str, Any], analysis2: Dict[str, Any]) -> float:
    """
    Calculate similarity score between two competitors.
    
    Args:
        url1: First competitor URL
        url2: Second competitor URL
        analysis1: First competitor analysis
        analysis2: Second competitor analysis
        
    Returns:
        float: Similarity score (0-1)
    """
    try:
        similarity_factors = []
        
        # Domain similarity
        domain1 = extract_domain_from_url(url1)
        domain2 = extract_domain_from_url(url2)
        if domain1 and domain2:
            # Check for common parts in domain
            domain_parts1 = set(domain1.split('.'))
            domain_parts2 = set(domain2.split('.'))
            domain_similarity = len(domain_parts1 & domain_parts2) / len(domain_parts1 | domain_parts2)
            similarity_factors.append(domain_similarity)
        
        # Content type similarity
        types1 = set(analysis1.get('content_types', []))
        types2 = set(analysis2.get('content_types', []))
        if types1 or types2:
            type_similarity = len(types1 & types2) / len(types1 | types2)
            similarity_factors.append(type_similarity)
        
        # Keyword similarity
        keywords1 = set(analysis1.get('top_keywords', []))
        keywords2 = set(analysis2.get('top_keywords', []))
        if keywords1 or keywords2:
            keyword_similarity = len(keywords1 & keywords2) / len(keywords1 | keywords2)
            similarity_factors.append(keyword_similarity)
        
        # Metric similarity (normalized difference)
        numeric_fields = ['domain_authority', 'content_count', 'avg_quality_score']
        for field in numeric_fields:
            val1 = analysis1.get(field, 0)
            val2 = analysis2.get(field, 0)
            if val1 > 0 or val2 > 0:
                max_val = max(val1, val2)
                if max_val > 0:
                    similarity = 1 - abs(val1 - val2) / max_val
                    similarity_factors.append(similarity)
        
        # Calculate overall similarity
        if similarity_factors:
            return sum(similarity_factors) / len(similarity_factors)
        else:
            return 0.0  # No similarity factors available
            
    except Exception as e:
        logger.error(f"Error calculating similarity score: {e}")
        return 0.0


def filter_competitors_by_criteria(competitors: List[Dict[str, Any]],
                                 min_domain_authority: int = 0,
                                 max_domain_authority: int = 100,
                                 content_types: Optional[List[str]] = None,
                                 competitor_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """
    Filter competitors based on specified criteria.
    
    Args:
        competitors: List of competitor analyses
        min_domain_authority: Minimum domain authority
        max_domain_authority: Maximum domain authority
        content_types: Required content types
        competitor_types: Required competitor types
        
    Returns:
        List[Dict[str, Any]]: Filtered competitors
    """
    try:
        filtered = []
        
        for competitor in competitors:
            # Filter by domain authority
            da = competitor.get('domain_authority', 0)
            if da < min_domain_authority or da > max_domain_authority:
                continue
            
            # Filter by content types
            if content_types:
                competitor_types_list = competitor.get('content_types', [])
                if not any(ct in competitor_types_list for ct in content_types):
                    continue
            
            # Filter by competitor types
            if competitor_types:
                comp_type = competitor.get('competitor_type', '')
                if comp_type not in competitor_types:
                    continue
            
            filtered.append(competitor)
        
        return filtered
        
    except Exception as e:
        logger.error(f"Error filtering competitors: {e}")
        return competitors  # Return original list if filtering fails
