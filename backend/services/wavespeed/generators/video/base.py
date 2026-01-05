"""
Base functionality for video operations.

Shared utilities for HTTP requests, video download, and common operations.
"""

import requests
from typing import Optional
from fastapi import HTTPException

from utils.logger_utils import get_service_logger

logger = get_service_logger("wavespeed.generators.video.base")


class VideoBase:
    """Base class for video operations with shared functionality."""
    
    def __init__(self, api_key: str, base_url: str, polling):
        """Initialize video base.
        
        Args:
            api_key: WaveSpeed API key
            base_url: WaveSpeed API base URL
            polling: WaveSpeedPolling instance for async operations
        """
        self.api_key = api_key
        self.base_url = base_url
        self.polling = polling
    
    def _get_headers(self) -> dict:
        """Get HTTP headers for API requests."""
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
    
    def _download_video(self, video_url: str, timeout: int = 180) -> bytes:
        """Download video from URL.
        
        Args:
            video_url: URL to download video from
            timeout: Request timeout in seconds
            
        Returns:
            bytes: Video bytes
            
        Raises:
            HTTPException: If download fails
        """
        logger.info(f"[WaveSpeed] Downloading video from: {video_url}")
        video_response = requests.get(video_url, timeout=timeout)
        
        if video_response.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail={
                    "error": "Failed to download video",
                    "status_code": video_response.status_code,
                    "response": video_response.text[:200],
                }
            )
        
        return video_response.content
    
    def _extract_video_url(self, outputs: list) -> Optional[str]:
        """Extract video URL from outputs array.
        
        Args:
            outputs: Array of outputs (can be strings or dicts)
            
        Returns:
            Optional[str]: Video URL if found, None otherwise
        """
        if not outputs:
            return None
        
        output = outputs[0]
        if isinstance(output, str):
            return output if output.startswith("http") else None
        elif isinstance(output, dict):
            return output.get("url") or output.get("video_url")
        
        return None
