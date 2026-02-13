"""YouTube API Constants and Configuration

Shared constants, directory paths, and configuration values for the YouTube API.
"""

from pathlib import Path

# Base directory for YouTube assets
base_dir = Path(__file__).parent.parent.parent.parent

# YouTube asset directories
YOUTUBE_VIDEO_DIR = base_dir / "youtube_videos"
YOUTUBE_VIDEO_DIR.mkdir(parents=True, exist_ok=True)

YOUTUBE_AVATARS_DIR = base_dir / "youtube_avatars"
YOUTUBE_AVATARS_DIR.mkdir(parents=True, exist_ok=True)

YOUTUBE_IMAGES_DIR = base_dir / "youtube_images"
YOUTUBE_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

# Video processing constants
DEFAULT_VIDEO_RESOLUTION = "720p"
DEFAULT_VOICE_ID = "Wise_Woman"
SUPPORTED_RESOLUTIONS = ["480p", "720p", "1080p"]
SUPPORTED_VIDEO_TYPES = [
    "tutorial", "review", "educational", "entertainment",
    "vlog", "product_demo", "reaction", "storytelling"
]
SUPPORTED_DURATION_TYPES = ["shorts", "medium", "long"]

# Task processing constants
MAX_CONCURRENT_VIDEO_TASKS = 3
VIDEO_TASK_TIMEOUT_SECONDS = 3600  # 1 hour
SCENE_TASK_TIMEOUT_SECONDS = 1800  # 30 minutes

# File size limits (in MB)
MAX_VIDEO_SIZE_MB = 500
MAX_IMAGE_SIZE_MB = 50
MAX_AUDIO_SIZE_MB = 100

# API rate limiting (requests per minute)
API_RATE_LIMIT_REQUESTS_PER_MINUTE = 10

# Cost estimation defaults
DEFAULT_IMAGE_MODEL = "ideogram-v3-turbo"