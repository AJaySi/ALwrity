"""
Competitor Analyzer API Facade

Unified API that orchestrates all specialized competitor analyzer services.
Provides a single entry point for all competitor analysis functionality while maintaining
backward compatibility with the original interface.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger
import asyncio

from ..services.competitor_analysis_service import CompetitorAnalysisService
from ..services.market_positioning_service import MarketPositioningService
from ..services.content_gap_analysis_service import ContentGapAnalysisService
from ..services.seo_analysis_service import SEOAnalysisService
from ..models.competitor_models import CompetitorAnalysis
from ..models.market_analysis import MarketPositioning, CompetitiveLandscape
from ..models.content_gap_models import ContentGapAnalysis
from ..models.seo_analysis import SEOAnalysis
from ..models.shared import (
    AnalysisStatus,
    APIResponse,
    ValidationError,
)
from ..utils.competitor_utils import (
    validate_competitor_url,
    normalize_competitor_urls,
    batch_process_urls,
)
from ..utils.data_transformers import (
    transform_to_api_response,
    transform_analysis_summary,
    merge_analysis_results,
    filter_analysis_by_criteria,
)
from ..dependencies import get_dependencies, initialize_dependencies


class CompetitorAnalyzerAPI:
    """
    Unified API facade for competitor analyzer services.
    
    This class provides a single entry point for all competitor analysis functionality
    while orchestrating specialized services in the background.
    """
    
    def __init__(self):
        """Initialize the competitor analyzer API."""
        self.service_name = "CompetitorAnalyzerAPI"
        self.version = "2.0.0"
        
        # Initialize specialized services
        self.competitor_service = CompetitorAnalysisService()
        self.market_service = MarketPositioningService()
        self.content_gap_service = ContentGapAnalysisService()
        self.seo_service = SEOAnalysisService()
        
        # Dependency manager
        self.dependencies = None
        
        logger.info(f"✅ {self.service_name} v{self.version} initialized")
    
    async def initialize(self):
        """Initialize the API and all dependencies."""
        try:
            logger.info("🔄 Initializing Competitor Analyzer API...")
            
            # Initialize dependencies
            await initialize_dependencies()
            self.dependencies = get_dependencies()
            
            # Check service health
            health_status = await self.health_check()
            if health_status.get('status') != 'healthy':
                logger.warning(f"⚠️ Some services may be degraded: {health_status}")
            
            logger.info("✅ Competitor Analyzer API initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Competitor Analyzer API: {e}")
            raise
    
    async def analyze_competitors(self, 
                                 competitor_urls: List[str], 
                                 industry: str = "",
                                 target_keywords: Optional[List[str]] = None,
                                 analysis_depth: str = "comprehensive",
                                 include_market_analysis: bool = True,
                                 include_content_gaps: bool = True,
                                 include_seo_analysis: bool = True) -> Dict[str, Any]:
        """
        Main entry point for competitor analysis.
        
        Args:
            competitor_urls: List of competitor URLs to analyze
            industry: Industry category
            target_keywords: Target keywords for analysis
            analysis_depth: Depth of analysis (basic/standard/comprehensive)
            include_market_analysis: Whether to include market positioning analysis
            include_content_gaps: Whether to include content gap analysis
            include_seo_analysis: Whether to include SEO analysis
            
        Returns:
            Dict[str, Any]: Comprehensive competitor analysis results
        """
        try:
            logger.info(f"🔍 Starting comprehensive competitor analysis for {len(competitor_urls)} competitors")
            
            # Validate and normalize URLs
            normalized_urls = normalize_competitor_urls(competitor_urls)
            if not normalized_urls:
                raise ValueError("No valid competitor URLs provided")
            
            # Initialize results structure
            analysis_id = f"analysis_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            results = {
                'analysis_id': analysis_id,
                'status': AnalysisStatus.IN_PROGRESS,
                'industry': industry,
                'competitor_urls': normalized_urls,
                'target_keywords': target_keywords or [],
                'analysis_depth': analysis_depth,
                'started_at': datetime.utcnow().isoformat(),
                'services_used': [],
            }
            
            # Step 1: Analyze competitors (always included)
            logger.info("📊 Step 1: Analyzing competitors...")
            competitor_analyses = await self.competitor_service.analyze_multiple_competitors(
                normalized_urls, industry, target_keywords
            )
            results['competitor_analyses'] = [comp.dict() for comp in competitor_analyses]
            results['services_used'].append('competitor_analysis')
            
            # Step 2: Market positioning analysis (optional)
            if include_market_analysis:
                logger.info("📈 Step 2: Analyzing market positioning...")
                market_positioning = await self.market_service.analyze_market_positioning(
                    competitor_analyses, total_market_size=1000000  # Would be calculated
                )
                results['market_positioning'] = market_positioning.dict()
                results['services_used'].append('market_positioning')
            
            # Step 3: Content gap analysis (optional)
            if include_content_gaps:
                logger.info("🔍 Step 3: Analyzing content gaps...")
                content_gaps = await self.content_gap_service.analyze_content_gaps(
                    competitor_analyses, target_keywords, industry
                )
                results['content_gap_analysis'] = content_gaps.dict()
                results['services_used'].append('content_gap_analysis')
            
            # Step 4: SEO analysis (optional)
            if include_seo_analysis:
                logger.info("🔍 Step 4: Analyzing SEO gaps...")
                seo_analysis = await self.seo_service.analyze_seo_gaps(
                    competitor_analyses, target_keywords, industry
                )
                results['seo_analysis'] = seo_analysis.dict()
                results['services_used'].append('seo_analysis')
            
            # Generate summary
            results['summary'] = await self._generate_analysis_summary(results)
            
            # Update status
            results['status'] = AnalysisStatus.COMPLETED
            results['completed_at'] = datetime.utcnow().isoformat()
            
            logger.info(f"✅ Competitor analysis completed: {analysis_id}")
            return results
            
        except Exception as e:
            logger.error(f"❌ Error in competitor analysis: {e}")
            return {
                'analysis_id': analysis_id if 'analysis_id' in locals() else 'unknown',
                'status': AnalysisStatus.FAILED,
                'error': str(e),
                'failed_at': datetime.utcnow().isoformat()
            }
    
    async def analyze_single_competitor(self, 
                                       url: str, 
                                       industry: str = "",
                                       target_keywords: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Analyze a single competitor.
        
        Args:
            url: Competitor URL to analyze
            industry: Industry category
            target_keywords: Target keywords for analysis
            
        Returns:
            Dict[str, Any]: Single competitor analysis results
        """
        try:
            logger.info(f"🔍 Analyzing single competitor: {url}")
            
            # Validate URL
            is_valid, error = validate_competitor_url(url)
            if not is_valid:
                raise ValueError(f"Invalid competitor URL: {error}")
            
            # Analyze competitor
            competitor_analysis = await self.competitor_service.analyze_single_competitor(
                url, industry, target_keywords
            )
            
            # Generate summary
            summary = {
                'competitor_url': url,
                'competitor_name': competitor_analysis.profile.name,
                'competitor_type': competitor_analysis.profile.competitor_type,
                'domain_authority': competitor_analysis.metrics.seo_metrics.domain_authority,
                'content_count': competitor_analysis.metrics.content_analysis.content_count,
                'avg_quality_score': competitor_analysis.metrics.content_analysis.avg_quality_score,
                'strengths_count': len(competitor_analysis.strengths),
                'weaknesses_count': len(competitor_analysis.weaknesses),
                'opportunities_count': len(competitor_analysis.opportunities),
                'confidence_score': competitor_analysis.confidence_score,
            }
            
            result = {
                'competitor_analysis': competitor_analysis.dict(),
                'summary': summary,
                'analysis_date': datetime.utcnow().isoformat(),
            }
            
            logger.info(f"✅ Single competitor analysis completed: {url}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error analyzing single competitor {url}: {e}")
            return {
                'competitor_url': url,
                'status': 'failed',
                'error': str(e),
                'analysis_date': datetime.utcnow().isoformat(),
            }
    
    async def get_competitor_summary(self, analysis_id: str) -> Dict[str, Any]:
        """
        Get summary of competitor analysis.
        
        Args:
            analysis_id: Analysis identifier
            
        Returns:
            Dict[str, Any]: Analysis summary
        """
        try:
            logger.info(f"📊 Getting competitor analysis summary: {analysis_id}")
            
            # In a real implementation, this would fetch from database
            # For now, return a placeholder summary
            summary = {
                'analysis_id': analysis_id,
                'status': AnalysisStatus.COMPLETED,
                'competitors_analyzed': 5,
                'content_gaps_identified': 8,
                'competitive_insights': 6,
                'market_position': 'Competitive',
                'estimated_impact': 'High',
                'completion_percentage': 100,
                'last_updated': datetime.utcnow().isoformat(),
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Error getting competitor summary {analysis_id}: {e}")
            return {
                'analysis_id': analysis_id,
                'status': 'error',
                'error': str(e),
            }
    
    async def analyze_content_structure(self, competitor_urls: List[str]) -> Dict[str, Any]:
        """
        Analyze content structure across competitors.
        
        Args:
            competitor_urls: List of competitor URLs
            
        Returns:
            Dict[str, Any]: Content structure analysis
        """
        try:
            logger.info(f"🔍 Analyzing content structure for {len(competitor_urls)} competitors")
            
            # Analyze competitors
            competitor_analyses = await self.competitor_service.analyze_multiple_competitors(
                competitor_urls
            )
            
            # Analyze content structure
            content_analysis = {
                'topic_distribution': {},  # Would be calculated from actual data
                'content_depth': {},
                'content_formats': {},
                'content_quality': {},
                'publishing_frequency': {},
                'content_recommendations': [],
            }
            
            # Extract content structure data
            for analysis in competitor_analyses:
                content = analysis.metrics.content_analysis
                url = analysis.profile.url
                
                # Content types distribution
                for content_type in content.content_types:
                    if content_type.value not in content_analysis['content_formats']:
                        content_analysis['content_formats'][content_type.value] = 0
                    content_analysis['content_formats'][content_type.value] += 1
                
                # Quality scores
                content_analysis['content_quality'][url] = content.avg_quality_score
                
                # Content count
                content_analysis['content_depth'][url] = content.content_count
            
            # Generate recommendations
            content_analysis['content_recommendations'] = [
                "Increase content variety with different formats",
                "Focus on improving content quality scores",
                "Maintain consistent publishing schedule",
                "Optimize content depth for better engagement"
            ]
            
            logger.info("✅ Content structure analysis completed")
            return content_analysis
            
        except Exception as e:
            logger.error(f"❌ Error analyzing content structure: {e}")
            return {'error': str(e)}
    
    async def analyze_content_performance(self, competitor_urls: List[str]) -> Dict[str, Any]:
        """
        Analyze content performance metrics for competitors.
        
        Args:
            competitor_urls: List of competitor URLs
            
        Returns:
            Dict[str, Any]: Content performance analysis
        """
        try:
            logger.info(f"🔍 Analyzing content performance for {len(competitor_urls)} competitors")
            
            # Analyze competitors
            competitor_analyses = await self.competitor_service.analyze_multiple_competitors(
                competitor_urls
            )
            
            # Analyze performance metrics
            performance_analysis = {
                'engagement_metrics': {},
                'traffic_metrics': {},
                'social_metrics': {},
                'conversion_metrics': {},
                'performance_rankings': {},
                'improvement_opportunities': [],
            }
            
            # Extract performance data
            for analysis in competitor_analyses:
                engagement = analysis.metrics.engagement_metrics
                url = analysis.profile.url
                
                performance_analysis['engagement_metrics'][url] = {
                    'avg_time_on_page': engagement.avg_time_on_page,
                    'bounce_rate': engagement.bounce_rate,
                    'social_shares': engagement.social_shares,
                    'page_views': engagement.page_views,
                    'unique_visitors': engagement.unique_visitors,
                    'conversion_rate': engagement.conversion_rate,
                }
            
            # Calculate rankings
            performance_analysis['performance_rankings'] = {
                'most_engaging': max(performance_analysis['engagement_metrics'].items(), 
                                   key=lambda x: x[1]['avg_time_on_page'])[0],
                'most_shared': max(performance_analysis['engagement_metrics'].items(), 
                                 key=lambda x: x[1]['social_shares'])[0],
                'lowest_bounce': min(performance_analysis['engagement_metrics'].items(), 
                                   key=lambda x: x[1]['bounce_rate'])[0],
            }
            
            # Generate improvement opportunities
            performance_analysis['improvement_opportunities'] = [
                "Optimize content for better engagement",
                "Increase social sharing incentives",
                "Improve page load speed",
                "Enhance mobile user experience",
                "Implement better call-to-actions"
            ]
            
            logger.info("✅ Content performance analysis completed")
            return performance_analysis
            
        except Exception as e:
            logger.error(f"❌ Error analyzing content performance: {e}")
            return {'error': str(e)}
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check for all services.
        
        Returns:
            Dict[str, Any]: Health check results
        """
        try:
            logger.info("🔍 Performing comprehensive health check...")
            
            health_status = {
                'service': self.service_name,
                'version': self.version,
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'services': {},
                'dependencies': {},
                'overall_score': 0,
            }
            
            # Check specialized services
            services = {
                'competitor_analysis': self.competitor_service,
                'market_positioning': self.market_service,
                'content_gap_analysis': self.content_gap_service,
                'seo_analysis': self.seo_service,
            }
            
            service_scores = []
            for service_name, service in services.items():
                try:
                    service_health = await service.health_check()
                    health_status['services'][service_name] = service_health
                    
                    if service_health.get('status') == 'healthy':
                        service_scores.append(100)
                    elif service_health.get('status') == 'degraded':
                        service_scores.append(70)
                    else:
                        service_scores.append(0)
                        health_status['status'] = 'degraded'
                        
                except Exception as e:
                    health_status['services'][service_name] = {
                        'status': 'error',
                        'error': str(e)
                    }
                    service_scores.append(0)
                    health_status['status'] = 'degraded'
            
            # Check dependencies
            if self.dependencies:
                try:
                    dependency_health = await self.dependencies.health_check()
                    health_status['dependencies'] = dependency_health
                    
                    if dependency_health.get('status') == 'healthy':
                        service_scores.append(100)
                    else:
                        service_scores.append(70)
                        health_status['status'] = 'degraded'
                        
                except Exception as e:
                    health_status['dependencies'] = {
                        'status': 'error',
                        'error': str(e)
                    }
                    service_scores.append(0)
                    health_status['status'] = 'degraded'
            
            # Calculate overall score
            if service_scores:
                health_status['overall_score'] = round(sum(service_scores) / len(service_scores), 1)
            
            # Determine final status
            if health_status['overall_score'] >= 90:
                health_status['status'] = 'healthy'
            elif health_status['overall_score'] >= 70:
                health_status['status'] = 'degraded'
            else:
                health_status['status'] = 'unhealthy'
            
            logger.info(f"✅ Health check completed - Status: {health_status['status']}")
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
    
    async def _generate_analysis_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive analysis summary."""
        try:
            summary = {
                'analysis_id': results.get('analysis_id'),
                'status': results.get('status'),
                'industry': results.get('industry'),
                'competitors_analyzed': len(results.get('competitor_analyses', [])),
                'services_used': results.get('services_used', []),
                'key_metrics': {},
                'insights': [],
                'recommendations': [],
                'analysis_duration': None,
            }
            
            # Calculate key metrics
            competitor_analyses = results.get('competitor_analyses', [])
            if competitor_analyses:
                # Calculate averages
                avg_domain_authority = sum(comp.get('metrics', {}).get('seo_metrics', {}).get('domain_authority', 0) 
                                         for comp in competitor_analyses) / len(competitor_analyses)
                avg_content_quality = sum(comp.get('metrics', {}).get('content_analysis', {}).get('avg_quality_score', 0) 
                                        for comp in competitor_analyses) / len(competitor_analyses)
                total_content_pieces = sum(comp.get('metrics', {}).get('content_analysis', {}).get('content_count', 0) 
                                         for comp in competitor_analyses)
                
                summary['key_metrics'] = {
                    'avg_domain_authority': round(avg_domain_authority, 1),
                    'avg_content_quality': round(avg_content_quality, 1),
                    'total_content_pieces': total_content_pieces,
                }
            
            # Extract insights from different analyses
            if 'market_positioning' in results:
                market_data = results['market_positioning']
                summary['insights'].extend([
                    f"Market leader: {market_data.get('market_leader', 'Unknown')}",
                    f"Competitive intensity: {market_data.get('competitive_intensity', 'Unknown')}",
                ])
            
            if 'content_gap_analysis' in results:
                gap_data = results['content_gap_analysis']
                summary['insights'].append(f"Content gaps identified: {gap_data.get('total_gaps_identified', 0)}")
            
            if 'seo_analysis' in results:
                seo_data = results['seo_analysis']
                summary['insights'].append(f"SEO gaps identified: {seo_data.get('total_gaps_identified', 0)}")
            
            # Calculate analysis duration
            if 'started_at' in results and 'completed_at' in results:
                start_time = datetime.fromisoformat(results['started_at'].replace('Z', '+00:00'))
                end_time = datetime.fromisoformat(results['completed_at'].replace('Z', '+00:00'))
                duration = end_time - start_time
                summary['analysis_duration'] = str(duration)
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Error generating analysis summary: {e}")
            return {'error': str(e)}
    
    async def get_service_info(self) -> Dict[str, Any]:
        """Get comprehensive service information."""
        try:
            service_info = {
                'service_name': self.service_name,
                'version': self.version,
                'description': 'Unified API for competitor analysis services',
                'architecture': 'Microservices with API facade',
                'specialized_services': [
                    {
                        'name': 'CompetitorAnalysisService',
                        'description': 'Individual competitor analysis and profiling',
                        'status': 'active'
                    },
                    {
                        'name': 'MarketPositioningService',
                        'description': 'Market positioning and competitive landscape analysis',
                        'status': 'active'
                    },
                    {
                        'name': 'ContentGapAnalysisService',
                        'description': 'Content gap identification and analysis',
                        'status': 'active'
                    },
                    {
                        'name': 'SEOAnalysisService',
                        'description': 'SEO gap analysis and optimization recommendations',
                        'status': 'active'
                    }
                ],
                'capabilities': [
                    'Comprehensive competitor analysis',
                    'Market positioning analysis',
                    'Content gap identification',
                    'SEO gap analysis',
                    'Performance metrics analysis',
                    'Strategic recommendations',
                    'Implementation roadmaps'
                ],
                'api_endpoints': [
                    'analyze_competitors',
                    'analyze_single_competitor',
                    'get_competitor_summary',
                    'analyze_content_structure',
                    'analyze_content_performance',
                    'health_check'
                ],
                'dependencies': [
                    'AI providers (llm_text_gen, Gemini)',
                    'Website analyzer service (optional)',
                    'Database connections',
                    'Cache clients'
                ],
                'supported_formats': [
                    'JSON',
                    'Pydantic models',
                    'API responses'
                ],
                'performance_metrics': {
                    'max_concurrent_analyses': 10,
                    'analysis_timeout': 300,  # 5 minutes
                    'cache_ttl': 3600,  # 1 hour
                }
            }
            
            return service_info
            
        except Exception as e:
            logger.error(f"❌ Error getting service info: {e}")
            return {'error': str(e)}
    
    async def shutdown(self):
        """Shutdown the API and all services."""
        try:
            logger.info("🔄 Shutting down Competitor Analyzer API...")
            
            # Shutdown dependencies
            if self.dependencies:
                await self.dependencies.shutdown()
            
            logger.info("✅ Competitor Analyzer API shutdown complete")
            
        except Exception as e:
            logger.error(f"❌ Error during shutdown: {e}")


# Global API instance
_api_instance: Optional[CompetitorAnalyzerAPI] = None


async def get_competitor_analyzer_api() -> CompetitorAnalyzerAPI:
    """
    Get the global competitor analyzer API instance.
    
    Returns:
        CompetitorAnalyzerAPI: API instance
    """
    global _api_instance
    
    if _api_instance is None:
        _api_instance = CompetitorAnalyzerAPI()
        await _api_instance.initialize()
    
    return _api_instance


async def shutdown_competitor_analyzer_api():
    """Shutdown the global API instance."""
    global _api_instance
    
    if _api_instance:
        await _api_instance.shutdown()
        _api_instance = None
