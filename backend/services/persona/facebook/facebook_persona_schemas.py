"""
Facebook Persona Schemas
Defines Facebook-specific persona data structures and validation schemas.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class FacebookPersonaSchema(BaseModel):
    """Facebook-specific persona schema with platform optimizations."""
    
    # Core persona fields (inherited from base persona)
    persona_name: str = Field(..., description="Name of the persona")
    archetype: str = Field(..., description="Persona archetype")
    core_belief: str = Field(..., description="Core belief driving the persona")
    
    # Facebook-specific optimizations
    facebook_algorithm_optimization: Dict[str, Any] = Field(
        default_factory=dict,
        description="Facebook algorithm optimization strategies"
    )
    
    facebook_engagement_strategies: Dict[str, Any] = Field(
        default_factory=dict,
        description="Facebook-specific engagement strategies"
    )
    
    facebook_content_formats: Dict[str, Any] = Field(
        default_factory=dict,
        description="Facebook content format optimizations"
    )
    
    facebook_audience_targeting: Dict[str, Any] = Field(
        default_factory=dict,
        description="Facebook audience targeting strategies"
    )
    
    facebook_community_building: Dict[str, Any] = Field(
        default_factory=dict,
        description="Facebook community building strategies"
    )


class FacebookPersonaConstraints:
    """Facebook platform constraints and best practices."""
    
    @staticmethod
    def get_facebook_constraints() -> Dict[str, Any]:
        """Get Facebook-specific platform constraints."""
        return {
            "character_limit": 63206,
            "optimal_length": "40-80 words",
            "hashtag_limit": 30,
            "image_support": True,
            "video_support": True,
            "link_preview": True,
            "event_support": True,
            "group_sharing": True,
            "story_support": True,
            "reel_support": True,
            "carousel_support": True,
            "poll_support": True,
            "live_support": True,
            "algorithm_favors": [
                "engagement",
                "meaningful_interactions",
                "video_content",
                "community_posts",
                "authentic_content"
            ],
            "content_types": [
                "text_posts",
                "image_posts",
                "video_posts",
                "carousel_posts",
                "story_posts",
                "reel_posts",
                "event_posts",
                "poll_posts",
                "live_posts"
            ],
            "engagement_metrics": [
                "likes",
                "comments",
                "shares",
                "saves",
                "clicks",
                "reactions",
                "video_views",
                "story_views"
            ],
            "posting_frequency": {
                "optimal": "1-2 times per day",
                "maximum": "3-4 times per day",
                "minimum": "3-4 times per week"
            },
            "best_posting_times": [
                "9:00 AM - 11:00 AM",
                "1:00 PM - 3:00 PM",
                "5:00 PM - 7:00 PM"
            ],
            "content_guidelines": {
                "authenticity": "High priority - Facebook favors authentic content",
                "community_focus": "Build community and meaningful connections",
                "visual_content": "Images and videos perform better than text-only",
                "engagement_bait": "Avoid engagement bait - Facebook penalizes it",
                "clickbait": "Avoid clickbait headlines and misleading content"
            }
        }


class FacebookPersonaValidation:
    """Facebook persona validation rules and scoring."""
    
    @staticmethod
    def validate_facebook_persona(persona_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Facebook persona data for completeness and quality."""
        
        validation_results = {
            "is_valid": True,
            "quality_score": 0.0,
            "completeness_score": 0.0,
            "facebook_optimization_score": 0.0,
            "engagement_strategy_score": 0.0,
            "missing_fields": [],
            "incomplete_fields": [],
            "recommendations": [],
            "quality_issues": [],
            "strengths": [],
            "validation_details": {}
        }
        
        # Check required fields
        required_fields = [
            "persona_name", "archetype", "core_belief",
            "facebook_algorithm_optimization", "facebook_engagement_strategies"
        ]
        
        for field in required_fields:
            if not persona_data.get(field):
                validation_results["missing_fields"].append(field)
                validation_results["is_valid"] = False
        
        # Calculate completeness score
        total_fields = len(required_fields)
        present_fields = total_fields - len(validation_results["missing_fields"])
        validation_results["completeness_score"] = (present_fields / total_fields) * 100
        
        # Validate Facebook-specific optimizations
        facebook_opt = persona_data.get("facebook_algorithm_optimization", {})
        if facebook_opt:
            validation_results["facebook_optimization_score"] = 85.0
            validation_results["strengths"].append("Facebook algorithm optimization present")
        else:
            validation_results["quality_issues"].append("Missing Facebook algorithm optimization")
            validation_results["recommendations"].append("Add Facebook-specific algorithm strategies")
        
        # Validate engagement strategies
        engagement_strategies = persona_data.get("facebook_engagement_strategies", {})
        if engagement_strategies:
            validation_results["engagement_strategy_score"] = 80.0
            validation_results["strengths"].append("Facebook engagement strategies defined")
        else:
            validation_results["quality_issues"].append("Missing Facebook engagement strategies")
            validation_results["recommendations"].append("Define Facebook-specific engagement tactics")
        
        # Calculate overall quality score
        validation_results["quality_score"] = (
            validation_results["completeness_score"] * 0.4 +
            validation_results["facebook_optimization_score"] * 0.3 +
            validation_results["engagement_strategy_score"] * 0.3
        )
        
        # Add validation details
        validation_results["validation_details"] = {
            "total_fields_checked": total_fields,
            "present_fields": present_fields,
            "facebook_optimization_present": bool(facebook_opt),
            "engagement_strategies_present": bool(engagement_strategies),
            "validation_timestamp": "2024-01-01T00:00:00Z"  # Will be updated with actual timestamp
        }
        
        return validation_results


class FacebookPersonaOptimization:
    """Facebook persona optimization strategies and techniques."""
    
    @staticmethod
    def get_facebook_optimization_strategies() -> Dict[str, Any]:
        """Get comprehensive Facebook optimization strategies."""
        return {
            "algorithm_optimization": {
                "engagement_optimization": [
                    "Post when your audience is most active",
                    "Use Facebook's native video uploads instead of external links",
                    "Encourage meaningful comments and discussions",
                    "Respond to comments within 2 hours",
                    "Use Facebook Live for real-time engagement",
                    "Create shareable, valuable content",
                    "Use Facebook Stories for behind-the-scenes content",
                    "Leverage Facebook Groups for community building"
                ],
                "content_quality_optimization": [
                    "Create authentic, original content",
                    "Use high-quality images and videos",
                    "Write compelling captions that encourage engagement",
                    "Use Facebook's built-in editing tools",
                    "Create content that sparks conversations",
                    "Share user-generated content",
                    "Use Facebook's trending topics and hashtags",
                    "Create content that provides value to your audience"
                ],
                "timing_optimization": [
                    "Post during peak engagement hours (9-11 AM, 1-3 PM, 5-7 PM)",
                    "Use Facebook Insights to find your best posting times",
                    "Post consistently but not too frequently",
                    "Schedule posts for different time zones if global audience",
                    "Use Facebook's scheduling feature for optimal timing",
                    "Post when your competitors are less active",
                    "Consider your audience's daily routines and habits"
                ],
                "audience_targeting_optimization": [
                    "Use Facebook's audience insights for targeting",
                    "Create content for specific audience segments",
                    "Use Facebook's lookalike audiences",
                    "Target based on interests and behaviors",
                    "Use Facebook's custom audiences",
                    "Create content that resonates with your core audience",
                    "Use Facebook's demographic targeting",
                    "Leverage Facebook's psychographic targeting"
                ]
            },
            "engagement_strategies": {
                "community_building": [
                    "Create and moderate Facebook Groups",
                    "Host Facebook Live sessions regularly",
                    "Respond to all comments and messages",
                    "Share user-generated content",
                    "Create Facebook Events for community gatherings",
                    "Use Facebook's community features",
                    "Encourage user participation and feedback",
                    "Build relationships with your audience"
                ],
                "content_engagement": [
                    "Ask questions in your posts",
                    "Use polls and surveys to engage audience",
                    "Create interactive content like quizzes",
                    "Use Facebook's reaction buttons strategically",
                    "Create content that encourages sharing",
                    "Use Facebook's tagging feature appropriately",
                    "Create content that sparks discussions",
                    "Use Facebook's story features for engagement"
                ],
                "conversion_optimization": [
                    "Use clear call-to-actions in posts",
                    "Create Facebook-specific landing pages",
                    "Use Facebook's conversion tracking",
                    "Create content that drives traffic to your website",
                    "Use Facebook's lead generation features",
                    "Create content that builds trust and credibility",
                    "Use Facebook's retargeting capabilities",
                    "Create content that showcases your products/services"
                ]
            },
            "content_formats": {
                "text_posts": {
                    "optimal_length": "40-80 words",
                    "best_practices": [
                        "Use compelling headlines",
                        "Include relevant hashtags (1-2)",
                        "Ask questions to encourage engagement",
                        "Use emojis sparingly but effectively",
                        "Include clear call-to-actions"
                    ]
                },
                "image_posts": {
                    "optimal_specs": "1200x630 pixels",
                    "best_practices": [
                        "Use high-quality, original images",
                        "Include text overlay for key messages",
                        "Use consistent branding and colors",
                        "Create visually appealing graphics",
                        "Use Facebook's image editing tools"
                    ]
                },
                "video_posts": {
                    "optimal_length": "15-60 seconds for feed, 2-3 minutes for longer content",
                    "best_practices": [
                        "Upload videos directly to Facebook",
                        "Create engaging thumbnails",
                        "Add captions for accessibility",
                        "Use Facebook's video editing tools",
                        "Create videos that work without sound"
                    ]
                },
                "carousel_posts": {
                    "optimal_slides": "3-5 slides",
                    "best_practices": [
                        "Tell a story across slides",
                        "Use consistent design elements",
                        "Include clear navigation",
                        "Create slides that work individually",
                        "Use carousels for product showcases"
                    ]
                }
            },
            "audience_targeting": {
                "demographic_targeting": [
                    "Age and gender targeting",
                    "Location-based targeting",
                    "Education and work targeting",
                    "Relationship status targeting",
                    "Language targeting"
                ],
                "interest_targeting": [
                    "Hobbies and interests",
                    "Brand and product interests",
                    "Entertainment preferences",
                    "Lifestyle and behavior targeting",
                    "Purchase behavior targeting"
                ],
                "behavioral_targeting": [
                    "Device usage patterns",
                    "Travel behavior",
                    "Purchase behavior",
                    "Digital activity patterns",
                    "Life events targeting"
                ]
            },
            "community_building": {
                "group_management": [
                    "Create and moderate relevant Facebook Groups",
                    "Set clear group rules and guidelines",
                    "Encourage member participation",
                    "Share valuable content in groups",
                    "Use groups for customer support",
                    "Create group events and activities",
                    "Recognize and reward active members",
                    "Use groups for market research"
                ],
                "event_management": [
                    "Create Facebook Events for promotions",
                    "Use events for product launches",
                    "Host virtual events and webinars",
                    "Create recurring events for consistency",
                    "Use events for community building",
                    "Promote events across all channels",
                    "Follow up with event attendees",
                    "Use events for lead generation"
                ],
                "live_streaming": [
                    "Host regular Facebook Live sessions",
                    "Use live streaming for Q&A sessions",
                    "Create behind-the-scenes content",
                    "Use live streaming for product demos",
                    "Engage with viewers in real-time",
                    "Use live streaming for announcements",
                    "Create interactive live content",
                    "Use live streaming for customer support"
                ]
            }
        }
