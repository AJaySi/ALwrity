"""Runtime calibration for Noise Congestion Index (NCI)."""

import os

from services.intelligence.nci import NCICalibrationConfig


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, default))
    except (TypeError, ValueError):
        return default


def get_nci_calibration_config() -> NCICalibrationConfig:
    return NCICalibrationConfig(
        version=os.getenv("NCI_VERSION", "1.0"),
        competitor_velocity_weight=_env_float("NCI_WEIGHT_COMPETITOR_VELOCITY", 0.35),
        feed_density_weight=_env_float("NCI_WEIGHT_FEED_DENSITY", 0.25),
        topic_overlap_weight=_env_float("NCI_WEIGHT_TOPIC_OVERLAP", 0.25),
        authority_weighting_weight=_env_float("NCI_WEIGHT_AUTHORITY", 0.15),
        clear_max=_env_float("NCI_THRESHOLD_CLEAR_MAX", 0.33),
        caution_max=_env_float("NCI_THRESHOLD_CAUTION_MAX", 0.66),
    )

