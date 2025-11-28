"""
Content Asset Service
Service for managing and tracking all AI-generated content assets.
"""

from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from datetime import datetime
from models.content_asset_models import (
    ContentAsset,
    AssetCollection,
    AssetType,
    AssetSource
)
import logging

logger = logging.getLogger(__name__)


class ContentAssetService:
    """Service for managing content assets across all modules."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_asset(
        self,
        user_id: str,
        asset_type: AssetType,
        source_module: AssetSource,
        filename: str,
        file_url: str,
        file_path: Optional[str] = None,
        file_size: Optional[int] = None,
        mime_type: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        prompt: Optional[str] = None,
        tags: Optional[List[str]] = None,
        asset_metadata: Optional[Dict[str, Any]] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        cost: Optional[float] = None,
        generation_time: Optional[float] = None,
    ) -> ContentAsset:
        """
        Create a new content asset record.
        
        Args:
            user_id: Clerk user ID
            asset_type: Type of asset (text, image, video, audio)
            source_module: Source module that generated it
            filename: Original filename
            file_url: Public URL to access the asset
            file_path: Server file path (optional)
            file_size: File size in bytes (optional)
            mime_type: MIME type (optional)
            title: Asset title (optional)
            description: Asset description (optional)
            prompt: Generation prompt (optional)
            tags: List of tags (optional)
            asset_metadata: Additional metadata (optional)
            provider: AI provider used (optional)
            model: Model used (optional)
            cost: Generation cost (optional)
            generation_time: Generation time in seconds (optional)
        
        Returns:
            Created ContentAsset instance
        """
        try:
            asset = ContentAsset(
                user_id=user_id,
                asset_type=asset_type,
                source_module=source_module,
                filename=filename,
                file_url=file_url,
                file_path=file_path,
                file_size=file_size,
                mime_type=mime_type,
                title=title,
                description=description,
                prompt=prompt,
                tags=tags or [],
                asset_metadata=asset_metadata or {},
                provider=provider,
                model=model,
                cost=cost or 0.0,
                generation_time=generation_time,
            )
            
            self.db.add(asset)
            self.db.commit()
            self.db.refresh(asset)
            
            logger.info(f"Created asset {asset.id} for user {user_id} from {source_module.value}")
            return asset
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating asset: {str(e)}", exc_info=True)
            raise
    
    def get_user_assets(
        self,
        user_id: str,
        asset_type: Optional[AssetType] = None,
        source_module: Optional[AssetSource] = None,
        search_query: Optional[str] = None,
        tags: Optional[List[str]] = None,
        favorites_only: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> Tuple[List[ContentAsset], int]:
        """
        Get assets for a user with optional filtering.
        
        Args:
            user_id: Clerk user ID
            asset_type: Filter by asset type (optional)
            source_module: Filter by source module (optional)
            search_query: Search in title, description, prompt (optional)
            tags: Filter by tags (optional)
            favorites_only: Only return favorites (optional)
            limit: Maximum number of results
            offset: Offset for pagination
        
        Returns:
            List of ContentAsset instances
        """
        try:
            query = self.db.query(ContentAsset).filter(
                ContentAsset.user_id == user_id
            )
            
            if asset_type:
                query = query.filter(ContentAsset.asset_type == asset_type)
            
            if source_module:
                query = query.filter(ContentAsset.source_module == source_module)
            
            if favorites_only:
                query = query.filter(ContentAsset.is_favorite == True)
            
            if search_query:
                search_filter = or_(
                    ContentAsset.title.ilike(f"%{search_query}%"),
                    ContentAsset.description.ilike(f"%{search_query}%"),
                    ContentAsset.prompt.ilike(f"%{search_query}%"),
                    ContentAsset.filename.ilike(f"%{search_query}%"),
                )
                query = query.filter(search_filter)
            
            if tags:
                # Filter by tags (JSON array contains any of the tags)
                tag_filters = [ContentAsset.tags.contains([tag]) for tag in tags]
                query = query.filter(or_(*tag_filters))
            
            # Get total count before pagination
            total_count = query.count()
            
            # Apply ordering and pagination
            query = query.order_by(desc(ContentAsset.created_at))
            query = query.limit(limit).offset(offset)
            
            return query.all(), total_count
            
        except Exception as e:
            logger.error(f"Error fetching assets: {str(e)}", exc_info=True)
            raise
    
    def get_asset_by_id(self, asset_id: int, user_id: str) -> Optional[ContentAsset]:
        """Get a specific asset by ID."""
        try:
            return self.db.query(ContentAsset).filter(
                and_(
                    ContentAsset.id == asset_id,
                    ContentAsset.user_id == user_id
                )
            ).first()
        except Exception as e:
            logger.error(f"Error fetching asset {asset_id}: {str(e)}", exc_info=True)
            return None
    
    def toggle_favorite(self, asset_id: int, user_id: str) -> bool:
        """Toggle favorite status of an asset."""
        try:
            asset = self.get_asset_by_id(asset_id, user_id)
            if not asset:
                return False
            
            asset.is_favorite = not asset.is_favorite
            self.db.commit()
            return asset.is_favorite
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error toggling favorite: {str(e)}", exc_info=True)
            return False
    
    def delete_asset(self, asset_id: int, user_id: str) -> bool:
        """Delete an asset."""
        try:
            asset = self.get_asset_by_id(asset_id, user_id)
            if not asset:
                return False
            
            self.db.delete(asset)
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting asset: {str(e)}", exc_info=True)
            return False
    
    def update_asset(
        self,
        asset_id: int,
        user_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        asset_metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[ContentAsset]:
        """Update asset metadata."""
        try:
            asset = self.get_asset_by_id(asset_id, user_id)
            if not asset:
                return None
            
            if title is not None:
                asset.title = title
            if description is not None:
                asset.description = description
            if tags is not None:
                asset.tags = tags
            if asset_metadata is not None:
                asset.asset_metadata = {**(asset.asset_metadata or {}), **asset_metadata}
            
            asset.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(asset)
            
            logger.info(f"Updated asset {asset_id} for user {user_id}")
            return asset
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating asset: {str(e)}", exc_info=True)
            return None
    
    def update_asset_usage(self, asset_id: int, user_id: str, action: str = "access"):
        """Update asset usage statistics."""
        try:
            asset = self.get_asset_by_id(asset_id, user_id)
            if not asset:
                return
            
            if action == "download":
                asset.download_count += 1
            elif action == "share":
                asset.share_count += 1
            
            asset.last_accessed = datetime.utcnow()
            self.db.commit()
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating asset usage: {str(e)}", exc_info=True)
    
    def get_asset_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get statistics about user's assets."""
        try:
            total = self.db.query(func.count(ContentAsset.id)).filter(
                ContentAsset.user_id == user_id
            ).scalar() or 0
            
            by_type = self.db.query(
                ContentAsset.asset_type,
                func.count(ContentAsset.id)
            ).filter(
                ContentAsset.user_id == user_id
            ).group_by(ContentAsset.asset_type).all()
            
            by_source = self.db.query(
                ContentAsset.source_module,
                func.count(ContentAsset.id)
            ).filter(
                ContentAsset.user_id == user_id
            ).group_by(ContentAsset.source_module).all()
            
            total_cost = self.db.query(func.sum(ContentAsset.cost)).filter(
                ContentAsset.user_id == user_id
            ).scalar() or 0.0
            
            favorites_count = self.db.query(func.count(ContentAsset.id)).filter(
                and_(
                    ContentAsset.user_id == user_id,
                    ContentAsset.is_favorite == True
                )
            ).scalar() or 0
            
            return {
                "total": total,
                "by_type": {str(t): c for t, c in by_type},
                "by_source": {str(s): c for s, c in by_source},
                "total_cost": float(total_cost),
                "favorites_count": favorites_count,
            }
            
        except Exception as e:
            logger.error(f"Error getting asset statistics: {str(e)}", exc_info=True)
            return {
                "total": 0,
                "by_type": {},
                "by_source": {},
                "total_cost": 0.0,
                "favorites_count": 0,
            }

