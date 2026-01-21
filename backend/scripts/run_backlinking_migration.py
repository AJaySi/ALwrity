#!/usr/bin/env python3
"""
Run Backlinking Database Migration

This script creates all the backlinking database tables.
Run this from the backend directory.
"""

import os
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

def run_migration():
    """Run the backlinking database migration."""
    try:
        print("🚀 Starting backlinking database migration...")

        # Import database components
        from services.database import engine, Base, init_database
        from models.backlinking import (
            BacklinkingCampaign,
            BacklinkOpportunity,
            BacklinkingEmail,
            BacklinkingResponse,
            BacklinkingAnalytics,
            AILearningData,
            BacklinkingTemplate,
        )

        print("✅ Database imports successful")

        # Initialize database
        init_database()
        print("✅ Database initialized")

        # Create all backlinking tables
        print("📊 Creating backlinking tables...")
        Base.metadata.create_all(engine)
        print("✅ Backlinking tables created successfully!")

        # List created tables
        print("\n📋 Created tables:")
        tables = [
            'backlinking_campaigns',
            'backlinking_opportunities',
            'backlinking_emails',
            'backlinking_responses',
            'backlinking_analytics',
            'ai_learning_data',
            'backlinking_templates'
        ]

        for table in tables:
            print(f"  ✓ {table}")

        print("\n🎉 Migration completed successfully!")
        print("You can now use the AI Backlinking feature with real database persistence.")

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    run_migration()