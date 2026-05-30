"""
AI Visibility Insights Service

Detects Google AI Overview impact signals from GSC search analytics data.

Core heuristic:
  - AIO Impacted keywords: high impressions + high position (top 3) + very low CTR
    → content likely being shown/cited in Google AI Overviews without clicks
  - AIO Opportunity keywords: strong CTR + moderate position
    → content already performing well, potential for AIO citation with optimization

All thresholds are configurable for flexibility.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from loguru import logger

from services.gsc_service import GSCService


@dataclass
class AIOThresholds:
    """Configurable thresholds for AI Overview detection."""

    # AIO Impacted detection
    impacted_min_impressions: int = 500
    impacted_max_position: float = 4.0
    impacted_max_ctr: float = 2.0

    # AIO Opportunity detection
    opportunity_min_impressions: int = 300
    opportunity_min_position: float = 4.0
    opportunity_max_position: float = 10.0
    opportunity_min_ctr: float = 5.0


@dataclass
class AIOVisibilityResult:
    """Structured result from AI Overview analysis."""

    summary: Dict[str, Any] = field(default_factory=dict)
    impacted_keywords: List[Dict[str, Any]] = field(default_factory=list)
    opportunity_keywords: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    error: Optional[str] = None


class AIVisibilityInsightsService:
    """Analyze GSC data for AI Overview impact signals."""

    def __init__(self, gsc_service: GSCService):
        self.gsc_service = gsc_service

    def analyze(
        self,
        user_id: str,
        site_url: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        thresholds: Optional[AIOThresholds] = None,
    ) -> AIOVisibilityResult:
        """
        Analyze GSC data for AI Overview insights.

        Args:
            user_id: Clerk user ID
            site_url: Verified GSC site URL (e.g., "https://example.com/")
            start_date: ISO date string; defaults to 30 days ago
            end_date: ISO date string; defaults to today
            thresholds: Custom thresholds; uses defaults if omitted

        Returns:
            AIOVisibilityResult with summary, keyword lists, and recommendations
        """
        t = thresholds or AIOThresholds()
        result = AIOVisibilityResult()

        try:
            # Set date defaults
            if not end_date:
                end_date = datetime.now().strftime("%Y-%m-%d")
            if not start_date:
                start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

            logger.info(
                f"AIVisibility: analyzing {site_url} for user {user_id} "
                f"({start_date} to {end_date})"
            )

            # Fetch GSC search analytics
            analytics = self.gsc_service.get_search_analytics(
                user_id=user_id,
                site_url=site_url,
                start_date=start_date,
                end_date=end_date,
            )

            # Validate response
            error = analytics.get("error")
            if error:
                result.error = error
                return result

            query_data = analytics.get("query_data", {})
            rows = query_data.get("rows", [])
            if not rows:
                result.error = "No query data returned from GSC"
                return result

            # Parse and classify each keyword
            total_keywords = 0
            total_impressions = 0
            total_clicks = 0
            aio_impressions = 0
            aio_estimated_clicks = 0
            impact_count = 0
            opportunity_count = 0

            impacted_list = []
            opportunity_list = []

            for row in rows:
                keys = row.get("keys", [])
                keyword = keys[0] if keys else "(not set)"
                impressions = row.get("impressions", 0)
                clicks = row.get("clicks", 0)
                ctr_decimal = row.get("ctr", 0)
                ctr_pct = round(ctr_decimal * 100, 2)
                position = round(row.get("position", 0), 1)

                total_keywords += 1
                total_impressions += impressions
                total_clicks += clicks

                entry = {
                    "keyword": keyword,
                    "impressions": impressions,
                    "clicks": clicks,
                    "ctr": ctr_pct,
                    "position": position,
                }

                # AIO Impacted: high impressions, top position, very low CTR
                if (
                    impressions >= t.impacted_min_impressions
                    and position <= t.impacted_max_position
                    and ctr_pct <= t.impacted_max_ctr
                ):
                    # Estimate what clicks WOULD be at a healthy top-3 CTR (~8%)
                    target_ctr = 8.0
                    expected_clicks = int(impressions * target_ctr / 100)
                    traffic_loss = max(0, expected_clicks - clicks)

                    entry["estimated_traffic_loss"] = traffic_loss
                    entry["target_ctr"] = target_ctr
                    entry["aio_impacted"] = True
                    impacted_list.append(entry)
                    aio_impressions += impressions
                    aio_estimated_clicks += traffic_loss
                    impact_count += 1

                # AIO Opportunity: good CTR, position 4-10 — strong enough to target AIO citation
                if (
                    impressions >= t.opportunity_min_impressions
                    and t.opportunity_min_position <= position <= t.opportunity_max_position
                    and ctr_pct >= t.opportunity_min_ctr
                ):
                    entry["aio_opportunity"] = True
                    entry["recommendation"] = self._suggest_aio_format(keyword, position, ctr_pct)
                    opportunity_list.append(entry)
                    opportunity_count += 1

            # Sort by impact/opportunity
            impacted_list.sort(key=lambda x: x.get("estimated_traffic_loss", 0), reverse=True)
            opportunity_list.sort(key=lambda x: x["impressions"], reverse=True)

            # Compute summary
            avg_ctr = round((total_clicks / total_impressions * 100) if total_impressions else 0, 2)
            avg_position = (
                round(
                    sum(r.get("position", 0) for r in rows) / len(rows), 1
                )
                if rows
                else 0
            )

            result.summary = {
                "total_keywords_analyzed": total_keywords,
                "total_impressions": total_impressions,
                "total_clicks": total_clicks,
                "average_ctr": avg_ctr,
                "average_position": avg_position,
                "aio_impacted_keywords": impact_count,
                "aio_opportunity_keywords": opportunity_count,
                "aio_zero_click_impressions": aio_impressions,
                "aio_estimated_traffic_loss": aio_estimated_clicks,
                "date_range": {"start": start_date, "end": end_date},
                "thresholds_used": {
                    "impacted": {
                        "min_impressions": t.impacted_min_impressions,
                        "max_position": t.impacted_max_position,
                        "max_ctr": t.impacted_max_ctr,
                    },
                    "opportunity": {
                        "min_impressions": t.opportunity_min_impressions,
                        "min_position": t.opportunity_min_position,
                        "max_position": t.opportunity_max_position,
                        "min_ctr": t.opportunity_min_ctr,
                    },
                },
            }

            # Build recommendations
            result.recommendations = self._build_recommendations(
                impacted_list, opportunity_list, result.summary
            )

            result.impacted_keywords = impacted_list[:20]
            result.opportunity_keywords = opportunity_list[:20]

            logger.info(
                f"AIVisibility: analysis complete for {site_url} — "
                f"{impact_count} impacted, {opportunity_count} opportunities"
            )

        except Exception as e:
            logger.error(f"AIVisibility: analysis error for {user_id}: {e}")
            result.error = str(e)

        return result

    @staticmethod
    def _suggest_aio_format(keyword: str, position: float, ctr: float) -> str:
        """Suggest content format for AIO optimization based on keyword pattern."""
        kw_lower = keyword.lower()

        if any(w in kw_lower for w in ["how", "steps", "guide", "tutorial", "way to"]):
            return "Create a step-by-step guide with clear numbered lists for AIO citation"
        if any(w in kw_lower for w in ["what", "define", "meaning", "explain", "overview"]):
            return "Add a concise definition/summary block at the top of the article"
        if any(w in kw_lower for w in ["vs", "versus", "difference", "comparison", "or"]):
            return "Use a structured comparison table — AI crawlers favor tabular data"
        if any(w in kw_lower for w in ["best", "top", "recommended", "review"]):
            return "Format as a ranked list with bullet-point pros/cons for AI snippet extraction"
        if any(w in kw_lower for w in ["why", "reason", "cause", "benefit"]):
            return "Include a bullet-point summary of key reasons/benefits for AIO extraction"
        if any(w in kw_lower for w in ["price", "cost", "pricing", "cheap", "affordable"]):
            return "Add a pricing/comparison table — highly structured data for AI citation"
        if any(w in kw_lower for w in ["example", "sample", "template", "checklist"]):
            return "Provide actionable examples or a downloadable template checklist"

        if position <= 3 and ctr < 3:
            return "Optimize content with FAQ schema and concise summary paragraphs to reclaim AIO clicks"
        if position <= 5:
            return "Add structured data markup (FAQ, HowTo) and a TL;DR box for AI Overview targeting"
        return "Improve content depth with data-backed insights and structured formatting for AI snippet eligibility"

    @staticmethod
    def _build_recommendations(
        impacted: List[Dict[str, Any]],
        opportunities: List[Dict[str, Any]],
        summary: Dict[str, Any],
    ) -> List[str]:
        """Generate AI Overview optimization recommendations."""
        recs = []
        impacted_count = summary.get("aio_impacted_keywords", 0)
        opportunity_count = summary.get("aio_opportunity_keywords", 0)
        traffic_loss = summary.get("aio_estimated_traffic_loss", 0)

        if impacted_count > 0:
            recs.append(
                f"⚠️ {impacted_count} keyword(s) show AI Overview impact signals "
                f"(estimated {traffic_loss} lost clicks). "
                "Add concise, structured summary blocks early in your content to reclaim visibility."
            )
        if opportunity_count > 0:
            recs.append(
                f"✅ {opportunity_count} keyword(s) are strong AIO optimization candidates. "
                "Apply FAQ schema, HowTo schema, and clear bullet-point summaries."
            )
        if impacted_count == 0 and opportunity_count == 0:
            recs.append(
                "No clear AI Overview signals detected. "
                "Consider expanding your keyword coverage in conversational/intent-based queries."
            )

        recs.append(
            "General AIO best practices: "
            "1) Use FAQ schema for question-based queries, "
            "2) Add <table> elements for comparative data, "
            "3) Keep key takeaways in the first 100 words, "
            "4) Use descriptive headings (H2/H3) that mirror natural language queries."
        )

        return recs
