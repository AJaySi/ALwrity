"""
Intent-Aware Result Analyzer

Analyzes research results based on user intent.
Extracts exactly what the user needs from raw research data.

This is the key innovation - instead of generic analysis,
we analyze results through the lens of what the user wants to accomplish.

Author: ALwrity Team
Version: 1.0
"""

import json
from typing import Dict, Any, List, Optional
from loguru import logger

from models.research_intent_models import (
    ResearchIntent,
    IntentDrivenResearchResult,
    ExpectedDeliverable,
    StatisticWithCitation,
    ExpertQuote,
    CaseStudySummary,
    TrendAnalysis,
    ComparisonTable,
    ComparisonItem,
    ProsCons,
    SourceWithRelevance,
)
from models.research_persona_models import ResearchPersona
from .intent_prompt_builder import IntentPromptBuilder


class IntentAwareAnalyzer:
    """
    Analyzes research results based on user intent.
    
    Instead of generic summaries, this extracts exactly what the user
    needs: statistics, quotes, case studies, trends, etc.
    """
    
    def __init__(self):
        """Initialize the analyzer."""
        self.prompt_builder = IntentPromptBuilder()
        logger.info("IntentAwareAnalyzer initialized")
    
    async def analyze(
        self,
        raw_results: Dict[str, Any],
        intent: ResearchIntent,
        research_persona: Optional[ResearchPersona] = None,
    ) -> IntentDrivenResearchResult:
        """
        Analyze raw research results based on user intent.
        
        Args:
            raw_results: Raw results from Exa/Tavily/Google
            intent: The user's research intent
            research_persona: Optional persona for context
            
        Returns:
            IntentDrivenResearchResult with extracted deliverables
        """
        try:
            logger.info(f"Analyzing results for intent: {intent.primary_question[:50]}...")
            
            # Format raw results for analysis
            formatted_results = self._format_raw_results(raw_results)
            
            # Build the analysis prompt
            prompt = self.prompt_builder.build_intent_aware_analysis_prompt(
                raw_results=formatted_results,
                intent=intent,
                research_persona=research_persona,
            )
            
            # Define the expected JSON schema
            analysis_schema = self._build_analysis_schema(intent.expected_deliverables)
            
            # Call LLM for analysis
            from services.llm_providers.main_text_generation import llm_text_gen
            
            result = llm_text_gen(
                prompt=prompt,
                json_struct=analysis_schema,
                user_id=None
            )
            
            if isinstance(result, dict) and "error" in result:
                logger.error(f"Intent-aware analysis failed: {result.get('error')}")
                return self._create_fallback_result(raw_results, intent)
            
            # Parse and validate the result
            analyzed_result = self._parse_analysis_result(result, intent, raw_results)
            
            logger.info(
                f"Analysis complete: {len(analyzed_result.key_takeaways)} takeaways, "
                f"{len(analyzed_result.statistics)} stats, "
                f"{len(analyzed_result.sources)} sources"
            )
            
            return analyzed_result
            
        except Exception as e:
            logger.error(f"Error in intent-aware analysis: {e}")
            return self._create_fallback_result(raw_results, intent)
    
    def _format_raw_results(self, raw_results: Dict[str, Any]) -> str:
        """Format raw research results for LLM analysis."""
        
        formatted_parts = []
        
        # Extract content
        content = raw_results.get("content", "")
        if content:
            formatted_parts.append(f"=== MAIN CONTENT ===\n{content[:8000]}")
        
        # Extract sources with their content
        sources = raw_results.get("sources", [])
        if sources:
            formatted_parts.append("\n=== SOURCES ===")
            for i, source in enumerate(sources[:15], 1):  # Limit to 15 sources
                title = source.get("title", "Untitled")
                url = source.get("url", "")
                excerpt = source.get("excerpt", source.get("text", source.get("content", "")))
                
                formatted_parts.append(f"\nSource {i}: {title}")
                formatted_parts.append(f"URL: {url}")
                if excerpt:
                    formatted_parts.append(f"Content: {excerpt[:500]}")
        
        # Extract grounding metadata if available (from Google)
        grounding = raw_results.get("grounding_metadata", {})
        if grounding:
            formatted_parts.append("\n=== GROUNDING DATA ===")
            formatted_parts.append(json.dumps(grounding, indent=2)[:2000])
        
        # Extract any AI answers (from Tavily)
        answer = raw_results.get("answer", "")
        if answer:
            formatted_parts.append(f"\n=== AI-GENERATED ANSWER ===\n{answer}")
        
        return "\n".join(formatted_parts)
    
    def _build_analysis_schema(self, expected_deliverables: List[str]) -> Dict[str, Any]:
        """Build JSON schema based on expected deliverables."""
        
        # Base schema
        schema = {
            "type": "object",
            "properties": {
                "primary_answer": {"type": "string"},
                "secondary_answers": {
                    "type": "object",
                    "additionalProperties": {"type": "string"}
                },
                "executive_summary": {"type": "string"},
                "key_takeaways": {
                    "type": "array",
                    "items": {"type": "string"},
                    "maxItems": 7
                },
                "confidence": {"type": "number"},
                "gaps_identified": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "follow_up_queries": {
                    "type": "array",
                    "items": {"type": "string"}
                },
            },
            "required": ["primary_answer", "executive_summary", "key_takeaways", "confidence"]
        }
        
        # Add deliverable-specific properties
        if ExpectedDeliverable.KEY_STATISTICS.value in expected_deliverables:
            schema["properties"]["statistics"] = {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "statistic": {"type": "string"},
                        "value": {"type": "string"},
                        "context": {"type": "string"},
                        "source": {"type": "string"},
                        "url": {"type": "string"},
                        "credibility": {"type": "number"},
                        "recency": {"type": "string"}
                    },
                    "required": ["statistic", "context", "source", "url"]
                }
            }
        
        if ExpectedDeliverable.EXPERT_QUOTES.value in expected_deliverables:
            schema["properties"]["expert_quotes"] = {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "quote": {"type": "string"},
                        "speaker": {"type": "string"},
                        "title": {"type": "string"},
                        "organization": {"type": "string"},
                        "source": {"type": "string"},
                        "url": {"type": "string"}
                    },
                    "required": ["quote", "speaker", "source", "url"]
                }
            }
        
        if ExpectedDeliverable.CASE_STUDIES.value in expected_deliverables:
            schema["properties"]["case_studies"] = {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "organization": {"type": "string"},
                        "challenge": {"type": "string"},
                        "solution": {"type": "string"},
                        "outcome": {"type": "string"},
                        "key_metrics": {"type": "array", "items": {"type": "string"}},
                        "source": {"type": "string"},
                        "url": {"type": "string"}
                    },
                    "required": ["title", "organization", "challenge", "solution", "outcome"]
                }
            }
        
        if ExpectedDeliverable.TRENDS.value in expected_deliverables:
            schema["properties"]["trends"] = {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "trend": {"type": "string"},
                        "direction": {"type": "string"},
                        "evidence": {"type": "array", "items": {"type": "string"}},
                        "impact": {"type": "string"},
                        "timeline": {"type": "string"},
                        "sources": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["trend", "direction", "evidence"]
                }
            }
        
        if ExpectedDeliverable.COMPARISONS.value in expected_deliverables:
            schema["properties"]["comparisons"] = {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "criteria": {"type": "array", "items": {"type": "string"}},
                        "items": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "pros": {"type": "array", "items": {"type": "string"}},
                                    "cons": {"type": "array", "items": {"type": "string"}},
                                    "features": {"type": "object"}
                                }
                            }
                        },
                        "verdict": {"type": "string"}
                    }
                }
            }
        
        if ExpectedDeliverable.PROS_CONS.value in expected_deliverables:
            schema["properties"]["pros_cons"] = {
                "type": "object",
                "properties": {
                    "subject": {"type": "string"},
                    "pros": {"type": "array", "items": {"type": "string"}},
                    "cons": {"type": "array", "items": {"type": "string"}},
                    "balanced_verdict": {"type": "string"}
                }
            }
        
        if ExpectedDeliverable.BEST_PRACTICES.value in expected_deliverables:
            schema["properties"]["best_practices"] = {
                "type": "array",
                "items": {"type": "string"}
            }
        
        if ExpectedDeliverable.STEP_BY_STEP.value in expected_deliverables:
            schema["properties"]["step_by_step"] = {
                "type": "array",
                "items": {"type": "string"}
            }
        
        if ExpectedDeliverable.DEFINITIONS.value in expected_deliverables:
            schema["properties"]["definitions"] = {
                "type": "object",
                "additionalProperties": {"type": "string"}
            }
        
        if ExpectedDeliverable.EXAMPLES.value in expected_deliverables:
            schema["properties"]["examples"] = {
                "type": "array",
                "items": {"type": "string"}
            }
        
        if ExpectedDeliverable.PREDICTIONS.value in expected_deliverables:
            schema["properties"]["predictions"] = {
                "type": "array",
                "items": {"type": "string"}
            }
        
        # Always include sources and suggested outline
        schema["properties"]["sources"] = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "url": {"type": "string"},
                    "relevance_score": {"type": "number"},
                    "relevance_reason": {"type": "string"},
                    "content_type": {"type": "string"},
                    "credibility_score": {"type": "number"}
                },
                "required": ["title", "url"]
            }
        }
        
        schema["properties"]["suggested_outline"] = {
            "type": "array",
            "items": {"type": "string"}
        }
        
        return schema
    
    def _parse_analysis_result(
        self,
        result: Dict[str, Any],
        intent: ResearchIntent,
        raw_results: Dict[str, Any],
    ) -> IntentDrivenResearchResult:
        """Parse LLM analysis result into structured format."""
        
        # Parse statistics
        statistics = []
        for stat in result.get("statistics", []):
            try:
                statistics.append(StatisticWithCitation(
                    statistic=stat.get("statistic", ""),
                    value=stat.get("value"),
                    context=stat.get("context", ""),
                    source=stat.get("source", ""),
                    url=stat.get("url", ""),
                    credibility=float(stat.get("credibility", 0.8)),
                    recency=stat.get("recency"),
                ))
            except Exception as e:
                logger.warning(f"Failed to parse statistic: {e}")
        
        # Parse expert quotes
        expert_quotes = []
        for quote in result.get("expert_quotes", []):
            try:
                expert_quotes.append(ExpertQuote(
                    quote=quote.get("quote", ""),
                    speaker=quote.get("speaker", ""),
                    title=quote.get("title"),
                    organization=quote.get("organization"),
                    context=quote.get("context"),
                    source=quote.get("source", ""),
                    url=quote.get("url", ""),
                ))
            except Exception as e:
                logger.warning(f"Failed to parse expert quote: {e}")
        
        # Parse case studies
        case_studies = []
        for cs in result.get("case_studies", []):
            try:
                case_studies.append(CaseStudySummary(
                    title=cs.get("title", ""),
                    organization=cs.get("organization", ""),
                    challenge=cs.get("challenge", ""),
                    solution=cs.get("solution", ""),
                    outcome=cs.get("outcome", ""),
                    key_metrics=cs.get("key_metrics", []),
                    source=cs.get("source", ""),
                    url=cs.get("url", ""),
                ))
            except Exception as e:
                logger.warning(f"Failed to parse case study: {e}")
        
        # Parse trends
        trends = []
        for trend in result.get("trends", []):
            try:
                trends.append(TrendAnalysis(
                    trend=trend.get("trend", ""),
                    direction=trend.get("direction", "growing"),
                    evidence=trend.get("evidence", []),
                    impact=trend.get("impact"),
                    timeline=trend.get("timeline"),
                    sources=trend.get("sources", []),
                ))
            except Exception as e:
                logger.warning(f"Failed to parse trend: {e}")
        
        # Parse comparisons
        comparisons = []
        for comp in result.get("comparisons", []):
            try:
                items = []
                for item in comp.get("items", []):
                    items.append(ComparisonItem(
                        name=item.get("name", ""),
                        description=item.get("description"),
                        pros=item.get("pros", []),
                        cons=item.get("cons", []),
                        features=item.get("features", {}),
                        rating=item.get("rating"),
                        source=item.get("source"),
                    ))
                comparisons.append(ComparisonTable(
                    title=comp.get("title", ""),
                    criteria=comp.get("criteria", []),
                    items=items,
                    winner=comp.get("winner"),
                    verdict=comp.get("verdict"),
                ))
            except Exception as e:
                logger.warning(f"Failed to parse comparison: {e}")
        
        # Parse pros/cons
        pros_cons = None
        pc_data = result.get("pros_cons")
        if pc_data:
            try:
                pros_cons = ProsCons(
                    subject=pc_data.get("subject", intent.original_input),
                    pros=pc_data.get("pros", []),
                    cons=pc_data.get("cons", []),
                    balanced_verdict=pc_data.get("balanced_verdict", ""),
                )
            except Exception as e:
                logger.warning(f"Failed to parse pros/cons: {e}")
        
        # Parse sources
        sources = []
        for src in result.get("sources", []):
            try:
                sources.append(SourceWithRelevance(
                    title=src.get("title", ""),
                    url=src.get("url", ""),
                    excerpt=src.get("excerpt"),
                    relevance_score=float(src.get("relevance_score", 0.8)),
                    relevance_reason=src.get("relevance_reason"),
                    content_type=src.get("content_type"),
                    published_date=src.get("published_date"),
                    credibility_score=float(src.get("credibility_score", 0.8)),
                ))
            except Exception as e:
                logger.warning(f"Failed to parse source: {e}")
        
        # If no sources from analysis, extract from raw results
        if not sources:
            sources = self._extract_sources_from_raw(raw_results)
        
        return IntentDrivenResearchResult(
            success=True,
            primary_answer=result.get("primary_answer", ""),
            secondary_answers=result.get("secondary_answers", {}),
            statistics=statistics,
            expert_quotes=expert_quotes,
            case_studies=case_studies,
            comparisons=comparisons,
            trends=trends,
            best_practices=result.get("best_practices", []),
            step_by_step=result.get("step_by_step", []),
            pros_cons=pros_cons,
            definitions=result.get("definitions", {}),
            examples=result.get("examples", []),
            predictions=result.get("predictions", []),
            executive_summary=result.get("executive_summary", ""),
            key_takeaways=result.get("key_takeaways", []),
            suggested_outline=result.get("suggested_outline", []),
            sources=sources,
            raw_content=self._format_raw_results(raw_results)[:5000],
            confidence=float(result.get("confidence", 0.7)),
            gaps_identified=result.get("gaps_identified", []),
            follow_up_queries=result.get("follow_up_queries", []),
            original_intent=intent,
        )
    
    def _extract_sources_from_raw(self, raw_results: Dict[str, Any]) -> List[SourceWithRelevance]:
        """Extract sources from raw results when analysis doesn't provide them."""
        
        sources = []
        for src in raw_results.get("sources", [])[:10]:
            try:
                sources.append(SourceWithRelevance(
                    title=src.get("title", "Untitled"),
                    url=src.get("url", ""),
                    excerpt=src.get("excerpt", src.get("text", ""))[:200],
                    relevance_score=0.8,
                    credibility_score=float(src.get("credibility_score", 0.8)),
                ))
            except Exception as e:
                logger.warning(f"Failed to extract source: {e}")
        
        return sources
    
    def _create_fallback_result(
        self,
        raw_results: Dict[str, Any],
        intent: ResearchIntent,
    ) -> IntentDrivenResearchResult:
        """Create a fallback result when AI analysis fails."""
        
        # Extract basic information from raw results
        content = raw_results.get("content", "")
        sources = self._extract_sources_from_raw(raw_results)
        
        # Create basic takeaways from content
        key_takeaways = []
        if content:
            sentences = content.split(". ")[:5]
            key_takeaways = [s.strip() + "." for s in sentences if len(s) > 20]
        
        return IntentDrivenResearchResult(
            success=True,
            primary_answer=f"Research findings for: {intent.primary_question}",
            secondary_answers={},
            executive_summary=content[:300] if content else "Research completed",
            key_takeaways=key_takeaways,
            sources=sources,
            raw_content=self._format_raw_results(raw_results)[:5000],
            confidence=0.5,
            gaps_identified=[
                "AI analysis failed - showing raw results",
                "Manual review recommended"
            ],
            follow_up_queries=[],
            original_intent=intent,
        )
