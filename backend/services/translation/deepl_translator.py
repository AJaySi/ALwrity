"""
DeepL Translation Provider.

Low-cost, high-quality text translation using DeepL API.
Free tier: 500,000 characters/month

API Documentation: https://www.deepl.com/docs-api
"""

import os
from typing import Dict, List, Optional

import httpx

from utils.logger_utils import get_service_logger
from .base_translation import (
    BaseTranslationProvider,
    TranslationQuality,
    TranslationResult,
)

logger = get_service_logger("translation.deepl")

DEEPL_API_URL = "https://api-free.deepl.com/v2/translate"
DEEPL_API_URL_PRO = "https://api.deepl.com/v2/translate"

DEEPL_LANGUAGE_MAPPING: Dict[str, str] = {
    "BG": "BG",
    "CS": "CS",
    "DA": "DA",
    "DE": "DE",
    "EL": "EL",
    "EN": "EN-US",
    "EN-GB": "EN-GB",
    "EN-US": "EN-US",
    "ES": "ES",
    "ET": "ET",
    "FI": "FI",
    "FR": "FR",
    "HU": "HU",
    "ID": "ID",
    "IT": "IT",
    "JA": "JA",
    "KO": "KO",
    "LT": "LT",
    "LV": "LV",
    "NB": "NB",
    "NL": "NL",
    "PL": "PL",
    "PT": "PT-PT",
    "PT-BR": "PT-BR",
    "PT-PT": "PT-PT",
    "RO": "RO",
    "RU": "RU",
    "SK": "SK",
    "SL": "SL",
    "SV": "SV",
    "TR": "TR",
    "UK": "UK",
    "ZH": "ZH",
    "ZH-HANS": "ZH-HANS",
    "ZH-HANT": "ZH-HANT",
}

DEEPL_SUPPORTED_LANGUAGES: Dict[str, str] = {
    "bg": "Bulgarian",
    "cs": "Czech",
    "da": "Danish",
    "de": "German",
    "el": "Greek",
    "en": "English (American)",
    "en-gb": "English (British)",
    "es": "Spanish",
    "et": "Estonian",
    "fi": "Finnish",
    "fr": "French",
    "hu": "Hungarian",
    "id": "Indonesian",
    "it": "Italian",
    "ja": "Japanese",
    "ko": "Korean",
    "lt": "Lithuanian",
    "lv": "Latvian",
    "nb": "Norwegian",
    "nl": "Dutch",
    "pl": "Polish",
    "pt": "Portuguese",
    "pt-br": "Portuguese (Brazilian)",
    "pt-pt": "Portuguese (European)",
    "ro": "Romanian",
    "ru": "Russian",
    "sk": "Slovak",
    "sl": "Slovenian",
    "sv": "Swedish",
    "tr": "Turkish",
    "uk": "Ukrainian",
    "zh": "Chinese",
    "zh-hans": "Chinese (Simplified)",
    "zh-hant": "Chinese (Traditional)",
}


class DeepLTranslator(BaseTranslationProvider):
    
    COST_PER_CHARACTER = 0.00001
    
    def __init__(self, api_key: Optional[str] = None, use_pro: bool = False):
        super().__init__()
        self._api_key = api_key or os.getenv("DEEPL_API_KEY", "")
        self._use_pro = use_pro or os.getenv("DEEPL_USE_PRO", "false").lower() == "true"
        
        if not self._api_key:
            logger.warning("DeepL API key not configured. Set DEEPL_API_KEY in environment.")
        
        self._api_url = DEEPL_API_URL_PRO if self._use_pro else DEEPL_API_URL
    
    @property
    def provider_name(self) -> str:
        return "DeepL"
    
    @property
    def quality(self) -> TranslationQuality:
        return TranslationQuality.LOW
    
    def _get_deepl_lang_code(self, language: str) -> str:
        normalized = self.normalize_language_code(language)
        upper = normalized.upper()
        
        if upper in DEEPL_LANGUAGE_MAPPING:
            return DEEPL_LANGUAGE_MAPPING[upper]
        
        for deepl_code, lang_name in DEEPL_SUPPORTED_LANGUAGES.items():
            if lang_name.lower() == normalized.lower() or deepl_code.lower() == normalized.lower():
                return deepl_code.upper() if deepl_code.upper() in DEEPL_LANGUAGE_MAPPING else deepl_code
        
        return upper
    
    def translate(
        self,
        text: str,
        target_language: str,
        source_language: Optional[str] = None,
    ) -> TranslationResult:
        self.validate_text(text)
        
        if not self._api_key:
            raise ValueError("DeepL API key not configured. Set DEEPL_API_KEY environment variable.")
        
        target_code = self._get_deepl_lang_code(target_language)
        source_code = self._get_deepl_lang_code(source_language) if source_language else None
        
        headers = {
            "Authorization": f"DeepL-Auth-Key {self._api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "text": [text],
            "target_lang": target_code,
        }
        
        if source_code:
            payload["source_lang"] = source_code
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(self._api_url, headers=headers, json=payload)
                response.raise_for_status()
                
                data = response.json()
                translations = data.get("translations", [])
                
                if not translations:
                    raise ValueError("No translation returned from DeepL API")
                
                primary = translations[0]
                alternatives = [
                    t["text"] for t in translations[1:] if t.get("text")
                ]
                
                detected_lang = primary.get("detected_source_language", "")
                
                return TranslationResult(
                    translated_text=primary["text"],
                    source_language=detected_lang if not source_language else source_language,
                    target_language=target_language,
                    provider=self.provider_name,
                    quality=self.quality,
                    confidence=0.95,
                    alternative_translations=alternatives,
                    metadata={
                        "deepl_target_lang": target_code,
                        "character_count": len(text),
                        "translations_count": len(translations),
                    },
                )
                
        except httpx.HTTPStatusError as e:
            logger.error(f"DeepL API HTTP error: {e.response.status_code} - {e.response.text}")
            raise RuntimeError(f"DeepL API error: {e.response.status_code}")
        except httpx.RequestError as e:
            logger.error(f"DeepL API request error: {str(e)}")
            raise RuntimeError(f"DeepL API request failed: {str(e)}")
    
    def translate_batch(
        self,
        texts: List[str],
        target_language: str,
        source_language: Optional[str] = None,
    ) -> List[TranslationResult]:
        if not texts:
            return []
        
        self.validate_text("\n".join(texts))
        
        if not self._api_key:
            raise ValueError("DeepL API key not configured. Set DEEPL_API_KEY environment variable.")
        
        target_code = self._get_deepl_lang_code(target_language)
        source_code = self._get_deepl_lang_code(source_language) if source_language else None
        
        headers = {
            "Authorization": f"DeepL-Auth-Key {self._api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "text": texts,
            "target_lang": target_code,
        }
        
        if source_code:
            payload["source_lang"] = source_code
        
        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(self._api_url, headers=headers, json=payload)
                response.raise_for_status()
                
                data = response.json()
                translations = data.get("translations", [])
                
                results = []
                detected_source = None
                
                for i, translation in enumerate(translations):
                    if i == 0:
                        detected_source = translation.get("detected_source_language", "")
                    
                    results.append(TranslationResult(
                        translated_text=translation["text"],
                        source_language=detected_source or source_language or "auto",
                        target_language=target_language,
                        provider=self.provider_name,
                        quality=self.quality,
                        confidence=0.95,
                        metadata={
                            "deepl_target_lang": target_code,
                            "batch_size": len(texts),
                        },
                    ))
                
                return results
                
        except httpx.HTTPStatusError as e:
            logger.error(f"DeepL API HTTP error: {e.response.status_code}")
            raise RuntimeError(f"DeepL API error: {e.response.status_code}")
        except httpx.RequestError as e:
            logger.error(f"DeepL API request error: {str(e)}")
            raise RuntimeError(f"DeepL API request failed: {str(e)}")
    
    def get_supported_languages(self) -> Dict[str, str]:
        return DEEPL_SUPPORTED_LANGUAGES.copy()
    
    def is_language_supported(self, language: str) -> bool:
        normalized = self.normalize_language_code(language).lower()
        return normalized in DEEPL_SUPPORTED_LANGUAGES
    
    def calculate_cost(self, text_length: int, char_count: int = 0) -> float:
        chars = char_count or text_length
        return chars * self.COST_PER_CHARACTER
    
    def get_usage_info(self) -> Dict[str, any]:
        if not self._api_key:
            return {"configured": False, "message": "API key not set"}
        
        usage_url = "https://api-free.deepl.com/v2/usage" if not self._use_pro else "https://api.deepl.com/v2/usage"
        
        headers = {
            "Authorization": f"DeepL-Auth-Key {self._api_key}",
        }
        
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(usage_url, headers=headers)
                response.raise_for_status()
                
                data = response.json()
                return {
                    "configured": True,
                    "character_count": data.get("character_count", 0),
                    "character_limit": data.get("character_limit", 0),
                    "usage_percent": (data.get("character_count", 0) / data.get("character_limit", 1)) * 100,
                }
        except Exception as e:
            logger.error(f"Failed to get DeepL usage info: {str(e)}")
            return {"configured": True, "error": str(e)}
