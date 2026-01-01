"""
Base classes and interfaces for video generation services.

Provides common interfaces and data structures for video generation providers.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict, Any, Protocol, Callable


@dataclass
class VideoGenerationOptions:
    """Options for video generation."""
    prompt: str
    duration: int = 5
    resolution: str = "720p"
    negative_prompt: Optional[str] = None
    seed: Optional[int] = None
    audio_base64: Optional[str] = None
    enable_prompt_expansion: bool = True
    model: Optional[str] = None
    extra: Optional[Dict[str, Any]] = None


@dataclass
class VideoGenerationResult:
    """Result from video generation."""
    video_bytes: bytes
    prompt: str
    duration: float
    model_name: str
    cost: float
    provider: str
    resolution: str
    width: int
    height: int
    metadata: Dict[str, Any]
    source_video_url: Optional[str] = None
    prediction_id: Optional[str] = None


class VideoGenerationProvider(Protocol):
    """Protocol for video generation providers."""
    
    async def generate_video(
        self,
        options: VideoGenerationOptions,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> VideoGenerationResult:
        """Generate video with given options."""
        ...
