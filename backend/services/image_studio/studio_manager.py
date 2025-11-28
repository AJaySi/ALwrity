"""Image Studio Manager - Main orchestration service for all image operations."""

from typing import Optional, Dict, Any, List

from .create_service import CreateStudioService, CreateStudioRequest
from .edit_service import EditStudioService, EditStudioRequest
from .upscale_service import UpscaleStudioService, UpscaleStudioRequest
from .control_service import ControlStudioService, ControlStudioRequest
from .social_optimizer_service import SocialOptimizerService, SocialOptimizerRequest
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

