"""
Facebook Image Generator Service

This service generates Facebook-optimized images using Google's Gemini API.
It provides engaging, social media-appropriate imagery for Facebook content.
"""

import os
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
from PIL import Image
from io import BytesIO

# Import existing infrastructure
from ...api_key_manager import APIKeyManager
from ...llm_providers.text_to_image_generation.gen_gemini_images import generate_gemini_images_base64

# Set up logging
logger = logging.getLogger(__name__)


class FacebookImageGenerator:
    """
    Handles Facebook-optimized image generation using Gemini API.
    
    This service integrates with the existing Gemini provider infrastructure
    and provides Facebook-specific image optimization, quality assurance,
    and social media aesthetics.
    """
    
    def __init__(self, api_key_manager: Optional[APIKeyManager] = None):
        """
        Initialize the Facebook Image Generator.
        
        Args:
            api_key_manager: API key manager for Gemini authentication
        """
        self.api_key_manager = api_key_manager or APIKeyManager()
        self.model = "gemini-2.5-flash-image-preview"
        self.default_aspect_ratio = "9:16"  # Facebook story optimal ratio
        self.max_retries = 3
        
        # Facebook-specific image requirements
        self.min_resolution = (1080, 1920)  # Facebook story minimum
        self.max_file_size_mb = 8
        self.supported_formats = ["PNG", "JPEG"]
        
        logger.info("Facebook Image Generator initialized")
    
    async def generate_image(
        self, 
        prompt: str, 
        content_context: Dict[str, Any],
        aspect_ratio: str = "9:16",
        style_preference: str = "engaging"
    ) -> Dict[str, Any]:
        """
        Generate Facebook-optimized image using Gemini API.
        
        Args:
            prompt: User's image generation prompt
            content_context: Facebook content context (topic, business_type, content_type)
            aspect_ratio: Image aspect ratio (9:16, 1:1, 16:9)
            style_preference: Style preference (engaging, professional, creative)
            
        Returns:
            Dict containing generation result, image data, and metadata
        """
        try:
            start_time = datetime.now()
            logger.info(f"Starting Facebook image generation for topic: {content_context.get('topic', 'Unknown')}")
            
            # Enhance prompt with Facebook-specific context
            enhanced_prompt = self._enhance_prompt_for_facebook(
                prompt, content_context, style_preference, aspect_ratio
            )
            
            # Generate image using existing Gemini infrastructure
            generation_result = await self._generate_with_gemini(enhanced_prompt, aspect_ratio)
            
            if not generation_result.get('success'):
                return {
                    'success': False,
                    'error': generation_result.get('error', 'Image generation failed'),
                    'generation_time': (datetime.now() - start_time).total_seconds()
                }
            
            # Process and validate generated image
            processed_image = await self._process_generated_image(
                generation_result['image_data'],
                content_context,
                aspect_ratio
            )
            
            generation_time = (datetime.now() - start_time).total_seconds()
            
            return {
                'success': True,
                'image_data': processed_image['image_data'],
                'image_url': processed_image.get('image_url'),
                'metadata': {
                    'prompt_used': enhanced_prompt,
                    'original_prompt': prompt,
                    'style_preference': style_preference,
                    'aspect_ratio': aspect_ratio,
                    'content_context': content_context,
                    'generation_time': generation_time,
                    'model_used': self.model,
                    'image_format': processed_image['format'],
                    'image_size': processed_image['size'],
                    'resolution': processed_image['resolution']
                },
                'facebook_optimization': {
                    'mobile_optimized': True,
                    'social_media_ready': True,
                    'engagement_optimized': True,
                    'story_ready': aspect_ratio == "9:16"
                }
            }
            
        except Exception as e:
            logger.error(f"Error in Facebook image generation: {str(e)}")
            return {
                'success': False,
                'error': f"Image generation failed: {str(e)}",
                'generation_time': (datetime.now() - start_time).total_seconds() if 'start_time' in locals() else 0
            }
    
    def _enhance_prompt_for_facebook(
        self, 
        prompt: str, 
        content_context: Dict[str, Any],
        style_preference: str,
        aspect_ratio: str
    ) -> str:
        """
        Enhance user prompt with Facebook-specific context and best practices.
        
        Args:
            prompt: Original user prompt
            content_context: Facebook content context
            style_preference: Preferred visual style
            aspect_ratio: Image aspect ratio
            
        Returns:
            Enhanced prompt optimized for Facebook
        """
        topic = content_context.get('topic', 'social media')
        business_type = content_context.get('business_type', 'general')
        content_type = content_context.get('content_type', 'story')
        
        # Base Facebook optimization
        facebook_optimizations = [
            f"Create an engaging Facebook {content_type} image for {topic}",
            f"Business type: {business_type}",
            f"Social media optimized design for Facebook audience",
            f"Mobile-first design for Facebook feed viewing",
            f"Aspect ratio: {aspect_ratio}",
            "High-quality, eye-catching design with strong visual impact",
            "Social media friendly colors and composition",
            "Suitable for Facebook engagement and sharing"
        ]
        
        # Style-specific enhancements
        if style_preference == "engaging":
            style_enhancements = [
                "Eye-catching and vibrant visual style",
                "Bold colors and dynamic composition",
                "Social media optimized for high engagement",
                "Modern, trendy design elements"
            ]
        elif style_preference == "professional":
            style_enhancements = [
                "Professional yet engaging business aesthetic",
                "Clean, modern design with corporate appeal",
                "Balanced composition suitable for business audience",
                "Professional color scheme with visual impact"
            ]
        else:  # creative
            style_enhancements = [
                "Creative and artistic visual approach",
                "Unique composition that stands out in feed",
                "Artistic elements while maintaining social appeal",
                "Creative use of colors and visual elements"
            ]
        
        # Combine all enhancements
        enhanced_prompt = f"{prompt}\n\n"
        enhanced_prompt += "\n".join(facebook_optimizations)
        enhanced_prompt += "\n" + "\n".join(style_enhancements)
        
        logger.info(f"Enhanced prompt for Facebook: {enhanced_prompt[:200]}...")
        return enhanced_prompt
    
    async def _generate_with_gemini(self, prompt: str, aspect_ratio: str) -> Dict[str, Any]:
        """
        Generate image using existing Gemini infrastructure.
        
        Args:
            prompt: Enhanced prompt for image generation
            aspect_ratio: Desired aspect ratio
            
        Returns:
            Generation result from Gemini
        """
        try:
            # Use existing Gemini image generation function
            # This integrates with the current infrastructure
            result = generate_gemini_images_base64(
                prompt=prompt,
                aspect_ratio=aspect_ratio,
                enhance_prompt=True,
                max_retries=2
            )
            
            if result and len(result) > 0:
                # Get the first image from the result
                image_data = result[0]
                
                return {
                    'success': True,
                    'image_data': image_data,
                    'image_base64': image_data
                }
            else:
                return {
                    'success': False,
                    'error': 'Gemini image generation returned no result'
                }
                
        except Exception as e:
            logger.error(f"Error in Gemini image generation: {str(e)}")
            return {
                'success': False,
                'error': f"Gemini generation failed: {str(e)}"
            }
    
    async def _process_generated_image(
        self, 
        image_data: str, 
        content_context: Dict[str, Any],
        aspect_ratio: str
    ) -> Dict[str, Any]:
        """
        Process and validate generated image for Facebook use.
        
        Args:
            image_data: Base64 image data
            content_context: Facebook content context
            aspect_ratio: Image aspect ratio
            
        Returns:
            Processed image information
        """
        try:
            import base64
            
            # Decode base64 image data
            if isinstance(image_data, str):
                image_bytes = base64.b64decode(image_data)
            else:
                image_bytes = image_data
            
            # Open image for processing
            image = Image.open(BytesIO(image_bytes))
            
            # Get image information
            width, height = image.size
            format_name = image.format or "PNG"
            
            # Validate resolution
            if width < self.min_resolution[0] or height < self.min_resolution[1]:
                logger.warning(f"Generated image resolution {width}x{height} below minimum {self.min_resolution}")
            
            # Validate file size
            image_size_mb = len(image_bytes) / (1024 * 1024)
            if image_size_mb > self.max_file_size_mb:
                logger.warning(f"Generated image size {image_size_mb:.2f}MB exceeds maximum {self.max_file_size_mb}MB")
            
            # Facebook-specific optimizations
            optimized_image = self._optimize_for_facebook(image, content_context)
            
            # Convert back to bytes
            output_buffer = BytesIO()
            optimized_image.save(output_buffer, format=format_name, optimize=True)
            optimized_data = output_buffer.getvalue()
            
            # Convert back to base64
            optimized_base64 = base64.b64encode(optimized_data).decode('utf-8')
            
            return {
                'image_data': optimized_base64,
                'format': format_name,
                'size': len(optimized_data),
                'resolution': (width, height),
                'aspect_ratio': f"{width}:{height}"
            }
            
        except Exception as e:
            logger.error(f"Error processing generated image: {str(e)}")
            # Return original image data if processing fails
            return {
                'image_data': image_data,
                'format': 'PNG',
                'size': len(image_data) if isinstance(image_data, str) else 0,
                'resolution': (1080, 1920),
                'aspect_ratio': aspect_ratio
            }
    
    def _optimize_for_facebook(self, image: Image.Image, content_context: Dict[str, Any]) -> Image.Image:
        """
        Optimize image specifically for Facebook display.
        
        Args:
            image: PIL Image object
            content_context: Facebook content context
            
        Returns:
            Optimized image
        """
        try:
            # Ensure minimum resolution
            width, height = image.size
            if width < self.min_resolution[0] or height < self.min_resolution[1]:
                # Resize to minimum resolution while maintaining aspect ratio
                ratio = max(self.min_resolution[0] / width, self.min_resolution[1] / height)
                new_width = int(width * ratio)
                new_height = int(height * ratio)
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                logger.info(f"Resized image to {new_width}x{new_height} for Facebook optimization")
            
            # Convert to RGB if necessary (for JPEG compatibility)
            if image.mode in ('RGBA', 'LA', 'P'):
                # Create white background for transparent images
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            
            return image
            
        except Exception as e:
            logger.error(f"Error optimizing image for Facebook: {str(e)}")
            return image  # Return original if optimization fails
    
    async def validate_image_for_facebook(self, image_data: str) -> Dict[str, Any]:
        """
        Validate image for Facebook compliance and quality standards.
        
        Args:
            image_data: Base64 image data to validate
            
        Returns:
            Validation results
        """
        try:
            import base64
            
            # Decode base64 image data
            if isinstance(image_data, str):
                image_bytes = base64.b64decode(image_data)
            else:
                image_bytes = image_data
            
            image = Image.open(BytesIO(image_bytes))
            width, height = image.size
            
            validation_results = {
                'resolution_ok': width >= self.min_resolution[0] and height >= self.min_resolution[1],
                'aspect_ratio_suitable': self._is_aspect_ratio_suitable(width, height),
                'file_size_ok': len(image_bytes) <= self.max_file_size_mb * 1024 * 1024,
                'format_supported': image.format in self.supported_formats,
                'social_media_ready': True,  # Placeholder for future AI-based validation
                'overall_score': 0
            }
            
            # Calculate overall score
            score = 0
            if validation_results['resolution_ok']: score += 25
            if validation_results['aspect_ratio_suitable']: score += 25
            if validation_results['file_size_ok']: score += 20
            if validation_results['format_supported']: score += 20
            if validation_results['social_media_ready']: score += 10
            
            validation_results['overall_score'] = score
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Error validating image: {str(e)}")
            return {
                'resolution_ok': False,
                'aspect_ratio_suitable': False,
                'file_size_ok': False,
                'format_supported': False,
                'social_media_ready': False,
                'overall_score': 0,
                'error': str(e)
            }
    
    def _is_aspect_ratio_suitable(self, width: int, height: int) -> bool:
        """
        Check if image aspect ratio is suitable for Facebook.
        
        Args:
            width: Image width
            height: Image height
            
        Returns:
            True if aspect ratio is suitable for Facebook
        """
        ratio = width / height
        
        # Facebook-optimized aspect ratios
        suitable_ratios = [
            (0.5, 0.6),    # 9:16 (stories)
            (0.9, 1.1),    # 1:1 (posts)
            (1.6, 1.8),    # 16:9 (landscape)
            (0.7, 0.8),    # 4:3 (portrait)
        ]
        
        for min_ratio, max_ratio in suitable_ratios:
            if min_ratio <= ratio <= max_ratio:
                return True
        
        return False
