"""
LinkedIn Article Generation Prompts

This module contains prompt templates and builders for generating LinkedIn articles.
"""

from typing import Any, Optional, Dict


class ArticlePromptBuilder:
    """Builder class for LinkedIn article generation prompts."""
    
    @staticmethod
    def build_article_prompt(request: Any, persona: Optional[Dict[str, Any]] = None) -> str:
        """
        Build prompt for article generation.
        
        Args:
            request: LinkedInArticleRequest object containing generation parameters
            
        Returns:
            Formatted prompt string for article generation
        """
        persona_block = ""
        if persona:
            try:
                core = persona.get('core_persona', persona)
                platform_adaptation = persona.get('platform_adaptation', persona.get('platform_persona', {}))
                linguistic = core.get('linguistic_fingerprint', {})
                sentence_metrics = linguistic.get('sentence_metrics', {})
                lexical_features = linguistic.get('lexical_features', {})
                tonal_range = core.get('tonal_range', {})
                persona_block = f"""
        PERSONA CONTEXT:
        - Persona Name: {core.get('persona_name', 'N/A')}
        - Archetype: {core.get('archetype', 'N/A')}
        - Core Belief: {core.get('core_belief', 'N/A')}
        - Default Tone: {tonal_range.get('default_tone', request.tone)}
        - Avg Sentence Length: {sentence_metrics.get('average_sentence_length_words', 18)} words
        - Go-to Words: {', '.join(lexical_features.get('go_to_words', [])[:5])}
        """.rstrip()
            except Exception:
                persona_block = ""

        prompt = f"""
        You are a senior content strategist and industry expert specializing in {request.industry}. Create a comprehensive, thought-provoking LinkedIn article that establishes authority, drives engagement, and provides genuine value to professionals in this field.

        TOPIC: {request.topic}
        INDUSTRY: {request.industry}
        TONE: {request.tone}
        TARGET AUDIENCE: {request.target_audience or 'Industry professionals, executives, and thought leaders'}
        WORD COUNT: {request.word_count} words

        {persona_block}

        CONTENT STRUCTURE:
        - Compelling headline that promises specific value
        - Engaging introduction with a hook and clear value proposition
        - 3-5 main sections with actionable insights and examples
        - Data-driven insights with proper citations
        - Practical takeaways and next steps
        - Strong conclusion with a call-to-action

        CONTENT QUALITY REQUIREMENTS:
        - Include current industry statistics and trends (2024-2025)
        - Provide real-world examples and case studies
        - Address common challenges and pain points
        - Offer actionable strategies and frameworks
        - Use industry-specific terminology appropriately
        - Include expert quotes or insights when relevant

        SEO & ENGAGEMENT OPTIMIZATION:
        - Use relevant keywords naturally throughout the content
        - Include engaging subheadings for scannability
        - Add bullet points and numbered lists for key insights
        - Include relevant hashtags for discoverability
        - End with thought-provoking questions to encourage comments

        VISUAL ELEMENTS:
        - Suggest 2-3 relevant images or graphics
        - Recommend data visualization opportunities
        - Include pull quotes for key insights

        KEY SECTIONS TO COVER: {', '.join(request.key_sections) if request.key_sections else 'Industry overview, current challenges, emerging trends, practical solutions, future outlook'}

        REMEMBER: This article should position the author as a thought leader while providing actionable insights that readers can immediately apply in their professional lives.
        """
        return prompt.strip()
