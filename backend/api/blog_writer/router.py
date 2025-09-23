"""
AI Blog Writer API Router

Main router for blog writing operations including research, outline generation,
content creation, SEO analysis, and publishing.
"""

from fastapi import APIRouter, HTTPException
from typing import Any, Dict, List
from loguru import logger

from models.blog_models import (
    BlogResearchRequest,
    BlogResearchResponse,
    BlogOutlineRequest,
    BlogOutlineResponse,
    BlogOutlineRefineRequest,
    BlogSectionRequest,
    BlogSectionResponse,
    BlogOptimizeRequest,
    BlogOptimizeResponse,
    BlogSEOAnalyzeRequest,
    BlogSEOAnalyzeResponse,
    BlogSEOMetadataRequest,
    BlogSEOMetadataResponse,
    BlogPublishRequest,
    BlogPublishResponse,
    HallucinationCheckRequest,
    HallucinationCheckResponse,
)
from services.blog_writer.blog_service import BlogWriterService
from .task_manager import task_manager
from .cache_manager import cache_manager
from models.blog_models import MediumBlogGenerateRequest


router = APIRouter(prefix="/api/blog", tags=["AI Blog Writer"])

service = BlogWriterService()


@router.get("/health")
async def health() -> Dict[str, Any]:
    """Health check endpoint."""
    return {"status": "ok", "service": "ai_blog_writer"}


# Research Endpoints
@router.post("/research/start")
async def start_research(request: BlogResearchRequest) -> Dict[str, Any]:
    """Start a research operation and return a task ID for polling."""
    try:
        task_id = task_manager.start_research_task(request)
        return {"task_id": task_id, "status": "started"}
    except Exception as e:
        logger.error(f"Failed to start research: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/research/status/{task_id}")
async def get_research_status(task_id: str) -> Dict[str, Any]:
    """Get the status of a research operation."""
    try:
        status = task_manager.get_task_status(task_id)
        if status is None:
            raise HTTPException(status_code=404, detail="Task not found")
        
        logger.info(f"Research status request for {task_id}: {status['status']} with {len(status.get('progress_messages', []))} progress messages")
        return status
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get research status for {task_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Outline Endpoints
@router.post("/outline/start")
async def start_outline_generation(request: BlogOutlineRequest) -> Dict[str, Any]:
    """Start an outline generation operation and return a task ID for polling."""
    try:
        task_id = task_manager.start_outline_task(request)
        return {"task_id": task_id, "status": "started"}
    except Exception as e:
        logger.error(f"Failed to start outline generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/outline/status/{task_id}")
async def get_outline_status(task_id: str) -> Dict[str, Any]:
    """Get the status of an outline generation operation."""
    try:
        status = task_manager.get_task_status(task_id)
        if status is None:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return status
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get outline status for {task_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/outline/refine", response_model=BlogOutlineResponse)
async def refine_outline(request: BlogOutlineRefineRequest) -> BlogOutlineResponse:
    """Refine an existing outline with AI improvements."""
    try:
        return await service.refine_outline(request)
    except Exception as e:
        logger.error(f"Failed to refine outline: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/outline/enhance-section")
async def enhance_section(section_data: Dict[str, Any], focus: str = "general improvement"):
    """Enhance a specific section with AI improvements."""
    try:
        from models.blog_models import BlogOutlineSection
        section = BlogOutlineSection(**section_data)
        enhanced_section = await service.enhance_section_with_ai(section, focus)
        return enhanced_section.dict()
    except Exception as e:
        logger.error(f"Failed to enhance section: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/outline/optimize")
async def optimize_outline(outline_data: Dict[str, Any], focus: str = "general optimization"):
    """Optimize entire outline for better flow, SEO, and engagement."""
    try:
        from models.blog_models import BlogOutlineSection
        outline = [BlogOutlineSection(**section) for section in outline_data.get('outline', [])]
        optimized_outline = await service.optimize_outline_with_ai(outline, focus)
        return {"outline": [section.dict() for section in optimized_outline]}
    except Exception as e:
        logger.error(f"Failed to optimize outline: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/outline/rebalance")
async def rebalance_outline(outline_data: Dict[str, Any], target_words: int = 1500):
    """Rebalance word count distribution across outline sections."""
    try:
        from models.blog_models import BlogOutlineSection
        outline = [BlogOutlineSection(**section) for section in outline_data.get('outline', [])]
        rebalanced_outline = service.rebalance_word_counts(outline, target_words)
        return {"outline": [section.dict() for section in rebalanced_outline]}
    except Exception as e:
        logger.error(f"Failed to rebalance outline: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Content Generation Endpoints
@router.post("/section/generate", response_model=BlogSectionResponse)
async def generate_section(request: BlogSectionRequest) -> BlogSectionResponse:
    """Generate content for a specific section."""
    try:
        return await service.generate_section(request)
    except Exception as e:
        logger.error(f"Failed to generate section: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/section/{section_id}/continuity")
async def get_section_continuity(section_id: str) -> Dict[str, Any]:
    """Fetch last computed continuity metrics for a section (if available)."""
    try:
        # Access the in-memory continuity from the generator
        gen = service.content_generator
        # Find the last stored summary for the given section id
        # For now, expose the most recent metrics if the section was just generated
        # We keep a small in-memory snapshot on the generator object
        continuity: Dict[str, Any] = getattr(gen, "_last_continuity", {})
        metrics = continuity.get(section_id)
        return {"section_id": section_id, "continuity_metrics": metrics}
    except Exception as e:
        logger.error(f"Failed to get section continuity for {section_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/flow-analysis/basic")
async def analyze_flow_basic(request: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze flow metrics for entire blog using single AI call (cost-effective)."""
    try:
        result = await service.analyze_flow_basic(request)
        return result
    except Exception as e:
        logger.error(f"Failed to perform basic flow analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/flow-analysis/advanced")
async def analyze_flow_advanced(request: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze flow metrics for each section individually (detailed but expensive)."""
    try:
        result = await service.analyze_flow_advanced(request)
        return result
    except Exception as e:
        logger.error(f"Failed to perform advanced flow analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/section/optimize", response_model=BlogOptimizeResponse)
async def optimize_section(request: BlogOptimizeRequest) -> BlogOptimizeResponse:
    """Optimize a specific section for better quality and engagement."""
    try:
        return await service.optimize_section(request)
    except Exception as e:
        logger.error(f"Failed to optimize section: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Quality Assurance Endpoints
@router.post("/quality/hallucination-check", response_model=HallucinationCheckResponse)
async def hallucination_check(request: HallucinationCheckRequest) -> HallucinationCheckResponse:
    """Check content for potential hallucinations and factual inaccuracies."""
    try:
        return await service.hallucination_check(request)
    except Exception as e:
        logger.error(f"Failed to perform hallucination check: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# SEO Endpoints
@router.post("/seo/analyze", response_model=BlogSEOAnalyzeResponse)
async def seo_analyze(request: BlogSEOAnalyzeRequest) -> BlogSEOAnalyzeResponse:
    """Analyze content for SEO optimization opportunities."""
    try:
        return await service.seo_analyze(request)
    except Exception as e:
        logger.error(f"Failed to perform SEO analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/seo/metadata", response_model=BlogSEOMetadataResponse)
async def seo_metadata(request: BlogSEOMetadataRequest) -> BlogSEOMetadataResponse:
    """Generate SEO metadata for the blog post."""
    try:
        return await service.seo_metadata(request)
    except Exception as e:
        logger.error(f"Failed to generate SEO metadata: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Publishing Endpoints
@router.post("/publish", response_model=BlogPublishResponse)
async def publish(request: BlogPublishRequest) -> BlogPublishResponse:
    """Publish the blog post to the specified platform."""
    try:
        return await service.publish(request)
    except Exception as e:
        logger.error(f"Failed to publish blog: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Cache Management Endpoints
@router.get("/cache/stats")
async def get_cache_stats() -> Dict[str, Any]:
    """Get research cache statistics."""
    try:
        return cache_manager.get_research_cache_stats()
    except Exception as e:
        logger.error(f"Failed to get cache stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/cache/clear")
async def clear_cache() -> Dict[str, Any]:
    """Clear the research cache."""
    try:
        return cache_manager.clear_research_cache()
    except Exception as e:
        logger.error(f"Failed to clear cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cache/outline/stats")
async def get_outline_cache_stats():
    """Get outline cache statistics."""
    try:
        return cache_manager.get_outline_cache_stats()
    except Exception as e:
        logger.error(f"Failed to get outline cache stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/cache/outline/clear")
async def clear_outline_cache():
    """Clear all cached outline entries."""
    try:
        return cache_manager.clear_outline_cache()
    except Exception as e:
        logger.error(f"Failed to clear outline cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cache/outline/invalidate")
async def invalidate_outline_cache(request: Dict[str, List[str]]):
    """Invalidate outline cache entries for specific keywords."""
    try:
        return cache_manager.invalidate_outline_cache_for_keywords(request["keywords"])
    except Exception as e:
        logger.error(f"Failed to invalidate outline cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cache/outline/entries")
async def get_outline_cache_entries(limit: int = 20):
    """Get recent outline cache entries for debugging."""
    try:
        return cache_manager.get_recent_outline_cache_entries(limit)
    except Exception as e:
        logger.error(f"Failed to get outline cache entries: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------
# Medium Blog Generation API
# ---------------------------

@router.post("/generate/medium/start")
async def start_medium_generation(request: MediumBlogGenerateRequest):
    """Start medium-length blog generation (≤1000 words) and return a task id."""
    try:
        # Simple server-side guard
        if (request.globalTargetWords or 1000) > 1000:
            raise HTTPException(status_code=400, detail="Global target words exceed 1000; use per-section generation")

        task_id = task_manager.start_medium_generation_task(request)
        return {"task_id": task_id, "status": "started"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start medium generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/generate/medium/status/{task_id}")
async def medium_generation_status(task_id: str):
    """Poll status for medium blog generation task."""
    try:
        status = task_manager.get_task_status(task_id)
        if status is None:
            raise HTTPException(status_code=404, detail="Task not found")
        return status
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get medium generation status for {task_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rewrite/start")
async def start_blog_rewrite(request: Dict[str, Any]) -> Dict[str, Any]:
    """Start blog rewrite task with user feedback."""
    try:
        task_id = service.start_blog_rewrite(request)
        return {"task_id": task_id, "status": "started"}
    except Exception as e:
        logger.error(f"Failed to start blog rewrite: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/rewrite/status/{task_id}")
async def rewrite_status(task_id: str):
    """Poll status for blog rewrite task."""
    try:
        status = service.task_manager.get_task_status(task_id)
        if status is None:
            raise HTTPException(status_code=404, detail="Task not found")
        return status
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get rewrite status for {task_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))