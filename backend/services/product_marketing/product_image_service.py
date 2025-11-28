"""
Product Image Service
Specialized service for generating product-focused images using AI models.
Optimized for e-commerce product photography, product showcases, and product marketing assets.
"""

import hashlib
import time
import os
import shutil
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from pathlib import Path
from loguru import logger

from services.wavespeed.client import WaveSpeedClient
from utils.asset_tracker import save_asset_to_library
from services.database import SessionLocal
from fastapi import HTTPException


class ProductImageServiceError(Exception):
    """Base exception for Product Image Service errors."""
    pass


class ValidationError(ProductImageServiceError):
    """Validation error for invalid requests."""
    pass


class ImageGenerationError(ProductImageServiceError):
    """Error during image generation."""
    pass


class StorageError(ProductImageServiceError):
    """Error saving image to storage."""
    pass


@dataclass
class ProductImageRequest:
    """Request for product image generation."""
    product_name: str
    product_description: str
    environment: str = "studio"  # studio, lifestyle, outdoor, minimalist, luxury
    background_style: str = "white"  # white, transparent, lifestyle, branded
    lighting: str = "natural"  # natural, studio, dramatic, soft
    product_variant: Optional[str] = None  # color, size, etc.
    angle: Optional[str] = None  # front, side, top, 360, etc.
    style: str = "photorealistic"  # photorealistic, minimalist, luxury, technical
    resolution: str = "1024x1024"  # 1024x1024, 1280x720, etc.
    num_variations: int = 1
    brand_colors: Optional[List[str]] = None  # Brand color palette
    additional_context: Optional[str] = None


@dataclass
class ProductImageResult:
    """Result from product image generation."""
    success: bool
    product_name: str
    image_url: Optional[str] = None
    image_bytes: Optional[bytes] = None
    asset_id: Optional[int] = None  # Asset Library ID
    provider: Optional[str] = None
    model: Optional[str] = None
    cost: float = 0.0
    generation_time: float = 0.0
    error: Optional[str] = None


class ProductImageService:
    """Service for generating product marketing images."""
    
    # Product photography style presets
    ENVIRONMENT_PROMPTS = {
        "studio": "professional studio photography, clean white background, even lighting",
        "lifestyle": "lifestyle photography, product in use, natural environment, relatable setting",
        "outdoor": "outdoor photography, natural lighting, outdoor environment, dynamic setting",
        "minimalist": "minimalist product photography, simple composition, clean aesthetic",
        "luxury": "luxury product photography, premium aesthetic, sophisticated lighting, high-end",
    }
    
    BACKGROUND_STYLES = {
        "white": "clean white background",
        "transparent": "transparent background, isolated product",
        "lifestyle": "lifestyle background, contextual environment",
        "branded": "branded background with brand colors",
    }
    
    LIGHTING_STYLES = {
        "natural": "natural lighting, soft shadows, balanced exposure",
        "studio": "professional studio lighting, even illumination, no harsh shadows",
        "dramatic": "dramatic lighting, high contrast, artistic shadows",
        "soft": "soft diffused lighting, gentle shadows, elegant",
    }
    
    # Valid values for request parameters
    VALID_ENVIRONMENTS = {"studio", "lifestyle", "outdoor", "minimalist", "luxury"}
    VALID_BACKGROUND_STYLES = {"white", "transparent", "lifestyle", "branded"}
    VALID_LIGHTING_STYLES = {"natural", "studio", "dramatic", "soft"}
    VALID_STYLES = {"photorealistic", "minimalist", "luxury", "technical"}
    VALID_ANGLES = {"front", "side", "top", "360"}
    
    # Maximum values
    MAX_RESOLUTION = (4096, 4096)
    MIN_RESOLUTION = (256, 256)
    MAX_NUM_VARIATIONS = 10
    MAX_PRODUCT_NAME_LENGTH = 500
    MAX_PRODUCT_DESCRIPTION_LENGTH = 2000
    
    def __init__(self):
        """Initialize Product Image Service."""
        try:
            self.wavespeed_client = WaveSpeedClient()
            logger.info("[Product Image Service] Initialized")
        except Exception as e:
            logger.error(f"[Product Image Service] Failed to initialize WaveSpeed client: {str(e)}")
            raise ProductImageServiceError(f"Failed to initialize service: {str(e)}") from e
    
    def validate_request(self, request: ProductImageRequest) -> None:
        """
        Validate product image generation request.
        
        Args:
            request: Product image generation request
            
        Raises:
            ValidationError: If request is invalid
        """
        errors = []
        
        # Validate product_name
        if not request.product_name or not request.product_name.strip():
            errors.append("Product name is required")
        elif len(request.product_name) > self.MAX_PRODUCT_NAME_LENGTH:
            errors.append(f"Product name must be <= {self.MAX_PRODUCT_NAME_LENGTH} characters")
        
        # Validate product_description
        if request.product_description and len(request.product_description) > self.MAX_PRODUCT_DESCRIPTION_LENGTH:
            errors.append(f"Product description must be <= {self.MAX_PRODUCT_DESCRIPTION_LENGTH} characters")
        
        # Validate environment
        if request.environment not in self.VALID_ENVIRONMENTS:
            errors.append(f"Invalid environment: {request.environment}. Valid: {', '.join(self.VALID_ENVIRONMENTS)}")
        
        # Validate background_style
        if request.background_style not in self.VALID_BACKGROUND_STYLES:
            errors.append(f"Invalid background_style: {request.background_style}. Valid: {', '.join(self.VALID_BACKGROUND_STYLES)}")
        
        # Validate lighting
        if request.lighting not in self.VALID_LIGHTING_STYLES:
            errors.append(f"Invalid lighting: {request.lighting}. Valid: {', '.join(self.VALID_LIGHTING_STYLES)}")
        
        # Validate style
        if request.style not in self.VALID_STYLES:
            errors.append(f"Invalid style: {request.style}. Valid: {', '.join(self.VALID_STYLES)}")
        
        # Validate angle
        if request.angle and request.angle not in self.VALID_ANGLES:
            errors.append(f"Invalid angle: {request.angle}. Valid: {', '.join(self.VALID_ANGLES)}")
        
        # Validate num_variations
        if request.num_variations < 1:
            errors.append("num_variations must be >= 1")
        elif request.num_variations > self.MAX_NUM_VARIATIONS:
            errors.append(f"num_variations must be <= {self.MAX_NUM_VARIATIONS}")
        
        # Validate resolution
        try:
            width, height = self._parse_resolution(request.resolution)
            if width < self.MIN_RESOLUTION[0] or height < self.MIN_RESOLUTION[1]:
                errors.append(f"Resolution must be >= {self.MIN_RESOLUTION[0]}x{self.MIN_RESOLUTION[1]}")
            if width > self.MAX_RESOLUTION[0] or height > self.MAX_RESOLUTION[1]:
                errors.append(f"Resolution must be <= {self.MAX_RESOLUTION[0]}x{self.MAX_RESOLUTION[1]}")
        except Exception as e:
            errors.append(f"Invalid resolution format: {request.resolution}. Error: {str(e)}")
        
        if errors:
            raise ValidationError(f"Validation failed: {'; '.join(errors)}")
    
    def build_product_prompt(
        self,
        request: ProductImageRequest,
        brand_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Build optimized prompt for product image generation.
        
        Args:
            request: Product image generation request
            brand_context: Optional brand DNA context for personalization
            
        Returns:
            Optimized prompt string
        """
        prompt_parts = []
        
        # Base product description
        prompt_parts.append(f"Professional product photography of {request.product_name}")
        if request.product_description:
            prompt_parts.append(f": {request.product_description}")
        
        # Product variant
        if request.product_variant:
            prompt_parts.append(f", {request.product_variant}")
        
        # Environment and style
        env_prompt = self.ENVIRONMENT_PROMPTS.get(request.environment, self.ENVIRONMENT_PROMPTS["studio"])
        prompt_parts.append(f", {env_prompt}")
        
        # Background
        bg_prompt = self.BACKGROUND_STYLES.get(request.background_style, self.BACKGROUND_STYLES["white"])
        if request.background_style == "branded" and request.brand_colors:
            bg_prompt += f", using brand colors: {', '.join(request.brand_colors)}"
        prompt_parts.append(f", {bg_prompt}")
        
        # Lighting
        lighting_prompt = self.LIGHTING_STYLES.get(request.lighting, self.LIGHTING_STYLES["natural"])
        prompt_parts.append(f", {lighting_prompt}")
        
        # Angle/view
        if request.angle:
            angle_map = {
                "front": "front view, centered composition",
                "side": "side profile view, showing depth",
                "top": "top-down view, flat lay style",
                "360": "3/4 angle view, showing multiple sides",
            }
            angle_prompt = angle_map.get(request.angle, request.angle)
            prompt_parts.append(f", {angle_prompt}")
        
        # Style
        style_map = {
            "photorealistic": "photorealistic, highly detailed, professional photography",
            "minimalist": "minimalist aesthetic, clean composition, simple and elegant",
            "luxury": "luxury aesthetic, premium quality, sophisticated and refined",
            "technical": "technical product photography, detailed features, professional documentation style",
        }
        style_prompt = style_map.get(request.style, style_map["photorealistic"])
        prompt_parts.append(f", {style_prompt}")
        
        # Additional context
        if request.additional_context:
            prompt_parts.append(f", {request.additional_context}")
        
        # Brand DNA integration (if available)
        if brand_context:
            brand_tone = brand_context.get("visual_identity", {}).get("style_guidelines")
            if brand_tone:
                prompt_parts.append(f", brand style: {brand_tone}")
        
        # Quality keywords
        prompt_parts.append(", high resolution, professional quality, sharp focus, commercial photography")
        
        full_prompt = " ".join(prompt_parts)
        logger.debug(f"[Product Image Service] Built prompt: {full_prompt[:200]}...")
        
        return full_prompt
    
    def _generate_image_with_retry(
        self,
        model: str,
        prompt: str,
        width: int,
        height: int,
        max_retries: int = 3,
        retry_delay: float = 2.0
    ) -> bytes:
        """
        Generate image with retry logic for transient failures.
        
        Args:
            model: Model to use
            prompt: Generation prompt
            width: Image width
            height: Image height
            max_retries: Maximum number of retries
            retry_delay: Delay between retries in seconds
            
        Returns:
            Generated image bytes
            
        Raises:
            ImageGenerationError: If generation fails after retries
        """
        last_error = None
        
        for attempt in range(max_retries):
            try:
                logger.info(f"[Product Image Service] Image generation attempt {attempt + 1}/{max_retries}")
                
                image_bytes = self.wavespeed_client.generate_image(
                    model=model,
                    prompt=prompt,
                    width=width,
                    height=height,
                    enable_sync_mode=True,
                    timeout=120,
                )
                
                if not image_bytes:
                    raise ValueError("Image generation returned empty result")
                
                if len(image_bytes) < 100:  # Sanity check: image should be at least 100 bytes
                    raise ValueError(f"Generated image too small: {len(image_bytes)} bytes")
                
                logger.info(f"[Product Image Service] ✅ Image generated successfully: {len(image_bytes)} bytes")
                return image_bytes
                
            except Exception as e:
                last_error = e
                error_msg = str(e)
                logger.warning(f"[Product Image Service] Attempt {attempt + 1} failed: {error_msg}")
                
                # Don't retry on validation errors or client errors (4xx)
                if "4" in error_msg or "validation" in error_msg.lower() or "invalid" in error_msg.lower():
                    logger.error(f"[Product Image Service] Non-retryable error: {error_msg}")
                    raise ImageGenerationError(f"Image generation failed: {error_msg}") from e
                
                # Retry on transient errors
                if attempt < max_retries - 1:
                    logger.info(f"[Product Image Service] Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 1.5  # Exponential backoff
                else:
                    logger.error(f"[Product Image Service] All retry attempts failed")
        
        raise ImageGenerationError(f"Image generation failed after {max_retries} attempts: {str(last_error)}") from last_error
    
    async def generate_product_image(
        self,
        request: ProductImageRequest,
        user_id: str,
        brand_context: Optional[Dict[str, Any]] = None
    ) -> ProductImageResult:
        """
        Generate product image using AI models.
        
        Args:
            request: Product image generation request
            user_id: User ID for tracking
            brand_context: Optional brand DNA for personalization
            
        Returns:
            ProductImageResult with generated image
        """
        start_time = time.time()
        
        try:
            # Validate request
            self.validate_request(request)
            
            # Validate user_id
            if not user_id or not user_id.strip():
                raise ValidationError("user_id is required")
            
            # Build optimized prompt
            prompt = self.build_product_prompt(request, brand_context)
            
            # Parse resolution
            width, height = self._parse_resolution(request.resolution)
            
            # Select model based on style/quality needs
            model = "ideogram-v3-turbo"  # Default to Ideogram V3 for photorealistic products
            if request.style == "minimalist":
                model = "ideogram-v3-turbo"  # Still use Ideogram for quality
            elif request.style == "technical":
                model = "ideogram-v3-turbo"
            
            logger.info(f"[Product Image Service] Generating product image for '{request.product_name}' using {model}")
            
            # Generate image using WaveSpeed with retry logic
            try:
                image_bytes = self._generate_image_with_retry(
                    model=model,
                    prompt=prompt,
                    width=width,
                    height=height,
                    max_retries=3,
                    retry_delay=2.0
                )
            except ImageGenerationError as e:
                logger.error(f"[Product Image Service] Image generation failed: {str(e)}")
                generation_time = time.time() - start_time
                return ProductImageResult(
                    success=False,
                    product_name=request.product_name,
                    error=f"Image generation failed: {str(e)}",
                    generation_time=generation_time,
                )
            
            # Save image to file and Asset Library
            asset_id = None
            image_url = None
            
            try:
                asset_id, image_url = self._save_product_image(
                    image_bytes=image_bytes,
                    request=request,
                    user_id=user_id,
                    prompt=prompt,
                    model=model,
                    start_time=start_time
                )
            except StorageError as storage_error:
                logger.error(f"[Product Image Service] Storage failed: {str(storage_error)}", exc_info=True)
                # Continue with generation result even if storage fails
                # The image_bytes is still available in the result
            except Exception as save_error:
                logger.error(f"[Product Image Service] Unexpected error saving image: {str(save_error)}", exc_info=True)
                # Continue even if save fails
            
            generation_time = time.time() - start_time
            
            return ProductImageResult(
                success=True,
                product_name=request.product_name,
                image_url=image_url,
                image_bytes=image_bytes,
                asset_id=asset_id,
                provider="wavespeed",
                model=model,
                cost=0.10,
                generation_time=generation_time,
            )
            
        except ValidationError as ve:
            logger.error(f"[Product Image Service] Validation error: {str(ve)}")
            generation_time = time.time() - start_time
            return ProductImageResult(
                success=False,
                product_name=request.product_name if hasattr(request, 'product_name') else "unknown",
                error=f"Validation error: {str(ve)}",
                generation_time=generation_time,
            )
        except Exception as e:
            logger.error(f"[Product Image Service] ❌ Unexpected error generating product image: {str(e)}", exc_info=True)
            generation_time = time.time() - start_time
            return ProductImageResult(
                success=False,
                product_name=request.product_name if hasattr(request, 'product_name') else "unknown",
                error=f"Unexpected error: {str(e)}",
                generation_time=generation_time,
            )
    
    def _save_product_image(
        self,
        image_bytes: bytes,
        request: ProductImageRequest,
        user_id: str,
        prompt: str,
        model: str,
        start_time: float
    ) -> tuple[Optional[int], Optional[str]]:
        """
        Save product image to disk and Asset Library.
        
        Args:
            image_bytes: Generated image bytes
            request: Product image generation request
            user_id: User ID
            prompt: Generation prompt
            model: Model used
            start_time: Generation start time
            
        Returns:
            Tuple of (asset_id, image_url)
            
        Raises:
            StorageError: If saving fails
        """
        db = None
        asset_id = None
        image_url = None
        image_path = None
        
        try:
            # Generate filename
            product_hash = hashlib.md5(request.product_name.encode()).hexdigest()[:8]
            timestamp = int(start_time)
            filename = f"product_{product_hash}_{timestamp}.png"
            
            # Determine base directory and create product_images folder
            base_dir = Path(__file__).parent.parent.parent
            product_images_dir = base_dir / "product_images"
            
            # Create directory with error handling
            try:
                product_images_dir.mkdir(parents=True, exist_ok=True)
            except PermissionError as pe:
                raise StorageError(f"Permission denied creating directory: {str(pe)}") from pe
            except OSError as oe:
                raise StorageError(f"Failed to create directory: {str(oe)}") from oe
            
            # Check disk space (rough estimate - at least 10MB free)
            try:
                stat = shutil.disk_usage(product_images_dir)
                free_space_mb = stat.free / (1024 * 1024)
                if free_space_mb < 10:
                    raise StorageError(f"Insufficient disk space: {free_space_mb:.1f}MB free (need at least 10MB)")
            except OSError as oe:
                logger.warning(f"[Product Image Service] Could not check disk space: {str(oe)}")
            
            # Save image to disk
            image_path = product_images_dir / filename
            try:
                with open(image_path, "wb") as f:
                    f.write(image_bytes)
                # Verify file was written
                if not image_path.exists() or image_path.stat().st_size == 0:
                    raise StorageError("Image file was not written correctly")
            except PermissionError as pe:
                raise StorageError(f"Permission denied writing file: {str(pe)}") from pe
            except OSError as oe:
                raise StorageError(f"Failed to write file: {str(oe)}") from oe
            
            file_size = len(image_bytes)
            image_url = f"/api/product-marketing/images/{filename}"
            
            # Save to Asset Library
            db = SessionLocal()
            try:
                asset_id = save_asset_to_library(
                    db=db,
                    user_id=user_id,
                    asset_type="image",
                    source_module="product_marketing",
                    filename=filename,
                    file_url=image_url,
                    file_path=str(image_path),
                    file_size=file_size,
                    mime_type="image/png",
                    title=f"{request.product_name} - Product Image",
                    description=f"Product image: {request.product_description or request.product_name}",
                    prompt=prompt,
                    tags=["product_marketing", "product_image", request.environment, request.style],
                    provider="wavespeed",
                    model=model,
                    cost=0.10,  # Estimated cost for Ideogram V3
                    asset_metadata={
                        "product_name": request.product_name,
                        "product_description": request.product_description,
                        "environment": request.environment,
                        "background_style": request.background_style,
                        "lighting": request.lighting,
                        "style": request.style,
                        "variant": request.product_variant,
                        "angle": request.angle,
                    },
                )
                
                if asset_id:
                    logger.info(f"[Product Image Service] ✅ Saved product image to Asset Library: ID={asset_id}")
                else:
                    logger.warning(f"[Product Image Service] ⚠️ Asset Library save returned None (file saved but not tracked)")
                    
            except Exception as db_error:
                logger.error(f"[Product Image Service] Database error saving to Asset Library: {str(db_error)}", exc_info=True)
                # File is saved, but database tracking failed
                # This is not critical - image is still accessible
                raise StorageError(f"Failed to save to Asset Library: {str(db_error)}") from db_error
            finally:
                if db:
                    try:
                        db.close()
                    except Exception as close_error:
                        logger.warning(f"[Product Image Service] Error closing database: {str(close_error)}")
            
            return (asset_id, image_url)
            
        except StorageError:
            # Clean up partial files on storage error
            if image_path and image_path.exists():
                try:
                    image_path.unlink()
                    logger.info(f"[Product Image Service] Cleaned up partial file: {image_path}")
                except Exception as cleanup_error:
                    logger.warning(f"[Product Image Service] Failed to cleanup partial file: {str(cleanup_error)}")
            raise
    
    def _parse_resolution(self, resolution: str) -> tuple[int, int]:
        """
        Parse resolution string to width, height tuple.
        
        Args:
            resolution: Resolution string (e.g., "1024x1024", "square", "landscape")
            
        Returns:
            Tuple of (width, height)
        """
        try:
            resolution = resolution.strip().lower()
            
            if "x" in resolution:
                parts = resolution.split("x")
                if len(parts) != 2:
                    raise ValueError(f"Invalid resolution format: {resolution}")
                width = int(parts[0].strip())
                height = int(parts[1].strip())
                
                # Validate resolution values
                if width < 1 or height < 1:
                    raise ValueError(f"Resolution dimensions must be positive: {width}x{height}")
                
                return (width, height)
            elif resolution == "square":
                return (1024, 1024)
            elif resolution == "landscape":
                return (1280, 720)
            elif resolution == "portrait":
                return (720, 1280)
            else:
                # Try to parse as single number (assume square)
                try:
                    size = int(resolution)
                    return (size, size)
                except ValueError:
                    # Default to square
                    logger.warning(f"[Product Image Service] Could not parse resolution '{resolution}', defaulting to 1024x1024")
                    return (1024, 1024)
        except Exception as e:
            logger.warning(f"[Product Image Service] Error parsing resolution '{resolution}': {str(e)}, defaulting to 1024x1024")
            return (1024, 1024)
    
    def estimate_cost(self, request: ProductImageRequest) -> float:
        """Estimate cost for product image generation."""
        # Ideogram V3 Turbo: ~$0.10 per image
        # Multiply by number of variations
        base_cost = 0.10
        return base_cost * request.num_variations

