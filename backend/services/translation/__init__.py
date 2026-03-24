"""
Translation Service for ALwrity.

Provides text translation capabilities using multiple providers:
- DeepL (low-cost, high-quality text translation)
- WaveSpeed (high-quality video/audio dubbing)

This is a COMMON module that can be used across the entire application:
- Podcast Maker: Audio/video dubbing
- Content Creation: Translate blog posts, marketing copy
- AI Writer: Multilingual content generation
- Video Studio: Video translation and subtitles

Usage:
    # Simple usage
    from services.translation import translate_text, TranslationQuality
    result = translate_text("Hello world", target_language="Spanish")
    print(result.translated_text)

    # Advanced usage
    from services.translation import get_translator
    translator = get_translator(TranslationQuality.LOW)
    result = translator.translate(
        text="Your text here",
        target_language="fr",
        source_language="en"
    )

Environment Variables:
    DEEPL_API_KEY - DeepL API key for text translation (free tier: 500k chars/month)
    DEEPL_USE_PRO - Set to "true" for DeepL Pro account

Examples:
    # Translate a single text
    >>> from services.translation import translate_text
    >>> result = translate_text("Hello", target_language="es")
    >>> print(result.translated_text)
    Hola

    # Batch translation
    >>> from services.translation import translate_batch
    >>> results = translate_batch(
    ...     texts=["Hello", "Goodbye"],
    ...     target_language="fr"
    ... )

    # Check supported languages
    >>> from services.translation import list_supported_languages
    >>> langs = list_supported_languages()
    >>> print(f"Supports {len(langs)} languages")
"""

from .base_translation import BaseTranslationProvider, TranslationQuality, TranslationResult
from .deepl_translator import DeepLTranslator
from .translation_factory import (
    get_translator,
    list_supported_languages,
    translate_text,
    translate_batch,
    is_language_supported,
    clear_translator_cache,
)

__all__ = [
    # Enums and dataclasses
    "TranslationQuality",
    "TranslationResult",
    # Classes
    "BaseTranslationProvider",
    "DeepLTranslator",
    # Factory functions
    "get_translator",
    "list_supported_languages",
    "is_language_supported",
    "clear_translator_cache",
    # Convenience functions
    "translate_text",
    "translate_batch",
]
