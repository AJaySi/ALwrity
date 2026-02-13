"""
SEO Utilities for Competitor Analyzer Service

This module contains utility functions for SEO analysis,
gap identification, and SEO comparison across competitors.
"""

from typing import Dict, Any, List, Optional, Tuple, Set
from collections import Counter, defaultdict
import statistics
import re
from loguru import logger

from ..constants import (
    HIGH_DOMAIN_AUTHORITY_THRESHOLD,
    MEDIUM_DOMAIN_AUTHORITY_THRESHOLD,
    LOW_DOMAIN_AUTHORITY_THRESHOLD,
    GOOD_PAGE_SPEED_THRESHOLD,
    FAIR_PAGE_SPEED_THRESHOLD,
    POOR_PAGE_SPEED_THRESHOLD,
    OPTIMAL_TITLE_LENGTH,
    MAX_TITLE_LENGTH,
    MIN_TITLE_LENGTH,
    OPTIMAL_META_DESCRIPTION_LENGTH,
    MAX_META_DESCRIPTION_LENGTH,
    MIN_META_DESCRIPTION_LENGTH,
    DEFAULT_KEYWORD_DENSITY,
    OPTIMAL_KEYWORD_DENSITY_MIN,
    OPTIMAL_KEYWORD_DENSITY_MAX,
    DEFAULT_READABILITY_SCORE,
    HIGH_READABILITY_THRESHOLD,
    MEDIUM_READABILITY_THRESHOLD,
    LOW_READABILITY_THRESHOLD,
)
from ..models.seo_analysis import (
    SEOGapType,
    KeywordGap,
    TechnicalSEOGap,
    BacklinkGap,
    SEOComparison,
    SEOGap,
    SEORecommendation,
    PriorityLevel,
    ImpactLevel,
    KeywordDifficulty,
    SearchIntent,
    SEOMetric,
)
from ..models.shared import ValidationError


def analyze_seo_metrics(competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze SEO metrics across competitors.
    
    Args:
        competitors: List of competitor data
        
    Returns:
        Dict[str, Any]: SEO metrics analysis
    """
    try:
        seo_analysis = {
            'domain_authority': {},
            'page_authority': {},
            'page_speed': {},
            'mobile_friendly': {},
            'ssl_certificate': {},
            'indexed_pages': {},
            'backlinks_count': {},
            'organic_traffic': {},
            'keyword_rankings': {},
            'technical_seo': {},
            'onpage_seo': {},
            'seo_scores': {}
        }
        
        # Collect all metrics
        all_da = []
        all_pa = []
        all_speed = []
        all_backlinks = []
        all_traffic = []
        all_rankings = []
        
        for competitor in competitors:
            url = competitor.get('url', '')
            seo_metrics = competitor.get('seo_metrics', {})
            
            # Domain Authority
            da = seo_metrics.get('domain_authority', 50)
            seo_analysis['domain_authority'][url] = da
            all_da.append(da)
            
            # Page Authority
            pa = seo_metrics.get('page_authority', 0)
            seo_analysis['page_authority'][url] = pa
            all_pa.append(pa)
            
            # Page Speed
            speed = seo_metrics.get('page_speed', 75)
            seo_analysis['page_speed'][url] = speed
            all_speed.append(speed)
            
            # Mobile Friendly
            mobile = seo_metrics.get('mobile_friendly', True)
            seo_analysis['mobile_friendly'][url] = mobile
            
            # SSL Certificate
            ssl = seo_metrics.get('ssl_certificate', True)
            seo_analysis['ssl_certificate'][url] = ssl
            
            # Indexed Pages
            indexed = seo_metrics.get('indexed_pages', 0)
            seo_analysis['indexed_pages'][url] = indexed
            
            # Backlinks
            backlinks = seo_metrics.get('backlinks_count', 0)
            seo_analysis['backlinks_count'][url] = backlinks
            all_backlinks.append(backlinks)
            
            # Organic Traffic
            traffic = seo_metrics.get('organic_traffic', 0)
            seo_analysis['organic_traffic'][url] = traffic
            all_traffic.append(traffic)
            
            # Keyword Rankings
            rankings = seo_metrics.get('keyword_rankings', 0)
            seo_analysis['keyword_rankings'][url] = rankings
            all_rankings.append(rankings)
            
            # Calculate overall SEO score
            seo_score = calculate_seo_score(seo_metrics)
            seo_analysis['seo_scores'][url] = seo_score
        
        # Calculate statistics
        if all_da:
            seo_analysis['statistics'] = {
                'domain_authority': {
                    'average': statistics.mean(all_da),
                    'median': statistics.median(all_da),
                    'min': min(all_da),
                    'max': max(all_da)
                },
                'page_speed': {
                    'average': statistics.mean(all_speed),
                    'median': statistics.median(all_speed),
                    'min': min(all_speed),
                    'max': max(all_speed)
                },
                'backlinks_count': {
                    'average': statistics.mean(all_backlinks),
                    'median': statistics.median(all_backlinks),
                    'min': min(all_backlinks),
                    'max': max(all_backlinks)
                },
                'organic_traffic': {
                    'average': statistics.mean(all_traffic),
                    'median': statistics.median(all_traffic),
                    'min': min(all_traffic),
                    'max': max(all_traffic)
                }
            }
        
        # Identify SEO leaders
        seo_analysis['leaders'] = {
            'domain_authority': max(seo_analysis['domain_authority'].items(), key=lambda x: x[1])[0],
            'page_speed': max(seo_analysis['page_speed'].items(), key=lambda x: x[1])[0],
            'backlinks': max(seo_analysis['backlinks_count'].items(), key=lambda x: x[1])[0],
            'organic_traffic': max(seo_analysis['organic_traffic'].items(), key=lambda x: x[1])[0],
            'overall_seo': max(seo_analysis['seo_scores'].items(), key=lambda x: x[1])[0]
        }
        
        return seo_analysis
        
    except Exception as e:
        logger.error(f"Error analyzing SEO metrics: {e}")
        return {}


def calculate_seo_score(seo_metrics: Dict[str, Any]) -> float:
    """
    Calculate overall SEO score based on multiple metrics.
    
    Args:
        seo_metrics: SEO metrics dictionary
        
    Returns:
        float: SEO score (0-10)
    """
    try:
        score = 0.0
        
        # Domain Authority (0-2 points)
        da = seo_metrics.get('domain_authority', 50)
        if da >= HIGH_DOMAIN_AUTHORITY_THRESHOLD:
            score += 2.0
        elif da >= MEDIUM_DOMAIN_AUTHORITY_THRESHOLD:
            score += 1.5
        elif da >= LOW_DOMAIN_AUTHORITY_THRESHOLD:
            score += 1.0
        else:
            score += 0.5
        
        # Page Speed (0-2 points)
        speed = seo_metrics.get('page_speed', 75)
        if speed >= GOOD_PAGE_SPEED_THRESHOLD:
            score += 2.0
        elif speed >= FAIR_PAGE_SPEED_THRESHOLD:
            score += 1.5
        elif speed >= POOR_PAGE_SPEED_THRESHOLD:
            score += 1.0
        else:
            score += 0.5
        
        # Mobile Friendly (0-1 point)
        if seo_metrics.get('mobile_friendly', False):
            score += 1.0
        
        # SSL Certificate (0-1 point)
        if seo_metrics.get('ssl_certificate', False):
            score += 1.0
        
        # Backlinks (0-2 points)
        backlinks = seo_metrics.get('backlinks_count', 0)
        if backlinks >= 10000:
            score += 2.0
        elif backlinks >= 1000:
            score += 1.5
        elif backlinks >= 100:
            score += 1.0
        else:
            score += 0.5
        
        # Indexed Pages (0-1 point)
        indexed = seo_metrics.get('indexed_pages', 0)
        if indexed >= 1000:
            score += 1.0
        elif indexed >= 100:
            score += 0.5
        
        # Organic Traffic (0-1 point)
        traffic = seo_metrics.get('organic_traffic', 0)
        if traffic >= 100000:
            score += 1.0
        elif traffic >= 10000:
            score += 0.5
        
        return min(10.0, score)
        
    except Exception as e:
        logger.error(f"Error calculating SEO score: {e}")
        return 5.0


def analyze_keyword_gaps(competitors: List[Dict[str, Any]], 
                       target_keywords: List[str]) -> List[KeywordGap]:
    """
    Analyze keyword gaps across competitors.
    
    Args:
        competitors: List of competitor data
        target_keywords: List of target keywords
        
    Returns:
        List[KeywordGap]: List of keyword gaps
    """
    try:
        keyword_gaps = []
        
        # Analyze each target keyword
        for keyword in target_keywords:
            # Collect competitor rankings for this keyword
            competitor_rankings = {}
            search_volume = estimate_search_volume(keyword)
            keyword_difficulty = estimate_keyword_difficulty(keyword)
            search_intent = determine_search_intent(keyword)
            
            for competitor in competitors:
                url = competitor.get('url', '')
                keyword_rankings = competitor.get('keyword_rankings', {})
                
                # Get ranking for this keyword (simplified)
                ranking = keyword_rankings.get(keyword, 0)  # 0 means not ranking
                if ranking == 0:
                    # Estimate ranking based on domain authority and content relevance
                    da = competitor.get('seo_metrics', {}).get('domain_authority', 50)
                    has_keyword_content = keyword.lower() in ' '.join(competitor.get('top_keywords', [])).lower()
                    
                    if has_keyword_content:
                        ranking = max(1, int(100 - da))  # Rough estimate
                    else:
                        ranking = 0
                
                competitor_rankings[url] = ranking
            
            # Calculate gap opportunity
            your_ranking = competitor_rankings.get('your_site', 0)  # Would be actual data
            gap_opportunity = calculate_keyword_gap_opportunity(
                competitor_rankings, your_ranking, search_volume
            )
            
            # Estimate traffic potential
            traffic_potential = estimate_keyword_traffic_potential(search_volume, your_ranking)
            
            # Determine content difficulty
            content_difficulty = estimate_content_difficulty(keyword_difficulty)
            
            # Get competition level
            competition_level = determine_keyword_competition_level(competitor_rankings)
            
            # Get trend direction
            trend_direction = estimate_keyword_trend(keyword)
            
            # Generate content suggestions
            content_suggestions = generate_keyword_content_suggestions(keyword, search_intent)
            
            # Determine priority
            priority = calculate_keyword_priority(
                gap_opportunity, competition_level, content_difficulty
            )
            
            keyword_gap = KeywordGap(
                keyword=keyword,
                search_volume=search_volume,
                keyword_difficulty=keyword_difficulty,
                search_intent=search_intent,
                competitor_rankings=competitor_rankings,
                your_ranking=your_ranking if your_ranking > 0 else None,
                gap_opportunity=gap_opportunity,
                estimated_traffic_potential=traffic_potential,
                content_difficulty=content_difficulty,
                competition_level=competition_level,
                trend_direction=trend_direction,
                seasonal_pattern=estimate_seasonal_pattern(keyword),
                related_keywords=get_related_keywords(keyword),
                content_suggestions=content_suggestions,
                priority=priority,
            )
            
            keyword_gaps.append(keyword_gap)
        
        # Sort by opportunity score
        keyword_gaps.sort(key=lambda x: x.gap_opportunity, reverse=True)
        
        return keyword_gaps
        
    except Exception as e:
        logger.error(f"Error analyzing keyword gaps: {e}")
        return []


def estimate_search_volume(keyword: str) -> int:
    """
    Estimate search volume for a keyword.
    
    Args:
        keyword: Keyword to estimate volume for
        
    Returns:
        int: Estimated monthly search volume
    """
    try:
        # Simplified estimation based on keyword characteristics
        keyword_lower = keyword.lower()
        
        # High volume indicators
        if any(term in keyword_lower for term in ['how to', 'what is', 'best', 'top', 'review']):
            base_volume = 10000
        # Medium volume indicators
        elif any(term in keyword_lower for term in ['guide', 'tutorial', 'example', 'tips']):
            base_volume = 5000
        # Low volume indicators
        elif any(term in keyword_lower for term in ['advanced', 'expert', 'technical']):
            base_volume = 1000
        else:
            base_volume = 3000
        
        # Adjust for keyword length
        length_factor = max(0.5, 1.0 - (len(keyword.split()) - 2) * 0.1)
        
        return int(base_volume * length_factor)
        
    except Exception as e:
        logger.error(f"Error estimating search volume for {keyword}: {e}")
        return 1000


def estimate_keyword_difficulty(keyword: str) -> KeywordDifficulty:
    """
    Estimate keyword difficulty.
    
    Args:
        keyword: Keyword to estimate difficulty for
        
    Returns:
        KeywordDifficulty: Estimated difficulty
    """
    try:
        keyword_lower = keyword.lower()
        
        # High difficulty indicators
        if any(term in keyword_lower for term in ['insurance', 'loan', 'lawyer', 'software', 'technology']):
            return KeywordDifficulty.VERY_DIFFICULT
        
        # Medium-high difficulty indicators
        elif any(term in keyword_lower for term in ['marketing', 'business', 'finance', 'health']):
            return KeywordDifficulty.DIFFICULT
        
        # Medium difficulty indicators
        elif any(term in keyword_lower for term in ['guide', 'tutorial', 'best', 'top']):
            return KeywordDifficulty.MODERATE
        
        # Low difficulty indicators
        elif any(term in keyword_lower for term in ['tips', 'tricks', 'simple', 'basic']):
            return KeywordDifficulty.EASY
        
        # Very low difficulty indicators
        elif any(term in keyword_lower for term in ['niche', 'specific', 'detailed']):
            return KeywordDifficulty.VERY_EASY
        
        else:
            return KeywordDifficulty.MODERATE
        
    except Exception as e:
        logger.error(f"Error estimating keyword difficulty for {keyword}: {e}")
        return KeywordDifficulty.MODERATE


def determine_search_intent(keyword: str) -> SearchIntent:
    """
    Determine search intent for a keyword.
    
    Args:
        keyword: Keyword to analyze
        
    Returns:
        SearchIntent: Determined search intent
    """
    try:
        keyword_lower = keyword.lower()
        
        # Informational intent
        if any(term in keyword_lower for term in ['what', 'how', 'why', 'when', 'where', 'guide', 'tutorial']):
            return SearchIntent.INFORMATIONAL
        
        # Commercial intent
        elif any(term in keyword_lower for term in ['best', 'top', 'review', 'comparison', 'vs']):
            return SearchIntent.COMMERCIAL
        
        # Transactional intent
        elif any(term in keyword_lower for term in ['buy', 'price', 'cost', 'deal', 'discount', 'shop']):
            return SearchIntent.TRANSACTIONAL
        
        # Navigational intent
        elif any(term in keyword_lower for term in ['login', 'signin', 'account', 'official']):
            return SearchIntent.NAVIGATIONAL
        
        else:
            return SearchIntent.INFORMATIONAL
        
    except Exception as e:
        logger.error(f"Error determining search intent for {keyword}: {e}")
        return SearchIntent.INFORMATIONAL


def calculate_keyword_gap_opportunity(competitor_rankings: Dict[str, int],
                                   your_ranking: Optional[int],
                                   search_volume: int) -> float:
    """
    Calculate keyword gap opportunity score.
    
    Args:
        competitor_rankings: Competitor rankings for keyword
        your_ranking: Your ranking for keyword
        search_volume: Search volume for keyword
        
    Returns:
        float: Opportunity score (0-10)
    """
    try:
        opportunity_score = 0.0
        
        # Factor 1: Search volume (0-3 points)
        if search_volume >= 10000:
            opportunity_score += 3.0
        elif search_volume >= 5000:
            opportunity_score += 2.0
        elif search_volume >= 1000:
            opportunity_score += 1.0
        
        # Factor 2: Competition gap (0-4 points)
        if your_ranking and your_ranking > 0:
            # If you're ranking, opportunity is lower
            if your_ranking <= 10:
                opportunity_score += 0.5
            elif your_ranking <= 20:
                opportunity_score += 1.0
            elif your_ranking <= 50:
                opportunity_score += 2.0
            else:
                opportunity_score += 3.0
        else:
            # If you're not ranking, higher opportunity
            opportunity_score += 4.0
        
        # Factor 3: Competitor weakness (0-3 points)
        high_ranking_competitors = [r for r in competitor_rankings.values() if r <= 10]
        if len(high_ranking_competitors) == 0:
            opportunity_score += 3.0
        elif len(high_ranking_competitors) <= 2:
            opportunity_score += 2.0
        elif len(high_ranking_competitors) <= 5:
            opportunity_score += 1.0
        
        return min(10.0, opportunity_score)
        
    except Exception as e:
        logger.error(f"Error calculating keyword gap opportunity: {e}")
        return 5.0


def estimate_keyword_traffic_potential(search_volume: int, ranking: int) -> int:
    """
    Estimate traffic potential based on search volume and ranking.
    
    Args:
        search_volume: Monthly search volume
        ranking: Search engine ranking
        
    Returns:
        int: Estimated monthly traffic
    """
    try:
        # Click-through rate by position
        ctr_by_position = {
            1: 0.30,  # 30%
            2: 0.15,  # 15%
            3: 0.10,  # 10%
            4: 0.08,  # 8%
            5: 0.06,  # 6%
            6: 0.05,  # 5%
            7: 0.04,  # 4%
            8: 0.03,  # 3%
            9: 0.02,  # 2%
            10: 0.02, # 2%
        }
        
        if ranking <= 10:
            ctr = ctr_by_position.get(ranking, 0.02)
        else:
            ctr = 0.01  # 1% for positions beyond 10
        
        return int(search_volume * ctr)
        
    except Exception as e:
        logger.error(f"Error estimating keyword traffic potential: {e}")
        return 0


def estimate_content_difficulty(keyword_difficulty: KeywordDifficulty) -> float:
    """
    Estimate content creation difficulty based on keyword difficulty.
    
    Args:
        keyword_difficulty: Keyword difficulty level
        
    Returns:
        float: Content difficulty score (0-10)
    """
    try:
        difficulty_map = {
            KeywordDifficulty.VERY_EASY: 2.0,
            KeywordDifficulty.EASY: 3.0,
            KeywordDifficulty.MODERATE: 5.0,
            KeywordDifficulty.DIFFICULT: 7.0,
            KeywordDifficulty.VERY_DIFFICULT: 9.0,
        }
        
        return difficulty_map.get(keyword_difficulty, 5.0)
        
    except Exception as e:
        logger.error(f"Error estimating content difficulty: {e}")
        return 5.0


def determine_keyword_competition_level(competitor_rankings: Dict[str, int]) -> str:
    """
    Determine competition level for a keyword.
    
    Args:
        competitor_rankings: Competitor rankings
        
    Returns:
        str: Competition level
    """
    try:
        # Count competitors in top 10
        top_10_competitors = len([r for r in competitor_rankings.values() if 1 <= r <= 10])
        total_competitors = len(competitor_rankings)
        
        if top_10_competitors >= total_competitors * 0.8:
            return "high"
        elif top_10_competitors >= total_competitors * 0.5:
            return "medium"
        else:
            return "low"
        
    except Exception as e:
        logger.error(f"Error determining keyword competition level: {e}")
        return "medium"


def estimate_keyword_trend(keyword: str) -> str:
    """
    Estimate keyword trend direction.
    
    Args:
        keyword: Keyword to analyze
        
    Returns:
        str: Trend direction
    """
    try:
        keyword_lower = keyword.lower()
        
        # Growing trends
        if any(term in keyword_lower for term in ['ai', 'machine learning', 'sustainability', 'remote work']):
            return "growing"
        
        # Declining trends
        elif any(term in keyword_lower for term in ['flash', 'obsolete', 'deprecated']):
            return "declining"
        
        # Stable trends
        else:
            return "stable"
        
    except Exception as e:
        logger.error(f"Error estimating keyword trend: {e}")
        return "stable"


def estimate_seasonal_pattern(keyword: str) -> Optional[str]:
    """
    Estimate seasonal pattern for a keyword.
    
    Args:
        keyword: Keyword to analyze
        
    Returns:
        Optional[str]: Seasonal pattern
    """
    try:
        keyword_lower = keyword.lower()
        
        # Seasonal patterns
        if any(term in keyword_lower for term in ['christmas', 'holiday', 'summer', 'winter', 'fall', 'spring']):
            return "high"
        elif any(term in keyword_lower for term in ['black friday', 'cyber monday', 'prime day']):
            return "very_high"
        elif any(term in keyword_lower for term in ['evergreen', 'general', 'basic']):
            return "none"
        else:
            return "moderate"
        
    except Exception as e:
        logger.error(f"Error estimating seasonal pattern: {e}")
        return "moderate"


def get_related_keywords(keyword: str) -> List[str]:
    """
    Get related keywords for a keyword.
    
    Args:
        keyword: Base keyword
        
    Returns:
        List[str]: Related keywords
    """
    try:
        keyword_lower = keyword.lower()
        
        # Simple related keyword generation
        related = []
        
        # Add variations
        if 'how to' in keyword_lower:
            related.append(keyword.replace('how to', 'guide to'))
            related.append(keyword.replace('how to', 'tutorial on'))
        
        # Add synonyms
        synonyms = {
            'guide': 'tutorial',
            'tutorial': 'guide',
            'best': 'top',
            'top': 'best',
            'tips': 'tricks',
            'tricks': 'tips',
        }
        
        for word, synonym in synonyms.items():
            if word in keyword_lower:
                related.append(keyword.replace(word, synonym))
        
        # Add long-tail variations
        if len(keyword.split()) <= 2:
            related.append(f"{keyword} for beginners")
            related.append(f"advanced {keyword}")
        
        return list(set(related))[:5]  # Return up to 5 unique related keywords
        
    except Exception as e:
        logger.error(f"Error getting related keywords: {e}")
        return []


def generate_keyword_content_suggestions(keyword: str, search_intent: SearchIntent) -> List[str]:
    """
    Generate content suggestions for a keyword.
    
    Args:
        keyword: Target keyword
        search_intent: Search intent
        
    Returns:
        List[str]: Content suggestions
    """
    try:
        suggestions = []
        
        if search_intent == SearchIntent.INFORMATIONAL:
            suggestions = [
                f"Comprehensive guide to {keyword}",
                f"What is {keyword} and how it works",
                f"{keyword} explained for beginners",
                f"Everything you need to know about {keyword}"
            ]
        elif search_intent == SearchIntent.COMMERCIAL:
            suggestions = [
                f"Best {keyword} options available",
                f"{keyword} comparison and review",
                f"Top {keyword} choices for [year]",
                f"{keyword} buying guide"
            ]
        elif search_intent == SearchIntent.TRANSACTIONAL:
            suggestions = [
                f"Where to buy {keyword}",
                f"{keyword} pricing and deals",
                f"How to purchase {keyword}",
                f"{keyword} purchase guide"
            ]
        else:  # Navigational
            suggestions = [
                f"Official {keyword} website",
                f"How to access {keyword}",
                f"{keyword} login guide",
                f"{keyword} account setup"
            ]
        
        return suggestions[:3]  # Return top 3 suggestions
        
    except Exception as e:
        logger.error(f"Error generating keyword content suggestions: {e}")
        return [f"Create content about {keyword}"]


def calculate_keyword_priority(gap_opportunity: float,
                             competition_level: str,
                             content_difficulty: float) -> PriorityLevel:
    """
    Calculate priority level for a keyword gap.
    
    Args:
        gap_opportunity: Opportunity score (0-10)
        competition_level: Competition level
        content_difficulty: Content difficulty score (0-10)
        
    Returns:
        PriorityLevel: Priority level
    """
    try:
        # Base score from opportunity
        base_score = gap_opportunity
        
        # Adjust for competition
        competition_multiplier = {
            "low": 1.5,
            "medium": 1.0,
            "high": 0.7,
        }
        
        adjusted_score = base_score * competition_multiplier.get(competition_level, 1.0)
        
        # Adjust for difficulty (inverse)
        difficulty_penalty = max(0, (content_difficulty - 5) * 0.2)
        final_score = adjusted_score - difficulty_penalty
        
        # Determine priority
        if final_score >= 8.0:
            return PriorityLevel.HIGH
        elif final_score >= 5.0:
            return PriorityLevel.MEDIUM
        else:
            return PriorityLevel.LOW
        
    except Exception as e:
        logger.error(f"Error calculating keyword priority: {e}")
        return PriorityLevel.MEDIUM


def analyze_technical_seo_gaps(competitors: List[Dict[str, Any]]) -> List[TechnicalSEOGap]:
    """
    Analyze technical SEO gaps across competitors.
    
    Args:
        competitors: List of competitor data
        
    Returns:
        List[TechnicalSEOGap]: List of technical SEO gaps
    """
    try:
        technical_gaps = []
        
        # Analyze common technical SEO issues
        technical_checks = {
            'mobile_friendly': {
                'description': 'Mobile optimization',
                'ideal_status': 'mobile_friendly',
                'current_status': 'not_mobile_friendly',
                'fix_complexity': PriorityLevel.MEDIUM,
                'estimated_fix_time': '1-2 weeks'
            },
            'ssl_certificate': {
                'description': 'SSL certificate implementation',
                'ideal_status': 'https_enabled',
                'current_status': 'http_only',
                'fix_complexity': PriorityLevel.LOW,
                'estimated_fix_time': '1-3 days'
            },
            'page_speed': {
                'description': 'Page speed optimization',
                'ideal_status': 'fast_loading',
                'current_status': 'slow_loading',
                'fix_complexity': PriorityLevel.HIGH,
                'estimated_fix_time': '2-4 weeks'
            },
            'structured_data': {
                'description': 'Structured data implementation',
                'ideal_status': 'schema_implemented',
                'current_status': 'no_schema',
                'fix_complexity': PriorityLevel.MEDIUM,
                'estimated_fix_time': '1-2 weeks'
            }
        }
        
        for check_type, check_info in technical_checks.items():
            # Analyze current status across competitors
            current_status = {}
            for competitor in competitors:
                url = competitor.get('url', '')
                seo_metrics = competitor.get('seo_metrics', {})
                
                if check_type == 'mobile_friendly':
                    status = 'mobile_friendly' if seo_metrics.get('mobile_friendly', False) else 'not_mobile_friendly'
                elif check_type == 'ssl_certificate':
                    status = 'https_enabled' if seo_metrics.get('ssl_certificate', False) else 'http_only'
                elif check_type == 'page_speed':
                    speed = seo_metrics.get('page_speed', 75)
                    status = 'fast_loading' if speed >= GOOD_PAGE_SPEED_THRESHOLD else 'slow_loading'
                elif check_type == 'structured_data':
                    status = 'schema_implemented' if seo_metrics.get('structured_data', False) else 'no_schema'
                else:
                    status = 'unknown'
                
                current_status[url] = status
            
            # Determine if there's a gap
            ideal_count = sum(1 for status in current_status.values() if status == check_info['ideal_status'])
            total_count = len(current_status)
            
            if ideal_count < total_count:  # Not all competitors have ideal status
                gap_percentage = ((total_count - ideal_count) / total_count) * 100
                
                # Determine severity
                if gap_percentage >= 70:
                    severity = PriorityLevel.HIGH
                elif gap_percentage >= 40:
                    severity = PriorityLevel.MEDIUM
                else:
                    severity = PriorityLevel.LOW
                
                # Determine impact
                if check_type in ['mobile_friendly', 'page_speed']:
                    impact = ImpactLevel.HIGH
                elif check_type in ['ssl_certificate', 'structured_data']:
                    impact = ImpactLevel.MEDIUM
                else:
                    impact = ImpactLevel.LOW
                
                technical_gap = TechnicalSEOGap(
                    gap_type=SEOGapType.TECHNICAL_SEO_GAP,
                    issue_description=check_info['description'],
                    severity=severity,
                    impact_level=impact,
                    current_status=current_status,
                    ideal_status=check_info['ideal_status'],
                    competitor_performance=current_status,
                    fix_complexity=check_info['fix_complexity'],
                    estimated_fix_time=check_info['estimated_fix_time'],
                    technical_requirements=get_technical_requirements(check_type),
                    tools_needed=get_seo_tools_for_gap(check_type),
                    expected_improvement=get_expected_improvement(check_type),
                    implementation_steps=get_implementation_steps(check_type),
                    monitoring_metrics=get_monitoring_metrics(check_type),
                )
                
                technical_gaps.append(technical_gap)
        
        return technical_gaps
        
    except Exception as e:
        logger.error(f"Error analyzing technical SEO gaps: {e}")
        return []


def get_technical_requirements(check_type: str) -> List[str]:
    """Get technical requirements for a technical SEO check."""
    requirements_map = {
        'mobile_friendly': ['Responsive design', 'Mobile-optimized content', 'Touch-friendly navigation'],
        'ssl_certificate': ['SSL certificate', 'HTTPS configuration', 'Security headers'],
        'page_speed': ['Image optimization', 'Code minification', 'CDN implementation'],
        'structured_data': ['Schema markup', 'JSON-LD implementation', 'Testing tools']
    }
    return requirements_map.get(check_type, ['Technical implementation'])


def get_seo_tools_for_gap(check_type: str) -> List[str]:
    """Get SEO tools needed for a technical SEO gap."""
    tools_map = {
        'mobile_friendly': ['Google Mobile-Friendly Test', 'BrowserStack', 'Responsive Design Checker'],
        'ssl_certificate': ['SSL Checker', 'Let\'s Encrypt', 'SSL Labs'],
        'page_speed': ['Google PageSpeed Insights', 'GTmetrix', 'WebPageTest'],
        'structured_data': ['Google Rich Results Test', 'Schema.org Validator', 'JSON-LD Playground']
    }
    return tools_map.get(check_type, ['SEO tools'])


def get_expected_improvement(check_type: str) -> str:
    """Get expected improvement for a technical SEO fix."""
    improvement_map = {
        'mobile_friendly': 'Improved mobile rankings and user experience',
        'ssl_certificate': 'Better security and slight ranking boost',
        'page_speed': 'Improved user experience and rankings',
        'structured_data': 'Enhanced search result appearance and CTR'
    }
    return improvement_map.get(check_type, 'SEO improvement')


def get_implementation_steps(check_type: str) -> List[str]:
    """Get implementation steps for a technical SEO fix."""
    steps_map = {
        'mobile_friendly': ['Audit mobile experience', 'Implement responsive design', 'Test on multiple devices'],
        'ssl_certificate': ['Purchase SSL certificate', 'Install certificate', 'Update internal links'],
        'page_speed': ['Analyze performance bottlenecks', 'Optimize images and code', 'Implement caching'],
        'structured_data': ['Identify schema opportunities', 'Implement markup', 'Test and validate']
    }
    return steps_map.get(check_type, ['Implement fix'])


def get_monitoring_metrics(check_type: str) -> List[str]:
    """Get monitoring metrics for a technical SEO fix."""
    metrics_map = {
        'mobile_friendly': ['Mobile traffic percentage', 'Mobile bounce rate', 'Mobile conversion rate'],
        'ssl_certificate': ['Security certificate status', 'HTTPS adoption rate'],
        'page_speed': ['Page load time', 'Time to first byte', 'Core Web Vitals'],
        'structured_data': ['Rich result impressions', 'Click-through rate', 'Schema validation status']
    }
    return metrics_map.get(check_type, ['Performance metrics'])


def validate_seo_data(data: Dict[str, Any]) -> List[ValidationError]:
    """
    Validate SEO analysis data.
    
    Args:
        data: SEO data to validate
        
    Returns:
        List[ValidationError]: List of validation errors
    """
    errors = []
    
    try:
        # Validate domain authority
        da = data.get('domain_authority')
        if da is not None and (not isinstance(da, (int, float)) or da < 0 or da > 100):
            errors.append(ValidationError(
                field='domain_authority',
                message='Domain authority must be between 0 and 100',
                value=da,
                error_code='INVALID_DOMAIN_AUTHORITY'
            ))
        
        # Validate page speed
        speed = data.get('page_speed')
        if speed is not None and (not isinstance(speed, (int, float)) or speed < 0 or speed > 100):
            errors.append(ValidationError(
                field='page_speed',
                message='Page speed must be between 0 and 100',
                value=speed,
                error_code='INVALID_PAGE_SPEED'
            ))
        
        # Validate keyword rankings
        rankings = data.get('keyword_rankings')
        if rankings is not None:
            if not isinstance(rankings, (int, float)) or rankings < 0:
                errors.append(ValidationError(
                    field='keyword_rankings',
                    message='Keyword rankings must be a non-negative number',
                    value=rankings,
                    error_code='INVALID_KEYWORD_RANKINGS'
                ))
        
        # Validate boolean fields
        boolean_fields = ['mobile_friendly', 'ssl_certificate', 'structured_data']
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
        logger.error(f"Error validating SEO data: {e}")
        errors.append(ValidationError(
            field='validation',
            message=f'Validation error: {str(e)}',
            value=data,
            error_code='VALIDATION_ERROR'
        ))
    
    return errors
