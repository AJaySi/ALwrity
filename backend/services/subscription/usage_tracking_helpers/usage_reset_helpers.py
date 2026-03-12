"""Helpers extracted from UsageTrackingService.reset_current_billing_period."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from models.subscription_models import UsageStatus


_CALL_FIELDS = [
    "gemini_calls",
    "openai_calls",
    "anthropic_calls",
    "mistral_calls",
    "wavespeed_calls",
    "tavily_calls",
    "serper_calls",
    "metaphor_calls",
    "firecrawl_calls",
    "stability_calls",
    "exa_calls",
    "video_calls",
    "audio_calls",
    "image_edit_calls",
]

_TOKEN_FIELDS = [
    "gemini_tokens",
    "openai_tokens",
    "anthropic_tokens",
    "mistral_tokens",
    "wavespeed_tokens",
]

_COST_FIELDS = [
    "gemini_cost",
    "openai_cost",
    "anthropic_cost",
    "mistral_cost",
    "wavespeed_cost",
    "tavily_cost",
    "serper_cost",
    "metaphor_cost",
    "firecrawl_cost",
    "stability_cost",
    "exa_cost",
    "video_cost",
    "image_edit_cost",
    "audio_cost",
]


def reset_usage_summary_counters(summary: Any) -> None:
    """Reset all known usage counters to baseline values."""
    summary.usage_status = UsageStatus.ACTIVE

    for field in _CALL_FIELDS:
        if hasattr(summary, field):
            setattr(summary, field, 0)

    for field in _TOKEN_FIELDS:
        if hasattr(summary, field):
            setattr(summary, field, 0)

    for field in _COST_FIELDS:
        if hasattr(summary, field):
            setattr(summary, field, 0.0)

    summary.total_calls = 0
    summary.total_tokens = 0
    summary.total_cost = 0.0
    summary.updated_at = datetime.utcnow()
