from __future__ import annotations

from loguru import logger


def log_video_stack_diagnostics() -> None:
    try:
        import sys
        import platform
        import importlib

        mv = importlib.import_module("moviepy")
        im = importlib.import_module("imageio")
        try:
            import imageio_ffmpeg as iff
            ff = iff.get_ffmpeg_exe()
        except Exception:
            ff = "unresolved"
        logger.info(
            "[VideoStack] py={} plat={} moviepy={} imageio={} ffmpeg={}",
            sys.executable,
            platform.platform(),
            getattr(mv, "__version__", "NA"),
            getattr(im, "__version__", "NA"),
            ff,
        )
    except Exception as e:
        logger.error("[VideoStack] diagnostics failed: {}", e)


def assert_supported_moviepy() -> None:
    """Fail fast if MoviePy isn't version 2.x."""
    try:
        import pkg_resources as pr
        mv = pr.get_distribution("moviepy").version
        if not mv.startswith("2."):
            raise RuntimeError(
                f"Unsupported MoviePy version {mv}. Expected 2.x. "
                "Please install with: pip install moviepy==2.1.2"
            )
    except Exception as e:
        # Log and re-raise so startup fails clearly
        logger.error("[VideoStack] version check failed: {}", e)
        raise


