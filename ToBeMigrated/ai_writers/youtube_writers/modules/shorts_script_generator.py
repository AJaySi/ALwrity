"""
YouTube Shorts Script Generator Module

This module provides functionality for generating optimized scripts for YouTube Shorts.
"""

import streamlit as st
import time
import logging
from lib.gpt_providers.text_generation.main_text_generation import llm_text_gen

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('youtube_shorts_generator')

def generate_shorts_script(hook_type, main_topic, target_audience, tone_style, 
                         content_type, duration_seconds=60, include_captions=True,
                         include_text_overlay=True, include_sound_effects=False,
                         vertical_framing_notes=True, language="English"):
    """Generate a YouTube Shorts script optimized for vertical format and short duration."""
    
    # Create a custom system prompt for Shorts script generation
    system_prompt = f"""You are a YouTube Shorts expert specializing in creating viral, engaging scripts for vertical short-form videos.
    Your task is to generate scripts that are perfectly timed for {duration_seconds} seconds or less.
    Focus on hooks that grab attention in the first 1-2 seconds.
    Format the script with clear sections for visuals, audio, and text overlays.
    Write the entire script in {language}.
    Remember that Shorts are viewed vertically (9:16 aspect ratio) and need to work without sound."""
    
    # Build hook-specific instructions
    hook_instructions = {
        "Question": "Start with an intriguing question that stops the scroll",
        "Statistic": "Begin with a surprising statistic or fact",
        "Challenge": "Present a challenge or dare to the viewer",
        "Tutorial": "Jump straight into a quick how-to or life hack",
        "Transformation": "Show a before/after or transformation hook",
        "Trend": "Leverage a current trend or sound",
        "Story": "Start with a captivating micro-story",
        "Controversy": "Present a controversial or surprising statement"
    }
    
    # Build the prompt
    prompt = f"""
    **Instructions:**

    Create a YouTube Shorts script about **{main_topic}** with these specifications:

    **Core Elements:**
    - Hook Type: {hook_type} - {hook_instructions.get(hook_type, "Create an attention-grabbing opening")}
    - Target Audience: {target_audience}
    - Tone/Style: {tone_style}
    - Content Type: {content_type}
    - Duration: {duration_seconds} seconds
    - Language: {language}

    **Required Elements:**
    {"- Include caption suggestions for accessibility" if include_captions else ""}
    {"- Include text overlay positions and timing" if include_text_overlay else ""}
    {"- Include sound effect suggestions" if include_sound_effects else ""}
    {"- Include vertical framing notes for optimal composition" if vertical_framing_notes else ""}

    **Format the script in this structure:**
    1. HOOK (0-2 seconds)
    2. MAIN CONTENT (3-50 seconds)
    3. CALL TO ACTION (last 10 seconds)

    **For each section, specify:**
    - Visual Instructions (what to show)
    - Text Overlays (what text appears and where)
    - Audio/Voiceover
    - Timing (in seconds)
    - Camera Angles/Framing Notes

    **Remember:**
    - Scripts must work without sound (many viewers watch on mute)
    - Text should be centered in the middle 50% of the vertical frame
    - Keep text concise and readable
    - Include pattern interrupts every 3-5 seconds
    - End with a clear call-to-action
    """
    
    try:
        response = llm_text_gen(prompt, system_prompt=system_prompt)
        return response
    except Exception as err:
        st.error(f"Error: Failed to get response from LLM: {err}")
        return None

def analyze_shorts_script(script):
    """Analyze a Shorts script for optimal engagement metrics."""
    analysis = {
        'duration_estimate': 0,
        'hook_strength': 0,
        'pattern_interrupts': 0,
        'text_overlay_count': 0,
        'readability_score': 0,
        'optimization_score': 0
    }
    
    # Basic analysis (can be enhanced with more sophisticated metrics)
    lines = script.split('\n')
    word_count = len(script.split())
    
    # Estimate duration (rough approximation)
    analysis['duration_estimate'] = word_count * 0.4  # Average speaking speed
    
    # Count pattern interrupts
    analysis['pattern_interrupts'] = script.lower().count('cut to') + script.lower().count('transition')
    
    # Count text overlays
    analysis['text_overlay_count'] = script.lower().count('text:') + script.lower().count('overlay:')
    
    # Calculate optimization score
    score = 100
    
    # Penalize if estimated duration is too long
    if analysis['duration_estimate'] > 60:
        score -= (analysis['duration_estimate'] - 60) * 2
    
    # Check for hook presence
    if not any(hook in script.lower() for hook in ['hook:', 'opening:', '0-2 seconds:']):
        score -= 20
    
    # Check for pattern interrupts (ideal is 1 every 5 seconds)
    ideal_interrupts = analysis['duration_estimate'] / 5
    if analysis['pattern_interrupts'] < ideal_interrupts:
        score -= 10
    
    # Check for text overlay usage
    if analysis['text_overlay_count'] < 3:
        score -= 10
    
    # Check for call-to-action
    if not any(cta in script.lower() for cta in ['call to action', 'cta:', 'subscribe', 'follow']):
        score -= 15
    
    analysis['optimization_score'] = max(0, score)
    return analysis

def generate_shorts_narration(shorts_script, language="English"):
    system_prompt = f"""You are an expert at converting YouTube Shorts scripts into natural, engaging narration.\nYour task is to read the provided Shorts script and output only the narration lines, as they would be spoken in the video.\nOmit all visual instructions, timing, text overlays, and technical cues. Write the narration in {language}."""
    prompt = f"""Shorts Script:\n{shorts_script}\n\nInstructions:\nExtract and rewrite only the narration lines, as they would be spoken in the video. Do not include any section headers, cues, or formatting. Output only the narration text."""
    try:
        response = llm_text_gen(prompt, system_prompt=system_prompt)
        return response.strip()
    except Exception as err:
        st.error(f"Error: Failed to get narration from LLM: {err}")
        return ""

def write_yt_shorts():
    """Create a user interface for YouTube Shorts Script Generator."""
    st.write("Generate optimized scripts for YouTube Shorts that grab attention and drive engagement.")
    
    # Initialize session state for generated script and active tab if they don't exist
    if "generated_shorts_script" not in st.session_state:
        st.session_state.generated_shorts_script = None
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = "Core Elements"
    
    # Create tabs for different sections
    tab1, tab2, tab3 = st.tabs(["Core Elements", "Style & Format", "Preview & Export"])
    
    # Set the active tab based on session state
    if st.session_state.active_tab == "Core Elements":
        tab1.active = True
    elif st.session_state.active_tab == "Style & Format":
        tab2.active = True
    elif st.session_state.active_tab == "Preview & Export":
        tab3.active = True
    
    with tab1:
        # Core elements
        main_topic = st.text_area("Main Topic/Concept", 
                                placeholder="e.g., Quick cooking hack, Life-changing productivity tip")
        
        col1, col2 = st.columns(2)
        with col1:
            hook_type = st.selectbox("Hook Type", [
                "Question",
                "Statistic",
                "Challenge",
                "Tutorial",
                "Transformation",
                "Trend",
                "Story",
                "Controversy"
            ])
            
            target_audience = st.text_input("Target Audience", 
                                          placeholder="e.g., Gen Z, busy professionals")
        
        with col2:
            content_type = st.selectbox("Content Type", [
                "Tutorial/How-to",
                "Life Hack",
                "Entertainment",
                "Educational",
                "Trend",
                "Story",
                "Challenge",
                "Review"
            ])
            
            tone_style = st.selectbox("Tone/Style", [
                "Energetic",
                "Professional",
                "Casual",
                "Humorous",
                "Dramatic",
                "Inspirational"
            ])
    
    with tab2:
        # Style and format options
        col1, col2 = st.columns(2)
        
        with col1:
            duration_seconds = st.slider("Duration (seconds)", 15, 60, 60)
            language = st.selectbox("Language", [
                "English",
                "Spanish",
                "French",
                "German",
                "Italian",
                "Portuguese",
                "Russian",
                "Japanese",
                "Korean",
                "Chinese"
            ])
        
        with col2:
            include_captions = st.checkbox("Include Captions", value=True)
            include_text_overlay = st.checkbox("Include Text Overlay Positions", value=True)
            include_sound_effects = st.checkbox("Include Sound Effects", value=False)
            vertical_framing_notes = st.checkbox("Include Vertical Framing Notes", value=True)
    
    with tab3:
        if st.session_state.generated_shorts_script:
            # Display the generated script
            st.subheader("Generated Shorts Script")
            
            # Create tabs for different views
            script_tab1, script_tab2, script_tab3 = st.tabs(["Formatted", "Analysis", "Export"])
            
            with script_tab1:
                st.markdown(st.session_state.generated_shorts_script)
            
            with script_tab2:
                # Analyze the script
                analysis = analyze_shorts_script(st.session_state.generated_shorts_script)
                
                # Display analysis results
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Estimated Duration", f"{analysis['duration_estimate']:.1f}s")
                    st.metric("Pattern Interrupts", analysis['pattern_interrupts'])
                    st.metric("Text Overlays", analysis['text_overlay_count'])
                
                with col2:
                    # Display optimization score with color
                    score = analysis['optimization_score']
                    color = "red" if score < 60 else "orange" if score < 80 else "green"
                    st.markdown(f"### Optimization Score: <span style='color: {color}'>{score}%</span>", 
                              unsafe_allow_html=True)
            
            with script_tab3:
                # Export options
                export_format = st.selectbox("Export Format", [
                    "Text",
                    "Markdown",
                    "Shot List",
                    "Storyboard"
                ])
                
                if st.button("Export Script"):
                    # Implement export functionality based on selected format
                    st.success(f"Script exported in {export_format} format!")
                    st.download_button(
                        "Download Script",
                        st.session_state.generated_shorts_script,
                        file_name=f"shorts_script.{export_format.lower()}",
                        mime="text/plain"
                    )
    
    # Generate button
    if st.button("Generate Shorts Script"):
        if not main_topic:
            st.error("Please enter a main topic/concept.")
            return
        
        with st.spinner("Generating Shorts script..."):
            script = generate_shorts_script(
                hook_type, main_topic, target_audience, tone_style, content_type,
                duration_seconds, include_captions, include_text_overlay,
                include_sound_effects, vertical_framing_notes, language
            )
            
            if script:
                st.session_state.generated_shorts_script = script
                # Set active tab to Preview & Export
                st.session_state.active_tab = "Preview & Export"
                st.success("✨ Script generated successfully! Check the 'Preview & Export' tab to view, analyze, and download your script.")
                st.rerun()
            else:
                st.error("Failed to generate script. Please try again.")
    
    # Add a message about preview and export if script exists but we're not on the Preview tab
    if st.session_state.generated_shorts_script and st.session_state.active_tab != "Preview & Export":
        st.info("💡 Your generated script is ready! Go to the 'Preview & Export' tab to view, analyze, and download it.") 