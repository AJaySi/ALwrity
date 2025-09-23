"""
Title Generator - Handles title generation and formatting for blog outlines.

Extracts content angles from research data and combines them with AI-generated titles.
"""

from typing import List
from loguru import logger


class TitleGenerator:
    """Handles title generation, formatting, and combination logic."""
    
    def __init__(self):
        """Initialize the title generator."""
        pass
    
    def extract_content_angle_titles(self, research) -> List[str]:
        """
        Extract content angles from research data and convert them to blog titles.
        
        Args:
            research: BlogResearchResponse object containing suggested_angles
            
        Returns:
            List of title-formatted content angles
        """
        if not research or not hasattr(research, 'suggested_angles'):
            return []
        
        content_angles = research.suggested_angles or []
        if not content_angles:
            return []
        
        # Convert content angles to title format
        title_formatted_angles = []
        for angle in content_angles:
            if isinstance(angle, str) and angle.strip():
                # Clean and format the angle as a title
                formatted_angle = self._format_angle_as_title(angle.strip())
                if formatted_angle and formatted_angle not in title_formatted_angles:
                    title_formatted_angles.append(formatted_angle)
        
        logger.info(f"Extracted {len(title_formatted_angles)} content angle titles from research data")
        return title_formatted_angles
    
    def _format_angle_as_title(self, angle: str) -> str:
        """
        Format a content angle as a proper blog title.
        
        Args:
            angle: Raw content angle string
            
        Returns:
            Formatted title string
        """
        if not angle or len(angle.strip()) < 10:  # Too short to be a good title
            return ""
        
        # Clean up the angle
        cleaned_angle = angle.strip()
        
        # Capitalize first letter of each sentence and proper nouns
        sentences = cleaned_angle.split('. ')
        formatted_sentences = []
        for sentence in sentences:
            if sentence.strip():
                # Use title case for better formatting
                formatted_sentence = sentence.strip().title()
                formatted_sentences.append(formatted_sentence)
        
        formatted_title = '. '.join(formatted_sentences)
        
        # Ensure it ends with proper punctuation
        if not formatted_title.endswith(('.', '!', '?')):
            formatted_title += '.'
        
        # Limit length to reasonable blog title size
        if len(formatted_title) > 100:
            formatted_title = formatted_title[:97] + "..."
        
        return formatted_title
    
    def combine_title_options(self, ai_titles: List[str], content_angle_titles: List[str], primary_keywords: List[str]) -> List[str]:
        """
        Combine AI-generated titles with content angle titles, ensuring variety and quality.
        
        Args:
            ai_titles: AI-generated title options
            content_angle_titles: Titles derived from content angles
            primary_keywords: Primary keywords for fallback generation
            
        Returns:
            Combined list of title options (max 6 total)
        """
        all_titles = []
        
        # Add content angle titles first (these are research-based and valuable)
        for title in content_angle_titles[:3]:  # Limit to top 3 content angles
            if title and title not in all_titles:
                all_titles.append(title)
        
        # Add AI-generated titles
        for title in ai_titles:
            if title and title not in all_titles:
                all_titles.append(title)
        
        # Note: Removed fallback titles as requested - only use research and AI-generated titles
        
        # Limit to 6 titles maximum for UI usability
        final_titles = all_titles[:6]
        
        logger.info(f"Combined title options: {len(final_titles)} total (AI: {len(ai_titles)}, Content angles: {len(content_angle_titles)})")
        return final_titles
    
    def generate_fallback_titles(self, primary_keywords: List[str]) -> List[str]:
        """Generate fallback titles when AI generation fails."""
        primary_keyword = primary_keywords[0] if primary_keywords else "Topic"
        return [
            f"The Complete Guide to {primary_keyword}",
            f"{primary_keyword}: Everything You Need to Know",
            f"How to Master {primary_keyword} in 2024"
        ]
