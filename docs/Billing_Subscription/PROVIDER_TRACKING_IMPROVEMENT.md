# Provider Tracking Improvement

## Problem Statement

The billing dashboard's API Usage Logs were showing generic provider names (e.g., "Video", "Audio", "Stability") instead of the actual providers (WaveSpeed, Google/Gemini, HuggingFace). This made it difficult to:
- Understand which providers are actually being used
- Analyze costs by provider
- Make informed decisions about provider usage
- Track provider-specific trends and patterns

## Solution

Added `actual_provider_name` field to track the real provider behind generic enum values, with intelligent detection based on model names and endpoints.

## Implementation

### 1. Database Model Update

**File**: `backend/models/subscription_models.py`

Added `actual_provider_name` field to `APIUsageLog`:
```python
actual_provider_name = Column(String(50), nullable=True)  # e.g., "wavespeed", "google", "huggingface"
```

### 2. Provider Detection Utility

**File**: `backend/services/subscription/provider_detection.py`

Created intelligent provider detection function that identifies actual providers from:
- Model names (e.g., "alibaba/wan-2.5/text-to-video" → "wavespeed")
- Endpoints (e.g., "/video-generation/wavespeed" → "wavespeed")
- Provider enum values (with fallback logic)

**Supported Providers**:
- **WaveSpeed**: OSS models (Qwen, Ideogram, FLUX, WAN 2.5, Minimax Speech)
- **Google**: Gemini models (gemini-2.5-flash, gemini-2.5-pro, etc.)
- **HuggingFace**: GPT-OSS-120B, Tencent HunyuanVideo, etc.
- **Stability AI**: Stable Diffusion models
- **OpenAI**: GPT-4o, GPT-4o-mini, TTS-1
- **Anthropic**: Claude 3.5 Sonnet

### 3. Service Updates

Updated all media generation services to use provider detection:

- **Video Generation** (`backend/services/llm_providers/main_video_generation.py`)
- **Image Generation** (`backend/services/llm_providers/main_image_generation.py`)
- **Audio Generation** (`backend/services/llm_providers/main_audio_generation.py`)
- **Usage Tracking Service** (`backend/services/subscription/usage_tracking_service.py`)

All services now automatically detect and store the actual provider name when tracking API usage.

### 4. API Endpoint Update

**File**: `backend/api/subscription_api.py`

Updated `/api/subscription/usage-logs` endpoint to:
- Return `actual_provider_name` in response
- Use `actual_provider_name` for display if available
- Fallback to enum value with special handling for MISTRAL → HuggingFace

### 5. Frontend Updates

**Files**:
- `frontend/src/types/billing.ts` - Added `actual_provider_name` to `UsageLog` interface
- `frontend/src/components/billing/UsageLogsTable.tsx` - Display actual provider name prominently

**UI Display**:
- Shows actual provider name (e.g., "WaveSpeed") in bold
- Shows generic enum value (e.g., "video") in smaller text below if different
- Example: "**WaveSpeed**" (video)

### 6. Database Migration

**File**: `backend/scripts/add_actual_provider_name_column.py`

Migration script that:
- Adds `actual_provider_name` column to `api_usage_logs` table
- Backfills existing records with detected provider names
- Safe to run multiple times (checks if column exists)

## Usage

### Running the Migration

```bash
cd backend
python scripts/add_actual_provider_name_column.py
```

### Provider Detection Examples

```python
from services.subscription.provider_detection import detect_actual_provider
from models.subscription_models import APIProvider

# Video generation - WaveSpeed
provider = detect_actual_provider(
    provider_enum=APIProvider.VIDEO,
    model_name="alibaba/wan-2.5/text-to-video",
    endpoint="/video-generation/wavespeed"
)
# Returns: "wavespeed"

# Image generation - WaveSpeed OSS
provider = detect_actual_provider(
    provider_enum=APIProvider.STABILITY,
    model_name="qwen-image",
    endpoint="/image-generation/wavespeed"
)
# Returns: "wavespeed"

# Audio generation - WaveSpeed
provider = detect_actual_provider(
    provider_enum=APIProvider.AUDIO,
    model_name="minimax/speech-02-hd",
    endpoint="/audio-generation/wavespeed"
)
# Returns: "wavespeed"

# LLM - Google Gemini
provider = detect_actual_provider(
    provider_enum=APIProvider.GEMINI,
    model_name="gemini-2.5-flash"
)
# Returns: "google"

# LLM - HuggingFace (MISTRAL enum)
provider = detect_actual_provider(
    provider_enum=APIProvider.MISTRAL,
    model_name="openai/gpt-oss-120b:groq"
)
# Returns: "huggingface"
```

## Benefits

1. **Accurate Provider Tracking**: Know exactly which providers (WaveSpeed, Google, HuggingFace) are being used
2. **Better Cost Analysis**: Analyze costs by actual provider, not generic categories
3. **Usage Insights**: Understand provider usage patterns and trends
4. **Informed Decisions**: Make data-driven decisions about provider selection
5. **Backward Compatible**: Existing records are backfilled, new records automatically tracked

## Future Enhancements

1. **Provider Analytics Dashboard**: Visualize usage and costs by actual provider
2. **Provider Recommendations**: Suggest provider switches based on cost/performance
3. **Provider Cost Comparison**: Compare costs across providers for similar operations
4. **Provider Performance Metrics**: Track response times, success rates by provider

## Testing

After running the migration, verify:

1. **Database**: Check that `actual_provider_name` column exists and has values
   ```sql
   SELECT provider, actual_provider_name, model_used, COUNT(*) 
   FROM api_usage_logs 
   GROUP BY provider, actual_provider_name, model_used;
   ```

2. **API**: Check that `/api/subscription/usage-logs` returns `actual_provider_name`
   ```bash
   curl http://localhost:8000/api/subscription/usage-logs?user_id=YOUR_USER_ID
   ```

3. **UI**: Check that billing dashboard shows actual provider names in Usage Logs table

## Notes

- The `provider` enum field is still used for limit enforcement (VIDEO, AUDIO, STABILITY, etc.)
- The `actual_provider_name` field is for display and analytics only
- Detection is based on heuristics (model names, endpoints) - may need refinement for edge cases
- Existing records are backfilled, but may not be 100% accurate if model names are ambiguous
