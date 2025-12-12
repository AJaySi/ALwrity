"""
Audio Generation Service for Story Writer

Generates audio narration for story scenes using TTS (Text-to-Speech) providers.
"""

import os
import uuid
from typing import List, Dict, Any, Optional
from pathlib import Path
from loguru import logger
from fastapi import HTTPException


class StoryAudioGenerationService:
    """Service for generating audio narration for story scenes."""
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize the audio generation service.
        
        Parameters:
            output_dir (str, optional): Directory to save generated audio files.
                                      Defaults to 'backend/story_audio' if not provided.
        """
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            # Default to backend/story_audio directory
            base_dir = Path(__file__).parent.parent.parent
            self.output_dir = base_dir / "story_audio"
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"[StoryAudioGeneration] Initialized with output directory: {self.output_dir}")
    
    def _generate_audio_filename(self, scene_number: int, scene_title: str) -> str:
        """Generate a unique filename for a scene audio file."""
        # Clean scene title for filename
        clean_title = "".join(c if c.isalnum() or c in ('-', '_') else '_' for c in scene_title[:30])
        unique_id = str(uuid.uuid4())[:8]
        return f"scene_{scene_number}_{clean_title}_{unique_id}.mp3"
    
    def _generate_audio_gtts(
        self,
        text: str,
        output_path: Path,
        lang: str = "en",
        slow: bool = False
    ) -> bool:
        """
        Generate audio using Google Text-to-Speech (gTTS).
        
        Parameters:
            text (str): Text to convert to speech.
            output_path (Path): Path to save the audio file.
            lang (str): Language code (default: "en").
            slow (bool): Whether to speak slowly (default: False).
        
        Returns:
            bool: True if generation was successful, False otherwise.
        """
        try:
            from gtts import gTTS
            
            # Generate speech
            tts = gTTS(text=text, lang=lang, slow=slow)
            
            # Save to file
            tts.save(str(output_path))
            
            logger.info(f"[StoryAudioGeneration] Generated audio using gTTS: {output_path}")
            return True
            
        except ImportError as e:
            logger.error(f"[StoryAudioGeneration] gTTS not installed. ImportError: {e}. Install with: pip install gtts")
            return False
        except Exception as e:
            logger.error(f"[StoryAudioGeneration] Error generating audio with gTTS: {type(e).__name__}: {e}")
            return False
    
    def _generate_audio_pyttsx3(
        self,
        text: str,
        output_path: Path,
        rate: int = 150,
        voice: Optional[str] = None
    ) -> bool:
        """
        Generate audio using pyttsx3 (offline TTS).
        
        Parameters:
            text (str): Text to convert to speech.
            output_path (Path): Path to save the audio file.
            rate (int): Speech rate (default: 150).
            voice (str, optional): Voice ID to use.
        
        Returns:
            bool: True if generation was successful, False otherwise.
        """
        try:
            import pyttsx3
            
            # Initialize TTS engine
            engine = pyttsx3.init()
            
            # Set speech rate
            engine.setProperty('rate', rate)
            
            # Set voice if provided
            if voice:
                voices = engine.getProperty('voices')
                for v in voices:
                    if voice in v.id:
                        engine.setProperty('voice', v.id)
                        break
            
            # Generate speech and save to file
            engine.save_to_file(text, str(output_path))
            engine.runAndWait()
            
            logger.info(f"[StoryAudioGeneration] Generated audio using pyttsx3: {output_path}")
            return True
            
        except ImportError:
            logger.error("[StoryAudioGeneration] pyttsx3 not installed. Install with: pip install pyttsx3")
            return False
        except Exception as e:
            logger.error(f"[StoryAudioGeneration] Error generating audio with pyttsx3: {e}")
            return False
    
    def generate_scene_audio(
        self,
        scene: Dict[str, Any],
        user_id: str,
        provider: str = "gtts",
        lang: str = "en",
        slow: bool = False,
        rate: int = 150
    ) -> Dict[str, Any]:
        """
        Generate audio narration for a single story scene.
        
        Parameters:
            scene (Dict[str, Any]): Scene data with audio_narration text.
            user_id (str): Clerk user ID for subscription checking (for future usage tracking).
            provider (str): TTS provider to use ("gtts", "pyttsx3", etc.).
            lang (str): Language code for TTS (default: "en").
            slow (bool): Whether to speak slowly (default: False, gTTS only).
            rate (int): Speech rate (default: 150, pyttsx3 only).
        
        Returns:
            Dict[str, Any]: Audio metadata including file path, URL, and scene info.
        """
        scene_number = scene.get("scene_number", 0)
        scene_title = scene.get("title", "Untitled")
        audio_narration = scene.get("audio_narration", "")
        
        if not audio_narration:
            raise ValueError(f"Scene {scene_number} ({scene_title}) has no audio_narration")
        
        try:
            logger.info(f"[StoryAudioGeneration] Generating audio for scene {scene_number}: {scene_title}")
            logger.debug(f"[StoryAudioGeneration] Audio narration: {audio_narration[:100]}...")
            
            # Generate audio filename
            audio_filename = self._generate_audio_filename(scene_number, scene_title)
            audio_path = self.output_dir / audio_filename
            
            # Generate audio based on provider
            success = False
            if provider == "gtts":
                success = self._generate_audio_gtts(
                    text=audio_narration,
                    output_path=audio_path,
                    lang=lang,
                    slow=slow
                )
            elif provider == "pyttsx3":
                success = self._generate_audio_pyttsx3(
                    text=audio_narration,
                    output_path=audio_path,
                    rate=rate
                )
            else:
                # Default to gTTS
                logger.warning(f"[StoryAudioGeneration] Unknown provider '{provider}', using gTTS")
                success = self._generate_audio_gtts(
                    text=audio_narration,
                    output_path=audio_path,
                    lang=lang,
                    slow=slow
                )
            
            if not success or not audio_path.exists():
                raise RuntimeError(f"Failed to generate audio file: {audio_path}")
            
            # Get file size
            file_size = audio_path.stat().st_size
            
            logger.info(f"[StoryAudioGeneration] Saved audio to: {audio_path} ({file_size} bytes)")
            
            # Return audio metadata
            return {
                "scene_number": scene_number,
                "scene_title": scene_title,
                "audio_path": str(audio_path),
                "audio_filename": audio_filename,
                "audio_url": f"/api/story/audio/{audio_filename}",  # API endpoint to serve audio
                "provider": provider,
                "file_size": file_size,
            }
            
        except HTTPException:
            # Re-raise HTTPExceptions (e.g., 429 subscription limit)
            raise
        except Exception as e:
            logger.error(f"[StoryAudioGeneration] Error generating audio for scene {scene_number}: {e}")
            raise RuntimeError(f"Failed to generate audio for scene {scene_number}: {str(e)}") from e
    
    def generate_scene_audio_list(
        self,
        scenes: List[Dict[str, Any]],
        user_id: str,
        provider: str = "gtts",
        lang: str = "en",
        slow: bool = False,
        rate: int = 150,
        progress_callback: Optional[callable] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate audio narration for multiple story scenes.
        
        Parameters:
            scenes (List[Dict[str, Any]]): List of scene data with audio_narration text.
            user_id (str): Clerk user ID for subscription checking.
            provider (str): TTS provider to use ("gtts", "pyttsx3", etc.).
            lang (str): Language code for TTS (default: "en").
            slow (bool): Whether to speak slowly (default: False, gTTS only).
            rate (int): Speech rate (default: 150, pyttsx3 only).
            progress_callback (callable, optional): Callback function for progress updates.
        
        Returns:
            List[Dict[str, Any]]: List of audio metadata for each scene.
        """
        if not scenes:
            raise ValueError("No scenes provided for audio generation")
        
        logger.info(f"[StoryAudioGeneration] Generating audio for {len(scenes)} scenes")
        
        audio_results = []
        total_scenes = len(scenes)
        
        for idx, scene in enumerate(scenes):
            try:
                # Generate audio for scene
                audio_result = self.generate_scene_audio(
                    scene=scene,
                    user_id=user_id,
                    provider=provider,
                    lang=lang,
                    slow=slow,
                    rate=rate
                )
                
                audio_results.append(audio_result)
                
                # Call progress callback if provided
                if progress_callback:
                    progress = ((idx + 1) / total_scenes) * 100
                    progress_callback(progress, f"Generated audio for scene {scene.get('scene_number', idx + 1)}")
                
                logger.info(f"[StoryAudioGeneration] Generated audio {idx + 1}/{total_scenes}")
                
            except Exception as e:
                logger.error(f"[StoryAudioGeneration] Failed to generate audio for scene {idx + 1}: {e}")
                # Continue with next scene instead of failing completely
                # Use empty strings for required fields instead of None
                audio_results.append({
                    "scene_number": scene.get("scene_number", idx + 1),
                    "scene_title": scene.get("title", "Untitled"),
                    "audio_filename": "",
                    "audio_url": "",
                    "provider": provider,
                    "file_size": 0,
                    "error": str(e),
                })
        
        logger.info(f"[StoryAudioGeneration] Generated {len(audio_results)} audio files out of {total_scenes} scenes")
        return audio_results
    
    def generate_ai_audio(
        self,
        scene_number: int,
        scene_title: str,
        text: str,
        user_id: str,
        voice_id: str = "Wise_Woman",
        speed: float = 1.0,
        volume: float = 1.0,
        pitch: float = 0.0,
        emotion: str = "happy",
        english_normalization: bool = False,
    ) -> Dict[str, Any]:
        """
        Generate AI audio for a single scene using main_audio_generation.
        
        Parameters:
            scene_number (int): Scene number.
            scene_title (str): Scene title.
            text (str): Text to convert to speech.
            user_id (str): Clerk user ID for subscription checking.
            voice_id (str): Voice ID for AI audio generation (default: "Wise_Woman").
            speed (float): Speech speed (0.5-2.0, default: 1.0).
            volume (float): Speech volume (0.1-10.0, default: 1.0).
            pitch (float): Speech pitch (-12 to 12, default: 0.0).
            emotion (str): Emotion for speech (default: "happy").
            english_normalization (bool): Enable English text normalization for better number reading (default: False).
        
        Returns:
            Dict[str, Any]: Audio metadata including file path, URL, and scene info.
        """
        if not text or not text.strip():
            raise ValueError(f"Scene {scene_number} ({scene_title}) requires non-empty text")
        
        try:
            logger.info(f"[StoryAudioGeneration] Generating AI audio for scene {scene_number}: {scene_title}")
            logger.debug(f"[StoryAudioGeneration] Text length: {len(text)} characters, voice: {voice_id}")
            
            # Import main_audio_generation
            from services.llm_providers.main_audio_generation import generate_audio
            
            # Generate audio using main_audio_generation service
            result = generate_audio(
                text=text.strip(),
                voice_id=voice_id,
                speed=speed,
                volume=volume,
                pitch=pitch,
                emotion=emotion,
                user_id=user_id,
                english_normalization=english_normalization,
            )
            
            # Save audio to file
            audio_filename = self._generate_audio_filename(scene_number, scene_title)
            audio_path = self.output_dir / audio_filename
            
            with open(audio_path, "wb") as f:
                f.write(result.audio_bytes)
            
            logger.info(f"[StoryAudioGeneration] Saved AI audio to: {audio_path} ({result.file_size} bytes)")
            
            # Calculate cost (for response)
            character_count = result.text_length
            cost_per_1000_chars = 0.05
            cost = (character_count / 1000.0) * cost_per_1000_chars
            
            # Return audio metadata
            return {
                "scene_number": scene_number,
                "scene_title": scene_title,
                "audio_path": str(audio_path),
                "audio_filename": audio_filename,
                "audio_url": f"/api/story/audio/{audio_filename}",
                "provider": result.provider,
                "model": result.model,
                "voice_id": result.voice_id,
                "text_length": result.text_length,
                "file_size": result.file_size,
                "cost": cost,
            }
            
        except HTTPException:
            # Re-raise HTTPExceptions (e.g., 429 subscription limit)
            raise
        except Exception as e:
            logger.error(f"[StoryAudioGeneration] Error generating AI audio for scene {scene_number}: {e}")
            raise RuntimeError(f"Failed to generate AI audio for scene {scene_number}: {str(e)}") from e

