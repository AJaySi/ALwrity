import os
import sys
import time
import datetime
import base64
import random
from typing import List, Optional, Tuple
from PIL import Image
from io import BytesIO
import logging

# Import APIKeyManager
from ...api_key_manager import APIKeyManager

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    logging.getLogger('gemini_image_generator').warning(
        "Google genai library not available. Install with: pip install google-generativeai"
    )


from .save_image import save_generated_image
from .alternative_image_generators import AlternativeImageGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('gemini_image_generator')

# Imagen fallback configuration
IMAGEN_FALLBACK_CONFIG = {
    'enabled': os.getenv('IMAGEN_FALLBACK_ENABLED', 'true').lower() == 'true',  # Master switch for Imagen fallback
    'auto_fallback': os.getenv('IMAGEN_AUTO_FALLBACK', 'true').lower() == 'true',  # Automatically fall back on Gemini failures
    'preferred_model': os.getenv('IMAGEN_MODEL', 'imagen-4.0-generate-001'),  # Fast model for quick generation
    'fallback_aspect_ratios': {
        '1:1': '1:1',
        '3:4': '3:4',
        '4:3': '4:3', 
        '9:16': '9:16',
        '16:9': '16:9'
    },
    'max_images': int(os.getenv('IMAGEN_MAX_IMAGES', '1')),  # Generate 1 image for LinkedIn posts
}

# Log configuration on startup
logger.info(f"🔄 Imagen fallback configuration: {IMAGEN_FALLBACK_CONFIG}")

# With image generation in Gemini, your imagination is the limit.
# Follow Google AI best practices for detailed prompts and iterative refinement.

# Generate images using Gemini
# Gemini 2.0 Flash Experimental supports the ability to output text and inline images. 
# This lets you use Gemini to conversationally edit images or generate outputs with interwoven text (for example, generating a blog post with text and images in a single turn).
# Note: Make sure to include responseModalities: ["Text", "Image"] in your generation configuration for text and image output with gemini-2.0-flash-exp-image-generation. Image only is not allowed.


class AIPromptGenerator:
    """
    Generates enhanced AI image prompts based on user keywords,
    following the guidelines of the Imagen documentation.
    """

    def __init__(self):
        self.photography_styles = ["photo", "photograph"]
        self.art_styles = ["painting", "sketch", "drawing", "illustration", "digital art", "render"]
        self.art_techniques = ["technical pencil drawing", "charcoal drawing", "color pencil drawing", "pastel painting", "digital art", "art deco (poster)", "impressionist painting", "renaissance painting", "pop art"]
        self.camera_proximity = ["close-up", "zoomed out", "taken from far away"]
        self.camera_position = ["aerial", "from below"]
        self.lighting = ["natural lighting", "dramatic lighting", "warm lighting", "cold lighting", "studio lighting", "golden hour lighting"]
        self.camera_settings = ["motion blur", "soft focus", "bokeh", "portrait"]
        self.lens_types = ["35mm lens", "50mm lens", "fisheye lens", "wide angle lens", "macro lens", "telephoto lens"]
        self.film_types = ["black and white film", "polaroid"]
        self.materials = ["made of cheese", "made of paper", "made of neon tubes", "metallic", "glass", "wooden", "stone"]
        self.shapes = ["in the shape of a bird", "angular", "curved", "geometric"]
        self.quality_modifiers_general = ["high-quality", "beautiful", "stylized", "detailed", "epic", "grand"]
        self.quality_modifiers_photo = ["4K", "HDR", "studio photo", "professional photo", "photorealistic"]
        self.quality_modifiers_art = ["by a professional artist", "intricate details", "masterpiece"]
        self.aspect_ratios = ["1:1 aspect ratio", "4:3 aspect ratio", "3:4 aspect ratio", "16:9 aspect ratio", "9:16 aspect ratio"]
        self.photorealistic_modifiers = {
            "portraits": ["prime lens", "zoom lens", "24-35mm", "black and white film", "film noir", "shallow depth of field", "duotone (mention two colors)"],
            "objects": ["macro lens", "60-105mm", "high detail", "precise focusing", "controlled lighting"],
            "motion": ["telephoto zoom lens", "100-400mm", "fast shutter speed", "action shot", "movement tracking"],
            "wide-angle": ["wide-angle lens", "10-24mm", "long exposure", "sharp focus", "smooth water or clouds", "astro photography"]
        }

    def generate_prompt(self, keywords):
        """
        Generates an enhanced AI image prompt based on user-provided keywords.

        Args:
            keywords (list): A list of keywords describing the desired image.

        Returns:
            str: An enhanced AI image prompt.
        """
        if not keywords:
            return "A beautiful image."

        prompt_parts = []
        subject = " ".join(keywords)
        prompt_parts.append(subject)

        # Add context and background (optional)
        context_options = ["in a detailed background", "outdoors", "indoors", "in a studio", "with a blurred background"]
        if random.random() < 0.6:  # Add context with a probability
            prompt_parts.append(random.choice(context_options))

        # Add style (optional)
        style_options = self.photography_styles + [f"{art} of" for art in self.art_styles]
        if random.random() < 0.7:
            prompt_parts.insert(0, random.choice(style_options))
            if prompt_parts[0].startswith("painting of") or prompt_parts[0].startswith("sketch of") or prompt_parts[0].startswith("drawing of"):
                if random.random() < 0.5:
                    prompt_parts.append(f"in the style of {random.choice(self.art_techniques)}")

        # Add photography modifiers (if photography style is chosen)
        if any(style in prompt_parts[0] for style in self.photography_styles):
            if random.random() < 0.4:
                prompt_parts.append(random.choice(self.camera_proximity))
            if random.random() < 0.3:
                prompt_parts.append(random.choice(self.camera_position))
            if random.random() < 0.5:
                prompt_parts.append(random.choice(self.lighting))
            if random.random() < 0.3:
                prompt_parts.append(random.choice(self.camera_settings))
            if random.random() < 0.2:
                prompt_parts.append(random.choice(self.lens_types))
            if random.random() < 0.1:
                prompt_parts.append(random.choice(self.film_types))

        # Add shapes and materials (optional)
        if random.random() < 0.3:
            prompt_parts.append(random.choice(self.materials))
        if random.random() < 0.2:
            prompt_parts.append(random.choice(self.shapes))

        # Add quality modifiers (optional)
        if random.random() < 0.6:
            quality_options = self.quality_modifiers_general
            if any(style in prompt_parts[0] for style in self.photography_styles):
                quality_options += self.quality_modifiers_photo
            else:
                quality_options += self.quality_modifiers_art
            prompt_parts.append(random.choice(list(set(quality_options)))) # Avoid duplicates

        # Add aspect ratio (optional)
        if random.random() < 0.2:
            prompt_parts.append(random.choice(self.aspect_ratios))

        return ", ".join(prompt_parts)

    def generate_photorealistic_prompt(self, keywords, focus=""):
        """
        Generates an enhanced AI image prompt specifically for photorealistic images.

        Args:
            keywords (list): A list of keywords describing the desired image.
            focus (str, optional): The focus of the photorealistic image (e.g., "portraits", "objects", "motion", "wide-angle"). Defaults to "".

        Returns:
            str: An enhanced photorealistic AI image prompt.
        """
        if not keywords:
            return "A photorealistic image."

        prompt_parts = ["A photo of", "photorealistic"]
        prompt_parts.append(" ".join(keywords))

        if focus and focus in self.photorealistic_modifiers:
            modifiers = self.photorealistic_modifiers[focus]
            if modifiers:
                num_modifiers = random.randint(1, min(3, len(modifiers)))
                selected_modifiers = random.sample(modifiers, num_modifiers)
                prompt_parts.extend(selected_modifiers)

        # Add general quality modifiers
        if random.random() < 0.5:
            prompt_parts.append(random.choice(self.quality_modifiers_photo))

        # Add lighting
        if random.random() < 0.4:
            prompt_parts.append(random.choice(self.lighting))

        return ", ".join(prompt_parts)

def _ensure_client() -> Optional[object]:
    """Create a Gemini client if available and API key is configured."""
    api_key_manager = APIKeyManager()
    api_key = api_key_manager.get_api_key("gemini")
    if not api_key or genai is None:
        if not api_key:
            logger.warning("No Gemini API key found")
        if genai is None:
            logger.warning("Google Generative AI library not available")
        return None
    try:
        logger.info("Creating Gemini client...")
        # Create a client using the correct API pattern
        # The API key is passed directly to the Client constructor
        client = genai.Client(api_key=api_key)
        logger.info("Gemini client created successfully")
        return client
    except Exception as e:
        logger.error(f"Failed to create Gemini client: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return None


def _generate_imagen_images_base64(prompt: str, aspect_ratio: str = "1:1") -> List[str]:
    """
    Generate images using Imagen API as a fallback method.
    
    This function implements the Imagen API following the official documentation:
    https://ai.google.dev/gemini-api/docs/imagen
    
    Args:
        prompt: Text prompt for image generation
        aspect_ratio: Desired aspect ratio (1:1, 3:4, 4:3, 9:16, 16:9)
    
    Returns:
        List of base64-encoded PNG images
    """
    logger = logging.getLogger('gemini_image_generator')
    logger.info("🔄 Falling back to Imagen API for image generation")
    
    try:
        # Get API key for Imagen (can use same Gemini API key)
        api_key_manager = APIKeyManager()
        api_key = api_key_manager.get_api_key("gemini")  # Imagen uses same API key
        
        if not api_key:
            logger.error("No API key available for Imagen fallback")
            return []
        
        # Create Imagen client
        client = genai.Client(api_key=api_key)
        
        # Map aspect ratio to Imagen format using configuration
        imagen_aspect_ratio = IMAGEN_FALLBACK_CONFIG['fallback_aspect_ratios'].get(aspect_ratio, "1:1")
        
        # Optimize prompt for Imagen (remove Gemini-specific formatting)
        imagen_prompt = _optimize_prompt_for_imagen(prompt)
        
        logger.info(f"Generating Imagen images with prompt: {imagen_prompt[:100]}...")
        logger.info(f"Using aspect ratio: {imagen_aspect_ratio}")
        logger.info(f"Using model: {IMAGEN_FALLBACK_CONFIG['preferred_model']}")
        
        # Generate images using the free Imagen API approach
        response = client.models.generate_images(
            model="models/imagen-4.0-generate-001",
            prompt=imagen_prompt,
            config=dict(
                number_of_images=IMAGEN_FALLBACK_CONFIG['max_images'],
                output_mime_type="image/jpeg",
                aspect_ratio=imagen_aspect_ratio,
                image_size="1K",
            )
        )
        
        # Extract base64 images from response using the new approach
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
            logger.info(f"✅ Imagen fallback successful! Generated {len(images_b64)} images")
            return images_b64
        else:
            logger.warning("Imagen fallback returned no images")
            return []
            
    except Exception as e:
        logger.error(f"❌ Imagen fallback failed: {e}")
        import traceback
        logger.error(f"Imagen error traceback: {traceback.format_exc()}")
        return []


def _optimize_prompt_for_imagen(prompt: str) -> str:
    """
    Optimize prompt for Imagen API by removing Gemini-specific formatting
    and enhancing it with Imagen best practices.
    
    Based on Imagen prompt guide: https://ai.google.dev/gemini-api/docs/imagen
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


def generate_gemini_images_base64(
    prompt: str,
    *,
    keywords: Optional[list] = None,
    style: Optional[str] = None,
    focus: Optional[str] = None,
    enhance_prompt: bool = True,
    aspect_ratio: str = "9:16",
    max_retries: int = 2,
    initial_retry_delay: float = 1.0,
    enable_imagen_fallback: bool = True,
) -> List[str]:
    """
    Return list of base64 PNG images generated from a prompt.
    
    Primary method: Gemini 2.5 Flash Image Preview model
    Fallback method: Imagen API when Gemini fails (quota limits, API errors, etc.)

    Implements best practices per Gemini docs: send text prompt, parse inline image parts,
    and return base64 data suitable for API responses. No Streamlit, no printing.

    Docs: 
    - Gemini: https://ai.google.dev/gemini-api/docs/image-generation
    - Imagen: https://ai.google.dev/gemini-api/docs/imagen
    """
    logger = logging.getLogger('gemini_image_generator')
    logger.info("Generating image (base64) with Gemini 2.5 Flash Image Preview (with Imagen fallback)")

    if enhance_prompt and keywords:
        pg = AIPromptGenerator()
        enhanced = (
            pg.generate_photorealistic_prompt(keywords, focus)
            if style == "photorealistic" and focus
            else pg.generate_prompt(keywords)
        )
        prompt = f"{prompt}\n\nEnhanced prompt: {enhanced}"

    # Optional hint in-text for aspect ratio; API doesn't take ratio param directly
    if aspect_ratio:
        prompt = f"{prompt}\n\nAspect ratio: {aspect_ratio}"

    # Try Gemini first
    client = _ensure_client()
    if client is None:
        logger.warning("Gemini client not available or API key missing")
        if enable_imagen_fallback and IMAGEN_FALLBACK_CONFIG['enabled']:
            logger.info("Falling back to Imagen API")
            return _generate_imagen_images_base64(prompt, aspect_ratio)
        return []

    retry = 0
    delay = initial_retry_delay
    while retry <= max_retries:
        try:
            # Use the new Gemini 2.5 Flash Image Preview model
            response = client.models.generate_content(
                model="gemini-2.5-flash-image-preview",
                contents=[prompt],
            )
            
            images_b64: List[str] = []
            for part in response.candidates[0].content.parts:
                if getattr(part, 'inline_data', None) is not None:
                    # part.inline_data.data is bytes (base64 decoded by SDK?)
                    # Standardize to base64 string for API consumers
                    raw = part.inline_data.data
                    if isinstance(raw, bytes):
                        images_b64.append(base64.b64encode(raw).decode('utf-8'))
                    else:
                        # Some SDKs may already present base64 str
                        images_b64.append(str(raw))
            
            if images_b64:
                logger.info(f"✅ Gemini 2.5 Flash Image Preview generated {len(images_b64)} images successfully")
                return images_b64
            else:
                logger.warning("Gemini 2.5 Flash Image Preview returned no images, falling back to Imagen")
                if enable_imagen_fallback and IMAGEN_FALLBACK_CONFIG['enabled']:
                    return _generate_imagen_images_base64(prompt, aspect_ratio)
                return []
                
        except Exception as e:
            msg = str(e)
            logger.warning(f"Gemini 2.5 Flash Image Preview error: {msg}")
            
            # Check if this is a quota/API error that warrants fallback
            if any(error_type in msg.lower() for error_type in [
                'quota', 'resource_exhausted', 'rate_limit', 'billing', 'api_key', '403', '429'
            ]):
                logger.info("Gemini quota/API error detected, trying alternative generators")
                try:
                    alternative_generator = AlternativeImageGenerator()
                    alternative_images = alternative_generator.generate_images(prompt, aspect_ratio=aspect_ratio, n=1)
                    if alternative_images:
                        logger.info(f"✅ Alternative generator produced {len(alternative_images)} images")
                        return alternative_images
                except Exception as alt_e:
                    logger.error(f"Alternative generators failed: {str(alt_e)}")
                
                # Fall back to Imagen if alternatives fail
                if enable_imagen_fallback and IMAGEN_FALLBACK_CONFIG['enabled']:
                    logger.info("Falling back to Imagen")
                    return _generate_imagen_images_base64(prompt, aspect_ratio)
                return []
            
            # For other errors, retry if possible
            if "503" in msg and retry < max_retries:
                time.sleep(delay)
                delay *= 2
                retry += 1
                continue
            
            # Final fallback for any other errors
            if enable_imagen_fallback and IMAGEN_FALLBACK_CONFIG['enabled']:
                logger.info("Final fallback to Imagen due to Gemini error")
                return _generate_imagen_images_base64(prompt, aspect_ratio)
            return []
    
    # If all retries exhausted, try alternative generators
    logger.info("All Gemini retries exhausted, trying alternative image generators")
    try:
        alternative_generator = AlternativeImageGenerator()
        alternative_images = alternative_generator.generate_images(prompt, aspect_ratio=aspect_ratio, n=1)
        if alternative_images:
            logger.info(f"✅ Alternative generator produced {len(alternative_images)} images")
            return alternative_images
    except Exception as e:
        logger.error(f"Alternative generators failed: {str(e)}")
    
    # Final fallback to Imagen if enabled
    if enable_imagen_fallback and IMAGEN_FALLBACK_CONFIG['enabled']:
        logger.info("Falling back to Imagen as final option")
        return _generate_imagen_images_base64(prompt, aspect_ratio)
    
    return []


def generate_gemini_image(
    prompt,
    keywords=None,
    style=None,
    focus=None,
    enhance_prompt=True,
    max_retries=2,
    initial_retry_delay=1.0,
    aspect_ratio="9:16",
    enable_imagen_fallback=True,
):
    """
    Backward-compatible wrapper that generates a single image file on disk and returns path.
    Now includes Imagen fallback for improved reliability.
    
    Prefer generate_gemini_images_base64 in new code paths.
    """
    logger = logging.getLogger('gemini_image_generator')
    images = generate_gemini_images_base64(
        prompt,
        keywords=keywords,
        style=style,
        focus=focus,
        enhance_prompt=enhance_prompt,
        aspect_ratio=aspect_ratio,
        max_retries=max_retries,
        initial_retry_delay=initial_retry_delay,
        enable_imagen_fallback=enable_imagen_fallback,
    )
    if not images:
        return None
    
    # Persist first image to file for legacy callers
    img_b64 = images[0]
    img_bytes = base64.b64decode(img_b64)
    img = Image.open(BytesIO(img_bytes))
    
    # Update filename to indicate which API was used
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    if 'imagen' in prompt.lower() or 'fallback' in prompt.lower():
        out_name = f'imagen-fallback-image-{timestamp}.png'
    else:
        out_name = f'gemini-native-image-{timestamp}.png'
    
    try:
        img.save(out_name)
        # Also call save_generated_image to reuse existing pipeline
        save_generated_image({"artifacts": [{"base64": img_b64}]})
        logger.info(f"✅ Image saved successfully: {out_name}")
        return out_name
    except Exception as e:
        logger.error(f"❌ Failed to save image: {e}")
        return None


def generate_gemini_image_edit(
    text_prompt: str,
    base_image: str,  # Base64 encoded image
    max_retries: int = 3
) -> Optional[str]:
    """
    Edit an existing image using Gemini 2.5 Flash Image Preview model.
    
    Args:
        text_prompt: Text describing the edit to make
        base_image: Base64 encoded image to edit
        max_retries: Maximum number of retry attempts
        
    Returns:
        Base64 encoded edited image or None if failed
    """
    logger = logging.getLogger('gemini_image_generator')
    
    client = _ensure_client()
    if client is None:
        logger.error("Gemini client not available or API key missing")
        return None
    
    try:
        # Decode base64 image
        image_data = base64.b64decode(base_image)
        image = Image.open(BytesIO(image_data))
        
        logger.info(f"Editing image with prompt: {text_prompt[:100]}...")
        
        # Generate content with text and image input
        response = client.models.generate_content(
            model="gemini-2.5-flash-image-preview",
            contents=[text_prompt, image],
        )
        
        # Extract edited image data
        image_parts = [
            part.inline_data.data
            for part in response.candidates[0].content.parts
            if part.inline_data
        ]
        
        if not image_parts:
            logger.warning("No edited images generated in response")
            return None
        
        # Convert to base64
        edited_image_data = image_parts[0]
        base64_edited_image = base64.b64encode(edited_image_data).decode('utf-8')
        
        logger.info("Successfully edited image")
        return base64_edited_image
            
    except Exception as e:
        logger.error(f"Error editing image with Gemini: {str(e)}")
        return None


def edit_image(image_path, prompt, max_retries=2, initial_retry_delay=1.0):
    """
    - Image editing (text and image to image)
    Example prompt: "Edit this image to make it look like a cartoon"
    Example prompt: [image of a cat] + [image of a pillow] + "Create a cross stitch of my cat on this pillow."
    
    - Multi-turn image editing (chat)
    Example prompts: [upload an image of a blue car.] "Turn this car into a convertible." "Now change the color to yellow."
    
    Image editing with Gemini
    To perform image editing, add an image as input. 
    The following example demonstrats uploading base64 encoded images. 
    For multiple images and larger payloads, check the image input section.

    Args:
        image_path (str): The path to the image to edit.
        prompt (str): The prompt to edit the image with.
        max_retries (int, optional): Maximum number of retry attempts for handling 503 errors. Defaults to 3.
        initial_retry_delay (int, optional): Initial delay in seconds before retrying. Defaults to 2.

    Returns:
        str: The path to the edited image.
    """
    import PIL.Image
    image = PIL.Image.open(image_path)

    retry_count = 0
    retry_delay = initial_retry_delay
    
    while retry_count <= max_retries:
        try:
            client = _ensure_client()
            if client is None:
                return None
            text_input = (prompt)

            logger.info("Sending request to Gemini API for image editing")
            response = client.models.generate_content(
                model="gemini-2.5-flash-image-preview",
                contents=[text_input, image],
            )
            logger.info("Received response from Gemini API for image editing")

            edited_img_name = None
            for part in response.candidates[0].content.parts:
                if getattr(part, 'inline_data', None) is not None:
                    logger.info("Received edited image data from Gemini")
                    edited_image = Image.open(BytesIO(part.inline_data.data))
                    
                    # Save the edited image
                    edited_img_name = f'edited-{os.path.basename(image_path)}'
                    try:
                        logger.info(f"Saving edited image to: {edited_img_name}")
                        edited_image.save(edited_img_name)
                        
                        # Create a dictionary with the expected format for save_generated_image
                        img_response = {
                            "artifacts": [
                                {
                                    "base64": base64.b64encode(open(edited_img_name, "rb").read()).decode('utf-8')
                                }
                            ]
                        }
                        
                        # Call save_generated_image with the correct format
                        save_generated_image(img_response)
                    except Exception as err:
                        logger.error(f"Failed to save edited image: {err}")
            
            logger.info(f"Image editing completed. Edited image name: {edited_img_name}")
            return edited_img_name
        except Exception as err:
            error_message = str(err)
            logger.error(f"Error in edit_image: {err}")
            # Retry on transient 503
            if "503" in error_message and retry_count < max_retries:
                retry_count += 1
                logger.info(f"Retrying in {retry_delay} seconds (attempt {retry_count}/{max_retries})")
                time.sleep(retry_delay)
                # Exponential backoff
                retry_delay *= 2
            else:
                return None
    # If we've exhausted all retries
    return None


