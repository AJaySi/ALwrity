"""
WaveSpeed Translation Provider.

High-quality video/text translation using WaveSpeed API.
This will be used for Phase 3 (High-Quality Dubbing).

API: Uses existing WaveSpeed video translation API.
"""

from typing import Dict, List, Optional

from utils.logger_utils import get_service_logger
from .base_translation import (
    BaseTranslationProvider,
    TranslationQuality,
    TranslationResult,
)

logger = get_service_logger("translation.wavespeed")

WAVESPEED_SUPPORTED_LANGUAGES: Dict[str, str] = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "ja": "Japanese",
    "ko": "Korean",
    "zh": "Chinese",
    "ar": "Arabic",
    "hi": "Hindi",
    "ru": "Russian",
    "nl": "Dutch",
    "pl": "Polish",
    "tr": "Turkish",
    "vi": "Vietnamese",
    "th": "Thai",
    "id": "Indonesian",
    "ms": "Malay",
    "fil": "Filipino",
    "he": "Hebrew",
    "cs": "Czech",
    "da": "Danish",
    "fi": "Finnish",
    "el": "Greek",
    "hu": "Hungarian",
    "nb": "Norwegian",
    "ro": "Romanian",
    "sk": "Slovak",
    "sv": "Swedish",
    "uk": "Ukrainian",
}


class WaveSpeedTranslator(BaseTranslationProvider):
    
    COST_PER_CHARACTER = 0.0001
    
    def __init__(self):
        super().__init__()
        logger.info("[WaveSpeedTranslator] Initialized (high-quality mode)")
    
    @property
    def provider_name(self) -> str:
        return "WaveSpeed"
    
    @property
    def quality(self) -> TranslationQuality:
        return TranslationQuality.HIGH
    
    def translate(
        self,
        text: str,
        target_language: str,
        source_language: Optional[str] = None,
    ) -> TranslationResult:
        self.validate_text(text)
        
        raise NotImplementedError(
            "WaveSpeed text translation not yet implemented. "
            "For high-quality translation, use the video translation API "
            "or fall back to DeepL for text translation."
        )
    
    def translate_batch(
        self,
        texts: List[str],
        target_language: str,
        source_language: Optional[str] = None,
    ) -> List[TranslationResult]:
        raise NotImplementedError(
            "WaveSpeed batch translation not yet implemented."
        )
    
    def get_supported_languages(self) -> Dict[str, str]:
        return WAVESPEED_SUPPORTED_LANGUAGES.copy()
    
    def is_language_supported(self, language: str) -> bool:
        normalized = self.normalize_language_code(language).lower()
        return normalized in WAVESPEED_SUPPORTED_LANGUAGES
    
    def calculate_cost(self, text_length: int, char_count: int = 0) -> float:
        chars = char_count or text_length
        return chars * self.COST_PER_CHARACTER
    
    def translate_video(
        self,
        video_path: str,
        target_language: str,
        source_language: Optional[str] = None,
    ) -> bytes:
        """
        Translate video using WaveSpeed video translation API.
        
        This is the primary use case for high-quality dubbing.
        
        Args:
            video_path: Path to video file
            target_language: Target language
            source_language: Source language (auto-detect if None)
            
        Returns:
            Translated video bytes
        """
        from ..wavespeed.generators.video.translation import VideoTranslation
        
        translator = VideoTranslation()
        target_lang = self.normalize_language_code(target_language)
        
        with open(video_path, "rb") as f:
            video_bytes = f.read()
        
        return translator.video_translate(
            video=video_bytes,
            output_language=target_lang,
            enable_sync_mode=True,
        )
