"""
Research Intent Inference Service

Analyzes user input to understand their research intent.
Uses AI to infer:
- What the user wants to accomplish
- What questions need answering
- What deliverables they expect

Author: ALwrity Team
Version: 1.0
"""

import json
from typing import Dict, Any, List, Optional
from loguru import logger

from models.research_intent_models import (
    ResearchIntent,
    ResearchPurpose,
    ContentOutput,
    ExpectedDeliverable,
    ResearchDepthLevel,
    InputType,
    IntentInferenceRequest,
    IntentInferenceResponse,
    ResearchQuery,
)
from models.research_persona_models import ResearchPersona
from .intent_prompt_builder import IntentPromptBuilder


class ResearchIntentInference:
    """
    Infers user research intent from minimal input.
    
    Instead of asking a formal questionnaire, this service
    uses AI to understand what the user really wants.
    """
    
    def __init__(self):
        """Initialize the intent inference service."""
        self.prompt_builder = IntentPromptBuilder()
        logger.info("ResearchIntentInference initialized")
    
    async def infer_intent(
        self,
        user_input: str,
        keywords: Optional[List[str]] = None,
        research_persona: Optional[ResearchPersona] = None,
        competitor_data: Optional[List[Dict]] = None,
        industry: Optional[str] = None,
        target_audience: Optional[str] = None,
    ) -> IntentInferenceResponse:
        """
        Analyze user input and infer their research intent.
        
        Args:
            user_input: User's keywords, question, or goal
            keywords: Extracted keywords (optional)
            research_persona: User's research persona (optional)
            competitor_data: Competitor analysis data (optional)
            industry: Industry context (optional)
            target_audience: Target audience context (optional)
            
        Returns:
            IntentInferenceResponse with inferred intent and suggested queries
        """
        try:
            logger.info(f"Inferring intent for: {user_input[:100]}...")
            
            keywords = keywords or []
            
            # Build the inference prompt
            prompt = self.prompt_builder.build_intent_inference_prompt(
                user_input=user_input,
                keywords=keywords,
                research_persona=research_persona,
                competitor_data=competitor_data,
                industry=industry,
                target_audience=target_audience,
            )
            
            # Define the expected JSON schema
            intent_schema = {
                "type": "object",
                "properties": {
                    "input_type": {"type": "string", "enum": ["keywords", "question", "goal", "mixed"]},
                    "primary_question": {"type": "string"},
                    "secondary_questions": {"type": "array", "items": {"type": "string"}},
                    "purpose": {"type": "string"},
                    "content_output": {"type": "string"},
                    "expected_deliverables": {"type": "array", "items": {"type": "string"}},
                    "depth": {"type": "string", "enum": ["overview", "detailed", "expert"]},
                    "focus_areas": {"type": "array", "items": {"type": "string"}},
                    "perspective": {"type": "string"},
                    "time_sensitivity": {"type": "string"},
                    "confidence": {"type": "number"},
                    "needs_clarification": {"type": "boolean"},
                    "clarifying_questions": {"type": "array", "items": {"type": "string"}},
                    "analysis_summary": {"type": "string"}
                },
                "required": [
                    "input_type", "primary_question", "purpose", "content_output",
                    "expected_deliverables", "depth", "confidence", "analysis_summary"
                ]
            }
            
            # Call LLM for intent inference
            from services.llm_providers.main_text_generation import llm_text_gen
            
            result = llm_text_gen(
                prompt=prompt,
                json_struct=intent_schema,
                user_id=None
            )
            
            if isinstance(result, dict) and "error" in result:
                logger.error(f"Intent inference failed: {result.get('error')}")
                return self._create_fallback_response(user_input, keywords)
            
            # Parse and validate the result
            intent = self._parse_intent_result(result, user_input)
            
            # Generate quick options for UI
            quick_options = self._generate_quick_options(intent, result)
            
            # Create response
            response = IntentInferenceResponse(
                success=True,
                intent=intent,
                analysis_summary=result.get("analysis_summary", "Research intent analyzed"),
                suggested_queries=[],  # Will be populated by query generator
                suggested_keywords=self._extract_keywords_from_input(user_input, keywords),
                suggested_angles=result.get("focus_areas", []),
                quick_options=quick_options,
            )
            
            logger.info(f"Intent inferred: purpose={intent.purpose}, confidence={intent.confidence}")
            return response
            
        except Exception as e:
            logger.error(f"Error inferring intent: {e}")
            return self._create_fallback_response(user_input, keywords or [])
    
    def _parse_intent_result(self, result: Dict[str, Any], user_input: str) -> ResearchIntent:
        """Parse LLM result into ResearchIntent model."""
        
        # Map string values to enums safely
        input_type = self._safe_enum(InputType, result.get("input_type", "keywords"), InputType.KEYWORDS)
        purpose = self._safe_enum(ResearchPurpose, result.get("purpose", "learn"), ResearchPurpose.LEARN)
        content_output = self._safe_enum(ContentOutput, result.get("content_output", "general"), ContentOutput.GENERAL)
        depth = self._safe_enum(ResearchDepthLevel, result.get("depth", "detailed"), ResearchDepthLevel.DETAILED)
        
        # Parse expected deliverables
        raw_deliverables = result.get("expected_deliverables", [])
        expected_deliverables = []
        for d in raw_deliverables:
            try:
                expected_deliverables.append(ExpectedDeliverable(d).value)
            except ValueError:
                # Skip invalid deliverables
                pass
        
        # Ensure we have at least some deliverables
        if not expected_deliverables:
            expected_deliverables = self._infer_deliverables_from_purpose(purpose)
        
        return ResearchIntent(
            primary_question=result.get("primary_question", user_input),
            secondary_questions=result.get("secondary_questions", []),
            purpose=purpose.value,
            content_output=content_output.value,
            expected_deliverables=expected_deliverables,
            depth=depth.value,
            focus_areas=result.get("focus_areas", []),
            perspective=result.get("perspective"),
            time_sensitivity=result.get("time_sensitivity"),
            input_type=input_type.value,
            original_input=user_input,
            confidence=float(result.get("confidence", 0.7)),
            needs_clarification=result.get("needs_clarification", False),
            clarifying_questions=result.get("clarifying_questions", []),
        )
    
    def _safe_enum(self, enum_class, value: str, default):
        """Safely convert string to enum, returning default if invalid."""
        try:
            return enum_class(value)
        except ValueError:
            return default
    
    def _infer_deliverables_from_purpose(self, purpose: ResearchPurpose) -> List[str]:
        """Infer expected deliverables based on research purpose."""
        
        purpose_deliverables = {
            ResearchPurpose.LEARN: [
                ExpectedDeliverable.DEFINITIONS.value,
                ExpectedDeliverable.EXAMPLES.value,
                ExpectedDeliverable.KEY_STATISTICS.value,
            ],
            ResearchPurpose.CREATE_CONTENT: [
                ExpectedDeliverable.KEY_STATISTICS.value,
                ExpectedDeliverable.EXPERT_QUOTES.value,
                ExpectedDeliverable.EXAMPLES.value,
                ExpectedDeliverable.CASE_STUDIES.value,
            ],
            ResearchPurpose.MAKE_DECISION: [
                ExpectedDeliverable.PROS_CONS.value,
                ExpectedDeliverable.COMPARISONS.value,
                ExpectedDeliverable.BEST_PRACTICES.value,
            ],
            ResearchPurpose.COMPARE: [
                ExpectedDeliverable.COMPARISONS.value,
                ExpectedDeliverable.PROS_CONS.value,
                ExpectedDeliverable.KEY_STATISTICS.value,
            ],
            ResearchPurpose.SOLVE_PROBLEM: [
                ExpectedDeliverable.STEP_BY_STEP.value,
                ExpectedDeliverable.BEST_PRACTICES.value,
                ExpectedDeliverable.CASE_STUDIES.value,
            ],
            ResearchPurpose.FIND_DATA: [
                ExpectedDeliverable.KEY_STATISTICS.value,
                ExpectedDeliverable.CITATIONS.value,
            ],
            ResearchPurpose.EXPLORE_TRENDS: [
                ExpectedDeliverable.TRENDS.value,
                ExpectedDeliverable.PREDICTIONS.value,
                ExpectedDeliverable.KEY_STATISTICS.value,
            ],
            ResearchPurpose.VALIDATE: [
                ExpectedDeliverable.CITATIONS.value,
                ExpectedDeliverable.KEY_STATISTICS.value,
                ExpectedDeliverable.EXPERT_QUOTES.value,
            ],
            ResearchPurpose.GENERATE_IDEAS: [
                ExpectedDeliverable.EXAMPLES.value,
                ExpectedDeliverable.TRENDS.value,
                ExpectedDeliverable.CASE_STUDIES.value,
            ],
        }
        
        return purpose_deliverables.get(purpose, [ExpectedDeliverable.KEY_STATISTICS.value])
    
    def _generate_quick_options(self, intent: ResearchIntent, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate quick options for UI confirmation."""
        
        options = []
        
        # Purpose option
        options.append({
            "id": "purpose",
            "label": "Research Purpose",
            "value": intent.purpose,
            "display": self._purpose_display(intent.purpose),
            "alternatives": [p.value for p in ResearchPurpose],
            "confidence": result.get("confidence", 0.7),
        })
        
        # Content output option
        if intent.content_output != ContentOutput.GENERAL.value:
            options.append({
                "id": "content_output",
                "label": "Content Type",
                "value": intent.content_output,
                "display": intent.content_output.replace("_", " ").title(),
                "alternatives": [c.value for c in ContentOutput],
                "confidence": result.get("confidence", 0.7),
            })
        
        # Deliverables option
        options.append({
            "id": "deliverables",
            "label": "What I'll Find",
            "value": intent.expected_deliverables,
            "display": [d.replace("_", " ").title() for d in intent.expected_deliverables[:4]],
            "alternatives": [d.value for d in ExpectedDeliverable],
            "confidence": result.get("confidence", 0.7),
            "multi_select": True,
        })
        
        # Depth option
        options.append({
            "id": "depth",
            "label": "Research Depth",
            "value": intent.depth,
            "display": intent.depth.title(),
            "alternatives": [d.value for d in ResearchDepthLevel],
            "confidence": result.get("confidence", 0.7),
        })
        
        return options
    
    def _purpose_display(self, purpose: str) -> str:
        """Get display-friendly purpose text."""
        display_map = {
            "learn": "Understand this topic",
            "create_content": "Create content about this",
            "make_decision": "Make a decision",
            "compare": "Compare options",
            "solve_problem": "Solve a problem",
            "find_data": "Find specific data",
            "explore_trends": "Explore trends",
            "validate": "Validate information",
            "generate_ideas": "Generate ideas",
        }
        return display_map.get(purpose, purpose.replace("_", " ").title())
    
    def _extract_keywords_from_input(self, user_input: str, keywords: List[str]) -> List[str]:
        """Extract and enhance keywords from user input."""
        
        # Start with provided keywords
        extracted = list(keywords) if keywords else []
        
        # Simple extraction from input (split on common delimiters)
        words = user_input.lower().replace(",", " ").replace(";", " ").split()
        
        # Filter out common words
        stop_words = {
            "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
            "have", "has", "had", "do", "does", "did", "will", "would", "could",
            "should", "may", "might", "must", "shall", "can", "need", "dare",
            "to", "of", "in", "for", "on", "with", "at", "by", "from", "up",
            "about", "into", "through", "during", "before", "after", "above",
            "below", "between", "under", "again", "further", "then", "once",
            "here", "there", "when", "where", "why", "how", "all", "each",
            "few", "more", "most", "other", "some", "such", "no", "nor", "not",
            "only", "own", "same", "so", "than", "too", "very", "just", "and",
            "but", "if", "or", "because", "as", "until", "while", "i", "we",
            "you", "they", "what", "which", "who", "whom", "this", "that",
            "these", "those", "am", "want", "write", "blog", "post", "article",
        }
        
        for word in words:
            if word not in stop_words and len(word) > 2 and word not in extracted:
                extracted.append(word)
        
        return extracted[:15]  # Limit to 15 keywords
    
    def _create_fallback_response(self, user_input: str, keywords: List[str]) -> IntentInferenceResponse:
        """Create a fallback response when AI inference fails."""
        
        # Create a basic intent from the input
        fallback_intent = ResearchIntent(
            primary_question=f"What are the key insights about: {user_input}?",
            secondary_questions=[
                f"What are the latest trends in {user_input}?",
                f"What are best practices for {user_input}?",
            ],
            purpose=ResearchPurpose.LEARN.value,
            content_output=ContentOutput.GENERAL.value,
            expected_deliverables=[
                ExpectedDeliverable.KEY_STATISTICS.value,
                ExpectedDeliverable.EXAMPLES.value,
                ExpectedDeliverable.BEST_PRACTICES.value,
            ],
            depth=ResearchDepthLevel.DETAILED.value,
            focus_areas=[],
            input_type=InputType.KEYWORDS.value,
            original_input=user_input,
            confidence=0.5,
            needs_clarification=True,
            clarifying_questions=[
                "What type of content are you creating?",
                "What specific aspects are you most interested in?",
            ],
        )
        
        return IntentInferenceResponse(
            success=True,  # Still return success, just with lower confidence
            intent=fallback_intent,
            analysis_summary=f"Basic research analysis for: {user_input}",
            suggested_queries=[],
            suggested_keywords=keywords,
            suggested_angles=[],
            quick_options=[],
        )
