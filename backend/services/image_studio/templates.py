"""Template system for Image Studio with platform-specific presets."""

from dataclasses import dataclass
from typing import Dict, List, Optional, Literal
from enum import Enum


class Platform(str, Enum):
    """Supported social media platforms."""
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    YOUTUBE = "youtube"
    PINTEREST = "pinterest"
    TIKTOK = "tiktok"
    BLOG = "blog"
    EMAIL = "email"
    WEBSITE = "website"


class TemplateCategory(str, Enum):
    """Template categories."""
    SOCIAL_MEDIA = "social_media"
    BLOG_CONTENT = "blog_content"
    AD_CREATIVE = "ad_creative"
    PRODUCT = "product"
    BRAND_ASSETS = "brand_assets"
    EMAIL_MARKETING = "email_marketing"


@dataclass
class AspectRatio:
    """Aspect ratio configuration."""
    ratio: str  # e.g., "1:1", "16:9"
    width: int
    height: int
    label: str  # e.g., "Square", "Widescreen"


@dataclass
class ImageTemplate:
    """Image generation template."""
    id: str
    name: str
    category: TemplateCategory
    platform: Optional[Platform]
    aspect_ratio: AspectRatio
    description: str
    recommended_provider: str
    style_preset: str
    quality: Literal["draft", "standard", "premium"]
    prompt_template: Optional[str] = None
    negative_prompt_template: Optional[str] = None
    use_cases: List[str] = None


class PlatformTemplates:
    """Platform-specific template definitions."""
    
    # Aspect Ratios
    SQUARE_1_1 = AspectRatio("1:1", 1080, 1080, "Square")
    PORTRAIT_4_5 = AspectRatio("4:5", 1080, 1350, "Portrait")
    STORY_9_16 = AspectRatio("9:16", 1080, 1920, "Story/Reel")
    LANDSCAPE_16_9 = AspectRatio("16:9", 1920, 1080, "Landscape")
    WIDE_21_9 = AspectRatio("21:9", 2560, 1080, "Ultra Wide")
    TWITTER_2_1 = AspectRatio("2:1", 1200, 600, "Twitter Card")
    TWITTER_3_1 = AspectRatio("3:1", 1500, 500, "Twitter Header")
    FACEBOOK_1_91_1 = AspectRatio("1.91:1", 1200, 630, "Facebook Feed")
    LINKEDIN_1_91_1 = AspectRatio("1.91:1", 1200, 628, "LinkedIn Feed")
    LINKEDIN_2_1 = AspectRatio("2:1", 1200, 627, "LinkedIn Article")
    LINKEDIN_4_1 = AspectRatio("4:1", 1128, 191, "LinkedIn Cover")
    PINTEREST_2_3 = AspectRatio("2:3", 1000, 1500, "Pinterest Pin")
    YOUTUBE_16_9 = AspectRatio("16:9", 1280, 720, "YouTube Thumbnail")
    FACEBOOK_COVER_16_9 = AspectRatio("16:9", 820, 312, "Facebook Cover")
    
    @classmethod
    def get_platform_templates(cls) -> Dict[Platform, List[ImageTemplate]]:
        """Get all platform-specific templates."""
        return {
            Platform.INSTAGRAM: cls._instagram_templates(),
            Platform.FACEBOOK: cls._facebook_templates(),
            Platform.TWITTER: cls._twitter_templates(),
            Platform.LINKEDIN: cls._linkedin_templates(),
            Platform.YOUTUBE: cls._youtube_templates(),
            Platform.PINTEREST: cls._pinterest_templates(),
            Platform.TIKTOK: cls._tiktok_templates(),
            Platform.BLOG: cls._blog_templates(),
            Platform.EMAIL: cls._email_templates(),
            Platform.WEBSITE: cls._website_templates(),
        }
    
    @classmethod
    def _instagram_templates(cls) -> List[ImageTemplate]:
        """Instagram templates."""
        return [
            ImageTemplate(
                id="instagram_feed_square",
                name="Instagram Feed Post (Square)",
                category=TemplateCategory.SOCIAL_MEDIA,
                platform=Platform.INSTAGRAM,
                aspect_ratio=cls.SQUARE_1_1,
                description="Perfect for Instagram feed posts with maximum visibility",
                recommended_provider="ideogram",
                style_preset="photographic",
                quality="premium",
                use_cases=["Product showcase", "Lifestyle posts", "Brand content"]
            ),
            ImageTemplate(
                id="instagram_feed_portrait",
                name="Instagram Feed Post (Portrait)",
                category=TemplateCategory.SOCIAL_MEDIA,
                platform=Platform.INSTAGRAM,
                aspect_ratio=cls.PORTRAIT_4_5,
                description="Vertical format for maximum feed real estate",
                recommended_provider="ideogram",
                style_preset="photographic",
                quality="premium",
                use_cases=["Fashion", "Food", "Product photography"]
            ),
            ImageTemplate(
                id="instagram_story",
                name="Instagram Story",
                category=TemplateCategory.SOCIAL_MEDIA,
                platform=Platform.INSTAGRAM,
                aspect_ratio=cls.STORY_9_16,
                description="Full-screen vertical stories",
                recommended_provider="ideogram",
                style_preset="digital-art",
                quality="standard",
                use_cases=["Behind-the-scenes", "Announcements", "Quick updates"]
            ),
            ImageTemplate(
                id="instagram_reel_cover",
                name="Instagram Reel Cover",
                category=TemplateCategory.SOCIAL_MEDIA,
                platform=Platform.INSTAGRAM,
                aspect_ratio=cls.STORY_9_16,
                description="Eye-catching reel cover images",
                recommended_provider="ideogram",
                style_preset="cinematic",
                quality="premium",
                use_cases=["Video covers", "Thumbnails", "Highlights"]
            ),
        ]
    
    @classmethod
    def _facebook_templates(cls) -> List[ImageTemplate]:
        """Facebook templates."""
        return [
            ImageTemplate(
                id="facebook_feed",
                name="Facebook Feed Post",
                category=TemplateCategory.SOCIAL_MEDIA,
                platform=Platform.FACEBOOK,
                aspect_ratio=cls.FACEBOOK_1_91_1,
                description="Optimized for Facebook news feed",
                recommended_provider="ideogram",
                style_preset="photographic",
                quality="standard",
                use_cases=["Page posts", "Shared content", "Community posts"]
            ),
            ImageTemplate(
                id="facebook_feed_square",
                name="Facebook Feed Post (Square)",
                category=TemplateCategory.SOCIAL_MEDIA,
                platform=Platform.FACEBOOK,
                aspect_ratio=cls.SQUARE_1_1,
                description="Square format for feed posts",
                recommended_provider="ideogram",
                style_preset="photographic",
                quality="standard",
                use_cases=["Page posts", "Product highlights"]
            ),
            ImageTemplate(
                id="facebook_story",
                name="Facebook Story",
                category=TemplateCategory.SOCIAL_MEDIA,
                platform=Platform.FACEBOOK,
                aspect_ratio=cls.STORY_9_16,
                description="Full-screen vertical stories",
                recommended_provider="ideogram",
                style_preset="digital-art",
                quality="standard",
                use_cases=["Quick updates", "Promotions", "Events"]
            ),
            ImageTemplate(
                id="facebook_cover",
                name="Facebook Cover Photo",
                category=TemplateCategory.SOCIAL_MEDIA,
                platform=Platform.FACEBOOK,
                aspect_ratio=cls.FACEBOOK_COVER_16_9,
                description="Wide cover photo for pages",
                recommended_provider="ideogram",
                style_preset="photographic",
                quality="premium",
                use_cases=["Page branding", "Events", "Seasonal updates"]
            ),
        ]
    
    @classmethod
    def _twitter_templates(cls) -> List[ImageTemplate]:
        """Twitter/X templates."""
        return [
            ImageTemplate(
                id="twitter_post",
                name="Twitter/X Post",
                category=TemplateCategory.SOCIAL_MEDIA,
                platform=Platform.TWITTER,
                aspect_ratio=cls.LANDSCAPE_16_9,
                description="Optimized for Twitter feed",
                recommended_provider="ideogram",
                style_preset="photographic",
                quality="standard",
                use_cases=["Tweets", "News", "Updates"]
            ),
            ImageTemplate(
                id="twitter_card",
                name="Twitter Card",
                category=TemplateCategory.SOCIAL_MEDIA,
                platform=Platform.TWITTER,
                aspect_ratio=cls.TWITTER_2_1,
                description="Twitter card with link preview",
                recommended_provider="ideogram",
                style_preset="digital-art",
                quality="standard",
                use_cases=["Link sharing", "Articles", "Blog posts"]
            ),
            ImageTemplate(
                id="twitter_header",
                name="Twitter Header",
                category=TemplateCategory.SOCIAL_MEDIA,
                platform=Platform.TWITTER,
                aspect_ratio=cls.TWITTER_3_1,
                description="Profile header image",
                recommended_provider="ideogram",
                style_preset="photographic",
                quality="premium",
                use_cases=["Profile branding", "Personal brand", "Business identity"]
            ),
        ]
    
    @classmethod
    def _linkedin_templates(cls) -> List[ImageTemplate]:
        """LinkedIn templates."""
        return [
            ImageTemplate(
                id="linkedin_post",
                name="LinkedIn Post",
                category=TemplateCategory.SOCIAL_MEDIA,
                platform=Platform.LINKEDIN,
                aspect_ratio=cls.LINKEDIN_1_91_1,
                description="Professional feed posts",
                recommended_provider="ideogram",
                style_preset="photographic",
                quality="premium",
                use_cases=["Professional content", "Industry news", "Thought leadership"]
            ),
            ImageTemplate(
                id="linkedin_post_square",
                name="LinkedIn Post (Square)",
                category=TemplateCategory.SOCIAL_MEDIA,
                platform=Platform.LINKEDIN,
                aspect_ratio=cls.SQUARE_1_1,
                description="Square format for LinkedIn feed",
                recommended_provider="ideogram",
                style_preset="photographic",
                quality="premium",
                use_cases=["Quick tips", "Infographics", "Quotes"]
            ),
            ImageTemplate(
                id="linkedin_article",
                name="LinkedIn Article Header",
                category=TemplateCategory.SOCIAL_MEDIA,
                platform=Platform.LINKEDIN,
                aspect_ratio=cls.LINKEDIN_2_1,
                description="Article header images",
                recommended_provider="ideogram",
                style_preset="photographic",
                quality="premium",
                use_cases=["Long-form content", "Articles", "Newsletters"]
            ),
            ImageTemplate(
                id="linkedin_cover",
                name="LinkedIn Company Cover",
                category=TemplateCategory.SOCIAL_MEDIA,
                platform=Platform.LINKEDIN,
                aspect_ratio=cls.LINKEDIN_4_1,
                description="Company page cover photo",
                recommended_provider="ideogram",
                style_preset="photographic",
                quality="premium",
                use_cases=["Company branding", "Recruitment", "Brand identity"]
            ),
        ]
    
    @classmethod
    def _youtube_templates(cls) -> List[ImageTemplate]:
        """YouTube templates."""
        return [
            ImageTemplate(
                id="youtube_thumbnail",
                name="YouTube Thumbnail",
                category=TemplateCategory.SOCIAL_MEDIA,
                platform=Platform.YOUTUBE,
                aspect_ratio=cls.YOUTUBE_16_9,
                description="Eye-catching video thumbnails",
                recommended_provider="ideogram",
                style_preset="cinematic",
                quality="premium",
                use_cases=["Video thumbnails", "Channel branding", "Playlists"]
            ),
            ImageTemplate(
                id="youtube_channel_art",
                name="YouTube Channel Art",
                category=TemplateCategory.SOCIAL_MEDIA,
                platform=Platform.YOUTUBE,
                aspect_ratio=cls.LANDSCAPE_16_9,
                description="Channel banner art",
                recommended_provider="ideogram",
                style_preset="photographic",
                quality="premium",
                use_cases=["Channel branding", "Personal brand", "Business identity"]
            ),
        ]
    
    @classmethod
    def _pinterest_templates(cls) -> List[ImageTemplate]:
        """Pinterest templates."""
        return [
            ImageTemplate(
                id="pinterest_pin",
                name="Pinterest Pin",
                category=TemplateCategory.SOCIAL_MEDIA,
                platform=Platform.PINTEREST,
                aspect_ratio=cls.PINTEREST_2_3,
                description="Vertical pin format",
                recommended_provider="ideogram",
                style_preset="photographic",
                quality="premium",
                use_cases=["Product pins", "DIY guides", "Recipes", "Inspiration"]
            ),
            ImageTemplate(
                id="pinterest_story",
                name="Pinterest Story Pin",
                category=TemplateCategory.SOCIAL_MEDIA,
                platform=Platform.PINTEREST,
                aspect_ratio=cls.STORY_9_16,
                description="Full-screen story pins",
                recommended_provider="ideogram",
                style_preset="digital-art",
                quality="standard",
                use_cases=["Step-by-step guides", "Tutorials", "Quick tips"]
            ),
        ]
    
    @classmethod
    def _tiktok_templates(cls) -> List[ImageTemplate]:
        """TikTok templates."""
        return [
            ImageTemplate(
                id="tiktok_video_cover",
                name="TikTok Video Cover",
                category=TemplateCategory.SOCIAL_MEDIA,
                platform=Platform.TIKTOK,
                aspect_ratio=cls.STORY_9_16,
                description="Vertical video cover",
                recommended_provider="ideogram",
                style_preset="cinematic",
                quality="premium",
                use_cases=["Video covers", "Thumbnails", "Profile highlights"]
            ),
        ]
    
    @classmethod
    def _blog_templates(cls) -> List[ImageTemplate]:
        """Blog content templates."""
        return [
            ImageTemplate(
                id="blog_header",
                name="Blog Header",
                category=TemplateCategory.BLOG_CONTENT,
                platform=Platform.BLOG,
                aspect_ratio=cls.LANDSCAPE_16_9,
                description="Blog post featured image",
                recommended_provider="ideogram",
                style_preset="photographic",
                quality="premium",
                use_cases=["Featured images", "Article headers", "Post thumbnails"]
            ),
            ImageTemplate(
                id="blog_header_wide",
                name="Blog Header (Wide)",
                category=TemplateCategory.BLOG_CONTENT,
                platform=Platform.BLOG,
                aspect_ratio=cls.WIDE_21_9,
                description="Ultra-wide blog header",
                recommended_provider="ideogram",
                style_preset="photographic",
                quality="premium",
                use_cases=["Hero sections", "Wide headers", "Landing pages"]
            ),
        ]
    
    @classmethod
    def _email_templates(cls) -> List[ImageTemplate]:
        """Email marketing templates."""
        return [
            ImageTemplate(
                id="email_banner",
                name="Email Banner",
                category=TemplateCategory.EMAIL_MARKETING,
                platform=Platform.EMAIL,
                aspect_ratio=cls.LANDSCAPE_16_9,
                description="Email header banner",
                recommended_provider="ideogram",
                style_preset="photographic",
                quality="standard",
                use_cases=["Email headers", "Newsletter banners", "Promotions"]
            ),
            ImageTemplate(
                id="email_product",
                name="Email Product Image",
                category=TemplateCategory.EMAIL_MARKETING,
                platform=Platform.EMAIL,
                aspect_ratio=cls.SQUARE_1_1,
                description="Product showcase for emails",
                recommended_provider="ideogram",
                style_preset="photographic",
                quality="premium",
                use_cases=["Product highlights", "Promotions", "Offers"]
            ),
        ]
    
    @classmethod
    def _website_templates(cls) -> List[ImageTemplate]:
        """Website templates."""
        return [
            ImageTemplate(
                id="website_hero",
                name="Website Hero Image",
                category=TemplateCategory.BRAND_ASSETS,
                platform=Platform.WEBSITE,
                aspect_ratio=cls.WIDE_21_9,
                description="Hero section background",
                recommended_provider="ideogram",
                style_preset="photographic",
                quality="premium",
                use_cases=["Hero sections", "Landing pages", "Home page banners"]
            ),
            ImageTemplate(
                id="website_banner",
                name="Website Banner",
                category=TemplateCategory.BRAND_ASSETS,
                platform=Platform.WEBSITE,
                aspect_ratio=cls.LANDSCAPE_16_9,
                description="Section banners",
                recommended_provider="ideogram",
                style_preset="photographic",
                quality="premium",
                use_cases=["Section headers", "Category pages", "Feature sections"]
            ),
        ]


class TemplateManager:
    """Manager for image templates with search and recommendation."""
    
    def __init__(self):
        """Initialize template manager."""
        self.templates = PlatformTemplates.get_platform_templates()
        self._all_templates: Optional[List[ImageTemplate]] = None
    
    def get_all_templates(self) -> List[ImageTemplate]:
        """Get all templates across all platforms."""
        if self._all_templates is None:
            self._all_templates = []
            for platform_templates in self.templates.values():
                self._all_templates.extend(platform_templates)
        return self._all_templates
    
    def get_by_platform(self, platform: Platform) -> List[ImageTemplate]:
        """Get templates for a specific platform."""
        return self.templates.get(platform, [])
    
    def get_by_category(self, category: TemplateCategory) -> List[ImageTemplate]:
        """Get templates by category."""
        all_templates = self.get_all_templates()
        return [t for t in all_templates if t.category == category]
    
    def get_by_id(self, template_id: str) -> Optional[ImageTemplate]:
        """Get template by ID."""
        all_templates = self.get_all_templates()
        for template in all_templates:
            if template.id == template_id:
                return template
        return None
    
    def search(self, query: str) -> List[ImageTemplate]:
        """Search templates by query."""
        query = query.lower()
        all_templates = self.get_all_templates()
        results = []
        
        for template in all_templates:
            # Search in name, description, and use cases
            searchable = (
                template.name.lower() + " " +
                template.description.lower() + " " +
                " ".join(template.use_cases or []).lower()
            )
            if query in searchable:
                results.append(template)
        
        return results
    
    def recommend_for_use_case(self, use_case: str, platform: Optional[Platform] = None) -> List[ImageTemplate]:
        """Recommend templates based on use case and platform."""
        use_case_lower = use_case.lower()
        all_templates = self.get_all_templates()
        
        # Filter by platform if specified
        if platform:
            all_templates = [t for t in all_templates if t.platform == platform]
        
        # Find matching templates
        matches = []
        for template in all_templates:
            if template.use_cases:
                for case in template.use_cases:
                    if use_case_lower in case.lower():
                        matches.append(template)
                        break
        
        return matches
    
    def get_aspect_ratio_options(self) -> List[AspectRatio]:
        """Get all available aspect ratios."""
        return [
            PlatformTemplates.SQUARE_1_1,
            PlatformTemplates.PORTRAIT_4_5,
            PlatformTemplates.STORY_9_16,
            PlatformTemplates.LANDSCAPE_16_9,
            PlatformTemplates.WIDE_21_9,
            PlatformTemplates.TWITTER_2_1,
            PlatformTemplates.TWITTER_3_1,
            PlatformTemplates.FACEBOOK_1_91_1,
            PlatformTemplates.LINKEDIN_1_91_1,
            PlatformTemplates.LINKEDIN_2_1,
            PlatformTemplates.LINKEDIN_4_1,
            PlatformTemplates.PINTEREST_2_3,
            PlatformTemplates.YOUTUBE_16_9,
            PlatformTemplates.FACEBOOK_COVER_16_9,
        ]

