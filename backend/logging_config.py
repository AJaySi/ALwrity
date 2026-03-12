"""Logging configuration for ALwrity backend.

Use ``ALWRITY_LOG_LEVEL_OVERRIDES`` to override logger levels in non-verbose mode
with a comma-separated ``module=LEVEL`` list (for example:
``moduleA=INFO,moduleB=ERROR``).
"""

import logging
import os
import sys
from loguru import logger


DEFAULT_NAMESPACE_LEVEL_POLICIES = {
    "sqlalchemy": "CRITICAL",
    "sqlalchemy.engine": "CRITICAL",
    "sqlalchemy.pool": "CRITICAL",
    "sqlalchemy.dialects": "CRITICAL",
    "sqlalchemy.orm": "CRITICAL",
    "sqlalchemy.engine.Engine": "CRITICAL",
    "services": "WARNING",
    "api": "WARNING",
    "models": "WARNING",
    "uvicorn.access": "WARNING",
}

NOISY_LOGGERS = (
    "linkedin_persona_service",
    "facebook_persona_service",
    "core_persona_service",
    "persona_analysis_service",
    "ai_service_manager",
    "ai_engine_service",
    "website_analyzer",
    "competitor_analyzer",
    "keyword_researcher",
    "content_gap_analyzer",
    "onboarding_data_service",
    "comprehensive_user_data",
    "strategy_data",
    "gap_analysis_data",
    "phase1_steps",
    "daily_schedule_generator",
    "gsc_service",
    "wordpress_oauth",
    "data_filter",
    "source_mapper",
    "grounding_engine",
    "blog_content_seo_analyzer",
    "linkedin_service",
    "citation_manager",
    "content_analyzer",
    "linkedin_prompt_generator",
    "linkedin_image_storage",
    "hallucination_detector",
    "writing_assistant",
    "enhanced_linguistic_analyzer",
    "persona_quality_improver",
    "logging_middleware",
    "exa_service",
    "step3_research_service",
    "sitemap_service",
    "linkedin_image_generator",
    "router_manager",
    "frontend_serving",
    "database",
    "user_business_info",
    "auth_middleware",
    "pricing_service",
    "create_billing_tables",
)


def _is_enabled(env_var_name: str, default: str = "false") -> bool:
    return os.getenv(env_var_name, default).strip().lower() in {"1", "true", "yes", "on"}


def _parse_log_level_overrides(raw_overrides: str | None) -> dict[str, str]:
    """Parse ``module=LEVEL`` comma-separated overrides into a deduplicated map."""
    if not raw_overrides:
        return {}

    parsed_overrides: dict[str, str] = {}
    for entry in raw_overrides.split(","):
        item = entry.strip()
        if not item or "=" not in item:
            continue

        logger_name, log_level_name = (part.strip() for part in item.split("=", 1))
        normalized_level = log_level_name.upper()
        if not logger_name or normalized_level not in logging._nameToLevel:
            continue

        # Last duplicate wins by design.
        parsed_overrides[logger_name] = normalized_level

    return parsed_overrides


def _build_logger_level_policies() -> dict[str, str]:
    policies = {
        **DEFAULT_NAMESPACE_LEVEL_POLICIES,
        **{logger_name: "WARNING" for logger_name in NOISY_LOGGERS},
    }
    override_policies = _parse_log_level_overrides(os.getenv("ALWRITY_LOG_LEVEL_OVERRIDES"))
    policies.update(override_policies)
    return policies


def _apply_logger_level_policies(policies: dict[str, str]) -> None:
    for logger_name, log_level_name in policies.items():
        logging.getLogger(logger_name).setLevel(getattr(logging, log_level_name))


def setup_clean_logging():
    """Set up clean logging for end users."""
    verbose_mode = _is_enabled("ALWRITY_VERBOSE")
    
    # Always remove all existing handlers first to prevent conflicts
    logger.remove()
    
    if not verbose_mode:
        _apply_logger_level_policies(_build_logger_level_policies())
        
        # Configure loguru to be less verbose (only show warnings and errors)
        def warning_only_filter(record):
            return record["level"].name in ["WARNING", "ERROR", "CRITICAL"]

        logger.add(
            sys.stdout.write,
            level="WARNING",
            format="{time:HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}\n",
            filter=warning_only_filter
        )
        if _is_enabled("ALWRITY_ENABLE_STORY_VIDEO_LOG_FILTER"):
            # Add a focused sink to surface Story Video Generation INFO logs in console.
            def video_generation_filter(record):
                msg = record.get("message", "")
                name = record.get("name", "")
                service = record.get("extra", {}).get("service")
                return (
                    "[StoryVideoGeneration]" in msg
                    or "services.story_writer.video_generation_service" in name
                    or "[video_gen]" in msg
                    or service == "video_generation_service"
                    or "services.llm_providers.main_video_generation" in name
                )

            logger.add(
                sys.stdout.write,
                level="INFO",
                format="{time:HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}\n",
                filter=video_generation_filter,
            )
    else:
        # In verbose mode, show all log levels with detailed formatting
        logger.add(
            sys.stdout.write,
            level="DEBUG",
            format="{time:HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}\n"
        )
    
    return verbose_mode


def get_uvicorn_log_level():
    """Get appropriate uvicorn log level based on verbose mode."""
    verbose_mode = _is_enabled("ALWRITY_VERBOSE")
    return "debug" if verbose_mode else "warning"
