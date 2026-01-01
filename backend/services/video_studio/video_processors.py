"""
Video processing utilities for Transform Studio.

Handles format conversion, aspect ratio conversion, speed adjustment,
resolution scaling, and compression using MoviePy/FFmpeg.
"""

import io
import tempfile
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
from fastapi import HTTPException

from utils.logger_utils import get_service_logger

logger = get_service_logger("video_studio.video_processors")

try:
    from moviepy import VideoFileClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    logger.warning("[VideoProcessors] MoviePy not available. Video processing will not work.")


def _check_moviepy():
    """Check if MoviePy is available."""
    if not MOVIEPY_AVAILABLE:
        raise HTTPException(
            status_code=500,
            detail="MoviePy is not installed. Please install it: pip install moviepy imageio imageio-ffmpeg"
        )


def _get_resolution_dimensions(resolution: str) -> Tuple[int, int]:
    """Get width and height for a resolution string."""
    resolution_map = {
        "480p": (854, 480),
        "720p": (1280, 720),
        "1080p": (1920, 1080),
        "1440p": (2560, 1440),
        "4k": (3840, 2160),
    }
    return resolution_map.get(resolution.lower(), (1280, 720))


def _get_aspect_ratio_dimensions(aspect_ratio: str, target_height: int = 720) -> Tuple[int, int]:
    """Get width and height for an aspect ratio."""
    aspect_map = {
        "16:9": (16, 9),
        "9:16": (9, 16),
        "1:1": (1, 1),
        "4:5": (4, 5),
        "21:9": (21, 9),
    }
    
    if aspect_ratio not in aspect_map:
        return (1280, 720)  # Default to 16:9
    
    width_ratio, height_ratio = aspect_map[aspect_ratio]
    width = int((width_ratio / height_ratio) * target_height)
    return (width, target_height)


def convert_format(
    video_bytes: bytes,
    output_format: str = "mp4",
    codec: str = "libx264",
    quality: str = "medium",
    audio_codec: str = "aac",
) -> bytes:
    """
    Convert video to a different format.
    
    Args:
        video_bytes: Input video as bytes
        output_format: Output format (mp4, mov, webm, gif)
        codec: Video codec (libx264, libvpx-vp9, etc.)
        quality: Quality preset (high, medium, low)
        audio_codec: Audio codec (aac, mp3, opus, etc.)
        
    Returns:
        Converted video as bytes
    """
    _check_moviepy()
    
    quality_presets = {
        "high": {"bitrate": "5000k", "preset": "slow"},
        "medium": {"bitrate": "2500k", "preset": "medium"},
        "low": {"bitrate": "1000k", "preset": "fast"},
    }
    preset = quality_presets.get(quality, quality_presets["medium"])
    
    # Save input to temp file
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as input_file:
        input_file.write(video_bytes)
        input_path = input_file.name
    
    try:
        # Load video
        clip = VideoFileClip(input_path)
        
        # Format-specific codec selection
        if output_format == "webm":
            codec = "libvpx-vp9"
            audio_codec = "libopus"
        elif output_format == "gif":
            # For GIF, we need to handle differently
            codec = None
            audio_codec = None
        elif output_format == "mov":
            codec = "libx264"
            audio_codec = "aac"
        else:  # mp4
            codec = codec or "libx264"
            audio_codec = audio_codec or "aac"
        
        # Write to temp output file
        output_suffix = f".{output_format}" if output_format != "gif" else ".gif"
        with tempfile.NamedTemporaryFile(suffix=output_suffix, delete=False) as output_file:
            output_path = output_file.name
        
        if output_format == "gif":
            # For GIF, use write_gif
            clip.write_gif(output_path, fps=15, logger=None)
        else:
            # For video formats
            clip.write_videofile(
                output_path,
                codec=codec,
                audio_codec=audio_codec,
                bitrate=preset["bitrate"],
                preset=preset["preset"],
                threads=4,
                logger=None,
            )
        
        # Read output file
        with open(output_path, "rb") as f:
            output_bytes = f.read()
        
        # Cleanup
        clip.close()
        Path(input_path).unlink(missing_ok=True)
        Path(output_path).unlink(missing_ok=True)
        
        logger.info(f"[VideoProcessors] Format conversion successful: {output_format}, size={len(output_bytes)} bytes")
        return output_bytes
        
    except Exception as e:
        # Cleanup on error
        Path(input_path).unlink(missing_ok=True)
        Path(output_path).unlink(missing_ok=True) if 'output_path' in locals() else None
        logger.error(f"[VideoProcessors] Format conversion failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Format conversion failed: {str(e)}")


def convert_aspect_ratio(
    video_bytes: bytes,
    target_aspect: str,
    crop_mode: str = "center",
) -> bytes:
    """
    Convert video to a different aspect ratio.
    
    Args:
        video_bytes: Input video as bytes
        target_aspect: Target aspect ratio (16:9, 9:16, 1:1, 4:5, 21:9)
        crop_mode: Crop mode (center, smart, letterbox)
        
    Returns:
        Converted video as bytes
    """
    _check_moviepy()
    
    # Save input to temp file
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as input_file:
        input_file.write(video_bytes)
        input_path = input_file.name
    
    try:
        # Load video
        clip = VideoFileClip(input_path)
        original_width, original_height = clip.size
        
        # Calculate target dimensions
        target_width, target_height = _get_aspect_ratio_dimensions(target_aspect, original_height)
        target_aspect_ratio = target_width / target_height
        original_aspect_ratio = original_width / original_height
        
        # Determine crop dimensions
        if crop_mode == "letterbox":
            # Letterboxing: add black bars
            if target_aspect_ratio > original_aspect_ratio:
                # Target is wider, add horizontal bars
                new_height = int(original_width / target_aspect_ratio)
                y_offset = (original_height - new_height) // 2
                clip = clip.crop(y1=y_offset, y2=y_offset + new_height)
            else:
                # Target is taller, add vertical bars
                new_width = int(original_height * target_aspect_ratio)
                x_offset = (original_width - new_width) // 2
                clip = clip.crop(x1=x_offset, x2=x_offset + new_width)
        else:
            # Center crop (default)
            if target_aspect_ratio > original_aspect_ratio:
                # Need to crop height
                new_height = int(original_width / target_aspect_ratio)
                y_offset = (original_height - new_height) // 2
                clip = clip.crop(y1=y_offset, y2=y_offset + new_height)
            else:
                # Need to crop width
                new_width = int(original_height * target_aspect_ratio)
                x_offset = (original_width - new_width) // 2
                clip = clip.crop(x1=x_offset, x2=x_offset + new_width)
        
        # Resize to target dimensions (maintain quality)
        clip = clip.resize((target_width, target_height))
        
        # Write to temp output file
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as output_file:
            output_path = output_file.name
        
        clip.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac",
            preset="medium",
            threads=4,
            logger=None,
        )
        
        # Read output file
        with open(output_path, "rb") as f:
            output_bytes = f.read()
        
        # Cleanup
        clip.close()
        Path(input_path).unlink(missing_ok=True)
        Path(output_path).unlink(missing_ok=True)
        
        logger.info(f"[VideoProcessors] Aspect ratio conversion successful: {target_aspect}, size={len(output_bytes)} bytes")
        return output_bytes
        
    except Exception as e:
        # Cleanup on error
        Path(input_path).unlink(missing_ok=True)
        Path(output_path).unlink(missing_ok=True) if 'output_path' in locals() else None
        logger.error(f"[VideoProcessors] Aspect ratio conversion failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Aspect ratio conversion failed: {str(e)}")


def adjust_speed(
    video_bytes: bytes,
    speed_factor: float,
) -> bytes:
    """
    Adjust video playback speed.
    
    Args:
        video_bytes: Input video as bytes
        speed_factor: Speed multiplier (0.25, 0.5, 1.0, 1.5, 2.0, 4.0)
        
    Returns:
        Speed-adjusted video as bytes
    """
    _check_moviepy()
    
    if speed_factor <= 0:
        raise HTTPException(status_code=400, detail="Speed factor must be greater than 0")
    
    # Save input to temp file
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as input_file:
        input_file.write(video_bytes)
        input_path = input_file.name
    
    try:
        # Load video
        clip = VideoFileClip(input_path)
        
        # Adjust speed using MoviePy's speedx effect
        try:
            # Try MoviePy v2 API first
            from moviepy.video.fx.speedx import speedx
            clip = clip.fx(speedx, speed_factor)
        except (ImportError, AttributeError):
            try:
                # Fallback: try direct import
                from moviepy.video.fx import speedx
                clip = clip.fx(speedx, speed_factor)
            except (ImportError, AttributeError):
                # Fallback: Manual speed adjustment (less accurate but works)
                # This maintains audio sync by adjusting fps and duration
                original_fps = clip.fps
                new_fps = original_fps * speed_factor
                original_duration = clip.duration
                new_duration = original_duration / speed_factor
                clip = clip.with_fps(new_fps).with_duration(new_duration)
        
        # Write to temp output file
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as output_file:
            output_path = output_file.name
        
        clip.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac",
            preset="medium",
            threads=4,
            logger=None,
        )
        
        # Read output file
        with open(output_path, "rb") as f:
            output_bytes = f.read()
        
        # Cleanup
        clip.close()
        Path(input_path).unlink(missing_ok=True)
        Path(output_path).unlink(missing_ok=True)
        
        logger.info(f"[VideoProcessors] Speed adjustment successful: {speed_factor}x, size={len(output_bytes)} bytes")
        return output_bytes
        
    except Exception as e:
        # Cleanup on error
        Path(input_path).unlink(missing_ok=True)
        Path(output_path).unlink(missing_ok=True) if 'output_path' in locals() else None
        logger.error(f"[VideoProcessors] Speed adjustment failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Speed adjustment failed: {str(e)}")


def scale_resolution(
    video_bytes: bytes,
    target_resolution: str,
    maintain_aspect: bool = True,
) -> bytes:
    """
    Scale video to target resolution.
    
    Args:
        video_bytes: Input video as bytes
        target_resolution: Target resolution (480p, 720p, 1080p, 1440p, 4k)
        maintain_aspect: Whether to maintain aspect ratio
        
    Returns:
        Scaled video as bytes
    """
    _check_moviepy()
    
    # Save input to temp file
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as input_file:
        input_file.write(video_bytes)
        input_path = input_file.name
    
    try:
        # Load video
        clip = VideoFileClip(input_path)
        target_width, target_height = _get_resolution_dimensions(target_resolution)
        
        # Resize
        if maintain_aspect:
            clip = clip.resize(height=target_height)  # Maintain aspect ratio
        else:
            clip = clip.resize((target_width, target_height))
        
        # Write to temp output file
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as output_file:
            output_path = output_file.name
        
        clip.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac",
            preset="medium",
            threads=4,
            logger=None,
        )
        
        # Read output file
        with open(output_path, "rb") as f:
            output_bytes = f.read()
        
        # Cleanup
        clip.close()
        Path(input_path).unlink(missing_ok=True)
        Path(output_path).unlink(missing_ok=True)
        
        logger.info(f"[VideoProcessors] Resolution scaling successful: {target_resolution}, size={len(output_bytes)} bytes")
        return output_bytes
        
    except Exception as e:
        # Cleanup on error
        Path(input_path).unlink(missing_ok=True)
        Path(output_path).unlink(missing_ok=True) if 'output_path' in locals() else None
        logger.error(f"[VideoProcessors] Resolution scaling failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Resolution scaling failed: {str(e)}")


def compress_video(
    video_bytes: bytes,
    target_size_mb: Optional[float] = None,
    quality: str = "medium",
) -> bytes:
    """
    Compress video to reduce file size.
    
    Args:
        video_bytes: Input video as bytes
        target_size_mb: Target file size in MB (optional)
        quality: Quality preset (high, medium, low)
        
    Returns:
        Compressed video as bytes
    """
    _check_moviepy()
    
    quality_presets = {
        "high": {"bitrate": "5000k", "preset": "slow"},
        "medium": {"bitrate": "2500k", "preset": "medium"},
        "low": {"bitrate": "1000k", "preset": "fast"},
    }
    preset = quality_presets.get(quality, quality_presets["medium"])
    
    # Save input to temp file
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as input_file:
        input_file.write(video_bytes)
        input_path = input_file.name
    
    try:
        # Load video
        clip = VideoFileClip(input_path)
        
        # Calculate bitrate if target size is specified
        if target_size_mb:
            duration = clip.duration
            target_size_bits = target_size_mb * 8 * 1024 * 1024  # Convert MB to bits
            calculated_bitrate = int(target_size_bits / duration)
            # Ensure reasonable bitrate (min 500k, max 10000k)
            bitrate = f"{max(500, min(10000, calculated_bitrate // 1000))}k"
        else:
            bitrate = preset["bitrate"]
        
        # Write to temp output file
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as output_file:
            output_path = output_file.name
        
        clip.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac",
            bitrate=bitrate,
            preset=preset["preset"],
            threads=4,
            logger=None,
        )
        
        # Read output file
        with open(output_path, "rb") as f:
            output_bytes = f.read()
        
        # Cleanup
        clip.close()
        Path(input_path).unlink(missing_ok=True)
        Path(output_path).unlink(missing_ok=True)
        
        original_size_mb = len(video_bytes) / (1024 * 1024)
        compressed_size_mb = len(output_bytes) / (1024 * 1024)
        compression_ratio = (1 - compressed_size_mb / original_size_mb) * 100
        
        logger.info(
            f"[VideoProcessors] Compression successful: "
            f"{original_size_mb:.2f}MB -> {compressed_size_mb:.2f}MB ({compression_ratio:.1f}% reduction)"
        )
        return output_bytes
        
    except Exception as e:
        # Cleanup on error
        Path(input_path).unlink(missing_ok=True)
        Path(output_path).unlink(missing_ok=True) if 'output_path' in locals() else None
        logger.error(f"[VideoProcessors] Compression failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Compression failed: {str(e)}")


def trim_video(
    video_bytes: bytes,
    start_time: float = 0.0,
    end_time: Optional[float] = None,
    max_duration: Optional[float] = None,
    trim_mode: str = "beginning",
) -> bytes:
    """
    Trim video to specified duration or time range.
    
    Args:
        video_bytes: Input video as bytes
        start_time: Start time in seconds (default: 0.0)
        end_time: End time in seconds (optional, uses video duration if not provided)
        max_duration: Maximum duration in seconds (trims if video is longer)
        trim_mode: How to trim if max_duration is set ("beginning", "middle", "end")
        
    Returns:
        Trimmed video as bytes
    """
    _check_moviepy()
    
    # Save input to temp file
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as input_file:
        input_file.write(video_bytes)
        input_path = input_file.name
    
    try:
        # Load video
        clip = VideoFileClip(input_path)
        original_duration = clip.duration
        
        # Determine trim range
        if max_duration and original_duration > max_duration:
            # Need to trim to max_duration
            if trim_mode == "beginning":
                # Keep the beginning
                start_time = 0.0
                end_time = max_duration
            elif trim_mode == "end":
                # Keep the end
                start_time = original_duration - max_duration
                end_time = original_duration
            else:  # middle
                # Keep the middle
                start_time = (original_duration - max_duration) / 2
                end_time = start_time + max_duration
        else:
            # Use provided times or full video
            if end_time is None:
                end_time = original_duration
        
        # Ensure valid range
        start_time = max(0.0, min(start_time, original_duration))
        end_time = max(start_time, min(end_time, original_duration))
        
        # Trim video
        trimmed_clip = clip.subclip(start_time, end_time)
        
        # Write to temp output file
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as output_file:
            output_path = output_file.name
        
        trimmed_clip.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac",
            preset="medium",
            threads=4,
            logger=None,
        )
        
        # Read output file
        with open(output_path, "rb") as f:
            output_bytes = f.read()
        
        # Cleanup
        trimmed_clip.close()
        clip.close()
        Path(input_path).unlink(missing_ok=True)
        Path(output_path).unlink(missing_ok=True)
        
        logger.info(
            f"[VideoProcessors] Video trimmed: {start_time:.2f}s-{end_time:.2f}s, "
            f"duration={end_time - start_time:.2f}s, size={len(output_bytes)} bytes"
        )
        return output_bytes
        
    except Exception as e:
        # Cleanup on error
        Path(input_path).unlink(missing_ok=True)
        Path(output_path).unlink(missing_ok=True) if 'output_path' in locals() else None
        logger.error(f"[VideoProcessors] Video trimming failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Video trimming failed: {str(e)}")


def extract_thumbnail(
    video_bytes: bytes,
    time_position: Optional[float] = None,
    width: int = 1280,
    height: int = 720,
) -> bytes:
    """
    Extract a thumbnail frame from video.
    
    Args:
        video_bytes: Input video as bytes
        time_position: Time position in seconds (default: middle of video)
        width: Thumbnail width (default: 1280)
        height: Thumbnail height (default: 720)
        
    Returns:
        Thumbnail image as bytes (JPEG format)
    """
    _check_moviepy()
    
    # Save input to temp file
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as input_file:
        input_file.write(video_bytes)
        input_path = input_file.name
    
    try:
        # Load video
        clip = VideoFileClip(input_path)
        
        # Determine time position
        if time_position is None:
            time_position = clip.duration / 2  # Middle of video
        
        # Ensure valid time position
        time_position = max(0.0, min(time_position, clip.duration))
        
        # Get frame at specified time
        frame = clip.get_frame(time_position)
        
        # Convert numpy array to PIL Image
        from PIL import Image
        img = Image.fromarray(frame)
        
        # Resize if needed
        if img.size != (width, height):
            img = img.resize((width, height), Image.Resampling.LANCZOS)
        
        # Convert to bytes (JPEG)
        output_buffer = io.BytesIO()
        img.save(output_buffer, format="JPEG", quality=90)
        output_bytes = output_buffer.getvalue()
        
        # Cleanup
        clip.close()
        Path(input_path).unlink(missing_ok=True)
        
        logger.info(
            f"[VideoProcessors] Thumbnail extracted: time={time_position:.2f}s, "
            f"size={width}x{height}, image_size={len(output_bytes)} bytes"
        )
        return output_bytes
        
    except Exception as e:
        # Cleanup on error
        Path(input_path).unlink(missing_ok=True)
        logger.error(f"[VideoProcessors] Thumbnail extraction failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Thumbnail extraction failed: {str(e)}")
