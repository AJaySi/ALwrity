"""
Renewal History Retention Service
Manages retention policies for subscription renewal history records.

Retention Policy:
- 0-12 months: Full records with usage snapshots
- 12-24 months: Full records (compressed/removed usage snapshots)
- 24-84 months: Summary records (no usage snapshots, payment data only)
- 84+ months: Mark for archive (payment data preserved indefinitely)
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from loguru import logger
import json

from models.subscription_models import SubscriptionRenewalHistory


class RenewalHistoryRetentionService:
    """Service for managing renewal history retention policies."""
    
    # Retention periods (in days)
    COMPRESS_SNAPSHOT_DAYS = 365  # 12 months - compress/remove usage snapshots
    SUMMARY_RECORDS_DAYS = 730  # 24 months - create summary records
    ARCHIVE_DAYS = 2555  # 84 months (7 years) - mark for archive
    
    def __init__(self, db: Session):
        self.db = db
    
    def check_and_apply_retention(self, user_id: str) -> Dict[str, Any]:
        """
        Check and apply retention policies for renewal history.
        
        Applies retention in stages:
        1. Compress usage snapshots for records 12-24 months old
        2. Create summary records for records 24-84 months old
        3. Mark records older than 84 months for archive
        
        Returns:
            Dict with retention status and statistics
        """
        try:
            now = datetime.utcnow()
            compress_cutoff = now - timedelta(days=self.COMPRESS_SNAPSHOT_DAYS)
            summary_cutoff = now - timedelta(days=self.SUMMARY_RECORDS_DAYS)
            archive_cutoff = now - timedelta(days=self.ARCHIVE_DAYS)
            
            # Count records in each retention tier
            total_count = self.db.query(func.count(SubscriptionRenewalHistory.id)).filter(
                SubscriptionRenewalHistory.user_id == user_id
            ).scalar() or 0
            
            records_to_compress = self.db.query(SubscriptionRenewalHistory).filter(
                SubscriptionRenewalHistory.user_id == user_id,
                SubscriptionRenewalHistory.created_at < compress_cutoff,
                SubscriptionRenewalHistory.created_at >= summary_cutoff,
                SubscriptionRenewalHistory.usage_before_renewal.isnot(None)  # Has snapshot to compress
            ).all()
            
            records_to_summarize = self.db.query(SubscriptionRenewalHistory).filter(
                SubscriptionRenewalHistory.user_id == user_id,
                SubscriptionRenewalHistory.created_at < summary_cutoff,
                SubscriptionRenewalHistory.created_at >= archive_cutoff,
                SubscriptionRenewalHistory.usage_before_renewal.isnot(None)  # Has snapshot to remove
            ).all()
            
            records_to_archive = self.db.query(SubscriptionRenewalHistory).filter(
                SubscriptionRenewalHistory.user_id == user_id,
                SubscriptionRenewalHistory.created_at < archive_cutoff
            ).all()
            
            # Apply retention policies
            compressed_count = self._compress_usage_snapshots(records_to_compress)
            summarized_count = self._create_summary_records(records_to_summarize)
            archived_count = self._mark_for_archive(records_to_archive)
            
            total_processed = compressed_count + summarized_count + archived_count
            
            if total_processed == 0:
                return {
                    'retention_applied': False,
                    'total_records': total_count,
                    'records_to_compress': len(records_to_compress),
                    'records_to_summarize': len(records_to_summarize),
                    'records_to_archive': len(records_to_archive),
                    'message': 'No records require retention processing'
                }
            
            self.db.commit()
            
            logger.info(
                f"[RenewalRetention] Applied retention for user {user_id}: "
                f"{compressed_count} compressed, {summarized_count} summarized, "
                f"{archived_count} archived"
            )
            
            return {
                'retention_applied': True,
                'total_records': total_count,
                'compressed_count': compressed_count,
                'summarized_count': summarized_count,
                'archived_count': archived_count,
                'total_processed': total_processed,
                'message': f'Processed {total_processed} records: {compressed_count} compressed, {summarized_count} summarized, {archived_count} archived'
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"[RenewalRetention] Error applying retention for user {user_id}: {e}", exc_info=True)
            return {
                'retention_applied': False,
                'error': str(e),
                'message': f'Error applying retention: {str(e)}'
            }
    
    def _compress_usage_snapshots(self, records: List[SubscriptionRenewalHistory]) -> int:
        """
        Compress usage snapshots for records 12-24 months old.
        
        Strategy: Replace detailed JSON snapshot with summary statistics only.
        Keeps only essential metrics: total_calls, total_tokens, total_cost.
        """
        compressed = 0
        for record in records:
            if record.usage_before_renewal:
                try:
                    usage_data = record.usage_before_renewal
                    
                    # Handle both dict (SQLAlchemy JSON) and string formats
                    if isinstance(usage_data, str):
                        try:
                            usage_data = json.loads(usage_data)
                        except json.JSONDecodeError:
                            # If it's not valid JSON, remove it
                            record.usage_before_renewal = None
                            compressed += 1
                            continue
                    elif not isinstance(usage_data, dict):
                        # If it's not a dict or string, remove it
                        record.usage_before_renewal = None
                        compressed += 1
                        continue
                    
                    # Check if already compressed (has 'compressed_at' key)
                    if isinstance(usage_data, dict) and 'compressed_at' in usage_data:
                        # Already compressed, skip
                        continue
                    
                    # Create compressed summary (keep only key metrics)
                    compressed_summary = {
                        'total_calls': usage_data.get('total_calls', 0),
                        'total_tokens': usage_data.get('total_tokens', 0),
                        'total_cost': usage_data.get('total_cost', 0.0),
                        'compressed_at': datetime.utcnow().isoformat(),
                        'note': 'Usage snapshot compressed after 12 months'
                    }
                    
                    record.usage_before_renewal = compressed_summary
                    compressed += 1
                    
                except (TypeError, AttributeError, KeyError) as e:
                    logger.warning(f"[RenewalRetention] Failed to compress snapshot for record {record.id}: {e}")
                    # If compression fails, remove snapshot entirely
                    record.usage_before_renewal = None
                    compressed += 1
        
        return compressed
    
    def _create_summary_records(self, records: List[SubscriptionRenewalHistory]) -> int:
        """
        Create summary records for records 24-84 months old.
        
        Strategy: Remove usage snapshots, keep only payment and subscription data.
        """
        summarized = 0
        for record in records:
            if record.usage_before_renewal is not None:
                # Remove usage snapshot, keep payment and subscription data
                record.usage_before_renewal = None
                summarized += 1
        
        return summarized
    
    def _mark_for_archive(self, records: List[SubscriptionRenewalHistory]) -> int:
        """
        Mark records older than 84 months for archive.
        
        Strategy: Ensure usage snapshots are removed, payment data is preserved.
        Note: In future, these could be moved to an archive table.
        """
        archived = 0
        for record in records:
            # Ensure usage snapshot is removed (should already be done)
            if record.usage_before_renewal is not None:
                record.usage_before_renewal = None
                archived += 1
            else:
                # Already processed, just count
                archived += 1
        
        return archived
    
    def get_retention_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Get retention statistics for a user's renewal history.
        
        Returns breakdown by retention tier.
        """
        try:
            now = datetime.utcnow()
            compress_cutoff = now - timedelta(days=self.COMPRESS_SNAPSHOT_DAYS)
            summary_cutoff = now - timedelta(days=self.SUMMARY_RECORDS_DAYS)
            archive_cutoff = now - timedelta(days=self.ARCHIVE_DAYS)
            
            total = self.db.query(func.count(SubscriptionRenewalHistory.id)).filter(
                SubscriptionRenewalHistory.user_id == user_id
            ).scalar() or 0
            
            recent = self.db.query(func.count(SubscriptionRenewalHistory.id)).filter(
                SubscriptionRenewalHistory.user_id == user_id,
                SubscriptionRenewalHistory.created_at >= compress_cutoff
            ).scalar() or 0
            
            to_compress = self.db.query(func.count(SubscriptionRenewalHistory.id)).filter(
                SubscriptionRenewalHistory.user_id == user_id,
                SubscriptionRenewalHistory.created_at < compress_cutoff,
                SubscriptionRenewalHistory.created_at >= summary_cutoff,
                SubscriptionRenewalHistory.usage_before_renewal.isnot(None)
            ).scalar() or 0
            
            to_summarize = self.db.query(func.count(SubscriptionRenewalHistory.id)).filter(
                SubscriptionRenewalHistory.user_id == user_id,
                SubscriptionRenewalHistory.created_at < summary_cutoff,
                SubscriptionRenewalHistory.created_at >= archive_cutoff,
                SubscriptionRenewalHistory.usage_before_renewal.isnot(None)
            ).scalar() or 0
            
            to_archive = self.db.query(func.count(SubscriptionRenewalHistory.id)).filter(
                SubscriptionRenewalHistory.user_id == user_id,
                SubscriptionRenewalHistory.created_at < archive_cutoff
            ).scalar() or 0
            
            return {
                'total_records': total,
                'recent_records': recent,  # 0-12 months
                'records_to_compress': to_compress,  # 12-24 months
                'records_to_summarize': to_summarize,  # 24-84 months
                'records_to_archive': to_archive,  # 84+ months
                'retention_policy': {
                    'compress_after_days': self.COMPRESS_SNAPSHOT_DAYS,
                    'summarize_after_days': self.SUMMARY_RECORDS_DAYS,
                    'archive_after_days': self.ARCHIVE_DAYS
                }
            }
            
        except Exception as e:
            logger.error(f"[RenewalRetention] Error getting retention stats for user {user_id}: {e}", exc_info=True)
            return {
                'error': str(e),
                'total_records': 0
            }
