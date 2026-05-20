"""
GSC Brainstorm Service for ALwrity.

Analyzes Google Search Console data to suggest blog topics the user should write about.
Combines rule-based heuristics (high-impression/low-CTR keywords, near-page-1 positions)
with LLM-powered strategic recommendations tailored to the user's topic intent.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from loguru import logger

from services.gsc_service import GSCService
from services.llm_providers.main_text_generation import llm_text_gen


class GSCBrainstormService:
    """
    Suggests blog topics based on the user's live GSC data.

    Flow:
    1. Fetch real GSC search analytics (query + page data, 30 days)
    2. Apply rule-based filters (Content Optimization, Content Enhancement, Keyword Gap)
    3. Generate LLM-powered strategic recommendations contextualised to the user's keywords
    4. Return structured results
    """

    def __init__(self, gsc_service: GSCService = None):
        self.gsc_service = gsc_service or GSCService()

    # ------------------------------------------------------------------ #
    #  Public entry point
    # ------------------------------------------------------------------ #

    def brainstorm_topics(
        self,
        user_id: str,
        keywords: str,
        site_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate blog topic suggestions from the user's GSC data.

        Args:
            user_id: Clerk user ID (must have GSC connected).
            keywords: User's 3+ word topic intent (e.g. "content marketing strategy").
            site_url: Optional site URL; auto-selected from user's first GSC site if omitted.

        Returns:
            Dict with content_opportunities, keyword_gaps, ai_recommendations, summary.
        """
        self._user_id = user_id
        # 1. Resolve site_url
        if not site_url:
            sites = self.gsc_service.get_site_list(user_id)
            if not sites:
                return {
                    "error": "No GSC sites found. Make sure your site is verified in Google Search Console.",
                    "content_opportunities": [],
                    "keyword_gaps": [],
                    "ai_recommendations": {},
                    "summary": {},
                }
            site_url = sites[0].get("siteUrl", "")

        # 2. Fetch GSC analytics (30 days)
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        analytics = self.gsc_service.get_search_analytics(
            user_id=user_id,
            site_url=site_url,
            start_date=start_date,
            end_date=end_date,
        )

        if "error" in analytics:
            return {
                "error": analytics.get("error", "Failed to fetch GSC data"),
                "content_opportunities": [],
                "keyword_gaps": [],
                "ai_recommendations": {},
                "summary": {},
            }

        # 3. Parse GSC rows into structured data
        query_rows = analytics.get("query_data", {}).get("rows", [])
        page_rows = analytics.get("page_data", {}).get("rows", [])

        keywords_data = self._parse_query_rows(query_rows)
        pages_data = self._parse_page_rows(page_rows)

        if not keywords_data:
            return {
                "error": "No keyword data available for the selected period.",
                "content_opportunities": [],
                "keyword_gaps": [],
                "ai_recommendations": {},
                "summary": {
                    "site_url": site_url,
                    "date_range": {"start": start_date, "end": end_date},
                    "total_keywords_analyzed": 0,
                },
            }

        # 4. Rule-based analysis
        content_opportunities = self._identify_content_opportunities(keywords_data)
        keyword_gaps = self._identify_keyword_gaps(keywords_data)

        # 5. Summary metrics
        summary = self._compute_summary(keywords_data, pages_data, site_url, start_date, end_date)

        # 6. AI recommendations (best-effort; don't fail the whole request on LLM error)
        ai_recommendations = self._generate_ai_recommendations(
            keywords_data, pages_data, summary, keywords
        )

        return {
            "content_opportunities": content_opportunities,
            "keyword_gaps": keyword_gaps,
            "ai_recommendations": ai_recommendations,
            "summary": summary,
        }

    # ------------------------------------------------------------------ #
    #  Data parsing helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _parse_query_rows(rows: List[Dict]) -> List[Dict[str, Any]]:
        parsed = []
        for row in rows:
            keys = row.get("keys", [])
            keyword = keys[0] if len(keys) >= 1 else "(not set)"
            parsed.append({
                "keyword": keyword,
                "clicks": row.get("clicks", 0),
                "impressions": row.get("impressions", 0),
                "ctr": round(row.get("ctr", 0) * 100, 2),
                "position": round(row.get("position", 0), 1),
            })
        return parsed

    @staticmethod
    def _parse_page_rows(rows: List[Dict]) -> List[Dict[str, Any]]:
        parsed = []
        for row in rows:
            keys = row.get("keys", [])
            page = keys[0] if len(keys) >= 1 else "(not set)"
            parsed.append({
                "page": page,
                "clicks": row.get("clicks", 0),
                "impressions": row.get("impressions", 0),
                "ctr": round(row.get("ctr", 0) * 100, 2),
                "position": round(row.get("position", 0), 1),
            })
        return parsed

    # ------------------------------------------------------------------ #
    #  Rule-based opportunity identification
    # ------------------------------------------------------------------ #

    @staticmethod
    def _identify_content_opportunities(
        keywords_data: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        opportunities: List[Dict[str, Any]] = []

        # Rule 1: Content Optimization — high impressions, low CTR
        for kw in keywords_data:
            if kw["impressions"] > 500 and kw["ctr"] < 3:
                opportunities.append({
                    "type": "Content Optimization",
                    "keyword": kw["keyword"],
                    "opportunity": (
                        f"Optimize existing content for '{kw['keyword']}' "
                        f"to improve CTR from {kw['ctr']:.1f}% "
                        f"(position {kw['position']:.1f})"
                    ),
                    "potential_impact": "High",
                    "current_position": kw["position"],
                    "impressions": kw["impressions"],
                    "priority": "High" if kw["impressions"] > 1000 else "Medium",
                })

        # Rule 2: Content Enhancement — positions 11-20 with decent impressions
        for kw in keywords_data:
            if 10 < kw["position"] <= 20 and kw["impressions"] > 100:
                opportunities.append({
                    "type": "Content Enhancement",
                    "keyword": kw["keyword"],
                    "opportunity": (
                        f"Enhance content for '{kw['keyword']}' to move from "
                        f"position {kw['position']:.1f} to the first page"
                    ),
                    "potential_impact": "Medium",
                    "current_position": kw["position"],
                    "impressions": kw["impressions"],
                    "priority": "Medium",
                })

        # Sort by impressions descending, keep top 10
        opportunities.sort(key=lambda x: x["impressions"], reverse=True)
        return opportunities[:10]

    @staticmethod
    def _identify_keyword_gaps(
        keywords_data: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        gaps: List[Dict[str, Any]] = []

        for kw in keywords_data:
            if 4 <= kw["position"] <= 20 and kw["impressions"] >= 50:
                gaps.append({
                    "keyword": kw["keyword"],
                    "position": kw["position"],
                    "impressions": kw["impressions"],
                })

        gaps.sort(key=lambda x: x["impressions"], reverse=True)
        return gaps[:10]

    # ------------------------------------------------------------------ #
    #  Summary metrics
    # ------------------------------------------------------------------ #

    @staticmethod
    def _compute_summary(
        keywords_data: List[Dict],
        pages_data: List[Dict],
        site_url: str,
        start_date: str,
        end_date: str,
    ) -> Dict[str, Any]:
        total_impressions = sum(kw["impressions"] for kw in keywords_data)
        total_clicks = sum(kw["clicks"] for kw in keywords_data)
        avg_ctr = round((total_clicks / total_impressions * 100) if total_impressions else 0, 2)
        avg_position = round(
            sum(kw["position"] for kw in keywords_data) / len(keywords_data), 1
        ) if keywords_data else 0

        pos_1_3 = len([kw for kw in keywords_data if kw["position"] <= 3])
        pos_4_10 = len([kw for kw in keywords_data if 3 < kw["position"] <= 10])
        pos_11_20 = len([kw for kw in keywords_data if 10 < kw["position"] <= 20])
        pos_21_plus = len([kw for kw in keywords_data if kw["position"] > 20])

        top_keywords = sorted(keywords_data, key=lambda x: x["impressions"], reverse=True)[:5]
        top_pages = sorted(pages_data, key=lambda x: x["clicks"], reverse=True)[:3]

        return {
            "site_url": site_url,
            "date_range": {"start": start_date, "end": end_date},
            "total_keywords_analyzed": len(keywords_data),
            "total_impressions": total_impressions,
            "total_clicks": total_clicks,
            "avg_ctr": avg_ctr,
            "avg_position": avg_position,
            "keyword_distribution": {
                "positions_1_3": pos_1_3,
                "positions_4_10": pos_4_10,
                "positions_11_20": pos_11_20,
                "positions_21_plus": pos_21_plus,
            },
            "top_keywords": [
                {"keyword": kw["keyword"], "impressions": kw["impressions"], "position": kw["position"]}
                for kw in top_keywords
            ],
            "top_pages": [
                {"page": pg["page"], "clicks": pg["clicks"], "impressions": pg["impressions"]}
                for pg in top_pages
            ],
        }

    # ------------------------------------------------------------------ #
    #  AI-powered strategic recommendations
    # ------------------------------------------------------------------ #

    def _generate_ai_recommendations(
        self,
        keywords_data: List[Dict],
        pages_data: List[Dict],
        summary: Dict,
        user_keywords: str,
    ) -> Dict[str, Any]:
        try:
            top_kw = ", ".join(kw["keyword"] for kw in summary.get("top_keywords", []))
            dist = summary.get("keyword_distribution", {})

            prompt = f"""Analyze this Google Search Console data and suggest blog topics the user should write about.

USER'S TOPIC INTENT: "{user_keywords}"

SEARCH PERFORMANCE SUMMARY:
- Total Keywords Tracked: {summary.get('total_keywords_analyzed', 0)}
- Total Impressions: {summary.get('total_impressions', 0):,}
- Total Clicks: {summary.get('total_clicks', 0):,}
- Average CTR: {summary.get('avg_ctr', 0):.2f}%
- Average Position: {summary.get('avg_position', 0):.1f}

TOP PERFORMING KEYWORDS:
{top_kw}

KEYWORD POSITION DISTRIBUTION:
- Positions 1-3: {dist.get('positions_1_3', 0)}
- Positions 4-10: {dist.get('positions_4_10', 0)}
- Positions 11-20: {dist.get('positions_11_20', 0)}
- Positions 21+: {dist.get('positions_21_plus', 0)}

Based on this data, provide:

1. IMMEDIATE TOPIC OPPORTUNITIES (0-30 days):
   - Specific blog post titles the user should write
   - Each tied to a keyword opportunity from the data
   - 3-5 suggestions

2. CONTENT STRATEGY TOPICS (1-3 months):
   - New topic clusters to build authority
   - Content pillar ideas
   - 3-5 suggestions

3. LONG-TERM CONTENT VISION (3-12 months):
   - Market expansion topics
   - Authority-building content ideas
   - 3-5 suggestions

IMPORTANT: Relate every topic suggestion to the user's interest in "{user_keywords}".
Return your response in this exact JSON format:
{{
  "immediate_opportunities": ["topic 1", "topic 2", "topic 3"],
  "content_strategy": ["strategy 1", "strategy 2", "strategy 3"],
  "long_term_strategy": ["vision 1", "vision 2", "vision 3"]
}}"""

            system_prompt = (
                "You are an enterprise SEO content strategist. Provide specific, data-driven "
                "blog topic suggestions that will improve the user's search performance. "
                "Always respond with valid JSON matching the requested format."
            )

            result = llm_text_gen(
                prompt=prompt,
                system_prompt=system_prompt,
                user_id=getattr(self, '_user_id', None),
                flow_type="gsc_brainstorm",
            )

            if result:
                parsed = self._parse_ai_response(result)
                if parsed:
                    return parsed

            return self._fallback_ai_recommendations(keywords_data)

        except Exception as e:
            logger.warning(f"GSC brainstorm AI recommendations failed: {e}")
            return self._fallback_ai_recommendations(keywords_data)

    @staticmethod
    def _parse_ai_response(raw: str) -> Optional[Dict[str, List[str]]]:
        try:
            json_start = raw.find("{")
            json_end = raw.rfind("}") + 1
            if json_start == -1 or json_end == 0:
                return None

            chunk = raw[json_start:json_end]
            parsed = json.loads(chunk)

            return {
                "immediate_opportunities": parsed.get("immediate_opportunities", [])[:5],
                "content_strategy": parsed.get("content_strategy", [])[:5],
                "long_term_strategy": parsed.get("long_term_strategy", [])[:5],
            }
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Failed to parse AI brainstorm response as JSON: {e}")
            return None

    @staticmethod
    def _fallback_ai_recommendations(
        keywords_data: List[Dict],
    ) -> Dict[str, Any]:
        top_kw = keywords_data[:3] if keywords_data else []
        immediate = []
        for kw in top_kw:
            immediate.append(
                f"Write a comprehensive guide on '{kw['keyword']}' "
                f"(currently at position {kw['position']:.1f} with "
                f"{kw['impressions']} impressions)"
            )

        return {
            "immediate_opportunities": immediate or ["No keyword data available for recommendations"],
            "content_strategy": [
                "Develop topic clusters around your top-performing keywords",
                "Create comparison and vs-style content for competitive terms",
                "Build FAQ sections targeting question-based queries",
            ],
            "long_term_strategy": [
                "Build domain authority through pillar content",
                "Expand into adjacent topic areas",
                "Develop thought leadership content series",
            ],
        }