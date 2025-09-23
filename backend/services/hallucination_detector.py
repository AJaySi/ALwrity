"""
Hallucination Detector Service

This service implements fact-checking functionality using Exa.ai API
to detect and verify claims in AI-generated content, similar to the
Exa.ai demo implementation.
"""

import json
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import requests
import os
import asyncio
import concurrent.futures
try:
    from google import genai
    GOOGLE_GENAI_AVAILABLE = True
except Exception:
    GOOGLE_GENAI_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class Claim:
    """Represents a single verifiable claim extracted from text."""
    text: str
    confidence: float
    assessment: str  # "supported", "refuted", "insufficient_information"
    supporting_sources: List[Dict[str, Any]]
    refuting_sources: List[Dict[str, Any]]
    reasoning: str = ""

@dataclass
class HallucinationResult:
    """Result of hallucination detection analysis."""
    claims: List[Claim]
    overall_confidence: float
    total_claims: int
    supported_claims: int
    refuted_claims: int
    insufficient_claims: int
    timestamp: str

class HallucinationDetector:
    """
    Hallucination detector using Exa.ai for fact-checking.
    
    Implements the three-step process from Exa.ai demo:
    1. Extract verifiable claims from text
    2. Search for evidence using Exa.ai
    3. Verify claims against sources
    """
    
    def __init__(self):
        self.exa_api_key = os.getenv('EXA_API_KEY')
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        
        if not self.exa_api_key:
            logger.warning("EXA_API_KEY not found. Hallucination detection will be limited.")
        
        if not self.gemini_api_key:
            logger.warning("GEMINI_API_KEY not found. Falling back to heuristic claim extraction.")
        
        # Initialize Gemini client for claim extraction and assessment
        self.gemini_client = genai.Client(api_key=self.gemini_api_key) if (GOOGLE_GENAI_AVAILABLE and self.gemini_api_key) else None
        
        # Rate limiting to prevent API abuse
        self.daily_api_calls = 0
        self.daily_limit = 20  # Max 20 API calls per day for fact checking
        self.last_reset_date = None
    
    def _check_rate_limit(self) -> bool:
        """Check if we're within daily API usage limits."""
        from datetime import date
        
        today = date.today()
        
        # Reset counter if it's a new day
        if self.last_reset_date != today:
            self.daily_api_calls = 0
            self.last_reset_date = today
        
        # Check if we've exceeded the limit
        if self.daily_api_calls >= self.daily_limit:
            logger.warning(f"Daily API limit reached ({self.daily_limit} calls). Fact checking disabled for today.")
            return False
        
        # Increment counter for this API call
        self.daily_api_calls += 1
        logger.info(f"Fact check API call #{self.daily_api_calls}/{self.daily_limit} today")
        return True
        
    async def detect_hallucinations(self, text: str) -> HallucinationResult:
        """
        Main method to detect hallucinations in the given text.
        
        Args:
            text: The text to analyze for factual accuracy
            
        Returns:
            HallucinationResult with claims analysis and confidence scores
        """
        try:
            logger.info(f"Starting hallucination detection for text of length: {len(text)}")
            logger.info(f"Text sample: {text[:200]}...")
            
            # Check rate limits first
            if not self._check_rate_limit():
                return HallucinationResult(
                    claims=[],
                    overall_confidence=0.0,
                    total_claims=0,
                    supported_claims=0,
                    refuted_claims=0,
                    insufficient_claims=0,
                    timestamp=datetime.now().isoformat()
                )
            
            # Validate required API keys
            if not self.gemini_api_key:
                raise Exception("GEMINI_API_KEY not configured. Cannot perform hallucination detection.")
            if not self.exa_api_key:
                raise Exception("EXA_API_KEY not configured. Cannot search for evidence.")
            
            # Step 1: Extract claims from text
            claims_texts = await self._extract_claims(text)
            logger.info(f"Extracted {len(claims_texts)} claims from text: {claims_texts}")
            
            if not claims_texts:
                logger.warning("No verifiable claims found in text")
                return HallucinationResult(
                    claims=[],
                    overall_confidence=0.0,
                    total_claims=0,
                    supported_claims=0,
                    refuted_claims=0,
                    insufficient_claims=0,
                    timestamp=datetime.now().isoformat()
                )
            
            # Step 2 & 3: Verify claims in batch to reduce API calls
            verified_claims = await self._verify_claims_batch(claims_texts)
            
            # Calculate overall metrics
            total_claims = len(verified_claims)
            supported_claims = sum(1 for c in verified_claims if c.assessment == "supported")
            refuted_claims = sum(1 for c in verified_claims if c.assessment == "refuted")
            insufficient_claims = sum(1 for c in verified_claims if c.assessment == "insufficient_information")
            
            # Calculate overall confidence (weighted average)
            if total_claims > 0:
                overall_confidence = sum(c.confidence for c in verified_claims) / total_claims
            else:
                overall_confidence = 0.0
            
            result = HallucinationResult(
                claims=verified_claims,
                overall_confidence=overall_confidence,
                total_claims=total_claims,
                supported_claims=supported_claims,
                refuted_claims=refuted_claims,
                insufficient_claims=insufficient_claims,
                timestamp=datetime.now().isoformat()
            )
            
            logger.info(f"Hallucination detection completed. Overall confidence: {overall_confidence:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Error in hallucination detection: {str(e)}")
            raise Exception(f"Hallucination detection failed: {str(e)}")
    
    async def _extract_claims(self, text: str) -> List[str]:
        """
        Extract verifiable claims from text using LLM.
        
        Args:
            text: Input text to extract claims from
            
        Returns:
            List of claim strings
        """
        if not self.gemini_client:
            raise Exception("Gemini client not available. Cannot extract claims without AI provider.")
        
        try:
            prompt = (
                "Extract verifiable factual claims from the following text. "
                "A verifiable claim is a statement that can be checked against external sources for accuracy.\n\n"
                "Return ONLY a valid JSON array of strings, where each string is a single verifiable claim.\n\n"
                "Examples of GOOD verifiable claims:\n"
                "- \"The company was founded in 2020\"\n"
                "- \"Sales increased by 25% last quarter\"\n"
                "- \"The product has 10,000 users\"\n"
                "- \"The market size is $50 billion\"\n"
                "- \"The software supports 15 languages\"\n"
                "- \"The company has offices in 5 countries\"\n\n"
                "Examples of BAD claims (opinions, subjective statements):\n"
                "- \"This is the best product\"\n"
                "- \"Customers love our service\"\n"
                "- \"We are innovative\"\n"
                "- \"The future looks bright\"\n\n"
                "IMPORTANT: Extract at least 2-3 verifiable claims if possible. "
                "Look for specific facts, numbers, dates, locations, and measurable statements.\n\n"
                f"Text to analyze: {text}\n\n"
                "Return only the JSON array of verifiable claims:"
            )
            
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                resp = await loop.run_in_executor(executor, lambda: self.gemini_client.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=prompt
                ))
            
            if not resp or not resp.text:
                raise Exception("Empty response from Gemini API")
            
            claims_text = resp.text.strip()
            logger.info(f"Raw Gemini response for claims: {claims_text[:200]}...")
            
            # Try to extract JSON from the response
            try:
                claims = json.loads(claims_text)
            except json.JSONDecodeError:
                # Try to find JSON array in the response (handle markdown code blocks)
                import re
                # First try to extract from markdown code blocks
                code_block_match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', claims_text, re.DOTALL)
                if code_block_match:
                    claims = json.loads(code_block_match.group(1))
                else:
                    # Try to find JSON array directly
                    json_match = re.search(r'\[.*?\]', claims_text, re.DOTALL)
                    if json_match:
                        claims = json.loads(json_match.group())
                    else:
                        raise Exception(f"Could not parse JSON from Gemini response: {claims_text[:100]}")
            
            if isinstance(claims, list):
                valid_claims = [claim for claim in claims if isinstance(claim, str) and claim.strip()]
                logger.info(f"Successfully extracted {len(valid_claims)} claims")
                return valid_claims
            else:
                raise Exception(f"Expected JSON array, got: {type(claims)}")
                
        except Exception as e:
            logger.error(f"Error extracting claims: {str(e)}")
            raise Exception(f"Failed to extract claims: {str(e)}")
    
    
    async def _verify_claims_batch(self, claims: List[str]) -> List[Claim]:
        """
        Verify multiple claims in batch to reduce API calls.
        
        Args:
            claims: List of claims to verify
            
        Returns:
            List of Claim objects with verification results
        """
        try:
            logger.info(f"Starting batch verification of {len(claims)} claims")
            
            # Limit to maximum 3 claims to prevent excessive API usage
            max_claims = min(len(claims), 3)
            claims_to_verify = claims[:max_claims]
            
            if len(claims) > max_claims:
                logger.warning(f"Limited verification to {max_claims} claims to prevent API rate limits")
            
            # Step 1: Search for evidence for all claims in one batch
            all_sources = await self._search_evidence_batch(claims_to_verify)
            
            # Step 2: Assess all claims against sources in one API call
            verified_claims = await self._assess_claims_batch(claims_to_verify, all_sources)
            
            # Add any remaining claims as insufficient information
            for i in range(max_claims, len(claims)):
                verified_claims.append(Claim(
                    text=claims[i],
                    confidence=0.0,
                    assessment="insufficient_information",
                    supporting_sources=[],
                    refuting_sources=[],
                    reasoning="Not verified due to API rate limit protection"
                ))
            
            logger.info(f"Batch verification completed for {len(verified_claims)} claims")
            return verified_claims
            
        except Exception as e:
            logger.error(f"Error in batch verification: {str(e)}")
            # Return all claims as insufficient information
            return [
                Claim(
                    text=claim,
                    confidence=0.0,
                    assessment="insufficient_information",
                    supporting_sources=[],
                    refuting_sources=[],
                    reasoning=f"Batch verification failed: {str(e)}"
                )
                for claim in claims
            ]

    async def _verify_claim(self, claim: str) -> Claim:
        """
        Verify a single claim using Exa.ai search.
        
        Args:
            claim: The claim to verify
            
        Returns:
            Claim object with verification results
        """
        try:
            # Search for evidence using Exa.ai
            sources = await self._search_evidence(claim)
            
            if not sources:
                return Claim(
                    text=claim,
                    confidence=0.5,
                    assessment="insufficient_information",
                    supporting_sources=[],
                    refuting_sources=[],
                    reasoning="No sources found for verification"
                )
            
            # Verify claim against sources using LLM
            verification_result = await self._assess_claim_against_sources(claim, sources)
            
            return Claim(
                text=claim,
                confidence=verification_result.get('confidence', 0.5),
                assessment=verification_result.get('assessment', 'insufficient_information'),
                supporting_sources=verification_result.get('supporting_sources', []),
                refuting_sources=verification_result.get('refuting_sources', []),
                reasoning=verification_result.get('reasoning', '')
            )
            
        except Exception as e:
            logger.error(f"Error verifying claim '{claim}': {str(e)}")
            return Claim(
                text=claim,
                confidence=0.5,
                assessment="insufficient_information",
                supporting_sources=[],
                refuting_sources=[],
                reasoning=f"Error during verification: {str(e)}"
            )
    
    async def _search_evidence_batch(self, claims: List[str]) -> List[Dict[str, Any]]:
        """
        Search for evidence for multiple claims in one API call.
        
        Args:
            claims: List of claims to search for
            
        Returns:
            List of sources relevant to the claims
        """
        try:
            # Combine all claims into one search query
            combined_query = " ".join(claims[:2])  # Use first 2 claims to avoid query length limits
            
            logger.info(f"Searching for evidence for {len(claims)} claims with combined query")
            
            # Use the existing search method with combined query
            sources = await self._search_evidence(combined_query)
            
            # Limit sources to prevent excessive processing
            max_sources = 5
            if len(sources) > max_sources:
                sources = sources[:max_sources]
                logger.info(f"Limited sources to {max_sources} to prevent API rate limits")
            
            return sources
            
        except Exception as e:
            logger.error(f"Error in batch evidence search: {str(e)}")
            return []

    async def _assess_claims_batch(self, claims: List[str], sources: List[Dict[str, Any]]) -> List[Claim]:
        """
        Assess multiple claims against sources in one API call.
        
        Args:
            claims: List of claims to assess
            sources: List of sources to assess against
            
        Returns:
            List of Claim objects with assessment results
        """
        if not self.gemini_client:
            raise Exception("Gemini client not available. Cannot assess claims without AI provider.")
        
        try:
            # Limit to 3 claims to prevent excessive API usage
            claims_to_assess = claims[:3]
            
            # Prepare sources text
            combined_sources = "\n\n".join([
                f"Source {i+1}: {src.get('url','')}\nText: {src.get('text','')[:1000]}"
                for i, src in enumerate(sources)
            ])
            
            # Prepare claims text
            claims_text = "\n".join([
                f"Claim {i+1}: {claim}"
                for i, claim in enumerate(claims_to_assess)
            ])
            
            prompt = (
                "You are a strict fact-checker. Analyze each claim against the provided sources.\n\n"
                "Return ONLY a valid JSON object with this exact structure:\n"
                "{\n"
                '  "assessments": [\n'
                '    {\n'
                '      "claim_index": 0,\n'
                '      "assessment": "supported" or "refuted" or "insufficient_information",\n'
                '      "confidence": number between 0.0 and 1.0,\n'
                '      "supporting_sources": [array of source indices that support the claim],\n'
                '      "refuting_sources": [array of source indices that refute the claim],\n'
                '      "reasoning": "brief explanation of your assessment"\n'
                '    }\n'
                '  ]\n'
                "}\n\n"
                f"Claims to verify:\n{claims_text}\n\n"
                f"Sources:\n{combined_sources}\n\n"
                "Return only the JSON object:"
            )
            
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                resp = await loop.run_in_executor(executor, lambda: self.gemini_client.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=prompt
                ))
            
            if not resp or not resp.text:
                raise Exception("Empty response from Gemini API for batch assessment")
            
            result_text = resp.text.strip()
            logger.info(f"Raw Gemini response for batch assessment: {result_text[:200]}...")
            
            # Try to extract JSON from the response
            try:
                result = json.loads(result_text)
            except json.JSONDecodeError:
                # Try to find JSON object in the response (handle markdown code blocks)
                import re
                code_block_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', result_text, re.DOTALL)
                if code_block_match:
                    result = json.loads(code_block_match.group(1))
                else:
                    json_match = re.search(r'\{.*?\}', result_text, re.DOTALL)
                    if json_match:
                        result = json.loads(json_match.group())
                    else:
                        raise Exception(f"Could not parse JSON from Gemini response: {result_text[:100]}")
            
            # Process assessments
            assessments = result.get('assessments', [])
            verified_claims = []
            
            for i, claim in enumerate(claims_to_assess):
                # Find assessment for this claim
                assessment = None
                for a in assessments:
                    if a.get('claim_index') == i:
                        assessment = a
                        break
                
                if assessment:
                    # Process supporting and refuting sources
                    supporting_sources = []
                    refuting_sources = []
                    
                    if isinstance(assessment.get('supporting_sources'), list):
                        for idx in assessment['supporting_sources']:
                            if isinstance(idx, int) and 0 <= idx < len(sources):
                                supporting_sources.append(sources[idx])
                    
                    if isinstance(assessment.get('refuting_sources'), list):
                        for idx in assessment['refuting_sources']:
                            if isinstance(idx, int) and 0 <= idx < len(sources):
                                refuting_sources.append(sources[idx])
                    
                    verified_claims.append(Claim(
                        text=claim,
                        confidence=float(assessment.get('confidence', 0.5)),
                        assessment=assessment.get('assessment', 'insufficient_information'),
                        supporting_sources=supporting_sources,
                        refuting_sources=refuting_sources,
                        reasoning=assessment.get('reasoning', '')
                    ))
                else:
                    # No assessment found for this claim
                    verified_claims.append(Claim(
                        text=claim,
                        confidence=0.0,
                        assessment="insufficient_information",
                        supporting_sources=[],
                        refuting_sources=[],
                        reasoning="No assessment provided"
                    ))
            
            logger.info(f"Successfully assessed {len(verified_claims)} claims in batch")
            return verified_claims
            
        except Exception as e:
            logger.error(f"Error in batch assessment: {str(e)}")
            # Return all claims as insufficient information
            return [
                Claim(
                    text=claim,
                    confidence=0.0,
                    assessment="insufficient_information",
                    supporting_sources=[],
                    refuting_sources=[],
                    reasoning=f"Batch assessment failed: {str(e)}"
                )
                for claim in claims_to_assess
            ]

    async def _search_evidence(self, claim: str) -> List[Dict[str, Any]]:
        """
        Search for evidence using Exa.ai API.
        
        Args:
            claim: The claim to search evidence for
            
        Returns:
            List of source documents with evidence
        """
        if not self.exa_api_key:
            raise Exception("Exa API key not available. Cannot search for evidence without Exa.ai access.")
        
        try:
            headers = {
                'x-api-key': self.exa_api_key,
                'Content-Type': 'application/json'
            }
            
            payload = {
                'query': claim,
                'numResults': 5,
                'text': True,
                'useAutoprompt': True
            }
            
            response = requests.post(
                'https://api.exa.ai/search',
                headers=headers,
                json=payload,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                
                if not results:
                    raise Exception(f"No search results found for claim: {claim}")
                
                sources = []
                for result in results:
                    source = {
                        'title': result.get('title', 'Untitled'),
                        'url': result.get('url', ''),
                        'text': result.get('text', ''),
                        'publishedDate': result.get('publishedDate', ''),
                        'author': result.get('author', ''),
                        'score': result.get('score', 0.5)
                    }
                    sources.append(source)
                
                logger.info(f"Found {len(sources)} sources for claim: {claim[:50]}...")
                return sources
            else:
                raise Exception(f"Exa API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"Error searching evidence with Exa: {str(e)}")
            raise Exception(f"Failed to search evidence: {str(e)}")
    
    
    async def _assess_claim_against_sources(self, claim: str, sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Assess whether sources support or refute the claim using LLM.
        
        Args:
            claim: The claim to assess
            sources: List of source documents
            
        Returns:
            Dictionary with assessment results
        """
        if not self.gemini_client:
            raise Exception("Gemini client not available. Cannot assess claims without AI provider.")
        
        try:
            combined_sources = "\n\n".join([
                f"Source {i+1}: {src.get('url','')}\nText: {src.get('text','')[:2000]}"
                for i, src in enumerate(sources)
            ])
            
            prompt = (
                "You are a strict fact-checker. Analyze the claim against the provided sources.\n\n"
                "Return ONLY a valid JSON object with this exact structure:\n"
                "{\n"
                '  "assessment": "supported" or "refuted" or "insufficient_information",\n'
                '  "confidence": number between 0.0 and 1.0,\n'
                '  "supporting_sources": [array of source indices that support the claim],\n'
                '  "refuting_sources": [array of source indices that refute the claim],\n'
                '  "reasoning": "brief explanation of your assessment"\n'
                "}\n\n"
                f"Claim to verify: {claim}\n\n"
                f"Sources:\n{combined_sources}\n\n"
                "Return only the JSON object:"
            )
            
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                resp = await loop.run_in_executor(executor, lambda: self.gemini_client.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=prompt
                ))
            
            if not resp or not resp.text:
                raise Exception("Empty response from Gemini API for claim assessment")
            
            result_text = resp.text.strip()
            logger.info(f"Raw Gemini response for assessment: {result_text[:200]}...")
            
            # Try to extract JSON from the response
            try:
                result = json.loads(result_text)
            except json.JSONDecodeError:
                # Try to find JSON object in the response (handle markdown code blocks)
                import re
                # First try to extract from markdown code blocks
                code_block_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', result_text, re.DOTALL)
                if code_block_match:
                    result = json.loads(code_block_match.group(1))
                else:
                    # Try to find JSON object directly
                    json_match = re.search(r'\{.*?\}', result_text, re.DOTALL)
                    if json_match:
                        result = json.loads(json_match.group())
                    else:
                        raise Exception(f"Could not parse JSON from Gemini response: {result_text[:100]}")
            
            # Validate required fields
            required_fields = ['assessment', 'confidence', 'supporting_sources', 'refuting_sources', 'reasoning']
            for field in required_fields:
                if field not in result:
                    raise Exception(f"Missing required field '{field}' in assessment response")
            
            # Process supporting and refuting sources
            supporting_sources = []
            refuting_sources = []
            
            if isinstance(result.get('supporting_sources'), list):
                for idx in result['supporting_sources']:
                    if isinstance(idx, int) and 0 <= idx < len(sources):
                        supporting_sources.append(sources[idx])
            
            if isinstance(result.get('refuting_sources'), list):
                for idx in result['refuting_sources']:
                    if isinstance(idx, int) and 0 <= idx < len(sources):
                        refuting_sources.append(sources[idx])
            
            # Validate assessment value
            valid_assessments = ['supported', 'refuted', 'insufficient_information']
            if result['assessment'] not in valid_assessments:
                raise Exception(f"Invalid assessment value: {result['assessment']}")
            
            # Validate confidence value
            confidence = float(result['confidence'])
            if not (0.0 <= confidence <= 1.0):
                raise Exception(f"Invalid confidence value: {confidence}")
            
            logger.info(f"Successfully assessed claim: {result['assessment']} (confidence: {confidence})")
            
            return {
                'assessment': result['assessment'],
                'confidence': confidence,
                'supporting_sources': supporting_sources,
                'refuting_sources': refuting_sources,
                'reasoning': result['reasoning']
            }
            
        except Exception as e:
            logger.error(f"Error assessing claim against sources: {str(e)}")
            raise Exception(f"Failed to assess claim: {str(e)}")
    
