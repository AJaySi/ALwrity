"""
Backlinking Cost Tracker

Simple, effective cost tracking and budget management for backlinking research.
Focuses on transparency and control rather than complex optimization.
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from loguru import logger

from .logging_utils import campaign_logger


class BacklinkingCostTracker:
    """
    Simple cost tracking and budget management for backlinking operations.

    Features:
    - Budget limit enforcement
    - Cost tracking and reporting
    - Basic caching for cost efficiency
    """

    def __init__(self, monthly_budget_limit: float = 50.0):
        """
        Initialize the cost tracker.

        Args:
            monthly_budget_limit: Maximum monthly budget for API costs
        """
        self.monthly_budget_limit = monthly_budget_limit

        # API pricing (per search)
        self.exa_cost_per_search = 0.005
        self.tavily_cost_per_search = 0.005

        # Simple cache for results (in production, this would be Redis/memcached)
        self.result_cache = {}
        self.cache_ttl = timedelta(hours=24)  # Cache results for 24 hours

        campaign_logger.info("BacklinkingCostTracker initialized")

    async def track_and_validate_budget(
        self,
        exa_queries_count: int,
        tavily_queries_count: int,
        user_budget_limit: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Track costs and validate against budget limits.

        Args:
            exa_queries_count: Number of Exa queries
            tavily_queries_count: Number of Tavily queries
            user_budget_limit: User's specific budget limit

        Returns:
            Budget validation and cost breakdown
        """
        try:
            # Calculate costs
            exa_cost = exa_queries_count * self.exa_cost_per_search
            tavily_cost = tavily_queries_count * self.tavily_cost_per_search
            total_cost = exa_cost + tavily_cost

            # Check against budget
            budget_limit = user_budget_limit or self.monthly_budget_limit
            within_budget = total_cost <= budget_limit

            result = {
                "total_cost": total_cost,
                "exa_cost": exa_cost,
                "tavily_cost": tavily_cost,
                "budget_limit": budget_limit,
                "within_budget": within_budget,
                "budget_utilization_percent": (total_cost / budget_limit) * 100 if budget_limit > 0 else 0,
                "queries": {
                    "exa": exa_queries_count,
                    "tavily": tavily_queries_count,
                    "total": exa_queries_count + tavily_queries_count
                }
            }

            if not within_budget:
                campaign_logger.warning(f"Budget exceeded: ${total_cost:.2f} > ${budget_limit:.2f}")
                result["warning"] = f"Estimated cost ${total_cost:.2f} exceeds budget limit of ${budget_limit:.2f}"

            return result

        except Exception as e:
            campaign_logger.error(f"Error in budget tracking: {e}")
            return {
                "total_cost": 0.0,
                "within_budget": False,
                "error": str(e)
            }

    async def get_cached_result(self, query: str, api_type: str) -> Optional[Dict[str, Any]]:
        """
        Check if query result is cached and still valid.

        Args:
            query: Search query
            api_type: API type (exa or tavily)

        Returns:
            Cached result if available and valid, None otherwise
        """
        cache_key = f"{api_type}:{query}"

        if cache_key in self.result_cache:
            cached_entry = self.result_cache[cache_key]
            if datetime.utcnow() - cached_entry['timestamp'] < self.cache_ttl:
                return cached_entry['result']

            # Remove expired entry
            del self.result_cache[cache_key]

        return None

    async def cache_result(self, query: str, api_type: str, result: Dict[str, Any]):
        """
        Cache a query result.

        Args:
            query: Search query
            api_type: API type (exa or tavily)
            result: Result to cache
        """
        cache_key = f"{api_type}:{query}"

        self.result_cache[cache_key] = {
            'result': result,
            'timestamp': datetime.utcnow()
        }

        # Simple cache size management (keep last 1000 entries)
        if len(self.result_cache) > 1000:
            # Remove oldest entries (simple FIFO)
            oldest_keys = sorted(
                self.result_cache.keys(),
                key=lambda k: self.result_cache[k]['timestamp']
            )[:100]

            for key in oldest_keys:
                del self.result_cache[key]

    async def estimate_execution_cost(
        self,
        exa_results: List[Dict[str, Any]],
        tavily_results: List[Dict[str, Any]]
    ) -> float:
        """
        Estimate the cost of API execution based on results.

        Args:
            exa_results: Results from Exa API
            tavily_results: Results from Tavily API

        Returns:
            Estimated cost in dollars
        """
        # For now, provide a simple estimate
        # In production, this would track actual API calls
        exa_cost = len(exa_results) * 0.005  # Rough estimate
        tavily_cost = len(tavily_results) * 0.005  # Rough estimate

        return exa_cost + tavily_cost