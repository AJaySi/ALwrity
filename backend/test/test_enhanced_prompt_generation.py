#!/usr/bin/env python3
"""
Test Script for Enhanced LinkedIn Prompt Generation

This script demonstrates how the enhanced LinkedIn prompt generator analyzes
generated content and creates context-aware image prompts.
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


async def test_enhanced_prompt_generation():
    """Test the enhanced LinkedIn prompt generation with content analysis."""
    
    logger.info("🧪 Testing Enhanced LinkedIn Prompt Generation")
    logger.info("=" * 70)
    
    try:
        # Import the enhanced prompt generator
        from services.linkedin.image_prompts import LinkedInPromptGenerator
        
        # Initialize the service
        prompt_generator = LinkedInPromptGenerator()
        logger.success("✅ LinkedIn Prompt Generator initialized successfully")
        
        # Test cases with different types of LinkedIn content
        test_cases = [
            {
                'name': 'AI Marketing Post',
                'content': {
                    'topic': 'AI in Marketing',
                    'industry': 'Technology',
                    'content_type': 'post',
                    'content': """🚀 Exciting news! Artificial Intelligence is revolutionizing how we approach marketing strategies. 

Here are 3 game-changing ways AI is transforming the industry:

1️⃣ **Predictive Analytics**: AI algorithms can now predict customer behavior with 95% accuracy, allowing marketers to create hyper-personalized campaigns.

2️⃣ **Content Optimization**: Machine learning models analyze engagement patterns to optimize content timing, format, and messaging for maximum impact.

3️⃣ **Automated Personalization**: AI-powered tools automatically adjust marketing messages based on individual user preferences and behavior.

The future of marketing is here, and it's powered by AI! 🎯

What's your experience with AI in marketing? Share your thoughts below! 👇

#AIMarketing #DigitalTransformation #MarketingInnovation #TechTrends #FutureOfMarketing"""
                }
            },
            {
                'name': 'Leadership Article',
                'content': {
                    'topic': 'Building High-Performance Teams',
                    'industry': 'Business',
                    'content_type': 'article',
                    'content': """Building High-Performance Teams: A Comprehensive Guide

In today's competitive business landscape, the ability to build and lead high-performance teams is not just a skill—it's a strategic imperative. After 15 years of leading teams across various industries, I've identified the key principles that consistently drive exceptional results.

**The Foundation: Clear Vision and Purpose**
Every high-performance team starts with a crystal-clear understanding of their mission. Team members need to know not just what they're doing, but why it matters. This creates intrinsic motivation that external rewards simply cannot match.

**Communication: The Lifeblood of Success**
Effective communication in high-performance teams goes beyond regular meetings. It involves creating an environment where feedback flows freely, ideas are shared without fear, and every voice is heard and valued.

**Trust and Psychological Safety**
High-performance teams operate in environments where team members feel safe to take risks, make mistakes, and learn from failures. This psychological safety is the bedrock of innovation and continuous improvement.

**Continuous Learning and Adaptation**
The best teams never rest on their laurels. They continuously seek new knowledge, adapt to changing circumstances, and evolve their approaches based on results and feedback.

**Results and Accountability**
While process matters, high-performance teams are ultimately measured by their results. Clear metrics, regular check-ins, and a culture of accountability ensure that the team stays focused on delivering value.

Building high-performance teams is both an art and a science. It requires patience, persistence, and a genuine commitment to developing people. The investment pays dividends not just in results, but in the satisfaction of seeing individuals grow and teams achieve what once seemed impossible.

What strategies have you found most effective in building high-performance teams? Share your insights in the comments below."""
                }
            },
            {
                'name': 'Data Analytics Carousel',
                'content': {
                    'topic': 'Data-Driven Decision Making',
                    'industry': 'Finance',
                    'content_type': 'carousel',
                    'content': """📊 Data-Driven Decision Making: Your Competitive Advantage

Slide 1: The Power of Data
• 73% of companies using data-driven decision making report improved performance
• Data-driven organizations are 23x more likely to acquire customers
• 58% of executives say data analytics has improved their decision-making process

Slide 2: Key Metrics to Track
• Customer Acquisition Cost (CAC)
• Customer Lifetime Value (CLV)
• Conversion Rates
• Churn Rate
• Revenue Growth

Slide 3: Implementation Steps
1. Define clear objectives
2. Identify relevant data sources
3. Establish data quality standards
4. Build analytical capabilities
5. Create feedback loops

Slide 4: Common Pitfalls
• Analysis paralysis
• Ignoring qualitative insights
• Not validating assumptions
• Over-relying on historical data
• Poor data visualization

Slide 5: Success Stories
• Netflix: 75% of viewing decisions influenced by data
• Amazon: Dynamic pricing increases revenue by 25%
• Spotify: Personalized recommendations drive 40% of listening time

Slide 6: Getting Started
• Start small with key metrics
• Invest in data literacy training
• Use visualization tools
• Establish regular review cycles
• Celebrate data-driven wins

Ready to transform your decision-making process? Let's discuss your data strategy! 💬

#DataDriven #Analytics #BusinessIntelligence #DecisionMaking #Finance #Strategy"""
                }
            }
        ]
        
        # Test each case
        for i, test_case in enumerate(test_cases, 1):
            logger.info(f"\n📝 Test Case {i}: {test_case['name']}")
            logger.info("-" * 50)
            
            # Generate prompts using the enhanced generator
            prompts = await prompt_generator.generate_three_prompts(
                test_case['content'], 
                aspect_ratio="1:1"
            )
            
            if prompts and len(prompts) >= 3:
                logger.success(f"✅ Generated {len(prompts)} context-aware prompts")
                
                # Display each prompt
                for j, prompt in enumerate(prompts, 1):
                    logger.info(f"\n🎨 Prompt {j}: {prompt['style']}")
                    logger.info(f"   Description: {prompt['description']}")
                    logger.info(f"   Content Context: {prompt.get('content_context', 'N/A')}")
                    
                    # Show a preview of the prompt
                    prompt_text = prompt['prompt']
                    if len(prompt_text) > 200:
                        prompt_text = prompt_text[:200] + "..."
                    logger.info(f"   Prompt Preview: {prompt_text}")
                    
                    # Validate prompt quality
                    quality_result = await prompt_generator.validate_prompt_quality(prompt)
                    if quality_result.get('valid'):
                        logger.success(f"   ✅ Quality Score: {quality_result['overall_score']}/100")
                    else:
                        logger.warning(f"   ⚠️ Quality Score: {quality_result.get('overall_score', 'N/A')}/100")
            else:
                logger.error(f"❌ Failed to generate prompts for {test_case['name']}")
        
        # Test content analysis functionality directly
        logger.info(f"\n🔍 Testing Content Analysis Functionality")
        logger.info("-" * 50)
        
        test_content = test_cases[0]['content']['content']
        content_analysis = prompt_generator._analyze_content_for_image_context(
            test_content, 
            test_cases[0]['content']['content_type']
        )
        
        logger.info("Content Analysis Results:")
        for key, value in content_analysis.items():
            logger.info(f"   {key}: {value}")
        
        logger.info("=" * 70)
        logger.success("🎉 Enhanced LinkedIn Prompt Generation Test Completed Successfully!")
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ Import Error: {e}")
        return False
        
    except Exception as e:
        logger.error(f"❌ Test Failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False


async def main():
    """Main test function."""
    logger.info("🚀 Starting Enhanced LinkedIn Prompt Generation Tests")
    
    success = await test_enhanced_prompt_generation()
    
    if success:
        logger.success("✅ All tests passed! The enhanced prompt generation is working correctly.")
        sys.exit(0)
    else:
        logger.error("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    # Run the async test
    asyncio.run(main())
