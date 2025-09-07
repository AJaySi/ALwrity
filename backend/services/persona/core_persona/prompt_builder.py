"""
Persona Prompt Builder

Handles building comprehensive prompts for persona generation.
"""

from typing import Dict, Any
import json
from loguru import logger


class PersonaPromptBuilder:
    """Builds comprehensive prompts for persona generation."""
    
    def build_persona_analysis_prompt(self, onboarding_data: Dict[str, Any]) -> str:
        """Build the main persona analysis prompt with comprehensive data."""
        
        # Get enhanced analysis data
        enhanced_analysis = onboarding_data.get("enhanced_analysis", {})
        website_analysis = onboarding_data.get("website_analysis", {}) or {}
        research_prefs = onboarding_data.get("research_preferences", {}) or {}
        
        prompt = f"""
COMPREHENSIVE PERSONA GENERATION TASK: Create a highly detailed, data-driven writing persona based on extensive AI analysis of user's website and content strategy.

=== COMPREHENSIVE ONBOARDING DATA ANALYSIS ===

WEBSITE ANALYSIS OVERVIEW:
- URL: {website_analysis.get('website_url', 'Not provided')}
- Analysis Date: {website_analysis.get('analysis_date', 'Not provided')}
- Status: {website_analysis.get('status', 'Not provided')}

=== DETAILED STYLE ANALYSIS ===
{json.dumps(enhanced_analysis.get('comprehensive_style_analysis', {}), indent=2)}

=== CONTENT INSIGHTS ===
{json.dumps(enhanced_analysis.get('content_insights', {}), indent=2)}

=== AUDIENCE INTELLIGENCE ===
{json.dumps(enhanced_analysis.get('audience_intelligence', {}), indent=2)}

=== BRAND VOICE ANALYSIS ===
{json.dumps(enhanced_analysis.get('brand_voice_analysis', {}), indent=2)}

=== TECHNICAL WRITING METRICS ===
{json.dumps(enhanced_analysis.get('technical_writing_metrics', {}), indent=2)}

=== COMPETITIVE ANALYSIS ===
{json.dumps(enhanced_analysis.get('competitive_analysis', {}), indent=2)}

=== CONTENT STRATEGY INSIGHTS ===
{json.dumps(enhanced_analysis.get('content_strategy_insights', {}), indent=2)}

=== RESEARCH PREFERENCES ===
{json.dumps(enhanced_analysis.get('research_preferences', {}), indent=2)}

=== LEGACY DATA (for compatibility) ===
Website Analysis: {json.dumps(website_analysis.get('writing_style', {}), indent=2)}
Content Characteristics: {json.dumps(website_analysis.get('content_characteristics', {}) or {}, indent=2)}
Target Audience: {json.dumps(website_analysis.get('target_audience', {}), indent=2)}
Style Patterns: {json.dumps(website_analysis.get('style_patterns', {}), indent=2)}

=== COMPREHENSIVE PERSONA GENERATION REQUIREMENTS ===

1. IDENTITY CREATION (Based on Brand Analysis):
   - Create a memorable persona name that captures the essence of the brand personality and writing style
   - Define a clear archetype that reflects the brand's positioning and audience appeal
   - Articulate a core belief that drives the writing philosophy and brand values
   - Write a comprehensive brand voice description incorporating all style elements

2. LINGUISTIC FINGERPRINT (Quantitative Analysis from Technical Metrics):
   - Calculate precise average sentence length from sentence structure analysis
   - Determine preferred sentence types based on paragraph organization patterns
   - Analyze active vs passive voice ratio from voice characteristics
   - Extract go-to words and phrases from vocabulary patterns and style analysis
   - List words and phrases to avoid based on brand alignment guidelines
   - Determine contraction usage patterns from formality level
   - Assess vocabulary complexity level from readability scores

3. RHETORICAL ANALYSIS (From Style Patterns):
   - Identify metaphor patterns and themes from rhetorical devices
   - Analyze analogy usage from content strategy insights
   - Assess rhetorical question frequency from engagement tips
   - Determine storytelling approach from content flow analysis

4. TONAL RANGE (From Comprehensive Style Analysis):
   - Define the default tone from tone analysis and brand personality
   - List permissible tones based on emotional appeal and audience considerations
   - Identify forbidden tones from avoid elements and brand alignment
   - Describe emotional range from psychographic profile and engagement level

5. STYLISTIC CONSTRAINTS (From Technical Writing Metrics):
   - Define punctuation preferences from paragraph structure analysis
   - Set formatting guidelines from content structure insights
   - Establish paragraph structure preferences from organization patterns
   - Include transition phrase preferences from style patterns

6. PLATFORM-SPECIFIC ADAPTATIONS (From Content Strategy):
   - Incorporate SEO optimization strategies
   - Include conversion optimization techniques
   - Apply engagement tips for different platforms
   - Use competitive advantages for differentiation

7. CONTENT STRATEGY INTEGRATION:
   - Incorporate best practices from content strategy insights
   - Include AI generation tips for consistent output
   - Apply content calendar suggestions for timing
   - Use competitive advantages for positioning

=== ENHANCED ANALYSIS INSTRUCTIONS ===
- Base your analysis on ALL the comprehensive data provided above
- Use the detailed technical metrics for precise linguistic analysis
- Incorporate brand voice analysis for authentic personality
- Apply audience intelligence for targeted communication
- Include competitive analysis for market positioning
- Use content strategy insights for practical application
- Ensure the persona reflects the brand's unique elements and competitive advantages
- Provide a confidence score (0-100) based on data richness and quality
- Include detailed analysis notes explaining your reasoning and data sources

Generate a comprehensive, data-driven persona profile that can be used to replicate this writing style across different platforms while maintaining brand authenticity and competitive positioning.
"""
        
        return prompt
    
    def build_platform_adaptation_prompt(self, core_persona: Dict[str, Any], platform: str, onboarding_data: Dict[str, Any], platform_constraints: Dict[str, Any]) -> str:
        """Build prompt for platform-specific persona adaptation."""
        
        prompt = f"""
PLATFORM ADAPTATION TASK: Adapt the core writing persona for {platform.upper()}.

CORE PERSONA:
{json.dumps(core_persona, indent=2)}

PLATFORM: {platform.upper()}

PLATFORM CONSTRAINTS:
{json.dumps(platform_constraints, indent=2)}

ADAPTATION REQUIREMENTS:

1. SENTENCE METRICS:
   - Adjust sentence length for platform optimal performance
   - Adapt sentence variety for platform engagement
   - Consider platform reading patterns

2. LEXICAL ADAPTATIONS:
   - Identify platform-specific vocabulary and slang
   - Define hashtag strategy (if applicable)
   - Set emoji usage guidelines
   - Establish mention and tagging strategy

3. CONTENT FORMAT RULES:
   - Respect character/word limits
   - Optimize paragraph structure for platform
   - Define call-to-action style
   - Set link placement strategy

4. ENGAGEMENT PATTERNS:
   - Determine optimal posting frequency
   - Identify best posting times for audience
   - Define engagement tactics
   - Set community interaction guidelines

5. PLATFORM BEST PRACTICES:
   - List platform-specific optimization techniques
   - Consider algorithm preferences
   - Include trending format adaptations

INSTRUCTIONS:
- Maintain the core persona identity while optimizing for platform performance
- Ensure all adaptations align with the original brand voice
- Consider platform-specific audience behavior
- Provide actionable, specific guidelines

Generate a platform-optimized persona adaptation that maintains brand consistency while maximizing platform performance.
"""
        
        return prompt
    
    def get_persona_schema(self) -> Dict[str, Any]:
        """Get the schema for core persona generation."""
        return {
            "type": "object",
            "properties": {
                "identity": {
                    "type": "object",
                    "properties": {
                        "persona_name": {"type": "string"},
                        "archetype": {"type": "string"},
                        "core_belief": {"type": "string"},
                        "brand_voice_description": {"type": "string"}
                    },
                    "required": ["persona_name", "archetype", "core_belief"]
                },
                "linguistic_fingerprint": {
                    "type": "object",
                    "properties": {
                        "sentence_metrics": {
                            "type": "object",
                            "properties": {
                                "average_sentence_length_words": {"type": "number"},
                                "preferred_sentence_type": {"type": "string"},
                                "active_to_passive_ratio": {"type": "string"},
                                "complexity_level": {"type": "string"}
                            }
                        },
                        "lexical_features": {
                            "type": "object",
                            "properties": {
                                "go_to_words": {"type": "array", "items": {"type": "string"}},
                                "go_to_phrases": {"type": "array", "items": {"type": "string"}},
                                "avoid_words": {"type": "array", "items": {"type": "string"}},
                                "contractions": {"type": "string"},
                                "filler_words": {"type": "string"},
                                "vocabulary_level": {"type": "string"}
                            }
                        },
                        "rhetorical_devices": {
                            "type": "object",
                            "properties": {
                                "metaphors": {"type": "string"},
                                "analogies": {"type": "string"},
                                "rhetorical_questions": {"type": "string"},
                                "storytelling_style": {"type": "string"}
                            }
                        }
                    }
                },
                "tonal_range": {
                    "type": "object",
                    "properties": {
                        "default_tone": {"type": "string"},
                        "permissible_tones": {"type": "array", "items": {"type": "string"}},
                        "forbidden_tones": {"type": "array", "items": {"type": "string"}},
                        "emotional_range": {"type": "string"}
                    }
                },
                "stylistic_constraints": {
                    "type": "object",
                    "properties": {
                        "punctuation": {
                            "type": "object",
                            "properties": {
                                "ellipses": {"type": "string"},
                                "em_dash": {"type": "string"},
                                "exclamation_points": {"type": "string"}
                            }
                        },
                        "formatting": {
                            "type": "object",
                            "properties": {
                                "paragraphs": {"type": "string"},
                                "lists": {"type": "string"},
                                "markdown": {"type": "string"}
                            }
                        }
                    }
                },
                "confidence_score": {"type": "number"},
                "analysis_notes": {"type": "string"}
            },
            "required": ["identity", "linguistic_fingerprint", "tonal_range", "confidence_score"]
        }
    
    def get_platform_schema(self) -> Dict[str, Any]:
        """Get the schema for platform-specific persona adaptation."""
        return {
            "type": "object",
            "properties": {
                "platform_type": {"type": "string"},
                "sentence_metrics": {
                    "type": "object",
                    "properties": {
                        "max_sentence_length": {"type": "number"},
                        "optimal_sentence_length": {"type": "number"},
                        "sentence_variety": {"type": "string"}
                    }
                },
                "lexical_adaptations": {
                    "type": "object",
                    "properties": {
                        "platform_specific_words": {"type": "array", "items": {"type": "string"}},
                        "hashtag_strategy": {"type": "string"},
                        "emoji_usage": {"type": "string"},
                        "mention_strategy": {"type": "string"}
                    }
                },
                "content_format_rules": {
                    "type": "object",
                    "properties": {
                        "character_limit": {"type": "number"},
                        "paragraph_structure": {"type": "string"},
                        "call_to_action_style": {"type": "string"},
                        "link_placement": {"type": "string"}
                    }
                },
                "engagement_patterns": {
                    "type": "object",
                    "properties": {
                        "posting_frequency": {"type": "string"},
                        "optimal_posting_times": {"type": "array", "items": {"type": "string"}},
                        "engagement_tactics": {"type": "array", "items": {"type": "string"}},
                        "community_interaction": {"type": "string"}
                    }
                },
                "platform_best_practices": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": ["platform_type", "sentence_metrics", "content_format_rules", "engagement_patterns"]
        }
