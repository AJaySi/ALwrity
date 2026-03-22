"""
Utility functions for the AI Story Illustrator module.

This module provides helper functions for file operations, string manipulation,
and simple text analysis relevant to story processing.
"""

import os
import re
import tempfile
import uuid
import logging
import shutil
from pathlib import Path
from typing import List, Tuple, Optional, Union

# Attempt to import Pillow for image dimensions, but don't fail if not installed
# unless the specific function is called.
try:
    from PIL import Image
    _PIL_AVAILABLE = True
except ImportError:
    _PIL_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger('story_illustrator_utils')

# --- Constants ---
IMAGE_EXTENSIONS = frozenset(['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'])
TEXT_EXTENSIONS = frozenset(['.txt', '.md', '.text'])
# Common English words that often start sentences, excluded from simple name detection
COMMON_START_WORDS = frozenset([
    'The', 'A', 'An', 'And', 'But', 'Or', 'For', 'Nor', 'So', 'Yet', 'He', 'She',
    'It', 'They', 'We', 'You', 'I', 'In', 'On', 'At', 'To', 'From', 'With',
    'About', 'As', 'Is', 'Was', 'Were', 'Be', 'Been', 'Being', 'Have', 'Has',
    'Had', 'Do', 'Does', 'Did', 'Will', 'Would', 'Shall', 'Should', 'May',
    'Might', 'Must', 'Can', 'Could'
])


# --- File/Directory Operations ---

def create_temp_directory(prefix: str = "story_illustrator_") -> str:
    """
    Creates a temporary directory using tempfile.mkdtemp.

    Args:
        prefix: A prefix for the temporary directory name.

    Returns:
        The absolute path to the created temporary directory.
    """
    try:
        temp_dir = tempfile.mkdtemp(prefix=prefix)
        logger.info(f"Created temporary directory: {temp_dir}")
        return temp_dir
    except Exception as e:
        logger.error(f"Failed to create temporary directory: {e}", exc_info=True)
        raise  # Re-raise the exception after logging


def sanitize_filename(filename: str) -> str:
    """
    Sanitizes a filename by removing/replacing invalid characters for common filesystems.

    Args:
        filename: The original filename string.

    Returns:
        A sanitized filename string suitable for use in file paths.
    """
    if not isinstance(filename, str):
        logger.warning("sanitize_filename received non-string input, converting.")
        filename = str(filename)

    # Remove characters invalid for Windows/Unix filenames
    # Replace them with an underscore.
    sanitized = re.sub(r'[\\/*?:"<>|\']', "_", filename)
    # Replace consecutive underscores/spaces with a single underscore
    sanitized = re.sub(r'[_ ]+', '_', sanitized)
    # Remove leading/trailing spaces, dots, and underscores
    sanitized = sanitized.strip("._ ")

    # Ensure the filename is not empty after sanitization
    if not sanitized:
        sanitized = "unnamed_file"
        logger.warning("Filename was empty after sanitization, using default.")

    # Limit filename length (optional, adjust as needed)
    # max_len = 255 # Example limit
    # if len(sanitized) > max_len:
    #     name, ext = os.path.splitext(sanitized)
    #     sanitized = name[:max_len - len(ext) - 1] + "_" + ext
    #     logger.warning(f"Filename truncated to maximum length: {sanitized}")

    return sanitized


def get_temp_file_path(
    directory: str, prefix: str = "file_", suffix: str = ".tmp"
) -> str:
    """
    Generates a unique temporary file path within the specified directory.

    Args:
        directory: The directory where the temporary file should be located.
        prefix: A prefix for the filename.
        suffix: A suffix (extension) for the filename.

    Returns:
        The full path for the unique temporary file.
    """
    # Ensure suffix starts with a dot if it's meant to be an extension
    if suffix and not suffix.startswith("."):
        suffix = "." + suffix

    unique_id = uuid.uuid4().hex[:12] # Longer hex UUID for better uniqueness
    filename = f"{prefix}{unique_id}{suffix}"
    return os.path.join(directory, filename)


def ensure_directory_exists(directory: Union[str, Path]) -> str:
    """
    Ensures that a directory exists, creating it recursively if necessary.

    Args:
        directory: The path to the directory (string or Path object).

    Returns:
        The absolute path to the directory as a string.

    Raises:
        OSError: If the directory cannot be created (e.g., permission issues).
    """
    dir_path = Path(directory).resolve() # Use Pathlib for robust handling
    try:
        dir_path.mkdir(parents=True, exist_ok=True)
        # Log only if it needed creation (or if verbose logging is on)
        # logger.info(f"Ensured directory exists: {dir_path}")
        return str(dir_path)
    except OSError as e:
        logger.error(f"Failed to create or access directory {dir_path}: {e}", exc_info=True)
        raise


def cleanup_directory(directory: Union[str, Path]) -> None:
    """
    Removes a directory and all its contents recursively. Handles errors gracefully.

    Args:
        directory: The path to the directory to remove (string or Path object).
    """
    dir_path = Path(directory)
    if not dir_path.exists():
        logger.debug(f"Cleanup skipped: Directory '{directory}' does not exist.")
        return

    if not dir_path.is_dir():
         logger.warning(f"Cleanup warning: Path '{directory}' is not a directory.")
         return

    try:
        shutil.rmtree(dir_path)
        logger.info(f"Successfully removed directory: {directory}")
    except OSError as e:
        logger.error(f"Error removing directory {directory}: {e}", exc_info=True)
    except Exception as e:
        logger.error(
            f"Unexpected error removing directory {directory}: {e}", exc_info=True
        )


# --- File Type Checks ---

def get_file_extension(file_path: Union[str, Path]) -> str:
    """
    Gets the lowercased file extension (including the dot) from a file path.

    Args:
        file_path: The path to the file (string or Path object).

    Returns:
        The file extension (e.g., '.txt', '.png') or an empty string if no extension.
    """
    return Path(file_path).suffix.lower()


def is_image_file(file_path: Union[str, Path]) -> bool:
    """
    Checks if a file is likely an image based on its extension.

    Args:
        file_path: The path to the file (string or Path object).

    Returns:
        True if the file extension is in IMAGE_EXTENSIONS, False otherwise.
    """
    return get_file_extension(file_path) in IMAGE_EXTENSIONS


def is_text_file(file_path: Union[str, Path]) -> bool:
    """
    Checks if a file is likely a text file based on its extension.

    Args:
        file_path: The path to the file (string or Path object).

    Returns:
        True if the file extension is in TEXT_EXTENSIONS, False otherwise.
    """
    return get_file_extension(file_path) in TEXT_EXTENSIONS


# --- Text Analysis (Simple Heuristics) ---

def extract_story_title_from_text(text: str) -> str:
    """
    Attempts to extract a title from story text using simple heuristics.

    Looks for patterns (in order):
    1. Markdown headers (#, ##, etc.) at the start of a line.
    2. The first non-empty line if it's short (< 100 chars) and followed by
       a blank line or is the only line.
    3. The first non-empty line if it's entirely in uppercase (< 100 chars).

    Args:
        text: The story text content.

    Returns:
        An extracted title string, or "Untitled Story" if no pattern matches.
    """
    if not isinstance(text, str) or not text.strip():
        return "Untitled Story"

    # 1. Check for markdown headers ( # Title, ## Title )
    # Needs to match start of line (^) with optional whitespace before #
    header_match = re.search(r'^\s*#+\s+(.+)$', text.strip(), re.MULTILINE)
    if header_match:
        title = header_match.group(1).strip()
        if title: return title

    lines = text.strip().split('\n')
    if not lines:
        return "Untitled Story"

    first_line = lines[0].strip()
    if not first_line: # Skip if first line is blank
        if len(lines) > 1:
            first_line = lines[1].strip() # Try second line
        else:
            return "Untitled Story"

    if not first_line: # Still no title found
         return "Untitled Story"

    # 2. Check if first line is short and potentially a title
    is_short = len(first_line) < 100
    is_followed_by_blank = len(lines) > 1 and not lines[1].strip()
    is_only_line = len(lines) == 1

    if is_short and (is_followed_by_blank or is_only_line):
        return first_line

    # 3. Check if first line is all caps (and short)
    is_all_caps = first_line == first_line.upper() and first_line.isalpha() # Check if it contains letters
    if is_short and is_all_caps:
        return first_line

    # Default if no other pattern matched
    return "Untitled Story"


def estimate_reading_time(text: str, words_per_minute: int = 200) -> float:
    """
    Estimates the reading time of a text in minutes.

    Args:
        text: The text content.
        words_per_minute: The assumed average reading speed.

    Returns:
        The estimated reading time in minutes. Returns 0.0 for empty text.
    """
    if not isinstance(text, str) or not text.strip():
        return 0.0
    if words_per_minute <= 0:
        raise ValueError("words_per_minute must be positive.")

    word_count = len(text.split())
    minutes = word_count / words_per_minute
    return minutes


def count_sentences(text: str) -> int:
    """
    Counts the number of sentences in a text using a very simple heuristic.

    Note: This is a basic implementation counting sentence-ending punctuation
    (. ! ?). It will be inaccurate with abbreviations (Mr., Mrs., etc.),
    ellipses, and complex sentence structures.

    Args:
        text: The text content.

    Returns:
        An estimated count of sentences. Returns 0 for empty text.
    """
    if not isinstance(text, str) or not text.strip():
        return 0

    # Find sequences of one or more sentence-ending punctuation marks
    sentence_endings = re.findall(r'[.!?]+', text)
    count = len(sentence_endings)

    # Handle edge case where text might not end with punctuation but isn't empty
    if count == 0 and len(text.strip()) > 0:
        return 1 # Assume at least one sentence if text exists but no terminators found
    return count


def extract_character_names(text: str, min_occurrences: int = 2) -> List[str]:
    """
    Attempts to extract potential character names from story text.

    Note: This is a simple heuristic based on finding capitalized words
    (excluding common sentence starters) that appear multiple times. It has
    limitations and may produce false positives or miss actual names.

    Args:
        text: The story text content.
        min_occurrences: The minimum number of times a capitalized word must
                         appear to be considered a potential name.

    Returns:
        A list of potential character name strings.
    """
    if not isinstance(text, str) or not text.strip():
        return []
    if min_occurrences < 1:
        min_occurrences = 1 # Ensure at least one occurrence is required

    # Find words starting with an uppercase letter, potentially followed by lowercase
    # Allows for single-letter names like 'X' but focuses on typical Name structure
    capitalized_words = re.findall(r'\b[A-Z][a-zA-Z]*\b', text)

    # Count occurrences, excluding common words
    word_counts: Dict[str, int] = {}
    for word in capitalized_words:
        if word not in COMMON_START_WORDS:
            word_counts[word] = word_counts.get(word, 0) + 1

    # Filter for words that meet the minimum occurrence threshold
    potential_names = [
        word for word, count in word_counts.items() if count >= min_occurrences
    ]

    # Sort for consistency (optional)
    potential_names.sort()

    return potential_names


def extract_setting_details(text: str) -> List[str]:
    """
    Attempts to extract potential setting details using simple regex patterns.

    Note: This is a very basic heuristic looking for common prepositional
    phrases (e.g., "in the forest", "at the castle"). It is highly limited
    and likely to miss many setting details or extract irrelevant phrases.

    Args:
        text: The story text content.

    Returns:
        A list of potential setting phrases found.
    """
    if not isinstance(text, str) or not text.strip():
        return []

    # Patterns looking for prepositions followed by nouns/adjectives
    # Making patterns slightly more general:
    # (\b\w+\b) captures single words
    # (\b\w+\s+\w+\b) captures two-word phrases
    # (\b[A-Z]\w*\b) captures capitalized words (potential proper nouns)
    setting_patterns = [
        r'\b(?:in|on|at|near|beside|inside|outside|under|over|through)\s+(?:the|a|an)\s+((?:[A-Z]\w*|\w+)(?:\s+\w+){0,2})\b', # e.g., in the old house
        r'\b(?:in|on|at)\s+((?:[A-Z]\w+)(?:\s+[A-Z]\w+)*)\b', # e.g., in New York City
        r'\b(?:during|before|after)\s+(?:the|a|an)\s+(\w+(?:\s+\w+){0,2})\b', # e.g., during the storm
    ]

    settings_found = set() # Use a set to avoid duplicates
    for pattern in setting_patterns:
        try:
            matches = re.findall(pattern, text, re.IGNORECASE) # Ignore case
            for match in matches:
                 # If match is tuple due to multiple capture groups, join them?
                 # For these patterns, it should be single strings.
                 if isinstance(match, str):
                      phrase = match.strip()
                      if phrase and len(phrase.split()) <= 5: # Limit phrase length
                           settings_found.add(phrase)
        except re.error as e:
             logger.warning(f"Regex error in extract_setting_details: {e} with pattern: {pattern}")


    # Convert set back to list and sort for consistency
    sorted_settings = sorted(list(settings_found))
    return sorted_settings


# --- Image Operations ---

def get_image_dimensions(image_path: Union[str, Path]) -> Optional[Tuple[int, int]]:
    """
    Gets the (width, height) dimensions of an image file using Pillow.

    Args:
        image_path: The path to the image file (string or Path object).

    Returns:
        A tuple (width, height) if successful, or None if the file is not
        a valid image, Pillow is not installed, or an error occurs.
    """
    if not _PIL_AVAILABLE:
        logger.warning("Pillow (PIL) library not installed. Cannot get image dimensions.")
        return None

    img_path = Path(image_path)
    if not img_path.is_file():
        logger.error(f"Image file not found or is not a file: {image_path}")
        return None

    try:
        with Image.open(img_path) as img:
            width, height = img.size
            logger.debug(f"Dimensions for {image_path}: {width}x{height}")
            return width, height
    except FileNotFoundError:
        logger.error(f"Image file not found at path: {image_path}")
        return None
    except UnidentifiedImageError: # Specific Pillow error for invalid images
         logger.error(f"Could not identify image file (invalid format or corrupted): {image_path}")
         return None
    except Exception as e:
        logger.error(f"Error getting dimensions for image {image_path}: {e}", exc_info=True)
        return None