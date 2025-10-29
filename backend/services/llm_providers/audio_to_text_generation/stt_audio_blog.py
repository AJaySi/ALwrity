import os
import re
import sys
import tempfile

from pytubefix import YouTube
from loguru import logger
from openai import OpenAI
from tqdm import tqdm
import streamlit as st

from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)  # for exponential backoff

from .gemini_audio_text import transcribe_audio

# Import APIKeyManager
from ...onboarding.api_key_manager import APIKeyManager


def progress_function(stream, chunk, bytes_remaining):
    # Calculate the percentage completion
    current = ((stream.filesize - bytes_remaining) / stream.filesize)
    progress_bar.update(current - progress_bar.n)  # Update the progress bar


def rename_file_with_underscores(file_path):
    """Rename a file by replacing spaces and special characters with underscores.

    Args:
        file_path (str): The original file path.

    Returns:
        str: The new file path with underscores.
    """
    # Extract the directory and the filename
    dir_name, original_filename = os.path.split(file_path)
    
    # Replace spaces and special characters with underscores in the filename
    new_filename = re.sub(r'[^\w\-_\.]', '_', original_filename)
    
    # Create the new file path
    new_file_path = os.path.join(dir_name, new_filename)
    
    # Rename the file
    os.rename(file_path, new_file_path)
    
    return new_file_path


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def speech_to_text(video_url):
    """
    Transcribes speech to text from a YouTube video URL using OpenAI's Whisper model.

    Args:
        video_url (str): URL of the YouTube video to transcribe.
        output_path (str, optional): Directory where the audio file will be saved. Defaults to '.'.

    Returns:
        str: The transcribed text from the video.

    Raises:
        SystemExit: If a critical error occurs that prevents successful execution.
    """
    output_path = os.getenv("CONTENT_SAVE_DIR")
    yt = None
    audio_file = None
    with st.status("Started Writing..", expanded=False) as status:
        try:
            if video_url.startswith("https://www.youtube.com/") or video_url.startswith("http://www.youtube.com/"):
                logger.info(f"Accessing YouTube URL: {video_url}")
                status.update(label=f"Accessing YouTube URL: {video_url}")
                try:
                    vid_id = video_url.split("=")[1]
                    yt = YouTube(video_url, on_progress_callback=progress_function)
                except Exception as err:
                    logger.error(f"Failed to get pytube stream object: {err}")
                    st.stop()
    
                logger.info(f"Fetching the highest quality audio stream:{yt.title}")
                status.update(label=f"Fetching the highest quality audio stream: {yt.title}")
                try:
                    audio_stream = yt.streams.filter(only_audio=True).first()
                except Exception as err:
                    logger.error(f"Failed to Download Youtube Audio: {err}")
                    st.stop()

                if audio_stream is None:
                    logger.warning("No audio stream found for this video.")
                    st.warning("No audio stream found for this video.")
                    st.stop()
    
                logger.info(f"Downloading audio for: {yt.title}")
                status.update(label=f"Downloading audio for: {yt.title}")
                global progress_bar
                progress_bar = tqdm(total=1.0, unit='iB', unit_scale=True, desc=yt.title)
                try:
                    audio_filename = re.sub(r'[^\w\-_\.]', '_', yt.title) + '.mp4'
                    audio_file = audio_stream.download(
                            output_path=os.getenv("CONTENT_SAVE_DIR"), 
                            filename=audio_filename)
                    #audio_file = rename_file_with_underscores(audio_file)
                except Exception as err:
                    logger.error(f"Failed to download audio file: {audio_file}")
    
                progress_bar.close()
                logger.info(f"Audio downloaded: {yt.title} to {audio_file}")
                status.update(label=f"Audio downloaded: {yt.title} to {output_path}")
            # Audio filepath from local directory.
            elif os.path.exists(audio_input):
                audio_file = video_url
    
            # Checking file size
            max_file_size = 24 * 1024 * 1024  # 24MB
            file_size = os.path.getsize(audio_file)
            # Convert file size to MB for logging
            file_size_MB = file_size / (1024 * 1024)  # Convert bytes to MB
    
            logger.info(f"Downloaded Audio Size is: {file_size_MB:.2f} MB")
            status.update(label=f"Downloaded Audio Size is: {file_size_MB:.2f} MB")
            
            if file_size > max_file_size:
                logger.error("File size exceeds 24MB limit.")
                # FIXME: We can chunk hour long videos, the code is not tested.
                #long_video(audio_file)
                sys.exit("File size limit exceeded.")
                st.error("Audio File size limit exceeded. File a fixme/issues at ALwrity github.")
    
            try:
                print(f"Audio File: {audio_file}")
                transcript = transcribe_audio(audio_file)
                print(f"\n\n\n--- Tracribe: {transcript}  ----\n\n\n")
                exit(1)
                status.update(label=f"Initializing OpenAI client for transcription: {audio_file}")
                logger.info(f"Initializing OpenAI client for transcription: {audio_file}")
                
                # Use APIKeyManager instead of direct environment variable access
                api_key_manager = APIKeyManager()
                api_key = api_key_manager.get_api_key("openai")
                
                if not api_key:
                    raise ValueError("OpenAI API key not found. Please configure it in the onboarding process.")
                
                client = OpenAI(api_key=api_key)
    
                logger.info("Transcribing using OpenAI's Whisper model.")
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=open(audio_file, "rb"),
                    response_format="text"
                )
                logger.info(f"\nYouTube video transcription:\n{yt.title}\n{transcript}\n")
                status.update(label=f"\nYouTube video transcription:\n{yt.title}\n{transcript}\n")
                return transcript, yt.title
    
            except Exception as e:
                logger.error(f"Failed in Whisper transcription: {e}")
                st.warning(f"Failed in Openai Whisper transcription: {e}")
                transcript = transcribe_audio(audio_file)
                print(f"\n\n\n--- Tracribe: {transcript}  ----\n\n\n")
                return transcript, yt.title
    
        except Exception as e:
            st.error(f"An error occurred during YouTube video processing: {e}")
    
        finally:
            try:
                if os.path.exists(audio_file):
                    os.remove(audio_file)
                    logger.info("Temporary audio file removed.")
            except PermissionError:
                st.error(f"Permission error: Cannot remove '{audio_file}'. Please make sure of necessary permissions.")
            except Exception as e:
                st.error(f"An error occurred removing audio file: {e}")


def long_video(temp_file_name):
    """
    Transcribes a YouTube video using OpenAI's Whisper API by processing the video in chunks.

    This function handles videos longer than the context limit of the Whisper API by dividing the video into
    10-minute segments, transcribing each segment individually, and then combining the results.

    Key Changes and Notes:
    1. Video Splitting: Splits the audio into 10-minute chunks using the moviepy library.
    2. Chunk Transcription: Each audio chunk is transcribed separately and the results are concatenated.
    3. Temporary Files for Chunks: Uses temporary files for each audio chunk for transcription.
    4. Error Handling: Exception handling is included to capture and return any errors during the process.
    5. Logging: Process steps are logged for debugging and monitoring.
    6. Cleaning Up: Removes temporary files for both the entire video and individual audio chunks after processing.

    Args:
        video_url (str): URL of the YouTube video to be transcribed.
    """
    # Extract audio and split into chunks
    logger.info(f"Processing the YT video: {temp_file_name}")
    full_audio = mp.AudioFileClip(temp_file_name)
    duration = full_audio.duration
    chunk_length = 600  # 10 minutes in seconds
    chunks = [full_audio.subclip(start, min(start + chunk_length, duration)) for start in range(0, int(duration), chunk_length)]

    combined_transcript = ""
    for i, chunk in enumerate(chunks):
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as audio_chunk_file:
            chunk.write_audiofile(audio_chunk_file.name, codec="mp3")
            with open(audio_chunk_file.name, "rb", encoding="utf-8") as audio_file:
                # Transcribe each chunk using OpenAI's Whisper API
                app.logger.info(f"Transcribing chunk {i+1}/{len(chunks)}")
                transcript = openai.Audio.transcribe("whisper-1", audio_file)
                combined_transcript += transcript['text'] + "\n\n"

            # Remove the chunk audio file
            os.remove(audio_chunk_file.name)

