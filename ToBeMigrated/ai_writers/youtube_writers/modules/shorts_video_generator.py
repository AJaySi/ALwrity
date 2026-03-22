"""
YouTube Shorts Video Generator

This module provides functionality to generate YouTube Shorts videos using AI.
It adapts the story video generator for the vertical format and shorter duration of Shorts.
"""

import os
import re
import time
import json
import uuid
import tempfile
import logging
import traceback
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional, Union, Callable
from functools import wraps
from datetime import datetime
import random
import functools

import streamlit as st
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import requests

# Try importing moviepy with proper error handling
try:
    from moviepy.editor import (
        ImageSequenceClip,
        TextClip,
        CompositeVideoClip,
        AudioFileClip,
        AudioClip,
        CompositeAudioClip,
    )
    MOVIEPY_AVAILABLE = True
except ImportError as e:
    st.error(
        "MoviePy is not properly installed. Please install it using:\n"
        "pip install moviepy imageio imageio-ffmpeg"
    )
    MOVIEPY_AVAILABLE = False

# Try importing gTTS with proper error handling
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    st.error(
        "gTTS is not installed. Please install it using:\n"
        "pip install gTTS"
    )
    GTTS_AVAILABLE = False

# Import LLM text generation and image generation
from lib.gpt_providers.text_generation.main_text_generation import llm_text_gen
from lib.gpt_providers.text_to_image_generation.main_generate_image_from_prompt import generate_image
from .shorts_script_generator import generate_shorts_script, generate_shorts_narration
from lib.ai_writers.ai_story_video_generator.story_video_generator import StoryVideoGenerator

# Configure logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
log_file = log_dir / f"shorts_generator_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Constants
DEFAULT_FPS = 30  # Higher FPS for smoother Shorts
DEFAULT_DURATION = 2  # seconds per scene (shorter for Shorts)
DEFAULT_TRANSITION_DURATION = 0.5  # seconds for transition
DEFAULT_FONT_SIZE = 32  # Larger font for vertical format
DEFAULT_FONT_COLOR = "white"
DEFAULT_MUSIC_URL = "https://freepd.com/music/Upbeat%20Uplifting%20Corporate.mp3"  # Example free music URL
DEFAULT_IMAGE_WIDTH = 1080  # Standard Shorts width
DEFAULT_IMAGE_HEIGHT = 1920  # Standard Shorts height (9:16 aspect ratio)
TEXT_AREA_HEIGHT_RATIO = 1/4  # Smaller text area for vertical format
TEXT_PADDING = 30
TEXT_OVERLAY_ALPHA = 180  # More opaque overlay for better readability

# Shorts-specific constants
MAX_SHORTS_DURATION = 60  # Maximum duration for YouTube Shorts
MIN_SHORTS_DURATION = 15  # Minimum duration for YouTube Shorts
DEFAULT_SHORTS_DURATION = 30  # Default duration for Shorts
MAX_SCENES = 15  # Maximum number of scenes to generate
MIN_SCENES = 5   # Minimum number of scenes
WORDS_PER_SECOND = 2.5  # Average speaking rate for narration

# Video resolutions for Shorts (vertical format)
VIDEO_RESOLUTIONS = {
    "1080p": (1080, 1920),  # Standard Shorts resolution
    "720p": (720, 1280),    # Lower resolution option
}

# Transition styles optimized for Shorts
TRANSITION_STYLES = {
    "None": None,
    "Fade": "fade",
    "Slide Up": "slide_up",
    "Slide Down": "slide_down",
    "Zoom": "zoom",
    "Wipe": "wipe"
}

# Content styles for Shorts
CONTENT_STYLES = {
    "Tutorial": {
        "style": "tutorial",
        "description": "Step-by-step instructional content"
    },
    "Story": {
        "style": "story",
        "description": "Narrative-driven content"
    },
    "Tips": {
        "style": "tips",
        "description": "Quick tips and tricks"
    },
    "Review": {
        "style": "review",
        "description": "Product or service reviews"
    },
    "Behind the Scenes": {
        "style": "behind_scenes",
        "description": "Behind-the-scenes content"
    }
}

# Narration languages
NARRATION_LANGUAGES = {
    "English (US)": "en-us",
    "English (UK)": "en-gb",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Italian": "it",
    "Japanese": "ja",
    "Korean": "ko",
    "Chinese": "zh-cn",
    "Hindi": "hi"
}

# Retry configuration
MAX_RETRIES = 3
INITIAL_RETRY_DELAY = 1  # Initial delay in seconds
MAX_RETRY_DELAY = 30     # Maximum delay in seconds
RETRYABLE_ERRORS = (
    ConnectionError,
    TimeoutError,
    requests.exceptions.RequestException,
    OSError,  # For file system operations
    IOError,  # For file system operations
)

def retry_on_error(max_retries: int = MAX_RETRIES, initial_delay: int = INITIAL_RETRY_DELAY, max_delay: int = MAX_RETRY_DELAY):
    """
    Decorator for retrying functions on specific errors with exponential backoff.
    
    # ... existing code ...
"""

def extract_narration_from_shorts_script(script: str) -> str:
    """
    Extract and optimize narration from the script for Shorts format.
    Ensures narration is concise, valuable, and properly timed.
    """
    scenes = re.split(r'\n\n+', script)
    narration_lines = []
    total_words = 0
    max_words = 75  # Target for 30-second video (2.5 words per second)
    
    # Extract all potential narration lines first
    potential_lines = []
    for scene in scenes:
        match = re.search(r'Audio/Voiceover:\s*(.*)', scene)
        if match:
            narration = match.group(1).strip()
            narration = re.split(r'\n[A-Z][^:]+:', narration)[0].strip()
            if narration:
                potential_lines.append(narration)
    
    # Process lines to create engaging narration
    if potential_lines:
        # Start with a hook
        first_line = potential_lines[0]
        if not any(word in first_line.lower() for word in ['discover', 'learn', 'find out', 'see how', 'watch']):
            first_line = f"Discover how to {first_line.lower()}"
        narration_lines.append(first_line)
        total_words += len(first_line.split())
        
        # Process middle lines
        for line in potential_lines[1:-1]:
            # Add value-focused phrases
            if not any(word in line.lower() for word in ['because', 'why', 'how', 'what', 'when', 'where']):
                line = f"Here's why: {line}"
            
            # Check word count
            words = line.split()
            if total_words + len(words) <= max_words:
                narration_lines.append(line)
                total_words += len(words)
            else:
                break
        
        # Add a strong closing
        if len(potential_lines) > 1:
            last_line = potential_lines[-1]
            if not any(phrase in last_line.lower() for phrase in ['try it', 'get started', 'follow for more']):
                last_line = f"Ready to try it? {last_line}"
            if total_words + len(last_line.split()) <= max_words:
                narration_lines.append(last_line)
    
    # If we have too few words, add a call to action
    if total_words < 50 and narration_lines:
        cta = "Follow for more tips like this!"
        if total_words + len(cta.split()) <= max_words:
            narration_lines.append(cta)
    
    # Join with proper pacing and emphasis
    final_narration = ' '.join(narration_lines)
    
    # Add emphasis to key points
    final_narration = re.sub(r'([.!?])\s+', r'\1\n\n', final_narration)  # Add pauses
    
    return final_narration

def generate_shorts_narration(script: str, language: str = "en-us", target_duration: int = 30) -> str:
    """
    Generate a clean, natural-sounding narration script for YouTube Shorts.
    Focuses only on what the listener needs to hear, without technical details.
    """
    # Calculate target word count based on duration and user-defined speaking rate
    words_per_second = getattr(st.session_state, 'svgen_words_per_second', WORDS_PER_SECOND)
    narration_padding = getattr(st.session_state, 'svgen_narration_padding', 0.5)
    target_words = int((target_duration - narration_padding) * words_per_second)
    
    # Extract key information from the script
    scenes = re.split(r'\n\n+', script)
    audio_lines = []
    
    for scene in scenes:
        # Extract only the audio/voiceover content
        audio_match = re.search(r'Audio/Voiceover:\s*(.*?)(?=\n|$)', scene)
        if audio_match:
            audio_lines.append(audio_match.group(1).strip())
    
    # Create a specialized prompt for clean narration generation
    narration_prompt = f"""
    Create a natural, conversational narration script for a YouTube Shorts video.
    Focus ONLY on what the listener needs to hear - no technical details, scene descriptions, or timing markers.
    
    Content Context:
    {script}
    
    Requirements:
    1. Length: {target_duration} seconds (approximately {target_words} words)
    2. Style: Natural, conversational, and engaging
    3. Structure:
       - Start with a hook
       - Present key points
       - End with a call to action
    4. Tone: {st.session_state.svgen_content_style.lower()}
    
    Important Guidelines:
    - Write ONLY the spoken words - no descriptions, timing, or technical details
    - Use natural language that sounds good when spoken
    - Keep sentences short and clear
    - Add natural pauses with ellipsis (...)
    - No scene numbers, timing markers, or technical instructions
    - No sound effect descriptions or music cues
    - No formatting markers or special characters
    - Target word count: {target_words} words (±10%)
    - Speaking rate: {words_per_second} words per second
    
    Example of good narration:
    "Writer's block got you down? Meet your new secret weapon: an AI content writer! This tool helps you write ten times faster. No more blank page terror! Blog posts, social media, even killer emails - all generated in seconds. Ready to unleash your content creation superpowers? Try it free today!"
    
    Format the narration as a single, flowing script with natural pauses.
    """
    
    try:
        # Generate narration using LLM
        narration = llm_text_gen(narration_prompt)
        if narration:
            # Clean up the narration
            narration = re.sub(r'\s+', ' ', narration)  # Remove extra spaces
            narration = re.sub(r'[^\w\s.,!?…-]', '', narration)  # Keep only essential punctuation
            narration = re.sub(r'([.!?])\s+', r'\1\n\n', narration)  # Add natural pauses
            narration = re.sub(r'\*\*.*?\*\*', '', narration)  # Remove any markdown
            narration = re.sub(r'\(.*?\)', '', narration)  # Remove any parenthetical notes
            narration = re.sub(r'\n\s*\n', '\n\n', narration)  # Clean up extra line breaks
            
            # Verify word count
            word_count = len(narration.split())
            if word_count < target_words * 0.9 or word_count > target_words * 1.1:
                print(f'[WARNING] Generated narration word count ({word_count}) is outside target range ({target_words}±10%)')
            
            return narration.strip()
    except Exception as e:
        print(f'[ERROR] Failed to generate narration: {e}')
        return None

def write_yt_shorts_video():
    """
    Main function to generate a YouTube Shorts video.
    This function provides a Streamlit interface for users to generate Shorts videos.
    """
    st.markdown("""
        <style>
        .stepper {
            display: flex;
            justify-content: space-between;
            margin-bottom: 2rem;
        }
        .step {
            flex: 1;
            text-align: center;
            padding: 0.5rem 0;
            border-bottom: 4px solid #e0e0e0;
            color: #888;
            font-weight: 600;
            font-size: 1.1rem;
        }
        .step.active {
            color: #2563eb;
            border-bottom: 4px solid #2563eb;
            background: #f0f6ff;
            border-radius: 8px 8px 0 0;
        }
        .card {
            background: #f8fafc;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
            padding: 2rem 2rem 1.5rem 2rem;
            margin-bottom: 2rem;
        }
        .section-title {
            font-size: 1.3rem;
            font-weight: 700;
            margin-bottom: 1rem;
            color: #222;
            display: flex;
            align-items: center;
        }
        .section-title svg {
            margin-right: 0.5rem;
        }
        .primary-btn {
            background: #2563eb;
            color: #fff;
            border-radius: 8px;
            font-size: 1.1rem;
            font-weight: 600;
            padding: 0.75rem 2.5rem;
            border: none;
            margin-top: 1.5rem;
            margin-bottom: 0.5rem;
            box-shadow: 0 2px 8px rgba(37,99,235,0.08);
        }
        </style>
    """, unsafe_allow_html=True)

    # Stepper logic
    if 'shorts_stage' not in st.session_state:
        st.session_state.shorts_stage = 1
    if 'generated_script' not in st.session_state:
        st.session_state.generated_script = None
    if 'script_approved' not in st.session_state:
        st.session_state.script_approved = False

    # Stepper UI
    st.markdown(f'''
    <div class="stepper">
        <div class="step {'active' if st.session_state.shorts_stage == 1 else ''}">1. Input Details</div>
        <div class="step {'active' if st.session_state.shorts_stage == 2 else ''}">2. Script Review</div>
        <div class="step {'active' if st.session_state.shorts_stage == 3 else ''}">3. Video Generation</div>
    </div>
    ''', unsafe_allow_html=True)

    # --- Stage 1: Input Details ---
    if st.session_state.shorts_stage == 1:
        print('[DEBUG] Stage 1: Input Details loaded')
        st.markdown('---')
        st.markdown('### 1️⃣ Input Video Details')
        st.info("Fill in all details below, then click **Generate Script** to continue.")
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">📝 Video Content</div>', unsafe_allow_html=True)
            video_topic = st.text_input(
                "What's your video about?",
                placeholder="Enter the main topic or theme of your Shorts video",
                help="Be specific about what you want to create"
            )
            style_col, duration_col = st.columns(2)
            with style_col:
                content_style = st.selectbox(
                    "Content Style",
                    list(CONTENT_STYLES.keys()),
                    help="Select the style that best fits your content"
                )
            with duration_col:
                video_duration = st.slider(
                    "Duration (seconds)",
                    MIN_SHORTS_DURATION,
                    MAX_SHORTS_DURATION,
                    DEFAULT_SHORTS_DURATION,
                    help=f"Shorts must be between {MIN_SHORTS_DURATION} and {MAX_SHORTS_DURATION} seconds"
                )
                
                # Calculate and display scene count based on duration
                scene_duration = DEFAULT_DURATION  # seconds per scene
                max_possible_scenes = min(MAX_SCENES, int(video_duration / scene_duration))
                min_possible_scenes = max(MIN_SCENES, int(video_duration / (scene_duration * 2)))
                
                scene_count = st.slider(
                    "Number of Scenes",
                    min_possible_scenes,
                    max_possible_scenes,
                    min(max_possible_scenes, 10),  # Default to 10 or max possible
                    help=f"Based on {scene_duration}s per scene, you can have {min_possible_scenes}-{max_possible_scenes} scenes"
                )
            st.markdown('</div>', unsafe_allow_html=True)

        with st.container():
            settings_col = st.columns(1)[0]
            with settings_col:
                with st.expander("⚙️ Video Settings", expanded=True):
                    res_col, trans_col = st.columns(2)
                    with res_col:
                        resolution = st.selectbox(
                            "Resolution",
                            list(VIDEO_RESOLUTIONS.keys()),
                            help="Higher resolution = better quality but longer processing time"
                        )
                    with trans_col:
                        transition_style = st.selectbox(
                            "Transition Style",
                            list(TRANSITION_STYLES.keys()),
                            help="How scenes transition between each other"
                        )
                    
                    # Add timing controls
                    st.markdown("---")
                    st.markdown("#### ⏱️ Timing Settings")
                    
                    # Scene timing controls
                    timing_col1, timing_col2 = st.columns(2)
                    with timing_col1:
                        scene_duration = st.slider(
                            "Seconds per Scene",
                            min_value=1.0,
                            max_value=5.0,
                            value=DEFAULT_DURATION,
                            step=0.5,
                            help="How long each scene should be displayed"
                        )
                        st.session_state.svgen_scene_duration = scene_duration
                        
                    with timing_col2:
                        transition_duration = st.slider(
                            "Transition Duration (seconds)",
                            min_value=0.1,
                            max_value=1.0,
                            value=DEFAULT_TRANSITION_DURATION,
                            step=0.1,
                            help="Duration of transitions between scenes"
                        )
                        st.session_state.svgen_transition_duration = transition_duration
                    
                    # Narration timing controls
                    narr_timing_col1, narr_timing_col2 = st.columns(2)
                    with narr_timing_col1:
                        words_per_second = st.slider(
                            "Speaking Rate (words/second)",
                            min_value=1.5,
                            max_value=3.5,
                            value=WORDS_PER_SECOND,
                            step=0.1,
                            help="Adjust narration speed (default: 2.5 words/second)"
                        )
                        st.session_state.svgen_words_per_second = words_per_second
                        
                    with narr_timing_col2:
                        narration_padding = st.slider(
                            "Narration Padding (seconds)",
                            min_value=0.0,
                            max_value=2.0,
                            value=0.5,
                            step=0.1,
                            help="Extra time to add to narration duration"
                        )
                        st.session_state.svgen_narration_padding = narration_padding
                    
                    # Calculate and display timing information
                    total_scene_time = scene_duration * scene_count
                    total_transition_time = transition_duration * (scene_count - 1)
                    total_video_time = total_scene_time + total_transition_time
                    
                    st.info(f"""
                    **Timing Summary:**
                    - Total Scene Time: {total_scene_time:.1f}s
                    - Total Transition Time: {total_transition_time:.1f}s
                    - Estimated Video Duration: {total_video_time:.1f}s
                    - Target Narration Length: {int(total_video_time * words_per_second)} words
                    """)
                with st.expander("🎙️ Narration Settings", expanded=True):
                    narr_col1, narr_col2 = st.columns(2)
                    with narr_col1:
                        narration_language = st.selectbox(
                            "Language",
                            list(NARRATION_LANGUAGES.keys()),
                            help="Select the language for narration"
                        )
                    with narr_col2:
                        include_music = st.checkbox(
                            "Include Background Music",
                            value=True,
                            help="Add background music to enhance the video"
                        )
        st.markdown('---')
        can_generate_script = bool(video_topic and content_style and video_duration and resolution and narration_language)
        if st.button("📝 Generate Script", key="generate_script_btn", help="Generate a script for your Shorts video", use_container_width=True, disabled=not can_generate_script):
            print(f'[DEBUG] Generate Script button clicked. Topic: {video_topic}, Style: {content_style}, Duration: {video_duration}, Resolution: {resolution}, Language: {narration_language}')
            try:
                with st.spinner("Generating script..."):
                    script = generate_shorts_script(
                        hook_type="Question",
                        main_topic=video_topic,
                        target_audience="general",
                        tone_style=content_style,
                        content_type=CONTENT_STYLES[content_style]["style"],
                        duration_seconds=video_duration,
                        include_captions=True,
                        include_text_overlay=True,
                        include_sound_effects=True,
                        vertical_framing_notes=True,
                        language=narration_language
                    )
                    print(f'[DEBUG] Script generated: {bool(script)}')
                    if script:
                        st.session_state.generated_script = script
                        st.session_state.script_approved = False
                        st.session_state.shorts_stage = 2
                        st.session_state.svgen_resolution = resolution
                        st.session_state.svgen_transition_style = transition_style
                        st.session_state.svgen_narration_language = narration_language
                        st.session_state.svgen_include_music = include_music
                        st.session_state.svgen_content_style = content_style
                        st.session_state.svgen_video_duration = video_duration
                        st.session_state.svgen_video_topic = video_topic
                        print('[DEBUG] Script saved to session state and moving to Stage 2')
                        st.success("Script generated! Review and edit below.")
                    else:
                        print('[ERROR] Script generation failed')
                        st.error("Failed to generate script. Please try again.")
            except Exception as e:
                print(f'[ERROR] Exception during script generation: {e}')
                st.error(f"An error occurred while generating the script: {str(e)}")
                logger.error(f"Error in script generation: {str(e)}")
                logger.error(traceback.format_exc())
        if not can_generate_script:
            st.warning("Please fill in all required fields above to enable script generation.")
        st.markdown('---')
        st.info("Next: Review and edit your script.")

    # --- Stage 2: Script Review & Edit ---
    if st.session_state.shorts_stage == 2:
        print('[DEBUG] Stage 2: Script Review & Edit loaded')
        st.markdown('---')
        st.markdown('### 2️⃣ Script Review & Edit')
        st.info("Review your generated script. Use the Edit tab to make changes. Approve to continue.")
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📄 Script Preview & Edit</div>', unsafe_allow_html=True)
        preview_tab, edit_tab = st.tabs(["Preview", "Edit"])
        with preview_tab:
            st.markdown(st.session_state.generated_script)
            if not st.session_state.script_approved:
                if st.button("✅ Approve Script", key="approve_script_btn", use_container_width=True):
                    st.session_state.script_approved = True
                    print('[DEBUG] Script approved by user')
                    st.success("Script approved! You can now generate your video.")
        with edit_tab:
            edited_script = st.text_area(
                "Edit Script",
                value=st.session_state.generated_script,
                height=400,
                help="Make any necessary changes to the script. The format should be maintained."
            )
            if edited_script != st.session_state.generated_script:
                print('[DEBUG] Script edited by user')
                st.session_state.generated_script = edited_script
                st.session_state.script_approved = False
                st.info("Script updated. Please review and approve the changes.")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('---')
        st.button("⬅️ Back to Details", key="back_to_details_btn", use_container_width=True, on_click=lambda: st.session_state.update({'shorts_stage': 1}))
        if st.session_state.script_approved:
            st.success("Script approved! You can now generate your video.")
            st.button("🎬 Proceed to Video Generation", key="proceed_to_video_btn", use_container_width=True, on_click=lambda: st.session_state.update({'shorts_stage': 3}))
        else:
            st.warning("Please approve your script before proceeding.")
        st.markdown('---')
        st.info("Next: Review and edit narration, then generate your video.")

    # --- Stage 3: Video Generation ---
    if st.session_state.shorts_stage == 3:
        print('[DEBUG] Stage 3: Narration & Video Generation loaded')
        st.markdown('---')
        st.markdown('### 3️⃣ Narration & Video Generation')
        st.info("Edit or generate narration, preview audio, then click **Generate Video**.")
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🗣️ Narration for Review & Edit</div>', unsafe_allow_html=True)
        narr_col1, narr_col2 = st.columns([4, 1])
        with narr_col1:
            if 'editable_narration' not in st.session_state:
                st.session_state.editable_narration = generate_shorts_narration(
                    st.session_state.generated_script,
                    language=st.session_state.svgen_narration_language,
                    target_duration=st.session_state.svgen_video_duration
                )
                print('[DEBUG] Initial narration generated')
            
            edited_narration = st.text_area(
                "Edit narration to be used for TTS:",
                value=st.session_state.editable_narration,
                height=120,
                key="editable_narration_area",
                help="Edit the narration to sound natural when spoken. No technical details needed."
            )
            st.session_state.editable_narration = edited_narration
            
            # Calculate and display timing information
            narration_word_count = len(edited_narration.split())
            words_per_second = 2.5  # Standard speaking rate
            estimated_duration = narration_word_count / words_per_second
            
            narration_stats = (
                f"Words: {narration_word_count} | "
                f"Est. duration: {estimated_duration:.1f}s | "
                f"Target: {st.session_state.svgen_video_duration}s"
            )
            st.caption(narration_stats)
            
            # Display timing warnings
            if estimated_duration < 20:
                st.warning("⚠️ Narration is too short for a 30-second video. Consider generating a new narration.")
            elif estimated_duration > 35:
                st.warning("⚠️ Narration is too long for a 30-second video. Consider generating a new narration.")
            
            # Narration Tips in an expander
            with st.expander("💡 Narration Tips", expanded=False):
                st.markdown("""
                ### Tips for Natural Narration
                
                - Write only what should be spoken
                - Keep it conversational and clear
                - Use natural pauses (...)
                - Focus on the message, not the technical details
                - End with a clear call to action
                """)
            
            tts_col1, tts_col2 = st.columns(2)
            with tts_col1:
                tts_gender = st.selectbox("Voice Gender (affects some TTS engines)", ["Default", "Female", "Male"], key="tts_gender_select")
            with tts_col2:
                tts_speed = st.selectbox("Speech Speed", ["Normal", "Slow"], key="tts_speed_select")
            if st.button("🔊 Preview Narration Audio", key="preview_tts_btn"):
                print('[DEBUG] TTS preview button clicked')
                try:
                    tts_kwargs = {"lang": NARRATION_LANGUAGES[st.session_state.svgen_narration_language]}
                    tts_kwargs["slow"] = tts_speed == "Slow"
                    tts = gTTS(text=edited_narration, **tts_kwargs)
                    preview_audio_path = os.path.join(tempfile.gettempdir(), f"tts_preview_{os.getpid()}.mp3")
                    tts.save(preview_audio_path)
                    with open(preview_audio_path, "rb") as audio_file:
                        audio_bytes = audio_file.read()
                    st.audio(audio_bytes, format="audio/mp3")
                    print('[DEBUG] TTS preview audio generated and played')
                except Exception as tts_err:
                    print(f'[ERROR] Failed to generate TTS preview: {tts_err}')
                    st.error(f"Failed to generate TTS preview: {tts_err}")
            if narration_word_count < 10:
                st.warning("Narration is very short. Consider adding more detail.")
            elif narration_word_count > 120:
                st.warning("Narration is quite long. Consider shortening for Shorts.")
        with narr_col2:
            if st.button("🔄 Generate New Narration", key="generate_narration_btn"):
                with st.spinner("Generating engaging narration..."):
                    new_narration = generate_shorts_narration(
                        st.session_state.generated_script,
                        language=st.session_state.svgen_narration_language,
                        target_duration=st.session_state.svgen_video_duration
                    )
                    if new_narration:
                        st.session_state.editable_narration = new_narration
                        print('[DEBUG] New narration generated')
                        st.success("New narration generated successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to generate narration. Please try again.")
            
            if st.button("🤖 Generate AI Narration", key="ai_narration_btn"):
                with st.spinner("Generating AI-optimized narration..."):
                    ai_narr = generate_shorts_narration(
                        st.session_state.generated_script,
                        language=st.session_state.svgen_narration_language,
                        target_duration=st.session_state.svgen_video_duration
                    )
                    if ai_narr:
                        st.session_state.editable_narration = ai_narr
                        print('[DEBUG] AI-generated narration updated')
                        st.success("AI-generated narration updated.")
                        st.rerun()
                    else:
                        st.error("Failed to generate AI narration. Please try again.")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('---')
        st.markdown('### 3️⃣ Video Generation')
        st.info("Click **Generate Video** to start the final process. This may take a few minutes.")
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title"> Video Generation</div>', unsafe_allow_html=True)
        
        # Video Information in an expander
        with st.expander("📋 Video Information", expanded=True):
            st.markdown("""
            ### Video Details
            | Setting | Value |
            |---------|--------|
            | Video Topic | {} |
            | Content Style | {} |
            | Duration | {} seconds |
            | Resolution | {} |
            | Narration Language | {} |
            | Background Music | {} |
            """.format(
                st.session_state.svgen_video_topic,
                st.session_state.svgen_content_style,
                st.session_state.svgen_video_duration,
                st.session_state.svgen_resolution,
                st.session_state.svgen_narration_language,
                "Yes" if st.session_state.svgen_include_music else "No"
            ))
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div style="text-align:center">', unsafe_allow_html=True)
        st.button("⬅️ Back to Script Review", key="back_to_script_btn", use_container_width=True, on_click=lambda: st.session_state.update({'shorts_stage': 2}))
        if st.button("🚀 Generate Video", key="generate_video_btn", use_container_width=True):
            print('[DEBUG] Generate Video button clicked')
            try:
                with st.spinner("Generating your Shorts video..."):
                    st.info("Step 1/3: Generating images...")
                    image_paths = []
                    temp_dir = Path(tempfile.mkdtemp())
                    # Filter out empty scenes and limit to MAX_SCENES
                    scenes = [s.strip() for s in st.session_state.generated_script.split("\n\n") if s.strip()][:MAX_SCENES]
                    resolution = st.session_state.svgen_resolution
                    narration_language = st.session_state.svgen_narration_language
                    scene_count = 0
                    num_scenes_total = len(scenes)
                    progress_bar = st.progress(0.0)
                    status_text = st.empty()
                    
                    # Initialize or load image cache
                    if 'generated_image_paths' not in st.session_state:
                        st.session_state.generated_image_paths = {}
                    generated_image_paths = st.session_state.generated_image_paths
                    
                    # Clear any invalid cache entries
                    generated_image_paths = {k: v for k, v in generated_image_paths.items() 
                                          if os.path.exists(v) and k < num_scenes_total}
                    st.session_state.generated_image_paths = generated_image_paths
                    
                    preview_container = st.container()
                    preview_thumbnails = []

                    def retry_on_error(max_retries=3, initial_delay=1, max_delay=10):
                        def decorator(func):
                            @functools.wraps(func)
                            def wrapper(*args, **kwargs):
                                delay = initial_delay
                                for attempt in range(max_retries):
                                    try:
                                        return func(*args, **kwargs)
                                    except Exception as e:
                                        if attempt == max_retries - 1:
                                            raise
                                        print(f'[WARN] Retry {attempt+1}/{max_retries} for image generation: {e}')
                                        time.sleep(delay)
                                        delay = min(delay * 2, max_delay)
                                return None
                            return wrapper
                        return decorator

                    @retry_on_error(max_retries=3, initial_delay=2, max_delay=10)
                    def safe_generate_image(prompt):
                        return generate_image(prompt)
                    
                    for i, scene in enumerate(scenes):
                        print(f'[DEBUG] Processing scene {i+1}/{num_scenes_total}')
                        status_text.text(f"Generating image for scene {i+1}/{num_scenes_total}...")
                        
                        # Check cache first
                        if i in generated_image_paths:
                            image_paths.append(generated_image_paths[i])
                            preview_thumbnails.append((generated_image_paths[i], i+1))
                            print(f'[DEBUG] Using cached image for scene {i+1}')
                            scene_count += 1
                            progress_bar.progress(scene_count / num_scenes_total)
                            continue
                        
                        # Extract details for a more specific prompt
                        visual_desc = scene.split("Visual Instructions:")[1].split("\n")[0] if "Visual Instructions:" in scene else scene
                        narration_match = re.search(r'Audio/Voiceover:\s*(.*)', scene)
                        narration_line = narration_match.group(1).strip() if narration_match else ""
                        
                        # Enhanced prompt with more specific details and style guidance
                        prompt = (
                            f"Create a vertical (9:16) image for YouTube Shorts video.\n"
                            f"Scene {i+1} of {num_scenes_total}:\n"
                            f"Visual Description: {visual_desc}\n"
                            f"Context: {narration_line}\n"
                            f"Style Requirements:\n"
                            f"- High contrast and vibrant colors for better mobile viewing\n"
                            f"- Clear focal point in the center for vertical format\n"
                            f"- Professional quality, cinematic lighting\n"
                            f"- Text-safe areas on top and bottom\n"
                            f"- Visually distinct from other scenes\n"
                            f"- Modern, engaging composition\n"
                            f"- Suitable for {st.session_state.svgen_content_style} style content\n"
                            f"Technical Requirements:\n"
                            f"- Vertical 9:16 aspect ratio\n"
                            f"- High resolution, sharp details\n"
                            f"- No text or watermarks\n"
                            f"- No blurry or low-quality elements"
                        )
                        
                        try:
                            image_path = safe_generate_image(prompt)
                            if image_path:
                                img = Image.open(image_path)
                                target_size = VIDEO_RESOLUTIONS[resolution]
                                img = img.resize(target_size, Image.LANCZOS)
                                resized_path = temp_dir / f"scene_{i}.png"
                                img.save(resized_path)
                                image_paths.append(str(resized_path))
                                generated_image_paths[i] = str(resized_path)
                                st.session_state.generated_image_paths = generated_image_paths
                                preview_thumbnails.append((str(resized_path), i+1))
                                print(f'[DEBUG] Generated and cached new image for scene {i+1}')
                            else:
                                print(f'[ERROR] Image generation failed for scene {i+1}')
                                st.warning(f"Image generation failed for scene {i+1}. Skipping.")
                        except Exception as img_err:
                            print(f'[ERROR] Exception during image generation for scene {i+1}: {img_err}')
                            st.warning(f"Error generating image for scene {i+1}: {img_err}")
                        
                        scene_count += 1
                        progress_bar.progress(scene_count / num_scenes_total)
                        
                        # Update preview after each image
                        with preview_container:
                            preview_container.empty()  # Clear previous preview
                            if preview_thumbnails:
                                # Create a grid layout with 5 columns
                                cols = st.columns(5)
                                
                                # Display thumbnails in a grid
                                for idx, (img_path, sc_num) in enumerate(preview_thumbnails):
                                    with cols[idx % 5]:
                                        # Create a smaller thumbnail
                                        img = Image.open(img_path)
                                        # Calculate aspect ratio to maintain 9:16
                                        target_width = 100  # Smaller width
                                        target_height = int(target_width * (16/9))
                                        img = img.resize((target_width, target_height), Image.LANCZOS)
                                        
                                        # Display with a compact caption
                                        st.image(
                                            img,
                                            caption=f"Scene {sc_num}",
                                            use_column_width=True,
                                            key=f"preview_{sc_num}"  # Add unique key for each image
                                        )
                                        
                                        # Add a small progress indicator
                                        if idx == len(preview_thumbnails) - 1:
                                            st.caption(f"Generating scene {scene_count + 1}...")
                                            
                                # Add a clear divider between preview and next steps
                                st.markdown("---")
                    status_text.text("Image generation complete!")
                    print(f'[DEBUG] Image generation complete. Total images: {len(image_paths)}')
                    if not image_paths:
                        print('[ERROR] No images generated')
                        st.error("Failed to generate images. Please try again.")
                        return
                    st.info("Step 2/3: Generating narration...")
                    narration_path = temp_dir / "narration.mp3"
                    narration_text = st.session_state.editable_narration
                    try:
                        tts = gTTS(text=narration_text, lang=NARRATION_LANGUAGES[narration_language])
                        tts.save(str(narration_path))
                        print('[DEBUG] Narration audio generated and saved')
                        
                        # Verify the audio file was created and is valid
                        if not os.path.exists(str(narration_path)):
                            raise Exception("Narration audio file was not created")
                        
                        # Test the audio file by loading it
                        test_audio = AudioFileClip(str(narration_path))
                        if test_audio.duration <= 0:
                            raise Exception("Generated audio file is invalid or empty")
                        test_audio.close()
                        
                    except Exception as tts_err:
                        print(f'[ERROR] Failed to generate narration: {tts_err}')
                        st.error(f"Failed to generate narration: {tts_err}")
                        return
                        
                    st.info("Step 3/3: Creating video...")
                    video_generator = StoryVideoGenerator()
                    try:
                        # Verify audio file exists before video creation
                        if not os.path.exists(str(narration_path)):
                            raise Exception("Narration audio file not found")
                            
                        video_path = video_generator.create_video(
                            image_paths=image_paths,
                            audio_path=str(narration_path),
                            fps=DEFAULT_FPS,
                            duration_per_image=getattr(st.session_state, 'svgen_scene_duration', DEFAULT_DURATION)
                        )
                        if video_path and os.path.exists(video_path):
                            print(f'[DEBUG] Video generated at {video_path}')
                            st.success("✨ Video generated successfully! Preview below and download your video.")
                            st.video(video_path)
                            safe_topic = re.sub(r'[^\w\-]+', '_', st.session_state.svgen_video_topic)
                            download_filename = f"{safe_topic}_shorts_video.mp4"
                            with open(video_path, "rb") as f:
                                video_bytes = f.read()
                            st.download_button(
                                label="⬇️ Download Video",
                                data=video_bytes,
                                file_name=download_filename,
                                mime="video/mp4"
                            )
                        else:
                            print('[ERROR] Video file not found after generation')
                            st.error("Failed to create video. Please try again.")
                    except Exception as vid_err:
                        print(f'[ERROR] Exception during video creation: {vid_err}')
                        st.error(f"An error occurred while creating the video: {vid_err}")
                        logger.error(f"Error in video generation: {vid_err}")
                        logger.error(traceback.format_exc())
            except Exception as e:
                print(f'[ERROR] Exception during full video generation: {e}')
                st.error(f"An error occurred while generating the video: {str(e)}")
                logger.error(f"Error in video generation: {str(e)}")
                logger.error(traceback.format_exc())
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('---')
        st.info("All done! You can download your video above or go back to make changes.") 