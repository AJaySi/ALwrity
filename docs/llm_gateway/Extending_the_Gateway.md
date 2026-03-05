# Extending the LLM Gateway

This guide provides a checklist and templates for adding new providers or modalities to the ALwrity LLM Gateway.

## Checklist

1.  **Define the Provider Interface**:
    - [ ] Create a new module in `backend/services/llm_providers/<modality>/`.
    - [ ] Define input options dataclass (e.g., `MyNewProviderOptions`).
    - [ ] Implement the standard Protocol (e.g., `ImageGenerationProvider`).

2.  **Configuration**:
    - [ ] Add necessary API keys to `.env.example` and `APIKeyManager`.
    - [ ] Add new provider enum to `backend/models/subscription_models.py` (`APIProvider`).

3.  **Pricing & Usage**:
    - [ ] Add default pricing in `PricingService` or migration script.
    - [ ] Ensure `UsageSummary` table has columns for this provider (if it's a major one) or map it to a generic category.

4.  **Integration**:
    - [ ] Register the provider in the main entry point (e.g., `main_image_generation.py`).
    - [ ] Update `preflight.py` to handle cost estimation for this provider.

5.  **Frontend**:
    - [ ] Update `billingService.ts` to handle the new provider key in usage stats (if applicable).
    - [ ] Add provider icon/color in `billingService.ts`.

## Skeleton Template (Python)

Here is a template for a new **Image Generation Provider**:

```python
from __future__ import annotations
import os
from typing import Optional, Dict, Any
from dataclasses import dataclass
from .base import ImageGenerationOptions, ImageGenerationResult, ImageGenerationProvider
from utils.logger_utils import get_service_logger

logger = get_service_logger("image_generation.my_new_provider")

class MyNewProvider(ImageGenerationProvider):
    """
    My New Provider implementation.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("MY_PROVIDER_API_KEY")
        if not self.api_key:
            raise RuntimeError("MY_PROVIDER_API_KEY is required")
        # Initialize client here

    def generate(self, options: ImageGenerationOptions) -> ImageGenerationResult:
        logger.info(f"Generating image with MyNewProvider: {options.prompt[:50]}...")
        
        try:
            # 1. Call External API
            # response = client.generate(...)
            
            # 2. Process Response (Mock)
            image_bytes = b"fake_image_data" 
            width = options.width
            height = options.height
            
            # 3. Return Standard Result
            return ImageGenerationResult(
                image_bytes=image_bytes,
                width=width,
                height=height,
                provider="my_new_provider",
                model=options.model or "default-model",
                seed=options.seed,
                metadata={"raw_response": "..."}
            )
            
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            raise
```

## Skeleton Template (Route Integration)

In `main_image_generation.py`:

```python
from .image_generation.my_new_provider import MyNewProvider

def generate_image(prompt: str, provider: str, ...):
    # ... existing code ...
    
    if provider == "my_new_provider":
        service = MyNewProvider()
        result = service.generate(options)
        
    # ... existing code ...
```
