"""
Content Gap Analysis Service

Specialized service for content gap identification and analysis.
Handles topic gaps, format gaps, quality gaps, and content opportunity analysis.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger
import asyncio

from ..models.content_gap_models import (
    ContentGap,
    ContentGapAnalysis,
    TopicGap,
    FormatGap,
    QualityGap,
    FrequencyGap,
    GapType,
    PriorityLevel,
    ImpactLevel,
    OpportunityLevel,
    ContentSuggestion,
    GapRecommendation,
)
from ..models.competitor_models import CompetitorAnalysis
from ..models.shared import (
    AnalysisStatus,
    ValidationError,
    AIInsight,
    Recommendation,
)
from ..utils.content_gap_utils import (
    analyze_topic_distribution,
    analyze_content_depth,
    analyze_content_formats,
    analyze_content_quality,
    identify_missing_topics,
    identify_format_gaps,
    calculate_gap_priority,
    validate_content_gap_data,
    calculate_format_effectiveness,
    determine_format_complexity,
    estimate_format_engagement,
    get_format_distribution_channels,
    get_format_repurposing_potential,
    get_format_competitive_advantage,
    estimate_format_implementation_time,
    get_format_resource_requirements,
)
from ..utils.data_transformers import (
    transform_content_gaps_to_analysis,
)
from ..dependencies import inject_ai_provider


class ContentGapAnalysisService:
    """
    Specialized service for content gap analysis.
    
    This service handles:
    - Topic gap identification and analysis
    - Content format gap analysis
    - Content quality gap assessment
    - Content frequency gap analysis
    - Content opportunity identification
    """
    
    def __init__(self):
        """Initialize the content gap analysis service."""
        self.service_name = "ContentGapAnalysisService"
        self.version = "1.0.0"
        logger.info(f"✅ {self.service_name} v{self.version} initialized")
    
    async def analyze_content_gaps(self, 
                                  competitor_analyses: List[CompetitorAnalysis],
                                  target_keywords: Optional[List[str]] = None,
                                  industry: str = "") -> ContentGapAnalysis:
        """
        Analyze content gaps across competitors.
        
        Args:
            competitor_analyses: List of competitor analyses
            target_keywords: Target keywords for gap analysis
            industry: Industry category
            
        Returns:
            ContentGapAnalysis: Comprehensive content gap analysis
        """
        try:
            logger.info(f"🔍 Analyzing content gaps for {len(competitor_analyses)} competitors")
            
            # Extract competitor data for analysis
            competitor_data = self._extract_competitor_data(competitor_analyses)
            
            # Identify different types of gaps
            topic_gaps = await self._identify_topic_gaps(competitor_data, target_keywords or [])
            format_gaps = await self._identify_format_gaps(competitor_data)
            quality_gaps = await self._identify_quality_gaps(competitor_data)
            frequency_gaps = await self._identify_frequency_gaps(competitor_data)
            
            # Create content gap analysis
            gap_analysis = ContentGapAnalysis(
                industry=industry,
                competitor_urls=[comp.profile.url for comp in competitor_analyses],
                analysis_date=datetime.utcnow(),
                total_gaps_identified=len(topic_gaps) + len(format_gaps) + len(quality_gaps) + len(frequency_gaps),
                gaps_by_type={
                    GapType.TOPIC_GAP: len(topic_gaps),
                    GapType.FORMAT_GAP: len(format_gaps),
                    GapType.QUALITY_GAP: len(quality_gaps),
                    GapType.FREQUENCY_GAP: len(frequency_gaps),
                },
                topic_gaps=topic_gaps,
                format_gaps=format_gaps,
                quality_gaps=quality_gaps,
                frequency_gaps=frequency_gaps,
                high_priority_gaps=self._get_high_priority_gaps(topic_gaps, format_gaps, quality_gaps, frequency_gaps),
                recommendations=await self._generate_gap_recommendations(topic_gaps, format_gaps, quality_gaps, frequency_gaps),
                implementation_roadmap=await self._create_implementation_roadmap(topic_gaps, format_gaps, quality_gaps, frequency_gaps),
                expected_impact=self._calculate_expected_impact(topic_gaps, format_gaps, quality_gaps, frequency_gaps),
                confidence_score=self._calculate_confidence_score(competitor_data),
            )
            
            logger.info("✅ Content gap analysis completed")
            return gap_analysis
            
        except Exception as e:
            logger.error(f"❌ Error in content gap analysis: {e}")
            raise
    
    async def analyze_topic_gaps(self, 
                                competitor_analyses: List[CompetitorAnalysis],
                                target_keywords: Optional[List[str]] = None) -> List[TopicGap]:
        """
        Analyze topic gaps specifically.
        
        Args:
            competitor_analyses: List of competitor analyses
            target_keywords: Target keywords for analysis
            
        Returns:
            List[TopicGap]: List of topic gaps
        """
        try:
            logger.info("🔍 Analyzing topic gaps")
            
            # Extract competitor data
            competitor_data = self._extract_competitor_data(competitor_analyses)
            
            # Identify topic gaps
            topic_gaps = await self._identify_topic_gaps(competitor_data, target_keywords or [])
            
            logger.info(f"✅ Identified {len(topic_gaps)} topic gaps")
            return topic_gaps
            
        except Exception as e:
            logger.error(f"❌ Error analyzing topic gaps: {e}")
            raise
    
    async def analyze_format_gaps(self, competitor_analyses: List[CompetitorAnalysis]) -> List[FormatGap]:
        """
        Analyze content format gaps specifically.
        
        Args:
            competitor_analyses: List of competitor analyses
            
        Returns:
            List[FormatGap]: List of format gaps
        """
        try:
            logger.info("🔍 Analyzing format gaps")
            
            # Extract competitor data
            competitor_data = self._extract_competitor_data(competitor_analyses)
            
            # Identify format gaps
            format_gaps = await self._identify_format_gaps(competitor_data)
            
            logger.info(f"✅ Identified {len(format_gaps)} format gaps")
            return format_gaps
            
        except Exception as e:
            logger.error(f"❌ Error analyzing format gaps: {e}")
            raise
    
    async def analyze_quality_gaps(self, competitor_analyses: List[CompetitorAnalysis]) -> List[QualityGap]:
        """
        Analyze content quality gaps specifically.
        
        Args:
            competitor_analyses: List of competitor analyses
            
        Returns:
            List[QualityGap]: List of quality gaps
        """
        try:
            logger.info("🔍 Analyzing quality gaps")
            
            # Extract competitor data
            competitor_data = self._extract_competitor_data(competitor_analyses)
            
            # Identify quality gaps
            quality_gaps = await self._identify_quality_gaps(competitor_data)
            
            logger.info(f"✅ Identified {len(quality_gaps)} quality gaps")
            return quality_gaps
            
        except Exception as e:
            logger.error(f"❌ Error analyzing quality gaps: {e}")
            raise
    
    def _extract_competitor_data(self, competitor_analyses: List[CompetitorAnalysis]) -> List[Dict[str, Any]]:
        """Extract relevant data from competitor analyses."""
        try:
            competitor_data = []
            
            for analysis in competitor_analyses:
                data = {
                    'url': analysis.profile.url,
                    'name': analysis.profile.name,
                    'content_count': analysis.metrics.content_analysis.content_count,
                    'avg_quality_score': analysis.metrics.content_analysis.avg_quality_score,
                    'content_types': [ct.value for ct in analysis.metrics.content_analysis.content_types],
                    'publishing_frequency': analysis.metrics.content_analysis.publishing_frequency.value,
                    'avg_word_count': analysis.metrics.content_analysis.avg_word_count,
                    'content_depth_score': analysis.metrics.content_analysis.content_depth_score,
                    'freshness_score': analysis.metrics.content_analysis.freshness_score,
                    'topic_diversity': analysis.metrics.content_analysis.topic_diversity,
                    'top_keywords': analysis.metrics.content_analysis.top_keywords,
                    'topics': analysis.metrics.content_analysis.top_keywords,  # Simplified
                    'content_structure': {
                        'word_count': analysis.metrics.content_analysis.avg_word_count,
                        'section_count': 10,  # Would be extracted from actual analysis
                        'headings': {
                            'h1': 1,
                            'h2': 5,
                            'h3': 10
                        }
                    },
                    'engagement_metrics': {
                        'avg_time_on_page': analysis.metrics.engagement_metrics.avg_time_on_page,
                        'bounce_rate': analysis.metrics.engagement_metrics.bounce_rate,
                        'social_shares': analysis.metrics.engagement_metrics.social_shares,
                    }
                }
                competitor_data.append(data)
            
            return competitor_data
            
        except Exception as e:
            logger.error(f"❌ Error extracting competitor data: {e}")
            return []
    
    async def _identify_topic_gaps(self, 
                                   competitor_data: List[Dict[str, Any]], 
                                   target_keywords: List[str]) -> List[TopicGap]:
        """Identify topic gaps in competitor content."""
        try:
            # Use utility function to identify missing topics
            topic_gaps = identify_missing_topics(competitor_data)
            
            # Enhance with AI insights
            enhanced_gaps = await self._enhance_topic_gaps_with_ai(topic_gaps, target_keywords)
            
            return enhanced_gaps
            
        except Exception as e:
            logger.error(f"❌ Error identifying topic gaps: {e}")
            return []
    
    async def _identify_format_gaps(self, competitor_data: List[Dict[str, Any]]) -> List[FormatGap]:
        """Identify content format gaps."""
        try:
            # Use utility function to identify format gaps
            format_gaps = identify_format_gaps(competitor_data)
            
            # Enhance with additional analysis
            enhanced_gaps = []
            for gap in format_gaps:
                # Calculate effectiveness and complexity
                effectiveness = estimate_format_engagement(gap.target_format.value)
                complexity = determine_format_complexity(gap.target_format.value)
                
                # Update gap with calculated values
                gap.audience_preference = effectiveness
                gap.production_complexity = complexity
                
                enhanced_gaps.append(gap)
            
            return enhanced_gaps
            
        except Exception as e:
            logger.error(f"❌ Error identifying format gaps: {e}")
            return []
    
    async def _identify_quality_gaps(self, competitor_data: List[Dict[str, Any]]) -> List[QualityGap]:
        """Identify content quality gaps."""
        try:
            quality_gaps = []
            
            # Analyze quality distribution
            quality_scores = [comp.get('avg_quality_score', 0) for comp in competitor_data]
            avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
            
            # Identify quality gaps
            if avg_quality < 7.0:
                quality_gaps.append(QualityGap(
                    gap_type=GapType.QUALITY_GAP,
                    description=f"Overall content quality is below optimal (avg: {avg_quality:.1f})",
                    current_quality_distribution={
                        'high': len([s for s in quality_scores if s >= 8.0]),
                        'medium': len([s for s in quality_scores if 6.0 <= s < 8.0]),
                        'low': len([s for s in quality_scores if s < 6.0])
                    },
                    target_quality_score=8.5,
                    improvement_areas=[
                        "Content depth and research",
                        "Readability and structure",
                        "Visual elements and formatting",
                        "Expert insights and data"
                    ],
                    quality_benchmarks={
                        'industry_average': avg_quality,
                        'top_performer': max(quality_scores) if quality_scores else 0,
                        'recommended_target': 8.5
                    },
                    implementation_complexity=PriorityLevel.MEDIUM,
                    estimated_improvement_time="3-6 months",
                    success_metrics=[
                        "Content quality scores",
                        "User engagement metrics",
                        "SEO rankings improvement",
                        "Time on page increase"
                    ],
                ))
            
            return quality_gaps
            
        except Exception as e:
            logger.error(f"❌ Error identifying quality gaps: {e}")
            return []
    
    async def _identify_frequency_gaps(self, competitor_data: List[Dict[str, Any]]) -> List[FrequencyGap]:
        """Identify content publishing frequency gaps."""
        try:
            frequency_gaps = []
            
            # Analyze publishing frequency distribution
            frequencies = [comp.get('publishing_frequency', 'weekly') for comp in competitor_data]
            frequency_counts = {}
            for freq in frequencies:
                frequency_counts[freq] = frequency_counts.get(freq, 0) + 1
            
            # Identify frequency gaps
            most_common_frequency = max(frequency_counts.items(), key=lambda x: x[1])[0]
            
            if most_common_frequency in ['weekly', 'bi_weekly', 'monthly']:
                frequency_gaps.append(FrequencyGap(
                    gap_type=GapType.FREQUENCY_GAP,
                    description=f"Opportunity to increase publishing frequency beyond {most_common_frequency}",
                    current_frequency_distribution=frequency_counts,
                    recommended_frequency='daily' if most_common_frequency == 'weekly' else 'weekly',
                    content_volume_analysis={
                        'avg_monthly_posts': self._estimate_monthly_posts(most_common_frequency),
                        'industry_leader_posts': 30,  # Would be based on actual data
                        'volume_gap_percentage': 50.0
                    },
                    calendar_gaps=[
                        "Weekend content opportunities",
                        "Holiday content planning",
                        "Seasonal content gaps"
                    ],
                    resource_requirements=[
                        "Content creation team",
                        "Content calendar management",
                        "Quality assurance processes"
                    ],
                    implementation_complexity=PriorityLevel.MEDIUM,
                    estimated_time_to_consistency="2-4 months",
                    expected_impact_score=7.5,
                    success_metrics=[
                        "Publishing frequency consistency",
                        "Audience engagement growth",
                        "SEO traffic increase",
                        "Brand visibility improvement"
                    ],
                ))
            
            return frequency_gaps
            
        except Exception as e:
            logger.error(f"❌ Error identifying frequency gaps: {e}")
            return []
    
    def _estimate_monthly_posts(self, frequency: str) -> int:
        """Estimate monthly posts based on frequency."""
        frequency_map = {
            'daily': 30,
            'weekly': 4,
            'bi_weekly': 2,
            'monthly': 1,
            'quarterly': 0.33,
            'irregular': 2
        }
        return frequency_map.get(frequency, 4)
    
    def _get_high_priority_gaps(self, 
                               topic_gaps: List[TopicGap],
                               format_gaps: List[FormatGap],
                               quality_gaps: List[QualityGap],
                               frequency_gaps: List[FrequencyGap]) -> List[ContentGap]:
        """Get high priority gaps from all gap types."""
        try:
            high_priority_gaps = []
            
            # Add high priority topic gaps
            high_priority_gaps.extend([gap for gap in topic_gaps if gap.opportunity_score >= 8.0])
            
            # Add high priority format gaps
            high_priority_gaps.extend([gap for gap in format_gaps if gap.priority == PriorityLevel.HIGH])
            
            # Add high priority quality gaps
            high_priority_gaps.extend([gap for gap in quality_gaps if gap.implementation_complexity != PriorityLevel.LOW])
            
            # Add high priority frequency gaps
            high_priority_gaps.extend([gap for gap in frequency_gaps if gap.expected_impact_score >= 7.0])
            
            # Sort by priority score
            high_priority_gaps.sort(key=lambda x: getattr(x, 'opportunity_score', getattr(x, 'expected_impact_score', 5.0)), reverse=True)
            
            return high_priority_gaps[:10]  # Return top 10 high priority gaps
            
        except Exception as e:
            logger.error(f"❌ Error getting high priority gaps: {e}")
            return []
    
    async def _generate_gap_recommendations(self, 
                                           topic_gaps: List[TopicGap],
                                           format_gaps: List[FormatGap],
                                           quality_gaps: List[QualityGap],
                                           frequency_gaps: List[FrequencyGap]) -> List[Recommendation]:
        """Generate recommendations based on identified gaps."""
        try:
            recommendations = []
            
            # Topic gap recommendations
            if topic_gaps:
                high_value_topics = [gap for gap in topic_gaps if gap.opportunity_score >= 8.0][:3]
                recommendations.append(Recommendation(
                    type="content_strategy",
                    recommendation=f"Focus on high-value topics: {', '.join([gap.topic_name for gap in high_value_topics])}",
                    priority=PriorityLevel.HIGH,
                    estimated_impact=ImpactLevel.HIGH,
                    implementation_time="1-3 months",
                    resources_required=["Subject matter experts", "Research team", "Content writers"],
                    success_metrics=["Topic authority", "Search rankings", "Organic traffic"],
                ))
            
            # Format gap recommendations
            if format_gaps:
                high_impact_formats = [gap for gap in format_gaps if gap.audience_preference >= 7.0][:2]
                recommendations.append(Recommendation(
                    type="content_format",
                    recommendation=f"Implement high-impact formats: {', '.join([gap.target_format.value for gap in high_impact_formats])}",
                    priority=PriorityLevel.MEDIUM,
                    estimated_impact=ImpactLevel.MEDIUM,
                    implementation_time="2-4 months",
                    resources_required=get_format_resource_requirements(high_impact_formats[0].target_format.value) if high_impact_formats else [],
                    success_metrics=["Engagement metrics", "Shareability", "Brand reach"],
                ))
            
            # Quality gap recommendations
            if quality_gaps:
                recommendations.append(Recommendation(
                    type="content_quality",
                    recommendation="Implement comprehensive quality improvement program",
                    priority=PriorityLevel.HIGH,
                    estimated_impact=ImpactLevel.HIGH,
                    implementation_time="3-6 months",
                    resources_required=["Content team training", "Quality tools", "Editorial processes"],
                    success_metrics=["Content quality scores", "User satisfaction", "SEO performance"],
                ))
            
            # Frequency gap recommendations
            if frequency_gaps:
                recommendations.append(Recommendation(
                    type="publishing_frequency",
                    recommendation="Increase content publishing frequency for better market presence",
                    priority=PriorityLevel.MEDIUM,
                    estimated_impact=ImpactLevel.MEDIUM,
                    implementation_time="2-3 months",
                    resources_required=["Content calendar", "Additional writers", "Automation tools"],
                    success_metrics=["Publishing consistency", "Audience growth", "Brand visibility"],
                ))
            
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Error generating gap recommendations: {e}")
            return []
    
    async def _create_implementation_roadmap(self, 
                                            topic_gaps: List[TopicGap],
                                            format_gaps: List[FormatGap],
                                            quality_gaps: List[QualityGap],
                                            frequency_gaps: List[FrequencyGap]) -> List[Dict[str, Any]]:
        """Create implementation roadmap for addressing gaps."""
        try:
            roadmap = []
            
            # Phase 1: Quick wins (1-2 months)
            quick_wins = []
            quick_wins.extend([gap for gap in topic_gaps if gap.opportunity_score >= 9.0][:2])
            quick_wins.extend([gap for gap in format_gaps if gap.production_complexity == PriorityLevel.LOW][:1])
            
            if quick_wins:
                roadmap.append({
                    'phase': 'Quick Wins',
                    'duration': '1-2 months',
                    'gaps': [gap.topic_name if hasattr(gap, 'topic_name') else gap.target_format.value for gap in quick_wins],
                    'priority': 'High',
                    'expected_impact': 'Immediate traffic and engagement boost'
                })
            
            # Phase 2: Strategic initiatives (3-6 months)
            strategic_initiatives = []
            strategic_initiatives.extend([gap for gap in quality_gaps])
            strategic_initiatives.extend([gap for gap in format_gaps if gap.production_complexity == PriorityLevel.MEDIUM][:2])
            
            if strategic_initiatives:
                roadmap.append({
                    'phase': 'Strategic Initiatives',
                    'duration': '3-6 months',
                    'gaps': ['Quality improvement', 'Format expansion'],
                    'priority': 'Medium',
                    'expected_impact': 'Long-term competitive advantage'
                })
            
            # Phase 3: Advanced opportunities (6-12 months)
            advanced_opportunities = []
            advanced_opportunities.extend([gap for gap in format_gaps if gap.production_complexity == PriorityLevel.HIGH])
            advanced_opportunities.extend([gap for gap in frequency_gaps])
            
            if advanced_opportunities:
                roadmap.append({
                    'phase': 'Advanced Opportunities',
                    'duration': '6-12 months',
                    'gaps': ['Advanced formats', 'Frequency optimization'],
                    'priority': 'Medium',
                    'expected_impact': 'Market leadership position'
                })
            
            return roadmap
            
        except Exception as e:
            logger.error(f"❌ Error creating implementation roadmap: {e}")
            return []
    
    def _calculate_expected_impact(self, 
                                  topic_gaps: List[TopicGap],
                                  format_gaps: List[FormatGap],
                                  quality_gaps: List[QualityGap],
                                  frequency_gaps: List[FrequencyGap]) -> str:
        """Calculate expected impact of addressing all gaps."""
        try:
            total_gaps = len(topic_gaps) + len(format_gaps) + len(quality_gaps) + len(frequency_gaps)
            high_priority_count = len(self._get_high_priority_gaps(topic_gaps, format_gaps, quality_gaps, frequency_gaps))
            
            if high_priority_count >= 5:
                return "Very High"
            elif high_priority_count >= 3:
                return "High"
            elif total_gaps >= 10:
                return "Medium"
            else:
                return "Low"
                
        except Exception as e:
            logger.error(f"❌ Error calculating expected impact: {e}")
            return "Medium"
    
    def _calculate_confidence_score(self, competitor_data: List[Dict[str, Any]]) -> float:
        """Calculate confidence score for the gap analysis."""
        try:
            base_confidence = 0.8
            
            # Adjust based on data quality
            if len(competitor_data) >= 5:
                base_confidence += 0.1
            
            # Check if competitors have quality data
            quality_data_count = sum(1 for comp in competitor_data if comp.get('avg_quality_score', 0) > 0)
            if quality_data_count >= len(competitor_data) * 0.8:
                base_confidence += 0.1
            
            return min(1.0, base_confidence)
            
        except Exception as e:
            logger.error(f"❌ Error calculating confidence score: {e}")
            return 0.7
    
    @inject_ai_provider
    async def _enhance_topic_gaps_with_ai(self, ai_provider, topic_gaps: List[TopicGap], target_keywords: List[str]) -> List[TopicGap]:
        """Enhance topic gaps with AI-generated insights."""
        try:
            enhanced_gaps = []
            
            for gap in topic_gaps:
                # Generate AI insights for each topic gap
                prompt = f"""
                Analyze this topic gap and provide additional insights:
                
                Topic: {gap.topic_name}
                Category: {gap.topic_category}
                Current Coverage: {len(gap.competitor_coverage)} competitors
                Opportunity Score: {gap.opportunity_score}
                Target Keywords: {', '.join(target_keywords)}
                
                Provide:
                1. Additional content angles not considered
                2. Expert quotes or statistics to include
                3. Data sources for research
                4. Seasonal trends for this topic
                5. Related subtopics to explore
                
                Format as structured JSON.
                """
                
                schema = {
                    "type": "object",
                    "properties": {
                        "additional_angles": {"type": "array", "items": {"type": "string"}},
                        "expert_insights": {"type": "array", "items": {"type": "string"}},
                        "data_sources": {"type": "array", "items": {"type": "string"}},
                        "seasonal_trends": {"type": "string"},
                        "related_subtopics": {"type": "array", "items": {"type": "string"}}
                    }
                }
                
                try:
                    ai_response = await ai_provider.generate_response(prompt, schema)
                    if isinstance(ai_response, dict):
                        # Enhance gap with AI insights
                        gap.content_angles.extend(ai_response.get('additional_angles', []))
                        gap.expert_quotes.extend(ai_response.get('expert_insights', []))
                        gap.data_sources.extend(ai_response.get('data_sources', []))
                except Exception as e:
                    logger.warning(f"AI enhancement failed for topic gap {gap.topic_name}: {e}")
                
                enhanced_gaps.append(gap)
            
            return enhanced_gaps
            
        except Exception as e:
            logger.error(f"❌ Error enhancing topic gaps with AI: {e}")
            return topic_gaps
    
    async def validate_content_gap_data(self, data: Dict[str, Any]) -> List[ValidationError]:
        """Validate content gap analysis data."""
        try:
            return validate_content_gap_data(data)
        except Exception as e:
            logger.error(f"❌ Error validating content gap data: {e}")
            return [ValidationError(
                field='validation',
                message=f'Validation error: {str(e)}',
                value=data,
                error_code='VALIDATION_ERROR'
            )]
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check for the service."""
        try:
            health_status = {
                'service': self.service_name,
                'version': self.version,
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'checks': {}
            }
            
            # Check topic distribution analysis
            try:
                test_data = [{'topics': [{'topic': 'test'}, {'topic': 'example'}]}]
                result = analyze_topic_distribution(test_data)
                health_status['checks']['topic_distribution'] = {
                    'status': 'healthy',
                    'message': 'Topic distribution analysis working'
                }
            except Exception as e:
                health_status['checks']['topic_distribution'] = {
                    'status': 'error',
                    'message': str(e)
                }
                health_status['status'] = 'degraded'
            
            # Check format analysis
            try:
                test_competitors = [{'content_types': ['blog', 'article']}]
                result = analyze_content_formats(test_competitors)
                health_status['checks']['format_analysis'] = {
                    'status': 'healthy',
                    'message': 'Format analysis working'
                }
            except Exception as e:
                health_status['checks']['format_analysis'] = {
                    'status': 'error',
                    'message': str(e)
                }
                health_status['status'] = 'degraded'
            
            return health_status
            
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            return {
                'service': self.service_name,
                'version': self.version,
                'status': 'unhealthy',
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e)
            }
    
    async def get_service_info(self) -> Dict[str, Any]:
        """Get service information."""
        return {
            'service_name': self.service_name,
            'version': self.version,
            'description': 'Specialized service for content gap analysis',
            'capabilities': [
                'Topic gap analysis',
                'Format gap analysis',
                'Quality gap analysis',
                'Frequency gap analysis',
                'Content opportunity identification',
                'Implementation roadmap creation'
            ],
            'dependencies': [
                'AI providers for insights enhancement'
            ],
            'supported_formats': [
                'ContentGap',
                'TopicGap',
                'FormatGap',
                'QualityGap',
                'FrequencyGap',
                'ContentGapAnalysis'
            ]
        }
