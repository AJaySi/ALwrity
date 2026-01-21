"""
Backlinking Cost Optimizer

Optimizes API costs while maintaining quality for backlinking research.
Implements intelligent query prioritization, caching, and budget management.
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from loguru import logger

from .logging_utils import campaign_logger


class BacklinkingCostOptimizer:
    """
    Cost optimization service for backlinking research operations.

    Features:
    - Dynamic query prioritization based on expected success rates
    - Intelligent budget allocation across campaigns
    - Result caching to avoid redundant API calls
    - Real-time cost tracking and limits
    """

    def __init__(self, monthly_budget_limit: float = 50.0):
        """
        Initialize the cost optimizer.

        Args:
            monthly_budget_limit: Maximum monthly budget for API costs
        """
        self.monthly_budget_limit = monthly_budget_limit

        # API pricing (per search)
        self.exa_cost_per_search = 0.005  # Base cost for 1-25 results
        self.tavily_cost_per_search = 0.005  # Base cost

        # Cache for results (in production, this would be Redis/memcached)
        self.result_cache = {}
        self.cache_ttl = timedelta(hours=24)  # Cache results for 24 hours

        # Query effectiveness scores (based on historical performance)
        self.query_effectiveness = {
            "primary_guest_post": 0.85,    # Highest success rate
            "long_tail_semantic": 0.75,    # Good semantic matching
            "advanced_operators": 0.70,    # Precise targeting
            "industry_specific": 0.65,     # Context-aware
            "authority_focused": 0.60,     # Quality-focused
            "fresh_content": 0.55         # Recency-focused
        }

        # Performance tracking for learning
        self.performance_history = {}  # Track actual performance vs predictions
        self.budget_tracking = {
            "monthly_spend": 0.0,
            "daily_spend": 0.0,
            "last_reset": datetime.utcnow().date(),
            "spend_by_category": {}
        }

        # Adaptive learning
        self.learning_enabled = True
        self.performance_samples = []  # Store recent performance data

        campaign_logger.info("BacklinkingCostOptimizer initialized with learning capabilities")

    async def optimize_query_execution(
        self,
        query_categories: Dict[str, List[str]],
        campaign_size: str = "medium",
        user_budget_limit: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Optimize which queries to execute based on cost and expected value.

        Args:
            query_categories: Dictionary of query categories with their queries
            campaign_size: Size of campaign (small, medium, large)
            user_budget_limit: User's specific budget limit

        Returns:
            Optimization results with query allocation and cost estimates
        """
        try:
            # Calculate campaign parameters
            campaign_params = self._get_campaign_parameters(campaign_size)
            budget_limit = user_budget_limit or campaign_params["budget_limit"]

            # Prioritize queries by expected effectiveness
            prioritized_queries = self._prioritize_queries(query_categories)

            # Allocate queries within budget
            allocation = self._allocate_budget_queries(
                prioritized_queries, budget_limit, campaign_params
            )

            # Calculate final costs and estimates
            cost_analysis = self._calculate_cost_analysis(allocation)

            optimization_result = {
                "exa_queries": allocation["exa_queries"],
                "tavily_queries": allocation["tavily_queries"],
                "estimated_cost": cost_analysis["total_cost"],
                "expected_opportunities": cost_analysis["expected_opportunities"],
                "cost_breakdown": cost_analysis,
                "budget_utilization": (cost_analysis["total_cost"] / budget_limit) * 100,
                "query_distribution": {
                    "exa_queries_count": len(allocation["exa_queries"]),
                    "tavily_queries_count": len(allocation["tavily_queries"])
                }
            }

            campaign_logger.info(f"Query optimization complete: {len(allocation['exa_queries'])} Exa, "
                              f"{len(allocation['tavily_queries'])} Tavily queries, "
                              f"${cost_analysis['total_cost']:.2f} estimated cost")

            return optimization_result

        except Exception as e:
            campaign_logger.error(f"Error in query optimization: {e}")
            # Return conservative fallback
            return {
                "exa_queries": query_categories.get("primary_guest_post", [])[:5],
                "tavily_queries": query_categories.get("advanced_operators", [])[:5],
                "estimated_cost": 0.05,
                "expected_opportunities": 3,
                "cost_breakdown": {"total_cost": 0.05},
                "budget_utilization": 10.0,
                "query_distribution": {"exa_queries_count": 5, "tavily_queries_count": 5}
            }

    def _get_campaign_parameters(self, campaign_size: str) -> Dict[str, Any]:
        """
        Get campaign parameters based on size.

        Args:
            campaign_size: Size category (small, medium, large)

        Returns:
            Campaign parameters
        """
        parameters = {
            "small": {
                "budget_limit": 15.0,
                "max_queries_per_category": 5,
                "priority_focus": ["primary_guest_post", "advanced_operators"]
            },
            "medium": {
                "budget_limit": 35.0,
                "max_queries_per_category": 8,
                "priority_focus": ["primary_guest_post", "long_tail_semantic", "industry_specific"]
            },
            "large": {
                "budget_limit": 75.0,
                "max_queries_per_category": 12,
                "priority_focus": ["primary_guest_post", "long_tail_semantic", "industry_specific", "advanced_operators"]
            }
        }

        return parameters.get(campaign_size, parameters["medium"])

    def _prioritize_queries(self, query_categories: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """
        Prioritize queries by expected effectiveness and distribute to APIs.

        Args:
            query_categories: Query categories with their queries

        Returns:
            Prioritized queries for each API
        """
        # Sort categories by effectiveness
        sorted_categories = sorted(
            query_categories.keys(),
            key=lambda cat: self.query_effectiveness.get(cat, 0.5),
            reverse=True
        )

        exa_queries = []
        tavily_queries = []

        for category in sorted_categories:
            if category not in query_categories:
                continue

            queries = query_categories[category]

            # Distribute based on API strengths
            if category in ["long_tail_semantic", "industry_specific", "primary_guest_post"]:
                # Exa excels at semantic understanding
                exa_queries.extend(queries)
            else:
                # Tavily excels at operators and authority filtering
                tavily_queries.extend(queries)

        return {
            "exa": exa_queries,
            "tavily": tavily_queries
        }

    def _allocate_budget_queries(
        self,
        prioritized_queries: Dict[str, List[str]],
        budget_limit: float,
        campaign_params: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """
        Allocate queries within budget constraints.

        Args:
            prioritized_queries: Prioritized queries by API
            budget_limit: Maximum budget
            campaign_params: Campaign parameters

        Returns:
            Final query allocation
        """
        max_queries_per_category = campaign_params["max_queries_per_category"]
        priority_focus = campaign_params["priority_focus"]

        # Start with high-priority queries
        allocated_exa = []
        allocated_tavily = []

        # First pass: Allocate priority categories
        for category in priority_focus:
            if category in ["long_tail_semantic", "industry_specific", "primary_guest_post"]:
                # Exa allocation
                category_queries = [q for q in prioritized_queries["exa"]
                                  if self._query_belongs_to_category(q, category)]
                allocated_exa.extend(category_queries[:max_queries_per_category])
            else:
                # Tavily allocation
                category_queries = [q for q in prioritized_queries["tavily"]
                                  if self._query_belongs_to_category(q, category)]
                allocated_tavily.extend(category_queries[:max_queries_per_category])

        # Second pass: Fill remaining budget with lower priority queries
        remaining_budget = budget_limit - self._calculate_allocation_cost(allocated_exa, allocated_tavily)

        if remaining_budget > 0:
            # Add more queries if budget allows
            for category in prioritized_queries["exa"]:
                if category not in allocated_exa:
                    allocated_exa.append(category)
                    if self._calculate_allocation_cost(allocated_exa, allocated_tavily) > budget_limit:
                        allocated_exa.pop()  # Remove if over budget
                        break

            for category in prioritized_queries["tavily"]:
                if category not in allocated_tavily:
                    allocated_tavily.append(category)
                    if self._calculate_allocation_cost(allocated_exa, allocated_tavily) > budget_limit:
                        allocated_tavily.pop()  # Remove if over budget
                        break

        return {
            "exa_queries": allocated_exa,
            "tavily_queries": allocated_tavily
        }

    def _query_belongs_to_category(self, query: str, category: str) -> bool:
        """
        Determine if a query belongs to a specific category.
        This is a simplified heuristic - in production, this would track query metadata.

        Args:
            query: Search query
            category: Category name

        Returns:
            True if query belongs to category
        """
        # Simplified category detection based on query patterns
        indicators = {
            "primary_guest_post": ['"write for us"', '"guest post"', '"submit guest post"'],
            "advanced_operators": ['intitle:', 'inurl:', 'site:'],
            "long_tail_semantic": ['"guest post opportunity"', '"contributor guidelines"'],
            "authority_focused": ['site:.edu', 'site:.gov', 'site:.org'],
            "fresh_content": ['"recently"', '"now accepting"']
        }

        category_indicators = indicators.get(category, [])
        return any(indicator in query for indicator in category_indicators)

    def _calculate_allocation_cost(self, exa_queries: List[str], tavily_queries: List[str]) -> float:
        """
        Calculate total cost for query allocation.

        Args:
            exa_queries: List of Exa queries
            tavily_queries: List of Tavily queries

        Returns:
            Total estimated cost
        """
        exa_cost = len(exa_queries) * self.exa_cost_per_search
        tavily_cost = len(tavily_queries) * self.tavily_cost_per_search

        return exa_cost + tavily_cost

    def _calculate_cost_analysis(self, allocation: Dict[str, List[str]]) -> Dict[str, Any]:
        """
        Calculate detailed cost analysis and opportunity estimates.

        Args:
            allocation: Query allocation

        Returns:
            Cost analysis dictionary
        """
        exa_count = len(allocation["exa_queries"])
        tavily_count = len(allocation["tavily_queries"])

        exa_cost = exa_count * self.exa_cost_per_search
        tavily_cost = tavily_count * self.tavily_cost_per_search
        total_cost = exa_cost + tavily_cost

        # Estimate opportunities (rough heuristic: 10% success rate per query)
        expected_opportunities = int((exa_count + tavily_count) * 0.1)
        expected_opportunities = max(1, min(expected_opportunities, 100))  # Reasonable bounds

        return {
            "exa_cost": exa_cost,
            "tavily_cost": tavily_cost,
            "total_cost": total_cost,
            "expected_opportunities": expected_opportunities,
            "cost_per_opportunity": total_cost / expected_opportunities if expected_opportunities > 0 else 0,
            "exa_queries": exa_count,
            "tavily_queries": tavily_count
        }

    # ===== CACHING METHODS =====

    async def get_cached_result(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Get cached result if still valid.

        Args:
            cache_key: Unique cache key

        Returns:
            Cached result or None if expired/not found
        """
        if cache_key not in self.result_cache:
            return None

        cached_item = self.result_cache[cache_key]
        cache_time = cached_item["timestamp"]

        # Check if cache is still valid
        if datetime.utcnow() - cache_time > self.cache_ttl:
            # Remove expired cache
            del self.result_cache[cache_key]
            return None

        campaign_logger.debug(f"Cache hit for key: {cache_key}")
        return cached_item["result"]

    async def cache_result(self, cache_key: str, result: Dict[str, Any]) -> None:
        """
        Cache a result with TTL.

        Args:
            cache_key: Unique cache key
            result: Result to cache
        """
        self.result_cache[cache_key] = {
            "result": result,
            "timestamp": datetime.utcnow()
        }

        # Clean up expired cache entries periodically
        await self._cleanup_expired_cache()

        campaign_logger.debug(f"Cached result for key: {cache_key}")

    async def _cleanup_expired_cache(self) -> None:
        """
        Remove expired cache entries.
        """
        current_time = datetime.utcnow()
        expired_keys = []

        for key, cached_item in self.result_cache.items():
            if current_time - cached_item["timestamp"] > self.cache_ttl:
                expired_keys.append(key)

        for key in expired_keys:
            del self.result_cache[key]

        if expired_keys:
            campaign_logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")

    def generate_cache_key(self, query: str, api_name: str, search_params: Dict[str, Any]) -> str:
        """
        Generate a unique cache key for a search query.

        Args:
            query: Search query
            api_name: API name (exa, tavily)
            search_params: Search parameters

        Returns:
            Unique cache key
        """
        # Create a deterministic key from query and important parameters
        key_components = [
            api_name,
            query,
            str(search_params.get("include_text", [])),
            str(search_params.get("exclude_text", [])),
            str(search_params.get("category", "")),
            str(search_params.get("time_range", ""))
        ]

        cache_key = "|".join(key_components)
        return f"backlinking_{hash(cache_key) % 1000000}"  # Keep key length reasonable

    # ===== BUDGET TRACKING METHODS =====

    def check_budget_limits(self, current_cost: float, user_budget_limit: Optional[float] = None) -> Dict[str, Any]:
        """
        Check if current cost is within budget limits.

        Args:
            current_cost: Current accumulated cost
            user_budget_limit: User's specific budget limit

        Returns:
            Budget status dictionary
        """
        budget_limit = user_budget_limit or self.monthly_budget_limit
        remaining_budget = budget_limit - current_cost
        utilization_percent = (current_cost / budget_limit) * 100

        status = {
            "within_budget": current_cost <= budget_limit,
            "current_cost": current_cost,
            "budget_limit": budget_limit,
            "remaining_budget": max(0, remaining_budget),
            "utilization_percent": utilization_percent,
            "warning_threshold": 80.0,  # Warn at 80% utilization
            "critical_threshold": 95.0  # Critical at 95% utilization
        }

        # Add status messages
        if utilization_percent >= status["critical_threshold"]:
            status["status"] = "critical"
            status["message"] = f"Critical: {utilization_percent:.1f}% of budget used"
        elif utilization_percent >= status["warning_threshold"]:
            status["status"] = "warning"
            status["message"] = f"Warning: {utilization_percent:.1f}% of budget used"
        else:
            status["status"] = "normal"
            status["message"] = f"Normal: {utilization_percent:.1f}% of budget used"

        return status

    def get_cost_recommendations(self, utilization_percent: float) -> List[str]:
        """
        Get cost optimization recommendations based on utilization.

        Args:
            utilization_percent: Current budget utilization percentage

        Returns:
            List of recommendations
        """
        recommendations = []

        if utilization_percent >= 90:
            recommendations.extend([
                "Reduce query volume by 50%",
                "Focus only on primary guest post queries",
                "Disable advanced operators",
                "Increase caching TTL to 48 hours"
            ])
        elif utilization_percent >= 75:
            recommendations.extend([
                "Reduce query volume by 25%",
                "Prioritize high-success-rate query categories",
                "Enable more aggressive caching"
            ])
        elif utilization_percent >= 50:
            recommendations.extend([
                "Monitor query effectiveness",
                "Consider upgrading to higher budget tier",
                "Optimize query categories based on performance"
            ])
        else:
            recommendations.append("Budget utilization is healthy")

        return recommendations

    # ===== UTILITY METHODS =====

    def get_api_cost_estimates(self) -> Dict[str, Any]:
        """
        Get current API cost estimates.

        Returns:
            Cost estimate information
        """
        return {
            "exa": {
                "cost_per_search": self.exa_cost_per_search,
                "description": "Neural search (1-25 results)"
            },
            "tavily": {
                "cost_per_search": self.tavily_cost_per_search,
                "description": "AI-powered search"
            },
            "monthly_budget_limit": self.monthly_budget_limit,
            "recommended_daily_limit": self.monthly_budget_limit / 30
        }

    def update_pricing(self, exa_cost: Optional[float] = None, tavily_cost: Optional[float] = None) -> None:
        """
        Update API pricing (for when pricing changes).

        Args:
            exa_cost: New Exa cost per search
            tavily_cost: New Tavily cost per search
        """
        if exa_cost is not None:
            self.exa_cost_per_search = exa_cost
            campaign_logger.info(f"Updated Exa cost to ${exa_cost} per search")

        if tavily_cost is not None:
            self.tavily_cost_per_search = tavily_cost
            campaign_logger.info(f"Updated Tavily cost to ${tavily_cost} per search")

    # ===== BUDGET TRACKING METHODS =====

    def record_api_usage(self, api_name: str, queries_executed: int, cost_incurred: float) -> None:
        """
        Record API usage for budget tracking.

        Args:
            api_name: API name (exa, tavily)
            queries_executed: Number of queries executed
            cost_incurred: Cost incurred
        """
        current_date = datetime.utcnow().date()

        # Reset monthly/daily counters if needed
        if current_date != self.budget_tracking["last_reset"]:
            self._reset_budget_tracking(current_date)

        # Update tracking
        self.budget_tracking["monthly_spend"] += cost_incurred
        self.budget_tracking["daily_spend"] += cost_incurred

        # Track by category
        if api_name not in self.budget_tracking["spend_by_category"]:
            self.budget_tracking["spend_by_category"][api_name] = 0.0
        self.budget_tracking["spend_by_category"][api_name] += cost_incurred

        campaign_logger.debug(f"Recorded ${cost_incurred:.3f} spend on {api_name} ({queries_executed} queries)")

    def _reset_budget_tracking(self, current_date: datetime.date) -> None:
        """
        Reset budget tracking counters for new period.

        Args:
            current_date: Current date
        """
        # Check if it's a new month
        if current_date.month != self.budget_tracking["last_reset"].month:
            campaign_logger.info(f"Resetting monthly budget tracking. Previous month spend: ${self.budget_tracking['monthly_spend']:.2f}")
            self.budget_tracking["monthly_spend"] = 0.0
            self.budget_tracking["spend_by_category"] = {}

        # Reset daily spend
        self.budget_tracking["daily_spend"] = 0.0
        self.budget_tracking["last_reset"] = current_date

    def get_budget_status(self) -> Dict[str, Any]:
        """
        Get current budget status.

        Returns:
            Budget status dictionary
        """
        monthly_used = self.budget_tracking["monthly_spend"]
        monthly_limit = self.monthly_budget_limit
        monthly_remaining = max(0, monthly_limit - monthly_used)

        return {
            "monthly_spend": monthly_used,
            "monthly_limit": monthly_limit,
            "monthly_remaining": monthly_remaining,
            "monthly_utilization_percent": (monthly_used / monthly_limit) * 100 if monthly_limit > 0 else 0,
            "daily_spend": self.budget_tracking["daily_spend"],
            "spend_by_category": self.budget_tracking["spend_by_category"],
            "last_reset": self.budget_tracking["last_reset"].isoformat()
        }

    # ===== PERFORMANCE LEARNING METHODS =====

    def record_performance(self, query_category: str, queries_executed: int, opportunities_found: int, cost: float) -> None:
        """
        Record query performance for learning.

        Args:
            query_category: Category of queries executed
            queries_executed: Number of queries
            opportunities_found: Number of opportunities found
            cost: Cost incurred
        """
        if not self.learning_enabled:
            return

        performance_data = {
            "query_category": query_category,
            "queries_executed": queries_executed,
            "opportunities_found": opportunities_found,
            "cost": cost,
            "cost_per_opportunity": cost / opportunities_found if opportunities_found > 0 else 0,
            "success_rate": opportunities_found / queries_executed if queries_executed > 0 else 0,
            "timestamp": datetime.utcnow()
        }

        self.performance_samples.append(performance_data)

        # Keep only recent samples (last 100)
        if len(self.performance_samples) > 100:
            self.performance_samples = self.performance_samples[-100:]

        # Update effectiveness scores based on recent performance
        self._update_effectiveness_scores()

        campaign_logger.debug(f"Recorded performance: {query_category} - {opportunities_found}/{queries_executed} opportunities at ${cost:.3f}")

    def _update_effectiveness_scores(self) -> None:
        """
        Update query effectiveness scores based on recent performance data.
        """
        if len(self.performance_samples) < 10:  # Need minimum samples
            return

        # Calculate recent performance by category
        category_performance = {}
        recent_samples = self.performance_samples[-20:]  # Last 20 samples

        for sample in recent_samples:
            category = sample["query_category"]
            if category not in category_performance:
                category_performance[category] = []
            category_performance[category].append(sample)

        # Update effectiveness scores
        for category, samples in category_performance.items():
            if len(samples) >= 3:  # Need at least 3 samples
                avg_success_rate = sum(s["success_rate"] for s in samples) / len(samples)
                # Blend with existing score (70% historical, 30% recent)
                new_score = (self.query_effectiveness.get(category, 0.5) * 0.7) + (avg_success_rate * 0.3)
                self.query_effectiveness[category] = min(1.0, max(0.1, new_score))

        campaign_logger.debug(f"Updated effectiveness scores: {self.query_effectiveness}")

    def get_performance_insights(self) -> Dict[str, Any]:
        """
        Get performance insights and recommendations.

        Returns:
            Performance insights dictionary
        """
        insights = {
            "effectiveness_scores": self.query_effectiveness,
            "total_samples": len(self.performance_samples),
            "budget_status": self.get_budget_status(),
            "recommendations": []
        }

        # Generate recommendations
        budget_status = insights["budget_status"]
        if budget_status["monthly_utilization_percent"] > 80:
            insights["recommendations"].append("High budget utilization - consider reducing query volume")

        # Find best performing categories
        if self.query_effectiveness:
            best_category = max(self.query_effectiveness.items(), key=lambda x: x[1])
            insights["recommendations"].append(f"Prioritize '{best_category[0]}' queries (highest effectiveness)")

        # Cost efficiency insights
        if self.performance_samples:
            avg_cost_per_opportunity = sum(
                s["cost_per_opportunity"] for s in self.performance_samples[-10:]
                if s["cost_per_opportunity"] > 0
            ) / len([s for s in self.performance_samples[-10:] if s["cost_per_opportunity"] > 0])

            if avg_cost_per_opportunity > 0.15:
                insights["recommendations"].append("Cost per opportunity is high - consider caching or query optimization")

        return insights

    def reset_performance_data(self) -> None:
        """
        Reset performance data (useful for testing or when patterns change).
        """
        self.performance_samples = []
        campaign_logger.info("Reset performance data and effectiveness scores")