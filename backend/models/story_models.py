"""
Story Writer Models

Pydantic models for story generation API requests and responses.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union


class StoryGenerationRequest(BaseModel):
    """Request model for story generation."""
    persona: str = Field(..., description="The persona statement for the author")
    story_setting: str = Field(..., description="The setting of the story")
    character_input: str = Field(..., description="The characters in the story")
    plot_elements: str = Field(..., description="The plot elements of the story")
    writing_style: str = Field(..., description="The writing style (e.g., Formal, Casual, Poetic, Humorous)")
    story_tone: str = Field(..., description="The tone of the story (e.g., Dark, Uplifting, Suspenseful, Whimsical)")
    narrative_pov: str = Field(..., description="The narrative point of view (e.g., First Person, Third Person Limited, Third Person Omniscient)")
    audience_age_group: str = Field(..., description="The target audience age group (e.g., Children, Young Adults, Adults)")
    content_rating: str = Field(..., description="The content rating (e.g., G, PG, PG-13, R)")
    ending_preference: str = Field(..., description="The preferred ending (e.g., Happy, Tragic, Cliffhanger, Twist)")
    story_length: str = Field(default="Medium", description="Target story length (Short: >1000 words, Medium: >5000 words, Long: >10000 words)")
    enable_explainer: bool = Field(default=True, description="Enable explainer features")
    enable_illustration: bool = Field(default=True, description="Enable illustration features")
    enable_video_narration: bool = Field(default=True, description="Enable story video and narration features")
    
    # Image generation settings
    image_provider: Optional[str] = Field(default=None, description="Image generation provider (gemini, huggingface, stability)")
    image_width: int = Field(default=1024, description="Image width in pixels")
    image_height: int = Field(default=1024, description="Image height in pixels")
    image_model: Optional[str] = Field(default=None, description="Image generation model")
    
    # Video generation settings
    video_fps: int = Field(default=24, description="Frames per second for video")
    video_transition_duration: float = Field(default=0.5, description="Duration of transitions between scenes in seconds")
    
    # Audio generation settings
    audio_provider: Optional[str] = Field(default="gtts", description="TTS provider (gtts, pyttsx3)")
    audio_lang: str = Field(default="en", description="Language code for TTS")
    audio_slow: bool = Field(default=False, description="Whether to speak slowly (gTTS only)")
    audio_rate: int = Field(default=150, description="Speech rate (pyttsx3 only)")


class StorySetupGenerationRequest(BaseModel):
    """Request model for AI story setup generation."""
    story_idea: str = Field(..., description="Basic story idea or information from the user")


class StorySetupOption(BaseModel):
    """A single story setup option."""
    persona: str = Field(..., description="The persona statement for the author")
    story_setting: str = Field(..., description="The setting of the story")
    character_input: str = Field(..., description="The characters in the story")
    plot_elements: str = Field(..., description="The plot elements of the story")
    writing_style: str = Field(..., description="The writing style")
    story_tone: str = Field(..., description="The tone of the story")
    narrative_pov: str = Field(..., description="The narrative point of view")
    audience_age_group: str = Field(..., description="The target audience age group")
    content_rating: str = Field(..., description="The content rating")
    ending_preference: str = Field(..., description="The preferred ending")
    story_length: str = Field(default="Medium", description="Target story length (Short: >1000 words, Medium: >5000 words, Long: >10000 words)")
    premise: str = Field(..., description="The story premise (1-2 sentences)")
    reasoning: str = Field(..., description="Brief reasoning for this setup option")
    
    # Image generation settings
    image_provider: Optional[str] = Field(default=None, description="Image generation provider (gemini, huggingface, stability)")
    image_width: int = Field(default=1024, description="Image width in pixels")
    image_height: int = Field(default=1024, description="Image height in pixels")
    image_model: Optional[str] = Field(default=None, description="Image generation model")
    
    # Video generation settings
    video_fps: int = Field(default=24, description="Frames per second for video")
    video_transition_duration: float = Field(default=0.5, description="Duration of transitions between scenes in seconds")
    
    # Audio generation settings
    audio_provider: Optional[str] = Field(default="gtts", description="TTS provider (gtts, pyttsx3)")
    audio_lang: str = Field(default="en", description="Language code for TTS")
    audio_slow: bool = Field(default=False, description="Whether to speak slowly (gTTS only)")
    audio_rate: int = Field(default=150, description="Speech rate (pyttsx3 only)")


class StorySetupGenerationResponse(BaseModel):
    """Response model for story setup generation."""
    options: List[StorySetupOption] = Field(..., description="Three story setup options")
    success: bool = Field(default=True, description="Whether the generation was successful")


class StoryScene(BaseModel):
    """Model for a story scene."""
    scene_number: int = Field(..., description="Scene number")
    title: str = Field(..., description="Scene title")
    description: str = Field(..., description="Scene description")
    image_prompt: str = Field(..., description="Image prompt for scene visualization")
    audio_narration: str = Field(..., description="Audio narration text for the scene")
    character_descriptions: List[str] = Field(default_factory=list, description="Character descriptions in the scene")
    key_events: List[str] = Field(default_factory=list, description="Key events in the scene")


class StoryStartRequest(StoryGenerationRequest):
    """Request model for story start generation."""
    premise: str = Field(..., description="The story premise")
    outline: Union[str, List[StoryScene], List[Dict[str, Any]]] = Field(..., description="The story outline (text or structured scenes)")


class StoryPremiseResponse(BaseModel):
    """Response model for premise generation."""
    premise: str = Field(..., description="Generated story premise")
    success: bool = Field(default=True, description="Whether the generation was successful")
    task_id: Optional[str] = Field(None, description="Task ID for async operations")


class StoryOutlineResponse(BaseModel):
    """Response model for outline generation."""
    outline: Union[str, List[StoryScene]] = Field(..., description="Generated story outline (text or structured scenes)")
    success: bool = Field(default=True, description="Whether the generation was successful")
    task_id: Optional[str] = Field(None, description="Task ID for async operations")
    is_structured: bool = Field(default=False, description="Whether the outline is structured (scenes) or plain text")


class StoryContentResponse(BaseModel):
    """Response model for story content generation."""
    story: str = Field(..., description="Generated story content")
    premise: Optional[str] = Field(None, description="Story premise")
    outline: Optional[str] = Field(None, description="Story outline")
    is_complete: bool = Field(default=False, description="Whether the story is complete")
    iterations: int = Field(default=0, description="Number of continuation iterations")
    success: bool = Field(default=True, description="Whether the generation was successful")
    task_id: Optional[str] = Field(None, description="Task ID for async operations")


class StoryFullGenerationResponse(BaseModel):
    """Response model for full story generation."""
    premise: str = Field(..., description="Generated story premise")
    outline: str = Field(..., description="Generated story outline")
    story: str = Field(..., description="Generated complete story")
    is_complete: bool = Field(default=False, description="Whether the story is complete")
    iterations: int = Field(default=0, description="Number of continuation iterations")
    success: bool = Field(default=True, description="Whether the generation was successful")
    task_id: Optional[str] = Field(None, description="Task ID for async operations")


class StoryContinueRequest(BaseModel):
    """Request model for continuing story generation."""
    premise: str = Field(..., description="The story premise")
    outline: Union[str, List[StoryScene], List[Dict[str, Any]]] = Field(..., description="The story outline (text or structured scenes)")
    story_text: str = Field(..., description="Current story text to continue from")
    persona: str = Field(..., description="The persona statement for the author")
    story_setting: str = Field(..., description="The setting of the story")
    character_input: str = Field(..., description="The characters in the story")
    plot_elements: str = Field(..., description="The plot elements of the story")
    writing_style: str = Field(..., description="The writing style")
    story_tone: str = Field(..., description="The tone of the story")
    narrative_pov: str = Field(..., description="The narrative point of view")
    audience_age_group: str = Field(..., description="The target audience age group")
    content_rating: str = Field(..., description="The content rating")
    ending_preference: str = Field(..., description="The preferred ending")
    story_length: str = Field(default="Medium", description="Target story length (Short: >1000 words, Medium: >5000 words, Long: >10000 words)")


class StoryContinueResponse(BaseModel):
    """Response model for story continuation."""
    continuation: str = Field(..., description="Generated story continuation")
    is_complete: bool = Field(default=False, description="Whether the story is complete (contains IAMDONE)")
    success: bool = Field(default=True, description="Whether the generation was successful")


class TaskStatus(BaseModel):
    """Task status model."""
    task_id: str = Field(..., description="Task ID")
    status: str = Field(..., description="Task status (pending, processing, completed, failed)")
    progress: Optional[float] = Field(None, description="Progress percentage (0-100)")
    message: Optional[str] = Field(None, description="Progress message")
    result: Optional[Dict[str, Any]] = Field(None, description="Task result when completed")
    error: Optional[str] = Field(None, description="Error message if failed")
    created_at: Optional[str] = Field(None, description="Task creation timestamp")
    updated_at: Optional[str] = Field(None, description="Task last update timestamp")


class StoryImageGenerationRequest(BaseModel):
    """Request model for image generation."""
    scenes: List[StoryScene] = Field(..., description="List of scenes to generate images for")
    provider: Optional[str] = Field(None, description="Image generation provider (gemini, huggingface, stability)")
    width: Optional[int] = Field(default=1024, description="Image width")
    height: Optional[int] = Field(default=1024, description="Image height")
    model: Optional[str] = Field(None, description="Image generation model")


class StoryImageResult(BaseModel):
    """Model for a generated image result."""
    scene_number: int = Field(..., description="Scene number")
    scene_title: str = Field(..., description="Scene title")
    image_filename: str = Field(..., description="Image filename")
    image_url: str = Field(..., description="Image URL")
    width: int = Field(..., description="Image width")
    height: int = Field(..., description="Image height")
    provider: str = Field(..., description="Image generation provider")
    model: Optional[str] = Field(None, description="Image generation model")
    seed: Optional[int] = Field(None, description="Image generation seed")
    error: Optional[str] = Field(None, description="Error message if generation failed")


class StoryImageGenerationResponse(BaseModel):
    """Response model for image generation."""
    images: List[StoryImageResult] = Field(..., description="List of generated images")
    success: bool = Field(default=True, description="Whether the generation was successful")
    task_id: Optional[str] = Field(None, description="Task ID for async operations")


class StoryAudioGenerationRequest(BaseModel):
    """Request model for audio generation."""
    scenes: List[StoryScene] = Field(..., description="List of scenes to generate audio for")
    provider: Optional[str] = Field(default="gtts", description="TTS provider (gtts, pyttsx3)")
    lang: Optional[str] = Field(default="en", description="Language code for TTS")
    slow: Optional[bool] = Field(default=False, description="Whether to speak slowly (gTTS only)")
    rate: Optional[int] = Field(default=150, description="Speech rate (pyttsx3 only)")


class StoryAudioResult(BaseModel):
    """Model for a generated audio result."""
    scene_number: int = Field(..., description="Scene number")
    scene_title: str = Field(..., description="Scene title")
    audio_filename: str = Field(..., description="Audio filename")
    audio_url: str = Field(..., description="Audio URL")
    provider: str = Field(..., description="TTS provider")
    file_size: int = Field(..., description="Audio file size in bytes")
    error: Optional[str] = Field(None, description="Error message if generation failed")


class StoryAudioGenerationResponse(BaseModel):
    """Response model for audio generation."""
    audio_files: List[StoryAudioResult] = Field(..., description="List of generated audio files")
    success: bool = Field(default=True, description="Whether the generation was successful")
    task_id: Optional[str] = Field(None, description="Task ID for async operations")


class StoryVideoGenerationRequest(BaseModel):
    """Request model for video generation."""
    scenes: List[StoryScene] = Field(..., description="List of scenes to generate video for")
    image_urls: List[str] = Field(..., description="List of image URLs for each scene")
    audio_urls: List[str] = Field(..., description="List of audio URLs for each scene")
    story_title: Optional[str] = Field(default="Story", description="Title of the story")
    fps: Optional[int] = Field(default=24, description="Frames per second for video")
    transition_duration: Optional[float] = Field(default=0.5, description="Duration of transitions between scenes")


class StoryVideoResult(BaseModel):
    """Model for a generated video result."""
    video_filename: str = Field(..., description="Video filename")
    video_url: str = Field(..., description="Video URL")
    duration: float = Field(..., description="Video duration in seconds")
    fps: int = Field(..., description="Frames per second")
    file_size: int = Field(..., description="Video file size in bytes")
    num_scenes: int = Field(..., description="Number of scenes in the video")
    error: Optional[str] = Field(None, description="Error message if generation failed")


class StoryVideoGenerationResponse(BaseModel):
    """Response model for video generation."""
    video: StoryVideoResult = Field(..., description="Generated video")
    success: bool = Field(default=True, description="Whether the generation was successful")
    task_id: Optional[str] = Field(None, description="Task ID for async operations")
