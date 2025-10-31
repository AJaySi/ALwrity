"""
EnhancedContentGenerator - thin orchestrator for section generation.

Provider parity:
- Uses main_text_generation.llm_text_gen to respect GPT_PROVIDER (Gemini/HF)
- No direct provider coupling here; Google grounding remains in research only
"""

from typing import Any, Dict

from services.llm_providers.main_text_generation import llm_text_gen
from .source_url_manager import SourceURLManager
from .context_memory import ContextMemory
from .transition_generator import TransitionGenerator
from .flow_analyzer import FlowAnalyzer


class EnhancedContentGenerator:
    def __init__(self):
        self.url_manager = SourceURLManager()
        self.memory = ContextMemory(max_entries=12)
        self.transitioner = TransitionGenerator()
        self.flow = FlowAnalyzer()

    async def generate_section(self, section: Any, research: Any, mode: str = "polished") -> Dict[str, Any]:
        prev_summary = self.memory.build_previous_sections_summary(limit=2)
        urls = self.url_manager.pick_relevant_urls(section, research)
        prompt = self._build_prompt(section, research, prev_summary, urls)
        # Provider-agnostic text generation (respect GPT_PROVIDER & circuit-breaker)
        content_text: str = ""
        try:
            ai_resp = llm_text_gen(
                prompt=prompt,
                json_struct=None,
                system_prompt=None,
            )
            if isinstance(ai_resp, dict) and ai_resp.get("text"):
                content_text = ai_resp.get("text", "")
            elif isinstance(ai_resp, str):
                content_text = ai_resp
            else:
                # Fallback best-effort extraction
                content_text = str(ai_resp or "")
        except Exception as e:
            content_text = ""

        result = {
            "content": content_text,
            "sources": [{"title": u.get("title", ""), "url": u.get("url", "")} for u in urls] if urls else [],
        }
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

    def _build_prompt(self, section: Any, research: Any, prev_summary: str, urls: list) -> str:
        heading = getattr(section, 'heading', 'Section')
        key_points = getattr(section, 'key_points', [])
        keywords = getattr(section, 'keywords', [])
        target_words = getattr(section, 'target_words', 300)
        url_block = "\n".join([f"- {u.get('title','')} ({u.get('url','')})" for u in urls]) if urls else "(no specific URLs provided)"

        return (
            f"You are writing the blog section '{heading}'.\n\n"
            f"Context summary (previous sections): {prev_summary}\n\n"
            f"Authoring requirements:\n"
            f"- Target word count: ~{target_words}\n"
            f"- Use the following key points: {', '.join(key_points)}\n"
            f"- Include these keywords naturally: {', '.join(keywords)}\n"
            f"- Cite insights from these sources when relevant (do not output raw URLs):\n{url_block}\n\n"
            "Write engaging, well-structured markdown with clear paragraphs (2-4 sentences each) separated by double line breaks."
        )


