"""Image Format Converter Service for converting between image formats."""

from __future__ import annotations

import base64
import io
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from PIL import Image, ImageCms

from utils.logger_utils import get_service_logger


logger = get_service_logger("image_studio.format_converter")


@dataclass
class FormatConversionRequest:
    """Request model for format conversion."""
    image_base64: str
    target_format: str  # png, jpeg, jpg, webp, gif, bmp, tiff
    preserve_transparency: bool = True
    quality: Optional[int] = None  # For lossy formats (1-100)
    color_space: Optional[str] = None  # sRGB, Adobe RGB, etc.
    strip_metadata: bool = False  # Keep metadata by default for conversion
    optimize: bool = True
    progressive: bool = True  # For JPEG


@dataclass
class FormatConversionResult:
    """Result of format conversion."""
    success: bool
    image_base64: str
    original_format: str
    target_format: str
    original_size_kb: float
    converted_size_kb: float
    width: int
    height: int
    transparency_preserved: bool
    metadata_preserved: bool
    color_space: Optional[str] = None


class ImageFormatConverterService:
    """Service for converting images between formats."""

    SUPPORTED_FORMATS = {
        "png": {
            "name": "PNG",
            "description": "Lossless format with transparency support",
            "supports_transparency": True,
            "supports_lossy": False,
            "mime_type": "image/png",
        },
        "jpeg": {
            "name": "JPEG",
            "description": "Lossy format, best for photos",
            "supports_transparency": False,
            "supports_lossy": True,
            "mime_type": "image/jpeg",
        },
        "jpg": {
            "name": "JPEG",
            "description": "Lossy format, best for photos",
            "supports_transparency": False,
            "supports_lossy": True,
            "mime_type": "image/jpeg",
        },
        "webp": {
            "name": "WebP",
            "description": "Modern format with excellent compression",
            "supports_transparency": True,
            "supports_lossy": True,
            "mime_type": "image/webp",
        },
        "gif": {
            "name": "GIF",
            "description": "Supports animation and transparency",
            "supports_transparency": True,
            "supports_lossy": False,
            "mime_type": "image/gif",
        },
        "bmp": {
            "name": "BMP",
            "description": "Uncompressed bitmap format",
            "supports_transparency": False,
            "supports_lossy": False,
            "mime_type": "image/bmp",
        },
        "tiff": {
            "name": "TIFF",
            "description": "High-quality format for print",
            "supports_transparency": True,
            "supports_lossy": False,
            "mime_type": "image/tiff",
        },
    }

    def __init__(self):
        logger.info("[Format Converter] ImageFormatConverterService initialized")

    def _decode_image(self, image_base64: str) -> tuple[Image.Image, int, str]:
        """Decode base64 image and return PIL Image, size, and format."""
        # Handle data URL format
        if "," in image_base64:
            image_base64 = image_base64.split(",", 1)[1]
        
        image_bytes = base64.b64decode(image_base64)
        original_size = len(image_bytes)
        
        image = Image.open(io.BytesIO(image_bytes))
        original_format = image.format.lower() if image.format else "unknown"
        
        return image, original_size, original_format

    def _strip_exif(self, image: Image.Image) -> Image.Image:
        """Remove EXIF metadata from image."""
        data = list(image.getdata())
        image_without_exif = Image.new(image.mode, image.size)
        image_without_exif.putdata(data)
        return image_without_exif

    def _convert_color_space(
        self,
        image: Image.Image,
        target_color_space: str,
    ) -> Image.Image:
        """Convert image color space."""
        try:
            # Get current color space
            if hasattr(image, 'info') and 'icc_profile' in image.info:
                # Image has ICC profile
                try:
                    src_profile = ImageCms.ImageCmsProfile(io.BytesIO(image.info['icc_profile']))
                    if target_color_space.lower() == "srgb":
                        dst_profile = ImageCms.createProfile("sRGB")
                    elif target_color_space.lower() == "adobe rgb":
                        dst_profile = ImageCms.createProfile("Adobe RGB")
                    else:
                        return image  # Unknown color space
                    
                    transform = ImageCms.ImageCmsTransform(src_profile, dst_profile, image.mode, image.mode)
                    image = ImageCms.applyTransform(image, transform)
                except Exception as e:
                    logger.warning(f"[Format Converter] Color space conversion failed: {e}")
            else:
                # No ICC profile, assume sRGB
                logger.info("[Format Converter] No ICC profile found, assuming sRGB")
        except Exception as e:
            logger.warning(f"[Format Converter] Color space conversion error: {e}")
        
        return image

    def _convert_image(
        self,
        image: Image.Image,
        target_format: str,
        quality: Optional[int],
        preserve_transparency: bool,
        optimize: bool,
        progressive: bool,
    ) -> bytes:
        """Convert image to target format."""
        buffer = io.BytesIO()
        format_lower = target_format.lower()
        
        # Handle format-specific conversions
        save_kwargs: Dict[str, Any] = {}
        
        # Check if source has transparency and target doesn't support it
        has_transparency = image.mode in ("RGBA", "LA", "P") and (
            "transparency" in image.info or image.mode == "RGBA"
        )
        
        if format_lower in ["jpeg", "jpg"]:
            # JPEG doesn't support transparency
            if has_transparency and preserve_transparency:
                # Convert to RGB, losing transparency
                if image.mode in ("RGBA", "LA"):
                    # Create white background
                    rgb_image = Image.new("RGB", image.size, (255, 255, 255))
                    if image.mode == "RGBA":
                        rgb_image.paste(image, mask=image.split()[3])  # Use alpha channel as mask
                    else:
                        rgb_image.paste(image)
                    image = rgb_image
                elif image.mode == "P":
                    image = image.convert("RGB")
                else:
                    image = image.convert("RGB")
            
            save_kwargs["format"] = "JPEG"
            if quality:
                save_kwargs["quality"] = quality
            else:
                save_kwargs["quality"] = 95  # Default high quality
            save_kwargs["optimize"] = optimize
            if progressive:
                save_kwargs["progressive"] = True
                
        elif format_lower == "png":
            save_kwargs["format"] = "PNG"
            save_kwargs["optimize"] = optimize
            # PNG compression level (0-9)
            if quality:
                compress_level = max(0, min(9, (100 - quality) // 11))
                save_kwargs["compress_level"] = compress_level
            else:
                save_kwargs["compress_level"] = 6  # Default
                
        elif format_lower == "webp":
            save_kwargs["format"] = "WEBP"
            if quality:
                save_kwargs["quality"] = quality
            else:
                save_kwargs["quality"] = 80  # Default
            save_kwargs["method"] = 6  # Best compression
            if preserve_transparency and has_transparency:
                # WebP supports transparency
                if image.mode not in ("RGBA", "LA"):
                    image = image.convert("RGBA")
                    
        elif format_lower == "gif":
            save_kwargs["format"] = "GIF"
            # GIF conversion
            if image.mode != "P":
                # Convert to palette mode for GIF
                image = image.convert("P", palette=Image.ADAPTIVE)
            save_kwargs["optimize"] = optimize
            if preserve_transparency and has_transparency:
                save_kwargs["transparency"] = 255  # Preserve transparency
                
        elif format_lower == "bmp":
            save_kwargs["format"] = "BMP"
            if image.mode in ("RGBA", "LA", "P") and has_transparency:
                # BMP doesn't support transparency, convert to RGB
                if image.mode == "RGBA":
                    rgb_image = Image.new("RGB", image.size, (255, 255, 255))
                    rgb_image.paste(image, mask=image.split()[3])
                    image = rgb_image
                else:
                    image = image.convert("RGB")
                    
        elif format_lower == "tiff":
            save_kwargs["format"] = "TIFF"
            save_kwargs["compression"] = "tiff_lzw"  # Lossless compression
            if preserve_transparency and has_transparency:
                # TIFF supports transparency
                if image.mode not in ("RGBA", "LA"):
                    image = image.convert("RGBA")
        else:
            raise ValueError(f"Unsupported target format: {target_format}")
        
        image.save(buffer, **save_kwargs)
        return buffer.getvalue()

    async def convert(
        self,
        request: FormatConversionRequest,
        user_id: Optional[str] = None,
    ) -> FormatConversionResult:
        """Convert an image to target format."""
        logger.info(f"[Format Converter] Processing conversion request for user: {user_id}")
        
        try:
            # Decode image
            image, original_size, original_format = self._decode_image(request.image_base64)
            original_size_kb = original_size / 1024
            
            logger.info(f"[Format Converter] Original: {original_format}, Target: {request.target_format}, Size: {original_size_kb:.2f} KB")
            
            # Validate target format
            format_lower = request.target_format.lower()
            if format_lower not in self.SUPPORTED_FORMATS:
                raise ValueError(f"Unsupported format: {request.target_format}. Supported: {list(self.SUPPORTED_FORMATS.keys())}")
            
            # Check transparency preservation
            has_transparency = image.mode in ("RGBA", "LA", "P") and (
                "transparency" in image.info or image.mode == "RGBA"
            )
            target_supports_transparency = self.SUPPORTED_FORMATS[format_lower]["supports_transparency"]
            transparency_preserved = (
                has_transparency and 
                target_supports_transparency and 
                request.preserve_transparency
            )
            
            # Color space conversion
            if request.color_space:
                image = self._convert_color_space(image, request.color_space)
            
            # Strip metadata if requested
            metadata_preserved = not request.strip_metadata
            if request.strip_metadata:
                image = self._strip_exif(image)
            
            # Convert format
            converted_bytes = self._convert_image(
                image,
                format_lower,
                request.quality,
                request.preserve_transparency,
                request.optimize,
                request.progressive,
            )
            
            converted_size_kb = len(converted_bytes) / 1024
            
            # Encode result
            mime_type = self.SUPPORTED_FORMATS[format_lower]["mime_type"]
            result_base64 = f"data:{mime_type};base64,{base64.b64encode(converted_bytes).decode()}"
            
            logger.info(f"[Format Converter] Converted: {original_size_kb:.2f}KB → {converted_size_kb:.2f}KB")
            
            return FormatConversionResult(
                success=True,
                image_base64=result_base64,
                original_format=original_format,
                target_format=format_lower,
                original_size_kb=round(original_size_kb, 2),
                converted_size_kb=round(converted_size_kb, 2),
                width=image.width,
                height=image.height,
                transparency_preserved=transparency_preserved,
                metadata_preserved=metadata_preserved,
                color_space=request.color_space,
            )
            
        except Exception as e:
            logger.error(f"[Format Converter] Failed to convert image: {e}")
            raise

    async def convert_batch(
        self,
        requests: List[FormatConversionRequest],
        user_id: Optional[str] = None,
    ) -> List[FormatConversionResult]:
        """Convert multiple images."""
        logger.info(f"[Format Converter] Processing batch of {len(requests)} images for user: {user_id}")
        
        results = []
        for i, request in enumerate(requests):
            try:
                result = await self.convert(request, user_id)
                results.append(result)
                logger.info(f"[Format Converter] Batch item {i+1}/{len(requests)} complete")
            except Exception as e:
                logger.error(f"[Format Converter] Batch item {i+1} failed: {e}")
                results.append(FormatConversionResult(
                    success=False,
                    image_base64="",
                    original_format="",
                    target_format="",
                    original_size_kb=0,
                    converted_size_kb=0,
                    width=0,
                    height=0,
                    transparency_preserved=False,
                    metadata_preserved=False,
                ))
        
        return results

    def get_supported_formats(self) -> List[Dict[str, Any]]:
        """Get list of supported formats with details."""
        return [
            {
                "id": fmt_id,
                "name": fmt_info["name"],
                "description": fmt_info["description"],
                "supports_transparency": fmt_info["supports_transparency"],
                "supports_lossy": fmt_info["supports_lossy"],
                "mime_type": fmt_info["mime_type"],
            }
            for fmt_id, fmt_info in self.SUPPORTED_FORMATS.items()
        ]

    def get_format_recommendations(self, source_format: str) -> List[Dict[str, Any]]:
        """Get format recommendations based on source format."""
        recommendations = {
            "png": [
                {"format": "webp", "reason": "60% smaller file size, maintains transparency"},
                {"format": "jpeg", "reason": "Best for photos, smaller file size"},
            ],
            "jpeg": [
                {"format": "webp", "reason": "25-34% smaller with similar quality"},
                {"format": "png", "reason": "Lossless, supports transparency"},
            ],
            "jpg": [
                {"format": "webp", "reason": "25-34% smaller with similar quality"},
                {"format": "png", "reason": "Lossless, supports transparency"},
            ],
            "webp": [
                {"format": "png", "reason": "Better compatibility, lossless"},
                {"format": "jpeg", "reason": "Universal compatibility"},
            ],
        }
        
        source_lower = source_format.lower()
        return recommendations.get(source_lower, [])
