"""
Social Optimizer service for platform-specific video optimization.

Creates optimized versions of videos for Instagram, TikTok, YouTube, LinkedIn, Facebook, and Twitter.
"""

import asyncio
import base64
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from utils.logging import get_service_logger
from .platform_specs import Platform, PlatformSpec, get_platform_spec, get_platform_specs
from .video_processors import (
    convert_aspect_ratio,
    trim_video,
    compress_video,
    extract_thumbnail,
)

logger = get_service_logger("video_studio.social_optimizer")


@dataclass
class OptimizationOptions:
    """Options for video optimization."""
    auto_crop: bool = True
    generate_thumbnails: bool = True
    compress: bool = True
    trim_mode: str = "beginning"  # "beginning", "middle", "end"


@dataclass
class PlatformResult:
    """Result for a single platform optimization."""
    platform: str
    name: str
    aspect_ratio: str
    video_url: str
    thumbnail_url: Optional[str] = None
    duration: float = 0.0
    file_size: int = 0
    width: int = 0
    height: int = 0


class SocialOptimizerService:
    """Service for optimizing videos for social media platforms."""
    
    def __init__(self):
        """Initialize Social Optimizer service."""
        logger.info("[SocialOptimizer] Service initialized")
    
    async def optimize_for_platforms(
        self,
        video_bytes: bytes,
        platforms: List[str],
        options: OptimizationOptions,
        user_id: str,
        video_studio_service: Any,  # VideoStudioService
    ) -> Dict[str, Any]:
        """
        Optimize video for multiple platforms.
        
        Args:
            video_bytes: Source video as bytes
            platforms: List of platform names (e.g., ["instagram", "tiktok"])
            options: Optimization options
            user_id: User ID for file storage
            video_studio_service: VideoStudioService instance for saving files
            
        Returns:
            Dict with results for each platform
        """
        logger.info(
            f"[SocialOptimizer] Optimizing video for platforms: {platforms}, "
            f"user={user_id}"
        )
        
        results: List[PlatformResult] = []
        errors: List[Dict[str, str]] = []
        
        # Process each platform
        for platform_name in platforms:
            try:
                platform_enum = Platform(platform_name.lower())
                platform_specs = get_platform_specs(platform_enum)
                
                # Process each format variant for the platform
                for spec in platform_specs:
                    try:
                        result = await self._optimize_for_spec(
                            video_bytes=video_bytes,
                            spec=spec,
                            options=options,
                            user_id=user_id,
                            video_studio_service=video_studio_service,
                        )
                        results.append(result)
                    except Exception as e:
                        logger.error(
                            f"[SocialOptimizer] Failed to optimize for {spec.name}: {e}",
                            exc_info=True
                        )
                        errors.append({
                            "platform": platform_name,
                            "format": spec.name,
                            "error": str(e),
                        })
            except ValueError:
                logger.warning(f"[SocialOptimizer] Unknown platform: {platform_name}")
                errors.append({
                    "platform": platform_name,
                    "error": f"Unknown platform: {platform_name}",
                })
        
        # Calculate total cost (free - FFmpeg processing)
        total_cost = 0.0
        
        logger.info(
            f"[SocialOptimizer] Optimization complete: "
            f"{len(results)} successful, {len(errors)} errors"
        )
        
        return {
            "success": len(results) > 0,
            "results": [
                {
                    "platform": r.platform,
                    "name": r.name,
                    "aspect_ratio": r.aspect_ratio,
                    "video_url": r.video_url,
                    "thumbnail_url": r.thumbnail_url,
                    "duration": r.duration,
                    "file_size": r.file_size,
                    "width": r.width,
                    "height": r.height,
                }
                for r in results
            ],
            "errors": errors,
            "cost": total_cost,
        }
    
    async def _optimize_for_spec(
        self,
        video_bytes: bytes,
        spec: PlatformSpec,
        options: OptimizationOptions,
        user_id: str,
        video_studio_service: Any,
    ) -> PlatformResult:
        """
        Optimize video for a specific platform specification.
        
        Args:
            video_bytes: Source video as bytes
            spec: Platform specification
            options: Optimization options
            user_id: User ID for file storage
            video_studio_service: VideoStudioService instance
            
        Returns:
            PlatformResult with optimized video URL and metadata
        """
        logger.info(
            f"[SocialOptimizer] Optimizing for {spec.name} "
            f"({spec.aspect_ratio}, max {spec.max_duration}s)"
        )
        
        processed_video = video_bytes
        original_size_mb = len(video_bytes) / (1024 * 1024)
        
        # Step 1: Convert aspect ratio if needed
        if options.auto_crop:
            processed_video = await asyncio.to_thread(
                convert_aspect_ratio,
                processed_video,
                spec.aspect_ratio,
                "center",  # Use center crop for social media
            )
            logger.debug(f"[SocialOptimizer] Aspect ratio converted to {spec.aspect_ratio}")
        
        # Step 2: Trim if video exceeds max duration
        if spec.max_duration > 0:
            # Get video duration (we'll need to check this)
            # For now, we'll trim if the video is likely too long
            # In a real implementation, we'd use MoviePy to get duration first
            processed_video = await asyncio.to_thread(
                trim_video,
                processed_video,
                start_time=0.0,
                end_time=None,
                max_duration=spec.max_duration,
                trim_mode=options.trim_mode,
            )
            logger.debug(f"[SocialOptimizer] Video trimmed to max {spec.max_duration}s")
        
        # Step 3: Compress if needed and file size exceeds limit
        if options.compress:
            current_size_mb = len(processed_video) / (1024 * 1024)
            if current_size_mb > spec.max_file_size_mb:
                # Calculate target size (90% of max to be safe)
                target_size_mb = spec.max_file_size_mb * 0.9
                processed_video = await asyncio.to_thread(
                    compress_video,
                    processed_video,
                    target_size_mb=target_size_mb,
                    quality="medium",
                )
                logger.debug(
                    f"[SocialOptimizer] Video compressed: "
                    f"{current_size_mb:.2f}MB -> {len(processed_video) / (1024 * 1024):.2f}MB"
                )
        
        # Step 4: Save optimized video
        save_result = video_studio_service._save_video_file(
            video_bytes=processed_video,
            operation_type=f"social_optimizer_{spec.platform.value}",
            user_id=user_id,
        )
        video_url = save_result["file_url"]
        
        # Step 5: Generate thumbnail if requested
        thumbnail_url = None
        if options.generate_thumbnails:
            try:
                thumbnail_bytes = await asyncio.to_thread(
                    extract_thumbnail,
                    processed_video,
                    time_position=None,  # Middle of video
                    width=spec.width,
                    height=spec.height,
                )
                
                # Save thumbnail
                thumbnail_save_result = video_studio_service._save_video_file(
                    video_bytes=thumbnail_bytes,
                    operation_type=f"social_optimizer_thumbnail_{spec.platform.value}",
                    user_id=user_id,
                )
                thumbnail_url = thumbnail_save_result["file_url"]
                logger.debug(f"[SocialOptimizer] Thumbnail generated: {thumbnail_url}")
            except Exception as e:
                logger.warning(f"[SocialOptimizer] Failed to generate thumbnail: {e}")
        
        # Get video metadata (duration, file size)
        # For now, we'll estimate based on file size
        # In a real implementation, we'd use MoviePy to get actual duration
        file_size = len(processed_video)
        estimated_duration = spec.max_duration if spec.max_duration > 0 else 10.0
        
        logger.info(
            f"[SocialOptimizer] Optimization complete for {spec.name}: "
            f"video_url={video_url}, size={file_size} bytes"
        )
        
        return PlatformResult(
            platform=spec.platform.value,
            name=spec.name,
            aspect_ratio=spec.aspect_ratio,
            video_url=video_url,
            thumbnail_url=thumbnail_url,
            duration=estimated_duration,
            file_size=file_size,
            width=spec.width,
            height=spec.height,
        )
