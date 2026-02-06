"""
Face Swap service for Video Studio.

Supports two models:
1. MoCha (wavespeed-ai/wan-2.1/mocha) - Character replacement with motion preservation
2. Video Face Swap (wavespeed-ai/video-face-swap) - Simple face swap with multi-face support
"""

import base64
from typing import Dict, Any, Optional, Callable
from fastapi import HTTPException

from utils.logging import get_service_logger
from ..wavespeed.client import WaveSpeedClient

logger = get_service_logger("video_studio.face_swap")


class FaceSwapService:
    """Service for face/character swap operations."""
    
    def __init__(self):
        """Initialize Face Swap service."""
        self.wavespeed_client = WaveSpeedClient()
        logger.info("[FaceSwap] Service initialized")
    
    def calculate_cost(self, model: str, resolution: Optional[str] = None, duration: float = 10.0) -> float:
        """
        Calculate cost for face swap operation.
        
        Args:
            model: Model to use ("mocha" or "video-face-swap")
            resolution: Output resolution for MoCha ("480p" or "720p"), ignored for video-face-swap
            duration: Video duration in seconds
            
        Returns:
            Cost in USD
        """
        if model == "video-face-swap":
            # Video Face Swap pricing: $0.01/s
            # Minimum charge: 5 seconds
            # Maximum: 600 seconds (10 minutes)
            cost_per_second = 0.01
            billed_duration = max(5.0, min(duration, 600.0))
            return cost_per_second * billed_duration
        else:
            # MoCha pricing: $0.04/s (480p), $0.08/s (720p)
            # Minimum charge: 5 seconds
            # Maximum billed: 120 seconds
            pricing = {
                "480p": 0.04,
                "720p": 0.08,
            }
            cost_per_second = pricing.get(resolution or "480p", pricing["480p"])
            billed_duration = max(5.0, min(duration, 120.0))
            return cost_per_second * billed_duration
    
    async def swap_face(
        self,
        image_data: bytes,
        video_data: bytes,
        model: str = "mocha",
        prompt: Optional[str] = None,
        resolution: str = "480p",
        seed: Optional[int] = None,
        target_gender: str = "all",
        target_index: int = 0,
        user_id: str = None,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> Dict[str, Any]:
        """
        Perform face/character swap using MoCha or Video Face Swap.
        
        Args:
            image_data: Reference image as bytes
            video_data: Source video as bytes
            model: Model to use ("mocha" or "video-face-swap")
            prompt: Optional prompt to guide the swap (MoCha only)
            resolution: Output resolution for MoCha ("480p" or "720p")
            seed: Random seed for reproducibility (MoCha only)
            target_gender: Filter which faces to swap (video-face-swap only: "all", "female", "male")
            target_index: Select which face to swap (video-face-swap only: 0 = largest)
            user_id: User ID for tracking
            progress_callback: Optional callback for progress updates
            
        Returns:
            Dict with swapped video_url, cost, and metadata
        """
        try:
            logger.info(
                f"[FaceSwap] Face swap request: user={user_id}, "
                f"model={model}, resolution={resolution if model == 'mocha' else 'N/A'}"
            )
            
            if not user_id:
                raise ValueError("user_id is required for face swap")
            
            # Validate model
            if model not in ("mocha", "video-face-swap"):
                raise ValueError("Model must be 'mocha' or 'video-face-swap'")
            
            # Convert image to base64 data URI
            image_b64 = base64.b64encode(image_data).decode('utf-8')
            image_uri = f"data:image/png;base64,{image_b64}"
            
            # Convert video to base64 data URI
            video_b64 = base64.b64encode(video_data).decode('utf-8')
            video_uri = f"data:video/mp4;base64,{video_b64}"
            
            # Estimate duration (we'll use a default, actual duration would come from video metadata)
            estimated_duration = 10.0  # Default estimate, should be improved with actual video duration
            
            # Calculate cost estimate
            cost = self.calculate_cost(model, resolution if model == "mocha" else None, estimated_duration)
            
            if progress_callback:
                model_name = "MoCha" if model == "mocha" else "Video Face Swap"
                progress_callback(10.0, f"Submitting face swap request to {model_name}...")
            
            # Perform face swap based on model
            if model == "mocha":
                # Validate resolution for MoCha
                if resolution not in ("480p", "720p"):
                    raise ValueError("Resolution must be '480p' or '720p' for MoCha")
                
                # face_swap is synchronous (uses sync_mode internally)
                swapped_video_bytes = self.wavespeed_client.face_swap(
                    image=image_uri,
                    video=video_uri,
                    prompt=prompt,
                    resolution=resolution,
                    seed=seed,
                    enable_sync_mode=True,
                    timeout=600,  # 10 minutes timeout
                    progress_callback=progress_callback,
                )
            else:  # video-face-swap
                # video_face_swap is synchronous (uses sync_mode internally)
                swapped_video_bytes = self.wavespeed_client.video_face_swap(
                    video=video_uri,
                    face_image=image_uri,
                    target_gender=target_gender,
                    target_index=target_index,
                    enable_sync_mode=True,
                    timeout=600,  # 10 minutes timeout
                    progress_callback=progress_callback,
                )
            
            if progress_callback:
                progress_callback(90.0, "Face swap complete, saving video...")
            
            # Save swapped video
            from . import VideoStudioService
            video_service = VideoStudioService()
            save_result = video_service._save_video_file(
                video_bytes=swapped_video_bytes,
                operation_type="face_swap",
                user_id=user_id,
            )
            
            # Recalculate cost with actual duration if available
            # For now, use estimated cost
            actual_cost = cost
            
            logger.info(
                f"[FaceSwap] Face swap successful: user={user_id}, "
                f"resolution={resolution}, cost=${actual_cost:.4f}"
            )
            
            metadata = {
                "original_image_size": len(image_data),
                "original_video_size": len(video_data),
                "swapped_video_size": len(swapped_video_bytes),
                "model": model,
            }
            
            if model == "mocha":
                metadata.update({
                    "resolution": resolution,
                    "seed": seed,
                    "prompt": prompt,
                })
            else:  # video-face-swap
                metadata.update({
                    "target_gender": target_gender,
                    "target_index": target_index,
                })
            
            return {
                "success": True,
                "video_url": save_result["file_url"],
                "video_bytes": swapped_video_bytes,
                "cost": actual_cost,
                "model": model,
                "resolution": resolution if model == "mocha" else None,
                "metadata": metadata,
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"[FaceSwap] Face swap error: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
