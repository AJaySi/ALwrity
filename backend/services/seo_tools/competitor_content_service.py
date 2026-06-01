"""
Competitor Content Service for ALwrity

Fetches full competitor content for gap topics using Exa with include_domains.
Phase 2 of the Content Gap Radar feature.

Usage:
    service = CompetitorContentService()
    result = await service.deep_dive(
        topics=["AI content strategy"],
        competitor_domains=["example.com"]
    )
"""

import os
import asyncio
import hashlib
import json
import time
from typing import Dict, List, Optional, Any
from loguru import logger


class CompetitorContentService:
    """
    Fetches competitor content for gap topics using Exa neural search.

    Uses Exa's `include_domains` to scope searches to known competitor domains,
    returning full text, highlights, and summaries for deeper competitive analysis.
    Results are cached for 24h to reduce API costs.
    Designed to be consumed by the future ContentGapRadarAgent.
    """

    CACHE_TTL = int(os.getenv("COMPETITOR_CONTENT_CACHE_TTL", "86400"))

    def __init__(self):
        self.api_key = os.getenv("EXA_API_KEY")
        if not self.api_key:
            logger.warning(
                "EXA_API_KEY not configured; CompetitorContentService disabled"
            )
        self._exa = None
        self._cache: Dict[str, Dict[str, Any]] = {}

    @property
    def exa(self):
        """Lazy-init Exa SDK to allow env injection after import."""
        if self._exa is None and self.api_key:
            from exa_py import Exa
            self._exa = Exa(self.api_key)
        return self._exa

    def _cache_key(self, topics: List[str], domains: List[str]) -> str:
        raw = json.dumps(
            {"t": sorted(topics), "d": sorted(domains)}, sort_keys=True
        )
        return hashlib.md5(raw.encode()).hexdigest()

    def _get_cached(self, key: str) -> Optional[Dict[str, Any]]:
        entry = self._cache.get(key)
        if entry and (time.time() - entry["ts"]) < self.CACHE_TTL:
            return entry["data"]
        return None

    def _set_cache(self, key: str, data: Dict[str, Any]):
        self._cache[key] = {"data": data, "ts": time.time()}

    async def deep_dive(
        self,
        topics: List[str],
        competitor_domains: List[str],
        max_total_results: int = 10,
        concurrency: int = 3,
        bypass_cache: bool = False,
    ) -> Dict[str, Any]:
        """
        Fetch competitor content for a list of gap topics.

        For each topic, searches Exa scoped to competitor domains and returns
        full text, highlights, and publishing metadata.

        Args:
            topics: Topic phrases to research (e.g. from SERP gap analysis)
            competitor_domains: Known competitor domains to scope search
            max_total_results: Max results per topic total (Exa API limit varies)
            concurrency: Max concurrent Exa API calls
            bypass_cache: Force fresh API calls, ignoring cache

        Returns:
            Dict with keys:
                results: List of per-topic competitor content results
                total_topics_analyzed: int
                topics_with_content: int
                cached: bool
        """
        if not topics or not competitor_domains:
            return {
                "results": [],
                "total_topics_analyzed": 0,
                "topics_with_content": 0,
                "cached": False,
            }

        ck = self._cache_key(topics, competitor_domains)
        if not bypass_cache:
            cached = self._get_cached(ck)
            if cached:
                logger.info("Returning cached competitor content results")
                return {**cached, "cached": True}

        if not self.api_key or not self.exa:
            return {
                "results": [],
                "total_topics_analyzed": len(topics),
                "topics_with_content": 0,
                "cached": False,
                "error": "EXA_API_KEY not configured",
            }

        semaphore = asyncio.Semaphore(concurrency)
        loop = asyncio.get_running_loop()

        async def search_topic(topic: str) -> Dict[str, Any]:
            async with semaphore:
                return await self._search_single_topic(
                    topic, competitor_domains, max_total_results, loop
                )

        tasks = [search_topic(topic) for topic in topics]
        results = await asyncio.gather(*tasks)

        output = {
            "results": results,
            "total_topics_analyzed": len(topics),
            "topics_with_content": sum(
                1 for r in results if r.get("total_results", 0) > 0
            ),
            "cached": False,
        }
        self._set_cache(ck, output)
        return output

    async def _search_single_topic(
        self,
        topic: str,
        competitor_domains: List[str],
        max_results: int,
        loop: asyncio.AbstractEventLoop,
    ) -> Dict[str, Any]:
        """
        Search Exa for a single topic, scoped to competitor domains.
        """
        query = topic

        search_kwargs = {
            "type": "auto",
            "num_results": max_results,
            "include_domains": competitor_domains,
            "text": {"max_characters": 2000},
            "highlights": {"num_sentences": 3, "highlights_per_url": 3},
            "summary": {"query": f"Key details about {topic}"},
        }

        try:
            results = await loop.run_in_executor(
                None,
                lambda: self.exa.search_and_contents(query, **search_kwargs),
            )

            content = []
            seen_urls = set()
            for result in getattr(results, "results", []) or []:
                url = getattr(result, "url", "")
                if not url or url in seen_urls:
                    continue
                seen_urls.add(url)
                content.append({
                    "domain": self._extract_domain(url),
                    "title": getattr(result, "title", "Untitled"),
                    "url": url,
                    "highlights": getattr(result, "highlights", []),
                    "summary": getattr(result, "summary", ""),
                    "text": getattr(result, "text", ""),
                    "published_date": getattr(result, "published_date", None),
                    "author": getattr(result, "author", None),
                })

            return {
                "topic": topic,
                "competitor_content": content,
                "total_results": len(content),
                "domains_found": list(
                    set(c["domain"] for c in content if c["domain"])
                ),
            }

        except Exception as e:
            logger.warning(f"Exa search failed for topic '{topic}': {e}")
            return {
                "topic": topic,
                "competitor_content": [],
                "total_results": 0,
                "domains_found": [],
                "error": str(e),
            }

    @staticmethod
    def _extract_domain(url: str) -> str:
        """Extract domain from URL."""
        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc.lower()
        except Exception:
            return url.lower()
