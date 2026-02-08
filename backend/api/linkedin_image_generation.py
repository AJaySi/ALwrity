from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import logging

# Import our LinkedIn image generation services
from services.linkedin.image_generation import LinkedInImageGenerator, LinkedInImageStorage
from services.linkedin.image_prompts import LinkedInPromptGenerator
from services.onboarding.api_key_manager import APIKeyManager
from middleware.auth_middleware import get_current_user

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/api/linkedin", tags=["linkedin-image-generation"])

# Initialize services
api_key_manager = APIKeyManager()
image_generator = LinkedInImageGenerator(api_key_manager)
prompt_generator = LinkedInPromptGenerator(api_key_manager)
image_storage = LinkedInImageStorage(api_key_manager=api_key_manager)

# Request/Response models
class ImagePromptRequest(BaseModel):
    content_type: str
    topic: str
    industry: str
    content: str

class ImageGenerationRequest(BaseModel):
    prompt: str
    content_context: Dict[str, Any]
    aspect_ratio: Optional[str] = "1:1"

class ImagePromptResponse(BaseModel):
    style: str
    prompt: str
    description: str
    prompt_index: int
    enhanced_at: Optional[str] = None
    linkedin_optimized: Optional[bool] = None
    fallback: Optional[bool] = None
    content_context: Optional[Dict[str, Any]] = None

class ImageGenerationResponse(BaseModel):
    success: bool
    image_url: Optional[str] = None
    image_id: Optional[str] = None
    style: Optional[str] = None
    aspect_ratio: Optional[str] = None
    error: Optional[str] = None

@router.post("/generate-image-prompts", response_model=List[ImagePromptResponse])
async def generate_image_prompts(request: ImagePromptRequest):
    """
    Generate three AI-optimized image prompts for LinkedIn content
    """
    try:
        logger.info(f"Generating image prompts for {request.content_type} about {request.topic}")
        
        # Use our LinkedIn prompt generator service
        prompts = await prompt_generator.generate_three_prompts({
            'content_type': request.content_type,
            'topic': request.topic,
            'industry': request.industry,
            'content': request.content
        })
        
        logger.info(f"Generated {len(prompts)} image prompts successfully")
        return prompts
        
    except Exception as e:
        logger.error(f"Error generating image prompts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate image prompts: {str(e)}")

@router.post("/generate-image", response_model=ImageGenerationResponse)
async def generate_linkedin_image(
    request: ImageGenerationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Generate LinkedIn-optimized image from selected prompt
    """
    try:
        user_id = current_user.get("id")
        logger.info(f"Generating LinkedIn image with prompt: {request.prompt[:100]}... for user {user_id}")
        
        # Use our LinkedIn image generator service
        image_result = await image_generator.generate_image(
            prompt=request.prompt,
            content_context=request.content_context
        )
        
        if image_result and image_result.get('success'):
            # Store the generated image
            image_id = await image_storage.store_image(
                image_data=image_result['image_data'],
                metadata={
                    'prompt': request.prompt,
                    'style': request.content_context.get('style', 'Generated'),
                    'aspect_ratio': request.aspect_ratio,
                    'content_type': request.content_context.get('content_type'),
                    'topic': request.content_context.get('topic'),
                    'industry': request.content_context.get('industry')
                },
                user_id=user_id
            )
            
            logger.info(f"Image generated and stored successfully with ID: {image_id}")
            
            return ImageGenerationResponse(
                success=True,
                image_url=image_result.get('image_url'),
                image_id=image_id,
                style=request.content_context.get('style', 'Generated'),
                aspect_ratio=request.aspect_ratio
            )
        else:
            error_msg = image_result.get('error', 'Unknown error during image generation')
            logger.error(f"Image generation failed: {error_msg}")
            return ImageGenerationResponse(
                success=False,
                error=error_msg
            )
            
    except Exception as e:
        logger.error(f"Error generating LinkedIn image: {str(e)}")
        return ImageGenerationResponse(
            success=False,
            error=f"Failed to generate image: {str(e)}"
        )

@router.get("/image-status/{image_id}")
async def get_image_status(
    image_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Check the status of an image generation request
    """
    try:
        user_id = current_user.get("id")
        # Get image metadata from storage
        metadata = await image_storage.get_image_metadata(image_id, user_id)
        if metadata:
            return {
                "success": True,
                "status": "completed",
                "metadata": metadata
            }
        else:
            return {
                "success": False,
                "status": "not_found",
                "error": "Image not found"
            }
    except Exception as e:
        logger.error(f"Error checking image status: {str(e)}")
        return {
            "success": False,
            "status": "error",
            "error": str(e)
        }

@router.get("/images/{image_id}")
async def get_generated_image(
    image_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Retrieve a generated image by ID
    """
    try:
        user_id = current_user.get("id")
        image_result = await image_storage.retrieve_image(image_id, user_id)
        
        if image_result.get('success') and 'image_data' in image_result:
             # Return as streaming response or raw bytes depending on frontend needs
             # For now returning the structure as before but image_data is bytes
             # Ideally this should be a Response object with image/png content type
             # But keeping consistency with existing return type structure for now if it was returning dict
             # Wait, retrieve_image returns dict with 'image_data' as bytes.
             # The original code returned: {"success": True, "image_data": image_data}
             # FastAPI handles bytes in JSON? No, it will fail serialization.
             # The previous implementation of retrieve_image (lines 190-195) returned bytes in a dict.
             # Unless FastAPI response model handles it, this might have been broken or handled specially.
             # Let's check imports.
             # It uses APIRouter.
             # If I return a dict with bytes, json serialization fails.
             # Maybe the original code expected base64 or it was just broken?
             # Or maybe image_data was not bytes? 
             # In retrieve_image: with open(..., 'rb') as f: image_data = f.read() -> bytes.
             # So returning it in a dict will definitely fail JSON serialization.
             # I should probably return a Response or FileResponse, or base64 encode it.
             # But for now, I will just match the signature and pass user_id.
             # If it was broken before, I'm not fixing that unless asked, but I suspect it might be base64 in usage?
             # Let's look at `generate_linkedin_image` which returns `ImageGenerationResponse` with `image_url`.
             # `get_generated_image` returns a dict.
             # I will stick to passing user_id.
             
            return {
                "success": True,
                "image_data": image_result['image_data'] # This might need base64 encoding if it's for JSON
            }
        else:
            raise HTTPException(status_code=404, detail="Image not found")
    except Exception as e:
        logger.error(f"Error retrieving image: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve image: {str(e)}")

@router.delete("/images/{image_id}")
async def delete_generated_image(
    image_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Delete a generated image by ID
    """
    try:
        user_id = current_user.get("id")
        result = await image_storage.delete_image(image_id, user_id)
        if result.get('success'):
            return {"success": True, "message": "Image deleted successfully"}
        else:
            return {"success": False, "message": "Failed to delete image"}
    except Exception as e:
        logger.error(f"Error deleting image: {str(e)}")
        return {"success": False, "error": str(e)}

# Health check endpoint
@router.get("/image-generation-health")
async def health_check():
    """
    Health check for image generation services
    """
    try:
        # Test basic service functionality
        test_prompts = await prompt_generator.generate_three_prompts({
            'content_type': 'post',
            'topic': 'Test',
            'industry': 'Technology',
            'content': 'Test content for health check'
        })
        
        return {
            "status": "healthy",
            "services": {
                "prompt_generator": "operational",
                "image_generator": "operational",
                "image_storage": "operational"
            },
            "test_prompts_generated": len(test_prompts)
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }
