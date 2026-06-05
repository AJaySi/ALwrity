"""
Keyword Curator - Smart keyword selection engine for SEO-optimized outline generation.

Instead of dumping all discovered keywords into the LLM prompt (which causes
keyword stuffing and dilutes topical focus), this module selects a highly
curated subset based on SEO best practices and assigns each keyword a
specific structural role in the outline.
"""

from typing import Dict, Any, List, Optional


class KeywordCurator:
    """
    Curates a strict, minimal keyword set for outline generation.
    
    Selection Rules (SEO Best Practice):
    1. Primary (H1 Focus)   → top 2 — brand name + core topic
    2. Secondary (H2 Focus) → top 2 — feature/benefit anchors
    3. Long-tail (H3 Focus) → top 2 — informational intent phrases
    4. Semantic (Body Context) → top 4 — prevent topical drift
    5. Trending (Mention)   → top 2 — brief contextual mentions
    6. Content Gap (Edge)   → top 1 — competitive differentiator
    """

    # How many keywords to select from each category
    SLOTS: Dict[str, int] = {
        "primary": 2,
        "secondary": 2,
        "long_tail": 2,
        "semantic": 4,
        "trending": 2,
        "content_gap": 1,
    }

    def curate(
        self,
        keyword_analysis: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Apply selection rules and return a structured, minimal keyword payload.
        
        Args:
            keyword_analysis: Raw keyword_analysis dict from research
                             (keys: primary, secondary, long_tail,
                              semantic_keywords, trending_terms, content_gaps, ...)
        
        Returns:
            Dict with curated keyword groups plus all other analysis fields preserved.
        """
        curated: Dict[str, Any] = {}

        # --- Select from keyword lists ---
        curated["primary"] = self._pick(keyword_analysis, "primary")
        curated["secondary"] = self._pick(keyword_analysis, "secondary")
        curated["long_tail"] = self._pick(keyword_analysis, "long_tail")

        # semantic_keywords is the actual key in the research data
        curated["semantic"] = self._pick(keyword_analysis, "semantic_keywords", slot_key="semantic")
        curated["trending"] = self._pick(keyword_analysis, "trending_terms", slot_key="trending")
        curated["content_gap"] = self._pick(keyword_analysis, "content_gaps", slot_key="content_gap")

        # --- Build a flat "locked" set for quick reference ---
        locked: List[str] = []
        for group in curated.values():
            if isinstance(group, list):
                locked.extend(group)
        curated["locked_keywords"] = locked

        # --- Track counts for transparency ---
        total_raw = 0
        total_curated = 0
        for source_key, limit in self.SLOTS.items():
            raw_key = self._source_key(source_key)
            raw_list = keyword_analysis.get(raw_key, [])
            total_raw += len(raw_list) if isinstance(raw_list, list) else 0
            curated_list = curated.get(source_key, [])
            total_curated += len(curated_list) if isinstance(curated_list, list) else 0
        curated["stats"] = {
            "total_raw": total_raw,
            "total_curated": total_curated,
            "reduction_pct": round((1 - total_curated / max(total_raw, 1)) * 100, 1),
        }

        # --- Preserve non-keyword analysis fields ---
        for field in ("search_intent", "difficulty", "analysis_insights"):
            if field in keyword_analysis:
                curated[field] = keyword_analysis[field]

        return curated

    def format_for_prompt(self, curated: Dict[str, Any]) -> str:
        """
        Format the curated keyword payload into a strict structural prompt section.
        
        Returns a string ready to be injected into the outline prompt.
        """
        lines: List[str] = []
        lines.append("## KEYWORD PLACEMENT DIRECTIVES\n")

        # H1 — primary
        primary = curated.get("primary", [])
        if primary:
            h1_text = " | ".join(primary)
            lines.append(f"### H1 (must contain, in order of priority): {h1_text}")
            lines.append("   → Anchor the title and main heading on these terms.")
        else:
            lines.append("### H1: No primary keywords provided — derive from topic context.")

        # H2 — secondary
        secondary = curated.get("secondary", [])
        if secondary:
            lines.append(f"### H2 sections must anchor on (one per major section): {', '.join(secondary)}")
            lines.append("   → Each secondary keyword should map to a distinct H2 section.")

        # H3 — long-tail
        long_tail = curated.get("long_tail", [])
        if long_tail:
            lines.append(f"### H3 / Subsection anchors for informational intent: {', '.join(long_tail)}")
            lines.append("   → Use these as deeper-dive subsections under the relevant H2.")

        # Body-level — semantic
        semantic = curated.get("semantic", [])
        if semantic:
            lines.append(f"### Body-level semantic signals (use naturally, max 1-2 mentions each): {', '.join(semantic)}")
            lines.append("   → These prevent topical drift. Weave into paragraph text, not headings.")

        # Trending — brief
        trending = curated.get("trending", [])
        if trending:
            lines.append(f"### Trending context (mention subtly if relevant): {', '.join(trending)}")
            lines.append("   → Optional. Only include if it strengthens timeliness/narrative.")

        # Content gap — competitive edge
        content_gap = curated.get("content_gap", [])
        if content_gap:
            lines.append(f"### Competitive advantage signal (must weave into narrative): {content_gap[0]}")
            lines.append("   → This is your primary differentiation hook. Surface it prominently in the unique value section.")

        lines.append("")
        lines.append("### SUGGESTED SECTION → KEYWORD MAPPING")
        lines.append("Map each outline section's keyword focus according to its narrative role:")
        lines.append("- Hook / Introduction → lead with primary and trending keywords for timeliness & relevance")
        lines.append("- Problem / Pain Point → anchor on secondary and long-tail keywords (informational intent)")
        lines.append("- Solution / How-To → weave in primary and secondary keywords for solution-oriented search")
        lines.append("- Comparison / Analysis → embed semantic keywords to prevent topical drift into tangents")
        lines.append("- Case Studies / Evidence → surface content gap keywords as differentiation proof points")
        lines.append("- Future / Trends → leverage trending and content gap keywords for forward-looking authority")
        lines.append("")
        lines.append("GUIDELINE: Treat these as the primary keyword anchors. You may include closely related")
        lines.append("intent-matching variations where natural, but avoid inserting every raw research keyword.")
        lines.append("Quality over density — each keyword earns its place by serving a clear structural purpose.")

        stats = curated.get("stats", {})
        if stats:
            lines.append(
                f"\n[From {stats.get('total_raw', '?')} raw research keywords "
                f"→ curated to {stats.get('total_curated', '?')} locked keywords "
                f"({stats.get('reduction_pct', '?')}% reduction)]"
            )

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _source_key(slot_key: str) -> str:
        """Map internal slot key to the actual field name in keyword_analysis."""
        mapping = {
            "primary": "primary",
            "secondary": "secondary",
            "long_tail": "long_tail",
            "semantic": "semantic_keywords",
            "trending": "trending_terms",
            "content_gap": "content_gaps",
        }
        return mapping.get(slot_key, slot_key)

    def _pick(
        self,
        data: Dict[str, Any],
        source_key: str,
        slot_key: Optional[str] = None,
    ) -> List[str]:
        """
        Pick up to N items from a keyword list with diversity sampling.
        
        When the raw list is significantly larger than the limit, selects
        evenly-spaced entries to capture semantic diversity rather than
        just the first N entries.
        
        Args:
            data: The raw keyword_analysis dict.
            source_key: The actual key in the dict (e.g. 'semantic_keywords').
            slot_key: The internal slot name for looking up the limit.
                      Falls back to source_key if not provided.
        Returns:
            List of at most N strings with diversity sampling.
        """
        limit_key = slot_key or source_key
        limit = self.SLOTS.get(limit_key, 5)
        raw: Any = data.get(source_key, [])
        if not isinstance(raw, list):
            return []
        if len(raw) <= limit:
            return raw
        if len(raw) <= limit * 2:
            return raw[:limit]
        indices = set()
        if limit >= 2:
            indices.add(0)
            indices.add(len(raw) - 1)
            step = (len(raw) - 1) / max(limit - 1, 1)
            for i in range(1, limit - 1):
                indices.add(int(round(i * step)))
        else:
            indices.add(0)
        return [raw[i] for i in sorted(indices) if i < len(raw)][:limit]
