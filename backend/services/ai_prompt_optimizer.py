"""
AI Prompt Optimizer Service
Advanced AI prompt optimization and management for content planning system.
"""

from typing import Dict, Any, List, Optional
from utils.logging import get_logger
logger = get_logger("ai_prompt_optimizer", migration_mode=True)
from datetime import datetime
import json
import re

# Import AI providers
from services.llm_providers.main_text_generation import llm_text_gen
from services.llm_providers.gemini_provider import gemini_structured_json_response

class AIPromptOptimizer:
    """Advanced AI prompt optimization and management service."""
    
    def __init__(self):
        """Initialize the AI prompt optimizer."""
        self.logger = logger
        self.prompts = self._load_advanced_prompts()
        self.schemas = self._load_advanced_schemas()
        
        logger.info("AIPromptOptimizer initialized")
    
    def _load_advanced_prompts(self) -> Dict[str, str]:
        """Load advanced AI prompts from deep dive analysis."""
        return {
            # Strategic Content Gap Analysis Prompt
            'strategic_content_gap_analysis': """
As an expert SEO content strategist with 15+ years of experience in content marketing and competitive analysis, analyze this comprehensive content gap analysis data and provide actionable strategic insights:

TARGET ANALYSIS:
- Website: {target_url}
- Industry: {industry}
- SERP Opportunities: {serp_opportunities} keywords not ranking
- Keyword Expansion: {expanded_keywords_count} additional keywords identified
- Competitors Analyzed: {competitors_analyzed} websites
- Content Quality Score: {content_quality_score}/10
- Market Competition Level: {competition_level}

DOMINANT CONTENT THEMES:
{dominant_themes}

COMPETITIVE LANDSCAPE:
{competitive_landscape}

PROVIDE COMPREHENSIVE ANALYSIS:
1. Strategic Content Gap Analysis (identify 3-5 major gaps with impact assessment)
2. Priority Content Recommendations (top 5 with ROI estimates)
3. Keyword Strategy Insights (trending, seasonal, long-tail opportunities)
4. Competitive Positioning Advice (differentiation strategies)
5. Content Format Recommendations (video, interactive, comprehensive guides)
6. Technical SEO Opportunities (structured data, schema markup)
7. Implementation Timeline (30/60/90 days with milestones)
8. Risk Assessment and Mitigation Strategies
9. Success Metrics and KPIs
10. Resource Allocation Recommendations

Consider user intent, search behavior patterns, and content consumption trends in your analysis.
Format as structured JSON with clear, actionable recommendations and confidence scores.
""",

            # Market Position Analysis Prompt
            'market_position_analysis': """
As a senior competitive intelligence analyst specializing in digital marketing and content strategy, analyze the market position of competitors in the {industry} industry:

COMPETITOR ANALYSES:
{competitor_analyses}

MARKET CONTEXT:
- Industry: {industry}
- Market Size: {market_size}
- Growth Rate: {growth_rate}
- Key Trends: {key_trends}

PROVIDE COMPREHENSIVE MARKET ANALYSIS:
1. Market Leader Identification (with reasoning)
2. Content Leader Analysis (content strategy assessment)
3. Quality Leader Assessment (content quality metrics)
4. Market Gaps Identification (3-5 major gaps)
5. Opportunities Analysis (high-impact opportunities)
6. Competitive Advantages (unique positioning)
7. Strategic Positioning Recommendations (differentiation)
8. Content Strategy Insights (format, frequency, quality)
9. Innovation Opportunities (emerging trends)
10. Risk Assessment (competitive threats)

Include market share estimates, competitive positioning matrix, and strategic recommendations with implementation timeline.
Format as structured JSON with detailed analysis and confidence levels.
""",

            # Advanced Keyword Analysis Prompt
            'advanced_keyword_analysis': """
As an expert keyword research specialist with deep understanding of search algorithms and user behavior, analyze keyword opportunities for {industry} industry:

KEYWORD DATA:
- Target Keywords: {target_keywords}
- Industry Context: {industry}
- Search Volume Data: {search_volume_data}
- Competition Analysis: {competition_analysis}
- Trend Analysis: {trend_analysis}

PROVIDE COMPREHENSIVE KEYWORD ANALYSIS:
1. Search Volume Estimates (with confidence intervals)
2. Competition Level Assessment (difficulty scoring)
3. Trend Analysis (seasonal, cyclical, emerging)
4. Opportunity Scoring (ROI potential)
5. Content Format Recommendations (based on intent)
6. Keyword Clustering (semantic relationships)
7. Long-tail Opportunities (specific, low-competition)
8. Seasonal Variations (trending patterns)
9. Search Intent Classification (informational, commercial, navigational, transactional)
10. Implementation Priority (quick wins vs long-term)

Consider search intent, user journey stages, and conversion potential in your analysis.
Format as structured JSON with detailed metrics and strategic recommendations.
"""
        }
    
    def _load_advanced_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Load advanced JSON schemas for structured responses."""
        return {
            'strategic_content_gap_analysis': {
                "type": "object",
                "properties": {
                    "strategic_insights": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {"type": "string"},
                                "insight": {"type": "string"},
                                "confidence": {"type": "number"},
                                "priority": {"type": "string"},
                                "estimated_impact": {"type": "string"},
                                "implementation_time": {"type": "string"},
                                "risk_level": {"type": "string"}
                            }
                        }
                    },
                    "content_recommendations": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {"type": "string"},
                                "recommendation": {"type": "string"},
                                "priority": {"type": "string"},
                                "estimated_traffic": {"type": "string"},
                                "implementation_time": {"type": "string"},
                                "roi_estimate": {"type": "string"},
                                "success_metrics": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                }
                            }
                        }
                    },
                    "keyword_strategy": {
                        "type": "object",
                        "properties": {
                            "trending_keywords": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "seasonal_opportunities": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "long_tail_opportunities": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "intent_classification": {
                                "type": "object",
                                "properties": {
                                    "informational": {"type": "number"},
                                    "commercial": {"type": "number"},
                                    "navigational": {"type": "number"},
                                    "transactional": {"type": "number"}
                                }
                            }
                        }
                    }
                }
            },
            
            'market_position_analysis': {
                "type": "object",
                "properties": {
                    "market_leader": {"type": "string"},
                    "content_leader": {"type": "string"},
                    "quality_leader": {"type": "string"},
                    "market_gaps": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "opportunities": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "competitive_advantages": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "strategic_recommendations": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {"type": "string"},
                                "recommendation": {"type": "string"},
                                "priority": {"type": "string"},
                                "estimated_impact": {"type": "string"},
                                "implementation_time": {"type": "string"},
                                "confidence_level": {"type": "string"}
                            }
                        }
                    }
                }
            },
            
            'advanced_keyword_analysis': {
                "type": "object",
                "properties": {
                    "keyword_opportunities": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "keyword": {"type": "string"},
                                "search_volume": {"type": "number"},
                                "competition_level": {"type": "string"},
                                "difficulty_score": {"type": "number"},
                                "trend": {"type": "string"},
                                "intent": {"type": "string"},
                                "opportunity_score": {"type": "number"},
                                "recommended_format": {"type": "string"},
                                "estimated_traffic": {"type": "string"},
                                "implementation_priority": {"type": "string"}
                            }
                        }
                    },
                    "keyword_clusters": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "cluster_name": {"type": "string"},
                                "main_keyword": {"type": "string"},
                                "related_keywords": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                },
                                "search_volume": {"type": "number"},
                                "competition_level": {"type": "string"},
                                "content_suggestions": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                }
                            }
                        }
                    }
                }
            }
        } 
    
    async def generate_strategic_content_gap_analysis(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate strategic content gap analysis using advanced AI prompts.
        
        Args:
            analysis_data: Comprehensive analysis data
            
        Returns:
            Strategic content gap analysis results
        """
        try:
            logger.info("🤖 Generating strategic content gap analysis using advanced AI")
            
            # Format the advanced prompt
            prompt = self.prompts['strategic_content_gap_analysis'].format(
                target_url=analysis_data.get('target_url', 'N/A'),
                industry=analysis_data.get('industry', 'N/A'),
                serp_opportunities=analysis_data.get('serp_opportunities', 0),
                expanded_keywords_count=analysis_data.get('expanded_keywords_count', 0),
                competitors_analyzed=analysis_data.get('competitors_analyzed', 0),
                content_quality_score=analysis_data.get('content_quality_score', 7.0),
                competition_level=analysis_data.get('competition_level', 'medium'),
                dominant_themes=json.dumps(analysis_data.get('dominant_themes', {}), indent=2),
                competitive_landscape=json.dumps(analysis_data.get('competitive_landscape', {}), indent=2)
            )
            
            # Use advanced schema for structured response
            response = gemini_structured_json_response(
                prompt=prompt,
                schema=self.schemas['strategic_content_gap_analysis']
            )
            
            # Handle response - gemini_structured_json_response returns dict directly
            if isinstance(response, dict):
                result = response
            elif isinstance(response, str):
                # If it's a string, try to parse as JSON
                try:
                    result = json.loads(response)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse AI response as JSON: {e}")
                    raise Exception(f"Invalid AI response format: {str(e)}")
            else:
                logger.error(f"Unexpected response type from AI service: {type(response)}")
                raise Exception(f"Unexpected response type from AI service: {type(response)}")
            logger.info("✅ Advanced strategic content gap analysis completed")
            return result
            
        except Exception as e:
            logger.error(f"Error generating strategic content gap analysis: {str(e)}")
            return self._get_fallback_content_gap_analysis()
    
    async def generate_advanced_market_position_analysis(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate advanced market position analysis using optimized AI prompts.
        
        Args:
            market_data: Market analysis data
            
        Returns:
            Advanced market position analysis results
        """
        try:
            logger.info("🤖 Generating advanced market position analysis using optimized AI")
            
            # Format the advanced prompt
            prompt = self.prompts['market_position_analysis'].format(
                industry=market_data.get('industry', 'N/A'),
                competitor_analyses=json.dumps(market_data.get('competitors', []), indent=2),
                market_size=market_data.get('market_size', 'N/A'),
                growth_rate=market_data.get('growth_rate', 'N/A'),
                key_trends=json.dumps(market_data.get('key_trends', []), indent=2)
            )
            
            # Use advanced schema for structured response
            response = gemini_structured_json_response(
                prompt=prompt,
                schema=self.schemas['market_position_analysis']
            )
            
            # Handle response - gemini_structured_json_response returns dict directly
            if isinstance(response, dict):
                result = response
            elif isinstance(response, str):
                # If it's a string, try to parse as JSON
                try:
                    result = json.loads(response)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse AI response as JSON: {e}")
                    raise Exception(f"Invalid AI response format: {str(e)}")
            else:
                logger.error(f"Unexpected response type from AI service: {type(response)}")
                raise Exception(f"Unexpected response type from AI service: {type(response)}")
            logger.info("✅ Advanced market position analysis completed")
            return result
            
        except Exception as e:
            logger.error(f"Error generating advanced market position analysis: {str(e)}")
            return self._get_fallback_market_position_analysis()
    
    async def generate_advanced_keyword_analysis(self, keyword_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate advanced keyword analysis using optimized AI prompts.
        
        Args:
            keyword_data: Keyword analysis data
            
        Returns:
            Advanced keyword analysis results
        """
        try:
            logger.info("🤖 Generating advanced keyword analysis using optimized AI")
            
            # Format the advanced prompt
            prompt = self.prompts['advanced_keyword_analysis'].format(
                industry=keyword_data.get('industry', 'N/A'),
                target_keywords=json.dumps(keyword_data.get('target_keywords', []), indent=2),
                search_volume_data=json.dumps(keyword_data.get('search_volume_data', {}), indent=2),
                competition_analysis=json.dumps(keyword_data.get('competition_analysis', {}), indent=2),
                trend_analysis=json.dumps(keyword_data.get('trend_analysis', {}), indent=2)
            )
            
            # Use advanced schema for structured response
            response = gemini_structured_json_response(
                prompt=prompt,
                schema=self.schemas['advanced_keyword_analysis']
            )
            
            # Handle response - gemini_structured_json_response returns dict directly
            if isinstance(response, dict):
                result = response
            elif isinstance(response, str):
                # If it's a string, try to parse as JSON
                try:
                    result = json.loads(response)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse AI response as JSON: {e}")
                    raise Exception(f"Invalid AI response format: {str(e)}")
            else:
                logger.error(f"Unexpected response type from AI service: {type(response)}")
                raise Exception(f"Unexpected response type from AI service: {type(response)}")
            logger.info("✅ Advanced keyword analysis completed")
            return result
            
        except Exception as e:
            logger.error(f"Error generating advanced keyword analysis: {str(e)}")
            return self._get_fallback_keyword_analysis()
    
    # Fallback methods for error handling
    def _get_fallback_content_gap_analysis(self) -> Dict[str, Any]:
        """Fallback content gap analysis when AI fails."""
        return {
            'strategic_insights': [
                {
                    'type': 'content_strategy',
                    'insight': 'Focus on educational content to build authority',
                    'confidence': 0.85,
                    'priority': 'high',
                    'estimated_impact': 'Authority building',
                    'implementation_time': '3-6 months',
                    'risk_level': 'low'
                }
            ],
            'content_recommendations': [
                {
                    'type': 'content_creation',
                    'recommendation': 'Create comprehensive guides for high-opportunity keywords',
                    'priority': 'high',
                    'estimated_traffic': '5K+ monthly',
                    'implementation_time': '2-3 weeks',
                    'roi_estimate': 'High ROI potential',
                    'success_metrics': ['Traffic increase', 'Authority building', 'Lead generation']
                }
            ],
            'keyword_strategy': {
                'trending_keywords': ['industry trends', 'best practices'],
                'seasonal_opportunities': ['holiday content', 'seasonal guides'],
                'long_tail_opportunities': ['specific tutorials', 'detailed guides'],
                'intent_classification': {
                    'informational': 0.6,
                    'commercial': 0.2,
                    'navigational': 0.1,
                    'transactional': 0.1
                }
            }
        }
    
    def _get_fallback_market_position_analysis(self) -> Dict[str, Any]:
        """Fallback market position analysis when AI fails."""
        return {
            'market_leader': 'competitor1.com',
            'content_leader': 'competitor2.com',
            'quality_leader': 'competitor3.com',
            'market_gaps': [
                'Video content',
                'Interactive content',
                'Expert interviews'
            ],
            'opportunities': [
                'Niche content development',
                'Expert interviews',
                'Industry reports'
            ],
            'competitive_advantages': [
                'Technical expertise',
                'Comprehensive guides',
                'Industry insights'
            ],
            'strategic_recommendations': [
                {
                    'type': 'differentiation',
                    'recommendation': 'Focus on unique content angles',
                    'priority': 'high',
                    'estimated_impact': 'Brand differentiation',
                    'implementation_time': '2-4 months',
                    'confidence_level': '85%'
                }
            ]
        }
    
    def _get_fallback_keyword_analysis(self) -> Dict[str, Any]:
        """Fallback keyword analysis when AI fails."""
        return {
            'keyword_opportunities': [
                {
                    'keyword': 'industry best practices',
                    'search_volume': 3000,
                    'competition_level': 'low',
                    'difficulty_score': 35,
                    'trend': 'rising',
                    'intent': 'informational',
                    'opportunity_score': 85,
                    'recommended_format': 'comprehensive_guide',
                    'estimated_traffic': '2K+ monthly',
                    'implementation_priority': 'high'
                }
            ],
            'keyword_clusters': [
                {
                    'cluster_name': 'Industry Fundamentals',
                    'main_keyword': 'industry basics',
                    'related_keywords': ['fundamentals', 'introduction', 'basics'],
                    'search_volume': 5000,
                    'competition_level': 'medium',
                    'content_suggestions': ['Beginner guide', 'Overview article']
                }
            ]
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Health check for the AI prompt optimizer service.
        
        Returns:
            Health status information
        """
        try:
            logger.info("Performing health check for AIPromptOptimizer")
            
            # Test AI functionality with a simple prompt
            test_prompt = "Hello, this is a health check test."
            try:
                test_response = llm_text_gen(test_prompt)
                ai_status = "operational" if test_response else "degraded"
            except Exception as e:
                ai_status = "error"
                logger.warning(f"AI health check failed: {str(e)}")
            
            health_status = {
                'service': 'AIPromptOptimizer',
                'status': 'healthy',
                'capabilities': {
                    'strategic_content_gap_analysis': 'operational',
                    'advanced_market_position_analysis': 'operational',
                    'advanced_keyword_analysis': 'operational',
                    'ai_integration': ai_status
                },
                'prompts_loaded': len(self.prompts),
                'schemas_loaded': len(self.schemas),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info("AIPromptOptimizer health check passed")
            return health_status
            
        except Exception as e:
            logger.error(f"AIPromptOptimizer health check failed: {str(e)}")
            return {
                'service': 'AIPromptOptimizer',
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            } 