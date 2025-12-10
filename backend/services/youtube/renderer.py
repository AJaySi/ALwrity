"""
YouTube Video Renderer Service

Handles video rendering using WAN 2.5 text-to-video and audio generation.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import base64
import uuid
import requests
from loguru import logger
from fastapi import HTTPException

from services.wavespeed.client import WaveSpeedClient
from services.llm_providers.main_audio_generation import generate_audio
from services.story_writer.video_generation_service import StoryVideoGenerationService
from services.subscription import PricingService
from services.subscription.preflight_validator import validate_scene_animation_operation
from services.llm_providers.main_video_generation import track_video_usage
from utils.logger_utils import get_service_logger
from utils.asset_tracker import save_asset_to_library

logger = get_service_logger("youtube.renderer")


class YouTubeVideoRendererService:
    """Service for rendering YouTube videos from scenes."""
    
    def __init__(self):
        """Initialize the renderer service."""
        self.wavespeed_client = WaveSpeedClient()
        
        # Video output directory
        base_dir = Path(__file__).parent.parent.parent.parent
        self.output_dir = base_dir / "youtube_videos"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"[YouTubeRenderer] Initialized with output directory: {self.output_dir}")
    
    def render_scene_video(
        self,
        scene: Dict[str, Any],
        video_plan: Dict[str, Any],
        user_id: str,
        resolution: str = "720p",
        generate_audio_enabled: bool = True,
        voice_id: str = "Wise_Woman",
    ) -> Dict[str, Any]:
        """
        Render a single scene into a video.
        
        Args:
            scene: Scene data with narration and visual prompts
            video_plan: Original video plan for context
            user_id: Clerk user ID
            resolution: Video resolution (480p, 720p, 1080p)
            generate_audio: Whether to generate narration audio
            voice_id: Voice ID for audio generation
            
        Returns:
            Dictionary with video metadata, bytes, and cost
        """
        try:
            scene_number = scene.get("scene_number", 1)
            narration = scene.get("narration", "").strip()
            visual_prompt = (scene.get("enhanced_visual_prompt") or scene.get("visual_prompt", "")).strip()
            duration_estimate = scene.get("duration_estimate", 5)
            
            # VALIDATION: Check inputs before making expensive API calls
            if not visual_prompt:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": f"Scene {scene_number} has no visual prompt",
                        "scene_number": scene_number,
                        "message": "Visual prompt is required for video generation",
                        "user_action": "Please add a visual description for this scene before rendering.",
                    }
                )
            
            if len(visual_prompt) < 10:
                logger.warning(
                    f"[YouTubeRenderer] Scene {scene_number} has very short visual prompt "
                    f"({len(visual_prompt)} chars), may result in poor quality"
                )
            
            # Clamp duration to valid WAN 2.5 values (5 or 10 seconds)
            duration = 5 if duration_estimate <= 7 else 10
            
            logger.info(
                f"[YouTubeRenderer] Rendering scene {scene_number}: "
                f"resolution={resolution}, duration={duration}s, prompt_length={len(visual_prompt)}"
            )
            
            # Generate audio if requested - only if narration is not empty
            audio_base64 = None
            if generate_audio_enabled and narration and len(narration.strip()) > 0:
                try:
                    audio_result = generate_audio(
                        text=narration,
                        voice_id=voice_id,
                        user_id=user_id,
                    )
                    # generate_audio may return raw bytes or AudioGenerationResult
                    audio_bytes = audio_result.audio_bytes if hasattr(audio_result, "audio_bytes") else audio_result
                    # Convert to base64 (just the base64 string, not data URI)
                    audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
                    logger.info(f"[YouTubeRenderer] Generated audio for scene {scene_number}")
                except Exception as e:
                    logger.warning(f"[YouTubeRenderer] Audio generation failed: {e}, continuing without audio")
            
            # VALIDATION: Final check before expensive video API call
            if not visual_prompt or len(visual_prompt.strip()) < 5:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": f"Scene {scene_number} has invalid visual prompt",
                        "scene_number": scene_number,
                        "message": "Visual prompt must be at least 5 characters",
                        "user_action": "Please provide a valid visual description for this scene.",
                    }
                )
            
            # Generate video using WAN 2.5 text-to-video
            # This is the expensive API call - all validation should be done before this
            # Use sync mode to wait for result directly (prevents timeout issues)
            try:
                video_result = self.wavespeed_client.generate_text_video(
                    prompt=visual_prompt,
                    resolution=resolution,
                    duration=duration,
                    audio_base64=audio_base64,  # Optional: enables lip-sync if provided
                    enable_prompt_expansion=True,
                    enable_sync_mode=True,  # Use sync mode to wait for result directly
                    timeout=600,  # Increased timeout for sync mode (10 minutes)
                )
            except requests.exceptions.Timeout as e:
                logger.error(f"[YouTubeRenderer] WaveSpeed API timed out for scene {scene_number}: {e}")
                raise HTTPException(
                    status_code=504,
                    detail={
                        "error": "WaveSpeed request timed out",
                        "scene_number": scene_number,
                        "message": "The video generation request timed out.",
                        "user_action": "Please retry. If it persists, try fewer scenes, lower resolution, or shorter durations.",
                    },
                ) from e
            except requests.exceptions.RequestException as e:
                logger.error(f"[YouTubeRenderer] WaveSpeed API request failed for scene {scene_number}: {e}")
                raise HTTPException(
                    status_code=502,
                    detail={
                        "error": "WaveSpeed request failed",
                        "scene_number": scene_number,
                        "message": str(e),
                        "user_action": "Please retry. If it persists, check network connectivity or try again later.",
                    },
                ) from e
            
            # Save scene video
            video_service = StoryVideoGenerationService(output_dir=str(self.output_dir))
            save_result = video_service.save_scene_video(
                video_bytes=video_result["video_bytes"],
                scene_number=scene_number,
                user_id=user_id,
            )
            
            # Update video URL to use YouTube API endpoint
            filename = save_result["video_filename"]
            save_result["video_url"] = f"/api/youtube/videos/{filename}"
            
            # Track usage
            usage_info = track_video_usage(
                user_id=user_id,
                provider=video_result["provider"],
                model_name=video_result["model_name"],
                prompt=visual_prompt,
                video_bytes=video_result["video_bytes"],
                cost_override=video_result["cost"],
            )
            
            logger.info(
                f"[YouTubeRenderer] ✅ Scene {scene_number} rendered: "
                f"cost=${video_result['cost']:.2f}, size={len(video_result['video_bytes'])} bytes"
            )
            
            return {
                "scene_number": scene_number,
                "video_filename": save_result["video_filename"],
                "video_url": save_result["video_url"],
                "video_path": save_result["video_path"],
                "duration": video_result["duration"],
                "cost": video_result["cost"],
                "resolution": resolution,
                "width": video_result["width"],
                "height": video_result["height"],
                "file_size": save_result["file_size"],
                "prediction_id": video_result.get("prediction_id"),
                "usage_info": usage_info,
            }
            
        except HTTPException as e:
            # Re-raise with better error message for UI
            error_detail = e.detail
            if isinstance(error_detail, dict):
                error_msg = error_detail.get("error", str(error_detail))
            else:
                error_msg = str(error_detail)
            
            logger.error(
                f"[YouTubeRenderer] Scene {scene_number} failed: {error_msg}",
                exc_info=True
            )
            raise HTTPException(
                status_code=e.status_code,
                detail={
                    "error": f"Failed to render scene {scene_number}",
                    "scene_number": scene_number,
                    "message": error_msg,
                    "user_action": "Please try again. If the issue persists, check your scene content and try a different resolution.",
                }
            )
        except Exception as e:
            logger.error(f"[YouTubeRenderer] Error rendering scene {scene_number}: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail={
                    "error": f"Failed to render scene {scene_number}",
                    "scene_number": scene_number,
                    "message": str(e),
                    "user_action": "Please try again. If the issue persists, check your scene content and try a different resolution.",
                }
            )
    
    def render_full_video(
        self,
        scenes: List[Dict[str, Any]],
        video_plan: Dict[str, Any],
        user_id: str,
        resolution: str = "720p",
        combine_scenes: bool = True,
        voice_id: str = "Wise_Woman",
    ) -> Dict[str, Any]:
        """
        Render a complete video from multiple scenes.
        
        Args:
            scenes: List of scene data
            video_plan: Original video plan
            user_id: Clerk user ID
            resolution: Video resolution
            combine_scenes: Whether to combine scenes into single video
            voice_id: Voice ID for narration
            
        Returns:
            Dictionary with video metadata and scene results
        """
        try:
            logger.info(
                f"[YouTubeRenderer] Rendering full video: {len(scenes)} scenes, "
                f"resolution={resolution}, user={user_id}"
            )
            
            # Filter enabled scenes
            enabled_scenes = [s for s in scenes if s.get("enabled", True)]
            if not enabled_scenes:
                raise HTTPException(status_code=400, detail="No enabled scenes to render")
            
            scene_results = []
            total_cost = 0.0
            
            # Render each scene
            for idx, scene in enumerate(enabled_scenes):
                logger.info(
                    f"[YouTubeRenderer] Rendering scene {idx + 1}/{len(enabled_scenes)}: "
                    f"Scene {scene.get('scene_number', idx + 1)}"
                )
                
                scene_result = self.render_scene_video(
                    scene=scene,
                    video_plan=video_plan,
                    user_id=user_id,
                    resolution=resolution,
                    generate_audio_enabled=True,
                    voice_id=voice_id,
                )
                
                scene_results.append(scene_result)
                total_cost += scene_result["cost"]
            
            # Combine scenes if requested
            final_video_path = None
            final_video_url = None
            if combine_scenes and len(scene_results) > 1:
                logger.info("[YouTubeRenderer] Combining scenes into final video...")
                
                # Prepare data for video concatenation
                scene_video_paths = [r["video_path"] for r in scene_results]
                scene_audio_paths = [r.get("audio_path") for r in scene_results if r.get("audio_path")]
                
                # Use StoryVideoGenerationService to combine
                video_service = StoryVideoGenerationService(output_dir=str(self.output_dir))
                
                # Create scene dicts for concatenation
                scene_dicts = [
                    {
                        "scene_number": r["scene_number"],
                        "title": f"Scene {r['scene_number']}",
                    }
                    for r in scene_results
                ]
                
                combined_result = video_service.generate_story_video(
                    scenes=scene_dicts,
                    image_paths=[None] * len(scene_results),  # No static images
                    audio_paths=scene_audio_paths if scene_audio_paths else [],
                    video_paths=scene_video_paths,  # Use rendered videos
                    user_id=user_id,
                    story_title=video_plan.get("video_summary", "YouTube Video")[:50],
                    fps=24,
                )
                
                final_video_path = combined_result["video_path"]
                final_video_url = combined_result["video_url"]
            
            logger.info(
                f"[YouTubeRenderer] ✅ Full video rendered: {len(scene_results)} scenes, "
                f"total_cost=${total_cost:.2f}"
            )
            
            return {
                "success": True,
                "scene_results": scene_results,
                "total_cost": total_cost,
                "final_video_path": final_video_path,
                "final_video_url": final_video_url,
                "num_scenes": len(scene_results),
                "resolution": resolution,
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"[YouTubeRenderer] Error rendering full video: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to render video: {str(e)}"
            )
    
    def estimate_render_cost(
        self,
        scenes: List[Dict[str, Any]],
        resolution: str = "720p",
    ) -> Dict[str, Any]:
        """
        Estimate the cost of rendering a video before actually rendering it.
        
        Args:
            scenes: List of scene data with duration estimates
            resolution: Video resolution (480p, 720p, 1080p)
            
        Returns:
            Dictionary with cost breakdown and total estimate
        """
        # Pricing per second (same as in WaveSpeedClient)
        pricing = {
            "480p": 0.05,
            "720p": 0.10,
            "1080p": 0.15,
        }
        
        price_per_second = pricing.get(resolution, 0.10)
        
        # Filter enabled scenes
        enabled_scenes = [s for s in scenes if s.get("enabled", True)]
        
        scene_costs = []
        total_cost = 0.0
        total_duration = 0.0
        
        for scene in enabled_scenes:
            scene_number = scene.get("scene_number", 0)
            duration_estimate = scene.get("duration_estimate", 5)
            
            # Clamp duration to valid WAN 2.5 values (5 or 10 seconds)
            duration = 5 if duration_estimate <= 7 else 10
            
            scene_cost = price_per_second * duration
            scene_costs.append({
                "scene_number": scene_number,
                "duration_estimate": duration_estimate,
                "actual_duration": duration,
                "cost": round(scene_cost, 2),
            })
            
            total_cost += scene_cost
            total_duration += duration
        
        return {
            "resolution": resolution,
            "price_per_second": price_per_second,
            "num_scenes": len(enabled_scenes),
            "total_duration_seconds": total_duration,
            "scene_costs": scene_costs,
            "total_cost": round(total_cost, 2),
            "estimated_cost_range": {
                "min": round(total_cost * 0.9, 2),  # 10% buffer
                "max": round(total_cost * 1.1, 2),  # 10% buffer
            },
        }

