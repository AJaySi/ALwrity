"""
AI Prompt Utilities

Utility functions for AI prompt generation and response parsing.
"""

from typing import Dict, Any, List, Optional
import json
from loguru import logger

from ..constants import DEFAULT_CONFIDENCE_SCORE
from ..enums import IntentType, ContentType


def generate_trend_analysis_prompt(industry: str, target_keywords: Optional[List[str]] = None) -> str:
    """
    Generate a comprehensive prompt for keyword trend analysis.
    
    Args:
        industry: Industry category
        target_keywords: Optional list of target keywords
        
    Returns:
        Formatted prompt string
    """
    keywords_str = str(target_keywords) if target_keywords else "[]"
    
    prompt = f"""
    Analyze keyword opportunities for {industry} industry:

    Target Keywords: {keywords_str}
    
    Provide comprehensive keyword analysis including:
    1. Search volume estimates
    2. Competition levels
    3. Trend analysis
    4. Opportunity scoring
    5. Content format recommendations
    6. Keyword difficulty assessment
    7. Seasonal trends
    
    Format as structured JSON with detailed analysis.
    """
    
    return prompt.strip()


def generate_trend_analysis_schema() -> Dict[str, Any]:
    """
    Generate JSON schema for trend analysis response.
    
    Returns:
        JSON schema dictionary
    """
    return {
        "type": "object",
        "properties": {
            "trends": {
                "type": "object",
                "additionalProperties": {
                    "type": "object",
                    "properties": {
                        "search_volume": {"type": "number"},
                        "difficulty": {"type": "number"},
                        "trend": {"type": "string"},
                        "competition": {"type": "string"},
                        "intent": {"type": "string"},
                        "cpc": {"type": "number"},
                        "seasonal_factor": {"type": "number"}
                    }
                }
            },
            "summary": {
                "type": "object",
                "properties": {
                    "total_keywords": {"type": "number"},
                    "high_volume_keywords": {"type": "number"},
                    "low_competition_keywords": {"type": "number"},
                    "trending_keywords": {"type": "number"},
                    "opportunity_score": {"type": "number"}
                }
            },
            "recommendations": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "keyword": {"type": "string"},
                        "recommendation": {"type": "string"},
                        "priority": {"type": "string"},
                        "estimated_impact": {"type": "string"}
                    }
                }
            }
        }
    }


def generate_intent_analysis_prompt(trend_analysis: Dict[str, Any]) -> str:
    """
    Generate a comprehensive prompt for search intent analysis.
    
    Args:
        trend_analysis: Keyword trend analysis results
        
    Returns:
        Formatted prompt string
    """
    prompt = f"""
    Analyze search intent based on the following keyword trend data:

    Trend Analysis: {json.dumps(trend_analysis, indent=2)}

    Provide comprehensive search intent analysis including:
    1. Intent classification (informational, transactional, navigational, commercial)
    2. User journey mapping
    3. Content format recommendations
    4. Conversion optimization suggestions
    5. User behavior patterns
    
    Format as structured JSON with detailed analysis.
    """
    
    return prompt.strip()


def generate_intent_analysis_schema() -> Dict[str, Any]:
    """
    Generate JSON schema for intent analysis response.
    
    Returns:
        JSON schema dictionary
    """
    return {
        "type": "object",
        "properties": {
            "informational": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "keyword": {"type": "string"},
                        "intent_type": {"type": "string"},
                        "content_suggestions": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    }
                }
            },
            "transactional": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "keyword": {"type": "string"},
                        "intent_type": {"type": "string"},
                        "content_suggestions": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    }
                }
            },
            "navigational": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "keyword": {"type": "string"},
                        "intent_type": {"type": "string"},
                        "content_suggestions": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    }
                }
            },
            "summary": {
                "type": "object",
                "properties": {
                    "dominant_intent": {"type": "string"},
                    "content_strategy_recommendations": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                }
            }
        }
    }


def generate_opportunity_identification_prompt(
    trend_analysis: Dict[str, Any],
    intent_analysis: Dict[str, Any]
) -> str:
    """
    Generate a comprehensive prompt for opportunity identification.
    
    Args:
        trend_analysis: Keyword trend analysis results
        intent_analysis: Search intent analysis results
        
    Returns:
        Formatted prompt string
    """
    prompt = f"""
    Identify keyword opportunities based on the following analysis:

    Trend Analysis: {json.dumps(trend_analysis, indent=2)}
    Intent Analysis: {json.dumps(intent_analysis, indent=2)}

    Provide comprehensive opportunity analysis including:
    1. High-value keyword opportunities
    2. Low-competition keywords
    3. Long-tail keyword suggestions
    4. Content gap opportunities
    5. Competitive advantage opportunities
    6. Implementation priorities
    
    Format as structured JSON with detailed opportunities.
    """
    
    return prompt.strip()


def generate_opportunity_identification_schema() -> Dict[str, Any]:
    """
    Generate JSON schema for opportunity identification response.
    
    Returns:
        JSON schema dictionary
    """
    return {
        "type": "object",
        "properties": {
            "opportunities": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "keyword": {"type": "string"},
                        "opportunity_type": {"type": "string"},
                        "search_volume": {"type": "number"},
                        "competition_level": {"type": "string"},
                        "difficulty_score": {"type": "number"},
                        "estimated_traffic": {"type": "string"},
                        "content_suggestions": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "priority": {"type": "string"},
                        "implementation_time": {"type": "string"}
                    }
                }
            }
        }
    }


def generate_insights_prompt(
    trend_analysis: Dict[str, Any],
    intent_analysis: Dict[str, Any],
    opportunities: List[Dict[str, Any]]
) -> str:
    """
    Generate a comprehensive prompt for insights generation.
    
    Args:
        trend_analysis: Keyword trend analysis results
        intent_analysis: Search intent analysis results
        opportunities: List of keyword opportunities
        
    Returns:
        Formatted prompt string
    """
    prompt = f"""
    Generate strategic keyword insights based on the following analysis:

    Trend Analysis: {json.dumps(trend_analysis, indent=2)}
    Intent Analysis: {json.dumps(intent_analysis, indent=2)}
    Opportunities: {json.dumps(opportunities, indent=2)}

    Provide strategic insights covering:
    1. Keyword strategy recommendations
    2. Content optimization suggestions
    3. Competitive positioning advice
    4. Implementation priorities
    5. Performance optimization tips
    
    Format as structured JSON with detailed insights.
    """
    
    return prompt.strip()


def generate_insights_schema() -> Dict[str, Any]:
    """
    Generate JSON schema for insights response.
    
    Returns:
        JSON schema dictionary
    """
    return {
        "type": "object",
        "properties": {
            "insights": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "insight": {"type": "string"},
                        "category": {"type": "string"},
                        "priority": {"type": "string"},
                        "estimated_impact": {"type": "string"},
                        "implementation_suggestion": {"type": "string"}
                    }
                }
            }
        }
    }


def generate_content_format_prompt(ai_insights: Dict[str, Any]) -> str:
    """
    Generate a comprehensive prompt for content format suggestions.
    
    Args:
        ai_insights: AI-processed insights
        
    Returns:
        Formatted prompt string
    """
    prompt = f"""
    Suggest content formats based on the following AI insights:

    AI Insights: {json.dumps(ai_insights, indent=2)}

    Provide comprehensive content format suggestions including:
    1. Content format recommendations
    2. Use cases for each format
    3. Recommended topics
    4. Estimated impact
    5. Implementation considerations
    6. Engagement potential
    
    Format as structured JSON with detailed suggestions.
    """
    
    return prompt.strip()


def generate_content_format_schema() -> Dict[str, Any]:
    """
    Generate JSON schema for content format response.
    
    Returns:
        JSON schema dictionary
    """
    return {
        "type": "object",
        "properties": {
            "content_formats": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "format": {"type": "string"},
                        "description": {"type": "string"},
                        "use_cases": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "recommended_topics": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "estimated_impact": {"type": "string"},
                        "engagement_potential": {"type": "string"},
                        "implementation_difficulty": {"type": "string"}
                    }
                }
            }
        }
    }


def generate_topic_cluster_prompt(ai_insights: Dict[str, Any]) -> str:
    """
    Generate a comprehensive prompt for topic cluster creation.
    
    Args:
        ai_insights: AI-processed insights
        
    Returns:
        Formatted prompt string
    """
    prompt = f"""
    Create topic clusters based on the following AI insights:

    AI Insights: {json.dumps(ai_insights, indent=2)}

    Provide comprehensive topic cluster analysis including:
    1. Main topic clusters
    2. Subtopics within each cluster
    3. Keyword relationships
    4. Content hierarchy
    5. Implementation strategy
    6. SEO optimization opportunities
    
    Format as structured JSON with detailed clusters.
    """
    
    return prompt.strip()


def generate_topic_cluster_schema() -> Dict[str, Any]:
    """
    Generate JSON schema for topic cluster response.
    
    Returns:
        JSON schema dictionary
    """
    return {
        "type": "object",
        "properties": {
            "topic_clusters": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "cluster_name": {"type": "string"},
                        "main_topic": {"type": "string"},
                        "subtopics": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "keywords": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "content_suggestions": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "priority": {"type": "string"},
                        "estimated_impact": {"type": "string"}
                    }
                }
            },
            "summary": {
                "type": "object",
                "properties": {
                    "total_clusters": {"type": "number"},
                    "total_keywords": {"type": "number"},
                    "implementation_priority": {"type": "string"},
                    "seo_opportunities": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                }
            }
        }
    }


def parse_ai_response(response: Any) -> Dict[str, Any]:
    """
    Parse and validate AI response.
    
    Args:
        response: Raw AI response (could be dict or string)
        
    Returns:
        Parsed response dictionary
    """
    try:
        if isinstance(response, dict):
            return response
        elif isinstance(response, str):
            return json.loads(response)
        else:
            logger.error(f"Unexpected response type from AI service: {type(response)}")
            raise ValueError(f"Unexpected response type: {type(response)}")
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse AI response as JSON: {e}")
        raise ValueError(f"Invalid JSON response: {str(e)}")
    except Exception as e:
        logger.error(f"Error parsing AI response: {e}")
        raise ValueError(f"Response parsing error: {str(e)}")


def validate_ai_response(response: Dict[str, Any], schema: Dict[str, Any]) -> bool:
    """
    Validate AI response against expected schema.
    
    Args:
        response: Parsed AI response
        schema: Expected schema
        
    Returns:
        True if response is valid, False otherwise
    """
    try:
        # Basic validation - check if required properties exist
        required_properties = schema.get("properties", {}).keys()
        
        for prop in required_properties:
            if prop not in response:
                logger.warning(f"Missing required property in AI response: {prop}")
                return False
        
        return True
    except Exception as e:
        logger.error(f"Error validating AI response: {e}")
        return False


def create_fallback_response(response_type: str, industry: str = "") -> Dict[str, Any]:
    """
    Create fallback response when AI fails.
    
    Args:
        response_type: Type of response (trend, intent, opportunity, insights)
        industry: Industry context
        
    Returns:
        Fallback response dictionary
    """
    fallback_responses = {
        "trend": {
            "trends": {
                f"{industry} trends" if industry else "industry trends": {
                    "search_volume": 5000,
                    "difficulty": 45,
                    "trend": "rising",
                    "competition": "medium",
                    "intent": "informational",
                    "cpc": 2.5,
                    "seasonal_factor": 1.2
                }
            },
            "summary": {
                "total_keywords": 1,
                "high_volume_keywords": 1,
                "low_competition_keywords": 0,
                "trending_keywords": 1,
                "opportunity_score": 75
            },
            "recommendations": [
                {
                    "keyword": f"{industry} trends" if industry else "industry trends",
                    "recommendation": "Create comprehensive trend analysis content",
                    "priority": "high",
                    "estimated_impact": "High traffic potential"
                }
            ]
        },
        "intent": {
            "informational": [
                {
                    "keyword": "how to guide",
                    "intent_type": "educational",
                    "content_suggestions": ["Tutorial", "Step-by-step guide", "Explainer video"]
                },
                {
                    "keyword": "what is",
                    "intent_type": "definition",
                    "content_suggestions": ["Definition", "Overview", "Introduction"]
                }
            ],
            "transactional": [
                {
                    "keyword": "buy",
                    "intent_type": "purchase",
                    "content_suggestions": ["Product page", "Pricing", "Comparison"]
                },
                {
                    "keyword": "price",
                    "intent_type": "cost_inquiry",
                    "content_suggestions": ["Pricing page", "Cost calculator", "Quote request"]
                }
            ],
            "navigational": [
                {
                    "keyword": "company name",
                    "intent_type": "brand_search",
                    "content_suggestions": ["About page", "Company overview", "Contact"]
                }
            ],
            "summary": {
                "dominant_intent": "informational",
                "content_strategy_recommendations": [
                    "Focus on educational content",
                    "Create comprehensive guides",
                    "Develop FAQ sections",
                    "Build authority through expertise"
                ]
            }
        },
        "opportunity": [
            {
                "keyword": "industry best practices",
                "opportunity_type": "content_gap",
                "search_volume": 3000,
                "competition_level": "low",
                "difficulty_score": 35,
                "estimated_traffic": "2K+ monthly",
                "content_suggestions": ["Comprehensive guide", "Best practices list", "Expert tips"],
                "priority": "high",
                "implementation_time": "2-3 weeks"
            },
            {
                "keyword": "industry trends 2024",
                "opportunity_type": "trending",
                "search_volume": 5000,
                "competition_level": "medium",
                "difficulty_score": 45,
                "estimated_traffic": "3K+ monthly",
                "content_suggestions": ["Trend analysis", "Industry report", "Future predictions"],
                "priority": "medium",
                "implementation_time": "3-4 weeks"
            }
        ],
        "insights": {
            "insights": [
                {
                    "insight": "Focus on educational content to capture informational search intent",
                    "category": "content_strategy",
                    "priority": "high",
                    "estimated_impact": "High engagement and authority building",
                    "implementation_suggestion": "Create comprehensive guides and tutorials"
                },
                {
                    "insight": "Develop comprehensive guides for high-opportunity keywords",
                    "category": "keyword_strategy",
                    "priority": "high",
                    "estimated_impact": "Improved search rankings",
                    "implementation_suggestion": "Focus on keywords with high opportunity scores"
                }
            ]
        }
    }
    
    return fallback_responses.get(response_type, {})


def get_content_recommendations_by_intent(intent_type: str) -> List[str]:
    """
    Get content recommendations based on intent type.
    
    Args:
        intent_type: Type of search intent
        
    Returns:
        List of content recommendations
    """
    recommendations = {
        IntentType.INFORMATIONAL: [
            "Create comprehensive guide",
            "Add step-by-step instructions",
            "Include examples and case studies",
            "Provide expert insights"
        ],
        IntentType.COMMERCIAL: [
            "Create comparison content",
            "Add product reviews",
            "Include pricing information",
            "Provide buying guides"
        ],
        IntentType.TRANSACTIONAL: [
            "Create product pages",
            "Add pricing information",
            "Include purchase options",
            "Provide customer testimonials"
        ],
        IntentType.NAVIGATIONAL: [
            "Create brand pages",
            "Add company information",
            "Include contact details",
            "Provide about us content"
        ]
    }
    
    return recommendations.get(intent_type, [])


def get_opportunity_recommendation(opportunity_type: str) -> str:
    """
    Get recommendation for opportunity type.
    
    Args:
        opportunity_type: Type of opportunity
        
    Returns:
        Recommendation string
    """
    recommendations = {
        'high_volume_low_competition': 'Create comprehensive content targeting this keyword',
        'medium_volume_medium_competition': 'Develop competitive content with unique angle',
        'trending_keyword': 'Create timely content to capitalize on trend',
        'high_value_commercial': 'Focus on conversion-optimized content',
        'content_gap': 'Fill content gap with comprehensive coverage',
        'low_competition_opportunity': 'Target this keyword for quick wins',
        'standard_opportunity': 'Create relevant content for this keyword'
    }
    
    return recommendations.get(opportunity_type, 'Create relevant content for this keyword')
