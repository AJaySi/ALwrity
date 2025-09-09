#!/usr/bin/env python3
"""
Reset Onboarding Script
Clears all onboarding progress and API keys from .env file.
Use this to start fresh with onboarding.
"""

import os
import json
from pathlib import Path
from loguru import logger

def reset_onboarding():
    """Reset all onboarding data."""
    try:
        logger.info("🔄 Starting onboarding reset...")
        
        # Get backend directory
        backend_dir = Path(__file__).parent
        env_path = backend_dir / ".env"
        progress_path = backend_dir / ".onboarding_progress.json"
        
        # Clear .env file of API keys
        if env_path.exists():
            logger.info("📝 Clearing API keys from .env file...")
            
            # Read current .env content
            with open(env_path, 'r') as f:
                lines = f.readlines()
            
            # Filter out API key lines
            api_key_vars = [
                "OPENAI_API_KEY", "GEMINI_API_KEY", "ANTHROPIC_API_KEY", 
                "MISTRAL_API_KEY", "TAVILY_API_KEY", "SERPER_API_KEY",
                "METAPHOR_API_KEY", "FIRECRAWL_API_KEY", "STABILITY_API_KEY"
            ]
            
            filtered_lines = []
            for line in lines:
                should_keep = True
                for api_var in api_key_vars:
                    if line.strip().startswith(f"{api_var}="):
                        should_keep = False
                        logger.info(f"🗑️ Removed {api_var} from .env")
                        break
                if should_keep:
                    filtered_lines.append(line)
            
            # Write back filtered content
            with open(env_path, 'w') as f:
                f.writelines(filtered_lines)
            
            logger.success("✅ API keys cleared from .env file")
        else:
            logger.info("ℹ️ No .env file found")
        
        # Clear onboarding progress file
        if progress_path.exists():
            logger.info("📝 Clearing onboarding progress...")
            os.remove(progress_path)
            logger.success("✅ Onboarding progress cleared")
        else:
            logger.info("ℹ️ No onboarding progress file found")
        
        # Clear database business info (if exists)
        db_path = backend_dir / "alwrity.db"
        if db_path.exists():
            try:
                import sqlite3
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()
                
                # Check if table exists and clear it
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='user_business_info'
                """)
                
                if cursor.fetchone():
                    cursor.execute("DELETE FROM user_business_info")
                    conn.commit()
                    logger.success("✅ Business info data cleared from database")
                else:
                    logger.info("ℹ️ No business info table found in database")
                
                conn.close()
            except Exception as e:
                logger.warning(f"⚠️ Could not clear database: {str(e)}")
        
        logger.success("🎉 Onboarding reset completed successfully!")
        logger.info("💡 You can now start a fresh onboarding process")
        
    except Exception as e:
        logger.error(f"❌ Error during onboarding reset: {str(e)}")

if __name__ == "__main__":
    reset_onboarding()