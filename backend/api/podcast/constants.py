"""
Podcast API Constants

Centralized constants and directory configuration for podcast module.
"""

from pathlib import Path
from services.story_writer.audio_generation_service import StoryAudioGenerationService

# Directory paths
# router.py is at: backend/api/podcast/router.py
# parents[0] = backend/api/podcast/
# parents[1] = backend/api/
# parents[2] = backend/
BASE_DIR = Path(__file__).resolve().parents[2]  # backend/
PODCAST_AUDIO_DIR = (BASE_DIR / "podcast_audio").resolve()
PODCAST_AUDIO_DIR.mkdir(parents=True, exist_ok=True)
PODCAST_IMAGES_DIR = (BASE_DIR / "podcast_images").resolve()
PODCAST_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
PODCAST_VIDEOS_DIR = (BASE_DIR / "podcast_videos").resolve()
PODCAST_VIDEOS_DIR.mkdir(parents=True, exist_ok=True)

# Video subdirectory
AI_VIDEO_SUBDIR = Path("AI_Videos")

# Initialize audio service
audio_service = StoryAudioGenerationService(output_dir=str(PODCAST_AUDIO_DIR))

