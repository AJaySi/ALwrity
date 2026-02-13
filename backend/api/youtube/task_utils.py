"""YouTube Task Execution Utilities

Background task execution functions for YouTube video processing.
Handles complex video rendering, scene processing, and task management.
"""

from typing import Dict, Any, List, Optional
import asyncio
from loguru import logger

from utils.logger_utils import get_service_logger
from .task_manager import task_manager
from .dependencies import get_youtube_renderer_service

logger = get_service_logger("api.youtube.task_utils")


def _execute_video_render_task(
    task_id: str,
    scenes: List[Dict[str, Any]],
    video_plan: Dict[str, Any],
    user_id: str,
    resolution: str,
    combine_scenes: bool,
    voice_id: str,
):
    """Background task to render video with progress updates."""
    logger.info(
        f"[YouTubeRenderer] Background task started for task {task_id}, "
        f"scenes={len(scenes)}, user={user_id}"
    )

    # Verify task exists before starting
    task_status = task_manager.get_task_status(task_id)
    if not task_status:
        logger.error(
            f"[YouTubeRenderer] Task {task_id} not found when background task started. "
            f"This should not happen - task may have been cleaned up."
        )
        return

    try:
        task_manager.update_task_status(
            task_id, "processing", progress=5.0, message="Initializing render..."
        )
        logger.info(f"[YouTubeRenderer] Task {task_id} status updated to processing")

        renderer = get_youtube_renderer_service()

        total_scenes = len(scenes)
        scene_results = []
        total_cost = 0.0

        # VALIDATION: Pre-validate all scenes before starting expensive API calls
        invalid_scenes = []
        for idx, scene in enumerate(scenes):
            scene_num = scene.get("scene_number", idx + 1)
            visual_prompt = (scene.get("enhanced_visual_prompt") or scene.get("visual_prompt", "")).strip()

            if not visual_prompt:
                invalid_scenes.append(f"Scene {scene_num}: missing visual prompt")

        if invalid_scenes:
            error_msg = f"Validation failed: {', '.join(invalid_scenes)}"
            logger.error(f"[YouTubeRenderer] {error_msg}")
            task_manager.update_task_status(
                task_id, "failed", message=error_msg
            )
            return

        # Process each scene
        for idx, scene in enumerate(scenes):
            scene_num = scene.get("scene_number", idx + 1)
            progress = 10.0 + (idx / total_scenes) * 80.0  # 10-90% range

            try:
                task_manager.update_task_status(
                    task_id, "processing",
                    progress=progress,
                    message=f"Rendering scene {scene_num}/{total_scenes}..."
                )

                # Render individual scene
                scene_result = renderer.render_scene(
                    scene=scene,
                    video_plan=video_plan,
                    user_id=user_id,
                    resolution=resolution,
                    voice_id=voice_id
                )

                if scene_result and scene_result.get("success"):
                    scene_results.append(scene_result)
                    total_cost += scene_result.get("cost", 0.0)
                    logger.info(
                        f"[YouTubeRenderer] Scene {scene_num} rendered successfully, "
                        f"cost=${scene_result.get('cost', 0.0):.2f}"
                    )
                else:
                    error_msg = scene_result.get("message", "Unknown error") if scene_result else "Render failed"
                    logger.error(f"[YouTubeRenderer] Scene {scene_num} failed: {error_msg}")
                    task_manager.update_task_status(
                        task_id, "failed",
                        message=f"Scene {scene_num} render failed: {error_msg}"
                    )
                    return

            except Exception as e:
                logger.error(f"[YouTubeRenderer] Scene {scene_num} error: {e}", exc_info=True)
                task_manager.update_task_status(
                    task_id, "failed",
                    message=f"Scene {scene_num} error: {str(e)}"
                )
                return

        # Combine scenes if requested
        if combine_scenes and len(scene_results) > 1:
            task_manager.update_task_status(
                task_id, "processing", progress=95.0, message="Combining scenes..."
            )

            try:
                combine_result = renderer.combine_scenes(
                    scene_results=scene_results,
                    video_plan=video_plan,
                    user_id=user_id,
                    resolution=resolution
                )

                if combine_result and combine_result.get("success"):
                    final_result = combine_result
                    total_cost += combine_result.get("cost", 0.0)
                    logger.info(
                        f"[YouTubeRenderer] Scenes combined successfully, "
                        f"final cost=${total_cost:.2f}"
                    )
                else:
                    error_msg = combine_result.get("message", "Unknown error") if combine_result else "Combine failed"
                    logger.error(f"[YouTubeRenderer] Scene combination failed: {error_msg}")
                    task_manager.update_task_status(
                        task_id, "failed", message=f"Scene combination failed: {error_msg}"
                    )
                    return

            except Exception as e:
                logger.error(f"[YouTubeRenderer] Scene combination error: {e}", exc_info=True)
                task_manager.update_task_status(
                    task_id, "failed", message=f"Scene combination error: {str(e)}"
                )
                return
        else:
            # Single scene result
            final_result = scene_results[0] if scene_results else None

        # Success
        if final_result:
            task_manager.update_task_status(
                task_id, "completed",
                progress=100.0,
                message="Video render completed successfully",
                result=final_result,
                total_cost=total_cost
            )
            logger.info(
                f"[YouTubeRenderer] Task {task_id} completed successfully, "
                f"total cost=${total_cost:.2f}"
            )
        else:
            task_manager.update_task_status(
                task_id, "failed", message="No valid results produced"
            )

    except Exception as e:
        logger.error(f"[YouTubeRenderer] Task {task_id} failed with error: {e}", exc_info=True)
        task_manager.update_task_status(
            task_id, "failed", message=f"Render failed: {str(e)}"
        )


def _execute_scene_video_render_task(
    task_id: str,
    scene: Dict[str, Any],
    video_plan: Dict[str, Any],
    user_id: str,
    resolution: str,
    voice_id: str,
    generate_audio_enabled: bool = False,
):
    """Background task to render a single scene video."""
    logger.info(
        f"[YouTubeRenderer] Single scene background task started for task {task_id}, "
        f"user={user_id}"
    )

    # Verify task exists
    task_status = task_manager.get_task_status(task_id)
    if not task_status:
        logger.error(f"[YouTubeRenderer] Task {task_id} not found for scene render")
        return

    try:
        task_manager.update_task_status(
            task_id, "processing", progress=10.0, message="Starting scene render..."
        )

        renderer = get_youtube_renderer_service()

        # Render the scene
        result = renderer.render_scene(
            scene=scene,
            video_plan=video_plan,
            user_id=user_id,
            resolution=resolution,
            voice_id=voice_id,
            generate_audio_enabled=generate_audio_enabled
        )

        if result and result.get("success"):
            cost = result.get("cost", 0.0)
            task_manager.update_task_status(
                task_id, "completed",
                progress=100.0,
                message="Scene render completed",
                result=result,
                total_cost=cost
            )
            logger.info(
                f"[YouTubeRenderer] Scene task {task_id} completed, cost=${cost:.2f}"
            )
        else:
            error_msg = result.get("message", "Unknown error") if result else "Render failed"
            task_manager.update_task_status(
                task_id, "failed", message=f"Scene render failed: {error_msg}"
            )
            logger.error(f"[YouTubeRenderer] Scene task {task_id} failed: {error_msg}")

    except Exception as e:
        logger.error(f"[YouTubeRenderer] Scene task {task_id} error: {e}", exc_info=True)
        task_manager.update_task_status(
            task_id, "failed", message=f"Scene render error: {str(e)}"
        )


def _execute_combine_video_task(
    task_id: str,
    scene_video_urls: List[str],
    user_id: str,
    resolution: str,
    title: Optional[str] = None,
):
    """Background task to combine multiple scene videos."""
    logger.info(
        f"[YouTubeRenderer] Combine task started for task {task_id}, "
        f"videos={len(scene_video_urls)}, user={user_id}"
    )

    # Verify task exists
    task_status = task_manager.get_task_status(task_id)
    if not task_status:
        logger.error(f"[YouTubeRenderer] Task {task_id} not found for combine")
        return

    try:
        task_manager.update_task_status(
            task_id, "processing", progress=20.0, message="Starting video combination..."
        )

        renderer = get_youtube_renderer_service()

        # Combine the videos
        result = renderer.combine_scene_videos(
            video_urls=scene_video_urls,
            user_id=user_id,
            resolution=resolution,
            title=title
        )

        if result and result.get("success"):
            cost = result.get("cost", 0.0)
            task_manager.update_task_status(
                task_id, "completed",
                progress=100.0,
                message="Video combination completed",
                result=result,
                total_cost=cost
            )
            logger.info(
                f"[YouTubeRenderer] Combine task {task_id} completed, cost=${cost:.2f}"
            )
        else:
            error_msg = result.get("message", "Unknown error") if result else "Combine failed"
            task_manager.update_task_status(
                task_id, "failed", message=f"Video combination failed: {error_msg}"
            )
            logger.error(f"[YouTubeRenderer] Combine task {task_id} failed: {error_msg}")

    except Exception as e:
        logger.error(f"[YouTubeRenderer] Combine task {task_id} error: {e}", exc_info=True)
        task_manager.update_task_status(
            task_id, "failed", message=f"Video combination error: {str(e)}"
        )