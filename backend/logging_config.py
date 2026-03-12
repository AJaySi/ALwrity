"""
Logging configuration for ALwrity backend.
Provides clean logging setup for end users vs developers.
"""

import logging
import os
import sys
from loguru import logger


_LOGGING_CONFIGURED = False


class LoguruInterceptHandler(logging.Handler):
    """Forward stdlib logging records to Loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def configure_logging(mode: str = "default", verbose: bool | None = None, app_name: str = "alwrity") -> bool:
    """Configure Loguru and stdlib logging into one shared pipeline."""
    global _LOGGING_CONFIGURED

    if verbose is None:
        verbose_mode = mode == "verbose" or os.getenv("ALWRITY_VERBOSE", "false").lower() == "true"
    else:
        verbose_mode = verbose

    if _LOGGING_CONFIGURED:
        return verbose_mode

    logger.remove()

    if not verbose_mode:
        # Suppress verbose logging for end users - be more aggressive
        logging.getLogger('sqlalchemy.engine').setLevel(logging.CRITICAL)
        logging.getLogger('sqlalchemy.pool').setLevel(logging.CRITICAL)
        logging.getLogger('sqlalchemy.dialects').setLevel(logging.CRITICAL)
        logging.getLogger('sqlalchemy.orm').setLevel(logging.CRITICAL)
        logging.getLogger('sqlalchemy').setLevel(logging.CRITICAL)
        logging.getLogger('sqlalchemy.engine.Engine').setLevel(logging.CRITICAL)
        
        # Suppress service initialization logs
        logging.getLogger('services').setLevel(logging.WARNING)
        logging.getLogger('api').setLevel(logging.WARNING)
        logging.getLogger('models').setLevel(logging.WARNING)
        
        # Suppress specific noisy loggers
        noisy_loggers = [
            'linkedin_persona_service',
            'facebook_persona_service', 
            'core_persona_service',
            'persona_analysis_service',
            'ai_service_manager',
            'ai_engine_service',
            'website_analyzer',
            'competitor_analyzer',
            'keyword_researcher',
            'content_gap_analyzer',
            'onboarding_data_service',
            'comprehensive_user_data',
            'strategy_data',
            'gap_analysis_data',
            'phase1_steps',
            'daily_schedule_generator',
            'gsc_service',
            'wordpress_oauth',
            'data_filter',
            'source_mapper',
            'grounding_engine',
            'blog_content_seo_analyzer',
            'linkedin_service',
            'citation_manager',
            'content_analyzer',
            'linkedin_prompt_generator',
            'linkedin_image_storage',
            'hallucination_detector',
            'writing_assistant',
            'onboarding_data_service',
            'enhanced_linguistic_analyzer',
            'persona_quality_improver',
            'logging_middleware',
            'exa_service',
            'step3_research_service',
            'sitemap_service',
            'linkedin_image_generator',
            'linkedin_prompt_generator',
            'linkedin_image_storage',
            'router_manager',
            'frontend_serving',
            'database',
            'user_business_info',
            'auth_middleware',
            'pricing_service',
            'create_billing_tables'
        ]
        
        for logger_name in noisy_loggers:
            logging.getLogger(logger_name).setLevel(logging.WARNING)
        
        # Configure loguru to be less verbose (only show warnings and errors)
        def warning_only_filter(record):
            return record["level"].name in ["WARNING", "ERROR", "CRITICAL"]

        logger.add(
            sys.stdout.write,
            level="WARNING",
            format=f"{app_name} | {{time:HH:mm:ss}} | {{level: <8}} | {{name}}:{{function}}:{{line}} - {{message}}\n",
            filter=warning_only_filter
        )
        # Add a focused sink to surface Story Video Generation INFO logs in console
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
            format=f"{app_name} | {{time:HH:mm:ss}} | {{level: <8}} | {{name}}:{{function}}:{{line}} - {{message}}\n",
            filter=video_generation_filter
        )
    else:
        # In verbose mode, show all log levels with detailed formatting
        logger.add(
            sys.stdout.write,
            level="DEBUG",
            format=f"{app_name} | {{time:HH:mm:ss}} | {{level: <8}} | {{name}}:{{function}}:{{line}} - {{message}}\n"
        )

    intercept_handler = LoguruInterceptHandler()
    root_logger = logging.getLogger()
    root_logger.handlers = [intercept_handler]
    root_logger.setLevel(logging.DEBUG if verbose_mode else logging.WARNING)

    logging.captureWarnings(True)
    warnings_logger = logging.getLogger("py.warnings")
    warnings_logger.handlers = [intercept_handler]
    warnings_logger.propagate = True

    for existing_logger in logging.root.manager.loggerDict.values():
        if isinstance(existing_logger, logging.Logger):
            existing_logger.handlers = []
            existing_logger.propagate = True

    _LOGGING_CONFIGURED = True
    return verbose_mode


def setup_clean_logging():
    """Backward-compatible wrapper for existing startup files."""
    return configure_logging(mode="default")


def get_uvicorn_log_level():
    """Get appropriate uvicorn log level based on verbose mode."""
    verbose_mode = os.getenv("ALWRITY_VERBOSE", "false").lower() == "true"
    return "debug" if verbose_mode else "warning"
