"""Create Studio service for AI-powered image generation."""

import os
from typing import Optional, Dict, Any, List, Literal
from dataclasses import dataclass

from services.llm_providers.image_generation import (
    ImageGenerationOptions,
    ImageGenerationResult,
    HuggingFaceImageProvider,
    GeminiImageProvider,
    StabilityImageProvider,
    WaveSpeedImageProvider,
)
from .templates import TemplateManager, ImageTemplate, Platform, TemplateCategory
from utils.logger_utils import get_service_logger


logger = get_service_logger("image_studio.create")


@dataclass
class CreateStudioRequest:
    """Request for image generation in Create Studio."""
    prompt: str
    template_id: Optional[str] = None
    provider: Optional[str] = None  # "auto", "stability", "wavespeed", "huggingface", "gemini"
    model: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    aspect_ratio: Optional[str] = None  # e.g., "1:1", "16:9"
    style_preset: Optional[str] = None
    quality: Literal["draft", "standard", "premium"] = "standard"
    negative_prompt: Optional[str] = None
    guidance_scale: Optional[float] = None
    steps: Optional[int] = None
    seed: Optional[int] = None
    num_variations: int = 1
    enhance_prompt: bool = True
    use_persona: bool = False
    persona_id: Optional[str] = None


class CreateStudioService:
    """Service for Create Studio image generation operations."""
    
    # Provider-to-model mapping for smart recommendations
    PROVIDER_MODELS = {
        "stability": {
            "ultra": "stability-ultra",  # Best quality, 8 credits
            "core": "stability-core",    # Fast & affordable, 3 credits
            "sd3": "sd3.5-large",        # SD3.5 model
        },
        "wavespeed": {
            "ideogram-v3-turbo": "ideogram-v3-turbo",  # Photorealistic, text rendering
            "qwen-image": "qwen-image",                 # Fast generation
        },
        "huggingface": {
            "flux": "black-forest-labs/FLUX.1-Krea-dev",
        },
        "gemini": {
            "imagen": "imagen-3.0-generate-001",
        }
    }
    
    # Quality-to-provider mapping
    QUALITY_PROVIDERS = {
        "draft": ["huggingface", "wavespeed:qwen-image"],  # Fast, low cost
        "standard": ["stability:core", "wavespeed:ideogram-v3-turbo"],  # Balanced
        "premium": ["wavespeed:ideogram-v3-turbo", "stability:ultra"],  # Best quality
    }
    
    def __init__(self):
        """Initialize Create Studio service."""
        self.template_manager = TemplateManager()
        logger.info("[Create Studio] Initialized with template manager")
    
    def _get_provider_instance(self, provider_name: str, api_key: Optional[str] = None):
        """Get provider instance by name.
        
        Args:
            provider_name: Name of the provider
            api_key: Optional API key (uses env vars if not provided)
            
        Returns:
            Provider instance
            
        Raises:
            ValueError: If provider is not supported
        """
        if provider_name == "stability":
            return StabilityImageProvider(api_key=api_key or os.getenv("STABILITY_API_KEY"))
        elif provider_name == "wavespeed":
            return WaveSpeedImageProvider(api_key=api_key or os.getenv("WAVESPEED_API_KEY"))
        elif provider_name == "huggingface":
            return HuggingFaceImageProvider(api_token=api_key or os.getenv("HF_API_KEY"))
        elif provider_name == "gemini":
            return GeminiImageProvider(api_key=api_key or os.getenv("GEMINI_API_KEY"))
        else:
            raise ValueError(f"Unsupported provider: {provider_name}")
    
    def _select_provider_and_model(
        self, 
        request: CreateStudioRequest,
        template: Optional[ImageTemplate] = None
    ) -> tuple[str, Optional[str]]:
        """Smart provider and model selection.
        
        Args:
            request: Create studio request
            template: Optional template with recommendations
            
        Returns:
            Tuple of (provider_name, model_name)
        """
        # Explicit provider selection
        if request.provider and request.provider != "auto":
            provider = request.provider
            model = request.model
            logger.info("[Provider Selection] User specified: %s (model: %s)", provider, model)
            return provider, model
        
        # Template recommendation
        if template and template.recommended_provider:
            provider = template.recommended_provider
            logger.info("[Provider Selection] Template recommends: %s", provider)
            
            # Map provider to specific model if not specified
            if not request.model:
                if provider == "ideogram":
                    return "wavespeed", "ideogram-v3-turbo"
                elif provider == "qwen":
                    return "wavespeed", "qwen-image"
                elif provider == "stability":
                    # Choose based on quality
                    if request.quality == "premium":
                        return "stability", "stability-ultra"
                    elif request.quality == "draft":
                        return "stability", "stability-core"
                    else:
                        return "stability", "stability-core"
            
            return provider, request.model
        
        # Quality-based selection
        quality_options = self.QUALITY_PROVIDERS.get(request.quality, self.QUALITY_PROVIDERS["standard"])
        selected = quality_options[0]  # Pick first option
        
        if ":" in selected:
            provider, model = selected.split(":", 1)
        else:
            provider = selected
            model = None
        
        logger.info("[Provider Selection] Quality-based (%s): %s (model: %s)", 
                   request.quality, provider, model)
        return provider, model
    
    def _enhance_prompt(self, prompt: str, style_preset: Optional[str] = None) -> str:
        """Enhance prompt with style and quality descriptors.
        
        Args:
            prompt: Original prompt
            style_preset: Style preset to apply
            
        Returns:
            Enhanced prompt
        """
        enhanced = prompt
        
        # Add style-specific enhancements
        style_enhancements = {
            "photographic": ", professional photography, high quality, detailed, sharp focus, natural lighting",
            "digital-art": ", digital art, vibrant colors, detailed, high quality, artstation trending",
            "cinematic": ", cinematic lighting, dramatic, film grain, high quality, professional",
            "3d-model": ", 3D render, octane render, unreal engine, high quality, detailed",
            "anime": ", anime style, vibrant colors, detailed, high quality",
            "line-art": ", clean line art, detailed linework, high contrast, professional",
        }
        
        if style_preset and style_preset in style_enhancements:
            enhanced += style_enhancements[style_preset]
        
        logger.info("[Prompt Enhancement] Original: %s", prompt[:100])
        logger.info("[Prompt Enhancement] Enhanced: %s", enhanced[:100])
        
        return enhanced
    
    def _apply_template(self, request: CreateStudioRequest, template: ImageTemplate) -> CreateStudioRequest:
        """Apply template settings to request.
        
        Args:
            request: Original request
            template: Template to apply
            
        Returns:
            Modified request
        """
        # Apply template dimensions if not specified
        if not request.width and not request.height:
            request.width = template.aspect_ratio.width
            request.height = template.aspect_ratio.height
        
        # Apply template style if not specified
        if not request.style_preset:
            request.style_preset = template.style_preset
        
        # Apply template quality if not specified
        if request.quality == "standard":
            request.quality = template.quality
        
        logger.info("[Template Applied] %s -> %dx%d, style=%s, quality=%s",
                   template.name, request.width, request.height, 
                   request.style_preset, request.quality)
        
        return request
    
    def _calculate_dimensions(
        self, 
        width: Optional[int], 
        height: Optional[int], 
        aspect_ratio: Optional[str]
    ) -> tuple[int, int]:
        """Calculate image dimensions from width/height or aspect ratio.
        
        Args:
            width: Explicit width
            height: Explicit height
            aspect_ratio: Aspect ratio string (e.g., "16:9")
            
        Returns:
            Tuple of (width, height)
        """
        # Both dimensions specified
        if width and height:
            return width, height
        
        # Aspect ratio specified
        if aspect_ratio:
            try:
                w_ratio, h_ratio = map(int, aspect_ratio.split(":"))
                
                # Use width if specified
                if width:
                    height = int(width * h_ratio / w_ratio)
                    return width, height
                
                # Use height if specified
                if height:
                    width = int(height * w_ratio / h_ratio)
                    return width, height
                
                # Default size based on aspect ratio
                # Use 1080p as base
                if w_ratio >= h_ratio:
                    # Landscape or square
                    width = 1920
                    height = int(1920 * h_ratio / w_ratio)
                else:
                    # Portrait
                    height = 1920
                    width = int(1920 * w_ratio / h_ratio)
                
                return width, height
            except ValueError:
                logger.warning("[Dimensions] Invalid aspect ratio: %s", aspect_ratio)
        
        # Default dimensions
        return 1024, 1024
    
    async def generate(
        self, 
        request: CreateStudioRequest,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate image(s) using Create Studio.
        
        Args:
            request: Create studio request
            user_id: User ID for validation and tracking
            
        Returns:
            Dictionary with generation results
            
        Raises:
            ValueError: If request is invalid
            RuntimeError: If generation fails
        """
        logger.info("[Create Studio] Starting generation: prompt=%s, template=%s",
                   request.prompt[:100], request.template_id)
        
        # Pre-flight validation: Check subscription and usage limits
        if user_id:
            from services.database import get_db
            from services.subscription import PricingService
            from services.subscription.preflight_validator import validate_image_generation_operations
            from fastapi import HTTPException
            
            db = next(get_db())
            try:
                pricing_service = PricingService(db)
                logger.info(f"[Create Studio] 🛂 Running pre-flight validation for user {user_id}")
                validate_image_generation_operations(
                    pricing_service=pricing_service,
                    user_id=user_id,
                    num_images=request.num_variations
                )
                logger.info(f"[Create Studio] ✅ Pre-flight validation passed - proceeding with generation")
            except HTTPException as http_ex:
                logger.error(f"[Create Studio] ❌ Pre-flight validation failed - blocking generation")
                raise
            finally:
                db.close()
        else:
            logger.warning("[Create Studio] ⚠️  No user_id provided - skipping pre-flight validation")
        
        # Load template if specified
        template = None
        if request.template_id:
            template = self.template_manager.get_by_id(request.template_id)
            if not template:
                raise ValueError(f"Template not found: {request.template_id}")
            
            # Apply template settings
            request = self._apply_template(request, template)
        
        # Calculate dimensions
        width, height = self._calculate_dimensions(
            request.width, request.height, request.aspect_ratio
        )
        
        # Enhance prompt if requested
        prompt = request.prompt
        if request.enhance_prompt:
            prompt = self._enhance_prompt(prompt, request.style_preset)
        
        # Select provider and model
        provider_name, model = self._select_provider_and_model(request, template)
        
        # Get provider instance
        try:
            provider = self._get_provider_instance(provider_name)
        except Exception as e:
            logger.error("[Create Studio] ❌ Failed to initialize provider %s: %s",
                        provider_name, str(e))
            raise RuntimeError(f"Provider initialization failed: {str(e)}")
        
        # Generate images
        results = []
        for i in range(request.num_variations):
            logger.info("[Create Studio] Generating variation %d/%d", 
                       i + 1, request.num_variations)
            
            try:
                # Prepare options
                options = ImageGenerationOptions(
                    prompt=prompt,
                    negative_prompt=request.negative_prompt,
                    width=width,
                    height=height,
                    guidance_scale=request.guidance_scale,
                    steps=request.steps,
                    seed=request.seed + i if request.seed else None,
                    model=model,
                    extra={"style_preset": request.style_preset} if request.style_preset else {}
                )
                
                # Generate image
                result: ImageGenerationResult = provider.generate(options)
                
                results.append({
                    "image_bytes": result.image_bytes,
                    "width": result.width,
                    "height": result.height,
                    "provider": result.provider,
                    "model": result.model,
                    "seed": result.seed,
                    "metadata": result.metadata,
                    "variation": i + 1,
                })
                
                logger.info("[Create Studio] ✅ Variation %d generated successfully", i + 1)
                
            except Exception as e:
                logger.error("[Create Studio] ❌ Failed to generate variation %d: %s",
                           i + 1, str(e), exc_info=True)
                results.append({
                    "error": str(e),
                    "variation": i + 1,
                })
        
        # Return results
        return {
            "success": True,
            "request": {
                "prompt": request.prompt,
                "enhanced_prompt": prompt if request.enhance_prompt else None,
                "template_id": request.template_id,
                "template_name": template.name if template else None,
                "provider": provider_name,
                "model": model,
                "dimensions": f"{width}x{height}",
                "quality": request.quality,
                "num_variations": request.num_variations,
            },
            "results": results,
            "total_generated": sum(1 for r in results if "image_bytes" in r),
            "total_failed": sum(1 for r in results if "error" in r),
        }
    
    def get_templates(
        self, 
        platform: Optional[Platform] = None,
        category: Optional[TemplateCategory] = None
    ) -> List[ImageTemplate]:
        """Get available templates.
        
        Args:
            platform: Filter by platform
            category: Filter by category
            
        Returns:
            List of templates
        """
        if platform:
            return self.template_manager.get_by_platform(platform)
        elif category:
            return self.template_manager.get_by_category(category)
        else:
            return self.template_manager.get_all_templates()
    
    def search_templates(self, query: str) -> List[ImageTemplate]:
        """Search templates by query.
        
        Args:
            query: Search query
            
        Returns:
            List of matching templates
        """
        return self.template_manager.search(query)
    
    def recommend_templates(
        self, 
        use_case: str, 
        platform: Optional[Platform] = None
    ) -> List[ImageTemplate]:
        """Recommend templates based on use case.
        
        Args:
            use_case: Description of use case
            platform: Optional platform filter
            
        Returns:
            List of recommended templates
        """
        return self.template_manager.recommend_for_use_case(use_case, platform)

