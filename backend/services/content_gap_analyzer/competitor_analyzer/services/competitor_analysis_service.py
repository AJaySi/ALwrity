"""
Competitor Analysis Service

Specialized service for analyzing individual competitors and their profiles.
Handles competitor data extraction, validation, and basic analysis.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger
import asyncio

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
from ..models.shared import (
    AnalysisStatus,
    ValidationError,
)
from ..utils.competitor_utils import (
    validate_competitor_url,
    normalize_competitor_urls,
    extract_domain_from_url,
    categorize_competitor_size,
    determine_competitor_type,
    calculate_competition_score,
    assess_domain_authority_tier,
    assess_page_speed_tier,
    assess_content_quality_tier,
    extract_competitor_insights,
    create_competitor_profile,
    create_competitor_metrics,
    validate_competitor_data,
    create_fallback_competitor_analysis,
)
from ..utils.data_transformers import (
    transform_engagement_metrics,
    transform_seo_metrics,
    transform_content_analysis,
)
from ..dependencies import inject_ai_provider, inject_external_service


class CompetitorAnalysisService:
    """
    Specialized service for competitor analysis.
    
    This service handles:
    - Individual competitor data extraction
    - Competitor profile creation and validation
    - Basic competitor metrics calculation
    - Competitor insights generation
    """
    
    def __init__(self):
        """Initialize the competitor analysis service."""
        self.service_name = "CompetitorAnalysisService"
        self.version = "1.0.0"
        logger.info(f"✅ {self.service_name} v{self.version} initialized")
    
    async def analyze_single_competitor(self, 
                                      url: str, 
                                      industry: str = "",
                                      target_keywords: Optional[List[str]] = None) -> CompetitorAnalysis:
        """
        Analyze a single competitor in detail.
        
        Args:
            url: Competitor URL to analyze
            industry: Industry category
            target_keywords: Target keywords for analysis
            
        Returns:
            CompetitorAnalysis: Detailed competitor analysis
        """
        try:
            logger.info(f"🔍 Analyzing competitor: {url}")
            
            # Validate URL
            is_valid, error = validate_competitor_url(url)
            if not is_valid:
                raise ValueError(f"Invalid competitor URL: {error}")
            
            # Create competitor profile
            profile = await self._create_competitor_profile(url, industry, target_keywords or [])
            
            # Extract competitor metrics
            metrics = await self._extract_competitor_metrics(url, profile)
            
            # Generate competitor insights
            insights = await self._generate_competitor_insights(profile, metrics)
            
            # Create competitor analysis
            analysis = CompetitorAnalysis(
                profile=profile,
                metrics=metrics,
                strengths=insights.get('strengths', []),
                weaknesses=insights.get('weaknesses', []),
                opportunities=insights.get('opportunities', []),
                threats=insights.get('threats', []),
                content_suggestions=await self._generate_content_suggestions(profile, metrics),
                competitive_advantages=insights.get('competitive_advantages', []),
                analysis_date=datetime.utcnow(),
                confidence_score=self._calculate_confidence_score(profile, metrics),
            )
            
            logger.info(f"✅ Competitor analysis completed for: {url}")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Error analyzing competitor {url}: {e}")
            # Return fallback analysis
            fallback_data = create_fallback_competitor_analysis(url)
            return CompetitorAnalysis(
                profile=CompetitorProfile(url=url, name="Unknown"),
                metrics=CompetitorMetrics(
                    engagement_metrics=EngagementMetrics(),
                    seo_metrics=SEOMetrics(),
                    content_analysis=ContentAnalysis()
                ),
                analysis_date=datetime.utcnow(),
                confidence_score=0.3,
            )
    
    async def analyze_multiple_competitors(self, 
                                         urls: List[str], 
                                         industry: str = "",
                                         target_keywords: Optional[List[str]] = None,
                                         max_concurrent: int = 5) -> List[CompetitorAnalysis]:
        """
        Analyze multiple competitors concurrently.
        
        Args:
            urls: List of competitor URLs
            industry: Industry category
            target_keywords: Target keywords for analysis
            max_concurrent: Maximum concurrent analyses
            
        Returns:
            List[CompetitorAnalysis]: List of competitor analyses
        """
        try:
            logger.info(f"🔍 Analyzing {len(urls)} competitors concurrently")
            
            # Normalize and validate URLs
            normalized_urls = normalize_competitor_urls(urls)
            if not normalized_urls:
                raise ValueError("No valid competitor URLs provided")
            
            # Create semaphore for concurrency control
            semaphore = asyncio.Semaphore(max_concurrent)
            
            async def analyze_with_semaphore(url: str) -> CompetitorAnalysis:
                async with semaphore:
                    return await self.analyze_single_competitor(url, industry, target_keywords)
            
            # Run analyses concurrently
            tasks = [analyze_with_semaphore(url) for url in normalized_urls]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions and return successful analyses
            successful_analyses = []
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"❌ Failed to analyze competitor: {result}")
                else:
                    successful_analyses.append(result)
            
            logger.info(f"✅ Completed {len(successful_analyses)} competitor analyses")
            return successful_analyses
            
        except Exception as e:
            logger.error(f"❌ Error in multiple competitor analysis: {e}")
            raise
    
    async def _create_competitor_profile(self, 
                                       url: str, 
                                       industry: str, 
                                       target_keywords: List[str]) -> CompetitorProfile:
        """Create competitor profile from URL and industry."""
        try:
            # Extract basic information
            domain = extract_domain_from_url(url)
            name = domain.replace('www.', '').title() if domain else "Unknown"
            
            # Determine competitor type and size
            competitor_type = determine_competitor_type(url, industry, target_keywords)
            
            # Create profile
            profile = create_competitor_profile(
                url=url,
                name=name,
                industry=industry,
                target_keywords=target_keywords,
                competitor_type=competitor_type,
            )
            
            return profile
            
        except Exception as e:
            logger.error(f"❌ Error creating competitor profile: {e}")
            raise
    
    async def _extract_competitor_metrics(self, 
                                        url: str, 
                                        profile: CompetitorProfile) -> CompetitorMetrics:
        """Extract competitor metrics from various sources."""
        try:
            # Try to get data from website analyzer
            website_data = await self._get_website_data(url)
            
            # Transform data to metrics
            engagement_metrics = transform_engagement_metrics(website_data.get('engagement', {}))
            seo_metrics = transform_seo_metrics(website_data.get('seo', {}))
            content_analysis = transform_content_analysis(website_data.get('content', {}))
            
            # Create metrics
            metrics = create_competitor_metrics(
                engagement_data=website_data.get('engagement', {}),
                seo_data=website_data.get('seo', {}),
                content_data=website_data.get('content', {}),
                estimated_monthly_traffic=website_data.get('traffic', {}).get('monthly', 0),
                market_share_percentage=website_data.get('market_share', 0.0),
            )
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Error extracting competitor metrics: {e}")
            # Return default metrics
            return CompetitorMetrics(
                engagement_metrics=EngagementMetrics(),
                seo_metrics=SEOMetrics(),
                content_analysis=ContentAnalysis(),
            )
    
    async def _generate_competitor_insights(self, 
                                           profile: CompetitorProfile, 
                                           metrics: CompetitorMetrics) -> Dict[str, List[str]]:
        """Generate insights from competitor profile and metrics."""
        try:
            # Create analysis data for insights extraction
            analysis_data = {
                'url': profile.url,
                'name': profile.name,
                'competitor_type': profile.competitor_type,
                'domain_authority': metrics.seo_metrics.domain_authority,
                'page_speed': metrics.seo_metrics.page_speed,
                'avg_quality_score': metrics.content_analysis.avg_quality_score,
                'content_count': metrics.content_analysis.content_count,
                'mobile_friendly': metrics.seo_metrics.mobile_friendly,
                'social_shares': metrics.engagement_metrics.social_shares,
                'backlinks_count': metrics.seo_metrics.backlinks_count,
            }
            
            # Extract insights
            insights = extract_competitor_insights(analysis_data)
            
            return insights
            
        except Exception as e:
            logger.error(f"❌ Error generating competitor insights: {e}")
            return {
                'strengths': [],
                'weaknesses': [],
                'opportunities': [],
                'threats': [],
                'competitive_advantages': []
            }
    
    async def _generate_content_suggestions(self, 
                                           profile: CompetitorProfile, 
                                           metrics: CompetitorMetrics) -> List[str]:
        """Generate content suggestions based on competitor analysis."""
        try:
            suggestions = []
            
            # Based on content gaps
            if metrics.content_analysis.content_count < 100:
                suggestions.append("Increase content volume to compete effectively")
            
            # Based on quality gaps
            if metrics.content_analysis.avg_quality_score < 7.0:
                suggestions.append("Focus on improving content quality and depth")
            
            # Based on format gaps
            current_formats = [ct.value for ct in metrics.content_analysis.content_types]
            missing_formats = ['video', 'infographic', 'case_study']
            for fmt in missing_formats:
                if fmt not in current_formats:
                    suggestions.append(f"Consider adding {fmt} content to your strategy")
            
            # Based on SEO gaps
            if metrics.seo_metrics.domain_authority < 50:
                suggestions.append("Build authority through quality backlinks and consistent content")
            
            if not metrics.seo_metrics.mobile_friendly:
                suggestions.append("Optimize for mobile to improve user experience and rankings")
            
            return suggestions[:5]  # Return top 5 suggestions
            
        except Exception as e:
            logger.error(f"❌ Error generating content suggestions: {e}")
            return ["Focus on creating high-quality, relevant content"]
    
    def _calculate_confidence_score(self, 
                                  profile: CompetitorProfile, 
                                  metrics: CompetitorMetrics) -> float:
        """Calculate confidence score for the analysis."""
        try:
            confidence = 0.8  # Base confidence
            
            # Adjust based on data completeness
            if metrics.engagement_metrics.page_views > 0:
                confidence += 0.1
            if metrics.seo_metrics.domain_authority > 0:
                confidence += 0.1
            if metrics.content_analysis.content_count > 0:
                confidence += 0.1
            
            return min(1.0, confidence)
            
        except Exception as e:
            logger.error(f"❌ Error calculating confidence score: {e}")
            return 0.5
    
    @inject_external_service("website_analyzer")
    async def _get_website_data(self, website_analyzer, url: str) -> Dict[str, Any]:
        """Get website data using website analyzer service."""
        try:
            if not website_analyzer:
                logger.warning("Website analyzer service not available, using fallback data")
                return self._get_fallback_website_data(url)
            
            # Use website analyzer to get data
            data = await website_analyzer.analyze_website(url)
            return data
            
        except Exception as e:
            logger.error(f"❌ Error getting website data: {e}")
            return self._get_fallback_website_data(url)
    
    def _get_fallback_website_data(self, url: str) -> Dict[str, Any]:
        """Get fallback website data when analyzer is not available."""
        return {
            'engagement': {
                'avg_time_on_page': 180,
                'bounce_rate': 0.35,
                'social_shares': 45,
                'page_views': 1000,
                'unique_visitors': 800,
                'conversion_rate': 0.02,
            },
            'seo': {
                'domain_authority': 50,
                'page_authority': 30,
                'page_speed': 75,
                'mobile_friendly': True,
                'ssl_certificate': True,
                'indexed_pages': 100,
                'backlinks_count': 500,
                'organic_traffic': 1000,
                'keyword_rankings': 50,
            },
            'content': {
                'content_count': 150,
                'avg_quality_score': 5.0,
                'top_keywords': ['AI', 'ML', 'Data Science'],
                'content_types': ['blog', 'article'],
                'publishing_frequency': 'weekly',
                'avg_word_count': 1000,
                'content_depth_score': 5.0,
                'freshness_score': 5.0,
                'topic_diversity': 5.0,
            },
            'traffic': {
                'monthly': 5000,
            },
            'market_share': 5.0,
        }
    
    async def validate_competitor_data(self, data: Dict[str, Any]) -> List[ValidationError]:
        """Validate competitor analysis data."""
        try:
            return validate_competitor_data(data)
        except Exception as e:
            logger.error(f"❌ Error validating competitor data: {e}")
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
            
            # Check basic functionality
            try:
                # Test URL validation
                is_valid, _ = validate_competitor_url("https://example.com")
                health_status['checks']['url_validation'] = {
                    'status': 'healthy' if is_valid else 'unhealthy',
                    'message': 'URL validation working' if is_valid else 'URL validation failed'
                }
            except Exception as e:
                health_status['checks']['url_validation'] = {
                    'status': 'error',
                    'message': str(e)
                }
                health_status['status'] = 'degraded'
            
            # Check data transformation
            try:
                test_data = {'avg_time_on_page': 180, 'bounce_rate': 0.35}
                transformed = transform_engagement_metrics(test_data)
                health_status['checks']['data_transformation'] = {
                    'status': 'healthy',
                    'message': 'Data transformation working'
                }
            except Exception as e:
                health_status['checks']['data_transformation'] = {
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
            'description': 'Specialized service for competitor analysis',
            'capabilities': [
                'Single competitor analysis',
                'Multiple competitor analysis',
                'Competitor profile creation',
                'Competitor metrics extraction',
                'Competitor insights generation',
                'Content suggestions',
                'Data validation'
            ],
            'dependencies': [
                'Website analyzer service (optional)',
                'AI providers for insights generation'
            ],
            'supported_formats': [
                'CompetitorProfile',
                'CompetitorMetrics',
                'CompetitorAnalysis'
            ]
        }
