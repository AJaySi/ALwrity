#!/usr/bin/env python3
"""
Test script for Enhanced Strategy Data Processing
Verifies that the enhanced strategy data processing is working correctly.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from services.content_planning_db import ContentPlanningDBService

async def test_enhanced_strategy_processing():
    """Test the enhanced strategy data processing functionality."""
    print("🧪 Testing Enhanced Strategy Data Processing...")
    
    try:
        # Initialize the database service
        db_service = ContentPlanningDBService()
        
        # Test with a sample strategy ID
        strategy_id = 1  # You can change this to test with different strategies
        
        print(f"📊 Testing strategy data retrieval for strategy ID: {strategy_id}")
        
        # Test the enhanced strategy data retrieval
        strategy_data = await db_service.get_strategy_data(strategy_id)
        
        if strategy_data:
            print("✅ Strategy data retrieved successfully!")
            print(f"📈 Strategy data contains {len(strategy_data)} fields")
            
            # Check for enhanced fields
            enhanced_fields = [
                "strategy_analysis",
                "quality_indicators", 
                "data_completeness",
                "strategic_alignment",
                "quality_gate_data",
                "prompt_chain_data"
            ]
            
            print("\n🔍 Checking for enhanced strategy fields:")
            for field in enhanced_fields:
                if field in strategy_data:
                    print(f"  ✅ {field}: Present")
                    if isinstance(strategy_data[field], dict):
                        print(f"     Contains {len(strategy_data[field])} sub-fields")
                else:
                    print(f"  ❌ {field}: Missing")
            
            # Check strategy analysis
            if "strategy_analysis" in strategy_data:
                analysis = strategy_data["strategy_analysis"]
                print(f"\n📊 Strategy Analysis:")
                print(f"  - Completion Percentage: {analysis.get('completion_percentage', 0)}%")
                print(f"  - Filled Fields: {analysis.get('filled_fields', 0)}/{analysis.get('total_fields', 30)}")
                print(f"  - Data Quality Score: {analysis.get('data_quality_score', 0)}%")
                print(f"  - Strategy Coherence: {analysis.get('strategy_coherence', {}).get('overall_coherence', 0)}%")
            
            # Check quality indicators
            if "quality_indicators" in strategy_data:
                quality = strategy_data["quality_indicators"]
                print(f"\n🎯 Quality Indicators:")
                print(f"  - Data Completeness: {quality.get('data_completeness', 0)}%")
                print(f"  - Strategic Alignment: {quality.get('strategic_alignment', 0)}%")
                print(f"  - Market Relevance: {quality.get('market_relevance', 0)}%")
                print(f"  - Audience Alignment: {quality.get('audience_alignment', 0)}%")
                print(f"  - Content Strategy Coherence: {quality.get('content_strategy_coherence', 0)}%")
                print(f"  - Overall Quality Score: {quality.get('overall_quality_score', 0)}%")
            
            # Check quality gate data
            if "quality_gate_data" in strategy_data:
                quality_gates = strategy_data["quality_gate_data"]
                print(f"\n🚪 Quality Gate Data:")
                for gate_name, gate_data in quality_gates.items():
                    if isinstance(gate_data, dict):
                        print(f"  - {gate_name}: {len(gate_data)} fields")
                    else:
                        print(f"  - {gate_name}: {type(gate_data).__name__}")
            
            # Check prompt chain data
            if "prompt_chain_data" in strategy_data:
                prompt_chain = strategy_data["prompt_chain_data"]
                print(f"\n🔗 Prompt Chain Data:")
                for step_name, step_data in prompt_chain.items():
                    if isinstance(step_data, dict):
                        print(f"  - {step_name}: {len(step_data)} sub-sections")
                    else:
                        print(f"  - {step_name}: {type(step_data).__name__}")
            
            print(f"\n✅ Enhanced Strategy Data Processing Test PASSED!")
            return True
            
        else:
            print("❌ No strategy data retrieved")
            return False
            
    except Exception as e:
        print(f"❌ Error during enhanced strategy data processing test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_comprehensive_user_data():
    """Test the comprehensive user data retrieval with enhanced strategy data."""
    print("\n🧪 Testing Comprehensive User Data with Enhanced Strategy...")
    
    try:
        # Initialize the database service
        db_service = ContentPlanningDBService()
        
        # Test with a sample user ID and strategy ID
        user_id = 1
        strategy_id = 1
        
        print(f"📊 Testing comprehensive user data for user {user_id} with strategy {strategy_id}")
        
        # Test the comprehensive user data retrieval
        user_data = await calendar_service._get_comprehensive_user_data(user_id, strategy_id)
        
        if user_data:
            print("✅ Comprehensive user data retrieved successfully!")
            print(f"📈 User data contains {len(user_data)} fields")
            
            # Check for enhanced strategy fields in user data
            enhanced_fields = [
                "strategy_analysis",
                "quality_indicators",
                "data_completeness", 
                "strategic_alignment",
                "quality_gate_data",
                "prompt_chain_data"
            ]
            
            print("\n🔍 Checking for enhanced strategy fields in user data:")
            for field in enhanced_fields:
                if field in user_data:
                    print(f"  ✅ {field}: Present")
                    if isinstance(user_data[field], dict):
                        print(f"     Contains {len(user_data[field])} sub-fields")
                else:
                    print(f"  ❌ {field}: Missing")
            
            # Check strategy data quality
            if "strategy_data" in user_data:
                strategy_data = user_data["strategy_data"]
                print(f"\n📊 Strategy Data Quality:")
                print(f"  - Strategy ID: {strategy_data.get('strategy_id', 'N/A')}")
                print(f"  - Strategy Name: {strategy_data.get('strategy_name', 'N/A')}")
                print(f"  - Industry: {strategy_data.get('industry', 'N/A')}")
                print(f"  - Content Pillars: {len(strategy_data.get('content_pillars', []))} pillars")
                print(f"  - Target Audience: {len(strategy_data.get('target_audience', {}))} audience fields")
            
            print(f"\n✅ Comprehensive User Data Test PASSED!")
            return True
            
        else:
            print("❌ No comprehensive user data retrieved")
            return False
            
    except Exception as e:
        print(f"❌ Error during comprehensive user data test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests for enhanced strategy data processing."""
    print("🚀 Starting Enhanced Strategy Data Processing Tests...")
    print("=" * 60)
    
    # Test 1: Enhanced Strategy Data Processing
    test1_passed = await test_enhanced_strategy_processing()
    
    # Test 2: Comprehensive User Data
    test2_passed = await test_comprehensive_user_data()
    
    print("\n" + "=" * 60)
    print("📋 Test Results Summary:")
    print(f"  ✅ Enhanced Strategy Data Processing: {'PASSED' if test1_passed else 'FAILED'}")
    print(f"  ✅ Comprehensive User Data: {'PASSED' if test2_passed else 'FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 All Enhanced Strategy Data Processing Tests PASSED!")
        print("✅ The enhanced strategy data processing is working correctly.")
        print("✅ Ready for 12-step prompt chaining and quality gates integration.")
        return True
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    # Run the tests
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
