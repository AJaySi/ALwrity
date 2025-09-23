"""
Pydantic models for hallucination detection API endpoints.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class AssessmentType(str, Enum):
    """Assessment types for claim verification."""
    SUPPORTED = "supported"
    REFUTED = "refuted"
    INSUFFICIENT_INFORMATION = "insufficient_information"

class SourceDocument(BaseModel):
    """Represents a source document used for fact-checking."""
    title: str = Field(..., description="Title of the source document")
    url: str = Field(..., description="URL of the source document")
    text: str = Field(..., description="Relevant text content from the source")
    published_date: Optional[str] = Field(None, description="Publication date of the source")
    author: Optional[str] = Field(None, description="Author of the source")
    score: float = Field(0.5, description="Relevance score of the source (0.0-1.0)")

class Claim(BaseModel):
    """Represents a single verifiable claim extracted from text."""
    text: str = Field(..., description="The claim text")
    confidence: float = Field(..., description="Confidence score for the claim assessment (0.0-1.0)")
    assessment: AssessmentType = Field(..., description="Assessment result for the claim")
    supporting_sources: List[SourceDocument] = Field(default_factory=list, description="Sources that support the claim")
    refuting_sources: List[SourceDocument] = Field(default_factory=list, description="Sources that refute the claim")
    reasoning: Optional[str] = Field(None, description="Explanation for the assessment")

class HallucinationDetectionRequest(BaseModel):
    """Request model for hallucination detection."""
    text: str = Field(..., description="Text to analyze for factual accuracy", min_length=10, max_length=5000)
    include_sources: bool = Field(True, description="Whether to include source documents in the response")
    max_claims: int = Field(10, description="Maximum number of claims to extract and verify", ge=1, le=20)

class HallucinationDetectionResponse(BaseModel):
    """Response model for hallucination detection."""
    success: bool = Field(..., description="Whether the analysis was successful")
    claims: List[Claim] = Field(default_factory=list, description="List of extracted and verified claims")
    overall_confidence: float = Field(..., description="Overall confidence score for the analysis (0.0-1.0)")
    total_claims: int = Field(..., description="Total number of claims extracted")
    supported_claims: int = Field(..., description="Number of claims that are supported by sources")
    refuted_claims: int = Field(..., description="Number of claims that are refuted by sources")
    insufficient_claims: int = Field(..., description="Number of claims with insufficient information")
    timestamp: str = Field(..., description="Timestamp of the analysis")
    processing_time_ms: Optional[int] = Field(None, description="Processing time in milliseconds")
    error: Optional[str] = Field(None, description="Error message if analysis failed")

class ClaimExtractionRequest(BaseModel):
    """Request model for claim extraction only."""
    text: str = Field(..., description="Text to extract claims from", min_length=10, max_length=5000)
    max_claims: int = Field(10, description="Maximum number of claims to extract", ge=1, le=20)

class ClaimExtractionResponse(BaseModel):
    """Response model for claim extraction."""
    success: bool = Field(..., description="Whether the extraction was successful")
    claims: List[str] = Field(default_factory=list, description="List of extracted claim texts")
    total_claims: int = Field(..., description="Total number of claims extracted")
    timestamp: str = Field(..., description="Timestamp of the extraction")
    error: Optional[str] = Field(None, description="Error message if extraction failed")

class ClaimVerificationRequest(BaseModel):
    """Request model for verifying a single claim."""
    claim: str = Field(..., description="Claim to verify", min_length=5, max_length=500)
    include_sources: bool = Field(True, description="Whether to include source documents in the response")

class ClaimVerificationResponse(BaseModel):
    """Response model for claim verification."""
    success: bool = Field(..., description="Whether the verification was successful")
    claim: Claim = Field(..., description="Verified claim with assessment results")
    timestamp: str = Field(..., description="Timestamp of the verification")
    processing_time_ms: Optional[int] = Field(None, description="Processing time in milliseconds")
    error: Optional[str] = Field(None, description="Error message if verification failed")

class HealthCheckResponse(BaseModel):
    """Response model for health check."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Service version")
    exa_api_available: bool = Field(..., description="Whether Exa API is available")
    openai_api_available: bool = Field(..., description="Whether OpenAI API is available")
    timestamp: str = Field(..., description="Timestamp of the health check")
