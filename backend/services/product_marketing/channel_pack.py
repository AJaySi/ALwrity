"""
Channel Pack Service
Maps channels to templates, copy frameworks, and platform-specific optimizations.
"""

from typing import Dict, Any, List, Optional
from loguru import logger

from services.image_studio.templates import Platform, TemplateManager
from services.image_studio.social_optimizer_service import SocialOptimizerService


class ChannelPackService:
    """Service to build channel-specific asset packs."""
    
    def __init__(self):
        """Initialize Channel Pack Service."""
        self.template_manager = TemplateManager()
        self.social_optimizer = SocialOptimizerService()
        self.logger = logger
        logger.info("[Channel Pack] Service initialized")
    
    def get_channel_pack(
        self,
        channel: str,
        asset_type: str = "social_post"
    ) -> Dict[str, Any]:
        """
        Get channel-specific pack configuration.
        
        Args:
            channel: Target channel (instagram, linkedin, tiktok, facebook, twitter, pinterest, youtube)
            asset_type: Type of asset (social_post, story, reel, cover, etc.)
            
        Returns:
            Channel pack configuration with templates, dimensions, copy frameworks
        """
        try:
            # Map channel string to Platform enum
            platform_map = {
                'instagram': Platform.INSTAGRAM,
                'linkedin': Platform.LINKEDIN,
                'tiktok': Platform.TIKTOK,
                'facebook': Platform.FACEBOOK,
                'twitter': Platform.TWITTER,
                'pinterest': Platform.PINTEREST,
                'youtube': Platform.YOUTUBE,
            }
            
            platform = platform_map.get(channel.lower())
            if not platform:
                raise ValueError(f"Unsupported channel: {channel}")
            
            # Get templates for this platform
            templates = self.template_manager.get_platform_templates().get(platform, [])
            
            # Get platform formats
            formats = self.social_optimizer.get_platform_formats(platform)
            
            # Build channel pack
            pack = {
                "channel": channel,
                "platform": platform.value,
                "asset_type": asset_type,
                "templates": [
                    {
                        "id": t.id,
                        "name": t.name,
                        "dimensions": f"{t.aspect_ratio.width}x{t.aspect_ratio.height}",
                        "aspect_ratio": t.aspect_ratio.ratio,
                        "recommended_provider": t.recommended_provider,
                        "quality": t.quality,
                    }
                    for t in templates
                ],
                "formats": formats,
                "copy_framework": self._get_copy_framework(channel, asset_type),
                "optimization_tips": self._get_optimization_tips(channel),
            }
            
            logger.info(f"[Channel Pack] Built pack for {channel} ({asset_type})")
            return pack
            
        except Exception as e:
            logger.error(f"[Channel Pack] Error building pack: {str(e)}")
            return {
                "channel": channel,
                "error": str(e),
            }
    
    def _get_copy_framework(
        self,
        channel: str,
        asset_type: str
    ) -> Dict[str, Any]:
        """Get copy framework for channel and asset type."""
        frameworks = {
            "instagram": {
                "social_post": {
                    "caption_length": "125-150 words optimal",
                    "hashtags": "5-10 relevant hashtags",
                    "cta": "Clear call-to-action in first line",
                    "emoji": "Use 1-3 emojis strategically",
                },
                "story": {
                    "text_overlay": "Keep text minimal, readable at small size",
                    "cta": "Swipe-up or link sticker",
                },
            },
            "linkedin": {
                "social_post": {
                    "length": "150-300 words for maximum engagement",
                    "hashtags": "3-5 professional hashtags",
                    "tone": "Professional, thought-leadership focused",
                    "cta": "Engage with question or call-to-action",
                },
            },
            "tiktok": {
                "video": {
                    "hook": "Strong hook in first 3 seconds",
                    "caption": "Short, engaging, use trending hashtags",
                    "hashtags": "3-5 trending hashtags",
                },
            },
        }
        
        return frameworks.get(channel, {}).get(asset_type, {})
    
    def _get_optimization_tips(self, channel: str) -> List[str]:
        """Get optimization tips for channel."""
        tips = {
            "instagram": [
                "Use square (1:1) or portrait (4:5) for feed posts",
                "Include text overlay safe zones (15% top/bottom, 10% left/right)",
                "Optimize for mobile viewing",
            ],
            "linkedin": {
                "Use landscape (1.91:1) for feed posts",
                "Professional photography style",
                "Include clear value proposition",
            },
            "tiktok": {
                "Vertical format (9:16) required",
                "Eye-catching first frame",
                "Fast-paced, engaging content",
            },
        }
        
        return tips.get(channel, [])
    
    def build_multi_channel_pack(
        self,
        channels: List[str],
        source_image_base64: str
    ) -> Dict[str, Any]:
        """
        Build optimized asset pack for multiple channels from single source.
        
        Args:
            channels: List of target channels
            source_image_base64: Source image to optimize
            
        Returns:
            Multi-channel pack with optimized variants
        """
        pack_results = []
        
        for channel in channels:
            pack = self.get_channel_pack(channel)
            pack_results.append({
                "channel": channel,
                "pack": pack,
            })
        
        return {
            "source_image": "provided",
            "channels": pack_results,
            "total_variants": len(channels),
        }

