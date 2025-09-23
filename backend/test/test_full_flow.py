#!/usr/bin/env python3
"""
Test the full 12-step calendar generation process to verify Step 5 fix.
"""

import asyncio
import time
from loguru import logger
import sys
import os

# Add the backend directory to the path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from services.calendar_generation_datasource_framework.prompt_chaining.orchestrator import PromptChainOrchestrator

async def test_full_12_step_process():
    """Test the complete 12-step process to verify Step 5 fix."""
    try:
        logger.info("🧪 Testing full 12-step calendar generation process")
        
        # Create orchestrator
        logger.info("✅ Creating orchestrator...")
        orchestrator = PromptChainOrchestrator()
        
        # Test parameters
        user_id = 1
        strategy_id = 1
        calendar_type = "monthly"
        industry = "technology"
        business_size = "sme"
        
        logger.info(f"🎯 Starting calendar generation for user {user_id}, strategy {strategy_id}")
        logger.info(f"📋 Parameters: {calendar_type}, {industry}, {business_size}")
        
        # Start the full process
        start_time = time.time()
        
        # Generate calendar using the orchestrator's main method
        logger.info("🚀 Executing full 12-step process...")
        final_calendar = await orchestrator.generate_calendar(
            user_id=user_id,
            strategy_id=strategy_id,
            calendar_type=calendar_type,
            industry=industry,
            business_size=business_size
        )
        
        # Extract context from the result for analysis
        context = {
            "step_results": final_calendar.get("step_results", {}),
            "quality_scores": final_calendar.get("quality_scores", {})
        }
        
        execution_time = time.time() - start_time
        
        logger.info(f"✅ Full 12-step process completed in {execution_time:.2f} seconds")
        
        # Analyze results
        step_results = context.get("step_results", {})
        quality_scores = context.get("quality_scores", {})
        
        logger.info("📊 Step Results Analysis:")
        logger.info(f"   Total steps executed: {len(step_results)}")
        
        # Check each step
        for step_key in sorted(step_results.keys()):
            step_result = step_results[step_key]
            status = step_result.get("status", "unknown")
            quality_score = step_result.get("quality_score", 0.0)
            validation_passed = step_result.get("validation_passed", False)
            
            logger.info(f"   {step_key}: status={status}, quality={quality_score:.2f}, validation_passed={validation_passed}")
            
            if status == "failed" or status == "error":
                logger.error(f"   ❌ {step_key} failed with status: {status}")
                error_message = step_result.get("error_message", "No error message")
                logger.error(f"   Error: {error_message}")
        
        # Check Step 5 specifically
        step_05_result = step_results.get("step_05", {})
        if step_05_result:
            step_05_status = step_05_result.get("status", "unknown")
            step_05_quality = step_05_result.get("quality_score", 0.0)
            step_05_validation = step_05_result.get("validation_passed", False)
            
            logger.info(f"🎯 Step 5 Analysis:")
            logger.info(f"   Status: {step_05_status}")
            logger.info(f"   Quality Score: {step_05_quality:.2f}")
            logger.info(f"   Validation Passed: {step_05_validation}")
            
            if step_05_status == "completed" and step_05_validation:
                logger.info("✅ Step 5 FIX VERIFIED - Working correctly in full process!")
            else:
                logger.error("❌ Step 5 still has issues in full process")
        else:
            logger.error("❌ Step 5 result not found in step_results")
        
        # Overall quality
        overall_quality = sum(quality_scores.values()) / len(quality_scores) if quality_scores else 0.0
        logger.info(f"📊 Overall Quality Score: {overall_quality:.2f}")
        
        # Success criteria
        completed_steps = sum(1 for result in step_results.values() if result.get("status") == "completed")
        total_steps = len(step_results)
        
        logger.info(f"📊 Process Summary:")
        logger.info(f"   Completed Steps: {completed_steps}/{total_steps}")
        logger.info(f"   Success Rate: {(completed_steps/total_steps)*100:.1f}%")
        logger.info(f"   Overall Quality: {overall_quality:.2f}")
        
        if completed_steps == total_steps and overall_quality > 0.8:
            logger.info("🎉 SUCCESS: Full 12-step process completed successfully!")
            return True
        else:
            logger.error("❌ FAILURE: Full 12-step process had issues")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error in full 12-step process test: {str(e)}")
        import traceback
        logger.error(f"📋 Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    # Configure logging
    logger.remove()
    logger.add(sys.stderr, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")
    
    # Run the test
    success = asyncio.run(test_full_12_step_process())
    
    if success:
        print("\n🎉 Test completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Test failed!")
        sys.exit(1)
