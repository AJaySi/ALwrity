"""
YouTube Channel Trailer Generator

This module generates professional channel trailers for YouTube channels using AI.
"""

import streamlit as st
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import sys
import os
from gtts import gTTS
import tempfile
import base64
from io import BytesIO
from datetime import datetime
import logging

# Add the project root to the Python path
project_root = str(Path(__file__).parent.parent.parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from lib.gpt_providers.text_generation.main_text_generation import llm_text_gen
from lib.gpt_providers.text_to_image_generation.main_generate_image_from_prompt import generate_image
from lib.utils.save_to_file import save_to_file, save_audio, save_json, save_text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrailerGeneratorError(Exception):
    """Custom exception for trailer generator errors."""
    pass

def validate_channel_info(channel_info: Dict) -> Tuple[bool, str]:
    """Validate channel information before processing."""
    required_fields = ['channel_name', 'channel_niche', 'target_audience', 'key_topics', 'unique_points']
    
    # Check for missing required fields
    for field in required_fields:
        if not channel_info.get(field):
            return False, f"Missing required field: {field}"
    
    # Validate field lengths
    if len(channel_info['channel_name']) < 3:
        return False, "Channel name must be at least 3 characters long"
    
    if len(channel_info['target_audience']) < 10:
        return False, "Target audience description must be at least 10 characters long"
    
    if len(channel_info['key_topics']) < 10:
        return False, "Key topics must be at least 10 characters long"
    
    if len(channel_info['unique_points']) < 10:
        return False, "Unique selling points must be at least 10 characters long"
    
    return True, ""

def handle_voice_over_error(error: Exception) -> None:
    """Handle voice-over generation errors gracefully."""
    error_messages = {
        "ConnectionError": "Unable to connect to the text-to-speech service. Please check your internet connection.",
        "ValueError": "Invalid text input for voice-over generation.",
        "Exception": f"An error occurred: {str(error)}"
    }
    error_type = type(error).__name__
    error_message = error_messages.get(error_type, error_messages["Exception"])
    logger.error(f"Voice-over generation error: {error_message}")
    st.error(error_message)

def validate_script(script: Dict) -> Tuple[bool, str]:
    """Validate the generated script."""
    required_sections = ['hook', 'introduction', 'showcase', 'value_proposition', 'call_to_action']
    
    # Check for missing sections
    for section in required_sections:
        if section not in script:
            return False, f"Missing required section: {section}"
    
    # Validate section content
    for section, content in script.items():
        if not content.get('text'):
            return False, f"Missing text in section: {section}"
        if not content.get('duration'):
            return False, f"Missing duration in section: {section}"
    
    # Validate total duration
    total_duration = sum(float(content['duration'].split()[0]) for content in script.values())
    if total_duration > 90:  # 90 seconds max
        return False, f"Total duration ({total_duration}s) exceeds maximum allowed (90s)"
    
    return True, ""

def validate_narration(narration: Dict) -> Tuple[bool, str]:
    """Validate the generated narration script."""
    if not narration.get('narration'):
        return False, "Missing narration content"
    
    required_sections = ['hook', 'introduction', 'showcase', 'value_proposition', 'call_to_action']
    for section in required_sections:
        if section not in narration['narration']:
            return False, f"Missing narration for section: {section}"
        
        section_content = narration['narration'][section]
        required_fields = ['text', 'voice_style', 'emotion', 'pauses', 'emphasis']
        for field in required_fields:
            if field not in section_content:
                return False, f"Missing {field} in {section} narration"
    
    return True, ""

# Voice-over configuration
VOICE_OPTIONS = {
    "languages": {
        "en": {
            "name": "English",
            "voices": ["en-US", "en-GB", "en-AU", "en-IN"],
            "default_voice": "en-US"
        },
        "es": {
            "name": "Spanish",
            "voices": ["es-ES", "es-MX", "es-AR"],
            "default_voice": "es-ES"
        },
        "fr": {
            "name": "French",
            "voices": ["fr-FR", "fr-CA"],
            "default_voice": "fr-FR"
        },
        "de": {
            "name": "German",
            "voices": ["de-DE", "de-AT"],
            "default_voice": "de-DE"
        },
        "ja": {
            "name": "Japanese",
            "voices": ["ja-JP"],
            "default_voice": "ja-JP"
        }
    },
    "voice_styles": {
        "professional": {
            "name": "Professional",
            "description": "Clear, confident, and authoritative tone",
            "pace": "moderate",
            "pitch": "medium"
        },
        "casual": {
            "name": "Casual",
            "description": "Friendly and conversational tone",
            "pace": "slightly_fast",
            "pitch": "medium_high"
        },
        "enthusiastic": {
            "name": "Enthusiastic",
            "description": "Energetic and engaging tone",
            "pace": "fast",
            "pitch": "high"
        },
        "calm": {
            "name": "Calm",
            "description": "Relaxed and soothing tone",
            "pace": "slow",
            "pitch": "low"
        },
        "energetic": {
            "name": "Energetic",
            "description": "Dynamic and vibrant tone",
            "pace": "fast",
            "pitch": "medium_high"
        }
    },
    "pacing_options": {
        "very_slow": 0.5,
        "slow": 0.75,
        "moderate": 1.0,
        "slightly_fast": 1.25,
        "fast": 1.5
    }
}

def get_voice_over_options() -> Dict:
    """Get available voice-over options."""
    return VOICE_OPTIONS

def get_voice_style_settings(style: str) -> Dict:
    """Get settings for a specific voice style."""
    return VOICE_OPTIONS["voice_styles"].get(style, VOICE_OPTIONS["voice_styles"]["professional"])

def adjust_text_for_voice_style(text: str, style: str) -> str:
    """Adjust text to better match the selected voice style."""
    style_settings = get_voice_style_settings(style)
    
    # Add pauses and emphasis based on style
    if style == "professional":
        # Add strategic pauses for clarity
        text = text.replace(".", ". [pause]")
        text = text.replace("!", "! [pause]")
    elif style == "casual":
        # Add conversational markers
        text = text.replace(".", "...")
    elif style == "enthusiastic":
        # Add emphasis markers
        text = text.replace("!", "! [emphasis]")
    elif style == "calm":
        # Add longer pauses
        text = text.replace(".", ". [long_pause]")
    elif style == "energetic":
        # Add dynamic emphasis
        text = text.replace("!", "! [dynamic_emphasis]")
    
    return text

@st.cache_data(ttl=3600)  # Cache for 1 hour
def generate_voice_over(
    text: str,
    language: str = 'en',
    voice_style: str = 'professional',
    slow: bool = False
) -> bytes:
    """Generate voice-over audio using gTTS with enhanced options."""
    try:
        # Get language settings
        lang_settings = VOICE_OPTIONS["languages"].get(language, VOICE_OPTIONS["languages"]["en"])
        voice = lang_settings["default_voice"]
        
        # Adjust text based on voice style
        adjusted_text = adjust_text_for_voice_style(text, voice_style)
        
        # Get style settings
        style_settings = get_voice_style_settings(voice_style)
        
        # Generate voice-over
        tts = gTTS(
            text=adjusted_text,
            lang=voice,
            slow=slow
        )
        
        audio_file = BytesIO()
        tts.write_to_fp(audio_file)
        audio_file.seek(0)
        return audio_file.getvalue()
    except Exception as e:
        handle_voice_over_error(e)
        return None

def display_voice_over_options() -> Dict:
    """Display voice-over options in the UI and return selected options."""
    st.markdown("### 🎤 Voice-over Settings")
    
    # Language selection
    language = st.selectbox(
        "Language",
        options=list(VOICE_OPTIONS["languages"].keys()),
        format_func=lambda x: VOICE_OPTIONS["languages"][x]["name"],
        help="Select the language for your voice-over"
    )
    
    # Voice style selection
    voice_style = st.selectbox(
        "Voice Style",
        options=list(VOICE_OPTIONS["voice_styles"].keys()),
        format_func=lambda x: VOICE_OPTIONS["voice_styles"][x]["name"],
        help="Select the style of voice-over"
    )
    
    # Display style description
    style_info = VOICE_OPTIONS["voice_styles"][voice_style]
    st.markdown(f"**Style Description:** {style_info['description']}")
    
    # Pace selection
    pace = st.select_slider(
        "Speaking Pace",
        options=list(VOICE_OPTIONS["pacing_options"].keys()),
        value=style_info["pace"],
        help="Adjust the speaking pace of the voice-over"
    )
    
    return {
        "language": language,
        "voice_style": voice_style,
        "pace": pace
    }

@st.cache_data(ttl=3600)  # Cache for 1 hour
def generate_trailer_script(
    channel_name: str,
    channel_niche: str,
    target_audience: str,
    key_topics: str,
    unique_points: str,
    trailer_length: str
) -> Dict:
    """Generate the trailer script using GPT with caching."""
    try:
        prompt = f"""Create a professional and engaging YouTube channel trailer script for a {channel_niche} channel named '{channel_name}'.

        Channel Details:
        - Target Audience: {target_audience}
        - Key Topics: {key_topics}
        - Unique Selling Points: {unique_points}
        - Desired Length: {trailer_length}

        The script should follow this detailed structure:

        1. Hook (5-10 seconds):
           - Start with a powerful question, statement, or visual hook
           - Address the viewer's pain points or interests
           - Create immediate curiosity
           - Use dynamic language and emotional triggers
           Visual Requirements:
           - Dynamic opening shot or animation
           - Text overlay with key hook phrase
           - Background elements that match the channel theme
           - Smooth camera movement or transition effects

        2. Channel Introduction (10-15 seconds):
           - Clearly state the channel name
           - Explain what makes this channel unique
           - Establish credibility and expertise
           - Use confident, engaging language
           Visual Requirements:
           - Channel logo reveal animation
           - Brand colors and typography
           - Professional backdrop or setting
           - Subtle motion graphics

        3. Content Showcase (10-20 seconds):
           - Highlight 2-3 key content types
           - Show the value and benefits of watching
           - Include specific examples of content
           - Use dynamic transitions between topics
           Visual Requirements:
           - Split-screen or grid layout for content previews
           - Thumbnail-style frames for each content type
           - Dynamic transitions between content examples
           - Overlay graphics showing key statistics or achievements

        4. Value Proposition (5-10 seconds):
           - Clearly state what viewers will gain
           - Emphasize unique benefits
           - Address viewer's needs and desires
           - Use compelling language
           Visual Requirements:
           - Benefit-focused graphics or icons
           - Animated text highlights
           - Background elements that reinforce the value
           - Professional color scheme

        5. Call to Action (5-10 seconds):
           - Clear subscription prompt
           - Mention notification bell
           - Create urgency or FOMO
           - End with channel branding
           Visual Requirements:
           - Subscription button animation
           - Notification bell icon
           - Channel branding elements
           - Final logo reveal

        Additional Requirements:
        - Keep language conversational and engaging
        - Use active voice and present tense
        - Include specific numbers and examples
        - Maintain consistent tone throughout
        - Ensure smooth transitions between sections
        - Optimize for the selected duration ({trailer_length})

        Format the response as a JSON with the following structure:
        {{
            "hook": {{
                "text": "the hook text",
                "duration": "estimated duration in seconds",
                "visual_suggestions": {{
                    "main_visual": "primary visual element description",
                    "text_overlay": "text overlay style and content",
                    "background": "background elements and effects",
                    "transitions": ["transition effects"],
                    "color_scheme": "color palette suggestions"
                }}
            }},
            "introduction": {{
                "text": "the introduction text",
                "duration": "estimated duration in seconds",
                "visual_suggestions": {{
                    "logo_animation": "logo reveal animation style",
                    "typography": "text style and animation",
                    "background": "background elements",
                    "motion_graphics": ["motion graphic elements"],
                    "color_scheme": "color palette suggestions"
                }}
            }},
            "showcase": {{
                "text": "the showcase text",
                "duration": "estimated duration in seconds",
                "visual_suggestions": {{
                    "layout": "content showcase layout style",
                    "thumbnails": ["thumbnail style descriptions"],
                    "transitions": ["transition effects between content"],
                    "overlay_graphics": ["overlay elements"],
                    "color_scheme": "color palette suggestions"
                }}
            }},
            "value_proposition": {{
                "text": "the value proposition text",
                "duration": "estimated duration in seconds",
                "visual_suggestions": {{
                    "benefit_graphics": ["benefit-focused visual elements"],
                    "text_animation": "text animation style",
                    "background": "background elements",
                    "icons": ["icon suggestions"],
                    "color_scheme": "color palette suggestions"
                }}
            }},
            "call_to_action": {{
                "text": "the call to action text",
                "duration": "estimated duration in seconds",
                "visual_suggestions": {{
                    "cta_animation": "call-to-action animation style",
                    "button_design": "subscription button design",
                    "notification_icon": "notification bell design",
                    "branding": "final branding elements",
                    "color_scheme": "color palette suggestions"
                }}
            }},
            "total_duration": "total estimated duration in seconds",
            "notes": {{
                "tone": "suggested tone and style",
                "music_suggestions": ["suggested music types or moods"],
                "transitions": ["suggested transition effects"],
                "special_effects": ["suggested special effects"],
                "production_tips": ["specific production recommendations"],
                "visual_consistency": "guidelines for maintaining visual consistency",
                "brand_guidelines": "specific brand implementation guidelines"
            }}
        }}

        Ensure the script is optimized for the {trailer_length} format and maintains high engagement throughout.
        """
        
        response = get_gpt_response(prompt)
        script = json.loads(response)
        
        # Validate the generated script
        is_valid, error_message = validate_script(script)
        if not is_valid:
            raise TrailerGeneratorError(f"Invalid script generated: {error_message}")
        
        return script
    except json.JSONDecodeError:
        logger.error("Error parsing GPT response as JSON")
        raise TrailerGeneratorError("Error generating script. Please try again.")
    except Exception as e:
        logger.error(f"Error generating script: {str(e)}")
        raise TrailerGeneratorError(f"An error occurred: {str(e)}")

@st.cache_data(ttl=3600)  # Cache for 1 hour
def generate_narration_script(script: Dict) -> Dict:
    """Generate a natural-sounding narration script from the trailer script with caching."""
    try:
        prompt = f"""Convert this YouTube channel trailer script into a natural-sounding narration script.
        The script should be engaging, conversational, and optimized for voice-over delivery.
        
        Original Script:
        {json.dumps(script, indent=2)}
        
        Requirements:
        1. Maintain the same structure and timing
        2. Add natural pauses and emphasis
        3. Include voice modulation suggestions
        4. Add emotional cues
        5. Make it sound conversational
        6. Include pronunciation guides for any technical terms
        7. Add emphasis markers for important points
        
        Format the response as a JSON with the following structure:
        {{
            "narration": {{
                "hook": {{
                    "text": "narration text with emphasis and pauses",
                    "voice_style": "suggested voice style",
                    "emotion": "suggested emotion",
                    "pauses": ["pause points"],
                    "emphasis": ["words to emphasize"]
                }},
                "introduction": {{
                    "text": "narration text with emphasis and pauses",
                    "voice_style": "suggested voice style",
                    "emotion": "suggested emotion",
                    "pauses": ["pause points"],
                    "emphasis": ["words to emphasize"]
                }},
                "showcase": {{
                    "text": "narration text with emphasis and pauses",
                    "voice_style": "suggested voice style",
                    "emotion": "suggested emotion",
                    "pauses": ["pause points"],
                    "emphasis": ["words to emphasize"]
                }},
                "value_proposition": {{
                    "text": "narration text with emphasis and pauses",
                    "voice_style": "suggested voice style",
                    "emotion": "suggested emotion",
                    "pauses": ["pause points"],
                    "emphasis": ["words to emphasize"]
                }},
                "call_to_action": {{
                    "text": "narration text with emphasis and pauses",
                    "voice_style": "suggested voice style",
                    "emotion": "suggested emotion",
                    "pauses": ["pause points"],
                    "emphasis": ["words to emphasize"]
                }}
            }},
            "voice_guidelines": {{
                "overall_tone": "suggested overall tone",
                "pace": "suggested speaking pace",
                "energy_level": "suggested energy level",
                "pronunciation_guide": {{
                    "term": "pronunciation"
                }},
                "special_instructions": ["special voice-over instructions"]
            }}
        }}
        """
        
        response = get_gpt_response(prompt)
        narration = json.loads(response)
        
        # Validate the generated narration
        is_valid, error_message = validate_narration(narration)
        if not is_valid:
            raise TrailerGeneratorError(f"Invalid narration generated: {error_message}")
        
        return narration
    except json.JSONDecodeError:
        logger.error("Error parsing GPT response as JSON")
        raise TrailerGeneratorError("Error generating narration script. Please try again.")
    except Exception as e:
        logger.error(f"Error generating narration script: {str(e)}")
        raise TrailerGeneratorError(f"An error occurred: {str(e)}")

def update_session_state(key: str, value: Any) -> None:
    """Update session state with feedback."""
    st.session_state[key] = value
    st.success(f"{key.replace('_', ' ').title()} updated successfully!")

def write_yt_channel_trailer():
    """Generate a YouTube channel trailer script and visual elements."""
    
    st.title("🎥 YouTube Channel Trailer Generator")
    st.markdown("Create an engaging channel trailer that converts visitors into subscribers.")
    
    # Initialize session state for workflow
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 1
    if 'channel_info' not in st.session_state:
        st.session_state.channel_info = {}
    if 'script' not in st.session_state:
        st.session_state.script = None
    if 'visuals' not in st.session_state:
        st.session_state.visuals = None
    if 'editing_section' not in st.session_state:
        st.session_state.editing_section = None
    if 'narration' not in st.session_state:
        st.session_state.narration = None
    if 'voice_overs' not in st.session_state:
        st.session_state.voice_overs = {}
    if 'errors' not in st.session_state:
        st.session_state.errors = []
    
    # Progress bar
    progress_text = {
        1: "Channel Information",
        2: "Script Generation",
        3: "Visual Elements",
        4: "Review & Edit",
        5: "Final Output"
    }
    st.progress((st.session_state.current_step - 1) / 4)
    st.markdown(f"**Step {st.session_state.current_step}/5: {progress_text[st.session_state.current_step]}**")
    
    # Display any errors
    if st.session_state.errors:
        for error in st.session_state.errors:
            st.error(error)
        st.session_state.errors = []
    
    # Step 1: Channel Information
    if st.session_state.current_step == 1:
        with st.expander("Channel Information", expanded=True):
            st.markdown("""
            ### 📝 Basic Information
            Let's start by gathering some basic information about your channel.
            This will help us create a trailer that perfectly represents your brand.
            """)
            
            channel_name = st.text_input("Channel Name", 
                                       value=st.session_state.channel_info.get('channel_name', ''),
                                       help="Enter your YouTube channel name")
            
            channel_niche = st.text_input("Channel Niche/Category", 
                                        value=st.session_state.channel_info.get('channel_niche', ''),
                                        help="e.g., Tech Reviews, Cooking, Gaming, etc.")
            
            st.markdown("### 👥 Target Audience")
            st.markdown("Describe who your content is for. Be specific about demographics, interests, and needs.")
            target_audience = st.text_area("Target Audience", 
                                         value=st.session_state.channel_info.get('target_audience', ''),
                                         help="Describe your target audience in detail")
            
            st.markdown("### 📚 Content Types")
            st.markdown("What kind of content do you create? List your main content types and topics.")
            key_topics = st.text_area("Key Topics/Content Types", 
                                    value=st.session_state.channel_info.get('key_topics', ''),
                                    help="List the main types of content you create")
            
            st.markdown("### ✨ Unique Selling Points")
            st.markdown("What makes your channel different? Highlight your unique features and value.")
            unique_points = st.text_area("Unique Selling Points", 
                                       value=st.session_state.channel_info.get('unique_points', ''),
                                       help="What makes your channel different?")
            
            col1, col2 = st.columns(2)
            with col1:
                trailer_length = st.selectbox(
                    "Trailer Length",
                    ["30 seconds", "60 seconds", "90 seconds"],
                    index=["30 seconds", "60 seconds", "90 seconds"].index(
                        st.session_state.channel_info.get('trailer_length', "60 seconds")
                    ),
                    help="Choose the desired length of your channel trailer"
                )
            with col2:
                brand_colors = st.color_picker(
                    "Brand Color",
                    value=st.session_state.channel_info.get('brand_colors', "#FF0000"),
                    help="Select your brand's primary color"
                )
            
            # Save channel info
            st.session_state.channel_info = {
                'channel_name': channel_name,
                'channel_niche': channel_niche,
                'target_audience': target_audience,
                'key_topics': key_topics,
                'unique_points': unique_points,
                'trailer_length': trailer_length,
                'brand_colors': brand_colors
            }
            
            if st.button("Next: Generate Script"):
                # Validate channel information
                is_valid, error_message = validate_channel_info(st.session_state.channel_info)
                if not is_valid:
                    st.session_state.errors.append(error_message)
                    st.rerun()
                else:
                    st.session_state.current_step = 2
                    st.rerun()
    
    # Step 2: Script Generation
    elif st.session_state.current_step == 2:
        st.markdown("### 📝 Script Generation")
        st.markdown("""
        We'll now generate a script for your channel trailer.
        The script will be divided into key sections, each with specific timing and visual suggestions.
        """)
        
        if st.button("Generate Script"):
            try:
                with st.spinner("Generating your channel trailer script..."):
                    script = generate_trailer_script(
                        channel_name=st.session_state.channel_info['channel_name'],
                        channel_niche=st.session_state.channel_info['channel_niche'],
                        target_audience=st.session_state.channel_info['target_audience'],
                        key_topics=st.session_state.channel_info['key_topics'],
                        unique_points=st.session_state.channel_info['unique_points'],
                        trailer_length=st.session_state.channel_info['trailer_length']
                    )
                    update_session_state('script', script)
                    
                    # Generate narration script
                    with st.spinner("Generating narration script..."):
                        narration = generate_narration_script(script)
                        update_session_state('narration', narration)
            except TrailerGeneratorError as e:
                st.session_state.errors.append(str(e))
                st.rerun()
        
        if st.session_state.script and st.session_state.narration:
            # Display script sections with edit buttons and voice-over options
            for section in ["hook", "introduction", "showcase", "value_proposition", "call_to_action"]:
                with st.expander(f"{section.replace('_', ' ').title()}", expanded=True):
                    st.markdown(f"**Duration:** {st.session_state.script[section]['duration']}")
                    st.markdown(f"**Text:** {st.session_state.script[section]['text']}")
                    
                    # Display narration details
                    st.markdown("### 🎤 Narration")
                    narration_section = st.session_state.narration['narration'][section]
                    st.markdown(f"**Voice Style:** {narration_section['voice_style']}")
                    st.markdown(f"**Emotion:** {narration_section['emotion']}")
                    st.markdown("**Emphasis Points:**")
                    for point in narration_section['emphasis']:
                        st.markdown(f"- {point}")
                    
                    # Voice-over generation with enhanced options
                    st.markdown("### 🎙️ Generate Voice-over")
                    voice_options = display_voice_over_options()
                    
                    if st.button(f"Generate Voice-over for {section.replace('_', ' ').title()}", 
                               key=f"voice_{section}"):
                        with st.spinner(f"Generating voice-over for {section}..."):
                            audio_bytes = generate_voice_over(
                                text=narration_section['text'],
                                language=voice_options['language'],
                                voice_style=voice_options['voice_style'],
                                slow=voice_options['pace'] in ['very_slow', 'slow']
                            )
                            if audio_bytes:
                                st.session_state.voice_overs[section] = {
                                    'audio': audio_bytes,
                                    'options': voice_options
                                }
                                st.markdown(get_audio_player_html(audio_bytes), unsafe_allow_html=True)
                    
                    # Display existing voice-over if available
                    if section in st.session_state.voice_overs:
                        st.markdown("### 🔊 Current Voice-over")
                        st.markdown(get_audio_player_html(st.session_state.voice_overs[section]['audio']), 
                                  unsafe_allow_html=True)
                        
                        # Show current voice-over settings
                        current_options = st.session_state.voice_overs[section]['options']
                        st.markdown("**Current Settings:**")
                        st.markdown(f"- Language: {VOICE_OPTIONS['languages'][current_options['language']]['name']}")
                        st.markdown(f"- Voice Style: {VOICE_OPTIONS['voice_styles'][current_options['voice_style']]['name']}")
                        st.markdown(f"- Pace: {current_options['pace'].replace('_', ' ').title()}")
                    
                    if st.button(f"Edit {section.replace('_', ' ').title()}", key=f"edit_{section}"):
                        st.session_state.editing_section = section
                        st.session_state.current_step = 4
                        st.rerun()
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Back to Channel Info"):
                    st.session_state.current_step = 1
                    st.rerun()
            with col2:
                if st.button("Next: Generate Visuals"):
                    st.session_state.current_step = 3
                    st.rerun()
    
    # Step 3: Visual Elements
    elif st.session_state.current_step == 3:
        st.markdown("### 🎨 Visual Elements")
        st.markdown("""
        Let's create the visual elements for your channel trailer.
        We'll generate a logo, background, and other visual assets that match your brand.
        """)
        
        if st.button("Generate Visuals"):
            with st.spinner("Generating visual elements..."):
                visuals = generate_trailer_visuals(
                    channel_name=st.session_state.channel_info['channel_name'],
                    channel_niche=st.session_state.channel_info['channel_niche'],
                    brand_color=st.session_state.channel_info['brand_colors']
                )
                st.session_state.visuals = visuals
                st.success("Visual elements generated successfully!")
        
        if st.session_state.visuals:
            for visual in st.session_state.visuals:
                with st.expander(f"{visual['type'].replace('_', ' ').title()}", expanded=True):
                    st.markdown(f"**Usage:** {visual['usage']}")
                    st.image(visual["image"], use_column_width=True)
                    if st.button(f"Regenerate {visual['type'].replace('_', ' ').title()}", 
                               key=f"regen_{visual['type']}"):
                        with st.spinner(f"Regenerating {visual['type']}..."):
                            new_visual = generate_trailer_visuals(
                                channel_name=st.session_state.channel_info['channel_name'],
                                channel_niche=st.session_state.channel_info['channel_niche'],
                                brand_color=st.session_state.channel_info['brand_colors']
                            )
                            st.session_state.visuals = new_visual
                            st.rerun()
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Back to Script"):
                    st.session_state.current_step = 2
                    st.rerun()
            with col2:
                if st.button("Next: Review & Edit"):
                    st.session_state.current_step = 4
                    st.rerun()
    
    # Step 4: Review & Edit
    elif st.session_state.current_step == 4:
        st.markdown("### ✍️ Review & Edit")
        
        if st.session_state.editing_section:
            st.markdown(f"### Editing {st.session_state.editing_section.replace('_', ' ').title()}")
            section = st.session_state.script[st.session_state.editing_section]
            narration_section = st.session_state.narration['narration'][st.session_state.editing_section]
            
            edited_text = st.text_area("Edit Text", value=section['text'])
            edited_duration = st.text_input("Edit Duration", value=section['duration'])
            
            st.markdown("### 🎤 Narration Settings")
            edited_narration = st.text_area("Edit Narration", value=narration_section['text'])
            edited_voice_style = st.text_input("Voice Style", value=narration_section['voice_style'])
            edited_emotion = st.text_input("Emotion", value=narration_section['emotion'])
            
            if st.button("Save Changes"):
                st.session_state.script[st.session_state.editing_section]['text'] = edited_text
                st.session_state.script[st.session_state.editing_section]['duration'] = edited_duration
                st.session_state.narration['narration'][st.session_state.editing_section]['text'] = edited_narration
                st.session_state.narration['narration'][st.session_state.editing_section]['voice_style'] = edited_voice_style
                st.session_state.narration['narration'][st.session_state.editing_section]['emotion'] = edited_emotion
                
                # Regenerate voice-over for the edited section
                if st.session_state.editing_section in st.session_state.voice_overs:
                    del st.session_state.voice_overs[st.session_state.editing_section]
                
                st.session_state.editing_section = None
                st.success("Changes saved successfully!")
                st.rerun()
            
            if st.button("Cancel Editing"):
                st.session_state.editing_section = None
                st.rerun()
        else:
            st.markdown("""
            Review your channel trailer content. You can:
            - Edit any section of the script
            - Regenerate visual elements
            - Download the final content
            """)
            
            # Display final preview
            display_trailer_content(st.session_state.script, st.session_state.visuals)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Back to Visuals"):
                    st.session_state.current_step = 3
                    st.rerun()
            with col2:
                if st.button("Finalize & Download"):
                    st.session_state.current_step = 5
                    st.rerun()
    
    # Step 5: Final Output
    elif st.session_state.current_step == 5:
        st.markdown("### 🎉 Final Output")
        st.success("Your channel trailer content is ready!")
        
        # Display final content
        display_trailer_content(st.session_state.script, st.session_state.visuals)
        
        # Display voice-over guidelines
        if st.session_state.narration:
            st.markdown("### 🎤 Voice-over Guidelines")
            guidelines = st.session_state.narration['voice_guidelines']
            st.markdown(f"**Overall Tone:** {guidelines['overall_tone']}")
            st.markdown(f"**Pace:** {guidelines['pace']}")
            st.markdown(f"**Energy Level:** {guidelines['energy_level']}")
            
            st.markdown("**Pronunciation Guide:**")
            for term, pronunciation in guidelines['pronunciation_guide'].items():
                st.markdown(f"- {term}: {pronunciation}")
            
            st.markdown("**Special Instructions:**")
            for instruction in guidelines['special_instructions']:
                st.markdown(f"- {instruction}")
        
        # Download options
        st.markdown("### 💾 Download Options")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("Download Script"):
                save_to_file(json.dumps(st.session_state.script, indent=2), "channel_trailer_script.json")
        with col2:
            if st.button("Download Narration"):
                save_to_file(json.dumps(st.session_state.narration, indent=2), "channel_trailer_narration.json")
        with col3:
            if st.button("Download Voice-overs"):
                # Save voice-overs logic here
                pass
        with col4:
            if st.button("Start New Trailer"):
                # Reset session state
                for key in ['current_step', 'channel_info', 'script', 'visuals', 'editing_section', 
                           'narration', 'voice_overs']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()

def generate_trailer_visuals(
    channel_name: str,
    channel_niche: str,
    brand_color: str
) -> List[Dict]:
    """Generate visual elements for the trailer."""
    
    # Generate channel logo concept
    logo_prompt = f"""Create a professional logo for a {channel_niche} YouTube channel named '{channel_name}'.
    Requirements:
    - Simple and memorable design
    - Works well in small sizes
    - Incorporates brand color: {brand_color}
    - Modern and clean style
    - Suitable for animation
    - Includes both icon and text elements
    - Maintains readability at different sizes
    """
    logo_image = generate_image(logo_prompt)
    
    # Generate background visuals
    background_prompt = f"""Create a dynamic background for a {channel_niche} YouTube channel trailer.
    Requirements:
    - Matches the channel's theme and niche
    - Incorporates brand color: {brand_color}
    - Includes subtle motion elements
    - Professional and modern design
    - Suitable for text overlay
    - Maintains visual hierarchy
    - Works well with channel branding
    """
    background_image = generate_image(background_prompt)
    
    # Generate thumbnail style previews
    thumbnail_prompt = f"""Create a professional thumbnail style for a {channel_niche} YouTube channel.
    Requirements:
    - Eye-catching design
    - Incorporates brand color: {brand_color}
    - Includes space for text
    - High contrast for visibility
    - Modern and clean style
    - Suitable for content preview
    """
    thumbnail_image = generate_image(thumbnail_prompt)
    
    # Generate motion graphic elements
    motion_prompt = f"""Create a set of motion graphic elements for a {channel_niche} YouTube channel.
    Requirements:
    - Modern and dynamic design
    - Incorporates brand color: {brand_color}
    - Suitable for transitions
    - Clean and professional style
    - Works well with channel branding
    """
    motion_image = generate_image(motion_prompt)
    
    return [
        {
            "type": "logo",
            "prompt": logo_prompt,
            "image": logo_image,
            "usage": "Channel branding and identification"
        },
        {
            "type": "background",
            "prompt": background_prompt,
            "image": background_image,
            "usage": "Main background and scene setting"
        },
        {
            "type": "thumbnail",
            "prompt": thumbnail_prompt,
            "image": thumbnail_image,
            "usage": "Content preview and showcase"
        },
        {
            "type": "motion_graphics",
            "prompt": motion_prompt,
            "image": motion_image,
            "usage": "Transitions and visual effects"
        }
    ]

def display_trailer_content(script: Dict, visuals: List[Dict]):
    """Display the generated trailer content."""
    
    # Display script
    st.markdown("### 📝 Trailer Script")
    
    # Create tabs for different sections
    script_tab, visuals_tab, production_tab = st.tabs(["Script", "Visuals", "Production Notes"])
    
    with script_tab:
        for section in ["hook", "introduction", "showcase", "value_proposition", "call_to_action"]:
            if section in script:
                st.markdown(f"#### {section.replace('_', ' ').title()}")
                st.markdown(f"**Duration:** {script[section]['duration']}")
                st.markdown(f"**Text:** {script[section]['text']}")
                
                # Display visual suggestions in an organized way
                st.markdown("**Visual Elements:**")
                visual_suggestions = script[section]['visual_suggestions']
                for key, value in visual_suggestions.items():
                    if isinstance(value, list):
                        st.markdown(f"**{key.replace('_', ' ').title()}:**")
                        for item in value:
                            st.markdown(f"- {item}")
                    else:
                        st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")
                st.markdown("---")
    
    with visuals_tab:
        st.markdown("### 🎨 Visual Elements")
        for visual in visuals:
            st.markdown(f"#### {visual['type'].replace('_', ' ').title()}")
            st.markdown(f"**Usage:** {visual['usage']}")
            st.image(visual["image"], use_column_width=True)
            st.markdown("---")
    
    with production_tab:
        if "notes" in script:
            st.markdown("### 📋 Production Notes")
            notes = script["notes"]
            
            st.markdown("#### 🎭 Tone and Style")
            st.write(notes["tone"])
            
            st.markdown("#### 🎵 Music Suggestions")
            for music in notes["music_suggestions"]:
                st.markdown(f"- {music}")
            
            st.markdown("#### 🔄 Transitions")
            for transition in notes["transitions"]:
                st.markdown(f"- {transition}")
            
            st.markdown("#### ✨ Special Effects")
            for effect in notes["special_effects"]:
                st.markdown(f"- {effect}")
            
            st.markdown("#### 💡 Production Tips")
            for tip in notes["production_tips"]:
                st.markdown(f"- {tip}")
            
            st.markdown("#### 🎨 Visual Consistency")
            st.write(notes["visual_consistency"])
            
            st.markdown("#### 📝 Brand Guidelines")
            st.write(notes["brand_guidelines"])
    
    # Add download options
    st.markdown("### 💾 Download Options")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Download Script"):
            save_to_file(json.dumps(script, indent=2), "channel_trailer_script.json")
    with col2:
        if st.button("Download Visuals"):
            # Save visuals logic here
            pass

def get_audio_player_html(audio_bytes: bytes) -> str:
    """Generate HTML for audio player with the given audio bytes."""
    b64 = base64.b64encode(audio_bytes).decode()
    return f"""
        <audio controls style="width: 100%;">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            Your browser does not support the audio element.
        </audio>
    """

if __name__ == "__main__":
    try:
        write_yt_channel_trailer()
    except Exception as e:
        logger.error(f"Unexpected error in trailer generator: {str(e)}")
        st.error("An unexpected error occurred. Please try again or contact support.") 