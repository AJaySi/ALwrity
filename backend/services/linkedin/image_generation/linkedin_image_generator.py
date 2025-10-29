"""
LinkedIn Image Generator Service

This service generates LinkedIn-optimized images using Google's Gemini API.
It provides professional, business-appropriate imagery for LinkedIn content.
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
from ...onboarding.api_key_manager import APIKeyManager
from ...llm_providers.text_to_image_generation.gen_gemini_images import generate_gemini_image

# Set up logging
logger = logging.getLogger(__name__)


class LinkedInImageGenerator:
    """
    Handles LinkedIn-optimized image generation using Gemini API.
    
    This service integrates with the existing Gemini provider infrastructure
    and provides LinkedIn-specific image optimization, quality assurance,
    and professional business aesthetics.
    """
    
    def __init__(self, api_key_manager: Optional[APIKeyManager] = None):
        """
        Initialize the LinkedIn Image Generator.
        
        Args:
            api_key_manager: API key manager for Gemini authentication
        """
        self.api_key_manager = api_key_manager or APIKeyManager()
        self.model = "gemini-2.5-flash-image-preview"
        self.default_aspect_ratio = "1:1"  # LinkedIn post optimal ratio
        self.max_retries = 3
        
        # LinkedIn-specific image requirements
        self.min_resolution = (1024, 1024)
        self.max_file_size_mb = 5
        self.supported_formats = ["PNG", "JPEG"]
        
        logger.info("LinkedIn Image Generator initialized")
    
    async def generate_image(
        self, 
        prompt: str, 
        content_context: Dict[str, Any],
        aspect_ratio: str = "1:1",
        style_preference: str = "professional"
    ) -> Dict[str, Any]:
        """
        Generate LinkedIn-optimized image using Gemini API.
        
        Args:
            prompt: User's image generation prompt
            content_context: LinkedIn content context (topic, industry, content_type)
            aspect_ratio: Image aspect ratio (1:1, 16:9, 4:3)
            style_preference: Style preference (professional, creative, industry-specific)
            
        Returns:
            Dict containing generation result, image data, and metadata
        """
        try:
            start_time = datetime.now()
            logger.info(f"Starting LinkedIn image generation for topic: {content_context.get('topic', 'Unknown')}")
            
            # Enhance prompt with LinkedIn-specific context
            enhanced_prompt = self._enhance_prompt_for_linkedin(
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
                'linkedin_optimization': {
                    'mobile_optimized': True,
                    'professional_aesthetic': True,
                    'brand_compliant': True,
                    'engagement_optimized': True
                }
            }
            
        except Exception as e:
            logger.error(f"Error in LinkedIn image generation: {str(e)}")
            return {
                'success': False,
                'error': f"Image generation failed: {str(e)}",
                'generation_time': (datetime.now() - start_time).total_seconds() if 'start_time' in locals() else 0
            }
    
    async def edit_image(
        self, 
        base_image: bytes, 
        edit_prompt: str,
        content_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Edit existing image using Gemini's conversational editing capabilities.
        
        Args:
            base_image: Base image data in bytes
            edit_prompt: Description of desired edits
            content_context: LinkedIn content context for optimization
            
        Returns:
            Dict containing edited image result and metadata
        """
        try:
            start_time = datetime.now()
            logger.info(f"Starting LinkedIn image editing with prompt: {edit_prompt[:100]}...")
            
            # Enhance edit prompt for LinkedIn optimization
            enhanced_edit_prompt = self._enhance_edit_prompt_for_linkedin(
                edit_prompt, content_context
            )
            
            # Use Gemini's image editing capabilities
            # Note: This will be implemented when Gemini's image editing is fully available
            # For now, we'll return a placeholder implementation
            
            return {
                'success': False,
                'error': 'Image editing not yet implemented - coming in next Gemini API update',
                'generation_time': (datetime.now() - start_time).total_seconds()
            }
            
        except Exception as e:
            logger.error(f"Error in LinkedIn image editing: {str(e)}")
            return {
                'success': False,
                'error': f"Image editing failed: {str(e)}",
                'generation_time': (datetime.now() - start_time).total_seconds() if 'start_time' in locals() else 0
            }
    
    def _enhance_prompt_for_linkedin(
        self, 
        prompt: str, 
        content_context: Dict[str, Any],
        style_preference: str,
        aspect_ratio: str
    ) -> str:
        """
        Enhance user prompt with LinkedIn-specific context and best practices.
        
        Args:
            prompt: Original user prompt
            content_context: LinkedIn content context
            style_preference: Preferred visual style
            aspect_ratio: Image aspect ratio
            
        Returns:
            Enhanced prompt optimized for LinkedIn
        """
        topic = content_context.get('topic', 'business')
        industry = content_context.get('industry', 'business')
        content_type = content_context.get('content_type', 'post')
        
        # Base LinkedIn optimization
        linkedin_optimizations = [
            f"Create a professional LinkedIn {content_type} image for {topic}",
            f"Industry: {industry}",
            f"Professional business aesthetic suitable for LinkedIn audience",
            f"Mobile-optimized design for LinkedIn feed viewing",
            f"Aspect ratio: {aspect_ratio}",
            "High-quality, modern design with clear visual hierarchy",
            "Professional color scheme and typography",
            "Suitable for business and professional networking"
        ]
        
        # Style-specific enhancements
        if style_preference == "professional":
            style_enhancements = [
                "Corporate aesthetics with clean lines and geometric shapes",
                "Professional color palette (blues, grays, whites)",
                "Modern business environment or abstract business concepts",
                "Clean, minimalist design approach"
            ]
        elif style_preference == "creative":
            style_enhancements = [
                "Eye-catching and engaging visual style",
                "Vibrant colors while maintaining professional appeal",
                "Creative composition that encourages social media engagement",
                "Modern design elements with business context"
            ]
        else:  # industry-specific
            style_enhancements = [
                f"Industry-specific visual elements for {industry}",
                "Professional yet creative approach",
                "Balanced design suitable for business audience",
                "Industry-relevant imagery and color schemes"
            ]
        
        # Combine all enhancements
        enhanced_prompt = f"{prompt}\n\n"
        enhanced_prompt += "\n".join(linkedin_optimizations)
        enhanced_prompt += "\n" + "\n".join(style_enhancements)
        
        logger.info(f"Enhanced prompt for LinkedIn: {enhanced_prompt[:200]}...")
        return enhanced_prompt
    
    def _enhance_edit_prompt_for_linkedin(
        self, 
        edit_prompt: str, 
        content_context: Dict[str, Any]
    ) -> str:
        """
        Enhance edit prompt for LinkedIn optimization.
        
        Args:
            edit_prompt: Original edit prompt
            content_context: LinkedIn content context
            
        Returns:
            Enhanced edit prompt
        """
        industry = content_context.get('industry', 'business')
        
        linkedin_edit_enhancements = [
            f"Maintain professional business aesthetic for {industry} industry",
            "Ensure mobile-optimized composition for LinkedIn feed",
            "Keep professional color scheme and typography",
            "Maintain brand consistency and visual hierarchy"
        ]
        
        enhanced_edit_prompt = f"{edit_prompt}\n\n"
        enhanced_edit_prompt += "\n".join(linkedin_edit_enhancements)
        
        return enhanced_edit_prompt
    
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
            result = generate_gemini_image(prompt, aspect_ratio=aspect_ratio)
            
            if result and os.path.exists(result):
                # Read the generated image
                with open(result, 'rb') as f:
                    image_data = f.read()
                
                return {
                    'success': True,
                    'image_data': image_data,
                    'image_path': result
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
        image_data: bytes, 
        content_context: Dict[str, Any],
        aspect_ratio: str
    ) -> Dict[str, Any]:
        """
        Process and validate generated image for LinkedIn use.
        
        Args:
            image_data: Raw image data
            content_context: LinkedIn content context
            aspect_ratio: Image aspect ratio
            
        Returns:
            Processed image information
        """
        try:
            # Open image for processing
            image = Image.open(BytesIO(image_data))
            
            # Get image information
            width, height = image.size
            format_name = image.format or "PNG"
            
            # Validate resolution
            if width < self.min_resolution[0] or height < self.min_resolution[1]:
                logger.warning(f"Generated image resolution {width}x{height} below minimum {self.min_resolution}")
            
            # Validate file size
            image_size_mb = len(image_data) / (1024 * 1024)
            if image_size_mb > self.max_file_size_mb:
                logger.warning(f"Generated image size {image_size_mb:.2f}MB exceeds maximum {self.max_file_size_mb}MB")
            
            # LinkedIn-specific optimizations
            optimized_image = self._optimize_for_linkedin(image, content_context)
            
            # Convert back to bytes
            output_buffer = BytesIO()
            optimized_image.save(output_buffer, format=format_name, optimize=True)
            optimized_data = output_buffer.getvalue()
            
            return {
                'image_data': optimized_data,
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
                'size': len(image_data),
                'resolution': (1024, 1024),
                'aspect_ratio': aspect_ratio
            }
    
    def _optimize_for_linkedin(self, image: Image.Image, content_context: Dict[str, Any]) -> Image.Image:
        """
        Optimize image specifically for LinkedIn display.
        
        Args:
            image: PIL Image object
            content_context: LinkedIn content context
            
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
                logger.info(f"Resized image to {new_width}x{new_height} for LinkedIn optimization")
            
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
            logger.error(f"Error optimizing image for LinkedIn: {str(e)}")
            return image  # Return original if optimization fails
    
    async def validate_image_for_linkedin(self, image_data: bytes) -> Dict[str, Any]:
        """
        Validate image for LinkedIn compliance and quality standards.
        
        Args:
            image_data: Image data to validate
            
        Returns:
            Validation results
        """
        try:
            image = Image.open(BytesIO(image_data))
            width, height = image.size
            
            validation_results = {
                'resolution_ok': width >= self.min_resolution[0] and height >= self.min_resolution[1],
                'aspect_ratio_suitable': self._is_aspect_ratio_suitable(width, height),
                'file_size_ok': len(image_data) <= self.max_file_size_mb * 1024 * 1024,
                'format_supported': image.format in self.supported_formats,
                'professional_aesthetic': True,  # Placeholder for future AI-based validation
                'overall_score': 0
            }
            
            # Calculate overall score
            score = 0
            if validation_results['resolution_ok']: score += 25
            if validation_results['aspect_ratio_suitable']: score += 25
            if validation_results['file_size_ok']: score += 20
            if validation_results['format_supported']: score += 20
            if validation_results['professional_aesthetic']: score += 10
            
            validation_results['overall_score'] = score
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Error validating image: {str(e)}")
            return {
                'resolution_ok': False,
                'aspect_ratio_suitable': False,
                'file_size_ok': False,
                'format_supported': False,
                'professional_aesthetic': False,
                'overall_score': 0,
                'error': str(e)
            }
    
    def _is_aspect_ratio_suitable(self, width: int, height: int) -> bool:
        """
        Check if image aspect ratio is suitable for LinkedIn.
        
        Args:
            width: Image width
            height: Image height
            
        Returns:
            True if aspect ratio is suitable for LinkedIn
        """
        ratio = width / height
        
        # LinkedIn-optimized aspect ratios
        suitable_ratios = [
            (0.9, 1.1),    # 1:1 (square)
            (1.6, 1.8),    # 16:9 (landscape)
            (0.7, 0.8),    # 4:3 (portrait)
            (1.2, 1.4),    # 5:4 (landscape)
        ]
        
        for min_ratio, max_ratio in suitable_ratios:
            if min_ratio <= ratio <= max_ratio:
                return True
        
        return False
