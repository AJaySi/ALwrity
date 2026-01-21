"""
Content Gap Analysis Service

Analyzes prospect websites for content gaps using sitemap parsing and AI-powered analysis.
Identifies opportunities for guest posting based on missing content topics.
"""

import asyncio
import re
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional, Set
from urllib.parse import urlparse, urljoin
from datetime import datetime
import aiohttp
from bs4 import BeautifulSoup
import logging

from .logging_utils import campaign_logger
from .config import get_config

# Import Google Trends service for trend-enhanced analysis
from ..research.trends.google_trends_service import GoogleTrendsService


class SitemapContentGapAnalyzer:
    """
    Analyzes website content gaps using sitemap parsing and AI analysis.

    Strategy:
    1. Discover and parse XML sitemaps
    2. Extract blog post titles and topics
    3. Use AI to identify content gaps
    4. Generate strategic recommendations
    """

    def __init__(self):
        self.config = get_config()
        self.session_timeout = aiohttp.ClientTimeout(total=30)
        self.max_sitemaps = 5
        self.max_pages_per_sitemap = 1000
        self.google_trends = GoogleTrendsService()  # Initialize Google Trends service

        # Common sitemap URL patterns
        self.sitemap_patterns = [
            '/sitemap.xml',
            '/sitemap_index.xml',
            '/sitemap.php',
            '/wp-sitemap.xml',      # WordPress
            '/sitemap/sitemap.xml', # Some CMS
            '/sitemaps/sitemap.xml',
        ]

        # Blog post URL patterns to identify content pages
        self.blog_patterns = [
            r'/blog/',
            r'/article/',
            r'/post/',
            r'/news/',
            r'/insight/',
            r'/guide/',
            r'/tutorial/',
            r'/how-to/',
            r'/tips/',
            r'/(\d{4})/(\d{2})/',  # Date-based URLs
        ]

    async def analyze_content_gaps(
        self,
        prospect_url: str,
        campaign_keywords: List[str],
        industry: str = "general",
        trend_data: Optional[Dict[str, Any]] = None,
        enable_trend_analysis: bool = False
    ) -> Dict[str, Any]:
        """
        Comprehensive content gap analysis for a prospect website.

        Args:
            prospect_url: Prospect website URL
            campaign_keywords: Campaign target keywords
            industry: Industry context
            trend_data: Optional Google Trends data for enhanced analysis
            enable_trend_analysis: Whether to include trend-based gap prioritization

        Returns:
            Detailed content gap analysis with optional trend enhancements
        """
        try:
            campaign_logger.info(f"Starting content gap analysis for: {prospect_url}")

            # Phase 1: Sitemap discovery
            sitemaps = await self._discover_sitemaps(prospect_url)
            campaign_logger.info(f"Found {len(sitemaps)} sitemaps for {prospect_url}")

            # Phase 2: Content extraction
            content_inventory = await self._extract_content_from_sitemaps(sitemaps)
            campaign_logger.info(f"Extracted {len(content_inventory['pages'])} pages from sitemaps")

            # Phase 3: Content analysis
            content_analysis = self._analyze_content_topics(content_inventory, campaign_keywords)

            # Phase 4: Gap identification with AI
            content_gaps = await self._identify_content_gaps_with_ai(
                content_analysis, campaign_keywords, industry
            )

            # Phase 5: Strategic recommendations
            recommendations = await self._generate_strategic_recommendations(
                content_gaps, content_analysis, campaign_keywords
            )

            # Phase 6: Trend-enhanced analysis (if enabled)
            trend_enhanced_results = {}
            if enable_trend_analysis and trend_data:
                campaign_logger.info("Phase 6: Applying trend-enhanced gap analysis")
                trend_enhanced_results = await self._apply_trend_enhanced_analysis(
                    content_gaps, content_analysis, recommendations, trend_data, campaign_keywords
                )

            methodology = 'sitemap_ai_trend_analysis' if enable_trend_analysis and trend_data else 'sitemap_ai_analysis'

            result = {
                'prospect_url': prospect_url,
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'content_inventory': content_inventory,
                'content_analysis': content_analysis,
                'content_gaps': content_gaps,
                'recommendations': recommendations,
                'methodology': methodology
            }

            # Add trend-enhanced results if available
            if trend_enhanced_results:
                result.update({
                    'trend_enhanced_gaps': trend_enhanced_results.get('prioritized_gaps', []),
                    'seasonal_opportunities': trend_enhanced_results.get('seasonal_opportunities', []),
                    'trend_insights': trend_enhanced_results.get('trend_insights', {}),
                    'trend_based_recommendations': trend_enhanced_results.get('trend_recommendations', [])
                })

            return result

        except Exception as e:
            campaign_logger.error(f"Content gap analysis failed for {prospect_url}: {e}")
            return {
                'prospect_url': prospect_url,
                'error': str(e),
                'methodology': 'sitemap_ai_analysis'
            }

    async def _discover_sitemaps(self, base_url: str) -> List[str]:
        """
        Discover all available sitemaps for a website.
        """
        sitemap_urls = []
        base_url = base_url.rstrip('/')

        async with aiohttp.ClientSession(timeout=self.session_timeout) as session:
            # Check standard sitemap locations
            for pattern in self.sitemap_patterns:
                sitemap_url = base_url + pattern

                try:
                    campaign_logger.debug(f"Checking sitemap: {sitemap_url}")

                    async with session.get(sitemap_url, allow_redirects=True) as response:
                        if response.status == 200:
                            content_type = response.headers.get('content-type', '')
                            if 'xml' in content_type or 'text' in content_type:
                                # Verify it's actually a sitemap
                                text = await response.text()
                                if self._is_valid_sitemap(text):
                                    sitemap_urls.append(sitemap_url)
                                    campaign_logger.debug(f"Valid sitemap found: {sitemap_url}")

                                    # Check if it's an index sitemap
                                    if 'sitemapindex' in text:
                                        subsitemaps = await self._extract_subsitemaps(session, text, base_url)
                                        sitemap_urls.extend(subsitemaps)

                        # Rate limiting
                        await asyncio.sleep(0.5)

                except Exception as e:
                    campaign_logger.debug(f"Sitemap check failed for {sitemap_url}: {e}")
                    continue

        return list(set(sitemap_urls))[:self.max_sitemaps]  # Limit and deduplicate

    async def _extract_subsitemaps(self, session: aiohttp.ClientSession, sitemap_content: str, base_url: str) -> List[str]:
        """
        Extract subsitemap URLs from a sitemap index.
        """
        subsitemaps = []

        try:
            root = ET.fromstring(sitemap_content)

            # Look for sitemap entries in the index
            for sitemap in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap'):
                loc_element = sitemap.find('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                if loc_element is not None and loc_element.text:
                    subsitemap_url = loc_element.text.strip()
                    # Convert relative URLs to absolute
                    if not subsitemap_url.startswith('http'):
                        subsitemap_url = urljoin(base_url, subsitemap_url)
                    subsitemaps.append(subsitemap_url)

        except Exception as e:
            campaign_logger.debug(f"Failed to extract subsitemaps: {e}")

        return subsitemaps

    def _is_valid_sitemap(self, content: str) -> bool:
        """
        Basic validation to check if content is a valid sitemap.
        """
        content_lower = content.lower()
        return (
            'urlset' in content_lower or
            'sitemapindex' in content_lower or
            '<?xml' in content_lower
        )

    async def _extract_content_from_sitemaps(self, sitemap_urls: List[str]) -> Dict[str, Any]:
        """
        Extract content information from discovered sitemaps.
        """
        all_pages = []
        blog_posts = []

        async with aiohttp.ClientSession(timeout=self.session_timeout) as session:
            for sitemap_url in sitemap_urls:
                try:
                    campaign_logger.debug(f"Parsing sitemap: {sitemap_url}")

                    async with session.get(sitemap_url) as response:
                        if response.status == 200:
                            content = await response.text()
                            pages = self._parse_sitemap_content(content, sitemap_url)

                            for page in pages:
                                all_pages.append(page)

                                # Identify blog posts
                                if self._is_blog_post_url(page['url']):
                                    blog_posts.append(page)

                except Exception as e:
                    campaign_logger.warning(f"Failed to parse sitemap {sitemap_url}: {e}")
                    continue

        return {
            'total_pages': len(all_pages),
            'blog_posts': blog_posts,
            'pages': all_pages[:self.max_pages_per_sitemap],  # Limit for performance
            'sitemaps_processed': len(sitemap_urls)
        }

    def _parse_sitemap_content(self, content: str, sitemap_url: str) -> List[Dict[str, Any]]:
        """
        Parse XML sitemap content and extract page information.
        """
        pages = []

        try:
            # Handle XML namespace
            # Remove XML declaration if present
            content = re.sub(r'<\?xml.*?\?>', '', content, flags=re.DOTALL)

            # Parse XML
            root = ET.fromstring(content)

            # Handle both regular sitemaps and sitemap indexes
            url_elements = root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url')
            if not url_elements:
                # Try without namespace
                url_elements = root.findall('.//url')

            for url_element in url_elements:
                try:
                    loc_element = url_element.find('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                    if loc_element is None:
                        loc_element = url_element.find('.//loc')

                    if loc_element is not None and loc_element.text:
                        page_url = loc_element.text.strip()

                        # Extract additional metadata
                        lastmod = None
                        priority = None
                        changefreq = None

                        lastmod_elem = url_element.find('.//{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod')
                        if lastmod_elem is None:
                            lastmod_elem = url_element.find('.//lastmod')
                        if lastmod_elem is not None:
                            lastmod = lastmod_elem.text

                        priority_elem = url_element.find('.//{http://www.sitemaps.org/schemas/sitemap/0.9}priority')
                        if priority_elem is None:
                            priority_elem = url_element.find('.//priority')
                        if priority_elem is not None:
                            priority = priority_elem.text

                        page_data = {
                            'url': page_url,
                            'lastmod': lastmod,
                            'priority': priority,
                            'changefreq': changefreq,
                            'title': self._extract_title_from_url(page_url),
                            'content_type': self._classify_content_type(page_url),
                            'topics': self._extract_topics_from_url(page_url),
                            'sitemap_source': sitemap_url
                        }

                        pages.append(page_data)

                except Exception as e:
                    campaign_logger.debug(f"Failed to parse URL element: {e}")
                    continue

        except Exception as e:
            campaign_logger.warning(f"Failed to parse sitemap content: {e}")

        return pages

    def _is_blog_post_url(self, url: str) -> bool:
        """
        Determine if a URL likely points to a blog post.
        """
        url_lower = url.lower()

        # Check for blog patterns
        for pattern in self.blog_patterns:
            if re.search(pattern, url_lower):
                return True

        # Check for date patterns in URL
        date_patterns = [
            r'/(\d{4})/(\d{2})/(\d{2})/',  # YYYY/MM/DD
            r'/(\d{4})/(\d{1,2})/(\d{1,2})/',  # YYYY/M/D variations
            r'-(\d{4})-(\d{2})-(\d{2})-',  # YYYY-MM-DD in slug
        ]

        for pattern in date_patterns:
            if re.search(pattern, url_lower):
                return True

        return False

    def _extract_title_from_url(self, url: str) -> str:
        """
        Extract a readable title from URL slug.
        """
        try:
            path = urlparse(url).path
            if not path or path == '/':
                return ""

            # Get the last meaningful part of the path
            parts = [p for p in path.split('/') if p and not p.isdigit()]
            if not parts:
                return ""

            # Take the last part and clean it up
            title_part = parts[-1]

            # Remove file extensions
            title_part = re.sub(r'\.(html|php|asp)$', '', title_part)

            # Convert slugs to readable title
            title = re.sub(r'[-_]', ' ', title_part)
            title = title.title()  # Capitalize words

            return title

        except Exception:
            return ""

    def _classify_content_type(self, url: str) -> str:
        """
        Classify the content type based on URL patterns.
        """
        url_lower = url.lower()

        # Blog content
        if any(pattern in url_lower for pattern in ['/blog/', '/article/', '/post/', '/news/']):
            return 'blog_post'

        # Guide/tutorial content
        if any(pattern in url_lower for pattern in ['/guide/', '/tutorial/', '/how-to/', '/tips/']):
            return 'guide'

        # Service/product pages
        if any(pattern in url_lower for pattern in ['/service', '/product', '/pricing/']):
            return 'service'

        # About/team pages
        if any(pattern in url_lower for pattern in ['/about', '/team', '/company/']):
            return 'about'

        # Contact pages
        if 'contact' in url_lower:
            return 'contact'

        return 'other'

    def _extract_topics_from_url(self, url: str) -> List[str]:
        """
        Extract potential topics from URL structure and slug.
        """
        topics = []

        try:
            path = urlparse(url).path.lower()

            # Extract meaningful words from path
            words = re.findall(r'\b[a-z]{3,}\b', path)

            # Filter out common stop words
            stop_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'her', 'was', 'one', 'our', 'had', 'by', 'word', 'how', 'said', 'each', 'which', 'their', 'time', 'will', 'about', 'many', 'then', 'them', 'these', 'so', 'some', 'her', 'would', 'make', 'like', 'him', 'into', 'has', 'look', 'more', 'write', 'go', 'see', 'no', 'way', 'could', 'people', 'my', 'than', 'first', 'water', 'been', 'call', 'who', 'oil', 'its', 'now', 'find', 'long', 'down', 'day', 'did', 'get', 'come', 'made', 'may', 'part'}

            topics = [word for word in words if word not in stop_words and len(word) > 2]

            # Limit to most relevant topics
            return list(set(topics))[:10]

        except Exception:
            return []

    def _analyze_content_topics(self, content_inventory: Dict[str, Any], campaign_keywords: List[str]) -> Dict[str, Any]:
        """
        Analyze the content topics and coverage.
        """
        blog_posts = content_inventory.get('blog_posts', [])
        all_pages = content_inventory.get('pages', [])

        # Extract all topics
        all_topics = set()
        topic_frequency = {}

        for page in all_pages:
            page_topics = page.get('topics', [])
            for topic in page_topics:
                all_topics.add(topic)
                topic_frequency[topic] = topic_frequency.get(topic, 0) + 1

        # Keyword coverage analysis
        keyword_coverage = {}
        for keyword in campaign_keywords:
            keyword_lower = keyword.lower()
            coverage_count = sum(1 for page in all_pages
                               if keyword_lower in ' '.join(page.get('topics', [])).lower())
            keyword_coverage[keyword] = {
                'covered_pages': coverage_count,
                'coverage_percentage': (coverage_count / len(all_pages)) * 100 if all_pages else 0
            }

        # Content type distribution
        content_types = {}
        for page in all_pages:
            content_type = page.get('content_type', 'other')
            content_types[content_type] = content_types.get(content_type, 0) + 1

        return {
            'total_topics': len(all_topics),
            'topics': list(all_topics),
            'topic_frequency': topic_frequency,
            'blog_post_count': len(blog_posts),
            'keyword_coverage': keyword_coverage,
            'content_type_distribution': content_types,
            'content_depth_score': self._calculate_content_depth_score(blog_posts)
        }

    def _calculate_content_depth_score(self, blog_posts: List[Dict[str, Any]]) -> float:
        """
        Calculate a content depth score based on posting frequency and variety.
        """
        if not blog_posts:
            return 0.0

        # Simple scoring based on post count and recency
        post_count = len(blog_posts)

        # Check for recent posts (rough estimate)
        recent_posts = 0
        current_year = datetime.now().year
        for post in blog_posts[:10]:  # Check first 10 posts
            if post.get('lastmod'):
                try:
                    post_date = datetime.fromisoformat(post['lastmod'].replace('Z', '+00:00'))
                    if post_date.year >= current_year - 1:  # Posts from last year
                        recent_posts += 1
                except:
                    continue

        # Score based on volume and recency
        volume_score = min(1.0, post_count / 50)  # 50 posts = max score
        recency_score = min(1.0, recent_posts / 10)  # 10 recent posts = max score

        return (volume_score + recency_score) / 2

    async def _identify_content_gaps_with_ai(
        self,
        content_analysis: Dict[str, Any],
        campaign_keywords: List[str],
        industry: str
    ) -> List[Dict[str, Any]]:
        """
        Use AI to identify content gaps and opportunities.
        """
        try:
            # Get LLM provider
            from services.llm_providers.gemini_grounded_provider import GeminiGroundedProvider
            llm_provider = GeminiGroundedProvider()

            # Prepare context for AI analysis
            context = {
                'existing_topics': content_analysis.get('topics', [])[:30],  # Limit for token efficiency
                'campaign_keywords': campaign_keywords,
                'industry': industry,
                'content_depth': content_analysis.get('content_depth_score', 0),
                'blog_post_count': content_analysis.get('blog_post_count', 0),
                'keyword_coverage': content_analysis.get('keyword_coverage', {})
            }

            prompt = f"""
            Analyze this website's content and identify significant content gaps that could be filled with guest posts.

            Website Content Analysis:
            - Existing Topics: {', '.join(context['existing_topics'])}
            - Industry: {context['industry']}
            - Content Depth Score: {context['content_depth']:.2f}/1.0
            - Blog Posts: {context['blog_post_count']}
            - Campaign Keywords: {', '.join(context['campaign_keywords'])}

            Identify content gaps in these categories:
            1. Keyword gaps (campaign keywords not covered)
            2. Topic gaps (industry topics missing)
            3. Trend gaps (current trends not addressed)
            4. Content format gaps (missing content types)

            For each gap, provide:
            - Gap type and description
            - Why it's a gap (opportunity rationale)
            - Suggested content topics/angles
            - Estimated value for guest posting

            Return as JSON array of gap objects.
            """

            ai_response = await llm_provider.generate_json(prompt)

            gaps = ai_response.get('content_gaps', [])

            # Enhance gaps with scoring
            for gap in gaps:
                gap['priority_score'] = self._calculate_gap_priority(gap, campaign_keywords)
                gap['opportunity_score'] = self._calculate_gap_opportunity(gap, content_analysis)

            return gaps

        except Exception as e:
            campaign_logger.warning(f"AI content gap analysis failed: {e}")
            return []

    def _calculate_gap_priority(self, gap: Dict[str, Any], campaign_keywords: List[str]) -> float:
        """
        Calculate priority score for a content gap.
        """
        score = 0.5  # Base score

        gap_type = gap.get('gap_type', '')

        # Keyword gaps are highest priority
        if gap_type == 'keyword_gap':
            score += 0.3
        elif gap_type == 'topic_gap':
            score += 0.2
        elif gap_type == 'trend_gap':
            score += 0.25

        # Check if gap relates to campaign keywords
        gap_description = gap.get('description', '').lower()
        keyword_matches = sum(1 for keyword in campaign_keywords
                            if keyword.lower() in gap_description)
        if keyword_matches > 0:
            score += 0.2

        return min(1.0, score)

    def _calculate_gap_opportunity(self, gap: Dict[str, Any], content_analysis: Dict[str, Any]) -> float:
        """
        Calculate opportunity score for a content gap.
        """
        score = 0.5  # Base score

        # Higher opportunity for underserved areas
        content_depth = content_analysis.get('content_depth_score', 0.5)
        if content_depth < 0.5:  # Low content depth = high opportunity
            score += 0.3

        # Consider blog post volume
        blog_count = content_analysis.get('blog_post_count', 0)
        if blog_count < 20:  # Small blogs have more gaps
            score += 0.2

        return min(1.0, score)

    async def _generate_strategic_recommendations(
        self,
        content_gaps: List[Dict[str, Any]],
        content_analysis: Dict[str, Any],
        campaign_keywords: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Generate strategic recommendations based on content gap analysis.
        """
        recommendations = []

        # Sort gaps by priority
        sorted_gaps = sorted(content_gaps, key=lambda x: x.get('priority_score', 0), reverse=True)

        for gap in sorted_gaps[:10]:  # Top 10 recommendations
            recommendation = {
                'gap_type': gap.get('gap_type', ''),
                'content_topic': gap.get('suggested_content', ''),
                'rationale': gap.get('description', ''),
                'priority_level': 'high' if gap.get('priority_score', 0) > 0.8 else 'medium',
                'estimated_value': self._estimate_content_value(gap, content_analysis),
                'target_keywords': self._extract_relevant_keywords(gap, campaign_keywords)
            }
            recommendations.append(recommendation)

        return recommendations

    def _estimate_content_value(self, gap: Dict[str, Any], content_analysis: Dict[str, Any]) -> str:
        """
        Estimate the value of filling this content gap.
        """
        priority = gap.get('priority_score', 0)
        opportunity = gap.get('opportunity_score', 0)

        if priority > 0.8 and opportunity > 0.7:
            return 'high'
        elif priority > 0.6 or opportunity > 0.6:
            return 'medium'
        else:
            return 'low'

    def _extract_relevant_keywords(self, gap: Dict[str, Any], campaign_keywords: List[str]) -> List[str]:
        """
        Extract campaign keywords relevant to this gap.
        """
        gap_text = f"{gap.get('description', '')} {gap.get('suggested_content', '')}".lower()

        relevant_keywords = []
        for keyword in campaign_keywords:
            if keyword.lower() in gap_text:
                relevant_keywords.append(keyword)

        return relevant_keywords

    # Google Trends Enhanced Analysis Methods

    async def _apply_trend_enhanced_analysis(
        self,
        content_gaps: List[Dict[str, Any]],
        content_analysis: Dict[str, Any],
        recommendations: List[Dict[str, Any]],
        trend_data: Dict[str, Any],
        campaign_keywords: List[str]
    ) -> Dict[str, Any]:
        """
        Apply Google Trends data to enhance content gap analysis.

        Args:
            content_gaps: Basic content gaps identified
            content_analysis: Content topic analysis
            recommendations: Basic strategic recommendations
            trend_data: Google Trends analysis data
            campaign_keywords: Campaign target keywords

        Returns:
            Trend-enhanced analysis results
        """
        try:
            # Phase 1: Trend-based gap prioritization
            prioritized_gaps = self._prioritize_gaps_by_trends(
                content_gaps, trend_data, campaign_keywords
            )

            # Phase 2: Seasonal content opportunity detection
            seasonal_opportunities = self._identify_seasonal_content_opportunities(
                content_analysis, trend_data, campaign_keywords
            )

            # Phase 3: Trend momentum analysis
            trend_insights = self._analyze_trend_momentum_and_opportunities(
                trend_data, campaign_keywords
            )

            # Phase 4: Trend-based recommendations enhancement
            trend_recommendations = self._generate_trend_based_recommendations(
                prioritized_gaps, seasonal_opportunities, trend_insights, campaign_keywords
            )

            return {
                'prioritized_gaps': prioritized_gaps,
                'seasonal_opportunities': seasonal_opportunities,
                'trend_insights': trend_insights,
                'trend_recommendations': trend_recommendations,
                'enhancement_timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            campaign_logger.warning(f"Trend-enhanced analysis failed: {e}")
            return {
                'prioritized_gaps': content_gaps,
                'seasonal_opportunities': [],
                'trend_insights': {},
                'trend_recommendations': recommendations,
                'error': str(e)
            }

    def _prioritize_gaps_by_trends(
        self,
        content_gaps: List[Dict[str, Any]],
        trend_data: Dict[str, Any],
        campaign_keywords: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Prioritize content gaps based on trend relevance and momentum.

        Args:
            content_gaps: Basic content gaps
            trend_data: Google Trends data
            campaign_keywords: Campaign keywords

        Returns:
            Gaps prioritized by trend factors
        """
        # Extract trend factors
        related_topics = trend_data.get("related_topics", {})
        rising_topics = related_topics.get("rising", [])
        top_topics = related_topics.get("top", [])

        related_queries = trend_data.get("related_queries", {})
        rising_queries = related_queries.get("rising", [])
        top_queries = related_queries.get("top", [])

        # Calculate trend scores for each gap
        enhanced_gaps = []
        for gap in content_gaps:
            gap_text = f"{gap.get('description', '')} {gap.get('suggested_content', '')}".lower()
            original_score = gap.get('priority_score', 0)

            # Calculate trend relevance
            trend_relevance = self._calculate_trend_relevance_score(
                gap_text, rising_topics, top_topics, rising_queries, top_queries, campaign_keywords
            )

            # Calculate seasonal alignment
            seasonal_alignment = self._calculate_seasonal_alignment_score(
                gap_text, trend_data.get("interest_over_time", [])
            )

            # Calculate overall trend score
            trend_score = (trend_relevance * 0.6) + (seasonal_alignment * 0.4)

            # Boost priority score with trend factors
            enhanced_priority_score = min(1.0, original_score + (trend_score * 0.3))

            enhanced_gap = gap.copy()
            enhanced_gap.update({
                'trend_relevance_score': trend_relevance,
                'seasonal_alignment_score': seasonal_alignment,
                'trend_boost_factor': trend_score,
                'priority_score': enhanced_priority_score,
                'trend_enhanced': True
            })

            enhanced_gaps.append(enhanced_gap)

        # Sort by enhanced priority score
        return sorted(enhanced_gaps, key=lambda x: x.get('priority_score', 0), reverse=True)

    def _calculate_trend_relevance_score(
        self,
        gap_text: str,
        rising_topics: List[Dict[str, Any]],
        top_topics: List[Dict[str, Any]],
        rising_queries: List[Dict[str, Any]],
        top_queries: List[Dict[str, Any]],
        campaign_keywords: List[str]
    ) -> float:
        """
        Calculate how relevant a content gap is to current trends.

        Returns score from 0.0 to 1.0
        """
        score = 0.0

        # Check rising topics (high weight)
        for topic in rising_topics[:10]:  # Top 10 rising topics
            topic_title = topic.get("topic_title", "").lower()
            if topic_title and topic_title in gap_text:
                score += 0.3  # Rising topics are highly valuable

        # Check top topics (medium weight)
        for topic in top_topics[:15]:  # Top 15 established topics
            topic_title = topic.get("topic_title", "").lower()
            if topic_title and topic_title in gap_text:
                score += 0.15

        # Check rising queries (high weight)
        for query in rising_queries[:10]:
            query_text = query.get("query", "").lower()
            if query_text and query_text in gap_text:
                score += 0.25

        # Check top queries (medium weight)
        for query in top_queries[:15]:
            query_text = query.get("query", "").lower()
            if query_text and query_text in gap_text:
                score += 0.1

        # Bonus for campaign keyword alignment
        campaign_matches = sum(1 for keyword in campaign_keywords if keyword.lower() in gap_text)
        score += min(0.2, campaign_matches * 0.1)  # Up to 0.2 bonus

        return min(1.0, score)

    def _calculate_seasonal_alignment_score(
        self,
        gap_text: str,
        interest_over_time: List[Dict[str, Any]]
    ) -> float:
        """
        Calculate how well a content gap aligns with seasonal trends.

        Returns score from 0.0 to 1.0
        """
        if not interest_over_time:
            return 0.0

        # Find peak interest periods
        values = [point.get("value", 0) for point in interest_over_time if isinstance(point, dict)]
        if not values:
            return 0.0

        avg_interest = sum(values) / len(values)
        max_interest = max(values)

        # Identify high-interest periods (above 75th percentile)
        threshold = sorted(values)[int(len(values) * 0.75)]
        high_interest_periods = [point for point in interest_over_time
                                if isinstance(point, dict) and point.get("value", 0) >= threshold]

        if not high_interest_periods:
            return 0.0

        # Look for seasonal keywords in gap text
        seasonal_keywords = [
            'seasonal', 'quarterly', 'monthly', 'annual', 'yearly', 'quarter',
            'january', 'february', 'march', 'april', 'may', 'june',
            'july', 'august', 'september', 'october', 'november', 'december',
            'holiday', 'holidays', 'summer', 'winter', 'spring', 'fall', 'autumn',
            'back to school', 'tax season', 'new year', 'christmas', 'thanksgiving',
            'easter', 'valentines', 'mothers day', 'fathers day', 'halloween'
        ]

        gap_lower = gap_text.lower()
        seasonal_matches = sum(1 for keyword in seasonal_keywords if keyword in gap_lower)

        # Score based on seasonal keywords and trend volatility
        volatility = (max_interest - min(values)) / avg_interest if avg_interest > 0 else 0
        seasonal_score = min(1.0, (seasonal_matches * 0.2) + (volatility * 0.3))

        return seasonal_score

    def _identify_seasonal_content_opportunities(
        self,
        content_analysis: Dict[str, Any],
        trend_data: Dict[str, Any],
        campaign_keywords: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Identify seasonal content opportunities based on trend patterns.

        Args:
            content_analysis: Content topic analysis
            trend_data: Google Trends data
            campaign_keywords: Campaign keywords

        Returns:
            List of seasonal content opportunities
        """
        seasonal_opportunities = []

        interest_over_time = trend_data.get("interest_over_time", [])
        if not interest_over_time:
            return seasonal_opportunities

        # Analyze seasonal patterns
        monthly_patterns = self._analyze_monthly_patterns(interest_over_time)

        # Generate seasonal content ideas
        for month, pattern in monthly_patterns.items():
            if pattern.get("is_peak", False):
                # Create seasonal content opportunity
                opportunity = {
                    'season': self._month_to_season(month),
                    'month': month,
                    'peak_score': pattern.get("relative_score", 0),
                    'content_ideas': self._generate_seasonal_content_ideas(
                        campaign_keywords, month, pattern
                    ),
                    'trend_context': pattern.get("trend_context", {}),
                    'opportunity_type': 'seasonal_peak'
                }
                seasonal_opportunities.append(opportunity)

            elif pattern.get("is_low", False):
                # Create off-season opportunity
                opportunity = {
                    'season': self._month_to_season(month),
                    'month': month,
                    'low_score': pattern.get("relative_score", 0),
                    'content_ideas': self._generate_offseason_content_ideas(
                        campaign_keywords, month, pattern
                    ),
                    'trend_context': pattern.get("trend_context", {}),
                    'opportunity_type': 'off_season'
                }
                seasonal_opportunities.append(opportunity)

        return seasonal_opportunities

    def _analyze_monthly_patterns(self, interest_over_time: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Analyze monthly interest patterns from trend data.

        Returns:
            Dictionary mapping months to pattern analysis
        """
        monthly_data = {}

        for point in interest_over_time:
            if isinstance(point, dict):
                date_str = point.get("date", "")
                value = point.get("value", 0)

                try:
                    # Extract month from date
                    if "T" in date_str:
                        date_str = date_str.split("T")[0]
                    date = datetime.fromisoformat(date_str)
                    month_key = f"{date.year}-{date.month:02d}"

                    if month_key not in monthly_data:
                        monthly_data[month_key] = {
                            "values": [],
                            "month": date.month,
                            "year": date.year
                        }

                    monthly_data[month_key]["values"].append(value)

                except (ValueError, KeyError):
                    continue

        # Calculate monthly statistics
        monthly_patterns = {}
        for month_key, data in monthly_data.items():
            values = data["values"]
            if values:
                avg_value = sum(values) / len(values)
                monthly_patterns[month_key] = {
                    "month": data["month"],
                    "average_interest": avg_value,
                    "data_points": len(values),
                    "trend_context": {
                        "period": month_key,
                        "avg_interest": round(avg_value, 2),
                        "data_points": len(values)
                    }
                }

        # Determine peaks and valleys
        if monthly_patterns:
            all_averages = [pattern["average_interest"] for pattern in monthly_patterns.values()]

            if all_averages:
                avg_of_averages = sum(all_averages) / len(all_averages)
                std_dev = (sum((x - avg_of_averages) ** 2 for x in all_averages) / len(all_averages)) ** 0.5

                # Define thresholds
                peak_threshold = avg_of_averages + (std_dev * 0.5)
                low_threshold = avg_of_averages - (std_dev * 0.5)

                for month_key, pattern in monthly_patterns.items():
                    avg_interest = pattern["average_interest"]
                    pattern["is_peak"] = avg_interest >= peak_threshold
                    pattern["is_low"] = avg_interest <= low_threshold
                    pattern["relative_score"] = (avg_interest - min(all_averages)) / (max(all_averages) - min(all_averages)) if max(all_averages) > min(all_averages) else 0.5

        return monthly_patterns

    def _month_to_season(self, month: int) -> str:
        """Convert month number to season name."""
        if month in [12, 1, 2]:
            return "winter"
        elif month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        else:  # 9, 10, 11
            return "fall"

    def _generate_seasonal_content_ideas(
        self,
        campaign_keywords: List[str],
        month: str,
        pattern: Dict[str, Any]
    ) -> List[str]:
        """Generate content ideas for seasonal peaks."""
        ideas = []
        base_keyword = campaign_keywords[0] if campaign_keywords else "content"

        month_names = {
            1: "January", 2: "February", 3: "March", 4: "April",
            5: "May", 6: "June", 7: "July", 8: "August",
            9: "September", 10: "October", 11: "November", 12: "December"
        }

        month_num = pattern.get("month", 1)
        month_name = month_names.get(month_num, "Monthly")

        seasonal_templates = [
            f"{month_name} {base_keyword} Trends and Insights",
            f"How {base_keyword} Evolves in {month_name}",
            f"{month_name} {base_keyword} Best Practices",
            f"Seasonal {base_keyword} Strategies for {month_name}",
            f"{base_keyword} in {month_name}: What to Expect"
        ]

        ideas.extend(seasonal_templates[:3])
        return ideas

    def _generate_offseason_content_ideas(
        self,
        campaign_keywords: List[str],
        month: str,
        pattern: Dict[str, Any]
    ) -> List[str]:
        """Generate content ideas for off-season periods."""
        ideas = []
        base_keyword = campaign_keywords[0] if campaign_keywords else "content"

        month_names = {
            1: "January", 2: "February", 3: "March", 4: "April",
            5: "May", 6: "June", 7: "July", 8: "August",
            9: "September", 10: "October", 11: "November", 12: "December"
        }

        month_num = pattern.get("month", 1)
        month_name = month_names.get(month_num, "Monthly")

        offseason_templates = [
            f"Year-Round {base_keyword} Strategies",
            f"Building {base_keyword} Momentum in Slow Months",
            f"Off-Season {base_keyword} Planning",
            f"Consistent {base_keyword} Growth Strategies",
            f"Building {base_keyword} During Quiet Periods"
        ]

        ideas.extend(offseason_templates[:3])
        return ideas

    def _analyze_trend_momentum_and_opportunities(
        self,
        trend_data: Dict[str, Any],
        campaign_keywords: List[str]
    ) -> Dict[str, Any]:
        """
        Analyze trend momentum and identify strategic opportunities.

        Args:
            trend_data: Google Trends analysis data
            campaign_keywords: Campaign target keywords

        Returns:
            Trend momentum analysis and opportunities
        """
        insights = {}

        # Analyze interest over time
        interest_over_time = trend_data.get("interest_over_time", [])
        if interest_over_time:
            # Calculate trend direction and momentum
            recent_values = [point.get("value", 0) for point in interest_over_time[-12:]]  # Last 12 points

            if len(recent_values) >= 2:
                # Calculate trend direction (simplified)
                first_half = recent_values[:len(recent_values)//2]
                second_half = recent_values[len(recent_values)//2:]

                first_avg = sum(first_half) / len(first_half) if first_half else 0
                second_avg = sum(second_half) / len(second_half) if second_half else 0

                trend_direction = "rising" if second_avg > first_avg * 1.1 else "falling" if second_avg < first_avg * 0.9 else "stable"

                insights["trend_direction"] = trend_direction
                insights["momentum_score"] = (second_avg - first_avg) / first_avg if first_avg > 0 else 0
                insights["volatility"] = self._calculate_trend_volatility(recent_values)

        # Analyze related topics and queries
        related_topics = trend_data.get("related_topics", {})
        rising_topics = related_topics.get("rising", [])
        top_topics = related_topics.get("top", [])

        insights["rising_topics_count"] = len(rising_topics)
        insights["top_topics_count"] = len(top_topics)
        insights["rising_topic_opportunities"] = len([t for t in rising_topics if isinstance(t, dict) and t.get("value", 0) > 50])

        # Geographic insights
        interest_by_region = trend_data.get("interest_by_region", [])
        if interest_by_region:
            top_regions = sorted(
                [r for r in interest_by_region if isinstance(r, dict)],
                key=lambda x: x.get("value", 0),
                reverse=True
            )[:5]

            insights["top_regions"] = [
                {"region": r.get("location", ""), "score": r.get("value", 0)}
                for r in top_regions
            ]

        return insights

    def _calculate_trend_volatility(self, values: List[float]) -> float:
        """Calculate trend volatility (coefficient of variation)."""
        if not values or len(values) < 2:
            return 0.0

        mean = sum(values) / len(values)
        if mean == 0:
            return 0.0

        variance = sum((x - mean) ** 2 for x in values) / len(values)
        std_dev = variance ** 0.5

        return std_dev / mean  # Coefficient of variation

    def _generate_trend_based_recommendations(
        self,
        prioritized_gaps: List[Dict[str, Any]],
        seasonal_opportunities: List[Dict[str, Any]],
        trend_insights: Dict[str, Any],
        campaign_keywords: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Generate trend-informed strategic recommendations.

        Args:
            prioritized_gaps: Trend-prioritized content gaps
            seasonal_opportunities: Seasonal content opportunities
            trend_insights: Trend momentum analysis
            campaign_keywords: Campaign keywords

        Returns:
            Enhanced strategic recommendations
        """
        recommendations = []

        # Top trend-prioritized gaps
        for gap in prioritized_gaps[:5]:
            recommendation = {
                'type': 'trend_prioritized_gap',
                'title': gap.get('suggested_content', ''),
                'rationale': f"High trend relevance ({gap.get('trend_relevance_score', 0):.2f}) and seasonal alignment ({gap.get('seasonal_alignment_score', 0):.2f})",
                'trend_boost': gap.get('trend_boost_factor', 0),
                'priority': 'high' if gap.get('priority_score', 0) > 0.8 else 'medium',
                'target_timing': self._recommend_publishing_timing(gap, trend_insights)
            }
            recommendations.append(recommendation)

        # Seasonal opportunities
        for seasonal in seasonal_opportunities[:3]:
            recommendation = {
                'type': 'seasonal_opportunity',
                'title': f"Seasonal Content for {seasonal.get('season', '').title()}",
                'rationale': f"Leverage {seasonal.get('season', '')} trend patterns with {len(seasonal.get('content_ideas', []))} content ideas",
                'season': seasonal.get('season', ''),
                'peak_score': seasonal.get('peak_score', 0),
                'content_ideas_count': len(seasonal.get('content_ideas', [])),
                'priority': 'medium',
                'target_timing': seasonal.get('month', '')
            }
            recommendations.append(recommendation)

        # Trend momentum insights
        trend_direction = trend_insights.get("trend_direction", "stable")
        momentum_score = trend_insights.get("momentum_score", 0)

        if abs(momentum_score) > 0.1:  # Significant momentum
            direction_text = "rising" if momentum_score > 0 else "declining"
            recommendation = {
                'type': 'trend_momentum_strategy',
                'title': f"Leverage {direction_text} trend momentum",
                'rationale': f"Campaign keywords show {direction_text} trend with {abs(momentum_score)*100:.1f}% momentum",
                'momentum_score': momentum_score,
                'trend_direction': trend_direction,
                'priority': 'high' if abs(momentum_score) > 0.2 else 'medium',
                'target_timing': 'immediate' if momentum_score > 0.2 else 'strategic'
            }
            recommendations.insert(0, recommendation)  # Add as first recommendation

        return recommendations

    def _recommend_publishing_timing(
        self,
        gap: Dict[str, Any],
        trend_insights: Dict[str, Any]
    ) -> str:
        """
        Recommend optimal publishing timing based on trend analysis.

        Args:
            gap: Content gap with trend scores
            trend_insights: Trend momentum analysis

        Returns:
            Recommended timing strategy
        """
        seasonal_score = gap.get('seasonal_alignment_score', 0)
        trend_relevance = gap.get('trend_relevance_score', 0)

        if seasonal_score > 0.7:
            return "seasonal_peak"
        elif trend_relevance > 0.8:
            return "immediate_high_trend"
        elif trend_relevance > 0.5:
            return "rising_trend"
        else:
            return "strategic_planning"