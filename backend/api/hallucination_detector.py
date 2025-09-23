"""
Hallucination Detector API endpoints.

Provides REST API endpoints for fact-checking and hallucination detection
using Exa.ai integration, similar to the Exa.ai demo implementation.
"""

import time
import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

from models.hallucination_models import (
    HallucinationDetectionRequest,
    HallucinationDetectionResponse,
    ClaimExtractionRequest,
    ClaimExtractionResponse,
    ClaimVerificationRequest,
    ClaimVerificationResponse,
    HealthCheckResponse,
    Claim,
    SourceDocument,
    AssessmentType
)
from services.hallucination_detector import HallucinationDetector

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/hallucination-detector", tags=["Hallucination Detector"])

# Initialize detector service
detector = HallucinationDetector()

@router.post("/detect", response_model=HallucinationDetectionResponse)
async def detect_hallucinations(request: HallucinationDetectionRequest) -> HallucinationDetectionResponse:
    """
    Detect hallucinations in the provided text.
    
    This endpoint implements the complete hallucination detection pipeline:
    1. Extract verifiable claims from the text
    2. Search for evidence using Exa.ai
    3. Verify each claim against the found sources
    
    Args:
        request: HallucinationDetectionRequest with text to analyze
        
    Returns:
        HallucinationDetectionResponse with analysis results
    """
    start_time = time.time()
    
    try:
        logger.info(f"Starting hallucination detection for text of length: {len(request.text)}")
        
        # Perform hallucination detection
        result = await detector.detect_hallucinations(request.text)
        
        # Convert to response format
        claims = []
        for claim in result.claims:
            # Convert sources to SourceDocument objects
            supporting_sources = [
                SourceDocument(
                    title=source.get('title', 'Untitled'),
                    url=source.get('url', ''),
                    text=source.get('text', ''),
                    published_date=source.get('publishedDate'),
                    author=source.get('author'),
                    score=source.get('score', 0.5)
                )
                for source in claim.supporting_sources
            ]
            
            refuting_sources = [
                SourceDocument(
                    title=source.get('title', 'Untitled'),
                    url=source.get('url', ''),
                    text=source.get('text', ''),
                    published_date=source.get('publishedDate'),
                    author=source.get('author'),
                    score=source.get('score', 0.5)
                )
                for source in claim.refuting_sources
            ]
            
            claim_obj = Claim(
                text=claim.text,
                confidence=claim.confidence,
                assessment=AssessmentType(claim.assessment),
                supporting_sources=supporting_sources if request.include_sources else [],
                refuting_sources=refuting_sources if request.include_sources else [],
                reasoning=getattr(claim, 'reasoning', None)
            )
            claims.append(claim_obj)
        
        processing_time = int((time.time() - start_time) * 1000)
        
        response = HallucinationDetectionResponse(
            success=True,
            claims=claims,
            overall_confidence=result.overall_confidence,
            total_claims=result.total_claims,
            supported_claims=result.supported_claims,
            refuted_claims=result.refuted_claims,
            insufficient_claims=result.insufficient_claims,
            timestamp=result.timestamp,
            processing_time_ms=processing_time
        )
        
        logger.info(f"Hallucination detection completed successfully. Processing time: {processing_time}ms")
        return response
        
    except Exception as e:
        logger.error(f"Error in hallucination detection: {str(e)}")
        processing_time = int((time.time() - start_time) * 1000)
        
        # Return proper error response
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e),
                "message": "Hallucination detection failed. Please check API keys and try again.",
                "timestamp": time.strftime('%Y-%m-%dT%H:%M:%S'),
                "processing_time_ms": processing_time
            }
        )

@router.post("/extract-claims", response_model=ClaimExtractionResponse)
async def extract_claims(request: ClaimExtractionRequest) -> ClaimExtractionResponse:
    """
    Extract verifiable claims from the provided text.
    
    This endpoint performs only the claim extraction step of the
    hallucination detection pipeline.
    
    Args:
        request: ClaimExtractionRequest with text to analyze
        
    Returns:
        ClaimExtractionResponse with extracted claims
    """
    try:
        logger.info(f"Extracting claims from text of length: {len(request.text)}")
        
        # Extract claims
        claims = await detector._extract_claims(request.text)
        
        # Limit claims if requested
        if request.max_claims and len(claims) > request.max_claims:
            claims = claims[:request.max_claims]
        
        response = ClaimExtractionResponse(
            success=True,
            claims=claims,
            total_claims=len(claims),
            timestamp=time.strftime('%Y-%m-%dT%H:%M:%S')
        )
        
        logger.info(f"Claim extraction completed. Extracted {len(claims)} claims")
        return response
        
    except Exception as e:
        logger.error(f"Error in claim extraction: {str(e)}")
        
        return ClaimExtractionResponse(
            success=False,
            claims=[],
            total_claims=0,
            timestamp=time.strftime('%Y-%m-%dT%H:%M:%S'),
            error=str(e)
        )

@router.post("/verify-claim", response_model=ClaimVerificationResponse)
async def verify_claim(request: ClaimVerificationRequest) -> ClaimVerificationResponse:
    """
    Verify a single claim against available sources.
    
    This endpoint performs claim verification using Exa.ai search
    and LLM-based assessment.
    
    Args:
        request: ClaimVerificationRequest with claim to verify
        
    Returns:
        ClaimVerificationResponse with verification results
    """
    start_time = time.time()
    
    try:
        logger.info(f"Verifying claim: {request.claim[:100]}...")
        
        # Verify the claim
        claim_result = await detector._verify_claim(request.claim)
        
        # Convert to response format
        supporting_sources = []
        refuting_sources = []
        
        if request.include_sources:
            supporting_sources = [
                SourceDocument(
                    title=source.get('title', 'Untitled'),
                    url=source.get('url', ''),
                    text=source.get('text', ''),
                    published_date=source.get('publishedDate'),
                    author=source.get('author'),
                    score=source.get('score', 0.5)
                )
                for source in claim_result.supporting_sources
            ]
            
            refuting_sources = [
                SourceDocument(
                    title=source.get('title', 'Untitled'),
                    url=source.get('url', ''),
                    text=source.get('text', ''),
                    published_date=source.get('publishedDate'),
                    author=source.get('author'),
                    score=source.get('score', 0.5)
                )
                for source in claim_result.refuting_sources
            ]
        
        claim_obj = Claim(
            text=claim_result.text,
            confidence=claim_result.confidence,
            assessment=AssessmentType(claim_result.assessment),
            supporting_sources=supporting_sources,
            refuting_sources=refuting_sources,
            reasoning=getattr(claim_result, 'reasoning', None)
        )
        
        processing_time = int((time.time() - start_time) * 1000)
        
        response = ClaimVerificationResponse(
            success=True,
            claim=claim_obj,
            timestamp=time.strftime('%Y-%m-%dT%H:%M:%S'),
            processing_time_ms=processing_time
        )
        
        logger.info(f"Claim verification completed. Assessment: {claim_result.assessment}")
        return response
        
    except Exception as e:
        logger.error(f"Error in claim verification: {str(e)}")
        processing_time = int((time.time() - start_time) * 1000)
        
        return ClaimVerificationResponse(
            success=False,
            claim=Claim(
                text=request.claim,
                confidence=0.0,
                assessment=AssessmentType.INSUFFICIENT_INFORMATION,
                supporting_sources=[],
                refuting_sources=[],
                reasoning="Error during verification"
            ),
            timestamp=time.strftime('%Y-%m-%dT%H:%M:%S'),
            processing_time_ms=processing_time,
            error=str(e)
        )

@router.get("/health", response_model=HealthCheckResponse)
async def health_check() -> HealthCheckResponse:
    """
    Health check endpoint for the hallucination detector service.
    
    Returns:
        HealthCheckResponse with service status and API availability
    """
    try:
        # Check API availability
        exa_available = bool(detector.exa_api_key)
        openai_available = bool(detector.openai_api_key)
        
        status = "healthy" if (exa_available or openai_available) else "degraded"
        
        response = HealthCheckResponse(
            status=status,
            version="1.0.0",
            exa_api_available=exa_available,
            openai_api_available=openai_available,
            timestamp=time.strftime('%Y-%m-%dT%H:%M:%S')
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error in health check: {str(e)}")
        
        return HealthCheckResponse(
            status="unhealthy",
            version="1.0.0",
            exa_api_available=False,
            openai_api_available=False,
            timestamp=time.strftime('%Y-%m-%dT%H:%M:%S')
        )

@router.get("/demo")
async def demo_endpoint() -> Dict[str, Any]:
    """
    Demo endpoint showing example usage of the hallucination detector.
    
    Returns:
        Dictionary with example request/response data
    """
    return {
        "description": "Hallucination Detector API Demo",
        "version": "1.0.0",
        "endpoints": {
            "detect": {
                "method": "POST",
                "path": "/api/hallucination-detector/detect",
                "description": "Detect hallucinations in text using Exa.ai",
                "example_request": {
                    "text": "The Eiffel Tower is located in Paris and was built in 1889. It is 330 meters tall.",
                    "include_sources": True,
                    "max_claims": 5
                }
            },
            "extract_claims": {
                "method": "POST", 
                "path": "/api/hallucination-detector/extract-claims",
                "description": "Extract verifiable claims from text",
                "example_request": {
                    "text": "Our company increased sales by 25% last quarter. We launched 3 new products.",
                    "max_claims": 10
                }
            },
            "verify_claim": {
                "method": "POST",
                "path": "/api/hallucination-detector/verify-claim", 
                "description": "Verify a single claim against sources",
                "example_request": {
                    "claim": "The Eiffel Tower is in Paris",
                    "include_sources": True
                }
            }
        },
        "features": [
            "Claim extraction using LLM",
            "Evidence search using Exa.ai",
            "Claim verification with confidence scores",
            "Source attribution and credibility assessment",
            "Fallback mechanisms for API unavailability"
        ]
    }
