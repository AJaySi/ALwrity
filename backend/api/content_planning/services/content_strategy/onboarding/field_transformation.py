"""
Field Transformation Service
Onboarding data to field mapping.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class FieldTransformationService:
    """Service for transforming onboarding data to strategic input fields."""

    def __init__(self):
        # Define field mapping configurations
        self.field_mappings = {
            # Business Context mappings
            'business_objectives': {
                'sources': ['website_analysis.content_goals', 'research_preferences.research_topics'],
                'transformation': 'extract_business_objectives'
            },
            'target_metrics': {
                'sources': ['website_analysis.performance_metrics', 'research_preferences.performance_tracking'],
                'transformation': 'extract_target_metrics'
            },
            'content_budget': {
                'sources': ['onboarding_session.session_data.budget'],
                'transformation': 'extract_budget'
            },
            'team_size': {
                'sources': ['onboarding_session.session_data.team_size'],
                'transformation': 'extract_team_size'
            },
            'implementation_timeline': {
                'sources': ['onboarding_session.session_data.timeline'],
                'transformation': 'extract_timeline'
            },
            'market_share': {
                'sources': ['website_analysis.performance_metrics'],
                'transformation': 'extract_market_share'
            },
            'competitive_position': {
                'sources': ['website_analysis.competitors', 'research_preferences.competitor_analysis'],
                'transformation': 'extract_competitive_position'
            },
            'performance_metrics': {
                'sources': ['website_analysis.performance_metrics'],
                'transformation': 'extract_performance_metrics'
            },

            # Audience Intelligence mappings
            'content_preferences': {
                'sources': ['research_preferences.content_types'],
                'transformation': 'extract_content_preferences'
            },
            'consumption_patterns': {
                'sources': ['website_analysis.target_audience', 'research_preferences.target_audience'],
                'transformation': 'extract_consumption_patterns'
            },
            'audience_pain_points': {
                'sources': ['website_analysis.content_gaps', 'research_preferences.research_topics'],
                'transformation': 'extract_pain_points'
            },
            'buying_journey': {
                'sources': ['website_analysis.target_audience', 'research_preferences.target_audience'],
                'transformation': 'extract_buying_journey'
            },
            'seasonal_trends': {
                'sources': ['research_preferences.trend_analysis'],
                'transformation': 'extract_seasonal_trends'
            },
            'engagement_metrics': {
                'sources': ['website_analysis.performance_metrics'],
                'transformation': 'extract_engagement_metrics'
            },

            # Competitive Intelligence mappings
            'top_competitors': {
                'sources': ['website_analysis.competitors'],
                'transformation': 'extract_competitors'
            },
            'competitor_content_strategies': {
                'sources': ['website_analysis.competitors', 'research_preferences.competitor_analysis'],
                'transformation': 'extract_competitor_strategies'
            },
            'market_gaps': {
                'sources': ['website_analysis.content_gaps', 'research_preferences.research_topics'],
                'transformation': 'extract_market_gaps'
            },
            'industry_trends': {
                'sources': ['website_analysis.industry', 'research_preferences.industry_focus'],
                'transformation': 'extract_industry_trends'
            },
            'emerging_trends': {
                'sources': ['research_preferences.trend_analysis'],
                'transformation': 'extract_emerging_trends'
            },

            # Content Strategy mappings
            'preferred_formats': {
                'sources': ['research_preferences.content_types'],
                'transformation': 'extract_preferred_formats'
            },
            'content_mix': {
                'sources': ['research_preferences.content_types', 'website_analysis.content_goals'],
                'transformation': 'extract_content_mix'
            },
            'content_frequency': {
                'sources': ['research_preferences.content_calendar'],
                'transformation': 'extract_content_frequency'
            },
            'optimal_timing': {
                'sources': ['research_preferences.content_calendar'],
                'transformation': 'extract_optimal_timing'
            },
            'quality_metrics': {
                'sources': ['website_analysis.performance_metrics'],
                'transformation': 'extract_quality_metrics'
            },
            'editorial_guidelines': {
                'sources': ['website_analysis.business_type', 'research_preferences.content_types'],
                'transformation': 'extract_editorial_guidelines'
            },
            'brand_voice': {
                'sources': ['website_analysis.business_type', 'onboarding_session.session_data.brand_voice'],
                'transformation': 'extract_brand_voice'
            },

            # Performance Analytics mappings
            'traffic_sources': {
                'sources': ['website_analysis.performance_metrics'],
                'transformation': 'extract_traffic_sources'
            },
            'conversion_rates': {
                'sources': ['website_analysis.performance_metrics'],
                'transformation': 'extract_conversion_rates'
            },
            'content_roi_targets': {
                'sources': ['onboarding_session.session_data.budget', 'website_analysis.performance_metrics'],
                'transformation': 'extract_roi_targets'
            },
            'ab_testing_capabilities': {
                'sources': ['onboarding_session.session_data.team_size'],
                'transformation': 'extract_ab_testing_capabilities'
            }
        }

    def transform_onboarding_data_to_fields(self, integrated_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform onboarding data to strategic input fields."""
        try:
            logger.info("Transforming onboarding data to strategic fields")
            
            transformed_fields = {}
            transformation_metadata = {
                'total_fields': 0,
                'populated_fields': 0,
                'data_sources_used': [],
                'confidence_scores': {}
            }
            
            # Process each field mapping
            for field_name, mapping in self.field_mappings.items():
                try:
                    sources = mapping.get('sources', [])
                    transformation_method = mapping.get('transformation')
                    
                    # Extract source data
                    source_data = self._extract_source_data(integrated_data, sources)
                    
                    # Apply transformation if method exists
                    if transformation_method and hasattr(self, transformation_method):
                        transform_func = getattr(self, transformation_method)
                        field_value = transform_func(source_data, integrated_data)
                    else:
                        # Default transformation - use first available source data
                        field_value = self._default_transformation(source_data, field_name)
                    
                    if field_value is not None and field_value != "":
                        transformed_fields[field_name] = {
                            'value': field_value,
                            'source': sources[0] if sources else 'default',
                            'confidence': self._calculate_field_confidence(source_data, sources),
                            'auto_populated': True
                        }
                        transformation_metadata['populated_fields'] += 1
                    
                    transformation_metadata['total_fields'] += 1
                    
                except Exception as e:
                    logger.error(f"Error transforming field {field_name}: {str(e)}")
                    # Don't provide fallback data - let the error propagate
                    transformation_metadata['total_fields'] += 1
            
            logger.info(f"Successfully transformed {transformation_metadata['populated_fields']} fields from onboarding data")
            
            return {
                'fields': transformed_fields,
                'sources': self._get_data_source_info(list(self.field_mappings.keys()), integrated_data),
                'transformation_metadata': transformation_metadata
            }
            
        except Exception as e:
            logger.error(f"Error in transform_onboarding_data_to_fields: {str(e)}")
            return {'fields': {}, 'sources': {}, 'transformation_metadata': {'error': str(e)}}

    def get_data_sources(self, integrated_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get data sources information for the transformed fields."""
        try:
            sources_info = {}
            for field_name, mapping in self.field_mappings.items():
                sources = mapping.get('sources', [])
                sources_info[field_name] = {
                    'sources': sources,
                    'source_count': len(sources),
                    'has_data': any(self._has_source_data(integrated_data, source) for source in sources)
                }
            return sources_info
        except Exception as e:
            logger.error(f"Error getting data sources: {str(e)}")
            return {}

    def get_detailed_input_data_points(self, integrated_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed input data points for debugging and analysis."""
        try:
            data_points = {}
            for field_name, mapping in self.field_mappings.items():
                sources = mapping.get('sources', [])
                source_data = {}
                
                for source in sources:
                    source_data[source] = {
                        'exists': self._has_source_data(integrated_data, source),
                        'value': self._get_nested_value(integrated_data, source),
                        'type': type(self._get_nested_value(integrated_data, source)).__name__
                    }
                
                data_points[field_name] = {
                    'sources': source_data,
                    'transformation_method': mapping.get('transformation'),
                    'has_data': any(source_data[source]['exists'] for source in sources)
                }
            return data_points
        except Exception as e:
            logger.error(f"Error getting detailed input data points: {str(e)}")
            return {}

    def _extract_source_data(self, integrated_data: Dict[str, Any], sources: List[str]) -> Dict[str, Any]:
        """Extract data from specified sources."""
        source_data = {}
        
        for source_path in sources:
            try:
                # Navigate nested dictionary structure
                keys = source_path.split('.')
                value = integrated_data
                
                for key in keys:
                    if isinstance(value, dict) and key in value:
                        value = value[key]
                    else:
                        value = None
                        break
                
                if value is not None:
                    source_data[source_path] = value
                    
            except Exception as e:
                logger.debug(f"Error extracting data from {source_path}: {str(e)}")
                continue
                
        return source_data

    def _get_data_source_info(self, sources: List[str], integrated_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get information about data sources for a field."""
        source_info = {
            'sources': sources,
            'data_quality': self._assess_source_quality(sources, integrated_data),
            'last_updated': datetime.utcnow().isoformat()
        }
        return source_info

    def _assess_source_quality(self, sources: List[str], integrated_data: Dict[str, Any]) -> float:
        """Assess the quality of data sources."""
        try:
            quality_scores = []
            
            for source in sources:
                # Check if source exists and has data
                keys = source.split('.')
                value = integrated_data
                
                for key in keys:
                    if isinstance(value, dict) and key in value:
                        value = value[key]
                    else:
                        value = None
                        break
                
                if value:
                    # Basic quality assessment
                    if isinstance(value, (list, dict)) and len(value) > 0:
                        quality_scores.append(1.0)
                    elif isinstance(value, str) and len(value.strip()) > 0:
                        quality_scores.append(0.8)
                    else:
                        quality_scores.append(0.5)
                else:
                    quality_scores.append(0.0)
            
            return sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
            
        except Exception as e:
            logger.error(f"Error assessing source quality: {str(e)}")
            return 0.0

    # Transformation methods for each field type
    def extract_business_objectives(self, source_data: Dict[str, Any], integrated_data: Dict[str, Any]) -> Optional[str]:
        """Extract business objectives from content goals and research topics."""
        try:
            objectives = []
            
            if 'website_analysis.content_goals' in source_data:
                goals = source_data['website_analysis.content_goals']
                if isinstance(goals, list):
                    objectives.extend(goals)
                elif isinstance(goals, str):
                    objectives.append(goals)
            
            if 'research_preferences.research_topics' in source_data:
                topics = source_data['research_preferences.research_topics']
                if isinstance(topics, list):
                    objectives.extend(topics)
                elif isinstance(topics, str):
                    objectives.append(topics)
            
            return ', '.join(objectives) if objectives else None
            
        except Exception as e:
            logger.error(f"Error extracting business objectives: {str(e)}")
            return None

    def extract_target_metrics(self, source_data: Dict[str, Any], integrated_data: Dict[str, Any]) -> Optional[str]:
        """Extract target metrics from performance data."""
        try:
            metrics = []
            
            if 'website_analysis.performance_metrics' in source_data:
                perf_metrics = source_data['website_analysis.performance_metrics']
                if isinstance(perf_metrics, dict):
                    metrics.extend([f"{k}: {v}" for k, v in perf_metrics.items()])
                elif isinstance(perf_metrics, str):
                    metrics.append(perf_metrics)
            
            if 'research_preferences.performance_tracking' in source_data:
                tracking = source_data['research_preferences.performance_tracking']
                if isinstance(tracking, list):
                    metrics.extend(tracking)
                elif isinstance(tracking, str):
                    metrics.append(tracking)
            
            return ', '.join(metrics) if metrics else None
            
        except Exception as e:
            logger.error(f"Error extracting target metrics: {str(e)}")
            return None

    def extract_budget(self, source_data: Dict[str, Any], integrated_data: Dict[str, Any]) -> Optional[str]:
        """Extract content budget from session data."""
        try:
            if 'onboarding_session.session_data.budget' in source_data:
                budget = source_data['onboarding_session.session_data.budget']
                if budget:
                    return str(budget)
            return None
            
        except Exception as e:
            logger.error(f"Error extracting budget: {str(e)}")
            return None

    def extract_team_size(self, source_data: Dict[str, Any], integrated_data: Dict[str, Any]) -> Optional[str]:
        """Extract team size from session data."""
        try:
            if 'onboarding_session.session_data.team_size' in source_data:
                team_size = source_data['onboarding_session.session_data.team_size']
                if team_size:
                    return str(team_size)
            return None
            
        except Exception as e:
            logger.error(f"Error extracting team size: {str(e)}")
            return None

    def extract_timeline(self, source_data: Dict[str, Any], integrated_data: Dict[str, Any]) -> Optional[str]:
        """Extract implementation timeline from session data."""
        try:
            if 'onboarding_session.session_data.timeline' in source_data:
                timeline = source_data['onboarding_session.session_data.timeline']
                if timeline:
                    return str(timeline)
            return None
            
        except Exception as e:
            logger.error(f"Error extracting timeline: {str(e)}")
            return None

    def extract_market_share(self, source_data: Dict[str, Any], integrated_data: Dict[str, Any]) -> Optional[str]:
        """Extract market share from performance metrics."""
        try:
            if 'website_analysis.performance_metrics' in source_data:
                metrics = source_data['website_analysis.performance_metrics']
                if isinstance(metrics, dict) and 'market_share' in metrics:
                    return str(metrics['market_share'])
            return None
            
        except Exception as e:
            logger.error(f"Error extracting market share: {str(e)}")
            return None

    def extract_competitive_position(self, source_data: Dict[str, Any], integrated_data: Dict[str, Any]) -> Optional[str]:
        """Extract and normalize competitive position to one of Leader, Challenger, Niche, Emerging."""
        try:
            text_blobs: list[str] = []
            
            if 'website_analysis.competitors' in source_data:
                competitors = source_data['website_analysis.competitors']
                if isinstance(competitors, (str, list, dict)):
                    text_blobs.append(str(competitors))
            
            if 'research_preferences.competitor_analysis' in source_data:
                analysis = source_data['research_preferences.competitor_analysis']
                if isinstance(analysis, (str, list, dict)):
                    text_blobs.append(str(analysis))

            blob = ' '.join(text_blobs).lower()
            
            # Simple keyword heuristics
            if any(kw in blob for kw in ['leader', 'market leader', 'category leader', 'dominant']):
                return 'Leader'
            if any(kw in blob for kw in ['challenger', 'fast follower', 'aggressive']):
                return 'Challenger'
            if any(kw in blob for kw in ['niche', 'niche player', 'specialized']):
                return 'Niche'
            if any(kw in blob for kw in ['emerging', 'new entrant', 'startup', 'growing']):
                return 'Emerging'

            # No clear signal; let default take over
            return None
        except Exception as e:
            logger.error(f"Error extracting competitive position: {str(e)}")
            return None

    def extract_performance_metrics(self, source_data: Dict[str, Any], integrated_data: Dict[str, Any]) -> Optional[str]:
        """Extract performance metrics."""
        try:
            if 'website_analysis.performance_metrics' in source_data:
                metrics = source_data['website_analysis.performance_metrics']
                if isinstance(metrics, dict):
                    return ', '.join([f"{k}: {v}" for k, v in metrics.items()])
                elif isinstance(metrics, str):
                    return metrics
            return None
            
        except Exception as e:
            logger.error(f"Error extracting performance metrics: {str(e)}")
            return None

    def extract_content_preferences(self, source_data: Dict[str, Any], integrated_data: Dict[str, Any]) -> Optional[str]:
        """Extract content preferences from research preferences."""
        try:
            if 'research_preferences.content_types' in source_data:
                content_types = source_data['research_preferences.content_types']
                if isinstance(content_types, list):
                    return ', '.join(content_types)
                elif isinstance(content_types, str):
                    return content_types
            return None
            
        except Exception as e:
            logger.error(f"Error extracting content preferences: {str(e)}")
            return None

    def extract_consumption_patterns(self, source_data: Dict[str, Any], integrated_data: Dict[str, Any]) -> Optional[str]:
        """Extract consumption patterns from audience data."""
        try:
            patterns = []
            
            if 'website_analysis.target_audience' in source_data:
                audience = source_data['website_analysis.target_audience']
                if audience:
                    patterns.append(f"Website Audience: {audience}")
            
            if 'research_preferences.target_audience' in source_data:
                research_audience = source_data['research_preferences.target_audience']
                if research_audience:
                    patterns.append(f"Research Audience: {research_audience}")
            
            # If we have consumption data as a dict, format it nicely
            if isinstance(integrated_data.get('consumption_patterns'), dict):
                consumption_data = integrated_data['consumption_patterns']
                if isinstance(consumption_data, dict):
                    formatted_patterns = []
                    for platform, percentage in consumption_data.items():
                        formatted_patterns.append(f"{platform.title()}: {percentage}%")
                    patterns.append(', '.join(formatted_patterns))
            
            return '; '.join(patterns) if patterns else None
            
        except Exception as e:
            logger.error(f"Error extracting consumption patterns: {str(e)}")
            return None

    def extract_pain_points(self, source_data: Dict[str, Any], integrated_data: Dict[str, Any]) -> Optional[str]:
        """Extract audience pain points from content gaps and research topics."""
        try:
            pain_points = []
            
            if 'website_analysis.content_gaps' in source_data:
                gaps = source_data['website_analysis.content_gaps']
                if isinstance(gaps, list):
                    pain_points.extend(gaps)
                elif isinstance(gaps, str):
                    pain_points.append(gaps)
            
            if 'research_preferences.research_topics' in source_data:
                topics = source_data['research_preferences.research_topics']
                if isinstance(topics, list):
                    pain_points.extend(topics)
                elif isinstance(topics, str):
                    pain_points.append(topics)
            
            return ', '.join(pain_points) if pain_points else None
            
        except Exception as e:
            logger.error(f"Error extracting pain points: {str(e)}")
            return None

    def extract_buying_journey(self, source_data: Dict[str, Any], integrated_data: Dict[str, Any]) -> Optional[str]:
        """Extract buying journey from audience data."""
        try:
            if 'website_analysis.target_audience' in source_data:
                audience = source_data['website_analysis.target_audience']
                if audience:
                    return f"Journey based on: {audience}"
            
            # If we have buying journey data as a dict, format it nicely
            if isinstance(integrated_data.get('buying_journey'), dict):
                journey_data = integrated_data['buying_journey']
                if isinstance(journey_data, dict):
                    formatted_journey = []
                    for stage, percentage in journey_data.items():
                        formatted_journey.append(f"{stage.title()}: {percentage}%")
                    return ', '.join(formatted_journey)
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting buying journey: {str(e)}")
            return None

    def extract_seasonal_trends(self, source_data: Dict[str, Any], integrated_data: Dict[str, Any]) -> Optional[str]:
        """Extract seasonal trends from trend analysis."""
        try:
            if 'research_preferences.trend_analysis' in source_data:
                trends = source_data['research_preferences.trend_analysis']
                if isinstance(trends, list):
                    return ', '.join(trends)
                elif isinstance(trends, str):
                    return trends
            return None
            
        except Exception as e:
            logger.error(f"Error extracting seasonal trends: {str(e)}")
            return None

    def extract_engagement_metrics(self, source_data: Dict[str, Any], integrated_data: Dict[str, Any]) -> Optional[str]:
        """Extract engagement metrics from performance data."""
        try:
            if 'website_analysis.performance_metrics' in source_data:
                metrics = source_data['website_analysis.performance_metrics']
                if isinstance(metrics, dict):
                    engagement_metrics = {k: v for k, v in metrics.items() if 'engagement' in k.lower()}
                    if engagement_metrics:
                        return ', '.join([f"{k}: {v}" for k, v in engagement_metrics.items()])
            return None
            
        except Exception as e:
            logger.error(f"Error extracting engagement metrics: {str(e)}")
            return None

    def extract_competitors(self, source_data: Dict[str, Any], integrated_data: Dict[str, Any]) -> Optional[str]:
        """Extract top competitors from competitor data."""
        try:
            if 'website_analysis.competitors' in source_data:
                competitors = source_data['website_analysis.competitors']
                if isinstance(competitors, list):
                    return ', '.join(competitors)
                elif isinstance(competitors, str):
                    return competitors
            return None
            
        except Exception as e:
            logger.error(f"Error extracting competitors: {str(e)}")
            return None

    def extract_competitor_strategies(self, source_data: Dict[str, Any], integrated_data: Dict[str, Any]) -> Optional[str]:
        """Extract competitor content strategies."""
        try:
            strategies = []
            
            if 'website_analysis.competitors' in source_data:
                competitors = source_data['website_analysis.competitors']
                if competitors:
                    strategies.append(f"Competitors: {competitors}")
            
            if 'research_preferences.competitor_analysis' in source_data:
                analysis = source_data['research_preferences.competitor_analysis']
                if analysis:
                    strategies.append(f"Analysis: {analysis}")
            
            return '; '.join(strategies) if strategies else None
            
        except Exception as e:
            logger.error(f"Error extracting competitor strategies: {str(e)}")
            return None

    def extract_market_gaps(self, source_data: Dict[str, Any], integrated_data: Dict[str, Any]) -> Optional[str]:
        """Extract market gaps from content gaps and research topics."""
        try:
            gaps = []
            
            if 'website_analysis.content_gaps' in source_data:
                content_gaps = source_data['website_analysis.content_gaps']
                if isinstance(content_gaps, list):
                    gaps.extend(content_gaps)
                elif isinstance(content_gaps, str):
                    gaps.append(content_gaps)
            
            if 'research_preferences.research_topics' in source_data:
                topics = source_data['research_preferences.research_topics']
                if isinstance(topics, list):
                    gaps.extend(topics)
                elif isinstance(topics, str):
                    gaps.append(topics)
            
            return ', '.join(gaps) if gaps else None
            
        except Exception as e:
            logger.error(f"Error extracting market gaps: {str(e)}")
            return None

    def extract_industry_trends(self, source_data: Dict[str, Any], integrated_data: Dict[str, Any]) -> Optional[str]:
        """Extract industry trends from industry data."""
        try:
            trends = []
            
            if 'website_analysis.industry' in source_data:
                industry = source_data['website_analysis.industry']
                if industry:
                    trends.append(f"Industry: {industry}")
            
            if 'research_preferences.industry_focus' in source_data:
                focus = source_data['research_preferences.industry_focus']
                if focus:
                    trends.append(f"Focus: {focus}")
            
            return '; '.join(trends) if trends else None
            
        except Exception as e:
            logger.error(f"Error extracting industry trends: {str(e)}")
            return None

    def extract_emerging_trends(self, source_data: Dict[str, Any], integrated_data: Dict[str, Any]) -> Optional[str]:
        """Extract emerging trends from trend analysis."""
        try:
            if 'research_preferences.trend_analysis' in source_data:
                trends = source_data['research_preferences.trend_analysis']
                if isinstance(trends, list):
                    return ', '.join(trends)
                elif isinstance(trends, str):
                    return trends
            return None
            
        except Exception as e:
            logger.error(f"Error extracting emerging trends: {str(e)}")
            return None

    def extract_preferred_formats(self, source_data: Dict[str, Any], integrated_data: Dict[str, Any]) -> Optional[str]:
        """Extract preferred content formats and normalize to UI option labels array."""
        try:
            def to_canonical(label: str) -> Optional[str]:
                normalized = label.strip().lower()
                mapping = {
                    'blog': 'Blog Posts',
                    'blog post': 'Blog Posts',
                    'blog posts': 'Blog Posts',
                    'article': 'Blog Posts',
                    'articles': 'Blog Posts',
                    'video': 'Videos',
                    'videos': 'Videos',
                    'infographic': 'Infographics',
                    'infographics': 'Infographics',
                    'webinar': 'Webinars',
                    'webinars': 'Webinars',
                    'podcast': 'Podcasts',
                    'podcasts': 'Podcasts',
                    'case study': 'Case Studies',
                    'case studies': 'Case Studies',
                    'whitepaper': 'Whitepapers',
                    'whitepapers': 'Whitepapers',
                    'social': 'Social Media Posts',
                    'social media': 'Social Media Posts',
                    'social media posts': 'Social Media Posts'
                }
                return mapping.get(normalized, None)

            if 'research_preferences.content_types' in source_data:
                content_types = source_data['research_preferences.content_types']
                canonical: list[str] = []
                if isinstance(content_types, list):
                    for item in content_types:
                        if isinstance(item, str):
                            canon = to_canonical(item)
                            if canon and canon not in canonical:
                                canonical.append(canon)
                elif isinstance(content_types, str):
                    for part in content_types.split(','):
                        canon = to_canonical(part)
                        if canon and canon not in canonical:
                            canonical.append(canon)
                if canonical:
                    return canonical
            return None
        except Exception as e:
            logger.error(f"Error extracting preferred formats: {str(e)}")
            return None

    def extract_content_mix(self, source_data: Dict[str, Any], integrated_data: Dict[str, Any]) -> Optional[str]:
        """Extract content mix from content types and goals."""
        try:
            mix_components = []
            
            if 'research_preferences.content_types' in source_data:
                content_types = source_data['research_preferences.content_types']
                if content_types:
                    mix_components.append(f"Types: {content_types}")
            
            if 'website_analysis.content_goals' in source_data:
                goals = source_data['website_analysis.content_goals']
                if goals:
                    mix_components.append(f"Goals: {goals}")
            
            return '; '.join(mix_components) if mix_components else None
            
        except Exception as e:
            logger.error(f"Error extracting content mix: {str(e)}")
            return None

    def extract_content_frequency(self, source_data: Dict[str, Any], integrated_data: Dict[str, Any]) -> Optional[str]:
        """Extract content frequency from calendar data."""
        try:
            if 'research_preferences.content_calendar' in source_data:
                calendar = source_data['research_preferences.content_calendar']
                if calendar:
                    return str(calendar)
            return None
            
        except Exception as e:
            logger.error(f"Error extracting content frequency: {str(e)}")
            return None

    def extract_optimal_timing(self, source_data: Dict[str, Any], integrated_data: Dict[str, Any]) -> Optional[str]:
        """Extract optimal timing from calendar data."""
        try:
            if 'research_preferences.content_calendar' in source_data:
                calendar = source_data['research_preferences.content_calendar']
                if calendar:
                    return str(calendar)
            
            # If we have optimal timing data as a dict, format it nicely
            if isinstance(integrated_data.get('optimal_timing'), dict):
                timing_data = integrated_data['optimal_timing']
                if isinstance(timing_data, dict):
                    formatted_timing = []
                    if 'best_days' in timing_data:
                        days = timing_data['best_days']
                        if isinstance(days, list):
                            formatted_timing.append(f"Best Days: {', '.join(days)}")
                    if 'best_time' in timing_data:
                        formatted_timing.append(f"Best Time: {timing_data['best_time']}")
                    return ', '.join(formatted_timing)
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting optimal timing: {str(e)}")
            return None

    def extract_quality_metrics(self, source_data: Dict[str, Any], integrated_data: Dict[str, Any]) -> Optional[str]:
        """Extract quality metrics from performance data."""
        try:
            if 'website_analysis.performance_metrics' in source_data:
                metrics = source_data['website_analysis.performance_metrics']
                if isinstance(metrics, dict):
                    quality_metrics = {k: v for k, v in metrics.items() if 'quality' in k.lower()}
                    if quality_metrics:
                        return ', '.join([f"{k.title()}: {v}" for k, v in quality_metrics.items()])
                elif isinstance(metrics, str):
                    return metrics
            
            # If we have quality metrics data as a dict, format it nicely
            if isinstance(integrated_data.get('quality_metrics'), dict):
                quality_data = integrated_data['quality_metrics']
                if isinstance(quality_data, dict):
                    formatted_metrics = []
                    for metric, value in quality_data.items():
                        formatted_metrics.append(f"{metric.title()}: {value}")
                    return ', '.join(formatted_metrics)
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting quality metrics: {str(e)}")
            return None

    def extract_editorial_guidelines(self, source_data: Dict[str, Any], integrated_data: Dict[str, Any]) -> Optional[str]:
        """Extract editorial guidelines from business type and content types."""
        try:
            guidelines = []
            
            if 'website_analysis.business_type' in source_data:
                business_type = source_data['website_analysis.business_type']
                if business_type:
                    guidelines.append(f"Business Type: {business_type}")
            
            if 'research_preferences.content_types' in source_data:
                content_types = source_data['research_preferences.content_types']
                if content_types:
                    guidelines.append(f"Content Types: {content_types}")
            
            return '; '.join(guidelines) if guidelines else None
            
        except Exception as e:
            logger.error(f"Error extracting editorial guidelines: {str(e)}")
            return None

    def extract_brand_voice(self, source_data: Dict[str, Any], integrated_data: Dict[str, Any]) -> Optional[str]:
        """Extract brand voice from business type and session data."""
        try:
            voice_indicators = []
            
            if 'website_analysis.business_type' in source_data:
                business_type = source_data['website_analysis.business_type']
                if business_type:
                    voice_indicators.append(f"Business Type: {business_type}")
            
            if 'onboarding_session.session_data.brand_voice' in source_data:
                brand_voice = source_data['onboarding_session.session_data.brand_voice']
                if brand_voice:
                    voice_indicators.append(f"Brand Voice: {brand_voice}")
            
            return '; '.join(voice_indicators) if voice_indicators else None
            
        except Exception as e:
            logger.error(f"Error extracting brand voice: {str(e)}")
            return None

    def extract_traffic_sources(self, source_data: Dict[str, Any], integrated_data: Dict[str, Any]) -> Optional[str]:
        """Extract traffic sources from performance metrics."""
        try:
            if 'website_analysis.performance_metrics' in source_data:
                metrics = source_data['website_analysis.performance_metrics']
                if isinstance(metrics, dict):
                    traffic_metrics = {k: v for k, v in metrics.items() if 'traffic' in k.lower()}
                    if traffic_metrics:
                        return ', '.join([f"{k.title()}: {v}%" for k, v in traffic_metrics.items()])
                elif isinstance(metrics, str):
                    return metrics
            return None
            
        except Exception as e:
            logger.error(f"Error extracting traffic sources: {str(e)}")
            return None

    def extract_conversion_rates(self, source_data: Dict[str, Any], integrated_data: Dict[str, Any]) -> Optional[str]:
        """Extract conversion rates from performance metrics."""
        try:
            if 'website_analysis.performance_metrics' in source_data:
                metrics = source_data['website_analysis.performance_metrics']
                if isinstance(metrics, dict):
                    conversion_metrics = {k: v for k, v in metrics.items() if 'conversion' in k.lower()}
                    if conversion_metrics:
                        return ', '.join([f"{k.title()}: {v}%" for k, v in conversion_metrics.items()])
                elif isinstance(metrics, str):
                    return metrics
            return None
            
        except Exception as e:
            logger.error(f"Error extracting conversion rates: {str(e)}")
            return None

    def extract_roi_targets(self, source_data: Dict[str, Any], integrated_data: Dict[str, Any]) -> Optional[str]:
        """Extract ROI targets from budget and performance data."""
        try:
            targets = []
            
            if 'onboarding_session.session_data.budget' in source_data:
                budget = source_data['onboarding_session.session_data.budget']
                if budget:
                    targets.append(f"Budget: {budget}")
            
            if 'website_analysis.performance_metrics' in source_data:
                metrics = source_data['website_analysis.performance_metrics']
                if isinstance(metrics, dict):
                    roi_metrics = {k: v for k, v in metrics.items() if 'roi' in k.lower()}
                    if roi_metrics:
                        targets.append(f"ROI Metrics: {roi_metrics}")
            
            return '; '.join(targets) if targets else None
            
        except Exception as e:
            logger.error(f"Error extracting ROI targets: {str(e)}")
            return None

    def extract_ab_testing_capabilities(self, source_data: Dict[str, Any], integrated_data: Dict[str, Any]) -> Optional[bool]:
        """Extract A/B testing capabilities from team size."""
        try:
            if 'onboarding_session.session_data.team_size' in source_data:
                team_size = source_data['onboarding_session.session_data.team_size']
                if team_size:
                    # Return boolean based on team size
                    team_size_int = int(team_size) if isinstance(team_size, (str, int, float)) else 1
                    return team_size_int > 2  # True if team size > 2, False otherwise
            
            # Default to False if no team size data
            return False
            
        except Exception as e:
            logger.error(f"Error extracting A/B testing capabilities: {str(e)}")
            return False

    def _default_transformation(self, source_data: Dict[str, Any], field_name: str) -> Any:
        """Default transformation when no specific method is available."""
        try:
            # Try to find any non-empty value in source data
            for key, value in source_data.items():
                if value is not None and value != "":
                    # For budget and team_size, try to convert to number
                    if field_name in ['content_budget', 'team_size'] and isinstance(value, (str, int, float)):
                        try:
                            return int(value) if field_name == 'team_size' else float(value)
                        except (ValueError, TypeError):
                            continue
                    # For other fields, return the first non-empty value
                    return value
            
            # If no value found, return None
            return None
        except Exception as e:
            logger.error(f"Error in default transformation for {field_name}: {str(e)}")
            return None

    def _calculate_field_confidence(self, source_data: Dict[str, Any], sources: List[str]) -> float:
        """Calculate confidence score for a field based on data quality and source availability."""
        try:
            if not source_data:
                return 0.3  # Low confidence when no data
            
            # Check data quality indicators
            data_quality_score = 0.0
            total_indicators = 0
            
            # Check if data is not empty
            for key, value in source_data.items():
                if value is not None and value != "":
                    data_quality_score += 1.0
                total_indicators += 1
            
            # Check source availability
            source_availability = len([s for s in sources if self._has_source_data(source_data, s)]) / max(len(sources), 1)
            
            # Calculate final confidence
            if total_indicators > 0:
                data_quality = data_quality_score / total_indicators
                confidence = (data_quality + source_availability) / 2
                return min(confidence, 1.0)  # Cap at 1.0
            else:
                return 0.3  # Default low confidence
                
        except Exception as e:
            logger.error(f"Error calculating field confidence: {str(e)}")
            return 0.3  # Default low confidence

    def _has_source_data(self, integrated_data: Dict[str, Any], source_path: str) -> bool:
        """Check if source data exists in integrated data."""
        try:
            value = self._get_nested_value(integrated_data, source_path)
            return value is not None and value != ""
        except Exception as e:
            logger.debug(f"Error checking source data for {source_path}: {str(e)}")
            return False

    def _get_nested_value(self, data: Dict[str, Any], path: str) -> Any:
        """Get nested value from dictionary using dot notation."""
        try:
            keys = path.split('.')
            value = data
            
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return None
            
            return value
        except Exception as e:
            logger.debug(f"Error getting nested value for {path}: {str(e)}")
            return None 