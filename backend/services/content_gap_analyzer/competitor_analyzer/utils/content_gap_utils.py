"""
Content Gap Utilities for Competitor Analyzer Service

This module contains utility functions for content gap analysis,
gap identification, and content opportunity analysis.
"""

from typing import Dict, Any, List, Optional, Tuple, Set
from collections import Counter, defaultdict
import statistics
from loguru import logger

from ..constants import (
    HIGH_PRIORITY_THRESHOLD,
    MEDIUM_PRIORITY_THRESHOLD,
    LOW_PRIORITY_THRESHOLD,
    HIGH_OPPORTUNITY_THRESHOLD,
    MEDIUM_OPPORTUNITY_THRESHOLD,
    LOW_OPPORTUNITY_THRESHOLD,
    DEFAULT_IMPLEMENTATION_TIME_SHORT,
    DEFAULT_IMPLEMENTATION_TIME_MEDIUM,
    DEFAULT_IMPLEMENTATION_TIME_LONG,
    FORMAT_SUGGESTIONS,
    DEFAULT_FORMAT_SUGGESTIONS,
)
from ..models.content_gap_models import (
    GapType,
    ContentFormat,
    ContentGap,
    TopicGap,
    FormatGap,
    QualityGap,
    FrequencyGap,
    ContentGapAnalysis,
    ContentOpportunity,
    GapRecommendation,
    PriorityLevel,
    ImpactLevel,
    OpportunityLevel,
    ContentSuggestion,
)
from ..models.shared import ValidationError


def analyze_topic_distribution(competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze topic distribution across competitors.
    
    Args:
        competitors: List of competitor data
        
    Returns:
        Dict[str, Any]: Topic distribution analysis
    """
    try:
        all_topics = []
        topic_frequency = Counter()
        topic_coverage = defaultdict(list)
        
        for competitor in competitors:
            topics = competitor.get('topics', [])
            competitor_url = competitor.get('url', '')
            
            for topic in topics:
                if isinstance(topic, dict):
                    topic_name = topic.get('topic', '')
                else:
                    topic_name = str(topic)
                
                if topic_name:
                    all_topics.append(topic_name)
                    topic_frequency[topic_name] += 1
                    topic_coverage[topic_name].append(competitor_url)
        
        # Calculate coverage percentages
        total_competitors = len(competitors)
        topic_coverage_percentages = {}
        for topic, urls in topic_coverage.items():
            topic_coverage_percentages[topic] = (len(urls) / total_competitors) * 100
        
        # Find common and unique topics
        common_topics = [topic for topic, count in topic_frequency.most_common(10) 
                        if count >= total_competitors * 0.6]  # Covered by 60%+ competitors
        unique_topics = [topic for topic, count in topic_frequency.items() 
                       if count == 1]  # Covered by only 1 competitor
        
        return {
            'total_topics': len(set(all_topics)),
            'common_topics': common_topics,
            'unique_topics': unique_topics,
            'topic_frequency': dict(topic_frequency.most_common()),
            'topic_coverage_percentages': topic_coverage_percentages,
            'topic_diversity_score': len(set(all_topics)) / len(all_topics) if all_topics else 0,
            'coverage_distribution': {
                'high_coverage': len([t for t, pct in topic_coverage_percentages.items() if pct >= 80]),
                'medium_coverage': len([t for t, pct in topic_coverage_percentages.items() if 40 <= pct < 80]),
                'low_coverage': len([t for t, pct in topic_coverage_percentages.items() if pct < 40]),
            }
        }
        
    except Exception as e:
        logger.error(f"Error analyzing topic distribution: {e}")
        return {}


def analyze_content_depth(competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze content depth across competitors.
    
    Args:
        competitors: List of competitor data
        
    Returns:
        Dict[str, Any]: Content depth analysis
    """
    try:
        depth_metrics = {
            'word_counts': {},
            'section_counts': {},
            'heading_distribution': defaultdict(list),
            'content_hierarchy': {},
            'depth_scores': {}
        }
        
        all_word_counts = []
        all_section_counts = []
        
        for competitor in competitors:
            url = competitor.get('url', '')
            content_structure = competitor.get('content_structure', {})
            
            # Extract word count
            word_count = content_structure.get('word_count', 1000)
            depth_metrics['word_counts'][url] = word_count
            all_word_counts.append(word_count)
            
            # Extract section count
            section_count = content_structure.get('section_count', 5)
            depth_metrics['section_counts'][url] = section_count
            all_section_counts.append(section_count)
            
            # Extract heading distribution
            headings = content_structure.get('headings', {})
            for heading_type, count in headings.items():
                depth_metrics['heading_distribution'][heading_type].append(count)
            
            # Calculate depth score
            depth_score = calculate_content_depth_score(word_count, section_count, headings)
            depth_metrics['depth_scores'][url] = depth_score
        
        # Calculate averages and ranges
        if all_word_counts:
            depth_metrics['averages'] = {
                'word_count': statistics.mean(all_word_counts),
                'section_count': statistics.mean(all_section_counts),
                'depth_score': statistics.mean(depth_metrics['depth_scores'].values())
            }
            
            depth_metrics['ranges'] = {
                'word_count': {
                    'min': min(all_word_counts),
                    'max': max(all_word_counts),
                    'median': statistics.median(all_word_counts)
                },
                'section_count': {
                    'min': min(all_section_counts),
                    'max': max(all_section_counts),
                    'median': statistics.median(all_section_counts)
                },
                'depth_score': {
                    'min': min(depth_metrics['depth_scores'].values()),
                    'max': max(depth_metrics['depth_scores'].values()),
                    'median': statistics.median(depth_metrics['depth_scores'].values())
                }
            }
        
        return depth_metrics
        
    except Exception as e:
        logger.error(f"Error analyzing content depth: {e}")
        return {}


def calculate_content_depth_score(word_count: int, section_count: int, headings: Dict[str, int]) -> float:
    """
    Calculate content depth score based on word count, sections, and headings.
    
    Args:
        word_count: Number of words
        section_count: Number of sections
        headings: Heading structure
        
    Returns:
        float: Depth score (0-10)
    """
    try:
        # Normalize word count (0-3 points)
        word_score = min(3.0, word_count / 1000.0)
        
        # Normalize section count (0-3 points)
        section_score = min(3.0, section_count / 10.0)
        
        # Normalize heading structure (0-4 points)
        heading_score = 0.0
        total_headings = sum(headings.values())
        if total_headings > 0:
            # Points for having different heading levels
            heading_levels = len([h for h, count in headings.items() if count > 0])
            heading_score = min(4.0, heading_levels * 1.0)
        
        total_score = word_score + section_score + heading_score
        return min(10.0, total_score)
        
    except Exception as e:
        logger.error(f"Error calculating content depth score: {e}")
        return 5.0


def analyze_content_formats(competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze content formats across competitors.
    
    Args:
        competitors: List of competitor data
        
    Returns:
        Dict[str, Any]: Content format analysis
    """
    try:
        format_analysis = {
            'format_distribution': defaultdict(int),
            'format_coverage': defaultdict(list),
            'format_effectiveness': {},
            'format_gaps': [],
            'format_recommendations': []
        }
        
        all_formats = []
        format_effectiveness_scores = defaultdict(list)
        
        for competitor in competitors:
            url = competitor.get('url', '')
            content_types = competitor.get('content_types', [])
            engagement_metrics = competitor.get('engagement_metrics', {})
            
            for content_type in content_types:
                format_analysis['format_distribution'][content_type] += 1
                format_analysis['format_coverage'][content_type].append(url)
                all_formats.append(content_type)
                
                # Calculate effectiveness score based on engagement
                effectiveness = calculate_format_effectiveness(content_type, engagement_metrics)
                format_effectiveness_scores[content_type].append(effectiveness)
        
        # Calculate average effectiveness for each format
        for content_type, scores in format_effectiveness_scores.items():
            if scores:
                format_analysis['format_effectiveness'][content_type] = statistics.mean(scores)
        
        # Identify format gaps (formats not widely used)
        total_competitors = len(competitors)
        common_formats = ['blog', 'article', 'video', 'infographic', 'case_study', 'whitepaper']
        
        for format_type in common_formats:
            coverage = len(format_analysis['format_coverage'][format_type])
            coverage_percentage = (coverage / total_competitors) * 100
            
            if coverage_percentage < 40:  # Used by less than 40% of competitors
                format_analysis['format_gaps'].append({
                    'format': format_type,
                    'coverage_percentage': coverage_percentage,
                    'opportunity_level': 'high' if coverage_percentage < 20 else 'medium'
                })
        
        # Generate format recommendations
        for gap in format_analysis['format_gaps']:
            format_type = gap['format']
            suggestions = FORMAT_SUGGESTIONS.get(format_type, DEFAULT_FORMAT_SUGGESTIONS)
            
            format_analysis['format_recommendations'].append({
                'format': format_type,
                'suggestions': suggestions,
                'opportunity_level': gap['opportunity_level'],
                'estimated_impact': 'high' if gap['opportunity_level'] == 'high' else 'medium'
            })
        
        return dict(format_analysis)
        
    except Exception as e:
        logger.error(f"Error analyzing content formats: {e}")
        return {}


def calculate_format_effectiveness(content_type: str, engagement_metrics: Dict[str, Any]) -> float:
    """
    Calculate effectiveness score for a content format.
    
    Args:
        content_type: Type of content
        engagement_metrics: Engagement metrics
        
    Returns:
        float: Effectiveness score (0-10)
    """
    try:
        score = 0.0
        
        # Factor 1: Time on page (0-3 points)
        avg_time = engagement_metrics.get('avg_time_on_page', 180)
        if avg_time >= 300:  # 5+ minutes
            score += 3.0
        elif avg_time >= 180:  # 3+ minutes
            score += 2.0
        elif avg_time >= 60:  # 1+ minute
            score += 1.0
        
        # Factor 2: Social shares (0-3 points)
        shares = engagement_metrics.get('social_shares', 0)
        if shares >= 100:
            score += 3.0
        elif shares >= 50:
            score += 2.0
        elif shares >= 10:
            score += 1.0
        
        # Factor 3: Bounce rate (inverse, 0-2 points)
        bounce_rate = engagement_metrics.get('bounce_rate', 0.35)
        if bounce_rate <= 0.3:
            score += 2.0
        elif bounce_rate <= 0.5:
            score += 1.0
        
        # Factor 4: Format-specific bonuses (0-2 points)
        if content_type == 'video':
            score += 2.0  # Video typically has higher engagement
        elif content_type in ['infographic', 'interactive']:
            score += 1.5
        elif content_type in ['case_study', 'whitepaper']:
            score += 1.0
        
        return min(10.0, score)
        
    except Exception as e:
        logger.error(f"Error calculating format effectiveness: {e}")
        return 5.0


def analyze_content_quality(competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze content quality across competitors.
    
    Args:
        competitors: List of competitor data
        
    Returns:
        Dict[str, Any]: Content quality analysis
    """
    try:
        quality_analysis = {
            'quality_scores': {},
            'quality_distribution': defaultdict(int),
            'quality_factors': {},
            'quality_gaps': [],
            'quality_benchmarks': {}
        }
        
        all_quality_scores = []
        quality_factors = defaultdict(list)
        
        for competitor in competitors:
            url = competitor.get('url', '')
            quality_score = competitor.get('avg_quality_score', 5.0)
            
            quality_analysis['quality_scores'][url] = quality_score
            all_quality_scores.append(quality_score)
            
            # Categorize quality level
            if quality_score >= 8.0:
                quality_analysis['quality_distribution']['high'] += 1
            elif quality_score >= 6.0:
                quality_analysis['quality_distribution']['medium'] += 1
            else:
                quality_analysis['quality_distribution']['low'] += 1
            
            # Collect quality factors
            content_analysis = competitor.get('content_analysis', {})
            quality_factors['readability'].append(content_analysis.get('readability_score', 75))
            quality_factors['freshness'].append(content_analysis.get('freshness_score', 5.0))
            quality_factors['depth'].append(content_analysis.get('content_depth_score', 5.0))
        
        # Calculate average quality factors
        for factor, scores in quality_factors.items():
            if scores:
                quality_analysis['quality_factors'][factor] = {
                    'average': statistics.mean(scores),
                    'min': min(scores),
                    'max': max(scores)
                }
        
        # Identify quality gaps
        if all_quality_scores:
            avg_quality = statistics.mean(all_quality_scores)
            
            # Competitors with below-average quality
            low_quality_competitors = [
                comp for comp in competitors 
                if comp.get('avg_quality_score', 0) < avg_quality - 1.0
            ]
            
            if low_quality_competitors:
                quality_analysis['quality_gaps'] = [
                    {
                        'type': 'quality_improvement',
                        'description': 'Quality improvement opportunity',
                        'affected_competitors': len(low_quality_competitors),
                        'opportunity_score': (avg_quality - min(all_quality_scores)) / 10.0
                    }
                ]
        
        # Set quality benchmarks
        if all_quality_scores:
            quality_analysis['quality_benchmarks'] = {
                'industry_average': statistics.mean(all_quality_scores),
                'top_quartile': statistics.quantile(all_quality_scores, 0.75),
                'median': statistics.median(all_quality_scores),
                'bottom_quartile': statistics.quantile(all_quality_scores, 0.25)
            }
        
        return quality_analysis
        
    except Exception as e:
        logger.error(f"Error analyzing content quality: {e}")
        return {}


def identify_missing_topics(competitors: List[Dict[str, Any]], 
                          coverage_threshold: float = 0.5) -> List[TopicGap]:
    """
    Identify topics that are missing or underrepresented.
    
    Args:
        competitors: List of competitor data
        coverage_threshold: Coverage threshold for identifying gaps
        
    Returns:
        List[TopicGap]: List of topic gaps
    """
    try:
        topic_gaps = []
        all_topics = set()
        topic_coverage = defaultdict(int)
        topic_data = defaultdict(list)
        
        # Collect all topics and their coverage
        for competitor in competitors:
            topics = competitor.get('topics', [])
            competitor_url = competitor.get('url', '')
            
            for topic in topics:
                if isinstance(topic, dict):
                    topic_name = topic.get('topic', '')
                    topic_data_dict = topic
                else:
                    topic_name = str(topic)
                    topic_data_dict = {'topic': topic_name}
                
                if topic_name:
                    all_topics.add(topic_name)
                    topic_coverage[topic_name] += 1
                    topic_data[topic_name].append({
                        'competitor_url': competitor_url,
                        'data': topic_data_dict
                    })
        
        # Identify missing or underrepresented topics
        total_competitors = len(competitors)
        
        for topic in all_topics:
            coverage = topic_coverage[topic] / total_competitors
            
            if coverage < coverage_threshold:  # Topic covered by less than threshold
                # Calculate opportunity score
                opportunity_score = (1 - coverage) * 10
                
                # Determine search trend (simplified)
                search_trend = "stable"  # Would integrate with actual search data
                if opportunity_score > 7:
                    search_trend = "growing"
                
                # Determine seasonal relevance
                seasonal_relevance = "moderate"  # Would integrate with actual seasonal data
                
                # Extract related keywords from competitor data
                related_keywords = []
                for topic_info in topic_data[topic]:
                    keywords = topic_info['data'].get('keywords', [])
                    related_keywords.extend(keywords)
                
                # Generate content angles
                content_angles = [
                    f"Comprehensive guide to {topic}",
                    f"Case study on {topic}",
                    f"Best practices for {topic}",
                    f"Future trends in {topic}"
                ]
                
                topic_gap = TopicGap(
                    topic_name=topic,
                    topic_category=categorize_topic(topic),
                    gap_description=f"Topic covered by only {coverage:.1%} of competitors",
                    competitor_coverage=[info['competitor_url'] for info in topic_data[topic]],
                    coverage_depth={info['competitor_url']: "basic" for info in topic_data[topic]},
                    opportunity_score=opportunity_score,
                    search_trend=search_trend,
                    seasonal_relevance=seasonal_relevance,
                    related_keywords=list(set(related_keywords)),
                    content_angles=content_angles,
                    expert_quotes=[f"Industry expert on {topic}"],
                    data_sources=[f"Industry reports on {topic}"],
                )
                
                topic_gaps.append(topic_gap)
        
        # Sort by opportunity score
        topic_gaps.sort(key=lambda x: x.opportunity_score, reverse=True)
        
        return topic_gaps
        
    except Exception as e:
        logger.error(f"Error identifying missing topics: {e}")
        return []


def categorize_topic(topic: str) -> str:
    """
    Categorize a topic into a broader category.
    
    Args:
        topic: Topic name
        
    Returns:
        str: Topic category
    """
    try:
        topic_lower = topic.lower()
        
        # Technology categories
        if any(tech in topic_lower for tech in ['ai', 'machine learning', 'ml', 'data science', 'python', 'java']):
            return 'technology'
        
        # Business categories
        if any(biz in topic_lower for biz in ['marketing', 'sales', 'strategy', 'management', 'business']):
            return 'business'
        
        # Content categories
        if any(content in topic_lower for tech in ['content', 'writing', 'blogging', 'seo', 'social media']):
            return 'content'
        
        # Finance categories
        if any(finance in topic_lower for tech in ['finance', 'investment', 'money', 'banking', 'trading']):
            return 'finance'
        
        # Healthcare categories
        if any(health in topic_lower for tech in ['health', 'medical', 'healthcare', 'wellness']):
            return 'healthcare'
        
        # Education categories
        if any(edu in topic_lower for tech in ['education', 'learning', 'training', 'course']):
            return 'education'
        
        # Default category
        return 'general'
        
    except Exception as e:
        logger.error(f"Error categorizing topic {topic}: {e}")
        return 'general'


def identify_format_gaps(competitors: List[Dict[str, Any]]) -> List[FormatGap]:
    """
    Identify gaps in content formats.
    
    Args:
        competitors: List of competitor data
        
    Returns:
        List[FormatGap]: List of format gaps
    """
    try:
        format_gaps = []
        
        # Analyze format coverage
        format_analysis = analyze_content_formats(competitors)
        
        for gap_info in format_analysis.get('format_gaps', []):
            format_type = gap_info['format']
            coverage_percentage = gap_info['coverage_percentage']
            opportunity_level = gap_info['opportunity_level']
            
            # Determine priority
            if opportunity_level == 'high':
                priority = PriorityLevel.HIGH
            elif opportunity_level == 'medium':
                priority = PriorityLevel.MEDIUM
            else:
                priority = PriorityLevel.LOW
            
            # Determine impact
            if format_type in ['video', 'interactive', 'webinar']:
                impact = ImpactLevel.HIGH
            elif format_type in ['infographic', 'case_study', 'whitepaper']:
                impact = ImpactLevel.MEDIUM
            else:
                impact = ImpactLevel.LOW
            
            # Calculate production complexity
            complexity = determine_format_complexity(format_type)
            
            # Estimate engagement potential
            engagement_potential = estimate_format_engagement(format_type)
            
            # Get distribution channels
            distribution_channels = get_format_distribution_channels(format_type)
            
            # Get repurposing potential
            repurposing_potential = get_format_repurposing_potential(format_type)
            
            # Determine competitive advantage
            competitive_advantage = get_format_competitive_advantage(format_type)
            
            # Estimate implementation timeline
            implementation_timeline = estimate_format_implementation_time(format_type)
            
            format_gap = FormatGap(
                target_format=ContentFormat(format_type),
                current_coverage={},  # Would be populated with actual data
                format_effectiveness={},  # Would be populated with actual data
                audience_preference=engagement_potential,
                production_complexity=complexity,
                resource_requirements=get_format_resource_requirements(format_type),
                estimated_engagement=engagement_potential,
                distribution_channels=distribution_channels,
                repurposing_potential=repurposing_potential,
                competitive_advantage=competitive_advantage,
                implementation_timeline=implementation_timeline,
            )
            
            format_gaps.append(format_gap)
        
        return format_gaps
        
    except Exception as e:
        logger.error(f"Error identifying format gaps: {e}")
        return []


def determine_format_complexity(format_type: str) -> PriorityLevel:
    """
    Determine production complexity for a content format.
    
    Args:
        format_type: Content format type
        
    Returns:
        PriorityLevel: Production complexity
    """
    try:
        complexity_map = {
            'video': PriorityLevel.HIGH,
            'webinar': PriorityLevel.HIGH,
            'interactive': PriorityLevel.HIGH,
            'infographic': PriorityLevel.MEDIUM,
            'case_study': PriorityLevel.MEDIUM,
            'whitepaper': PriorityLevel.MEDIUM,
            'ebook': PriorityLevel.MEDIUM,
            'podcast': PriorityLevel.MEDIUM,
            'article': PriorityLevel.LOW,
            'blog_post': PriorityLevel.LOW,
        }
        
        return complexity_map.get(format_type, PriorityLevel.MEDIUM)
        
    except Exception as e:
        logger.error(f"Error determining format complexity: {e}")
        return PriorityLevel.MEDIUM


def estimate_format_engagement(format_type: str) -> float:
    """
    Estimate engagement potential for a content format.
    
    Args:
        format_type: Content format type
        
    Returns:
        float: Engagement potential score (0-10)
    """
    try:
        engagement_map = {
            'video': 8.5,
            'interactive': 8.0,
            'webinar': 7.5,
            'infographic': 7.0,
            'case_study': 6.5,
            'podcast': 6.0,
            'whitepaper': 5.5,
            'ebook': 5.0,
            'article': 4.5,
            'blog_post': 4.0,
        }
        
        return engagement_map.get(format_type, 5.0)
        
    except Exception as e:
        logger.error(f"Error estimating format engagement: {e}")
        return 5.0


def get_format_distribution_channels(format_type: str) -> List[str]:
    """
    Get distribution channels for a content format.
    
    Args:
        format_type: Content format type
        
    Returns:
        List[str]: Distribution channels
    """
    try:
        channel_map = {
            'video': ['YouTube', 'Vimeo', 'Social Media', 'Website'],
            'webinar': ['Zoom', 'Teams', 'YouTube', 'Website'],
            'interactive': ['Website', 'Social Media', 'Email'],
            'infographic': ['Pinterest', 'Instagram', 'Website', 'Social Media'],
            'case_study': ['Website', 'LinkedIn', 'Email', 'PDF'],
            'whitepaper': ['Website', 'LinkedIn', 'Email', 'PDF'],
            'ebook': ['Website', 'Amazon', 'Email', 'PDF'],
            'podcast': ['Spotify', 'Apple Podcasts', 'Website'],
            'article': ['Website', 'LinkedIn', 'Medium', 'Email'],
            'blog_post': ['Website', 'Social Media', 'Email', 'RSS'],
        }
        
        return channel_map.get(format_type, ['Website', 'Social Media'])
        
    except Exception as e:
        logger.error(f"Error getting format distribution channels: {e}")
        return ['Website', 'Social Media']


def get_format_repurposing_potential(format_type: str) -> List[ContentFormat]:
    """
    Get repurposing potential for a content format.
    
    Args:
        format_type: Content format type
        
    Returns:
        List[ContentFormat]: Formats that can be created from this format
    """
    try:
        repurposing_map = {
            'video': [ContentFormat.ARTICLE, ContentFormat.INFOGRAPHIC, ContentFormat.PODCAST],
            'webinar': [ContentFormat.VIDEO, ContentFormat.ARTICLE, ContentFormat.BLOG_POST],
            'whitepaper': [ContentFormat.BLOG_POST, ContentFormat.INFOGRAPHIC, ContentFormat.ARTICLE],
            'case_study': [ContentFormat.BLOG_POST, ContentFormat.INFOGRAPHIC, ContentFormat.VIDEO],
            'podcast': [ContentFormat.BLOG_POST, ContentFormat.ARTICLE, ContentFormat.INFOGRAPHIC],
            'article': [ContentFormat.INFOGRAPHIC, ContentFormat.VIDEO, ContentFormat.PODCAST],
            'blog_post': [ContentFormat.INFOGRAPHIC, ContentFormat.VIDEO, ContentFormat.ARTICLE],
        }
        
        return repurposing_map.get(format_type, [])
        
    except Exception as e:
        logger.error(f"Error getting format repurposing potential: {e}")
        return []


def get_format_competitive_advantage(format_type: str) -> str:
    """
    Get competitive advantage description for a content format.
    
    Args:
        format_type: Content format type
        
    Returns:
        str: Competitive advantage description
    """
    try:
        advantage_map = {
            'video': "Higher engagement and shareability",
            'webinar': "Direct audience interaction and lead generation",
            'interactive': "Increased user engagement and time on site",
            'infographic': "Visual appeal and easy sharing",
            'case_study': "Proof of concept and credibility",
            'whitepaper': "Thought leadership and lead generation",
            'ebook': "Comprehensive value and email capture",
            'podcast': "Convenient consumption and audience building",
            'article': "SEO optimization and evergreen value",
            'blog_post': "Regular content and community building",
        }
        
        return advantage_map.get(format_type, "Content diversification")
        
    except Exception as e:
        logger.error(f"Error getting format competitive advantage: {e}")
        return "Content diversification"


def estimate_format_implementation_time(format_type: str) -> str:
    """
    Estimate implementation time for a content format.
    
    Args:
        format_type: Content format type
        
    Returns:
        str: Implementation time estimate
    """
    try:
        time_map = {
            'video': DEFAULT_IMPLEMENTATION_TIME_LONG,
            'webinar': DEFAULT_IMPLEMENTATION_TIME_MEDIUM,
            'interactive': DEFAULT_IMPLEMENTATION_TIME_LONG,
            'infographic': DEFAULT_IMPLEMENTATION_TIME_MEDIUM,
            'case_study': DEFAULT_IMPLEMENTATION_TIME_MEDIUM,
            'whitepaper': DEFAULT_IMPLEMENTATION_TIME_LONG,
            'ebook': DEFAULT_IMPLEMENTATION_TIME_LONG,
            'podcast': DEFAULT_IMPLEMENTATION_TIME_MEDIUM,
            'article': DEFAULT_IMPLEMENTATION_TIME_SHORT,
            'blog_post': DEFAULT_IMPLEMENTATION_TIME_SHORT,
        }
        
        return time_map.get(format_type, DEFAULT_IMPLEMENTATION_TIME_MEDIUM)
        
    except Exception as e:
        logger.error(f"Error estimating format implementation time: {e}")
        return DEFAULT_IMPLEMENTATION_TIME_MEDIUM


def get_format_resource_requirements(format_type: str) -> List[str]:
    """
    Get resource requirements for a content format.
    
    Args:
        format_type: Content format type
        
    Returns:
        List[str]: Resource requirements
    """
    try:
        requirements_map = {
            'video': ['Camera equipment', 'Video editing software', 'Lighting', 'Audio equipment'],
            'webinar': ['Webinar platform', 'Presentation software', 'Microphone', 'Camera'],
            'interactive': ['Development tools', 'Design software', 'Testing environment'],
            'infographic': ['Design software', 'Data sources', 'Design skills'],
            'case_study': ['Research skills', 'Writing skills', 'Data analysis'],
            'whitepaper': ['Research skills', 'Writing skills', 'Design software'],
            'ebook': ['Writing skills', 'Design software', 'Editing skills'],
            'podcast': ['Microphone', 'Audio editing software', 'Recording space'],
            'article': ['Writing skills', 'Research skills', 'SEO knowledge'],
            'blog_post': ['Writing skills', 'SEO knowledge', 'Content management'],
        }
        
        return requirements_map.get(format_type, ['Content creation skills'])
        
    except Exception as e:
        logger.error(f"Error getting format resource requirements: {e}")
        return ['Content creation skills']


def calculate_gap_priority(gap_type: GapType, 
                         opportunity_score: float,
                         implementation_complexity: PriorityLevel,
                         estimated_impact: ImpactLevel) -> PriorityLevel:
    """
    Calculate priority level for a content gap.
    
    Args:
        gap_type: Type of gap
        opportunity_score: Opportunity score (0-10)
        implementation_complexity: Implementation complexity
        estimated_impact: Estimated impact
        
    Returns:
        PriorityLevel: Priority level
    """
    try:
        # Base score from opportunity
        base_score = opportunity_score
        
        # Adjust for impact
        impact_multiplier = {
            ImpactLevel.VERY_HIGH: 1.5,
            ImpactLevel.HIGH: 1.3,
            ImpactLevel.MEDIUM: 1.0,
            ImpactLevel.LOW: 0.7,
        }
        
        adjusted_score = base_score * impact_multiplier.get(estimated_impact, 1.0)
        
        # Adjust for complexity (inverse)
        complexity_penalty = {
            PriorityLevel.VERY_HIGH: -2.0,
            PriorityLevel.HIGH: -1.0,
            PriorityLevel.MEDIUM: 0.0,
            PriorityLevel.LOW: 1.0,
            PriorityLevel.URGENT: -2.0,
        }
        
        final_score = adjusted_score + complexity_penalty.get(implementation_complexity, 0.0)
        
        # Determine priority
        if final_score >= HIGH_PRIORITY_THRESHOLD:
            return PriorityLevel.HIGH
        elif final_score >= MEDIUM_PRIORITY_THRESHOLD:
            return PriorityLevel.MEDIUM
        else:
            return PriorityLevel.LOW
        
    except Exception as e:
        logger.error(f"Error calculating gap priority: {e}")
        return PriorityLevel.MEDIUM


def validate_content_gap_data(data: Dict[str, Any]) -> List[ValidationError]:
    """
    Validate content gap analysis data.
    
    Args:
        data: Content gap data to validate
        
    Returns:
        List[ValidationError]: List of validation errors
    """
    errors = []
    
    try:
        # Validate gap type
        gap_type = data.get('gap_type')
        if gap_type and gap_type not in [gt.value for gt in GapType]:
            errors.append(ValidationError(
                field='gap_type',
                message=f'Invalid gap type. Must be one of: {[gt.value for gt in GapType]}',
                value=gap_type,
                error_code='INVALID_GAP_TYPE'
            ))
        
        # Validate opportunity score
        opportunity_score = data.get('opportunity_score')
        if opportunity_score is not None:
            if not isinstance(opportunity_score, (int, float)) or opportunity_score < 0 or opportunity_score > 10:
                errors.append(ValidationError(
                    field='opportunity_score',
                    message='Opportunity score must be between 0 and 10',
                    value=opportunity_score,
                    error_code='INVALID_OPPORTUNITY_SCORE'
                ))
        
        # Validate priority and impact levels
        priority = data.get('priority')
        if priority and priority not in [pl.value for pl in PriorityLevel]:
            errors.append(ValidationError(
                field='priority',
                message=f'Invalid priority level. Must be one of: {[pl.value for pl in PriorityLevel]}',
                value=priority,
                error_code='INVALID_PRIORITY'
            ))
        
        impact = data.get('estimated_impact')
        if impact and impact not in [il.value for il in ImpactLevel]:
            errors.append(ValidationError(
                field='estimated_impact',
                message=f'Invalid impact level. Must be one of: {[il.value for il in ImpactLevel]}',
                value=impact,
                error_code='INVALID_IMPACT'
            ))
        
    except Exception as e:
        logger.error(f"Error validating content gap data: {e}")
        errors.append(ValidationError(
            field='validation',
            message=f'Validation error: {str(e)}',
            value=data,
            error_code='VALIDATION_ERROR'
        ))
    
    return errors
