"""Deep website scraper for backlink outreach discovery.

Orchestrates Exa neural search + DuckDuckGo fallback to find guest-post
opportunities with full-page content extraction and quality scoring.
"""

from __future__ import annotations

import asyncio
import re
import time
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from loguru import logger


class BacklinkOutreachScraper:
    """Scrapes websites for backlink outreach opportunities using Exa + DuckDuckGo."""

    GUEST_POST_KEYWORDS = [
        "write for us", "guest post", "submit guest post",
        "guest contributor", "become a guest blogger", "guest bloggers wanted",
        "add guest post", "submit article", "guest post opportunities",
        "contribute to our blog", "write for our blog",
    ]

    def __init__(self, user_id: Optional[str] = None):
        self.user_id = user_id
        self._exa_svc = None

    # -- Public API --

    async def deep_discover(
        self, keyword: str, max_results: int = 15
    ) -> Dict[str, Any]:
        """Discover guest-post opportunities using Exa, falling back to DuckDuckGo."""
        if self._is_exa_available():
            logger.info(f"[BacklinkScraper] Using Exa for keyword: {keyword}")
            return await self._discover_with_exa(keyword, max_results)
        logger.info(f"[BacklinkScraper] Exa unavailable, falling back to DuckDuckGo for: {keyword}")
        return await self._discover_with_duckduckgo(keyword, max_results)

    def scrape_urls(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Fetch full page content for a list of URLs using Exa get_contents."""
        exa = self._get_exa_sdk()
        if not exa:
            return self._scrape_urls_fallback(urls)
        try:
            result = exa.get_contents(urls, text={"max_characters": 5000})
            return self._parse_get_contents_result(result)
        except Exception as e:
            logger.warning(f"[BacklinkScraper] Exa get_contents failed: {e}")
            return self._scrape_urls_fallback(urls)

    # -- Availability --

    def _is_exa_available(self) -> bool:
        try:
            exa = self._get_exa_sdk()
            return exa is not None
        except Exception:
            return False

    def _get_exa_sdk(self):
        """Get Exa SDK instance via ExaService, respecting per-user API key."""
        if self._exa_svc is None:
            from services.research.exa_service import ExaService
            self._exa_svc = ExaService()
        self._exa_svc._try_initialize()
        return self._exa_svc.exa if self._exa_svc.enabled else None

    # -- Preflight & Usage Tracking --

    def _preflight_subscription_check(self, user_id: str) -> bool:
        """Check Exa usage limits. Returns True if allowed."""
        if not user_id:
            return True
        try:
            from services.database import get_session_for_user
            from services.subscription import PricingService
            from models.subscription_models import APIProvider
            db = get_session_for_user(user_id)
            if not db:
                return True
            try:
                pricing = PricingService(db)
                allowed, _, _ = pricing.check_usage_limits(
                    user_id=user_id, provider=APIProvider.EXA, tokens_requested=0,
                )
                return allowed
            finally:
                db.close()
        except Exception as e:
            logger.warning(f"[BacklinkScraper] Preflight check failed: {e}")
            return True

    def _track_exa_usage(self, user_id: str, cost: float = 0.005):
        """Record Exa usage after successful search."""
        if not user_id:
            return
        try:
            from services.database import get_session_for_user
            from services.subscription import PricingService
            from sqlalchemy import text as sql_text
            db = get_session_for_user(user_id)
            if not db:
                return
            try:
                pricing = PricingService(db)
                period = pricing.get_current_billing_period(user_id)
                db.execute(sql_text("""
                    UPDATE usage_summaries
                    SET exa_calls = COALESCE(exa_calls, 0) + 1,
                        exa_cost = COALESCE(exa_cost, 0) + :cost,
                        total_calls = total_calls + 1,
                        total_cost = total_cost + :cost
                    WHERE user_id = :user_id AND billing_period = :period
                """), {"cost": cost, "user_id": user_id, "period": period})
                db.commit()
            finally:
                db.close()
        except Exception as e:
            logger.warning(f"[BacklinkScraper] Usage tracking failed: {e}")

    # -- Exa Discovery --

    async def _discover_with_exa(self, keyword: str, max_results: int) -> Dict[str, Any]:
        exa = self._get_exa_sdk()
        if not exa:
            return await self._discover_with_duckduckgo(keyword, max_results)

        queries = self._generate_search_queries(keyword)
        dedup: Dict[str, Dict[str, Any]] = {}
        results_per_query = max(1, max_results // len(queries))

        for query in queries[:4]:
            rows = await self._exa_search_and_contents(exa, query, results_per_query)
            for row in rows:
                norm_url = self._normalize_url(row.get("url", ""))
                if not norm_url or norm_url in dedup:
                    continue
                dedup[norm_url] = row
            if len(dedup) >= max_results:
                break

        opportunities = self._build_enriched_opportunities(dedup, keyword, "exa")
        self._track_exa_usage(self.user_id)

        return {
            "keyword": keyword,
            "source": "exa",
            "total_found": len(opportunities),
            "opportunities": opportunities,
        }

    async def _exa_search_and_contents(
        self, exa, query: str, num_results: int
    ) -> List[Dict[str, Any]]:
        """Run Exa search_and_contents in executor to avoid blocking."""
        loop = asyncio.get_running_loop()
        try:
            result = await loop.run_in_executor(
                None,
                lambda: exa.search_and_contents(
                    query,
                    type="auto",
                    num_results=num_results,
                    text={"max_characters": 3000},
                    highlights={"num_sentences": 3, "highlights_per_url": 3},
                ),
            )
            return self._parse_search_and_contents_result(result)
        except Exception as e:
            logger.warning(f"[BacklinkScraper] Exa search_and_contents failed: {e}")
            return []

    def _parse_search_and_contents_result(self, result) -> List[Dict[str, Any]]:
        rows = []
        results = getattr(result, "results", [])
        for r in results:
            rows.append({
                "url": getattr(r, "url", ""),
                "title": getattr(r, "title", ""),
                "text": getattr(r, "text", ""),
                "highlights": getattr(r, "highlights", []),
                "summary": getattr(r, "summary", ""),
                "score": getattr(r, "score", 0.5),
                "published_date": getattr(r, "publishedDate", None),
            })
        return rows

    def _parse_get_contents_result(self, result) -> List[Dict[str, Any]]:
        rows = []
        results = getattr(result, "results", [])
        for r in results:
            rows.append({
                "url": getattr(r, "url", ""),
                "title": getattr(r, "title", ""),
                "text": getattr(r, "text", ""),
                "highlights": getattr(r, "highlights", []),
                "summary": getattr(r, "summary", ""),
            })
        return rows

    # -- DuckDuckGo Fallback Discovery --

    async def _discover_with_duckduckgo(self, keyword: str, max_results: int) -> Dict[str, Any]:
        queries = self._generate_search_queries(keyword)
        dedup: Dict[str, Dict[str, Any]] = {}

        for query in queries[:4]:
            rows = self._duckduckgo_search(query)
            for row in rows:
                norm_url = self._normalize_url(row.get("url", ""))
                if not norm_url or norm_url in dedup:
                    continue
                dedup[norm_url] = row
            if len(dedup) >= max_results:
                break
            time.sleep(0.4)

        # Scrape discovered URLs with Exa get_contents (or fallback)
        urls_to_scrape = list(dedup.keys())[:max_results]
        scraped = self.scrape_urls(urls_to_scrape)
        scraped_map = {self._normalize_url(s.get("url", "")): s for s in scraped}

        # Merge DDG results with scraped content
        merged = {}
        for norm_url, ddg_row in dedup.items():
            full = scraped_map.get(norm_url, {})
            merged[norm_url] = {
                "url": norm_url,
                "title": full.get("title") or ddg_row.get("title", ""),
                "text": full.get("text", ""),
                "highlights": full.get("highlights", ddg_row.get("highlights", [])),
                "summary": full.get("summary", ddg_row.get("snippet", "")),
                "snippet": ddg_row.get("snippet", ""),
                "score": 0.5,
            }

        opportunities = self._build_enriched_opportunities(merged, keyword, "duckduckgo")

        return {
            "keyword": keyword,
            "source": "duckduckgo",
            "total_found": len(opportunities),
            "opportunities": opportunities,
        }

    def _duckduckgo_search(self, query: str, retries: int = 2) -> List[Dict[str, Any]]:
        encoded = requests.utils.quote(query)
        url = f"https://duckduckgo.com/html/?q={encoded}"
        headers = {"User-Agent": "Mozilla/5.0 ALwrityBacklinkBot/1.0"}
        for attempt in range(retries + 1):
            try:
                resp = requests.get(url, headers=headers, timeout=12)
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, "html.parser")
                results = []
                for result in soup.select("div.result")[:10]:
                    anchor = result.select_one("a.result__a")
                    snippet_el = result.select_one("a.result__snippet") or result.select_one("div.result__snippet")
                    if not anchor or not anchor.get("href"):
                        continue
                    results.append({
                        "url": anchor.get("href"),
                        "title": anchor.get_text(strip=True),
                        "snippet": snippet_el.get_text(" ", strip=True) if snippet_el else "",
                        "highlights": [],
                    })
                return results
            except Exception:
                if attempt == retries:
                    return []
                time.sleep(0.6 * (attempt + 1))
        return []

    def _scrape_urls_fallback(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Basic HTTP scrape when Exa is unavailable."""
        results = []
        headers = {"User-Agent": "Mozilla/5.0 ALwrityBacklinkBot/1.0"}
        for url in urls[:5]:
            try:
                resp = requests.get(url, headers=headers, timeout=15)
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, "html.parser")
                for tag in soup(["script", "style", "nav", "footer", "header"]):
                    tag.decompose()
                text = soup.get_text(separator=" ", strip=True)
                title = soup.title.get_text(strip=True) if soup.title else ""
                results.append({"url": url, "title": title, "text": text[:5000], "highlights": [], "summary": ""})
            except Exception:
                continue
        return results

    # -- Enrichment Pipeline --

    def _build_enriched_opportunities(
        self, dedup: Dict[str, Dict[str, Any]], keyword: str, source: str
    ) -> List[Dict[str, Any]]:
        opportunities = []
        for norm_url, row in dedup.items():
            text = row.get("text", "")
            title = row.get("title", row.get("snippet", ""))
            quality = self._score_quality(text, title)
            contacts = self._extract_contacts(text)
            domain = self._extract_domain(norm_url)
            has_guidelines = self._check_guest_post_signals(text)

            opportunities.append({
                "url": norm_url,
                "domain": domain,
                "page_title": title,
                "snippet": row.get("snippet") or (text[:300] if text else ""),
                "full_text": text[:5000],
                "email": contacts.get("email"),
                "contact_page": contacts.get("contact_page"),
                "confidence_score": min(1.0, quality + 0.1),
                "quality_score": quality,
                "word_count": len(text.split()),
                "has_guest_post_guidelines": has_guidelines,
                "discovery_source": source,
            })
        opportunities.sort(key=lambda x: x["quality_score"], reverse=True)
        return opportunities

    def _extract_domain(self, url: str) -> str:
        try:
            return urlparse(url).netloc
        except Exception:
            return url

    def _normalize_url(self, url: str) -> str:
        u = (url or "").strip().strip("`")
        if not u:
            return ""
        if u.startswith("//"):
            u = f"https:{u}"
        if not re.match(r"^https?://", u):
            return ""
        return u.split("#")[0].rstrip("/")

    def _extract_contacts(self, text: str) -> Dict[str, Optional[str]]:
        result: Dict[str, Optional[str]] = {"email": None, "contact_page": None}
        if not text:
            return result
        email_match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
        if email_match:
            result["email"] = email_match.group(0)
        contact_match = re.search(
            r"(https?://[^\s\"'<>]*(?:contact|about|team|write-for-us|guest-post)[^\s\"'<>]*)",
            text, re.IGNORECASE,
        )
        if contact_match:
            result["contact_page"] = contact_match.group(1).rstrip("/")
        return result

    def _score_quality(self, text: str, title: str) -> float:
        score = 0.3
        words = text.split()
        wc = len(words)
        if wc > 2000:
            score += 0.3
        elif wc > 800:
            score += 0.2
        elif wc > 200:
            score += 0.1
        hay = f"{title} {text[:2000]}".lower()
        cues_found = sum(1 for cue in self.GUEST_POST_KEYWORDS if cue in hay)
        score += min(0.3, cues_found * 0.06)
        spam_signals = [
            r"buy\s+links?" in hay, r"cheap\s+backlinks?" in hay,
            r"pbn" in hay, r"private\s+blog\s+network" in hay,
        ]
        if any(spam_signals):
            score -= 0.3
        return max(0.0, min(1.0, score))

    def _check_guest_post_signals(self, text: str) -> bool:
        if not text:
            return False
        hay = text.lower()
        guidelines = [
            "guest post guidelines", "submission guidelines",
            "write for us", "guest post", "submit a guest post",
            "guest contributor guidelines", "contributor guidelines",
        ]
        return any(g in hay for g in guidelines)

    def _generate_search_queries(self, keyword: str) -> List[str]:
        kw = (keyword or "").strip()
        if not kw:
            return []
        return [
            f"{kw} write for us",
            f"{kw} guest post",
            f"{kw} submit guest post",
            f"{kw} guest contributor",
            f"{kw} become a guest blogger",
            f"{kw} add guest post",
            f"{kw} guest post opportunities",
            f"{kw} submit article",
        ]
