#!/usr/bin/env python3
"""
Test script for Step 5 debugging
"""

import asyncio
import sys
import os
import time

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_step5_debug():
    """Debug Step 5 execution specifically."""
    
    print("🧪 Debugging Step 5: Content Pillar Distribution")
    
    try:
        # Import Step 5
        from services.calendar_generation_datasource_framework.prompt_chaining.steps.phase2.step5_implementation import ContentPillarDistributionStep
        
        # Create test context with data from previous steps
        context = {
            "user_id": 1,
            "strategy_id": 1,
            "calendar_type": "monthly",
            "industry": "technology",
            "business_size": "sme",
            "previous_step_results": {
                4: {
                    "results": {
                        "calendarStructure": {
                            "type": "monthly",
                            "total_weeks": 4,
                            "posting_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
                            "posting_frequency": {
                                "daily": 2,
                                "weekly": 10,
                                "monthly": 40
                            }
                        }
                    }
                }
            },
            "step_results": {},
            "quality_scores": {}
        }
        
        # Create Step 5 instance
        print("✅ Creating Step 5 instance...")
        step5 = ContentPillarDistributionStep()
        print("✅ Step 5 instance created successfully")
        
        # Test Step 5 execution with timing
        print("🔄 Executing Step 5...")
        start_time = time.time()
        
        result = await step5.run(context)
        
        execution_time = time.time() - start_time
        print(f"⏱️ Step 5 execution time: {execution_time:.2f} seconds")
        
        if result:
            print("✅ Step 5 executed successfully!")
            print(f"Status: {result.get('status', 'unknown')}")
            print(f"Quality Score: {result.get('quality_score', 0)}")
            print(f"Execution Time: {result.get('execution_time', 'unknown')}")
            
            if result.get('status') == 'error':
                print(f"❌ Step 5 Error: {result.get('error_message', 'Unknown error')}")
            else:
                print("📊 Step 5 Results:")
                results = result.get('results', {})
                print(f"  - Pillar Mapping: {results.get('pillarMapping', {}).get('distribution_balance', 0):.1%} balance")
                print(f"  - Theme Development: {results.get('themeDevelopment', {}).get('variety_score', 0):.1%} variety")
                print(f"  - Strategic Validation: {results.get('strategicValidation', {}).get('alignment_score', 0):.1%} alignment")
                print(f"  - Diversity Assurance: {results.get('diversityAssurance', {}).get('diversity_score', 0):.1%} diversity")
        else:
            print("❌ Step 5 returned None")
            
    except Exception as e:
        print(f"❌ Error testing Step 5: {e}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(test_step5_debug())
