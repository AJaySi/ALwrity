"""Stability AI service for handling API interactions."""

import aiohttp
import asyncio
from typing import Dict, Any, Optional, Union, Tuple
import os
from loguru import logger
import json
import base64
from fastapi import HTTPException, UploadFile


class StabilityAIService:
    """Service class for interacting with Stability AI API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Stability AI service.
        
        Args:
            api_key: Stability AI API key. If not provided, will try to get from environment.
        """
        self.api_key = api_key or os.getenv("STABILITY_API_KEY")
        if not self.api_key:
            raise ValueError("Stability AI API key is required. Set STABILITY_API_KEY environment variable or pass api_key parameter.")
        
        self.base_url = "https://api.stability.ai"
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    def _get_headers(self, accept_type: str = "image/*") -> Dict[str, str]:
        """Get common headers for API requests.
        
        Args:
            accept_type: Accept header value
            
        Returns:
            Headers dictionary
        """
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": accept_type,
            "User-Agent": "ALwrity-Backend/1.0"
        }
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        accept_type: str = "image/*",
        timeout: int = 300
    ) -> Union[bytes, Dict[str, Any]]:
        """Make HTTP request to Stability AI API.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Form data
            files: File data
            accept_type: Accept header value
            timeout: Request timeout in seconds
            
        Returns:
            Response data (bytes for images/audio, dict for JSON)
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
            
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers(accept_type)
        
        # Remove content-type header to let aiohttp set it automatically for multipart
        if files:
            headers.pop("Content-Type", None)
        
        try:
            # Prepare multipart data
            form_data = aiohttp.FormData()
            
            # Add files
            if files:
                for key, file_data in files.items():
                    if isinstance(file_data, UploadFile):
                        content = await file_data.read()
                        form_data.add_field(key, content, filename=file_data.filename or "file", content_type=file_data.content_type)
                    elif isinstance(file_data, bytes):
                        form_data.add_field(key, file_data, filename="file")
                    else:
                        form_data.add_field(key, file_data)
            
            # Add form data
            if data:
                for key, value in data.items():
                    if value is not None:
                        form_data.add_field(key, str(value))
            
            timeout_config = aiohttp.ClientTimeout(total=timeout)
            
            async with self.session.request(
                method=method,
                url=url,
                headers=headers,
                data=form_data,
                timeout=timeout_config
            ) as response:
                
                # Handle different response types
                content_type = response.headers.get('Content-Type', '')
                
                if response.status == 200:
                    if 'application/json' in content_type:
                        return await response.json()
                    else:
                        return await response.read()
                elif response.status == 202:
                    # Async generation started
                    return await response.json()
                else:
                    # Error response
                    try:
                        error_data = await response.json()
                        logger.error(f"Stability AI API error: {error_data}")
                        raise HTTPException(
                            status_code=response.status,
                            detail=error_data
                        )
                    except:
                        error_text = await response.text()
                        logger.error(f"Stability AI API error: {error_text}")
                        raise HTTPException(
                            status_code=response.status,
                            detail={"error": error_text}
                        )
                        
        except asyncio.TimeoutError:
            logger.error(f"Timeout error for {endpoint}")
            raise HTTPException(status_code=504, detail="Request timeout")
        except Exception as e:
            logger.error(f"Request error for {endpoint}: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def _prepare_image_file(self, image: Union[UploadFile, bytes, str]) -> bytes:
        """Prepare image file for upload.
        
        Args:
            image: Image data in various formats
            
        Returns:
            Image bytes
        """
        if isinstance(image, UploadFile):
            return await image.read()
        elif isinstance(image, bytes):
            return image
        elif isinstance(image, str):
            # Assume base64 encoded
            return base64.b64decode(image)
        else:
            raise ValueError("Unsupported image format")
    
    async def _prepare_audio_file(self, audio: Union[UploadFile, bytes, str]) -> bytes:
        """Prepare audio file for upload.
        
        Args:
            audio: Audio data in various formats
            
        Returns:
            Audio bytes
        """
        if isinstance(audio, UploadFile):
            return await audio.read()
        elif isinstance(audio, bytes):
            return audio
        elif isinstance(audio, str):
            # Assume base64 encoded
            return base64.b64decode(audio)
        else:
            raise ValueError("Unsupported audio format")
    
    def _validate_image_requirements(self, width: int, height: int, min_pixels: int = 4096, max_pixels: int = 9437184):
        """Validate image dimension requirements.
        
        Args:
            width: Image width
            height: Image height
            min_pixels: Minimum pixel count
            max_pixels: Maximum pixel count
        """
        total_pixels = width * height
        if total_pixels < min_pixels:
            raise ValueError(f"Image must have at least {min_pixels} pixels")
        if total_pixels > max_pixels:
            raise ValueError(f"Image must have at most {max_pixels} pixels")
        if width < 64 or height < 64:
            raise ValueError("Image dimensions must be at least 64x64 pixels")
    
    def _validate_aspect_ratio(self, width: int, height: int, min_ratio: float = 0.4, max_ratio: float = 2.5):
        """Validate image aspect ratio.
        
        Args:
            width: Image width
            height: Image height
            min_ratio: Minimum aspect ratio (1:2.5)
            max_ratio: Maximum aspect ratio (2.5:1)
        """
        aspect_ratio = width / height
        if aspect_ratio < min_ratio or aspect_ratio > max_ratio:
            raise ValueError(f"Aspect ratio must be between {min_ratio}:1 and {max_ratio}:1")
    
    # ==================== GENERATE METHODS ====================
    
    async def generate_ultra(
        self, 
        prompt: str,
        image: Optional[Union[UploadFile, bytes]] = None,
        **kwargs
    ) -> Union[bytes, Dict[str, Any]]:
        """Generate image using Stable Image Ultra.
        
        Args:
            prompt: Text prompt for generation
            image: Optional input image for image-to-image
            **kwargs: Additional parameters
            
        Returns:
            Generated image bytes or JSON response
        """
        data = {"prompt": prompt}
        data.update({k: v for k, v in kwargs.items() if v is not None})
        
        files = {}
        if image:
            files["image"] = await self._prepare_image_file(image)
        
        return await self._make_request(
            method="POST",
            endpoint="/v2beta/stable-image/generate/ultra",
            data=data,
            files=files if files else None
        )
    
    async def generate_core(
        self, 
        prompt: str,
        **kwargs
    ) -> Union[bytes, Dict[str, Any]]:
        """Generate image using Stable Image Core.
        
        Args:
            prompt: Text prompt for generation
            **kwargs: Additional parameters
            
        Returns:
            Generated image bytes or JSON response
        """
        data = {"prompt": prompt}
        data.update({k: v for k, v in kwargs.items() if v is not None})
        
        return await self._make_request(
            method="POST",
            endpoint="/v2beta/stable-image/generate/core",
            data=data
        )
    
    async def generate_sd3(
        self, 
        prompt: str,
        image: Optional[Union[UploadFile, bytes]] = None,
        **kwargs
    ) -> Union[bytes, Dict[str, Any]]:
        """Generate image using Stable Diffusion 3.5.
        
        Args:
            prompt: Text prompt for generation
            image: Optional input image for image-to-image
            **kwargs: Additional parameters
            
        Returns:
            Generated image bytes or JSON response
        """
        data = {"prompt": prompt}
        data.update({k: v for k, v in kwargs.items() if v is not None})
        
        files = {}
        if image:
            files["image"] = await self._prepare_image_file(image)
        
        return await self._make_request(
            method="POST",
            endpoint="/v2beta/stable-image/generate/sd3",
            data=data,
            files=files if files else None
        )
    
    # ==================== EDIT METHODS ====================
    
    async def erase(
        self, 
        image: Union[UploadFile, bytes],
        mask: Optional[Union[UploadFile, bytes]] = None,
        **kwargs
    ) -> Union[bytes, Dict[str, Any]]:
        """Erase objects from image using mask.
        
        Args:
            image: Input image
            mask: Optional mask image
            **kwargs: Additional parameters
            
        Returns:
            Edited image bytes or JSON response
        """
        data = {}
        data.update({k: v for k, v in kwargs.items() if v is not None})
        
        files = {"image": await self._prepare_image_file(image)}
        if mask:
            files["mask"] = await self._prepare_image_file(mask)
        
        return await self._make_request(
            method="POST",
            endpoint="/v2beta/stable-image/edit/erase",
            data=data,
            files=files
        )
    
    async def inpaint(
        self, 
        image: Union[UploadFile, bytes],
        prompt: str,
        mask: Optional[Union[UploadFile, bytes]] = None,
        **kwargs
    ) -> Union[bytes, Dict[str, Any]]:
        """Inpaint image with new content.
        
        Args:
            image: Input image
            prompt: Text prompt for inpainting
            mask: Optional mask image
            **kwargs: Additional parameters
            
        Returns:
            Edited image bytes or JSON response
        """
        data = {"prompt": prompt}
        data.update({k: v for k, v in kwargs.items() if v is not None})
        
        files = {"image": await self._prepare_image_file(image)}
        if mask:
            files["mask"] = await self._prepare_image_file(mask)
        
        return await self._make_request(
            method="POST",
            endpoint="/v2beta/stable-image/edit/inpaint",
            data=data,
            files=files
        )
    
    async def outpaint(
        self, 
        image: Union[UploadFile, bytes],
        **kwargs
    ) -> Union[bytes, Dict[str, Any]]:
        """Outpaint image in specified directions.
        
        Args:
            image: Input image
            **kwargs: Additional parameters including left, right, up, down
            
        Returns:
            Edited image bytes or JSON response
        """
        data = {}
        data.update({k: v for k, v in kwargs.items() if v is not None})
        
        files = {"image": await self._prepare_image_file(image)}
        
        return await self._make_request(
            method="POST",
            endpoint="/v2beta/stable-image/edit/outpaint",
            data=data,
            files=files
        )
    
    async def search_and_replace(
        self, 
        image: Union[UploadFile, bytes],
        prompt: str,
        search_prompt: str,
        **kwargs
    ) -> Union[bytes, Dict[str, Any]]:
        """Replace objects in image using search prompt.
        
        Args:
            image: Input image
            prompt: Text prompt for replacement
            search_prompt: What to search for
            **kwargs: Additional parameters
            
        Returns:
            Edited image bytes or JSON response
        """
        data = {"prompt": prompt, "search_prompt": search_prompt}
        data.update({k: v for k, v in kwargs.items() if v is not None})
        
        files = {"image": await self._prepare_image_file(image)}
        
        return await self._make_request(
            method="POST",
            endpoint="/v2beta/stable-image/edit/search-and-replace",
            data=data,
            files=files
        )
    
    async def search_and_recolor(
        self, 
        image: Union[UploadFile, bytes],
        prompt: str,
        select_prompt: str,
        **kwargs
    ) -> Union[bytes, Dict[str, Any]]:
        """Recolor objects in image using select prompt.
        
        Args:
            image: Input image
            prompt: Text prompt for recoloring
            select_prompt: What to select for recoloring
            **kwargs: Additional parameters
            
        Returns:
            Edited image bytes or JSON response
        """
        data = {"prompt": prompt, "select_prompt": select_prompt}
        data.update({k: v for k, v in kwargs.items() if v is not None})
        
        files = {"image": await self._prepare_image_file(image)}
        
        return await self._make_request(
            method="POST",
            endpoint="/v2beta/stable-image/edit/search-and-recolor",
            data=data,
            files=files
        )
    
    async def remove_background(
        self, 
        image: Union[UploadFile, bytes],
        **kwargs
    ) -> Union[bytes, Dict[str, Any]]:
        """Remove background from image.
        
        Args:
            image: Input image
            **kwargs: Additional parameters
            
        Returns:
            Edited image bytes or JSON response
        """
        data = {}
        data.update({k: v for k, v in kwargs.items() if v is not None})
        
        files = {"image": await self._prepare_image_file(image)}
        
        return await self._make_request(
            method="POST",
            endpoint="/v2beta/stable-image/edit/remove-background",
            data=data,
            files=files
        )
    
    async def replace_background_and_relight(
        self, 
        subject_image: Union[UploadFile, bytes],
        background_reference: Optional[Union[UploadFile, bytes]] = None,
        light_reference: Optional[Union[UploadFile, bytes]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Replace background and relight image (async).
        
        Args:
            subject_image: Subject image
            background_reference: Optional background reference image
            light_reference: Optional light reference image
            **kwargs: Additional parameters
            
        Returns:
            Generation ID for async polling
        """
        data = {}
        data.update({k: v for k, v in kwargs.items() if v is not None})
        
        files = {"subject_image": await self._prepare_image_file(subject_image)}
        if background_reference:
            files["background_reference"] = await self._prepare_image_file(background_reference)
        if light_reference:
            files["light_reference"] = await self._prepare_image_file(light_reference)
        
        return await self._make_request(
            method="POST",
            endpoint="/v2beta/stable-image/edit/replace-background-and-relight",
            data=data,
            files=files,
            accept_type="application/json"
        )
    
    # ==================== UPSCALE METHODS ====================
    
    async def upscale_fast(
        self, 
        image: Union[UploadFile, bytes],
        **kwargs
    ) -> Union[bytes, Dict[str, Any]]:
        """Fast upscale image by 4x.
        
        Args:
            image: Input image
            **kwargs: Additional parameters
            
        Returns:
            Upscaled image bytes or JSON response
        """
        data = {}
        data.update({k: v for k, v in kwargs.items() if v is not None})
        
        files = {"image": await self._prepare_image_file(image)}
        
        return await self._make_request(
            method="POST",
            endpoint="/v2beta/stable-image/upscale/fast",
            data=data,
            files=files
        )
    
    async def upscale_conservative(
        self, 
        image: Union[UploadFile, bytes],
        prompt: str,
        **kwargs
    ) -> Union[bytes, Dict[str, Any]]:
        """Conservative upscale to 4K resolution.
        
        Args:
            image: Input image
            prompt: Text prompt for upscaling
            **kwargs: Additional parameters
            
        Returns:
            Upscaled image bytes or JSON response
        """
        data = {"prompt": prompt}
        data.update({k: v for k, v in kwargs.items() if v is not None})
        
        files = {"image": await self._prepare_image_file(image)}
        
        return await self._make_request(
            method="POST",
            endpoint="/v2beta/stable-image/upscale/conservative",
            data=data,
            files=files
        )
    
    async def upscale_creative(
        self, 
        image: Union[UploadFile, bytes],
        prompt: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Creative upscale to 4K resolution (async).
        
        Args:
            image: Input image
            prompt: Text prompt for upscaling
            **kwargs: Additional parameters
            
        Returns:
            Generation ID for async polling
        """
        data = {"prompt": prompt}
        data.update({k: v for k, v in kwargs.items() if v is not None})
        
        files = {"image": await self._prepare_image_file(image)}
        
        return await self._make_request(
            method="POST",
            endpoint="/v2beta/stable-image/upscale/creative",
            data=data,
            files=files,
            accept_type="application/json"
        )
    
    # ==================== CONTROL METHODS ====================
    
    async def control_sketch(
        self, 
        image: Union[UploadFile, bytes],
        prompt: str,
        **kwargs
    ) -> Union[bytes, Dict[str, Any]]:
        """Generate image from sketch with prompt.
        
        Args:
            image: Input sketch image
            prompt: Text prompt for generation
            **kwargs: Additional parameters
            
        Returns:
            Generated image bytes or JSON response
        """
        data = {"prompt": prompt}
        data.update({k: v for k, v in kwargs.items() if v is not None})
        
        files = {"image": await self._prepare_image_file(image)}
        
        return await self._make_request(
            method="POST",
            endpoint="/v2beta/stable-image/control/sketch",
            data=data,
            files=files
        )
    
    async def control_structure(
        self, 
        image: Union[UploadFile, bytes],
        prompt: str,
        **kwargs
    ) -> Union[bytes, Dict[str, Any]]:
        """Generate image maintaining structure of input.
        
        Args:
            image: Input structure image
            prompt: Text prompt for generation
            **kwargs: Additional parameters
            
        Returns:
            Generated image bytes or JSON response
        """
        data = {"prompt": prompt}
        data.update({k: v for k, v in kwargs.items() if v is not None})
        
        files = {"image": await self._prepare_image_file(image)}
        
        return await self._make_request(
            method="POST",
            endpoint="/v2beta/stable-image/control/structure",
            data=data,
            files=files
        )
    
    async def control_style(
        self, 
        image: Union[UploadFile, bytes],
        prompt: str,
        **kwargs
    ) -> Union[bytes, Dict[str, Any]]:
        """Generate image using style from input image.
        
        Args:
            image: Input style image
            prompt: Text prompt for generation
            **kwargs: Additional parameters
            
        Returns:
            Generated image bytes or JSON response
        """
        data = {"prompt": prompt}
        data.update({k: v for k, v in kwargs.items() if v is not None})
        
        files = {"image": await self._prepare_image_file(image)}
        
        return await self._make_request(
            method="POST",
            endpoint="/v2beta/stable-image/control/style",
            data=data,
            files=files
        )
    
    async def control_style_transfer(
        self, 
        init_image: Union[UploadFile, bytes],
        style_image: Union[UploadFile, bytes],
        **kwargs
    ) -> Union[bytes, Dict[str, Any]]:
        """Transfer style between images.
        
        Args:
            init_image: Initial image
            style_image: Style reference image
            **kwargs: Additional parameters
            
        Returns:
            Generated image bytes or JSON response
        """
        data = {}
        data.update({k: v for k, v in kwargs.items() if v is not None})
        
        files = {
            "init_image": await self._prepare_image_file(init_image),
            "style_image": await self._prepare_image_file(style_image)
        }
        
        return await self._make_request(
            method="POST",
            endpoint="/v2beta/stable-image/control/style-transfer",
            data=data,
            files=files
        )
    
    # ==================== 3D METHODS ====================
    
    async def generate_3d_fast(
        self, 
        image: Union[UploadFile, bytes],
        **kwargs
    ) -> bytes:
        """Generate 3D model using Stable Fast 3D.
        
        Args:
            image: Input image
            **kwargs: Additional parameters
            
        Returns:
            3D model binary data (GLB format)
        """
        data = {}
        data.update({k: v for k, v in kwargs.items() if v is not None})
        
        files = {"image": await self._prepare_image_file(image)}
        
        return await self._make_request(
            method="POST",
            endpoint="/v2beta/3d/stable-fast-3d",
            data=data,
            files=files,
            accept_type="model/gltf-binary"
        )
    
    async def generate_3d_point_aware(
        self, 
        image: Union[UploadFile, bytes],
        **kwargs
    ) -> bytes:
        """Generate 3D model using Stable Point Aware 3D.
        
        Args:
            image: Input image
            **kwargs: Additional parameters
            
        Returns:
            3D model binary data (GLB format)
        """
        data = {}
        data.update({k: v for k, v in kwargs.items() if v is not None})
        
        files = {"image": await self._prepare_image_file(image)}
        
        return await self._make_request(
            method="POST",
            endpoint="/v2beta/3d/stable-point-aware-3d",
            data=data,
            files=files,
            accept_type="model/gltf-binary"
        )
    
    # ==================== AUDIO METHODS ====================
    
    async def generate_audio_from_text(
        self, 
        prompt: str,
        **kwargs
    ) -> Union[bytes, Dict[str, Any]]:
        """Generate audio from text prompt.
        
        Args:
            prompt: Text prompt for audio generation
            **kwargs: Additional parameters
            
        Returns:
            Generated audio bytes or JSON response
        """
        data = {"prompt": prompt}
        data.update({k: v for k, v in kwargs.items() if v is not None})
        
        # Use empty files dict to trigger multipart form
        files = {"none": ""}
        
        return await self._make_request(
            method="POST",
            endpoint="/v2beta/audio/stable-audio-2/text-to-audio",
            data=data,
            files=files,
            accept_type="audio/*"
        )
    
    async def generate_audio_from_audio(
        self, 
        prompt: str,
        audio: Union[UploadFile, bytes],
        **kwargs
    ) -> Union[bytes, Dict[str, Any]]:
        """Generate audio from audio input.
        
        Args:
            prompt: Text prompt for audio generation
            audio: Input audio
            **kwargs: Additional parameters
            
        Returns:
            Generated audio bytes or JSON response
        """
        data = {"prompt": prompt}
        data.update({k: v for k, v in kwargs.items() if v is not None})
        
        files = {"audio": await self._prepare_audio_file(audio)}
        
        return await self._make_request(
            method="POST",
            endpoint="/v2beta/audio/stable-audio-2/audio-to-audio",
            data=data,
            files=files,
            accept_type="audio/*"
        )
    
    async def inpaint_audio(
        self, 
        prompt: str,
        audio: Union[UploadFile, bytes],
        **kwargs
    ) -> Union[bytes, Dict[str, Any]]:
        """Inpaint audio with new content.
        
        Args:
            prompt: Text prompt for audio inpainting
            audio: Input audio
            **kwargs: Additional parameters
            
        Returns:
            Generated audio bytes or JSON response
        """
        data = {"prompt": prompt}
        data.update({k: v for k, v in kwargs.items() if v is not None})
        
        files = {"audio": await self._prepare_audio_file(audio)}
        
        return await self._make_request(
            method="POST",
            endpoint="/v2beta/audio/stable-audio-2/inpaint",
            data=data,
            files=files,
            accept_type="audio/*"
        )
    
    # ==================== RESULTS METHODS ====================
    
    async def get_generation_result(
        self, 
        generation_id: str,
        accept_type: str = "*/*"
    ) -> Union[bytes, Dict[str, Any]]:
        """Get result of async generation.
        
        Args:
            generation_id: Generation ID from async operation
            accept_type: Accept header value
            
        Returns:
            Generation result (bytes or JSON)
        """
        return await self._make_request(
            method="GET",
            endpoint=f"/v2beta/results/{generation_id}",
            accept_type=accept_type
        )
    
    # ==================== V1 LEGACY METHODS ====================
    
    async def v1_text_to_image(
        self, 
        engine_id: str,
        text_prompts: List[Dict[str, Any]],
        **kwargs
    ) -> Dict[str, Any]:
        """V1 text-to-image generation.
        
        Args:
            engine_id: Engine ID
            text_prompts: Text prompts list
            **kwargs: Additional parameters
            
        Returns:
            Generation response with artifacts
        """
        data = {"text_prompts": text_prompts}
        data.update({k: v for k, v in kwargs.items() if v is not None})
        
        headers = self._get_headers("application/json")
        headers["Content-Type"] = "application/json"
        
        async with self.session.post(
            f"{self.base_url}/v1/generation/{engine_id}/text-to-image",
            headers=headers,
            json=data
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                error_data = await response.json()
                raise HTTPException(status_code=response.status, detail=error_data)
    
    async def v1_image_to_image(
        self, 
        engine_id: str,
        init_image: Union[UploadFile, bytes],
        text_prompts: List[Dict[str, Any]],
        **kwargs
    ) -> Dict[str, Any]:
        """V1 image-to-image generation.
        
        Args:
            engine_id: Engine ID
            init_image: Initial image
            text_prompts: Text prompts list
            **kwargs: Additional parameters
            
        Returns:
            Generation response with artifacts
        """
        data = {}
        data.update({k: v for k, v in kwargs.items() if v is not None})
        
        # Add text prompts to form data
        for i, prompt in enumerate(text_prompts):
            data[f"text_prompts[{i}][text]"] = prompt["text"]
            if "weight" in prompt:
                data[f"text_prompts[{i}][weight]"] = prompt["weight"]
        
        files = {"init_image": await self._prepare_image_file(init_image)}
        
        return await self._make_request(
            method="POST",
            endpoint=f"/v1/generation/{engine_id}/image-to-image",
            data=data,
            files=files,
            accept_type="application/json"
        )
    
    async def v1_masking(
        self, 
        engine_id: str,
        init_image: Union[UploadFile, bytes],
        mask_image: Optional[Union[UploadFile, bytes]],
        text_prompts: List[Dict[str, Any]],
        mask_source: str,
        **kwargs
    ) -> Dict[str, Any]:
        """V1 image masking generation.
        
        Args:
            engine_id: Engine ID
            init_image: Initial image
            mask_image: Optional mask image
            text_prompts: Text prompts list
            mask_source: Mask source type
            **kwargs: Additional parameters
            
        Returns:
            Generation response with artifacts
        """
        data = {"mask_source": mask_source}
        data.update({k: v for k, v in kwargs.items() if v is not None})
        
        # Add text prompts to form data
        for i, prompt in enumerate(text_prompts):
            data[f"text_prompts[{i}][text]"] = prompt["text"]
            if "weight" in prompt:
                data[f"text_prompts[{i}][weight]"] = prompt["weight"]
        
        files = {"init_image": await self._prepare_image_file(init_image)}
        if mask_image:
            files["mask_image"] = await self._prepare_image_file(mask_image)
        
        return await self._make_request(
            method="POST",
            endpoint=f"/v1/generation/{engine_id}/image-to-image/masking",
            data=data,
            files=files,
            accept_type="application/json"
        )
    
    # ==================== USER & ACCOUNT METHODS ====================
    
    async def get_account_details(self) -> Dict[str, Any]:
        """Get account details.
        
        Returns:
            Account information
        """
        headers = self._get_headers("application/json")
        
        async with self.session.get(
            f"{self.base_url}/v1/user/account",
            headers=headers
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                error_data = await response.json()
                raise HTTPException(status_code=response.status, detail=error_data)
    
    async def get_account_balance(self) -> Dict[str, Any]:
        """Get account balance.
        
        Returns:
            Account balance information
        """
        headers = self._get_headers("application/json")
        
        async with self.session.get(
            f"{self.base_url}/v1/user/balance",
            headers=headers
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                error_data = await response.json()
                raise HTTPException(status_code=response.status, detail=error_data)
    
    async def list_engines(self) -> Dict[str, Any]:
        """List available engines.
        
        Returns:
            List of available engines
        """
        headers = self._get_headers("application/json")
        
        async with self.session.get(
            f"{self.base_url}/v1/engines/list",
            headers=headers
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                error_data = await response.json()
                raise HTTPException(status_code=response.status, detail=error_data)


# Global service instance
stability_service = None


async def get_stability_service() -> StabilityAIService:
    """Get or create Stability AI service instance.
    
    Returns:
        Stability AI service instance
    """
    global stability_service
    if stability_service is None:
        stability_service = StabilityAIService()
    return stability_service