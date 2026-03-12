"""Centralized, production-ready logging configuration for the ALwrity backend."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
from typing import Dict, Optional, Tuple

from loguru import logger

_LOGGING_CONFIGURED = False

DEFAULT_LOG_OVERRIDES: Dict[str, str] = {
    "sqlalchemy": "ERROR",
    "sqlalchemy.engine": "ERROR",
    "sqlalchemy.pool": "ERROR",
    "uvicorn.access": "WARNING",
    "watchfiles": "WARNING",
    "httpx": "WARNING",
    "urllib3": "WARNING",
    "apscheduler": "INFO",
}

VIDEO_SERVICE_NAMES = {
    "video_generation_service",
    "services.story_writer.video_generation_service",
    "services.llm_providers.main_video_generation",
}


class InterceptHandler(logging.Handler):
    """Forward standard-library logging records into Loguru sinks."""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        stdlib_extra = {
            key: value
            for key, value in record.__dict__.items()
            if key
            not in {
                "name", "msg", "args", "levelname", "levelno", "pathname", "filename",
                "module", "exc_info", "exc_text", "stack_info", "lineno", "funcName",
                "created", "msecs", "relativeCreated", "thread", "threadName", "processName",
                "process", "message", "asctime"
            }
        }

        log = logger.bind(stdlib_logger=record.name, **stdlib_extra)
        log.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _parse_level_overrides() -> Dict[str, str]:
    overrides = dict(DEFAULT_LOG_OVERRIDES)
    raw_overrides = os.getenv("ALWRITY_LOG_LEVEL_OVERRIDES", "").strip()
    if not raw_overrides:
        return overrides

    for pair in raw_overrides.split(","):
        pair = pair.strip()
        if not pair or "=" not in pair:
            continue
        logger_name, level = pair.split("=", 1)
        logger_name = logger_name.strip()
        level = level.strip().upper()
        if logger_name and level:
            overrides[logger_name] = level

    return overrides


def _resolve_log_level(level_name: str, default: int = logging.INFO) -> Tuple[int, bool]:
    try:
        return logging._checkLevel(level_name), True
    except (TypeError, ValueError):
        return default, False


def _apply_logger_overrides(verbose_mode: bool) -> None:
    root_level = logging.DEBUG if verbose_mode else logging.INFO
    logging.getLogger().setLevel(root_level)

    for logger_name, level_name in _parse_level_overrides().items():
        level_no, valid = _resolve_log_level(level_name)
        if not valid:
            logger.warning(
                "Invalid log level override '{}' for logger '{}'; defaulting to INFO",
                level_name,
                logger_name,
            )
        logging.getLogger(logger_name).setLevel(level_no)


def _serialize_record(record: Dict) -> str:
    payload = {
        "time": record["time"].isoformat(),
        "level": record["level"].name,
        "name": record["name"],
        "function": record["function"],
        "line": record["line"],
        "message": record["message"],
        "extra": record.get("extra", {}),
    }
    if record.get("exception"):
        payload["exception"] = str(record["exception"])
    return json.dumps(payload, default=str)


def _base_log_format(verbose_mode: bool) -> str:
    if verbose_mode:
        return (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "rid={extra[request_id]} jid={extra[job_id]} uid={extra[user_id]} | "
            "{message}"
        )

    return (
        "<green>{time:HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{line}</cyan> | "
        "{message}"
    )


def _patch_record(record: Dict) -> Dict:
    extra = record.setdefault("extra", {})
    extra.setdefault("request_id", "-")
    extra.setdefault("job_id", "-")
    extra.setdefault("user_id", "-")
    return record


def _video_generation_filter(record: Dict) -> bool:
    message = record.get("message", "")
    name = record.get("name", "")
    service_name = record.get("extra", {}).get("service")
    return (
        "[StoryVideoGeneration]" in message
        or "[video_gen]" in message
        or service_name in VIDEO_SERVICE_NAMES
        or any(service in name for service in VIDEO_SERVICE_NAMES)
    )


def _configure_loguru_sinks(verbose_mode: bool) -> None:
    logger.remove()

    logger.configure(patcher=_patch_record)

    log_json = _env_bool("ALWRITY_LOG_JSON", default=False)
    console_format = _serialize_record if log_json else _base_log_format(verbose_mode)

    logger.add(
        sys.stdout,
        level="DEBUG" if verbose_mode else "WARNING",
        format=console_format,
        backtrace=True,
        diagnose=verbose_mode,
        enqueue=True,
    )

    enable_video_focus = _env_bool("ALWRITY_ENABLE_VIDEO_LOG_FOCUS", default=not verbose_mode)
    if enable_video_focus and not verbose_mode:
        logger.add(
            sys.stdout,
            level="INFO",
            format=console_format,
            filter=_video_generation_filter,
            enqueue=True,
        )

    log_file = os.getenv("ALWRITY_LOG_FILE", "").strip()
    if log_file:
        logger.add(
            log_file,
            level="DEBUG" if verbose_mode else "INFO",
            format=console_format,
            rotation=os.getenv("ALWRITY_LOG_ROTATION", "50 MB"),
            retention=os.getenv("ALWRITY_LOG_RETENTION", "14 days"),
            enqueue=True,
            backtrace=True,
            diagnose=verbose_mode,
        )


def _configure_stdlib_intercept(verbose_mode: bool) -> None:
    intercept_handler = InterceptHandler()
    root_logger = logging.getLogger()
    root_logger.handlers = [intercept_handler]
    root_logger.setLevel(logging.DEBUG if verbose_mode else logging.INFO)

    for name in ("uvicorn", "uvicorn.error", "uvicorn.access", "gunicorn", "gunicorn.error"):
        target_logger = logging.getLogger(name)
        target_logger.handlers = [intercept_handler]
        target_logger.propagate = False

    logging.captureWarnings(True)


def _register_exception_hooks() -> None:
    def _excepthook(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        logger.opt(exception=(exc_type, exc_value, exc_traceback)).critical("Uncaught exception")

    def _async_exception_handler(loop, context):
        exc = context.get("exception")
        if exc:
            logger.opt(exception=exc).error("Unhandled asyncio exception")
        else:
            logger.error("Unhandled asyncio exception: {}", context.get("message", context))

    sys.excepthook = _excepthook

    try:
        loop = asyncio.get_running_loop()
        loop.set_exception_handler(_async_exception_handler)
    except RuntimeError:
        pass


def configure_logging(*, verbose_mode: Optional[bool] = None, force: bool = False, bootstrap_source: str = "unknown") -> bool:
    """Configure Loguru + stdlib logging in one place.

    Environment variables:
        - ALWRITY_VERBOSE=true|false
        - ALWRITY_LOG_LEVEL_OVERRIDES="sqlalchemy=ERROR,uvicorn.access=WARNING"
        - ALWRITY_ENABLE_VIDEO_LOG_FOCUS=true|false
        - ALWRITY_LOG_JSON=true|false
        - ALWRITY_LOG_FILE=/path/to/backend.log
        - ALWRITY_LOG_ROTATION=50 MB
        - ALWRITY_LOG_RETENTION=14 days
    """
    global _LOGGING_CONFIGURED

    if _LOGGING_CONFIGURED and not force:
        return os.getenv("ALWRITY_VERBOSE", "false").lower() == "true"

    if verbose_mode is None:
        verbose_mode = _env_bool("ALWRITY_VERBOSE", default=False)

    os.environ["ALWRITY_VERBOSE"] = "true" if verbose_mode else "false"

    _configure_loguru_sinks(verbose_mode)
    _configure_stdlib_intercept(verbose_mode)
    _apply_logger_overrides(verbose_mode)
    _register_exception_hooks()

    logger.bind(source=bootstrap_source).info(
        "Logging configured (verbose={}, source={})",
        verbose_mode,
        bootstrap_source,
    )

    _LOGGING_CONFIGURED = True
    return verbose_mode



def bind_logger_context(*, request_id: Optional[str] = None, job_id: Optional[str] = None, user_id: Optional[str] = None):
    """Return a context-bound logger for request/job/user correlation."""
    return logger.bind(
        request_id=request_id or "-",
        job_id=job_id or "-",
        user_id=user_id or "-",
    )


def setup_clean_logging() -> bool:
    """Backward-compatible wrapper for existing imports."""
    return configure_logging(bootstrap_source="setup_clean_logging")


def get_uvicorn_log_level() -> str:
    """Get uvicorn log level based on verbose mode."""
    verbose_mode = _env_bool("ALWRITY_VERBOSE", default=False)
    return "debug" if verbose_mode else "warning"
