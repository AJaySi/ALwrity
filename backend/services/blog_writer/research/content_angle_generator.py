"""
Content Angle Generator - AI-powered content angle discovery.

Generates strategic content angles from research content for blog posts.
"""

from typing import List
from loguru import logger


class ContentAngleGenerator:
    """Generates strategic content angles from research content."""
    
    def generate(self, content: str, topic: str, industry: str) -> List[str]:
        """Parse strategic content angles from the research content using AI."""
        angles_prompt = f"""
        Analyze the following research content and create strategic content angles for: {topic} in {industry}
        
        Research Content:
        {content[:3000]}
        
        Create 7 compelling content angles that:
        1. Leverage current trends and data from the research
        2. Address content gaps and opportunities
        3. Appeal to different audience segments
        4. Include unique perspectives not covered by competitors
        5. Incorporate specific statistics, case studies, or expert insights
        6. Create emotional connection and urgency
        7. Provide actionable value to readers
        
        Each angle should be:
        - Specific and data-driven
        - Unique and differentiated
        - Compelling and click-worthy
        - Actionable for readers
        
        Respond with JSON:
        {{
            "content_angles": [
                "Specific angle 1 with data/trends",
                "Specific angle 2 with unique perspective",
                "Specific angle 3 with actionable insights",
                "Specific angle 4 with case study focus",
                "Specific angle 5 with future outlook",
                "Specific angle 6 with problem-solving focus",
                "Specific angle 7 with industry insights"
            ]
        }}
        """
        
        from services.llm_providers.gemini_provider import gemini_structured_json_response
        
        angles_schema = {
            "type": "object",
            "properties": {
                "content_angles": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 5,
                    "maxItems": 7
                }
            },
            "required": ["content_angles"]
        }
        
        angles_result = gemini_structured_json_response(
            prompt=angles_prompt,
            schema=angles_schema,
            temperature=0.7,
            max_tokens=4000
        )
        
        if isinstance(angles_result, dict) and 'content_angles' in angles_result:
            logger.info("✅ AI content angles generation completed successfully")
            return angles_result['content_angles'][:7]
        else:
            # Fail gracefully - no fallback data
            error_msg = angles_result.get('error', 'Unknown error') if isinstance(angles_result, dict) else str(angles_result)
            logger.error(f"AI content angles generation failed: {error_msg}")
            raise ValueError(f"Content angles generation failed: {error_msg}")
    
