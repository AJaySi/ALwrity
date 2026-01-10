"""
Video Studio Service

Main service for AI video generation operations including:
- Text-to-video generation
- Image-to-video transformation
- Avatar generation
- Video enhancement

Integrates with WaveSpeed AI models and handles cost tracking.
"""

import asyncio
import base64
import io
import uuid
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from fastapi import HTTPException

from ..wavespeed.client import WaveSpeedClient
from ..llm_providers.main_video_generation import ai_video_generate
from ..subscription.pricing_service import PricingService
from ..database import get_db
from utils.logger_utils import get_service_logger
from utils.file_storage import save_file_safely, sanitize_filename
from .video_processors import (
    convert_format,
    convert_aspect_ratio,
    adjust_speed,
    scale_resolution,
    compress_video,
)

logger = get_service_logger("video_studio")


class VideoStudioService:
    """Main service for Video Studio operations."""

    def __init__(self):
        """Initialize Video Studio service."""
        self.wavespeed_client = WaveSpeedClient()
        
        # Video output directory
        # __file__ is: backend/services/video_studio/video_studio_service.py
        # We need: backend/video_studio_videos
        base_dir = Path(__file__).parent.parent.parent.parent
        self.output_dir = base_dir / "video_studio_videos"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Verify directory was created
        if not self.output_dir.exists():
            raise RuntimeError(f"Failed to create video_studio_videos directory: {self.output_dir}")
        
        logger.info(f"[VideoStudio] Initialized with output directory: {self.output_dir}")
    
    def _save_video_file(
        self,
        video_bytes: bytes,
        operation_type: str,
        user_id: str,
    ) -> Dict[str, Any]:
        """Save video file to disk.
        
        Args:
            video_bytes: Video content as bytes
            operation_type: Type of operation (e.g., "text-to-video", "image-to-video")
            user_id: User ID for directory organization
            
        Returns:
            Dictionary with filename, file_path, and file_url
        """
        # Create user-specific directory
        user_dir = self.output_dir / user_id
        user_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        filename = f"{operation_type}_{uuid.uuid4().hex[:8]}.mp4"
        filename = sanitize_filename(filename)
        
        # Save file
        file_path, error = save_file_safely(
            content=video_bytes,
            directory=user_dir,
            filename=filename,
            max_file_size=500 * 1024 * 1024  # 500MB max for videos
        )
        
        if error:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save video file: {error}"
            )
        
        file_url = f"/api/video-studio/videos/{user_id}/{filename}"
        
        return {
            "filename": filename,
            "file_path": str(file_path),
            "file_url": file_url,
            "file_size": len(video_bytes),
        }

    async def generate_text_to_video(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        duration: int = 5,
        resolution: str = "720p",
        aspect_ratio: str = "16:9",
        motion_preset: str = "medium",
        provider: str = "wavespeed",
        model: str = "hunyuan-video-1.5",
        user_id: str = None,
    ) -> Dict[str, Any]:
        """
        Generate video from text prompt using AI models.

        Args:
            prompt: Text description of desired video
            negative_prompt: What to avoid in the video
            duration: Video duration in seconds
            resolution: Video resolution (480p, 720p, 1080p)
            aspect_ratio: Video aspect ratio (9:16, 1:1, 16:9)
            motion_preset: Motion intensity (subtle, medium, dynamic)
            provider: AI provider (wavespeed, huggingface, etc.)
            model: Specific model to use
            user_id: User ID for tracking

        Returns:
            Dict with video_url, cost, and metadata
        """
        try:
            logger.info(f"[VideoStudio] Text-to-video: model={model}, duration={duration}s, user={user_id}")

            # Map model names to WaveSpeed endpoints
            model_mapping = {
                "hunyuan-video-1.5": "hunyuan-video-1.5/text-to-video",
                "lightricks/ltx-2-pro": "lightricks/ltx-2-pro/text-to-video",
                "lightricks/ltx-2-fast": "lightricks/ltx-2-fast/text-to-video",
                "lightricks/ltx-2-retake": "lightricks/ltx-2-retake/text-to-video",
            }

            wavespeed_model = model_mapping.get(model, model)

            # Prepare parameters
            params = {
                "duration": duration,
                "resolution": resolution,
                "aspect_ratio": aspect_ratio,
                "motion_preset": motion_preset,
            }

            if negative_prompt:
                params["negative_prompt"] = negative_prompt

            # Generate video using WaveSpeed
            result = await self.wavespeed_client.generate_video(
                prompt=prompt,
                model=wavespeed_model,
                **params
            )

            if result.get("success"):
                # Calculate cost
                cost = self._calculate_cost(
                    operation="text-to-video",
                    model=model,
                    duration=duration,
                    resolution=resolution
                )

                return {
                    "success": True,
                    "video_url": result.get("video_url"),
                    "cost": cost,
                    "estimated_duration": duration,
                    "model_used": model,
                    "provider": provider,
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Video generation failed")
                }

        except Exception as e:
            logger.error(f"[VideoStudio] Text-to-video error: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    async def generate_image_to_video(
        self,
        image_data: bytes,
        prompt: Optional[str] = None,
        duration: int = 5,
        resolution: str = "720p",
        aspect_ratio: str = "16:9",
        motion_preset: str = "medium",
        provider: str = "wavespeed",
        model: str = "alibaba/wan-2.5",
        user_id: str = None,
    ) -> Dict[str, Any]:
        """
        Transform image to video using unified video generation entry point.

        Args:
            image_data: Image file data as bytes
            prompt: Optional text prompt to guide transformation
            duration: Video duration in seconds
            resolution: Video resolution
            aspect_ratio: Video aspect ratio (not used by WAN 2.5, kept for API compatibility)
            motion_preset: Motion intensity (not used by WAN 2.5, kept for API compatibility)
            provider: AI provider (must be "wavespeed" for image-to-video)
            model: Specific model to use (alibaba/wan-2.5 or wavespeed/kandinsky5-pro)
            user_id: User ID for tracking

        Returns:
            Dict with video_url, cost, and metadata
        """
        try:
            logger.info(f"[VideoStudio] Image-to-video: model={model}, duration={duration}s, user={user_id}")

            if not user_id:
                raise ValueError("user_id is required for video generation")

            # Map model names to full model paths
            model_mapping = {
                "alibaba/wan-2.5": "alibaba/wan-2.5/image-to-video",
                "wavespeed/kandinsky5-pro": "wavespeed/kandinsky5-pro/image-to-video",
            }
            full_model = model_mapping.get(model, model)

            # Use unified video generation entry point
            # This handles pre-flight validation, generation, and usage tracking
            # Returns dict with video_bytes and full metadata
            result = ai_video_generate(
                image_data=image_data,
                prompt=prompt or "",
                operation_type="image-to-video",
                provider=provider,
                user_id=user_id,
                duration=duration,
                resolution=resolution,
                model=full_model,
                # Note: aspect_ratio and motion_preset are not supported by WAN 2.5
                # but we keep them in the API for future compatibility
            )

            # Extract video bytes and metadata
            video_bytes = result["video_bytes"]
            
            # Save video to disk
            save_result = self._save_video_file(
                video_bytes=video_bytes,
                operation_type="image-to-video",
                user_id=user_id,
            )
            
            # Save to asset library
            try:
                from utils.asset_tracker import save_asset_to_library
                db = next(get_db())
                try:
                    save_asset_to_library(
                        db=db,
                        user_id=user_id,
                        asset_type="video",
                        source_module="video_studio",
                        filename=save_result["filename"],
                        file_url=save_result["file_url"],
                        file_path=save_result["file_path"],
                        file_size=save_result["file_size"],
                        mime_type="video/mp4",
                        title=f"Video Studio: Image-to-Video ({resolution})",
                        description=f"Generated video: {prompt[:100] if prompt else 'No prompt'}",
                        prompt=result.get("prompt", prompt or ""),
                        tags=["video_studio", "image-to-video", resolution],
                        provider=result.get("provider", provider),
                        model=result.get("model_name", model),
                        cost=result.get("cost", 0.0),
                        asset_metadata={
                            "resolution": result.get("resolution", resolution),
                            "duration": result.get("duration", float(duration)),
                            "operation": "image-to-video",
                            "width": result.get("width", 1280),
                            "height": result.get("height", 720),
                        }
                    )
                    logger.info(f"[VideoStudio] Video saved to asset library")
                finally:
                    db.close()
            except Exception as e:
                logger.warning(f"[VideoStudio] Failed to save to asset library: {e}")
            
            return {
                "success": True,
                "video_url": save_result["file_url"],
                "cost": result.get("cost", 0.0),
                "estimated_duration": result.get("duration", float(duration)),
                "model_used": result.get("model_name", model),
                "provider": result.get("provider", provider),
                "resolution": result.get("resolution", resolution),
                "width": result.get("width", 1280),
                "height": result.get("height", 720),
                "file_size": save_result["file_size"],
                "metadata": result.get("metadata", {}),
            }

        except Exception as e:
            logger.error(f"[VideoStudio] Image-to-video error: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    async def generate_avatar_video(
        self,
        avatar_data: bytes,
        audio_data: Optional[bytes] = None,
        video_data: Optional[bytes] = None,
        text: Optional[str] = None,
        language: str = "en",
        provider: str = "wavespeed",
        model: str = "wavespeed/mocha",
        user_id: str = None,
    ) -> Dict[str, Any]:
        """
        Generate talking avatar video or perform face swap.

        Args:
            avatar_data: Avatar/face image as bytes
            audio_data: Audio file data for lip sync
            video_data: Source video for face swap
            text: Text to convert to speech
            language: Language for text-to-speech
            provider: AI provider
            model: Specific model to use
            user_id: User ID for tracking

        Returns:
            Dict with video_url, cost, and metadata
        """
        try:
            logger.info(f"[VideoStudio] Avatar generation: model={model}, user={user_id}")

            # Convert avatar to base64
            avatar_b64 = base64.b64encode(avatar_data).decode('utf-8')
            avatar_uri = f"data:image/png;base64,{avatar_b64}"

            # Map model names to WaveSpeed endpoints
            model_mapping = {
                "wavespeed/mocha": "wavespeed/mocha/face-swap",
                "heygen/video-translate": "heygen/video-translate",
            }

            wavespeed_model = model_mapping.get(model, model)

            # Prepare parameters
            params = {
                "avatar": avatar_uri,
                "language": language,
            }

            if audio_data:
                audio_b64 = base64.b64encode(audio_data).decode('utf-8')
                params["audio"] = f"data:audio/wav;base64,{audio_b64}"
            elif text:
                params["text"] = text
            elif video_data:
                video_b64 = base64.b64encode(video_data).decode('utf-8')
                params["source_video"] = f"data:video/mp4;base64,{video_b64}"

            # Generate avatar video using WaveSpeed
            result = await self.wavespeed_client.generate_video(
                model=wavespeed_model,
                **params
            )

            if result.get("success"):
                # Calculate cost (avatars are typically more expensive)
                cost = self._calculate_cost(
                    operation="avatar",
                    model=model,
                    duration=10  # Assume 10 second avatar videos
                )

                return {
                    "success": True,
                    "video_url": result.get("video_url"),
                    "cost": cost,
                    "model_used": model,
                    "provider": provider,
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Avatar generation failed")
                }

        except Exception as e:
            logger.error(f"[VideoStudio] Avatar generation error: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    async def enhance_video(
        self,
        video_data: bytes,
        enhancement_type: str,
        target_resolution: Optional[str] = None,
        provider: str = "wavespeed",
        model: str = "flashvsr",
        user_id: str = None,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> Dict[str, Any]:
        """
        Enhance existing video using AI models.

        Args:
            video_data: Video file data as bytes
            enhancement_type: Type of enhancement (upscale, stabilize, etc.)
            target_resolution: Target resolution for upscale ("720p", "1080p", "2k", "4k")
            provider: AI provider
            model: Specific model to use (default: "flashvsr")
            user_id: User ID for tracking
            progress_callback: Optional callback for progress updates

        Returns:
            Dict with enhanced video_url, cost, and metadata
        """
        try:
            logger.info(f"[VideoStudio] Video enhancement: type={enhancement_type}, model={model}, resolution={target_resolution}, user={user_id}")

            # Default target resolution for upscale
            if enhancement_type == "upscale" and not target_resolution:
                target_resolution = "1080p"

            # Convert video to base64 data URI
            video_b64 = base64.b64encode(video_data).decode('utf-8')
            video_uri = f"data:video/mp4;base64,{video_b64}"

            # Handle different enhancement types
            if enhancement_type == "upscale" and model in ("flashvsr", "wavespeed/flashvsr", "wavespeed-ai/flashvsr"):
                # Use FlashVSR for upscaling
                enhanced_video_bytes = await asyncio.to_thread(
                    self.wavespeed_client.upscale_video,
                    video=video_uri,
                    target_resolution=target_resolution or "1080p",
                    enable_sync_mode=False,  # Always use async with polling
                    timeout=600,  # 10 minutes max for long videos
                    progress_callback=progress_callback,
                )

                # Calculate cost based on video duration and resolution
                # FlashVSR pricing: $0.06-$0.16 per 5 seconds based on resolution
                pricing = {
                    "720p": 0.06 / 5,   # $0.012 per second
                    "1080p": 0.09 / 5,  # $0.018 per second
                    "2k": 0.12 / 5,     # $0.024 per second
                    "4k": 0.16 / 5,     # $0.032 per second
                }
                
                # Estimate video duration (rough estimate: 1MB ≈ 1 second at 1080p)
                # In production, you'd parse the video file to get actual duration
                estimated_duration = max(5, len(video_data) / (1024 * 1024))  # Minimum 5 seconds
                resolution_key = (target_resolution or "1080p").lower()
                cost_per_second = pricing.get(resolution_key, pricing["1080p"])
                cost = estimated_duration * cost_per_second

                # Save enhanced video
                save_result = self._save_video_file(
                    video_bytes=enhanced_video_bytes,
                    operation_type="enhancement_upscale",
                    user_id=user_id,
                )

                logger.info(f"[VideoStudio] Video upscaling successful: user={user_id}, cost=${cost:.4f}")

                return {
                    "success": True,
                    "video_url": save_result["file_url"],
                    "video_bytes": enhanced_video_bytes,
                    "cost": cost,
                    "enhancement_type": enhancement_type,
                    "target_resolution": target_resolution,
                    "model_used": "wavespeed-ai/flashvsr",
                    "provider": provider,
                    "metadata": {
                        "original_size": len(video_data),
                        "enhanced_size": len(enhanced_video_bytes),
                        "estimated_duration": estimated_duration,
                    },
                }
            else:
                # Other enhancement types (stabilize, colorize, etc.) - to be implemented
                logger.warning(f"[VideoStudio] Enhancement type '{enhancement_type}' not yet implemented")
                return {
                    "success": False,
                    "error": f"Enhancement type '{enhancement_type}' is not yet supported. Currently only 'upscale' with FlashVSR is available."
                }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"[VideoStudio] Video enhancement error: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    async def extend_video(
        self,
        video_data: bytes,
        prompt: str,
        model: str = "wan-2.5",
        audio_data: Optional[bytes] = None,
        negative_prompt: Optional[str] = None,
        resolution: str = "720p",
        duration: int = 5,
        enable_prompt_expansion: bool = False,
        generate_audio: bool = True,
        camera_fixed: bool = False,
        seed: Optional[int] = None,
        user_id: str = None,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> Dict[str, Any]:
        """
        Extend video duration using WAN 2.5, WAN 2.2 Spicy, or Seedance 1.5 Pro video-extend.

        Args:
            video_data: Video file data as bytes
            prompt: Text prompt describing how to extend the video
            model: Model to use ("wan-2.5", "wan-2.2-spicy", or "seedance-1.5-pro")
            audio_data: Optional audio file data as bytes (WAN 2.5 only)
            negative_prompt: Optional negative prompt (WAN 2.5 only)
            resolution: Output resolution (varies by model)
            duration: Duration of extended video in seconds (varies by model)
            enable_prompt_expansion: Enable prompt optimizer (WAN 2.5 only)
            generate_audio: Generate audio for extended video (Seedance 1.5 Pro only)
            camera_fixed: Fix camera position (Seedance 1.5 Pro only)
            seed: Random seed for reproducibility
            user_id: User ID for tracking
            progress_callback: Optional callback for progress updates

        Returns:
            Dict with extended video_url, cost, and metadata
        """
        try:
            logger.info(f"[VideoStudio] Video extension: model={model}, duration={duration}s, resolution={resolution}, user={user_id}")

            # Validate model-specific constraints
            if model in ("wan-2.2-spicy", "wavespeed-ai/wan-2.2-spicy/video-extend"):
                if resolution not in ["480p", "720p"]:
                    raise ValueError("WAN 2.2 Spicy only supports 480p and 720p resolutions")
                if duration not in [5, 8]:
                    raise ValueError("WAN 2.2 Spicy only supports 5 or 8 second durations")
                if audio_data:
                    logger.warning("[VideoStudio] Audio not supported for WAN 2.2 Spicy, ignoring")
                    audio_data = None
                if negative_prompt:
                    logger.warning("[VideoStudio] Negative prompt not supported for WAN 2.2 Spicy, ignoring")
                    negative_prompt = None
                if enable_prompt_expansion:
                    logger.warning("[VideoStudio] Prompt expansion not supported for WAN 2.2 Spicy, ignoring")
                    enable_prompt_expansion = False
            elif model in ("seedance-1.5-pro", "bytedance/seedance-v1.5-pro/video-extend"):
                if resolution not in ["480p", "720p"]:
                    raise ValueError("Seedance 1.5 Pro only supports 480p and 720p resolutions")
                if duration < 4 or duration > 12:
                    raise ValueError("Seedance 1.5 Pro only supports 4-12 second durations")
                if audio_data:
                    logger.warning("[VideoStudio] Audio upload not supported for Seedance 1.5 Pro (use generate_audio instead), ignoring")
                    audio_data = None
                if negative_prompt:
                    logger.warning("[VideoStudio] Negative prompt not supported for Seedance 1.5 Pro, ignoring")
                    negative_prompt = None
                if enable_prompt_expansion:
                    logger.warning("[VideoStudio] Prompt expansion not supported for Seedance 1.5 Pro, ignoring")
                    enable_prompt_expansion = False

            # Convert video to base64 data URI
            video_b64 = base64.b64encode(video_data).decode('utf-8')
            video_uri = f"data:video/mp4;base64,{video_b64}"

            # Convert audio to base64 if provided (WAN 2.5 only)
            audio_uri = None
            if audio_data and model not in ("wan-2.2-spicy", "wavespeed-ai/wan-2.2-spicy/video-extend", "seedance-1.5-pro", "bytedance/seedance-v1.5-pro/video-extend"):
                audio_b64 = base64.b64encode(audio_data).decode('utf-8')
                audio_uri = f"data:audio/mp3;base64,{audio_b64}"

            # Extend video using WaveSpeed
            extended_video_bytes = await asyncio.to_thread(
                self.wavespeed_client.extend_video,
                video=video_uri,
                prompt=prompt,
                model=model,
                audio=audio_uri,
                negative_prompt=negative_prompt,
                resolution=resolution,
                duration=duration,
                enable_prompt_expansion=enable_prompt_expansion,
                generate_audio=generate_audio,
                camera_fixed=camera_fixed,
                seed=seed,
                enable_sync_mode=False,  # Always use async with polling
                timeout=600,  # 10 minutes max
                progress_callback=progress_callback,
            )

            # Calculate cost (model-specific pricing)
            if model in ("wan-2.2-spicy", "wavespeed-ai/wan-2.2-spicy/video-extend"):
                # WAN 2.2 Spicy pricing: $0.03/s (480p), $0.06/s (720p)
                pricing = {
                    "480p": 0.03,
                    "720p": 0.06,
                }
            elif model in ("seedance-1.5-pro", "bytedance/seedance-v1.5-pro/video-extend"):
                # Seedance 1.5 Pro pricing varies by audio generation
                # With audio: $0.024/s (480p), $0.052/s (720p)
                # Without audio: $0.012/s (480p), $0.026/s (720p)
                if generate_audio:
                    pricing = {
                        "480p": 0.024,
                        "720p": 0.052,
                    }
                else:
                    pricing = {
                        "480p": 0.012,
                        "720p": 0.026,
                    }
            else:
                # WAN 2.5 pricing: $0.05/s (480p), $0.10/s (720p), $0.15/s (1080p)
                pricing = {
                    "480p": 0.05,
                    "720p": 0.10,
                    "1080p": 0.15,
                }
            cost = pricing.get(resolution, pricing.get("720p", 0.10)) * duration

            # Determine model name for metadata
            if model in ("wan-2.2-spicy", "wavespeed-ai/wan-2.2-spicy/video-extend"):
                model_name = "wavespeed-ai/wan-2.2-spicy/video-extend"
            elif model in ("seedance-1.5-pro", "bytedance/seedance-v1.5-pro/video-extend"):
                model_name = "bytedance/seedance-v1.5-pro/video-extend"
            else:
                model_name = "alibaba/wan-2.5/video-extend"

            # Save extended video
            save_result = self._save_video_file(
                video_bytes=extended_video_bytes,
                operation_type="extend",
                user_id=user_id,
            )

            logger.info(f"[VideoStudio] Video extension successful: user={user_id}, model={model_name}, cost=${cost:.4f}")

            return {
                "success": True,
                "video_url": save_result["file_url"],
                "video_bytes": extended_video_bytes,
                "cost": cost,
                "duration": duration,
                "resolution": resolution,
                "model_used": model_name,
                "provider": "wavespeed",
                "metadata": {
                    "original_size": len(video_data),
                    "extended_size": len(extended_video_bytes),
                    "duration": duration,
                },
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"[VideoStudio] Video extension error: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    async def transform_video(
        self,
        video_data: bytes,
        transform_type: str,
        user_id: str = None,
        # Format conversion parameters
        output_format: Optional[str] = None,
        codec: Optional[str] = None,
        quality: Optional[str] = None,
        audio_codec: Optional[str] = None,
        # Aspect ratio parameters
        target_aspect: Optional[str] = None,
        crop_mode: Optional[str] = None,
        # Speed parameters
        speed_factor: Optional[float] = None,
        # Resolution parameters
        target_resolution: Optional[str] = None,
        maintain_aspect: bool = True,
        # Compression parameters
        target_size_mb: Optional[float] = None,
        compress_quality: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Transform video using FFmpeg/MoviePy (format, aspect, speed, resolution, compression).

        Args:
            video_data: Video file data as bytes
            transform_type: Type of transformation ("format", "aspect", "speed", "resolution", "compress")
            user_id: User ID for tracking
            output_format: Output format for format conversion (mp4, mov, webm, gif)
            codec: Video codec (libx264, libvpx-vp9, etc.)
            quality: Quality preset (high, medium, low)
            audio_codec: Audio codec (aac, mp3, opus, etc.)
            target_aspect: Target aspect ratio (16:9, 9:16, 1:1, 4:5, 21:9)
            crop_mode: Crop mode for aspect conversion (center, letterbox)
            speed_factor: Speed multiplier (0.25, 0.5, 1.0, 1.5, 2.0, 4.0)
            target_resolution: Target resolution (480p, 720p, 1080p, 1440p, 4k)
            maintain_aspect: Whether to maintain aspect ratio when scaling
            target_size_mb: Target file size in MB for compression
            compress_quality: Quality preset for compression (high, medium, low)

        Returns:
            Dict with transformed video_url, cost (0 for FFmpeg operations), and metadata
        """
        try:
            logger.info(f"[VideoStudio] Video transformation: type={transform_type}, user={user_id}")

            if not user_id:
                raise ValueError("user_id is required for video transformation")

            # Process video based on transform type
            transformed_video_bytes = None

            if transform_type == "format":
                if not output_format:
                    raise ValueError("output_format is required for format conversion")
                transformed_video_bytes = await asyncio.to_thread(
                    convert_format,
                    video_bytes=video_data,
                    output_format=output_format,
                    codec=codec or "libx264",
                    quality=quality or "medium",
                    audio_codec=audio_codec or "aac",
                )

            elif transform_type == "aspect":
                if not target_aspect:
                    raise ValueError("target_aspect is required for aspect ratio conversion")
                transformed_video_bytes = await asyncio.to_thread(
                    convert_aspect_ratio,
                    video_bytes=video_data,
                    target_aspect=target_aspect,
                    crop_mode=crop_mode or "center",
                )

            elif transform_type == "speed":
                if speed_factor is None:
                    raise ValueError("speed_factor is required for speed adjustment")
                transformed_video_bytes = await asyncio.to_thread(
                    adjust_speed,
                    video_bytes=video_data,
                    speed_factor=speed_factor,
                )

            elif transform_type == "resolution":
                if not target_resolution:
                    raise ValueError("target_resolution is required for resolution scaling")
                transformed_video_bytes = await asyncio.to_thread(
                    scale_resolution,
                    video_bytes=video_data,
                    target_resolution=target_resolution,
                    maintain_aspect=maintain_aspect,
                )

            elif transform_type == "compress":
                transformed_video_bytes = await asyncio.to_thread(
                    compress_video,
                    video_bytes=video_data,
                    target_size_mb=target_size_mb,
                    quality=compress_quality or "medium",
                )

            else:
                raise ValueError(f"Unsupported transform type: {transform_type}")

            if not transformed_video_bytes:
                raise RuntimeError("Video transformation failed - no output generated")

            # Save transformed video
            save_result = self._save_video_file(
                video_bytes=transformed_video_bytes,
                operation_type=f"transform_{transform_type}",
                user_id=user_id,
            )

            # FFmpeg operations are free (no AI cost)
            cost = 0.0

            logger.info(
                f"[VideoStudio] Video transformation successful: "
                f"type={transform_type}, user={user_id}, "
                f"original={len(video_data)} bytes, transformed={len(transformed_video_bytes)} bytes"
            )

            return {
                "success": True,
                "video_url": save_result["file_url"],
                "video_bytes": transformed_video_bytes,
                "cost": cost,
                "transform_type": transform_type,
                "metadata": {
                    "original_size": len(video_data),
                    "transformed_size": len(transformed_video_bytes),
                    "transform_type": transform_type,
                },
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"[VideoStudio] Video transformation error: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    def get_available_models(self, operation_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get available AI models for video operations.

        Args:
            operation_type: Filter by operation type (optional)

        Returns:
            List of available models with metadata
        """
        all_models = {
            "text-to-video": [
                {
                    "id": "hunyuan-video-1.5",
                    "name": "Hunyuan Video 1.5",
                    "provider": "wavespeed",
                    "description": "High-quality text-to-video generation",
                    "cost_per_second": 0.10,
                    "supported_resolutions": ["720p", "1080p"],
                    "max_duration": 10,
                },
                {
                    "id": "lightricks/ltx-2-pro",
                    "name": "LTX-2 Pro",
                    "provider": "wavespeed",
                    "description": "Professional quality text-to-video",
                    "cost_per_second": 0.15,
                    "supported_resolutions": ["720p", "1080p"],
                    "max_duration": 10,
                },
                {
                    "id": "lightricks/ltx-2-fast",
                    "name": "LTX-2 Fast",
                    "provider": "wavespeed",
                    "description": "Fast text-to-video generation",
                    "cost_per_second": 0.08,
                    "supported_resolutions": ["720p"],
                    "max_duration": 10,
                },
            ],
            "image-to-video": [
                {
                    "id": "alibaba/wan-2.5",
                    "name": "WAN 2.5",
                    "provider": "wavespeed",
                    "description": "Advanced image-to-video transformation",
                    "cost_per_second": 0.12,
                    "supported_resolutions": ["480p", "720p", "1080p"],
                    "max_duration": 10,
                },
                {
                    "id": "wavespeed/kandinsky5-pro",
                    "name": "Kandinsky 5 Pro",
                    "provider": "wavespeed",
                    "description": "Artistic image-to-video generation",
                    "cost_per_second": 0.10,
                    "supported_resolutions": ["720p", "1080p"],
                    "max_duration": 8,
                },
            ],
            "avatar": [
                {
                    "id": "wavespeed/mocha",
                    "name": "MoCha Face Swap",
                    "provider": "wavespeed",
                    "description": "Advanced face swap and avatar generation",
                    "cost_per_video": 0.50,
                    "supported_languages": ["en", "es", "fr", "de"],
                },
                {
                    "id": "heygen/video-translate",
                    "name": "HeyGen Video Translate",
                    "provider": "wavespeed",
                    "description": "Multi-language avatar video translation",
                    "cost_per_video": 0.75,
                    "supported_languages": ["en", "es", "fr", "de", "it", "pt", "ja", "ko", "zh"],
                },
            ],
            "enhancement": [
                {
                    "id": "wavespeed/flashvsr",
                    "name": "FlashVSR",
                    "provider": "wavespeed",
                    "description": "Video super-resolution and enhancement",
                    "cost_per_video": 0.20,
                },
                {
                    "id": "wavespeed/ditto",
                    "name": "Ditto",
                    "provider": "wavespeed",
                    "description": "Synthetic to real video conversion",
                    "cost_per_video": 0.30,
                },
            ],
        }

        if operation_type:
            return all_models.get(operation_type, [])
        else:
            # Return all models flattened
            result = []
            for op_type, models in all_models.items():
                for model in models:
                    model["operation_type"] = op_type
                    result.append(model)
            return result

    def estimate_cost(
        self,
        operation_type: str,
        duration: Optional[int] = None,
        resolution: Optional[str] = None,
        model: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Estimate cost for video generation operations.

        Args:
            operation_type: Type of operation
            duration: Video duration in seconds
            resolution: Video resolution
            model: Specific model

        Returns:
            Cost estimate with breakdown
        """
        try:
            # Get pricing from database
            db = next(get_db())
            pricing_service = PricingService(db)

            # Default values
            duration = duration or 5
            resolution = resolution or "720p"
            model = model or self._get_default_model(operation_type)

            # Get pricing for the model
            pricing = pricing_service.get_pricing_for_provider_model("video", model)

            if pricing and pricing.get("cost_per_request"):
                base_cost = pricing["cost_per_request"]
            else:
                # Fallback pricing
                base_cost = self._calculate_cost(operation_type, model, duration, resolution)

            # Apply resolution multiplier
            resolution_multiplier = {
                "480p": 0.8,
                "720p": 1.0,
                "1080p": 1.5,
            }.get(resolution, 1.0)

            estimated_cost = base_cost * resolution_multiplier

            return {
                "estimated_cost": round(estimated_cost, 2),
                "currency": "USD",
                "breakdown": {
                    "base_cost": base_cost,
                    "resolution_multiplier": resolution_multiplier,
                    "duration": duration,
                    "resolution": resolution,
                },
                "model": model,
                "operation_type": operation_type,
            }

        except Exception as e:
            logger.error(f"[VideoStudio] Cost estimation error: {e}", exc_info=True)
            return {
                "estimated_cost": 0.50,  # Fallback
                "currency": "USD",
                "error": "Could not calculate exact cost",
            }
        finally:
            db.close()

    def _calculate_cost(
        self,
        operation: str,
        model: str,
        duration: int = 5,
        resolution: str = "720p"
    ) -> float:
        """Calculate cost for video operations."""
        # Base pricing per operation type
        base_pricing = {
            "text-to-video": 0.10,  # per second
            "image-to-video": 0.12,  # per second
            "avatar": 0.50,  # per video
            "enhancement": 0.20,  # per video
        }

        # Model-specific multipliers
        model_multipliers = {
            "lightricks/ltx-2-pro": 1.5,
            "hunyuan-video-1.5": 1.0,
            "lightricks/ltx-2-fast": 0.8,
            "alibaba/wan-2.5": 1.2,
            "wavespeed/mocha": 1.0,
            "heygen/video-translate": 1.5,
        }

        # Resolution multipliers
        resolution_multipliers = {
            "480p": 0.8,
            "720p": 1.0,
            "1080p": 1.5,
        }

        base_cost = base_pricing.get(operation, 0.10)
        model_multiplier = model_multipliers.get(model, 1.0)
        resolution_multiplier = resolution_multipliers.get(resolution, 1.0)

        if operation in ["avatar", "enhancement"]:
            # Fixed cost per video
            return base_cost * model_multiplier
        else:
            # Cost per second
            return base_cost * duration * model_multiplier * resolution_multiplier

    def _get_default_model(self, operation_type: str) -> str:
        """Get default model for operation type (OSS-focused defaults)."""
        defaults = {
            "text-to-video": "wan-2.5",  # OSS: WAN 2.5 ($0.25) vs HunyuanVideo ($0.10) - better quality/value
            "image-to-video": "wan-2.5",  # OSS: WAN 2.5 (same as text-to-video)
            "avatar": "wavespeed/mocha",
            "enhancement": "wavespeed/flashvsr",
        }
        return defaults.get(operation_type, "wan-2.5")  # Default to OSS model