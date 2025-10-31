from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict, Any, Protocol


@dataclass
class ImageGenerationOptions:
    prompt: str
    negative_prompt: Optional[str] = None
    width: int = 1024
    height: int = 1024
    guidance_scale: Optional[float] = None
    steps: Optional[int] = None
    seed: Optional[int] = None
    model: Optional[str] = None
    extra: Optional[Dict[str, Any]] = None


@dataclass
class ImageGenerationResult:
    image_bytes: bytes
    width: int
    height: int
    provider: str
    model: Optional[str] = None
    seed: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


class ImageGenerationProvider(Protocol):
    """Protocol for image generation providers."""

    def generate(self, options: ImageGenerationOptions) -> ImageGenerationResult:
        ...


