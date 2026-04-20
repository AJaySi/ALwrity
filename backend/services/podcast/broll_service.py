"""
B-Roll Service - Orchestrator for programmatic B-roll video composition.

This service handles:
- Chart data extraction from research
- Individual scene B-roll video generation
- Final video composition from multiple B-roll scenes
"""

import json
import uuid
import os
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, List
from loguru import logger

# Import chart generators directly
from services.podcast.broll_composer import (
    make_bar_chart,
    make_horizontal_bar,
    make_line_trend,
    make_pie_chart,
    make_stacked_bar,
    make_bullet_overlay,
    make_insight_card,
)


class BrollService:
    """Orchestrates B-roll composition for podcast scenes."""
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize B-roll service.
        
        Args:
            output_dir: Base directory for B-roll output. Defaults to temp directory.
        """
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            self.output_dir = Path(tempfile.gettempdir()) / "broll_output"
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"[BrollService] Initialized with output directory: {self.output_dir}")
    
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
        
        Args:
            chart_data: Chart data dict with labels, before/after, etc.
            chart_type: Type of chart (bar_comparison, bar_horizontal, line_trend, pie, stacked_bar, bullet)
            title: Title for the chart
            subtitle: Optional subtitle at bottom
            
        Returns:
            Path to generated PNG file
        """
        resolved_chart_id = chart_id or uuid.uuid4().hex[:8]
        out_path = str(self.get_chart_preview_path(resolved_chart_id))
        
        try:
            if chart_type == "bar_comparison":
                make_bar_chart(chart_data, out_path, title, subtitle=subtitle)
            elif chart_type == "bar_horizontal":
                make_horizontal_bar(chart_data, out_path, title)
            elif chart_type == "line_trend":
                make_line_trend(chart_data, out_path, title)
            elif chart_type == "pie":
                make_pie_chart(chart_data, out_path, title)
            elif chart_type == "pie":
                make_pie_chart(chart_data, out_path, title)
            elif chart_type == "stacked_bar":
                make_stacked_bar(chart_data, out_path, title)
            elif chart_type == "bullet":
                bullet_points = chart_data.get("bullet_points", [])
                if bullet_points:
                    make_bullet_overlay(bullet_points, out_path)
                else:
                    logger.warning("[BrollService] No bullet points provided")
                    return ""
            else:
                logger.warning(f"[BrollService] Unknown chart type: {chart_type}")
                return ""
            
            logger.info(f"[BrollService] Chart preview generated: {out_path}")
            return out_path
            
        except Exception as e:
            logger.error(f"[BrollService] Failed to generate chart preview: {e}")
            return ""
    
    def generate_scene_broll(
        self,
        scene_id: str,
        key_insight: str,
        supporting_stat: str,
        chart_data: Optional[Dict[str, Any]],
        visual_cue: str,  # bar_chart_comparison, bullet_points, full_avatar
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
    
    def cleanup(self, file_paths: List[str] = None):
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


# Singleton instance for reuse
_broll_service_instance: Optional[BrollService] = None


def get_broll_service(output_dir: Optional[str] = None) -> BrollService:
    """Get or create B-roll service singleton."""
    global _broll_service_instance
    if _broll_service_instance is None:
        _broll_service_instance = BrollService(output_dir=output_dir)
    return _broll_service_instance
