"""
Market Utilities for Competitor Analyzer Service

This module contains utility functions for market analysis,
positioning, share calculations, and competitive landscape analysis.
"""

from typing import Dict, Any, List, Optional, Tuple
from collections import Counter, defaultdict
import statistics
from loguru import logger

from ..constants import (
    HIGH_MARKET_SHARE_THRESHOLD,
    MEDIUM_MARKET_SHARE_THRESHOLD,
    LOW_MARKET_SHARE_THRESHOLD,
    HIGH_GROWTH_RATE_THRESHOLD,
    MEDIUM_GROWTH_RATE_THRESHOLD,
    LOW_GROWTH_RATE_THRESHOLD,
)
from ..models.market_analysis import (
    MarketPosition,
    CompetitiveIntensity,
    MarketShare,
    MarketPositioning,
    CompetitiveLandscape,
    MarketSegment,
    MarketOpportunity,
    MarketTrend,
)
from ..models.shared import ValidationError


def calculate_market_share(values: List[float], total_market_size: float) -> List[MarketShare]:
    """
    Calculate market share for multiple competitors.
    
    Args:
        values: List of competitor values (revenue, traffic, etc.)
        total_market_size: Total market size
        
    Returns:
        List[MarketShare]: Market share data for each competitor
    """
    try:
        if total_market_size <= 0:
            raise ValueError("Total market size must be greater than 0")
        
        market_shares = []
        
        for i, value in enumerate(values):
            if value < 0:
                logger.warning(f"Negative value detected for competitor {i}: {value}")
                continue
            
            share_percentage = (value / total_market_size) * 100
            
            market_shares.append(MarketShare(
                competitor_url=f"competitor_{i+1}.com",
                competitor_name=f"Competitor {i+1}",
                share_type="revenue",  # Default to revenue
                share_percentage=share_percentage,
                share_value=value,
                period="current",
                data_source="analysis",
                confidence_level=0.8,
            ))
        
        return market_shares
        
    except Exception as e:
        logger.error(f"Error calculating market share: {e}")
        return []


def determine_market_position(market_share_percentage: float,
                            quality_score: float,
                            growth_rate: float = 0.0) -> MarketPosition:
    """
    Determine market position based on share, quality, and growth.
    
    Args:
        market_share_percentage: Market share percentage
        quality_score: Quality score (0-10)
        growth_rate: Growth rate percentage
        
    Returns:
        MarketPosition: Determined market position
    """
    try:
        # Leader: High market share + high quality
        if market_share_percentage >= HIGH_MARKET_SHARE_THRESHOLD and quality_score >= 8.0:
            return MarketPosition.LEADER
        
        # Challenger: Medium-high share + high growth
        elif (market_share_percentage >= MEDIUM_MARKET_SHARE_THRESHOLD and 
              growth_rate >= HIGH_GROWTH_RATE_THRESHOLD):
            return MarketPosition.CHALLENGER
        
        # Follower: Medium share + stable growth
        elif market_share_percentage >= MEDIUM_MARKET_SHARE_THRESHOLD:
            return MarketPosition.FOLLOWER
        
        # Niche: Low share but high quality
        elif quality_score >= 8.0:
            return MarketPosition.NICHE
        
        # Emerging: Low share but high growth
        elif growth_rate >= HIGH_GROWTH_RATE_THRESHOLD:
            return MarketPosition.EMERGING
        
        # Default to follower
        else:
            return MarketPosition.FOLLOWER
        
    except Exception as e:
        logger.error(f"Error determining market position: {e}")
        return MarketPosition.FOLLOWER


def assess_competitive_intensity(total_competitors: int,
                               market_concentration: float,
                               entry_barriers_count: int,
                               price_competition: float = 0.5) -> CompetitiveIntensity:
    """
    Assess competitive intensity in the market.
    
    Args:
        total_competitors: Number of competitors
        market_concentration: Market concentration index (0-1)
        entry_barriers_count: Number of entry barriers
        price_competition: Price competition level (0-1)
        
    Returns:
        CompetitiveIntensity: Assessed competitive intensity
    """
    try:
        intensity_score = 0.0
        
        # Factor 1: Number of competitors
        if total_competitors >= 20:
            intensity_score += 0.3
        elif total_competitors >= 10:
            intensity_score += 0.2
        elif total_competitors >= 5:
            intensity_score += 0.1
        
        # Factor 2: Market concentration (inverse - lower concentration = higher intensity)
        if market_concentration < 0.3:
            intensity_score += 0.3
        elif market_concentration < 0.6:
            intensity_score += 0.2
        else:
            intensity_score += 0.1
        
        # Factor 3: Entry barriers (inverse - fewer barriers = higher intensity)
        if entry_barriers_count <= 2:
            intensity_score += 0.2
        elif entry_barriers_count <= 5:
            intensity_score += 0.1
        
        # Factor 4: Price competition
        intensity_score += price_competition * 0.2
        
        # Determine intensity level
        if intensity_score >= 0.8:
            return CompetitiveIntensity.VERY_HIGH
        elif intensity_score >= 0.6:
            return CompetitiveIntensity.HIGH
        elif intensity_score >= 0.4:
            return CompetitiveIntensity.MODERATE
        else:
            return CompetitiveIntensity.LOW
        
    except Exception as e:
        logger.error(f"Error assessing competitive intensity: {e}")
        return CompetitiveIntensity.MODERATE


def calculate_market_concentration(market_shares: List[float]) -> float:
    """
    Calculate market concentration using Herfindahl-Hirschman Index (HHI).
    
    Args:
        market_shares: List of market share percentages
        
    Returns:
        float: Market concentration index (0-1)
    """
    try:
        if not market_shares:
            return 0.0
        
        # Convert to decimal and calculate HHI
        shares_decimal = [share / 100.0 for share in market_shares]
        hhi = sum(share ** 2 for share in shares_decimal)
        
        # Normalize to 0-1 scale
        return min(1.0, hhi)
        
    except Exception as e:
        logger.error(f"Error calculating market concentration: {e}")
        return 0.5  # Default to moderate concentration


def identify_market_leaders(competitors: List[Dict[str, Any]], 
                           metric: str = 'market_share') -> List[str]:
    """
    Identify market leaders based on specified metric.
    
    Args:
        competitors: List of competitor data
        metric: Metric to use for ranking
        
    Returns:
        List[str]: List of market leader URLs
    """
    try:
        if not competitors:
            return []
        
        # Sort competitors by metric
        sorted_competitors = sorted(
            competitors,
            key=lambda x: x.get(metric, 0),
            reverse=True
        )
        
        # Top 3 are considered leaders
        leaders = [comp.get('url', '') for comp in sorted_competitors[:3]]
        return [url for url in leaders if url]  # Remove empty URLs
        
    except Exception as e:
        logger.error(f"Error identifying market leaders: {e}")
        return []


def analyze_market_segments(competitors: List[Dict[str, Any]]) -> List[MarketSegment]:
    """
    Analyze market segments based on competitor data.
    
    Args:
        competitors: List of competitor data
        
    Returns:
        List[MarketSegment]: Market segment analysis
    """
    try:
        segments = []
        
        # Group competitors by industry focus
        industry_groups = defaultdict(list)
        for comp in competitors:
            industries = comp.get('industry_focus', ['general'])
            for industry in industries:
                industry_groups[industry].append(comp)
        
        # Create segments for each industry
        for industry, comps in industry_groups.items():
            if not comps:
                continue
            
            # Calculate segment metrics
            total_competitors = len(comps)
            avg_growth_rate = statistics.mean([c.get('growth_rate', 0) for c in comps])
            
            # Find market leader in segment
            leader = max(comps, key=lambda x: x.get('market_share', 0))
            
            # Identify entry barriers
            barriers = []
            if any(c.get('domain_authority', 0) > 70 for c in comps):
                barriers.append("High domain authority requirements")
            if any(c.get('content_count', 0) > 1000 for c in comps):
                barriers.append("Large content volume")
            if avg_growth_rate < 5:
                barriers.append("Mature market with slow growth")
            
            # Identify key success factors
            success_factors = []
            if all(c.get('mobile_friendly', True) for c in comps):
                success_factors.append("Mobile optimization")
            if all(c.get('avg_quality_score', 0) > 7 for c in comps):
                success_factors.append("High content quality")
            if any(c.get('social_shares', 0) > 1000 for c in comps):
                success_factors.append("Strong social presence")
            
            # Estimate segment size (simplified)
            segment_size = total_competitors * 1000000  # Rough estimate
            
            segments.append(MarketSegment(
                segment_name=industry,
                segment_size=segment_size,
                growth_rate=avg_growth_rate,
                competitor_count=total_competitors,
                market_leader=leader.get('name', 'Unknown'),
                entry_barriers=barriers,
                key_success_factors=success_factors,
                trends=[f"Growth rate: {avg_growth_rate:.1f}%"],
                opportunities=[f"Content quality improvement" if avg_growth_rate > 10 else "Market expansion"],
            ))
        
        return segments
        
    except Exception as e:
        logger.error(f"Error analyzing market segments: {e}")
        return []


def identify_market_opportunities(competitors: List[Dict[str, Any]],
                                gaps: List[Dict[str, Any]]) -> List[MarketOpportunity]:
    """
    Identify market opportunities based on competitor analysis and gaps.
    
    Args:
        competitors: List of competitor data
        gaps: List of identified gaps
        
    Returns:
        List[MarketOpportunity]: Market opportunities
    """
    try:
        opportunities = []
        
        # Analyze content format gaps
        format_gaps = [gap for gap in gaps if gap.get('gap_type') == 'format_gap']
        if format_gaps:
            opportunities.append(MarketOpportunity(
                opportunity_name="Content Format Innovation",
                opportunity_type="format_gap",
                description="Exploit underutilized content formats",
                market_size=len(format_gaps) * 100000,
                growth_potential=15.0,
                competition_level=CompetitiveIntensity.MODERATE,
                time_to_market="3-6 months",
                success_factors=["Creative content development", "Format expertise"],
                barriers=["Content creation resources", "Format-specific skills"],
                strategic_fit="high",
            ))
        
        # Analyze quality gaps
        quality_gaps = [gap for gap in gaps if gap.get('gap_type') == 'quality_gap']
        if quality_gaps:
            opportunities.append(MarketOpportunity(
                opportunity_name="Quality Leadership",
                opportunity_type="quality_gap",
                description="Establish quality leadership in the market",
                market_size=len(quality_gaps) * 50000,
                growth_potential=20.0,
                competition_level=CompetitiveIntensity.HIGH,
                time_to_market="6-12 months",
                success_factors=["Content expertise", "Quality processes"],
                barriers=["High content standards", "Resource investment"],
                strategic_fit="very_high",
            ))
        
        # Analyze topic gaps
        topic_gaps = [gap for gap in gaps if gap.get('gap_type') == 'topic_gap']
        if topic_gaps:
            opportunities.append(MarketOpportunity(
                opportunity_name="Topic Authority",
                opportunity_type="topic_gap",
                description="Become authority in underserved topics",
                market_size=len(topic_gaps) * 75000,
                growth_potential=25.0,
                competition_level=CompetitiveIntensity.LOW,
                time_to_market="2-4 months",
                success_factors=["Subject matter expertise", "Research capabilities"],
                barriers=["Expert knowledge", "Research resources"],
                strategic_fit="high",
            ))
        
        # Analyze market position opportunities
        avg_market_share = statistics.mean([c.get('market_share', 0) for c in competitors])
        if avg_market_share < MEDIUM_MARKET_SHARE_THRESHOLD:
            opportunities.append(MarketOpportunity(
                opportunity_name="Market Share Growth",
                opportunity_type="market_share",
                description="Increase market share through aggressive strategy",
                market_size=1000000,
                growth_potential=30.0,
                competition_level=CompetitiveIntensity.HIGH,
                time_to_market="12-18 months",
                success_factors=["Marketing budget", "Sales team", "Product differentiation"],
                barriers=["Established competitors", "Customer acquisition costs"],
                strategic_fit="medium",
            ))
        
        return opportunities
        
    except Exception as e:
        logger.error(f"Error identifying market opportunities: {e}")
        return []


def analyze_market_trends(competitors: List[Dict[str, Any]]) -> List[MarketTrend]:
    """
    Analyze market trends based on competitor data.
    
    Args:
        competitors: List of competitor data
        
    Returns:
        List[MarketTrend]: Market trends
    """
    try:
        trends = []
        
        # Analyze content type trends
        content_types = []
        for comp in competitors:
            content_types.extend(comp.get('content_types', []))
        
        if content_types:
            type_counter = Counter(content_types)
            most_common_type = type_counter.most_common(1)[0][0]
            
            trends.append(MarketTrend(
                trend_name=f"Rise of {most_common_type} content",
                trend_description=f"{most_common_type.title()} content is becoming dominant in the market",
                trend_direction="growing",
                impact_level="high",
                time_horizon="6-12 months",
                confidence_level=0.8,
                supporting_data={"type_frequency": dict(type_counter)},
                implications=["Focus on " + most_common_type + " content creation"],
                opportunities={"Early adoption": f"Establish expertise in {most_common_type}"},
                threats=["Competitors focusing on same format"],
            ))
        
        # Analyze quality trends
        quality_scores = [c.get('avg_quality_score', 0) for c in competitors]
        if quality_scores:
            avg_quality = statistics.mean(quality_scores)
            
            if avg_quality >= 8.0:
                trend_direction = "growing"
                description = "Content quality standards are rising across the market"
            elif avg_quality <= 5.0:
                trend_direction = "declining"
                description = "Content quality is declining, creating opportunity"
            else:
                trend_direction = "stable"
                description = "Content quality remains stable"
            
            trends.append(MarketTrend(
                trend_name="Content Quality Evolution",
                trend_description=description,
                trend_direction=trend_direction,
                impact_level="medium",
                time_horizon="ongoing",
                confidence_level=0.7,
                supporting_data={"average_quality": avg_quality},
                implications=["Quality investment needed"] if avg_quality >= 8.0 else ["Quality opportunity available"],
                opportunities=["Quality leadership"] if avg_quality <= 5.0 else ["Maintain quality standards"],
                threats=["Quality competition"] if avg_quality >= 8.0 else [],
            ))
        
        # Analyze mobile optimization trends
        mobile_friendly_count = sum(1 for c in competitors if c.get('mobile_friendly', False))
        mobile_percentage = (mobile_friendly_count / len(competitors)) * 100 if competitors else 0
        
        if mobile_percentage >= 80:
            trend_direction = "stable"
            description = "Mobile optimization is standard across competitors"
        elif mobile_percentage >= 50:
            trend_direction = "growing"
            description = "Mobile optimization is becoming standard"
        else:
            trend_direction = "emerging"
            description = "Mobile optimization is still emerging"
        
        trends.append(MarketTrend(
            trend_name="Mobile Optimization",
            trend_description=description,
            trend_direction=trend_direction,
            impact_level="high",
            time_horizon="ongoing",
            confidence_level=0.9,
            supporting_data={"mobile_friendly_percentage": mobile_percentage},
            implications=["Mobile optimization essential"],
            opportunities=["Mobile-first approach"] if mobile_percentage < 80 else ["Mobile experience optimization"],
            threats=["Mobile competition"] if mobile_percentage >= 80 else ["Mobile gap"],
        ))
        
        return trends
        
    except Exception as e:
        logger.error(f"Error analyzing market trends: {e}")
        return []


def create_market_positioning(competitors: List[Dict[str, Any]]) -> MarketPositioning:
    """
    Create comprehensive market positioning analysis.
    
    Args:
        competitors: List of competitor data
        
    Returns:
        MarketPositioning: Market positioning analysis
    """
    try:
        if not competitors:
            raise ValueError("No competitors provided")
        
        # Identify leaders by different criteria
        market_leader = identify_market_leaders(competitors, 'market_share')[0] if competitors else ""
        content_leader = identify_market_leaders(competitors, 'content_count')[0] if competitors else ""
        quality_leader = identify_market_leaders(competitors, 'avg_quality_score')[0] if competitors else ""
        
        # Identify market gaps
        gaps = []
        
        # Content format gaps
        all_formats = set()
        for comp in competitors:
            all_formats.update(comp.get('content_types', []))
        
        common_formats = [fmt for fmt, count in Counter([fmt for comp in competitors for fmt in comp.get('content_types', [])]).most_common() if count >= len(competitors) * 0.6]
        missing_formats = [fmt for fmt in ['video', 'podcast', 'webinar', 'infographic'] if fmt not in common_formats]
        
        if missing_formats:
            gaps.extend(missing_formats)
        
        # Quality gaps
        avg_quality = statistics.mean([c.get('avg_quality_score', 0) for c in competitors])
        if avg_quality < 7.0:
            gaps.append("Content quality improvement")
        
        # Identify opportunities
        opportunities = []
        if avg_quality < 8.0:
            opportunities.append("Quality leadership opportunity")
        if len(missing_formats) > 0:
            opportunities.append("Format innovation opportunity")
        
        # Identify competitive advantages
        advantages = []
        high_da_competitors = [c for c in competitors if c.get('domain_authority', 0) > 70]
        if high_da_competitors:
            advantages.append("Strong domain authority")
        
        high_content_competitors = [c for c in competitors if c.get('content_count', 0) > 500]
        if high_content_competitors:
            advantages.append("Extensive content library")
        
        return MarketPositioning(
            market_leader=market_leader or "Unknown",
            content_leader=content_leader or "Unknown",
            quality_leader=quality_leader or "Unknown",
            market_gaps=gaps,
            opportunities=opportunities,
            competitive_advantages=advantages,
            strategic_recommendations=[],  # To be populated by AI
            positioning_map={},
            market_maturity="mature" if avg_quality >= 7.0 else "developing",
            growth_potential="medium" if avg_quality >= 6.0 else "high",
        )
        
    except Exception as e:
        logger.error(f"Error creating market positioning: {e}")
        raise


def create_competitive_landscape(competitors: List[Dict[str, Any]]) -> CompetitiveLandscape:
    """
    Create competitive landscape analysis.
    
    Args:
        competitors: List of competitor data
        
    Returns:
        CompetitiveLandscape: Competitive landscape analysis
    """
    try:
        if not competitors:
            raise ValueError("No competitors provided")
        
        # Count competitor types
        direct_competitors = len([c for c in competitors if c.get('competitor_type') == 'direct'])
        indirect_competitors = len([c for c in competitors if c.get('competitor_type') == 'indirect'])
        
        # Calculate market concentration
        market_shares = [c.get('market_share', 0) for c in competitors]
        market_concentration = calculate_market_concentration(market_shares)
        
        # Assess competitive intensity
        entry_barriers = len(set().union(*[c.get('entry_barriers', []) for c in competitors]))
        competitive_intensity = assess_competitive_intensity(
            len(competitors),
            market_concentration,
            entry_barriers
        )
        
        # Identify market leaders
        market_leaders = identify_market_leaders(competitors, 'market_share')
        
        # Identify emerging competitors (high growth)
        emerging_competitors = [
            c.get('name', '') for c in competitors 
            if c.get('growth_rate', 0) > HIGH_GROWTH_RATE_THRESHOLD
        ]
        
        # Identify market trends
        trends = ["Increasing content quality standards", "Mobile optimization priority", "Video content growth"]
        
        # Identify disruption risks
        disruption_risks = []
        if any(c.get('domain_authority', 0) < 30 for c in competitors):
            disruption_risks.append("New entrants with low barriers")
        if market_concentration < 0.3:
            disruption_risks.append("Fragmented market vulnerable to consolidation")
        
        # Identify entry barriers
        all_barriers = set()
        for comp in competitors:
            all_barriers.update(comp.get('entry_barriers', []))
        
        # Identify success factors
        success_factors = []
        if all(c.get('mobile_friendly', False) for c in competitors):
            success_factors.append("Mobile optimization")
        if statistics.mean([c.get('avg_quality_score', 0) for c in competitors]) > 7:
            success_factors.append("High content quality")
        
        return CompetitiveLandscape(
            total_competitors=len(competitors),
            direct_competitors=direct_competitors,
            indirect_competitors=indirect_competitors,
            market_concentration=market_concentration,
            competitive_intensity=competitive_intensity,
            market_leaders=market_leaders,
            emerging_competitors=emerging_competitors,
            market_trends=trends,
            disruption_risks=disruption_risks,
            entry_barriers=list(all_barriers),
            success_factors=success_factors,
        )
        
    except Exception as e:
        logger.error(f"Error creating competitive landscape: {e}")
        raise


def calculate_growth_potential(current_metrics: Dict[str, Any],
                             market_metrics: Dict[str, Any]) -> float:
    """
    Calculate growth potential based on current and market metrics.
    
    Args:
        current_metrics: Current competitor metrics
        market_metrics: Overall market metrics
        
    Returns:
        float: Growth potential score (0-10)
    """
    try:
        factors = []
        
        # Factor 1: Market gap (how far below market average)
        current_quality = current_metrics.get('avg_quality_score', 0)
        market_quality = market_metrics.get('avg_quality_score', 5)
        quality_gap = max(0, (market_quality - current_quality) / market_quality)
        factors.append(quality_gap)
        
        # Factor 2: Content volume gap
        current_content = current_metrics.get('content_count', 0)
        market_content = market_metrics.get('avg_content_count', 100)
        content_gap = max(0, (market_content - current_content) / market_content)
        factors.append(content_gap)
        
        # Factor 3: Market share opportunity
        current_share = current_metrics.get('market_share', 0)
        max_share = max(market_metrics.get('market_shares', [10]))
        share_opportunity = max(0, (max_share - current_share) / max_share)
        factors.append(share_opportunity)
        
        # Factor 4: Growth rate comparison
        current_growth = current_metrics.get('growth_rate', 0)
        market_growth = market_metrics.get('avg_growth_rate', 5)
        growth_potential = max(0, (market_growth - current_growth) / max(market_growth, 1))
        factors.append(growth_potential)
        
        # Calculate weighted average
        if factors:
            return sum(factors) / len(factors) * 10  # Scale to 0-10
        else:
            return 5.0  # Default to medium potential
        
    except Exception as e:
        logger.error(f"Error calculating growth potential: {e}")
        return 5.0


def validate_market_data(data: Dict[str, Any]) -> List[ValidationError]:
    """
    Validate market analysis data.
    
    Args:
        data: Market data to validate
        
    Returns:
        List[ValidationError]: List of validation errors
    """
    errors = []
    
    try:
        # Validate market share values
        market_shares = data.get('market_shares', [])
        for i, share in enumerate(market_shares):
            if not isinstance(share, (int, float)) or share < 0 or share > 100:
                errors.append(ValidationError(
                    field=f'market_shares[{i}]',
                    message='Market share must be between 0 and 100',
                    value=share,
                    error_code='INVALID_MARKET_SHARE'
                ))
        
        # Validate growth rates
        growth_rates = data.get('growth_rates', [])
        for i, rate in enumerate(growth_rates):
            if not isinstance(rate, (int, float)) or rate < -100 or rate > 1000:
                errors.append(ValidationError(
                    field=f'growth_rates[{i}]',
                    message='Growth rate must be between -100 and 1000',
                    value=rate,
                    error_code='INVALID_GROWTH_RATE'
                ))
        
        # Validate market size
        market_size = data.get('market_size')
        if market_size is not None and (not isinstance(market_size, (int, float)) or market_size <= 0):
            errors.append(ValidationError(
                field='market_size',
                message='Market size must be a positive number',
                value=market_size,
                error_code='INVALID_MARKET_SIZE'
            ))
        
    except Exception as e:
        logger.error(f"Error validating market data: {e}")
        errors.append(ValidationError(
            field='validation',
            message=f'Validation error: {str(e)}',
            value=data,
            error_code='VALIDATION_ERROR'
        ))
    
    return errors


def create_market_benchmark(metric_name: str,
                          industry_average: float,
                          top_quartile: float,
                          your_value: float) -> Dict[str, Any]:
    """
    Create market benchmark comparison.
    
    Args:
        metric_name: Name of the metric
        industry_average: Industry average value
        top_quartile: Top quartile value
        your_value: Your value
        
    Returns:
        Dict[str, Any]: Benchmark comparison
    """
    try:
        # Calculate percentile rank
        if your_value >= top_quartile:
            percentile_rank = 75 + (your_value - top_quartile) / (top_quartile - industry_average) * 25
        elif your_value >= industry_average:
            percentile_rank = 50 + (your_value - industry_average) / (top_quartile - industry_average) * 25
        else:
            percentile_rank = 50 * (your_value / industry_average)
        
        percentile_rank = max(0, min(100, percentile_rank))
        
        # Calculate performance gap
        performance_gap = top_quartile - your_value
        improvement_potential = (performance_gap / top_quartile) * 100
        
        return {
            'metric_name': metric_name,
            'industry_average': industry_average,
            'top_quartile': top_quartile,
            'your_value': your_value,
            'percentile_rank': round(percentile_rank, 1),
            'performance_gap': round(performance_gap, 2),
            'improvement_potential': round(improvement_potential, 1),
            'benchmark_date': 'current',
            'data_source': 'market_analysis'
        }
        
    except Exception as e:
        logger.error(f"Error creating market benchmark: {e}")
        return {}
