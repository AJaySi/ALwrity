# Changelog

All notable changes to the ALwrity project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added

#### Auto-Dubbing Feature (Podcast Maker)
- **Translation Service** (`backend/services/translation/`)
  - Common translation module for use across the entire application
  - DeepL integration for low-cost, high-quality text translation (500k chars/month free)
  - WaveSpeed integration for high-quality video/audio translation
  - Support for 34+ languages
  - Batch translation support
  - Factory pattern for provider selection
  - Cost estimation utilities

- **Audio Dubbing Service** (`backend/services/dubbing/`)
  - Audio dubbing with STT → Translate → TTS pipeline
  - Voice cloning support to preserve original speaker's voice
  - Low-quality (DeepL) and high-quality (WaveSpeed) modes
  - Batch dubbing support
  - Cost estimation

- **Podcast API Endpoints** (`backend/api/podcast/`)
  - `POST /api/podcast/dub/audio` - Create audio dubbing task
  - `GET /api/podcast/dub/{task_id}/result` - Get dubbing result
  - `POST /api/podcast/dub/voices/clone` - Clone voice from audio sample
  - `GET /api/podcast/dub/voices/{task_id}/result` - Get voice clone result
  - `POST /api/podcast/dub/estimate` - Estimate dubbing cost
  - `GET /api/podcast/dub/languages` - List supported languages
  - `GET /api/podcast/dub/voices` - List available TTS voices

- **Bug Fixes**
  - Fixed missing `Path` import in `scene_animation.py`

### Changed

- Updated `backend/services/__init__.py` to export translation and dubbing services
- Updated `.env` with DeepL API key placeholder

### Documentation

- Added `backend/docs/AUTO_DUBBING.md` with comprehensive feature documentation

## [Previous Releases]

See git history for previous changelog entries.
