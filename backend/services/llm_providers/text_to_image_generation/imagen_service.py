import os
import base64
import logging
from typing import List, Optional, Dict, Any
from io import BytesIO
from PIL import Image

logger = logging.getLogger(__name__)

# Check if Gemini is available
try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("Google Gemini not available. Install with: pip install google-generativeai")

class ImagenService:
    """Service for generating images using Google Imagen API."""
    
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')  # Imagen uses same API key as Gemini
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not found in environment variables")
        else:
            logger.info("Imagen service initialized successfully")
    
    def generate_images(
        self, 
        prompt: str, 
        number_of_images: int = 1,
        aspect_ratio: str = "1:1"
    ) -> List[str]:
        """
        Generate images using Imagen API.
        
        Args:
            prompt: Text prompt for image generation
            number_of_images: Number of images to generate (1-4)
            aspect_ratio: Aspect ratio (1:1, 3:4, 4:3, 9:16, 16:9)
            
        Returns:
            List of base64 encoded images
        """
        if not GEMINI_AVAILABLE:
            logger.error("Google Gemini library not available")
            return []
        
        if not self.api_key:
            logger.error("Imagen API key not available")
            return []
        
        try:
            # Create Imagen client
            client = genai.Client(api_key=self.api_key)
            
            # Optimize prompt for Imagen
            imagen_prompt = self._optimize_prompt_for_imagen(prompt)
            
            logger.info(f"Generating Imagen images with prompt: {imagen_prompt[:100]}...")
            logger.info(f"Number of images: {number_of_images}")
            logger.info(f"Aspect ratio: {aspect_ratio}")
            
            # Try minimal config first (can work on free usage for some projects)
            try:
                response = client.models.generate_images(
                    model="models/imagen-4.0-generate-001",
                    prompt=imagen_prompt,
                    config=dict(
                        number_of_images=number_of_images,
                    )
                )
            except Exception as e:
                logger.info(f"Imagen minimal config failed ({e}); retrying with aspect_ratio={aspect_ratio}")
                response = client.models.generate_images(
                    model="models/imagen-4.0-generate-001",
                    prompt=imagen_prompt,
                    config=dict(
                        number_of_images=number_of_images,
                        output_mime_type="image/jpeg",
                        aspect_ratio=aspect_ratio,
                        image_size="1K",
                    )
                )
            
            # Extract base64 images from response
            images_b64: List[str] = []
            for generated_image in response.generated_images:
                if hasattr(generated_image, 'image'):
                    # Get image data directly from the generated_image.image object
                    if hasattr(generated_image.image, 'image_bytes'):
                        # Convert image bytes to base64
                        image_bytes = generated_image.image.image_bytes
                        if isinstance(image_bytes, bytes):
                            images_b64.append(base64.b64encode(image_bytes).decode('utf-8'))
                        else:
                            # If already base64 string
                            images_b64.append(str(image_bytes))
                    elif hasattr(generated_image.image, 'data'):
                        # Alternative: if image data is in 'data' attribute
                        image_data = generated_image.image.data
                        if isinstance(image_data, bytes):
                            images_b64.append(base64.b64encode(image_data).decode('utf-8'))
                        else:
                            images_b64.append(str(image_data))
            
            if images_b64:
                logger.info(f"✅ Imagen generated {len(images_b64)} images successfully")
                return images_b64
            else:
                logger.warning("Imagen returned no images")
                return []
                
        except Exception as e:
            logger.error(f"Error generating images with Imagen: {str(e)}")
            return []
    
    def _optimize_prompt_for_imagen(self, prompt: str) -> str:
        """
        Optimize prompt for Imagen API by removing Gemini-specific formatting
        and enhancing it with Imagen best practices.
        """
        # Remove Gemini-specific formatting
        prompt = prompt.replace('\n\nEnhanced prompt:', '')
        prompt = prompt.replace('\n\nAspect ratio:', '')
        
        # Clean up extra whitespace
        prompt = ' '.join(prompt.split())
        
        # Add Imagen-specific enhancements if not present
        if 'professional' in prompt.lower() and 'linkedin' in prompt.lower():
            # Enhance for LinkedIn professional content
            prompt += ", high quality, professional photography, business appropriate"
        
        if 'digital transformation' in prompt.lower() or 'technology' in prompt.lower():
            # Enhance for tech content
            prompt += ", modern, innovative, clean design, corporate aesthetic"
        
        # Ensure prompt doesn't exceed Imagen's 480 token limit
        if len(prompt) > 400:  # Leave some buffer
            prompt = prompt[:400] + "..."
        
        return prompt
    
    def test_imagen_generation(self) -> bool:
        """
        Test if Imagen image generation is working.
        
        Returns:
            True if working, False otherwise
        """
        try:
            test_prompt = "A simple test image of a cat sitting on a wooden floor"
            result = self.generate_images(test_prompt, number_of_images=1, aspect_ratio="1:1")
            return len(result) > 0
        except Exception as e:
            logger.error(f"Imagen image generation test failed: {str(e)}")
            return False


def test_imagen_service() -> Dict[str, Any]:
    """
    Test the Imagen service and return results.
    
    Returns:
        Dictionary with test results
    """
    results = {
        "available": False,
        "api_key_configured": False,
        "test_successful": False,
        "error": None
    }
    
    try:
        service = ImagenService()
        results["api_key_configured"] = service.api_key is not None
        
        if results["api_key_configured"]:
            results["available"] = True
            results["test_successful"] = service.test_imagen_generation()
        else:
            results["error"] = "API key not configured"
            
    except Exception as e:
        results["error"] = str(e)
    
    return results


if __name__ == "__main__":
    # Test the Imagen service
    print("Testing Imagen service...")
    results = test_imagen_service()
    
    print(f"Available: {results['available']}")
    print(f"API Key Configured: {results['api_key_configured']}")
    print(f"Test Successful: {results['test_successful']}")
    
    if results['error']:
        print(f"Error: {results['error']}")
    
    if results['available'] and results['test_successful']:
        print("\n✅ Imagen service is working correctly!")
    else:
        print("\n❌ Imagen service needs configuration or has issues.")
