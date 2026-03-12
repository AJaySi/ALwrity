"""
Hugging Face Provider Module for ALwrity.

Provides text and structured JSON generation through Hugging Face Router
(OpenAI-compatible API), with retry and explicit fallback controls.
"""

import json
import os
import re
from functools import lru_cache
from typing import Any, Dict, List, Optional

from tenacity import retry, retry_if_exception, stop_after_attempt, wait_random_exponential

from utils.logger_utils import get_service_logger
from .routing_policy import PREMIUM_DEFAULT_MODEL, SIF_LOW_COST_MODEL_DEFAULTS

logger = get_service_logger("huggingface_provider")

try:
    from openai import NotFoundError, OpenAI

    OPENAI_AVAILABLE = True
except ImportError:  # pragma: no cover - environment-dependent
    OPENAI_AVAILABLE = False
    OpenAI = None
    NotFoundError = Exception
    logger.warning("OpenAI library not available. Install with: pip install openai")

HF_FALLBACK_MODELS = [
    PREMIUM_DEFAULT_MODEL,
    "moonshotai/Kimi-K2-Instruct-0905:groq",
    "meta-llama/Llama-3.1-8B-Instruct:groq",
    SIF_LOW_COST_MODEL_DEFAULTS[0],
]


def _candidate_model_variants(model: str):
    """Yield model IDs to try for a single logical model preference."""
    if not model:
        return

    # Try configured model first (supports provider suffixes like ':groq').
    yield model

    # Fallback to base repo id when provider suffix isn't recognized.
    if ":" in model:
        base_model = model.split(":", 1)[0]
        if base_model:
            yield base_model


def _fallback_model_sequence(model: str, fallback_models: Optional[List[str]] = None):
    """Yield unique model candidates preserving caller-defined order.

    IMPORTANT: no implicit global fallback chain is applied here; callers must
    explicitly pass fallback_models if they want multi-model retries.
    """
    if fallback_models:
        sequence = [model] + fallback_models
    else:
        sequence = [model]

    seen = set()
    for preferred_model in sequence:
        for candidate in _candidate_model_variants(preferred_model):
            if candidate and candidate not in seen:
                seen.add(candidate)
                yield candidate


def _is_non_retryable_hf_error(exc: Exception) -> bool:
    msg = str(exc).lower()
    status = getattr(exc, "status_code", None)

    if isinstance(exc, NotFoundError) or "not found" in msg or "404" in msg:
        return True
    if status == 402 or "402" in msg or "depleted" in msg or "credits" in msg:
        return True
    if status == 401 or "unauthorized" in msg or "401" in msg:
        return True
    if status == 403 or "forbidden" in msg or "403" in msg:
        return True
    return False


def _should_retry_hf_error(exc: Exception) -> bool:
    return not _is_non_retryable_hf_error(exc)


def _classify_hf_error(exc: Exception) -> str:
    msg = str(exc).lower()
    if any(token in msg for token in ["insufficient", "balance", "quota", "billing", "payment", "402"]):
        return "billing_or_quota"
    if "unauthorized" in msg or "forbidden" in msg or "401" in msg or "403" in msg:
        return "auth_or_permission"
    if "not found" in msg or "404" in msg:
        return "model_not_found"
    return "unknown"


def _error_details(exc: Exception) -> Dict[str, str]:
    return {
        "type": type(exc).__name__,
        "message": str(exc),
        "repr": repr(exc),
    }


def get_huggingface_api_key(explicit_api_key: Optional[str] = None) -> str:
    """Get Hugging Face API key with basic validation."""
    api_key = explicit_api_key or os.getenv("HF_TOKEN")
    if not api_key:
        error_msg = "HF_TOKEN environment variable is not set. Please set it in your .env file."
        logger.error(error_msg)
        raise ValueError(error_msg)

    if not api_key.startswith("hf_"):
        error_msg = "HF_TOKEN appears to be invalid. It should start with 'hf_'."
        logger.error(error_msg)
        raise ValueError(error_msg)

    return api_key


@lru_cache(maxsize=16)
def _get_hf_client(api_key: str):
    return OpenAI(base_url="https://router.huggingface.co/v1", api_key=api_key)


@retry(
    retry=retry_if_exception(_should_retry_hf_error),
    wait=wait_random_exponential(min=1, max=60),
    stop=stop_after_attempt(6),
)
def huggingface_text_response(
    prompt: str,
    model: str = PREMIUM_DEFAULT_MODEL,
    fallback_models: Optional[List[str]] = None,
    temperature: float = 0.7,
    max_tokens: int = 2048,
    top_p: float = 0.9,
    system_prompt: Optional[str] = None,
    api_key: Optional[str] = None,
) -> str:
    """Generate text with explicit fallback model sequence."""
    try:
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI library not available. Install with: pip install openai")

        hf_api_key = get_huggingface_api_key(api_key)
        client = _get_hf_client(hf_api_key)

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = None
        last_error = None
        for candidate_model in _fallback_model_sequence(model, fallback_models):
            try:
                response = client.chat.completions.create(
                    model=candidate_model,
                    messages=messages,
                    temperature=temperature,
                    top_p=top_p,
                    max_tokens=max_tokens,
                )
                if candidate_model != model:
                    logger.warning("HF text fallback model used: {}", candidate_model)
                break
            except NotFoundError as nf_err:
                last_error = nf_err
                logger.warning("HF text model not found: {}", candidate_model)
                continue
            except Exception as call_err:
                last_error = call_err
                logger.warning("HF text call failed for model {}: {}", candidate_model, _error_details(call_err))
                continue

        if response is None:
            raise last_error or RuntimeError("All fallback models failed")

        generated_text = response.choices[0].message.content or ""
        generated_text = re.sub(r"```[a-zA-Z]*\n?", "", generated_text)
        generated_text = re.sub(r"```\n?", "", generated_text).strip()
        return generated_text

    except Exception as exc:
        details = _error_details(exc)
        logger.error(
            "❌ Hugging Face text generation failed | error_class={} | type={} | message={} | repr={}",
            _classify_hf_error(exc),
            details["type"],
            details["message"],
            details["repr"],
        )
        raise Exception(f"Hugging Face text generation failed: {exc}") from exc


@retry(
    retry=retry_if_exception(_should_retry_hf_error),
    wait=wait_random_exponential(min=1, max=60),
    stop=stop_after_attempt(6),
)
def huggingface_structured_json_response(
    prompt: str,
    schema: Dict[str, Any],
    model: str = PREMIUM_DEFAULT_MODEL,
    fallback_models: Optional[List[str]] = None,
    temperature: float = 0.7,
    max_tokens: int = 8192,
    system_prompt: Optional[str] = None,
    api_key: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate structured JSON with explicit fallback model sequence."""
    try:
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI library not available. Install with: pip install openai")

        hf_api_key = get_huggingface_api_key(api_key)
        client = _get_hf_client(hf_api_key)

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = None
        last_error = None

        for candidate_model in _fallback_model_sequence(model, fallback_models):
            try:
                response = client.chat.completions.create(
                    model=candidate_model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    response_format={"type": "json_object"},
                )
                if candidate_model != model:
                    logger.warning("HF structured fallback model used: {}", candidate_model)
                break
            except Exception as err:
                last_error = err
                if isinstance(err, NotFoundError):
                    logger.warning("HF structured model not found: {}", candidate_model)
                    continue

                msg = str(err).lower()
                if "422" in msg or "not supported" in msg:
                    try:
                        response = client.chat.completions.create(
                            model=candidate_model,
                            messages=messages,
                            temperature=temperature,
                            max_tokens=max_tokens,
                        )
                        if candidate_model != model:
                            logger.warning("HF structured fallback(no response_format) model: {}", candidate_model)
                        break
                    except Exception as second_err:
                        last_error = second_err
                        continue

        if response is None:
            raise last_error or RuntimeError("All fallback models failed")

        response_text = (response.choices[0].message.content or "").strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()

        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {"error": "Failed to parse JSON response", "raw_response": response_text}

    except Exception as exc:
        details = _error_details(exc)
        logger.error(
            "❌ Hugging Face structured JSON generation failed | error_class={} | type={} | message={} | repr={}",
            _classify_hf_error(exc),
            details["type"],
            details["message"],
            details["repr"],
        )
        raise Exception(f"Hugging Face structured JSON generation failed: {exc}") from exc


def get_available_models() -> list:
    """Get list of available Hugging Face models for text generation."""
    return [
        PREMIUM_DEFAULT_MODEL,
        "moonshotai/Kimi-K2-Instruct-0905:groq",
        "Qwen/Qwen2.5-VL-7B-Instruct",
        "meta-llama/Llama-3.1-8B-Instruct:groq",
        "microsoft/Phi-3-medium-4k-instruct:groq",
        SIF_LOW_COST_MODEL_DEFAULTS[0],
    ]


def validate_model(model: str) -> bool:
    """Validate if a model identifier is supported."""
    return model in get_available_models()
