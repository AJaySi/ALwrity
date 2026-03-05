# LLM Gateway – Module Reference

This document catalogs the modules under [llm_providers](file:///C:/Users/diksha%20rawat/Desktop/ALwrity/backend/services/llm_providers) with their responsibilities, key classes/functions, configuration, and integration points.

## Text Generation
- **Entry point**: [main_text_generation.py](file:///C:/Users/diksha%20rawat/Desktop/ALwrity/backend/services/llm_providers/main_text_generation.py)
  - llm_text_gen(prompt, system_prompt, json_struct, user_id)
  - Responsibilities:
    - Resolve provider (env or APIKeyManager)
    - Perform strict subscription checks (PricingService, UsageTrackingService)
    - Call Gemini or Hugging Face implementations
  - Integration:
    - models.subscription_models.APIProvider mapping
    - services.subscription.PricingService, UsageTrackingService

- **Gemini provider**: [gemini_provider.py](file:///C:/Users/diksha%20rawat/Desktop/ALwrity/backend/services/llm_providers/gemini_provider.py)
  - get_gemini_api_key() – env validation
  - gemini_text_response(...) – tenacity‑backed retries, text output
  - gemini_structured_json_response(...) – structured JSON output
  - Config: GEMINI_API_KEY
  - SDK: google.generativeai

- **Hugging Face provider**: [huggingface_provider.py](file:///C:/Users/diksha%20rawat/Desktop/ALwrity/backend/services/llm_providers/huggingface_provider.py)
  - get_huggingface_api_key() – env validation
  - huggingface_text_response(...) – Responses API (OpenAI client), retries
  - huggingface_structured_json_response(...) – structured JSON output
  - Config: HF_TOKEN
  - SDK: openai client pointed at Hugging Face router

## Image Generation
- **Contracts**: [image_generation/base.py](file:///C:/Users/diksha%20rawat/Desktop/ALwrity/backend/services/llm_providers/image_generation/base.py)
  - ImageGenerationOptions, ImageGenerationResult
  - ImageEditOptions, FaceSwapOptions (with to_dict helpers)
  - Protocols: ImageGenerationProvider, ImageEditProvider, FaceSwapProvider

- **Hugging Face image**: [image_generation/hf_provider.py](file:///C:/Users/diksha%20rawat/Desktop/ALwrity/backend/services/llm_providers/image_generation/hf_provider.py)
  - Class: HuggingFaceImageProvider(ImageGenerationProvider)
  - generate(options) -> ImageGenerationResult
  - Config: HF_TOKEN, HF_IMAGE_MODEL (default FLUX.1‑Krea‑dev)
  - SDK: huggingface_hub.InferenceClient (provider="fal-ai")

- **Other image modules**:
  - [image_generation/gemini_provider.py](file:///C:/Users/diksha%20rawat/Desktop/ALwrity/backend/services/llm_providers/image_generation/gemini_provider.py) – Gemini image generation integration
  - [image_generation/wavespeed_provider.py](file:///C:/Users/diksha%20rawat/Desktop/ALwrity/backend/services/llm_providers/image_generation/wavespeed_provider.py) – WaveSpeed image editing
  - [image_generation/wavespeed_face_swap_provider.py](file:///C:/Users/diksha%20rawat/Desktop/ALwrity/backend/services/llm_providers/image_generation/wavespeed_face_swap_provider.py) – Face swap
  - [image_generation/wavespeed_edit_provider.py](file:///C:/Users/diksha%20rawat/Desktop/ALwrity/backend/services/llm_providers/image_generation/wavespeed_edit_provider.py) – General edits

## Video Generation
- **Contracts**: [video_generation/base.py](file:///C:/Users/diksha%20rawat/Desktop/ALwrity/backend/services/llm_providers/video_generation/base.py)
  - VideoGenerationOptions, VideoGenerationResult
  - Protocol: VideoGenerationProvider (async, progress callbacks)

- **WaveSpeed video**: [video_generation/wavespeed_provider.py](file:///C:/Users/diksha%20rawat/Desktop/ALwrity/backend/services/llm_providers/video_generation/wavespeed_provider.py)
  - BaseWaveSpeedTextToVideoService:
    - MODEL_NAME/PATH contract
    - calculate_cost(resolution, duration)
    - input validation helpers
  - Model services (e.g., HunyuanVideoService, LTX‑2 variants)
  - Client: services.wavespeed.client.WaveSpeedClient

## Audio / STT
- **Modules**:
  - [audio_to_text_generation/gemini_audio_text.py](file:///C:/Users/diksha%20rawat/Desktop/ALwrity/backend/services/llm_providers/audio_to_text_generation/gemini_audio_text.py)
  - [audio_to_text_generation/stt_audio_blog.py](file:///C:/Users/diksha%20rawat/Desktop/ALwrity/backend/services/llm_providers/audio_to_text_generation/stt_audio_blog.py)
  - Responsibilities:
    - Convert audio to text
    - Provide structured outputs for downstream blog/content workflows

## Shared Patterns
- **Environment handling**:
  - Providers validate their own secrets and default models
  - No secrets logged; provider‑scoped logger via utils.logger_utils.get_service_logger
- **Result normalization**:
  - Binary payloads (image_bytes, video_bytes) and metadata are standardized
  - Provider name/model surfaced in result for analytics
- **Retries and resilience**:
  - Text providers use tenacity exponential backoff
  - Media providers implement validation and sensible defaults

## Integration Points
- Subscription enforcement and preflight:
  - [api/subscription/routes/preflight.py](file:///C:/Users/diksha%20rawat/Desktop/ALwrity/backend/api/subscription/routes/preflight.py)
  - PricingService/UsageTrackingService are invoked prior to calling providers
- Usage logging:
  - Centralized in subscription services; gateway returns normalized data for logging
- Pricing:
  - Per‑provider and per‑model costs reflected in preflight and service layers

## Extending the Gateway
1. Choose modality (text/image/video/audio)
2. Implement the appropriate Protocol and dataclasses
3. Validate and load configuration from environment
4. Normalize outputs to gateway result types
5. Add pricing/preflight entries and update subscription limit checks
6. Add route handlers that perform validation then call the new provider

Following this reference ensures new providers integrate smoothly with ALwrity’s subscription, pricing, and analytics subsystems while keeping UI/API stable across diverse models.
