"""FastAPI router for Stability AI endpoints."""

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from fastapi.responses import Response
from typing import Optional, List, Union
import base64
import io
from loguru import logger

from models.stability_models import (
    # Request models
    StableImageUltraRequest, StableImageCoreRequest, StableSD3Request,
    EraseRequest, InpaintRequest, OutpaintRequest, SearchAndReplaceRequest,
    SearchAndRecolorRequest, RemoveBackgroundRequest, ReplaceBackgroundAndRelightRequest,
    FastUpscaleRequest, ConservativeUpscaleRequest, CreativeUpscaleRequest,
    SketchControlRequest, StructureControlRequest, StyleControlRequest, StyleTransferRequest,
    StableFast3DRequest, StablePointAware3DRequest,
    TextToAudioRequest, AudioToAudioRequest, AudioInpaintRequest,
    V1TextToImageRequest, V1ImageToImageRequest, V1MaskingRequest,
    
    # Response models
    GenerationResponse, ImageGenerationResponse, AudioGenerationResponse,
    GenerationStatusResponse, AccountResponse, BalanceResponse, ListEnginesResponse,
    
    # Enums
    OutputFormat, AudioOutputFormat, AspectRatio, StylePreset, GenerationMode,
    SD3Model, AudioModel, TextureResolution, RemeshType, TargetType,
    LightSourceDirection, InpaintMode
)
from services.stability_service import get_stability_service, StabilityAIService

router = APIRouter(prefix="/api/stability", tags=["Stability AI"])


# ==================== GENERATE ENDPOINTS ====================

@router.post("/generate/ultra", summary="Stable Image Ultra Generation")
async def generate_ultra(
    prompt: str = Form(..., description="Text prompt for image generation"),
    image: Optional[UploadFile] = File(None, description="Optional input image for image-to-image"),
    negative_prompt: Optional[str] = Form(None, description="What you do not want to see"),
    aspect_ratio: Optional[str] = Form("1:1", description="Aspect ratio"),
    seed: Optional[int] = Form(0, description="Random seed"),
    output_format: Optional[str] = Form("png", description="Output format"),
    style_preset: Optional[str] = Form(None, description="Style preset"),
    strength: Optional[float] = Form(None, description="Image influence strength (required if image provided)"),
    stability_service: StabilityAIService = Depends(get_stability_service)
):
    """Generate high-quality images using Stable Image Ultra.
    
    Stable Image Ultra is the most advanced text-to-image model, producing the highest quality,
    photorealistic outputs perfect for professional print media and large format applications.
    """
    async with stability_service:
        result = await stability_service.generate_ultra(
            prompt=prompt,
            image=image,
            negative_prompt=negative_prompt,
            aspect_ratio=aspect_ratio,
            seed=seed,
            output_format=output_format,
            style_preset=style_preset,
            strength=strength
        )
        
        if isinstance(result, bytes):
            return Response(content=result, media_type=f"image/{output_format}")
        return result


@router.post("/generate/core", summary="Stable Image Core Generation")
async def generate_core(
    prompt: str = Form(..., description="Text prompt for image generation"),
    negative_prompt: Optional[str] = Form(None, description="What you do not want to see"),
    aspect_ratio: Optional[str] = Form("1:1", description="Aspect ratio"),
    seed: Optional[int] = Form(0, description="Random seed"),
    output_format: Optional[str] = Form("png", description="Output format"),
    style_preset: Optional[str] = Form(None, description="Style preset"),
    stability_service: StabilityAIService = Depends(get_stability_service)
):
    """Generate images using Stable Image Core.
    
    Optimized for fast and affordable image generation, great for rapidly iterating
    on concepts during ideation. Next generation model following Stable Diffusion XL.
    """
    async with stability_service:
        result = await stability_service.generate_core(
            prompt=prompt,
            negative_prompt=negative_prompt,
            aspect_ratio=aspect_ratio,
            seed=seed,
            output_format=output_format,
            style_preset=style_preset
        )
        
        if isinstance(result, bytes):
            return Response(content=result, media_type=f"image/{output_format}")
        return result


@router.post("/generate/sd3", summary="Stable Diffusion 3.5 Generation")
async def generate_sd3(
    prompt: str = Form(..., description="Text prompt for image generation"),
    mode: Optional[str] = Form("text-to-image", description="Generation mode"),
    image: Optional[UploadFile] = File(None, description="Input image for image-to-image mode"),
    strength: Optional[float] = Form(None, description="Image influence strength (image-to-image only)"),
    aspect_ratio: Optional[str] = Form("1:1", description="Aspect ratio (text-to-image only)"),
    model: Optional[str] = Form("sd3.5-large", description="SD3 model variant"),
    negative_prompt: Optional[str] = Form(None, description="What you do not want to see"),
    seed: Optional[int] = Form(0, description="Random seed"),
    output_format: Optional[str] = Form("png", description="Output format"),
    style_preset: Optional[str] = Form(None, description="Style preset"),
    cfg_scale: Optional[float] = Form(None, description="CFG scale"),
    stability_service: StabilityAIService = Depends(get_stability_service)
):
    """Generate images using Stable Diffusion 3.5 models.
    
    The different versions of our open models are available via API, letting you test
    and adjust speed and quality based on your use case.
    """
    async with stability_service:
        result = await stability_service.generate_sd3(
            prompt=prompt,
            mode=mode,
            image=image,
            strength=strength,
            aspect_ratio=aspect_ratio,
            model=model,
            negative_prompt=negative_prompt,
            seed=seed,
            output_format=output_format,
            style_preset=style_preset,
            cfg_scale=cfg_scale
        )
        
        if isinstance(result, bytes):
            return Response(content=result, media_type=f"image/{output_format}")
        return result


# ==================== EDIT ENDPOINTS ====================

@router.post("/edit/erase", summary="Erase Objects from Image")
async def erase_image(
    image: UploadFile = File(..., description="Image to edit"),
    mask: Optional[UploadFile] = File(None, description="Optional mask image"),
    grow_mask: Optional[float] = Form(5, description="Mask edge growth in pixels"),
    seed: Optional[int] = Form(0, description="Random seed"),
    output_format: Optional[str] = Form("png", description="Output format"),
    stability_service: StabilityAIService = Depends(get_stability_service)
):
    """Remove unwanted objects from images using masks.
    
    The Erase service removes unwanted objects, such as blemishes on portraits
    or items on desks, using image masks.
    """
    async with stability_service:
        result = await stability_service.erase(
            image=image,
            mask=mask,
            grow_mask=grow_mask,
            seed=seed,
            output_format=output_format
        )
        
        if isinstance(result, bytes):
            return Response(content=result, media_type=f"image/{output_format}")
        return result


@router.post("/edit/inpaint", summary="Inpaint Image with New Content")
async def inpaint_image(
    image: UploadFile = File(..., description="Image to edit"),
    prompt: str = Form(..., description="Text prompt for inpainting"),
    mask: Optional[UploadFile] = File(None, description="Optional mask image"),
    negative_prompt: Optional[str] = Form(None, description="What you do not want to see"),
    grow_mask: Optional[float] = Form(5, description="Mask edge growth in pixels"),
    seed: Optional[int] = Form(0, description="Random seed"),
    output_format: Optional[str] = Form("png", description="Output format"),
    style_preset: Optional[str] = Form(None, description="Style preset"),
    stability_service: StabilityAIService = Depends(get_stability_service)
):
    """Intelligently modify images by filling in or replacing specified areas.
    
    The Inpaint service modifies images by filling in or replacing specified areas
    with new content based on the content of a mask image.
    """
    async with stability_service:
        result = await stability_service.inpaint(
            image=image,
            prompt=prompt,
            mask=mask,
            negative_prompt=negative_prompt,
            grow_mask=grow_mask,
            seed=seed,
            output_format=output_format,
            style_preset=style_preset
        )
        
        if isinstance(result, bytes):
            return Response(content=result, media_type=f"image/{output_format}")
        return result


@router.post("/edit/outpaint", summary="Outpaint Image in Directions")
async def outpaint_image(
    image: UploadFile = File(..., description="Image to edit"),
    left: Optional[int] = Form(0, description="Pixels to outpaint left"),
    right: Optional[int] = Form(0, description="Pixels to outpaint right"),
    up: Optional[int] = Form(0, description="Pixels to outpaint up"),
    down: Optional[int] = Form(0, description="Pixels to outpaint down"),
    creativity: Optional[float] = Form(0.5, description="Creativity level"),
    prompt: Optional[str] = Form("", description="Text prompt for outpainting"),
    seed: Optional[int] = Form(0, description="Random seed"),
    output_format: Optional[str] = Form("png", description="Output format"),
    style_preset: Optional[str] = Form(None, description="Style preset"),
    stability_service: StabilityAIService = Depends(get_stability_service)
):
    """Insert additional content in an image to fill in the space in any direction.
    
    The outpaint service allows you to 'zoom-out' of an image by expanding it
    in any direction with AI-generated content.
    """
    # Validate at least one direction is specified
    if not any([left, right, up, down]):
        raise HTTPException(status_code=400, detail="At least one outpaint direction must be specified")
    
    async with stability_service:
        result = await stability_service.outpaint(
            image=image,
            left=left,
            right=right,
            up=up,
            down=down,
            creativity=creativity,
            prompt=prompt,
            seed=seed,
            output_format=output_format,
            style_preset=style_preset
        )
        
        if isinstance(result, bytes):
            return Response(content=result, media_type=f"image/{output_format}")
        return result


@router.post("/edit/search-and-replace", summary="Search and Replace Objects")
async def search_and_replace(
    image: UploadFile = File(..., description="Image to edit"),
    prompt: str = Form(..., description="Text prompt for replacement"),
    search_prompt: str = Form(..., description="What to search for"),
    negative_prompt: Optional[str] = Form(None, description="What you do not want to see"),
    grow_mask: Optional[float] = Form(3, description="Mask edge growth in pixels"),
    seed: Optional[int] = Form(0, description="Random seed"),
    output_format: Optional[str] = Form("png", description="Output format"),
    style_preset: Optional[str] = Form(None, description="Style preset"),
    stability_service: StabilityAIService = Depends(get_stability_service)
):
    """Replace specified objects with new content using prompts.
    
    Similar to inpaint, allows to replace specified areas with new content,
    but this time with the help of a prompt instead of a mask.
    """
    async with stability_service:
        result = await stability_service.search_and_replace(
            image=image,
            prompt=prompt,
            search_prompt=search_prompt,
            negative_prompt=negative_prompt,
            grow_mask=grow_mask,
            seed=seed,
            output_format=output_format,
            style_preset=style_preset
        )
        
        if isinstance(result, bytes):
            return Response(content=result, media_type=f"image/{output_format}")
        return result


@router.post("/edit/search-and-recolor", summary="Search and Recolor Objects")
async def search_and_recolor(
    image: UploadFile = File(..., description="Image to edit"),
    prompt: str = Form(..., description="Text prompt for recoloring"),
    select_prompt: str = Form(..., description="What to select for recoloring"),
    negative_prompt: Optional[str] = Form(None, description="What you do not want to see"),
    grow_mask: Optional[float] = Form(3, description="Mask edge growth in pixels"),
    seed: Optional[int] = Form(0, description="Random seed"),
    output_format: Optional[str] = Form("png", description="Output format"),
    style_preset: Optional[str] = Form(None, description="Style preset"),
    stability_service: StabilityAIService = Depends(get_stability_service)
):
    """Change the color of specific objects in an image using prompts.
    
    The Search and Recolor service provides the ability to change the color of a
    specific object in an image using a prompt.
    """
    async with stability_service:
        result = await stability_service.search_and_recolor(
            image=image,
            prompt=prompt,
            select_prompt=select_prompt,
            negative_prompt=negative_prompt,
            grow_mask=grow_mask,
            seed=seed,
            output_format=output_format,
            style_preset=style_preset
        )
        
        if isinstance(result, bytes):
            return Response(content=result, media_type=f"image/{output_format}")
        return result


@router.post("/edit/remove-background", summary="Remove Background from Image")
async def remove_background(
    image: UploadFile = File(..., description="Image to edit"),
    output_format: Optional[str] = Form("png", description="Output format"),
    stability_service: StabilityAIService = Depends(get_stability_service)
):
    """Accurately segment foreground and remove background.
    
    The Remove Background service accurately segments the foreground from an image
    and removes the background.
    """
    async with stability_service:
        result = await stability_service.remove_background(
            image=image,
            output_format=output_format
        )
        
        if isinstance(result, bytes):
            return Response(content=result, media_type=f"image/{output_format}")
        return result


@router.post("/edit/replace-background-and-relight", summary="Replace Background and Relight (Async)")
async def replace_background_and_relight(
    subject_image: UploadFile = File(..., description="Subject image"),
    background_reference: Optional[UploadFile] = File(None, description="Background reference image"),
    background_prompt: Optional[str] = Form(None, description="Background description"),
    light_reference: Optional[UploadFile] = File(None, description="Light reference image"),
    foreground_prompt: Optional[str] = Form(None, description="Subject description"),
    negative_prompt: Optional[str] = Form(None, description="What you do not want to see"),
    preserve_original_subject: Optional[float] = Form(0.6, description="Subject preservation"),
    original_background_depth: Optional[float] = Form(0.5, description="Background depth matching"),
    keep_original_background: Optional[bool] = Form(False, description="Keep original background"),
    light_source_direction: Optional[str] = Form(None, description="Light direction"),
    light_source_strength: Optional[float] = Form(0.3, description="Light strength"),
    seed: Optional[int] = Form(0, description="Random seed"),
    output_format: Optional[str] = Form("png", description="Output format"),
    stability_service: StabilityAIService = Depends(get_stability_service)
):
    """Replace background and relight image with AI-generated or uploaded images.
    
    This service lets users swap backgrounds with AI-generated or uploaded images
    while adjusting lighting to match the subject.
    """
    # Validate that either background_reference or background_prompt is provided
    if not background_reference and not background_prompt:
        raise HTTPException(
            status_code=400, 
            detail="Either background_reference or background_prompt must be provided"
        )
    
    async with stability_service:
        result = await stability_service.replace_background_and_relight(
            subject_image=subject_image,
            background_reference=background_reference,
            background_prompt=background_prompt,
            light_reference=light_reference,
            foreground_prompt=foreground_prompt,
            negative_prompt=negative_prompt,
            preserve_original_subject=preserve_original_subject,
            original_background_depth=original_background_depth,
            keep_original_background=keep_original_background,
            light_source_direction=light_source_direction,
            light_source_strength=light_source_strength,
            seed=seed,
            output_format=output_format
        )
        
        return result  # Always returns JSON for async operations


# ==================== UPSCALE ENDPOINTS ====================

@router.post("/upscale/fast", summary="Fast Upscale (4x)")
async def upscale_fast(
    image: UploadFile = File(..., description="Image to upscale"),
    output_format: Optional[str] = Form("png", description="Output format"),
    stability_service: StabilityAIService = Depends(get_stability_service)
):
    """Fast 4x upscaling using predictive and generative AI.
    
    This lightweight and fast service (processing in ~1 second) is ideal for
    enhancing the quality of compressed images.
    """
    async with stability_service:
        result = await stability_service.upscale_fast(
            image=image,
            output_format=output_format
        )
        
        if isinstance(result, bytes):
            return Response(content=result, media_type=f"image/{output_format}")
        return result


@router.post("/upscale/conservative", summary="Conservative Upscale to 4K")
async def upscale_conservative(
    image: UploadFile = File(..., description="Image to upscale"),
    prompt: str = Form(..., description="Text prompt for upscaling"),
    negative_prompt: Optional[str] = Form(None, description="What you do not want to see"),
    creativity: Optional[float] = Form(0.35, description="Creativity level"),
    seed: Optional[int] = Form(0, description="Random seed"),
    output_format: Optional[str] = Form("png", description="Output format"),
    stability_service: StabilityAIService = Depends(get_stability_service)
):
    """Conservative upscale to 4K resolution with minimal alterations.
    
    Can upscale images by 20 to 40 times up to a 4 megapixel output image
    with minimal alteration to the original image.
    """
    async with stability_service:
        result = await stability_service.upscale_conservative(
            image=image,
            prompt=prompt,
            negative_prompt=negative_prompt,
            creativity=creativity,
            seed=seed,
            output_format=output_format
        )
        
        if isinstance(result, bytes):
            return Response(content=result, media_type=f"image/{output_format}")
        return result


@router.post("/upscale/creative", summary="Creative Upscale to 4K (Async)")
async def upscale_creative(
    image: UploadFile = File(..., description="Image to upscale"),
    prompt: str = Form(..., description="Text prompt for upscaling"),
    negative_prompt: Optional[str] = Form(None, description="What you do not want to see"),
    creativity: Optional[float] = Form(0.3, description="Creativity level"),
    seed: Optional[int] = Form(0, description="Random seed"),
    output_format: Optional[str] = Form("png", description="Output format"),
    style_preset: Optional[str] = Form(None, description="Style preset"),
    stability_service: StabilityAIService = Depends(get_stability_service)
):
    """Creative upscale for highly degraded images with creative enhancements.
    
    Can upscale highly degraded images (lower than 1 megapixel) with a creative
    twist to provide high resolution results.
    """
    async with stability_service:
        result = await stability_service.upscale_creative(
            image=image,
            prompt=prompt,
            negative_prompt=negative_prompt,
            creativity=creativity,
            seed=seed,
            output_format=output_format,
            style_preset=style_preset
        )
        
        return result  # Always returns JSON for async operations


# ==================== CONTROL ENDPOINTS ====================

@router.post("/control/sketch", summary="Control Generation with Sketch")
async def control_sketch(
    image: UploadFile = File(..., description="Sketch or image with contour lines"),
    prompt: str = Form(..., description="Text prompt for generation"),
    control_strength: Optional[float] = Form(0.7, description="Control strength"),
    negative_prompt: Optional[str] = Form(None, description="What you do not want to see"),
    seed: Optional[int] = Form(0, description="Random seed"),
    output_format: Optional[str] = Form("png", description="Output format"),
    style_preset: Optional[str] = Form(None, description="Style preset"),
    stability_service: StabilityAIService = Depends(get_stability_service)
):
    """Upgrade sketches to refined outputs with precise control.
    
    This service offers an ideal solution for design projects that require
    brainstorming and frequent iterations.
    """
    async with stability_service:
        result = await stability_service.control_sketch(
            image=image,
            prompt=prompt,
            control_strength=control_strength,
            negative_prompt=negative_prompt,
            seed=seed,
            output_format=output_format,
            style_preset=style_preset
        )
        
        if isinstance(result, bytes):
            return Response(content=result, media_type=f"image/{output_format}")
        return result


@router.post("/control/structure", summary="Control Generation with Structure")
async def control_structure(
    image: UploadFile = File(..., description="Image whose structure to maintain"),
    prompt: str = Form(..., description="Text prompt for generation"),
    control_strength: Optional[float] = Form(0.7, description="Control strength"),
    negative_prompt: Optional[str] = Form(None, description="What you do not want to see"),
    seed: Optional[int] = Form(0, description="Random seed"),
    output_format: Optional[str] = Form("png", description="Output format"),
    style_preset: Optional[str] = Form(None, description="Style preset"),
    stability_service: StabilityAIService = Depends(get_stability_service)
):
    """Generate images by maintaining the structure of an input image.
    
    This service excels in generating images by maintaining the structure of an
    input image, making it especially valuable for advanced content creation scenarios.
    """
    async with stability_service:
        result = await stability_service.control_structure(
            image=image,
            prompt=prompt,
            control_strength=control_strength,
            negative_prompt=negative_prompt,
            seed=seed,
            output_format=output_format,
            style_preset=style_preset
        )
        
        if isinstance(result, bytes):
            return Response(content=result, media_type=f"image/{output_format}")
        return result


@router.post("/control/style", summary="Control Generation with Style")
async def control_style(
    image: UploadFile = File(..., description="Style reference image"),
    prompt: str = Form(..., description="Text prompt for generation"),
    negative_prompt: Optional[str] = Form(None, description="What you do not want to see"),
    aspect_ratio: Optional[str] = Form("1:1", description="Aspect ratio"),
    fidelity: Optional[float] = Form(0.5, description="Style fidelity"),
    seed: Optional[int] = Form(0, description="Random seed"),
    output_format: Optional[str] = Form("png", description="Output format"),
    style_preset: Optional[str] = Form(None, description="Style preset"),
    stability_service: StabilityAIService = Depends(get_stability_service)
):
    """Extract stylistic elements from an input image for generation.
    
    This service extracts stylistic elements from an input image and uses it to
    guide the creation of an output image based on the prompt.
    """
    async with stability_service:
        result = await stability_service.control_style(
            image=image,
            prompt=prompt,
            negative_prompt=negative_prompt,
            aspect_ratio=aspect_ratio,
            fidelity=fidelity,
            seed=seed,
            output_format=output_format,
            style_preset=style_preset
        )
        
        if isinstance(result, bytes):
            return Response(content=result, media_type=f"image/{output_format}")
        return result


@router.post("/control/style-transfer", summary="Transfer Style Between Images")
async def control_style_transfer(
    init_image: UploadFile = File(..., description="Initial image to restyle"),
    style_image: UploadFile = File(..., description="Style reference image"),
    prompt: Optional[str] = Form("", description="Text prompt for generation"),
    negative_prompt: Optional[str] = Form(None, description="What you do not want to see"),
    style_strength: Optional[float] = Form(1, description="Style strength"),
    composition_fidelity: Optional[float] = Form(0.9, description="Composition fidelity"),
    change_strength: Optional[float] = Form(0.9, description="Change strength"),
    seed: Optional[int] = Form(0, description="Random seed"),
    output_format: Optional[str] = Form("png", description="Output format"),
    stability_service: StabilityAIService = Depends(get_stability_service)
):
    """Apply visual characteristics from reference style images to target images.
    
    Style Transfer applies visual characteristics from reference style images to target
    images while preserving the original composition.
    """
    async with stability_service:
        result = await stability_service.control_style_transfer(
            init_image=init_image,
            style_image=style_image,
            prompt=prompt,
            negative_prompt=negative_prompt,
            style_strength=style_strength,
            composition_fidelity=composition_fidelity,
            change_strength=change_strength,
            seed=seed,
            output_format=output_format
        )
        
        if isinstance(result, bytes):
            return Response(content=result, media_type=f"image/{output_format}")
        return result


# ==================== 3D ENDPOINTS ====================

@router.post("/3d/stable-fast-3d", summary="Generate 3D Model (Fast)")
async def generate_3d_fast(
    image: UploadFile = File(..., description="Image to convert to 3D"),
    texture_resolution: Optional[str] = Form("1024", description="Texture resolution"),
    foreground_ratio: Optional[float] = Form(0.85, description="Foreground ratio"),
    remesh: Optional[str] = Form("none", description="Remesh algorithm"),
    vertex_count: Optional[int] = Form(-1, description="Target vertex count"),
    stability_service: StabilityAIService = Depends(get_stability_service)
):
    """Generate high-quality 3D assets from a single 2D input image.
    
    Stable Fast 3D generates high-quality 3D assets from a single 2D input image
    with fast processing times.
    """
    async with stability_service:
        result = await stability_service.generate_3d_fast(
            image=image,
            texture_resolution=texture_resolution,
            foreground_ratio=foreground_ratio,
            remesh=remesh,
            vertex_count=vertex_count
        )
        
        return Response(content=result, media_type="model/gltf-binary")


@router.post("/3d/stable-point-aware-3d", summary="Generate 3D Model (Point Aware)")
async def generate_3d_point_aware(
    image: UploadFile = File(..., description="Image to convert to 3D"),
    texture_resolution: Optional[str] = Form("1024", description="Texture resolution"),
    foreground_ratio: Optional[float] = Form(1.3, description="Foreground ratio"),
    remesh: Optional[str] = Form("none", description="Remesh algorithm"),
    target_type: Optional[str] = Form("none", description="Target type"),
    target_count: Optional[int] = Form(1000, description="Target count"),
    guidance_scale: Optional[float] = Form(3, description="Guidance scale"),
    seed: Optional[int] = Form(0, description="Random seed"),
    stability_service: StabilityAIService = Depends(get_stability_service)
):
    """Generate 3D model with improved backside prediction and editing capabilities.
    
    Stable Point Aware 3D (SPAR3D) can make real-time edits and create the complete
    structure of a 3D object from a single image in a few seconds.
    """
    async with stability_service:
        result = await stability_service.generate_3d_point_aware(
            image=image,
            texture_resolution=texture_resolution,
            foreground_ratio=foreground_ratio,
            remesh=remesh,
            target_type=target_type,
            target_count=target_count,
            guidance_scale=guidance_scale,
            seed=seed
        )
        
        return Response(content=result, media_type="model/gltf-binary")


# ==================== AUDIO ENDPOINTS ====================

@router.post("/audio/text-to-audio", summary="Generate Audio from Text")
async def generate_audio_from_text(
    prompt: str = Form(..., description="Text prompt for audio generation"),
    duration: Optional[float] = Form(190, description="Duration in seconds"),
    seed: Optional[int] = Form(0, description="Random seed"),
    steps: Optional[int] = Form(None, description="Sampling steps"),
    cfg_scale: Optional[float] = Form(None, description="CFG scale"),
    model: Optional[str] = Form("stable-audio-2", description="Audio model"),
    output_format: Optional[str] = Form("mp3", description="Output format"),
    stability_service: StabilityAIService = Depends(get_stability_service)
):
    """Generate high-quality music and sound effects from text descriptions.
    
    Stable Audio generates high-quality music and sound effects up to three minutes
    long at 44.1kHz stereo from text descriptions.
    """
    async with stability_service:
        result = await stability_service.generate_audio_from_text(
            prompt=prompt,
            duration=duration,
            seed=seed,
            steps=steps,
            cfg_scale=cfg_scale,
            model=model,
            output_format=output_format
        )
        
        if isinstance(result, bytes):
            return Response(content=result, media_type=f"audio/{output_format}")
        return result


@router.post("/audio/audio-to-audio", summary="Transform Audio with Text")
async def generate_audio_from_audio(
    prompt: str = Form(..., description="Text prompt for audio transformation"),
    audio: UploadFile = File(..., description="Input audio file"),
    duration: Optional[float] = Form(190, description="Duration in seconds"),
    seed: Optional[int] = Form(0, description="Random seed"),
    steps: Optional[int] = Form(None, description="Sampling steps"),
    cfg_scale: Optional[float] = Form(None, description="CFG scale"),
    model: Optional[str] = Form("stable-audio-2", description="Audio model"),
    output_format: Optional[str] = Form("mp3", description="Output format"),
    strength: Optional[float] = Form(1, description="Audio influence strength"),
    stability_service: StabilityAIService = Depends(get_stability_service)
):
    """Transform existing audio samples into new compositions using text instructions.
    
    Stable Audio transforms existing audio samples into new high-quality compositions
    up to three minutes long at 44.1kHz stereo using text instructions.
    """
    async with stability_service:
        result = await stability_service.generate_audio_from_audio(
            prompt=prompt,
            audio=audio,
            duration=duration,
            seed=seed,
            steps=steps,
            cfg_scale=cfg_scale,
            model=model,
            output_format=output_format,
            strength=strength
        )
        
        if isinstance(result, bytes):
            return Response(content=result, media_type=f"audio/{output_format}")
        return result


@router.post("/audio/inpaint", summary="Inpaint Audio Segments")
async def inpaint_audio(
    prompt: str = Form(..., description="Text prompt for audio inpainting"),
    audio: UploadFile = File(..., description="Input audio file"),
    duration: Optional[float] = Form(190, description="Duration in seconds"),
    seed: Optional[int] = Form(0, description="Random seed"),
    steps: Optional[int] = Form(8, description="Sampling steps"),
    output_format: Optional[str] = Form("mp3", description="Output format"),
    mask_start: Optional[float] = Form(30, description="Mask start time"),
    mask_end: Optional[float] = Form(190, description="Mask end time"),
    stability_service: StabilityAIService = Depends(get_stability_service)
):
    """Inpaint specific segments of audio with new content.
    
    Stable Audio 2.5 transforms existing audio samples into new high-quality
    compositions with selective inpainting of audio segments.
    """
    async with stability_service:
        result = await stability_service.inpaint_audio(
            prompt=prompt,
            audio=audio,
            duration=duration,
            seed=seed,
            steps=steps,
            output_format=output_format,
            mask_start=mask_start,
            mask_end=mask_end
        )
        
        if isinstance(result, bytes):
            return Response(content=result, media_type=f"audio/{output_format}")
        return result


# ==================== RESULTS ENDPOINTS ====================

@router.get("/results/{generation_id}", summary="Get Async Generation Result")
async def get_generation_result(
    generation_id: str,
    accept_type: Optional[str] = "image/*",
    stability_service: StabilityAIService = Depends(get_stability_service)
):
    """Fetch the result of an async generation by ID.
    
    Make sure to use the same API key to fetch the generation result that you used
    to create the generation, otherwise you will receive a 404 response.
    
    Results are stored for 24 hours after generation.
    """
    async with stability_service:
        result = await stability_service.get_generation_result(
            generation_id=generation_id,
            accept_type=accept_type
        )
        
        if isinstance(result, bytes):
            # Determine media type based on accept_type
            if "audio" in accept_type:
                return Response(content=result, media_type="audio/mpeg")
            elif "model" in accept_type:
                return Response(content=result, media_type="model/gltf-binary")
            else:
                return Response(content=result, media_type="image/png")
        return result


# ==================== V1 LEGACY ENDPOINTS ====================

@router.post("/v1/generation/{engine_id}/text-to-image", summary="V1 Text-to-Image")
async def v1_text_to_image(
    engine_id: str,
    request: V1TextToImageRequest,
    stability_service: StabilityAIService = Depends(get_stability_service)
):
    """Generate images using V1 text-to-image API.
    
    Legacy endpoint for SDXL 1.0 and other V1 engines.
    """
    async with stability_service:
        result = await stability_service.v1_text_to_image(
            engine_id=engine_id,
            text_prompts=[prompt.dict() for prompt in request.text_prompts],
            height=request.height,
            width=request.width,
            cfg_scale=request.cfg_scale,
            samples=request.samples,
            steps=request.steps,
            seed=request.seed
        )
        
        return result


@router.post("/v1/generation/{engine_id}/image-to-image", summary="V1 Image-to-Image")
async def v1_image_to_image(
    engine_id: str,
    init_image: UploadFile = File(..., description="Initial image"),
    text_prompts: str = Form(..., description="JSON string of text prompts"),
    image_strength: Optional[float] = Form(0.35, description="Image strength"),
    init_image_mode: Optional[str] = Form("IMAGE_STRENGTH", description="Init image mode"),
    cfg_scale: Optional[float] = Form(7, description="CFG scale"),
    samples: Optional[int] = Form(1, description="Number of samples"),
    steps: Optional[int] = Form(30, description="Diffusion steps"),
    seed: Optional[int] = Form(0, description="Random seed"),
    stability_service: StabilityAIService = Depends(get_stability_service)
):
    """Generate images using V1 image-to-image API.
    
    Legacy endpoint for SDXL 1.0 and other V1 engines.
    """
    import json
    try:
        text_prompts_list = json.loads(text_prompts)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in text_prompts")
    
    async with stability_service:
        result = await stability_service.v1_image_to_image(
            engine_id=engine_id,
            init_image=init_image,
            text_prompts=text_prompts_list,
            image_strength=image_strength,
            init_image_mode=init_image_mode,
            cfg_scale=cfg_scale,
            samples=samples,
            steps=steps,
            seed=seed
        )
        
        return result


@router.post("/v1/generation/{engine_id}/image-to-image/masking", summary="V1 Image Masking")
async def v1_masking(
    engine_id: str,
    init_image: UploadFile = File(..., description="Initial image"),
    mask_image: Optional[UploadFile] = File(None, description="Mask image"),
    text_prompts: str = Form(..., description="JSON string of text prompts"),
    mask_source: str = Form(..., description="Mask source type"),
    cfg_scale: Optional[float] = Form(7, description="CFG scale"),
    samples: Optional[int] = Form(1, description="Number of samples"),
    steps: Optional[int] = Form(30, description="Diffusion steps"),
    seed: Optional[int] = Form(0, description="Random seed"),
    stability_service: StabilityAIService = Depends(get_stability_service)
):
    """Generate images using V1 masking API.
    
    Legacy endpoint for SDXL 1.0 and other V1 engines with masking support.
    """
    import json
    try:
        text_prompts_list = json.loads(text_prompts)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in text_prompts")
    
    async with stability_service:
        result = await stability_service.v1_masking(
            engine_id=engine_id,
            init_image=init_image,
            mask_image=mask_image,
            text_prompts=text_prompts_list,
            mask_source=mask_source,
            cfg_scale=cfg_scale,
            samples=samples,
            steps=steps,
            seed=seed
        )
        
        return result


# ==================== USER & ACCOUNT ENDPOINTS ====================

@router.get("/user/account", summary="Get Account Details", response_model=AccountResponse)
async def get_account_details(
    stability_service: StabilityAIService = Depends(get_stability_service)
):
    """Get information about the account associated with the provided API key."""
    async with stability_service:
        return await stability_service.get_account_details()


@router.get("/user/balance", summary="Get Account Balance", response_model=BalanceResponse)
async def get_account_balance(
    stability_service: StabilityAIService = Depends(get_stability_service)
):
    """Get the credit balance of the account/organization associated with the API key."""
    async with stability_service:
        return await stability_service.get_account_balance()


@router.get("/engines/list", summary="List Available Engines")
async def list_engines(
    stability_service: StabilityAIService = Depends(get_stability_service)
):
    """List all engines available to your organization/user."""
    async with stability_service:
        return await stability_service.list_engines()


# ==================== UTILITY ENDPOINTS ====================

@router.get("/health", summary="Health Check")
async def health_check():
    """Health check endpoint for Stability AI service."""
    return {"status": "healthy", "service": "stability-ai"}


@router.get("/models/info", summary="Get Model Information")
async def get_models_info():
    """Get information about available Stability AI models and their capabilities."""
    return {
        "generate": {
            "ultra": {
                "description": "Photorealistic, Large-Scale Output",
                "features": ["Highest quality", "Professional print media", "Exceptional detail"],
                "credits": 8,
                "resolution": "1 megapixel"
            },
            "core": {
                "description": "Fast and Affordable",
                "features": ["Fast generation", "Affordable", "Rapid iteration"],
                "credits": 3,
                "resolution": "1.5 megapixel"
            },
            "sd3": {
                "description": "Stable Diffusion 3.5 Model Suite",
                "models": {
                    "sd3.5-large": {"credits": 6.5, "description": "8B parameters, superior quality"},
                    "sd3.5-large-turbo": {"credits": 4, "description": "Fast distilled version"},
                    "sd3.5-medium": {"credits": 3.5, "description": "2.5B parameters, balanced"},
                    "sd3.5-flash": {"credits": 2.5, "description": "Fastest distilled version"}
                }
            }
        },
        "edit": {
            "erase": {"credits": 5, "description": "Remove unwanted objects"},
            "inpaint": {"credits": 5, "description": "Fill/replace specified areas"},
            "outpaint": {"credits": 4, "description": "Expand image in any direction"},
            "search_and_replace": {"credits": 5, "description": "Replace objects via prompt"},
            "search_and_recolor": {"credits": 5, "description": "Recolor objects via prompt"},
            "remove_background": {"credits": 5, "description": "Remove background"},
            "replace_background_and_relight": {"credits": 8, "description": "Replace background and adjust lighting"}
        },
        "upscale": {
            "fast": {"credits": 2, "description": "4x upscaling in ~1 second"},
            "conservative": {"credits": 40, "description": "20-40x upscaling to 4K"},
            "creative": {"credits": 60, "description": "Creative upscaling for degraded images"}
        },
        "control": {
            "sketch": {"credits": 5, "description": "Generate from sketches"},
            "structure": {"credits": 5, "description": "Maintain image structure"},
            "style": {"credits": 5, "description": "Extract and apply style"},
            "style_transfer": {"credits": 8, "description": "Transfer style between images"}
        },
        "3d": {
            "stable_fast_3d": {"credits": 10, "description": "Fast 3D model generation"},
            "stable_point_aware_3d": {"credits": 4, "description": "Advanced 3D with editing"}
        },
        "audio": {
            "text_to_audio": {"credits": 20, "description": "Generate audio from text"},
            "audio_to_audio": {"credits": 20, "description": "Transform audio with text"},
            "inpaint": {"credits": 20, "description": "Inpaint audio segments"}
        }
    }


@router.get("/supported-formats", summary="Get Supported File Formats")
async def get_supported_formats():
    """Get information about supported file formats for different operations."""
    return {
        "image_input": ["jpeg", "png", "webp"],
        "image_output": ["jpeg", "png", "webp"],
        "audio_input": ["mp3", "wav"],
        "audio_output": ["mp3", "wav"],
        "3d_output": ["glb"],
        "aspect_ratios": ["21:9", "16:9", "3:2", "5:4", "1:1", "4:5", "2:3", "9:16", "9:21"],
        "style_presets": [
            "enhance", "anime", "photographic", "digital-art", "comic-book",
            "fantasy-art", "line-art", "analog-film", "neon-punk", "isometric",
            "low-poly", "origami", "modeling-compound", "cinematic", "3d-model",
            "pixel-art", "tile-texture"
        ]
    }


# ==================== BATCH OPERATIONS ====================

@router.post("/batch/generate", summary="Batch Image Generation")
async def batch_generate(
    requests: List[dict],
    stability_service: StabilityAIService = Depends(get_stability_service)
):
    """Process multiple generation requests in batch.
    
    This endpoint allows you to submit multiple generation requests at once
    for efficient processing.
    """
    results = []
    
    async with stability_service:
        for req in requests:
            try:
                operation = req.get("operation")
                params = req.get("parameters", {})
                
                if operation == "generate_ultra":
                    result = await stability_service.generate_ultra(**params)
                elif operation == "generate_core":
                    result = await stability_service.generate_core(**params)
                elif operation == "generate_sd3":
                    result = await stability_service.generate_sd3(**params)
                else:
                    result = {"error": f"Unsupported operation: {operation}"}
                
                results.append({
                    "request_id": req.get("id", len(results)),
                    "status": "success" if not isinstance(result, dict) or "error" not in result else "error",
                    "result": base64.b64encode(result).decode() if isinstance(result, bytes) else result
                })
                
            except Exception as e:
                results.append({
                    "request_id": req.get("id", len(results)),
                    "status": "error",
                    "error": str(e)
                })
    
    return {"results": results}


# ==================== WEBHOOK ENDPOINTS ====================

@router.post("/webhook/generation-complete", summary="Generation Completion Webhook")
async def generation_complete_webhook(
    payload: dict
):
    """Webhook endpoint for generation completion notifications.
    
    This endpoint can be used to receive notifications when async generations
    are completed.
    """
    # Log the webhook payload for debugging
    logger.info(f"Received generation completion webhook: {payload}")
    
    # Here you could implement custom logic for handling completed generations
    # such as notifying users, storing results, etc.
    
    return {"status": "received", "message": "Webhook processed successfully"}


# ==================== HELPER ENDPOINTS ====================

@router.post("/utils/image-info", summary="Get Image Information")
async def get_image_info(
    image: UploadFile = File(..., description="Image to analyze")
):
    """Get information about an uploaded image.
    
    Returns dimensions, format, and other metadata about the image.
    """
    from PIL import Image
    
    try:
        # Read image and get info
        content = await image.read()
        img = Image.open(io.BytesIO(content))
        
        return {
            "filename": image.filename,
            "format": img.format,
            "mode": img.mode,
            "size": img.size,
            "width": img.width,
            "height": img.height,
            "total_pixels": img.width * img.height,
            "aspect_ratio": round(img.width / img.height, 3),
            "file_size": len(content),
            "has_alpha": img.mode in ("RGBA", "LA") or "transparency" in img.info
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing image: {str(e)}")


@router.post("/utils/validate-prompt", summary="Validate Text Prompt")
async def validate_prompt(
    prompt: str = Form(..., description="Text prompt to validate")
):
    """Validate a text prompt for Stability AI services.
    
    Checks prompt length, content, and provides suggestions for improvement.
    """
    issues = []
    suggestions = []
    
    # Check prompt length
    if len(prompt) < 10:
        issues.append("Prompt is too short (minimum 10 characters recommended)")
        suggestions.append("Add more descriptive details to improve generation quality")
    elif len(prompt) > 10000:
        issues.append("Prompt exceeds maximum length of 10,000 characters")
    
    # Check for common issues
    if not prompt.strip():
        issues.append("Prompt cannot be empty")
    
    # Basic content analysis
    word_count = len(prompt.split())
    if word_count < 3:
        suggestions.append("Consider adding more descriptive words for better results")
    
    # Check for style keywords
    style_keywords = ["photorealistic", "digital art", "painting", "sketch", "3d render"]
    has_style = any(keyword in prompt.lower() for keyword in style_keywords)
    if not has_style:
        suggestions.append("Consider adding style descriptors (e.g., 'photorealistic', 'digital art')")
    
    return {
        "prompt": prompt,
        "length": len(prompt),
        "word_count": word_count,
        "is_valid": len(issues) == 0,
        "issues": issues,
        "suggestions": suggestions,
        "estimated_credits": {
            "ultra": 8,
            "core": 3,
            "sd3_large": 6.5,
            "sd3_medium": 3.5
        }
    }