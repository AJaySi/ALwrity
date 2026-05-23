"""
GSC Brainstorm Service for ALwrity.

Analyzes Google Search Console data to suggest blog topics the user should write about.
Combines rule-based heuristics with LLM-powered strategic recommendations tailored to
the user's topic intent. Designed for non-SEO-experts: every insight includes plain-English
explanations of WHY it matters and WHAT to do about it.
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
    2. Compute derived metrics (CTR benchmarks, estimated traffic uplift, content formats)
    3. Apply rule-based filters (Quick Wins, Optimization, Enhancement, Rising Stars, Page Issues)
    4. Generate LLM-powered strategic recommendations contextualised to the user's keywords
    5. Return structured results with all data exposed for rich frontend display
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
        self._user_id = user_id

        # 1. Resolve site_url
        if not site_url:
            sites = self.gsc_service.get_site_list(user_id)
            if not sites:
                return {
                    "error": "No GSC sites found. Make sure your site is verified in Google Search Console.",
                    "content_opportunities": [],
                    "keyword_gaps": [],
                    "quick_wins": [],
                    "page_opportunities": [],
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
                "quick_wins": [],
                "page_opportunities": [],
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
                "error": "No keyword data available for the selected period. This usually means your site is new to GSC or hasn't received search traffic yet.",
                "content_opportunities": [],
                "keyword_gaps": [],
                "quick_wins": [],
                "page_opportunities": [],
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
        quick_wins = self._identify_quick_wins(keywords_data)
        page_opportunities = self._identify_page_opportunities(pages_data)

        # 5. Summary metrics
        summary = self._compute_summary(keywords_data, pages_data, site_url, start_date, end_date)

        # 6. AI recommendations
        ai_recommendations = self._generate_ai_recommendations(
            keywords_data, pages_data, summary, keywords,
            content_opportunities, quick_wins, keyword_gaps,
        )

        return {
            "content_opportunities": content_opportunities,
            "keyword_gaps": keyword_gaps,
            "quick_wins": quick_wins,
            "page_opportunities": page_opportunities,
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
        # Meaning: Google is SHOWING your page for this query but people aren't clicking.
        #          The content probably ranks but title/meta/snippet isn't compelling enough.
        for kw in keywords_data:
            if kw["impressions"] > 500 and kw["ctr"] < 3:
                estimated_gain = int(kw["impressions"] * 0.05) - kw["clicks"]
                opportunities.append({
                    "type": "Content Optimization",
                    "keyword": kw["keyword"],
                    "opportunity": (
                        f"Your site appears for '{kw['keyword']}' ({kw['impressions']:,} times/month) "
                        f"but only {kw['ctr']:.1f}% click. Improving your title and meta description "
                        f"could bring ~{max(estimated_gain, 5)} more clicks/month."
                    ),
                    "potential_impact": "High" if kw["impressions"] > 1000 else "Medium",
                    "current_position": kw["position"],
                    "current_ctr": kw["ctr"],
                    "impressions": kw["impressions"],
                    "clicks": kw["clicks"],
                    "estimated_traffic_gain": max(estimated_gain, 5),
                    "priority": "High" if kw["impressions"] > 1000 else "Medium",
                    "suggested_format": GSCBrainstormService._suggest_format(kw["keyword"]),
                })

        # Rule 2: Content Enhancement — positions 11-20 with decent impressions
        # Meaning: You're on page 2 of Google. A small content boost could push you to page 1,
        #          where CTR increases dramatically (page 1 gets ~95% of all clicks).
        for kw in keywords_data:
            if 10 < kw["position"] <= 20 and kw["impressions"] > 100:
                estimated_gain = int(kw["impressions"] * 0.08)
                opportunities.append({
                    "type": "Content Enhancement",
                    "keyword": kw["keyword"],
                    "opportunity": (
                        f"'{kw['keyword']}' ranks #{kw['position']:.0f} (page 2). "
                        f"Moving to page 1 could capture ~{estimated_gain} more clicks/month "
                        f"from {kw['impressions']:,} impressions."
                    ),
                    "potential_impact": "High" if kw["impressions"] > 500 else "Medium",
                    "current_position": kw["position"],
                    "current_ctr": kw["ctr"],
                    "impressions": kw["impressions"],
                    "clicks": kw["clicks"],
                    "estimated_traffic_gain": estimated_gain,
                    "priority": "High" if kw["impressions"] > 500 else "Medium",
                    "suggested_format": GSCBrainstormService._suggest_format(kw["keyword"]),
                })

        opportunities.sort(key=lambda x: x["impressions"], reverse=True)
        return opportunities[:10]

    @staticmethod
    def _identify_keyword_gaps(
        keywords_data: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        gaps: List[Dict[str, Any]] = []

        for kw in keywords_data:
            if 4 <= kw["position"] <= 20 and kw["impressions"] >= 50:
                # Estimate traffic gain if this keyword moved to position 1-3
                # Position 1 avg CTR ~31%, position 3 ~11%, current position CTR estimate
                position_1_ctr = 31.0
                current_ctr = kw["ctr"]
                estimated_gain = max(int(kw["impressions"] * (position_1_ctr - current_ctr) / 100), 1)

                gaps.append({
                    "keyword": kw["keyword"],
                    "position": kw["position"],
                    "impressions": kw["impressions"],
                    "current_ctr": kw["ctr"],
                    "clicks": kw["clicks"],
                    "estimated_traffic_if_page1": estimated_gain,
                    "gap_from_page1": round(kw["position"] - 3, 1),
                })

        gaps.sort(key=lambda x: x["impressions"], reverse=True)
        return gaps[:10]

    @staticmethod
    def _identify_quick_wins(
        keywords_data: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Keywords already on page 1 (positions 4-10) that could reach top 3
        with minor improvements — the highest-ROI opportunities."""
        quick_wins: List[Dict[str, Any]] = []

        for kw in keywords_data:
            if 4 <= kw["position"] <= 10 and kw["impressions"] >= 100:
                # Position 3 CTR ≈ 11%, position 5 CTR ≈ 6%
                # Small improvements can yield big traffic gains
                target_ctr = 11.0  # approximate CTR for position 3
                estimated_gain = max(int(kw["impressions"] * (target_ctr - kw["ctr"]) / 100), 1)

                quick_wins.append({
                    "keyword": kw["keyword"],
                    "position": kw["position"],
                    "impressions": kw["impressions"],
                    "current_ctr": kw["ctr"],
                    "clicks": kw["clicks"],
                    "estimated_traffic_gain": estimated_gain,
                    "reason": (
                        f"Already on page 1 at position #{kw['position']:.0f}. "
                        f"Optimizing this page could increase CTR from {kw['ctr']:.1f}% "
                        f"to ~{target_ctr:.0f}%, gaining ~{estimated_gain} clicks/month."
                    ),
                })

        quick_wins.sort(key=lambda x: x["estimated_traffic_gain"], reverse=True)
        return quick_wins[:5]

    @staticmethod
    def _identify_page_opportunities(
        pages_data: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Pages with high impressions but low CTR — the content or meta needs work."""
        opportunities: List[Dict[str, Any]] = []

        for pg in pages_data:
            if pg["impressions"] > 300 and pg["ctr"] < 2.0:
                short_page = pg["page"].rstrip("/").rsplit("/", 1)[-1].replace("-", " ").title()
                if len(short_page) > 60:
                    short_page = short_page[:57] + "..."
                opportunities.append({
                    "page": pg["page"],
                    "page_title": short_page,
                    "impressions": pg["impressions"],
                    "clicks": pg["clicks"],
                    "current_ctr": pg["ctr"],
                    "current_position": pg["position"],
                    "reason": (
                        f"This page gets {pg['impressions']:,} impressions but only {pg['ctr']:.1f}% CTR. "
                        f"Reviewing the title and meta description could significantly boost clicks."
                    ),
                })

        opportunities.sort(key=lambda x: x["impressions"], reverse=True)
        return opportunities[:5]

    # ------------------------------------------------------------------ #
    #  Content format suggestion
    # ------------------------------------------------------------------ #

    @staticmethod
    def _suggest_format(keyword: str) -> str:
        """Suggest a content format based on keyword patterns."""
        kw = keyword.lower()
        if any(w in kw for w in ["how to", "how do", "guide", "tutorial", "steps"]):
            return "How-To Guide"
        if any(w in kw for w in ["vs", "versus", "compare", "comparison", "difference"]):
            return "Comparison"
        if any(w in kw for w in ["best", "top", "recommended", "review", "reviews"]):
            return "Top Picks / Review"
        if any(w in kw for w in ["what is", "definition", "meaning", "explained"]):
            return "Explainer"
        if any(w in kw for w in ["list", "examples", "ideas", "tips", "ways"]):
            return "Listicle"
        if any(w in kw for w in ["free", "cheap", "alternative", "budget"]):
            return "Budget / Alternative"
        if any(w in kw for w in ["template", "calculator", "tool", "checker"]):
            return "Tool / Template"
        if any(w in kw for w in ["2024", "2025", "2026", "trends", "prediction", "future"]):
            return "Trend Report"
        return "In-Depth Article"

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

        # Health score: 0-100 based on how many keywords are on page 1
        total_kw = len(keywords_data) or 1
        page1_pct = (pos_1_3 + pos_4_10) / total_kw * 100
        top3_pct = pos_1_3 / total_kw * 100
        health_score = round(min(top3_pct * 3 + page1_pct * 0.7, 100), 0)

        # CTR benchmark: industry average is ~3.1% for position 1-10
        ctr_benchmark = 3.1
        ctr_vs_benchmark = round(avg_ctr - ctr_benchmark, 2)

        return {
            "site_url": site_url,
            "date_range": {"start": start_date, "end": end_date},
            "total_keywords_analyzed": len(keywords_data),
            "total_impressions": total_impressions,
            "total_clicks": total_clicks,
            "avg_ctr": avg_ctr,
            "avg_position": avg_position,
            "ctr_vs_benchmark": ctr_vs_benchmark,
            "health_score": health_score,
            "keyword_distribution": {
                "positions_1_3": pos_1_3,
                "positions_4_10": pos_4_10,
                "positions_11_20": pos_11_20,
                "positions_21_plus": pos_21_plus,
            },
            "top_keywords": [
                {
                    "keyword": kw["keyword"],
                    "impressions": kw["impressions"],
                    "clicks": kw["clicks"],
                    "position": kw["position"],
                    "ctr": kw["ctr"],
                }
                for kw in top_keywords
            ],
            "top_pages": [
                {
                    "page": pg["page"],
                    "clicks": pg["clicks"],
                    "impressions": pg["impressions"],
                    "ctr": pg["ctr"],
                }
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
        content_opportunities: List[Dict],
        quick_wins: List[Dict],
        keyword_gaps: List[Dict],
    ) -> Dict[str, Any]:
        try:
            top_kw_list = summary.get("top_keywords", [])
            top_kw_str = "\n".join(
                f"  • {kw['keyword']}: {kw['impressions']:,} impressions, position {kw['position']}, {kw['ctr']:.1f}% CTR"
                for kw in top_kw_list[:10]
            )
            dist = summary.get("keyword_distribution", {})

            opp_str = ""
            if content_opportunities:
                opp_str = "\nCONTENT OPPORTUNITIES (rule-based findings):\n" + "\n".join(
                    f"  • {o['keyword']}: {o['opportunity']}"
                    for o in content_opportunities[:5]
                )
            else:
                opp_str = "\nNo major content opportunities detected from rule-based analysis."

            qw_str = ""
            if quick_wins:
                qw_str = "\nQUICK WINS (already on page 1, easy to optimize):\n" + "\n".join(
                    f"  • {q['keyword']}: position #{q['position']:.0f}, {q['current_ctr']:.1f}% CTR, est. +{q['estimated_traffic_gain']} clicks/month"
                    for q in quick_wins[:3]
                )

            prompt = f"""You are an expert SEO content strategist analyzing real Google Search Console data for a blog writer.

The user wants to write about: "{user_keywords}"

Here is their GSC data for the last 30 days:

PERFORMANCE OVERVIEW:
- Total Keywords: {summary.get('total_keywords_analyzed', 0)}
- Total Impressions: {summary.get('total_impressions', 0):,}
- Total Clicks: {summary.get('total_clicks', 0):,}
- Average CTR: {summary.get('avg_ctr', 0):.2f}% (industry avg for positions 1-10 is ~3.1%)
- Average Position: {summary.get('avg_position', 0):.1f}
- SEO Health Score: {summary.get('health_score', 0)}/100

TOP KEYWORDS BY IMPRESSIONS:
{top_kw_str}

KEYWORD POSITION DISTRIBUTION:
- Position 1-3 (top results): {dist.get('positions_1_3', 0)} keywords
- Position 4-10 (page 1): {dist.get('positions_4_10', 0)} keywords
- Position 11-20 (page 2): {dist.get('positions_11_20', 0)} keywords
- Position 21+ (page 3+): {dist.get('positions_21_plus', 0)} keywords
{opp_str}
{qw_str}

Based on this data, provide EXACT blog post suggestions the user should write.

For each suggestion include:
1. A specific, compelling blog post TITLE (not vague topic)
2. The keyword it targets and why (based on the data above)
3. The recommended content format (how-to, listicle, comparison, etc.)
4. Estimated impact (how many more clicks/month they could gain)

Return your response in this EXACT JSON format (no markdown, no code fences):
{{
  "immediate_opportunities": [
    {{
      "title": "Specific Blog Post Title Here",
      "keyword": "target keyword",
      "reason": "Why this will work based on the data",
      "format": "How-To Guide | Listicle | Comparison | Explainer | etc.",
      "estimated_impact": "Estimated X more clicks/month"
    }}
  ],
  "content_strategy": [
    {{
      "title": "Pillar Content Title",
      "keyword": "target keyword",
      "reason": "Strategic reasoning",
      "format": "Content format",
      "estimated_impact": "Expected impact"
    }}
  ],
  "long_term_strategy": [
    {{
      "title": "Authority Building Title",
      "keyword": "target keyword",
      "reason": "Long-term reasoning",
      "format": "Content format",
      "estimated_impact": "Expected long-term impact"
    }}
  ]
}}

IMPORTANT:
- Provide 3-5 items in each category
- Every suggestion MUST relate to the user's interest in "{user_keywords}"
- Titles should be specific and compelling, like real blog post headlines
- Use the data above to justify each recommendation
- Prioritize keywords with high impressions but low CTR or low position"""

            system_prompt = (
                "You are an expert SEO content strategist. You analyze Google Search Console data "
                "and provide specific, actionable blog post recommendations that will drive real traffic. "
                "You always respond with valid JSON matching the requested format. "
                "Every recommendation must be backed by the data provided."
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

            return self._fallback_ai_recommendations(keywords_data, content_opportunities, quick_wins)

        except Exception as e:
            logger.warning(f"GSC brainstorm AI recommendations failed: {e}")
            return self._fallback_ai_recommendations(keywords_data, content_opportunities, quick_wins)

    def _parse_ai_response(self, raw: str) -> Optional[Dict[str, Any]]:
        try:
            # Strip markdown code fences if present
            cleaned = raw.strip()
            if cleaned.startswith("```"):
                first_newline = cleaned.find("\n")
                if first_newline != -1:
                    cleaned = cleaned[first_newline + 1:]
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3].strip()

            json_start = cleaned.find("{")
            json_end = cleaned.rfind("}") + 1
            if json_start == -1 or json_end == 0:
                return None

            chunk = cleaned[json_start:json_end]
            parsed = json.loads(chunk)

            def normalize_section(section: Any) -> List[Dict[str, str]]:
                if not isinstance(section, list):
                    return []
                result = []
                for item in section:
                    if isinstance(item, str):
                        result.append({
                            "title": item.split(":")[0].strip() if ":" in item else item[:60],
                            "keyword": "",
                            "reason": item,
                            "format": "",
                            "estimated_impact": "",
                        })
                    elif isinstance(item, dict):
                        result.append({
                            "title": str(item.get("title", "")),
                            "keyword": str(item.get("keyword", "")),
                            "reason": str(item.get("reason", "")),
                            "format": str(item.get("format", "")),
                            "estimated_impact": str(item.get("estimated_impact", "")),
                        })
                return result

            return {
                "immediate_opportunities": normalize_section(parsed.get("immediate_opportunities", []))[:5],
                "content_strategy": normalize_section(parsed.get("content_strategy", []))[:5],
                "long_term_strategy": normalize_section(parsed.get("long_term_strategy", []))[:5],
            }
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Failed to parse AI brainstorm response as JSON: {e}")
            return None

    @staticmethod
    def _fallback_ai_recommendations(
        keywords_data: List[Dict],
        content_opportunities: List[Dict],
        quick_wins: List[Dict],
    ) -> Dict[str, Any]:
        top_kw = keywords_data[:3] if keywords_data else []
        immediate = []

        # Build from quick wins first (highest ROI)
        for qw in quick_wins[:2]:
            immediate.append({
                "title": f"How to Rank #{int(qw['position'])} for '{qw['keyword']}' — Optimization Guide",
                "keyword": qw["keyword"],
                "reason": qw.get("reason", f"Already on page 1 at position {qw['position']:.0f}"),
                "format": "How-To Guide",
                "estimated_impact": f"+{qw.get('estimated_traffic_gain', 10)} clicks/month",
            })

        # Then from content opportunities
        for opp in content_opportunities[:2]:
            immediate.append({
                "title": f"Complete Guide to {opp['keyword'].title()}",
                "keyword": opp["keyword"],
                "reason": opp.get("opportunity", f"{opp['impressions']:,} impressions with room to improve"),
                "format": opp.get("suggested_format", "In-Depth Article"),
                "estimated_impact": f"+{opp.get('estimated_traffic_gain', 10)} clicks/month",
            })

        # Fill remaining with top keywords
        remaining = 5 - len(immediate)
        for kw in top_kw[:remaining]:
            immediate.append({
                "title": f"The Ultimate Guide to {kw['keyword'].title()}",
                "keyword": kw["keyword"],
                "reason": f"Top keyword with {kw['impressions']:,} impressions (position {kw['position']:.1f})",
                "format": "In-Depth Article",
                "estimated_impact": f"+{max(int(kw['impressions'] * 0.03), 5)} clicks/month",
            })

        return {
            "immediate_opportunities": immediate or [{"title": "No keyword data available", "keyword": "", "reason": "Connect GSC to get personalized suggestions", "format": "", "estimated_impact": ""}],
            "content_strategy": [
                {"title": "Topic Cluster: Build Authority Around Your Core Topics", "keyword": "", "reason": "Clustered content ranks higher and captures more long-tail queries", "format": "Pillar Page + Spokes", "estimated_impact": "+50-200 clicks/month over 3 months"},
                {"title": "Comparison Guide: Your Product vs. Alternatives", "keyword": "", "reason": "Comparison content captures high-intent searchers ready to decide", "format": "Comparison", "estimated_impact": "+20-80 clicks/month"},
                {"title": "FAQ: Answer What Your Audience Is Asking", "keyword": "", "reason": "FAQs capture featured snippets and voice search queries", "format": "FAQ / Listicle", "estimated_impact": "+30-100 clicks/month"},
            ],
            "long_term_strategy": [
                {"title": "Pillar Content: The Definitive Resource in Your Niche", "keyword": "", "reason": "Comprehensive guides become authoritative references that attract backlinks", "format": "Long-Form Guide", "estimated_impact": "+100-500 clicks/month over 6-12 months"},
                {"title": "Trend Report: What's Next in Your Industry", "keyword": "", "reason": "Forward-looking content captures emerging search demand early", "format": "Trend Report", "estimated_impact": "+50-200 clicks/month"},
                {"title": "Thought Leadership: Expert Roundup and Insights", "keyword": "", "reason": "Expert content builds E-E-A-T signals that improve overall domain authority", "format": "Expert Roundup", "estimated_impact": "+30-100 clicks/month per piece"},
            ],
        }