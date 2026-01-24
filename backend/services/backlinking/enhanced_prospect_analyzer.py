"""
Enhanced Prospect Analyzer for Backlinking

Integrates comprehensive website analysis services for superior prospect intelligence.
Uses existing ALwrity content_gap_analyzer and website_analyzer services.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import hashlib
from loguru import logger

from .logging_utils import campaign_logger
from .config import get_config


class EnhancedProspectAnalyzer:
    """
    Provides comprehensive prospect analysis using existing ALwrity services.

    This service integrates:
    - ContentGapAnalyzer: Comprehensive content gap analysis
    - WebsiteAnalyzer: Detailed website structure and content analysis
    - CompetitorAnalyzer: Competitor analysis and positioning

    All existing services remain unchanged and continue to serve other ALwrity modules.
    """

    def __init__(self):
        """Initialize the enhanced prospect analyzer."""
        # Lazy load expensive services only when needed
        self._content_analyzer = None
        self._website_analyzer = None
        self._competitor_analyzer = None

        # Simple in-memory cache for analysis results
        self._analysis_cache: Dict[str, Dict[str, Any]] = {}

        # Get configuration
        self.config = get_config()

        campaign_logger.info("EnhancedProspectAnalyzer initialized")

    def _get_cache_key(self, prospect_url: str, keywords: List[str], analysis_type: str) -> str:
        """Generate a cache key for analysis results."""
        key_components = [prospect_url, analysis_type] + sorted(keywords)
        key_string = json.dumps(key_components, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()

    def _get_cached_analysis(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached analysis if still valid."""
        if not self.config.prospect_analysis.cache_analysis_results:
            return None

        cached_data = self._analysis_cache.get(cache_key)
        if not cached_data:
            return None

        # Check if cache is still valid
        cached_at = datetime.fromisoformat(cached_data.get('cached_at', '2000-01-01T00:00:00'))
        cache_ttl = timedelta(hours=self.config.prospect_analysis.analysis_cache_ttl_hours)
        if datetime.utcnow() - cached_at > cache_ttl:
            # Cache expired, remove it
            del self._analysis_cache[cache_key]
            return None

        campaign_logger.debug(f"Using cached analysis for key: {cache_key[:8]}...")
        return cached_data.get('data')

    def _cache_analysis_result(self, cache_key: str, result: Dict[str, Any]):
        """Cache analysis result."""
        if not self.config.prospect_analysis.cache_analysis_results:
            return

        self._analysis_cache[cache_key] = {
            'data': result,
            'cached_at': datetime.utcnow().isoformat()
        }

        # Clean up old cache entries periodically (simple approach)
        if len(self._analysis_cache) > 100:  # Arbitrary limit
            self._cleanup_expired_cache()

    def _cleanup_expired_cache(self):
        """Remove expired cache entries."""
        cache_ttl = timedelta(hours=self.config.prospect_analysis.analysis_cache_ttl_hours)
        cutoff_time = datetime.utcnow() - cache_ttl

        expired_keys = []
        for key, data in self._analysis_cache.items():
            cached_at = datetime.fromisoformat(data.get('cached_at', '2000-01-01T00:00:00'))
            if cached_at < cutoff_time:
                expired_keys.append(key)

        for key in expired_keys:
            del self._analysis_cache[key]

        if expired_keys:
            campaign_logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")

    @property
    def content_analyzer(self):
        """Lazy load content gap analyzer."""
        if self._content_analyzer is None:
            try:
                from services.content_gap_analyzer.content_gap_analyzer import ContentGapAnalyzer
                self._content_analyzer = ContentGapAnalyzer()
                campaign_logger.debug("ContentGapAnalyzer loaded successfully")
            except ImportError as e:
                campaign_logger.error(f"Failed to load ContentGapAnalyzer: {e}")
                raise
        return self._content_analyzer

    @property
    def website_analyzer(self):
        """Lazy load website analyzer."""
        if self._website_analyzer is None:
            try:
                from services.content_gap_analyzer.website_analyzer import WebsiteAnalyzer
                self._website_analyzer = WebsiteAnalyzer()
                campaign_logger.debug("WebsiteAnalyzer loaded successfully")
            except ImportError as e:
                campaign_logger.error(f"Failed to load WebsiteAnalyzer: {e}")
                raise
        return self._website_analyzer

    @property
    def competitor_analyzer(self):
        """Lazy load competitor analyzer."""
        if self._competitor_analyzer is None:
            try:
                from services.content_gap_analyzer.competitor_analyzer import CompetitorAnalyzer
                self._competitor_analyzer = CompetitorAnalyzer()
                campaign_logger.debug("CompetitorAnalyzer loaded successfully")
            except ImportError as e:
                campaign_logger.error(f"Failed to load CompetitorAnalyzer: {e}")
                raise
        return self._competitor_analyzer

    async def analyze_prospect_comprehensive(self,
                                           prospect_url: str,
                                           campaign_keywords: List[str],
                                           user_id: str,
                                           enable_deep_analysis: bool = True,
                                           industry: str = "general") -> Dict[str, Any]:
        """
        Comprehensive prospect analysis for personalized outreach.

        Args:
            prospect_url: Prospect website URL to analyze
            campaign_keywords: Campaign target keywords
            user_id: User ID for subscription validation and AI calls
            enable_deep_analysis: Whether to perform full analysis (vs quick sitemap-only)
            industry: Industry category for context

        Returns:
            Comprehensive analysis results with website profile, content intelligence,
            outreach insights, and personalization opportunities
        """
        try:
            campaign_logger.info(f"Starting comprehensive analysis for prospect: {prospect_url}")

            # Check cache first
            cache_key = self._get_cache_key(prospect_url, campaign_keywords, 'enhanced' if enable_deep_analysis else 'quick')
            cached_result = self._get_cached_analysis(cache_key)
            if cached_result:
                campaign_logger.info(f"Returning cached analysis for {prospect_url}")
                return cached_result

            results = {
                'prospect_url': prospect_url,
                'campaign_keywords': campaign_keywords,
                'industry': industry,
                'analysis_type': 'enhanced' if enable_deep_analysis else 'quick',
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'website_profile': {},
                'content_intelligence': {},
                'outreach_insights': {},
                'personalization_opportunities': {},
                'analysis_metadata': {
                    'deep_analysis_enabled': enable_deep_analysis,
                    'services_used': [],
                    'processing_time_seconds': 0,
                    'cached': False
                }
            }

            start_time = datetime.utcnow()

            # Phase 1: Website Structure Analysis (always performed)
            campaign_logger.info(f"Phase 1: Analyzing website structure for {prospect_url}")
            try:
                website_profile = await self.website_analyzer.analyze_website(
                    url=prospect_url,
                    industry=industry
                )
                results['website_profile'] = website_profile
                results['analysis_metadata']['services_used'].append('website_analyzer')
                campaign_logger.info(f"✅ Website structure analysis completed for {prospect_url}")
            except Exception as e:
                campaign_logger.warning(f"Website analysis failed for {prospect_url}: {e}")
                # Continue with other analyses - website analysis is not critical

            # Phase 2: Content Intelligence Analysis (if deep analysis enabled)
            if enable_deep_analysis:
                campaign_logger.info(f"Phase 2: Performing deep content intelligence for {prospect_url}")

                try:
                    # Attempt to find competitors for comparison
                    competitor_urls = await self._discover_competitors(prospect_url, campaign_keywords[:3])

                    content_intelligence = await self.content_analyzer.analyze_comprehensive_gap(
                        target_url=prospect_url,
                        competitor_urls=competitor_urls[:3],  # Limit for performance
                        target_keywords=campaign_keywords,
                        industry=industry
                    )
                    results['content_intelligence'] = content_intelligence
                    results['analysis_metadata']['services_used'].extend(['content_gap_analyzer', 'competitor_analyzer'])
                    campaign_logger.info(f"✅ Content intelligence analysis completed for {prospect_url}")

                except Exception as e:
                    campaign_logger.warning(f"Content intelligence analysis failed for {prospect_url}: {e}")
                    # Continue with basic content analysis if available

            # Phase 3: Generate Outreach Insights (if we have data to work with)
            if results['website_profile'] or results['content_intelligence']:
                campaign_logger.info(f"Phase 3: Generating outreach insights for {prospect_url}")

                try:
                    outreach_insights = await self._generate_outreach_insights(
                        website_profile=results['website_profile'],
                        content_intelligence=results.get('content_intelligence', {}),
                        campaign_keywords=campaign_keywords,
                        industry=industry,
                        user_id=user_id
                    )
                    results['outreach_insights'] = outreach_insights
                    campaign_logger.info(f"✅ Outreach insights generated for {prospect_url}")

                except Exception as e:
                    campaign_logger.warning(f"Outreach insights generation failed for {prospect_url}: {e}")

            # Phase 4: Calculate Personalization Potential
            campaign_logger.info(f"Phase 4: Calculating personalization opportunities for {prospect_url}")

            try:
                personalization_score = self._calculate_personalization_potential(
                    website_profile=results['website_profile'],
                    content_intelligence=results.get('content_intelligence', {}),
                    campaign_keywords=campaign_keywords
                )
                results['personalization_opportunities'] = personalization_score
                campaign_logger.info(f"✅ Personalization potential calculated for {prospect_url}")

            except Exception as e:
                campaign_logger.warning(f"Personalization calculation failed for {prospect_url}: {e}")

            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            results['analysis_metadata']['processing_time_seconds'] = processing_time

            # Cache the result
            self._cache_analysis_result(cache_key, results)

            campaign_logger.info(f"✅ Comprehensive analysis completed for {prospect_url} in {processing_time:.1f}s")
            return results

        except Exception as e:
            campaign_logger.error(f"Enhanced prospect analysis failed for {prospect_url}: {e}")
            fallback_result = self._create_fallback_analysis(prospect_url, campaign_keywords, str(e))
            # Cache fallback result to avoid repeated failures
            self._cache_analysis_result(cache_key, fallback_result)
            return fallback_result

    async def _discover_competitors(self, target_url: str, keywords: List[str]) -> List[str]:
        """
        Discover competitor URLs for comparison.

        Uses basic domain similarity and keyword matching to find potential competitors.
        In a production implementation, this would use SERP analysis and backlink data.
        """
        try:
            # Extract domain from target URL
            from urllib.parse import urlparse
            target_domain = urlparse(target_url).netloc.lower()

            # For now, return empty list to avoid performance issues
            # Competitor analysis can be enabled later with proper SERP integration
            # This prevents breaking existing functionality while providing the framework

            campaign_logger.debug(f"Competitor discovery placeholder for {target_domain} - returning empty list for performance")
            return []

        except Exception as e:
            campaign_logger.warning(f"Competitor discovery failed: {e}")
            return []

    async def _generate_outreach_insights(self,
                                        website_profile: Dict[str, Any],
                                        content_intelligence: Dict[str, Any],
                                        campaign_keywords: List[str],
                                        industry: str,
                                        user_id: str) -> Dict[str, Any]:
        """
        Generate personalized outreach insights using AI analysis of prospect data.
        """
        try:
            # Use centralized llm_text_gen with subscription checks
            from services.llm_providers.main_text_generation import llm_text_gen

            # Compile prospect intelligence for AI analysis
            prospect_intelligence = {
                'writing_style': website_profile.get('content_analysis', {}).get('writing_style', {}),
                'target_audience': website_profile.get('ai_insights', {}).get('target_audience', {}),
                'content_themes': website_profile.get('content_analysis', {}).get('content_themes', []),
                'content_gaps': content_intelligence.get('gap_analysis', {}).get('identified_gaps', []),
                'brand_voice': website_profile.get('ai_insights', {}).get('brand_voice', {}),
                'campaign_keywords': campaign_keywords,
                'industry': industry,
                'seo_performance': website_profile.get('seo_analysis', {}),
                'performance_metrics': website_profile.get('performance_analysis', {})
            }

            prompt = f"""
            Based on this comprehensive analysis of a prospect's website, generate personalized outreach insights for guest posting:

            Prospect Intelligence:
            {json.dumps(prospect_intelligence, indent=2)}

            Analyze the prospect's content strategy, writing style, and audience to provide:

            1. **Personalization Angles**: Key insights about their brand voice, writing style, and audience that can be referenced in outreach emails

            2. **Content Opportunities**: Specific content gaps or underserved topics in their content strategy that align with the campaign keywords

            3. **Tone Recommendations**: How to match their communication style and professional tone

            4. **Value Propositions**: Strategic value propositions based on their content needs and audience pain points

            5. **Subject Line Suggestions**: 5 compelling email subject lines that would resonate with this prospect

            6. **Strategic Insights**: High-level strategic observations about their content strategy and market positioning

            Return as JSON with keys: personalization_angles, content_opportunities, tone_recommendations, value_propositions, subject_line_suggestions, strategic_insights

            Focus on actionable insights that can improve outreach success rates.
            """

            insights = llm_text_gen(
                prompt=prompt,
                json_struct={
                    "personalization_angles": ["string"],
                    "content_opportunities": ["string"],
                    "tone_recommendations": ["string"],
                    "value_propositions": ["string"],
                    "subject_line_suggestions": ["string"],
                    "strategic_insights": ["string"]
                },
                user_id=user_id
            )

            return insights if insights else {}

        except Exception as e:
            campaign_logger.warning(f"Outreach insights generation failed: {e}")
            return {}

    def _calculate_personalization_potential(self,
                                          website_profile: Dict[str, Any],
                                          content_intelligence: Dict[str, Any],
                                          campaign_keywords: List[str]) -> Dict[str, Any]:
        """
        Calculate the personalization potential score based on available intelligence.
        """
        try:
            score = 0.0
            factors = {}

            # Writing style analysis available
            if website_profile.get('content_analysis', {}).get('writing_style'):
                score += 0.2
                factors['writing_style'] = True

            # Target audience insights
            if website_profile.get('ai_insights', {}).get('target_audience'):
                score += 0.15
                factors['audience_insights'] = True

            # Content themes identified
            content_themes = website_profile.get('content_analysis', {}).get('content_themes', [])
            if content_themes and len(content_themes) > 0:
                score += 0.15
                factors['content_themes'] = len(content_themes)

            # SEO analysis available
            if website_profile.get('seo_analysis'):
                score += 0.1
                factors['seo_analysis'] = True

            # Performance metrics
            if website_profile.get('performance_analysis'):
                score += 0.1
                factors['performance_metrics'] = True

            # Content gaps identified
            gaps = content_intelligence.get('gap_analysis', {}).get('identified_gaps', [])
            if gaps and len(gaps) > 0:
                score += 0.2
                factors['content_gaps'] = len(gaps)

            # Keyword alignment analysis
            if content_intelligence.get('keyword_expansion'):
                score += 0.1
                factors['keyword_analysis'] = True

            # Determine personalization level
            if score >= 0.8:
                level = "excellent"
                description = "High-confidence personalization with comprehensive prospect intelligence"
            elif score >= 0.6:
                level = "good"
                description = "Strong personalization potential with multiple data points"
            elif score >= 0.4:
                level = "moderate"
                description = "Moderate personalization with basic website analysis"
            elif score >= 0.2:
                level = "basic"
                description = "Limited personalization with minimal insights"
            else:
                level = "none"
                description = "Insufficient data for personalization"

            return {
                'personalization_score': min(1.0, score),
                'personalization_level': level,
                'description': description,
                'factors_available': factors,
                'confidence_level': 'high' if score >= 0.6 else 'medium' if score >= 0.3 else 'low'
            }

        except Exception as e:
            campaign_logger.warning(f"Personalization potential calculation failed: {e}")
            return {
                'personalization_score': 0.0,
                'personalization_level': 'none',
                'description': 'Analysis failed - using default scoring',
                'factors_available': {},
                'confidence_level': 'low'
            }

    def _create_fallback_analysis(self, prospect_url: str, campaign_keywords: List[str], error: str = None) -> Dict[str, Any]:
        """
        Create fallback analysis when comprehensive analysis fails.
        """
        return {
            'prospect_url': prospect_url,
            'campaign_keywords': campaign_keywords,
            'analysis_type': 'fallback',
            'analysis_timestamp': datetime.utcnow().isoformat(),
            'website_profile': {},
            'content_intelligence': {},
            'outreach_insights': {},
            'personalization_opportunities': {
                'personalization_score': 0.0,
                'personalization_level': 'none',
                'description': f'Analysis failed: {error}' if error else 'Analysis unavailable - using fallback',
                'factors_available': {},
                'confidence_level': 'low'
            },
                'analysis_metadata': {
                    'deep_analysis_enabled': False,
                    'services_used': [],
                    'processing_time_seconds': 0,
                    'cached': False,
                    'error': error
                }
        }

    async def get_service_health(self) -> Dict[str, Any]:
        """
        Check the health of integrated services.
        """
        health = {
            'enhanced_prospect_analyzer': 'healthy',
            'integrated_services': {},
            'overall_status': 'healthy'
        }

        services_to_check = [
            ('content_gap_analyzer', lambda: self.content_analyzer),
            ('website_analyzer', lambda: self.website_analyzer),
            ('competitor_analyzer', lambda: self.competitor_analyzer)
        ]

        for service_name, service_getter in services_to_check:
            try:
                service = service_getter()
                health['integrated_services'][service_name] = 'healthy'
            except Exception as e:
                health['integrated_services'][service_name] = f'unhealthy: {str(e)}'
                health['overall_status'] = 'degraded'

        return health