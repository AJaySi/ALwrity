"""GSC task report service for onboarding step-5 and SEO dashboard sections."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from loguru import logger

from services.gsc_service import GSCService


class GSCTaskReportService:
    """Builds report payloads for issue 1-4 task sections."""

    GOOGLE_QUERY_TEMPLATES = [
        'site:{domain} "{query}"',
        'site:{domain} intitle:"{query}"',
        'site:{domain} inurl:{topic}',
        '"{query}" site:{competitor}',
        'intitle:"{query}" "{competitor}"',
        'related:{domain}',
        'site:{domain} -inurl:tag -inurl:category "{query}"'
    ]

    def __init__(self):
        self.gsc_service = GSCService()

    def _get_site_url(self, user_id: str, site_url: Optional[str]) -> Optional[str]:
        if site_url:
            return site_url
        sites = self.gsc_service.get_site_list(user_id)
        if not sites:
            return None
        return sites[0].get("siteUrl")

    def _fetch_query_rows(self, user_id: str, site_url: str, days: int = 30) -> List[Dict[str, Any]]:
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        return self._fetch_query_rows_range(user_id, site_url, start_date, end_date)

    def _fetch_query_rows_range(
        self,
        user_id: str,
        site_url: str,
        start_date: str,
        end_date: str,
    ) -> List[Dict[str, Any]]:
        data = self.gsc_service.get_search_analytics(
            user_id=user_id,
            site_url=site_url,
            start_date=start_date,
            end_date=end_date,
        )
        return data.get("query_data", {}).get("rows", [])

    def _high_impression_low_ctr(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        opportunities: List[Dict[str, Any]] = []
        for row in rows:
            keys = row.get("keys", [])
            query = keys[0] if keys else None
            impressions = float(row.get("impressions", 0) or 0)
            ctr = float(row.get("ctr", 0) or 0)
            position = float(row.get("position", 0) or 0)
            if query and impressions >= 100 and ctr < 0.03 and 1 <= position <= 20:
                opportunities.append({
                    "query": query,
                    "impressions": int(impressions),
                    "clicks": int(float(row.get("clicks", 0) or 0)),
                    "ctr": round(ctr * 100, 2),
                    "position": round(position, 2),
                    "recommended_action": "Rewrite title/meta + align H1 intro to intent",
                })
        return sorted(opportunities, key=lambda x: x["impressions"], reverse=True)[:10]

    def _decay_summary(self, current: List[Dict[str, Any]], previous: List[Dict[str, Any]]) -> Dict[str, Any]:
        current_map = {((r.get("keys") or [None])[0]): r for r in current if r.get("keys")}
        previous_map = {((r.get("keys") or [None])[0]): r for r in previous if r.get("keys")}
        decayed = 0
        samples = []
        for query, row in current_map.items():
            if not query or query not in previous_map:
                continue
            curr_clicks = float(row.get("clicks", 0) or 0)
            prev_clicks = float(previous_map[query].get("clicks", 0) or 0)
            curr_ctr = float(row.get("ctr", 0) or 0)
            prev_ctr = float(previous_map[query].get("ctr", 0) or 0)
            curr_pos = float(row.get("position", 0) or 0)
            prev_pos = float(previous_map[query].get("position", 0) or 0)
            if prev_clicks > 0 and (curr_clicks < prev_clicks * 0.8 or curr_ctr < prev_ctr - 0.01 or curr_pos > prev_pos + 1):
                decayed += 1
                samples.append({
                    "query": query,
                    "clicks_delta_pct": round(((curr_clicks - prev_clicks) / prev_clicks) * 100, 2),
                    "ctr_delta_pp": round((curr_ctr - prev_ctr) * 100, 2),
                    "position_delta": round(curr_pos - prev_pos, 2),
                })
        return {"decayed_queries": decayed, "samples": samples[:8]}

    def build_task_report(self, user_id: str, site_url: Optional[str] = None) -> Dict[str, Any]:
        selected_site = self._get_site_url(user_id, site_url)
        if not selected_site:
            return {
                "connected": False,
                "site_url": site_url,
                "message": "No GSC site connected",
                "sections": [],
                "google_query_templates": self.GOOGLE_QUERY_TEMPLATES,
            }

        # Compare two equivalent windows: current 30d vs previous 30d.
        current_end = datetime.now().date()
        current_start = current_end - timedelta(days=30)
        prev_end = current_start
        prev_start = prev_end - timedelta(days=30)

        rows_30d = self._fetch_query_rows_range(
            user_id,
            selected_site,
            current_start.strftime('%Y-%m-%d'),
            current_end.strftime('%Y-%m-%d'),
        )
        rows_prev_30d = self._fetch_query_rows_range(
            user_id,
            selected_site,
            prev_start.strftime('%Y-%m-%d'),
            prev_end.strftime('%Y-%m-%d'),
        )

        issue1 = self._high_impression_low_ctr(rows_30d)
        issue2 = self._decay_summary(rows_30d, rows_prev_30d)

        sections = [
            {
                "issue_key": "issue_1",
                "title": "Keyword-to-brief opportunities",
                "description": "High impression / low CTR queries to refresh titles/meta/outlines.",
                "metrics": {
                    "opportunities_count": len(issue1),
                    "top_impression": issue1[0]["impressions"] if issue1 else 0,
                },
                "items": issue1,
            },
            {
                "issue_key": "issue_2",
                "title": "Intent-aware refresh queue",
                "description": "Weekly decayed queries and recommended rewrites.",
                "metrics": {
                    "decayed_queries": issue2["decayed_queries"],
                    "sample_count": len(issue2["samples"]),
                },
                "items": issue2["samples"],
            },
            {
                "issue_key": "issue_3",
                "title": "Property-aware publishing guardrails",
                "description": "Publishing guidance requires GSC + CMS integrations.",
                "metrics": {
                    "guardrails_enabled": True,
                    "required_integrations": ["gsc", "wordpress_or_wix"],
                },
                "items": [],
            },
            {
                "issue_key": "issue_4",
                "title": "Google query monitoring templates",
                "description": "Exact Google query templates for SERP checks and AI report prompts.",
                "metrics": {
                    "templates_count": len(self.GOOGLE_QUERY_TEMPLATES),
                },
                "items": [{"query_template": q} for q in self.GOOGLE_QUERY_TEMPLATES],
            },
        ]

        return {
            "connected": True,
            "site_url": selected_site,
            "generated_at": datetime.utcnow().isoformat(),
            "sections": sections,
            "google_query_templates": self.GOOGLE_QUERY_TEMPLATES,
        }

    def run_single_task(self, user_id: str, task_key: str, site_url: Optional[str] = None) -> Dict[str, Any]:
        report = self.build_task_report(user_id, site_url)
        sections = report.get("sections", [])
        selected = next((s for s in sections if s.get("issue_key") == task_key), None)
        if not selected:
            return {"success": False, "error": f"Unknown task key: {task_key}"}
        logger.info("[GSCTaskReportService] run_single_task user={} task={}", user_id, task_key)
        return {
            "success": True,
            "task_key": task_key,
            "site_url": report.get("site_url"),
            "result": selected,
            "generated_at": report.get("generated_at"),
        }
