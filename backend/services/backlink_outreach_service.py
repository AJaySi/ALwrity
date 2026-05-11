"""Canonical backlink outreach service entrypoint."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List
import re
import time

import requests
from bs4 import BeautifulSoup

from services.backlink_outreach_models import OpportunityContactInfo, OpportunityRecord, PolicyValidationRequest, PolicyValidationResponse




# Temporary in-memory control plane until DB wiring is complete
SUPPRESSION_LIST = set()
SENT_IDEMPOTENCY_KEYS = set()
AUDIT_LOGS: list[dict] = []
SEND_COUNTERS_BY_USER: dict[str, int] = {}
SEND_COUNTERS_BY_DOMAIN: dict[str, int] = {}
DEFAULT_USER_DAILY_CAP = 100
DEFAULT_DOMAIN_DAILY_CAP = 20

@dataclass
class SearchResult:
    url: str
    title: str
    snippet: str


class BacklinkOutreachService:
    def list_backlink_modules(self) -> List[Dict[str, Any]]:
        return [
            {"identifier": "backlink", "module_path": "backend/services/backlink_outreach_service.py", "purpose": "Canonical backlink service facade"},
            {"identifier": "outreach", "module_path": "backend/routers/backlink_outreach.py", "purpose": "HTTP API entrypoint for backlink outreach"},
            {"identifier": "guest_post", "module_path": "frontend/src/api/backlinkOutreachApi.ts", "purpose": "Frontend API integration for guest-post workflows"},
        ]

    def generate_guest_post_queries(self, keyword: str) -> List[str]:
        normalized = (keyword or "").strip()
        if not normalized:
            return []
        return [
            f"{normalized} + 'Guest Contributor'",
            f"{normalized} + 'Add Guest Post'",
            f"{normalized} + 'Guest Bloggers Wanted'",
            f"{normalized} + 'Write for Us'",
            f"{normalized} + 'Submit Guest Post'",
            f"{normalized} + 'Become a Guest Blogger'",
            f"{normalized} + 'guest post opportunities'",
            f"{normalized} + 'Submit article'",
        ]

    def search_for_urls(self, query: str, timeout_seconds: int = 12, retries: int = 2) -> List[SearchResult]:
        encoded_query = requests.utils.quote(query)
        url = f"https://duckduckgo.com/html/?q={encoded_query}"
        headers = {"User-Agent": "Mozilla/5.0 ALwrityBacklinkBot/1.0"}

        for attempt in range(retries + 1):
            try:
                response = requests.get(url, headers=headers, timeout=timeout_seconds)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")
                rows: List[SearchResult] = []
                for result in soup.select("div.result")[:10]:
                    anchor = result.select_one("a.result__a")
                    snippet = result.select_one("a.result__snippet") or result.select_one("div.result__snippet")
                    if not anchor or not anchor.get("href"):
                        continue
                    rows.append(
                        SearchResult(
                            url=anchor.get("href"),
                            title=anchor.get_text(strip=True),
                            snippet=snippet.get_text(" ", strip=True) if snippet else "",
                        )
                    )
                return rows
            except Exception:
                if attempt == retries:
                    return []
                time.sleep(0.6 * (attempt + 1))
        return []

    def discover_opportunities(self, keyword: str, max_results: int = 10) -> Dict[str, Any]:
        queries = self.generate_guest_post_queries(keyword)[:4]
        dedup: Dict[str, SearchResult] = {}

        for query in queries:
            for result in self.search_for_urls(query):
                normalized_url = self._normalize_url(result.url)
                if not normalized_url or normalized_url in dedup:
                    continue
                dedup[normalized_url] = result
                if len(dedup) >= max_results:
                    break
            if len(dedup) >= max_results:
                break
            time.sleep(0.4)

        opportunities: List[OpportunityRecord] = []
        for normalized_url, row in dedup.items():
            contact = self._extract_contact_info(row.snippet)
            score = self._score_confidence(row.title, row.snippet)
            opportunities.append(
                OpportunityRecord(
                    url=normalized_url,
                    title=row.title or "Untitled",
                    snippet=row.snippet,
                    metadata={"source": "duckduckgo_html", "query_keyword": keyword},
                    contact_info=contact,
                    confidence_score=score,
                )
            )

        return {"keyword": keyword, "queries": queries, "opportunities": opportunities}

    def _normalize_url(self, url: str) -> str:
        u = (url or "").strip()
        if not u:
            return ""
        if u.startswith("//"):
            u = f"https:{u}"
        if not re.match(r"^https?://", u):
            return ""
        return u.split("#")[0].rstrip("/")

    def _extract_contact_info(self, text: str) -> OpportunityContactInfo:
        if not text:
            return OpportunityContactInfo()
        email_match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
        return OpportunityContactInfo(email=email_match.group(0) if email_match else None)

    def _score_confidence(self, title: str, snippet: str) -> float:
        hay = f"{title} {snippet}".lower()
        cues = ["write for us", "guest post", "submit", "contributor", "guest blogger"]
        hits = sum(1 for cue in cues if cue in hay)
        return min(1.0, 0.35 + (0.13 * hits))


    def validate_send_policy(self, payload: PolicyValidationRequest) -> PolicyValidationResponse:
        reasons: List[str] = []

        if payload.workspace_id.startswith("new-") and not payload.approved_by_human:
            reasons.append("human_review_required_for_new_workspace")
        if payload.legal_basis.lower() not in {"legitimate_interest", "consent", "contract"}:
            reasons.append("invalid_legal_basis")
        if payload.recipient_region.lower() in {"eu", "eea"} and payload.legal_basis.lower() != "consent":
            reasons.append("region_requires_explicit_consent")
        if not payload.unsubscribe_url:
            reasons.append("unsubscribe_url_required")
        if len(payload.sender_identity.strip()) < 3:
            reasons.append("sender_identity_required")

        recipient_key = f"{payload.recipient_email.lower()}::{payload.recipient_domain.lower()}"
        if recipient_key in SUPPRESSION_LIST:
            reasons.append("recipient_suppressed")
        if payload.idempotency_key in SENT_IDEMPOTENCY_KEYS:
            reasons.append("duplicate_idempotency_key")

        user_count = SEND_COUNTERS_BY_USER.get(payload.user_id, 0)
        domain_count = SEND_COUNTERS_BY_DOMAIN.get(payload.recipient_domain.lower(), 0)
        if user_count >= DEFAULT_USER_DAILY_CAP:
            reasons.append("user_daily_cap_exceeded")
        if domain_count >= DEFAULT_DOMAIN_DAILY_CAP:
            reasons.append("domain_daily_cap_exceeded")

        allowed = len(reasons) == 0
        final_status = "approved" if allowed else "blocked"

        AUDIT_LOGS.append({
            "event": "policy_check",
            "user_id": payload.user_id,
            "campaign_id": payload.campaign_id,
            "recipient": str(payload.recipient_email),
            "allowed": allowed,
            "reasons": reasons,
            "override": payload.approved_by_human,
        })

        if allowed:
            SENT_IDEMPOTENCY_KEYS.add(payload.idempotency_key)
            SEND_COUNTERS_BY_USER[payload.user_id] = user_count + 1
            SEND_COUNTERS_BY_DOMAIN[payload.recipient_domain.lower()] = domain_count + 1

        return PolicyValidationResponse(allowed=allowed, reasons=reasons, final_status=final_status)

    def get_reporting_snapshot(self) -> Dict[str, Any]:
        total_decisions = len(AUDIT_LOGS)
        approved = sum(1 for row in AUDIT_LOGS if row.get("allowed"))
        return {
            "send_volume": approved,
            "decision_events": total_decisions,
            "response_rate": 0.0,
            "placement_conversion": 0.0,
        }

    def get_migration_coverage(self) -> Dict[str, Any]:
        implemented = [
            "discoverable backend router + service",
            "frontend API/store/UI integration point",
            "legacy guest-post search query generation templates",
            "provider-backed URL discovery + normalization + deduplication",
            "typed opportunity records and confidence score",
        ]
        planned = [
            "deep webpage scraping + contact-page extraction",
            "email sending automation + response tracking",
            "follow-up orchestration and campaign analytics",
        ]
        return {
            "legacy_reference": "ToBeMigrated/ai_marketing_tools/ai_backlinker/ai_backlinking.py",
            "implemented_count": len(implemented),
            "planned_count": len(planned),
            "implemented": implemented,
            "planned": planned,
        }


backlink_outreach_service = BacklinkOutreachService()
