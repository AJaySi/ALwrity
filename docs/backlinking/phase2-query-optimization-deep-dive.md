# Phase 2 Deep Dive: Intelligent Query Generation & API Optimization for Backlinking

## Critical Insight: Good Queries = Success

**The success of the entire backlinking feature depends on finding quality leads. If we find leads, the tool fails.** We must focus relentlessly on generating queries that actually discover real guest post opportunities.

## Research Findings: Effective Backlinking Search Patterns

### Top-Performing Query Patterns (From Analysis)

#### Primary Guest Post Indicators
```python
PRIMARY_GUEST_POST_QUERIES = [
    '"write for us" {keyword}',
    '"guest post" {keyword}',
    '"submit guest post" {keyword}',
    '"contributor guidelines" {keyword}',
    '"become a contributor" {keyword}',
    '"become a guest writer" {keyword}',
    '"guest blogger wanted" {keyword}',
    '"accepting guest posts" {keyword}',
    '"now accepting guest posts" {keyword}',
    '"blogs that accept guest posts" {keyword}',
    '"submit your content" {keyword}',
    '"contribute to our site" {keyword}',
    '"guest post guidelines" {keyword}',
    '"suggest a post" {keyword}',
    '"submit an article" {keyword}',
    '"contributor" {keyword}',
    '"guest column" {keyword}',
    '"submit content" {keyword}'
]
```

#### Advanced Google-Style Operators (Translated to API)
```python
ADVANCED_OPERATOR_QUERIES = [
    'intitle:"write for us" {keyword}',
    'intitle:"guest post" {keyword}',
    'intitle:"become a contributor" {keyword}',
    'intitle:"contributor guidelines" {keyword}',
    'inurl:contribute {keyword}',
    'inurl:guest-post {keyword}',
    'inurl:write-for-us {keyword}',
    'inurl:contributor {keyword}',
    '"blogs that accept" {keyword} guest posts',
    '"we accept guest" {keyword}',
    '"guest blogging guidelines" {keyword}',
    '"submit blog post" {keyword}',
    '"add guest post" {keyword}',
    '"now accepting" {keyword} guest posts'
]
```

#### Industry-Specific Variations
```python
INDUSTRY_SPECIFIC_PATTERNS = {
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
    ]
}
```

#### Long-Tail & Semantic Variations
```python
LONG_TAIL_QUERIES = [
    '"write for us" {keyword} "guest post opportunity"',
    '"submit guest post" {keyword} "contributor guidelines"',
    '"become a contributor" {keyword} "guest blogging"',
    '"guest post" {keyword} "write for us page"',
    '"contributor" {keyword} "submit your article"',
    '"guest blogger" {keyword} "blogging guidelines"',
    '"submit content" {keyword} "guest post submission"'
]
```

## Intelligent API Parameter Selection

### Exa API: Neural Search Optimization for Backlinking

#### Primary Search Configuration
```python
EXA_BACKLINKING_CONFIG = {
    "type": "neural",  # Semantic understanding crucial for backlinking
    "num_results": 25,  # Higher volume for backlinking discovery
    "category": None,  # General web search, not restricted to specific content types
    "include_text": [
        "write for us",
        "guest post",
        "contributor guidelines",
        "submit guest post",
        "become a contributor",
        "accepting guest posts"
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
```

#### Advanced Exa Strategies for Backlinking
```python
EXA_ADVANCED_BACKLINKING = {
    # Use deep search for comprehensive results
    "deep_search_config": {
        "type": "deep",
        "additional_queries": [
            '"write for us" {keyword} guidelines',
            '"guest post" {keyword} submission',
            '"contributor" {keyword} requirements'
        ]
    },

    # Category-specific searches for different content types
    "category_focused": {
        "blog_focused": {
            "include_domains": [],  # Will be populated with blog domains
            "include_text": ["blog", "article", "post"]
        },
        "news_focused": {
            "category": "news",
            "include_text": ["guest contributor", "opinion piece"]
        }
    },

    # Date filtering for fresh opportunities
    "fresh_opportunities": {
        "start_crawl_date": "2024-01-01T00:00:00.000Z",  # Recent pages
        "end_crawl_date": None  # Up to present
    }
}
```

### Tavily API: Real-Time Search Optimization for Backlinking

#### Primary Search Configuration
```python
TAVILY_BACKLINKING_CONFIG = {
    "topic": "general",  # General web search for backlinking
    "search_depth": "advanced",  # Advanced for better content analysis
    "max_results": 20,
    "include_answer": False,  # We want raw results, not AI summaries
    "include_raw_content": False,  # Focus on snippets for speed
    "include_images": False,  # Not needed for backlinking
    "include_favicon": True,  # Useful for domain validation
    "time_range": "month",  # Recent content more likely to accept guests
    "chunks_per_source": 3,  # Multiple content chunks for analysis
    "include_domains": [],  # Will be filtered based on quality criteria
    "exclude_domains": [
        "facebook.com", "twitter.com", "instagram.com", "linkedin.com",
        "youtube.com", "reddit.com", "pinterest.com", "tiktok.com",
        "amazon.com", "ebay.com", "etsy.com", "shopify.com"
    ]
}
```

#### Tavily Search Depth Strategy
```python
TAVILY_DEPTH_STRATEGY = {
    "initial_discovery": {
        "search_depth": "advanced",
        "max_results": 20,
        "time_range": "month",
        "chunks_per_source": 3
    },
    "deep_analysis": {
        "search_depth": "advanced",
        "max_results": 15,
        "time_range": "week",  # Very recent for active opportunities
        "chunks_per_source": 5,
        "include_raw_content": True  # Full content for detailed analysis
    },
    "fast_validation": {
        "search_depth": "fast",
        "max_results": 10,
        "time_range": "month",
        "chunks_per_source": 1  # Quick validation only
    }
}
```

## Smart Query Generation System

### AI-Powered Query Expansion
```python
class BacklinkingQueryGenerator:
    """
    Intelligent query generation for backlinking opportunities.
    Uses AI to expand user keywords into effective search queries.
    """

    def generate_queries(self, keywords: List[str], industry: str = None) -> Dict[str, List[str]]:
        """
        Generate comprehensive query set for backlinking discovery.

        Args:
            keywords: User-provided keywords
            industry: Optional industry context

        Returns:
            Dictionary of query categories with query lists
        """
        base_keywords = self._extract_base_keywords(keywords)

        return {
            "primary_guest_post": self._generate_primary_queries(base_keywords),
            "advanced_operators": self._generate_operator_queries(base_keywords),
            "industry_specific": self._generate_industry_queries(base_keywords, industry),
            "long_tail_semantic": self._generate_semantic_queries(base_keywords),
            "authority_focused": self._generate_authority_queries(base_keywords),
            "fresh_content": self._generate_fresh_queries(base_keywords)
        }

    def _generate_primary_queries(self, keywords: List[str]) -> List[str]:
        """Generate primary guest post queries."""
        queries = []
        guest_post_indicators = [
            '"write for us"',
            '"guest post"',
            '"submit guest post"',
            '"contributor guidelines"',
            '"become a contributor"',
            '"become a guest writer"',
            '"guest blogger wanted"',
            '"accepting guest posts"'
        ]

        for keyword in keywords[:3]:  # Limit to top 3 keywords
            for indicator in guest_post_indicators:
                queries.append(f'{indicator} {keyword}')
                queries.append(f'{indicator} "{keyword}"')  # Exact match

        return queries[:20]  # Limit total queries

    def _generate_operator_queries(self, keywords: List[str]) -> List[str]:
        """Generate advanced operator-style queries."""
        queries = []
        operators = [
            'intitle:"write for us"',
            'intitle:"guest post"',
            'intitle:"become a contributor"',
            'inurl:contribute',
            'inurl:guest-post',
            'inurl:write-for-us'
        ]

        for keyword in keywords[:2]:  # Limit to top 2 for operators
            for operator in operators:
                queries.append(f'{operator} {keyword}')
                queries.append(f'{operator} "{keyword}"')

        return queries[:15]

    def _generate_industry_queries(self, keywords: List[str], industry: str = None) -> List[str]:
        """Generate industry-specific queries."""
        queries = []
        industries = {
            "technology": ["tech", "software", "programming", "developer"],
            "health": ["health", "medical", "wellness", "fitness"],
            "business": ["business", "entrepreneur", "startup", "marketing"],
            "finance": ["finance", "investment", "money", "wealth"]
        }

        industry_terms = industries.get(industry, ["general"])

        for keyword in keywords[:2]:
            for industry_term in industry_terms[:2]:
                queries.extend([
                    f'"write for us" {keyword} {industry_term}',
                    f'"guest post" {keyword} {industry_term} blog',
                    f'{industry_term} "contributor wanted" {keyword}'
                ])

        return queries[:12]

    def _generate_semantic_queries(self, keywords: List[str]) -> List[str]:
        """Generate semantic long-tail queries."""
        queries = []
        semantic_patterns = [
            '"write for us" {keyword} "guest post opportunity"',
            '"submit guest post" {keyword} "contributor guidelines"',
            '"become a contributor" {keyword} "guest blogging"',
            '"guest post" {keyword} "write for us page"',
            '"contributor" {keyword} "submit your article"',
            '"guest blogger" {keyword} "blogging guidelines"'
        ]

        for keyword in keywords[:2]:
            for pattern in semantic_patterns:
                queries.append(pattern.format(keyword=keyword))

        return queries[:10]

    def _generate_authority_queries(self, keywords: List[str]) -> List[str]:
        """Generate queries targeting authoritative sites."""
        queries = []
        authority_indicators = [
            'site:.edu "write for us" {keyword}',
            'site:.gov "guest post" {keyword}',
            'site:.org "contributor" {keyword}',
            '"authority site" "write for us" {keyword}'
        ]

        for keyword in keywords[:1]:  # Single keyword for authority
            for indicator in authority_indicators:
                queries.append(indicator.format(keyword=keyword))

        return queries[:8]

    def _generate_fresh_queries(self, keywords: List[str]) -> List[str]:
        """Generate queries for recently updated content."""
        queries = []
        fresh_indicators = [
            '"recently started accepting" "guest posts" {keyword}',
            '"now accepting" "guest contributors" {keyword}',
            '"new contributor" "guidelines" {keyword}',
            '"updated" "write for us" {keyword}'
        ]

        for keyword in keywords[:1]:
            for indicator in fresh_indicators:
                queries.append(indicator.format(keyword=keyword))

        return queries[:6]

    def _extract_base_keywords(self, keywords: List[str]) -> List[str]:
        """Extract and normalize base keywords."""
        # Remove duplicates, sort by length (shorter first for broader searches)
        unique_keywords = list(set(keywords))
        return sorted(unique_keywords, key=len)[:5]  # Top 5 keywords
```

## Dual API Execution Strategy

### Parallel Search Execution
```python
class DualAPISearchExecutor:
    """
    Execute searches across Exa and Tavily APIs in parallel.
    Intelligently distribute queries based on API strengths.
    """

    async def execute_backlinking_search(
        self,
        query_categories: Dict[str, List[str]]
    ) -> Dict[str, Any]:
        """
        Execute comprehensive backlinking search across both APIs.
        """

        # Distribute queries based on API strengths
        exa_queries = self._select_queries_for_exa(query_categories)
        tavily_queries = self._select_queries_for_tavily(query_categories)

        # Execute in parallel
        exa_task = self._execute_exa_searches(exa_queries)
        tavily_task = self._execute_tavily_searches(tavily_queries)

        exa_results, tavily_results = await asyncio.gather(
            exa_task, tavily_task, return_exceptions=True
        )

        # Handle exceptions and merge results
        return self._merge_api_results(exa_results, tavily_results)

    def _select_queries_for_exa(self, query_categories: Dict[str, List[str]]) -> List[str]:
        """Select best queries for Exa API."""
        selected = []

        # Exa excels at semantic understanding
        selected.extend(query_categories.get("long_tail_semantic", [])[:5])
        selected.extend(query_categories.get("industry_specific", [])[:5])
        selected.extend(query_categories.get("primary_guest_post", [])[:10])

        return selected[:20]  # Exa API limit considerations

    def _select_queries_for_tavily(self, query_categories: Dict[str, List[str]]) -> List[str]:
        """Select best queries for Tavily API."""
        selected = []

        # Tavily excels at real-time results and speed
        selected.extend(query_categories.get("fresh_content", [])[:5])
        selected.extend(query_categories.get("advanced_operators", [])[:8])
        selected.extend(query_categories.get("authority_focused", [])[:7])

        return selected[:20]

    async def _execute_exa_searches(self, queries: List[str]) -> List[Dict[str, Any]]:
        """Execute searches on Exa API."""
        results = []

        for query in queries:
            try:
                search_result = await self.exa_service.search(
                    query=query,
                    **EXA_BACKLINKING_CONFIG
                )

                if search_result.get("success"):
                    results.extend(search_result.get("results", []))

            except Exception as e:
                logger.warning(f"Exa search failed for query '{query}': {e}")
                continue

        return results

    async def _execute_tavily_searches(self, queries: List[str]) -> List[Dict[str, Any]]:
        """Execute searches on Tavily API."""
        results = []

        for query in queries:
            try:
                search_result = await self.tavily_service.search(
                    query=query,
                    **TAVILY_BACKLINKING_CONFIG
                )

                if search_result.get("success"):
                    results.extend(search_result.get("results", []))

            except Exception as e:
                logger.warning(f"Tavily search failed for query '{query}': {e}")
                continue

        return results
```

## Intelligent Result Processing & Deduplication

### Smart Deduplication
```python
class BacklinkingResultProcessor:
    """
    Process and deduplicate results from multiple APIs.
    Apply quality scoring and filtering.
    """

    def process_results(self, exa_results: List[Dict], tavily_results: List[Dict]) -> List[Dict]:
        """
        Process and merge results from both APIs.
        """
        # Combine all results
        all_results = exa_results + tavily_results

        # Deduplicate by URL
        unique_results = self._deduplicate_by_url(all_results)

        # Score and filter
        scored_results = []
        for result in unique_results:
            score = self._calculate_opportunity_score(result)
            if score > 0.3:  # Minimum quality threshold
                result["opportunity_score"] = score
                result["api_source"] = self._determine_api_source(result, exa_results, tavily_results)
                scored_results.append(result)

        # Sort by score and return top results
        return sorted(scored_results, key=lambda x: x["opportunity_score"], reverse=True)

    def _deduplicate_by_url(self, results: List[Dict]) -> List[Dict]:
        """Remove duplicate results based on URL."""
        seen_urls = set()
        unique_results = []

        for result in results:
            url = result.get("url", "").lower().strip()
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)

        return unique_results

    def _calculate_opportunity_score(self, result: Dict) -> float:
        """Calculate comprehensive opportunity score."""
        score = 0.0
        content = result.get("content", "").lower()
        title = result.get("title", "").lower()

        # Primary guest post indicators (high weight)
        primary_indicators = [
            "write for us", "guest post", "contributor guidelines",
            "become a contributor", "submit guest post"
        ]

        for indicator in primary_indicators:
            if indicator in content or indicator in title:
                score += 0.4
                break

        # Secondary indicators (medium weight)
        secondary_indicators = [
            "accepting guest posts", "guest blogger wanted",
            "submit your content", "contributor wanted"
        ]

        for indicator in secondary_indicators:
            if indicator in content:
                score += 0.2
                break

        # Content quality indicators
        if len(content) > 500:
            score += 0.1
        if "guidelines" in content or "submission" in content:
            score += 0.15
        if any(word in content for word in ["blog", "article", "content", "writing"]):
            score += 0.1

        # Domain authority proxy (basic)
        url = result.get("url", "")
        if any(ext in url for ext in [".edu", ".gov", ".org"]):
            score += 0.1
        elif any(domain in url for domain in ["medium.com", "wordpress.com"]):
            score -= 0.1  # Lower quality platforms

        return min(1.0, score)

    def _determine_api_source(self, result: Dict, exa_results: List[Dict], tavily_results: List[Dict]) -> str:
        """Determine which API originally found this result."""
        url = result.get("url")

        # Check Exa results first (more comprehensive analysis)
        for exa_result in exa_results:
            if exa_result.get("url") == url:
                return "exa"

        # Check Tavily results
        for tavily_result in tavily_results:
            if tavily_result.get("url") == url:
                return "tavily"

        return "unknown"
```

## Cost Optimization & Rate Limiting

### Intelligent Cost Management
```python
class BacklinkingCostOptimizer:
    """
    Optimize API costs while maintaining quality.
    """

    def __init__(self):
        self.exa_cost_per_query = 0.005  # Base cost
        self.tavily_cost_per_query = 0.005
        self.monthly_budget_limit = 50.0

    def optimize_query_execution(self, query_categories: Dict[str, List[str]]) -> Dict[str, Any]:
        """
        Optimize which queries to execute based on budget and expected value.
        """
        total_queries = sum(len(queries) for queries in query_categories.values())

        # Calculate budget allocation
        if total_queries <= 20:
            # Small campaign - run all queries
            exa_budget = 15.0
            tavily_budget = 15.0
        elif total_queries <= 50:
            # Medium campaign - selective execution
            exa_budget = 25.0
            tavily_budget = 25.0
        else:
            # Large campaign - aggressive optimization
            exa_budget = 35.0
            tavily_budget = 35.0

        # Prioritize high-value queries
        prioritized_queries = self._prioritize_queries(query_categories)

        return {
            "exa_queries": prioritized_queries["exa"][:int(exa_budget / self.exa_cost_per_query)],
            "tavily_queries": prioritized_queries["tavily"][:int(tavily_budget / self.tavily_cost_per_query)],
            "estimated_cost": (len(prioritized_queries["exa"]) * self.exa_cost_per_query +
                             len(prioritized_queries["tavily"]) * self.tavily_cost_per_query),
            "expected_opportunities": self._estimate_opportunities(prioritized_queries)
        }

    def _prioritize_queries(self, query_categories: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """Prioritize queries based on expected success rate."""
        priority_order = [
            "primary_guest_post",     # Highest success rate
            "long_tail_semantic",     # Good semantic matching
            "advanced_operators",     # Precise targeting
            "industry_specific",      # Context-aware
            "authority_focused",      # Quality-focused
            "fresh_content"           # Recency-focused
        ]

        exa_queries = []
        tavily_queries = []

        for category in priority_order:
            if category in query_categories:
                queries = query_categories[category]

                # Distribute based on API strengths
                if category in ["long_tail_semantic", "industry_specific", "primary_guest_post"]:
                    exa_queries.extend(queries)  # Exa better for semantic
                else:
                    tavily_queries.extend(queries)  # Tavily better for operators

        return {
            "exa": exa_queries,
            "tavily": tavily_queries
        }

    def _estimate_opportunities(self, prioritized_queries: Dict[str, List[str]]) -> int:
        """Estimate number of opportunities we'll find."""
        exa_count = len(prioritized_queries["exa"])
        tavily_count = len(prioritized_queries["tavily"])

        # Rough estimation: 5-15% success rate per query
        estimated_opportunities = (exa_count + tavily_count) * 0.1

        return max(1, int(estimated_opportunities))
```

## Integration with Existing Backlinking Service

### Updated BacklinkingResearchService
```python
class BacklinkingResearchService:
    """
    Specialized research service for backlinking opportunities.
    Uses intelligent query generation and dual API execution.
    """

    def __init__(self):
        self.exa_service = ExaService()
        self.tavily_service = TavilyService()
        self.query_generator = BacklinkingQueryGenerator()
        self.search_executor = DualAPISearchExecutor()
        self.result_processor = BacklinkingResultProcessor()
        self.cost_optimizer = BacklinkingCostOptimizer()
        self.db_service = BacklinkingDatabaseService()

    async def discover_opportunities(
        self,
        campaign_id: str,
        user_keywords: List[str],
        industry: str = None,
        target_audience: str = None
    ) -> List[BacklinkOpportunity]:
        """
        Main entry point for opportunity discovery with intelligent query generation.
        """

        # Generate comprehensive query set
        query_categories = self.query_generator.generate_queries(
            user_keywords, industry
        )

        # Optimize execution based on cost and expected value
        execution_plan = self.cost_optimizer.optimize_query_execution(query_categories)

        logger.info(f"Executing {len(execution_plan['exa_queries'])} Exa queries "
                   f"and {len(execution_plan['tavily_queries'])} Tavily queries")
        logger.info(f"Estimated cost: ${execution_plan['estimated_cost']:.2f}")

        # Execute searches across both APIs
        search_results = await self.search_executor.execute_backlinking_search({
            "exa": execution_plan["exa_queries"],
            "tavily": execution_plan["tavily_queries"]
        })

        # Process and score results
        processed_results = self.result_processor.process_results(
            search_results.get("exa_results", []),
            search_results.get("tavily_results", [])
        )

        # Convert to opportunity objects and store
        opportunities = []
        for result in processed_results[:50]:  # Limit to top 50
            opportunity = await self._create_opportunity_from_result(
                campaign_id, result, user_keywords
            )
            if opportunity:
                opportunities.append(opportunity)

        logger.info(f"Discovered {len(opportunities)} quality opportunities")

        return opportunities

    async def _create_opportunity_from_result(
        self,
        campaign_id: str,
        result: Dict[str, Any],
        user_keywords: List[str]
    ) -> Optional[BacklinkOpportunity]:
        """
        Create a BacklinkOpportunity object from search result.
        """

        # Analyze content for guest posting signals
        analysis = await self._analyze_opportunity_content(
            result.get("url", ""),
            result.get("content", ""),
            user_keywords
        )

        if not analysis.get("is_guest_post_opportunity", False):
            return None

        # Create opportunity data
        opportunity_data = {
            "url": result.get("url"),
            "domain": self._extract_domain(result.get("url")),
            "title": result.get("title"),
            "ai_content_analysis": analysis,
            "ai_relevance_score": analysis.get("relevance_score", 0),
            "ai_authority_score": self._estimate_authority_score(result),
            "ai_content_quality_score": analysis.get("content_quality", 0),
            "primary_topics": analysis.get("detected_topics", []),
            "content_categories": analysis.get("content_categories", []),
            "submission_guidelines": analysis.get("submission_guidelines"),
            "word_count_min": analysis.get("word_count_min"),
            "word_count_max": analysis.get("word_count_max"),
            "ai_contact_recommendation": analysis.get("contact_strategy"),
            "ai_email_template_suggestion": analysis.get("suggested_template"),
            "domain_authority": self._calculate_domain_authority(result),
            "quality_score": result.get("opportunity_score", 0),
            "ai_spam_risk_score": analysis.get("spam_risk", 0)
        }

        # Store in database
        return await self.db_service.create_opportunity(campaign_id, opportunity_data)
```

## Success Metrics & Validation

### Quality Validation Criteria
```python
OPPORTUNITY_QUALITY_CRITERIA = {
    "minimum_relevance_score": 0.4,
    "minimum_authority_score": 0.3,
    "minimum_content_quality": 0.5,
    "maximum_spam_risk": 0.3,
    "required_signals": [
        "has_write_for_us_page",
        "has_submission_guidelines",
        "accepts_guest_contributors"
    ],
    "preferred_indicators": [
        "recent_content",
        "active_blog",
        "clear_author_guidelines",
        "editorial_calendar"
    ]
}
```

### Performance Benchmarks
```python
PERFORMANCE_TARGETS = {
    "queries_per_second": 2,  # API rate limits
    "opportunities_per_query": 0.1,  # 10% success rate
    "cost_per_quality_opportunity": 0.08,  # $0.08 per opportunity
    "processing_time_seconds": 30,  # Max 30 seconds
    "deduplication_rate": 0.85,  # 85% unique results
    "relevance_accuracy": 0.90  # 90% of results are relevant
}
```

This comprehensive system transforms the backlinking discovery from a basic keyword search into an intelligent, AI-powered opportunity identification engine that leverages the unique strengths of both Exa and Tavily APIs while maintaining cost efficiency and high-quality results.