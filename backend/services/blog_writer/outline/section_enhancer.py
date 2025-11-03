"""
Section Enhancer - AI-powered section enhancement and improvement.

Enhances individual outline sections for better engagement and value.
"""

from loguru import logger

from models.blog_models import BlogOutlineSection


class SectionEnhancer:
    """Enhances individual outline sections using AI."""
    
    async def enhance(self, section: BlogOutlineSection, focus: str, user_id: str) -> BlogOutlineSection:
        """Enhance a section using AI with research context.
        
        Args:
            section: Outline section to enhance
            focus: Enhancement focus (e.g., "general improvement")
            user_id: User ID (required for subscription checks and usage tracking)
            
        Returns:
            Enhanced outline section
            
        Raises:
            ValueError: If user_id is not provided
        """
        if not user_id:
            raise ValueError("user_id is required for section enhancement (subscription checks and usage tracking)")
        
        enhancement_prompt = f"""
        Enhance the following blog section to make it more engaging, comprehensive, and valuable:
        
        Current Section:
        Heading: {section.heading}
        Subheadings: {', '.join(section.subheadings)}
        Key Points: {', '.join(section.key_points)}
        Target Words: {section.target_words}
        Keywords: {', '.join(section.keywords)}
        
        Enhancement Focus: {focus}
        
        Improve:
        1. Make subheadings more specific and actionable
        2. Add more comprehensive key points with data/insights
        3. Include practical examples and case studies
        4. Address common questions and objections
        5. Optimize for SEO with better keyword integration
        
        Respond with JSON:
        {{
            "heading": "Enhanced heading",
            "subheadings": ["enhanced subheading 1", "enhanced subheading 2"],
            "key_points": ["enhanced point 1", "enhanced point 2"],
            "target_words": 400,
            "keywords": ["keyword1", "keyword2"]
        }}
        """
        
        try:
            from services.llm_providers.main_text_generation import llm_text_gen
            
            enhancement_schema = {
                "type": "object",
                "properties": {
                    "heading": {"type": "string"},
                    "subheadings": {"type": "array", "items": {"type": "string"}},
                    "key_points": {"type": "array", "items": {"type": "string"}},
                    "target_words": {"type": "integer"},
                    "keywords": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["heading", "subheadings", "key_points", "target_words", "keywords"]
            }
            
            enhanced_data = llm_text_gen(
                prompt=enhancement_prompt,
                json_struct=enhancement_schema,
                system_prompt=None,
                user_id=user_id
            )
            
            if isinstance(enhanced_data, dict) and 'error' not in enhanced_data:
                return BlogOutlineSection(
                    id=section.id,
                    heading=enhanced_data.get('heading', section.heading),
                    subheadings=enhanced_data.get('subheadings', section.subheadings),
                    key_points=enhanced_data.get('key_points', section.key_points),
                    references=section.references,
                    target_words=enhanced_data.get('target_words', section.target_words),
                    keywords=enhanced_data.get('keywords', section.keywords)
                )
        except Exception as e:
            logger.warning(f"AI section enhancement failed: {e}")
        
        return section
