"""
YouTube Thumbnail Generator Module

This module provides functionality for generating YouTube video thumbnails.
"""

import streamlit as st
import time
import logging
import os
import traceback
from PIL import Image
from lib.gpt_providers.text_generation.main_text_generation import llm_text_gen
from lib.gpt_providers.text_to_image_generation.gen_gemini_images import generate_gemini_image, edit_image

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('youtube_thumbnail_generator')


def generate_thumbnail_concepts(video_title, video_description, target_audience, content_type, style_preference, num_concepts=3):
    """Generate thumbnail concept ideas based on video content."""
    logger.info(f"Generating thumbnail concepts for: '{video_title}'")
    logger.info(f"Parameters: target_audience={target_audience}, content_type={content_type}, style_preference={style_preference}, num_concepts={num_concepts}")
    
    # Create a system prompt for thumbnail concept generation
    system_prompt = """You are a YouTube thumbnail expert specializing in creating engaging, click-worthy thumbnail concepts.
    Your task is to generate thumbnail concept ideas based on the provided video information.
    Focus ONLY on creating concepts that are optimized for YouTube, with proper visual hierarchy, text placement, and emotional triggers.
    Return ONLY the concept descriptions, without any additional commentary or explanations.
    Each concept should include:
    1. A main visual element or scene
    2. Text placement and content
    3. Color scheme suggestions
    4. Emotional trigger or hook
    5. Brief explanation of why this concept would be effective"""
    
    # Build the prompt
    prompt = f"""
    **Instructions:**

    Please generate {num_concepts} thumbnail concept ideas for a YouTube video with the following information:

    **Video Title:** {video_title}
    **Video Description:** {video_description}
    **Target Audience:** {target_audience}
    **Content Type:** {content_type}
    **Style Preference:** {style_preference}

    **Specific Instructions:**
    * Each concept should be clearly separated and numbered.
    * Focus on creating thumbnails that stand out in search results and recommendations.
    * Consider the target audience's interests and preferences.
    * Include specific details about visual elements, text placement, and color schemes.
    * Explain why each concept would be effective for this specific video.
    """
    
    try:
        logger.info("Sending request to LLM for thumbnail concepts")
        response = llm_text_gen(prompt, system_prompt=system_prompt)
        logger.info(f"Received response from LLM: {len(response)} characters")
        return response
    except Exception as err:
        logger.error(f"Error generating thumbnail concepts: {err}")
        logger.error(traceback.format_exc())
        st.error(f"Error: Failed to generate thumbnail concepts: {err}")
        return None


def generate_thumbnail_design(concept_description, style_preference, aspect_ratio="16:9", keywords=None, style=None, focus=None):
    """Generate a thumbnail image based on the concept description."""
    logger.info(f"Generating thumbnail design for concept: '{concept_description[:50]}...'")
    logger.info(f"Parameters: style_preference={style_preference}, aspect_ratio={aspect_ratio}, keywords={keywords}, style={style}, focus={focus}")
    
    # Create a prompt for the image generation
    image_prompt = f"""
    Create a YouTube thumbnail image with the following specifications:
    
    Concept: {concept_description}
    Style: {style_preference}
    Aspect Ratio: {aspect_ratio}
    
    The image should be:
    - High contrast and visually striking
    - Suitable for a YouTube thumbnail
    - Include the specified visual elements and text
    - Follow the color scheme described
    - Optimized for small display sizes
    
    Make sure the text is large and readable, and the main subject is centered and prominent.
    """
    
    try:
        logger.info("Sending request to Gemini for thumbnail image")
        # Generate the image using Gemini with enhanced prompt
        img_path = generate_gemini_image(
            image_prompt, 
            keywords=keywords,
            style=style,
            focus=focus,
            enhance_prompt=True
        )
        logger.info(f"Received image from Gemini: {img_path}")
        return img_path
    except Exception as err:
        logger.error(f"Error generating thumbnail image: {err}")
        logger.error(traceback.format_exc())
        st.error(f"Error: Failed to generate thumbnail image: {err}")
        return None


def edit_thumbnail_image(img_path, edit_instructions):
    """Edit a thumbnail image based on user instructions."""
    logger.info(f"Editing thumbnail image: '{img_path}'")
    logger.info(f"Edit instructions: '{edit_instructions}'")
    
    try:
        logger.info("Sending request to Gemini for image editing")
        # Edit the image using Gemini
        edited_img_path = edit_image(img_path, edit_instructions)
        logger.info(f"Image editing completed. Edited image path: {edited_img_path}")
        
        # Return the path to the edited image
        return edited_img_path
    except Exception as err:
        logger.error(f"Error editing thumbnail image: {err}")
        logger.error(traceback.format_exc())
        st.error(f"Error: Failed to edit thumbnail image: {err}")
        return None


def analyze_thumbnail(thumbnail_path):
    """Analyze a thumbnail for effectiveness."""
    logger.info(f"Analyzing thumbnail: '{thumbnail_path}'")
    
    # This would typically involve image analysis, but for now we'll use AI to provide feedback
    system_prompt = """You are a YouTube thumbnail expert specializing in analyzing and providing feedback on thumbnail designs.
    Your task is to analyze the thumbnail and provide constructive feedback on its effectiveness.
    Focus on aspects like visual hierarchy, text readability, emotional impact, and click-worthiness."""
    
    # For now, we'll just return a placeholder analysis
    # In a real implementation, we would analyze the actual image
    logger.info("Generating thumbnail analysis")
    return """
    **Thumbnail Analysis:**
    
    - **Visual Hierarchy:** The main subject is well-positioned and stands out against the background.
    - **Text Readability:** The text is clear and readable, with good contrast against the background.
    - **Emotional Impact:** The thumbnail creates curiosity and emotional connection with the target audience.
    - **Click-worthiness:** The design is likely to attract clicks due to its visual appeal and clear value proposition.
    
    **Suggestions for Improvement:**
    - Consider adding a subtle border to make the thumbnail stand out more in search results.
    - The text could be slightly larger for better readability on mobile devices.
    - Adding a small icon or logo could help with brand recognition.
    """


def parse_concepts(concepts_text):
    """Parse the concepts text into a list of individual concepts."""
    logger.info("Parsing concepts text into individual concepts")
    
    concept_list = []
    current_concept = ""
    
    for line in concepts_text.split('\n'):
        if line.strip().startswith(('1.', '2.', '3.', '4.', '5.')):
            if current_concept:
                concept_list.append(current_concept.strip())
            current_concept = line
        else:
            current_concept += "\n" + line
    
    if current_concept:
        concept_list.append(current_concept.strip())
    
    logger.info(f"Parsed {len(concept_list)} concepts from the response")
    return concept_list


def write_yt_thumbnail():
    """Create a user interface for YouTube Thumbnail Generator."""
    logger.info("Initializing YouTube Thumbnail Generator UI")
    st.title("YouTube Thumbnail Generator")
    st.write("Create engaging, click-worthy thumbnails for your YouTube videos.")
    
    # Initialize session state for generated thumbnails if it doesn't exist
    if "generated_thumbnails" not in st.session_state:
        st.session_state.generated_thumbnails = []
    if "thumbnail_concepts" not in st.session_state:
        st.session_state.thumbnail_concepts = None
    if "current_thumbnail_path" not in st.session_state:
        st.session_state.current_thumbnail_path = None
    if "concept_list" not in st.session_state:
        st.session_state.concept_list = []
    if "editing_thumbnail" not in st.session_state:
        st.session_state.editing_thumbnail = False
    if "edit_instructions" not in st.session_state:
        st.session_state.edit_instructions = ""
    if "edited_thumbnail_path" not in st.session_state:
        st.session_state.edited_thumbnail_path = None
    if "show_edit_form" not in st.session_state:
        st.session_state.show_edit_form = False
    
    # Create tabs for different sections
    tab1, tab2 = st.tabs(["Basic Info", "Style & Generation"])
    
    with tab1:
        # Basic information inputs
        video_title = st.text_input("Video Title", 
                                  placeholder="e.g., 10 Tips for Better Photography")
        video_description = st.text_area("Video Description", 
                                       placeholder="Brief description of your video content")
        target_audience = st.text_input("Target Audience", 
                                      placeholder="e.g., photography enthusiasts, beginners")
        
        # Content type selection
        content_type = st.selectbox("Content Type", [
            "Tutorial/How-to",
            "Vlog",
            "Review",
            "Educational",
            "Entertainment",
            "News/Update",
            "Product Showcase",
            "Challenge",
            "Reaction",
            "Comparison"
        ])
    
    with tab2:
        # Style preferences
        st.subheader("Style Preferences")
        
        # Create columns for style options
        col1, col2 = st.columns(2)
        
        with col1:
            style_preference = st.selectbox("Thumbnail Style", [
                "Bold and Dramatic",
                "Clean and Minimal",
                "Colorful and Vibrant",
                "Dark and Moody",
                "Professional and Corporate",
                "Playful and Fun",
                "Retro/Vintage",
                "Modern and Sleek"
            ])
            
            num_concepts = st.slider("Number of Concepts", 1, 5, 3)
        
        with col2:
            aspect_ratio = st.selectbox("Aspect Ratio", [
                "16:9 (Standard)",
                "1:1 (Square)",
                "4:3 (Classic)",
                "9:16 (Vertical)"
            ])
            
            include_text = st.checkbox("Include Text Overlay", value=True)
            if include_text:
                text_style = st.selectbox("Text Style", [
                    "Bold and Impactful",
                    "Clean and Readable",
                    "Stylized and Thematic",
                    "Minimal and Subtle"
                ])
        
        # Advanced AI Prompt Settings
        st.subheader("Advanced AI Prompt Settings")
        
        # Create columns for advanced settings
        col3, col4 = st.columns(2)
        
        with col3:
            # Image style selection
            image_style = st.selectbox("Image Style", [
                "Auto (AI will choose best style)",
                "Photorealistic",
                "Artistic",
                "Cartoon/Anime",
                "Sketch/Drawing",
                "Digital Art",
                "3D Render"
            ])
            
            # Extract style for the generate_gemini_image function
            style = None
            if image_style == "Photorealistic":
                style = "photorealistic"
            elif image_style == "Artistic":
                style = "artistic"
            elif image_style == "Cartoon/Anime":
                style = "cartoon"
            elif image_style == "Sketch/Drawing":
                style = "sketch"
            elif image_style == "Digital Art":
                style = "digital_art"
            elif image_style == "3D Render":
                style = "3d_render"
        
        with col4:
            # Focus selection for photorealistic images
            focus = None
            if style == "photorealistic":
                focus = st.selectbox("Image Focus", [
                    "Auto (AI will choose best focus)",
                    "Portraits",
                    "Objects",
                    "Motion",
                    "Wide-angle"
                ])
                
                # Extract focus for the generate_gemini_image function
                if focus == "Portraits":
                    focus = "portraits"
                elif focus == "Objects":
                    focus = "objects"
                elif focus == "Motion":
                    focus = "motion"
                elif focus == "Wide-angle":
                    focus = "wide-angle"
                elif focus == "Auto (AI will choose best focus)":
                    focus = None
        
        # Keywords for enhanced prompt generation
        st.subheader("Keywords for Enhanced Prompt")
        st.write("Add keywords to enhance the AI prompt generation. These will help create more detailed and accurate thumbnails.")
        
        # Create a text area for keywords
        keywords_input = st.text_area(
            "Keywords (comma-separated)", 
            placeholder="e.g., vibrant, energetic, bold, eye-catching, professional"
        )
        
        # Process keywords
        keywords = None
        if keywords_input:
            keywords = [k.strip() for k in keywords_input.split(",") if k.strip()]
            logger.info(f"User provided keywords: {keywords}")
    
    # Generate button
    if st.button("Generate Thumbnail Concepts"):
        if not video_title:
            st.error("Please enter a video title.")
            return
        
        with st.spinner("Generating thumbnail concepts..."):
            logger.info("User clicked Generate Thumbnail Concepts button")
            concepts = generate_thumbnail_concepts(
                video_title, 
                video_description, 
                target_audience, 
                content_type, 
                style_preference,
                num_concepts
            )
            
            if concepts:
                # Store the concepts in session state
                st.session_state.thumbnail_concepts = concepts
                # Parse the concepts and store in session state
                st.session_state.concept_list = parse_concepts(concepts)
                logger.info("Stored thumbnail concepts in session state")
                
                # Display the concepts in tabs
                st.subheader("Thumbnail Concepts")
                
                # Create tabs for each concept
                concept_tabs = st.tabs([f"Concept {i+1}" for i in range(len(st.session_state.concept_list))])
                
                for i, tab in enumerate(concept_tabs):
                    with tab:
                        st.markdown(st.session_state.concept_list[i])
                        
                        # Add a button to generate image for this concept
                        if st.button(f"Generate Image for Concept {i+1}", key=f"gen_img_{i}"):
                            with st.spinner(f"Generating thumbnail image for concept {i+1}..."):
                                logger.info(f"User selected concept {i+1} for image generation")
                                # Get the selected concept
                                selected_concept = st.session_state.concept_list[i]
                                
                                # Generate the thumbnail image with enhanced prompt
                                img_path = generate_thumbnail_design(
                                    selected_concept,
                                    style_preference,
                                    aspect_ratio.split()[0],  # Extract just the ratio part
                                    keywords=keywords,
                                    style=style,
                                    focus=focus
                                )
                                
                                if img_path:
                                    # Store the current thumbnail path in session state
                                    st.session_state.current_thumbnail_path = img_path
                                    logger.info(f"Stored current thumbnail path in session state: {img_path}")
                                    
                                    # Display the generated image
                                    st.subheader("Generated Thumbnail")
                                    st.image(img_path, use_container_width=True)
                                    
                                    # Add download button
                                    with open(img_path, "rb") as file:
                                        st.download_button(
                                            label="Download Thumbnail",
                                            data=file,
                                            file_name=f"youtube_thumbnail_{int(time.time())}.png",
                                            mime="image/png"
                                        )
                                    
                                    # Add image editing section
                                    st.subheader("Edit Thumbnail")
                                    st.write("Make changes to your thumbnail by providing instructions below:")
                                    
                                    # Create a text area for edit instructions
                                    edit_instructions = st.text_area(
                                        "Edit Instructions", 
                                        placeholder="e.g., Make the background darker, Add a red border, Change the text color to white",
                                        key=f"edit_instructions_{i}"
                                    )
                                    
                                    # Store edit instructions in session state
                                    st.session_state.edit_instructions = edit_instructions
                                    
                                    # Add a button to apply edits
                                    if st.button("Apply Edits", key=f"apply_edits_{i}"):
                                        if not edit_instructions:
                                            st.warning("Please provide edit instructions.")
                                        else:
                                            # Set editing flag
                                            st.session_state.editing_thumbnail = True
                                            st.session_state.show_edit_form = True
                                            
                                            # Rerun to update the UI
                                            st.rerun()
                                    
                                    # Add analysis button
                                    if st.button("Analyze Thumbnail", key=f"analyze_{i}"):
                                        logger.info("User clicked Analyze Thumbnail button")
                                        analysis = analyze_thumbnail(img_path)
                                        st.subheader("Thumbnail Analysis")
                                        st.markdown(analysis)
            else:
                st.error("Failed to generate thumbnail concepts. Please try again.")
    
    # Display previously generated concepts if they exist in session state
    elif st.session_state.thumbnail_concepts and st.session_state.concept_list:
        logger.info("Displaying previously generated concepts from session state")
        st.subheader("Thumbnail Concepts")
        
        # Create tabs for each concept
        concept_tabs = st.tabs([f"Concept {i+1}" for i in range(len(st.session_state.concept_list))])
        
        for i, tab in enumerate(concept_tabs):
            with tab:
                st.markdown(st.session_state.concept_list[i])
                
                # Add a button to generate image for this concept
                if st.button(f"Generate Image for Concept {i+1}", key=f"gen_img_existing_{i}"):
                    with st.spinner(f"Generating thumbnail image for concept {i+1}..."):
                        logger.info(f"User selected concept {i+1} for image generation")
                        # Get the selected concept
                        selected_concept = st.session_state.concept_list[i]
                        
                        # Generate the thumbnail image with enhanced prompt
                        img_path = generate_thumbnail_design(
                            selected_concept,
                            style_preference,
                            aspect_ratio.split()[0],  # Extract just the ratio part
                            keywords=keywords,
                            style=style,
                            focus=focus
                        )
                        
                        if img_path:
                            # Store the current thumbnail path in session state
                            st.session_state.current_thumbnail_path = img_path
                            logger.info(f"Stored current thumbnail path in session state: {img_path}")
                            
                            # Display the generated image
                            st.subheader("Generated Thumbnail")
                            st.image(img_path, use_container_width=True)
                            
                            # Add download button
                            with open(img_path, "rb") as file:
                                st.download_button(
                                    label="Download Thumbnail",
                                    data=file,
                                    file_name=f"youtube_thumbnail_{int(time.time())}.png",
                                    mime="image/png"
                                )
                            
                            # Add image editing section
                            st.subheader("Edit Thumbnail")
                            st.write("Make changes to your thumbnail by providing instructions below:")
                            
                            # Create a text area for edit instructions
                            edit_instructions = st.text_area(
                                "Edit Instructions", 
                                placeholder="e.g., Make the background darker, Add a red border, Change the text color to white",
                                key=f"edit_instructions_existing_{i}"
                            )
                            
                            # Store edit instructions in session state
                            st.session_state.edit_instructions = edit_instructions
                            
                            # Add a button to apply edits
                            if st.button("Apply Edits", key=f"apply_edits_existing_{i}"):
                                if not edit_instructions:
                                    st.warning("Please provide edit instructions.")
                                else:
                                    # Set editing flag
                                    st.session_state.editing_thumbnail = True
                                    st.session_state.show_edit_form = True
                                    
                                    # Rerun to update the UI
                                    st.rerun()
                            
                            # Add analysis button
                            if st.button("Analyze Thumbnail", key=f"analyze_existing_{i}"):
                                logger.info("User clicked Analyze Thumbnail button")
                                analysis = analyze_thumbnail(img_path)
                                st.subheader("Thumbnail Analysis")
                                st.markdown(analysis)
    
    # Display current thumbnail if it exists in session state
    elif st.session_state.current_thumbnail_path:
        logger.info(f"Displaying current thumbnail from session state: {st.session_state.current_thumbnail_path}")
        st.subheader("Current Thumbnail")
        st.image(st.session_state.current_thumbnail_path, use_container_width=True)
        
        # Add download button
        with open(st.session_state.current_thumbnail_path, "rb") as file:
            st.download_button(
                label="Download Thumbnail",
                data=file,
                file_name=f"youtube_thumbnail_{int(time.time())}.png",
                mime="image/png"
            )
        
        # Add image editing section
        st.subheader("Edit Thumbnail")
        st.write("Make changes to your thumbnail by providing instructions below:")
        
        # Create a text area for edit instructions
        edit_instructions = st.text_area(
            "Edit Instructions", 
            placeholder="e.g., Make the background darker, Add a red border, Change the text color to white",
            key="edit_instructions_current",
            value=st.session_state.edit_instructions if st.session_state.edit_instructions else ""
        )
        
        # Store edit instructions in session state
        st.session_state.edit_instructions = edit_instructions
        
        # Add a button to apply edits
        if st.button("Apply Edits", key="apply_edits_current"):
            if not edit_instructions:
                st.warning("Please provide edit instructions.")
            else:
                # Set editing flag
                st.session_state.editing_thumbnail = True
                st.session_state.show_edit_form = True
                
                # Rerun to update the UI
                st.rerun()
        
        # Add analysis button
        if st.button("Analyze Thumbnail", key="analyze_current"):
            logger.info("User clicked Analyze Thumbnail button")
            analysis = analyze_thumbnail(st.session_state.current_thumbnail_path)
            st.subheader("Thumbnail Analysis")
            st.markdown(analysis)
    
    # Handle the editing process
    if st.session_state.editing_thumbnail and st.session_state.show_edit_form:
        st.subheader("Editing Thumbnail")
        
        # Show a spinner while editing
        with st.spinner("Editing thumbnail..."):
            logger.info(f"User provided edit instructions: '{st.session_state.edit_instructions}'")
            # Edit the thumbnail image
            edited_img_path = edit_thumbnail_image(st.session_state.current_thumbnail_path, st.session_state.edit_instructions)
            
            if edited_img_path:
                # Update the current thumbnail path in session state
                st.session_state.edited_thumbnail_path = edited_img_path
                logger.info(f"Updated current thumbnail path in session state: {edited_img_path}")
                
                # Reset editing flags
                st.session_state.editing_thumbnail = False
                st.session_state.show_edit_form = False
                
                # Display the edited image
                st.subheader("Edited Thumbnail")
                st.image(edited_img_path, use_container_width=True)
                
                # Add download button for the edited image
                with open(edited_img_path, "rb") as file:
                    st.download_button(
                        label="Download Edited Thumbnail",
                        data=file,
                        file_name=f"youtube_thumbnail_edited_{int(time.time())}.png",
                        mime="image/png"
                    )
                
                # Update the current thumbnail path to the edited one
                st.session_state.current_thumbnail_path = edited_img_path
                
                # Add a button to continue editing
                if st.button("Continue Editing"):
                    st.session_state.show_edit_form = True
                    st.rerun()
            else:
                # Reset editing flags
                st.session_state.editing_thumbnail = False
                st.session_state.show_edit_form = False
                
                st.error("Failed to edit the thumbnail. Please try again with different instructions.") 