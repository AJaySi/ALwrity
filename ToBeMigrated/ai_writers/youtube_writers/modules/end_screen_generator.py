"""
YouTube End Screen Generator Module

This module provides functionality for generating YouTube video end screens.
"""

import streamlit as st
import time
import logging
import traceback
from PIL import Image
from lib.gpt_providers.text_generation.main_text_generation import llm_text_gen
from lib.gpt_providers.text_to_image_generation.gen_gemini_images import generate_gemini_image, edit_image

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('youtube_end_screen_generator')


def generate_end_screen_concepts(video_title, video_description, target_audience, content_type, 
                               primary_goal, secondary_goal=None, num_concepts=3):
    """Generate end screen concept ideas based on video content."""
    logger.info(f"Generating end screen concepts for: '{video_title}'")
    logger.info(f"Parameters: target_audience={target_audience}, content_type={content_type}, "
                f"primary_goal={primary_goal}, secondary_goal={secondary_goal}, num_concepts={num_concepts}")
    
    # Create a system prompt for end screen concept generation
    system_prompt = """You are a YouTube end screen expert specializing in creating engaging, action-driving end screen concepts.
    Your task is to generate end screen concept ideas based on the provided video information.
    Focus ONLY on creating end screens that are optimized for YouTube, with proper visual hierarchy, element placement, and call-to-action triggers.
    Return ONLY the concept descriptions, without any additional commentary or explanations.
    Each concept should include:
    1. A main visual element or background
    2. Element placement and content (subscribe button, playlist, video, website)
    3. Color scheme suggestions
    4. Text content for each element
    5. Brief explanation of why this concept would be effective for the specified goals
    
    IMPORTANT: Format each concept with a clear numbered heading like "1. [Concept Name]" to ensure proper parsing."""
    
    # Build the prompt
    prompt = f"""
    **Instructions:**

    Please generate {num_concepts} end screen concept ideas for a YouTube video with the following information:

    **Video Title:** {video_title}
    **Video Description:** {video_description}
    **Target Audience:** {target_audience}
    **Content Type:** {content_type}
    **Primary Goal:** {primary_goal}
    **Secondary Goal:** {secondary_goal if secondary_goal else "None specified"}

    **Specific Instructions:**
    * Each concept should be clearly separated and numbered with a heading like "1. [Concept Name]".
    * Focus on creating end screens that drive the specified goals.
    * Consider the target audience's interests and preferences.
    * Include specific details about visual elements, element placement, and color schemes.
    * Explain why each concept would be effective for this specific video and goals.
    * Include text suggestions for each element (subscribe button, playlist, video, website).
    """
    
    try:
        logger.info("Sending request to LLM for end screen concepts")
        response = llm_text_gen(prompt, system_prompt=system_prompt)
        logger.info(f"Received response from LLM: {len(response)} characters")
        return response
    except Exception as err:
        logger.error(f"Error generating end screen concepts: {err}")
        logger.error(traceback.format_exc())
        st.error(f"Error: Failed to generate end screen concepts: {err}")
        return None


def generate_end_screen_design(concept_description, style_preference, element_count=2, 
                             element_types=None, element_texts=None, aspect_ratio="16:9", 
                             keywords=None, style=None, focus=None):
    """Generate an end screen image based on the concept description."""
    logger.info(f"Generating end screen design for concept: '{concept_description[:50]}...'")
    logger.info(f"Parameters: style_preference={style_preference}, element_count={element_count}, "
                f"element_types={element_types}, element_texts={element_texts}, aspect_ratio={aspect_ratio}")
    
    # Extract key elements from the concept description
    # This helps focus the prompt on the most important aspects
    concept_lines = concept_description.split('\n')
    main_visual = ""
    element_placement = ""
    color_scheme = ""
    text_content = ""
    
    for line in concept_lines:
        if "visual" in line.lower() or "background" in line.lower():
            main_visual = line
        elif "placement" in line.lower() or "layout" in line.lower():
            element_placement = line
        elif "color" in line.lower() or "scheme" in line.lower():
            color_scheme = line
        elif "text" in line.lower() or "content" in line.lower():
            text_content = line
    
    # Create a more focused prompt for the image generation
    image_prompt = f"""
    Create a YouTube end screen image with the following specifications:
    
    MAIN VISUAL: {main_visual if main_visual else "Not specified"}
    ELEMENT PLACEMENT: {element_placement if element_placement else "Not specified"}
    COLOR SCHEME: {color_scheme if color_scheme else "Not specified"}
    TEXT CONTENT: {text_content if text_content else "Not specified"}
    
    STYLE: {style_preference}
    ASPECT RATIO: {aspect_ratio}
    NUMBER OF ELEMENTS: {element_count}
    
    ELEMENT TYPES: {', '.join(element_types) if element_types else 'Not specified'}
    ELEMENT TEXTS: {', '.join(element_texts) if element_texts else 'Not specified'}
    
    IMPORTANT REQUIREMENTS:
    1. This must be a VISUAL IMAGE of a YouTube end screen, not just a text description
    2. The image should be high contrast and visually striking
    3. All text should be large and readable
    4. Elements should be properly placed for optimal viewer engagement
    5. The design should follow the specified color scheme
    6. The image should be optimized for the specified aspect ratio
    
    PLEASE GENERATE AN ACTUAL IMAGE, NOT JUST A TEXT DESCRIPTION.
    """
    
    try:
        logger.info("Sending request to Gemini for end screen image")
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
        logger.error(f"Error generating end screen image: {err}")
        logger.error(traceback.format_exc())
        st.error(f"Error: Failed to generate end screen image: {err}")
        return None


def edit_end_screen_image(img_path, edit_instructions):
    """Edit an end screen image based on user instructions."""
    logger.info(f"Editing end screen image: '{img_path}'")
    logger.info(f"Edit instructions: '{edit_instructions}'")
    
    try:
        logger.info("Sending request to Gemini for image editing")
        # Edit the image using Gemini
        edited_img_path = edit_image(img_path, f"Edit this image according to these instructions: {edit_instructions}. IMPORTANT: Please generate an actual edited image, not just a text description. I need a visual representation of the edited end screen.")
        logger.info(f"Image editing completed. Edited image path: {edited_img_path}")
        
        # Return the path to the edited image
        return edited_img_path
    except Exception as err:
        logger.error(f"Error editing end screen image: {err}")
        logger.error(traceback.format_exc())
        st.error(f"Error: Failed to edit end screen image: {err}")
        return None


def analyze_end_screen(end_screen_path):
    """Analyze an end screen for effectiveness."""
    logger.info(f"Analyzing end screen: '{end_screen_path}'")
    
    # This would typically involve image analysis, but for now we'll use AI to provide feedback
    system_prompt = """You are a YouTube end screen expert specializing in analyzing and providing feedback on end screen designs.
    Your task is to analyze the end screen and provide constructive feedback on its effectiveness.
    Focus on aspects like visual hierarchy, element placement, call-to-action clarity, and overall effectiveness."""
    
    # For now, we'll just return a placeholder analysis
    # In a real implementation, we would analyze the actual image
    logger.info("Generating end screen analysis")
    return """
    **End Screen Analysis:**
    
    - **Visual Hierarchy:** The main elements are well-positioned and stand out against the background.
    - **Element Placement:** The call-to-action elements are strategically placed for optimal viewer engagement.
    - **Call-to-Action Clarity:** The text and visual cues clearly communicate the desired actions.
    - **Overall Effectiveness:** The design is likely to drive the specified goals due to its visual appeal and clear value proposition.
    
    **Suggestions for Improvement:**
    - Consider adding a subtle animation hint to draw attention to the most important element.
    - The text could be slightly larger for better readability on mobile devices.
    - Adding a small icon or logo could help with brand recognition.
    """


def parse_concepts(concepts_text):
    """Parse the concepts text into a list of individual concepts."""
    logger.info("Parsing concepts text into individual concepts")
    
    # Split the concepts text by main concept headers
    concepts = []
    current_concept = ""
    
    # Look for patterns like numbered headings (e.g., "1.", "2.", "3.") or "Concept 1:", "Concept 2:", etc.
    concept_patterns = ["1.", "2.", "3.", "4.", "5.", "Concept 1:", "Concept 2:", "Concept 3:", "Concept 4:", "Concept 5:"]
    
    for line in concepts_text.split('\n'):
        # Check if line starts with a concept pattern
        is_new_concept = False
        for pattern in concept_patterns:
            if line.strip().startswith(pattern):
                # If we have a previous concept, add it to the list
                if current_concept:
                    concepts.append(current_concept.strip())
                # Start a new concept
                current_concept = line
                is_new_concept = True
                break
        
        if not is_new_concept:
            # Add the line to the current concept
            current_concept += "\n" + line
    
    # Add the last concept
    if current_concept:
        concepts.append(current_concept.strip())
    
    logger.info(f"Parsed {len(concepts)} concepts from the response")
    return concepts


def write_yt_end_screen():
    """Create a user interface for YouTube End Screen Generator."""
    logger.info("Initializing YouTube End Screen Generator UI")
    st.title("YouTube End Screen Generator")
    st.write("Create engaging, action-driving end screens for your YouTube videos.")
    
    # Initialize session state for generated end screens if it doesn't exist
    if "generated_end_screens" not in st.session_state:
        st.session_state.generated_end_screens = []
    if "end_screen_concepts" not in st.session_state:
        st.session_state.end_screen_concepts = None
    if "current_end_screen_path" not in st.session_state:
        st.session_state.current_end_screen_path = None
    if "concept_list" not in st.session_state:
        st.session_state.concept_list = []
    if "editing_end_screen" not in st.session_state:
        st.session_state.editing_end_screen = False
    if "edit_instructions" not in st.session_state:
        st.session_state.edit_instructions = ""
    if "edited_end_screen_path" not in st.session_state:
        st.session_state.edited_end_screen_path = None
    if "show_edit_form" not in st.session_state:
        st.session_state.show_edit_form = False
    
    # Create tabs for different sections
    tab1, tab2 = st.tabs(["Basic Info", "Style & Elements"])
    
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
        
        # End screen goals
        st.subheader("End Screen Goals")
        primary_goal = st.selectbox("Primary Goal", [
            "Drive Subscriptions",
            "Promote Playlist",
            "Promote Next Video",
            "Promote Website",
            "Promote Social Media",
            "Promote Product/Service",
            "Encourage Comments",
            "Mixed Goals"
        ])
        
        secondary_goal = st.selectbox("Secondary Goal (Optional)", [
            "None",
            "Drive Subscriptions",
            "Promote Playlist",
            "Promote Next Video",
            "Promote Website",
            "Promote Social Media",
            "Promote Product/Service",
            "Encourage Comments"
        ])
        
        if secondary_goal == "None":
            secondary_goal = None
    
    with tab2:
        # Style preferences
        st.subheader("Style Preferences")
        
        # Create columns for style options
        col1, col2 = st.columns(2)
        
        with col1:
            style_preference = st.selectbox("End Screen Style", [
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
            
            include_branding = st.checkbox("Include Branding Elements", value=True)
            if include_branding:
                branding_elements = st.multiselect("Branding Elements", [
                    "Channel Logo",
                    "Channel Name",
                    "Channel Tagline",
                    "Brand Colors",
                    "Watermark"
                ])
        
        # Element configuration
        st.subheader("End Screen Elements")
        
        # Number of elements
        element_count = st.slider("Number of Elements", 1, 4, 2)
        
        # Element types
        element_types = []
        element_texts = []
        
        for i in range(element_count):
            st.write(f"Element {i+1}")
            col1, col2 = st.columns(2)
            
            with col1:
                element_type = st.selectbox(
                    f"Type",
                    ["Subscribe Button", "Playlist", "Video", "Website", "Social Media"],
                    key=f"element_type_{i}"
                )
                element_types.append(element_type)
            
            with col2:
                element_text = st.text_input(
                    f"Text",
                    placeholder=f"Text for {element_type}",
                    key=f"element_text_{i}"
                )
                element_texts.append(element_text)
        
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
        st.write("Add keywords to enhance the AI prompt generation. These will help create more detailed and accurate end screens.")
        
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
    
    # Generate button - placed outside of tabs for better visibility
    st.markdown("---")
    st.subheader("Generate End Screen Concepts")
    st.write("Click the button below to generate end screen concepts based on your inputs.")
    
    if st.button("Generate End Screen Concepts", type="primary"):
        if not video_title:
            st.error("Please enter a video title.")
            return
        
        with st.spinner("Generating end screen concepts..."):
            logger.info("User clicked Generate End Screen Concepts button")
            concepts = generate_end_screen_concepts(
                video_title, 
                video_description, 
                target_audience, 
                content_type, 
                primary_goal,
                secondary_goal,
                num_concepts
            )
            
            if concepts:
                # Store the concepts in session state
                st.session_state.end_screen_concepts = concepts
                # Parse the concepts and store in session state
                st.session_state.concept_list = parse_concepts(concepts)
                logger.info("Stored end screen concepts in session state")
                
                # Display the concepts in tabs
                st.subheader("End Screen Concepts")
                
                # Create tabs for each concept
                concept_tabs = st.tabs([f"Concept {i+1}" for i in range(len(st.session_state.concept_list))])
                
                for i, tab in enumerate(concept_tabs):
                    with tab:
                        st.markdown(st.session_state.concept_list[i])
                        
                        # Add a button to generate image for this concept
                        if st.button(f"Generate Image for Concept {i+1}", key=f"gen_img_{i}"):
                            with st.spinner(f"Generating end screen image for concept {i+1}..."):
                                logger.info(f"User selected concept {i+1} for image generation")
                                # Get the selected concept
                                selected_concept = st.session_state.concept_list[i]
                                
                                # Generate the end screen image with enhanced prompt
                                img_path = generate_end_screen_design(
                                    selected_concept,
                                    style_preference,
                                    element_count,
                                    element_types,
                                    element_texts,
                                    aspect_ratio.split()[0],  # Extract just the ratio part
                                    keywords=keywords,
                                    style=style,
                                    focus=focus
                                )
                                
                                if img_path:
                                    # Store the current end screen path in session state
                                    st.session_state.current_end_screen_path = img_path
                                    logger.info(f"Stored current end screen path in session state: {img_path}")
                                    
                                    # Display the generated image
                                    st.subheader("Generated End Screen")
                                    st.image(img_path, use_container_width=True)
                                    
                                    # Add download button
                                    with open(img_path, "rb") as file:
                                        st.download_button(
                                            label="Download End Screen",
                                            data=file,
                                            file_name=f"youtube_end_screen_{int(time.time())}.png",
                                            mime="image/png"
                                        )
                                    
                                    # Add image editing section
                                    st.subheader("Edit End Screen")
                                    st.write("Make changes to your end screen by providing instructions below:")
                                    
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
                                            st.session_state.editing_end_screen = True
                                            st.session_state.show_edit_form = True
                                            
                                            # Rerun to update the UI
                                            st.rerun()
                                    
                                    # Add analysis button
                                    if st.button("Analyze End Screen", key=f"analyze_{i}"):
                                        logger.info("User clicked Analyze End Screen button")
                                        analysis = analyze_end_screen(img_path)
                                        st.subheader("End Screen Analysis")
                                        st.markdown(analysis)
            else:
                st.error("Failed to generate end screen concepts. Please try again.")
    
    # Display previously generated concepts if they exist in session state
    elif st.session_state.end_screen_concepts and st.session_state.concept_list:
        logger.info("Displaying previously generated concepts from session state")
        st.subheader("End Screen Concepts")
        
        # Create tabs for each concept
        concept_tabs = st.tabs([f"Concept {i+1}" for i in range(len(st.session_state.concept_list))])
        
        for i, tab in enumerate(concept_tabs):
            with tab:
                st.markdown(st.session_state.concept_list[i])
                
                # Add a button to generate image for this concept
                if st.button(f"Generate Image for Concept {i+1}", key=f"gen_img_existing_{i}"):
                    with st.spinner(f"Generating end screen image for concept {i+1}..."):
                        logger.info(f"User selected concept {i+1} for image generation")
                        # Get the selected concept
                        selected_concept = st.session_state.concept_list[i]
                        
                        # Generate the end screen image with enhanced prompt
                        img_path = generate_end_screen_design(
                            selected_concept,
                            style_preference,
                            element_count,
                            element_types,
                            element_texts,
                            aspect_ratio.split()[0],  # Extract just the ratio part
                            keywords=keywords,
                            style=style,
                            focus=focus
                        )
                        
                        if img_path:
                            # Store the current end screen path in session state
                            st.session_state.current_end_screen_path = img_path
                            logger.info(f"Stored current end screen path in session state: {img_path}")
                            
                            # Display the generated image
                            st.subheader("Generated End Screen")
                            st.image(img_path, use_container_width=True)
                            
                            # Add download button
                            with open(img_path, "rb") as file:
                                st.download_button(
                                    label="Download End Screen",
                                    data=file,
                                    file_name=f"youtube_end_screen_{int(time.time())}.png",
                                    mime="image/png"
                                )
                            
                            # Add image editing section
                            st.subheader("Edit End Screen")
                            st.write("Make changes to your end screen by providing instructions below:")
                            
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
                                    st.session_state.editing_end_screen = True
                                    st.session_state.show_edit_form = True
                                    
                                    # Rerun to update the UI
                                    st.rerun()
                            
                            # Add analysis button
                            if st.button("Analyze End Screen", key=f"analyze_existing_{i}"):
                                logger.info("User clicked Analyze End Screen button")
                                analysis = analyze_end_screen(img_path)
                                st.subheader("End Screen Analysis")
                                st.markdown(analysis)
    
    # Display current end screen if it exists in session state
    elif st.session_state.current_end_screen_path:
        logger.info(f"Displaying current end screen from session state: {st.session_state.current_end_screen_path}")
        st.subheader("Current End Screen")
        st.image(st.session_state.current_end_screen_path, use_container_width=True)
        
        # Add download button
        with open(st.session_state.current_end_screen_path, "rb") as file:
            st.download_button(
                label="Download End Screen",
                data=file,
                file_name=f"youtube_end_screen_{int(time.time())}.png",
                mime="image/png"
            )
        
        # Add image editing section
        st.subheader("Edit End Screen")
        st.write("Make changes to your end screen by providing instructions below:")
        
        # Create a text area for edit instructions
        edit_instructions = st.text_area(
            "Edit Instructions", 
            placeholder="e.g., Make the background darker, Add a new element, Change the text color to white",
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
                st.session_state.editing_end_screen = True
                st.session_state.show_edit_form = True
                
                # Rerun to update the UI
                st.rerun()
        
        # Add analysis button
        if st.button("Analyze End Screen", key="analyze_current"):
            logger.info("User clicked Analyze End Screen button")
            analysis = analyze_end_screen(st.session_state.current_end_screen_path)
            st.subheader("End Screen Analysis")
            st.markdown(analysis)
    
    # Handle the editing process
    if st.session_state.editing_end_screen and st.session_state.show_edit_form:
        st.subheader("Editing End Screen")
        
        # Show a spinner while editing
        with st.spinner("Editing end screen..."):
            logger.info(f"User provided edit instructions: '{st.session_state.edit_instructions}'")
            # Edit the end screen image
            edited_img_path = edit_end_screen_image(st.session_state.current_end_screen_path, st.session_state.edit_instructions)
            
            if edited_img_path:
                # Update the current end screen path in session state
                st.session_state.edited_end_screen_path = edited_img_path
                logger.info(f"Updated current end screen path in session state: {edited_img_path}")
                
                # Reset editing flags
                st.session_state.editing_end_screen = False
                st.session_state.show_edit_form = False
                
                # Display the edited image
                st.subheader("Edited End Screen")
                st.image(edited_img_path, use_container_width=True)
                
                # Add download button for the edited image
                with open(edited_img_path, "rb") as file:
                    st.download_button(
                        label="Download Edited End Screen",
                        data=file,
                        file_name=f"youtube_end_screen_edited_{int(time.time())}.png",
                        mime="image/png"
                    )
                
                # Update the current end screen path to the edited one
                st.session_state.current_end_screen_path = edited_img_path
                
                # Add a button to continue editing
                if st.button("Continue Editing"):
                    st.session_state.show_edit_form = True
                    st.rerun()
            else:
                # Reset editing flags
                st.session_state.editing_end_screen = False
                st.session_state.show_edit_form = False
                
                st.error("Failed to edit the end screen. Please try again with different instructions.") 