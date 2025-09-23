"""
EnhancedContentGenerator - thin orchestrator combining URL selection and Gemini provider.

Provides Draft vs Polished modes and optional URL Context usage.
"""

from typing import Any, Dict

from services.llm_providers.gemini_grounded_provider import GeminiGroundedProvider
from .source_url_manager import SourceURLManager
from .context_memory import ContextMemory
from .transition_generator import TransitionGenerator
from .flow_analyzer import FlowAnalyzer


class EnhancedContentGenerator:
    def __init__(self):
        self.provider = GeminiGroundedProvider()
        self.url_manager = SourceURLManager()
        self.memory = ContextMemory(max_entries=12)
        self.transitioner = TransitionGenerator()
        self.flow = FlowAnalyzer()

    async def generate_section(self, section: Any, research: Any, mode: str = "polished") -> Dict[str, Any]:
        urls = self.url_manager.pick_relevant_urls(section, research)
        prev_summary = self.memory.build_previous_sections_summary(limit=2)
        prompt = self._build_prompt(section, research, prev_summary)
        result = await self.provider.generate_grounded_content(
            prompt=prompt,
            content_type="linkedin_article",
            temperature=0.6 if mode == "polished" else 0.8,
            max_tokens=2048,
            urls=urls,
            mode=mode,
        )
        # Generate transition and compute intelligent flow metrics
        previous_text = prev_summary
        current_text = result.get("content", "")
        transition = self.transitioner.generate_transition(previous_text, getattr(section, 'heading', 'This section'), use_llm=True)
        metrics = self.flow.assess_flow(previous_text, current_text, use_llm=True)

        # Update memory for subsequent sections and store continuity snapshot
        if current_text:
            self.memory.update_with_section(getattr(section, 'id', 'unknown'), current_text, use_llm=True)

        # Return enriched result
        result["transition"] = transition
        result["continuity_metrics"] = metrics
        # Persist a lightweight continuity snapshot for API access
        try:
            sid = getattr(section, 'id', 'unknown')
            if not hasattr(self, "_last_continuity"):
                self._last_continuity = {}
            self._last_continuity[sid] = metrics
        except Exception:
            pass
        return result

    def _build_prompt(self, section: Any, research: Any, prev_summary: str) -> str:
        heading = getattr(section, 'heading', 'Section')
        key_points = getattr(section, 'key_points', [])
        keywords = getattr(section, 'keywords', [])
        target_words = getattr(section, 'target_words', 300)

        return (
            f"You are writing the blog section '{heading}'.\n\n"
            f"Context summary: {prev_summary}\n"
            f"Key points: {', '.join(key_points)}\n"
            f"Keywords: {', '.join(keywords)}\n"
            f"Target word count: {target_words}.\n"
            "Use only factual info from provided sources; add short transition, then body."
        )


