"""
SourceURLManager - selects the most relevant source URLs for a section.

Low-effort heuristic using keywords and titles; safe defaults if no research.
"""

from typing import List, Dict, Any


class SourceURLManager:
    def pick_relevant_urls(self, section: Any, research: Any, limit: int = 5) -> List[str]:
        if not research or not getattr(research, 'sources', None):
            return []

        section_keywords = set([k.lower() for k in getattr(section, 'keywords', [])])
        scored: List[tuple[float, str]] = []
        for s in research.sources:
            url = getattr(s, 'url', None) or getattr(s, 'uri', None) or s.get('url') if isinstance(s, dict) else None
            title = getattr(s, 'title', None) or s.get('title') if isinstance(s, dict) else ''
            if not url or not isinstance(url, str):
                continue
            title_l = (title or '').lower()
            # simple overlap score
            score = 0.0
            for kw in section_keywords:
                if kw and kw in title_l:
                    score += 1.0
            # prefer https and reputable domains lightly
            if url.startswith('https://'):
                score += 0.2
            scored.append((score, url))

        scored.sort(key=lambda x: x[0], reverse=True)
        dedup: List[str] = []
        for _, u in scored:
            if u not in dedup:
                dedup.append(u)
            if len(dedup) >= limit:
                break
        return dedup


