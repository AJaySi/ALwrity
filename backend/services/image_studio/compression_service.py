"""Image Compression Service for optimizing image file sizes."""

from __future__ import annotations

import base64
import io
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Literal

from PIL import Image, ExifTags

from utils.logger_utils import get_service_logger


logger = get_service_logger("image_studio.compression")


@dataclass
class CompressionRequest:
    """Request model for image compression."""
    image_base64: str
    quality: int = 85  # 1-100, where 100 is best quality
    format: str = "jpeg"  # jpeg, png, webp, avif
    target_size_kb: Optional[int] = None  # Target file size in KB
    strip_metadata: bool = True
    progressive: bool = True  # Progressive JPEG
    optimize: bool = True  # Optimize encoding


@dataclass 
class CompressionResult:
    """Result of compression operation."""
    success: bool
    image_base64: str
    original_size_kb: float
    compressed_size_kb: float
    compression_ratio: float
    format: str
    width: int
    height: int
    quality_used: int
    metadata_stripped: bool


class ImageCompressionService:
    """Service for image compression and optimization."""

    SUPPORTED_FORMATS = ["jpeg", "jpg", "png", "webp"]
    
    # Format-specific options
    FORMAT_OPTIONS = {
        "jpeg": {"quality": (1, 100), "progressive": True, "optimize": True},
        "jpg": {"quality": (1, 100), "progressive": True, "optimize": True},
        "png": {"compress_level": (0, 9), "optimize": True},
        "webp": {"quality": (1, 100), "lossless": False},
    }

    def __init__(self):
        logger.info("[Compression] ImageCompressionService initialized")

    def _decode_image(self, image_base64: str) -> tuple[Image.Image, int]:
        """Decode base64 image and return PIL Image and original size."""
        # Handle data URL format
        if "," in image_base64:
            image_base64 = image_base64.split(",", 1)[1]
        
        image_bytes = base64.b64decode(image_base64)
        original_size = len(image_bytes)
        
        image = Image.open(io.BytesIO(image_bytes))
        return image, original_size

    def _strip_exif(self, image: Image.Image) -> Image.Image:
        """Remove EXIF metadata from image."""
        # Create a new image without EXIF data
        data = list(image.getdata())
        image_without_exif = Image.new(image.mode, image.size)
        image_without_exif.putdata(data)
        return image_without_exif

    def _compress_to_target_size(
        self,
        image: Image.Image,
        target_size_kb: int,
        format: str,
        min_quality: int = 10,
        max_quality: int = 95,
    ) -> tuple[bytes, int]:
        """Compress image to target file size using binary search."""
        target_bytes = target_size_kb * 1024
        
        low, high = min_quality, max_quality
        best_result = None
        best_quality = max_quality
        
        while low <= high:
            mid = (low + high) // 2
            compressed = self._compress_image(image, format, mid, True, True)
            
            if len(compressed) <= target_bytes:
                best_result = compressed
                best_quality = mid
                low = mid + 1  # Try higher quality
            else:
                high = mid - 1  # Try lower quality
        
        if best_result is None:
            # Even minimum quality exceeds target, return min quality result
            best_result = self._compress_image(image, format, min_quality, True, True)
            best_quality = min_quality
        
        return best_result, best_quality

    def _compress_image(
        self,
        image: Image.Image,
        format: str,
        quality: int,
        progressive: bool,
        optimize: bool,
    ) -> bytes:
        """Compress image with given settings."""
        buffer = io.BytesIO()
        
        # Handle format-specific options
        save_kwargs: Dict[str, Any] = {}
        
        format_lower = format.lower()
        if format_lower in ["jpeg", "jpg"]:
            # Convert to RGB if necessary (JPEG doesn't support alpha)
            if image.mode in ("RGBA", "P"):
                image = image.convert("RGB")
            save_kwargs["format"] = "JPEG"
            save_kwargs["quality"] = quality
            save_kwargs["optimize"] = optimize
            if progressive:
                save_kwargs["progressive"] = True
        elif format_lower == "png":
            save_kwargs["format"] = "PNG"
            save_kwargs["optimize"] = optimize
            # PNG uses compress_level (0-9) instead of quality
            compress_level = max(0, min(9, (100 - quality) // 11))
            save_kwargs["compress_level"] = compress_level
        elif format_lower == "webp":
            save_kwargs["format"] = "WEBP"
            save_kwargs["quality"] = quality
            save_kwargs["method"] = 6  # Best compression
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        image.save(buffer, **save_kwargs)
        return buffer.getvalue()

    async def compress(
        self,
        request: CompressionRequest,
        user_id: Optional[str] = None,
    ) -> CompressionResult:
        """Compress an image with specified settings."""
        logger.info(f"[Compression] Processing compression request for user: {user_id}")
        
        try:
            # Decode image
            image, original_size = self._decode_image(request.image_base64)
            original_size_kb = original_size / 1024
            
            logger.info(f"[Compression] Original size: {original_size_kb:.2f} KB, dimensions: {image.size}")
            
            # Strip metadata if requested
            if request.strip_metadata:
                image = self._strip_exif(image)
            
            # Validate format
            format_lower = request.format.lower()
            if format_lower not in self.SUPPORTED_FORMATS:
                raise ValueError(f"Unsupported format: {request.format}. Supported: {self.SUPPORTED_FORMATS}")
            
            # Compress to target size or with quality setting
            if request.target_size_kb:
                compressed_bytes, quality_used = self._compress_to_target_size(
                    image,
                    request.target_size_kb,
                    format_lower,
                )
            else:
                compressed_bytes = self._compress_image(
                    image,
                    format_lower,
                    request.quality,
                    request.progressive,
                    request.optimize,
                )
                quality_used = request.quality
            
            compressed_size_kb = len(compressed_bytes) / 1024
            compression_ratio = (1 - compressed_size_kb / original_size_kb) * 100 if original_size_kb > 0 else 0
            
            # Encode result
            mime_type = "image/jpeg" if format_lower in ["jpeg", "jpg"] else f"image/{format_lower}"
            result_base64 = f"data:{mime_type};base64,{base64.b64encode(compressed_bytes).decode()}"
            
            logger.info(f"[Compression] Compressed: {original_size_kb:.2f}KB → {compressed_size_kb:.2f}KB ({compression_ratio:.1f}% reduction)")
            
            return CompressionResult(
                success=True,
                image_base64=result_base64,
                original_size_kb=round(original_size_kb, 2),
                compressed_size_kb=round(compressed_size_kb, 2),
                compression_ratio=round(compression_ratio, 2),
                format=format_lower,
                width=image.width,
                height=image.height,
                quality_used=quality_used,
                metadata_stripped=request.strip_metadata,
            )
            
        except Exception as e:
            logger.error(f"[Compression] Failed to compress image: {e}")
            raise

    async def compress_batch(
        self,
        requests: List[CompressionRequest],
        user_id: Optional[str] = None,
    ) -> List[CompressionResult]:
        """Compress multiple images with same or individual settings."""
        logger.info(f"[Compression] Processing batch of {len(requests)} images for user: {user_id}")
        
        results = []
        for i, request in enumerate(requests):
            try:
                result = await self.compress(request, user_id)
                results.append(result)
                logger.info(f"[Compression] Batch item {i+1}/{len(requests)} complete")
            except Exception as e:
                logger.error(f"[Compression] Batch item {i+1} failed: {e}")
                # Return partial success
                results.append(CompressionResult(
                    success=False,
                    image_base64="",
                    original_size_kb=0,
                    compressed_size_kb=0,
                    compression_ratio=0,
                    format="",
                    width=0,
                    height=0,
                    quality_used=0,
                    metadata_stripped=False,
                ))
        
        return results

    async def estimate_compression(
        self,
        image_base64: str,
        format: str = "jpeg",
        quality: int = 85,
    ) -> Dict[str, Any]:
        """Estimate compression results without actually compressing."""
        try:
            image, original_size = self._decode_image(image_base64)
            original_size_kb = original_size / 1024
            
            # Quick estimation based on format and quality
            if format.lower() in ["jpeg", "jpg"]:
                # JPEG compression ratio estimate
                estimated_ratio = 0.1 + (quality / 100) * 0.4  # 10-50% of original
            elif format.lower() == "webp":
                # WebP is typically 25-34% smaller than JPEG
                estimated_ratio = 0.08 + (quality / 100) * 0.35
            else:  # PNG
                estimated_ratio = 0.7 + (quality / 100) * 0.2  # PNG is less compressible
            
            estimated_size_kb = original_size_kb * estimated_ratio
            
            return {
                "original_size_kb": round(original_size_kb, 2),
                "estimated_size_kb": round(estimated_size_kb, 2),
                "estimated_reduction_percent": round((1 - estimated_ratio) * 100, 1),
                "width": image.width,
                "height": image.height,
                "format": format.lower(),
            }
        except Exception as e:
            logger.error(f"[Compression] Estimation failed: {e}")
            raise

    def get_supported_formats(self) -> List[Dict[str, Any]]:
        """Get list of supported compression formats with details."""
        return [
            {
                "id": "jpeg",
                "name": "JPEG",
                "extension": ".jpg",
                "description": "Best for photos. Lossy compression with excellent size reduction.",
                "supports_transparency": False,
                "quality_range": [1, 100],
                "recommended_quality": 85,
                "use_cases": ["Photos", "Blog images", "Email", "Social media"],
            },
            {
                "id": "png",
                "name": "PNG",
                "extension": ".png",
                "description": "Best for graphics with transparency. Lossless compression.",
                "supports_transparency": True,
                "quality_range": [1, 100],
                "recommended_quality": 90,
                "use_cases": ["Logos", "Icons", "Graphics", "Screenshots"],
            },
            {
                "id": "webp",
                "name": "WebP",
                "extension": ".webp",
                "description": "Modern format with excellent compression. 25-34% smaller than JPEG.",
                "supports_transparency": True,
                "quality_range": [1, 100],
                "recommended_quality": 80,
                "use_cases": ["Web images", "Fast loading", "Modern browsers"],
            },
        ]

    def get_presets(self) -> List[Dict[str, Any]]:
        """Get compression presets for common use cases."""
        return [
            {
                "id": "web",
                "name": "Web Optimized",
                "description": "Balanced quality and size for web pages",
                "format": "webp",
                "quality": 80,
                "strip_metadata": True,
            },
            {
                "id": "email",
                "name": "Email Friendly",
                "description": "Small file size for email attachments (<200KB target)",
                "format": "jpeg",
                "quality": 70,
                "target_size_kb": 200,
                "strip_metadata": True,
            },
            {
                "id": "social",
                "name": "Social Media",
                "description": "Optimized for social platforms",
                "format": "jpeg",
                "quality": 85,
                "strip_metadata": True,
            },
            {
                "id": "high_quality",
                "name": "High Quality",
                "description": "Minimal compression for quality-critical images",
                "format": "png",
                "quality": 95,
                "strip_metadata": False,
            },
            {
                "id": "maximum",
                "name": "Maximum Compression",
                "description": "Smallest possible file size",
                "format": "webp",
                "quality": 60,
                "strip_metadata": True,
            },
        ]
