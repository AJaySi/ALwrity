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


@dataclass
class ImageEditOptions:
    """Options for image editing operations."""
    image_base64: str
    prompt: str
    operation: str  # "general_edit", "inpaint", "outpaint", "remove_background", etc.
    mask_base64: Optional[str] = None
    negative_prompt: Optional[str] = None
    model: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    guidance_scale: Optional[float] = None
    steps: Optional[int] = None
    seed: Optional[int] = None
    extra: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API calls."""
        result = {
            "image_base64": self.image_base64,
            "prompt": self.prompt,
            "operation": self.operation,
        }
        if self.mask_base64:
            result["mask_base64"] = self.mask_base64
        if self.negative_prompt:
            result["negative_prompt"] = self.negative_prompt
        if self.model:
            result["model"] = self.model
        if self.width:
            result["width"] = self.width
        if self.height:
            result["height"] = self.height
        if self.guidance_scale is not None:
            result["guidance_scale"] = self.guidance_scale
        if self.steps:
            result["steps"] = self.steps
        if self.seed is not None:
            result["seed"] = self.seed
        if self.extra:
            result.update(self.extra)
        return result


class ImageGenerationProvider(Protocol):
    """Protocol for image generation providers."""

    def generate(self, options: ImageGenerationOptions) -> ImageGenerationResult:
        ...


@dataclass
class FaceSwapOptions:
    """Options for face swap operations."""
    base_image_base64: str  # Image to swap face into
    face_image_base64: str  # Face to swap
    model: Optional[str] = None
    target_face_index: Optional[int] = None  # For multi-face images (0 = largest)
    target_gender: Optional[str] = None  # "all", "female", "male" (for some models)
    extra: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API calls."""
        result = {
            "base_image_base64": self.base_image_base64,
            "face_image_base64": self.face_image_base64,
        }
        if self.model:
            result["model"] = self.model
        if self.target_face_index is not None:
            result["target_face_index"] = self.target_face_index
        if self.target_gender:
            result["target_gender"] = self.target_gender
        if self.extra:
            result.update(self.extra)
        return result


class ImageEditProvider(Protocol):
    """Protocol for image editing providers."""

    def edit(self, options: ImageEditOptions) -> ImageGenerationResult:
        ...


class FaceSwapProvider(Protocol):
    """Protocol for face swap providers."""

    def swap_face(self, options: FaceSwapOptions) -> ImageGenerationResult:
        ...


