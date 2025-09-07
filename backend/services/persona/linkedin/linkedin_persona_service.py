"""
LinkedIn Persona Service
Handles LinkedIn-specific persona generation and optimization.
"""

from typing import Dict, Any, Optional
from loguru import logger

from services.llm_providers.gemini_provider import gemini_structured_json_response
from .linkedin_persona_prompts import LinkedInPersonaPrompts
from .linkedin_persona_schemas import LinkedInPersonaSchemas


class LinkedInPersonaService:
    """Service for generating LinkedIn-specific persona adaptations."""
    
    def __init__(self):
        """Initialize the LinkedIn persona service."""
        self.prompts = LinkedInPersonaPrompts()
        self.schemas = LinkedInPersonaSchemas()
        logger.info("LinkedInPersonaService initialized")
    
    def generate_linkedin_persona(self, core_persona: Dict[str, Any], onboarding_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate LinkedIn-specific persona adaptation using optimized chained prompts.
        
        Args:
            core_persona: The core writing persona
            onboarding_data: User's onboarding data
            
        Returns:
            LinkedIn-optimized persona data
        """
        try:
            logger.info("Generating LinkedIn-specific persona with optimized prompts")
            
            # Build focused LinkedIn prompt (without core persona JSON)
            prompt = self.prompts.build_focused_linkedin_prompt(onboarding_data)
            
            # Create system prompt with core persona
            system_prompt = self.prompts.build_linkedin_system_prompt(core_persona)
            
            # Get LinkedIn-specific schema
            schema = self.schemas.get_enhanced_linkedin_schema()
            
            # Generate structured response using Gemini with optimized prompts
            response = gemini_structured_json_response(
                prompt=prompt,
                schema=schema,
                temperature=0.2,
                max_tokens=4096,
                system_prompt=system_prompt
            )
            
            if "error" in response:
                logger.error(f"LinkedIn persona generation failed: {response['error']}")
                return {"error": f"LinkedIn persona generation failed: {response['error']}"}
            
            # Validate the generated persona
            validation_results = self.validate_linkedin_persona(response)
            logger.info(f"LinkedIn persona validation: Quality Score: {validation_results['quality_score']:.1f}%, Valid: {validation_results['is_valid']}")

            # Add validation results to persona data
            response["validation_results"] = validation_results

            # Apply comprehensive algorithm optimization
            optimized_response = self.optimize_for_linkedin_algorithm(response)
            logger.info("✅ LinkedIn persona algorithm optimization applied")

            logger.info("✅ LinkedIn persona generated and optimized successfully")
            return optimized_response
            
        except Exception as e:
            logger.error(f"Error generating LinkedIn persona: {str(e)}")
            return {"error": f"Failed to generate LinkedIn persona: {str(e)}"}
    
    def get_linkedin_constraints(self) -> Dict[str, Any]:
        """Get LinkedIn platform constraints."""
        return self.prompts.get_linkedin_platform_constraints()
    
    def validate_linkedin_persona(self, persona_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive validation of LinkedIn persona data for completeness and quality.
        
        Args:
            persona_data: LinkedIn persona data to validate
            
        Returns:
            Detailed validation results with quality metrics and recommendations
        """
        try:
            validation_results = {
                "is_valid": True,
                "quality_score": 0.0,
                "completeness_score": 0.0,
                "professional_context_score": 0.0,
                "linkedin_optimization_score": 0.0,
                "missing_fields": [],
                "incomplete_fields": [],
                "recommendations": [],
                "quality_issues": [],
                "strengths": [],
                "validation_details": {}
            }
            
            # 1. CORE FIELDS VALIDATION (30% of score)
            core_fields_score = self._validate_core_fields(persona_data, validation_results)
            
            # 2. LINKEDIN-SPECIFIC FIELDS VALIDATION (40% of score)
            linkedin_fields_score = self._validate_linkedin_specific_fields(persona_data, validation_results)
            
            # 3. PROFESSIONAL CONTEXT VALIDATION (20% of score)
            professional_context_score = self._validate_professional_context(persona_data, validation_results)
            
            # 4. CONTENT QUALITY VALIDATION (10% of score)
            content_quality_score = self._validate_content_quality(persona_data, validation_results)
            
            # Calculate overall quality score
            validation_results["quality_score"] = (
                core_fields_score * 0.3 +
                linkedin_fields_score * 0.4 +
                professional_context_score * 0.2 +
                content_quality_score * 0.1
            )
            
            # Set completeness score
            validation_results["completeness_score"] = core_fields_score
            validation_results["professional_context_score"] = professional_context_score
            validation_results["linkedin_optimization_score"] = linkedin_fields_score
            
            # Determine if persona is valid
            validation_results["is_valid"] = (
                validation_results["quality_score"] >= 70.0 and
                len(validation_results["missing_fields"]) == 0
            )
            
            # Add quality assessment
            self._assess_persona_quality(validation_results)
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Error validating LinkedIn persona: {str(e)}")
            return {
                "is_valid": False,
                "quality_score": 0.0,
                "error": str(e)
            }
    
    def _validate_core_fields(self, persona_data: Dict[str, Any], validation_results: Dict[str, Any]) -> float:
        """Validate core LinkedIn persona fields."""
        core_fields = {
            "platform_type": {"required": True, "type": str},
            "sentence_metrics": {"required": True, "type": dict, "subfields": ["max_sentence_length", "optimal_sentence_length"]},
            "lexical_adaptations": {"required": True, "type": dict, "subfields": ["platform_specific_words", "hashtag_strategy"]},
            "content_format_rules": {"required": True, "type": dict, "subfields": ["character_limit", "paragraph_structure"]},
            "engagement_patterns": {"required": True, "type": dict, "subfields": ["posting_frequency", "optimal_posting_times"]},
            "platform_best_practices": {"required": True, "type": list}
        }
        
        score = 0.0
        total_fields = len(core_fields)
        
        for field, config in core_fields.items():
            if field not in persona_data:
                validation_results["missing_fields"].append(field)
                continue
            
            field_data = persona_data[field]
            field_score = 0.0
            
            # Check field type
            if isinstance(field_data, config["type"]):
                field_score += 0.5
            else:
                validation_results["quality_issues"].append(f"{field} has incorrect type: expected {config['type'].__name__}")
            
            # Check subfields if specified
            if "subfields" in config and isinstance(field_data, dict):
                subfield_score = 0.0
                for subfield in config["subfields"]:
                    if subfield in field_data and field_data[subfield]:
                        subfield_score += 1.0
                    else:
                        validation_results["incomplete_fields"].append(f"{field}.{subfield}")
                
                if config["subfields"]:
                    field_score += (subfield_score / len(config["subfields"])) * 0.5
            
            score += field_score
            validation_results["validation_details"][field] = {
                "present": True,
                "type_correct": isinstance(field_data, config["type"]),
                "completeness": field_score
            }
        
        return (score / total_fields) * 100
    
    def _validate_linkedin_specific_fields(self, persona_data: Dict[str, Any], validation_results: Dict[str, Any]) -> float:
        """Validate LinkedIn-specific optimization fields."""
        linkedin_fields = {
            "professional_networking": {
                "required": True,
                "subfields": ["thought_leadership_positioning", "industry_authority_building", "professional_relationship_strategies"]
            },
            "linkedin_features": {
                "required": True,
                "subfields": ["articles_strategy", "polls_optimization", "events_networking", "carousels_education"]
            },
            "algorithm_optimization": {
                "required": True,
                "subfields": ["engagement_patterns", "content_timing", "professional_value_metrics"]
            },
            "professional_context_optimization": {
                "required": True,
                "subfields": ["industry_specific_positioning", "expertise_level_adaptation", "demographic_targeting"]
            }
        }
        
        score = 0.0
        total_fields = len(linkedin_fields)
        
        for field, config in linkedin_fields.items():
            if field not in persona_data:
                validation_results["missing_fields"].append(field)
                validation_results["recommendations"].append(f"Add {field} for enhanced LinkedIn optimization")
                continue
            
            field_data = persona_data[field]
            if not isinstance(field_data, dict):
                validation_results["quality_issues"].append(f"{field} should be a dictionary")
                continue
            
            field_score = 0.0
            for subfield in config["subfields"]:
                if subfield in field_data and field_data[subfield]:
                    field_score += 1.0
                else:
                    validation_results["incomplete_fields"].append(f"{field}.{subfield}")
            
            field_score = (field_score / len(config["subfields"])) * 100
            score += field_score
            
            validation_results["validation_details"][field] = {
                "present": True,
                "completeness": field_score,
                "subfields_present": len([sf for sf in config["subfields"] if sf in field_data and field_data[sf]])
            }
        
        return score / total_fields
    
    def _validate_professional_context(self, persona_data: Dict[str, Any], validation_results: Dict[str, Any]) -> float:
        """Validate professional context optimization."""
        if "professional_context_optimization" not in persona_data:
            validation_results["missing_fields"].append("professional_context_optimization")
            return 0.0
        
        context_data = persona_data["professional_context_optimization"]
        if not isinstance(context_data, dict):
            validation_results["quality_issues"].append("professional_context_optimization should be a dictionary")
            return 0.0
        
        professional_fields = [
            "industry_specific_positioning",
            "expertise_level_adaptation", 
            "company_size_considerations",
            "business_model_alignment",
            "professional_role_authority",
            "demographic_targeting",
            "psychographic_engagement",
            "conversion_optimization"
        ]
        
        score = 0.0
        for field in professional_fields:
            if field in context_data and context_data[field]:
                score += 1.0
                # Check for meaningful content (not just placeholder text)
                if isinstance(context_data[field], str) and len(context_data[field]) > 50:
                    score += 0.5
            else:
                validation_results["incomplete_fields"].append(f"professional_context_optimization.{field}")
        
        return (score / len(professional_fields)) * 100
    
    def _validate_content_quality(self, persona_data: Dict[str, Any], validation_results: Dict[str, Any]) -> float:
        """Validate content quality and depth."""
        score = 0.0
        
        # Check for meaningful content in key fields
        quality_checks = [
            ("sentence_metrics", "optimal_sentence_length"),
            ("lexical_adaptations", "platform_specific_words"),
            ("professional_networking", "thought_leadership_positioning"),
            ("linkedin_features", "articles_strategy")
        ]
        
        for field, subfield in quality_checks:
            if field in persona_data and subfield in persona_data[field]:
                content = persona_data[field][subfield]
                if isinstance(content, str) and len(content) > 30:
                    score += 1.0
                elif isinstance(content, list) and len(content) > 3:
                    score += 1.0
                else:
                    validation_results["quality_issues"].append(f"{field}.{subfield} content too brief")
            else:
                validation_results["quality_issues"].append(f"{field}.{subfield} missing or empty")
        
        return (score / len(quality_checks)) * 100
    
    def _assess_persona_quality(self, validation_results: Dict[str, Any]) -> None:
        """Assess overall persona quality and provide recommendations."""
        quality_score = validation_results["quality_score"]
        
        if quality_score >= 90:
            validation_results["strengths"].append("Excellent LinkedIn persona with comprehensive optimization")
        elif quality_score >= 80:
            validation_results["strengths"].append("Strong LinkedIn persona with good optimization")
        elif quality_score >= 70:
            validation_results["strengths"].append("Good LinkedIn persona with basic optimization")
        else:
            validation_results["quality_issues"].append("LinkedIn persona needs significant improvement")
        
        # Add specific recommendations based on missing fields
        if "professional_context_optimization" in validation_results["missing_fields"]:
            validation_results["recommendations"].append("Add professional context optimization for industry-specific positioning")
        
        if "algorithm_optimization" in validation_results["missing_fields"]:
            validation_results["recommendations"].append("Add algorithm optimization for better LinkedIn reach")
        
        if validation_results["incomplete_fields"]:
            validation_results["recommendations"].append(f"Complete {len(validation_results['incomplete_fields'])} incomplete fields for better optimization")
        
        # Add enterprise-grade recommendations
        if quality_score >= 80:
            validation_results["recommendations"].append("Persona is enterprise-ready for professional LinkedIn content")
        else:
            validation_results["recommendations"].append("Consider regenerating persona with more comprehensive data")
    
    def optimize_for_linkedin_algorithm(self, persona_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive LinkedIn algorithm optimization for maximum reach and engagement.
        
        Args:
            persona_data: LinkedIn persona data to optimize
            
        Returns:
            Algorithm-optimized persona data with advanced optimization features
        """
        try:
            optimized_persona = persona_data.copy()
            
            # Initialize algorithm optimization if not present
            if "algorithm_optimization" not in optimized_persona:
                optimized_persona["algorithm_optimization"] = {}
            
            # 1. CONTENT QUALITY OPTIMIZATION
            optimized_persona["algorithm_optimization"]["content_quality_optimization"] = {
                "original_insights_priority": [
                    "Share proprietary industry insights and case studies",
                    "Publish data-driven analyses and research findings",
                    "Create thought leadership content with unique perspectives",
                    "Avoid generic or recycled content that lacks value"
                ],
                "professional_credibility_boost": [
                    "Include relevant credentials and expertise indicators",
                    "Reference industry experience and achievements",
                    "Use professional language and terminology appropriately",
                    "Maintain consistent brand voice and messaging"
                ],
                "content_depth_requirements": [
                    "Provide actionable insights and practical advice",
                    "Include specific examples and real-world applications",
                    "Offer comprehensive analysis rather than surface-level content",
                    "Create content that solves professional problems"
                ]
            }
            
            # 2. MULTIMEDIA FORMAT OPTIMIZATION
            optimized_persona["algorithm_optimization"]["multimedia_strategy"] = {
                "native_video_optimization": [
                    "Upload videos directly to LinkedIn for maximum reach",
                    "Keep videos 1-3 minutes for optimal engagement",
                    "Include captions for accessibility and broader reach",
                    "Start with compelling hooks to retain viewers"
                ],
                "carousel_document_strategy": [
                    "Create swipeable educational content and tutorials",
                    "Use 5-10 slides for optimal engagement",
                    "Include clear, scannable text and visuals",
                    "End with strong call-to-action"
                ],
                "visual_content_optimization": [
                    "Use high-quality, professional images and graphics",
                    "Create infographics that convey complex information simply",
                    "Design visually appealing quote cards and statistics",
                    "Ensure all visuals align with professional brand"
                ]
            }
            
            # 3. ENGAGEMENT OPTIMIZATION
            optimized_persona["algorithm_optimization"]["engagement_optimization"] = {
                "comment_encouragement_strategies": [
                    "Ask thought-provoking questions that invite discussion",
                    "Pose industry-specific challenges or scenarios",
                    "Request personal experiences and insights",
                    "Create polls and surveys for interactive engagement"
                ],
                "network_interaction_boost": [
                    "Respond to comments within 2-4 hours for maximum visibility",
                    "Engage meaningfully with others' content before posting",
                    "Share and comment on industry leaders' posts",
                    "Participate actively in relevant LinkedIn groups"
                ],
                "professional_relationship_building": [
                    "Tag relevant connections when appropriate",
                    "Mention industry experts and thought leaders",
                    "Collaborate with peers on joint content",
                    "Build genuine professional relationships"
                ]
            }
            
            # 4. TIMING AND FREQUENCY OPTIMIZATION
            optimized_persona["algorithm_optimization"]["timing_optimization"] = {
                "optimal_posting_schedule": [
                    "Tuesday-Thursday: 8-11 AM EST for maximum professional engagement",
                    "Wednesday: Peak day for B2B content and thought leadership",
                    "Avoid posting on weekends unless targeting specific audiences",
                    "Maintain consistent posting schedule for algorithm recognition"
                ],
                "frequency_optimization": [
                    "Post 3-5 times per week for consistent visibility",
                    "Balance original content with curated industry insights",
                    "Space posts 4-6 hours apart to avoid audience fatigue",
                    "Monitor engagement rates to adjust frequency"
                ],
                "timezone_considerations": [
                    "Consider global audience time zones for international reach",
                    "Adjust posting times based on target audience location",
                    "Use LinkedIn Analytics to identify peak engagement times",
                    "Test different time slots to optimize reach"
                ]
            }
            
            # 5. HASHTAG AND DISCOVERABILITY OPTIMIZATION
            optimized_persona["algorithm_optimization"]["discoverability_optimization"] = {
                "strategic_hashtag_usage": [
                    "Use 3-5 relevant hashtags for optimal reach",
                    "Mix broad industry hashtags with niche-specific tags",
                    "Include trending hashtags when relevant to content",
                    "Create branded hashtags for consistent brand recognition"
                ],
                "keyword_optimization": [
                    "Include industry-specific keywords naturally in content",
                    "Use professional terminology that resonates with target audience",
                    "Optimize for LinkedIn's search algorithm",
                    "Include location-based keywords for local reach"
                ],
                "content_categorization": [
                    "Tag content appropriately for LinkedIn's content categorization",
                    "Use consistent themes and topics for algorithm recognition",
                    "Create content series for sustained engagement",
                    "Leverage LinkedIn's content suggestions and trending topics"
                ]
            }
            
            # 6. LINKEDIN FEATURES OPTIMIZATION
            optimized_persona["algorithm_optimization"]["linkedin_features_optimization"] = {
                "articles_strategy": [
                    "Publish long-form articles for thought leadership positioning",
                    "Use compelling headlines that encourage clicks",
                    "Include relevant images and formatting for readability",
                    "Cross-promote articles in regular posts"
                ],
                "polls_and_surveys": [
                    "Create engaging polls to drive interaction",
                    "Ask industry-relevant questions that spark discussion",
                    "Use poll results to create follow-up content",
                    "Share poll insights to provide value to audience"
                ],
                "events_and_networking": [
                    "Host or participate in LinkedIn events and webinars",
                    "Use LinkedIn's event features for promotion and networking",
                    "Create virtual networking opportunities",
                    "Leverage LinkedIn Live for real-time engagement"
                ]
            }
            
            # 7. PERFORMANCE MONITORING AND OPTIMIZATION
            optimized_persona["algorithm_optimization"]["performance_monitoring"] = {
                "key_metrics_tracking": [
                    "Monitor engagement rate (likes, comments, shares, saves)",
                    "Track reach and impression metrics",
                    "Analyze click-through rates on links and CTAs",
                    "Measure follower growth and network expansion"
                ],
                "content_performance_analysis": [
                    "Identify top-performing content types and topics",
                    "Analyze posting times for optimal engagement",
                    "Track hashtag performance and reach",
                    "Monitor audience demographics and interests"
                ],
                "optimization_recommendations": [
                    "A/B test different content formats and styles",
                    "Experiment with posting frequencies and timing",
                    "Test various hashtag combinations and strategies",
                    "Continuously refine content based on performance data"
                ]
            }
            
            # 8. PROFESSIONAL CONTEXT OPTIMIZATION
            optimized_persona["algorithm_optimization"]["professional_context_optimization"] = {
                "industry_specific_optimization": [
                    "Tailor content to industry-specific trends and challenges",
                    "Use industry terminology and references appropriately",
                    "Address current industry issues and developments",
                    "Position as thought leader within specific industry"
                ],
                "career_stage_targeting": [
                    "Create content relevant to different career stages",
                    "Address professional development and growth topics",
                    "Share career insights and advancement strategies",
                    "Provide value to both junior and senior professionals"
                ],
                "company_size_considerations": [
                    "Adapt content for different company sizes and structures",
                    "Address challenges specific to startups, SMBs, and enterprises",
                    "Provide relevant insights for different organizational contexts",
                    "Consider decision-making processes and hierarchies"
                ]
            }
            
            logger.info("✅ LinkedIn persona comprehensively optimized for 2024 algorithm performance")
            return optimized_persona
            
        except Exception as e:
            logger.error(f"Error optimizing LinkedIn persona for algorithm: {str(e)}")
            return persona_data
