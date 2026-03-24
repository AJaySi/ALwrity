"""
Translation Factory.

Factory pattern for getting translation providers based on quality tier.
"""

from typing import Dict, Optional

from utils.logger_utils import get_service_logger
from .base_translation import (
    BaseTranslationProvider,
    TranslationQuality,
    TranslationResult,
)
from .deepl_translator import DeepLTranslator

logger = get_service_logger("translation.factory")

_TRANSLATOR_CACHE: Dict[str, BaseTranslationProvider] = {}


def get_translator(
    quality: TranslationQuality = TranslationQuality.LOW,
    force_new: bool = False,
    **kwargs,
) -> BaseTranslationProvider:
    """
    Get a translation provider instance based on quality tier.
    
    Args:
        quality: The quality tier (LOW or HIGH)
        force_new: Force creation of new instance instead of cached
        **kwargs: Additional arguments for the provider
        
    Returns:
        Translation provider instance
        
    Raises:
        ValueError: If quality tier is not supported
    """
    global _TRANSLATOR_CACHE
    
    cache_key = f"{quality.value}_{id(kwargs)}"
    
    if not force_new and cache_key in _TRANSLATOR_CACHE:
        return _TRANSLATOR_CACHE[cache_key]
    
    if quality == TranslationQuality.LOW:
        translator = DeepLTranslator(**kwargs)
        logger.info(f"Created DeepL translator (LOW quality)")
    elif quality == TranslationQuality.HIGH:
        from .wavespeed_translator import WaveSpeedTranslator
        translator = WaveSpeedTranslator(**kwargs)
        logger.info(f"Created WaveSpeed translator (HIGH quality)")
    else:
        raise ValueError(f"Unsupported translation quality: {quality}")
    
    _TRANSLATOR_CACHE[cache_key] = translator
    return translator


def translate_text(
    text: str,
    target_language: str,
    source_language: Optional[str] = None,
    quality: TranslationQuality = TranslationQuality.LOW,
) -> TranslationResult:
    """
    Convenience function to translate text.
    
    Args:
        text: Text to translate
        target_language: Target language code or name
        source_language: Source language (auto-detect if None)
        quality: Quality tier
        
    Returns:
        TranslationResult
    """
    translator = get_translator(quality)
    return translator.translate(text, target_language, source_language)


def translate_batch(
    texts: list[str],
    target_language: str,
    source_language: Optional[str] = None,
    quality: TranslationQuality = TranslationQuality.LOW,
) -> list[TranslationResult]:
    """
    Convenience function to translate multiple texts.
    
    Args:
        texts: List of texts to translate
        target_language: Target language code or name
        source_language: Source language (auto-detect if None)
        quality: Quality tier
        
    Returns:
        List of TranslationResults
    """
    translator = get_translator(quality)
    return translator.translate_batch(texts, target_language, source_language)


def list_supported_languages(
    quality: Optional[TranslationQuality] = None,
) -> Dict[str, str]:
    """
    List supported languages.
    
    Args:
        quality: Optional quality filter. Returns all if None.
        
    Returns:
        Dictionary of language codes to names
    """
    if quality == TranslationQuality.LOW:
        return DeepLTranslator().get_supported_languages()
    elif quality == TranslationQuality.HIGH:
        from .wavespeed_translator import WaveSpeedTranslator
        return WaveSpeedTranslator().get_supported_languages()
    else:
        base_langs = DeepLTranslator.SUPPORTED_LANGUAGES
        try:
            from .wavespeed_translator import WaveSpeedTranslator
            wavespeed_langs = WaveSpeedTranslator.SUPPORTED_LANGUAGES
            all_langs = {**base_langs, **wavespeed_langs}
            return all_langs
        except (ImportError, Exception):
            return base_langs


def is_language_supported(
    language: str,
    quality: Optional[TranslationQuality] = None,
) -> bool:
    """
    Check if a language is supported.
    
    Args:
        language: Language code or name
        quality: Optional quality filter
        
    Returns:
        True if supported
    """
    if quality == TranslationQuality.LOW:
        return DeepLTranslator().is_language_supported(language)
    elif quality == TranslationQuality.HIGH:
        from .wavespeed_translator import WaveSpeedTranslator
        return WaveSpeedTranslator().is_language_supported(language)
    else:
        return (
            DeepLTranslator().is_language_supported(language) or
            _check_wavespeed_support(language)
        )


def _check_wavespeed_support(language: str) -> bool:
    try:
        from .wavespeed_translator import WaveSpeedTranslator
        return WaveSpeedTranslator().is_language_supported(language)
    except (ImportError, Exception):
        return False


def clear_translator_cache() -> None:
    """Clear the translator cache."""
    global _TRANSLATOR_CACHE
    _TRANSLATOR_CACHE.clear()
    logger.info("Translation provider cache cleared")
