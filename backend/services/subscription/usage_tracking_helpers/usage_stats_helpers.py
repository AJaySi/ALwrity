"""Helper utilities extracted from UsageTrackingService.get_user_usage_stats."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Iterable, Tuple

from loguru import logger

from models.subscription_models import APIProvider, APIUsageLog


def _safe_getattr(obj: Any, attr: str, default: Any) -> Any:
    """Return object attribute using a defensive default fallback."""
    value = getattr(obj, attr, default)
    return default if value is None else value


def build_default_usage_percentages(providers: Iterable[APIProvider]) -> Dict[str, float]:
    """Create zeroed usage percentages for all provider call limits plus cost."""
    usage_percentages = {f"{provider.value}_calls": 0 for provider in providers}
    usage_percentages["cost"] = 0
    return usage_percentages


def build_empty_usage_response(
    *,
    billing_period: str,
    limits: Dict[str, Any] | None,
    providers: Iterable[APIProvider],
) -> Dict[str, Any]:
    """Build a no-usage response payload with complete shape."""
    provider_breakdown = {
        provider.value: {"calls": 0, "tokens": 0, "cost": 0.0} for provider in providers
    }

    return {
        "billing_period": billing_period,
        "usage_status": "active",
        "total_calls": 0,
        "total_tokens": 0,
        "total_cost": 0.0,
        "avg_response_time": 0.0,
        "error_rate": 0.0,
        "last_updated": datetime.now().isoformat(),
        "limits": limits,
        "provider_breakdown": provider_breakdown,
        "alerts": [],
        "usage_percentages": build_default_usage_percentages(providers),
    }


def _resolve_cost_from_logs(
    *,
    db: Any,
    user_id: str,
    billing_period: str,
    provider: APIProvider,
    current_calls: int,
    current_cost: float,
    debug_label: str,
) -> float:
    """Backfill provider cost from usage logs only when needed."""
    if current_calls <= 0 or current_cost != 0.0:
        return current_cost

    logs = (
        db.query(APIUsageLog)
        .filter(
            APIUsageLog.user_id == user_id,
            APIUsageLog.provider == provider,
            APIUsageLog.billing_period == billing_period,
        )
        .all()
    )
    if not logs:
        return current_cost

    calculated_cost = sum(float(log.cost_total or 0.0) for log in logs)
    logger.info(
        f"[UsageStats] Calculated {debug_label} cost from {len(logs)} logs: ${calculated_cost:.6f}"
    )
    return calculated_cost


def build_provider_breakdown(
    *,
    db: Any,
    user_id: str,
    billing_period: str,
    summary: Any,
) -> Tuple[Dict[str, Dict[str, float | int]], Dict[str, float], Dict[str, int]]:
    """Build provider breakdown while preserving existing backfill behavior."""
    provider_breakdown: Dict[str, Dict[str, float | int]] = {}

    gemini_calls = int(_safe_getattr(summary, "gemini_calls", 0) or 0)
    gemini_tokens = int(_safe_getattr(summary, "gemini_tokens", 0) or 0)
    gemini_cost = float(_safe_getattr(summary, "gemini_cost", 0.0) or 0.0)
    gemini_cost = _resolve_cost_from_logs(
        db=db,
        user_id=user_id,
        billing_period=billing_period,
        provider=APIProvider.GEMINI,
        current_calls=gemini_calls,
        current_cost=gemini_cost,
        debug_label="gemini",
    )
    provider_breakdown["gemini"] = {"calls": gemini_calls, "tokens": gemini_tokens, "cost": gemini_cost}

    mistral_calls = int(_safe_getattr(summary, "mistral_calls", 0) or 0)
    mistral_tokens = int(_safe_getattr(summary, "mistral_tokens", 0) or 0)
    mistral_cost = float(_safe_getattr(summary, "mistral_cost", 0.0) or 0.0)
    mistral_cost = _resolve_cost_from_logs(
        db=db,
        user_id=user_id,
        billing_period=billing_period,
        provider=APIProvider.MISTRAL,
        current_calls=mistral_calls,
        current_cost=mistral_cost,
        debug_label="mistral (HuggingFace)",
    )
    provider_breakdown["huggingface"] = {
        "calls": mistral_calls,
        "tokens": mistral_tokens,
        "cost": mistral_cost,
    }

    mapped_providers = {
        "video": ("video_calls", "video_cost", APIProvider.VIDEO),
        "audio": ("audio_calls", "audio_cost", APIProvider.AUDIO),
        "image": ("stability_calls", "stability_cost", APIProvider.STABILITY),
        "image_edit": ("image_edit_calls", "image_edit_cost", APIProvider.IMAGE_EDIT),
    }
    resolved_costs = {
        "gemini_cost": gemini_cost,
        "mistral_cost": mistral_cost,
    }

    for key, (calls_attr, cost_attr, provider_enum) in mapped_providers.items():
        calls = int(_safe_getattr(summary, calls_attr, 0) or 0)
        cost = float(_safe_getattr(summary, cost_attr, 0.0) or 0.0)
        cost = _resolve_cost_from_logs(
            db=db,
            user_id=user_id,
            billing_period=billing_period,
            provider=provider_enum,
            current_calls=calls,
            current_cost=cost,
            debug_label=key,
        )
        provider_breakdown[key] = {"calls": calls, "tokens": 0, "cost": cost}
        resolved_costs[cost_attr] = cost

    wavespeed_logs = (
        db.query(APIUsageLog)
        .filter(
            APIUsageLog.user_id == user_id,
            APIUsageLog.billing_period == billing_period,
            APIUsageLog.actual_provider_name == "wavespeed",
        )
        .all()
    )
    if wavespeed_logs:
        wavespeed_calls = len(wavespeed_logs)
        wavespeed_tokens = sum((log.tokens_total or 0) for log in wavespeed_logs)
        wavespeed_cost = sum(float(log.cost_total or 0.0) for log in wavespeed_logs)
        provider_breakdown["wavespeed"] = {
            "calls": wavespeed_calls,
            "tokens": wavespeed_tokens,
            "cost": wavespeed_cost,
        }
        logger.info(
            f"[UsageStats] Calculated WaveSpeed usage: {wavespeed_calls} calls, ${wavespeed_cost:.6f}"
        )
    else:
        provider_breakdown["wavespeed"] = {"calls": 0, "tokens": 0, "cost": 0.0}

    for search_provider in ("tavily", "serper", "exa"):
        calls = int(_safe_getattr(summary, f"{search_provider}_calls", 0) or 0)
        cost = float(_safe_getattr(summary, f"{search_provider}_cost", 0.0) or 0.0)
        provider_breakdown[search_provider] = {"calls": calls, "tokens": 0, "cost": cost}
        resolved_costs[f"{search_provider}_cost"] = cost

    core_counts = {
        "gemini_calls": gemini_calls,
        "mistral_calls": mistral_calls,
    }

    return provider_breakdown, resolved_costs, core_counts


def calculate_final_total_cost(summary_total_cost: float, resolved_costs: Dict[str, float]) -> Tuple[float, float]:
    """Return calculated and chosen total cost values."""
    calculated_total_cost = float(
        resolved_costs.get("gemini_cost", 0.0)
        + resolved_costs.get("mistral_cost", 0.0)
        + resolved_costs.get("video_cost", 0.0)
        + resolved_costs.get("audio_cost", 0.0)
        + resolved_costs.get("stability_cost", 0.0)
        + resolved_costs.get("image_edit_cost", 0.0)
        + resolved_costs.get("tavily_cost", 0.0)
        + resolved_costs.get("serper_cost", 0.0)
        + resolved_costs.get("exa_cost", 0.0)
    )
    final_total_cost = calculated_total_cost if calculated_total_cost > (summary_total_cost or 0.0) else (summary_total_cost or 0.0)
    return calculated_total_cost, final_total_cost


def maybe_persist_reconciled_costs(
    *,
    db: Any,
    summary: Any,
    summary_total_cost: float,
    calculated_total_cost: float,
    final_total_cost: float,
    resolved_costs: Dict[str, float],
) -> None:
    """Persist summary cost reconciliation when calculated values are more complete."""
    if not (
        calculated_total_cost > 0
        and (summary_total_cost == 0.0 or calculated_total_cost > summary_total_cost)
    ):
        return

    logger.info(
        "[UsageStats] Updating summary costs (was {}): total_cost={:.6f}, gemini_cost={:.6f}, "
        "mistral_cost={:.6f}, video_cost={:.6f}, audio_cost={:.6f}, image_cost={:.6f}".format(
            summary_total_cost,
            final_total_cost,
            resolved_costs.get("gemini_cost", 0.0),
            resolved_costs.get("mistral_cost", 0.0),
            resolved_costs.get("video_cost", 0.0),
            resolved_costs.get("audio_cost", 0.0),
            resolved_costs.get("stability_cost", 0.0),
        )
    )

    summary.total_cost = final_total_cost
    summary.gemini_cost = resolved_costs.get("gemini_cost", 0.0)
    summary.mistral_cost = resolved_costs.get("mistral_cost", 0.0)

    for summary_attr in ("video_cost", "audio_cost", "stability_cost", "image_edit_cost"):
        if hasattr(summary, summary_attr):
            setattr(summary, summary_attr, resolved_costs.get(summary_attr, 0.0))

    try:
        db.commit()
    except Exception as e:
        logger.error(f"[UsageStats] Error updating summary costs: {e}")
        db.rollback()
