"""
SEO Analysis Service

Specialized service for SEO analysis, gap identification, and optimization recommendations.
Handles keyword gaps, technical SEO gaps, backlink gaps, and SEO performance analysis.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger
import asyncio

from ..models.seo_analysis import (
    SEOAnalysis,
    SEOGap,
    KeywordGap,
    TechnicalSEOGap,
    BacklinkGap,
    SEOGapType,
    SEOComparison,
    SEORecommendation,
    PriorityLevel,
    ImpactLevel,
    KeywordDifficulty,
    SearchIntent,
)
from ..models.competitor_models import CompetitorAnalysis
from ..models.shared import (
    AnalysisStatus,
    ValidationError,
    Recommendation,
)
from ..utils.seo_utils import (
    analyze_seo_metrics,
    calculate_seo_score,
    analyze_keyword_gaps,
    estimate_search_volume,
    estimate_keyword_difficulty,
    determine_search_intent,
    calculate_keyword_gap_opportunity,
    estimate_keyword_traffic_potential,
    estimate_content_difficulty,
    determine_keyword_competition_level,
    estimate_keyword_trend,
    estimate_seasonal_pattern,
    get_related_keywords,
    generate_keyword_content_suggestions,
    calculate_keyword_priority,
    analyze_technical_seo_gaps,
    get_technical_requirements,
    get_seo_tools_for_gap,
    get_expected_improvement,
    get_implementation_steps,
    get_monitoring_metrics,
    validate_seo_data,
)
from ..utils.data_transformers import (
    transform_seo_gaps_to_analysis,
)
from ..dependencies import inject_ai_provider


class SEOAnalysisService:
    """
    Specialized service for SEO analysis.
    
    This service handles:
    - Keyword gap analysis and identification
    - Technical SEO gap assessment
    - Backlink gap analysis
    - SEO performance comparison
    - SEO optimization recommendations
    """
    
    def __init__(self):
        """Initialize the SEO analysis service."""
        self.service_name = "SEOAnalysisService"
        self.version = "1.0.0"
        logger.info(f"✅ {self.service_name} v{self.version} initialized")
    
    async def analyze_seo_gaps(self, 
                               competitor_analyses: List[CompetitorAnalysis],
                               target_keywords: Optional[List[str]] = None,
                               industry: str = "") -> SEOAnalysis:
        """
        Analyze SEO gaps across competitors.
        
        Args:
            competitor_analyses: List of competitor analyses
            target_keywords: Target keywords for SEO analysis
            industry: Industry category
            
        Returns:
            SEOAnalysis: Comprehensive SEO gap analysis
        """
        try:
            logger.info(f"🔍 Analyzing SEO gaps for {len(competitor_analyses)} competitors")
            
            # Extract competitor data for analysis
            competitor_data = self._extract_competitor_data(competitor_analyses)
            
            # Identify different types of SEO gaps
            keyword_gaps = await self._identify_keyword_gaps(competitor_data, target_keywords or [])
            technical_seo_gaps = await self._identify_technical_seo_gaps(competitor_data)
            backlink_gaps = await self._identify_backlink_gaps(competitor_data)
            
            # Create SEO comparisons
            seo_comparisons = await self._create_seo_comparisons(competitor_data)
            
            # Calculate overall SEO scores
            overall_seo_scores = self._calculate_overall_seo_scores(competitor_data)
            
            # Create SEO analysis
            seo_analysis = SEOAnalysis(
                industry=industry,
                competitor_urls=[comp.profile.url for comp in competitor_analyses],
                analysis_date=datetime.utcnow(),
                total_gaps_identified=len(keyword_gaps) + len(technical_seo_gaps) + len(backlink_gaps),
                gaps_by_type={
                    SEOGapType.KEYWORD_GAP: len(keyword_gaps),
                    SEOGapType.TECHNICAL_SEO_GAP: len(technical_seo_gaps),
                    SEOGapType.BACKLINK_GAP: len(backlink_gaps),
                },
                keyword_gaps=keyword_gaps,
                technical_seo_gaps=technical_seo_gaps,
                backlink_gaps=backlink_gaps,
                seo_comparisons=seo_comparisons,
                overall_seo_scores=overall_seo_scores,
                high_priority_gaps=self._get_high_priority_seo_gaps(keyword_gaps, technical_seo_gaps, backlink_gaps),
                recommendations=await self._generate_seo_recommendations(keyword_gaps, technical_seo_gaps, backlink_gaps),
                implementation_roadmap=await self._create_seo_roadmap(keyword_gaps, technical_seo_gaps, backlink_gaps),
                expected_impact_timeline=self._calculate_expected_impact_timeline(keyword_gaps, technical_seo_gaps, backlink_gaps),
                confidence_score=self._calculate_confidence_score(competitor_data),
            )
            
            logger.info("✅ SEO gap analysis completed")
            return seo_analysis
            
        except Exception as e:
            logger.error(f"❌ Error in SEO gap analysis: {e}")
            raise
    
    async def analyze_keyword_gaps(self, 
                                  competitor_analyses: List[CompetitorAnalysis],
                                  target_keywords: Optional[List[str]] = None) -> List[KeywordGap]:
        """
        Analyze keyword gaps specifically.
        
        Args:
            competitor_analyses: List of competitor analyses
            target_keywords: Target keywords for analysis
            
        Returns:
            List[KeywordGap]: List of keyword gaps
        """
        try:
            logger.info("🔍 Analyzing keyword gaps")
            
            # Extract competitor data
            competitor_data = self._extract_competitor_data(competitor_analyses)
            
            # Identify keyword gaps
            keyword_gaps = await self._identify_keyword_gaps(competitor_data, target_keywords or [])
            
            logger.info(f"✅ Identified {len(keyword_gaps)} keyword gaps")
            return keyword_gaps
            
        except Exception as e:
            logger.error(f"❌ Error analyzing keyword gaps: {e}")
            raise
    
    async def analyze_technical_seo_gaps(self, competitor_analyses: List[CompetitorAnalysis]) -> List[TechnicalSEOGap]:
        """
        Analyze technical SEO gaps specifically.
        
        Args:
            competitor_analyses: List of competitor analyses
            
        Returns:
            List[TechnicalSEOGap]: List of technical SEO gaps
        """
        try:
            logger.info("🔍 Analyzing technical SEO gaps")
            
            # Extract competitor data
            competitor_data = self._extract_competitor_data(competitor_analyses)
            
            # Identify technical SEO gaps
            technical_gaps = await self._identify_technical_seo_gaps(competitor_data)
            
            logger.info(f"✅ Identified {len(technical_gaps)} technical SEO gaps")
            return technical_gaps
            
        except Exception as e:
            logger.error(f"❌ Error analyzing technical SEO gaps: {e}")
            raise
    
    def _extract_competitor_data(self, competitor_analyses: List[CompetitorAnalysis]) -> List[Dict[str, Any]]:
        """Extract relevant SEO data from competitor analyses."""
        try:
            competitor_data = []
            
            for analysis in competitor_analyses:
                data = {
                    'url': analysis.profile.url,
                    'name': analysis.profile.name,
                    'domain_authority': analysis.metrics.seo_metrics.domain_authority,
                    'page_authority': analysis.metrics.seo_metrics.page_authority,
                    'page_speed': analysis.metrics.seo_metrics.page_speed,
                    'mobile_friendly': analysis.metrics.seo_metrics.mobile_friendly,
                    'ssl_certificate': analysis.metrics.seo_metrics.ssl_certificate,
                    'indexed_pages': analysis.metrics.seo_metrics.indexed_pages,
                    'backlinks_count': analysis.metrics.seo_metrics.backlinks_count,
                    'organic_traffic': analysis.metrics.seo_metrics.organic_traffic,
                    'keyword_rankings': analysis.metrics.seo_metrics.keyword_rankings,
                    'structured_data': True,  # Would be extracted from actual analysis
                    'top_keywords': analysis.metrics.content_analysis.top_keywords,
                    'content_count': analysis.metrics.content_analysis.content_count,
                    'avg_quality_score': analysis.metrics.content_analysis.avg_quality_score,
                }
                competitor_data.append(data)
            
            return competitor_data
            
        except Exception as e:
            logger.error(f"❌ Error extracting competitor SEO data: {e}")
            return []
    
    async def _identify_keyword_gaps(self, 
                                    competitor_data: List[Dict[str, Any]], 
                                    target_keywords: List[str]) -> List[KeywordGap]:
        """Identify keyword gaps in competitor SEO strategies."""
        try:
            # Use utility function to analyze keyword gaps
            keyword_gaps = analyze_keyword_gaps(competitor_data, target_keywords)
            
            # Enhance with additional analysis
            enhanced_gaps = []
            for gap in keyword_gaps:
                # Calculate additional metrics
                content_difficulty = estimate_content_difficulty(gap.keyword_difficulty)
                competition_level = determine_keyword_competition_level(gap.competitor_rankings)
                
                # Update gap with calculated values
                gap.content_difficulty = content_difficulty
                gap.competition_level = competition_level
                
                enhanced_gaps.append(gap)
            
            return enhanced_gaps
            
        except Exception as e:
            logger.error(f"❌ Error identifying keyword gaps: {e}")
            return []
    
    async def _identify_technical_seo_gaps(self, competitor_data: List[Dict[str, Any]]) -> List[TechnicalSEOGap]:
        """Identify technical SEO gaps."""
        try:
            # Use utility function to analyze technical SEO gaps
            technical_gaps = analyze_technical_seo_gaps(competitor_data)
            
            # Enhance with additional analysis
            enhanced_gaps = []
            for gap in technical_gaps:
                # Get technical requirements and tools
                requirements = get_technical_requirements(gap.issue_description)
                tools = get_seo_tools_for_gap(gap.issue_description)
                improvement = get_expected_improvement(gap.issue_description)
                steps = get_implementation_steps(gap.issue_description)
                metrics = get_monitoring_metrics(gap.issue_description)
                
                # Update gap with technical details
                gap.technical_requirements = requirements
                gap.tools_needed = tools
                gap.expected_improvement = improvement
                gap.implementation_steps = steps
                gap.monitoring_metrics = metrics
                
                enhanced_gaps.append(gap)
            
            return enhanced_gaps
            
        except Exception as e:
            logger.error(f"❌ Error identifying technical SEO gaps: {e}")
            return []
    
    async def _identify_backlink_gaps(self, competitor_data: List[Dict[str, Any]]) -> List[BacklinkGap]:
        """Identify backlink gaps."""
        try:
            backlink_gaps = []
            
            # Analyze backlink distribution
            backlink_counts = [comp.get('backlinks_count', 0) for comp in competitor_data]
            avg_backlinks = sum(backlink_counts) / len(backlink_counts) if backlink_counts else 0
            max_backlinks = max(backlink_counts) if backlink_counts else 0
            
            # Identify backlink gaps
            if avg_backlinks > 1000:  # Significant backlink activity
                backlink_gaps.append(BacklinkGap(
                    gap_type=SEOGapType.BACKLINK_GAP,
                    description=f"Backlink gap identified - competitors average {avg_backlinks:.0f} backlinks",
                    current_backlink_profile={
                        'total_backlinks': 0,  # Would be your actual backlink count
                        'domain_authority_distribution': {
                            'high': len([da for da in [comp.get('domain_authority', 0) for comp in competitor_data] if da >= 70]),
                            'medium': len([da for da in [comp.get('domain_authority', 0) for comp in competitor_data] if 40 <= da < 70]),
                            'low': len([da for da in [comp.get('domain_authority', 0) for comp in competitor_data] if da < 40])
                        }
                    },
                    competitor_backlink_analysis={
                        'average_backlinks': avg_backlinks,
                        'top_performer_backlinks': max_backlinks,
                        'backlink_growth_rate': 5.0,  # Would be calculated from historical data
                    },
                    link_building_opportunities=[
                        "Guest posting on industry blogs",
                        "Broken link building",
                        "Resource page link building",
                        "Digital PR campaigns",
                        "Partnership opportunities"
                    ],
                    anchor_text_optimization={
                        'current_distribution': {'branded': 40, 'exact_match': 10, 'partial_match': 30, 'naked_url': 20},
                        'recommended_distribution': {'branded': 50, 'exact_match': 5, 'partial_match': 25, 'naked_url': 20}
                    },
                    implementation_complexity=PriorityLevel.HIGH,
                    estimated_time_to_impact="6-12 months",
                    success_metrics=[
                        "Backlink count growth",
                        "Domain authority improvement",
                        "Referral traffic increase",
                        "Search ranking improvement"
                    ],
                ))
            
            return backlink_gaps
            
        except Exception as e:
            logger.error(f"❌ Error identifying backlink gaps: {e}")
            return []
    
    async def _create_seo_comparisons(self, competitor_data: List[Dict[str, Any]]) -> List[SEOComparison]:
        """Create SEO comparisons between competitors."""
        try:
            comparisons = []
            
            # Compare key SEO metrics
            metrics_to_compare = [
                'domain_authority',
                'page_speed',
                'mobile_friendly',
                'backlinks_count',
                'organic_traffic',
                'keyword_rankings'
            ]
            
            for metric in metrics_to_compare:
                values = [comp.get(metric, 0) for comp in competitor_data]
                if values:
                    comparison = SEOComparison(
                        metric_name=metric,
                        your_value=0,  # Would be your actual value
                        competitor_values={comp.get('url', ''): comp.get(metric, 0) for comp in competitor_data},
                        industry_average=sum(values) / len(values),
                        top_quartile=sorted(values)[int(len(values) * 0.75)] if len(values) > 4 else max(values),
                        percentile_rank=0,  # Would calculate your percentile
                        performance_gap=0,  # Would calculate gap to leader
                        improvement_potential=0,  # Would calculate potential
                        benchmark_date=datetime.utcnow(),
                        recommendations=[],  # Would generate metric-specific recommendations
                    )
                    comparisons.append(comparison)
            
            return comparisons
            
        except Exception as e:
            logger.error(f"❌ Error creating SEO comparisons: {e}")
            return []
    
    def _calculate_overall_seo_scores(self, competitor_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate overall SEO scores for competitors."""
        try:
            seo_scores = {}
            
            for comp in competitor_data:
                url = comp.get('url', '')
                seo_metrics = {
                    'domain_authority': comp.get('domain_authority', 0),
                    'page_speed': comp.get('page_speed', 0),
                    'mobile_friendly': comp.get('mobile_friendly', False),
                    'ssl_certificate': comp.get('ssl_certificate', False),
                    'backlinks_count': comp.get('backlinks_count', 0),
                    'indexed_pages': comp.get('indexed_pages', 0),
                    'organic_traffic': comp.get('organic_traffic', 0),
                    'keyword_rankings': comp.get('keyword_rankings', 0),
                }
                
                score = calculate_seo_score(seo_metrics)
                seo_scores[url] = score
            
            return seo_scores
            
        except Exception as e:
            logger.error(f"❌ Error calculating overall SEO scores: {e}")
            return {}
    
    def _get_high_priority_seo_gaps(self, 
                                   keyword_gaps: List[KeywordGap],
                                   technical_seo_gaps: List[TechnicalSEOGap],
                                   backlink_gaps: List[BacklinkGap]) -> List[SEOGap]:
        """Get high priority SEO gaps from all gap types."""
        try:
            high_priority_gaps = []
            
            # Add high priority keyword gaps
            high_priority_gaps.extend([gap for gap in keyword_gaps if gap.priority == PriorityLevel.HIGH])
            
            # Add high priority technical SEO gaps
            high_priority_gaps.extend([gap for gap in technical_seo_gaps if gap.impact_level == ImpactLevel.HIGH])
            
            # Add backlink gaps (always high priority)
            high_priority_gaps.extend(backlink_gaps)
            
            # Sort by priority score
            high_priority_gaps.sort(key=lambda x: getattr(x, 'priority_score', getattr(x, 'opportunity_score', 5.0)), reverse=True)
            
            return high_priority_gaps[:10]  # Return top 10 high priority gaps
            
        except Exception as e:
            logger.error(f"❌ Error getting high priority SEO gaps: {e}")
            return []
    
    async def _generate_seo_recommendations(self, 
                                           keyword_gaps: List[KeywordGap],
                                           technical_seo_gaps: List[TechnicalSEOGap],
                                           backlink_gaps: List[BacklinkGap]) -> List[Recommendation]:
        """Generate SEO recommendations based on identified gaps."""
        try:
            recommendations = []
            
            # Keyword gap recommendations
            if keyword_gaps:
                high_value_keywords = [gap for gap in keyword_gaps if gap.opportunity_score >= 8.0][:3]
                recommendations.append(Recommendation(
                    type="keyword_strategy",
                    recommendation=f"Target high-value keywords: {', '.join([gap.keyword for gap in high_value_keywords])}",
                    priority=PriorityLevel.HIGH,
                    estimated_impact=ImpactLevel.HIGH,
                    implementation_time="1-3 months",
                    resources_required=["Content team", "SEO tools", "Keyword research"],
                    success_metrics=["Keyword rankings", "Organic traffic", "Conversion rate"],
                ))
            
            # Technical SEO recommendations
            if technical_seo_gaps:
                critical_issues = [gap for gap in technical_seo_gaps if gap.impact_level == ImpactLevel.HIGH][:2]
                recommendations.append(Recommendation(
                    type="technical_seo",
                    recommendation=f"Fix critical technical SEO issues: {', '.join([gap.issue_description for gap in critical_issues])}",
                    priority=PriorityLevel.HIGH,
                    estimated_impact=ImpactLevel.HIGH,
                    implementation_time="1-2 months",
                    resources_required=["Development team", "SEO tools", "Technical expertise"],
                    success_metrics=["Page speed", "Mobile usability", "Index coverage"],
                ))
            
            # Backlink recommendations
            if backlink_gaps:
                recommendations.append(Recommendation(
                    type="link_building",
                    recommendation="Implement comprehensive link building strategy",
                    priority=PriorityLevel.MEDIUM,
                    estimated_impact=ImpactLevel.HIGH,
                    implementation_time="6-12 months",
                    resources_required=["Outreach team", "Content creation", "SEO tools"],
                    success_metrics=["Backlink growth", "Domain authority", "Referral traffic"],
                ))
            
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Error generating SEO recommendations: {e}")
            return []
    
    async def _create_seo_roadmap(self, 
                                  keyword_gaps: List[KeywordGap],
                                  technical_seo_gaps: List[TechnicalSEOGap],
                                  backlink_gaps: List[BacklinkGap]) -> List[Dict[str, Any]]:
        """Create implementation roadmap for addressing SEO gaps."""
        try:
            roadmap = []
            
            # Phase 1: Technical fixes (1-2 months)
            if technical_seo_gaps:
                critical_technical = [gap for gap in technical_seo_gaps if gap.impact_level == ImpactLevel.HIGH]
                if critical_technical:
                    roadmap.append({
                        'phase': 'Technical Foundation',
                        'duration': '1-2 months',
                        'gaps': [gap.issue_description for gap in critical_technical],
                        'priority': 'High',
                        'expected_impact': 'Improved crawlability and user experience'
                    })
            
            # Phase 2: Keyword targeting (2-4 months)
            if keyword_gaps:
                high_value_keywords = [gap for gap in keyword_gaps if gap.opportunity_score >= 8.0][:5]
                if high_value_keywords:
                    roadmap.append({
                        'phase': 'Keyword Targeting',
                        'duration': '2-4 months',
                        'gaps': [gap.keyword for gap in high_value_keywords],
                        'priority': 'High',
                        'expected_impact': 'Increased organic traffic and rankings'
                    })
            
            # Phase 3: Link building (6-12 months)
            if backlink_gaps:
                roadmap.append({
                    'phase': 'Authority Building',
                    'duration': '6-12 months',
                    'gaps': ['Backlink gap closure'],
                    'priority': 'Medium',
                    'expected_impact': 'Improved domain authority and rankings'
                })
            
            return roadmap
            
        except Exception as e:
            logger.error(f"❌ Error creating SEO roadmap: {e}")
            return []
    
    def _calculate_expected_impact_timeline(self, 
                                          keyword_gaps: List[KeywordGap],
                                          technical_seo_gaps: List[TechnicalSEOGap],
                                          backlink_gaps: List[BacklinkGap]) -> str:
        """Calculate expected impact timeline for addressing SEO gaps."""
        try:
            total_gaps = len(keyword_gaps) + len(technical_seo_gaps) + len(backlink_gaps)
            high_priority_count = len(self._get_high_priority_seo_gaps(keyword_gaps, technical_seo_gaps, backlink_gaps))
            
            if technical_seo_gaps:
                return "1-3 months"  # Technical fixes show quick results
            elif high_priority_count >= 5:
                return "3-6 months"
            elif total_gaps >= 10:
                return "6-9 months"
            else:
                return "2-4 months"
                
        except Exception as e:
            logger.error(f"❌ Error calculating expected impact timeline: {e}")
            return "3-6 months"
    
    def _calculate_confidence_score(self, competitor_data: List[Dict[str, Any]]) -> float:
        """Calculate confidence score for the SEO analysis."""
        try:
            base_confidence = 0.8
            
            # Adjust based on data quality
            if len(competitor_data) >= 5:
                base_confidence += 0.1
            
            # Check if competitors have comprehensive SEO data
            complete_data_count = sum(1 for comp in competitor_data 
                                    if comp.get('domain_authority', 0) > 0 and 
                                       comp.get('backlinks_count', 0) > 0)
            if complete_data_count >= len(competitor_data) * 0.8:
                base_confidence += 0.1
            
            return min(1.0, base_confidence)
            
        except Exception as e:
            logger.error(f"❌ Error calculating confidence score: {e}")
            return 0.7
    
    @inject_ai_provider
    async def enhance_keyword_analysis_with_ai(self, ai_provider, keyword_gaps: List[KeywordGap]) -> List[KeywordGap]:
        """Enhance keyword analysis with AI-generated insights."""
        try:
            enhanced_gaps = []
            
            for gap in keyword_gaps:
                # Generate AI insights for each keyword gap
                prompt = f"""
                Analyze this keyword gap and provide additional insights:
                
                Keyword: {gap.keyword}
                Search Volume: {gap.search_volume}
                Difficulty: {gap.keyword_difficulty}
                Intent: {gap.search_intent}
                Opportunity Score: {gap.opportunity_score}
                
                Provide:
                1. Long-tail keyword variations
                2. Content format recommendations
                3. Seasonal trends and timing
                4. Competitor analysis insights
                5. Ranking difficulty factors
                
                Format as structured JSON.
                """
                
                schema = {
                    "type": "object",
                    "properties": {
                        "long_tail_variations": {"type": "array", "items": {"type": "string"}},
                        "content_formats": {"type": "array", "items": {"type": "string"}},
                        "seasonal_insights": {"type": "string"},
                        "competitor_insights": {"type": "array", "items": {"type": "string"}},
                        "ranking_factors": {"type": "array", "items": {"type": "string"}}
                    }
                }
                
                try:
                    ai_response = await ai_provider.generate_response(prompt, schema)
                    if isinstance(ai_response, dict):
                        # Enhance gap with AI insights
                        gap.related_keywords.extend(ai_response.get('long_tail_variations', []))
                        gap.content_suggestions.extend(ai_response.get('content_formats', []))
                except Exception as e:
                    logger.warning(f"AI enhancement failed for keyword gap {gap.keyword}: {e}")
                
                enhanced_gaps.append(gap)
            
            return enhanced_gaps
            
        except Exception as e:
            logger.error(f"❌ Error enhancing keyword analysis with AI: {e}")
            return keyword_gaps
    
    async def validate_seo_data(self, data: Dict[str, Any]) -> List[ValidationError]:
        """Validate SEO analysis data."""
        try:
            return validate_seo_data(data)
        except Exception as e:
            logger.error(f"❌ Error validating SEO data: {e}")
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
            
            # Check SEO metrics analysis
            try:
                test_data = [{'domain_authority': 50, 'page_speed': 75, 'mobile_friendly': True}]
                result = analyze_seo_metrics(test_data)
                health_status['checks']['seo_metrics_analysis'] = {
                    'status': 'healthy',
                    'message': 'SEO metrics analysis working'
                }
            except Exception as e:
                health_status['checks']['seo_metrics_analysis'] = {
                    'status': 'error',
                    'message': str(e)
                }
                health_status['status'] = 'degraded'
            
            # Check keyword gap analysis
            try:
                test_competitors = [{'url': 'example.com', 'keyword_rankings': {'test': 10}}]
                result = analyze_keyword_gaps(test_competitors, ['test'])
                health_status['checks']['keyword_gap_analysis'] = {
                    'status': 'healthy',
                    'message': 'Keyword gap analysis working'
                }
            except Exception as e:
                health_status['checks']['keyword_gap_analysis'] = {
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
            'description': 'Specialized service for SEO analysis',
            'capabilities': [
                'Keyword gap analysis',
                'Technical SEO gap analysis',
                'Backlink gap analysis',
                'SEO performance comparison',
                'SEO optimization recommendations',
                'Implementation roadmap creation'
            ],
            'dependencies': [
                'AI providers for insights enhancement'
            ],
            'supported_formats': [
                'SEOAnalysis',
                'KeywordGap',
                'TechnicalSEOGap',
                'BacklinkGap',
                'SEOComparison'
            ]
        }
