"""
Podcast Video Combination Service

Dedicated service for combining podcast scene videos into final episodes.
Separate from StoryVideoGenerationService to avoid breaking story writer functionality.
"""

import uuid
import warnings
import time
import threading
from typing import List, Dict, Any, Optional
from pathlib import Path
from loguru import logger


class PodcastVideoCombinationService:
    """Service for combining podcast scene videos into final episodes."""
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize the podcast video combination service.
        
        Parameters:
            output_dir (str, optional): Directory to save combined videos.
                                      Defaults to 'backend/podcast_videos/Final_Videos' if not provided.
        """
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            # Default to root/data/media/podcast_videos/Final_Videos directory
            base_dir = Path(__file__).resolve().parents[3]
            self.output_dir = base_dir / "data" / "media" / "podcast_videos" / "Final_Videos"
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"[PodcastVideoCombination] Initialized with output directory: {self.output_dir}")
    
    def combine_videos(
        self,
        video_paths: List[str],
        podcast_title: str,
        fps: int = 30,
        progress_callback: Optional[callable] = None,
    ) -> Dict[str, Any]:
        """
        Combine multiple video files into a single final podcast video.
        
        This method is specifically designed for podcast videos that already have
        embedded audio. It does not require separate audio files.
        
        Parameters:
            video_paths (List[str]): List of video file paths to combine.
            podcast_title (str): Title of the podcast episode.
            fps (int): Frames per second for output video (default: 30).
            progress_callback (callable, optional): Callback function for progress updates.
                                                    Signature: callback(progress: float, message: str)
        
        Returns:
            Dict[str, Any]: Video metadata including file path, URL, duration, and file size.
        
        Raises:
            ValueError: If no valid video files are provided.
            RuntimeError: If video combination fails.
        """
        if not video_paths:
            raise ValueError("No video paths provided")
        
        # Validate all video files exist
        valid_video_paths = []
        for video_path in video_paths:
            path = Path(video_path)
            if path.exists() and path.is_file():
                valid_video_paths.append(str(path))
            else:
                logger.warning(f"[PodcastVideoCombination] Video not found: {video_path}")
        
        if not valid_video_paths:
            raise ValueError("No valid video files found to combine")
        
        logger.info(f"[PodcastVideoCombination] Combining {len(valid_video_paths)} videos")
        
        try:
            # Import MoviePy
            try:
                from moviepy import VideoFileClip, concatenate_videoclips
            except Exception as e:
                logger.error(f"[PodcastVideoCombination] MoviePy not installed: {e}")
                raise RuntimeError("MoviePy is not installed. Please install it to combine videos.")
            
            # Suppress MoviePy warnings about incomplete frames (common with some video encodings)
            warnings.filterwarnings("ignore", category=UserWarning, module="moviepy")
            
            if progress_callback:
                progress_callback(10.0, "Loading video clips...")
            
            # Load all video clips
            video_clips = []
            total_duration = 0.0
            
            for idx, video_path in enumerate(valid_video_paths):
                try:
                    logger.info(f"[PodcastVideoCombination] Loading video {idx + 1}/{len(valid_video_paths)}: {video_path}")
                    
                    # Load video clip with error handling for incomplete files
                    # MoviePy will use the last valid frame if frames are missing at the end
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore", UserWarning)
                        video_clip = VideoFileClip(str(video_path))
                    
                    # Validate clip was loaded successfully
                    if video_clip.duration <= 0:
                        logger.warning(f"[PodcastVideoCombination] Video {video_path} has invalid duration, skipping")
                        video_clip.close()
                        continue
                    
                    # Videos already have embedded audio, no need to replace
                    video_clips.append(video_clip)
                    total_duration += video_clip.duration
                    
                    if progress_callback:
                        progress = 10.0 + ((idx + 1) / len(valid_video_paths)) * 60.0
                        progress_callback(progress, f"Loaded video {idx + 1}/{len(valid_video_paths)}")
                    
                except Exception as e:
                    logger.error(f"[PodcastVideoCombination] Failed to load video {video_path}: {e}")
                    # Continue with other videos instead of failing completely
                    continue
            
            if not video_clips:
                raise RuntimeError("No valid video clips were loaded")
            
            logger.info(f"[PodcastVideoCombination] Loaded {len(video_clips)} clips, total duration: {total_duration:.2f}s")
            
            if progress_callback:
                progress_callback(75.0, f"Concatenating {len(video_clips)} videos ({total_duration:.1f}s total)...")
            
            # Concatenate all video clips
            logger.info(f"[PodcastVideoCombination] Concatenating {len(video_clips)} video clips (total duration: {total_duration:.2f}s)")
            final_video = concatenate_videoclips(video_clips, method="compose")
            logger.info(f"[PodcastVideoCombination] Concatenation complete, final video duration: {final_video.duration:.2f}s")
            
            # Generate output filename
            video_filename = self._generate_video_filename(podcast_title)
            video_path = self.output_dir / video_filename
            
            if progress_callback:
                progress_callback(85.0, f"Rendering final video ({total_duration:.1f}s total)...")
            
            # Write final video file
            logger.info(
                f"[PodcastVideoCombination] Rendering final video to: {video_path} "
                f"(duration: {total_duration:.2f}s, {len(video_clips)} clips)"
            )
            
            # Use faster preset for quicker encoding (still good quality)
            # 'ultrafast' is fastest but lower quality, 'fast' is good balance
            encoding_preset = 'fast'  # Faster than 'medium' but still good quality
            
            # Suppress warnings during video writing as well
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                
                # Write video with optimized settings
                # Note: write_videofile is blocking and can take several minutes for longer videos
                # Estimated time: ~1-2 minutes per minute of video content
                estimated_time_minutes = max(1, int(total_duration / 60) * 2)
                logger.info(
                    f"[PodcastVideoCombination] Starting video encoding "
                    f"(estimated time: ~{estimated_time_minutes} minutes for {total_duration:.1f}s video)..."
                )
                
                start_time = time.time()
                
                # Start a thread to update progress periodically during encoding
                # Since write_videofile is blocking, we'll simulate progress
                progress_thread = None
                encoding_done = threading.Event()
                
                if progress_callback:
                    def update_progress_periodically():
                        """Update progress every 5 seconds during encoding"""
                        base_progress = 87.0
                        max_progress = 98.0
                        progress_range = max_progress - base_progress
                        update_interval = 5.0  # Update every 5 seconds
                        elapsed = 0.0
                        
                        try:
                            while not encoding_done.is_set():
                                elapsed += update_interval
                                # Simulate progress: start at 87%, gradually increase to 98%
                                # Use logarithmic curve to slow down as we approach completion
                                progress = base_progress + (progress_range * min(1.0, elapsed / (estimated_time_minutes * 60)))
                                progress = min(max_progress, progress)
                                
                                remaining_minutes = max(0, estimated_time_minutes - int(elapsed / 60))
                                message = f"Encoding video... ({remaining_minutes} min remaining)"
                                if remaining_minutes == 0:
                                    message = "Finalizing video..."
                                
                                try:
                                    progress_callback(progress, message)
                                except Exception as e:
                                    logger.warning(f"[PodcastVideoCombination] Error in progress callback: {e}")
                                    break
                                
                                # Use wait with timeout instead of sleep to check event more frequently
                                if encoding_done.wait(timeout=update_interval):
                                    break  # Event was set, exit immediately
                        except Exception as e:
                            logger.warning(f"[PodcastVideoCombination] Error in progress thread: {e}")
                    
                    progress_thread = threading.Thread(target=update_progress_periodically, daemon=True)
                    progress_thread.start()
                
                # Write video file - this is the blocking operation
                logger.info(f"[PodcastVideoCombination] Calling write_videofile...")
                try:
                    final_video.write_videofile(
                        str(video_path),
                        fps=fps,
                        codec='libx264',
                        audio_codec='aac',
                        preset=encoding_preset,  # Faster encoding
                        threads=4,
                        logger=None,  # Disable MoviePy's default logger
                        bitrate=None,  # Let encoder choose optimal bitrate
                        audio_bitrate='192k',  # Good quality audio
                        temp_audiofile=str(video_path.with_suffix('.m4a')),  # Temporary audio file
                        remove_temp=True,  # Clean up temp files
                        write_logfile=False,  # Don't write log file
                    )
                    logger.info(f"[PodcastVideoCombination] write_videofile completed successfully")
                except Exception as write_error:
                    logger.error(f"[PodcastVideoCombination] Error in write_videofile: {write_error}")
                    # Check if file was created despite error
                    if video_path.exists() and video_path.stat().st_size > 0:
                        logger.warning(f"[PodcastVideoCombination] Video file exists despite error, continuing...")
                    else:
                        raise
                finally:
                    # Always signal that encoding is done - don't wait for progress thread
                    if progress_thread:
                        encoding_done.set()
                        # Don't join - let it finish on its own (daemon thread)
                
                elapsed_time = time.time() - start_time
                logger.info(
                    f"[PodcastVideoCombination] Video encoding completed in {elapsed_time:.1f} seconds "
                    f"({elapsed_time/60:.1f} minutes)"
                )
                
                if progress_callback:
                    progress_callback(99.0, "Video encoding complete! Finalizing...")
            
            # Verify file was created and get file size
            # Use retry logic in case file is still being written
            max_retries = 5
            file_size = 0
            for retry in range(max_retries):
                if video_path.exists():
                    file_size = video_path.stat().st_size
                    if file_size > 0:
                        break
                if retry < max_retries - 1:
                    logger.info(f"[PodcastVideoCombination] Waiting for video file to be written (retry {retry + 1}/{max_retries})...")
                    time.sleep(1)
            
            if not video_path.exists():
                raise RuntimeError(f"Video file was not created: {video_path}")
            
            if file_size == 0:
                raise RuntimeError(f"Video file is empty: {video_path}")
            
            logger.info(f"[PodcastVideoCombination] Video file verified: {video_path} ({file_size} bytes)")
            
            # Clean up clips immediately but quickly - don't block
            # Close clips synchronously but with timeout protection
            try:
                final_video.close()
            except Exception as e:
                logger.warning(f"[PodcastVideoCombination] Error closing final video clip: {e}")
            
            # Close individual clips quickly
            for clip in video_clips:
                try:
                    clip.close()
                except Exception as e:
                    logger.warning(f"[PodcastVideoCombination] Error closing video clip: {e}")
            
            if progress_callback:
                progress_callback(100.0, "Video combination complete!")
            
            logger.info(f"[PodcastVideoCombination] Saved combined video to: {video_path} ({file_size} bytes)")
            
            # Return video metadata immediately - don't wait for cleanup
            # This prevents blocking if cleanup hangs
            return {
                "video_path": str(video_path),
                "video_filename": video_filename,
                "video_url": f"/api/podcast/final-videos/{video_filename}",
                "duration": total_duration,
                "fps": fps,
                "file_size": file_size,
                "num_scenes": len(video_clips),
            }
            
        except Exception as e:
            logger.exception(f"[PodcastVideoCombination] Error combining videos: {e}")
            raise RuntimeError(f"Failed to combine videos: {str(e)}") from e
    
    def save_scene_video(self, video_bytes: bytes, scene_number: int, user_id: str) -> Dict[str, str]:
        """
        Save a single scene video to disk.
        
        This is a utility method for saving individual scene videos before combination.
        Separate from story writer to maintain clear separation of concerns.
        
        Parameters:
            video_bytes (bytes): Raw video file bytes.
            scene_number (int): Scene number for filename.
            user_id (str): User ID for filename.
        
        Returns:
            Dict[str, str]: Dictionary with 'video_filename', 'video_path', 'video_url', and 'file_size'.
        """
        import uuid
        
        try:
            # Generate unique filename matching story writer format
            clean_user_id = "".join(c if c.isalnum() or c in ('-', '_') else '_' for c in user_id[:16])
            timestamp = str(uuid.uuid4())[:8]
            video_filename = f"scene_{scene_number}_{clean_user_id}_{timestamp}.mp4"
            
            # Save to AI_Videos subdirectory (scene videos before combination)
            # output_dir is Final_Videos, so parent is podcast_videos, then AI_Videos
            scene_videos_dir = self.output_dir.parent / "AI_Videos"
            scene_videos_dir.mkdir(parents=True, exist_ok=True)
            
            video_path = scene_videos_dir / video_filename
            
            # Write video bytes to file
            with open(video_path, "wb") as f:
                f.write(video_bytes)
            
            file_size = video_path.stat().st_size
            logger.info(f"[PodcastVideoCombination] Saved scene {scene_number} video: {video_filename} ({file_size} bytes)")
            
            # Generate URL path (relative to /api/podcast/videos/)
            video_url = f"/api/podcast/videos/{video_filename}"
            
            return {
                "video_filename": video_filename,
                "video_url": video_url,
                "video_path": str(video_path),
                "file_size": file_size,
            }
            
        except Exception as e:
            logger.error(f"[PodcastVideoCombination] Error saving scene video: {e}", exc_info=True)
            raise RuntimeError(f"Failed to save scene video: {str(e)}") from e
    
    def _generate_video_filename(self, podcast_title: str) -> str:
        """
        Generate a unique filename for the combined video.
        
        Parameters:
            podcast_title (str): Title of the podcast episode.
        
        Returns:
            str: Generated filename.
        """
        # Sanitize title for filename
        safe_title = "".join(c for c in podcast_title if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_title = safe_title.replace(' ', '_')[:50]  # Limit length
        
        # Add unique ID and timestamp
        unique_id = str(uuid.uuid4())[:8]
        timestamp = int(Path(__file__).stat().st_mtime)  # Use file modification time as simple timestamp
        
        return f"podcast_{safe_title}_{unique_id}_{timestamp}.mp4"

