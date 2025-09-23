#!/usr/bin/env python3
"""
Test Script for LinkedIn Content Generation Keyword Fix

This script tests the fixed keyword processing by calling the LinkedIn content generation
endpoint directly and capturing detailed logs to analyze API usage patterns.
"""

import asyncio
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'test_linkedin_keyword_fix_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Import the LinkedIn service
from services.linkedin_service import LinkedInService
from models.linkedin_models import LinkedInPostRequest, LinkedInPostType, LinkedInTone, GroundingLevel, SearchEngine


class LinkedInKeywordTest:
    """Test class for LinkedIn keyword processing fix."""
    
    def __init__(self):
        self.linkedin_service = LinkedInService()
        self.test_results = []
        self.api_call_count = 0
        self.start_time = None
        
    def log_api_call(self, endpoint: str, duration: float, success: bool):
        """Log API call details."""
        self.api_call_count += 1
        logger.info(f"API Call #{self.api_call_count}: {endpoint} - Duration: {duration:.2f}s - Success: {success}")
    
    async def test_keyword_phrase(self, phrase: str, test_name: str) -> Dict[str, Any]:
        """Test a specific keyword phrase."""
        logger.info(f"\n{'='*60}")
        logger.info(f"TESTING: {test_name}")
        logger.info(f"KEYWORD PHRASE: '{phrase}'")
        logger.info(f"{'='*60}")
        
        test_start = time.time()
        
        try:
            # Create the request
            request = LinkedInPostRequest(
                topic=phrase,
                industry="Technology",
                post_type=LinkedInPostType.PROFESSIONAL,
                tone=LinkedInTone.PROFESSIONAL,
                grounding_level=GroundingLevel.ENHANCED,
                search_engine=SearchEngine.GOOGLE,
                research_enabled=True,
                include_citations=True,
                max_length=1000
            )
            
            logger.info(f"Request created: {request.topic}")
            logger.info(f"Research enabled: {request.research_enabled}")
            logger.info(f"Search engine: {request.search_engine}")
            logger.info(f"Grounding level: {request.grounding_level}")
            
            # Call the LinkedIn service
            logger.info("Calling LinkedIn service...")
            response = await self.linkedin_service.generate_linkedin_post(request)
            
            test_duration = time.time() - test_start
            self.log_api_call("LinkedIn Post Generation", test_duration, response.success)
            
            # Analyze the response
            result = {
                "test_name": test_name,
                "keyword_phrase": phrase,
                "success": response.success,
                "duration": test_duration,
                "api_calls": self.api_call_count,
                "error": response.error if not response.success else None,
                "content_length": len(response.data.content) if response.success and response.data else 0,
                "sources_count": len(response.research_sources) if response.success and response.research_sources else 0,
                "citations_count": len(response.data.citations) if response.success and response.data and response.data.citations else 0,
                "grounding_status": response.grounding_status if response.success else None,
                "generation_metadata": response.generation_metadata if response.success else None
            }
            
            if response.success:
                logger.info(f"✅ SUCCESS: Generated {result['content_length']} characters")
                logger.info(f"📊 Sources: {result['sources_count']}, Citations: {result['citations_count']}")
                logger.info(f"⏱️ Total duration: {test_duration:.2f}s")
                logger.info(f"🔢 API calls made: {self.api_call_count}")
                
                # Log content preview
                if response.data and response.data.content:
                    content_preview = response.data.content[:200] + "..." if len(response.data.content) > 200 else response.data.content
                    logger.info(f"📝 Content preview: {content_preview}")
                
                # Log grounding status
                if response.grounding_status:
                    logger.info(f"🔍 Grounding status: {response.grounding_status}")
                    
            else:
                logger.error(f"❌ FAILED: {response.error}")
                
            return result
            
        except Exception as e:
            test_duration = time.time() - test_start
            logger.error(f"❌ EXCEPTION in {test_name}: {str(e)}")
            self.log_api_call("LinkedIn Post Generation", test_duration, False)
            
            return {
                "test_name": test_name,
                "keyword_phrase": phrase,
                "success": False,
                "duration": test_duration,
                "api_calls": self.api_call_count,
                "error": str(e),
                "content_length": 0,
                "sources_count": 0,
                "citations_count": 0,
                "grounding_status": None,
                "generation_metadata": None
            }
    
    async def run_comprehensive_test(self):
        """Run comprehensive tests for keyword processing."""
        logger.info("🚀 Starting LinkedIn Keyword Processing Test Suite")
        logger.info(f"Test started at: {datetime.now()}")
        
        self.start_time = time.time()
        
        # Test cases
        test_cases = [
            {
                "phrase": "ALwrity content generation",
                "name": "Single Phrase Test (Should be preserved as-is)"
            },
            {
                "phrase": "AI tools, content creation, marketing automation",
                "name": "Comma-Separated Test (Should be split by commas)"
            },
            {
                "phrase": "LinkedIn content strategy",
                "name": "Another Single Phrase Test"
            },
            {
                "phrase": "social media, digital marketing, brand awareness",
                "name": "Another Comma-Separated Test"
            }
        ]
        
        # Run all tests
        for test_case in test_cases:
            result = await self.test_keyword_phrase(
                test_case["phrase"], 
                test_case["name"]
            )
            self.test_results.append(result)
            
            # Reset API call counter for next test
            self.api_call_count = 0
            
            # Small delay between tests
            await asyncio.sleep(2)
        
        # Generate summary report
        self.generate_summary_report()
    
    def generate_summary_report(self):
        """Generate a comprehensive summary report."""
        total_time = time.time() - self.start_time
        
        logger.info(f"\n{'='*80}")
        logger.info("📊 COMPREHENSIVE TEST SUMMARY REPORT")
        logger.info(f"{'='*80}")
        
        logger.info(f"🕐 Total test duration: {total_time:.2f} seconds")
        logger.info(f"🧪 Total tests run: {len(self.test_results)}")
        
        successful_tests = [r for r in self.test_results if r["success"]]
        failed_tests = [r for r in self.test_results if not r["success"]]
        
        logger.info(f"✅ Successful tests: {len(successful_tests)}")
        logger.info(f"❌ Failed tests: {len(failed_tests)}")
        
        if successful_tests:
            avg_duration = sum(r["duration"] for r in successful_tests) / len(successful_tests)
            avg_content_length = sum(r["content_length"] for r in successful_tests) / len(successful_tests)
            avg_sources = sum(r["sources_count"] for r in successful_tests) / len(successful_tests)
            avg_citations = sum(r["citations_count"] for r in successful_tests) / len(successful_tests)
            
            logger.info(f"📈 Average generation time: {avg_duration:.2f}s")
            logger.info(f"📝 Average content length: {avg_content_length:.0f} characters")
            logger.info(f"🔍 Average sources found: {avg_sources:.1f}")
            logger.info(f"📚 Average citations: {avg_citations:.1f}")
        
        # Detailed results
        logger.info(f"\n📋 DETAILED TEST RESULTS:")
        for i, result in enumerate(self.test_results, 1):
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            logger.info(f"{i}. {status} - {result['test_name']}")
            logger.info(f"   Phrase: '{result['keyword_phrase']}'")
            logger.info(f"   Duration: {result['duration']:.2f}s")
            if result["success"]:
                logger.info(f"   Content: {result['content_length']} chars, Sources: {result['sources_count']}, Citations: {result['citations_count']}")
            else:
                logger.info(f"   Error: {result['error']}")
        
        # API Usage Analysis
        logger.info(f"\n🔍 API USAGE ANALYSIS:")
        total_api_calls = sum(r["api_calls"] for r in self.test_results)
        logger.info(f"Total API calls across all tests: {total_api_calls}")
        
        if successful_tests:
            avg_api_calls = sum(r["api_calls"] for r in successful_tests) / len(successful_tests)
            logger.info(f"Average API calls per successful test: {avg_api_calls:.1f}")
        
        # Save detailed results to JSON file
        report_data = {
            "test_summary": {
                "total_duration": total_time,
                "total_tests": len(self.test_results),
                "successful_tests": len(successful_tests),
                "failed_tests": len(failed_tests),
                "total_api_calls": total_api_calls
            },
            "test_results": self.test_results,
            "timestamp": datetime.now().isoformat()
        }
        
        report_filename = f"linkedin_keyword_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        logger.info(f"📄 Detailed report saved to: {report_filename}")
        logger.info(f"{'='*80}")


async def main():
    """Main test execution function."""
    try:
        test_suite = LinkedInKeywordTest()
        await test_suite.run_comprehensive_test()
        
    except Exception as e:
        logger.error(f"❌ Test suite failed: {str(e)}")
        raise


if __name__ == "__main__":
    print("🚀 Starting LinkedIn Keyword Processing Test Suite")
    print("This will test the keyword fix and analyze API usage patterns...")
    print("=" * 60)
    
    asyncio.run(main())
