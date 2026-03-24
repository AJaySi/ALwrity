# Auto-Dubbing Feature Documentation

## Overview

Auto-Dubbing enables automatic translation of podcast audio to different languages with optional voice cloning to preserve the original speaker's voice.

## Features

- **Text Translation**: Translate audio transcripts using DeepL (low-cost) or WaveSpeed (high-quality)
- **Voice Cloning**: Preserve original speaker's voice in dubbed audio
- **Multiple Quality Tiers**: Choose between low-cost (DeepL) and high-quality (WaveSpeed) translation
- **Cost Estimation**: Preview costs before starting dubbing tasks
- **Progress Tracking**: Real-time progress updates for long-running tasks

## Architecture

```
backend/services/
├── translation/          # Common translation service
│   ├── __init__.py
│   ├── base_translation.py
│   ├── deepl_translator.py
│   ├── wavespeed_translator.py
│   └── translation_factory.py
│
├── dubbing/             # Audio dubbing service
│   └── __init__.py      # AudioDubbingService
│
└── api/podcast/
    ├── handlers/
    │   └── dubbing.py   # API endpoints
    └── models.py        # Request/response models
```

## Quick Start

### 1. Configure Environment

Add your DeepL API key to `.env`:

```bash
# backend/.env
DEEPL_API_KEY=your-deepl-api-key-here
```

Get a free DeepL API key at: https://www.deepl.com/pro-api

### 2. Basic Audio Dubbing

```python
from services.dubbing import AudioDubbingService

service = AudioDubbingService()
result = service.dub_audio(
    source_audio="/path/to/audio.mp3",
    target_language="Spanish",
    quality="low",  # or "high"
)
```

### 3. High-Quality Dubbing with Voice Clone

```python
result = service.dub_audio(
    source_audio="/path/to/audio.mp3",
    target_language="French",
    quality="high",
    use_voice_clone=True,  # Preserve original voice
    custom_voice_id="my_podcast_voice",
    accuracy=0.8,  # 0.1-1.0
)
```

## API Endpoints

### Create Dubbing Task

```bash
POST /api/podcast/dub/audio
```

**Request:**
```json
{
    "source_audio_url": "https://example.com/audio.mp3",
    "target_language": "Spanish",
    "quality": "low",
    "voice_id": "Wise_Woman",
    "speed": 1.0,
    "use_voice_clone": false
}
```

**Response:**
```json
{
    "task_id": "abc123",
    "status": "pending",
    "message": "Audio dubbing task created"
}
```

### Get Dubbing Result

```bash
GET /api/podcast/dub/{task_id}/result
```

**Response (completed):**
```json
{
    "task_id": "abc123",
    "status": "completed",
    "dubbed_audio_url": "/api/podcast/dub/audio/dubbed_xyz123.mp3",
    "original_transcript": "Hello, welcome to my podcast...",
    "translated_transcript": "Hola, bienvenidos a mi podcast...",
    "source_language": "en",
    "target_language": "Spanish",
    "voice_id": "Wise_Woman",
    "quality": "low",
    "voice_clone_used": false,
    "cost": 0.05,
    "file_size": 45000
}
```

### Clone Voice

```bash
POST /api/podcast/dub/voices/clone
```

**Request:**
```json
{
    "source_audio_url": "https://example.com/voice_sample.mp3",
    "custom_voice_id": "podcast_voice_1",
    "accuracy": 0.7,
    "language_boost": "Spanish"
}
```

**Response:**
```json
{
    "task_id": "clone123",
    "status": "pending",
    "message": "Voice cloning task created"
}
```

### Estimate Cost

```bash
POST /api/podcast/dub/estimate
```

**Request:**
```json
{
    "audio_duration_seconds": 60,
    "target_language": "Spanish",
    "quality": "low",
    "use_voice_clone": false
}
```

**Response:**
```json
{
    "estimated_characters": 900,
    "translation_cost": 0.009,
    "tts_cost": 0.9,
    "voice_clone_cost": 0.0,
    "total_cost": 0.909,
    "currency": "USD"
}
```

### Get Supported Languages

```bash
GET /api/podcast/dub/languages
```

**Response:**
```json
{
    "languages": [
        {"code": "es", "name": "Spanish"},
        {"code": "fr", "name": "French"},
        {"code": "de", "name": "German"},
        ...
    ],
    "count": 34
}
```

### Get Available Voices

```bash
GET /api/podcast/dub/voices
```

**Response:**
```json
{
    "voices": [
        {"id": "Wise_Woman", "name": "Wise Woman", "gender": "female"},
        {"id": "Warm_Man", "name": "Warm Man", "gender": "male"},
        ...
    ],
    "count": 10
}
```

## Translation Pipeline

### Low Quality (DeepL)
```
Source Audio → Download → STT (Gemini) → Translate (DeepL) → TTS (WaveSpeed) → Dubbed Audio
```

### High Quality (WaveSpeed + Voice Clone)
```
Source Audio → Voice Clone → Download → STT → Translate (WaveSpeed) → TTS (cloned voice) → Dubbed Audio
```

## Cost Structure

| Component | Low Quality | High Quality |
|-----------|-------------|--------------|
| Translation | $0.00001/char | $0.0001/char |
| TTS | $0.001/char | $0.001/char |
| Voice Clone | N/A | $0.05/voice |

**Example: 60-second audio (~900 chars)**
- Low quality: ~$0.91
- High quality with voice clone: ~$0.96

## Common Module Usage

The translation service can be used anywhere in the application:

```python
from services.translation import translate_text, TranslationQuality

# Simple translation
result = translate_text(
    text="Hello world",
    target_language="Spanish",
    quality=TranslationQuality.LOW
)
print(result.translated_text)  # "Hola mundo"

# Batch translation
from services.translation import translate_batch
results = translate_batch(
    texts=["Hello", "Goodbye"],
    target_language="French",
    quality=TranslationQuality.LOW
)
```

## Error Handling

The dubbing service returns standard HTTP exceptions:

- `400 Bad Request`: Invalid parameters
- `404 Not Found`: Task or file not found
- `500 Internal Server Error`: Dubbing failed (check task error message)

## Background Tasks

Dubbing tasks run in the background. Poll the result endpoint:

```python
import time
while True:
    result = get_dubbing_result(task_id)
    if result.status == "completed":
        print(f"Dubbed audio: {result.dubbed_audio_url}")
        break
    elif result.status == "failed":
        print(f"Failed: {result.error}")
        break
    time.sleep(2)
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DEEPL_API_KEY` | DeepL API key for low-quality translation | Yes (for low quality) |
| `DEEPL_USE_PRO` | Use DeepL Pro API | No |
| `WAVESPEED_API_KEY` | WaveSpeed API key (already configured) | Yes |

## Supported Languages

DeepL supports 34 languages including:
- English, Spanish, French, German, Italian, Portuguese
- Japanese, Chinese, Korean, Arabic, Hindi
- Russian, Dutch, Polish, Turkish, Vietnamese
- And more...

See full list via: `GET /api/podcast/dub/languages`
