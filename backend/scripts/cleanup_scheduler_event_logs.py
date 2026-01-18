#!/usr/bin/env python3
"""
Scheduler Event Logs Cleanup Script

This script manages the retention policy for scheduler event logs.
It removes old event logs based on the configured retention period.

Usage:
    python cleanup_scheduler_event_logs.py [--dry-run] [--days DAYS] [--force]

Arguments:
    --dry-run: Show what would be deleted without actually deleting
    --days DAYS: Number of days to keep (default: 90)
    --force: Skip confirmation prompts

Environment Variables:
    DATABASE_URL: Database connection string
"""

import os
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

from models.scheduler_models import SchedulerEventLog
from services.database import DATABASE_URL

def cleanup_event_logs(dry_run: bool = False, days_to_keep: int = 90, force: bool = False):
    """
    Clean up old scheduler event logs.

    Args:
        dry_run: If True, only show what would be deleted
        days_to_keep: Number of days of logs to retain
        force: Skip confirmation prompts
    """
    print(f"{'DRY RUN: ' if dry_run else ''}Cleaning up scheduler event logs older than {days_to_keep} days...")

    # Use database URL from config
    database_url = DATABASE_URL
    if not database_url:
        print("ERROR: Could not get database URL")
        return False

    # Create engine and session
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    try:
        db = SessionLocal()

        # Calculate cutoff date
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)

        # Count records before cleanup
        total_before = db.query(func.count(SchedulerEventLog.id)).scalar() or 0
        print(f"Total event logs before cleanup: {total_before}")

        # Count records that would be deleted
        to_delete_count = db.query(func.count(SchedulerEventLog.id)).filter(
            SchedulerEventLog.created_at < cutoff_date
        ).scalar() or 0

        print(f"Event logs older than {days_to_keep} days: {to_delete_count}")
        print(f"Cutoff date: {cutoff_date}")

        if to_delete_count == 0:
            print("No old event logs to clean up.")
            return True

        # Show age distribution
        print("\nAge distribution:")
        now = datetime.utcnow()
        age_ranges = [
            ("Last 24 hours", now - timedelta(hours=24)),
            ("Last 7 days", now - timedelta(days=7)),
            ("Last 30 days", now - timedelta(days=30)),
            ("Last 90 days", now - timedelta(days=90)),
            ("Older than 90 days", now - timedelta(days=90))
        ]

        for label, date_threshold in age_ranges:
            if "Older than" in label:
                count = db.query(func.count(SchedulerEventLog.id)).filter(
                    SchedulerEventLog.created_at < date_threshold
                ).scalar() or 0
            else:
                count = db.query(func.count(SchedulerEventLog.id)).filter(
                    SchedulerEventLog.created_at >= date_threshold
                ).scalar() or 0
            print(f"  {label}: {count}")

        print(f"\nWould delete {to_delete_count} event logs...")

        # Confirm deletion unless forced or dry run
        if not dry_run and not force:
            response = input(f"\nDelete {to_delete_count} old event logs? (y/N): ").strip().lower()
            if response not in ['y', 'yes']:
                print("Cleanup cancelled.")
                return False

        if not dry_run:
            # Perform the deletion
            deleted_count = db.query(SchedulerEventLog).filter(
                SchedulerEventLog.created_at < cutoff_date
            ).delete(synchronize_session=False)

            db.commit()

            # Verify the deletion
            total_after = db.query(func.count(SchedulerEventLog.id)).scalar() or 0

            print(f"\nCleanup completed:")
            print(f"  Deleted: {deleted_count} event logs")
            print(f"  Remaining: {total_after} event logs")

            return deleted_count == to_delete_count
        else:
            print("Dry run completed - no changes made.")
            return True

    except Exception as e:
        print(f"ERROR: {e}")
        if 'db' in locals():
            db.rollback()
        return False
    finally:
        if 'db' in locals():
            db.close()

def main():
    parser = argparse.ArgumentParser(description="Clean up old scheduler event logs")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be deleted without deleting")
    parser.add_argument("--days", type=int, default=90, help="Number of days to keep (default: 90)")
    parser.add_argument("--force", action="store_true", help="Skip confirmation prompts")

    args = parser.parse_args()

    if args.days < 7:
        print("ERROR: Retention period must be at least 7 days")
        sys.exit(1)

    if args.days > 365:
        print("ERROR: Retention period cannot exceed 365 days")
        sys.exit(1)

    success = cleanup_event_logs(
        dry_run=args.dry_run,
        days_to_keep=args.days,
        force=args.force
    )

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()