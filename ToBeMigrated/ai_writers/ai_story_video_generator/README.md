# AI Story Video Generator

This module allows users to generate animated story videos using AI. It leverages Google's Gemini model to create stories and generate images for each scene, then combines them into a video.

## Features

- Generate complete stories based on user prompts
- Create scene-by-scene storyboards
- Generate images for each scene using Gemini
- Compile images into an animated video
- Add background music and text overlays
- Export videos in MP4 format

## How It Works

1. User provides a story prompt and preferences
2. AI generates a complete story with multiple scenes
3. For each scene, an image is generated
4. Images are compiled into a video with transitions
5. Optional background music and text overlays are added
6. The final video is available for download

## Requirements

- Google Gemini API key
- FFmpeg for video processing
- Python libraries: moviepy, pillow, requests

## Usage

Access this tool through the Streamlit interface by selecting "AI Story Video Generator" from the main menu.