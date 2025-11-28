"""
LinkedIn Content Generation Router

FastAPI router for LinkedIn content generation endpoints.
Provides comprehensive LinkedIn content creation functionality with
proper error handling, monitoring, and documentation.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Request
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
import time
from loguru import logger
from pathlib import Path

from models.linkedin_models import (
    LinkedInPostRequest, LinkedInArticleRequest, LinkedInCarouselRequest,
    LinkedInVideoScriptRequest, LinkedInCommentResponseRequest,
    LinkedInPostResponse, LinkedInArticleResponse, LinkedInCarouselResponse,
    LinkedInVideoScriptResponse, LinkedInCommentResponseResult
)
from services.linkedin_service import LinkedInService
from middleware.auth_middleware import get_current_user
from utils.text_asset_tracker import save_and_track_text_content

# Initialize the LinkedIn service instance
linkedin_service = LinkedInService()
from services.subscription.monitoring_middleware import DatabaseAPIMonitor
from services.database import get_db as get_db_dependency
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


# Use the proper database dependency from services.database
get_db = get_db_dependency


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
    db: Session = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
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
        
        # Extract user_id
        user_id = None
        if current_user:
            user_id = str(current_user.get('id', '') or current_user.get('sub', ''))
        if not user_id:
            user_id = http_request.headers.get("X-User-ID") or http_request.headers.get("Authorization")
        
        # Generate post content
        response = await linkedin_service.generate_linkedin_post(request)
        
        # Log successful request
        duration = time.time() - start_time
        background_tasks.add_task(
            log_api_request, http_request, db, duration, 200
        )
        
        if not response.success:
            raise HTTPException(status_code=500, detail=response.error)
        
        # Save and track text content (non-blocking)
        if user_id and response.data and response.data.content:
            try:
                # Combine all text content
                text_content = response.data.content
                if response.data.call_to_action:
                    text_content += f"\n\nCall to Action: {response.data.call_to_action}"
                if response.data.hashtags:
                    hashtag_text = " ".join([f"#{h.hashtag}" if isinstance(h, dict) else f"#{h.get('hashtag', '')}" for h in response.data.hashtags])
                    text_content += f"\n\nHashtags: {hashtag_text}"
                
                save_and_track_text_content(
                    db=db,
                    user_id=user_id,
                    content=text_content,
                    source_module="linkedin_writer",
                    title=f"LinkedIn Post: {request.topic[:80]}",
                    description=f"LinkedIn post for {request.industry} industry",
                    prompt=f"Topic: {request.topic}\nIndustry: {request.industry}\nTone: {request.tone}",
                    tags=["linkedin", "post", request.industry.lower().replace(' ', '_')],
                    asset_metadata={
                        "post_type": request.post_type.value if hasattr(request.post_type, 'value') else str(request.post_type),
                        "tone": request.tone.value if hasattr(request.tone, 'value') else str(request.tone),
                        "character_count": response.data.character_count,
                        "hashtag_count": len(response.data.hashtags),
                        "grounding_enabled": response.data.grounding_enabled if hasattr(response.data, 'grounding_enabled') else False
                    },
                    subdirectory="posts"
                )
            except Exception as track_error:
                logger.warning(f"Failed to track LinkedIn post asset: {track_error}")
        
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
    db: Session = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
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
        
        # Extract user_id
        user_id = None
        if current_user:
            user_id = str(current_user.get('id', '') or current_user.get('sub', ''))
        if not user_id:
            user_id = http_request.headers.get("X-User-ID") or http_request.headers.get("Authorization")
        
        # Generate article content
        response = await linkedin_service.generate_linkedin_article(request)
        
        # Log successful request
        duration = time.time() - start_time
        background_tasks.add_task(
            log_api_request, http_request, db, duration, 200
        )
        
        if not response.success:
            raise HTTPException(status_code=500, detail=response.error)
        
        # Save and track text content (non-blocking)
        if user_id and response.data:
            try:
                # Combine article content
                text_content = f"# {response.data.title}\n\n"
                text_content += response.data.content
                
                if response.data.sections:
                    text_content += "\n\n## Sections:\n"
                    for section in response.data.sections:
                        if isinstance(section, dict):
                            text_content += f"\n### {section.get('heading', 'Section')}\n{section.get('content', '')}\n"
                
                if response.data.seo_metadata:
                    text_content += f"\n\n## SEO Metadata\n{response.data.seo_metadata}\n"
                
                save_and_track_text_content(
                    db=db,
                    user_id=user_id,
                    content=text_content,
                    source_module="linkedin_writer",
                    title=f"LinkedIn Article: {response.data.title[:80] if response.data.title else request.topic[:80]}",
                    description=f"LinkedIn article for {request.industry} industry",
                    prompt=f"Topic: {request.topic}\nIndustry: {request.industry}\nTone: {request.tone}\nWord Count: {request.word_count}",
                    tags=["linkedin", "article", request.industry.lower().replace(' ', '_')],
                    asset_metadata={
                        "tone": request.tone.value if hasattr(request.tone, 'value') else str(request.tone),
                        "word_count": response.data.word_count,
                        "reading_time": response.data.reading_time,
                        "section_count": len(response.data.sections) if response.data.sections else 0,
                        "grounding_enabled": response.data.grounding_enabled if hasattr(response.data, 'grounding_enabled') else False
                    },
                    subdirectory="articles",
                    file_extension=".md"
                )
            except Exception as track_error:
                logger.warning(f"Failed to track LinkedIn article asset: {track_error}")
        
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
    db: Session = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
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
        
        # Extract user_id
        user_id = None
        if current_user:
            user_id = str(current_user.get('id', '') or current_user.get('sub', ''))
        if not user_id:
            user_id = http_request.headers.get("X-User-ID") or http_request.headers.get("Authorization")
        
        # Generate carousel content
        response = await linkedin_service.generate_linkedin_carousel(request)
        
        # Log successful request
        duration = time.time() - start_time
        background_tasks.add_task(
            log_api_request, http_request, db, duration, 200
        )
        
        if not response.success:
            raise HTTPException(status_code=500, detail=response.error)
        
        # Save and track text content (non-blocking)
        if user_id and response.data:
            try:
                # Combine carousel content
                text_content = f"# {response.data.title}\n\n"
                for slide in response.data.slides:
                    text_content += f"\n## Slide {slide.slide_number}: {slide.title}\n{slide.content}\n"
                    if slide.visual_elements:
                        text_content += f"\nVisual Elements: {', '.join(slide.visual_elements)}\n"
                
                save_and_track_text_content(
                    db=db,
                    user_id=user_id,
                    content=text_content,
                    source_module="linkedin_writer",
                    title=f"LinkedIn Carousel: {response.data.title[:80] if response.data.title else request.topic[:80]}",
                    description=f"LinkedIn carousel for {request.industry} industry",
                    prompt=f"Topic: {request.topic}\nIndustry: {request.industry}\nSlides: {getattr(request, 'number_of_slides', request.slide_count if hasattr(request, 'slide_count') else 5)}",
                    tags=["linkedin", "carousel", request.industry.lower().replace(' ', '_')],
                    asset_metadata={
                        "slide_count": len(response.data.slides),
                        "has_cover": response.data.cover_slide is not None,
                        "has_cta": response.data.cta_slide is not None
                    },
                    subdirectory="carousels",
                    file_extension=".md"
                )
            except Exception as track_error:
                logger.warning(f"Failed to track LinkedIn carousel asset: {track_error}")
        
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
    db: Session = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
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
        
        video_duration = getattr(request, 'video_duration', getattr(request, 'video_length', 60))
        if video_duration < 15 or video_duration > 300:
            raise HTTPException(status_code=422, detail="Video length must be between 15 and 300 seconds")
        
        # Extract user_id
        user_id = None
        if current_user:
            user_id = str(current_user.get('id', '') or current_user.get('sub', ''))
        if not user_id:
            user_id = http_request.headers.get("X-User-ID") or http_request.headers.get("Authorization")
        
        # Generate video script content
        response = await linkedin_service.generate_linkedin_video_script(request)
        
        # Log successful request
        duration = time.time() - start_time
        background_tasks.add_task(
            log_api_request, http_request, db, duration, 200
        )
        
        if not response.success:
            raise HTTPException(status_code=500, detail=response.error)
        
        # Save and track text content (non-blocking)
        if user_id and response.data:
            try:
                # Combine video script content
                text_content = f"# Video Script: {request.topic}\n\n"
                text_content += f"## Hook\n{response.data.hook}\n\n"
                text_content += "## Main Content\n"
                for scene in response.data.main_content:
                    if isinstance(scene, dict):
                        text_content += f"\n### Scene {scene.get('scene_number', '')}\n"
                        text_content += f"{scene.get('content', '')}\n"
                        if scene.get('duration'):
                            text_content += f"Duration: {scene.get('duration')}s\n"
                        if scene.get('visual_notes'):
                            text_content += f"Visual Notes: {scene.get('visual_notes')}\n"
                text_content += f"\n## Conclusion\n{response.data.conclusion}\n"
                if response.data.captions:
                    text_content += f"\n## Captions\n" + "\n".join(response.data.captions) + "\n"
                if response.data.thumbnail_suggestions:
                    text_content += f"\n## Thumbnail Suggestions\n" + "\n".join(response.data.thumbnail_suggestions) + "\n"
                
                save_and_track_text_content(
                    db=db,
                    user_id=user_id,
                    content=text_content,
                    source_module="linkedin_writer",
                    title=f"LinkedIn Video Script: {request.topic[:80]}",
                    description=f"LinkedIn video script for {request.industry} industry",
                    prompt=f"Topic: {request.topic}\nIndustry: {request.industry}\nDuration: {video_duration}s",
                    tags=["linkedin", "video_script", request.industry.lower().replace(' ', '_')],
                    asset_metadata={
                        "video_duration": video_duration,
                        "scene_count": len(response.data.main_content),
                        "has_captions": bool(response.data.captions)
                    },
                    subdirectory="video_scripts",
                    file_extension=".md"
                )
            except Exception as track_error:
                logger.warning(f"Failed to track LinkedIn video script asset: {track_error}")
        
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
    db: Session = Depends(get_db),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """Generate a LinkedIn comment response based on the provided parameters."""
    start_time = time.time()
    
    try:
        logger.info("Received LinkedIn comment response generation request")
        
        # Validate request
        original_comment = getattr(request, 'original_comment', getattr(request, 'comment', ''))
        post_context = getattr(request, 'post_context', getattr(request, 'original_post', ''))
        
        if not original_comment.strip():
            raise HTTPException(status_code=422, detail="Original comment cannot be empty")
        
        if not post_context.strip():
            raise HTTPException(status_code=422, detail="Post context cannot be empty")
        
        # Extract user_id
        user_id = None
        if current_user:
            user_id = str(current_user.get('id', '') or current_user.get('sub', ''))
        if not user_id:
            user_id = http_request.headers.get("X-User-ID") or http_request.headers.get("Authorization")
        
        # Generate comment response
        response = await linkedin_service.generate_linkedin_comment_response(request)
        
        # Log successful request
        duration = time.time() - start_time
        background_tasks.add_task(
            log_api_request, http_request, db, duration, 200
        )
        
        if not response.success:
            raise HTTPException(status_code=500, detail=response.error)
        
        # Save and track text content (non-blocking)
        if user_id and hasattr(response, 'response') and response.response:
            try:
                text_content = f"# Comment Response\n\n"
                text_content += f"## Original Comment\n{original_comment}\n\n"
                text_content += f"## Post Context\n{post_context}\n\n"
                text_content += f"## Generated Response\n{response.response}\n"
                if hasattr(response, 'alternatives') and response.alternatives:
                    text_content += f"\n## Alternative Responses\n"
                    for i, alt in enumerate(response.alternatives, 1):
                        text_content += f"\n### Alternative {i}\n{alt}\n"
                
                save_and_track_text_content(
                    db=db,
                    user_id=user_id,
                    content=text_content,
                    source_module="linkedin_writer",
                    title=f"LinkedIn Comment Response: {original_comment[:60]}",
                    description=f"LinkedIn comment response for {request.industry} industry",
                    prompt=f"Original Comment: {original_comment}\nPost Context: {post_context}\nIndustry: {request.industry}",
                    tags=["linkedin", "comment_response", request.industry.lower().replace(' ', '_')],
                    asset_metadata={
                        "response_length": getattr(request, 'response_length', 'medium'),
                        "tone": request.tone.value if hasattr(request.tone, 'value') else str(request.tone),
                        "has_alternatives": hasattr(response, 'alternatives') and bool(response.alternatives)
                    },
                    subdirectory="comment_responses",
                    file_extension=".md"
                )
            except Exception as track_error:
                logger.warning(f"Failed to track LinkedIn comment response asset: {track_error}")
        
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