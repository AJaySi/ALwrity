"""
AI Story Video Generator

This module provides functionality to generate animated story videos using AI.
It adapts the Google Gemini cookbook example for Streamlit.
"""

import os
import re
import time
import json
import uuid
import tempfile
import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional, Union

import streamlit as st
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import requests
from moviepy.editor import (
    ImageSequenceClip,
    TextClip,
    CompositeVideoClip,
    AudioFileClip,
)

# Import Gemini functionality (Ensure these paths are correct in your project)
try:
    from lib.gpt_providers.text_generation.main_text_generation import (
        llm_text_gen,
    )
    from lib.gpt_providers.text_to_image_generation.gen_gemini_images import (
        generate_gemini_image,
    )
except ImportError as e:
    st.error(
        f"Failed to import custom libraries: {e}. "
        "Please ensure 'lib/gpt_providers/...' structure is correct and accessible."
    )
    # You might want to exit or disable functionality if imports fail
    llm_text_gen = None
    generate_gemini_image = None

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for maximum verbosity
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Console handler
        logging.FileHandler('story_video_generator.log')  # File handler
    ]
)
logger = logging.getLogger(__name__)

# Constants
DEFAULT_FPS = 1
DEFAULT_DURATION = 3  # seconds per image
DEFAULT_TRANSITION_DURATION = 1  # seconds for transition (Currently unused, potential future feature)
DEFAULT_FONT_SIZE = 24
DEFAULT_FONT_COLOR = "white"
DEFAULT_MUSIC_URL = "https://freepd.com/music/Magical%20Transition.mp3"  # Example free music URL
DEFAULT_IMAGE_WIDTH = 1024
DEFAULT_IMAGE_HEIGHT = 768
TEXT_AREA_HEIGHT_RATIO = 1 / 3
TEXT_PADDING = 20
TEXT_OVERLAY_ALPHA = 160 # Semi-transparent overlay (0-255)

class StoryVideoGenerator:
    """Class to handle the generation of animated story videos."""

    def __init__(self):
        """Initialize the StoryVideoGenerator."""
        logger.info("Initializing StoryVideoGenerator")
        self.temp_dir = tempfile.mkdtemp()
        logger.debug(f"Created temporary directory: {self.temp_dir}")
        # Register cleanup on program exit
        import atexit
        atexit.register(self.cleanup)
        logger.info("StoryVideoGenerator initialized successfully")

    def cleanup(self):
        """Clean up temporary files and resources."""
        logger.info("Starting cleanup process")
        try:
            import shutil
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                logger.info(f"Successfully cleaned up temporary directory: {self.temp_dir}")
            else:
                logger.warning(f"Temporary directory not found: {self.temp_dir}")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}", exc_info=True)

    def __del__(self):
        """Destructor to ensure cleanup."""
        logger.debug("Destructor called")
        self.cleanup()

    def generate_story(
        self, prompt: str, num_scenes: int = 5, style: str = "children's story"
    ) -> Dict[str, Any]:
        """
        Generate a story based on the given prompt using an LLM.

        Args:
            prompt: The story prompt.
            num_scenes: Number of scenes to generate.
            style: Style of the story (e.g., "children's story", "sci-fi").

        Returns:
            A dictionary containing the story title and a list of scenes.

        Raises:
            Exception: If story generation or parsing fails.
        """
        logger.info(f"Generating story with parameters: prompt='{prompt}', num_scenes={num_scenes}, style='{style}'")
        
        if not llm_text_gen:
            logger.error("LLM text generation function not available")
            raise RuntimeError("LLM text generation function not available.")

        try:
            system_prompt = f"""You are a creative story writer specializing in {style} stories.
            Create a short story based on the prompt below.
            The story should have exactly {num_scenes} scenes.
            Format your response STRICTLY as a JSON object with the following structure:
            {{
            "title": "Story Title",
            "scenes": [
            {{
            "scene_number": 1,
            "description": "Brief visual description of the scene suitable for image generation",
            "narration": "The narration text for this scene"
            }},
            ...
            ]
            }}
            Ensure each scene has a clear visual description and corresponding narration.
            Do not include any text outside the JSON structure itself (e.g., no '```json' markers).
            """
            logger.debug(f"Generated system prompt: {system_prompt}")

            user_prompt = f"Create a {style} story about: {prompt}"
            logger.debug(f"Generated user prompt: {user_prompt}")

            response = llm_text_gen(user_prompt, system_prompt=system_prompt)
            logger.debug(f"Raw LLM response received: {response}")

            # Parse and validate the response
            try:
                cleaned_response = re.sub(r'^```(json)?\s*|\s*```$', '', response, flags=re.DOTALL | re.IGNORECASE).strip()
                story_data = json.loads(cleaned_response)
                logger.info("Successfully parsed JSON response")
            except json.JSONDecodeError as json_err:
                logger.error(f"JSONDecodeError: {json_err}. Raw response was: {response}")
                json_match = re.search(r'\{\s*"title":.*\}\s*$', cleaned_response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    try:
                        story_data = json.loads(json_str)
                        logger.info("Successfully parsed JSON using regex fallback")
                    except json.JSONDecodeError as fallback_err:
                        logger.error(f"Fallback JSON parsing failed: {fallback_err}")
                        raise Exception(f"Failed to parse LLM response as JSON. Response:\n{response}") from fallback_err
                else:
                    raise Exception(f"Could not find valid JSON in LLM response. Response:\n{response}") from json_err

            # Validate structure
            if "title" not in story_data or "scenes" not in story_data:
                logger.error("Generated JSON missing 'title' or 'scenes' key")
                raise ValueError("Generated JSON missing 'title' or 'scenes' key")
            if not isinstance(story_data["scenes"], list):
                logger.error("'scenes' key must contain a list")
                raise ValueError("'scenes' key must contain a list")

            logger.info(f"Successfully generated story: {story_data.get('title', 'Untitled')}")
            return story_data

        except Exception as e:
            logger.error(f"Error generating story: {str(e)}", exc_info=True)
            raise Exception(f"Failed to generate or parse story: {str(e)}") from e

    def generate_scene_image(
        self, scene: Dict[str, Any], style: str = "digital art"
    ) -> str:
        """
        Generate an image for a single scene using an image generation model.

        Args:
            scene: The scene dictionary containing "scene_number" and "description".
            style: The visual style for the image (e.g., "digital art", "cartoon").

        Returns:
            Path to the generated image file. Falls back to a placeholder on error.
        """
        scene_num = scene.get("scene_number", "unknown")
        description = scene.get("description", "No description provided.")
        logger.info(f"Generating image for scene {scene_num}: '{description}', style: '{style}'")

        if not generate_gemini_image:
            logger.error("Image generation function not available")
            raise RuntimeError("Image generation function not available.")

        prompt = f"Create a {style} image representing this scene: {description}. Image should be visually clear and focus on the core elements described."
        logger.debug(f"Generated image prompt: {prompt}")

        try:
            # Generate image using the imported function
            # This function should save the image and return its path
            image_path = generate_gemini_image(prompt, style=style) # Assuming this function saves the image and returns path

            if not image_path or not os.path.exists(image_path):
                logger.error(f"Image generation function did not return a valid path: {image_path}")
                raise Exception(f"Image generation function did not return a valid path: {image_path}")

            logger.info(f"Successfully generated image for scene {scene_num}: {image_path}")
            return image_path

        except Exception as e:
            logger.error(f"Error generating image for scene {scene_num}: {str(e)}", exc_info=True)
            logger.warning(f"Creating placeholder image for scene {scene_num}")
            return self._create_placeholder_image(scene_num, description)

    def _create_placeholder_image(
        self, scene_num: Union[int, str], description: str
    ) -> str:
        """Create a placeholder image with text when image generation fails."""
        logger.info(f"Creating placeholder image for scene {scene_num}")
        width, height = DEFAULT_IMAGE_WIDTH, DEFAULT_IMAGE_HEIGHT
        image = Image.new("RGB", (width, height), color=(73, 109, 137))
        draw = ImageDraw.Draw(image)

        try:
            # Try loading a common font, fall back to default
            font_size = 36
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except IOError:
                try:
                    font = ImageFont.truetype("DejaVuSans.ttf", font_size) # Common on Linux
                except IOError:
                    font = ImageFont.load_default()
                    logger.warning("Arial/DejaVuSans font not found. Using default PIL font.")

            text = f"Scene {scene_num}\n\nImage Generation Failed\n\nDescription:\n{description}"

            # Simple text wrapping
            max_text_width = width - 2 * TEXT_PADDING
            lines = []
            words = text.split()
            current_line = ""
            for word in words:
                 if not current_line:
                      test_line = word
                 else:
                      test_line = current_line + " " + word

                 # Use textbbox for potentially more accurate width estimation
                 try:
                      bbox = draw.textbbox((0,0), test_line, font=font)
                      line_width = bbox[2] - bbox[0]
                 except AttributeError: # older Pillow versions might not have textbbox
                      line_width = draw.textlength(test_line, font=font) # Use textlength


                 if line_width <= max_text_width:
                      current_line = test_line
                 else:
                      lines.append(current_line)
                      current_line = word
            lines.append(current_line) # Add the last line

            # Calculate text block height and starting position
            total_text_height = 0
            line_heights = []
            for line in lines:
                  try:
                       bbox = draw.textbbox((0,0), line, font=font)
                       h = bbox[3] - bbox[1]
                  except AttributeError:
                       # Estimate height if textbbox not available
                       (_, h) = draw.textsize(line, font=font)
                  line_heights.append(h)
                  total_text_height += h + 5 # Add small spacing

            start_y = (height - total_text_height) // 2

            # Draw text line by line
            current_y = start_y
            for i, line in enumerate(lines):
                  try:
                       bbox = draw.textbbox((0,0), line, font=font)
                       line_width = bbox[2] - bbox[0]
                  except AttributeError:
                       line_width = draw.textlength(line, font=font)

                  x_position = (width - line_width) // 2
                  draw.text((x_position, current_y), line, fill="white", font=font)
                  current_y += line_heights[i] + 5 # Move y for next line

        except Exception as font_err:
            logger.error(f"Error drawing text on placeholder: {font_err}", exc_info=True)
            # Draw a simple error message if font loading/drawing fails
            draw.text((10, 10), f"Error creating placeholder text for Scene {scene_num}", fill="red")


        # Save image
        output_path = os.path.join(
            self.temp_dir, f"placeholder_scene_{scene_num}_{uuid.uuid4()}.png"
        )
        image.save(output_path)
        logger.info(f"Saved placeholder image to {output_path}")
        return output_path

    def add_text_to_image(self, image_path: str, text: str) -> str:
        """
        Add narration text overlayed on an image.

        Args:
            image_path: Path to the source image.
            text: The narration text to add.

        Returns:
            Path to the new image with text overlay. Returns original path on error.
        """
        logger.info(f"Adding text overlay to image: {image_path}")
        try:
            image = Image.open(image_path).convert("RGBA") # Ensure RGBA for overlay
            width, height = image.size

            # Create a semi-transparent overlay for the bottom part
            overlay_height = int(height * TEXT_AREA_HEIGHT_RATIO)
            overlay = Image.new(
                "RGBA", (width, overlay_height), (0, 0, 0, TEXT_OVERLAY_ALPHA)
            )

            # Paste overlay onto a copy of the image
            image_with_overlay = image.copy()
            image_with_overlay.paste(
                overlay, (0, height - overlay_height), overlay
            )

            # Prepare to draw text
            draw = ImageDraw.Draw(image_with_overlay)
            try:
                font = ImageFont.truetype("arial.ttf", DEFAULT_FONT_SIZE)
            except IOError:
                 try:
                      font = ImageFont.truetype("DejaVuSans.ttf", DEFAULT_FONT_SIZE)
                 except IOError:
                      font = ImageFont.load_default()
                      logger.warning("Arial/DejaVuSans font not found. Using default PIL font for overlay.")


            # Wrap text
            max_text_width = width - 2 * TEXT_PADDING
            words = text.split()
            lines = []
            current_line = ""

            if not words: # Handle empty narration
                logger.warning(f"Empty narration text for image {image_path}. No text added.")
                return image_path # Return original if no text

            for word in words:
                 if not current_line:
                      test_line = word
                 else:
                      test_line = current_line + " " + word

                 try:
                      bbox = draw.textbbox((0,0), test_line, font=font)
                      line_width = bbox[2] - bbox[0]
                 except AttributeError:
                      line_width = draw.textlength(test_line, font=font)

                 if line_width <= max_text_width:
                      current_line = test_line
                 else:
                      lines.append(current_line)
                      current_line = word
            lines.append(current_line) # Add the last line

            # Calculate starting Y position for text
            total_text_height = 0
            line_heights = []
            line_spacing = 10
            for line in lines:
                  try:
                       bbox = draw.textbbox((0,0), line, font=font)
                       h = bbox[3] - bbox[1]
                  except AttributeError:
                        (_, h) = draw.textsize(line, font=font)
                  line_heights.append(h)
                  total_text_height += h + line_spacing

            total_text_height -= line_spacing # Remove extra spacing after last line

            # Adjust starting position to center text vertically within the overlay area
            text_area_top = height - overlay_height
            start_y = text_area_top + (overlay_height - total_text_height) // 2
            if start_y < text_area_top + TEXT_PADDING: # Ensure padding from top of overlay
                start_y = text_area_top + TEXT_PADDING

            # Draw text lines
            current_y = start_y
            for i, line in enumerate(lines):
                try:
                    bbox = draw.textbbox((0,0), line, font=font)
                    line_width = bbox[2] - bbox[0]
                except AttributeError:
                    line_width = draw.textlength(line, font=font)

                x_position = (width - line_width) // 2 # Center horizontally
                draw.text(
                    (x_position, current_y),
                    line,
                    fill=DEFAULT_FONT_COLOR,
                    font=font,
                )
                current_y += line_heights[i] + line_spacing

            # Save the new image (use PNG to preserve transparency)
            base_name = os.path.basename(image_path)
            name, ext = os.path.splitext(base_name)
            output_path = os.path.join(
                self.temp_dir, f"text_{name}_{uuid.uuid4()}.png"
            )
             # Convert back to RGB before saving if target format doesn't need alpha
            image_with_overlay.convert("RGB").save(output_path)
            logger.info(f"Added text overlay to {image_path}, saved as {output_path}")
            return output_path

        except FileNotFoundError:
             logger.error(f"Error adding text: Image file not found at {image_path}")
             return image_path # Return original path if file is missing
        except Exception as e:
            logger.error(
                f"Error adding text to image {image_path}: {str(e)}", exc_info=True
            )
            return image_path  # Return original image path if text addition fails

    def download_audio(self, url: str) -> Optional[str]:
        """
        Download audio file from a URL.

        Args:
            url: URL of the audio file (expects MP3).

        Returns:
            Path to the downloaded audio file, or None if download fails.
        """
        logger.info(f"Downloading audio from URL: {url}")
        if not url:
            logger.warning("No audio URL provided.")
            return None

        try:
            response = requests.get(url, stream=True, timeout=30) # Add timeout
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

            # Check content type (optional but recommended)
            content_type = response.headers.get('content-type')
            if content_type and 'audio' not in content_type:
                 logger.warning(f"URL content type is '{content_type}', expected audio. Proceeding anyway.")

            audio_path = os.path.join(self.temp_dir, f"background_music_{uuid.uuid4()}.mp3")
            with open(audio_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            logger.info(f"Successfully downloaded audio to {audio_path}")
            return audio_path

        except requests.exceptions.RequestException as e:
            logger.error(f"Error downloading audio from {url}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"An unexpected error occurred during audio download: {str(e)}", exc_info=True)
            return None


    def create_video(
        self,
        image_paths: List[str],
        audio_path: Optional[str] = None,
        fps: int = DEFAULT_FPS,
        duration_per_image: int = DEFAULT_DURATION,
    ) -> str:
        """
        Create a video from a sequence of images with optional audio.

        Args:
            image_paths: List of paths to the image files (should include text overlays if added).
            audio_path: Path to the background audio file (optional).
            fps: Frames per second for the output video.
            duration_per_image: How long each image should be displayed in seconds.

        Returns:
            Path to the created video file.

        Raises:
            Exception: If video creation fails.
            FileNotFoundError: If any image path is invalid.
        """
        logger.info(f"Creating video with {len(image_paths)} images, fps={fps}, duration={duration_per_image}s/image")
        if not image_paths:
            logger.error("Cannot create video with no images.")
            raise ValueError("Cannot create video with no images.")

        # Verify all image paths exist before processing
        for img_path in image_paths:
             if not os.path.exists(img_path):
                  logger.error(f"Image file not found: {img_path}")
                  raise FileNotFoundError(f"Image file not found: {img_path}")

        try:
            # Create a unique output filename
            output_path = os.path.join(
                self.temp_dir, f"story_video_{uuid.uuid4()}.mp4"
            )

            # Load images and create frames list
            # Need to ensure all images are the same size, resize if necessary
            frames = []
            target_size = None

            logger.info("Loading and processing images for video...")
            for i, img_path in enumerate(image_paths):
                 try:
                      img = Image.open(img_path).convert("RGB") # Ensure RGB format for video

                      if target_size is None:
                           target_size = img.size
                           logger.info(f"Video frame size set to: {target_size}")
                      elif img.size != target_size:
                           logger.warning(f"Image {i} ({img_path}) has size {img.size}, resizing to {target_size}")
                           img = img.resize(target_size, Image.LANCZOS) # Use high-quality resize filter

                      # Duplicate frame for the duration
                      num_frames_per_image = duration_per_image * fps
                      img_array = np.array(img)
                      for _ in range(num_frames_per_image):
                           frames.append(img_array)
                 except Exception as img_err:
                      logger.error(f"Error processing image {img_path}: {img_err}", exc_info=True)
                      # Option: skip image, use placeholder, or raise error
                      raise Exception(f"Failed to load or process image: {img_path}") from img_err


            if not frames:
                logger.error("No valid frames could be generated from the images.")
                raise ValueError("No valid frames could be generated from the images.")

            # Create video clip from image sequence
            logger.info(f"Creating ImageSequenceClip with {len(frames)} total frames.")
            clip = ImageSequenceClip(frames, fps=fps)

            # Add audio if provided and valid
            final_audio_clip = None
            if audio_path and os.path.exists(audio_path):
                 logger.info(f"Adding audio from: {audio_path}")
                 try:
                      audio_clip = AudioFileClip(audio_path)
                      video_duration = clip.duration

                      # Loop or trim audio to match video duration
                      if audio_clip.duration < video_duration:
                           logger.info(f"Looping audio (duration {audio_clip.duration}s) for video (duration {video_duration}s)")
                           final_audio_clip = audio_clip.loop(duration=video_duration)
                      elif audio_clip.duration > video_duration:
                           logger.info(f"Trimming audio (duration {audio_clip.duration}s) to video duration ({video_duration}s)")
                           final_audio_clip = audio_clip.subclip(0, video_duration)
                      else:
                            final_audio_clip = audio_clip # Duration matches exactly

                      clip = clip.set_audio(final_audio_clip)
                 except Exception as audio_err:
                      logger.error(f"Error processing audio file {audio_path}: {audio_err}. Proceeding without audio.", exc_info=True)
                      # Ensure audio clip resources are closed if error occurs mid-process
                      if 'audio_clip' in locals() and hasattr(audio_clip, 'close'):
                          audio_clip.close()
            elif audio_path:
                logger.warning(f"Audio path provided ({audio_path}) but file not found. Creating video without audio.")


            # Write video file
            logger.info(f"Writing video file to: {output_path}")
            # Use sensible codecs and parameters
            clip.write_videofile(
                output_path,
                codec="libx264",    # Common and efficient codec
                audio_codec="aac",  # Standard audio codec
                ffmpeg_params=["-pix_fmt", "yuv420p"], # Ensure compatibility
                logger='bar'        # Show progress bar
            )

            logger.info(f"Successfully created video: {output_path}")

            # Clean up moviepy resources
            clip.close()
            if final_audio_clip and hasattr(final_audio_clip, 'close'):
                final_audio_clip.close()

            return output_path

        except Exception as e:
            logger.error(f"Error creating video: {str(e)}", exc_info=True)
            # Clean up partial resources if possible
            if 'clip' in locals() and hasattr(clip, 'close'):
                clip.close()
            if 'final_audio_clip' in locals() and hasattr(final_audio_clip, 'close'):
                final_audio_clip.close()

            raise Exception(f"Failed to create video: {str(e)}") from e

# --- Streamlit UI ---

def write_story_video_generator():
    """Main function to run the Streamlit application interface."""
    logger.info("Starting Story Video Generator UI")
    
    if not MOVIEPY_AVAILABLE:
        logger.error("MoviePy is not available")
        st.error(
            "MoviePy is required for video generation but is not properly installed. "
            "Please install it using:\n"
            "```\n"
            "pip install moviepy imageio imageio-ffmpeg\n"
            "```"
        )
        return

    # Check if dependencies are loaded
    if not llm_text_gen or not generate_gemini_image:
        logger.error("Core AI functionalities could not be loaded")
        st.error("Core AI functionalities could not be loaded. Please check the logs and library paths.")
        st.stop()

    # Initialize session state variables
    logger.debug("Initializing session state variables")
    if "story_data" not in st.session_state:
        st.session_state.story_data = None
    if "generated_images" not in st.session_state:
        st.session_state.generated_images = []
    if "original_images" not in st.session_state:
        st.session_state.original_images = []
    if "video_path" not in st.session_state:
        st.session_state.video_path = None

    tab1, tab2, tab3, tab4 = st.tabs(
        ["**1. Story Prompt**", "**2. Storyboard**", "**3. Generate Images**", "**4. Create Video**"]
    )

    # --- Step 1: Story Prompt ---
    with tab1:
        st.header("Step 1: Create Your Story")

        col1, col2 = st.columns([2, 1])

        with col1:
            story_prompt = st.text_area(
                "Enter your story idea:",
                placeholder="e.g., A brave squirrel who learns to fly with the help of an old owl.",
                height=100,
                key="story_prompt_input"
            )

            col1_1, col1_2 = st.columns(2)
            with col1_1:
                num_scenes = st.slider(
                    "Number of Scenes", min_value=2, max_value=10, value=4, key="num_scenes_slider"
                )
            with col1_2:
                story_style = st.selectbox(
                    "Story Style",
                    [
                        "children's story",
                        "adventure story",
                        "fairy tale",
                        "sci-fi story",
                        "fantasy story",
                        "mystery story",
                        "fable",
                    ],
                    key="story_style_select"
                )

        with col2:
            st.markdown("#### Tips for Good Prompts")
            st.markdown(
                """
                * **Be specific:** Mention characters, setting, and the main plot point.
                * **Include conflict:** What challenge do the characters face?
                * **Suggest a mood:** Happy, mysterious, exciting?
                * **Target Audience:** Helps the AI tailor the tone (e.g., "for young children").
                * **Example:** "A funny children's story about a clumsy robot trying to bake a cake for its creator's birthday in a futuristic kitchen."
                """
            )

        if st.button("✨ Generate Story", type="primary", key="generate_story_button"):
            if not story_prompt:
                st.error("Please enter a story prompt.")
            else:
                with st.spinner("✍️ Generating your story... This may take a moment."):
                    try:
                        generator = StoryVideoGenerator() # Create instance
                        story_data = generator.generate_story(
                            story_prompt, num_scenes, story_style
                        )
                        st.session_state.story_data = story_data
                        # Reset downstream states
                        st.session_state.generated_images = []
                        st.session_state.original_images = []
                        st.session_state.video_path = None
                        st.success(
                            "Story generated successfully! Proceed to the **Storyboard** tab to review and edit."
                        )
                        # Consider automatically switching tabs here if desired (more complex JS interaction)
                    except Exception as e:
                        st.error(f"Error generating story: {str(e)}")
                        logger.error("Story generation failed in UI", exc_info=True)


    # --- Step 2: Storyboard ---
    with tab2:
        st.header("Step 2: Review Your Storyboard")

        if st.session_state.story_data:
            story_data = st.session_state.story_data

            st.subheader(f"Title: {story_data.get('title', 'Untitled Story')}")
            st.markdown("Review and edit the scene descriptions and narrations below.")

            # Use st.form to batch edits? Could be smoother but adds complexity.
            # Simple sequential editing for now.
            edited = False
            for i, scene in enumerate(story_data["scenes"]):
                st.markdown("---")
                st.markdown(f"**🎬 Scene {scene.get('scene_number', i+1)}**")

                # Store original values for comparison/reset?
                original_desc = scene.get("description", "")
                original_narr = scene.get("narration", "")

                # Use unique keys for each text area
                desc_key = f"desc_{scene.get('scene_number', i)}"
                narr_key = f"narr_{scene.get('scene_number', i)}"

                new_description = st.text_area(
                    "Visual Description (for image generation)",
                    value=original_desc,
                    key=desc_key,
                    height=100
                )
                new_narration = st.text_area(
                    "Narration Text (for voiceover/overlay)",
                    value=original_narr,
                    key=narr_key,
                    height=100
                )

                # Update the scene data in session state if changed
                if new_description != original_desc:
                    st.session_state.story_data["scenes"][i]["description"] = new_description
                    edited = True
                if new_narration != original_narr:
                    st.session_state.story_data["scenes"][i]["narration"] = new_narration
                    edited = True

            if edited:
                 # Use st.info for non-blocking notification
                 st.info("Changes saved in session. Proceed when ready.")

            if st.button("🖼️ Proceed to Image Generation", type="primary", key="proceed_to_images_button"):
                # Re-check story_data exists before proceeding
                if not st.session_state.story_data or not st.session_state.story_data.get("scenes"):
                    st.error("No story data available. Please generate a story first.")
                else:
                    # Reset image/video state if proceeding from edits
                    st.session_state.generated_images = []
                    st.session_state.original_images = []
                    st.session_state.video_path = None
                    st.success("Ready! Go to the **Generate Images** tab.")

        else:
            st.info("Generate a story in **Step 1** first.")

    # --- Step 3: Generate Images ---
    with tab3:
        st.header("Step 3: Generate Scene Images")

        if st.session_state.story_data and st.session_state.story_data.get("scenes"):
            story_data = st.session_state.story_data

            col1, col2 = st.columns([1, 2]) # Settings | Preview

            with col1:
                st.subheader("Image Settings")
                image_style = st.selectbox(
                    "Image Style",
                    [
                        "digital art",
                        "cartoon",
                        "watercolor",
                        "photorealistic", # Changed 'realistic'
                        "anime",
                        "pixel art",
                        "oil painting",
                        "line art",
                        "cinematic",
                    ],
                    key="image_style_select"
                )

                include_text = st.checkbox(
                    "Overlay narration text on images", value=True, key="include_text_checkbox"
                )

                st.markdown("---")

                if st.button("🎨 Generate All Images", type="primary", key="generate_images_button"):
                    # Check if images already exist for current story? Ask to regenerate?
                    # Simple approach: always regenerate when button is clicked.
                    with st.spinner("Generating images... This can take some time depending on the number of scenes."):
                        try:
                            generator = StoryVideoGenerator() # New instance for this task
                            generated_images = []
                            original_images = [] # Store originals separately

                            num_scenes_total = len(story_data["scenes"])
                            progress_bar = st.progress(0.0)
                            status_text = st.empty()

                            for i, scene in enumerate(story_data["scenes"]):
                                status_text.text(f"Generating image for scene {i+1}/{num_scenes_total}...")
                                # Generate the base image
                                original_image_path = generator.generate_scene_image(
                                    scene, image_style
                                )
                                original_images.append(original_image_path)

                                # Add text if requested
                                if include_text:
                                     status_text.text(f"Adding text overlay for scene {i+1}...")
                                     final_image_path = generator.add_text_to_image(
                                         original_image_path, scene.get("narration", "")
                                     )
                                     # Check if text addition failed (returned original path)
                                     if final_image_path == original_image_path and scene.get("narration", ""):
                                          st.warning(f"Could not add text overlay to scene {i+1}. Using original image.")
                                     generated_images.append(final_image_path)
                                else:
                                     generated_images.append(original_image_path) # Use original if no text needed

                                progress_bar.progress((i + 1) / num_scenes_total)

                            status_text.text("Image generation complete!")
                            st.session_state.original_images = original_images
                            st.session_state.generated_images = generated_images
                            st.session_state.video_path = None # Reset video path
                            st.success(
                                "All images generated! Review them here and proceed to the **Create Video** tab."
                            )
                        except FileNotFoundError as fnf_err:
                            st.error(f"Image Generation Error: A required file was not found. {fnf_err}")
                            logger.error("Image generation failed due to FileNotFoundError", exc_info=True)
                        except Exception as e:
                            st.error(f"Error generating images: {str(e)}")
                            logger.error("Image generation failed in UI", exc_info=True)
                            # Clear potentially partial results
                            st.session_state.generated_images = []
                            st.session_state.original_images = []


            with col2:
                st.subheader("Image Preview")
                if st.session_state.generated_images:
                    # Display images (final versions with text if applicable)
                    for i, img_path in enumerate(st.session_state.generated_images):
                        scene_num = st.session_state.story_data["scenes"][i].get("scene_number", i+1)
                        st.image(
                            img_path,
                            caption=f"Scene {scene_num}",
                            use_column_width=True,
                        )
                else:
                    st.info(
                        "Click 'Generate All Images' after configuring settings."
                    )
        else:
            st.info(
                "Please generate or review a story in **Step 1** or **Step 2** first."
            )


    # --- Step 4: Create Video ---
    with tab4:
        st.header("Step 4: Create Your Story Video")

        if st.session_state.generated_images:
            col1, col2 = st.columns([1, 1]) # Settings | Video Player

            with col1:
                st.subheader("Video Settings")
                fps = st.slider(
                    "Frames Per Second (Video Smoothness)",
                    min_value=1,
                    max_value=30,
                    value=max(DEFAULT_FPS, 10), # Default to slightly smoother
                    key="fps_slider"
                )
                duration_per_image = st.slider(
                    "Seconds Per Scene",
                    min_value=1,
                    max_value=15,
                    value=DEFAULT_DURATION,
                    key="duration_slider"
                )

                st.markdown("---")
                st.subheader("Audio Settings")
                use_music = st.checkbox("Add background music", value=True, key="use_music_checkbox")

                music_url_to_use = None
                if use_music:
                    music_option = st.radio(
                        "Music Source",
                        ["Use default soothing music", "Provide music URL (MP3)"],
                        key="music_option_radio",
                        horizontal=True
                    )

                    if music_option == "Provide music URL (MP3)":
                        custom_music_url = st.text_input(
                            "Music URL (must be direct MP3 link)",
                            placeholder="https://example.com/path/to/music.mp3",
                            key="custom_music_url_input"
                        )
                        if custom_music_url:
                            music_url_to_use = custom_music_url
                        else:
                            # Explicitly set to None if field is empty but option selected
                            music_url_to_use = None
                    else:
                        music_url_to_use = DEFAULT_MUSIC_URL
                        st.caption(f"Using default: {DEFAULT_MUSIC_URL}")

                st.markdown("---")

                if st.button("🎞️ Create Video", type="primary", key="create_video_button"):
                    if not st.session_state.generated_images:
                         st.error("No images found. Please generate images in Step 3.")
                    else:
                         with st.spinner("🎬 Creating your story video... This might take some time."):
                            try:
                                generator = StoryVideoGenerator() # New instance

                                # Download audio if requested and URL is valid
                                audio_path = None
                                if use_music and music_url_to_use:
                                     status_text = st.empty()
                                     status_text.text("Downloading background music...")
                                     audio_path = generator.download_audio(music_url_to_use)
                                     if not audio_path:
                                          st.warning("Failed to download music. Proceeding without audio.")
                                          status_text.text("Music download failed. Continuing...")
                                     else:
                                          status_text.text("Music downloaded.")

                                # Create video using the final generated images
                                status_text.text("Compiling video...")
                                video_path = generator.create_video(
                                    st.session_state.generated_images, # Use images (potentially with text)
                                    audio_path,
                                    fps,
                                    duration_per_image,
                                )

                                st.session_state.video_path = video_path
                                status_text.empty() # Clear status message
                                st.success("Video created successfully!")

                            except FileNotFoundError as fnf_err:
                                 st.error(f"Video Creation Error: A required file was not found. {fnf_err}")
                                 logger.error("Video creation failed due to FileNotFoundError", exc_info=True)
                            except Exception as e:
                                st.error(f"Error creating video: {str(e)}")
                                logger.error("Video creation failed in UI", exc_info=True)
                                st.session_state.video_path = None # Clear video path on error

            with col2:
                st.subheader("Video Preview")
                if st.session_state.video_path:
                    try:
                        video_file = open(st.session_state.video_path, "rb")
                        video_bytes = video_file.read()
                        st.video(video_bytes)
                        video_file.close() # Close the file handle

                        # Prepare download button
                        try:
                            video_title = st.session_state.story_data.get("title", "story")
                            safe_title = re.sub(r'[^\w\-]+', '_', video_title) # Sanitize title for filename
                            download_filename = f"{safe_title}_video.mp4"

                            st.download_button(
                                label="⬇️ Download Video",
                                data=video_bytes, # Use the bytes already read
                                file_name=download_filename,
                                mime="video/mp4",
                                key="download_video_button"
                            )
                        except Exception as download_err:
                             st.error(f"Error preparing download button: {download_err}")

                    except FileNotFoundError:
                         st.error("The generated video file could not be found. Please try generating again.")
                         st.session_state.video_path = None # Reset state
                    except Exception as display_err:
                         st.error(f"Error displaying video: {display_err}")
                         logger.error("Error displaying video in UI", exc_info=True)


                else:
                    st.info(
                        "Click 'Create Video' after generating images and configuring settings."
                    )
        else:
            st.info(
                "Please generate images in **Step 3** first."
            )

    # --- Footer ---
    st.markdown("---")
    st.markdown(
        "Powered by AI | Story generation, image creation, and video compilation."
    )
    # Add link to your repo or project if desired
    # st.markdown("[GitHub Repository](your-link-here)")

    logger.info("Story Video Generator UI initialized successfully")

if __name__ == "__main__":
    # Ensure essential libraries are installed
    try:
        import streamlit
        import numpy
        import PIL
        import requests
        import moviepy
        # Optionally check for google-generativeai if it's the backend
        # import google.generativeai
    except ImportError as e:
        logger.error(f"Error: Missing required library: {e.name}")
        st.error(f"Error: Missing required library: {e.name}")
        st.error("Please install all required libraries: pip install streamlit numpy Pillow requests moviepy")
        # Add other dependencies like google-generativeai if needed
        exit(1)

    write_story_video_generator()