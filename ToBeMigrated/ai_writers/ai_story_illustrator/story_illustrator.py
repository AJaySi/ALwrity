"""
AI Story Illustrator - Generate illustrations for stories using Gemini AI

This module provides functionality to generate illustrations for stories using Google's Gemini AI.
Users can input stories via text, file upload, or URL, and the system will generate appropriate
illustrations for different scenes in the story.

Based on: https://github.com/google-gemini/cookbook/blob/main/examples/Book_illustration.ipynb
"""

import streamlit as st
import os
import re
import time
import tempfile
import requests
from pathlib import Path
import io
import base64
import json
import uuid
import logging
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import zipfile

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('story_illustrator')

# Constants
MAX_STORY_LENGTH = 10000  # Maximum story length in characters
MIN_SEGMENT_LENGTH = 100  # Minimum segment length for illustration
MAX_SEGMENTS = 20  # Maximum number of segments to illustrate
DEFAULT_STYLE = "digital art"  # Default illustration style
DEFAULT_ASPECT_RATIO = "16:9"  # Default aspect ratio


def extract_text_from_url(url):
    """Extract text content from a URL."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()
        
        # Get text
        text = soup.get_text(separator='\\n')
        
        # Break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # Drop blank lines
        text = '\\n'.join(chunk for chunk in chunks if chunk)
        
        return text
    except Exception as e:
        logger.error(f"Error extracting text from URL: {e}")
        return None


def segment_story(story_text, min_segment_length=MIN_SEGMENT_LENGTH, max_segments=MAX_SEGMENTS):
    """
    Segment a story into logical parts for illustration.
    Uses paragraph breaks, scene changes, and other indicators to create segments.
    """
    # Clean up the text
    story_text = story_text.strip()
    
    # Split by paragraphs first
    paragraphs = re.split(r'\\n\s*\\n', story_text)
    
    # Initialize segments
    segments = []
    current_segment = ""
    
    for paragraph in paragraphs:
        # Skip empty paragraphs
        if not paragraph.strip():
            continue
            
        # If adding this paragraph would make the segment too long, start a new segment
        if len(current_segment) + len(paragraph) > 1000:  # Limit segment size
            if current_segment:
                segments.append(current_segment.strip())
            current_segment = paragraph
        else:
            # Add paragraph to current segment
            if current_segment:
                current_segment += "\\n\\n" + paragraph
            else:
                current_segment = paragraph
    
    # Add the last segment if it exists
    if current_segment:
        segments.append(current_segment.strip())
    
    # Combine very short segments
    i = 0
    while i < len(segments) - 1:
        if len(segments[i]) < min_segment_length:
            segments[i] += "\\n\\n" + segments[i+1]
            segments.pop(i+1)
        else:
            i += 1
    
    # Limit the number of segments
    if len(segments) > max_segments:
        # Combine segments to reduce the total number
        new_segments = []
        segment_size = len(segments) / max_segments
        
        for i in range(max_segments):
            start_idx = int(i * segment_size)
            end_idx = int((i + 1) * segment_size)
            combined_segment = "\\n\\n".join(segments[start_idx:end_idx])
            new_segments.append(combined_segment)
        
        segments = new_segments
    
    return segments


def extract_scene_elements(segment):
    """
    Extract key scene elements from a story segment using LLM.
    This helps create more accurate illustration prompts.
    """
    from ...gpt_providers.text_generation.main_text_generation import llm_text_gen
    
    prompt = f"""
    Analyze the following story segment and extract key visual elements for an illustration:
    
    {segment}
    
    Please provide:
    1. Main characters present (with brief visual descriptions)
    2. Setting/location details
    3. Key action or emotional moment to illustrate
    4. Important objects or props
    5. Time of day and lighting
    6. Weather or atmospheric conditions (if applicable)
    
    Format your response as JSON with these keys: "characters", "setting", "key_moment", "objects", "lighting", "atmosphere"
    """
    
    try:
        response = llm_text_gen(prompt)
        
        # Try to extract JSON from the response
        try:
            # Find JSON content between triple backticks if present
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Otherwise try to parse the whole response as JSON
                json_str = response
                
            scene_elements = json.loads(json_str)
            return scene_elements
        except json.JSONDecodeError:
            # If JSON parsing fails, extract information using regex
            characters = re.search(r'"characters":\s*"([^"]*)"', response)
            setting = re.search(r'"setting":\s*"([^"]*)"', response)
            
            return {
                "characters": characters.group(1) if characters else "",
                "setting": setting.group(1) if setting else "",
                "key_moment": "",
                "objects": "",
                "lighting": "",
                "atmosphere": ""
            }
    except Exception as e:
        logger.error(f"Error extracting scene elements: {e}")
        return {
            "characters": "",
            "setting": "",
            "key_moment": "",
            "objects": "",
            "lighting": "",
            "atmosphere": ""
        }


def generate_illustration_prompt(segment, style, characters=None, setting=None):
    """
    Generate a prompt for the illustration based on the segment content.
    
    Args:
        segment: The story segment to illustrate
        style: The artistic style for the illustration
        characters: Optional character descriptions
        setting: Optional setting description
    
    Returns:
        A prompt string for the image generation model
    """
    # Create a base prompt
    base_prompt = f"""
    Create a detailed illustration for the following story segment in {style} style:
    
    {segment[:500]}  # Limit segment length for prompt
    
    The illustration should capture the key elements, mood, and action of this scene.
    """
    
    # Add character information if provided
    if characters:
        base_prompt += f"\\n\\nThe main characters in this scene are: {characters}"
    
    # Add setting information if provided
    if setting:
        base_prompt += f"\\n\\nThe setting is: {setting}"
    
    # Add style-specific instructions
    if "watercolor" in style.lower():
        base_prompt += "\\n\\nUse soft, flowing watercolor techniques with visible brush strokes and color blending."
    elif "digital art" in style.lower():
        base_prompt += "\\n\\nCreate a polished digital illustration with clean lines and vibrant colors."
    elif "pencil sketch" in style.lower():
        base_prompt += "\\n\\nUse pencil sketch techniques with visible hatching, shading, and line work."
    
    # Add final quality instructions
    base_prompt += """
    
    Make the illustration:
    - Visually engaging and detailed
    - Appropriate for a storybook
    - Focused on the main action or emotion of the scene
    - With good composition and visual storytelling
    """
    
    return base_prompt.strip()


def create_illustration(segment, style, aspect_ratio="16:9"):
    """
    Create an illustration for a story segment.
    
    Args:
        segment: The story segment to illustrate
        style: The artistic style for the illustration
        aspect_ratio: The aspect ratio for the illustration
    
    Returns:
        Path to the generated image
    """
    # Import here to avoid circular imports
    from ...gpt_providers.text_to_image_generation.gen_gemini_images import generate_gemini_image
    
    # Extract scene elements to enhance the prompt
    scene_elements = extract_scene_elements(segment)
    
    # Create a detailed prompt for the illustration
    prompt = generate_illustration_prompt(
        segment, 
        style,
        characters=scene_elements.get("characters", ""),
        setting=scene_elements.get("setting", "")
    )
    
    # Add key elements to the prompt
    key_moment = scene_elements.get("key_moment", "")
    objects = scene_elements.get("objects", "")
    lighting = scene_elements.get("lighting", "")
    atmosphere = scene_elements.get("atmosphere", "")
    
    if key_moment:
        prompt += f"\\n\\nFocus on this key moment: {key_moment}"
    
    if objects:
        prompt += f"\\n\\nInclude these important objects: {objects}"
    
    if lighting:
        prompt += f"\\n\\nThe lighting is: {lighting}"
    
    if atmosphere:
        prompt += f"\\n\\nThe atmosphere/weather is: {atmosphere}"
    
    # Generate the illustration
    try:
        # Parse aspect ratio
        if aspect_ratio == "16:9":
            width, height = 16, 9
        elif aspect_ratio == "4:3":
            width, height = 4, 3
        elif aspect_ratio == "1:1":
            width, height = 1, 1
        else:
            width, height = 16, 9  # Default
        
        # Generate image using Gemini
        image_path = generate_gemini_image(
            prompt=prompt,
            style=style.lower() if style else None,
            aspect_ratio=aspect_ratio
        )
        
        return image_path
    except Exception as e:
        logger.error(f"Error creating illustration: {e}")
        return None


def create_storybook_pdf(segments, illustrations, title, author, output_path):
    """
    Create a PDF storybook with text and illustrations.
    
    Args:
        segments: List of story segments
        illustrations: List of paths to illustrations
        title: Book title
        author: Book author
        output_path: Path to save the PDF
    
    Returns:
        Path to the created PDF
    """
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as ReportLabImage, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        
        # Create a PDF document
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []
        
        # Get styles
        styles = getSampleStyleSheet()
        title_style = styles['Title']
        author_style = styles['Normal']
        author_style.alignment = 1  # Center alignment
        normal_style = styles['Normal']
        
        # Add title page
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph(f"by {author}", author_style))
        story.append(PageBreak())
        
        # Add content pages
        for i, (segment, illustration_path) in enumerate(zip(segments, illustrations)):
            if illustration_path and os.path.exists(illustration_path):
                # Add illustration
                img = ReportLabImage(illustration_path, width=6*inch, height=4*inch)
                story.append(img)
                story.append(Spacer(1, 0.25*inch))
            
            # Add text
            for paragraph in segment.split('\\n\\n'):
                if paragraph.strip():
                    story.append(Paragraph(paragraph, normal_style))
                    story.append(Spacer(1, 0.1*inch))
            
            # Add page break between segments
            if i < len(segments) - 1:
                story.append(PageBreak())
        
        # Build the PDF
        doc.build(story)
        return output_path
    except Exception as e:
        logger.error(f"Error creating PDF: {e}")
        return None


def create_zip_archive(files, output_path):
    """
    Create a ZIP archive containing the provided files.
    
    Args:
        files: Dictionary of {filename: file_path} to include in the archive
        output_path: Path to save the ZIP file
    
    Returns:
        Path to the created ZIP file
    """
    try:
        with zipfile.ZipFile(output_path, 'w') as zipf:
            for filename, file_path in files.items():
                if os.path.exists(file_path):
                    zipf.write(file_path, arcname=filename)
        return output_path
    except Exception as e:
        logger.error(f"Error creating ZIP archive: {e}")
        return None


def write_story_illustrator():
    """Main function for the Story Illustrator Streamlit app."""
    st.title("AI Story Illustrator")
    st.write("Generate beautiful illustrations for your stories using AI")
    
    # Create tabs for different sections
    tab1, tab2, tab3 = st.tabs(["Story Input", "Illustration Settings", "Generate & Export"])
    
    # Initialize session state variables if they don't exist
    if "story_text" not in st.session_state:
        st.session_state.story_text = ""
    if "segments" not in st.session_state:
        st.session_state.segments = []
    if "illustrations" not in st.session_state:
        st.session_state.illustrations = []
    if "book_title" not in st.session_state:
        st.session_state.book_title = ""
    if "book_author" not in st.session_state:
        st.session_state.book_author = ""
    if "illustration_style" not in st.session_state:
        st.session_state.illustration_style = DEFAULT_STYLE
    if "aspect_ratio" not in st.session_state:
        st.session_state.aspect_ratio = DEFAULT_ASPECT_RATIO
    if "temp_files" not in st.session_state:
        st.session_state.temp_files = []
    
    # Tab 1: Story Input
    with tab1:
        st.header("Step 1: Input Your Story")
        
        # Input method selection
        input_method = st.radio(
            "Choose input method:",
            ["Text Input", "File Upload", "URL"]
        )
        
        if input_method == "Text Input":
            st.session_state.story_text = st.text_area(
                "Enter your story text:",
                value=st.session_state.story_text,
                height=300,
                max_chars=MAX_STORY_LENGTH,
                help="Enter the story text you want to illustrate (max 10,000 characters)"
            )
            
        elif input_method == "File Upload":
            uploaded_file = st.file_uploader("Upload a text file:", type=["txt", "md"])
            if uploaded_file is not None:
                try:
                    st.session_state.story_text = uploaded_file.getvalue().decode("utf-8")
                    st.success(f"Successfully loaded file: {uploaded_file.name}")
                    st.text_area("Preview:", value=st.session_state.story_text[:500] + "...", height=200, disabled=True)
                except Exception as e:
                    st.error(f"Error reading file: {e}")
                    
        elif input_method == "URL":
            url = st.text_input("Enter URL containing the story:")
            if url:
                if st.button("Extract Text from URL"):
                    with st.spinner("Extracting text from URL..."):
                        extracted_text = extract_text_from_url(url)
                        if extracted_text:
                            st.session_state.story_text = extracted_text
                            st.success("Successfully extracted text from URL")
                            st.text_area("Preview:", value=st.session_state.story_text[:500] + "...", height=200, disabled=True)
                        else:
                            st.error("Failed to extract text from URL")
        
        # Book metadata
        st.subheader("Book Metadata")
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.book_title = st.text_input("Book Title:", value=st.session_state.book_title)
        with col2:
            st.session_state.book_author = st.text_input("Author:", value=st.session_state.book_author)
        
        # Process story into segments
        if st.session_state.story_text:
            if st.button("Process Story into Segments"):
                with st.spinner("Processing story into segments..."):
                    st.session_state.segments = segment_story(st.session_state.story_text)
                    st.success(f"Story processed into {len(st.session_state.segments)} segments")
                    
                    # Initialize illustrations list with None values
                    st.session_state.illustrations = [None] * len(st.session_state.segments)
                    
                    # Display segments
                    st.subheader("Story Segments")
                    for i, segment in enumerate(st.session_state.segments):
                        with st.expander(f"Segment {i+1}"):
                            st.write(segment)
    
    # Tab 2: Illustration Settings
    with tab2:
        st.header("Step 2: Configure Illustration Settings")
        
        # Style selection
        st.subheader("Illustration Style")
        style_options = [
            "Digital Art",
            "Watercolor Painting",
            "Pencil Sketch",
            "Oil Painting",
            "Cartoon",
            "Anime",
            "3D Render",
            "Pixel Art",
            "Children's Book Illustration",
            "Comic Book Style",
            "Fantasy Art",
            "Realistic"
        ]
        
        st.session_state.illustration_style = st.selectbox(
            "Choose an illustration style:",
            style_options,
            index=style_options.index(st.session_state.illustration_style) if st.session_state.illustration_style in style_options else 0
        )
        
        # Custom style input
        use_custom_style = st.checkbox("Use custom style")
        if use_custom_style:
            custom_style = st.text_input("Describe your custom style:", 
                                       placeholder="e.g., Impressionist painting with vibrant colors and visible brushstrokes")
            if custom_style:
                st.session_state.illustration_style = custom_style
        
        # Display style examples
        st.info("💡 The style you choose will significantly impact the look and feel of your illustrations.")
        
        # Aspect ratio selection
        st.subheader("Image Settings")
        aspect_ratio_options = {
            "16:9 (Widescreen)": "16:9",
            "4:3 (Standard)": "4:3",
            "1:1 (Square)": "1:1"
        }
        
        selected_ratio = st.selectbox(
            "Choose aspect ratio:",
            list(aspect_ratio_options.keys()),
            index=list(aspect_ratio_options.values()).index(st.session_state.aspect_ratio) if st.session_state.aspect_ratio in aspect_ratio_options.values() else 0
        )
        st.session_state.aspect_ratio = aspect_ratio_options[selected_ratio]
        
        # Advanced settings
        with st.expander("Advanced Settings"):
            st.slider("Number of segments to illustrate:", 1, 
                     max(len(st.session_state.segments), 1) if st.session_state.segments else 1, 
                     min(len(st.session_state.segments), MAX_SEGMENTS) if st.session_state.segments else 1,
                     key="num_segments_to_illustrate")
            
            st.checkbox("Generate cover image", value=True, key="generate_cover")
            
            st.checkbox("Add text to illustrations", value=False, key="add_text_to_illustrations")
    
    # Tab 3: Generate & Export
    with tab3:
        st.header("Step 3: Generate Illustrations & Export")
        
        if not st.session_state.segments:
            st.warning("Please process your story into segments in Step 1 before generating illustrations.")
        else:
            # Generate illustrations
            st.subheader("Generate Illustrations")
            
            num_segments = min(len(st.session_state.segments), st.session_state.get("num_segments_to_illustrate", len(st.session_state.segments)))
            
            if st.button("Generate All Illustrations"):
                with st.spinner(f"Generating {num_segments} illustrations... This may take a while."):
                    progress_bar = st.progress(0)
                    
                    for i in range(num_segments):
                        # Update progress
                        progress_bar.progress((i) / num_segments)
                        st.write(f"Generating illustration {i+1} of {num_segments}...")
                        
                        # Generate illustration
                        illustration_path = create_illustration(
                            st.session_state.segments[i],
                            st.session_state.illustration_style,
                            st.session_state.aspect_ratio
                        )
                        
                        # Store the illustration path
                        if illustration_path:
                            st.session_state.illustrations[i] = illustration_path
                            st.session_state.temp_files.append(illustration_path)
                    
                    # Complete progress
                    progress_bar.progress(1.0)
                    st.success(f"Generated {num_segments} illustrations!")
            
            # Generate individual illustrations
            st.subheader("Generate Individual Illustrations")
            
            for i in range(num_segments):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    with st.expander(f"Segment {i+1}"):
                        st.write(st.session_state.segments[i][:300] + "..." if len(st.session_state.segments[i]) > 300 else st.session_state.segments[i])
                
                with col2:
                    if st.button(f"Generate #{i+1}", key=f"gen_btn_{i}"):
                        with st.spinner(f"Generating illustration {i+1}..."):
                            illustration_path = create_illustration(
                                st.session_state.segments[i],
                                st.session_state.illustration_style,
                                st.session_state.aspect_ratio
                            )
                            
                            if illustration_path:
                                st.session_state.illustrations[i] = illustration_path
                                st.session_state.temp_files.append(illustration_path)
                                st.success(f"Generated illustration {i+1}!")
            
            # Display generated illustrations
            st.subheader("Preview Illustrations")
            
            if any(st.session_state.illustrations):
                for i, illustration_path in enumerate(st.session_state.illustrations[:num_segments]):
                    if illustration_path and os.path.exists(illustration_path):
                        with st.expander(f"Illustration {i+1}"):
                            st.image(illustration_path, caption=f"Illustration for Segment {i+1}", use_column_width=True)
                            
                            # Regenerate button
                            if st.button(f"Regenerate", key=f"regen_btn_{i}"):
                                with st.spinner(f"Regenerating illustration {i+1}..."):
                                    new_illustration_path = create_illustration(
                                        st.session_state.segments[i],
                                        st.session_state.illustration_style,
                                        st.session_state.aspect_ratio
                                    )
                                    
                                    if new_illustration_path:
                                        st.session_state.illustrations[i] = new_illustration_path
                                        st.session_state.temp_files.append(new_illustration_path)
                                        st.rerun()
            else:
                st.info("No illustrations generated yet. Click 'Generate All Illustrations' or generate individual illustrations.")
            
            # Export options
            st.subheader("Export Options")
            
            if any(st.session_state.illustrations):
                export_format = st.radio(
                    "Export format:",
                    ["PDF Storybook", "Individual Images (ZIP)", "Both"]
                )
                
                if st.button("Export"):
                    with st.spinner("Preparing export..."):
                        # Create temporary directory for exports
                        with tempfile.TemporaryDirectory() as temp_dir:
                            # Filter out None values from illustrations
                            valid_illustrations = [path for path in st.session_state.illustrations[:num_segments] if path and os.path.exists(path)]
                            valid_segments = st.session_state.segments[:len(valid_illustrations)]
                            
                            # Prepare filenames
                            safe_title = "".join(c if c.isalnum() else "_" for c in st.session_state.book_title) if st.session_state.book_title else "story"
                            timestamp = int(time.time())
                            
                            # Export as PDF
                            if export_format in ["PDF Storybook", "Both"]:
                                pdf_path = os.path.join(temp_dir, f"{safe_title}_{timestamp}.pdf")
                                
                                try:
                                    pdf_result = create_storybook_pdf(
                                        valid_segments,
                                        valid_illustrations,
                                        st.session_state.book_title or "Untitled Story",
                                        st.session_state.book_author or "Anonymous",
                                        pdf_path
                                    )
                                    
                                    if pdf_result:
                                        with open(pdf_path, "rb") as f:
                                            st.download_button(
                                                label="Download PDF Storybook",
                                                data=f,
                                                file_name=f"{safe_title}.pdf",
                                                mime="application/pdf"
                                            )
                                except Exception as e:
                                    st.error(f"Error creating PDF: {e}")
                                    st.info("Please install ReportLab to enable PDF export: pip install reportlab")
                            
                            # Export as ZIP of images
                            if export_format in ["Individual Images (ZIP)", "Both"]:
                                zip_path = os.path.join(temp_dir, f"{safe_title}_illustrations_{timestamp}.zip")
                                
                                # Prepare files for ZIP
                                files_to_zip = {}
                                for i, img_path in enumerate(valid_illustrations):
                                    if img_path and os.path.exists(img_path):
                                        files_to_zip[f"illustration_{i+1}.png"] = img_path
                                
                                zip_result = create_zip_archive(files_to_zip, zip_path)
                                
                                if zip_result:
                                    with open(zip_path, "rb") as f:
                                        st.download_button(
                                            label="Download Illustrations ZIP",
                                            data=f,
                                            file_name=f"{safe_title}_illustrations.zip",
                                            mime="application/zip"
                                        )
            else:
                st.info("Generate illustrations before exporting.")
    
    # Cleanup temporary files when the session ends
    def cleanup_temp_files():
        for file_path in st.session_state.temp_files:
            try:
                if file_path and os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                logger.error(f"Error removing temporary file {file_path}: {e}")
    
    # Register the cleanup function to run when the session ends
    import atexit
    atexit.register(cleanup_temp_files)


if __name__ == "__main__":
    write_story_illustrator()
