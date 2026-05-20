"""
Hallucination Detector Service

Implements fact-checking using Exa.ai for evidence search and the
configured LLM provider (via GPT_PROVIDER) for claim extraction and assessment.
Respects GPT_PROVIDER env var: google, wavespeed, openai, huggingface.
"""

import json
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import os
import asyncio
import concurrent.futures

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


def _get_llm_provider_info() -> Dict[str, str]:
    """Determine the LLM provider from GPT_PROVIDER env var."""
    provider_env = os.getenv('GPT_PROVIDER', 'google').lower().strip()
    provider = provider_env.split(',')[0].strip() if provider_env else 'google'

    if provider in ('wavespeed', 'wave'):
        return {'provider': 'wavespeed', 'name': 'WaveSpeed'}
    elif provider in ('gemini', 'google'):
        return {'provider': 'google', 'name': 'Gemini'}
    elif provider in ('openai', 'gpt'):
        return {'provider': 'openai', 'name': 'OpenAI'}
    elif provider in ('hf_response_api', 'huggingface', 'hf'):
        return {'provider': 'huggingface', 'name': 'HuggingFace'}
    else:
        return {'provider': provider, 'name': provider.capitalize()}


class HallucinationDetector:
    """
    Hallucination detector using Exa.ai for evidence search
    and the configured LLM provider (GPT_PROVIDER) for claim extraction/assessment.

    Implements the three-step process:
    1. Extract verifiable claims from text
    2. Search for evidence using Exa.ai
    3. Verify claims against sources
    """

    def __init__(self):
        self._llm_provider_info = _get_llm_provider_info()

        # Check that at least one LLM key is available for the configured provider
        self._check_provider_keys()

        # Rate limiting
        self.daily_api_calls = 0
        self.daily_limit = 20
        self.last_reset_date = None

    def _check_provider_keys(self):
        """Check that API keys for the configured provider are available."""
        provider = self._llm_provider_info['provider']
        if provider == 'google':
            key = os.getenv('GEMINI_API_KEY')
            if not key:
                logger.warning(f"GEMINI_API_KEY not found. Hallucination detection will fail for provider '{provider}'.")
        elif provider == 'wavespeed':
            key = os.getenv('WAVESPEED_API_KEY')
            if not key:
                logger.warning(f"WAVESPEED_API_KEY not found. Hallucination detection will fail for provider '{provider}'.")
        elif provider == 'openai':
            key = os.getenv('OPENAI_API_KEY')
            if not key:
                logger.warning(f"OPENAI_API_KEY not found. Hallucination detection will fail for provider '{provider}'.")
        # huggingface uses serverless endpoint or HF token

    @property
    def provider_name(self) -> str:
        return self._llm_provider_info['name']

    @property
    def provider_key(self) -> str:
        return self._llm_provider_info['provider']

    def _check_rate_limit(self) -> bool:
        """Check if we're within daily API usage limits."""
        from datetime import date
        today = date.today()
        if self.last_reset_date != today:
            self.daily_api_calls = 0
            self.last_reset_date = today
        if self.daily_api_calls >= self.daily_limit:
            logger.warning(f"Daily API limit reached ({self.daily_limit} calls). Fact checking disabled for today.")
            return False
        self.daily_api_calls += 1
        logger.info(f"Fact check API call #{self.daily_api_calls}/{self.daily_limit} today")
        return True

    def _generate_text(self, prompt: str, system_prompt: Optional[str] = None, user_id: str = None) -> str:
        """Generate text using the configured LLM provider (respects GPT_PROVIDER)."""
        from services.llm_providers.main_text_generation import llm_text_gen

        result = llm_text_gen(
            prompt=prompt,
            system_prompt=system_prompt or "You are a precise fact-checking assistant. Respond only with valid JSON as instructed.",
            max_tokens=4000,
            user_id=user_id,
        )
        return result

    async def _generate_text_async(self, prompt: str, system_prompt: Optional[str] = None, user_id: str = None) -> str:
        """Async wrapper for _generate_text."""
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(
                executor,
                lambda: self._generate_text(prompt, system_prompt, user_id)
            )
        return result

    async def detect_hallucinations(self, text: str, user_id: str = None) -> HallucinationResult:
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

            # Step 1: Extract claims from text
            claims_texts = await self._extract_claims(text, user_id=user_id)
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

            # Step 2 & 3: Verify claims in batch
            verified_claims = await self._verify_claims_batch(claims_texts, user_id=user_id)

            # Calculate overall metrics
            total_claims = len(verified_claims)
            supported_claims = sum(1 for c in verified_claims if c.assessment == "supported")
            refuted_claims = sum(1 for c in verified_claims if c.assessment == "refuted")
            insufficient_claims = sum(1 for c in verified_claims if c.assessment == "insufficient_information")

            overall_confidence = sum(c.confidence for c in verified_claims) / total_claims if total_claims > 0 else 0.0

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

    async def _extract_claims(self, text: str, user_id: str = None) -> List[str]:
        """Extract verifiable claims from text using LLM."""
        try:
            prompt = (
                "Extract verifiable factual claims from the following text. "
                "A verifiable claim is a statement that can be checked against external sources for accuracy.\n\n"
                "Return ONLY a valid JSON array of strings, where each string is a single verifiable claim.\n\n"
                "Examples of GOOD verifiable claims:\n"
                '- "The company was founded in 2020"\n'
                '- "Sales increased by 25% last quarter"\n'
                '- "The product has 10,000 users"\n\n'
                "Examples of BAD claims (opinions, subjective statements):\n"
                '- "This is the best product"\n'
                '- "Customers love our service"\n\n'
                "IMPORTANT: Extract at least 2-3 verifiable claims if possible. "
                "Look for specific facts, numbers, dates, locations, and measurable statements.\n\n"
                f"Text to analyze: {text}\n\n"
                "Return only the JSON array of verifiable claims:"
            )

            result_text = await self._generate_text_async(prompt, user_id=user_id)
            logger.info(f"Raw LLM response for claims: {result_text[:200]}...")

            claims = self._parse_json_from_response(result_text, expect_array=True)

            if isinstance(claims, list):
                valid_claims = [claim for claim in claims if isinstance(claim, str) and claim.strip()]
                logger.info(f"Successfully extracted {len(valid_claims)} claims")
                return valid_claims
            else:
                raise Exception(f"Expected JSON array, got: {type(claims)}")

        except Exception as e:
            logger.error(f"Error extracting claims: {str(e)}")
            raise Exception(f"Failed to extract claims: {str(e)}")

    async def _verify_claims_batch(self, claims: List[str], user_id: str = None) -> List[Claim]:
        """Verify multiple claims in batch to reduce API calls."""
        try:
            logger.info(f"Starting batch verification of {len(claims)} claims")
            max_claims = min(len(claims), 3)
            claims_to_verify = claims[:max_claims]

            if len(claims) > max_claims:
                logger.warning(f"Limited verification to {max_claims} claims to prevent API rate limits")

            # Step 1: Search for evidence
            all_sources = await self._search_evidence_batch(claims_to_verify, user_id=user_id)

            # Step 2: Assess claims against sources
            verified_claims = await self._assess_claims_batch(claims_to_verify, all_sources, user_id=user_id)

            # Add remaining claims as insufficient information
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

    async def _verify_claim(self, claim: str, user_id: str = None) -> Claim:
        """Verify a single claim using Exa.ai search."""
        try:
            sources = await self._search_evidence(claim, user_id=user_id)

            if not sources:
                return Claim(
                    text=claim,
                    confidence=0.5,
                    assessment="insufficient_information",
                    supporting_sources=[],
                    refuting_sources=[],
                    reasoning="No sources found for verification"
                )

            verification_result = await self._assess_claim_against_sources(claim, sources, user_id=user_id)

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

    async def _search_evidence_batch(self, claims: List[str], user_id: str = None) -> List[Dict[str, Any]]:
        """Search for evidence for multiple claims in one API call."""
        try:
            combined_query = " ".join(claims[:2])
            logger.info(f"Searching for evidence for {len(claims)} claims with combined query")
            sources = await self._search_evidence(combined_query, user_id=user_id)

            max_sources = 5
            if len(sources) > max_sources:
                sources = sources[:max_sources]
                logger.info(f"Limited sources to {max_sources} to prevent API rate limits")

            return sources

        except Exception as e:
            logger.error(f"Error in batch evidence search: {str(e)}")
            return []

    async def _assess_claims_batch(self, claims: List[str], sources: List[Dict[str, Any]], user_id: str = None) -> List[Claim]:
        """Assess multiple claims against sources in one LLM call."""
        try:
            claims_to_assess = claims[:3]

            combined_sources = "\n\n".join([
                f"Source {i+1}: {src.get('url','')}\nText: {src.get('text','')[:1000]}"
                for i, src in enumerate(sources)
            ])

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

            result_text = await self._generate_text_async(prompt, user_id=user_id)
            logger.info(f"Raw LLM response for batch assessment: {result_text[:200]}...")

            result = self._parse_json_from_response(result_text, expect_array=False)

            assessments = result.get('assessments', [])
            verified_claims = []

            for i, claim in enumerate(claims_to_assess):
                assessment = None
                for a in assessments:
                    if a.get('claim_index') == i:
                        assessment = a
                        break

                if assessment:
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

    async def _search_evidence(self, claim: str, user_id: str = None) -> List[Dict[str, Any]]:
        """Search for evidence using ExaResearchProvider with subscription checks."""
        try:
            from services.blog_writer.research.exa_provider import ExaResearchProvider
            provider = ExaResearchProvider()
            sources = await provider.simple_search(
                query=claim,
                num_results=5,
                user_id=user_id,
            )
            if not sources:
                raise Exception(f"No search results found for claim: {claim}")
            logger.info(f"Found {len(sources)} sources for claim: {claim[:50]}...")
            return sources
        except Exception as e:
            logger.error(f"Error searching evidence with Exa: {str(e)}")
            raise Exception(f"Failed to search evidence: {str(e)}")

    async def _assess_claim_against_sources(self, claim: str, sources: List[Dict[str, Any]], user_id: str = None) -> Dict[str, Any]:
        """Assess whether sources support or refute the claim using LLM."""
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

            result_text = await self._generate_text_async(prompt, user_id=user_id)
            logger.info(f"Raw LLM response for assessment: {result_text[:200]}...")

            result = self._parse_json_from_response(result_text, expect_array=False)

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

    def _parse_json_from_response(self, text: str, expect_array: bool = False):
        """Extract and parse JSON from LLM response, handling markdown code blocks."""
        text = text.strip()

        # Try direct parse first
        try:
            result = json.loads(text)
            return result
        except json.JSONDecodeError:
            pass

        import re
        # Try to extract from markdown code blocks
        if expect_array:
            code_block_match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', text, re.DOTALL)
            if code_block_match:
                return json.loads(code_block_match.group(1))
            # Try to find JSON array directly
            json_match = re.search(r'\[.*\]', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        else:
            code_block_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
            if code_block_match:
                return json.loads(code_block_match.group(1))
            # Try to find JSON object directly
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())

        raise Exception(f"Could not parse JSON from LLM response: {text[:100]}")