"""Opportunity scoring helpers for search analytics data."""

from typing import Any, Dict, List


Opportunity = Dict[str, Any]
MetricRow = Dict[str, Any]


def high_impression_low_ctr_queries(
    query_rows: List[MetricRow],
    min_impressions: float = 100.0,
    max_ctr: float = 2.5,
) -> List[Opportunity]:
    """Return queries with strong impressions but weak CTR."""
    opportunities: List[Opportunity] = []
    for row in query_rows:
        current = row.get("current_metrics", {})
        impressions = float(current.get("impressions", 0) or 0)
        ctr = float(current.get("ctr", 0) or 0)
        if impressions < min_impressions or ctr > max_ctr:
            continue

        opportunities.append({
            "id": row.get("id") or f"q:{row.get('query', 'unknown')}",
            "query": row.get("query"),
            "page_url": row.get("page_url"),
            "reason": "high_impression_low_ctr_query",
            "score": 0.0,
            "current_metrics": current,
            "previous_metrics": row.get("previous_metrics", {}),
        })
    return opportunities


def rising_queries(
    query_rows: List[MetricRow],
    min_impression_delta: float = 50.0,
    min_click_delta: float = 5.0,
) -> List[Opportunity]:
    """Return query opportunities with positive window-over-window growth."""
    opportunities: List[Opportunity] = []
    for row in query_rows:
        current = row.get("current_metrics", {})
        previous = row.get("previous_metrics", {})
        delta_impressions = float(current.get("impressions", 0) or 0) - float(previous.get("impressions", 0) or 0)
        delta_clicks = float(current.get("clicks", 0) or 0) - float(previous.get("clicks", 0) or 0)
        if delta_impressions < min_impression_delta and delta_clicks < min_click_delta:
            continue

        opportunities.append({
            "id": row.get("id") or f"q:{row.get('query', 'unknown')}",
            "query": row.get("query"),
            "page_url": row.get("page_url"),
            "reason": "rising_query",
            "score": 0.0,
            "current_metrics": current,
            "previous_metrics": previous,
        })
    return opportunities


def declining_pages(
    page_rows: List[MetricRow],
    min_impression_drop: float = 50.0,
    min_click_drop: float = 5.0,
) -> List[Opportunity]:
    """Return page opportunities with negative window-over-window change."""
    opportunities: List[Opportunity] = []
    for row in page_rows:
        current = row.get("current_metrics", {})
        previous = row.get("previous_metrics", {})
        impression_drop = float(previous.get("impressions", 0) or 0) - float(current.get("impressions", 0) or 0)
        click_drop = float(previous.get("clicks", 0) or 0) - float(current.get("clicks", 0) or 0)
        if impression_drop < min_impression_drop and click_drop < min_click_drop:
            continue

        opportunities.append({
            "id": row.get("id") or f"p:{row.get('page_url', 'unknown')}",
            "query": row.get("query"),
            "page_url": row.get("page_url"),
            "reason": "declining_page",
            "score": 0.0,
            "current_metrics": current,
            "previous_metrics": previous,
        })
    return opportunities


def score_and_rank_opportunities(opportunities: List[Opportunity]) -> List[Opportunity]:
    """Assign simple priority score and return opportunities ordered by score."""
    scored: List[Opportunity] = []
    for item in opportunities:
        current = item.get("current_metrics", {})
        previous = item.get("previous_metrics", {})
        impressions = float(current.get("impressions", 0) or 0)
        clicks = float(current.get("clicks", 0) or 0)
        ctr = float(current.get("ctr", 0) or 0)

        previous_impressions = float(previous.get("impressions", 0) or 0)
        previous_clicks = float(previous.get("clicks", 0) or 0)
        momentum = abs(impressions - previous_impressions) + (abs(clicks - previous_clicks) * 10)

        opportunity_multiplier = {
            "high_impression_low_ctr_query": 1.2,
            "rising_query": 1.0,
            "declining_page": 1.3,
        }.get(item.get("reason"), 1.0)

        score = (impressions * 0.05) + (clicks * 0.8) + ((100.0 - ctr) * 0.1) + (momentum * 0.15)
        updated = dict(item)
        updated["score"] = round(score * opportunity_multiplier, 2)
        scored.append(updated)

    return sorted(scored, key=lambda x: (x.get("score", 0), str(x.get("id", ""))), reverse=True)


def categorize_opportunities(
    query_rows: List[MetricRow],
    page_rows: List[MetricRow],
) -> List[Opportunity]:
    """Build all opportunity categories and return a stable, ranked schema."""
    opportunities: List[Opportunity] = []
    opportunities.extend(high_impression_low_ctr_queries(query_rows))
    opportunities.extend(rising_queries(query_rows))
    opportunities.extend(declining_pages(page_rows))
    return score_and_rank_opportunities(opportunities)

