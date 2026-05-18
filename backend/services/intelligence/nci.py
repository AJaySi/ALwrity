"""Noise Congestion Index (NCI) scoring utilities.
"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass(frozen=True)
class NCICalibrationConfig:
    """Calibration knobs for NCI scoring and band thresholds."""

    version: str = "1.0"
    competitor_velocity_weight: float = 0.35
    feed_density_weight: float = 0.25
    topic_overlap_weight: float = 0.25
    authority_weighting_weight: float = 0.15
    clear_max: float = 0.33
    caution_max: float = 0.66


DEFAULT_NCI_CONFIG = NCICalibrationConfig()


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _weighted_average(weights: Dict[str, float], values: Dict[str, float]) -> float:
    total_weight = sum(max(0.0, w) for w in weights.values())
    if total_weight <= 0:
        return 0.0
    weighted_sum = sum(_clamp01(values.get(k, 0.0)) * max(0.0, w) for k, w in weights.items())
    return _clamp01(weighted_sum / total_weight)


def compute_nci(
    *,
    competitor_velocity: float,
    feed_density: float,
    topic_overlap: float,
    authority_weighting: float,
    config: NCICalibrationConfig = DEFAULT_NCI_CONFIG,
) -> Dict[str, Any]:
    """Compute normalized NCI score and congestion band from four inputs."""
    weights = {
        "competitor_velocity": config.competitor_velocity_weight,
        "feed_density": config.feed_density_weight,
        "topic_overlap": config.topic_overlap_weight,
        "authority_weighting": config.authority_weighting_weight,
    }
    values = {
        "competitor_velocity": competitor_velocity,
        "feed_density": feed_density,
        "topic_overlap": topic_overlap,
        "authority_weighting": authority_weighting,
    }
    score = _weighted_average(weights, values)

    if score <= config.clear_max:
        band = "clear"
    elif score <= config.caution_max:
        band = "caution"
    else:
        band = "congested"

    return {
        "score": round(score, 4),
        "band": band,
        "version": config.version,
        "inputs": {k: round(_clamp01(v), 4) for k, v in values.items()},
        "thresholds": {
            "clear_max": config.clear_max,
            "caution_max": config.caution_max,
        },
    }

