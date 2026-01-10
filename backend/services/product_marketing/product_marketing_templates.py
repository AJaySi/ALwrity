"""
Product Marketing Templates Library
Pre-built templates for common product marketing use cases.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum


class TemplateCategory(str, Enum):
    """Template categories."""
    PRODUCT_IMAGE = "product_image"
    PRODUCT_VIDEO = "product_video"
    PRODUCT_AVATAR = "product_avatar"


@dataclass
class ProductImageTemplate:
    """Product image generation template."""
    id: str
    name: str
    category: TemplateCategory
    description: str
    environment: str  # studio, lifestyle, outdoor, minimalist
    background_style: str  # white, transparent, lifestyle, branded
    lighting: str  # natural, studio, dramatic, soft
    style: str  # photorealistic, minimalist, luxury, technical
    angle: str  # front, side, top, 45_degree, 360
    use_cases: List[str]
    prompt_template: Optional[str] = None
    recommended_resolution: str = "1024x1024"


@dataclass
class ProductVideoTemplate:
    """Product video generation template."""
    id: str
    name: str
    category: TemplateCategory
    description: str
    video_type: str  # demo, storytelling, feature_highlight, launch
    resolution: str  # 480p, 720p, 1080p
    duration: int  # 5 or 10 seconds
    use_cases: List[str]
    prompt_template: Optional[str] = None


@dataclass
class ProductAvatarTemplate:
    """Product avatar/explainer video template."""
    id: str
    name: str
    category: TemplateCategory
    description: str
    explainer_type: str  # product_overview, feature_explainer, tutorial, brand_message
    resolution: str  # 480p, 720p
    use_cases: List[str]
    script_template: Optional[str] = None
    prompt_template: Optional[str] = None


class ProductMarketingTemplates:
    """Product Marketing template definitions."""
    
    @classmethod
    def get_product_image_templates(cls) -> List[ProductImageTemplate]:
        """Get all product image templates."""
        return [
            ProductImageTemplate(
                id="ecommerce_product_shot",
                name="E-commerce Product Shot",
                category=TemplateCategory.PRODUCT_IMAGE,
                description="Professional product photography for e-commerce listings. Clean white background, studio lighting, front angle.",
                environment="studio",
                background_style="white",
                lighting="studio",
                style="photorealistic",
                angle="front",
                use_cases=["E-commerce listings", "Product catalogs", "Amazon/Shopify"],
                prompt_template="{product_name} on white background, professional product photography, studio lighting, clean and minimalist, high quality, e-commerce style",
                recommended_resolution="1024x1024",
            ),
            ProductImageTemplate(
                id="lifestyle_product",
                name="Lifestyle Product Image",
                category=TemplateCategory.PRODUCT_IMAGE,
                description="Product in realistic lifestyle setting. Natural environment, authentic use case.",
                environment="lifestyle",
                background_style="lifestyle",
                lighting="natural",
                style="photorealistic",
                angle="45_degree",
                use_cases=["Social media", "Marketing campaigns", "Brand storytelling"],
                prompt_template="{product_name} in realistic lifestyle setting, natural environment, authentic use case, relatable scenario, professional photography",
                recommended_resolution="1024x1024",
            ),
            ProductImageTemplate(
                id="luxury_product_showcase",
                name="Luxury Product Showcase",
                category=TemplateCategory.PRODUCT_IMAGE,
                description="Premium product presentation. Dramatic lighting, elegant composition, luxury aesthetic.",
                environment="studio",
                background_style="minimalist",
                lighting="dramatic",
                style="luxury",
                angle="45_degree",
                use_cases=["Premium brands", "Luxury products", "High-end marketing"],
                prompt_template="{product_name} luxury product showcase, dramatic lighting, elegant composition, premium aesthetic, sophisticated, high-end",
                recommended_resolution="1024x1024",
            ),
            ProductImageTemplate(
                id="technical_product_detail",
                name="Technical Product Detail",
                category=TemplateCategory.PRODUCT_IMAGE,
                description="Technical product photography. Focus on details, specifications, features.",
                environment="studio",
                background_style="white",
                lighting="studio",
                style="technical",
                angle="front",
                use_cases=["Technical products", "Specification sheets", "Product documentation"],
                prompt_template="{product_name} technical product photography, detailed features visible, clean background, professional technical documentation style",
                recommended_resolution="1024x1024",
            ),
            ProductImageTemplate(
                id="social_media_product",
                name="Social Media Product Post",
                category=TemplateCategory.PRODUCT_IMAGE,
                description="Product image optimized for social media. Eye-catching, shareable, engaging.",
                environment="lifestyle",
                background_style="lifestyle",
                lighting="natural",
                style="photorealistic",
                angle="45_degree",
                use_cases=["Instagram", "Facebook", "TikTok", "Pinterest"],
                prompt_template="{product_name} social media product post, eye-catching, shareable, engaging, modern aesthetic, social media optimized",
                recommended_resolution="1024x1024",
            ),
        ]
    
    @classmethod
    def get_product_video_templates(cls) -> List[ProductVideoTemplate]:
        """Get all product video templates."""
        return [
            ProductVideoTemplate(
                id="product_demo_video",
                name="Product Demo Video",
                category=TemplateCategory.PRODUCT_VIDEO,
                description="Product demonstration video showing product in use, showcasing key features and benefits.",
                video_type="demo",
                resolution="720p",
                duration=10,
                use_cases=["Product launches", "Feature showcases", "Marketing campaigns"],
                prompt_template="{product_name} being demonstrated in use, showcasing key features and benefits, professional product demonstration, dynamic camera movement, engaging presentation",
            ),
            ProductVideoTemplate(
                id="product_storytelling",
                name="Product Storytelling Video",
                category=TemplateCategory.PRODUCT_VIDEO,
                description="Narrative-driven product showcase. Emotional connection, compelling visual story.",
                video_type="storytelling",
                resolution="1080p",
                duration=10,
                use_cases=["Brand storytelling", "Emotional marketing", "Campaign videos"],
                prompt_template="Story of {product_name}, narrative-driven product showcase, emotional connection, cinematic storytelling, compelling visual narrative",
            ),
            ProductVideoTemplate(
                id="feature_highlight_video",
                name="Feature Highlight Video",
                category=TemplateCategory.PRODUCT_VIDEO,
                description="Close-up shots highlighting key product features. Feature-focused presentation.",
                video_type="feature_highlight",
                resolution="720p",
                duration=10,
                use_cases=["Feature announcements", "Product updates", "Technical showcases"],
                prompt_template="{product_name} highlighting key features, close-up shots of important details, feature-focused presentation, professional product photography",
            ),
            ProductVideoTemplate(
                id="product_launch_video",
                name="Product Launch Video",
                category=TemplateCategory.PRODUCT_VIDEO,
                description="Exciting product launch reveal. Dynamic presentation, launch event aesthetic.",
                video_type="launch",
                resolution="1080p",
                duration=10,
                use_cases=["Product launches", "Announcements", "Launch events"],
                prompt_template="{product_name} product launch reveal, exciting unveiling, dynamic presentation, professional product showcase, launch event aesthetic",
            ),
        ]
    
    @classmethod
    def get_product_avatar_templates(cls) -> List[ProductAvatarTemplate]:
        """Get all product avatar/explainer templates."""
        return [
            ProductAvatarTemplate(
                id="product_overview_explainer",
                name="Product Overview Explainer",
                category=TemplateCategory.PRODUCT_AVATAR,
                description="Comprehensive product overview. Engaging and informative presentation.",
                explainer_type="product_overview",
                resolution="720p",
                use_cases=["Product introductions", "Landing pages", "Sales presentations"],
                script_template="Welcome! Today I'm excited to introduce {product_name}. {product_description}. This innovative product offers [key benefits]. Let me show you what makes it special...",
                prompt_template="Professional product presentation of {product_name}, engaging and informative, clear communication, confident expression",
            ),
            ProductAvatarTemplate(
                id="feature_explainer",
                name="Feature Explainer Video",
                category=TemplateCategory.PRODUCT_AVATAR,
                description="Detailed feature explanation. Pointing gestures, clear visual communication.",
                explainer_type="feature_explainer",
                resolution="720p",
                use_cases=["Feature announcements", "Product tutorials", "How-to guides"],
                script_template="Let me show you the key features of {product_name}. First, [feature 1] - this allows you to [benefit]. Next, [feature 2] - which enables [benefit]. Finally, [feature 3] - giving you [benefit]...",
                prompt_template="Demonstrating features of {product_name}, detailed explanation, pointing gestures, clear visual communication",
            ),
            ProductAvatarTemplate(
                id="product_tutorial",
                name="Product Tutorial Video",
                category=TemplateCategory.PRODUCT_AVATAR,
                description="Step-by-step product tutorial. Instructional and clear, friendly approach.",
                explainer_type="tutorial",
                resolution="720p",
                use_cases=["User guides", "Onboarding", "Training materials"],
                script_template="Welcome to this tutorial on {product_name}. Today I'll walk you through how to use it. Step 1: [instruction]. Step 2: [instruction]. Step 3: [instruction]...",
                prompt_template="Tutorial presentation for {product_name}, step-by-step explanation, instructional and clear, friendly and approachable",
            ),
            ProductAvatarTemplate(
                id="brand_message_video",
                name="Brand Message Video",
                category=TemplateCategory.PRODUCT_AVATAR,
                description="Brand message delivery. Authentic and compelling brand storytelling.",
                explainer_type="brand_message",
                resolution="720p",
                use_cases=["Brand campaigns", "Mission statements", "Company values"],
                script_template="At [Brand Name], we believe in {product_name} because [brand values]. Our mission is [mission statement]. This product represents [brand message]...",
                prompt_template="Brand message delivery for {product_name}, authentic and compelling, brand storytelling, emotional connection",
            ),
        ]
    
    @classmethod
    def get_template_by_id(cls, template_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific template by ID."""
        # Search in all template types
        for template in cls.get_product_image_templates():
            if template.id == template_id:
                return {
                    "id": template.id,
                    "name": template.name,
                    "category": template.category.value,
                    "description": template.description,
                    "template_data": {
                        "environment": template.environment,
                        "background_style": template.background_style,
                        "lighting": template.lighting,
                        "style": template.style,
                        "angle": template.angle,
                        "recommended_resolution": template.recommended_resolution,
                    },
                    "use_cases": template.use_cases,
                    "prompt_template": template.prompt_template,
                }
        
        for template in cls.get_product_video_templates():
            if template.id == template_id:
                return {
                    "id": template.id,
                    "name": template.name,
                    "category": template.category.value,
                    "description": template.description,
                    "template_data": {
                        "video_type": template.video_type,
                        "resolution": template.resolution,
                        "duration": template.duration,
                    },
                    "use_cases": template.use_cases,
                    "prompt_template": template.prompt_template,
                }
        
        for template in cls.get_product_avatar_templates():
            if template.id == template_id:
                return {
                    "id": template.id,
                    "name": template.name,
                    "category": template.category.value,
                    "description": template.description,
                    "template_data": {
                        "explainer_type": template.explainer_type,
                        "resolution": template.resolution,
                    },
                    "use_cases": template.use_cases,
                    "script_template": template.script_template,
                    "prompt_template": template.prompt_template,
                }
        
        return None
    
    @classmethod
    def get_templates_by_category(cls, category: TemplateCategory) -> List[Dict[str, Any]]:
        """Get all templates for a specific category."""
        if category == TemplateCategory.PRODUCT_IMAGE:
            return [
                {
                    "id": t.id,
                    "name": t.name,
                    "description": t.description,
                    "environment": t.environment,
                    "background_style": t.background_style,
                    "lighting": t.lighting,
                    "style": t.style,
                    "angle": t.angle,
                    "use_cases": t.use_cases,
                    "prompt_template": t.prompt_template,
                    "recommended_resolution": t.recommended_resolution,
                }
                for t in cls.get_product_image_templates()
            ]
        elif category == TemplateCategory.PRODUCT_VIDEO:
            return [
                {
                    "id": t.id,
                    "name": t.name,
                    "description": t.description,
                    "video_type": t.video_type,
                    "resolution": t.resolution,
                    "duration": t.duration,
                    "use_cases": t.use_cases,
                    "prompt_template": t.prompt_template,
                }
                for t in cls.get_product_video_templates()
            ]
        elif category == TemplateCategory.PRODUCT_AVATAR:
            return [
                {
                    "id": t.id,
                    "name": t.name,
                    "description": t.description,
                    "explainer_type": t.explainer_type,
                    "resolution": t.resolution,
                    "use_cases": t.use_cases,
                    "script_template": t.script_template,
                    "prompt_template": t.prompt_template,
                }
                for t in cls.get_product_avatar_templates()
            ]
        return []
    
    @classmethod
    def apply_template(
        cls,
        template_id: str,
        product_name: str,
        product_description: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Apply a template to product data.
        
        Args:
            template_id: Template ID to apply
            product_name: Product name
            product_description: Product description (optional)
            **kwargs: Additional template-specific parameters
            
        Returns:
            Template configuration ready for use
        """
        template = cls.get_template_by_id(template_id)
        if not template:
            raise ValueError(f"Template not found: {template_id}")
        
        # Format prompt/script templates with product data
        result = template.copy()
        
        if result.get("prompt_template"):
            result["prompt"] = result["prompt_template"].format(
                product_name=product_name,
                product_description=product_description or product_name,
                **kwargs
            )
        
        if result.get("script_template"):
            result["script"] = result["script_template"].format(
                product_name=product_name,
                product_description=product_description or product_name,
                **kwargs
            )
        
        return result
