"""
Chart Service — Shared chart generation for Blog Writer, Podcast Maker, and future modules.

Extracts the chart rendering logic from podcast/broll_composer into a reusable service
that any module can call. Supports:
  - Direct chart rendering (caller provides chart_type + chart_data)
  - AI-driven chart inference (caller provides text, LLM infers chart_type + chart_data)

Chart types: bar_comparison, bar_horizontal, line_trend, pie, stacked_bar, bullet_points
"""

import uuid
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from loguru import logger

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont

from services.llm_providers.main_text_generation import llm_text_gen


CHART_STYLE = {
    "bg": "#0D0D0D",
    "bar_before": "#2E4057",
    "bar_after": "#E63946",
    "text": "#F1F1EF",
    "grid": "#2A2A2A",
    "accent": "#E63946",
    "pie_colors": ["#E63946", "#2E4057", "#457B9D", "#A8DADC", "#F4A261", "#2A9D8F"],
}

VALID_CHART_TYPES = [
    "bar_comparison", "bar_chart_comparison",
    "bar_horizontal", "line_trend",
    "pie", "stacked_bar",
    "bullet", "bullet_points",
]

CHART_INFERENCE_SYSTEM_PROMPT = """You are a data visualization expert. Given text content, determine the most appropriate chart type and extract structured data for rendering.

You MUST respond with ONLY a valid JSON object (no markdown, no explanation) with this exact structure:
{
  "chart_type": "one of: bar_comparison, bar_horizontal, line_trend, pie, stacked_bar, bullet_points",
  "chart_data": { ... appropriate data structure for the chart type ... },
  "title": "A clear, concise chart title"
}

Chart data structures by type:
- bar_comparison: {"labels": [...], "before": [...], "after": [...]} OR {"labels": [...], "values": [...]}
- bar_horizontal: {"labels": [...], "values": [...]}
- line_trend: {"labels": [...], "values": [...]}
- pie: {"labels": [...], "values": [...]}
- stacked_bar: {"labels": [...], "stacks": [[...], [...]]}
- bullet_points: {"bullet_points": [...]}

Rules:
1. Choose the chart type that best represents the information in the text.
2. Use bar_comparison for before/after comparisons.
3. Use line_trend for time-series or sequential data.
4. Use pie for proportional breakdowns of a whole.
5. Use bar_horizontal for rankings or comparisons.
6. Use bullet_points if the text is qualitative with no strong numeric data.
7. Extract realistic numeric values from the text when available.
8. If no data is extractable, use bullet_points and list key points.
9. Keep labels short (under 20 chars)."""


CHART_INFERENCE_USER_PROMPT = """Create a chart from this text:

{text}

Return ONLY the JSON object with chart_type, chart_data, and title."""


CHART_ANALYSIS_SYSTEM_PROMPT = """You are a data visualization analyst. Given text from a blog section, your job is to:
1. Determine whether the text contains enough specific numeric data to create a meaningful chart
2. If YES: explain what data is available and suggest a chart type
3. If NO: suggest 2-3 specific search queries that would find relevant statistics/data to create a chart for this topic

You MUST respond with ONLY a valid JSON object (no markdown, no explanation):
{
  "has_data": true/false,
  "data_description": "brief description of what data is available or why it's insufficient",
  "suggested_chart_type": "best chart type if has_data is true, otherwise null",
  "search_queries": ["query1", "query2", "query3"] // Empty array if has_data is true
}

Be optimistic — if there's ANY numeric claim, percentage, comparison, or trend in the text, set has_data to true.
Only set has_data to false if the text is purely qualitative with no numbers, percentages, comparisons, or trends."""


CHART_ANALYSIS_USER_PROMPT = """Analyze this text for chart potential:

Section: {section_heading}
{key_points_section}
Text: {text}

Determine if this text contains enough data for a chart, or suggest search queries to find the data."""


CHART_SYNTHESIS_SYSTEM_PROMPT = """You are a data visualization expert. You have been given:
1. Original text from a blog section
2. Research data found from web searches

Create a chart that visualizes the most interesting insight from the combination of the original text and research data.

You MUST respond with ONLY a valid JSON object (no markdown, no explanation) with this exact structure:
{
  "chart_type": "one of: bar_comparison, bar_horizontal, line_trend, pie, stacked_bar, bullet_points",
  "chart_data": { ... appropriate data structure ... },
  "title": "A clear, concise chart title",
  "source": "Brief source attribution"
}

Chart data structures by type:
- bar_comparison: {"labels": [...], "before": [...], "after": [...]} OR {"labels": [...], "values": [...]}
- bar_horizontal: {"labels": [...], "values": [...]}
- line_trend: {"labels": [...], "values": [...]}
- pie: {"labels": [...], "values": [...]}
- stacked_bar: {"labels": [...], "stacks": [[...], [...]]}
- bullet_points: {"bullet_points": [...]}

Rules:
1. Use the research data to create accurate, fact-based charts
2. Prefer bar_comparison for before/after or categorical comparisons
3. Prefer line_trend for trends over time
4. Prefer pie for market share or proportional breakdowns
5. Keep labels short (under 20 characters)
6. Use realistic values from the research — do NOT invent numbers
7. Always include a source attribution based on where the data came from
8. If the research doesn't contain useful numeric data, fall back to bullet_points with key insights"""


CHART_SYNTHESIS_USER_PROMPT = """Original text:
{text}

Research data found:
{research}

Create a chart that visualizes the most interesting data insight from the combination above."""


def _normalize_chart_type(chart_type: str) -> str:
    """Normalize chart type aliases."""
    mapping = {
        "bar_chart_comparison": "bar_comparison",
        "bullet": "bullet_points",
    }
    return mapping.get(chart_type, chart_type)


def _add_source_overlay(image_path: str, source: str) -> None:
    """Add a source attribution overlay to a chart image (in-place)."""
    if not source or not os.path.exists(image_path):
        return
    try:
        img = Image.open(image_path).convert("RGBA")
        draw = ImageDraw.Draw(img)
        source_text = f"Source: {source[:80]}"
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
        except (OSError, IOError):
            try:
                font = ImageFont.truetype("arial.ttf", 11)
            except (OSError, IOError):
                font = ImageFont.load_default()
        text_bbox = draw.textbbox((0, 0), source_text, font=font)
        text_w = text_bbox[2] - text_bbox[0]
        text_h = text_bbox[3] - text_bbox[1]
        x = img.width - text_w - 12
        y = img.height - text_h - 8
        draw.rectangle([x - 4, y - 2, x + text_w + 4, y + text_h + 2], fill=(0, 0, 0, 140))
        draw.text((x, y), source_text, fill=(200, 200, 200, 220), font=font)
        img.save(image_path)
    except Exception as e:
        logger.warning(f"[ChartService] Source overlay failed (non-fatal): {e}")


# ---------------------------------------------------------------------------
# Chart generators (Matplotlib → PNG with transparency)
# ---------------------------------------------------------------------------

def make_bar_chart(data: dict, out_path: str, title: str = "",
                  show_legend: bool = True, value_suffix: str = "%",
                  subtitle: str = "") -> str:
    labels = data.get("labels", [])
    before = data.get("before", [])
    after = data.get("after", [])

    fig, ax = plt.subplots(figsize=(8, 4.5), facecolor="none")
    ax.set_facecolor("none")

    if not before and not after:
        values = data.get("values", [])
        if values and labels:
            n = min(len(labels), len(values))
            labels = labels[:n]
            before = [0] * n
            after = values[:n]
            data = {**data, "labels": labels, "before": before, "after": after}

    x = np.arange(len(labels))
    w = 0.35
    bars_b = ax.bar(x - w / 2, before, w, color=CHART_STYLE["bar_before"],
                    label="Before", zorder=3, edgecolor="none")
    bars_a = ax.bar(x + w / 2, after, w, color=CHART_STYLE["bar_after"],
                    label="After", zorder=3, edgecolor="none")

    ax.set_xticks(x)
    ax.set_xticklabels(labels, color=CHART_STYLE["text"], fontsize=11)
    ax.tick_params(axis="y", colors=CHART_STYLE["text"])
    ax.spines[:].set_visible(False)
    ax.yaxis.grid(True, color=CHART_STYLE["grid"], linewidth=0.6, zorder=0)
    ax.set_axisbelow(True)

    for bar in [*bars_b, *bars_a]:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + 0.5, f"{h:.0f}{value_suffix}",
                ha="center", va="bottom", color=CHART_STYLE["text"], fontsize=9,
                fontweight="bold")

    if show_legend:
        ax.legend(frameon=False, labelcolor=CHART_STYLE["text"],
                   fontsize=10, loc="upper left")

    if title:
        ax.set_title(title, color=CHART_STYLE["text"], fontsize=13,
                     fontweight="bold", pad=12)
    if subtitle:
        fig.text(0.5, 0.02, subtitle, ha='center', color=CHART_STYLE["text"],
                 fontsize=10, style='italic')

    fig.tight_layout(pad=0.5, rect=(0, 0.03 if subtitle else 0, 1, 1))
    fig.savefig(out_path, dpi=150, transparent=True, bbox_inches="tight")
    plt.close(fig)
    return out_path


def make_horizontal_bar(data: dict, out_path: str, title: str = "",
                        value_suffix: str = "%", bar_color: str = None) -> str:
    labels = data.get("labels", [])
    values = data.get("values", data.get("y", []))

    if not values:
        return ""

    bar_color = bar_color or CHART_STYLE["bar_after"]

    fig, ax = plt.subplots(figsize=(8, 4.5), facecolor="none")
    ax.set_facecolor("none")

    y_pos = np.arange(len(labels))
    bars = ax.barh(y_pos, values, color=bar_color, zorder=3, edgecolor="none", height=0.6)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, color=CHART_STYLE["text"], fontsize=11)
    ax.tick_params(axis="x", colors=CHART_STYLE["text"])
    ax.spines[:].set_visible(False)
    ax.xaxis.grid(True, color=CHART_STYLE["grid"], linewidth=0.6, zorder=0)
    ax.set_axisbelow(True)
    ax.invert_yaxis()

    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax.text(width + 0.5, bar.get_y() + bar.get_height()/2, f"{width:.0f}{value_suffix}",
                ha="left", va="center", color=CHART_STYLE["text"], fontsize=10,
                fontweight="bold")

    if title:
        ax.set_title(title, color=CHART_STYLE["text"], fontsize=13,
                     fontweight="bold", pad=12)

    fig.tight_layout(pad=0.5)
    fig.savefig(out_path, dpi=150, transparent=True, bbox_inches="tight")
    plt.close(fig)
    return out_path


def make_pie_chart(data: dict, out_path: str, title: str = "",
                   show_labels: bool = True, show_percent: bool = True,
                   donut: bool = False) -> str:
    labels = data.get("labels", [])
    values = data.get("values", data.get("y", []))

    if not values:
        return ""

    colors = CHART_STYLE["pie_colors"][:len(values)]

    fig, ax = plt.subplots(figsize=(6, 4.5), facecolor="none")
    ax.set_facecolor("none")

    if donut:
        wedges, texts, autotexts = ax.pie(
            values, labels=labels if show_labels else None,
            colors=colors, autopct=lambda p: f'{p:.1f}%' if show_percent else '',
            startangle=90, pctdistance=0.75,
            wedgeprops=dict(width=0.5, edgecolor="none")
        )
    else:
        wedges, texts, autotexts = ax.pie(
            values, labels=labels if show_labels else None,
            colors=colors, autopct=lambda p: f'{p:.1f}%' if show_percent else '',
            startangle=90, pctdistance=0.8
        )

    for text in texts:
        text.set_color(CHART_STYLE["text"])
        text.set_fontsize(10)

    for autotext in autotexts:
        autotext.set_color(CHART_STYLE["text"])
        autotext.set_fontsize(9)
        autotext.set_fontweight("bold")

    if title:
        ax.set_title(title, color=CHART_STYLE["text"], fontsize=13,
                     fontweight="bold", pad=12)

    fig.tight_layout(pad=0.5)
    fig.savefig(out_path, dpi=150, transparent=True, bbox_inches="tight")
    plt.close(fig)
    return out_path


def make_stacked_bar(data: dict, out_path: str, title: str = "",
                     stack_labels: list = None) -> str:
    labels = data.get("labels", [])
    stacks = data.get("stacks", [])

    if not stacks or len(stacks) < 2:
        return ""

    stack_labels = stack_labels or [f"Series {i+1}" for i in range(len(stacks))]

    fig, ax = plt.subplots(figsize=(8, 4.5), facecolor="none")
    ax.set_facecolor("none")

    x = np.arange(len(labels))
    bottom = np.zeros(len(labels))
    colors = CHART_STYLE["pie_colors"][:len(stacks)]

    for i, stack in enumerate(stacks):
        bars = ax.bar(x, stack, 0.6, bottom=bottom, color=colors[i],
                      label=stack_labels[i], zorder=3, edgecolor="none")

        for j, bar in enumerate(bars):
            height = bar.get_height()
            if height > 5:
                ax.text(bar.get_x() + bar.get_width()/2,
                        bottom[j] + height/2,
                        f"{height:.0f}", ha="center", va="center",
                        color=CHART_STYLE["text"], fontsize=8, fontweight="bold")

        bottom = bottom + np.array(stack)

    ax.set_xticks(x)
    ax.set_xticklabels(labels, color=CHART_STYLE["text"], fontsize=11)
    ax.tick_params(axis="y", colors=CHART_STYLE["text"])
    ax.spines[:].set_visible(False)
    ax.legend(frameon=False, labelcolor=CHART_STYLE["text"], fontsize=9, loc="upper left")

    if title:
        ax.set_title(title, color=CHART_STYLE["text"], fontsize=13,
                     fontweight="bold", pad=12)

    fig.tight_layout(pad=0.5)
    fig.savefig(out_path, dpi=150, transparent=True, bbox_inches="tight")
    plt.close(fig)
    return out_path


def make_line_trend(data: dict, out_path: str, title: str = "") -> str:
    x_labels = data.get("labels", data.get("x", []))
    y_vals = data.get("values", data.get("y", []))

    if not x_labels or not y_vals:
        return ""

    fig, ax = plt.subplots(figsize=(8, 4.5), facecolor="none")
    ax.set_facecolor("none")

    try:
        x_vals = [float(v) for v in x_labels]
    except (ValueError, TypeError):
        x_vals = list(range(len(x_labels)))

    ax.plot(x_vals, y_vals, color=CHART_STYLE["accent"],
            linewidth=2.5, marker="o", markersize=7, zorder=3)
    ax.fill_between(x_vals, y_vals, alpha=0.12, color=CHART_STYLE["accent"])
    ax.spines[:].set_visible(False)
    ax.tick_params(colors=CHART_STYLE["text"])
    ax.yaxis.grid(True, color=CHART_STYLE["grid"], linewidth=0.6, zorder=0)

    try:
        x_labels_f = [float(v) for v in x_labels]
    except (ValueError, TypeError):
        ax.set_xticks(x_vals)
        ax.set_xticklabels(x_labels, color=CHART_STYLE["text"], fontsize=10)

    if title:
        ax.set_title(title, color=CHART_STYLE["text"], fontsize=13,
                     fontweight="bold", pad=12)
    fig.tight_layout(pad=0.5)
    fig.savefig(out_path, dpi=150, transparent=True, bbox_inches="tight")
    plt.close(fig)
    return out_path


def make_bullet_overlay(lines: list, out_path: str,
                        width: int = 900, font_size: int = 32) -> str:
    padding = 32
    line_h = font_size + 16
    img_h = padding * 2 + len(lines) * line_h + 12
    img = Image.new("RGBA", (width, img_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    draw.rounded_rectangle([0, 0, width - 1, img_h - 1],
                            radius=18, fill=(10, 10, 10, 185))

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                                  font_size)
    except OSError:
        font = ImageFont.load_default()

    y = padding
    for line in lines:
        draw.text((padding + 18, y), f"\u2022 {line}", font=font, fill=(241, 241, 239, 255))
        y += line_h

    img.save(out_path, format="PNG")
    return out_path


CHART_RENDERERS = {
    "bar_comparison": make_bar_chart,
    "bar_chart_comparison": make_bar_chart,
    "bar_horizontal": make_horizontal_bar,
    "line_trend": make_line_trend,
    "pie": make_pie_chart,
    "stacked_bar": make_stacked_bar,
    "bullet_points": make_bullet_overlay,
    "bullet": make_bullet_overlay,
}


class ChartService:
    """Shared chart generation service for all modules."""

    def __init__(self, output_dir: Optional[str] = None, user_id: Optional[str] = None):
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            self.output_dir = self._default_chart_dir(user_id)

        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"[ChartService] Initialized with output directory: {self.output_dir}")

    @staticmethod
    def _default_chart_dir(user_id: Optional[str] = None) -> Path:
        """Get default chart directory (workspace-aware if user_id provided)."""
        if user_id:
            try:
                from api.podcast.constants import get_podcast_media_dir
                return get_podcast_media_dir("chart", user_id, ensure_exists=True)
            except Exception:
                pass
        base = Path.home() / ".alwrity" / "charts"
        base.mkdir(parents=True, exist_ok=True)
        return base

    def get_output_path(self, filename: str) -> Path:
        return self.output_dir / filename

    def get_chart_preview_path(self, chart_id: str) -> Path:
        return self.get_output_path(f"chart_preview_{chart_id}.png")

    def generate_chart(
        self,
        chart_data: Dict[str, Any],
        chart_type: str = "bar_comparison",
        title: str = "",
        subtitle: str = "",
        chart_id: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        Generate a chart PNG and return metadata.

        Returns:
            {"path": str, "chart_id": str, "filename": str}
            Returns {"path": "", "chart_id": str, "filename": ""} on failure.
        """
        resolved_id = chart_id or uuid.uuid4().hex[:8]
        out_path = str(self.get_chart_preview_path(resolved_id))
        normalized_type = _normalize_chart_type(chart_type)

        logger.info(f"[ChartService] Generating chart: type={normalized_type}, id={resolved_id}")

        try:
            result_path = self._render_chart(normalized_type, chart_data, out_path, title, subtitle)

            if not result_path or not os.path.exists(result_path):
                logger.warning(f"[ChartService] Chart rendering returned empty path or file missing for type={normalized_type}")
                return {"path": "", "chart_id": resolved_id, "filename": ""}

            source = chart_data.get("source", "").strip()
            if source:
                _add_source_overlay(result_path, source)

            filename = Path(result_path).name
            logger.info(f"[ChartService] Chart generated: id={resolved_id}, path={result_path}")
            return {"path": result_path, "chart_id": resolved_id, "filename": filename}

        except Exception as e:
            logger.error(f"[ChartService] Chart generation failed: {e}")
            return {"path": "", "chart_id": resolved_id, "filename": ""}

    def _render_chart(self, chart_type: str, chart_data: Dict[str, Any],
                     out_path: str, title: str, subtitle: str) -> str:
        """Dispatch to the appropriate chart renderer."""

        if chart_type in ("bar_comparison", "bar_chart_comparison"):
            labels = chart_data.get("labels", [])
            before = chart_data.get("before", [])
            after = chart_data.get("after", [])
            if not before and not after:
                values = chart_data.get("values", [])
                if values and labels:
                    n = min(len(labels), len(values))
                    chart_data = {**chart_data, "labels": labels[:n], "before": [0] * n, "after": values[:n]}
            return make_bar_chart(chart_data, out_path, title, subtitle=subtitle)

        elif chart_type == "bar_horizontal":
            return make_horizontal_bar(chart_data, out_path, title)

        elif chart_type == "line_trend":
            return make_line_trend(chart_data, out_path, title)

        elif chart_type == "pie":
            return make_pie_chart(chart_data, out_path, title)

        elif chart_type == "stacked_bar":
            return make_stacked_bar(chart_data, out_path, title)

        elif chart_type in ("bullet", "bullet_points"):
            bullet_points = chart_data.get("bullet_points", chart_data.get("labels", []))
            if bullet_points:
                return make_bullet_overlay(bullet_points, out_path)
            return ""

        else:
            logger.warning(f"[ChartService] Unknown chart type: {chart_type}, falling back to bar_comparison")
            return make_bar_chart(chart_data, out_path, title, subtitle=subtitle)

    def infer_chart_from_text(self, text: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Use LLM to infer chart_type and chart_data from text.

        Returns:
            {"chart_type": str, "chart_data": dict, "title": str}
            Falls back to bullet_points with key sentences extracted from text.
        """
        try:
            prompt = CHART_INFERENCE_USER_PROMPT.format(text=text[:3000])
            result = llm_text_gen(
                prompt=prompt,
                system_prompt=CHART_INFERENCE_SYSTEM_PROMPT,
                json_struct=None,
                max_tokens=2000,
                user_id=user_id,
            )

            if isinstance(result, dict) and result.get("text"):
                raw = result["text"]
            else:
                raw = str(result) if result else ""

            import json
            import re
            raw = raw.strip()
            if raw.startswith("```"):
                match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.DOTALL)
                if match:
                    raw = match.group(1)

            parsed = json.loads(raw)

            chart_type = parsed.get("chart_type", "bullet_points")
            chart_data = parsed.get("chart_data", {})
            title = parsed.get("title", "")

            if chart_type not in VALID_CHART_TYPES:
                chart_type = _normalize_chart_type(chart_type)
                if chart_type not in VALID_CHART_TYPES:
                    chart_type = "bullet_points"

            logger.info(f"[ChartService] Inferred chart: type={chart_type}, title={title}")
            return {"chart_type": chart_type, "chart_data": chart_data, "title": title}

        except Exception as e:
            logger.error(f"[ChartService] Chart inference failed: {e}")
            sentences = [s.strip() for s in text.replace(".", ". ").split(". ") if len(s.strip()) > 10][:5]
            return {
                "chart_type": "bullet_points",
                "chart_data": {"bullet_points": sentences or ["No data extracted"]},
                "title": "Key Points",
            }

    async def _analyze_chart_potential(
        self,
        text: str,
        section_heading: Optional[str] = None,
        section_key_points: Optional[List[str]] = None,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Stage 1: Analyze whether text has enough data for a chart.
        If not, suggest Exa search queries to find relevant data.

        Returns:
            {"has_data": bool, "data_description": str, "suggested_chart_type": str|null, "search_queries": [...]}
        """
        key_points_text = ""
        if section_key_points:
            key_points_text = f"\n\nKey points:\n" + "\n".join(f"- {p}" for p in section_key_points[:5])

        prompt = CHART_ANALYSIS_USER_PROMPT.format(
            section_heading=section_heading or "Blog Section",
            key_points_section=key_points_text,
            text=text[:3000],
        )

        try:
            result = llm_text_gen(
                prompt=prompt,
                system_prompt=CHART_ANALYSIS_SYSTEM_PROMPT,
                json_struct=None,
                max_tokens=1500,
                user_id=user_id,
            )

            raw = result.get("text", "") if isinstance(result, dict) else str(result) if result else ""

            import json
            import re
            raw = raw.strip()
            if raw.startswith("```"):
                match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.DOTALL)
                if match:
                    raw = match.group(1)

            parsed = json.loads(raw)

            has_data = parsed.get("has_data", False)
            data_description = parsed.get("data_description", "")
            suggested_chart_type = parsed.get("suggested_chart_type")
            search_queries = parsed.get("search_queries", [])

            if suggested_chart_type and suggested_chart_type not in VALID_CHART_TYPES:
                suggested_chart_type = _normalize_chart_type(suggested_chart_type)
                if suggested_chart_type not in VALID_CHART_TYPES:
                    suggested_chart_type = None

            logger.info(f"[ChartService] Chart analysis: has_data={has_data}, queries={search_queries}")
            return {
                "has_data": has_data,
                "data_description": data_description,
                "suggested_chart_type": suggested_chart_type,
                "search_queries": search_queries,
                "warnings": [],
            }

        except Exception as e:
            logger.error(f"[ChartService] Chart analysis failed: {e}")
            heading = section_heading or ""
            words = text.split()[:10]
            fallback_queries = [
                f"{heading} statistics data",
                f"{heading} trends report",
                f"{' '.join(words)} statistics",
            ] if heading.strip() or text.strip() else []
            return {
                "has_data": False,
                "data_description": f"Analysis failed: {e}",
                "suggested_chart_type": None,
                "search_queries": fallback_queries,
                "warnings": [f"Chart analysis LLM call failed: {e}"],
            }

    async def _search_for_chart_data(
        self,
        queries: List[str],
        section_heading: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Stage 2: Use Exa search to find relevant statistics and data for chart creation.

        Returns:
            {"research": str, "warnings": list[str]}
        """
        if not queries:
            return {"research": "", "warnings": []}

        warnings = []
        try:
            from services.blog_writer.research.exa_provider import ExaResearchProvider

            provider = ExaResearchProvider()
            all_results = []
            search_errors = 0

            for query in queries[:3]:
                try:
                    results = await provider.simple_search(
                        query=query,
                        num_results=3,
                        user_id=user_id,
                    )
                    all_results.extend(results)
                except Exception as e:
                    search_errors += 1
                    logger.warning(f"[ChartService] Exa search for '{query}' failed: {e}")
                    continue

            if search_errors == len(queries[:3]):
                warnings.append("All Exa search queries failed — external data search unavailable. Chart may lack supporting data.")

            if not all_results:
                return {"research": "", "warnings": warnings}

            research_parts = []
            seen_urls = set()
            for r in all_results:
                url = r.get("url", "")
                if url in seen_urls:
                    continue
                seen_urls.add(url)
                title = r.get("title", "Untitled")
                text = r.get("text", "")[:500]
                if text:
                    research_parts.append(f"- {title} ({url}): {text}")

            if not research_parts:
                return {"research": "", "warnings": warnings}

            return {"research": "\n".join(research_parts), "warnings": warnings}

        except ImportError:
            msg = "Exa provider not available — skipping external data search."
            logger.warning(f"[ChartService] {msg}")
            warnings.append(msg)
            return {"research": "", "warnings": warnings}
        except Exception as e:
            msg = f"Chart data search failed: {e}"
            logger.error(f"[ChartService] {msg}")
            warnings.append(msg)
            return {"research": "", "warnings": warnings}

    async def _synthesize_chart_from_research(
        self,
        text: str,
        research: str,
        section_heading: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Stage 3: Generate chart spec from text + research data using LLM.

        Returns:
            {"chart_type": str, "chart_data": dict, "title": str, "source": str}
        """
        try:
            prompt = CHART_SYNTHESIS_USER_PROMPT.format(
                text=text[:2000],
                research=research[:3000],
            )

            result = llm_text_gen(
                prompt=prompt,
                system_prompt=CHART_SYNTHESIS_SYSTEM_PROMPT,
                json_struct=None,
                max_tokens=2000,
                user_id=user_id,
            )

            raw = result.get("text", "") if isinstance(result, dict) else str(result) if result else ""

            import json
            import re
            raw = raw.strip()
            if raw.startswith("```"):
                match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.DOTALL)
                if match:
                    raw = match.group(1)

            parsed = json.loads(raw)

            chart_type = parsed.get("chart_type", "bullet_points")
            chart_data = parsed.get("chart_data", {})
            title = parsed.get("title", "")
            source = parsed.get("source", "")

            if chart_type not in VALID_CHART_TYPES:
                chart_type = _normalize_chart_type(chart_type)
                if chart_type not in VALID_CHART_TYPES:
                    chart_type = "bullet_points"

            if source and isinstance(chart_data, dict):
                chart_data["source"] = source

            logger.info(f"[ChartService] Synthesized chart: type={chart_type}, title={title}")
            return {"chart_type": chart_type, "chart_data": chart_data, "title": title}

        except Exception as e:
            logger.error(f"[ChartService] Chart synthesis failed: {e}")
            sentences = [s.strip() for s in text.replace(".", ". ").split(". ") if len(s.strip()) > 10][:5]
            return {
                "chart_type": "bullet_points",
                "chart_data": {"bullet_points": sentences or ["No data available"]},
                "title": section_heading or "Key Points",
            }

    async def infer_chart_with_research(
        self,
        text: str,
        section_heading: Optional[str] = None,
        section_key_points: Optional[List[str]] = None,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        3-stage chart inference pipeline:
        1. Analyze text for chart potential — does it have data? If not, what to search for?
        2. If no data, search Exa for relevant statistics.
        3. Synthesize chart spec from text + research data.

        Returns:
            {"chart_type": str, "chart_data": dict, "title": str, "warnings": list[str]}
        """
        warnings = []
        logger.info(f"[ChartService] infer_chart_with_research: heading={section_heading}, text_len={len(text)}, user={user_id}")

        # Stage 1: Analyze
        analysis = await self._analyze_chart_potential(
            text=text,
            section_heading=section_heading,
            section_key_points=section_key_points,
            user_id=user_id,
        )
        warnings.extend(analysis.get("warnings", []))

        if analysis.get("has_data") and analysis.get("suggested_chart_type"):
            # Text has enough data — do direct inference
            logger.info("[ChartService] Text has sufficient data, using direct inference")
            result = self.infer_chart_from_text(text, user_id=user_id)
            if analysis.get("suggested_chart_type") and result.get("chart_type") == "bullet_points":
                result["chart_type"] = analysis["suggested_chart_type"]
            result["warnings"] = warnings
            return result

        # Stage 2: Search for data
        search_queries = analysis.get("search_queries", [])
        if not search_queries:
            # Build queries from section heading + text keywords
            heading = section_heading or ""
            words = text.split()[:10]
            search_queries = [
                f"{heading} statistics data",
                f"{heading} trends report",
                f"{' '.join(words)} statistics",
            ]

        logger.info(f"[ChartService] Searching Exa for chart data, queries: {search_queries}")
        search_result = await self._search_for_chart_data(
            queries=search_queries,
            section_heading=section_heading,
            user_id=user_id,
        )
        research = search_result.get("research", "")
        warnings.extend(search_result.get("warnings", []))

        if not research:
            logger.warning("[ChartService] No research data found, falling back to text-only inference")
            result = self.infer_chart_from_text(text, user_id=user_id)
            result["warnings"] = warnings
            return result

        # Stage 3: Synthesize chart from text + research
        logger.info("[ChartService] Synthesizing chart from text + research data")
        result = await self._synthesize_chart_from_research(
            text=text,
            research=research,
            section_heading=section_heading,
            user_id=user_id,
        )
        result["warnings"] = warnings
        return result

    async def generate_chart_from_text(
        self,
        text: str,
        user_id: Optional[str] = None,
        chart_id: Optional[str] = None,
        section_heading: Optional[str] = None,
        section_key_points: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        End-to-end: analyze text, optionally research data, then infer and render chart.

        Uses the 3-stage pipeline (analyze → search → synthesize) for richer charts
        with real data from Exa when the original text lacks statistics.

        Returns:
            {"path": str, "chart_id": str, "filename": str, "chart_type": str, "chart_data": dict, "title": str}
        """
        inference = await self.infer_chart_with_research(
            text=text,
            section_heading=section_heading,
            section_key_points=section_key_points,
            user_id=user_id,
        )
        result = self.generate_chart(
            chart_data=inference["chart_data"],
            chart_type=inference["chart_type"],
            title=inference["title"],
            chart_id=chart_id,
        )
        result["chart_type"] = inference["chart_type"]
        result["chart_data"] = inference["chart_data"]
        result["title"] = inference["title"]
        result["warnings"] = inference.get("warnings", [])
        return result


# Per-user service instances
_chart_service_instances: Dict[str, ChartService] = {}


def get_chart_service(output_dir: Optional[str] = None, user_id: Optional[str] = None) -> ChartService:
    """Get or create ChartService for the given user."""
    cache_key = output_dir or user_id or "default"
    if cache_key not in _chart_service_instances:
        _chart_service_instances[cache_key] = ChartService(output_dir=output_dir, user_id=user_id)
    return _chart_service_instances[cache_key]