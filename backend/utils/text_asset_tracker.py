"""
Text Asset Tracker Utility
Helper utility for saving and tracking text content as files in the asset library.
"""

from typing import Dict, Any, Optional
from pathlib import Path
from sqlalchemy.orm import Session
from utils.asset_tracker import save_asset_to_library
from utils.file_storage import save_text_file_safely, generate_unique_filename, sanitize_filename
import logging

logger = logging.getLogger(__name__)


def save_and_track_text_content(
    db: Session,
    user_id: str,
    content: str,
    source_module: str,
    title: str,
    description: Optional[str] = None,
    prompt: Optional[str] = None,
    tags: Optional[list] = None,
    asset_metadata: Optional[Dict[str, Any]] = None,
    base_dir: Optional[Path] = None,
    subdirectory: Optional[str] = None,
    file_extension: str = ".txt"
) -> Optional[int]:
    """
    Save text content to disk and track it in the asset library.
    
    Args:
        db: Database session
        user_id: Clerk user ID
        content: Text content to save
        source_module: Source module name (e.g., "linkedin_writer", "facebook_writer")
        title: Title for the asset
        description: Description of the content
        prompt: Original prompt used for generation
        tags: List of tags for search/filtering
        asset_metadata: Additional metadata
        base_dir: Base directory for file storage (defaults to backend/{module}_text)
        subdirectory: Optional subdirectory (e.g., "posts", "articles")
        file_extension: File extension (.txt, .md, etc.)
    
    Returns:
        Asset ID if successful, None otherwise
    """
    try:
        if not content or not isinstance(content, str) or len(content.strip()) == 0:
            logger.warning("Empty or invalid content provided")
            return None
        
        if not user_id or not isinstance(user_id, str):
            logger.error("Invalid user_id provided")
            return None
        
        # Determine output directory
        if base_dir is None:
            try:
                # Try to get user workspace path
                from services.user_workspace_manager import UserWorkspaceManager
                workspace_manager = UserWorkspaceManager(db)
                workspace_info = workspace_manager.get_user_workspace(user_id)
                
                if workspace_info and workspace_info.get('workspace_path'):
                    user_workspace_path = Path(workspace_info['workspace_path'])
                    # Use 'media' subdirectory in workspace
                    # Structure: workspace/users/user_{id}/media/{module}_text
                    module_name = source_module.replace('_', '')
                    output_dir = user_workspace_path / "media" / f"{module_name}_text"
                else:
                    # Fallback to root/data/media directory if workspace not found
                    logger.warning(f"Workspace not found for user {user_id}, using default directory")
                    base_dir = Path(__file__).resolve().parents[2]  # root
                    module_name = source_module.replace('_', '')
                    output_dir = base_dir / "data" / "media" / f"{module_name}_text"
            except Exception as e:
                logger.error(f"Error resolving workspace path: {e}")
                # Fallback
                base_dir = Path(__file__).resolve().parents[2]  # root
                module_name = source_module.replace('_', '')
                output_dir = base_dir / "data" / "media" / f"{module_name}_text"
        else:
            output_dir = base_dir
        
        # Add subdirectory if specified
        if subdirectory:
            output_dir = output_dir / subdirectory
        
        # Generate safe filename from title
        safe_title = sanitize_filename(title, max_length=80)
        filename = generate_unique_filename(
            prefix=safe_title,
            extension=file_extension,
            include_uuid=True
        )
        
        # Save text file
        file_path, save_error = save_text_file_safely(
            content=content,
            directory=output_dir,
            filename=filename,
            encoding='utf-8',
            max_file_size=10 * 1024 * 1024  # 10MB for text
        )
        
        if not file_path or save_error:
            logger.error(f"Failed to save text file: {save_error}")
            return None
        
        # Generate file URL
        if base_dir:
            try:
                relative_path = file_path.relative_to(base_dir)
                file_url = f"/api/text-assets/{relative_path.as_posix()}"
            except ValueError:
                 # If file_path is not relative to base_dir (shouldn't happen if logic is correct, but safe fallback)
                 logger.warning(f"File path {file_path} is not relative to base_dir {base_dir}")
                 file_url = f"/api/text-assets/{file_path.name}"
        else:
             file_url = f"/api/text-assets/{file_path.name}"
        
        # Prepare metadata
        final_metadata = asset_metadata or {}
        final_metadata.update({
            "status": "completed",
            "character_count": len(content),
            "word_count": len(content.split())
        })
        
        # Save to asset library
        asset_id = save_asset_to_library(
            db=db,
            user_id=user_id,
            asset_type="text",
            source_module=source_module,
            filename=filename,
            file_url=file_url,
            file_path=str(file_path),
            file_size=len(content.encode('utf-8')),
            mime_type="text/plain" if file_extension == ".txt" else "text/markdown",
            title=title,
            description=description or f"Generated {source_module.replace('_', ' ')} content",
            prompt=prompt,
            tags=tags or [source_module, "text"],
            asset_metadata=final_metadata
        )
        
        if asset_id:
            logger.info(f"✅ Text asset saved to library: ID={asset_id}, filename={filename}")
        else:
            logger.warning(f"Asset tracking returned None for {filename}")
        
        return asset_id
        
    except Exception as e:
        logger.error(f"❌ Error saving and tracking text content: {str(e)}", exc_info=True)
        return None

