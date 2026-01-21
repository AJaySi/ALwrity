"""
Backlinking Query Generator

Intelligent query generation for backlinking opportunities.
Uses AI for semantic understanding and programmatic patterns for efficiency.
"""

import asyncio
from typing import Dict, List, Optional
from datetime import datetime
from loguru import logger

from .logging_utils import campaign_logger


class BacklinkingQueryGenerator:
    """
    Intelligent query generation for backlinking opportunities.

    Generates comprehensive query sets across multiple categories:
    - Primary guest post indicators
    - Advanced operator patterns
    - Industry-specific queries
    - Long-tail semantic queries
    - Authority-focused queries
    - Fresh content queries
    """

    def __init__(self):
        """Initialize the query generator with comprehensive predefined patterns."""
        # Core guest post indicators (most effective)
        self.primary_guest_post_indicators = [
            '"write for us"',
            '"guest post"',
            '"submit guest post"',
            '"contributor guidelines"',
            '"become a contributor"',
            '"become a guest writer"',
            '"guest blogger wanted"',
            '"accepting guest posts"',
            '"now accepting guest posts"',
            '"blogs that accept guest posts"',
            '"submit your content"',
            '"contribute to our site"',
            '"guest post guidelines"',
            '"suggest a post"',
            '"submit an article"',
            '"contributor"',
            '"guest column"',
            '"submit content"',
            '"write for us page"',
            '"guest posting"',
            '"guest author"',
            '"guest contributor"',
            '"submit guest article"',
            '"contributing writer"',
            '"freelance writer wanted"',
            '"blogger wanted"'
        ]

        # Alternative phrasings for variety
        self.secondary_indicators = [
            '"we accept guest posts"',
            '"guest posts welcome"',
            '"looking for guest bloggers"',
            '"guest post submissions"',
            '"write guest posts"',
            '"guest post opportunities"',
            '"become a guest blogger"',
            '"join our contributor team"',
            '"submit your guest post"',
            '"guest post submission"',
            '"contribute as guest"',
            '"guest post by"'
        ]

        self.advanced_operator_patterns = [
            'intitle:"write for us"',
            'intitle:"guest post"',
            'intitle:"become a contributor"',
            'intitle:"contributor guidelines"',
            'inurl:contribute',
            'inurl:guest-post',
            'inurl:write-for-us',
            'inurl:contributor',
            'inurl:submit-article',
            'inurl:guest-author'
        ]

        self.industry_patterns = {
            "technology": [
                '"write for us" {keyword} tech',
                '"guest post" {keyword} technology',
                '"developer blog" {keyword} guest post',
                '"tech writer" {keyword} wanted'
            ],
            "health": [
                '"write for us" {keyword} health',
                '"medical guest post" {keyword}',
                '"health blogger" {keyword} wanted',
                '"wellness contributor" {keyword}'
            ],
            "business": [
                '"write for us" {keyword} business',
                '"business guest post" {keyword}',
                '"entrepreneur contributor" {keyword}',
                '"business blogger" {keyword} wanted'
            ],
            "finance": [
                '"write for us" {keyword} finance',
                '"financial guest post" {keyword}',
                '"money blogger" {keyword} wanted',
                '"investment contributor" {keyword}'
            ],
            "marketing": [
                '"write for us" {keyword} marketing',
                '"marketing guest post" {keyword}',
                '"digital marketer" {keyword} wanted',
                '"SEO contributor" {keyword}'
            ]
        }

        self.long_tail_semantic_queries = [
            '"write for us" {keyword} "guest post opportunity"',
            '"submit guest post" {keyword} "contributor guidelines"',
            '"become a contributor" {keyword} "guest blogging"',
            '"guest post" {keyword} "write for us page"',
            '"contributor" {keyword} "submit your article"',
            '"guest blogger" {keyword} "blogging guidelines"',
            '"submit content" {keyword} "guest post submission"'
        ]

        # AI-powered query enhancement (strategic use)
        self.ai_enhancement_enabled = True
        self.llm_provider = None  # Lazy loaded when needed

        self.authority_focused_queries = [
            'site:.edu "write for us" {keyword}',
            'site:.gov "guest post" {keyword}',
            'site:.org "contributor" {keyword}',
            'site:.ac.uk "write for us" {keyword}',
            'site:.edu.au "guest post" {keyword}',
            '"authority site" "write for us" {keyword}'
        ]

        self.fresh_content_queries = [
            '"recently started accepting" "guest posts" {keyword}',
            '"now accepting" "guest contributors" {keyword}',
            '"new contributor" "guidelines" {keyword}',
            '"updated" "write for us" {keyword}',
            '"fresh content" "guest post" {keyword}',
            '"actively seeking" "contributors" {keyword}'
        ]

    async def generate_queries(
        self,
        keywords: List[str],
        industry: str = None,
        max_queries_per_category: int = 10,
        include_secondary_patterns: bool = True,
        use_ai_enhancement: bool = False,
        trend_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, List[str]]:
        """
        Generate comprehensive query set for backlinking discovery with enhanced validation.

        Args:
            keywords: User-provided keywords
            industry: Optional industry context
            max_queries_per_category: Maximum queries per category
            include_secondary_patterns: Whether to include secondary indicator patterns
            use_ai_enhancement: Whether to use AI for query enhancement
            trend_data: Optional Google Trends data for enhanced queries

        Returns:
            Dictionary of query categories with validated query lists
        """
        try:
            campaign_logger.info(f"Generating queries for keywords: {keywords}, industry: {industry}")

            # Extract and normalize base keywords
            base_keywords = self._extract_base_keywords(keywords)
            if not base_keywords:
                campaign_logger.warning("No valid keywords provided, using fallback")
                base_keywords = ["general"]

            # Generate queries for each category
            query_categories = {}

            # Primary guest post queries (highest priority)
            query_categories["primary_guest_post"] = self._generate_primary_queries(
                base_keywords, max_queries_per_category, include_secondary_patterns
            )

            # Advanced operator queries
            query_categories["advanced_operators"] = self._generate_operator_queries(
                base_keywords, max_queries_per_category
            )

            # Industry-specific queries
            query_categories["industry_specific"] = self._generate_industry_queries(
                base_keywords, industry, max_queries_per_category
            )

            # Long-tail semantic queries
            query_categories["long_tail_semantic"] = self._generate_semantic_queries(
                base_keywords, max_queries_per_category
            )

            # Authority-focused queries
            query_categories["authority_focused"] = self._generate_authority_queries(
                base_keywords, max_queries_per_category
            )

            # Fresh content queries
            query_categories["fresh_content"] = self._generate_fresh_queries(
                base_keywords, max_queries_per_category
            )

            # Trend-based queries (if trend data is available)
            if trend_data:
                campaign_logger.info("Generating trend-enhanced queries")
                query_categories["trending_queries"] = self._generate_trend_based_queries(
                    base_keywords, trend_data, max_queries_per_category
                )
                query_categories["seasonal_queries"] = self._generate_seasonal_queries(
                    base_keywords, trend_data, max_queries_per_category
                )

            # Validate and filter all queries
            query_categories = await self.validate_queries(query_categories)

            # Log query generation stats
            total_queries = sum(len(queries) for queries in query_categories.values())
            campaign_logger.info(f"Generated and validated {total_queries} queries across {len(query_categories)} categories")

            # Log category breakdown
            for category, queries in query_categories.items():
                campaign_logger.debug(f"Category '{category}': {len(queries)} queries")

            return query_categories

        except Exception as e:
            campaign_logger.error(f"Error generating queries: {e}")
            # Return minimal fallback queries
            fallback_keyword = keywords[0] if keywords else "general"
            return {
                "primary_guest_post": [f'"write for us" "{fallback_keyword}"'],
                "advanced_operators": [f'intitle:"write for us" "{fallback_keyword}"']
            }

    def _generate_primary_queries(self, keywords: List[str], max_queries: int, include_secondary: bool = True) -> List[str]:
        """Generate primary guest post queries with enhanced variety."""
        queries = []
        all_indicators = self.primary_guest_post_indicators.copy()

        if include_secondary:
            all_indicators.extend(self.secondary_indicators[:5])  # Add some secondary variety

        # Use top keywords and rotate through indicators for diversity
        for i, keyword in enumerate(keywords[:min(4, len(keywords))]):  # Up to 4 keywords
            # Rotate through indicators starting from different positions for variety
            start_idx = (i * 3) % len(all_indicators)  # Start at different positions
            indicators_to_use = all_indicators[start_idx:start_idx + 6]  # Use 6 indicators per keyword

            for indicator in indicators_to_use:
                # Generate multiple variations for each indicator
                queries.extend([
                    f'{indicator} {keyword}',
                    f'{indicator} "{keyword}"',  # Exact match
                    f'{keyword} {indicator}',    # Reverse order sometimes
                ])

        # Remove duplicates while preserving order
        seen = set()
        unique_queries = []
        for query in queries:
            if query not in seen and len(unique_queries) < max_queries * 2:  # Allow more for filtering
                seen.add(query)
                unique_queries.append(query)

        return unique_queries[:max_queries]

    def _generate_operator_queries(self, keywords: List[str], max_queries: int) -> List[str]:
        """Generate advanced operator-style queries."""
        queries = []

        for keyword in keywords[:2]:  # Limit to top 2 keywords for operators
            for operator in self.advanced_operator_patterns[:4]:  # Top 4 operators
                queries.append(f'{operator} {keyword}')
                queries.append(f'{operator} "{keyword}"')

        return queries[:max_queries]

    def _generate_industry_queries(self, keywords: List[str], industry: str, max_queries: int) -> List[str]:
        """Generate industry-specific queries."""
        queries = []

        if not industry or industry.lower() not in self.industry_patterns:
            # Use general industry patterns
            industry = "technology"  # Default fallback

        industry_templates = self.industry_patterns[industry.lower()]

        for keyword in keywords[:2]:
            for template in industry_templates[:3]:  # Top 3 industry patterns
                queries.append(template.format(keyword=keyword))

        return queries[:max_queries]

    def _generate_semantic_queries(self, keywords: List[str], max_queries: int) -> List[str]:
        """Generate semantic long-tail queries."""
        queries = []

        for keyword in keywords[:2]:
            for pattern in self.long_tail_semantic_queries[:4]:  # Top 4 semantic patterns
                queries.append(pattern.format(keyword=keyword))

        return queries[:max_queries]

    def _generate_authority_queries(self, keywords: List[str], max_queries: int) -> List[str]:
        """Generate queries targeting authoritative sites."""
        queries = []

        for keyword in keywords[:1]:  # Single keyword for authority queries
            for pattern in self.authority_focused_queries[:4]:  # Top 4 authority patterns
                queries.append(pattern.format(keyword=keyword))

        return queries[:max_queries]

    def _generate_fresh_queries(self, keywords: List[str], max_queries: int) -> List[str]:
        """Generate queries for recently updated content."""
        queries = []

        for keyword in keywords[:1]:
            for pattern in self.fresh_content_queries[:3]:  # Top 3 fresh patterns
                queries.append(pattern.format(keyword=keyword))

        return queries[:max_queries]

    def _extract_base_keywords(self, keywords: List[str]) -> List[str]:
        """
        Extract and normalize base keywords.

        Args:
            keywords: Raw keywords from user

        Returns:
            Normalized, deduplicated keywords sorted by length
        """
        if not keywords:
            return ["general"]  # Fallback

        # Remove duplicates, strip whitespace, convert to lowercase
        unique_keywords = list(set(keyword.strip().lower() for keyword in keywords if keyword.strip()))

        # Filter out very short or very long keywords
        filtered_keywords = [
            keyword for keyword in unique_keywords
            if 2 <= len(keyword) <= 50
        ]

        # Sort by length (shorter first for broader searches)
        return sorted(filtered_keywords, key=len)[:5]  # Top 5 keywords

    async def validate_queries(self, queries: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """
        Validate and filter queries for quality and effectiveness.

        Args:
            queries: Generated query categories

        Returns:
            Validated and filtered queries
        """
        validated_queries = {}

        for category, category_queries in queries.items():
            validated = []
            for query in category_queries:
                if self._is_valid_query(query):
                    validated.append(query)

            validated_queries[category] = validated

            campaign_logger.debug(f"Category '{category}': {len(validated)} valid queries out of {len(category_queries)}")

        return validated_queries

    def _is_valid_query(self, query: str) -> bool:
        """
        Validate if a query is well-formed and likely to be effective.

        Args:
            query: Query string to validate

        Returns:
            True if query is valid
        """
        if not query or len(query.strip()) < 5:
            return False

        # Check for basic structure
        query = query.strip()

        # Must contain at least one keyword (not just operators)
        has_keyword_content = any(len(word) > 3 for word in query.split() if not word.startswith('"') and not ':' in word)

        # Must not be too long
        if len(query) > 200:
            return False

        # Must not have unbalanced quotes
        quote_count = query.count('"')
        if quote_count % 2 != 0:
            return False

        return has_keyword_content

    def estimate_query_effectiveness(self, queries: Dict[str, List[str]]) -> Dict[str, float]:
        """
        Estimate the effectiveness score for each query category.

        Args:
            queries: Query categories with their queries

        Returns:
            Effectiveness scores by category (0-1 scale)
        """
        effectiveness_scores = {
            "primary_guest_post": 0.85,    # Highest success rate
            "long_tail_semantic": 0.75,    # Good semantic matching
            "advanced_operators": 0.70,    # Precise targeting
            "industry_specific": 0.65,     # Context-aware
            "authority_focused": 0.60,     # Quality-focused
            "fresh_content": 0.55         # Recency-focused
        }

        # Adjust based on query count and quality
        adjusted_scores = {}
        for category, category_queries in queries.items():
            base_score = effectiveness_scores.get(category, 0.5)
            query_count = len(category_queries)

            # Bonus for more queries (up to a point)
            count_bonus = min(query_count / 10, 0.1)  # Max 10% bonus

            adjusted_scores[category] = min(1.0, base_score + count_bonus)

        return adjusted_scores

    async def _apply_strategic_ai_enhancement(
        self,
        query_categories: Dict[str, List[str]],
        keywords: List[str],
        industry: str = None
    ) -> Dict[str, List[str]]:
        """
        Apply AI where it matters most: semantic query enhancement for long-tail discovery.

        Strategic AI usage: Only enhance semantic queries where AI provides clear value.
        """
        try:
            # Only enhance semantic queries - where AI semantic understanding matters most
            if "long_tail_semantic" in query_categories:
                enhanced_semantic = await self._enhance_semantic_queries_with_ai(
                    query_categories["long_tail_semantic"], keywords, industry
                )
                query_categories["long_tail_semantic"] = enhanced_semantic

            # Generate AI-powered industry-specific variations (low cost, high value)
            if industry and "industry_specific" in query_categories:
                ai_industry_queries = await self._generate_ai_industry_queries(
                    keywords, industry
                )
                if ai_industry_queries:
                    # Merge with existing, keeping only the best
                    combined = query_categories["industry_specific"] + ai_industry_queries
                    query_categories["industry_specific"] = combined[:12]  # Limit total

            return query_categories

        except Exception as e:
            campaign_logger.warning(f"AI enhancement failed, using programmatic queries: {e}")
            return query_categories  # Return original if AI fails

    async def _enhance_semantic_queries_with_ai(
        self,
        existing_queries: List[str],
        keywords: List[str],
        industry: str = None
    ) -> List[str]:
        """
        Use AI to generate semantically diverse long-tail queries.

        This is where AI matters: understanding semantic relationships between keywords.
        """
        try:
            # Lazy load LLM provider (only when needed)
            if self.llm_provider is None:
                try:
                    from services.llm_providers.gemini_grounded_provider import GeminiGroundedProvider
                    self.llm_provider = GeminiGroundedProvider()
                except ImportError:
                    campaign_logger.warning("LLM provider not available, skipping AI enhancement")
                    return existing_queries

            # Strategic AI prompt: focused on semantic understanding
            prompt = f"""
            Generate 8 diverse long-tail search queries for finding guest post opportunities about: {', '.join(keywords)}

            Industry context: {industry or 'general'}
            Focus: Semantic variations that search engines understand as related but different intents

            Requirements:
            - Include conversational search patterns
            - Add question-based queries
            - Include comparison and "vs" queries
            - Add seasonal/trending angles
            - Include "how to" and "guide" focused queries
            - Avoid exact duplicates of existing patterns

            Return only the search queries as a JSON array of strings.
            """

            ai_response = await self.llm_provider.generate_json(prompt)
            ai_queries = ai_response.get("queries", [])

            # Merge with existing, removing duplicates
            combined = existing_queries + ai_queries
            seen = set()
            deduplicated = []
            for query in combined:
                normalized = query.lower().strip('"')
                if normalized not in seen:
                    seen.add(normalized)
                    deduplicated.append(query)

            return deduplicated[:15]  # Limit to 15 total semantic queries

        except Exception as e:
            campaign_logger.warning(f"AI semantic enhancement failed: {e}")
            return existing_queries

    async def _generate_ai_industry_queries(
        self,
        keywords: List[str],
        industry: str
    ) -> List[str]:
        """
        Generate industry-specific queries using AI understanding of industry context.

        Low-cost, high-value AI usage for industry-specific search patterns.
        """
        try:
            if self.llm_provider is None:
                return []  # Skip if no LLM available

            prompt = f"""
            Generate 4 industry-specific search queries for guest posts in {industry} about: {', '.join(keywords)}

            Focus on industry-specific platforms, communities, and terminology that accept guest content.

            Return as JSON array of strings with industry-specific search operators and terms.
            """

            ai_response = await self.llm_provider.generate_json(prompt)
            return ai_response.get("queries", [])[:4]  # Limit to 4 high-quality queries

        except Exception as e:
            campaign_logger.warning(f"AI industry query generation failed: {e}")
            return []

    # Google Trends Integration Methods

    def _generate_trend_based_queries(
        self,
        base_keywords: List[str],
        trend_data: Dict[str, Any],
        max_queries: int
    ) -> List[str]:
        """
        Generate queries based on trending topics and queries from Google Trends.

        Args:
            base_keywords: Base keywords for the campaign
            trend_data: Google Trends analysis data
            max_queries: Maximum number of queries to generate

        Returns:
            List of trend-based search queries
        """
        trend_queries = []

        # Extract rising queries from Google Trends
        related_queries = trend_data.get("related_queries", {})
        rising_queries = related_queries.get("rising", [])

        for query_data in rising_queries[:max_queries//2]:  # Use half for rising queries
            if isinstance(query_data, dict) and "query" in query_data:
                query = query_data["query"]
                if query and len(query.split()) <= 6:  # Reasonable length
                    # Combine with guest post indicators
                    trend_queries.append(f'"{query}" "write for us"')
                    trend_queries.append(f'"{query}" "guest post"')

        # Extract rising topics and convert to queries
        related_topics = trend_data.get("related_topics", {})
        rising_topics = related_topics.get("rising", [])

        for topic_data in rising_topics[:max_queries//2]:  # Use remaining half for topics
            if isinstance(topic_data, dict) and "topic_title" in topic_data:
                topic = topic_data["topic_title"]
                if topic and len(topic.split()) <= 4:
                    # Create trend-focused guest post queries
                    trend_queries.append(f'"{topic}" "guest post"')
                    trend_queries.append(f'"{topic}" "write for us"')

        return trend_queries[:max_queries]

    def _generate_seasonal_queries(
        self,
        base_keywords: List[str],
        trend_data: Dict[str, Any],
        max_queries: int
    ) -> List[str]:
        """
        Generate seasonal queries based on trend patterns.

        Args:
            base_keywords: Base keywords for the campaign
            trend_data: Google Trends analysis data
            max_queries: Maximum number of queries to generate

        Returns:
            List of seasonal search queries
        """
        seasonal_queries = []

        # Analyze interest over time for seasonal patterns
        interest_over_time = trend_data.get("interest_over_time", [])

        if interest_over_time:
            # Find months with consistently high interest
            monthly_scores = {}
            for point in interest_over_time:
                if isinstance(point, dict) and "date" in point and "value" in point:
                    try:
                        date_str = point["date"].split('T')[0]  # Remove time component
                        date = datetime.fromisoformat(date_str)
                        month = date.month
                        value = point["value"]

                        if month not in monthly_scores:
                            monthly_scores[month] = []
                        monthly_scores[month].append(value)
                    except (ValueError, KeyError):
                        continue

            # Calculate average monthly scores
            month_averages = {}
            for month, scores in monthly_scores.items():
                if scores:
                    month_averages[month] = sum(scores) / len(scores)

            # Find high-interest months (above 70th percentile)
            if month_averages:
                scores = list(month_averages.values())
                scores.sort()
                threshold_index = int(len(scores) * 0.7)
                threshold = scores[threshold_index] if threshold_index < len(scores) else scores[-1]

                high_months = [month for month, avg in month_averages.items() if avg >= threshold]

                # Generate seasonal queries
                month_names = {
                    1: "January", 2: "February", 3: "March", 4: "April",
                    5: "May", 6: "June", 7: "July", 8: "August",
                    9: "September", 10: "October", 11: "November", 12: "December"
                }

                base_keyword = base_keywords[0] if base_keywords else "content"
                for month in high_months[:3]:  # Limit to top 3 months
                    month_name = month_names.get(month, "")
                    if month_name:
                        seasonal_queries.append(f'"{base_keyword}" "{month_name}" "write for us"')
                        seasonal_queries.append(f'"{base_keyword}" "{month_name}" "guest post"')

        return seasonal_queries[:max_queries]