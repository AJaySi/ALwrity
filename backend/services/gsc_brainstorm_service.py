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

        # 4. Score keywords for topic relevance and filter to topic-related subset
        logger.info(f"Filtering {len(keywords_data)} GSC keywords for topic relevance to: '{keywords}'")
        keywords_data, pages_data = self._filter_by_topic_relevance(
            keywords_data, pages_data, keywords
        )
        logger.info(f"After topic filter: {len(keywords_data)} keywords, {len(pages_data)} pages")

        if not keywords_data:
            return {
                "error": "No GSC keywords matched your topic. Try a broader research topic or check your GSC data.",
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

        # 5. Compute threshold multiplier based on available topic keywords
        #    When topic filtering yields fewer keywords, lower impression thresholds
        #    to surface more topic-relevant opportunities.
        filtered_count = len(keywords_data)
        threshold_multiplier = max(0.1, filtered_count / 200.0)
        logger.info(f"Threshold multiplier: {threshold_multiplier:.2f} ({filtered_count} topic keywords)")

        # 6. Rule-based analysis with adjusted thresholds
        content_opportunities = self._identify_content_opportunities(keywords_data, threshold_multiplier)
        keyword_gaps = self._identify_keyword_gaps(keywords_data, threshold_multiplier)
        quick_wins = self._identify_quick_wins(keywords_data, threshold_multiplier)
        page_opportunities = self._identify_page_opportunities(pages_data, threshold_multiplier)

        # 7. Summary metrics
        summary = self._compute_summary(keywords_data, pages_data, site_url, start_date, end_date)

        # 8. AI recommendations
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
    #  Topic relevance scoring and filtering
    # ------------------------------------------------------------------ #

    _semantic_model = None  # class-level cache for sentence-transformers

    @staticmethod
    def _compute_semantic_scores(
        keywords_data: List[Dict[str, Any]],
        user_keywords: str,
    ) -> Dict[int, float]:
        """Compute cosine similarity between embedding of each GSC keyword and user topic.

        Uses sentence-transformers (all-MiniLM-L6-v2) for lightweight semantic matching.
        Returns dict mapping keyword index to similarity score (0-1), or empty on failure.
        """
        try:
            import numpy as np
            from sentence_transformers import SentenceTransformer

            model = GSCBrainstormService._semantic_model
            if model is None:
                logger.info("Loading semantic embedding model (all-MiniLM-L6-v2)...")
                model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")
                GSCBrainstormService._semantic_model = model

            texts, indices = [], []
            for i, kw in enumerate(keywords_data):
                text = kw.get("keyword", "")
                if text.strip():
                    texts.append(text)
                    indices.append(i)

            if not texts:
                return {}

            all_texts = [user_keywords] + texts
            embeddings = model.encode(all_texts, show_progress_bar=False, convert_to_numpy=True)

            user_emb = embeddings[0]
            kw_embs = embeddings[1:]

            norms = np.linalg.norm(kw_embs, axis=1)
            user_norm = np.linalg.norm(user_emb)
            similarities = np.dot(kw_embs, user_emb) / (norms * user_norm + 1e-8)

            return dict(zip(indices, [float(s) for s in similarities]))
        except Exception as e:
            logger.warning(f"Semantic similarity scoring unavailable, falling back to term-only: {e}")
            return {}

    @staticmethod
    def _tokenize(text: str) -> set:
        """Lowercase and split into individual meaningful tokens."""
        import re
        tokens = re.findall(r"[a-zA-Z0-9]+", text.lower())
        return {t for t in tokens if len(t) >= 3}

    @staticmethod
    def _score_keyword_relevance(gsc_keyword: str, user_tokens: set, user_phrase: str) -> float:
        """Score a single GSC keyword for relevance to the user's topic tokens."""
        kw_lower = gsc_keyword.lower()
        # Exact phrase match → highest score
        if user_phrase.lower() in kw_lower:
            return 1.0
        score = 0.0
        kw_tokens = GSCBrainstormService._tokenize(gsc_keyword)
        if not kw_tokens:
            return 0.0
        # Count overlapping tokens
        matches = user_tokens & kw_tokens
        score += len(matches) * 0.5
        # Partial/substring matches for remaining user tokens
        for ut in user_tokens:
            if ut not in matches:
                if ut in kw_lower:
                    score += 0.2
        # Normalize by max possible score (capped at 1.0)
        return min(score, 1.0)

    def _filter_by_topic_relevance(
        self,
        keywords_data: List[Dict[str, Any]],
        pages_data: List[Dict[str, Any]],
        user_keywords: str,
    ) -> tuple:
        """Score GSC keywords for topic overlap and keep the most relevant subset.

        Returns (filtered_keywords, filtered_pages) where filtered_keywords
        includes topic-relevant keywords + top-performer fallbacks.
        """
        if not user_keywords or not user_keywords.strip():
            return keywords_data, pages_data

        user_tokens = self._tokenize(user_keywords)
        if not user_tokens:
            return keywords_data, pages_data

        # Compute semantic similarity scores (catches synonyms, e.g. "plant-based protein" for "vegan")
        semantic_scores = GSCBrainstormService._compute_semantic_scores(keywords_data, user_keywords)
        semantic_available = bool(semantic_scores)

        # Score every keyword: blend term overlap (50%) + semantic similarity (50%)
        scored = []
        for i, kw in enumerate(keywords_data):
            term_score = self._score_keyword_relevance(
                kw.get("keyword", ""), user_tokens, user_keywords
            )
            if semantic_available:
                sem_score = semantic_scores.get(i, 0.0)
                blended = 0.5 * term_score + 0.5 * sem_score
            else:
                blended = term_score  # fallback to term-only
            kw["_relevance"] = blended
            scored.append(kw)

        # Sort by blended relevance desc, then impressions desc
        scored.sort(key=lambda x: (-x["_relevance"], -x.get("impressions", 0)))

        # Take top 150 by relevance
        top_relevant = [k for k in scored if k["_relevance"] > 0][:150]

        # Also keep top 50 by impressions as fallback (ensures general site context)
        by_impressions = sorted(
            scored, key=lambda x: -x.get("impressions", 0)
        )[:50]

        # Merge and deduplicate by keyword
        seen = set()
        merged = []
        for kw in top_relevant + by_impressions:
            key = kw.get("keyword", "")
            if key not in seen:
                seen.add(key)
                merged.append(kw)

        # Remove internal score key from results
        for kw in merged:
            kw.pop("_relevance", None)

        logger.info(
            f"Topic relevance: {len(scored)} scored, "
            f"{len(top_relevant)} topic-relevant, "
            f"{len(merged)} after merge with top-by-impressions"
        )

        # Filter pages: keep pages whose URL contains any topic-relevant keyword
        relevant_keywords_lower = {kw.get("keyword", "").lower() for kw in merged if kw.get("keyword")}
        filtered_pages = []
        for pg in pages_data:
            page_url = pg.get("page", "").lower()
            # Keep page if any filtered keyword appears in the URL
            if any(kw in page_url for kw in relevant_keywords_lower):
                filtered_pages.append(pg)

        # Always keep at least top 20 pages by impressions for context
        pages_by_imp = sorted(pages_data, key=lambda x: -x.get("impressions", 0))[:20]
        seen_page_urls = {p.get("page", "") for p in filtered_pages}
        for pg in pages_by_imp:
            if pg.get("page", "") not in seen_page_urls:
                filtered_pages.append(pg)

        return merged, filtered_pages

    # ------------------------------------------------------------------ #
    #  Rule-based opportunity identification
    # ------------------------------------------------------------------ #

    @staticmethod
    def _identify_content_opportunities(
        keywords_data: List[Dict[str, Any]],
        threshold_multiplier: float = 1.0,
    ) -> List[Dict[str, Any]]:
        opportunities: List[Dict[str, Any]] = []

        _imp_high = int(500 * threshold_multiplier)
        _imp_impact_high = int(1000 * threshold_multiplier)
        _imp_enhance = int(100 * threshold_multiplier)
        _imp_enhance_high = int(500 * threshold_multiplier)

        # Rule 1: Content Optimization — high impressions, low CTR
        for kw in keywords_data:
            if kw["impressions"] > _imp_high and kw["ctr"] < 3:
                estimated_gain = int(kw["impressions"] * 0.05) - kw["clicks"]
                opportunities.append({
                    "type": "Content Optimization",
                    "keyword": kw["keyword"],
                    "opportunity": (
                        f"Your site appears for '{kw['keyword']}' ({kw['impressions']:,} times/month) "
                        f"but only {kw['ctr']:.1f}% click. Improving your title and meta description "
                        f"could bring ~{max(estimated_gain, 5)} more clicks/month."
                    ),
                    "potential_impact": "High" if kw["impressions"] > _imp_impact_high else "Medium",
                    "current_position": kw["position"],
                    "current_ctr": kw["ctr"],
                    "impressions": kw["impressions"],
                    "clicks": kw["clicks"],
                    "estimated_traffic_gain": max(estimated_gain, 5),
                    "priority": "High" if kw["impressions"] > _imp_impact_high else "Medium",
                    "suggested_format": GSCBrainstormService._suggest_format(kw["keyword"]),
                })

        # Rule 2: Content Enhancement — positions 11-20 with decent impressions
        for kw in keywords_data:
            if 10 < kw["position"] <= 20 and kw["impressions"] > _imp_enhance:
                estimated_gain = int(kw["impressions"] * 0.08)
                opportunities.append({
                    "type": "Content Enhancement",
                    "keyword": kw["keyword"],
                    "opportunity": (
                        f"'{kw['keyword']}' ranks #{kw['position']:.0f} (page 2). "
                        f"Moving to page 1 could capture ~{estimated_gain} more clicks/month "
                        f"from {kw['impressions']:,} impressions."
                    ),
                    "potential_impact": "High" if kw["impressions"] > _imp_enhance_high else "Medium",
                    "current_position": kw["position"],
                    "current_ctr": kw["ctr"],
                    "impressions": kw["impressions"],
                    "clicks": kw["clicks"],
                    "estimated_traffic_gain": estimated_gain,
                    "priority": "High" if kw["impressions"] > _imp_enhance_high else "Medium",
                    "suggested_format": GSCBrainstormService._suggest_format(kw["keyword"]),
                })

        opportunities.sort(key=lambda x: x["impressions"], reverse=True)
        return opportunities[:10]

    @staticmethod
    def _identify_keyword_gaps(
        keywords_data: List[Dict[str, Any]],
        threshold_multiplier: float = 1.0,
    ) -> List[Dict[str, Any]]:
        gaps: List[Dict[str, Any]] = []
        _imp_min = int(50 * threshold_multiplier)

        for kw in keywords_data:
            if 4 <= kw["position"] <= 20 and kw["impressions"] >= _imp_min:
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
        threshold_multiplier: float = 1.0,
    ) -> List[Dict[str, Any]]:
        quick_wins: List[Dict[str, Any]] = []
        _imp_min = int(100 * threshold_multiplier)

        for kw in keywords_data:
            if 4 <= kw["position"] <= 10 and kw["impressions"] >= _imp_min:
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
        threshold_multiplier: float = 1.0,
    ) -> List[Dict[str, Any]]:
        opportunities: List[Dict[str, Any]] = []
        _imp_min = int(300 * threshold_multiplier)

        for pg in pages_data:
            if pg["impressions"] > _imp_min and pg["ctr"] < 2.0:
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
            # Build topic-relevant keyword list from filtered keywords_data
            topic_keywords = sorted(
                keywords_data,
                key=lambda x: (x.get("impressions", 0) * max(1, 11 - min(x.get("position", 10), 10))),
                reverse=True
            )[:25]
            topic_kw_str = "\n".join(
                f"  • {kw['keyword']}: {kw['impressions']:,} impressions, position {kw['position']}, {kw['ctr']:.1f}% CTR"
                for kw in topic_keywords
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

Here is their GSC data for the last 30 days, already filtered to keywords related to their topic:

PERFORMANCE OVERVIEW:
- Total Topic-Relevant Keywords: {summary.get('total_keywords_analyzed', 0)}
- Total Impressions (topic): {summary.get('total_impressions', 0):,}
- Total Clicks (topic): {summary.get('total_clicks', 0):,}
- Average CTR: {summary.get('avg_ctr', 0):.2f}% (industry avg for positions 1-10 is ~3.1%)
- Average Position: {summary.get('avg_position', 0):.1f}
- SEO Health Score: {summary.get('health_score', 0)}/100

TOPIC-RELEVANT KEYWORDS (sorted by potential impact):
{topic_kw_str}

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
- Use the KEYWORD DATA above to justify each recommendation — reference specific keywords, their impressions, positions, and CTR
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