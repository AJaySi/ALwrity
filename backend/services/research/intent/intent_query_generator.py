"""
Intent Query Generator

Generates multiple targeted research queries based on user intent.
Each query targets a specific deliverable or question.

Author: ALwrity Team
Version: 1.0
"""

import json
from typing import Dict, Any, List, Optional
from loguru import logger

from models.research_intent_models import (
    ResearchIntent,
    ResearchQuery,
    ExpectedDeliverable,
    ResearchPurpose,
)
from models.research_persona_models import ResearchPersona
from .intent_prompt_builder import IntentPromptBuilder


class IntentQueryGenerator:
    """
    Generates targeted research queries based on user intent.
    
    Instead of a single generic search, generates multiple queries
    each targeting a specific deliverable or question.
    """
    
    def __init__(self):
        """Initialize the query generator."""
        self.prompt_builder = IntentPromptBuilder()
        logger.info("IntentQueryGenerator initialized")
    
    async def generate_queries(
        self,
        intent: ResearchIntent,
        research_persona: Optional[ResearchPersona] = None,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate targeted research queries based on intent.
        
        Args:
            intent: The inferred research intent
            research_persona: Optional persona for context
            
        Returns:
            Dict with queries, enhanced_keywords, and research_angles
        """
        try:
            logger.info(f"Generating queries for: {intent.primary_question[:50]}...")
            
            # Build the query generation prompt
            prompt = self.prompt_builder.build_query_generation_prompt(
                intent=intent,
                research_persona=research_persona,
            )
            
            # Define the expected JSON schema
            query_schema = {
                "type": "object",
                "properties": {
                    "queries": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string"},
                                "purpose": {"type": "string"},
                                "provider": {"type": "string"},
                                "priority": {"type": "integer"},
                                "expected_results": {"type": "string"}
                            },
                            "required": ["query", "purpose", "provider", "priority", "expected_results"]
                        }
                    },
                    "enhanced_keywords": {"type": "array", "items": {"type": "string"}},
                    "research_angles": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["queries", "enhanced_keywords", "research_angles"]
            }
            
            # Call LLM for query generation
            from services.llm_providers.main_text_generation import llm_text_gen
            
            result = llm_text_gen(
                prompt=prompt,
                json_struct=query_schema,
                user_id=user_id
            )
            
            if isinstance(result, dict) and "error" in result:
                logger.error(f"Query generation failed: {result.get('error')}")
                return self._create_fallback_queries(intent)
            
            # Parse queries
            queries = self._parse_queries(result.get("queries", []))
            
            # Ensure we have queries for all expected deliverables
            queries = self._ensure_deliverable_coverage(queries, intent)
            
            # Sort by priority
            queries.sort(key=lambda q: q.priority, reverse=True)
            
            logger.info(f"Generated {len(queries)} targeted queries")
            
            return {
                "queries": queries,
                "enhanced_keywords": result.get("enhanced_keywords", []),
                "research_angles": result.get("research_angles", []),
            }
            
        except Exception as e:
            logger.error(f"Error generating queries: {e}")
            return self._create_fallback_queries(intent)
    
    def _parse_queries(self, raw_queries: List[Dict]) -> List[ResearchQuery]:
        """Parse raw query data into ResearchQuery objects."""
        
        queries = []
        for q in raw_queries:
            try:
                # Validate purpose
                purpose_str = q.get("purpose", "key_statistics")
                try:
                    purpose = ExpectedDeliverable(purpose_str)
                except ValueError:
                    purpose = ExpectedDeliverable.KEY_STATISTICS
                
                query = ResearchQuery(
                    query=q.get("query", ""),
                    purpose=purpose,
                    provider=q.get("provider", "exa"),
                    priority=min(max(int(q.get("priority", 3)), 1), 5),  # Clamp 1-5
                    expected_results=q.get("expected_results", ""),
                    addresses_primary_question=q.get("addresses_primary_question", False),
                    addresses_secondary_questions=q.get("addresses_secondary_questions", []),
                    targets_focus_areas=q.get("targets_focus_areas", []),
                    covers_also_answering=q.get("covers_also_answering", []),
                    justification=q.get("justification"),
                )
                queries.append(query)
            except Exception as e:
                logger.warning(f"Failed to parse query: {e}")
                continue
        
        return queries
    
    def _ensure_deliverable_coverage(
        self,
        queries: List[ResearchQuery],
        intent: ResearchIntent,
    ) -> List[ResearchQuery]:
        """Ensure we have queries for all expected deliverables."""
        
        # Get deliverables already covered
        covered = set(q.purpose.value for q in queries)
        
        # Check for missing deliverables
        for deliverable in intent.expected_deliverables:
            if deliverable not in covered:
                # Generate a query for this deliverable
                query = self._generate_query_for_deliverable(
                    deliverable=deliverable,
                    intent=intent,
                )
                queries.append(query)
        
        return queries
    
    def _generate_query_for_deliverable(
        self,
        deliverable: str,
        intent: ResearchIntent,
    ) -> ResearchQuery:
        """Generate a query targeting a specific deliverable."""
        
        # Extract topic from primary question
        topic = intent.original_input
        
        # Query templates by deliverable type
        templates = {
            ExpectedDeliverable.KEY_STATISTICS.value: {
                "query": f"{topic} statistics data report study",
                "provider": "exa",
                "priority": 5,
                "expected": "Statistical data and research findings",
            },
            ExpectedDeliverable.EXPERT_QUOTES.value: {
                "query": f"{topic} expert opinion interview insights",
                "provider": "exa",
                "priority": 4,
                "expected": "Expert opinions and authoritative quotes",
            },
            ExpectedDeliverable.CASE_STUDIES.value: {
                "query": f"{topic} case study success story implementation example",
                "provider": "exa",
                "priority": 4,
                "expected": "Real-world case studies and examples",
            },
            ExpectedDeliverable.TRENDS.value: {
                "query": f"{topic} trends 2025 future predictions emerging",
                "provider": "tavily",
                "priority": 4,
                "expected": "Current trends and future predictions",
            },
            ExpectedDeliverable.COMPARISONS.value: {
                "query": f"{topic} comparison vs versus alternatives",
                "provider": "exa",
                "priority": 4,
                "expected": "Comparison and alternative options",
            },
            ExpectedDeliverable.BEST_PRACTICES.value: {
                "query": f"{topic} best practices recommendations guidelines",
                "provider": "exa",
                "priority": 3,
                "expected": "Best practices and recommendations",
            },
            ExpectedDeliverable.STEP_BY_STEP.value: {
                "query": f"{topic} how to guide tutorial steps",
                "provider": "exa",
                "priority": 3,
                "expected": "Step-by-step guides and tutorials",
            },
            ExpectedDeliverable.PROS_CONS.value: {
                "query": f"{topic} advantages disadvantages pros cons benefits",
                "provider": "exa",
                "priority": 3,
                "expected": "Pros, cons, and trade-offs",
            },
            ExpectedDeliverable.DEFINITIONS.value: {
                "query": f"what is {topic} definition explained",
                "provider": "exa",
                "priority": 3,
                "expected": "Clear definitions and explanations",
            },
            ExpectedDeliverable.EXAMPLES.value: {
                "query": f"{topic} examples real world applications",
                "provider": "exa",
                "priority": 3,
                "expected": "Real-world examples and applications",
            },
            ExpectedDeliverable.PREDICTIONS.value: {
                "query": f"{topic} future outlook predictions 2025 2030",
                "provider": "tavily",
                "priority": 4,
                "expected": "Future predictions and outlook",
            },
            ExpectedDeliverable.CITATIONS.value: {
                "query": f"{topic} research paper study academic",
                "provider": "exa",
                "priority": 4,
                "expected": "Authoritative academic sources",
            },
        }
        
        template = templates.get(deliverable, {
            "query": f"{topic}",
            "provider": "exa",
            "priority": 3,
            "expected": "General information",
        })
        
        return ResearchQuery(
            query=template["query"],
            purpose=ExpectedDeliverable(deliverable) if deliverable in [e.value for e in ExpectedDeliverable] else ExpectedDeliverable.KEY_STATISTICS,
            provider=template["provider"],
            priority=template["priority"],
            expected_results=template["expected"],
            addresses_primary_question=False,
            addresses_secondary_questions=[],
            targets_focus_areas=[],
            covers_also_answering=[],
        )
    
    def _create_fallback_queries(self, intent: ResearchIntent) -> Dict[str, Any]:
        """Create fallback queries when AI generation fails."""
        
        topic = intent.original_input
        
        # Generate basic queries for each expected deliverable
        queries = []
        for deliverable in intent.expected_deliverables[:5]:  # Limit to 5
            query = self._generate_query_for_deliverable(deliverable, intent)
            queries.append(query)
        
        # Add a general query if we have none
        if not queries:
            queries.append(ResearchQuery(
                query=topic,
                purpose=ExpectedDeliverable.KEY_STATISTICS,
                provider="exa",
                priority=5,
                expected_results="General information and insights",
                addresses_primary_question=True,
                addresses_secondary_questions=[],
                targets_focus_areas=[],
                covers_also_answering=[],
            ))
        
        return {
            "queries": queries,
            "enhanced_keywords": topic.split()[:10],
            "research_angles": [
                f"Overview of {topic}",
                f"Latest trends in {topic}",
            ],
        }


class QueryOptimizer:
    """
    Optimizes queries for different research providers.
    
    Different providers have different strengths:
    - Exa: Semantic search, good for deep research
    - Tavily: Real-time search, good for news/trends
    - Google: Factual search, good for basic info
    """
    
    @staticmethod
    def optimize_for_exa(query: str, intent: ResearchIntent) -> Dict[str, Any]:
        """Optimize query and parameters for Exa."""
        
        # Determine best Exa settings based on deliverable
        deliverables = intent.expected_deliverables
        
        # Determine category
        category = None
        if ExpectedDeliverable.CITATIONS.value in deliverables:
            category = "research paper"
        elif ExpectedDeliverable.TRENDS.value in deliverables:
            category = "news"
        elif intent.purpose == ResearchPurpose.COMPARE.value:
            category = "company"
        
        # Determine search type
        search_type = "neural"  # Default to neural for semantic understanding
        if ExpectedDeliverable.TRENDS.value in deliverables:
            search_type = "auto"  # Auto is better for time-sensitive queries
        
        # Number of results
        num_results = 10
        if intent.depth == "expert":
            num_results = 20
        elif intent.depth == "overview":
            num_results = 5
        
        return {
            "query": query,
            "type": search_type,
            "category": category,
            "num_results": num_results,
            "text": True,
            "highlights": True,
        }
    
    @staticmethod
    def optimize_for_tavily(query: str, intent: ResearchIntent) -> Dict[str, Any]:
        """Optimize query and parameters for Tavily."""
        
        deliverables = intent.expected_deliverables
        
        # Determine topic
        topic = "general"
        if ExpectedDeliverable.TRENDS.value in deliverables:
            topic = "news"
        
        # Determine search depth based on depth and time sensitivity
        # advanced = 2 credits (best quality), basic/fast/ultra-fast = 1 credit
        search_depth = "basic"  # Default: balanced
        if intent.depth == "expert":
            search_depth = "advanced"  # Best quality for expert research
        elif intent.depth == "detailed":
            search_depth = "advanced"  # Better snippets for detailed research
        elif intent.time_sensitivity == "real_time":
            search_depth = "ultra-fast"  # Minimize latency for real-time
        elif intent.time_sensitivity == "recent":
            search_depth = "fast"  # Good balance for recent content
        
        # Include answer for factual queries
        include_answer = False
        if ExpectedDeliverable.DEFINITIONS.value in deliverables:
            include_answer = "advanced"
        elif ExpectedDeliverable.KEY_STATISTICS.value in deliverables:
            include_answer = "basic"
        
        # Time range for trends
        time_range = None
        if intent.time_sensitivity == "real_time":
            time_range = "day"
        elif intent.time_sensitivity == "recent":
            time_range = "week"
        elif ExpectedDeliverable.TRENDS.value in deliverables:
            time_range = "month"
        
        return {
            "query": query,
            "topic": topic,
            "search_depth": search_depth,
            "include_answer": include_answer,
            "time_range": time_range,
            "max_results": 10,
        }
