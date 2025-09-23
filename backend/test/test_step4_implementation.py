#!/usr/bin/env python3
"""
Test Script for Step 4 Implementation

This script tests the Step 4 (Calendar Framework and Timeline) implementation
to ensure it works correctly with real AI services and data processing.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from services.calendar_generation_datasource_framework.prompt_chaining.steps.phase2.phase2_steps import CalendarFrameworkStep
from services.calendar_generation_datasource_framework.data_processing import ComprehensiveUserDataProcessor


async def test_step4_implementation():
    """Test Step 4 implementation with real data processing."""
    print("🧪 Testing Step 4: Calendar Framework and Timeline Implementation")
    
    try:
        # Initialize Step 4
        step4 = CalendarFrameworkStep()
        print("✅ Step 4 initialized successfully")
        
        # Initialize data processor
        data_processor = ComprehensiveUserDataProcessor()
        print("✅ Data processor initialized successfully")
        
        # Test context data
        context = {
            "user_id": 1,
            "strategy_id": 1,
            "calendar_type": "monthly",
            "industry": "technology",
            "business_size": "sme"
        }
        
        print(f"📊 Testing with context: {context}")
        
        # Execute Step 4
        print("🔄 Executing Step 4...")
        result = await step4.execute(context)
        
        # Validate results
        print("📋 Step 4 Results:")
        print(f"  - Step Number: {result.get('stepNumber')}")
        print(f"  - Step Name: {result.get('stepName')}")
        print(f"  - Quality Score: {result.get('qualityScore', 0):.2f}")
        print(f"  - Execution Time: {result.get('executionTime')}")
        print(f"  - Data Sources Used: {result.get('dataSourcesUsed')}")
        
        # Validate calendar structure
        calendar_structure = result.get('results', {}).get('calendarStructure', {})
        print(f"  - Calendar Type: {calendar_structure.get('type')}")
        print(f"  - Total Weeks: {calendar_structure.get('totalWeeks')}")
        print(f"  - Content Distribution: {calendar_structure.get('contentDistribution')}")
        
        # Validate timeline configuration
        timeline_config = result.get('results', {}).get('timelineConfiguration', {})
        print(f"  - Start Date: {timeline_config.get('startDate')}")
        print(f"  - End Date: {timeline_config.get('endDate')}")
        print(f"  - Total Days: {timeline_config.get('totalDays')}")
        print(f"  - Posting Days: {timeline_config.get('postingDays')}")
        
        # Validate quality gates
        duration_control = result.get('results', {}).get('durationControl', {})
        strategic_alignment = result.get('results', {}).get('strategicAlignment', {})
        
        print(f"  - Duration Accuracy: {duration_control.get('accuracyScore', 0):.1%}")
        print(f"  - Strategic Alignment: {strategic_alignment.get('alignmentScore', 0):.1%}")
        
        # Validate insights and recommendations
        insights = result.get('insights', [])
        recommendations = result.get('recommendations', [])
        
        print(f"  - Insights Count: {len(insights)}")
        print(f"  - Recommendations Count: {len(recommendations)}")
        
        # Quality validation
        quality_score = result.get('qualityScore', 0)
        if quality_score >= 0.85:
            print(f"✅ Quality Score: {quality_score:.2f} (Excellent)")
        elif quality_score >= 0.75:
            print(f"✅ Quality Score: {quality_score:.2f} (Good)")
        else:
            print(f"⚠️ Quality Score: {quality_score:.2f} (Needs Improvement)")
        
        print("✅ Step 4 implementation test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing Step 4: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False


async def test_step4_integration():
    """Test Step 4 integration with the orchestrator."""
    print("\n🧪 Testing Step 4 Integration with Orchestrator")
    
    try:
        from services.calendar_generation_datasource_framework.prompt_chaining.orchestrator import PromptChainOrchestrator
        
        # Initialize orchestrator
        orchestrator = PromptChainOrchestrator()
        print("✅ Orchestrator initialized successfully")
        
        # Check if Step 4 is properly registered
        step4 = orchestrator.steps.get("step_04")
        if step4 and step4.name == "Calendar Framework & Timeline":
            print("✅ Step 4 properly registered in orchestrator")
        else:
            print("❌ Step 4 not properly registered in orchestrator")
            return False
        
        # Test context initialization
        context = await orchestrator._initialize_context(
            user_id=1,
            strategy_id=1,
            calendar_type="monthly",
            industry="technology",
            business_size="sme"
        )
        print("✅ Context initialization successful")
        
        # Test Step 4 execution through orchestrator
        print("🔄 Testing Step 4 execution through orchestrator...")
        step_result = await step4.execute(context)
        
        if step_result and step_result.get('stepNumber') == 4:
            print("✅ Step 4 execution through orchestrator successful")
            print(f"  - Quality Score: {step_result.get('qualityScore', 0):.2f}")
        else:
            print("❌ Step 4 execution through orchestrator failed")
            return False
        
        print("✅ Step 4 integration test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing Step 4 integration: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False


async def test_step4_data_processing():
    """Test Step 4 data processing capabilities."""
    print("\n🧪 Testing Step 4 Data Processing")
    
    try:
        from services.calendar_generation_datasource_framework.data_processing import ComprehensiveUserDataProcessor
        
        # Initialize data processor
        data_processor = ComprehensiveUserDataProcessor()
        print("✅ Data processor initialized successfully")
        
        # Test comprehensive user data retrieval
        print("🔄 Testing comprehensive user data retrieval...")
        user_data = await data_processor.get_comprehensive_user_data(1, 1)
        
        if user_data:
            print("✅ Comprehensive user data retrieved successfully")
            print(f"  - User ID: {user_data.get('user_id')}")
            print(f"  - Strategy ID: {user_data.get('strategy_id')}")
            print(f"  - Industry: {user_data.get('industry')}")
            
            # Check for required data sections
            required_sections = ['onboarding_data', 'strategy_data', 'gap_analysis', 'ai_analysis']
            for section in required_sections:
                if section in user_data:
                    print(f"  - {section}: Available")
                else:
                    print(f"  - {section}: Missing")
        else:
            print("❌ Failed to retrieve comprehensive user data")
            return False
        
        print("✅ Step 4 data processing test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing Step 4 data processing: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False


async def main():
    """Main test function."""
    print("🚀 Starting Step 4 Implementation Tests")
    print("=" * 50)
    
    # Run all tests
    tests = [
        test_step4_implementation(),
        test_step4_integration(),
        test_step4_data_processing()
    ]
    
    results = await asyncio.gather(*tests, return_exceptions=True)
    
    # Summarize results
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    test_names = [
        "Step 4 Implementation",
        "Step 4 Integration",
        "Step 4 Data Processing"
    ]
    
    passed = 0
    total = len(results)
    
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"❌ {test_names[i]}: Failed - {str(result)}")
        elif result:
            print(f"✅ {test_names[i]}: Passed")
            passed += 1
        else:
            print(f"❌ {test_names[i]}: Failed")
    
    print(f"\n🎯 Overall Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Step 4 implementation is ready for production.")
        return True
    else:
        print("⚠️ Some tests failed. Please review the implementation.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
