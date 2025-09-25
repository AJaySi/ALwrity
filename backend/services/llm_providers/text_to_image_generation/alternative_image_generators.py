import os
import base64
import logging
import requests
from typing import List, Optional, Dict, Any
from io import BytesIO
from PIL import Image

logger = logging.getLogger(__name__)

class DALLEService:
    """Service for generating images using OpenAI DALL-E API."""
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not found in environment variables")
        else:
            logger.info("DALL-E service initialized successfully")
    
    def generate_images(self, prompt: str, n: int = 1, size: str = "1024x1024") -> List[str]:
        """
        Generate images using DALL-E API.
        
        Args:
            prompt: Text prompt for image generation
            n: Number of images to generate (1-10)
            size: Image size (1024x1024, 1792x1024, 1024x1792)
            
        Returns:
            List of base64 encoded images
        """
        if not self.api_key:
            logger.error("DALL-E API key not available")
            return []
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "dall-e-3",
                "prompt": prompt,
                "n": n,
                "size": size,
                "quality": "standard",
                "response_format": "b64_json"
            }
            
            logger.info(f"Generating DALL-E images with prompt: {prompt[:100]}...")
            
            response = requests.post(
                "https://api.openai.com/v1/images/generations",
                headers=headers,
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                images_b64 = []
                
                for image_data in result.get('data', []):
                    if 'b64_json' in image_data:
                        images_b64.append(image_data['b64_json'])
                
                logger.info(f"✅ DALL-E generated {len(images_b64)} images successfully")
                return images_b64
            else:
                logger.error(f"DALL-E API error: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Error generating images with DALL-E: {str(e)}")
            return []


class StableDiffusionService:
    """Service for generating images using Stable Diffusion API."""
    
    def __init__(self):
        self.api_key = os.getenv('STABILITY_API_KEY')
        if not self.api_key:
            logger.warning("STABILITY_API_KEY not found in environment variables")
        else:
            logger.info("Stable Diffusion service initialized successfully")
    
    def generate_images(self, prompt: str, n: int = 1, aspect_ratio: str = "9:16") -> List[str]:
        """
        Generate images using Stable Diffusion API.
        
        Args:
            prompt: Text prompt for image generation
            n: Number of images to generate (1-4)
            aspect_ratio: Aspect ratio (9:16, 16:9, 1:1, etc.)
            
        Returns:
            List of base64 encoded images
        """
        if not self.api_key:
            logger.error("Stable Diffusion API key not available")
            return []
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Map aspect ratios to Stable Diffusion format
            aspect_ratio_map = {
                "9:16": "9:16",
                "16:9": "16:9", 
                "1:1": "1:1",
                "3:4": "3:4",
                "4:3": "4:3"
            }
            
            sd_aspect_ratio = aspect_ratio_map.get(aspect_ratio, "9:16")
            
            data = {
                "text_prompts": [
                    {
                        "text": prompt,
                        "weight": 1
                    }
                ],
                "cfg_scale": 7,
                "height": 1024,
                "width": 576 if sd_aspect_ratio == "9:16" else 1024,
                "samples": n,
                "steps": 30,
                "style_preset": "photographic"
            }
            
            logger.info(f"Generating Stable Diffusion images with prompt: {prompt[:100]}...")
            
            response = requests.post(
                "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
                headers=headers,
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                images_b64 = []
                
                for artifact in result.get('artifacts', []):
                    if 'base64' in artifact:
                        images_b64.append(artifact['base64'])
                
                logger.info(f"✅ Stable Diffusion generated {len(images_b64)} images successfully")
                return images_b64
            else:
                logger.error(f"Stable Diffusion API error: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Error generating images with Stable Diffusion: {str(e)}")
            return []


class AlternativeImageGenerator:
    """Main service that tries multiple image generation providers."""
    
    def __init__(self):
        self.dalle_service = DALLEService()
        self.stable_diffusion_service = StableDiffusionService()
        
        # Priority order for fallback
        self.providers = [
            ("DALL-E", self.dalle_service.generate_images),
            ("Stable Diffusion", self.stable_diffusion_service.generate_images)
        ]
    
    def generate_images(
        self, 
        prompt: str, 
        aspect_ratio: str = "9:16",
        n: int = 1
    ) -> List[str]:
        """
        Generate images using available providers in priority order.
        
        Args:
            prompt: Text prompt for image generation
            aspect_ratio: Desired aspect ratio
            n: Number of images to generate
            
        Returns:
            List of base64 encoded images
        """
        logger.info(f"Attempting to generate {n} images with prompt: {prompt[:100]}...")
        
        for provider_name, generate_func in self.providers:
            try:
                logger.info(f"Trying {provider_name}...")
                
                if provider_name == "DALL-E":
                    # DALL-E uses different size format
                    size_map = {
                        "9:16": "1024x1792",
                        "16:9": "1792x1024", 
                        "1:1": "1024x1024"
                    }
                    size = size_map.get(aspect_ratio, "1024x1024")
                    images = generate_func(prompt, n=n, size=size)
                else:
                    # Stable Diffusion uses aspect ratio
                    images = generate_func(prompt, n=n, aspect_ratio=aspect_ratio)
                
                if images:
                    logger.info(f"✅ {provider_name} generated {len(images)} images successfully")
                    return images
                else:
                    logger.warning(f"{provider_name} returned no images")
                    
            except Exception as e:
                logger.error(f"Error with {provider_name}: {str(e)}")
                continue
        
        logger.error("All image generation providers failed")
        return []


def test_alternative_generators() -> Dict[str, bool]:
    """
    Test which alternative image generators are available.
    
    Returns:
        Dictionary with provider names and their availability status
    """
    results = {}
    
    # Test DALL-E
    dalle_service = DALLEService()
    results["DALL-E"] = dalle_service.api_key is not None
    
    # Test Stable Diffusion
    sd_service = StableDiffusionService()
    results["Stable Diffusion"] = sd_service.api_key is not None
    
    return results


if __name__ == "__main__":
    # Test the alternative generators
    print("Testing alternative image generators...")
    availability = test_alternative_generators()
    
    for provider, available in availability.items():
        status = "✅ Available" if available else "❌ Not configured"
        print(f"{provider}: {status}")
    
    if any(availability.values()):
        print("\nTesting image generation...")
        generator = AlternativeImageGenerator()
        result = generator.generate_images("A simple test image of a cat", aspect_ratio="1:1", n=1)
        print(f"Generated {len(result)} images")
    else:
        print("\nNo alternative generators are configured. Please set up API keys.")
