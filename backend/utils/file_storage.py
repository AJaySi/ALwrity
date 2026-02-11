"""
File Storage Utility
Robust file storage helper for saving generated content assets.

Logging policy:
- Avoid logging absolute host paths.
- Log either a workspace-relative path (preferred) or filename-only fallback.
- Keep operation context and size metadata for debugging.
"""

import os
import uuid
from pathlib import Path
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)

# Maximum filename length
MAX_FILENAME_LENGTH = 255

# Allowed characters in filenames (alphanumeric, dash, underscore, dot)
ALLOWED_FILENAME_CHARS = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.')


def _resolve_workspace_root() -> Path:
    """Resolve configured workspace root used for safe path logging."""
    configured_root = os.getenv("ALWRITY_WORKSPACE_ROOT") or os.getenv("WORKSPACE_ROOT")
    if configured_root:
        return Path(configured_root).expanduser().resolve()
    return Path.cwd().resolve()


def _safe_log_path(path: Path) -> str:
    """Return workspace-relative path when possible, otherwise filename only."""
    workspace_root = _resolve_workspace_root()
    resolved_path = path.expanduser().resolve()
    try:
        return str(resolved_path.relative_to(workspace_root))
    except ValueError:
        return resolved_path.name


def sanitize_filename(filename: str, max_length: int = 100) -> str:
    """
    Sanitize filename to be filesystem-safe.
    
    Args:
        filename: Original filename
        max_length: Maximum length for filename
    
    Returns:
        Sanitized filename
    """
    if not filename:
        return f"file_{uuid.uuid4().hex[:8]}"
    
    # Remove path separators and other dangerous characters
    sanitized = "".join(c if c in ALLOWED_FILENAME_CHARS else '_' for c in filename)
    
    # Remove leading/trailing dots and spaces
    sanitized = sanitized.strip('. ')
    
    # Ensure it's not empty
    if not sanitized:
        sanitized = f"file_{uuid.uuid4().hex[:8]}"
    
    # Truncate if too long
    if len(sanitized) > max_length:
        name, ext = os.path.splitext(sanitized)
        max_name_length = max_length - len(ext) - 1
        sanitized = name[:max_name_length] + ext
    
    return sanitized


def ensure_directory_exists(directory: Path) -> bool:
    """
    Ensure directory exists, creating it if necessary.
    
    Args:
        directory: Path to directory
    
    Returns:
        True if directory exists or was created, False otherwise
    """
    try:
        directory.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(
            "Failed to create directory (target=%s): %s",
            _safe_log_path(directory),
            e,
        )
        return False


def save_file_safely(
    content: bytes,
    directory: Path,
    filename: str,
    max_file_size: int = 100 * 1024 * 1024  # 100MB default
) -> Tuple[Optional[Path], Optional[str]]:
    """
    Safely save file content to disk.
    
    Args:
        content: File content as bytes
        directory: Directory to save file in
        filename: Filename (will be sanitized)
        max_file_size: Maximum allowed file size in bytes
    
    Returns:
        Tuple of (file_path, error_message). file_path is None on error.
    """
    try:
        # Validate file size
        if len(content) > max_file_size:
            return None, f"File size {len(content)} exceeds maximum {max_file_size}"
        
        if len(content) == 0:
            return None, "File content is empty"
        
        # Ensure directory exists
        if not ensure_directory_exists(directory):
            return None, f"Failed to create directory: {_safe_log_path(directory)}"
        
        # Sanitize filename
        safe_filename = sanitize_filename(filename)
        
        # Construct full path
        file_path = directory / safe_filename
        
        # Check if file already exists (unlikely with UUID, but check anyway)
        if file_path.exists():
            # Add UUID to make it unique
            name, ext = os.path.splitext(safe_filename)
            safe_filename = f"{name}_{uuid.uuid4().hex[:8]}{ext}"
            file_path = directory / safe_filename
        
        # Write file atomically (write to temp file first, then rename)
        temp_path = file_path.with_suffix(file_path.suffix + '.tmp')
        try:
            with open(temp_path, 'wb') as f:
                f.write(content)
            
            # Atomic rename
            temp_path.replace(file_path)
            
            logger.info(
                "Successfully saved file (target=%s, bytes=%d, operation=binary_save)",
                _safe_log_path(file_path),
                len(content),
            )
            return file_path, None
            
        except Exception as write_error:
            # Clean up temp file if it exists
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except:
                    pass
            raise write_error
            
    except Exception as e:
        logger.error(
            "Error saving file (target=%s, bytes=%d, operation=binary_save): %s",
            _safe_log_path(directory / sanitize_filename(filename)),
            len(content) if isinstance(content, (bytes, bytearray)) else -1,
            e,
            exc_info=True,
        )
        return None, str(e)


def generate_unique_filename(
    prefix: str,
    extension: str = ".png",
    include_uuid: bool = True
) -> str:
    """
    Generate a unique filename.
    
    Args:
        prefix: Filename prefix
        extension: File extension (with or without dot)
        include_uuid: Whether to include UUID in filename
    
    Returns:
        Unique filename
    """
    if not extension.startswith('.'):
        extension = '.' + extension
    
    prefix = sanitize_filename(prefix, max_length=50)
    
    if include_uuid:
        unique_id = uuid.uuid4().hex[:8]
        return f"{prefix}_{unique_id}{extension}"
    else:
        return f"{prefix}{extension}"


def save_text_file_safely(
    content: str,
    directory: Path,
    filename: str,
    encoding: str = 'utf-8',
    max_file_size: int = 10 * 1024 * 1024  # 10MB default for text
) -> Tuple[Optional[Path], Optional[str]]:
    """
    Safely save text content to disk.
    
    Args:
        content: Text content as string
        directory: Directory to save file in
        filename: Filename (will be sanitized)
        encoding: Text encoding (default: utf-8)
        max_file_size: Maximum allowed file size in bytes
    
    Returns:
        Tuple of (file_path, error_message). file_path is None on error.
    """
    try:
        # Validate content
        if not content or not isinstance(content, str):
            return None, "Content must be a non-empty string"
        
        # Convert to bytes for size check
        content_bytes = content.encode(encoding)
        
        # Validate file size
        if len(content_bytes) > max_file_size:
            return None, f"File size {len(content_bytes)} exceeds maximum {max_file_size}"
        
        # Ensure directory exists
        if not ensure_directory_exists(directory):
            return None, f"Failed to create directory: {_safe_log_path(directory)}"
        
        # Sanitize filename
        safe_filename = sanitize_filename(filename)
        
        # Ensure .txt extension if not present
        if not safe_filename.endswith(('.txt', '.md', '.json')):
            safe_filename = os.path.splitext(safe_filename)[0] + '.txt'
        
        # Construct full path
        file_path = directory / safe_filename
        
        # Check if file already exists
        if file_path.exists():
            # Add UUID to make it unique
            name, ext = os.path.splitext(safe_filename)
            safe_filename = f"{name}_{uuid.uuid4().hex[:8]}{ext}"
            file_path = directory / safe_filename
        
        # Write file atomically (write to temp file first, then rename)
        temp_path = file_path.with_suffix(file_path.suffix + '.tmp')
        try:
            with open(temp_path, 'w', encoding=encoding) as f:
                f.write(content)
            
            # Atomic rename
            temp_path.replace(file_path)
            
            logger.info(
                "Successfully saved text file (target=%s, bytes=%d, chars=%d, operation=text_save)",
                _safe_log_path(file_path),
                len(content_bytes),
                len(content),
            )
            return file_path, None
            
        except Exception as write_error:
            # Clean up temp file if it exists
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except:
                    pass
            raise write_error
            
    except Exception as e:
        logger.error(
            "Error saving text file (target=%s, bytes=%d, operation=text_save): %s",
            _safe_log_path(directory / sanitize_filename(filename)),
            len(content.encode(encoding)) if isinstance(content, str) else -1,
            e,
            exc_info=True,
        )
        return None, str(e)
