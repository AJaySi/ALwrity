"""Social Optimizer service for platform-specific image optimization."""

from __future__ import annotations

import base64
import io
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from PIL import Image, ImageDraw, ImageFont

from .templates import Platform
from utils.logging import get_service_logger


logger = get_service_logger("image_studio.social_optimizer")


@dataclass
class SafeZone:
    """Safe zone configuration for text overlay."""
    top: float = 0.1  # Percentage from top
    bottom: float = 0.1  # Percentage from bottom
    left: float = 0.1  # Percentage from left
    right: float = 0.1  # Percentage from right


@dataclass
class PlatformFormat:
    """Platform format specification."""
    name: str
    width: int
    height: int
    ratio: str
    safe_zone: SafeZone
    file_type: str = "PNG"
    max_size_mb: float = 5.0


# Platform format definitions with safe zones
PLATFORM_FORMATS: Dict[Platform, List[PlatformFormat]] = {
    Platform.INSTAGRAM: [
        PlatformFormat(
            name="Feed Post (Square)",
            width=1080,
            height=1080,
            ratio="1:1",
            safe_zone=SafeZone(top=0.15, bottom=0.15, left=0.1, right=0.1),
        ),
        PlatformFormat(
            name="Feed Post (Portrait)",
            width=1080,
            height=1350,
            ratio="4:5",
            safe_zone=SafeZone(top=0.2, bottom=0.2, left=0.1, right=0.1),
        ),
        PlatformFormat(
            name="Story",
            width=1080,
            height=1920,
            ratio="9:16",
            safe_zone=SafeZone(top=0.25, bottom=0.15, left=0.1, right=0.1),
        ),
        PlatformFormat(
            name="Reel",
            width=1080,
            height=1920,
            ratio="9:16",
            safe_zone=SafeZone(top=0.25, bottom=0.15, left=0.1, right=0.1),
        ),
    ],
    Platform.FACEBOOK: [
        PlatformFormat(
            name="Feed Post",
            width=1200,
            height=630,
            ratio="1.91:1",
            safe_zone=SafeZone(top=0.15, bottom=0.15, left=0.1, right=0.1),
        ),
        PlatformFormat(
            name="Feed Post (Square)",
            width=1080,
            height=1080,
            ratio="1:1",
            safe_zone=SafeZone(top=0.15, bottom=0.15, left=0.1, right=0.1),
        ),
        PlatformFormat(
            name="Story",
            width=1080,
            height=1920,
            ratio="9:16",
            safe_zone=SafeZone(top=0.25, bottom=0.15, left=0.1, right=0.1),
        ),
        PlatformFormat(
            name="Cover Photo",
            width=820,
            height=312,
            ratio="16:9",
            safe_zone=SafeZone(top=0.2, bottom=0.1, left=0.15, right=0.15),
        ),
    ],
    Platform.TWITTER: [
        PlatformFormat(
            name="Post",
            width=1200,
            height=675,
            ratio="16:9",
            safe_zone=SafeZone(top=0.15, bottom=0.15, left=0.1, right=0.1),
        ),
        PlatformFormat(
            name="Card",
            width=1200,
            height=600,
            ratio="2:1",
            safe_zone=SafeZone(top=0.15, bottom=0.15, left=0.1, right=0.1),
        ),
        PlatformFormat(
            name="Header",
            width=1500,
            height=500,
            ratio="3:1",
            safe_zone=SafeZone(top=0.2, bottom=0.1, left=0.15, right=0.15),
        ),
    ],
    Platform.LINKEDIN: [
        PlatformFormat(
            name="Feed Post",
            width=1200,
            height=628,
            ratio="1.91:1",
            safe_zone=SafeZone(top=0.15, bottom=0.15, left=0.1, right=0.1),
        ),
        PlatformFormat(
            name="Feed Post (Square)",
            width=1080,
            height=1080,
            ratio="1:1",
            safe_zone=SafeZone(top=0.15, bottom=0.15, left=0.1, right=0.1),
        ),
        PlatformFormat(
            name="Article",
            width=1200,
            height=627,
            ratio="2:1",
            safe_zone=SafeZone(top=0.15, bottom=0.15, left=0.1, right=0.1),
        ),
        PlatformFormat(
            name="Company Cover",
            width=1128,
            height=191,
            ratio="4:1",
            safe_zone=SafeZone(top=0.2, bottom=0.1, left=0.15, right=0.15),
        ),
    ],
    Platform.YOUTUBE: [
        PlatformFormat(
            name="Thumbnail",
            width=1280,
            height=720,
            ratio="16:9",
            safe_zone=SafeZone(top=0.15, bottom=0.15, left=0.1, right=0.1),
        ),
        PlatformFormat(
            name="Channel Art",
            width=2560,
            height=1440,
            ratio="16:9",
            safe_zone=SafeZone(top=0.2, bottom=0.1, left=0.15, right=0.15),
        ),
    ],
    Platform.PINTEREST: [
        PlatformFormat(
            name="Pin",
            width=1000,
            height=1500,
            ratio="2:3",
            safe_zone=SafeZone(top=0.2, bottom=0.2, left=0.1, right=0.1),
        ),
        PlatformFormat(
            name="Story Pin",
            width=1080,
            height=1920,
            ratio="9:16",
            safe_zone=SafeZone(top=0.25, bottom=0.15, left=0.1, right=0.1),
        ),
    ],
    Platform.TIKTOK: [
        PlatformFormat(
            name="Video Cover",
            width=1080,
            height=1920,
            ratio="9:16",
            safe_zone=SafeZone(top=0.25, bottom=0.15, left=0.1, right=0.1),
        ),
    ],
}


@dataclass
class SocialOptimizerRequest:
    """Request payload for social optimization."""

    image_base64: str
    platforms: List[Platform]  # List of platforms to optimize for
    format_names: Optional[Dict[Platform, str]] = None  # Specific format per platform
    show_safe_zones: bool = False  # Include safe zone overlay in output
    crop_mode: str = "smart"  # "smart", "center", "fit"
    focal_point: Optional[Dict[str, float]] = None  # {"x": 0.5, "y": 0.5} for smart crop
    output_format: str = "png"
    options: Dict[str, Any] = field(default_factory=dict)


class SocialOptimizerService:
    """Service for optimizing images for social media platforms."""

    def __init__(self):
        logger.info("[Social Optimizer] Initialized service")

    @staticmethod
    def _decode_base64_image(value: str) -> bytes:
        """Decode a base64 (or data URL) string to bytes."""
        try:
            if value.startswith("data:"):
                _, b64data = value.split(",", 1)
            else:
                b64data = value

            return base64.b64decode(b64data)
        except Exception as exc:
            logger.error(f"[Social Optimizer] Failed to decode base64 image: {exc}")
            raise ValueError("Invalid base64 image payload") from exc

    @staticmethod
    def _bytes_to_base64(image_bytes: bytes, output_format: str = "png") -> str:
        """Convert raw bytes to base64 data URL."""
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        return f"data:image/{output_format};base64,{b64}"

    @staticmethod
    def _smart_crop(
        image: Image.Image,
        target_width: int,
        target_height: int,
        focal_point: Optional[Dict[str, float]] = None,
    ) -> Image.Image:
        """Smart crop image to target dimensions, preserving important content."""
        img_width, img_height = image.size
        target_ratio = target_width / target_height
        img_ratio = img_width / img_height

        # If focal point is provided, use it for cropping
        if focal_point:
            focal_x = int(focal_point["x"] * img_width)
            focal_y = int(focal_point["y"] * img_height)
        else:
            # Default to center
            focal_x = img_width // 2
            focal_y = img_height // 2

        if img_ratio > target_ratio:
            # Image is wider than target - crop width
            new_width = int(img_height * target_ratio)
            left = max(0, min(focal_x - new_width // 2, img_width - new_width))
            right = left + new_width
            cropped = image.crop((left, 0, right, img_height))
        else:
            # Image is taller than target - crop height
            new_height = int(img_width / target_ratio)
            top = max(0, min(focal_y - new_height // 2, img_height - new_height))
            bottom = top + new_height
            cropped = image.crop((0, top, img_width, bottom))

        # Resize to exact target dimensions
        return cropped.resize((target_width, target_height), Image.Resampling.LANCZOS)

    @staticmethod
    def _fit_image(
        image: Image.Image,
        target_width: int,
        target_height: int,
    ) -> Image.Image:
        """Fit image to target dimensions while maintaining aspect ratio (adds padding if needed)."""
        img_width, img_height = image.size
        target_ratio = target_width / target_height
        img_ratio = img_width / img_height

        if img_ratio > target_ratio:
            # Image is wider - fit to height, pad width
            new_height = target_height
            new_width = int(img_width * (target_height / img_height))
            resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            # Create new image with target size and paste centered
            result = Image.new("RGB", (target_width, target_height), (255, 255, 255))
            paste_x = (target_width - new_width) // 2
            result.paste(resized, (paste_x, 0))
            return result
        else:
            # Image is taller - fit to width, pad height
            new_width = target_width
            new_height = int(img_height * (target_width / img_width))
            resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            # Create new image with target size and paste centered
            result = Image.new("RGB", (target_width, target_height), (255, 255, 255))
            paste_y = (target_height - new_height) // 2
            result.paste(resized, (0, paste_y))
            return result

    @staticmethod
    def _center_crop(
        image: Image.Image,
        target_width: int,
        target_height: int,
    ) -> Image.Image:
        """Center crop image to target dimensions."""
        img_width, img_height = image.size
        target_ratio = target_width / target_height
        img_ratio = img_width / img_height

        if img_ratio > target_ratio:
            # Image is wider - crop width
            new_width = int(img_height * target_ratio)
            left = (img_width - new_width) // 2
            cropped = image.crop((left, 0, left + new_width, img_height))
        else:
            # Image is taller - crop height
            new_height = int(img_width / target_ratio)
            top = (img_height - new_height) // 2
            cropped = image.crop((0, top, img_width, top + new_height))

        return cropped.resize((target_width, target_height), Image.Resampling.LANCZOS)

    @staticmethod
    def _draw_safe_zone(
        image: Image.Image,
        safe_zone: SafeZone,
    ) -> Image.Image:
        """Draw safe zone overlay on image."""
        draw = ImageDraw.Draw(image)
        width, height = image.size

        # Calculate safe zone boundaries
        top = int(height * safe_zone.top)
        bottom = int(height * (1 - safe_zone.bottom))
        left = int(width * safe_zone.left)
        right = int(width * (1 - safe_zone.right))

        # Draw semi-transparent overlay outside safe zone
        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)

        # Top area
        overlay_draw.rectangle([(0, 0), (width, top)], fill=(0, 0, 0, 100))
        # Bottom area
        overlay_draw.rectangle([(0, bottom), (width, height)], fill=(0, 0, 0, 100))
        # Left area
        overlay_draw.rectangle([(0, top), (left, bottom)], fill=(0, 0, 0, 100))
        # Right area
        overlay_draw.rectangle([(right, top), (width, bottom)], fill=(0, 0, 0, 100))

        # Draw safe zone border
        border_color = (255, 255, 0, 200)  # Yellow with transparency
        overlay_draw.rectangle(
            [(left, top), (right, bottom)],
            outline=border_color,
            width=2,
        )

        # Composite overlay onto image
        if image.mode != "RGBA":
            image = image.convert("RGBA")
        image = Image.alpha_composite(image, overlay)

        return image

    def get_platform_formats(self, platform: Platform) -> List[Dict[str, Any]]:
        """Get available formats for a platform."""
        formats = PLATFORM_FORMATS.get(platform, [])
        return [
            {
                "name": fmt.name,
                "width": fmt.width,
                "height": fmt.height,
                "ratio": fmt.ratio,
                "safe_zone": {
                    "top": fmt.safe_zone.top,
                    "bottom": fmt.safe_zone.bottom,
                    "left": fmt.safe_zone.left,
                    "right": fmt.safe_zone.right,
                },
                "file_type": fmt.file_type,
                "max_size_mb": fmt.max_size_mb,
            }
            for fmt in formats
        ]

    def optimize_image(
        self,
        request: SocialOptimizerRequest,
    ) -> Dict[str, Any]:
        """Optimize image for specified platforms."""
        logger.info(
            f"[Social Optimizer] Processing optimization for {len(request.platforms)} platform(s)"
        )

        # Decode input image
        image_bytes = self._decode_base64_image(request.image_base64)
        original_image = Image.open(io.BytesIO(image_bytes))

        # Convert to RGB if needed
        if original_image.mode in ("RGBA", "LA", "P"):
            if original_image.mode == "P":
                original_image = original_image.convert("RGBA")
            background = Image.new("RGB", original_image.size, (255, 255, 255))
            if original_image.mode == "RGBA":
                background.paste(original_image, mask=original_image.split()[-1])
            else:
                background.paste(original_image)
            original_image = background
        elif original_image.mode != "RGB":
            original_image = original_image.convert("RGB")

        results = []

        for platform in request.platforms:
            formats = PLATFORM_FORMATS.get(platform, [])
            if not formats:
                logger.warning(f"[Social Optimizer] No formats found for platform: {platform}")
                continue

            # Get format (use specified format or default to first)
            format_name = None
            if request.format_names and platform in request.format_names:
                format_name = request.format_names[platform]

            platform_format = None
            for fmt in formats:
                if format_name and fmt.name == format_name:
                    platform_format = fmt
                    break
            if not platform_format:
                platform_format = formats[0]  # Default to first format

            # Crop/resize image based on mode
            if request.crop_mode == "smart":
                optimized_image = self._smart_crop(
                    original_image,
                    platform_format.width,
                    platform_format.height,
                    request.focal_point,
                )
            elif request.crop_mode == "fit":
                optimized_image = self._fit_image(
                    original_image,
                    platform_format.width,
                    platform_format.height,
                )
            else:  # center
                optimized_image = self._center_crop(
                    original_image,
                    platform_format.width,
                    platform_format.height,
                )

            # Add safe zone overlay if requested
            if request.show_safe_zones:
                optimized_image = self._draw_safe_zone(optimized_image, platform_format.safe_zone)

            # Convert to bytes
            output_buffer = io.BytesIO()
            output_format = request.output_format.lower()
            if output_format == "jpg" or output_format == "jpeg":
                optimized_image = optimized_image.convert("RGB")
                optimized_image.save(output_buffer, format="JPEG", quality=95)
            else:
                optimized_image.save(output_buffer, format="PNG")
            output_bytes = output_buffer.getvalue()

            results.append(
                {
                    "platform": platform.value,
                    "format": platform_format.name,
                    "width": platform_format.width,
                    "height": platform_format.height,
                    "ratio": platform_format.ratio,
                    "image_base64": self._bytes_to_base64(output_bytes, request.output_format),
                    "safe_zone": {
                        "top": platform_format.safe_zone.top,
                        "bottom": platform_format.safe_zone.bottom,
                        "left": platform_format.safe_zone.left,
                        "right": platform_format.safe_zone.right,
                    },
                }
            )

        logger.info(f"[Social Optimizer] ✅ Generated {len(results)} optimized images")

        return {
            "success": True,
            "results": results,
            "total_optimized": len(results),
        }

