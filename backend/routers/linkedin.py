"""
LinkedIn Content Generation Router

FastAPI router for LinkedIn content generation endpoints.
Provides comprehensive LinkedIn content creation functionality with
proper error handling, monitoring, and documentation.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Request
from fastapi.responses import JSONResponse
from typing import Dict, Any
import time
from loguru import logger

from models.linkedin_models import (
    LinkedInPostRequest, LinkedInArticleRequest, LinkedInCarouselRequest,
    LinkedInVideoScriptRequest, LinkedInCommentResponseRequest,
    LinkedInPostResponse, LinkedInArticleResponse, LinkedInCarouselResponse,
    LinkedInVideoScriptResponse, LinkedInCommentResponseResult
)
from services.linkedin_service import LinkedInService

# Initialize the LinkedIn service instance
linkedin_service = LinkedInService()
from services.subscription.monitoring_middleware import DatabaseAPIMonitor
from services.database import get_db_session
from sqlalchemy.orm import Session

# Initialize router
router = APIRouter(
    prefix="/api/linkedin",
    tags=["LinkedIn Content Generation"],
    responses={
        404: {"description": "Not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    }
)

# Initialize monitoring
monitor = DatabaseAPIMonitor()


def get_db():
    """Dependency to get database session."""
    db = get_db_session()
    try:
        yield db
    finally:
        if db:
            db.close()


async def log_api_request(request: Request, db: Session, duration: float, status_code: int):
    """Log API request to database for monitoring."""
    try:
        await monitor.add_request(
            db=db,
            path=str(request.url.path),
            method=request.method,
            status_code=status_code,
            duration=duration,
            user_id=request.headers.get("X-User-ID"),
            request_size=len(await request.body()) if request.method == "POST" else 0,
            user_agent=request.headers.get("User-Agent"),
            ip_address=request.client.host if request.client else None
        )
        db.commit()
    except Exception as e:
        logger.error(f"Failed to log API request: {str(e)}")


@router.get("/health", summary="Health Check", description="Check LinkedIn service health")
async def health_check():
    """Health check endpoint for LinkedIn service."""
    return {
        "status": "healthy",
        "service": "linkedin_content_generation",
        "version": "1.0.0",
        "timestamp": time.time()
    }


@router.post(
    "/generate-post",
    response_model=LinkedInPostResponse,
    summary="Generate LinkedIn Post",
    description="""
    Generate a professional LinkedIn post with AI-powered content creation.
    
    Features:
    - Research-backed content using multiple search engines
    - Industry-specific optimization
    - Hashtag generation and optimization
    - Call-to-action suggestions
    - Engagement prediction
    - Multiple tone and style options
    
    The service conducts research on the specified topic and industry,
    then generates engaging content optimized for LinkedIn's algorithm.
    """
)
async def generate_post(
    request: LinkedInPostRequest,
    background_tasks: BackgroundTasks,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """Generate a LinkedIn post based on the provided parameters."""
    start_time = time.time()
    
    try:
        logger.info(f"Received LinkedIn post generation request for topic: {request.topic}")
        
        # Validate request
        if not request.topic.strip():
            raise HTTPException(status_code=422, detail="Topic cannot be empty")
        
        if not request.industry.strip():
            raise HTTPException(status_code=422, detail="Industry cannot be empty")
        
        # Generate post content
        response = await linkedin_service.generate_linkedin_post(request)
        
        # Log successful request
        duration = time.time() - start_time
        background_tasks.add_task(
            log_api_request, http_request, db, duration, 200
        )
        
        if not response.success:
            raise HTTPException(status_code=500, detail=response.error)
        
        logger.info(f"Successfully generated LinkedIn post in {duration:.2f} seconds")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Error generating LinkedIn post: {str(e)}")
        
        # Log failed request
        background_tasks.add_task(
            log_api_request, http_request, db, duration, 500
        )
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate LinkedIn post: {str(e)}"
        )


@router.post(
    "/generate-article",
    response_model=LinkedInArticleResponse,
    summary="Generate LinkedIn Article",
    description="""
    Generate a comprehensive LinkedIn article with AI-powered content creation.
    
    Features:
    - Long-form content generation
    - Research-backed insights and data
    - SEO optimization for LinkedIn
    - Section structuring and organization
    - Image placement suggestions
    - Reading time estimation
    - Multiple research sources integration
    
    Perfect for thought leadership and in-depth industry analysis.
    """
)
async def generate_article(
    request: LinkedInArticleRequest,
    background_tasks: BackgroundTasks,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """Generate a LinkedIn article based on the provided parameters."""
    start_time = time.time()
    
    try:
        logger.info(f"Received LinkedIn article generation request for topic: {request.topic}")
        
        # Validate request
        if not request.topic.strip():
            raise HTTPException(status_code=422, detail="Topic cannot be empty")
        
        if not request.industry.strip():
            raise HTTPException(status_code=422, detail="Industry cannot be empty")
        
        # Generate article content
        response = await linkedin_service.generate_linkedin_article(request)
        
        # Log successful request
        duration = time.time() - start_time
        background_tasks.add_task(
            log_api_request, http_request, db, duration, 200
        )
        
        if not response.success:
            raise HTTPException(status_code=500, detail=response.error)
        
        logger.info(f"Successfully generated LinkedIn article in {duration:.2f} seconds")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Error generating LinkedIn article: {str(e)}")
        
        # Log failed request
        background_tasks.add_task(
            log_api_request, http_request, db, duration, 500
        )
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate LinkedIn article: {str(e)}"
        )


@router.post(
    "/generate-carousel",
    response_model=LinkedInCarouselResponse,
    summary="Generate LinkedIn Carousel",
    description="""
    Generate a LinkedIn carousel post with multiple slides.
    
    Features:
    - Multi-slide content generation
    - Visual hierarchy optimization
    - Story arc development
    - Design guidelines and suggestions
    - Cover and CTA slide options
    - Professional slide structuring
    
    Ideal for step-by-step guides, tips, and visual storytelling.
    """
)
async def generate_carousel(
    request: LinkedInCarouselRequest,
    background_tasks: BackgroundTasks,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """Generate a LinkedIn carousel based on the provided parameters."""
    start_time = time.time()
    
    try:
        logger.info(f"Received LinkedIn carousel generation request for topic: {request.topic}")
        
        # Validate request
        if not request.topic.strip():
            raise HTTPException(status_code=422, detail="Topic cannot be empty")
        
        if not request.industry.strip():
            raise HTTPException(status_code=422, detail="Industry cannot be empty")
        
        if request.slide_count < 3 or request.slide_count > 15:
            raise HTTPException(status_code=422, detail="Slide count must be between 3 and 15")
        
        # Generate carousel content
        response = await linkedin_service.generate_linkedin_carousel(request)
        
        # Log successful request
        duration = time.time() - start_time
        background_tasks.add_task(
            log_api_request, http_request, db, duration, 200
        )
        
        if not response.success:
            raise HTTPException(status_code=500, detail=response.error)
        
        logger.info(f"Successfully generated LinkedIn carousel in {duration:.2f} seconds")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Error generating LinkedIn carousel: {str(e)}")
        
        # Log failed request
        background_tasks.add_task(
            log_api_request, http_request, db, duration, 500
        )
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate LinkedIn carousel: {str(e)}"
        )


@router.post(
    "/generate-video-script",
    response_model=LinkedInVideoScriptResponse,
    summary="Generate LinkedIn Video Script",
    description="""
    Generate a LinkedIn video script optimized for engagement.
    
    Features:
    - Attention-grabbing hooks
    - Structured storytelling
    - Visual cue suggestions
    - Caption generation
    - Thumbnail text recommendations
    - Timing and pacing guidance
    
    Perfect for creating professional video content for LinkedIn.
    """
)
async def generate_video_script(
    request: LinkedInVideoScriptRequest,
    background_tasks: BackgroundTasks,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """Generate a LinkedIn video script based on the provided parameters."""
    start_time = time.time()
    
    try:
        logger.info(f"Received LinkedIn video script generation request for topic: {request.topic}")
        
        # Validate request
        if not request.topic.strip():
            raise HTTPException(status_code=422, detail="Topic cannot be empty")
        
        if not request.industry.strip():
            raise HTTPException(status_code=422, detail="Industry cannot be empty")
        
        if request.video_length < 15 or request.video_length > 300:
            raise HTTPException(status_code=422, detail="Video length must be between 15 and 300 seconds")
        
        # Generate video script content
        response = await linkedin_service.generate_linkedin_video_script(request)
        
        # Log successful request
        duration = time.time() - start_time
        background_tasks.add_task(
            log_api_request, http_request, db, duration, 200
        )
        
        if not response.success:
            raise HTTPException(status_code=500, detail=response.error)
        
        logger.info(f"Successfully generated LinkedIn video script in {duration:.2f} seconds")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Error generating LinkedIn video script: {str(e)}")
        
        # Log failed request
        background_tasks.add_task(
            log_api_request, http_request, db, duration, 500
        )
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate LinkedIn video script: {str(e)}"
        )


@router.post(
    "/generate-comment-response",
    response_model=LinkedInCommentResponseResult,
    summary="Generate LinkedIn Comment Response",
    description="""
    Generate professional responses to LinkedIn comments.
    
    Features:
    - Context-aware responses
    - Multiple response type options
    - Tone optimization
    - Brand voice customization
    - Alternative response suggestions
    - Engagement goal targeting
    
    Helps maintain professional engagement and build relationships.
    """
)
async def generate_comment_response(
    request: LinkedInCommentResponseRequest,
    background_tasks: BackgroundTasks,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """Generate a LinkedIn comment response based on the provided parameters."""
    start_time = time.time()
    
    try:
        logger.info("Received LinkedIn comment response generation request")
        
        # Validate request
        if not request.original_post.strip():
            raise HTTPException(status_code=422, detail="Original post cannot be empty")
        
        if not request.comment.strip():
            raise HTTPException(status_code=422, detail="Comment cannot be empty")
        
        # Generate comment response
        response = await linkedin_service.generate_linkedin_comment_response(request)
        
        # Log successful request
        duration = time.time() - start_time
        background_tasks.add_task(
            log_api_request, http_request, db, duration, 200
        )
        
        if not response.success:
            raise HTTPException(status_code=500, detail=response.error)
        
        logger.info(f"Successfully generated LinkedIn comment response in {duration:.2f} seconds")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Error generating LinkedIn comment response: {str(e)}")
        
        # Log failed request
        background_tasks.add_task(
            log_api_request, http_request, db, duration, 500
        )
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate LinkedIn comment response: {str(e)}"
        )


@router.get(
    "/content-types",
    summary="Get Available Content Types",
    description="Get list of available LinkedIn content types and their descriptions"
)
async def get_content_types():
    """Get available LinkedIn content types."""
    return {
        "content_types": {
            "post": {
                "name": "LinkedIn Post",
                "description": "Short-form content for regular LinkedIn posts",
                "max_length": 3000,
                "features": ["hashtags", "call_to_action", "engagement_prediction"]
            },
            "article": {
                "name": "LinkedIn Article",
                "description": "Long-form content for LinkedIn articles",
                "max_length": 125000,
                "features": ["seo_optimization", "image_suggestions", "reading_time"]
            },
            "carousel": {
                "name": "LinkedIn Carousel",
                "description": "Multi-slide visual content",
                "slide_range": "3-15 slides",
                "features": ["visual_guidelines", "slide_design", "story_flow"]
            },
            "video_script": {
                "name": "LinkedIn Video Script",
                "description": "Script for LinkedIn video content",
                "length_range": "15-300 seconds",
                "features": ["hooks", "visual_cues", "captions", "thumbnails"]
            },
            "comment_response": {
                "name": "Comment Response",
                "description": "Professional responses to LinkedIn comments",
                "response_types": ["professional", "appreciative", "clarifying", "disagreement", "value_add"],
                "features": ["tone_matching", "brand_voice", "alternatives"]
            }
        }
    }


@router.get(
    "/usage-stats",
    summary="Get Usage Statistics",
    description="Get LinkedIn content generation usage statistics"
)
async def get_usage_stats(db: Session = Depends(get_db)):
    """Get usage statistics for LinkedIn content generation."""
    try:
        # This would query the database for actual usage stats
        # For now, returning mock data
        return {
            "total_requests": 1250,
            "content_types": {
                "posts": 650,
                "articles": 320,
                "carousels": 180,
                "video_scripts": 70,
                "comment_responses": 30
            },
            "success_rate": 0.96,
            "average_generation_time": 4.2,
            "top_industries": [
                "Technology",
                "Healthcare",
                "Finance",
                "Marketing",
                "Education"
            ]
        }
    except Exception as e:
        logger.error(f"Error retrieving usage stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve usage statistics"
        )