"""
Video Generation Service for Story Writer

Combines images and audio into animated video clips using MoviePy.
"""

import os
import uuid
from typing import List, Dict, Any, Optional
from pathlib import Path
from loguru import logger
from fastapi import HTTPException


class StoryVideoGenerationService:
    """Service for generating videos from story scenes, images, and audio."""
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize the video generation service.
        
        Parameters:
            output_dir (str, optional): Directory to save generated videos.
                                      Defaults to 'backend/story_videos' if not provided.
        """
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            # Default to backend/story_videos directory
            base_dir = Path(__file__).parent.parent.parent
            self.output_dir = base_dir / "story_videos"
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"[StoryVideoGeneration] Initialized with output directory: {self.output_dir}")
    
    def _generate_video_filename(self, story_title: str = "story") -> str:
        """Generate a unique filename for a story video."""
        # Clean story title for filename
        clean_title = "".join(c if c.isalnum() or c in ('-', '_') else '_' for c in story_title[:30])
        unique_id = str(uuid.uuid4())[:8]
        return f"story_{clean_title}_{unique_id}.mp4"
    
    def save_scene_video(self, video_bytes: bytes, scene_number: int, user_id: str) -> Dict[str, str]:
        """
        Save individual scene video bytes to file.
        
        Parameters:
            video_bytes: Raw video file bytes (mp4/webm format)
            scene_number: Scene number for naming
            user_id: Clerk user ID for naming
        
        Returns:
            Dict[str, str]: Video metadata with video_url and video_filename
        """
        try:
            # Generate filename with scene number and user ID
            clean_user_id = "".join(c if c.isalnum() or c in ('-', '_') else '_' for c in user_id[:16])
            timestamp = str(uuid.uuid4())[:8]
            filename = f"scene_{scene_number}_{clean_user_id}_{timestamp}.mp4"
            
            video_path = self.output_dir / filename
            
            # Write video bytes to file
            with open(video_path, 'wb') as f:
                f.write(video_bytes)
            
            file_size = video_path.stat().st_size
            logger.info(f"[StoryVideoGeneration] Saved scene {scene_number} video: {filename} ({file_size} bytes)")
            
            # Generate URL path (relative to /api/story/videos/)
            video_url = f"/api/story/videos/{filename}"
            
            return {
                "video_filename": filename,
                "video_url": video_url,
                "video_path": str(video_path),
                "file_size": file_size
            }
            
        except Exception as e:
            logger.error(f"[StoryVideoGeneration] Error saving scene video: {e}", exc_info=True)
            raise RuntimeError(f"Failed to save scene video: {str(e)}") from e
    
    def generate_scene_video(
        self,
        scene: Dict[str, Any],
        image_path: str,
        audio_path: str,
        user_id: str,
        duration: Optional[float] = None,
        fps: int = 24
    ) -> Dict[str, Any]:
        """
        Generate a video clip for a single story scene.
        
        Parameters:
            scene (Dict[str, Any]): Scene data.
            image_path (str): Path to the scene image file.
            audio_path (str): Path to the scene audio file.
            user_id (str): Clerk user ID for subscription checking (for future usage tracking).
            duration (float, optional): Video duration in seconds. If None, uses audio duration.
            fps (int): Frames per second for video (default: 24).
        
        Returns:
            Dict[str, Any]: Video metadata including file path, URL, and scene info.
        """
        scene_number = scene.get("scene_number", 0)
        scene_title = scene.get("title", "Untitled")
        
        try:
            logger.info(f"[StoryVideoGeneration] Generating video for scene {scene_number}: {scene_title}")
            
            # Import MoviePy
            try:
                # MoviePy v2.x exposes classes at top-level (moviepy.ImageClip, etc)
                from moviepy import ImageClip, AudioFileClip, concatenate_videoclips
            except Exception as _imp_err:
                # Detailed diagnostics to help users fix environment issues
                try:
                    import sys as _sys
                    import platform as _platform
                    import importlib
                    mv = None
                    imv = None
                    ff_path = "unresolved"
                    try:
                        mv = importlib.import_module("moviepy")
                    except Exception:
                        pass
                    try:
                        imv = importlib.import_module("imageio")
                    except Exception:
                        pass
                    try:
                        import imageio_ffmpeg as _iff
                        ff_path = _iff.get_ffmpeg_exe()
                    except Exception:
                        pass
                    logger.error(
                        "[StoryVideoGeneration] MoviePy import failed. "
                        f"py={_sys.executable} plat={_platform.platform()} "
                        f"moviepy_ver={getattr(mv,'__version__', 'NA')} "
                        f"imageio_ver={getattr(imv,'__version__', 'NA')} "
                        f"ffmpeg_path={ff_path} err={_imp_err}"
                    )
                except Exception:
                    # best-effort diagnostics
                    pass
                logger.error("[StoryVideoGeneration] MoviePy not installed. Install with: pip install moviepy imageio imageio-ffmpeg")
                raise RuntimeError("MoviePy is not installed. Please install it to generate videos.")
            
            # Load image and audio
            image_file = Path(image_path)
            audio_file = Path(audio_path)
            
            if not image_file.exists():
                raise FileNotFoundError(f"Image not found: {image_path}")
            if not audio_file.exists():
                raise FileNotFoundError(f"Audio not found: {audio_path}")
            
            # Load audio to get duration
            audio_clip = AudioFileClip(str(audio_file))
            audio_duration = audio_clip.duration
            
            # Use provided duration or audio duration
            video_duration = duration if duration is not None else audio_duration
            
            # Create image clip (MoviePy v2: use with_* API)
            image_clip = ImageClip(str(image_file)).with_duration(video_duration)
            image_clip = image_clip.with_fps(fps)
            
            # Set audio to image clip
            video_clip = image_clip.with_audio(audio_clip)
            
            # Generate video filename
            video_filename = f"scene_{scene_number}_{scene_title.replace(' ', '_').replace('/', '_')[:50]}_{uuid.uuid4().hex[:8]}.mp4"
            video_path = self.output_dir / video_filename
            
            # Write video file
            video_clip.write_videofile(
                str(video_path),
                fps=fps,
                codec='libx264',
                audio_codec='aac',
                preset='medium',
                threads=4,
                logger=None  # Disable MoviePy's default logger
            )
            
            # Clean up clips
            video_clip.close()
            audio_clip.close()
            image_clip.close()
            
            # Get file size
            file_size = video_path.stat().st_size
            
            logger.info(f"[StoryVideoGeneration] Saved video to: {video_path} ({file_size} bytes)")
            
            # Return video metadata
            return {
                "scene_number": scene_number,
                "scene_title": scene_title,
                "video_path": str(video_path),
                "video_filename": video_filename,
                "video_url": f"/api/story/videos/{video_filename}",  # API endpoint to serve videos
                "duration": video_duration,
                "fps": fps,
                "file_size": file_size,
            }
            
        except HTTPException:
            # Re-raise HTTPExceptions (e.g., 429 subscription limit)
            raise
        except Exception as e:
            logger.error(f"[StoryVideoGeneration] Error generating video for scene {scene_number}: {e}")
            raise RuntimeError(f"Failed to generate video for scene {scene_number}: {str(e)}") from e
    
    def generate_story_video(
        self,
        scenes: List[Dict[str, Any]],
        image_paths: List[Optional[str]],
        audio_paths: List[str],
        user_id: str,
        story_title: str = "Story",
        fps: int = 24,
        transition_duration: float = 0.5,
        progress_callback: Optional[callable] = None,
        video_paths: Optional[List[Optional[str]]] = None
    ) -> Dict[str, Any]:
        """
        Generate a complete story video from multiple scenes.
        
        Parameters:
            scenes (List[Dict[str, Any]]): List of scene data.
            image_paths (List[Optional[str]]): List of image file paths (None if scene has animated video).
            audio_paths (List[str]): List of audio file paths for each scene.
            user_id (str): Clerk user ID for subscription checking.
            story_title (str): Title of the story (default: "Story").
            fps (int): Frames per second for video (default: 24).
            transition_duration (float): Duration of transitions between scenes in seconds (default: 0.5).
            progress_callback (callable, optional): Callback function for progress updates.
            video_paths (Optional[List[Optional[str]]]): List of animated video file paths (None if scene has static image).
        
        Returns:
            Dict[str, Any]: Video metadata including file path, URL, and story info.
        """
        if not scenes or not audio_paths:
            raise ValueError("Scenes and audio paths are required")
        
        if len(scenes) != len(audio_paths):
            raise ValueError("Number of scenes and audio paths must match")
        
        # Ensure video_paths is a list and matches scenes length
        if video_paths is None:
            video_paths = [None] * len(scenes)
        elif len(video_paths) != len(scenes):
            video_paths = video_paths + [None] * (len(scenes) - len(video_paths))
        
        logger.debug(f"[StoryVideoGeneration] video_paths length: {len(video_paths)}, scenes length: {len(scenes)}")
        
        try:
            logger.info(f"[StoryVideoGeneration] Generating story video for {len(scenes)} scenes")
            
            # Import MoviePy
            try:
                from moviepy import ImageClip, AudioFileClip, concatenate_videoclips
            except Exception as _imp_err:
                # Detailed diagnostics to help users fix environment issues
                try:
                    import sys as _sys
                    import platform as _platform
                    import importlib
                    mv = None
                    imv = None
                    ff_path = "unresolved"
                    try:
                        mv = importlib.import_module("moviepy")
                    except Exception:
                        pass
                    try:
                        imv = importlib.import_module("imageio")
                    except Exception:
                        pass
                    try:
                        import imageio_ffmpeg as _iff
                        ff_path = _iff.get_ffmpeg_exe()
                    except Exception:
                        pass
                    logger.error(
                        "[StoryVideoGeneration] MoviePy import failed. "
                        f"py={_sys.executable} plat={_platform.platform()} "
                        f"moviepy_ver={getattr(mv,'__version__', 'NA')} "
                        f"imageio_ver={getattr(imv,'__version__', 'NA')} "
                        f"ffmpeg_path={ff_path} err={_imp_err}"
                    )
                except Exception:
                    pass
                logger.error("[StoryVideoGeneration] MoviePy not installed. Install with: pip install moviepy imageio imageio-ffmpeg")
                raise RuntimeError("MoviePy is not installed. Please install it to generate videos.")
            
            scene_clips = []
            total_duration = 0.0
            
            # Import VideoFileClip for animated videos
            try:
                from moviepy import VideoFileClip
            except ImportError:
                VideoFileClip = None
            
            for idx, (scene, image_path, audio_path, video_path) in enumerate(zip(scenes, image_paths, audio_paths, video_paths)):
                try:
                    scene_number = scene.get("scene_number", idx + 1)
                    scene_title = scene.get("title", "Untitled")
                    
                    logger.info(f"[StoryVideoGeneration] Processing scene {scene_number}/{len(scenes)}: {scene_title}")
                    logger.debug(f"[StoryVideoGeneration] Scene {scene_number} paths - video: {video_path}, audio: {audio_path}, image: {image_path}")
                    
                    # Prefer animated video if available
                    # Check video_path is not None and is a valid string before calling Path()
                    if video_path is not None and isinstance(video_path, (str, Path)) and video_path and Path(video_path).exists():
                        logger.info(f"[StoryVideoGeneration] Using animated video for scene {scene_number}: {video_path}")
                        # Load animated video
                        if VideoFileClip is None:
                            raise RuntimeError("VideoFileClip not available - MoviePy may not be fully installed")
                        video_clip = VideoFileClip(str(video_path))
                        
                        # Handle audio: use embedded audio if no separate audio_path provided
                        if audio_path is not None and isinstance(audio_path, (str, Path)) and audio_path and Path(audio_path).exists():
                            # Load separate audio file and replace video's audio
                            logger.info(f"[StoryVideoGeneration] Replacing video audio with separate audio file: {audio_path}")
                            audio_clip = AudioFileClip(str(audio_path))
                            audio_duration = audio_clip.duration
                            video_clip = video_clip.with_audio(audio_clip)
                            # Match duration to audio if needed
                            if video_clip.duration > audio_duration:
                                video_clip = video_clip.subclip(0, audio_duration)
                            elif video_clip.duration < audio_duration:
                                # Loop the video if it's shorter than audio
                                loops_needed = int(audio_duration / video_clip.duration) + 1
                                video_clip = concatenate_videoclips([video_clip] * loops_needed).subclip(0, audio_duration)
                                video_clip = video_clip.with_audio(audio_clip)
                        else:
                            # Use embedded audio from video
                            logger.info(f"[StoryVideoGeneration] Using embedded audio from video for scene {scene_number}")
                            audio_duration = video_clip.duration
                            # Video already has audio, no need to replace
                        
                        scene_clips.append(video_clip)
                        total_duration += audio_duration
                    elif audio_path is not None and isinstance(audio_path, (str, Path)) and audio_path and Path(audio_path).exists():
                        # No video, but we have audio - use with image or create blank
                        audio_file = Path(audio_path)
                        audio_clip = AudioFileClip(str(audio_file))
                        audio_duration = audio_clip.duration
                        
                        if image_path is not None and isinstance(image_path, (str, Path)) and image_path and Path(image_path).exists():
                            # Fall back to static image with audio
                            logger.info(f"[StoryVideoGeneration] Using static image for scene {scene_number}: {image_path}")
                            image_file = Path(image_path)
                            # Create image clip (MoviePy v2: use with_* API)
                            image_clip = ImageClip(str(image_file)).with_duration(audio_duration)
                            image_clip = image_clip.with_fps(fps)
                            # Set audio to image clip
                            video_clip = image_clip.with_audio(audio_clip)
                            scene_clips.append(video_clip)
                            total_duration += audio_duration
                        else:
                            logger.warning(f"[StoryVideoGeneration] Audio provided but no video or image for scene {scene_number}, skipping")
                            continue
                    else:
                        logger.warning(f"[StoryVideoGeneration] No video, audio, or image found for scene {scene_number}, skipping")
                        continue
                    
                    # Call progress callback if provided
                    if progress_callback:
                        progress = ((idx + 1) / len(scenes)) * 90  # Reserve 10% for final composition
                        progress_callback(progress, f"Processed scene {scene_number}/{len(scenes)}")
                    
                    logger.info(f"[StoryVideoGeneration] Processed scene {idx + 1}/{len(scenes)}")
                    
                except Exception as e:
                    logger.error(
                        f"[StoryVideoGeneration] Failed to process scene {idx + 1} ({scene_number}): {e}\n"
                        f"  video_path: {video_path} (type: {type(video_path)})\n"
                        f"  audio_path: {audio_path} (type: {type(audio_path)})\n"
                        f"  image_path: {image_path} (type: {type(image_path)})"
                    )
                    # Continue with next scene instead of failing completely
                    continue
            
            if not scene_clips:
                raise RuntimeError("No valid scene clips were created")
            
            # Concatenate all scene clips
            logger.info(f"[StoryVideoGeneration] Concatenating {len(scene_clips)} scene clips")
            final_video = concatenate_videoclips(scene_clips, method="compose")
            
            # Generate video filename
            video_filename = self._generate_video_filename(story_title)
            video_path = self.output_dir / video_filename
            
            # Call progress callback
            if progress_callback:
                progress_callback(95, "Rendering final video...")
            
            # Write video file
            final_video.write_videofile(
                str(video_path),
                fps=fps,
                codec='libx264',
                audio_codec='aac',
                preset='medium',
                threads=4,
                logger=None  # Disable MoviePy's default logger
            )
            
            # Get file size
            file_size = video_path.stat().st_size
            
            # Clean up clips
            final_video.close()
            for clip in scene_clips:
                clip.close()
            
            # Call progress callback
            if progress_callback:
                progress_callback(100, "Video generation complete!")
            
            logger.info(f"[StoryVideoGeneration] Saved story video to: {video_path} ({file_size} bytes)")
            
            # Return video metadata
            return {
                "video_path": str(video_path),
                "video_filename": video_filename,
                "video_url": f"/api/story/videos/{video_filename}",  # API endpoint to serve videos
                "duration": total_duration,
                "fps": fps,
                "file_size": file_size,
                "num_scenes": len(scene_clips),
            }
            
        except HTTPException:
            # Re-raise HTTPExceptions (e.g., 429 subscription limit)
            raise
        except Exception as e:
            logger.error(f"[StoryVideoGeneration] Error generating story video: {e}")
            raise RuntimeError(f"Failed to generate story video: {str(e)}") from e

