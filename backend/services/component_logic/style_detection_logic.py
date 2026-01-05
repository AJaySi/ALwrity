"""Style Detection Logic Service for ALwrity Backend.

This service handles business logic for content style detection and analysis,
migrated from the legacy StyleAnalyzer functionality.
"""

from typing import Dict, Any, List, Optional
from loguru import logger
from datetime import datetime
import json
import re
import sys
import os

# Add the backend directory to Python path for absolute imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Import the new backend LLM providers from services
from ..llm_providers.main_text_generation import llm_text_gen

class StyleDetectionLogic:
    """Business logic for content style detection and analysis."""
    
    def __init__(self):
        """Initialize the Style Detection Logic service."""
        logger.info("[StyleDetectionLogic.__init__] Initializing style detection service")
        
    def _clean_json_response(self, text: str) -> str:
        """
        Clean the LLM response to extract valid JSON.
        
        Args:
            text (str): Raw response from LLM
            
        Returns:
            str: Cleaned JSON string
        """
        try:
            # Remove markdown code block markers
            cleaned_string = text.replace("```json", "").replace("```", "").strip()
            
            # Log the cleaned JSON for debugging
            logger.debug(f"[StyleDetectionLogic._clean_json_response] Cleaned JSON: {cleaned_string}")
            
            return cleaned_string
            
        except Exception as e:
            logger.error(f"[StyleDetectionLogic._clean_json_response] Error cleaning response: {str(e)}")
            return ""
    
    def analyze_content_style(self, content: Dict[str, Any], user_id: str = None) -> Dict[str, Any]:
        """
        Analyze the style of the provided content using AI with enhanced prompts.

        Args:
            content (Dict): Content to analyze, containing main_content, title, etc.
            user_id (str): Clerk user ID for subscription checking

        Returns:
            Dict: Analysis results with writing style, characteristics, and recommendations
        """
        try:
            logger.info("[StyleDetectionLogic.analyze_content_style] Starting enhanced style analysis")
            
            # Extract content components
            title = content.get('title', '')
            description = content.get('description', '')
            main_content = content.get('main_content', '')
            headings = content.get('headings', [])
            domain_info = content.get('domain_info', {})
            brand_info = content.get('brand_info', {})
            social_media = content.get('social_media', {})
            content_structure = content.get('content_structure', {})
            
            # Construct the enhanced analysis prompt (strict JSON, minified, stable keys)
            prompt = f"""Analyze the following website content for comprehensive writing style, tone, and characteristics for personalization and AI generation.

            RULES:
            - Return ONE single-line MINIFIED JSON object only. No markdown, code fences, comments, or prose.
            - Use EXACTLY the keys and ordering from the schema below. Do not add extra top-level keys.
            - For unknown/unavailable fields use empty string "" or empty array [] and explain in meta.uncertainty.
            - Keep text concise; avoid repeating input text.
            - Assume token budget; consider only first 5000 chars of main_content and first 10 headings.

            WEBSITE INFORMATION:
            - Domain: {domain_info.get('domain_name', 'Unknown')}
            - Website Type: {self._determine_website_type(domain_info)}
            - Brand Name: {brand_info.get('company_name', 'Not specified')}
            - Tagline: {brand_info.get('tagline', 'Not specified')}
            - Social Media Presence: {', '.join(social_media.keys()) if social_media else 'None detected'}

            CONTENT STRUCTURE:
            - Headings: {len(headings)} total ({content_structure.get('headings', {}).get('h1', 0)} H1, {content_structure.get('headings', {}).get('h2', 0)} H2)
            - Paragraphs: {content_structure.get('paragraphs', 0)}
            - Images: {content_structure.get('images', 0)}
            - Links: {content_structure.get('links', 0)}
            - Has Navigation: {content_structure.get('has_navigation', False)}
            - Has Call-to-Action: {content_structure.get('has_call_to_action', False)}

            CONTENT TO ANALYZE:
            - Title: {title}
            - Description: {description}
            - Main Content (truncated): {main_content[:5000]}
            - Key Headings (first 10): {headings[:10]}

            ANALYSIS REQUIREMENTS:
            1. Analyze the writing style, tone, and voice characteristics
            2. Identify target audience demographics and expertise level
            3. Determine content type and purpose
            4. Assess content structure and organization patterns
            5. Evaluate brand voice consistency and personality
            6. Identify unique style elements and patterns
            7. Consider the website type and industry context
            8. Analyze social media presence impact on content style

            REQUIRED JSON SCHEMA (stable key order):
            {{
              "writing_style": {{
                "tone": "", "voice": "", "complexity": "", "engagement_level": "",
                "brand_personality": "", "formality_level": "", "emotional_appeal": ""
              }},
              "content_characteristics": {{
                "sentence_structure": "", "vocabulary_level": "", "paragraph_organization": "",
                "content_flow": "", "readability_score": "", "content_density": "",
                "visual_elements_usage": ""
              }},
              "target_audience": {{
                "demographics": [], "expertise_level": "", "industry_focus": "", "geographic_focus": "",
                "psychographic_profile": "", "pain_points": [], "motivations": []
              }},
              "content_type": {{
                "primary_type": "", "secondary_types": [], "purpose": "", "call_to_action": "",
                "conversion_focus": "", "educational_value": ""
              }},
              "brand_analysis": {{
                "brand_voice": "", "brand_values": [], "brand_positioning": "", "competitive_differentiation": "",
                "trust_signals": [], "authority_indicators": []
              }},
              "content_strategy_insights": {{
                "strengths": [], "weaknesses": [], "opportunities": [], "threats": [],
                "recommended_improvements": [], "content_gaps": []
              }},
              "recommended_settings": {{
                "writing_tone": "", "target_audience": "", "content_type": "", "creativity_level": "",
                "geographic_location": "", "industry_context": "", "brand_alignment": ""
              }},
              "meta": {{"schema_version": "1.1", "confidence": 0.0, "notes": "", "uncertainty": {{"fields": []}}}}
            }}
            """
            
            # Call the LLM for analysis
            logger.debug("[StyleDetectionLogic.analyze_content_style] Sending enhanced prompt to LLM")
            analysis_text = llm_text_gen(prompt, user_id=user_id)
            
            # Clean and parse the response
            cleaned_json = self._clean_json_response(analysis_text)
            
            try:
                analysis_results = json.loads(cleaned_json)
                logger.info("[StyleDetectionLogic.analyze_content_style] Successfully parsed enhanced analysis results")
                return {
                    'success': True,
                    'analysis': analysis_results
                }
            except json.JSONDecodeError as e:
                logger.error(f"[StyleDetectionLogic.analyze_content_style] Failed to parse JSON response: {e}")
                logger.debug(f"[StyleDetectionLogic.analyze_content_style] Raw response: {analysis_text}")
                return {
                    'success': False,
                    'error': 'Failed to parse analysis response'
                }
                
        except Exception as e:
            logger.error(f"[StyleDetectionLogic.analyze_content_style] Error in enhanced analysis: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def _determine_website_type(self, domain_info: Dict[str, Any]) -> str:
        """Determine the type of website based on domain and content analysis."""
        if domain_info.get('is_blog'):
            return 'Blog/Content Platform'
        elif domain_info.get('is_ecommerce'):
            return 'E-commerce/Online Store'
        elif domain_info.get('is_corporate'):
            return 'Corporate/Business Website'
        elif domain_info.get('has_blog_section'):
            return 'Business with Blog'
        elif domain_info.get('has_about_page') and domain_info.get('has_contact_page'):
            return 'Professional Services'
        else:
            return 'General Website'
    
    def _get_fallback_analysis(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Get fallback analysis when LLM analysis fails."""
        main_content = content.get("main_content", "")
        title = content.get("title", "")
        
        # Simple content analysis based on content characteristics
        content_length = len(main_content)
        word_count = len(main_content.split())
        
        # Determine tone based on content characteristics
        if any(word in main_content.lower() for word in ['professional', 'business', 'industry', 'company']):
            tone = "professional"
        elif any(word in main_content.lower() for word in ['casual', 'fun', 'enjoy', 'exciting']):
            tone = "casual"
        else:
            tone = "neutral"
        
        # Determine complexity based on sentence length and vocabulary
        avg_sentence_length = word_count / max(len([s for s in main_content.split('.') if s.strip()]), 1)
        if avg_sentence_length > 20:
            complexity = "complex"
        elif avg_sentence_length > 15:
            complexity = "moderate"
        else:
            complexity = "simple"
        
        return {
            "writing_style": {
                "tone": tone,
                "voice": "active",
                "complexity": complexity,
                "engagement_level": "medium"
            },
            "content_characteristics": {
                "sentence_structure": "standard",
                "vocabulary_level": "intermediate",
                "paragraph_organization": "logical",
                "content_flow": "smooth"
            },
            "target_audience": {
                "demographics": ["general audience"],
                "expertise_level": "intermediate",
                "industry_focus": "general",
                "geographic_focus": "global"
            },
            "content_type": {
                "primary_type": "article",
                "secondary_types": ["blog", "content"],
                "purpose": "inform",
                "call_to_action": "minimal"
            },
            "recommended_settings": {
                "writing_tone": tone,
                "target_audience": "general audience",
                "content_type": "article",
                "creativity_level": "medium",
                "geographic_location": "global"
            }
        }
    
    def analyze_style_patterns(self, content: Dict[str, Any], user_id: str = None) -> Dict[str, Any]:
        """
        Analyze recurring patterns in the content style.
        
        Args:
            content (Dict): Content to analyze
            
        Returns:
            Dict: Pattern analysis results
        """
        try:
            logger.info("[StyleDetectionLogic.analyze_style_patterns] Starting pattern analysis")
            
            main_content = content.get("main_content", "")
            
            prompt = f"""Analyze the content for recurring writing patterns and style characteristics.
            
            RULES:
            - Return ONE single-line MINIFIED JSON object only. No markdown, code fences, comments, or prose.
            - Use EXACTLY the keys and ordering from the schema below. No extra top-level keys.
            - If uncertain, set empty values and list field names in meta.uncertainty.fields.
            - Keep responses concise and avoid quoting long input spans.
            
            Content (truncated to 3000 chars): {main_content[:3000]}
            
            REQUIRED JSON SCHEMA (stable key order):
            {{
              "patterns": {{
                "sentence_length": "", "vocabulary_patterns": [], "rhetorical_devices": [],
                "paragraph_structure": "", "transition_phrases": []
              }},
              "style_consistency": "",
              "unique_elements": [],
              "meta": {{"schema_version": "1.1", "confidence": 0.0, "notes": "", "uncertainty": {{"fields": []}}}}
            }}
            """
            
            analysis_text = llm_text_gen(prompt, user_id=user_id)
            cleaned_json = self._clean_json_response(analysis_text)
            
            try:
                pattern_results = json.loads(cleaned_json)
                return {
                    'success': True,
                    'patterns': pattern_results
                }
            except json.JSONDecodeError as e:
                logger.error(f"[StyleDetectionLogic.analyze_style_patterns] Failed to parse JSON response: {e}")
                return {
                    'success': False,
                    'error': 'Failed to parse pattern analysis response'
                }
                
        except Exception as e:
            logger.error(f"[StyleDetectionLogic.analyze_style_patterns] Error during analysis: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_style_guidelines(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive content guidelines based on enhanced style analysis.
        
        Args:
            analysis_results (Dict): Results from enhanced style analysis
            
        Returns:
            Dict: Generated comprehensive guidelines
        """
        try:
            logger.info("[StyleDetectionLogic.generate_style_guidelines] Generating comprehensive style guidelines")
            
            # Extract key information from analysis
            writing_style = analysis_results.get('writing_style', {})
            content_characteristics = analysis_results.get('content_characteristics', {})
            target_audience = analysis_results.get('target_audience', {})
            brand_analysis = analysis_results.get('brand_analysis', {})
            content_strategy_insights = analysis_results.get('content_strategy_insights', {})
            
            prompt = f"""Generate actionable content creation guidelines based on the style analysis.

            ANALYSIS DATA:
            Writing Style: {writing_style}
            Content Characteristics: {content_characteristics}
            Target Audience: {target_audience}
            Brand Analysis: {brand_analysis}
            Content Strategy Insights: {content_strategy_insights}

            REQUIREMENTS:
            - Return ONE single-line MINIFIED JSON object only. No markdown, code fences, comments, or prose.
            - Use EXACTLY the keys and ordering from the schema below. No extra top-level keys.
            - Provide concise, implementation-ready bullets with an example for key items (e.g., tone and CTA examples).
            - Include negative guidance (what to avoid) tied to brand constraints where applicable.
            - If uncertain, set empty values and list field names in meta.uncertainty.fields.

            IMPORTANT: REQUIRED JSON SCHEMA (stable key order):
            {{
              "guidelines": {{
                "tone_recommendations": [],
                "structure_guidelines": [],
                "vocabulary_suggestions": [],
                "engagement_tips": [],
                "audience_considerations": [],
                "brand_alignment": [],
                "seo_optimization": [],
                "conversion_optimization": []
              }},
              "best_practices": [],
              "avoid_elements": [],
              "content_strategy": "",
              "ai_generation_tips": [],
              "competitive_advantages": [],
              "content_calendar_suggestions": [],
              "meta": {{"schema_version": "1.1", "confidence": 0.0, "notes": "", "uncertainty": {{"fields": []}}}}
            }}
            """
            
            guidelines_text = llm_text_gen(prompt)
            cleaned_json = self._clean_json_response(guidelines_text)
            
            try:
                guidelines = json.loads(cleaned_json)
                return {
                    'success': True,
                    'guidelines': guidelines
                }
            except json.JSONDecodeError as e:
                logger.error(f"[StyleDetectionLogic.generate_style_guidelines] Failed to parse JSON response: {e}")
                return {
                    'success': False,
                    'error': 'Failed to parse guidelines response'
                }
                
        except Exception as e:
            logger.error(f"[StyleDetectionLogic.generate_style_guidelines] Error generating guidelines: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def validate_style_analysis_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate style analysis request data.
        
        Args:
            request_data (Dict): Request data to validate
            
        Returns:
            Dict: Validation results
        """
        errors = []
        
        # Check if content is provided
        if not request_data.get('content') and not request_data.get('url') and not request_data.get('text_sample'):
            errors.append("Content is required for style analysis")
        
        # Check content length
        content = request_data.get('content', {})
        main_content = content.get('main_content', '')
        if len(main_content) < 50:
            errors.append("Content must be at least 50 characters long for meaningful analysis")
        
        # Check for required fields
        if not content.get('title') and not content.get('main_content'):
            errors.append("Either title or main content must be provided")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        } 