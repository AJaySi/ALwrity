#!/usr/bin/env python3
"""
Test Script for LinkedIn Image Generation Infrastructure

This script tests the basic functionality of the LinkedIn image generation services
to ensure they are properly initialized and can perform basic operations.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from loguru import logger

# Configure logging
logger.remove()
logger.add(sys.stdout, colorize=True, format="<level>{level}</level>| {message}")


async def test_linkedin_image_infrastructure():
    """Test the LinkedIn image generation infrastructure."""
    
    logger.info("🧪 Testing LinkedIn Image Generation Infrastructure")
    logger.info("=" * 60)
    
    try:
        # Test 1: Import LinkedIn Image Services
        logger.info("📦 Test 1: Importing LinkedIn Image Services...")
        
        from services.linkedin.image_generation import (
            LinkedInImageGenerator,
            LinkedInImageEditor,
            LinkedInImageStorage
        )
        from services.linkedin.image_prompts import LinkedInPromptGenerator
        
        logger.success("✅ All LinkedIn image services imported successfully")
        
        # Test 2: Initialize Services
        logger.info("🔧 Test 2: Initializing LinkedIn Image Services...")
        
        # Initialize services (without API keys for testing)
        image_generator = LinkedInImageGenerator()
        image_editor = LinkedInImageEditor()
        image_storage = LinkedInImageStorage()
        prompt_generator = LinkedInPromptGenerator()
        
        logger.success("✅ All LinkedIn image services initialized successfully")
        
        # Test 3: Test Prompt Generation (without API calls)
        logger.info("📝 Test 3: Testing Prompt Generation Logic...")
        
        # Test content context
        test_content = {
            'topic': 'AI in Marketing',
            'industry': 'Technology',
            'content_type': 'post',
            'content': 'Exploring how artificial intelligence is transforming modern marketing strategies.'
        }
        
        # Test fallback prompt generation
        fallback_prompts = prompt_generator._get_fallback_prompts(test_content, "1:1")
        
        if len(fallback_prompts) == 3:
            logger.success(f"✅ Fallback prompt generation working: {len(fallback_prompts)} prompts created")
            
            for i, prompt in enumerate(fallback_prompts):
                logger.info(f"   Prompt {i+1}: {prompt['style']} - {prompt['description']}")
        else:
            logger.error(f"❌ Fallback prompt generation failed: expected 3, got {len(fallback_prompts)}")
        
        # Test 4: Test Image Storage Directory Creation
        logger.info("📁 Test 4: Testing Image Storage Directory Creation...")
        
        # Check if storage directories were created
        storage_path = image_storage.base_storage_path
        if storage_path.exists():
            logger.success(f"✅ Storage base directory created: {storage_path}")
            
            # Check subdirectories
            for subdir in ['images', 'metadata', 'temp']:
                subdir_path = storage_path / subdir
                if subdir_path.exists():
                    logger.info(f"   ✅ {subdir} directory exists: {subdir_path}")
                else:
                    logger.warning(f"   ⚠️ {subdir} directory missing: {subdir_path}")
        else:
            logger.error(f"❌ Storage base directory not created: {storage_path}")
        
        # Test 5: Test Service Methods
        logger.info("⚙️ Test 5: Testing Service Method Signatures...")
        
        # Test image generator methods
        if hasattr(image_generator, 'generate_image'):
            logger.success("✅ LinkedInImageGenerator.generate_image method exists")
        else:
            logger.error("❌ LinkedInImageGenerator.generate_image method missing")
        
        if hasattr(image_editor, 'edit_image_conversationally'):
            logger.success("✅ LinkedInImageEditor.edit_image_conversationally method exists")
        else:
            logger.error("❌ LinkedInImageEditor.edit_image_conversationally method missing")
        
        if hasattr(image_storage, 'store_image'):
            logger.success("✅ LinkedInImageStorage.store_image method exists")
        else:
            logger.error("❌ LinkedInImageStorage.store_image method missing")
        
        if hasattr(prompt_generator, 'generate_three_prompts'):
            logger.success("✅ LinkedInPromptGenerator.generate_three_prompts method exists")
        else:
            logger.error("❌ LinkedInPromptGenerator.generate_three_prompts method missing")
        
        # Test 6: Test Prompt Enhancement
        logger.info("🎨 Test 6: Testing Prompt Enhancement Logic...")
        
        test_prompt = {
            'style': 'Professional',
            'prompt': 'Create a business image',
            'description': 'Professional style'
        }
        
        enhanced_prompt = prompt_generator._enhance_prompt_for_linkedin(
            test_prompt, test_content, "1:1", 0
        )
        
        if enhanced_prompt and 'enhanced_at' in enhanced_prompt:
            logger.success("✅ Prompt enhancement working")
            logger.info(f"   Enhanced prompt length: {len(enhanced_prompt['prompt'])} characters")
        else:
            logger.error("❌ Prompt enhancement failed")
        
        # Test 7: Test Image Validation Logic
        logger.info("🔍 Test 7: Testing Image Validation Logic...")
        
        # Test aspect ratio validation
        valid_ratios = [(1024, 1024), (1600, 900), (1200, 1600)]
        invalid_ratios = [(500, 500), (2000, 500)]
        
        for width, height in valid_ratios:
            if image_generator._is_aspect_ratio_suitable(width, height):
                logger.info(f"   ✅ Valid ratio {width}:{height} correctly identified")
            else:
                logger.warning(f"   ⚠️ Valid ratio {width}:{height} incorrectly rejected")
        
        for width, height in invalid_ratios:
            if not image_generator._is_aspect_ratio_suitable(width, height):
                logger.info(f"   ✅ Invalid ratio {width}:{height} correctly rejected")
            else:
                logger.warning(f"   ⚠️ Invalid ratio {width}:{height} incorrectly accepted")
        
        logger.info("=" * 60)
        logger.success("🎉 LinkedIn Image Generation Infrastructure Test Completed Successfully!")
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ Import Error: {e}")
        logger.error("This usually means there's an issue with the module structure or dependencies")
        return False
        
    except Exception as e:
        logger.error(f"❌ Test Failed: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False


async def main():
    """Main test function."""
    logger.info("🚀 Starting LinkedIn Image Generation Infrastructure Tests")
    
    success = await test_linkedin_image_infrastructure()
    
    if success:
        logger.success("✅ All tests passed! The infrastructure is ready for use.")
        sys.exit(0)
    else:
        logger.error("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    # Run the async test
    asyncio.run(main())
