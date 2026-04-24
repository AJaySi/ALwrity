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
from typing import Dict, Any, Optional, List, TYPE_CHECKING
from loguru import logger

# Import chart generators directly
from services.podcast.broll_composer import (
    Insight,
    SceneAssets,
    dispatch_scene,
    compose_video,
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
    
    def __init__(self, output_dir: Optional[str] = None, user_id: Optional[str] = None):
        """
        Initialize B-roll service.
        
        Args:
            output_dir: Base directory for B-roll output. Defaults to workspace chart directory.
            user_id: User ID for multi-tenant workspace isolation.
        """
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            self.output_dir = self._get_chart_dir(user_id)
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.warning(f"[BrollService] Initialized with output directory: {self.output_dir}")
    
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
        
        # Debug logging
        logger.warning(f"[BrollService] Generating: type={chart_type}, data keys={list(chart_data.keys())}")
        
        try:
            if chart_type == "bar_comparison":
                # Accept both formats: {labels, before, after} OR {labels, values}
                labels = chart_data.get("labels", [])
                before = chart_data.get("before", [])
                after = chart_data.get("after", [])
                # If using new format (labels, values), treat as single bar chart
                if not before and not after:
                    values = chart_data.get("values", [])
                    if values:
                        # Normalize to same length, truncating or padding as needed
                        n = min(len(labels), len(values))
                        labels = labels[:n]
                        before = [0] * n
                        after = values[:n]
                        # Create modified data dict with proper format for make_bar_chart
                        chart_data_for_render = {
                            "labels": labels,
                            "before": before,
                            "after": after
                        }
                    else:
                        chart_data_for_render = chart_data
                else:
                    chart_data_for_render = chart_data
                if not labels or (not before and not after):
                    logger.warning(f"[BrollService] Missing required data for bar_comparison: labels={len(labels)}, before={len(before)}, after={len(after)}")
                    return ""
                if len(labels) != len(before) or len(labels) != len(after):
                    logger.warning(f"[BrollService] Data shape mismatch: labels={len(labels)}, before={len(before)}, after={len(after)}")
                    return ""
                make_bar_chart(chart_data_for_render, out_path, title, subtitle=subtitle)
                logger.warning(f"[BrollService] bar_comparison rendered: {out_path}, exists={os.path.exists(out_path)}")
            elif chart_type == "bar_horizontal":
                labels = chart_data.get("labels", [])
                values = chart_data.get("values", [])
                if not labels or not values:
                    logger.warning("[BrollService] Missing required data for bar_horizontal")
                    return ""
                make_horizontal_bar(chart_data, out_path, title)
                logger.warning(f"[BrollService] bar_horizontal rendered: {out_path}, exists={os.path.exists(out_path)}")
            elif chart_type == "line_trend":
                labels = chart_data.get("labels", [])
                values = chart_data.get("values", [])
                if not labels or not values:
                    logger.warning("[BrollService] Missing required data for line_trend")
                    return ""
                make_line_trend(chart_data, out_path, title)
                logger.warning(f"[BrollService] line_trend rendered: {out_path}, exists={os.path.exists(out_path)}")
            elif chart_type == "pie":
                labels = chart_data.get("labels", [])
                values = chart_data.get("values", [])
                if not labels or not values:
                    logger.warning("[BrollService] Missing required data for pie")
                    return ""
                make_pie_chart(chart_data, out_path, title)
                logger.warning(f"[BrollService] pie rendered: {out_path}, exists={os.path.exists(out_path)}")
            elif chart_type == "stacked_bar":
                labels = chart_data.get("labels", [])
                segments = chart_data.get("segments", [])
                if not labels or not segments:
                    logger.warning("[BrollService] Missing required data for stacked_bar")
                    return ""
                make_stacked_bar(chart_data, out_path, title)
                logger.warning(f"[BrollService] stacked_bar rendered: {out_path}, exists={os.path.exists(out_path)}")
            elif chart_type == "bullet" or chart_type == "bullet_points":
                # Accept both: bullet_points OR labels
                bullet_points = chart_data.get("bullet_points", [])
                # If using new format, use labels as bullet points
                if not bullet_points:
                    bullet_points = chart_data.get("labels", [])
                if not bullet_points:
                    labels_fallback = chart_data.get("labels", [])
                    if labels_fallback:
                        bullet_points = labels_fallback
                if bullet_points:
                    make_bullet_overlay(bullet_points, out_path)
                    logger.warning(f"[BrollService] bullet_points rendered: {out_path}, exists={os.path.exists(out_path)}")
                else:
                    logger.warning("[BrollService] No bullet points provided")
                    return ""
            else:
                logger.warning(f"[BrollService] Unknown chart type: {chart_type}, falling back to bar_comparison")
                # Try bar_comparison as fallback
                try:
                    make_bar_chart(chart_data, out_path, title, subtitle=subtitle)
                    return out_path
                except Exception as fallback_err:
                    logger.warning(f"[BrollService] Fallback also failed: {fallback_err}")
                    return ""
            
            logger.warning(f"[BrollService] Chart preview generated: {out_path}, exists={os.path.exists(out_path) if out_path else 'N/A'}")
            
            # Add source attribution overlay if present
            source = chart_data.get("source", "").strip()
            if source and out_path and os.path.exists(out_path):
                try:
                    from PIL import Image as PILImage, ImageDraw, ImageFont
                    img = PILImage.open(out_path).convert("RGBA")
                    draw = ImageDraw.Draw(img)
                    source_text = f"Source: {source[:80]}"
                    try:
                        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
                    except (OSError, IOError):
                        try:
                            font = ImageFont.truetype("arial.ttf", 11)
                        except (OSError, IOError):
                            font = ImageFont.load_default()
                    text_bbox = draw.textbbox((0, 0), source_text, font=font)
                    text_w = text_bbox[2] - text_bbox[0]
                    text_h = text_bbox[3] - text_bbox[1]
                    x = img.width - text_w - 12
                    y = img.height - text_h - 8
                    draw.rectangle([x - 4, y - 2, x + text_w + 4, y + text_h + 2], fill=(0, 0, 0, 140))
                    draw.text((x, y), source_text, fill=(200, 200, 200, 220), font=font)
                    img.save(out_path)
                except Exception as src_err:
                    logger.warning(f"[BrollService] Source overlay failed (non-fatal): {src_err}")
            
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
