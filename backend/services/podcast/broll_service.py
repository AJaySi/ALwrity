"""
B-Roll Service - Orchestrator for programmatic B-roll video composition.

This service handles:
- Chart data extraction from research
- Individual scene B-roll video generation
- Final video composition from multiple B-roll scenes

Chart preview generation is delegated to the shared ChartService.
"""

import json
import uuid
import os
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, List, TYPE_CHECKING
from loguru import logger

# Import video compositing from broll_composer
from services.podcast.broll_composer import (
    Insight,
    SceneAssets,
    dispatch_scene,
    compose_video,
    make_insight_card,
)

# Import shared chart service for preview generation
from services.chart_service import ChartService, get_chart_service


class BrollService:
    """Orchestrates B-roll composition for podcast scenes."""
    
    def __init__(self, output_dir: Optional[str] = None, user_id: Optional[str] = None):
        """
        Initialize B-roll service.
        
        Args:
            output_dir: Base directory for B-roll output. Defaults to workspace chart directory.
            user_id: User ID for multi-tenant workspace isolation.
        """
        self._user_id = user_id
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            self.output_dir = self._get_chart_dir(user_id)
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"[BrollService] Initialized with output directory: {self.output_dir}")
    
    def _get_chart_dir(self, user_id: Optional[str] = None) -> Path:
        """Get chart directory from podcast constants (workspace-aware)."""
        from api.podcast.constants import get_podcast_media_dir
        return get_podcast_media_dir("chart", user_id, ensure_exists=True)
    
    def get_output_path(self, filename: str) -> Path:
        """Get output path for a file."""
        return self.output_dir / filename

    def get_chart_preview_filename(self, chart_id: str) -> str:
        """Build deterministic chart preview filename from chart ID."""
        return f"chart_preview_{chart_id}.png"

    def get_chart_preview_path(self, chart_id: str) -> Path:
        """Get deterministic chart preview path from chart ID."""
        return self.get_output_path(self.get_chart_preview_filename(chart_id))
    
    def generate_chart_preview(
        self,
        chart_data: Dict[str, Any],
        chart_type: str = "bar_comparison",
        title: str = "",
        subtitle: str = "",
        chart_id: Optional[str] = None,
    ) -> str:
        """
        Generate a chart PNG preview (static, for Write phase).
        
        Delegates to ChartService for rendering, then returns the local file path.
        """
        resolved_chart_id = chart_id or uuid.uuid4().hex[:8]
        
        logger.info(f"[BrollService] Generating chart preview: type={chart_type}, id={resolved_chart_id}")
        
        chart_svc = get_chart_service(user_id=self._user_id)
        result = chart_svc.generate_chart(
            chart_data=chart_data,
            chart_type=chart_type,
            title=title,
            subtitle=subtitle or "",
            chart_id=resolved_chart_id,
        )
        
        return result.get("path", "")
    
    def generate_scene_broll(
        self,
        scene_id: str,
        key_insight: str,
        supporting_stat: str,
        chart_data: Optional[Dict[str, Any]],
        visual_cue: str,  # bar_comparison, bar_horizontal, line_trend, pie, stacked_bar, bullet_points, full_avatar
        duration: float,
        background_img_path: str,
        avatar_video_path: Optional[str] = None,
    ) -> str:
        """
        Generate a B-roll video for a single scene.
        
        Args:
            scene_id: Scene identifier
            key_insight: Main insight text for overlay
            supporting_stat: Supporting statistic text
            chart_data: Chart data dict (optional)
            visual_cue: Type of scene to build
            duration: Scene duration in seconds
            background_img_path: Path to background image
            avatar_video_path: Path to avatar video (optional)
            
        Returns:
            Path to generated video file
        """
        scene_id_safe = scene_id.replace(" ", "_").replace("/", "_")
        out_path = str(self.get_output_path(f"broll_{scene_id_safe}.mp4"))
        
        try:
            insight = Insight(
                key_insight=key_insight,
                supporting_stat=supporting_stat,
                visual_cue=visual_cue,
                audio_tone="neutral",
                chart_data=chart_data or {},
                duration=duration,
            )
            
            assets = SceneAssets(
                background_img=background_img_path,
                avatar_video=avatar_video_path,
            )
            
            # Generate the scene
            scene = dispatch_scene(insight, assets)
            
            # Write video
            compose_video([scene], output_path=out_path)
            
            logger.info(f"[BrollService] B-roll scene generated: {out_path}")
            return out_path
            
        except Exception as e:
            logger.error(f"[BrollService] Failed to generate B-roll scene: {e}")
            raise
    
    def compose_final_video(
        self,
        video_paths: List[str],
        output_filename: str,
        fade_dur: float = 0.5,
        fps: int = 24,
    ) -> str:
        """
        Compose multiple B-roll scene videos into final video.
        
        Args:
            video_paths: List of video file paths to compose
            output_filename: Output filename
            fade_dur: Crossfade duration between scenes
            fps: Output FPS
            
        Returns:
            Path to final composed video
        """
        out_path = str(self.get_output_path(output_filename))
        
        try:
            scenes = []
            for video_path in video_paths:
                from moviepy import VideoFileClip
                clip = VideoFileClip(video_path)
                scenes.append(clip)
            
            if not scenes:
                raise ValueError("No video clips provided")
            
            # Use crossfade_concat from broll_composer
            from services.podcast.broll_composer import crossfade_concat
            
            final = crossfade_concat(scenes, fade_dur=fade_dur)
            
            final.write_videofile(
                out_path,
                fps=fps,
                codec="libx264",
                audio_codec="aac",
                threads=4,
                preset="fast",
                logger=None,
            )
            
            # Close clips
            for clip in scenes:
                clip.close()
            
            logger.info(f"[BrollService] Final video composed: {out_path}")
            return out_path
            
        except Exception as e:
            logger.error(f"[BrollService] Failed to compose final video: {e}")
            raise
    
    def cleanup(self, file_paths: Optional[List[str]] = None):
        """
        Clean up temporary B-roll files.
        
        Args:
            file_paths: Specific files to delete. If None, cleans output directory.
        """
        if file_paths:
            for path in file_paths:
                try:
                    if os.path.exists(path):
                        os.remove(path)
                        logger.debug(f"[BrollService] Removed: {path}")
                except Exception as e:
                    logger.warning(f"[BrollService] Failed to remove {path}: {e}")
        else:
            # Clean entire output directory
            for file in self.output_dir.glob("*"):
                try:
                    file.unlink()
                except Exception as e:
                    logger.warning(f"[BrollService] Failed to remove {file}: {e}")


# Per-user service instances for multi-tenant isolation
_broll_service_instances: Dict[str, BrollService] = {}


def get_broll_service(output_dir: Optional[str] = None, user_id: Optional[str] = None) -> BrollService:
    """
    Get or create B-roll service for the given user.
    
    For multi-tenant isolation, pass user_id to get user-specific directory.
    """
    if output_dir:
        return BrollService(output_dir=output_dir)
    
    # Create per-user instance based on user_id
    cache_key = user_id or "default"
    if cache_key not in _broll_service_instances:
        _broll_service_instances[cache_key] = BrollService(user_id=user_id)
    return _broll_service_instances[cache_key]
