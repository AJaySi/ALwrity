"""Image Studio Manager - Main orchestration service for all image operations."""

from typing import Optional, Dict, Any, List

from .create_service import CreateStudioService, CreateStudioRequest
from .edit_service import EditStudioService, EditStudioRequest
from .upscale_service import UpscaleStudioService, UpscaleStudioRequest
from .control_service import ControlStudioService, ControlStudioRequest
from .social_optimizer_service import SocialOptimizerService, SocialOptimizerRequest
from .face_swap_service import FaceSwapService, FaceSwapStudioRequest
from .compression_service import ImageCompressionService, CompressionRequest, CompressionResult
from .format_converter_service import ImageFormatConverterService, FormatConversionRequest, FormatConversionResult
from .transform_service import (
    TransformStudioService,
    TransformImageToVideoRequest,
    TalkingAvatarRequest,
)
from .templates import Platform, TemplateCategory, ImageTemplate
from utils.logger_utils import get_service_logger


logger = get_service_logger("image_studio.manager")


class ImageStudioManager:
    """Main manager for Image Studio operations."""
    
    def __init__(self):
        """Initialize Image Studio Manager."""
        self.create_service = CreateStudioService()
        self.edit_service = EditStudioService()
        self.upscale_service = UpscaleStudioService()
        self.control_service = ControlStudioService()
        self.social_optimizer_service = SocialOptimizerService()
        self.face_swap_service = FaceSwapService()
        self.compression_service = ImageCompressionService()
        self.format_converter_service = ImageFormatConverterService()
        self.transform_service = TransformStudioService()
        logger.info("[Image Studio Manager] Initialized successfully")
    
    # ====================
    # CREATE STUDIO
    # ====================
    
    async def create_image(
        self, 
        request: CreateStudioRequest,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create/generate image using Create Studio.
        
        Args:
            request: Create studio request
            user_id: User ID for validation
            
        Returns:
            Dictionary with generation results
        """
        logger.info("[Image Studio] Create image request from user: %s", user_id)
        return await self.create_service.generate(request, user_id=user_id)

    # ====================
    # EDIT STUDIO
    # ====================

    async def edit_image(
        self,
        request: EditStudioRequest,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Run Edit Studio operations."""
        logger.info("[Image Studio] Edit image request from user: %s", user_id)
        return await self.edit_service.process_edit(request, user_id=user_id)

    def get_edit_operations(self) -> Dict[str, Any]:
        """Expose edit operations for UI."""
        return self.edit_service.list_operations()
    
    def get_edit_models(
        self,
        operation: Optional[str] = None,
        tier: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get available editing models.
        
        Args:
            operation: Filter by operation type
            tier: Filter by tier (budget, mid, premium)
            
        Returns:
            Dictionary with models and metadata
        """
        return self.edit_service.get_available_models(operation=operation, tier=tier)
    
    def recommend_edit_model(
        self,
        operation: str,
        image_resolution: Optional[Dict[str, int]] = None,
        user_tier: Optional[str] = None,
        preferences: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Recommend best editing model for given context.
        
        Args:
            operation: Operation type
            image_resolution: Image dimensions
            user_tier: User subscription tier
            preferences: User preferences (prioritize_cost, prioritize_quality)
            
        Returns:
            Dictionary with recommended model and alternatives
        """
        return self.edit_service.recommend_model(
            operation=operation,
            image_resolution=image_resolution,
            user_tier=user_tier,
            preferences=preferences,
        )
    
    # ====================
    # FACE SWAP STUDIO
    # ====================
    
    async def face_swap(
        self,
        request: FaceSwapStudioRequest,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Run Face Swap Studio operations."""
        logger.info("[Image Studio] Face swap request from user: %s", user_id)
        return await self.face_swap_service.process_face_swap(request, user_id=user_id)
    
    def get_face_swap_models(
        self,
        tier: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get available face swap models.
        
        Args:
            tier: Filter by tier (budget, mid, premium)
            
        Returns:
            Dictionary with models and metadata
        """
        return self.face_swap_service.get_available_models(tier=tier)
    
    def recommend_face_swap_model(
        self,
        base_image_resolution: Optional[Dict[str, int]] = None,
        face_image_resolution: Optional[Dict[str, int]] = None,
        user_tier: Optional[str] = None,
        preferences: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Recommend best face swap model for given context.
        
        Args:
            base_image_resolution: Base image dimensions
            face_image_resolution: Face image dimensions
            user_tier: User subscription tier
            preferences: User preferences (prioritize_cost, prioritize_quality)
            
        Returns:
            Dictionary with recommended model and alternatives
        """
        return self.face_swap_service.recommend_model(
            base_image_resolution=base_image_resolution,
            face_image_resolution=face_image_resolution,
            user_tier=user_tier,
            preferences=preferences,
        )

    # ====================
    # UPSCALE STUDIO
    # ====================

    async def upscale_image(
        self,
        request: UpscaleStudioRequest,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Run Upscale Studio operations."""
        logger.info("[Image Studio] Upscale request from user: %s", user_id)
        return await self.upscale_service.process_upscale(request, user_id=user_id)
    
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
        return self.create_service.get_templates(platform=platform, category=category)
    
    def search_templates(self, query: str) -> List[ImageTemplate]:
        """Search templates by query.
        
        Args:
            query: Search query
            
        Returns:
            List of matching templates
        """
        return self.create_service.search_templates(query)
    
    def recommend_templates(
        self,
        use_case: str,
        platform: Optional[Platform] = None
    ) -> List[ImageTemplate]:
        """Recommend templates based on use case.
        
        Args:
            use_case: Use case description
            platform: Optional platform filter
            
        Returns:
            List of recommended templates
        """
        return self.create_service.recommend_templates(use_case, platform)
    
    def get_providers(self) -> Dict[str, Any]:
        """Get available image providers and their capabilities.
        
        Returns:
            Dictionary of providers with capabilities
        """
        return {
            "stability": {
                "name": "Stability AI",
                "models": ["ultra", "core", "sd3.5-large"],
                "capabilities": ["text-to-image", "editing", "upscaling", "control", "3d"],
                "max_resolution": (2048, 2048),
                "cost_range": "3-8 credits per image",
            },
            "wavespeed": {
                "name": "WaveSpeed AI",
                "models": ["ideogram-v3-turbo", "qwen-image"],
                "capabilities": ["text-to-image", "photorealistic", "fast-generation"],
                "max_resolution": (1024, 1024),
                "cost_range": "$0.05-$0.10 per image",
            },
            "huggingface": {
                "name": "HuggingFace",
                "models": ["FLUX.1-Krea-dev", "RunwayML"],
                "capabilities": ["text-to-image", "image-to-image"],
                "max_resolution": (1024, 1024),
                "cost_range": "Free tier available",
            },
            "gemini": {
                "name": "Google Gemini",
                "models": ["imagen-3.0"],
                "capabilities": ["text-to-image", "conversational-editing"],
                "max_resolution": (1024, 1024),
                "cost_range": "Free tier available",
            }
        }
    

    def get_cost_catalog(self) -> Dict[str, Any]:
        """Return backend-driven cost hints for dashboard modules."""
        return {
            "updated_at": "backend-static-v1",
            "confidence": "estimated",
            "modules": {
                "create": {"estimate": "$0.03 - $0.08 / image", "notes": "Depends on provider/model and variation count."},
                "edit": {"estimate": "$0.08 - $0.30 / edit", "notes": "Depends on selected edit operation and model."},
                "upscale": {"estimate": "$0.10 - $0.32 / image", "notes": "Creative 4K costs more than fast mode."},
                "transform": {"estimate": "$0.50+ / video", "notes": "Resolution and duration drive cost."},
                "optimizer": {"estimate": "$0.02 - $0.06 / rendition", "notes": "Per-platform rendition estimate."},
                "control": {"estimate": "$0.20 / render", "notes": "Control/styling features can increase compute cost."},
                "compress": {"estimate": "Free", "notes": "No credits required."},
                "processing": {"estimate": "Free for current tools", "notes": "Compression and format conversion only (roadmap features excluded)."},
                "library": {"estimate": "Included in plan", "notes": "Storage overages may apply by tier."},
            }
        }

    # ====================
    # COST ESTIMATION
    # ====================
    
    def estimate_cost(
        self,
        provider: str,
        model: Optional[str],
        operation: str,
        num_images: int = 1,
        resolution: Optional[tuple[int, int]] = None
    ) -> Dict[str, Any]:
        """Estimate cost for image operations.
        
        Args:
            provider: Provider name
            model: Model name
            operation: Operation type (generate, edit, upscale, etc.)
            num_images: Number of images
            resolution: Image resolution (width, height)
            
        Returns:
            Cost estimation details
        """
        # Base costs (adjust based on actual pricing)
        base_costs = {
            "stability": {
                "ultra": 0.08,  # 8 credits
                "core": 0.03,   # 3 credits
                "sd3": 0.065,   # 6.5 credits
            },
            "wavespeed": {
                "ideogram-v3-turbo": 0.10,
                "qwen-image": 0.05,
            },
            "huggingface": {
                "default": 0.0,  # Free tier
            },
            "gemini": {
                "default": 0.0,  # Free tier
            }
        }
        
        # Get base cost
        provider_costs = base_costs.get(provider, {})
        cost_per_image = provider_costs.get(model, provider_costs.get("default", 0.0))
        
        # Calculate total
        total_cost = cost_per_image * num_images
        
        return {
            "provider": provider,
            "model": model,
            "operation": operation,
            "num_images": num_images,
            "resolution": f"{resolution[0]}x{resolution[1]}" if resolution else "default",
            "cost_per_image": cost_per_image,
            "total_cost": total_cost,
            "currency": "USD",
            "estimated": True,
        }
    
    # ====================
    # CONTROL STUDIO
    # ====================

    async def control_image(
        self,
        request: ControlStudioRequest,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Run Control Studio operations."""
        logger.info("[Image Studio] Control request from user: %s", user_id)
        return await self.control_service.process_control(request, user_id=user_id)

    def get_control_operations(self) -> Dict[str, Any]:
        """Expose control operations for UI."""
        return self.control_service.list_operations()

    # ====================
    # SOCIAL OPTIMIZER
    # ====================

    async def optimize_for_social(
        self,
        request: SocialOptimizerRequest,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Optimize image for social media platforms."""
        logger.info("[Image Studio] Social optimization request from user: %s", user_id)
        return self.social_optimizer_service.optimize_image(request)

    def get_social_platform_formats(self, platform: Platform) -> List[Dict[str, Any]]:
        """Get available formats for a social platform."""
        return self.social_optimizer_service.get_platform_formats(platform)

    # ====================
    # PLATFORM SPECS
    # ====================
    
    def get_platform_specs(self, platform: Platform) -> Dict[str, Any]:
        """Get platform specifications and requirements.
        
        Args:
            platform: Platform to get specs for
            
        Returns:
            Platform specifications
        """
        specs = {
            Platform.INSTAGRAM: {
                "name": "Instagram",
                "formats": [
                    {"name": "Feed Post (Square)", "ratio": "1:1", "size": "1080x1080"},
                    {"name": "Feed Post (Portrait)", "ratio": "4:5", "size": "1080x1350"},
                    {"name": "Story", "ratio": "9:16", "size": "1080x1920"},
                    {"name": "Reel", "ratio": "9:16", "size": "1080x1920"},
                ],
                "file_types": ["JPG", "PNG"],
                "max_file_size": "30MB",
            },
            Platform.FACEBOOK: {
                "name": "Facebook",
                "formats": [
                    {"name": "Feed Post", "ratio": "1.91:1", "size": "1200x630"},
                    {"name": "Feed Post (Square)", "ratio": "1:1", "size": "1080x1080"},
                    {"name": "Story", "ratio": "9:16", "size": "1080x1920"},
                    {"name": "Cover Photo", "ratio": "16:9", "size": "820x312"},
                ],
                "file_types": ["JPG", "PNG"],
                "max_file_size": "30MB",
            },
            Platform.TWITTER: {
                "name": "Twitter/X",
                "formats": [
                    {"name": "Post", "ratio": "16:9", "size": "1200x675"},
                    {"name": "Card", "ratio": "2:1", "size": "1200x600"},
                    {"name": "Header", "ratio": "3:1", "size": "1500x500"},
                ],
                "file_types": ["JPG", "PNG", "GIF"],
                "max_file_size": "5MB",
            },
            Platform.LINKEDIN: {
                "name": "LinkedIn",
                "formats": [
                    {"name": "Feed Post", "ratio": "1.91:1", "size": "1200x628"},
                    {"name": "Feed Post (Square)", "ratio": "1:1", "size": "1080x1080"},
                    {"name": "Article", "ratio": "2:1", "size": "1200x627"},
                    {"name": "Company Cover", "ratio": "4:1", "size": "1128x191"},
                ],
                "file_types": ["JPG", "PNG"],
                "max_file_size": "8MB",
            },
            Platform.YOUTUBE: {
                "name": "YouTube",
                "formats": [
                    {"name": "Thumbnail", "ratio": "16:9", "size": "1280x720"},
                    {"name": "Channel Art", "ratio": "16:9", "size": "2560x1440"},
                ],
                "file_types": ["JPG", "PNG"],
                "max_file_size": "2MB",
            },
            Platform.PINTEREST: {
                "name": "Pinterest",
                "formats": [
                    {"name": "Pin", "ratio": "2:3", "size": "1000x1500"},
                    {"name": "Story Pin", "ratio": "9:16", "size": "1080x1920"},
                ],
                "file_types": ["JPG", "PNG"],
                "max_file_size": "20MB",
            },
            Platform.TIKTOK: {
                "name": "TikTok",
                "formats": [
                    {"name": "Video Cover", "ratio": "9:16", "size": "1080x1920"},
                ],
                "file_types": ["JPG", "PNG"],
                "max_file_size": "10MB",
            },
        }
        
        return specs.get(platform, {})
    
    # ====================
    # TRANSFORM STUDIO
    # ====================
    
    async def transform_image_to_video(
        self,
        request: TransformImageToVideoRequest,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Transform image to video using WAN 2.5."""
        logger.info("[Image Studio] Transform image-to-video request from user: %s", user_id)
        return await self.transform_service.transform_image_to_video(request, user_id=user_id or "anonymous")
    
    async def create_talking_avatar(
        self,
        request: TalkingAvatarRequest,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create talking avatar using InfiniteTalk."""
        logger.info("[Image Studio] Talking avatar request from user: %s", user_id)
        return await self.transform_service.create_talking_avatar(request, user_id=user_id or "anonymous")
    
    def estimate_transform_cost(
        self,
        operation: str,
        resolution: str,
        duration: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Estimate cost for transform operation."""
        return self.transform_service.estimate_cost(operation, resolution, duration)

    # ====================
    # COMPRESSION STUDIO
    # ====================
    
    async def compress_image(
        self,
        request: CompressionRequest,
        user_id: Optional[str] = None,
    ) -> CompressionResult:
        """Compress an image with specified settings."""
        logger.info("[Image Studio] Compress image request from user: %s", user_id)
        return await self.compression_service.compress(request, user_id=user_id)
    
    async def compress_batch(
        self,
        requests: List[CompressionRequest],
        user_id: Optional[str] = None,
    ) -> List[CompressionResult]:
        """Compress multiple images."""
        logger.info("[Image Studio] Batch compress request (%d images) from user: %s", len(requests), user_id)
        return await self.compression_service.compress_batch(requests, user_id=user_id)
    
    async def estimate_compression(
        self,
        image_base64: str,
        format: str = "jpeg",
        quality: int = 85,
    ) -> Dict[str, Any]:
        """Estimate compression results without compressing."""
        return await self.compression_service.estimate_compression(image_base64, format, quality)
    
    def get_compression_formats(self) -> List[Dict[str, Any]]:
        """Get supported compression formats."""
        return self.compression_service.get_supported_formats()
    
    def get_compression_presets(self) -> List[Dict[str, Any]]:
        """Get compression presets for common use cases."""
        return self.compression_service.get_presets()

    # ====================
    # FORMAT CONVERTER
    # ====================
    
    async def convert_format(
        self,
        request: FormatConversionRequest,
        user_id: Optional[str] = None,
    ) -> FormatConversionResult:
        """Convert an image to target format."""
        logger.info("[Image Studio] Convert format request from user: %s", user_id)
        return await self.format_converter_service.convert(request, user_id=user_id)
    
    async def convert_format_batch(
        self,
        requests: List[FormatConversionRequest],
        user_id: Optional[str] = None,
    ) -> List[FormatConversionResult]:
        """Convert multiple images."""
        logger.info("[Image Studio] Batch convert format request (%d images) from user: %s", len(requests), user_id)
        return await self.format_converter_service.convert_batch(requests, user_id=user_id)
    
    def get_supported_formats(self) -> List[Dict[str, Any]]:
        """Get supported conversion formats."""
        return self.format_converter_service.get_supported_formats()
    
    def get_format_recommendations(self, source_format: str) -> List[Dict[str, Any]]:
        """Get format recommendations based on source format."""
        return self.format_converter_service.get_format_recommendations(source_format)

