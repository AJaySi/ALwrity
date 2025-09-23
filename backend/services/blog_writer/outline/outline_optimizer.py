"""
Outline Optimizer - AI-powered outline optimization and rebalancing.

Optimizes outlines for better flow, SEO, and engagement.
"""

from typing import List
from loguru import logger

from models.blog_models import BlogOutlineSection


class OutlineOptimizer:
    """Optimizes outlines for better flow, SEO, and engagement."""
    
    async def optimize(self, outline: List[BlogOutlineSection], focus: str = "general optimization") -> List[BlogOutlineSection]:
        """Optimize entire outline for better flow, SEO, and engagement."""
        outline_text = "\n".join([f"{i+1}. {s.heading}" for i, s in enumerate(outline)])
        
        optimization_prompt = f"""Optimize this blog outline for better flow, engagement, and SEO:

Current Outline:
{outline_text}

Optimization Focus: {focus}

Goals: Improve narrative flow, enhance SEO, increase engagement, ensure comprehensive coverage.

Return JSON format:
{{
    "outline": [
        {{
            "heading": "Optimized heading",
            "subheadings": ["subheading 1", "subheading 2"],
            "key_points": ["point 1", "point 2"],
            "target_words": 300,
            "keywords": ["keyword1", "keyword2"]
        }}
    ]
}}"""
        
        try:
            from services.llm_providers.gemini_provider import gemini_structured_json_response
            
            optimization_schema = {
                "type": "object",
                "properties": {
                    "outline": {
                        "type": "array",
                        "items": {
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
                    }
                },
                "required": ["outline"],
                "propertyOrdering": ["outline"]
            }
            
            optimized_data = gemini_structured_json_response(
                prompt=optimization_prompt,
                schema=optimization_schema,
                temperature=0.3,
                max_tokens=6000  # Match main outline generator
            )
            
            # Handle the new schema format with "outline" wrapper
            if isinstance(optimized_data, dict) and 'outline' in optimized_data:
                optimized_sections = []
                for i, section_data in enumerate(optimized_data['outline']):
                    section = BlogOutlineSection(
                        id=f"s{i+1}",
                        heading=section_data.get('heading', f'Section {i+1}'),
                        subheadings=section_data.get('subheadings', []),
                        key_points=section_data.get('key_points', []),
                        references=outline[i].references if i < len(outline) else [],
                        target_words=section_data.get('target_words', 300),
                        keywords=section_data.get('keywords', [])
                    )
                    optimized_sections.append(section)
                logger.info(f"✅ Outline optimization completed: {len(optimized_sections)} sections optimized")
                return optimized_sections
            else:
                logger.warning(f"Invalid optimization response format: {type(optimized_data)}")
                
        except Exception as e:
            logger.warning(f"AI outline optimization failed: {e}")
            logger.info("Returning original outline without optimization")
        
        return outline
    
    def rebalance_word_counts(self, outline: List[BlogOutlineSection], target_words: int) -> List[BlogOutlineSection]:
        """Rebalance word count distribution across sections."""
        total_sections = len(outline)
        if total_sections == 0:
            return outline
        
        # Calculate target distribution
        intro_words = int(target_words * 0.12)  # 12% for intro
        conclusion_words = int(target_words * 0.12)  # 12% for conclusion
        main_content_words = target_words - intro_words - conclusion_words
        
        # Distribute main content words across sections
        words_per_section = main_content_words // total_sections
        remainder = main_content_words % total_sections
        
        for i, section in enumerate(outline):
            if i == 0:  # First section (intro)
                section.target_words = intro_words
            elif i == total_sections - 1:  # Last section (conclusion)
                section.target_words = conclusion_words
            else:  # Main content sections
                section.target_words = words_per_section + (1 if i < remainder else 0)
        
        return outline
