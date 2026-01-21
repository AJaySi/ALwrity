"""
Backlinking Research Service

Main orchestrator for AI-powered backlinking opportunity discovery.
Integrates query generation, dual API execution, result processing, and database operations.
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from loguru import logger

from .query_generator import BacklinkingQueryGenerator
from .dual_api_executor import DualAPISearchExecutor
from .database_service import BacklinkingDatabaseService
from .cost_tracker import BacklinkingCostTracker
from .email_extraction import EmailExtractionService
from .logging_utils import campaign_logger

# Import Google Trends service for trend analysis
from ..research.trends.google_trends_service import GoogleTrendsService


class BacklinkingResearchService:
    """
    Specialized research service for backlinking opportunities.

    Orchestrates the complete research pipeline:
    1. Generate intelligent queries based on user keywords
    2. Execute parallel searches across Exa and Tavily APIs
    3. Process and deduplicate results
    4. Analyze opportunities with AI-powered scoring
    5. Store validated opportunities in database
    """

    def __init__(self, db_service=None):
        """
        Initialize the backlinking research service.

        Args:
            db_service: Database service instance (optional, will create if None)
        """
        self.query_generator = BacklinkingQueryGenerator()
        self.api_executor = DualAPISearchExecutor()
        self.cost_tracker = BacklinkingCostTracker()
        self.email_extractor = EmailExtractionService()
        self.db_service = db_service or BacklinkingDatabaseService()
        self.google_trends = GoogleTrendsService()  # Initialize Google Trends service

        campaign_logger.info("BacklinkingResearchService initialized")

    async def discover_opportunities(
        self,
        campaign_id: str,
        user_keywords: List[str],
        industry: str = None,
        target_audience: str = None,
        max_opportunities: int = 50,
        enable_partial_results: bool = True,
        ai_enhanced: bool = False,
        enable_trend_analysis: bool = False
    ) -> Dict[str, Any]:
        """
        Main entry point for opportunity discovery.

        Args:
            campaign_id: Campaign identifier
            user_keywords: User-provided keywords for backlinking
            industry: Industry context (optional)
            target_audience: Target audience (optional, for future use)
            max_opportunities: Maximum opportunities to return
            enable_partial_results: Whether to enable partial results (default: True)
            ai_enhanced: Whether to use AI-enhanced mode (default: False)
            enable_trend_analysis: Whether to include Google Trends analysis (default: False)

        Returns:
            Dictionary containing discovery results and metadata
        """
        try:
            campaign_logger.info(f"Starting opportunity discovery for campaign {campaign_id}")
            campaign_logger.info(f"Keywords: {user_keywords}, Industry: {industry}")

            start_time = datetime.utcnow()

            # Initialize prospecting context for tracking all phases
            prospecting_context = {
                "campaign_metadata": {
                    "user_keywords": user_keywords,
                    "industry": industry,
                    "target_audience": target_audience,
                    "ai_enhanced_mode": ai_enhanced,
                    "trend_analysis_enabled": enable_trend_analysis,
                    "timestamp": start_time.isoformat(),
                    "max_opportunities": max_opportunities
                },
                "phase_1": {}, "phase_1_5": {}, "phase_2": {}, "phase_3": {}, "phase_4": {}
            }

            # Phase 1: Generate comprehensive query set with strategic AI enhancement
            campaign_logger.info("Phase 1: Generating search queries")
            use_ai_enhancement = len(user_keywords) >= 2  # Use AI when we have meaningful keywords
            query_categories = await self.query_generator.generate_queries(
                keywords=user_keywords,
                industry=industry,
                use_ai_enhancement=use_ai_enhancement,
                trend_data=trend_data if enable_trend_analysis else None
            )

            total_queries = sum(len(queries) for queries in query_categories.values())
            campaign_logger.info(f"Generated {total_queries} queries across {len(query_categories)} categories")

            # Update context with Phase 1 results
            prospecting_context["phase_1"].update({
                "query_categories": {cat: len(queries) for cat, queries in query_categories.items()},
                "total_queries": total_queries,
                "ai_enhanced_used": use_ai_enhancement,
                "status": "completed"
            })

            # Phase 1.5: Google Trends Analysis (if enabled)
            trend_data = None
            if enable_trend_analysis:
                campaign_logger.info("Phase 1.5: Analyzing Google Trends for enhanced prospecting")
                try:
                    trend_data = await self.google_trends.analyze_trends(
                        keywords=user_keywords[:5],  # Use first 5 keywords for trends
                        timeframe='today 12-m',
                        geo='US'
                    )

                    # Extract trending queries and seasonal insights
                    trending_queries = self._extract_trending_queries(trend_data)
                    seasonal_queries = self._extract_seasonal_queries(trend_data)

                    # Enhance query categories with trend data
                    if trending_queries:
                        query_categories["trending_queries"] = trending_queries[:5]  # Limit to 5
                        campaign_logger.info(f"Added {len(trending_queries)} trending queries")

                    if seasonal_queries:
                        query_categories["seasonal_queries"] = seasonal_queries[:3]  # Limit to 3
                        campaign_logger.info(f"Added {len(seasonal_queries)} seasonal queries")

                    # Update total queries count
                    total_queries = sum(len(queries) for queries in query_categories.values())

                    prospecting_context["phase_1_5"].update({
                        "trend_analysis": {
                            "keywords_analyzed": user_keywords[:5],
                            "timeframe": 'today 12-m',
                            "geo": 'US',
                            "trending_queries_added": len(trending_queries),
                            "seasonal_queries_added": len(seasonal_queries),
                            "total_queries_after_trends": total_queries
                        },
                        "trend_insights": {
                            "interest_over_time_points": len(trend_data.get("interest_over_time", [])),
                            "regions_analyzed": len(trend_data.get("interest_by_region", [])),
                            "related_topics_count": len(trend_data.get("related_topics", {}).get("top", [])),
                            "related_queries_count": len(trend_data.get("related_queries", {}).get("top", []))
                        },
                        "seasonal_recommendations": self._generate_seasonal_recommendations(trend_data),
                        "geographic_targets": self._identify_high_opportunity_regions(trend_data),
                        "status": "completed"
                    })

                    campaign_logger.info("Trend analysis completed successfully")

                except Exception as e:
                    campaign_logger.warning(f"Trend analysis failed: {e}")
                    prospecting_context["phase_1_5"]["error"] = str(e)
                    prospecting_context["phase_1_5"]["status"] = "failed"

            # Phase 2: Smart dual API execution with adaptive optimization
            campaign_logger.info("Phase 1.5: Executing smart adaptive search")
            search_results = await self.api_executor.execute_backlinking_search(
                query_categories=query_categories,
                target_opportunities=max_opportunities
            )

            # Update context with Phase 2 results
            prospecting_context["phase_2"]["api_calls"] = search_results.get("query_distribution", {})
            prospecting_context["phase_2"]["search_results"] = {
                "total_results": search_results.get("total_results", 0),
                "execution_time": search_results.get("execution_time", 0),
                "phases": search_results.get("phases", {})
            }

            if not search_results.get("success"):
                campaign_logger.error("Search execution failed")
                return {
                    "success": False,
                    "error": "Search execution failed",
                    "opportunities": [],
                    "stats": {}
                }

            # Phase 3: Process and deduplicate results
            campaign_logger.info("Phase 3: Processing and deduplicating results")
            processed_results = await self._process_search_results(search_results)

            # Update context with Phase 3 results
            prospecting_context["phase_3"]["processed_results"] = len(processed_results)
            prospecting_context["phase_3"]["deduplication_stats"] = {
                "raw_results": search_results.get("total_results", 0),
                "unique_results": len(processed_results)
            }

            # Phase 4: Analyze opportunities and create database objects
            campaign_logger.info("Phase 4: Analyzing opportunities and storing in database")
            opportunities = await self._analyze_and_store_opportunities(
                campaign_id=campaign_id,
                search_results=processed_results,
                user_keywords=user_keywords,
                max_opportunities=max_opportunities,
                prospecting_context=prospecting_context,
                trend_data=trend_data if enable_trend_analysis else None
            )

            # Calculate execution statistics
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()

            stats = {
                "execution_time_seconds": execution_time,
                "total_queries": total_queries,
                "queries_by_category": {cat: len(queries) for cat, queries in query_categories.items()},
                "raw_results": search_results.get("total_results", 0),
                "processed_results": len(processed_results),
                "final_opportunities": len(opportunities),
                "api_distribution": search_results.get("query_distribution", {}),
                "cost_estimate": await self.cost_tracker.estimate_execution_cost(
                    search_results.get("exa_results", []),
                    search_results.get("tavily_results", [])
                )
            }

            campaign_logger.info(f"Discovery completed in {execution_time:.2f}s")
            campaign_logger.info(f"Found {len(opportunities)} quality opportunities")

            return {
                "success": True,
                "opportunities": opportunities,
                "stats": stats,
                "campaign_id": campaign_id,
                "timestamp": end_time.isoformat()
            }

        except Exception as e:
            campaign_logger.error(f"Error in opportunity discovery: {e}")
            return {
                "success": False,
                "error": str(e),
                "opportunities": [],
                "stats": {},
                "prospecting_context": prospecting_context
            }

    async def _process_search_results(self, search_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Process and deduplicate search results from both APIs.

        Args:
            search_results: Raw search results from dual API execution

        Returns:
            Processed and deduplicated results
        """
        try:
            # Combine results from both APIs
            exa_results = search_results.get("exa_results", [])
            tavily_results = search_results.get("tavily_results", [])

            all_results = exa_results + tavily_results

            campaign_logger.debug(f"Processing {len(all_results)} raw results ({len(exa_results)} Exa, {len(tavily_results)} Tavily)")

            # Deduplicate by URL
            unique_results = self._deduplicate_by_url(all_results)

            campaign_logger.debug(f"After deduplication: {len(unique_results)} unique results")

            # Apply basic quality filtering
            quality_results = self._apply_quality_filter(unique_results)

            campaign_logger.debug(f"After quality filtering: {len(quality_results)} quality results")

            # Sort by potential relevance (basic scoring)
            sorted_results = self._sort_by_potential(quality_results)

            return sorted_results

        except Exception as e:
            campaign_logger.error(f"Error processing search results: {e}")
            return []

    def _deduplicate_by_url(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate results based on URL.

        Args:
            results: List of search results

        Returns:
            Deduplicated results
        """
        seen_urls = set()
        unique_results = []

        for result in results:
            url = result.get("url", "").lower().strip()
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)

        return unique_results

    def _apply_quality_filter(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Apply basic quality filtering to remove low-quality results.

        Args:
            results: Search results to filter

        Returns:
            Quality-filtered results
        """
        quality_results = []

        for result in results:
            # Skip if no URL
            if not result.get("url"):
                continue

            # Skip social media and e-commerce sites
            url = result.get("url", "").lower()
            skip_domains = [
                "facebook.com", "twitter.com", "instagram.com", "linkedin.com",
                "youtube.com", "reddit.com", "pinterest.com", "tiktok.com",
                "amazon.com", "ebay.com", "etsy.com", "shopify.com",
                "wikipedia.org"  # Too broad for backlinking
            ]

            if any(domain in url for domain in skip_domains):
                continue

            # Skip if content is too short
            content = result.get("content", "")
            title = result.get("title", "")

            if len(content) < 50 and len(title) < 10:
                continue

            quality_results.append(result)

        return quality_results

    def _sort_by_potential(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Sort results by backlinking potential.

        Args:
            results: Results to sort

        Returns:
            Sorted results (highest potential first)
        """
        def calculate_potential_score(result: Dict[str, Any]) -> float:
            """Calculate a basic potential score for sorting."""
            score = 0.0

            content = result.get("content", "").lower()
            title = result.get("title", "").lower()
            url = result.get("url", "").lower()

            # Guest post indicators in content/title
            guest_indicators = [
                "write for us", "guest post", "contributor", "submit article",
                "become a contributor", "accepting guests"
            ]

            for indicator in guest_indicators:
                if indicator in content or indicator in title:
                    score += 1.0
                    break

            # Authority domain bonus
            if any(ext in url for ext in [".edu", ".gov", ".org"]):
                score += 0.5

            # Content length bonus
            if len(content) > 200:
                score += 0.3

            return score

        # Sort by potential score (descending)
        return sorted(results, key=calculate_potential_score, reverse=True)

    async def _analyze_and_store_opportunities(
        self,
        campaign_id: str,
        search_results: List[Dict[str, Any]],
        user_keywords: List[str],
        max_opportunities: int,
        prospecting_context: Optional[Dict[str, Any]] = None,
        trend_data: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Analyze search results and store valid opportunities in database.

        Args:
            campaign_id: Campaign identifier
            search_results: Processed search results
            user_keywords: Original user keywords
            max_opportunities: Maximum opportunities to create
            prospecting_context: Context data from prospecting phases
            trend_data: Optional Google Trends data for enhanced analysis

        Returns:
            List of created opportunity objects
        """
        opportunities = []
        processed_count = 0

        for result in search_results[:max_opportunities * 2]:  # Process more than needed for quality filtering
            try:
                # Analyze the result for backlinking potential
                analysis = await self._analyze_opportunity_potential(
                    result=result,
                    user_keywords=user_keywords,
                    prospecting_context=prospecting_context,
                    trend_data=trend_data
                )

                # Only create opportunity if it passes quality thresholds
                if self._is_quality_opportunity(analysis):
                    # Extract email addresses for contact information
                    email_extraction = await self.email_extractor.extract_emails_from_opportunity(
                        url=result.get("url", ""),
                        content=result.get("content", ""),
                        title=result.get("title", "")
                    )

                    # Create opportunity data for database
                    opportunity_data = self._create_opportunity_data(
                        campaign_id=campaign_id,
                        result=result,
                        analysis=analysis,
                        email_extraction=email_extraction
                    )

                    # Store in database
                    opportunity = await self.db_service.create_opportunity(
                        campaign_id, opportunity_data
                    )

                    opportunities.append(opportunity)
                    processed_count += 1

                    campaign_logger.debug(f"Created opportunity {processed_count}: {opportunity.url}")

                    # Stop if we have enough opportunities
                    if len(opportunities) >= max_opportunities:
                        break

            except Exception as e:
                campaign_logger.warning(f"Error processing result {result.get('url', 'unknown')}: {e}")
                continue

        campaign_logger.info(f"Created {len(opportunities)} opportunities out of {processed_count} analyzed results")
        return opportunities

    async def _analyze_opportunity_potential(
        self,
        result: Dict[str, Any],
        user_keywords: List[str],
        prospecting_context: Optional[Dict[str, Any]] = None,
        trend_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze a search result for backlinking potential.

        Args:
            result: Search result to analyze
            user_keywords: User keywords for relevance scoring
            prospecting_context: Context data from prospecting phases
            trend_data: Optional Google Trends data for enhanced analysis

        Returns:
            Analysis dictionary with opportunity metrics
        """
        content = result.get("content", "").lower()
        title = result.get("title", "").lower()
        url = result.get("url", "")

        analysis = {
            "is_guest_post_opportunity": False,
            "relevance_score": 0.0,
            "content_quality": 0.0,
            "authority_score": 0.0,
            "spam_risk": 0.0,
            "detected_topics": [],
            "content_categories": [],
            "submission_guidelines": "",
            "contact_strategy": "email_outreach",
            "suggested_template": "professional_initial",
            "confidence_level": "low"
        }

        # Check for guest post signals (with optional AI enhancement)
        guest_signals = await self._detect_guest_post_signals(content, title, user_keywords)
        analysis.update(guest_signals)

        # Calculate relevance score
        analysis["relevance_score"] = self._calculate_relevance_score(
            content, title, user_keywords
        )

        # Assess content quality
        analysis["content_quality"] = self._assess_content_quality(content, title)

        # Estimate authority
        analysis["authority_score"] = self._estimate_authority_score(url)

        # Assess spam risk
        analysis["spam_risk"] = self._assess_spam_risk(url, content)

        # Determine if this is a quality opportunity
        analysis["is_guest_post_opportunity"] = self._evaluate_opportunity_quality(analysis)

        # Set confidence level
        analysis["confidence_level"] = self._determine_confidence_level(analysis)

        # Add trend-enhanced scoring if trend data is available
        if trend_data:
            trend_scoring = self._apply_trend_enhanced_scoring(
                analysis, result, trend_data, user_keywords, prospecting_context
            )
            analysis.update(trend_scoring)

        return analysis

    async def _detect_guest_post_signals(self, content: str, title: str, user_keywords: List[str] = None) -> Dict[str, Any]:
        """
        Detect signals that indicate guest posting acceptance.

        Args:
            content: Page content
            title: Page title

        Returns:
            Dictionary with guest post signal analysis
        """
        signals = {
            "has_write_for_us_page": False,
            "has_submission_guidelines": False,
            "has_guest_post_mentions": False,
            "has_contributor_sections": False,
            "has_contact_forms": False
        }

        combined_text = f"{title} {content}".lower()

        # Check for explicit "write for us" mentions
        if "write for us" in combined_text:
            signals["has_write_for_us_page"] = True

        # Check for submission guidelines
        guideline_keywords = ["submission guidelines", "how to submit", "guest post guidelines"]
        if any(keyword in combined_text for keyword in guideline_keywords):
            signals["has_submission_guidelines"] = True

        # Check for guest post mentions
        guest_keywords = ["guest post", "guest article", "guest contributor", "guest blogger"]
        if any(keyword in combined_text for keyword in guest_keywords):
            signals["has_guest_post_mentions"] = True

        # Check for contributor sections
        contributor_keywords = ["contributors", "our writers", "author guidelines"]
        if any(keyword in combined_text for keyword in contributor_keywords):
            signals["has_contributor_sections"] = True

        # Check for contact forms (basic detection)
        if "contact" in combined_text and ("form" in combined_text or "email" in combined_text):
            signals["has_contact_forms"] = True

        # Strategic AI enhancement: Use AI for complex content analysis when programmatic detection is uncertain
        if user_keywords and self._should_use_ai_for_content_analysis(signals, content):
            ai_signals = await self._ai_enhance_guest_post_detection(content, title, user_keywords)
            signals.update(ai_signals)

        return signals

    def _should_use_ai_for_content_analysis(self, current_signals: Dict[str, Any], content: str) -> bool:
        """
        Determine if AI enhancement would provide value for content analysis.

        Use AI strategically: when basic signals are weak but content is substantial enough for analysis.
        """
        # Count strong signals
        strong_signals = sum([
            current_signals.get("has_write_for_us_page", False),
            current_signals.get("has_submission_guidelines", False),
            current_signals.get("has_guest_post_mentions", False)
        ])

        # Use AI if: few strong signals BUT substantial content (where AI can find subtle patterns)
        content_length = len(content.strip())
        has_substantial_content = content_length > 1000  # Substantial content for AI analysis
        has_weak_signals = strong_signals <= 1  # Not too many clear signals already

        return has_substantial_content and has_weak_signals

    async def _ai_enhance_guest_post_detection(
        self,
        content: str,
        title: str,
        user_keywords: List[str]
    ) -> Dict[str, Any]:
        """
        Use AI strategically for complex content analysis where programmatic methods struggle.

        Focus: Subtle guest post signals that require semantic understanding.
        """
        try:
            # Lazy load LLM provider
            if not hasattr(self, '_llm_provider'):
                try:
                    from services.llm_providers.gemini_grounded_provider import GeminiGroundedProvider
                    self._llm_provider = GeminiGroundedProvider()
                except ImportError:
                    return {}  # Skip AI if not available

            # Strategic AI prompt: focused analysis of content for guest posting potential
            prompt = f"""
            Analyze this webpage content for guest post opportunities related to: {', '.join(user_keywords)}

            Title: {title}
            Content (first 2000 chars): {content[:2000]}

            Determine if this site accepts guest posts by looking for:
            1. Subtle mentions of guest contributions
            2. Contributor or writer opportunities
            3. Content partnership possibilities
            4. Editorial submission processes

            Return JSON with:
            - accepts_guest_posts: true/false/high_confidence
            - confidence_reason: brief explanation
            - detected_signals: array of specific signals found
            """

            ai_analysis = await self._llm_provider.generate_json(prompt)

            # Convert AI analysis to signal format
            ai_signals = {
                "ai_detected_guest_posts": ai_analysis.get("accepts_guest_posts", False),
                "ai_confidence_reason": ai_analysis.get("confidence_reason", ""),
                "ai_detected_signals": ai_analysis.get("detected_signals", [])
            }

            return ai_signals

        except Exception as e:
            campaign_logger.warning(f"AI content analysis failed: {e}")
            return {}

    def _calculate_relevance_score(self, content: str, title: str, user_keywords: List[str]) -> float:
        """
        Calculate relevance score based on keyword matching.

        Args:
            content: Page content
            title: Page title
            user_keywords: User's keywords

        Returns:
            Relevance score (0-1)
        """
        if not user_keywords:
            return 0.0

        combined_text = f"{title} {content}".lower()
        total_keywords = len(user_keywords)
        matched_keywords = 0

        for keyword in user_keywords:
            if keyword.lower() in combined_text:
                matched_keywords += 1

        # Bonus for keywords in title
        title_matches = sum(1 for keyword in user_keywords if keyword.lower() in title.lower())
        title_bonus = title_matches * 0.1

        base_score = matched_keywords / total_keywords
        final_score = min(1.0, base_score + title_bonus)

        return final_score

    def _assess_content_quality(self, content: str, title: str) -> float:
        """
        Assess the content quality of the page.

        Args:
            content: Page content
            title: Page title

        Returns:
            Quality score (0-1)
        """
        score = 0.0

        # Content length
        if len(content) > 500:
            score += 0.3
        elif len(content) > 200:
            score += 0.2
        elif len(content) > 50:
            score += 0.1

        # Title quality
        if len(title) > 10:
            score += 0.2

        # Structure indicators
        if "h1" in content.lower() or "h2" in content.lower():
            score += 0.1

        # Professional language
        professional_indicators = ["article", "content", "blog", "news", "industry"]
        professional_count = sum(1 for indicator in professional_indicators if indicator in content.lower())
        score += min(0.3, professional_count * 0.1)

        return min(1.0, score)

    def _estimate_authority_score(self, url: str) -> float:
        """
        Estimate domain authority based on URL patterns.

        Args:
            url: Page URL

        Returns:
            Authority score (0-1)
        """
        if not url:
            return 0.0

        url_lower = url.lower()
        score = 0.5  # Base score

        # High authority TLDs
        high_authority_tlds = [".edu", ".gov", ".org", ".mil"]
        if any(tld in url_lower for tld in high_authority_tlds):
            score += 0.3

        # Medium authority indicators
        medium_indicators = [".ac.uk", ".edu.au", ".gov.au"]
        if any(indicator in url_lower for indicator in medium_indicators):
            score += 0.2

        # Low quality indicators
        low_quality_domains = ["wordpress.com", "blogspot.com", "medium.com"]
        if any(domain in url_lower for domain in low_quality_domains):
            score -= 0.2

        return max(0.0, min(1.0, score))

    def _assess_spam_risk(self, url: str, content: str) -> float:
        """
        Assess spam risk of the page.

        Args:
            url: Page URL
            content: Page content

        Returns:
            Spam risk score (0-1, higher = more risky)
        """
        risk_score = 0.0

        # URL-based risk factors
        url_lower = url.lower()

        # Free hosting services (higher spam risk)
        free_hosts = ["000webhost", "freehost", "wordpress.com", "blogspot.com"]
        if any(host in url_lower for host in free_hosts):
            risk_score += 0.3

        # Excessive hyphens or numbers (potential spam indicators)
        if url.count('-') > 3 or any(char.isdigit() for char in url.split('/')[-1]):
            risk_score += 0.2

        # Content-based risk factors
        content_lower = content.lower()

        # Excessive promotional language
        promotional_words = ["buy now", "click here", "limited time", "best price"]
        promo_count = sum(1 for word in promotional_words if word in content_lower)
        risk_score += min(0.3, promo_count * 0.1)

        # Lack of substantial content
        if len(content.strip()) < 100:
            risk_score += 0.2

        return min(1.0, risk_score)

    # ===== UTILITY METHODS =====

    def _validate_discovery_inputs(self, campaign_id: str, user_keywords: List[str], max_opportunities: int) -> Dict[str, Any]:
        """
        Validate inputs for opportunity discovery.

        Args:
            campaign_id: Campaign identifier
            user_keywords: User keywords
            max_opportunities: Max opportunities

        Returns:
            Validation result dictionary
        """
        if not campaign_id or not isinstance(campaign_id, str):
            return {"valid": False, "error": "Invalid campaign_id"}

        if not user_keywords or not isinstance(user_keywords, list) or len(user_keywords) == 0:
            return {"valid": False, "error": "At least one keyword is required"}

        if len(user_keywords) > 10:
            return {"valid": False, "error": "Maximum 10 keywords allowed"}

        if not all(isinstance(kw, str) and kw.strip() for kw in user_keywords):
            return {"valid": False, "error": "All keywords must be non-empty strings"}

        if max_opportunities < 1 or max_opportunities > 200:
            return {"valid": False, "error": "max_opportunities must be between 1 and 200"}

        return {"valid": True}

    def _determine_campaign_size(self, max_opportunities: int) -> str:
        """
        Determine campaign size based on requested opportunities.

        Args:
            max_opportunities: Maximum opportunities requested

        Returns:
            Campaign size string
        """
        if max_opportunities <= 25:
            return "small"
        elif max_opportunities <= 75:
            return "medium"
        else:
            return "large"

    def _is_quality_opportunity(self, analysis: Dict[str, Any]) -> bool:
        """
        Determine if an analysis result represents a quality opportunity.

        Args:
            analysis: Opportunity analysis

        Returns:
            True if quality opportunity
        """
        # Must have minimum relevance
        if analysis.get("relevance_score", 0) < 0.3:
            return False

        # Must have minimum quality
        if analysis.get("content_quality", 0) < 0.4:
            return False

        # Must not have high spam risk
        if analysis.get("spam_risk", 0) > 0.6:
            return False

        # Must have at least one guest post signal
        signals = analysis.get("guest_post_signals", {})
        has_signals = any(signals.values())

        return has_signals

    def _evaluate_opportunity_quality(self, analysis: Dict[str, Any]) -> bool:
        """
        Evaluate if this represents a genuine guest posting opportunity.

        Args:
            analysis: Complete analysis dictionary

        Returns:
            True if genuine opportunity
        """
        signals = analysis.get("guest_post_signals", {})

        # Must have at least one strong signal
        strong_signals = [
            signals.get("has_write_for_us_page", False),
            signals.get("has_submission_guidelines", False),
            signals.get("has_guest_post_mentions", False)
        ]

        has_strong_signal = any(strong_signals)

        # Additional quality checks
        relevance_ok = analysis.get("relevance_score", 0) >= 0.3
        quality_ok = analysis.get("content_quality", 0) >= 0.4
        spam_ok = analysis.get("spam_risk", 0) <= 0.6

        return has_strong_signal and relevance_ok and quality_ok and spam_ok

    def _determine_confidence_level(self, analysis: Dict[str, Any]) -> str:
        """
        Determine confidence level in the opportunity assessment.

        Args:
            analysis: Analysis dictionary

        Returns:
            Confidence level string
        """
        score = 0.0

        # Strong signals add confidence
        signals = analysis.get("guest_post_signals", {})
        if signals.get("has_write_for_us_page"):
            score += 0.4
        if signals.get("has_submission_guidelines"):
            score += 0.3
        if signals.get("has_guest_post_mentions"):
            score += 0.2

        # Quality metrics add confidence
        if analysis.get("relevance_score", 0) > 0.5:
            score += 0.1

        if score > 0.6:
            return "high"
        elif score > 0.3:
            return "medium"
        else:
            return "low"

    def _create_opportunity_data(
        self,
        campaign_id: str,
        result: Dict[str, Any],
        analysis: Dict[str, Any],
        email_extraction: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create opportunity data dictionary for database storage.

        Args:
            campaign_id: Campaign identifier
            result: Search result
            analysis: Opportunity analysis
            email_extraction: Email extraction results

        Returns:
            Opportunity data dictionary
        """
        url = result.get("url", "")
        domain = self._extract_domain(url)

        # Extract best email and quality info
        best_email = email_extraction.get("best_email")
        best_email_quality = email_extraction.get("best_email_quality", 0)
        all_emails = email_extraction.get("emails", [])

        return {
            "url": url,
            "domain": domain,
            "title": result.get("title", ""),
            "description": result.get("content", "")[:500] if result.get("content") else "",
            "ai_content_analysis": analysis,
            "ai_relevance_score": analysis.get("relevance_score", 0),
            "ai_authority_score": analysis.get("authority_score", 0),
            "ai_content_quality_score": analysis.get("content_quality", 0),
            "ai_spam_risk_score": analysis.get("spam_risk", 0),
            "primary_topics": analysis.get("detected_topics", []),
            "content_categories": analysis.get("content_categories", []),
            "submission_guidelines": analysis.get("submission_guidelines", ""),
            "word_count_min": None,  # Will be extracted from guidelines
            "word_count_max": None,  # Will be extracted from guidelines
            "requires_images": False,  # Default
            "allows_links": True,     # Default
            "ai_contact_recommendation": analysis.get("contact_strategy", "email_outreach"),
            "ai_email_template_suggestion": analysis.get("suggested_template", "professional_initial"),
            "domain_authority": int(analysis.get("authority_score", 0) * 100),
            "quality_score": analysis.get("overall_score", 0),
            "status": "discovered" if best_email else "prospect",  # Only "discovered" if we have email
            "discovered_at": datetime.utcnow(),
            "ai_analysis_completed": True,
            # Email extraction fields
            "contact_email": best_email,
            "contact_email_quality": best_email_quality,
            "all_contact_emails": [email["email"] for email in all_emails],
            "email_extraction_method": email_extraction.get("extraction_method"),
            "email_extraction_confidence": "high" if best_email_quality >= 0.8 else "medium" if best_email_quality >= 0.6 else "low"
        }

    def _extract_domain(self, url: str) -> str:
        """
        Extract domain from URL.

        Args:
            url: Full URL

        Returns:
            Domain string
        """
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc.lower().replace("www.", "")
        except:
            return ""

    async def get_discovery_stats(self, campaign_id: str) -> Dict[str, Any]:
        """
        Get comprehensive statistics about opportunity discovery for a campaign.

        Args:
            campaign_id: Campaign identifier

        Returns:
            Discovery statistics
        """
        try:
            # This would integrate with the database service to get actual stats
            # For now, return placeholder
            return {
                "total_opportunities": 0,
                "quality_opportunities": 0,
                "api_usage": {"exa": 0, "tavily": 0},
                "cost_incurred": 0.0,
                "average_quality_score": 0.0
            }
        except Exception as e:
            campaign_logger.error(f"Error getting discovery stats: {e}")
            return {}

    # Google Trends Integration Helper Methods

    def _extract_trending_queries(self, trend_data: Dict[str, Any]) -> List[str]:
        """
        Extract trending query suggestions from Google Trends data.

        Args:
            trend_data: Google Trends analysis result

        Returns:
            List of trending query strings
        """
        trending_queries = []

        # Extract from related queries (rising)
        related_queries = trend_data.get("related_queries", {})
        rising_queries = related_queries.get("rising", [])

        for query_data in rising_queries[:5]:  # Limit to top 5
            if isinstance(query_data, dict) and "query" in query_data:
                query = query_data["query"]
                if query and len(query.split()) <= 6:  # Reasonable query length
                    trending_queries.append(query)

        # Extract from related topics (rising) and convert to queries
        related_topics = trend_data.get("related_topics", {})
        rising_topics = related_topics.get("rising", [])

        for topic_data in rising_topics[:3]:  # Limit to top 3
            if isinstance(topic_data, dict) and "topic_title" in topic_data:
                topic = topic_data["topic_title"]
                if topic and len(topic.split()) <= 4:  # Keep it concise
                    # Convert topic to potential query
                    query = f"{topic} guest post"
                    trending_queries.append(query)

        return list(set(trending_queries))  # Remove duplicates

    def _extract_seasonal_queries(self, trend_data: Dict[str, Any]) -> List[str]:
        """
        Extract seasonal query patterns from Google Trends data.

        Args:
            trend_data: Google Trends analysis result

        Returns:
            List of seasonal query strings
        """
        seasonal_queries = []
        interest_over_time = trend_data.get("interest_over_time", [])

        if not interest_over_time:
            return seasonal_queries

        # Analyze seasonal patterns (simplified approach)
        # Look for consistent patterns across the year
        monthly_patterns = {}
        for data_point in interest_over_time:
            if "date" in data_point and "value" in data_point:
                try:
                    date = datetime.fromisoformat(data_point["date"].split('T')[0])
                    month = date.month
                    value = data_point["value"]

                    if month not in monthly_patterns:
                        monthly_patterns[month] = []
                    monthly_patterns[month].append(value)
                except (ValueError, KeyError):
                    continue

        # Find months with consistently high interest
        high_season_months = []
        for month, values in monthly_patterns.items():
            if values and sum(values) / len(values) > 60:  # Above 60% of max
                high_season_months.append(month)

        # Generate seasonal queries for high-season months
        month_names = {
            1: "January", 2: "February", 3: "March", 4: "April",
            5: "May", 6: "June", 7: "July", 8: "August",
            9: "September", 10: "October", 11: "November", 12: "December"
        }

        keywords = trend_data.get("keywords", [])
        if keywords:
            base_keyword = keywords[0]
            for month in high_season_months:
                month_name = month_names.get(month, "")
                if month_name:
                    seasonal_queries.append(f"{base_keyword} {month_name}")

        return seasonal_queries[:3]  # Limit to 3 seasonal queries

    def _generate_seasonal_recommendations(self, trend_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate seasonal publishing recommendations based on trend data.

        Args:
            trend_data: Google Trends analysis result

        Returns:
            Seasonal recommendations dictionary
        """
        interest_over_time = trend_data.get("interest_over_time", [])

        if not interest_over_time:
            return {"available": False, "reason": "insufficient_data"}

        # Analyze trend patterns
        values = [point.get("value", 0) for point in interest_over_time if isinstance(point, dict)]
        if not values:
            return {"available": False, "reason": "no_values"}

        avg_interest = sum(values) / len(values)
        max_interest = max(values)
        min_interest = min(values)

        # Identify peak and low periods
        peak_threshold = avg_interest + (max_interest - avg_interest) * 0.7
        low_threshold = avg_interest - (avg_interest - min_interest) * 0.7

        peak_periods = []
        low_periods = []

        for i, point in enumerate(interest_over_time):
            if isinstance(point, dict):
                value = point.get("value", 0)
                date = point.get("date", "")

                if value >= peak_threshold:
                    peak_periods.append({"date": date, "value": value})
                elif value <= low_threshold:
                    low_periods.append({"date": date, "value": value})

        return {
            "available": True,
            "average_interest": round(avg_interest, 1),
            "peak_periods": peak_periods[:5],  # Top 5 peak periods
            "low_periods": low_periods[:5],    # Top 5 low periods
            "volatility": round((max_interest - min_interest) / avg_interest, 2),
            "recommendations": {
                "optimal_publish_times": len(peak_periods) > 0,
                "avoid_low_periods": len(low_periods) > 0,
                "seasonal_strategy_recommended": len(peak_periods) > 2
            }
        }

    def _identify_high_opportunity_regions(self, trend_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Identify geographic regions with high trend interest for targeting.

        Args:
            trend_data: Google Trends analysis result

        Returns:
            List of high-opportunity regions with interest scores
        """
        interest_by_region = trend_data.get("interest_by_region", [])

        if not interest_by_region:
            return []

        # Sort by interest score and get top regions
        sorted_regions = sorted(
            [region for region in interest_by_region if isinstance(region, dict)],
            key=lambda x: x.get("value", 0),
            reverse=True
        )

        # Return top 5 regions with scores above 50
        high_opportunity_regions = []
        for region in sorted_regions[:10]:  # Check top 10
            score = region.get("value", 0)
            if score >= 50:  # Minimum threshold for opportunity
                high_opportunity_regions.append({
                    "region": region.get("location", "Unknown"),
                    "interest_score": score,
                    "opportunity_level": "high" if score >= 75 else "medium"
                })

        return high_opportunity_regions[:5]  # Return top 5

    def _apply_trend_enhanced_scoring(
        self,
        analysis: Dict[str, Any],
        result: Dict[str, Any],
        trend_data: Dict[str, Any],
        user_keywords: List[str],
        prospecting_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Apply trend-enhanced scoring to opportunity analysis.

        Args:
            analysis: Base opportunity analysis
            result: Search result data
            trend_data: Google Trends analysis data
            user_keywords: Campaign keywords
            prospecting_context: Prospecting context data

        Returns:
            Trend-enhanced scoring additions
        """
        trend_scoring = {
            'trend_relevance_score': 0.0,
            'seasonal_alignment_score': 0.0,
            'geographic_trend_fit': 0.0,
            'trend_composite_score': 0.0,
            'trend_enhanced': True,
            'trend_opportunity_type': 'standard'
        }

        try:
            content = result.get("content", "").lower()
            title = result.get("title", "").lower()

            # Calculate trend relevance score
            trend_scoring['trend_relevance_score'] = self._calculate_trend_relevance_for_opportunity(
                content, title, trend_data, user_keywords
            )

            # Calculate seasonal alignment
            trend_scoring['seasonal_alignment_score'] = self._calculate_seasonal_alignment_for_opportunity(
                content, title, trend_data
            )

            # Calculate geographic fit
            trend_scoring['geographic_trend_fit'] = self._calculate_geographic_fit_for_opportunity(
                result.get("url", ""), trend_data
            )

            # Calculate composite trend score
            trend_scoring['trend_composite_score'] = (
                trend_scoring['trend_relevance_score'] * 0.5 +
                trend_scoring['seasonal_alignment_score'] * 0.3 +
                trend_scoring['geographic_trend_fit'] * 0.2
            )

            # Determine opportunity type based on trend factors
            if trend_scoring['trend_composite_score'] > 0.8:
                trend_scoring['trend_opportunity_type'] = 'high_trend_potential'
            elif trend_scoring['trend_composite_score'] > 0.6:
                trend_scoring['trend_opportunity_type'] = 'moderate_trend_potential'
            elif trend_scoring['seasonal_alignment_score'] > 0.7:
                trend_scoring['trend_opportunity_type'] = 'seasonal_opportunity'
            else:
                trend_scoring['trend_opportunity_type'] = 'standard_with_trend_context'

            # Boost overall opportunity quality if trend factors are strong
            if trend_scoring['trend_composite_score'] > 0.7:
                # Boost relevance score with trend factors
                original_relevance = analysis.get('relevance_score', 0)
                trend_boost = min(0.2, trend_scoring['trend_composite_score'] * 0.15)
                analysis['relevance_score'] = min(1.0, original_relevance + trend_boost)

                # Potentially upgrade confidence level
                if analysis.get('confidence_level') == 'low' and trend_scoring['trend_composite_score'] > 0.8:
                    analysis['confidence_level'] = 'medium'

        except Exception as e:
            campaign_logger.warning(f"Trend-enhanced scoring failed: {e}")
            trend_scoring['trend_enhanced'] = False
            trend_scoring['trend_scoring_error'] = str(e)

        return trend_scoring

    def _calculate_trend_relevance_for_opportunity(
        self,
        content: str,
        title: str,
        trend_data: Dict[str, Any],
        user_keywords: List[str]
    ) -> float:
        """
        Calculate trend relevance score for a specific opportunity.

        Args:
            content: Page content
            title: Page title
            trend_data: Google Trends data
            user_keywords: Campaign keywords

        Returns:
            Trend relevance score (0.0 to 1.0)
        """
        score = 0.0
        content_lower = f"{title} {content}".lower()

        # Check against rising topics
        rising_topics = trend_data.get('related_topics', {}).get('rising', [])
        for topic in rising_topics[:10]:  # Top 10 rising topics
            if isinstance(topic, dict):
                topic_title = topic.get('topic_title', '').lower()
                if topic_title in content_lower:
                    score += 0.3  # Strong signal for rising topic relevance

        # Check against rising queries
        rising_queries = trend_data.get('related_queries', {}).get('rising', [])
        for query in rising_queries[:10]:  # Top 10 rising queries
            if isinstance(query, dict):
                query_text = query.get('query', '').lower()
                if query_text in content_lower:
                    score += 0.25  # Good signal for rising query relevance

        # Check against top topics (weaker signal)
        top_topics = trend_data.get('related_topics', {}).get('top', [])
        for topic in top_topics[:15]:  # Top 15 established topics
            if isinstance(topic, dict):
                topic_title = topic.get('topic_title', '').lower()
                if topic_title in content_lower:
                    score += 0.15  # Moderate signal for established topic relevance

        # Bonus for user keyword alignment with trending topics
        for keyword in user_keywords:
            keyword_lower = keyword.lower()
            for topic in rising_topics[:5]:
                if isinstance(topic, dict):
                    topic_title = topic.get('topic_title', '').lower()
                    if keyword_lower in topic_title or topic_title in keyword_lower:
                        score += 0.1

        return min(1.0, score)

    def _calculate_seasonal_alignment_for_opportunity(
        self,
        content: str,
        title: str,
        trend_data: Dict[str, Any]
    ) -> float:
        """
        Calculate seasonal alignment score for content timing.

        Args:
            content: Page content
            title: Page title
            trend_data: Google Trends data

        Returns:
            Seasonal alignment score (0.0 to 1.0)
        """
        score = 0.0
        content_lower = f"{title} {content}".lower()

        # Seasonal keywords that indicate timing relevance
        seasonal_indicators = [
            'seasonal', 'quarterly', 'monthly', 'annual', 'yearly',
            'january', 'february', 'march', 'april', 'may', 'june',
            'july', 'august', 'september', 'october', 'november', 'december',
            'holiday', 'holidays', 'summer', 'winter', 'spring', 'fall', 'autumn',
            'back to school', 'tax season', 'new year', 'christmas', 'thanksgiving',
            'easter', 'valentines', 'mothers day', 'fathers day', 'halloween'
        ]

        # Count seasonal keyword matches
        seasonal_matches = sum(1 for keyword in seasonal_indicators if keyword in content_lower)
        score += min(0.4, seasonal_matches * 0.1)

        # Check if content aligns with peak trend periods
        interest_over_time = trend_data.get('interest_over_time', [])
        if interest_over_time:
            # Find current peak periods (simplified - could be enhanced with current date)
            values = [point.get('value', 0) for point in interest_over_time if isinstance(point, dict)]
            if values:
                avg_interest = sum(values) / len(values)
                peak_values = [v for v in values if v > avg_interest * 1.2]

                if peak_values:
                    # Content that mentions timing gets higher seasonal score
                    timing_keywords = ['now', 'current', 'today', 'this week', 'this month', 'latest', 'recent']
                    timing_matches = sum(1 for keyword in timing_keywords if keyword in content_lower)
                    score += min(0.3, timing_matches * 0.1)

                    # Boost score if content appears timely
                    score += 0.3

        return min(1.0, score)

    def _calculate_geographic_fit_for_opportunity(
        self,
        url: str,
        trend_data: Dict[str, Any]
    ) -> float:
        """
        Calculate geographic relevance for regional targeting.

        Args:
            url: Website URL
            trend_data: Google Trends data

        Returns:
            Geographic fit score (0.0 to 1.0)
        """
        score = 0.0

        # Extract domain information
        try:
            domain = self._extract_domain(url)
        except:
            return 0.0

        # Check against regional interest data
        interest_by_region = trend_data.get('interest_by_region', [])
        if not interest_by_region:
            return 0.0

        # Look for regional alignment
        for region_data in interest_by_region:
            if isinstance(region_data, dict):
                region_name = region_data.get('location', '').lower()
                interest_score = region_data.get('value', 0)

                # Check if region name appears in domain or content
                if region_name in domain.lower() or domain.lower() in region_name:
                    # Higher score for stronger regional interest
                    score = min(1.0, interest_score / 100.0)
                    break

        # If no direct regional match, check for high-interest regions overall
        if score == 0.0:
            top_regions = sorted(
                [r for r in interest_by_region if isinstance(r, dict)],
                key=lambda x: x.get('value', 0),
                reverse=True
            )[:3]  # Top 3 regions

            avg_top_interest = sum(r.get('value', 0) for r in top_regions) / len(top_regions) if top_regions else 0
            if avg_top_interest > 70:  # High regional interest overall
                score = 0.2  # Moderate geographic potential

        return score

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except:
            return ""