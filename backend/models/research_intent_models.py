"""
Research Intent Models

Pydantic models for understanding user research intent.
These models capture what the user actually wants to accomplish from their research,
enabling targeted query generation and intent-aware result analysis.

Author: ALwrity Team
Version: 1.0
"""

from enum import Enum
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field
from datetime import datetime


class ResearchPurpose(str, Enum):
    """Why is the user researching?"""
    LEARN = "learn"  # Understand a topic for personal knowledge
    CREATE_CONTENT = "create_content"  # Write article/blog/podcast/video
    MAKE_DECISION = "make_decision"  # Choose between options
    COMPARE = "compare"  # Compare alternatives/competitors
    SOLVE_PROBLEM = "solve_problem"  # Find solution to a problem
    FIND_DATA = "find_data"  # Get statistics/facts/citations
    EXPLORE_TRENDS = "explore_trends"  # Understand market/industry trends
    VALIDATE = "validate"  # Verify claims/information
    GENERATE_IDEAS = "generate_ideas"  # Brainstorm content ideas


class ContentOutput(str, Enum):
    """What content type will be created from this research?"""
    BLOG = "blog"
    PODCAST = "podcast"
    VIDEO = "video"
    SOCIAL_POST = "social_post"
    NEWSLETTER = "newsletter"
    PRESENTATION = "presentation"
    REPORT = "report"
    WHITEPAPER = "whitepaper"
    EMAIL = "email"
    GENERAL = "general"  # No specific output


class ExpectedDeliverable(str, Enum):
    """What specific outputs the user expects from research."""
    KEY_STATISTICS = "key_statistics"  # Numbers, data points, percentages
    EXPERT_QUOTES = "expert_quotes"  # Authoritative statements
    CASE_STUDIES = "case_studies"  # Real examples and success stories
    COMPARISONS = "comparisons"  # Side-by-side analysis
    TRENDS = "trends"  # Market/industry trends
    BEST_PRACTICES = "best_practices"  # Recommendations and guidelines
    STEP_BY_STEP = "step_by_step"  # Process/how-to instructions
    PROS_CONS = "pros_cons"  # Advantages/disadvantages
    DEFINITIONS = "definitions"  # Clear explanations of concepts
    CITATIONS = "citations"  # Authoritative sources
    EXAMPLES = "examples"  # Concrete examples
    PREDICTIONS = "predictions"  # Future outlook


class ResearchDepthLevel(str, Enum):
    """How deep the research should go."""
    OVERVIEW = "overview"  # Quick summary, surface level
    DETAILED = "detailed"  # In-depth analysis
    EXPERT = "expert"  # Comprehensive, expert-level research


class InputType(str, Enum):
    """Type of user input detected."""
    KEYWORDS = "keywords"  # Simple keywords: "AI healthcare 2025"
    QUESTION = "question"  # A question: "What are the best AI tools?"
    GOAL = "goal"  # Goal statement: "I need to write a blog about..."
    MIXED = "mixed"  # Combination of above


# ============================================================================
# Structured Deliverable Models
# ============================================================================

class StatisticWithCitation(BaseModel):
    """A statistic with full attribution."""
    statistic: str = Field(..., description="The full statistical statement")
    value: Optional[str] = Field(None, description="The numeric value (e.g., '72%')")
    context: str = Field(..., description="Context of when/where this was measured")
    source: str = Field(..., description="Source name/publication")
    url: str = Field(..., description="Source URL")
    credibility: float = Field(0.8, ge=0.0, le=1.0, description="Credibility score 0-1")
    recency: Optional[str] = Field(None, description="How recent the data is")


class ExpertQuote(BaseModel):
    """A quote from an authoritative source."""
    quote: str = Field(..., description="The actual quote")
    speaker: str = Field(..., description="Name of the speaker")
    title: Optional[str] = Field(None, description="Title/role of the speaker")
    organization: Optional[str] = Field(None, description="Organization/company")
    context: Optional[str] = Field(None, description="Context of the quote")
    source: str = Field(..., description="Source name")
    url: str = Field(..., description="Source URL")


class CaseStudySummary(BaseModel):
    """Summary of a case study."""
    title: str = Field(..., description="Case study title")
    organization: str = Field(..., description="Organization featured")
    challenge: str = Field(..., description="The challenge/problem faced")
    solution: str = Field(..., description="The solution implemented")
    outcome: str = Field(..., description="The results achieved")
    key_metrics: List[str] = Field(default_factory=list, description="Key metrics/numbers")
    source: str = Field(..., description="Source name")
    url: str = Field(..., description="Source URL")


class TrendAnalysis(BaseModel):
    """Analysis of a trend."""
    trend: str = Field(..., description="The trend description")
    direction: str = Field(..., description="growing, declining, emerging, stable")
    evidence: List[str] = Field(default_factory=list, description="Supporting evidence")
    impact: Optional[str] = Field(None, description="Potential impact")
    timeline: Optional[str] = Field(None, description="Timeline of the trend")
    sources: List[str] = Field(default_factory=list, description="Source URLs")


class ComparisonItem(BaseModel):
    """An item in a comparison."""
    name: str
    description: Optional[str] = None
    pros: List[str] = Field(default_factory=list)
    cons: List[str] = Field(default_factory=list)
    features: Dict[str, str] = Field(default_factory=dict)
    rating: Optional[float] = None
    source: Optional[str] = None


class ComparisonTable(BaseModel):
    """Comparison between options."""
    title: str = Field(..., description="Comparison title")
    criteria: List[str] = Field(default_factory=list, description="Comparison criteria")
    items: List[ComparisonItem] = Field(default_factory=list, description="Items being compared")
    winner: Optional[str] = Field(None, description="Recommended option if applicable")
    verdict: Optional[str] = Field(None, description="Summary verdict")


class ProsCons(BaseModel):
    """Pros and cons analysis."""
    subject: str = Field(..., description="What is being analyzed")
    pros: List[str] = Field(default_factory=list, description="Advantages")
    cons: List[str] = Field(default_factory=list, description="Disadvantages")
    balanced_verdict: str = Field(..., description="Balanced conclusion")


class SourceWithRelevance(BaseModel):
    """A source with relevance information."""
    title: str
    url: str
    excerpt: Optional[str] = None
    relevance_score: float = Field(0.8, ge=0.0, le=1.0)
    relevance_reason: Optional[str] = None
    content_type: Optional[str] = None  # article, research paper, news, etc.
    published_date: Optional[str] = None
    credibility_score: float = Field(0.8, ge=0.0, le=1.0)


# ============================================================================
# Intent Models
# ============================================================================

class ResearchIntent(BaseModel):
    """
    What the user actually wants from their research.
    This is inferred from user input + research persona.
    """
    
    # Core understanding
    primary_question: str = Field(..., description="The main question to answer")
    secondary_questions: List[str] = Field(
        default_factory=list, 
        description="Related questions that should be answered"
    )
    
    # Purpose classification
    purpose: ResearchPurpose = Field(
        ResearchPurpose.LEARN,
        description="Why the user is researching"
    )
    content_output: ContentOutput = Field(
        ContentOutput.GENERAL,
        description="What content type will be created"
    )
    
    # What they need from results
    expected_deliverables: List[ExpectedDeliverable] = Field(
        default_factory=list,
        description="Specific outputs the user expects"
    )
    
    # Depth and focus
    depth: ResearchDepthLevel = Field(
        ResearchDepthLevel.DETAILED,
        description="How deep the research should go"
    )
    focus_areas: List[str] = Field(
        default_factory=list,
        description="Specific aspects to focus on"
    )
    
    # Constraints
    perspective: Optional[str] = Field(
        None, 
        description="Perspective to research from (e.g., 'hospital administrator')"
    )
    time_sensitivity: Optional[str] = Field(
        None,
        description="Time constraint: 'real_time', 'recent', 'historical', 'evergreen'"
    )
    
    # Detected input type
    input_type: InputType = Field(
        InputType.KEYWORDS,
        description="Type of user input detected"
    )
    
    # Original user input (for reference)
    original_input: str = Field(..., description="The original user input")
    
    # Confidence in inference
    confidence: float = Field(
        0.8, 
        ge=0.0, 
        le=1.0,
        description="Confidence in the intent inference"
    )
    confidence_reason: Optional[str] = Field(
        None,
        description="Reason for the confidence level"
    )
    great_example: Optional[str] = Field(
        None,
        description="Example of what a great input would look like (if confidence is low)"
    )
    needs_clarification: bool = Field(
        False,
        description="True if AI is uncertain and needs user clarification"
    )
    clarifying_questions: List[str] = Field(
        default_factory=list,
        description="Questions to ask user if uncertain"
    )
    
    class Config:
        use_enum_values = True


class ResearchQuery(BaseModel):
    """A targeted research query with purpose."""
    query: str = Field(..., description="The search query")
    purpose: ExpectedDeliverable = Field(..., description="What this query targets")
    provider: str = Field("exa", description="Preferred provider: exa, tavily, google")
    priority: int = Field(1, ge=1, le=5, description="Priority 1-5, higher = more important")
    expected_results: str = Field(..., description="What we expect to find with this query")


class IntentInferenceRequest(BaseModel):
    """Request to infer research intent from user input."""
    user_input: str = Field(..., description="User's keywords, question, or goal")
    keywords: List[str] = Field(default_factory=list, description="Extracted keywords")
    use_persona: bool = Field(True, description="Use research persona for context")
    use_competitor_data: bool = Field(True, description="Use competitor data for context")


class IntentInferenceResponse(BaseModel):
    """Response from intent inference."""
    success: bool = True
    intent: ResearchIntent
    analysis_summary: str = Field(..., description="AI's understanding of user intent")
    suggested_queries: List[ResearchQuery] = Field(
        default_factory=list,
        description="Generated research queries based on intent"
    )
    suggested_keywords: List[str] = Field(
        default_factory=list,
        description="Enhanced/expanded keywords"
    )
    suggested_angles: List[str] = Field(
        default_factory=list,
        description="Research angles to explore"
    )
    quick_options: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Quick options for user to confirm/modify intent"
    )
    confidence_reason: Optional[str] = Field(None, description="Reason for confidence level")
    great_example: Optional[str] = Field(None, description="Example of great input (if confidence is low)")


# ============================================================================
# Intent-Driven Research Result
# ============================================================================

class IntentDrivenResearchResult(BaseModel):
    """
    Research results organized by what user needs.
    This is the final output after intent-aware analysis.
    """
    
    success: bool = True
    
    # Direct answers
    primary_answer: str = Field(..., description="Direct answer to primary question")
    secondary_answers: Dict[str, str] = Field(
        default_factory=dict,
        description="Answers to secondary questions (question → answer)"
    )
    
    # Deliverables (populated based on user's expected_deliverables)
    statistics: List[StatisticWithCitation] = Field(default_factory=list)
    expert_quotes: List[ExpertQuote] = Field(default_factory=list)
    case_studies: List[CaseStudySummary] = Field(default_factory=list)
    comparisons: List[ComparisonTable] = Field(default_factory=list)
    trends: List[TrendAnalysis] = Field(default_factory=list)
    best_practices: List[str] = Field(default_factory=list)
    step_by_step: List[str] = Field(default_factory=list)
    pros_cons: Optional[ProsCons] = None
    definitions: Dict[str, str] = Field(
        default_factory=dict,
        description="Term → definition mappings"
    )
    examples: List[str] = Field(default_factory=list)
    predictions: List[str] = Field(default_factory=list)
    
    # Content-ready outputs
    executive_summary: str = Field("", description="2-3 sentence summary")
    key_takeaways: List[str] = Field(
        default_factory=list,
        description="5-7 key bullet points"
    )
    suggested_outline: List[str] = Field(
        default_factory=list,
        description="Suggested content outline if creating content"
    )
    
    # Supporting data
    sources: List[SourceWithRelevance] = Field(default_factory=list)
    raw_content: Optional[str] = Field(None, description="Raw content for further processing")
    
    # Research quality metadata
    confidence: float = Field(0.8, ge=0.0, le=1.0)
    gaps_identified: List[str] = Field(
        default_factory=list,
        description="What we couldn't find"
    )
    follow_up_queries: List[str] = Field(
        default_factory=list,
        description="Suggested additional research"
    )
    
    # Original intent for reference
    original_intent: Optional[ResearchIntent] = None
    
    # Error handling
    error_message: Optional[str] = None
    
    class Config:
        use_enum_values = True

