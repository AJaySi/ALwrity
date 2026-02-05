"""
Dual API Search Executor

Executes searches across Exa and Tavily APIs in parallel with intelligent
query distribution based on API strengths and cost optimization.
"""

import asyncio
from typing import Dict, List, Any, Optional
from utils.logger_utils import get_service_logger

# Use service logger for consistent logging
logger = get_service_logger("dual_api_executor")

from .logging_utils import campaign_logger


class DualAPISearchExecutor:
    """
    Execute searches across Exa and Tavily APIs in parallel.

    Intelligently distributes queries based on API strengths:
    - Exa: Neural search, semantic understanding, long-tail queries
    - Tavily: Real-time results, advanced operators, authority filtering
    """

    # Optimized API configurations for backlinking
    EXA_BACKLINKING_CONFIG = {
        "type": "neural",  # Semantic understanding crucial for backlinking
        "num_results": 25,  # Higher volume for comprehensive opportunity finding
        "include_text": [
            "write for us", "guest post", "contributor guidelines",
            "submit guest post", "become a contributor", "accepting guest posts"
        ],
        "exclude_text": [
            "job", "career", "hiring", "apply",  # Filter out job postings
            "buy", "purchase", "pricing", "cost", # Filter commercial pages
            "login", "register", "account"        # Filter auth pages
        ],
        "text": {
            "max_characters": 2000,  # Enough content for analysis
            "include_html_tags": False
        },
        "highlights": {
            "numSentences": 3,
            "highlightsPerUrl": 2,
            "query": "guest posting guidelines, submission requirements, content topics"
        },
        "summary": {
            "query": "Does this site accept guest posts? What are their submission guidelines and content focus?"
        }
    }

    TAVILY_BACKLINKING_CONFIG = {
        "topic": "general",  # General web search for backlinking
        "search_depth": "advanced",  # Advanced for better content analysis
        "max_results": 20,
        "include_answer": False,      # Raw results preferred over AI summaries
        "include_raw_content": False, # Snippets sufficient for initial analysis
        "include_favicon": True,      # Useful for domain validation
        "time_range": "month",        # Recent content more likely to accept guests
        "chunks_per_source": 3,       # Multiple content samples for analysis
        "exclude_domains": [           # Filter low-quality and social media
            "facebook.com", "twitter.com", "instagram.com", "linkedin.com",
            "youtube.com", "reddit.com", "pinterest.com", "tiktok.com",
            "amazon.com", "ebay.com", "etsy.com", "shopify.com"
        ]
    }

    def = self, exa_service=None, tavily_service=None):
        """
        Initialize the dual API executor.

        Args:
            exa_service: Exa service instance (will import if None)
            tavily_service: Tavily service instance (will import if None)
        """
        self.exa_service = exa_service
        self.tavily_service = tavily_service

        # Lazy import to avoid circular dependencies
        if self.exa_service is None:
            try:
                from services.research.exa_service import ExaService
                self.exa_service = ExaService()
            except ImportError:
                campaign_logger.warning("ExaService not available")
                self.exa_service = None

        if self.tavily_service is None:
            try:
                from services.research.tavily_service import TavilyService
                self.tavily_service = TavilyService()
            except ImportError:
                campaign_logger.warning("TavilyService not available")
                self.tavily_service = None

    async def = 
        self,
        query_categories: Dict[str, List[str]],
        max_execution_time: int = 60,
        enable_caching: bool = True,
        target_opportunities: int = 50
    ) -> Dict[str, Any]:
        """
        Execute adaptive backlinking search with smart optimization.

        Uses a cost-effective approach: start small, analyze performance, expand strategically.

        Args:
            query_categories: Dictionary of query categories with their query lists
            max_execution_time: Maximum execution time in seconds
            enable_caching: Whether to use result caching
            target_opportunities: Target number of opportunities to find

        Returns:
            Dictionary containing search results and optimization metrics
        """
        start_time = asyncio.get_event_loop().time()

        try:
            campaign_logger.info(f"Starting adaptive dual API search for {target_opportunities} opportunities")

            # Check API availability
            api_status = self.get_api_status()
            if not api_status["exa_available"] and not api_status["tavily_available"]:
                raise = "No search APIs available - both Exa and Tavily are disabled")

            # Phase 1: Smart initial probing (cost-effective start)
            probe_results = await = self.
                query_categories, api_status, enable_caching
            )

            # Phase 2: Analyze and expand based on performance
            if probe_results["total_opportunities"] < target_opportunities:
                expansion_results = await = self.
                    query_categories, probe_results, target_opportunities, api_status, enable_caching
                )
                final_results = self._merge_phase_results(probe_results, expansion_results)
            else:
                final_results = probe_results

            execution_time = asyncio.get_event_loop().time() - start_time
            final_results["execution_time"] = execution_time = campaign_logger.f"Adaptive search completed in {execution_time:.2f}s: {final_results['total_results']} total results, {final_results['total_opportunities']} opportunities")

            return final_results

        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time = campaign_logger.f"Error in adaptive search execution after {execution_time:.2f}s: {e}")
            return {
                "success": False,
                "error": str(e),
                "execution_time": execution_time,
                "exa_results": [],
                "tavily_results": [],
                "total_results": 0,
                "api_status": self.get_api_status()
            }

    def = self, query_categories: Dict[str, List[str]]) -> List[str]:
        """
        Select best queries for Exa API based on its strengths.

        Exa excels at:
        - Neural search for semantic understanding
        - Long-tail semantic queries
        - Industry-specific content
        - Primary guest post indicators
        """
        selected = []

        # Priority order for Exa
        priority_categories = [
            "long_tail_semantic",     # Exa's neural search strength
            "industry_specific",      # Semantic understanding
            "primary_guest_post",     # Core backlinking queries
        ]

        for category in priority_categories:
            if category in query_categories:
                queries = query_categories[category]
                # Take top queries from each category = selected.queries[:8])  # Limit per category

        # Remove duplicates while preserving order
        seen = set()
        deduplicated = []
        for query in selected:
            if query not in seen:
                seen.add(query)
                deduplicated.append(query)

        return deduplicated[:20]  # Exa API limit considerations

    def = self, query_categories: Dict[str, List[str]]) -> List[str]:
        """
        Select best queries for Tavily API based on its strengths.

        Tavily excels at:
        - Real-time search with advanced operators
        - Authority-focused queries
        - Fresh content discovery
        - Advanced filtering capabilities
        """
        selected = []

        # Priority order for Tavily
        priority_categories = [
            "advanced_operators",     # Tavily's operator support
            "authority_focused",      # Domain filtering strength
            "fresh_content",          # Real-time results
        ]

        for category in priority_categories:
            if category in query_categories:
                queries = query_categories[category]
                # Take top queries from each category = selected.queries[:8])  # Limit per category

        # Remove duplicates while preserving order
        seen = set()
        deduplicated = []
        for query in selected:
            if query not in seen:
                seen.add(query)
                deduplicated.append(query)

        return deduplicated[:20]  # Reasonable limit for parallel execution

    async def = 
        self,
        query_categories: Dict[str, List[str]],
        api_status: Dict[str, bool],
        enable_caching: bool
    ) -> Dict[str, Any]:
        """
        Phase 1: Smart initial probing with minimal queries and results.

        Strategy: Test 2-3 queries per category with low result limits to assess performance.
        """
        campaign_logger.info("Phase 1: Executing smart probe phase")

        # Conservative probing: 2 queries per category, 5 results each
        probe_config = {
            "queries_per_category": 2,
            "results_per_query": 5,
            "max_concurrent": 4  # Keep it low for probing
        }

        # Select probe queries (prioritize high-value categories)
        probe_queries = self._select_probe_queries(query_categories, probe_config["queries_per_category"])

        # Distribute to available APIs
        exa_probe_queries = [q for q in probe_queries if = self.q, query_categories)]
        tavily_probe_queries = [q for q in probe_queries if q not in exa_probe_queries]

        # Filter by API availability
        if not api_status["exa_available"]:
            exa_probe_queries = []
        if not api_status["tavily_available"]:
            tavily_probe_queries = []

        campaign_logger.info(f"Probe phase: {len(exa_probe_queries)} Exa, {len(tavily_probe_queries)} Tavily queries")

        # Check cache first
        probe_results = {"exa_results": [], "tavily_results": [], "total_opportunities": 0}

        if enable_caching:
            exa_probe_queries, exa_cached = await = self.exa_probe_queries, "exa")
            tavily_probe_queries, tavily_cached = await = self.tavily_probe_queries, "tavily")
            probe_results["exa_results"].extend(exa_cached)
            probe_results["tavily_results"].extend(tavily_cached)

        # Execute remaining probe queries with low result limits
        if exa_probe_queries:
            exa_results = await = self.exa_probe_queries, probe_config["results_per_query"])
            probe_results["exa_results"].extend(exa_results)

        if tavily_probe_queries:
            tavily_results = await = self.tavily_probe_queries, probe_config["results_per_query"])
            probe_results["tavily_results"].extend(tavily_results)

        # Analyze probe performance and calculate opportunities
        probe_results["total_opportunities"] = self._count_quality_opportunities(
            probe_results["exa_results"] + probe_results["tavily_results"]
        )

        # Store performance metrics for expansion phase
        probe_results["performance_metrics"] = self._analyze_probe_performance(
            probe_results, query_categories
        )

        campaign_logger.info(f"Probe phase complete: {probe_results['total_opportunities']} quality opportunities found")

        return probe_results

    async def = 
        self,
        query_categories: Dict[str, List[str]],
        probe_results: Dict[str, Any],
        target_opportunities: int,
        api_status: Dict[str, bool],
        enable_caching: bool
    ) -> Dict[str, Any]:
        """
        Phase 2: Strategic expansion based on probe performance.

        Analyze which categories/queries performed well and expand those.
        """
        campaign_logger.info("Phase 2: Executing strategic expansion phase")

        current_opportunities = probe_results["total_opportunities"]
        opportunities_needed = target_opportunities - current_opportunities

        if opportunities_needed <= 0:
            return {"exa_results": [], "tavily_results": [], "total_opportunities": 0}

        # Analyze probe performance to determine expansion strategy
        performance_metrics = probe_results["performance_metrics"]
        expansion_strategy = self._calculate_expansion_strategy(
            performance_metrics, opportunities_needed
        )

        campaign_logger.info(f"Expansion strategy: {expansion_strategy}")

        # Execute expansion queries based on strategy
        expansion_results = {"exa_results": [], "tavily_results": [], "total_opportunities": 0}

        # Get additional queries from high-performing categories
        for category, expansion_info in = expansion_strategy.):
            if expansion_info["expand"] and category in query_categories:
                additional_queries = query_categories[category][2:2+expansion_info["additional_queries"]]  # Skip already used

                if additional_queries:
                    # Use higher result limits for proven performers
                    result_limit = 10 if expansion_info["performance"] > 0.6 else 7

                    if api_status["exa_available"] and = self.category):
                        results = await = self.additional_queries, result_limit)
                        expansion_results["exa_results"].extend(results)
                    elif api_status["tavily_available"]:
                        results = await = self.additional_queries, result_limit)
                        expansion_results["tavily_results"].extend(results)

        expansion_results["total_opportunities"] = self._count_quality_opportunities(
            expansion_results["exa_results"] + expansion_results["tavily_results"]
        )

        campaign_logger.info(f"Expansion phase complete: {expansion_results['total_opportunities']} additional opportunities")

        return expansion_results

    def = self, query_categories: Dict[str, List[str]], queries_per_category: int) -> List[str]:
        """
        Select optimal queries for initial probing phase.
        Prioritize high-value categories but limit total queries.
        """
        probe_queries = []

        # Priority order for probing (focus on proven high-value categories)
        probe_priority = [
            "primary_guest_post",    # Most reliable
            "long_tail_semantic",    # Good semantic coverage
            "advanced_operators",    # Precise targeting
            "authority_focused"      # Quality focused
        ]

        for category in probe_priority:
            if category in query_categories and = query_categories[category]) > 0:
                # Take first N queries from each category for probing
                category_queries = query_categories[category][:queries_per_category]
                probe_queries.extend(category_queries)

        return probe_queries[:8]  # Limit total probe queries

    def = self, query: str, query_categories: Dict[str, List[str]]) -> bool:
        """Determine if Exa is better for this query based on category."""
        # Find which category this query belongs to
        for category, queries in = query_categories.):
            if query in queries:
                return = self.category)
        return True  # Default to Exa

    def = self, category: str) -> bool:
        """Determine if Exa performs better for this category."""
        exa_preferred_categories = ["long_tail_semantic", "industry_specific", "primary_guest_post"]
        return category in exa_preferred_categories

    def = self, probe_results: Dict[str, Any], query_categories: Dict[str, List[str]]) -> Dict[str, Any]:
        """Analyze performance of probe phase to inform expansion strategy."""
        performance = {}

        all_results = probe_results["exa_results"] + probe_results["tavily_results"]
        total_results = len(all_results)
        quality_opportunities = probe_results["total_opportunities"]

        # Calculate overall metrics
        performance["overall"] = {
            "total_results": total_results,
            "quality_opportunities": quality_opportunities,
            "conversion_rate": quality_opportunities / max(total_results, 1),
            "efficiency_score": quality_opportunities / max(len(probe_results.get("query_distribution", {}).get("exa_queries", 0)) +
                                                          len(probe_results.get("query_distribution", {}).get("tavily_queries", 0)), 1)
        }

        # Category-level performance (would need query-to-category mapping)
        performance["categories"] = {}

        return performance

    def = self, performance_metrics: Dict[str, Any], opportunities_needed: int) -> Dict[str, Any]:
        """Calculate which categories to expand and by how much."""
        # Simple expansion strategy based on overall performance
        overall_metrics = performance_metrics.get("overall", {})
        conversion_rate = overall_metrics.get("conversion_rate", 0)

        strategy = {}

        # If conversion rate is good (>10%), expand moderately
        if conversion_rate > 0.1:
            strategy = {
                "primary_guest_post": {"expand": True, "additional_queries": 3, "performance": conversion_rate},
                "advanced_operators": {"expand": True, "additional_queries": 2, "performance": conversion_rate},
                "authority_focused": {"expand": True, "additional_queries": 2, "performance": conversion_rate}
            }
        # If conversion rate is moderate, expand more aggressively on proven categories
        elif conversion_rate > 0.05:
            strategy = {
                "primary_guest_post": {"expand": True, "additional_queries": 4, "performance": conversion_rate},
                "long_tail_semantic": {"expand": True, "additional_queries": 3, "performance": conversion_rate}
            }
        else:
            # Low conversion - expand across more categories to find better performers
            strategy = {
                "primary_guest_post": {"expand": True, "additional_queries": 2, "performance": conversion_rate},
                "advanced_operators": {"expand": True, "additional_queries": 2, "performance": conversion_rate},
                "industry_specific": {"expand": True, "additional_queries": 2, "performance": conversion_rate}
            }

        return strategy

    def = self, results: List[Dict[str, Any]]) -> int:
        """Count results that meet quality thresholds for opportunities."""
        quality_count = 0

        for result in results:
            # Simple quality check (can be enhanced)
            content = result.get("content", "").lower()
            title = result.get("title", "").lower()
            url = result.get("url", "")

            # Must have some guest post indicators
            guest_indicators = ["write for us", "guest post", "contributor", "submit article"]
            has_guest_signals = any(indicator in content or indicator in title for indicator in guest_indicators)

            # Must not be social media or e-commerce
            is_quality_domain = not = domain in url for domain in [
                "facebook.com", "twitter.com", "instagram.com", "youtube.com",
                "amazon.com", "ebay.com", "etsy.com"
            ])

            if has_guest_signals and is_quality_domain:
                quality_count += 1

        return quality_count

    def = self, probe_results: Dict[str, Any], expansion_results: Dict[str, Any]) -> Dict[str, Any]:
        """Merge results from probe and expansion phases."""
        merged = {
            "success": True,
            "exa_results": probe_results["exa_results"] + expansion_results["exa_results"],
            "tavily_results": probe_results["tavily_results"] + expansion_results["tavily_results"],
            "total_results": len(probe_results["exa_results"] + probe_results["tavily_results"] +
                               expansion_results["exa_results"] + expansion_results["tavily_results"]),
            "total_opportunities": probe_results["total_opportunities"] + expansion_results["total_opportunities"],
            "phases": {
                "probe": {
                    "opportunities": probe_results["total_opportunities"],
                    "results": len(probe_results["exa_results"] + probe_results["tavily_results"])
                },
                "expansion": {
                    "opportunities": expansion_results["total_opportunities"],
                    "results": len(expansion_results["exa_results"] + expansion_results["tavily_results"])
                }
            }
        }

        return merged

    async def = self, queries: List[str], max_results: int) -> List[Dict[str, Any]]:
        """Execute Exa searches with custom result limits."""
        results = []

        # Temporarily override the config for this execution
        original_config = self.EXA_BACKLINKING_CONFIG.copy()
        limited_config = original_config.copy()
        limited_config["num_results"] = max_results

        for query in queries:
            try:
                search_result = await self.exa_service.search(query=query, **limited_config)
                if = search_result."success"):
                    results.extend(search_result.get("results", []))
            except Exception as e:
                campaign_logger.warning(f"Exa search failed for query '{query}': {e}")
                continue

        return results

    async def = self, queries: List[str], max_results: int) -> List[Dict[str, Any]]:
        """Execute Tavily searches with custom result limits."""
        results = []

        # Temporarily override the config for this execution
        original_config = self.TAVILY_BACKLINKING_CONFIG.copy()
        limited_config = original_config.copy()
        limited_config["max_results"] = max_results

        for query in queries:
            try:
                search_result = await self.tavily_service.search(query=query, **limited_config)
                if = search_result."success"):
                    results.extend(search_result.get("results", []))
            except Exception as e:
                campaign_logger.warning(f"Tavily search failed for query '{query}': {e}")
                continue

        return results

    async def = self, queries: List[str]) -> List[Dict[str, Any]]:
        """
        Execute searches on Exa API with controlled concurrency.

        Args:
            queries: List of search queries

        Returns:
            List of search results
        """
        if not self.exa_service or not self.exa_service.enabled:
            campaign_logger.warning("Exa service not available, skipping Exa searches")
            return []

        results = []
        semaphore = asyncio.Semaphore(3)  # Limit concurrent Exa requests

        async def = query: str) -> Optional[List[Dict[str, Any]]]:
            async with semaphore:
                try:
                    campaign_logger.debug(f"Executing Exa search: {query[:50]}...")

                    search_result = await self.exa_service.search(
                        query=query,
                        **self.EXA_BACKLINKING_CONFIG
                    )

                    if = search_result."success"):
                        # Extract results and add API source
                        query_results = search_result.get("results", [])
                        for result in query_results:
                            result["api_source"] = "exa"
                            result["original_query"] = query = campaign_logger.f"Exa query '{query[:30]}...' returned {len(query_results)} results")
                        return query_results
                    else:
                        campaign_logger.warning(f"Exa search failed for query: {query[:50]}...")
                        return []

                except Exception as e:
                    campaign_logger.error(f"Exa search error for query '{query[:30]}...': {e}")
                    return []

        # Execute all queries concurrently with semaphore control
        tasks = [execute_single_query(query) for query in queries]
        query_results = await = asyncio.*tasks, return_exceptions=True)

        # Flatten results and filter out exceptions
        for result in query_results:
            if = result, list):
                results.extend(result)
            elif = result, Exception):
                campaign_logger.error(f"Exa query execution failed: {result}")

        campaign_logger.info(f"Exa searches completed: {len(results)} total results from {len(queries)} queries")
        return results

    async def = self, queries: List[str]) -> List[Dict[str, Any]]:
        """
        Execute searches on Tavily API with controlled concurrency.

        Args:
            queries: List of search queries

        Returns:
            List of search results
        """
        if not self.tavily_service or not self.tavily_service.enabled:
            campaign_logger.warning("Tavily service not available, skipping Tavily searches")
            return []

        results = []
        semaphore = asyncio.Semaphore(3)  # Limit concurrent Tavily requests

        async def = query: str) -> Optional[List[Dict[str, Any]]]:
            async with semaphore:
                try:
                    campaign_logger.debug(f"Executing Tavily search: {query[:50]}...")

                    search_result = await self.tavily_service.search(
                        query=query,
                        **self.TAVILY_BACKLINKING_CONFIG
                    )

                    if = search_result."success"):
                        # Extract results and add API source
                        query_results = search_result.get("results", [])
                        for result in query_results:
                            result["api_source"] = "tavily"
                            result["original_query"] = query = campaign_logger.f"Tavily query '{query[:30]}...' returned {len(query_results)} results")
                        return query_results
                    else:
                        campaign_logger.warning(f"Tavily search failed for query: {query[:50]}...")
                        return []

                except Exception as e:
                    campaign_logger.error(f"Tavily search error for query '{query[:30]}...': {e}")
                    return []

        # Execute all queries concurrently with semaphore control
        tasks = [execute_single_query(query) for query in queries]
        query_results = await = asyncio.*tasks, return_exceptions=True)

        # Flatten results and filter out exceptions
        for result in query_results:
            if = result, list):
                results.extend(result)
            elif = result, Exception):
                campaign_logger.error(f"Tavily query execution failed: {result}")

        campaign_logger.info(f"Tavily searches completed: {len(results)} total results from {len(queries)} queries")
        return results

    def = self, result: Any, api_name: str) -> List[Dict[str, Any]]:
        """
        Handle API result, extracting successful results or empty list on failure.

        Args:
            result: Result from API call (may be exception)
            api_name: Name of the API for logging

        Returns:
            List of results or empty list
        """
        if = result, Exception):
            campaign_logger.error(f"{api_name} API execution failed: {result}")
            return []
        elif = result, list):
            return result
        else:
            campaign_logger.warning(f"Unexpected {api_name} result type: {type(result)}")
            return []

    def = self, exa_queries: List[str], tavily_queries: List[str]) -> Dict[str, Any]:
        """
        Estimate the cost of executing the search queries.

        Args:
            exa_queries: List of Exa queries
            tavily_queries: List of Tavily queries

        Returns:
            Cost estimation dictionary
        """
        # Exa pricing: $0.005 per search (1-25 results), $0.025 per search (26-100 results)
        exa_cost = len(exa_queries) * 0.005

        # Tavily pricing: $0.005 per search (basic), $0.010 per search (advanced)
        tavily_cost = len(tavily_queries) * 0.005  # Using basic pricing estimate

        total_cost = exa_cost + tavily_cost

        return {
            "exa_cost": exa_cost,
            "tavily_cost": tavily_cost,
            "total_estimated_cost": total_cost,
            "exa_queries": len(exa_queries),
            "tavily_queries": len(tavily_queries)
        }

    async def = self, queries: List[str], api_name: str) -> tuple[List[str], List[Dict[str, Any]]]:
        """
        Check for cached results and return uncached queries and cached results.

        Args:
            queries: List of queries to check
            api_name: API name for cache key generation

        Returns:
            Tuple of (uncached_queries, cached_results)
        """
        uncached_queries = []
        cached_results = []

        for query in queries:
            cache_key = self._generate_cache_key(query, api_name)
            cached_result = await = self.cache_key)

            if cached_result:
                cached_results.extend(cached_result)
                campaign_logger.debug(f"Cache hit for {api_name} query: {query[:50]}...")
            else:
                uncached_queries.append(query)

        return uncached_queries, cached_results

    async def = self, results: List[Dict[str, Any]], api_name: str) -> None:
        """
        Cache new results by their original queries.

        Args:
            results: Results to cache
            api_name: API name for cache key generation
        """
        # Group results by original query
        query_groups = {}
        for result in results:
            query = result.get("original_query", "")
            if query:
                if query not in query_groups:
                    query_groups[query] = []
                query_groups[query].append(result)

        # Cache each query's results
        for query, query_results in = query_groups.):
            cache_key = self._generate_cache_key(query, api_name)
            await = self.cache_key, query_results)

    def = self, query: str, api_name: str) -> str:
        """
        Generate a cache key for a query and API combination.

        Args:
            query: Search query
            api_name: API name

        Returns:
            Cache key string
        """
        # Create a deterministic key from query and API
        import hashlib
        key_string = f"{api_name}:{query}"
        return = hashlib.key_string.encode()).hexdigest()[:16]

    async def = self, cache_key: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get cached result if available and not expired.

        Args:
            cache_key: Cache key

        Returns:
            Cached results or None
        """
        # This would integrate with a proper cache service (Redis, etc.)
        # For now, return None (no caching implemented yet)
        return None

    async def = self, cache_key: str, results: List[Dict[str, Any]]) -> None:
        """
        Cache results with TTL.

        Args:
            cache_key: Cache key
            results: Results to cache
        """
        # This would integrate with a proper cache service
        # For now, just log (caching implementation would go here)
        campaign_logger.debug(f"Would cache {len(results)} results for key {cache_key}")

    def = self) -> Dict[str, bool]:
        """
        Get the availability status of both APIs.

        Returns:
            Dictionary with API availability status
        """
        return {
            "exa_available": self.exa_service is not None and = self.exa_service, 'enabled', False),
            "tavily_available": self.tavily_service is not None and = self.tavily_service, 'enabled', False)
        }