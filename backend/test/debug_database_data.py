#!/usr/bin/env python3
"""
Debug Database Data

This script checks what data is actually in the database for debugging.
"""

import asyncio
import sys
import os
from loguru import logger

# Add the backend directory to the path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Add the services directory to the path
services_dir = os.path.join(backend_dir, "services")
if services_dir not in sys.path:
    sys.path.insert(0, services_dir)

async def debug_database_data():
    """Debug what data is in the database."""
    
    try:
        logger.info("🔍 Debugging database data")
        
        # Initialize database
        from services.database import init_database, get_db_session
        
        try:
            init_database()
            logger.info("✅ Database initialized successfully")
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {str(e)}")
            return False
        
        # Get database session
        db_session = get_db_session()
        if not db_session:
            logger.error("❌ Failed to get database session")
            return False
        
        from services.content_planning_db import ContentPlanningDBService
        
        db_service = ContentPlanningDBService(db_session)
        
        # Check content strategies
        logger.info("📋 Checking content strategies...")
        strategies = await db_service.get_user_content_strategies(1)
        logger.info(f"Found {len(strategies)} strategies for user 1")
        
        for strategy in strategies:
            logger.info(f"Strategy ID: {strategy.id}, Name: {strategy.name}")
            logger.info(f"  Content Pillars: {strategy.content_pillars}")
            logger.info(f"  Target Audience: {strategy.target_audience}")
        
        # Check gap analyses
        logger.info("📋 Checking gap analyses...")
        gap_analyses = await db_service.get_user_content_gap_analyses(1)
        logger.info(f"Found {len(gap_analyses)} gap analyses for user 1")
        
        for gap_analysis in gap_analyses:
            logger.info(f"Gap Analysis ID: {gap_analysis.id}")
            logger.info(f"  Website URL: {gap_analysis.website_url}")
            logger.info(f"  Analysis Results: {gap_analysis.analysis_results}")
            logger.info(f"  Recommendations: {gap_analysis.recommendations}")
            logger.info(f"  Opportunities: {gap_analysis.opportunities}")
            
            # Check if analysis_results has content_gaps
            if gap_analysis.analysis_results:
                content_gaps = gap_analysis.analysis_results.get("content_gaps", [])
                logger.info(f"  Content Gaps in analysis_results: {len(content_gaps)} items")
                for gap in content_gaps:
                    logger.info(f"    - {gap}")
            else:
                logger.info("  Analysis Results is None or empty")
        
        db_session.close()
        logger.info("✅ Database debugging completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Debug failed with error: {str(e)}")
        return False

if __name__ == "__main__":
    # Configure logging
    logger.remove()
    logger.add(sys.stderr, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")
    
    # Run the debug
    success = asyncio.run(debug_database_data())
    
    if success:
        logger.info("✅ Debug completed successfully!")
        sys.exit(0)
    else:
        logger.error("❌ Debug failed!")
        sys.exit(1)
