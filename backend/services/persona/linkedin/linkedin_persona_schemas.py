"""
LinkedIn Persona Schemas
Contains LinkedIn-specific JSON schemas for persona generation.
"""

from typing import Dict, Any


class LinkedInPersonaSchemas:
    """Handles LinkedIn-specific persona schema definitions."""
    
    @staticmethod
    def get_linkedin_platform_schema() -> Dict[str, Any]:
        """Get LinkedIn-specific platform persona schema."""
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
    
    @staticmethod
    def get_enhanced_linkedin_schema() -> Dict[str, Any]:
        """Get enhanced LinkedIn schema with additional professional fields."""
        base_schema = LinkedInPersonaSchemas.get_linkedin_platform_schema()
        
        # Add LinkedIn-specific professional fields
        base_schema["properties"]["professional_networking"] = {
            "type": "object",
            "properties": {
                "thought_leadership_positioning": {"type": "string"},
                "industry_authority_building": {"type": "string"},
                "professional_relationship_strategies": {"type": "array", "items": {"type": "string"}},
                "career_advancement_focus": {"type": "string"}
            }
        }
        
        base_schema["properties"]["linkedin_features"] = {
            "type": "object",
            "properties": {
                "articles_strategy": {"type": "string"},
                "polls_optimization": {"type": "string"},
                "events_networking": {"type": "string"},
                "carousels_education": {"type": "string"},
                "live_discussions": {"type": "string"},
                "native_video": {"type": "string"}
            }
        }
        
        base_schema["properties"]["algorithm_optimization"] = {
            "type": "object",
            "properties": {
                "engagement_patterns": {"type": "array", "items": {"type": "string"}},
                "content_timing": {"type": "array", "items": {"type": "string"}},
                "professional_value_metrics": {"type": "array", "items": {"type": "string"}},
                "network_interaction_strategies": {"type": "array", "items": {"type": "string"}}
            }
        }
        
        # Add professional context optimization
        base_schema["properties"]["professional_context_optimization"] = {
            "type": "object",
            "properties": {
                "industry_specific_positioning": {"type": "string"},
                "expertise_level_adaptation": {"type": "string"},
                "company_size_considerations": {"type": "string"},
                "business_model_alignment": {"type": "string"},
                "professional_role_authority": {"type": "string"},
                "demographic_targeting": {"type": "array", "items": {"type": "string"}},
                "psychographic_engagement": {"type": "string"},
                "conversion_optimization": {"type": "string"}
            }
        }
        
        return base_schema
