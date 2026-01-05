"""
Main VideoGenerator class that composes all video operation modules.

This class maintains backward compatibility with the original monolithic VideoGenerator
by delegating to specialized modules for different video operations.
"""

from typing import Any, Dict, Optional, Callable

from .base import VideoBase
from .generation import VideoGeneration
from .enhancement import VideoEnhancement
from .extension import VideoExtension
from .face_swap import VideoFaceSwap
from .translation import VideoTranslation
from .background import VideoBackground
from .audio import VideoAudio


class VideoGenerator(VideoBase):
    """
    Video generation generator for WaveSpeed API.
    
    This class composes multiple specialized modules to provide all video operations
    while maintaining a single unified interface for backward compatibility.
    """
    
    def __init__(self, api_key: str, base_url: str, polling):
        """Initialize video generator.
        
        Args:
            api_key: WaveSpeed API key
            base_url: WaveSpeed API base URL
            polling: WaveSpeedPolling instance for async operations
        """
        super().__init__(api_key, base_url, polling)
        
        # Initialize specialized modules
        self._generation = VideoGeneration(api_key, base_url, polling)
        self._enhancement = VideoEnhancement(api_key, base_url, polling)
        self._extension = VideoExtension(api_key, base_url, polling)
        self._face_swap = VideoFaceSwap(api_key, base_url, polling)
        self._translation = VideoTranslation(api_key, base_url, polling)
        self._background = VideoBackground(api_key, base_url, polling)
        self._audio = VideoAudio(api_key, base_url, polling)
    
    # Generation methods (delegated to VideoGeneration)
    def submit_image_to_video(
        self,
        model_path: str,
        payload: Dict[str, Any],
        timeout: int = 30,
    ) -> str:
        """Submit an image-to-video generation request."""
        return self._generation.submit_image_to_video(model_path, payload, timeout)
    
    def submit_text_to_video(
        self,
        model_path: str,
        payload: Dict[str, Any],
        timeout: int = 60,
    ) -> str:
        """Submit a text-to-video generation request to WaveSpeed."""
        return self._generation.submit_text_to_video(model_path, payload, timeout)
    
    def generate_text_video(
        self,
        prompt: str,
        resolution: str = "720p",
        duration: int = 5,
        audio_base64: Optional[str] = None,
        negative_prompt: Optional[str] = None,
        seed: Optional[int] = None,
        enable_prompt_expansion: bool = True,
        enable_sync_mode: bool = False,
        timeout: int = 180,
    ) -> Dict[str, Any]:
        """Generate video from text prompt using WAN 2.5 text-to-video."""
        return self._generation.generate_text_video(
            prompt=prompt,
            resolution=resolution,
            duration=duration,
            audio_base64=audio_base64,
            negative_prompt=negative_prompt,
            seed=seed,
            enable_prompt_expansion=enable_prompt_expansion,
            enable_sync_mode=enable_sync_mode,
            timeout=timeout,
        )
    
    # Enhancement methods (delegated to VideoEnhancement)
    def upscale_video(
        self,
        video: str,
        target_resolution: str = "1080p",
        enable_sync_mode: bool = False,
        timeout: int = 300,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> bytes:
        """Upscale video using FlashVSR."""
        return self._enhancement.upscale_video(
            video=video,
            target_resolution=target_resolution,
            enable_sync_mode=enable_sync_mode,
            timeout=timeout,
            progress_callback=progress_callback,
        )
    
    # Extension methods (delegated to VideoExtension)
    def extend_video(
        self,
        video: str,
        prompt: str,
        model: str = "wan-2.5",
        audio: Optional[str] = None,
        negative_prompt: Optional[str] = None,
        resolution: str = "720p",
        duration: int = 5,
        enable_prompt_expansion: bool = False,
        generate_audio: bool = True,
        camera_fixed: bool = False,
        seed: Optional[int] = None,
        enable_sync_mode: bool = False,
        timeout: int = 300,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> bytes:
        """Extend video duration using WAN 2.5, WAN 2.2 Spicy, or Seedance 1.5 Pro video-extend."""
        return self._extension.extend_video(
            video=video,
            prompt=prompt,
            model=model,
            audio=audio,
            negative_prompt=negative_prompt,
            resolution=resolution,
            duration=duration,
            enable_prompt_expansion=enable_prompt_expansion,
            generate_audio=generate_audio,
            camera_fixed=camera_fixed,
            seed=seed,
            enable_sync_mode=enable_sync_mode,
            timeout=timeout,
            progress_callback=progress_callback,
        )
    
    # Face swap methods (delegated to VideoFaceSwap)
    def face_swap(
        self,
        image: str,
        video: str,
        prompt: Optional[str] = None,
        resolution: str = "480p",
        seed: Optional[int] = None,
        enable_sync_mode: bool = False,
        timeout: int = 300,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> bytes:
        """Perform face/character swap using MoCha (wavespeed-ai/wan-2.1/mocha)."""
        return self._face_swap.face_swap(
            image=image,
            video=video,
            prompt=prompt,
            resolution=resolution,
            seed=seed,
            enable_sync_mode=enable_sync_mode,
            timeout=timeout,
            progress_callback=progress_callback,
        )
    
    def video_face_swap(
        self,
        video: str,
        face_image: str,
        target_gender: str = "all",
        target_index: int = 0,
        enable_sync_mode: bool = False,
        timeout: int = 300,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> bytes:
        """Perform face swap using Video Face Swap (wavespeed-ai/video-face-swap)."""
        return self._face_swap.video_face_swap(
            video=video,
            face_image=face_image,
            target_gender=target_gender,
            target_index=target_index,
            enable_sync_mode=enable_sync_mode,
            timeout=timeout,
            progress_callback=progress_callback,
        )
    
    # Translation methods (delegated to VideoTranslation)
    def video_translate(
        self,
        video: str,
        output_language: str = "English",
        enable_sync_mode: bool = False,
        timeout: int = 600,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> bytes:
        """Translate video to target language using HeyGen Video Translate."""
        return self._translation.video_translate(
            video=video,
            output_language=output_language,
            enable_sync_mode=enable_sync_mode,
            timeout=timeout,
            progress_callback=progress_callback,
        )
    
    # Background methods (delegated to VideoBackground)
    def remove_background(
        self,
        video: str,
        background_image: Optional[str] = None,
        enable_sync_mode: bool = False,
        timeout: int = 300,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> bytes:
        """Remove or replace video background using Video Background Remover."""
        return self._background.remove_background(
            video=video,
            background_image=background_image,
            enable_sync_mode=enable_sync_mode,
            timeout=timeout,
            progress_callback=progress_callback,
        )
    
    # Audio methods (delegated to VideoAudio)
    def hunyuan_video_foley(
        self,
        video: str,
        prompt: Optional[str] = None,
        seed: int = -1,
        enable_sync_mode: bool = False,
        timeout: int = 300,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> bytes:
        """Generate realistic Foley and ambient audio from video using Hunyuan Video Foley."""
        return self._audio.hunyuan_video_foley(
            video=video,
            prompt=prompt,
            seed=seed,
            enable_sync_mode=enable_sync_mode,
            timeout=timeout,
            progress_callback=progress_callback,
        )
    
    def think_sound(
        self,
        video: str,
        prompt: Optional[str] = None,
        seed: int = -1,
        enable_sync_mode: bool = False,
        timeout: int = 300,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> bytes:
        """Generate realistic sound effects and audio tracks from video using Think Sound."""
        return self._audio.think_sound(
            video=video,
            prompt=prompt,
            seed=seed,
            enable_sync_mode=enable_sync_mode,
            timeout=timeout,
            progress_callback=progress_callback,
        )
