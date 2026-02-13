# Brand Avatar API Documentation

## Overview
The Brand Avatar API provides endpoints for generating, varying, and enhancing brand avatars using WaveSpeed AI.

**Base URL**: `/api/onboarding/assets`

## Endpoints

### 1. Generate Avatar
Generate a new brand avatar from a text prompt.

- **URL**: `/generate-avatar`
- **Method**: `POST`
- **Body** (`application/json`):
  ```json
  {
    "prompt": "A professional tech entrepreneur, studio lighting",
    "style_preset": "Cinematic",
    "aspect_ratio": "1:1",
    "model": "ideogram-v3-turbo",
    "provider": "wavespeed"
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "image_url": "/api/assets/{user_id}/avatars/{filename}.png",
    "image_base64": "...",
    "asset_id": 123
  }
  ```

### 2. Create Variation
Create a variation of an existing avatar/image.

- **URL**: `/create-variation`
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`
- **Form Data**:
  - `prompt` (text): Description of the variation (e.g., "same person but smiling")
  - `file` (file): The reference image file
- **Response**:
  ```json
  {
    "success": true,
    "image_url": "/api/assets/{user_id}/avatars/{filename}.png",
    "image_base64": "...",
    "asset_id": 124
  }
  ```

### 3. Enhance Avatar
Upscale and enhance an existing avatar image.

- **URL**: `/enhance-avatar`
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`
- **Form Data**:
  - `file` (file): The image file to enhance
- **Response**:
  ```json
  {
    "success": true,
    "image_url": "/api/assets/{user_id}/avatars/{filename}.png",
    "image_base64": "...",
    "asset_id": 125
  }
  ```

### 4. Enhance Prompt
Optimize a simple prompt into a detailed, high-quality prompt using WaveSpeed.

- **URL**: `/enhance-prompt`
- **Method**: `POST`
- **Body**:
  ```json
  {
    "prompt": "man in suit"
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "original_prompt": "man in suit",
    "optimized_prompt": "A professional portrait of a man in a tailored navy blue suit, confident expression, studio lighting, 4k resolution..."
  }
  ```

## Providers
- **Default Provider**: `wavespeed`
- **Models**:
  - Generation: `ideogram-v3-turbo` (default), `qwen-image`
  - Editing/Variation: `qwen-edit-plus` (default)
  - Enhancement: `nano-banana-pro-edit-ultra` (4K upscale)
