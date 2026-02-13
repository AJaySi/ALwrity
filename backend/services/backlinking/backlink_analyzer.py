"""
Custom Backlink Analysis Service

Performs backlink analysis using search engines, web crawling, and social media
without depending on paid APIs like Majestic, Ahrefs, or Moz.
"""

import asyncio
import re
import time
from typing import List, Dict, Any, Optional, Set
from urllib.parse import urlparse, urljoin
from datetime import datetime, timedelta
import aiohttp
from bs4 import BeautifulSoup
import logging

from .logging_utils import campaign_logger
from .config import get_config
from .models import BacklinkData

# Import Google Trends service for competitor trend analysis
from ..research.trends.google_trends_service import GoogleTrendsService


class CustomBacklinkAnalyzer:
    """
    Custom backlink analysis using free methods and search engines.

    Strategies:
    1. Search engine queries with link operators
    2. Social media mention discovery
    3. Forum and community scraping
    4. Web crawling for inbound links
    """

    def __init__(self):
        self.config = get_config()
        self.session_timeout = aiohttp.ClientTimeout(total=30)
        self.rate_limit_delay = 1.0  # seconds between requests
        self.max_results_per_query = 100
        self.google_trends = GoogleTrendsService()  # Initialize Google Trends service

        # Search engine operators for backlink discovery
        self.backlink_operators = [
            'link:"{url}"',           # Google link operator (limited but useful)
            'site:* "{url}"',         # Find pages mentioning the URL
            'inurl:"{url}"',          # URL appears in page URL
            '"{url}" -site:{url}',    # External mentions of the URL
        ]

        # Social media platforms to check
        self.social_platforms = [
            'twitter.com',
            'facebook.com',
            'linkedin.com',
            'instagram.com',
            'pinterest.com',
            'reddit.com'
        ]

        # Forum and community sites
        self.forum_sites = [
            'reddit.com',
            'quora.com',
            'forum.',
            'community.',
            '.org/forum',
            'discourse.'
        ]

    async def analyze_backlinks(self, target_url: str, competitor_urls: List[str] = None) -> Dict[str, Any]:
        """
        Comprehensive backlink analysis for target URL and competitors.

        Args:
            target_url: Primary URL to analyze
            competitor_urls: Optional competitor URLs for comparison

        Returns:
            Comprehensive backlink analysis
        """
        try:
            campaign_logger.info(f"Starting backlink analysis for: {target_url}")

            # Parallel analysis of target and competitors
            analysis_tasks = [self._analyze_single_url(target_url)]
            if competitor_urls:
                for comp_url in competitor_urls[:3]:  # Limit to 3 competitors
                    analysis_tasks.append(self._analyze_single_url(comp_url))

            results = await asyncio.gather(*analysis_tasks, return_exceptions=True)

            # Process results
            target_analysis = results[0] if not isinstance(results[0], Exception) else {}
            competitor_analyses = [
                result for result in results[1:]
                if not isinstance(result, Exception)
            ]

            # Generate comparative insights
            comparative_insights = self._generate_comparative_insights(
                target_analysis, competitor_analyses
            )

            return {
                'target_url': target_url,
                'target_analysis': target_analysis,
                'competitor_analyses': competitor_analyses,
                'comparative_insights': comparative_insights,
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'methodology': 'custom_search_engine_crawling'
            }

        except Exception as e:
            campaign_logger.error(f"Backlink analysis failed for {target_url}: {e}")
            return {'error': str(e), 'target_url': target_url}

    async def _analyze_single_url(self, url: str) -> Dict[str, Any]:
        """
        Analyze backlinks for a single URL using multiple strategies.
        """
        clean_url = self._clean_url(url)

        # Execute different discovery methods in parallel
        search_backlinks = await self._discover_via_search_engines(clean_url)
        social_backlinks = await self._discover_social_mentions(clean_url)
        forum_backlinks = await self._discover_forum_mentions(clean_url)
        citation_backlinks = await self._discover_brand_citations(clean_url)

        # Combine all backlinks
        all_backlinks = (
            search_backlinks +
            social_backlinks +
            forum_backlinks +
            citation_backlinks
        )

        # Deduplicate and quality score
        unique_backlinks = self._deduplicate_backlinks(all_backlinks)
        quality_profile = self._assess_backlink_quality(unique_backlinks)

        return {
            'url': clean_url,
            'total_backlinks': len(unique_backlinks),
            'unique_domains': len(set(bl.get('source_domain', '') for bl in unique_backlinks)),
            'backlinks': unique_backlinks[:500],  # Limit for storage
            'quality_profile': quality_profile,
            'discovery_methods': {
                'search_engine': len(search_backlinks),
                'social_media': len(social_backlinks),
                'forums': len(forum_backlinks),
                'citations': len(citation_backlinks)
            }
        }

    async def _discover_via_search_engines(self, target_url: str) -> List[Dict[str, Any]]:
        """
        Discover backlinks using search engine queries.
        """
        backlinks = []

        # Use our Exa and Tavily APIs for backlink discovery
        for operator in self.backlink_operators:
            try:
                query = operator.format(url=target_url)

                # Use Exa for semantic search
                exa_results = await self._search_exa_for_backlinks(query)
                backlinks.extend(exa_results)

                # Use Tavily for broader search
                tavily_results = await self._search_tavily_for_backlinks(query)
                backlinks.extend(tavily_results)

                # Rate limiting
                await asyncio.sleep(self.rate_limit_delay)

            except Exception as e:
                campaign_logger.warning(f"Search query failed for {query}: {e}")
                continue

        return backlinks

    async def _search_exa_for_backlinks(self, query: str) -> List[Dict[str, Any]]:
        """
        Use Exa API to find backlink mentions.
        """
        try:
            from services.research.exa_service import ExaService

            exa_service = ExaService()
            results = await exa_service.search_and_contents(
                query=query,
                type="neural",
                num_results=25,
                include_text=[query.split('"')[1] if '"' in query else query]
            )

            backlinks = []
            for result in results.get('results', []):
                backlinks.append({
                    'source_url': result.get('url', ''),
                    'source_title': result.get('title', ''),
                    'anchor_text': self._extract_anchor_text(result.get('content', ''), query),
                    'link_type': 'search_mention',
                    'discovered_via': 'exa_api',
                    'content_snippet': result.get('content', '')[:200]
                })

            return backlinks

        except Exception as e:
            campaign_logger.warning(f"Exa backlink search failed: {e}")
            return []

    async def _search_tavily_for_backlinks(self, query: str) -> List[Dict[str, Any]]:
        """
        Use Tavily API to find backlink mentions.
        """
        try:
            from services.research.tavily_service import TavilyService

            tavily_service = TavilyService()
            results = await tavily_service.search(
                query=query,
                search_depth="advanced",
                max_results=20,
                include_raw_content=True
            )

            backlinks = []
            for result in results.get('results', []):
                backlinks.append({
                    'source_url': result.get('url', ''),
                    'source_title': result.get('title', ''),
                    'anchor_text': self._extract_anchor_text(result.get('content', ''), query),
                    'link_type': 'search_mention',
                    'discovered_via': 'tavily_api',
                    'content_snippet': result.get('content', '')[:200]
                })

            return backlinks

        except Exception as e:
            campaign_logger.warning(f"Tavily backlink search failed: {e}")
            return []

    async def _discover_social_mentions(self, target_url: str) -> List[Dict[str, Any]]:
        """
        Discover social media mentions and shares.
        """
        social_backlinks = []

        try:
            # Search for social media mentions using our APIs
            social_queries = [
                f'site:twitter.com "{target_url}"',
                f'site:linkedin.com "{target_url}"',
                f'site:facebook.com "{target_url}"',
                f'site:reddit.com "{target_url}"'
            ]

            for query in social_queries:
                try:
                    # Use Tavily for social discovery (good at finding social content)
                    from services.research.tavily_service import TavilyService
                    tavily_service = TavilyService()

                    results = await tavily_service.search(
                        query=query,
                        search_depth="basic",
                        max_results=10,
                        include_domains=self.social_platforms
                    )

                    for result in results.get('results', []):
                        social_backlinks.append({
                            'source_url': result.get('url', ''),
                            'source_title': result.get('title', ''),
                            'anchor_text': target_url,
                            'link_type': 'social_mention',
                            'discovered_via': 'tavily_social',
                            'platform': self._identify_social_platform(result.get('url', ''))
                        })

                    await asyncio.sleep(self.rate_limit_delay)

                except Exception as e:
                    campaign_logger.warning(f"Social query failed for {query}: {e}")
                    continue

        except Exception as e:
            campaign_logger.warning(f"Social media discovery failed: {e}")

        return social_backlinks

    async def _discover_forum_mentions(self, target_url: str) -> List[Dict[str, Any]]:
        """
        Discover forum and community mentions.
        """
        forum_backlinks = []

        try:
            # Search for forum mentions
            forum_query = f'"{target_url}" site:reddit.com OR site:quora.com OR site:forum.'

            from services.research.tavily_service import TavilyService
            tavily_service = TavilyService()

            results = await tavily_service.search(
                query=forum_query,
                search_depth="advanced",
                max_results=15,
                include_raw_content=True
            )

            for result in results.get('results', []):
                forum_backlinks.append({
                    'source_url': result.get('url', ''),
                    'source_title': result.get('title', ''),
                    'anchor_text': target_url,
                    'link_type': 'forum_mention',
                    'discovered_via': 'tavily_forum',
                    'content_snippet': result.get('content', '')[:300]
                })

        except Exception as e:
            campaign_logger.warning(f"Forum discovery failed: {e}")

        return forum_backlinks

    async def _discover_brand_citations(self, target_url: str) -> List[Dict[str, Any]]:
        """
        Discover brand citations that could be converted to backlinks.
        """
        citations = []

        try:
            # Extract domain for brand name variations
            domain = urlparse(target_url).netloc
            brand_name = domain.split('.')[0]  # Simple brand extraction

            citation_queries = [
                f'"{brand_name}" -site:{domain}',  # Brand mentions excluding own site
                f'"{domain}" -site:{domain}',      # Domain mentions excluding own site
            ]

            for query in citation_queries:
                try:
                    from services.research.exa_service import ExaService
                    exa_service = ExaService()

                    results = await exa_service.search_and_contents(
                        query=query,
                        type="neural",
                        num_results=15,
                        include_text=[brand_name, domain]
                    )

                    for result in results.get('results', []):
                        citations.append({
                            'source_url': result.get('url', ''),
                            'source_title': result.get('title', ''),
                            'anchor_text': brand_name,
                            'link_type': 'brand_citation',
                            'discovered_via': 'exa_citation',
                            'content_snippet': result.get('content', '')[:200]
                        })

                    await asyncio.sleep(self.rate_limit_delay)

                except Exception as e:
                    campaign_logger.warning(f"Citation query failed for {query}: {e}")
                    continue

        except Exception as e:
            campaign_logger.warning(f"Brand citation discovery failed: {e}")

        return citations

    def _deduplicate_backlinks(self, backlinks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate backlinks based on source URL.
        """
        seen_urls = set()
        unique_backlinks = []

        for backlink in backlinks:
            url = backlink.get('source_url', '').strip().lower()
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_backlinks.append(backlink)

        return unique_backlinks

    def _assess_backlink_quality(self, backlinks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Assess the overall quality of discovered backlinks.
        """
        if not backlinks:
            return {'overall_score': 0, 'quality_distribution': {}}

        # Simple quality scoring based on available data
        quality_scores = []

        for backlink in backlinks:
            score = 0.5  # Base score

            # Domain authority proxy (check TLD)
            url = backlink.get('source_url', '')
            if any(tld in url for tld in ['.edu', '.gov', '.org']):
                score += 0.3

            # Social media bonus
            if backlink.get('link_type') == 'social_mention':
                score += 0.1

            # Forum bonus
            if backlink.get('link_type') == 'forum_mention':
                score += 0.1

            # Content quality indicator
            content = backlink.get('content_snippet', '')
            if len(content) > 100:
                score += 0.1

            quality_scores.append(min(1.0, score))

        # Calculate distribution
        quality_distribution = {
            'high_quality': len([s for s in quality_scores if s >= 0.8]),
            'medium_quality': len([s for s in quality_scores if 0.6 <= s < 0.8]),
            'low_quality': len([s for s in quality_scores if s < 0.6])
        }

        return {
            'overall_score': sum(quality_scores) / len(quality_scores) if quality_scores else 0,
            'quality_distribution': quality_distribution,
            'total_backlinks': len(backlinks),
            'average_quality': sum(quality_scores) / len(quality_scores) if quality_scores else 0
        }

    def _generate_comparative_insights(self, target_analysis: Dict, competitor_analyses: List[Dict]) -> Dict[str, Any]:
        """
        Generate comparative insights between target and competitors.
        """
        insights = {
            'backlink_advantage': 'unknown',
            'quality_comparison': {},
            'opportunity_gaps': [],
            'recommendations': []
        }

        if not competitor_analyses:
            return insights

        target_score = target_analysis.get('quality_profile', {}).get('overall_score', 0)
        target_count = target_analysis.get('total_backlinks', 0)

        competitor_scores = [
            comp.get('quality_profile', {}).get('overall_score', 0)
            for comp in competitor_analyses
        ]
        competitor_counts = [
            comp.get('total_backlinks', 0)
            for comp in competitor_analyses
        ]

        # Compare backlink profiles
        avg_competitor_score = sum(competitor_scores) / len(competitor_scores) if competitor_scores else 0
        avg_competitor_count = sum(competitor_counts) / len(competitor_counts) if competitor_counts else 0

        if target_score > avg_competitor_score * 1.2:
            insights['backlink_advantage'] = 'strong'
            insights['recommendations'].append('Maintain strong backlink profile advantage')
        elif target_score < avg_competitor_score * 0.8:
            insights['backlink_advantage'] = 'weak'
            insights['recommendations'].append('Focus on backlink acquisition strategies')
            insights['opportunity_gaps'].append('Backlink quality gap with competitors')

        # Identify unique backlink sources
        target_domains = set()
        competitor_domains = set()

        for backlink in target_analysis.get('backlinks', []):
            domain = self._extract_domain(backlink.get('source_url', ''))
            target_domains.add(domain)

        for comp_analysis in competitor_analyses:
            for backlink in comp_analysis.get('backlinks', []):
                domain = self._extract_domain(backlink.get('source_url', ''))
                competitor_domains.add(domain)

        unique_competitor_domains = competitor_domains - target_domains
        if unique_competitor_domains:
            insights['opportunity_gaps'].append(
                f'Competitors have backlinks from {len(unique_competitor_domains)} unique domains'
            )
            insights['recommendations'].append(
                f'Consider targeting backlinks from domains: {list(unique_competitor_domains)[:5]}...'
            )

        return insights

    def _clean_url(self, url: str) -> str:
        """Clean and normalize URL."""
        if not url:
            return ""
        return url.strip().rstrip('/').lower()

    def _extract_anchor_text(self, content: str, query: str) -> str:
        """Extract anchor text around the target URL or brand."""
        # Simple extraction - could be enhanced
        if '"' in query:
            target = query.split('"')[1]
        else:
            target = query

        # Look for text around the target
        content_lower = content.lower()
        target_lower = target.lower()

        if target_lower in content_lower:
            start = content_lower.find(target_lower)
            # Extract some context around the target
            context_start = max(0, start - 50)
            context_end = min(len(content), start + len(target) + 50)
            context = content[context_start:context_end]

            # Try to find link-like patterns
            link_pattern = r'<a[^>]*>([^<]*)</a>'
            matches = re.findall(link_pattern, context, re.IGNORECASE)
            if matches:
                return matches[0].strip()

        return target  # Fallback to the target itself

    def _identify_social_platform(self, url: str) -> str:
        """Identify which social platform a URL belongs to."""
        domain = urlparse(url).netloc.lower()
        for platform in self.social_platforms:
            if platform in domain:
                return platform.split('.')[0]  # e.g., 'twitter' from 'twitter.com'
        return 'unknown'

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            return urlparse(url).netloc.lower()
        except:
            return ""

    # Google Trends Enhanced Competitor Analysis Methods

    async def analyze_competitor_trends(
        self,
        target_keywords: List[str],
        competitor_keywords: List[str],
        target_url: str = None,
        competitor_urls: List[str] = None,
        enable_trend_analysis: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze competitor trends and identify strategic opportunities.

        Args:
            target_keywords: Keywords for your campaign/target
            competitor_keywords: Keywords associated with competitors
            target_url: Your website URL (optional)
            competitor_urls: Competitor website URLs (optional)
            enable_trend_analysis: Whether to include trend analysis

        Returns:
            Comprehensive competitor trend analysis
        """
        try:
            campaign_logger.info(f"Starting competitor trend analysis with {len(target_keywords)} target and {len(competitor_keywords)} competitor keywords")

            analysis_result = {
                'target_keywords': target_keywords,
                'competitor_keywords': competitor_keywords,
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'trend_analysis_enabled': enable_trend_analysis
            }

            if not enable_trend_analysis:
                campaign_logger.info("Trend analysis disabled, returning basic structure")
                return analysis_result

            # Phase 1: Analyze target keyword trends
            target_trend_data = await self.google_trends.analyze_trends(
                keywords=target_keywords[:5],  # Limit to 5 for API efficiency
                timeframe='today 12-m',
                geo='US'
            )

            # Phase 2: Analyze competitor keyword trends
            competitor_trend_data = await self.google_trends.analyze_trends(
                keywords=competitor_keywords[:5],  # Limit to 5 for API efficiency
                timeframe='today 12-m',
                geo='US'
            )

            # Phase 3: Comparative trend analysis
            comparative_analysis = self._compare_trend_performance(
                target_trend_data, competitor_trend_data,
                target_keywords, competitor_keywords
            )

            # Phase 4: Strategic opportunity identification
            strategic_opportunities = self._identify_competitive_trend_opportunities(
                comparative_analysis, target_keywords, competitor_keywords
            )

            # Phase 5: Content gap analysis based on trends
            content_gaps = self._analyze_trend_based_content_gaps(
                target_trend_data, competitor_trend_data,
                target_keywords, competitor_keywords
            )

            analysis_result.update({
                'target_trend_data': target_trend_data,
                'competitor_trend_data': competitor_trend_data,
                'comparative_analysis': comparative_analysis,
                'strategic_opportunities': strategic_opportunities,
                'content_gaps': content_gaps,
                'trend_insights': self._generate_trend_insights(
                    target_trend_data, competitor_trend_data, comparative_analysis
                ),
                'recommendations': self._generate_competitive_recommendations(
                    comparative_analysis, strategic_opportunities, content_gaps
                )
            })

            campaign_logger.info("Competitor trend analysis completed successfully")
            return analysis_result

        except Exception as e:
            campaign_logger.error(f"Competitor trend analysis failed: {e}")
            return {
                'error': str(e),
                'target_keywords': target_keywords,
                'competitor_keywords': competitor_keywords,
                'analysis_timestamp': datetime.utcnow().isoformat()
            }

    def _compare_trend_performance(
        self,
        target_trends: Dict[str, Any],
        competitor_trends: Dict[str, Any],
        target_keywords: List[str],
        competitor_keywords: List[str]
    ) -> Dict[str, Any]:
        """
        Compare trend performance between target and competitor keywords.

        Args:
            target_trends: Trend data for target keywords
            competitor_trends: Trend data for competitor keywords
            target_keywords: Target keyword list
            competitor_keywords: Competitor keyword list

        Returns:
            Comparative trend analysis
        """
        try:
            comparison = {
                'target_avg_interest': 0,
                'competitor_avg_interest': 0,
                'target_volatility': 0,
                'competitor_volatility': 0,
                'keyword_comparisons': [],
                'trend_advantage_score': 0,
                'rising_topic_overlap': 0,
                'rising_query_overlap': 0
            }

            # Calculate average interest scores
            target_interest = target_trends.get('interest_over_time', [])
            competitor_interest = competitor_trends.get('interest_over_time', [])

            if target_interest:
                target_values = [p.get('value', 0) for p in target_interest if isinstance(p, dict)]
                comparison['target_avg_interest'] = sum(target_values) / len(target_values) if target_values else 0
                comparison['target_volatility'] = self._calculate_volatility(target_values)

            if competitor_interest:
                competitor_values = [p.get('value', 0) for p in competitor_interest if isinstance(p, dict)]
                comparison['competitor_avg_interest'] = sum(competitor_values) / len(competitor_values) if competitor_values else 0
                comparison['competitor_volatility'] = self._calculate_volatility(competitor_values)

            # Compare individual keyword performance
            keyword_comparisons = []
            for target_kw in target_keywords[:3]:  # Limit comparisons
                for comp_kw in competitor_keywords[:3]:
                    comparison_score = self._compare_keyword_trends(
                        target_kw, comp_kw, target_trends, competitor_trends
                    )
                    keyword_comparisons.append({
                        'target_keyword': target_kw,
                        'competitor_keyword': comp_kw,
                        'relative_performance': comparison_score
                    })

            comparison['keyword_comparisons'] = keyword_comparisons

            # Calculate trend advantage score
            if comparison['competitor_avg_interest'] > 0:
                comparison['trend_advantage_score'] = (
                    comparison['target_avg_interest'] - comparison['competitor_avg_interest']
                ) / comparison['competitor_avg_interest']
            else:
                comparison['trend_advantage_score'] = 1.0 if comparison['target_avg_interest'] > 0 else 0.0

            # Calculate topic and query overlaps
            target_rising_topics = set(
                topic.get('topic_title', '').lower()
                for topic in target_trends.get('related_topics', {}).get('rising', [])
                if isinstance(topic, dict)
            )
            competitor_rising_topics = set(
                topic.get('topic_title', '').lower()
                for topic in competitor_trends.get('related_topics', {}).get('rising', [])
                if isinstance(topic, dict)
            )

            target_rising_queries = set(
                query.get('query', '').lower()
                for query in target_trends.get('related_queries', {}).get('rising', [])
                if isinstance(query, dict)
            )
            competitor_rising_queries = set(
                query.get('query', '').lower()
                for query in competitor_trends.get('related_queries', {}).get('rising', [])
                if isinstance(query, dict)
            )

            if target_rising_topics or competitor_rising_topics:
                overlap = len(target_rising_topics & competitor_rising_topics)
                total = len(target_rising_topics | competitor_rising_topics)
                comparison['rising_topic_overlap'] = overlap / total if total > 0 else 0

            if target_rising_queries or competitor_rising_queries:
                overlap = len(target_rising_queries & competitor_rising_queries)
                total = len(target_rising_queries | competitor_rising_queries)
                comparison['rising_query_overlap'] = overlap / total if total > 0 else 0

            return comparison

        except Exception as e:
            campaign_logger.warning(f"Trend performance comparison failed: {e}")
            return {
                'error': str(e),
                'target_avg_interest': 0,
                'competitor_avg_interest': 0,
                'trend_advantage_score': 0
            }

    def _calculate_volatility(self, values: List[float]) -> float:
        """Calculate coefficient of variation for trend volatility."""
        if not values or len(values) < 2:
            return 0.0

        mean = sum(values) / len(values)
        if mean == 0:
            return 0.0

        variance = sum((x - mean) ** 2 for x in values) / len(values)
        std_dev = variance ** 0.5

        return std_dev / mean  # Coefficient of variation

    def _compare_keyword_trends(
        self,
        target_kw: str,
        competitor_kw: str,
        target_trends: Dict[str, Any],
        competitor_trends: Dict[str, Any]
    ) -> float:
        """
        Compare trend performance between two specific keywords.

        Returns: Relative performance score (-1 to 1, where positive favors target)
        """
        # Simplified comparison - in production, this would analyze overlap
        # between keyword mentions in related topics/queries
        target_relevance = 0
        competitor_relevance = 0

        # Check if keywords appear in rising topics
        for topic in target_trends.get('related_topics', {}).get('rising', []):
            if isinstance(topic, dict) and target_kw.lower() in topic.get('topic_title', '').lower():
                target_relevance += 1

        for topic in competitor_trends.get('related_topics', {}).get('rising', []):
            if isinstance(topic, dict) and competitor_kw.lower() in topic.get('topic_title', '').lower():
                competitor_relevance += 1

        if target_relevance + competitor_relevance == 0:
            return 0.0

        return (target_relevance - competitor_relevance) / (target_relevance + competitor_relevance)

    def _identify_competitive_trend_opportunities(
        self,
        comparative_analysis: Dict[str, Any],
        target_keywords: List[str],
        competitor_keywords: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Identify strategic opportunities based on competitive trend analysis.

        Args:
            comparative_analysis: Results from trend comparison
            target_keywords: Target keyword list
            competitor_keywords: Competitor keyword list

        Returns:
            List of strategic opportunities
        """
        opportunities = []

        # Opportunity 1: Trend advantage exploitation
        trend_advantage = comparative_analysis.get('trend_advantage_score', 0)
        if trend_advantage > 0.2:  # Target has significant trend advantage
            opportunities.append({
                'type': 'trend_advantage_exploitation',
                'title': 'Leverage Trend Momentum Advantage',
                'description': f'Your keywords show {trend_advantage*100:.1f}% higher trend momentum than competitors',
                'opportunity_score': min(1.0, trend_advantage),
                'recommended_action': 'Prioritize content around high-momentum keywords',
                'expected_impact': 'high'
            })

        # Opportunity 2: Rising topic gaps
        rising_topic_overlap = comparative_analysis.get('rising_topic_overlap', 0)
        if rising_topic_overlap < 0.3:  # Low overlap indicates differentiation opportunity
            opportunities.append({
                'type': 'rising_topic_differentiation',
                'title': 'Capitalize on Unique Rising Topics',
                'description': f'Only {rising_topic_overlap*100:.1f}% overlap in rising topics with competitors',
                'opportunity_score': 1.0 - rising_topic_overlap,
                'recommended_action': 'Create content around competitor-gap rising topics',
                'expected_impact': 'high'
            })

        # Opportunity 3: Volatility exploitation
        target_volatility = comparative_analysis.get('target_volatility', 0)
        competitor_volatility = comparative_analysis.get('competitor_volatility', 0)

        if target_volatility > competitor_volatility * 1.2:  # Target has more volatile (trending) keywords
            opportunities.append({
                'type': 'volatility_opportunity',
                'title': 'Exploit Keyword Trend Volatility',
                'description': f'Your keywords show {target_volatility/competitor_volatility:.1f}x more volatility than competitors',
                'opportunity_score': min(1.0, target_volatility / competitor_volatility if competitor_volatility > 0 else 1.0),
                'recommended_action': 'Focus on volatile keywords for breaking content opportunities',
                'expected_impact': 'medium'
            })

        # Opportunity 4: Interest score gaps
        target_avg = comparative_analysis.get('target_avg_interest', 0)
        competitor_avg = comparative_analysis.get('competitor_avg_interest', 0)

        if target_avg > competitor_avg * 1.1:  # Target has higher interest
            opportunities.append({
                'type': 'interest_score_advantage',
                'title': 'Capitalize on Higher Search Interest',
                'description': f'Your keywords have {target_avg/competitor_avg:.1f}x higher search interest',
                'opportunity_score': min(1.0, target_avg / competitor_avg if competitor_avg > 0 else 1.0),
                'recommended_action': 'Prioritize high-interest keywords for maximum visibility',
                'expected_impact': 'high'
            })

        return opportunities

    def _analyze_trend_based_content_gaps(
        self,
        target_trends: Dict[str, Any],
        competitor_trends: Dict[str, Any],
        target_keywords: List[str],
        competitor_keywords: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Identify content gaps based on trend analysis differences.

        Args:
            target_trends: Target keyword trend data
            competitor_trends: Competitor keyword trend data
            target_keywords: Target keywords
            competitor_keywords: Competitor keywords

        Returns:
            List of trend-based content gaps
        """
        content_gaps = []

        # Extract rising topics and queries
        target_rising_topics = target_trends.get('related_topics', {}).get('rising', [])
        competitor_rising_topics = competitor_trends.get('related_topics', {}).get('rising', [])

        target_rising_queries = target_trends.get('related_queries', {}).get('rising', [])
        competitor_rising_queries = competitor_trends.get('related_queries', {}).get('rising', [])

        # Find rising topics competitors are missing
        target_topic_titles = set(
            topic.get('topic_title', '').lower()
            for topic in target_rising_topics
            if isinstance(topic, dict)
        )
        competitor_topic_titles = set(
            topic.get('topic_title', '').lower()
            for topic in competitor_rising_topics
            if isinstance(topic, dict)
        )

        unique_target_topics = target_topic_titles - competitor_topic_titles

        for topic in unique_target_topics:
            content_gaps.append({
                'gap_type': 'unique_rising_topic',
                'content_topic': topic,
                'description': f"Rising topic '{topic}' appears in your trend analysis but not competitors'",
                'gap_score': 0.9,
                'competitive_advantage': 'high',
                'recommended_content': f"Comprehensive analysis of '{topic}' trends and implications"
            })

        # Find rising queries competitors are missing
        target_query_texts = set(
            query.get('query', '').lower()
            for query in target_rising_queries
            if isinstance(query, dict)
        )
        competitor_query_texts = set(
            query.get('query', '').lower()
            for query in competitor_rising_queries
            if isinstance(query, dict)
        )

        unique_target_queries = target_query_texts - competitor_query_texts

        for query in unique_target_queries:
            content_gaps.append({
                'gap_type': 'unique_rising_query',
                'content_topic': query,
                'description': f"Rising search query '{query}' appears in your trend analysis but not competitors'",
                'gap_score': 0.8,
                'competitive_advantage': 'high',
                'recommended_content': f"Definitive guide answering '{query}'"
            })

        return content_gaps

    def _generate_trend_insights(
        self,
        target_trends: Dict[str, Any],
        competitor_trends: Dict[str, Any],
        comparative_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive trend insights from comparative analysis.

        Args:
            target_trends: Target trend data
            competitor_trends: Competitor trend data
            comparative_analysis: Comparative analysis results

        Returns:
            Key trend insights
        """
        insights = {
            'target_trend_strength': 'weak',
            'competitor_trend_strength': 'weak',
            'competitive_position': 'neutral',
            'opportunity_level': 'low',
            'risk_level': 'low',
            'key_findings': []
        }

        # Assess trend strength
        target_avg = comparative_analysis.get('target_avg_interest', 0)
        competitor_avg = comparative_analysis.get('competitor_avg_interest', 0)

        if target_avg > 75:
            insights['target_trend_strength'] = 'strong'
        elif target_avg > 50:
            insights['target_trend_strength'] = 'moderate'

        if competitor_avg > 75:
            insights['competitor_trend_strength'] = 'strong'
        elif competitor_avg > 50:
            insights['competitor_trend_strength'] = 'moderate'

        # Determine competitive position
        advantage_score = comparative_analysis.get('trend_advantage_score', 0)

        if advantage_score > 0.2:
            insights['competitive_position'] = 'advantage'
            insights['opportunity_level'] = 'high'
            insights['key_findings'].append('Strong trend advantage over competitors')
        elif advantage_score < -0.2:
            insights['competitive_position'] = 'disadvantage'
            insights['risk_level'] = 'high'
            insights['key_findings'].append('Competitors have stronger trend momentum')
        else:
            insights['competitive_position'] = 'competitive'
            insights['opportunity_level'] = 'medium'

        # Add volatility insights
        target_volatility = comparative_analysis.get('target_volatility', 0)
        competitor_volatility = comparative_analysis.get('competitor_volatility', 0)

        if target_volatility > competitor_volatility * 1.2:
            insights['key_findings'].append('Your keywords show higher volatility - potential for breakout content')
        elif competitor_volatility > target_volatility * 1.2:
            insights['key_findings'].append('Competitors have more volatile keywords - they may be capturing trending topics')

        return insights

    def _generate_competitive_recommendations(
        self,
        comparative_analysis: Dict[str, Any],
        strategic_opportunities: List[Dict[str, Any]],
        content_gaps: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Generate actionable recommendations based on competitive trend analysis.

        Args:
            comparative_analysis: Comparative trend analysis
            strategic_opportunities: Identified strategic opportunities
            content_gaps: Trend-based content gaps

        Returns:
            Prioritized list of recommendations
        """
        recommendations = []

        # Sort opportunities by score
        sorted_opportunities = sorted(
            strategic_opportunities,
            key=lambda x: x.get('opportunity_score', 0),
            reverse=True
        )

        for opportunity in sorted_opportunities[:3]:  # Top 3 opportunities
            recommendations.append({
                'priority': 'high' if opportunity.get('expected_impact') == 'high' else 'medium',
                'category': 'competitive_strategy',
                'title': opportunity.get('title', ''),
                'description': opportunity.get('description', ''),
                'action_items': [opportunity.get('recommended_action', '')],
                'expected_impact': opportunity.get('expected_impact', 'medium'),
                'timeline': 'immediate' if opportunity.get('expected_impact') == 'high' else 'strategic'
            })

        # Add content gap recommendations
        for gap in content_gaps[:2]:  # Top 2 content gaps
            recommendations.append({
                'priority': 'high',
                'category': 'content_strategy',
                'title': f"Address Content Gap: {gap.get('content_topic', '')}",
                'description': gap.get('description', ''),
                'action_items': [gap.get('recommended_content', '')],
                'expected_impact': 'high',
                'timeline': 'immediate'
            })

        # Add general trend-based recommendations
        trend_advantage = comparative_analysis.get('trend_advantage_score', 0)

        if trend_advantage > 0:
            recommendations.append({
                'priority': 'high',
                'category': 'trend_optimization',
                'title': 'Optimize for Trend Momentum',
                'description': 'Leverage your trend advantage by focusing on high-momentum keywords and topics',
                'action_items': [
                    'Prioritize content around rising topics in your trend analysis',
                    'Monitor trend momentum weekly and adjust content calendar',
                    'Create trend-aware content series'
                ],
                'expected_impact': 'high',
                'timeline': 'ongoing'
            })

        return recommendations