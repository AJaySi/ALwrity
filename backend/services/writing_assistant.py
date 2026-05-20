import os
import asyncio
from typing import Any, Dict, List
from dataclasses import dataclass
from loguru import logger
import random

from services.llm_providers.main_text_generation import llm_text_gen


@dataclass
class WritingSuggestion:
    text: str
    confidence: float
    sources: List[Dict[str, Any]]


class WritingAssistantService:
    """
    Minimal writing assistant that combines Exa search with Gemini continuation.
    - Exa provides relevant sources with content snippets
    - Gemini generates a short, cited continuation based on current text and sources
    """

    def __init__(self) -> None:
        # COST CONTROL: Daily usage limits
        self.daily_api_calls = 0
        self.daily_limit = 50  # Max 50 API calls per day (~$2.50 max cost)
        self.last_reset_date = None

    def _get_cached_suggestion(self, text: str) -> WritingSuggestion | None:
        """No cached suggestions - always use real API calls for authentic results."""
        return None

    def _check_daily_limit(self) -> bool:
        """Check if we're within daily API usage limits."""
        import datetime
        
        today = datetime.date.today()
        
        # Reset counter if it's a new day
        if self.last_reset_date != today:
            self.daily_api_calls = 0
            self.last_reset_date = today
        
        # Check if we've exceeded the limit
        if self.daily_api_calls >= self.daily_limit:
            return False
        
        # Increment counter for this API call
        self.daily_api_calls += 1
        logger.info(f"Writing assistant API call #{self.daily_api_calls}/{self.daily_limit} today")
        return True

    async def suggest(self, text: str, user_id: str | None = None) -> List[WritingSuggestion]:
        if not text or len(text.strip()) < 6:
            return []

        cached_suggestion = self._get_cached_suggestion(text)
        if cached_suggestion:
            return [cached_suggestion]

        if not self._check_daily_limit():
            logger.warning("Daily API limit reached for writing assistant")
            return []

        if len(text.strip()) < 50:
            return []

        # 1) Find relevant sources via Exa
        sources = await self._search_sources(text, user_id=user_id)

        # 2) Generate continuation suggestion via LLM grounded in sources
        suggestion_text, confidence = await self._generate_continuation(text, sources, user_id=user_id)

        if not suggestion_text:
            return []

        return [WritingSuggestion(text=suggestion_text.strip(), confidence=confidence, sources=sources)]

    async def _search_sources(self, text: str, user_id: str = None) -> List[Dict[str, Any]]:
        """Search for relevant sources using ExaResearchProvider with subscription checks."""
        try:
            from services.blog_writer.research.exa_provider import ExaResearchProvider

            exa_query = (
                (text[-1000:] if len(text) > 1000 else text)
                + "\n\nIf you found the above interesting, here's another useful resource to read:"
            )

            provider = ExaResearchProvider()
            sources = await provider.simple_search(
                query=exa_query,
                num_results=3,
                user_id=user_id,
            )

            # Normalize keys to match expected format
            normalized = []
            for s in sources:
                normalized.append({
                    "title": s.get("title", "Untitled"),
                    "url": s.get("url", ""),
                    "text": s.get("text", ""),
                    "author": s.get("author", ""),
                    "published_date": s.get("publishedDate", ""),
                    "score": float(s.get("score", 0.5)),
                })

            if not normalized:
                raise Exception("No relevant sources found from Exa for the current context")
            return normalized
        except Exception as e:
            logger.error(f"WritingAssistant _search_sources error: {e}")
            raise

    async def _generate_continuation(self, text: str, sources: List[Dict[str, Any]], user_id: str | None = None) -> tuple[str, float]:
        source_blocks: List[str] = []
        for i, s in enumerate(sources[:5]):
            excerpt = (s.get("text", "") or "")
            excerpt = excerpt[:500]
            source_blocks.append(
                f"Source {i+1}: {s.get('title','') or 'Source'}\nURL: {s.get('url','')}\nExcerpt: {excerpt}"
            )
        sources_text = "\n\n".join(source_blocks)

        system_prompt = (
            "You are an assistive writing continuation bot. "
            "Only produce 1-2 SHORT sentences. Do not repeat or paraphrase the user's stub. "
            "Match tone and topic. Prefer concrete, current facts from the provided sources. "
            "Include exactly one brief citation hint in parentheses with an author (or 'Source') and URL in square brackets, e.g., ((Doe, 2021)[https://example.com])."
        )
        user_prompt = (
            f"User text to continue (do not repeat):\n{text}\n\n"
            f"Relevant sources to inform your continuation:\n{sources_text}\n\n"
            "Return only the continuation text, without quotes."
        )

        try:
            await asyncio.sleep(random.uniform(0.05, 0.15))

            ai_resp = llm_text_gen(
                prompt=user_prompt,
                json_struct=None,
                system_prompt=system_prompt,
                user_id=user_id,
            )
            if isinstance(ai_resp, dict) and ai_resp.get("text"):
                suggestion = (ai_resp.get("text", "") or "").strip()
            else:
                suggestion = (str(ai_resp or "")).strip()
            if not suggestion:
                raise Exception("Assistive writer returned empty suggestion")
            confidence = 0.7
            return suggestion, confidence
        except Exception as e:
            logger.error(f"WritingAssistant _generate_continuation error: {e}")
            raise


