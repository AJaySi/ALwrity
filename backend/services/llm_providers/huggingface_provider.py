"""
Hugging Face Provider Module for ALwrity.

Provides text and structured JSON generation through Hugging Face Router
(OpenAI-compatible API), with retry and explicit fallback controls.
"""

<<<<<<< HEAD
<<<<<<< HEAD
import os
=======
import hashlib
>>>>>>> pr-419
=======
>>>>>>> pr-437
import json
import os
import re
<<<<<<< HEAD
<<<<<<< HEAD
from functools import lru_cache
<<<<<<< HEAD
from typing import Optional, Dict, Any
=======
from typing import Optional, Dict, Any, List, Iterable
>>>>>>> pr-418
=======
import time
from threading import Lock
from typing import Optional, Dict, Any
>>>>>>> pr-419
=======
from typing import Any, Dict, List, Optional

from tenacity import retry, retry_if_exception, stop_after_attempt, wait_random_exponential
>>>>>>> pr-437

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

_HF_CLIENT_CACHE: Dict[str, Any] = {}
_HF_CLIENT_CACHE_LOCK = Lock()

<<<<<<< HEAD

def _masked_key_id(api_key: str) -> str:
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()[:12]


def get_huggingface_client(api_key: str):
    """Get or create a cached Hugging Face/OpenAI-compatible client for the API key."""
    key_id = _masked_key_id(api_key)
    with _HF_CLIENT_CACHE_LOCK:
        cached_client = _HF_CLIENT_CACHE.get(key_id)
        if cached_client is not None:
            logger.debug("Reusing cached Hugging Face client for key_id={}", key_id)
            return cached_client

        client = OpenAI(
            base_url="https://router.huggingface.co/hf/v1",
            api_key=api_key,
        )
        _HF_CLIENT_CACHE[key_id] = client
        logger.debug("Created new Hugging Face client for key_id={}", key_id)
        return client


def _candidate_model_variants(model: str, allow_model_variant_fallback: bool = True):
    """Yield model ids to try for a single logical model preference."""
=======
def _candidate_model_variants(model: str):
    """Yield model IDs to try for a single logical model preference."""
>>>>>>> pr-437
    if not model:
        return

    # Try configured model first (supports provider suffixes like ':groq').
    yield model

<<<<<<< HEAD
    # Fallback to base repo id when provider suffix is not recognized by the router
    if allow_model_variant_fallback and ":" in model:
=======
    # Fallback to base repo id when provider suffix isn't recognized.
    if ":" in model:
>>>>>>> pr-437
        base_model = model.split(":", 1)[0]
        if base_model:
            yield base_model


<<<<<<< HEAD
def _fallback_model_sequence(model: str, fallback_models: Optional[List[str]] = None):
    """Yield unique model candidates preserving caller-defined order.

    IMPORTANT: no implicit global fallback chain is applied here; callers must
    explicitly pass fallback_models if they want multi-model retries.
    """
    if fallback_models:
        sequence = [model] + fallback_models
    else:
        sequence = [model]
<<<<<<< HEAD
=======
def _fallback_model_sequence(
    model: str,
    fallback_models: Optional[List[str]] = None,
    allow_model_variant_fallback: bool = True,
):
    sequence: Iterable[str]
    if fallback_models is None:
        # Safe default only when caller doesn't provide explicit policy.
        sequence = [model] + HF_FALLBACK_MODELS
    else:
        # Caller owns fallback policy fully. Empty list means only requested model.
        sequence = [model] + list(fallback_models)

>>>>>>> pr-418
=======

>>>>>>> pr-437
    seen = set()
    for preferred_model in sequence:
        for candidate in _candidate_model_variants(
            preferred_model,
            allow_model_variant_fallback=allow_model_variant_fallback,
        ):
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

<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
@retry(
    retry=retry_if_exception(_should_retry_hf_error),
    wait=wait_random_exponential(min=1, max=60),
    stop=stop_after_attempt(6),
)
=======
=======

>>>>>>> pr-437
@lru_cache(maxsize=16)
def _get_hf_client(api_key: str):
    return OpenAI(base_url="https://router.huggingface.co/v1", api_key=api_key)


<<<<<<< HEAD
>>>>>>> pr-416
=======
@retry(
    wait=wait_random_exponential(min=0.5, max=8),
    stop=stop_after_attempt(3),
    reraise=True,
)
>>>>>>> pr-419
=======
@retry(
    retry=retry_if_exception(_should_retry_hf_error),
    wait=wait_random_exponential(min=1, max=60),
    stop=stop_after_attempt(6),
)
>>>>>>> pr-437
def huggingface_text_response(
    prompt: str,
    model: str = PREMIUM_DEFAULT_MODEL,
    fallback_models: Optional[List[str]] = None,
    temperature: float = 0.7,
    max_tokens: int = 2048,
    top_p: float = 0.9,
    system_prompt: Optional[str] = None,
<<<<<<< HEAD
    api_key: Optional[str] = None,
=======
    fallback_models: Optional[List[str]] = None,
    allow_model_variant_fallback: bool = True,
>>>>>>> pr-418
) -> str:
    """Generate text with explicit fallback model sequence."""
    try:
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI library not available. Install with: pip install openai")
<<<<<<< HEAD
        
        # Get API key with proper error handling
        api_key = get_huggingface_api_key(api_key)
        logger.info(f"🔑 Hugging Face API key loaded: {bool(api_key)} (length: {len(api_key) if api_key else 0})")
        
        if not api_key:
            raise Exception("HF_TOKEN not found in environment variables")
            
<<<<<<< HEAD
        # Initialize Hugging Face client
<<<<<<< HEAD
        client = OpenAI(
            base_url="https://router.huggingface.co/v1",
            api_key=api_key,
        )
=======
        client = _get_hf_client(api_key)
>>>>>>> pr-416
=======
        # Initialize/reuse Hugging Face client
        client = get_huggingface_client(api_key)
>>>>>>> pr-419
        logger.info("✅ Hugging Face client initialized for text response")
=======
>>>>>>> pr-437

        hf_api_key = get_huggingface_api_key(api_key)
        client = _get_hf_client(hf_api_key)

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

<<<<<<< HEAD
        # Add debugging for API call
        logger.info(
            "Hugging Face text call | model={} | prompt_len={} | temp={} | top_p={} | max_tokens={}",
            model,
            len(prompt) if isinstance(prompt, str) else '<non-str>',
            temperature,
            top_p,
            max_tokens,
        )
        
        logger.info("🚀 Making Hugging Face API call (chat completion)...")
        
<<<<<<< HEAD
<<<<<<< HEAD
        # Add rate limiting to prevent expensive API calls
        import time
        time.sleep(1)  # 1 second delay between API calls
        
<<<<<<< HEAD
        # Call exactly the requested model; no retries, no fallbacks, no variants
=======
>>>>>>> pr-416
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens
        )
=======
        response = None
        last_error = None
        for candidate_model in _fallback_model_sequence(
            model=model,
            fallback_models=fallback_models,
            allow_model_variant_fallback=allow_model_variant_fallback,
        ):
=======
        response = None
        last_error = None
        fallback_attempt = 0
        for candidate_model in _fallback_model_sequence(model):
            fallback_attempt += 1
            started_at = time.perf_counter()
>>>>>>> pr-419
            try:
                response = client.chat.completions.create(
                    model=candidate_model,
                    messages=messages,
                    temperature=temperature,
                    top_p=top_p,
                    max_tokens=max_tokens
                )
                elapsed_ms = (time.perf_counter() - started_at) * 1000
                logger.debug(
                    "HF text attempt={} model={} elapsed_ms={:.2f}",
                    fallback_attempt,
                    candidate_model,
                    elapsed_ms,
                )
                if candidate_model != model:
                    logger.warning("HF text generation switched to fallback model: {}", candidate_model)
                break
            except NotFoundError as nf_err:
                last_error = nf_err
                elapsed_ms = (time.perf_counter() - started_at) * 1000
                logger.debug(
                    "HF text attempt={} model={} elapsed_ms={:.2f} status=model_not_found",
                    fallback_attempt,
                    candidate_model,
                    elapsed_ms,
                )
                logger.warning("HF model not found: {}. Trying fallback model.", candidate_model)
                continue

        if response is None:
            raise last_error or Exception("Hugging Face text generation failed: all fallback models failed")
>>>>>>> pr-418
        
        # Extract text from response
        generated_text = response.choices[0].message.content
        
        # Clean up the response
        if generated_text:
            # Remove any markdown formatting if present
            generated_text = re.sub(r'```[a-zA-Z]*\n?', '', generated_text)
            generated_text = re.sub(r'```\n?', '', generated_text)
            generated_text = generated_text.strip()
        
        logger.info("✅ Hugging Face text response generated successfully (length: {})", len(generated_text))
        return generated_text
        
    except Exception as e:
        error_class = _classify_hf_error(e)
<<<<<<< HEAD
        error_details = _hf_error_details(e)
        logger.error(f"❌ Hugging Face text generation failed: {error_details}")
        
        # Extra diagnostics: try to capture raw response if available
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"🔍 HF Error Diagnostics:")
            logger.error(f"  - Status: {e.response.status_code}")
            logger.error(f"  - Headers: {dict(e.response.headers)}")
=======
        response = None
        last_error = None
        for candidate_model in _fallback_model_sequence(model, fallback_models):
>>>>>>> pr-437
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

<<<<<<< HEAD
<<<<<<< HEAD
=======
@retry(
    wait=wait_random_exponential(min=0.5, max=8),
    stop=stop_after_attempt(3),
    reraise=True,
)
>>>>>>> pr-419
=======
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
>>>>>>> pr-437
def huggingface_structured_json_response(
    prompt: str,
    schema: Dict[str, Any],
    model: str = PREMIUM_DEFAULT_MODEL,
    fallback_models: Optional[List[str]] = None,
    temperature: float = 0.7,
    max_tokens: int = 8192,
    system_prompt: Optional[str] = None,
<<<<<<< HEAD
    api_key: Optional[str] = None,
=======
    fallback_models: Optional[List[str]] = None,
    allow_model_variant_fallback: bool = True,
>>>>>>> pr-418
) -> Dict[str, Any]:
    """Generate structured JSON with explicit fallback model sequence."""
    try:
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI library not available. Install with: pip install openai")
<<<<<<< HEAD
        
        # Get API key with proper error handling
        api_key = get_huggingface_api_key(api_key)
        logger.info(f"🔑 Hugging Face API key loaded: {bool(api_key)} (length: {len(api_key) if api_key else 0})")
        
        if not api_key:
            raise Exception("HF_TOKEN not found in environment variables")
            
<<<<<<< HEAD
        # Initialize OpenAI client with Hugging Face base URL
        # Use standard Inference API endpoint
<<<<<<< HEAD
        client = OpenAI(
            base_url="https://router.huggingface.co/v1",
            api_key=api_key,
        )
=======
        client = _get_hf_client(api_key)
>>>>>>> pr-416
=======
        # Initialize/reuse OpenAI client with Hugging Face base URL
        client = get_huggingface_client(api_key)
>>>>>>> pr-419
        logger.info("✅ Hugging Face client initialized for structured JSON response")
=======
>>>>>>> pr-437

        hf_api_key = get_huggingface_api_key(api_key)
        client = _get_hf_client(hf_api_key)

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

<<<<<<< HEAD
        # Add debugging for API call
        logger.info(
            "Hugging Face structured call | model={} | prompt_len={} | schema_kind={} | temp={} | max_tokens={}",
            model,
            len(prompt) if isinstance(prompt, str) else '<non-str>',
            type(schema).__name__,
            temperature,
            max_tokens,
        )
        
        logger.info("🚀 Making Hugging Face structured API call...")
        
        # Make the API call using standard Chat Completions
        logger.info("🚀 Making Hugging Face API call (chat completion)...")
        
        # Add JSON schema to prompt for guidance
        json_schema_str = json.dumps(schema, indent=2)
        messages[-1]["content"] += f"\n\nJSON Schema:\n{json_schema_str}"
        
        try:
<<<<<<< HEAD
            response = None
            last_error = None
<<<<<<< HEAD
<<<<<<< HEAD
            for candidate_model in _fallback_model_sequence(model, fallback_models):
=======
            for candidate_model in _fallback_model_sequence(
                model=model,
                fallback_models=fallback_models,
                allow_model_variant_fallback=allow_model_variant_fallback,
            ):
>>>>>>> pr-418
=======
            fallback_attempt = 0
            for candidate_model in _fallback_model_sequence(model):
                fallback_attempt += 1
                started_at = time.perf_counter()
>>>>>>> pr-419
                try:
                    response = client.chat.completions.create(
                        model=candidate_model,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        response_format={"type": "json_object"} # Try to enforce JSON mode if supported
                    )
                    elapsed_ms = (time.perf_counter() - started_at) * 1000
                    logger.debug(
                        "HF structured attempt={} model={} elapsed_ms={:.2f} response_format=json_object",
                        fallback_attempt,
                        candidate_model,
                        elapsed_ms,
                    )
                    if candidate_model != model:
                        logger.warning("HF structured generation switched to fallback model: {}", candidate_model)
                    break
                except NotFoundError as nf_err:
                    last_error = nf_err
                    elapsed_ms = (time.perf_counter() - started_at) * 1000
                    logger.debug(
                        "HF structured attempt={} model={} elapsed_ms={:.2f} status=model_not_found response_format=json_object",
                        fallback_attempt,
                        candidate_model,
                        elapsed_ms,
                    )
                    logger.warning("HF structured model not found: {}. Trying fallback model.", candidate_model)
                    continue

            if response is None:
                raise last_error or Exception("Hugging Face structured generation failed: all fallback models failed")
            
            response_text = response.choices[0].message.content
            
            # Clean up response text if needed
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            try:
                parsed_json = json.loads(response_text)
                logger.info("✅ Hugging Face structured JSON response parsed successfully")
                return parsed_json
            except json.JSONDecodeError as json_err:
                logger.error(f"❌ JSON parsing failed: {json_err}")
                logger.error(f"Raw response: {response_text}")
                
                # Try to extract JSON from the response using regex
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    try:
                        extracted_json = json.loads(json_match.group())
                        logger.info("✅ JSON extracted using regex fallback")
                        return extracted_json
                    except json.JSONDecodeError:
                        pass
                
                return {"error": "Failed to parse JSON response", "raw_response": response_text}
                
        except Exception as e:
            logger.error(f"❌ Hugging Face API call failed: {e}")
            # If 422 Unprocessable Entity (often due to response_format not supported), retry without it
            if "422" in str(e) or "not supported" in str(e).lower() or isinstance(e, NotFoundError):
                logger.info("Retrying without response_format...")
                response = None
                last_error = None
<<<<<<< HEAD
<<<<<<< HEAD
                for candidate_model in _fallback_model_sequence(model, fallback_models):
=======
                for candidate_model in _fallback_model_sequence(
                    model=model,
                    fallback_models=fallback_models,
                    allow_model_variant_fallback=allow_model_variant_fallback,
                ):
>>>>>>> pr-418
=======
                fallback_attempt = 0
                for candidate_model in _fallback_model_sequence(model):
                    fallback_attempt += 1
                    started_at = time.perf_counter()
>>>>>>> pr-419
=======
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
>>>>>>> pr-437
                    try:
                        response = client.chat.completions.create(
                            model=candidate_model,
                            messages=messages,
                            temperature=temperature,
                            max_tokens=max_tokens,
                        )
                        elapsed_ms = (time.perf_counter() - started_at) * 1000
                        logger.debug(
                            "HF structured attempt={} model={} elapsed_ms={:.2f} response_format=none",
                            fallback_attempt,
                            candidate_model,
                            elapsed_ms,
                        )
                        if candidate_model != model:
                            logger.warning("HF structured fallback(no response_format) model: {}", candidate_model)
                        break
<<<<<<< HEAD
                    except NotFoundError as nf_err:
                        last_error = nf_err
                        elapsed_ms = (time.perf_counter() - started_at) * 1000
                        logger.debug(
                            "HF structured attempt={} model={} elapsed_ms={:.2f} status=model_not_found response_format=none",
                            fallback_attempt,
                            candidate_model,
                            elapsed_ms,
                        )
                        logger.warning("HF structured model not found (no response_format path): {}", candidate_model)
=======
                    except Exception as second_err:
                        last_error = second_err
>>>>>>> pr-437
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
