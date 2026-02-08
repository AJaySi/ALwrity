"""
Meta Description Generation Service

AI-powered SEO meta description generator that creates compelling,
optimized descriptions for content creators and digital marketers.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger

from ..llm_providers.main_text_generation import llm_text_gen
from middleware.logging_middleware import seo_logger


class MetaDescriptionService:
    """Service for generating AI-powered SEO meta descriptions"""
    
    def __init__(self):
        """Initialize the meta description service"""
        self.service_name = "meta_description_generator"
        logger.info(f"Initialized {self.service_name}")
    
    async def generate_meta_description(
        self,
        keywords: List[str],
        tone: str = "General",
        search_intent: str = "Informational Intent",
        language: str = "English",
        custom_prompt: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate AI-powered meta descriptions based on keywords and parameters
        
        Args:
            keywords: List of target keywords
            tone: Desired tone (General, Informative, Engaging, etc.)
            search_intent: Type of search intent
            language: Target language for generation
            custom_prompt: Optional custom prompt override
            
        Returns:
            Dictionary containing generated meta descriptions and analysis
        """
        try:
            start_time = datetime.utcnow()
            
            # Input validation
            if not keywords or len(keywords) == 0:
                raise ValueError("At least one keyword is required")
            
            # Prepare keywords string
            keywords_str = ", ".join(keywords[:10])  # Limit to 10 keywords
            
            # Build the generation prompt
            if custom_prompt:
                prompt = custom_prompt
            else:
                prompt = self._build_meta_description_prompt(
                    keywords_str, tone, search_intent, language
                )
            
            # Generate meta descriptions using AI
            logger.info(f"Generating meta descriptions for keywords: {keywords_str}")
            
            ai_response = llm_text_gen(
                prompt=prompt,
                system_prompt=self._get_system_prompt(language),
                user_id=user_id
            )
            
            # Parse and structure the response
            meta_descriptions = self._parse_ai_response(ai_response)
            
            # Analyze generated descriptions
            analysis = self._analyze_meta_descriptions(meta_descriptions, keywords)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            result = {
                "meta_descriptions": meta_descriptions,
                "analysis": analysis,
                "generation_params": {
                    "keywords": keywords,
                    "tone": tone,
                    "search_intent": search_intent,
                    "language": language,
                    "keywords_count": len(keywords)
                },
                "ai_model_info": {
                    "provider": "gemini",
                    "model": "gemini-2.0-flash-001",
                    "prompt_length": len(prompt),
                    "response_length": len(ai_response)
                },
                "execution_time": execution_time,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Log the operation
            await seo_logger.log_tool_usage(
                tool_name=self.service_name,
                input_data={
                    "keywords": keywords,
                    "tone": tone,
                    "search_intent": search_intent,
                    "language": language
                },
                output_data=result,
                success=True
            )
            
            await seo_logger.log_ai_analysis(
                tool_name=self.service_name,
                prompt=prompt,
                response=ai_response,
                model_used="gemini-2.0-flash-001"
            )
            
            logger.info(f"Successfully generated {len(meta_descriptions)} meta descriptions")
            return result
            
        except Exception as e:
            logger.error(f"Error generating meta descriptions: {e}")
            
            # Log the error
            await seo_logger.log_tool_usage(
                tool_name=self.service_name,
                input_data={
                    "keywords": keywords,
                    "tone": tone,
                    "search_intent": search_intent,
                    "language": language
                },
                output_data={"error": str(e)},
                success=False
            )
            
            raise
    
    def _build_meta_description_prompt(
        self,
        keywords: str,
        tone: str,
        search_intent: str,
        language: str
    ) -> str:
        """Build the AI prompt for meta description generation"""
        
        intent_guidance = {
            "Informational Intent": "Focus on providing value and answering questions",
            "Commercial Intent": "Emphasize benefits and competitive advantages",
            "Transactional Intent": "Include strong calls-to-action and urgency",
            "Navigational Intent": "Highlight brand recognition and specific page content"
        }
        
        tone_guidance = {
            "General": "balanced and professional",
            "Informative": "educational and authoritative",
            "Engaging": "compelling and conversational",
            "Humorous": "light-hearted and memorable",
            "Intriguing": "mysterious and curiosity-driven",
            "Playful": "fun and energetic"
        }
        
        prompt = f"""
Create 5 compelling SEO meta descriptions for content targeting these keywords: {keywords}

Requirements:
- Length: 150-160 characters (optimal for search results)
- Language: {language}
- Tone: {tone_guidance.get(tone, tone)}
- Search Intent: {search_intent} - {intent_guidance.get(search_intent, "")}
- Include primary keywords naturally
- Create urgency or curiosity where appropriate
- Ensure each description is unique and actionable

Guidelines for effective meta descriptions:
1. Start with action words or emotional triggers
2. Include primary keyword in first 120 characters
3. Add value proposition or benefit
4. Use active voice
5. Consider including numbers or specific details
6. End with compelling reason to click

Please provide 5 different meta descriptions, each on a new line, numbered 1-5.
Focus on creating descriptions that will improve click-through rates for content creators and digital marketers.
"""
        
        return prompt
    
    def _get_system_prompt(self, language: str) -> str:
        """Get system prompt for meta description generation"""
        return f"""You are an expert SEO copywriter specializing in meta descriptions that drive high click-through rates. 
        You understand search engine optimization, user psychology, and compelling copywriting.
        
        Your goal is to create meta descriptions that:
        - Accurately represent the content
        - Entice users to click
        - Include target keywords naturally
        - Comply with search engine best practices
        - Appeal to the target audience
        
        Language: {language}
        
        Always provide exactly 5 unique meta descriptions as requested, numbered 1-5.
        """
    
    def _parse_ai_response(self, ai_response: str) -> List[Dict[str, Any]]:
        """Parse AI response into structured meta descriptions"""
        descriptions = []
        lines = ai_response.strip().split('\n')
        
        current_desc = ""
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if line starts with a number (1., 2., etc.)
            if line and (line[0].isdigit() or line.startswith(('1.', '2.', '3.', '4.', '5.'))):
                if current_desc:
                    # Process previous description
                    cleaned_desc = self._clean_description(current_desc)
                    if cleaned_desc:
                        descriptions.append(self._analyze_single_description(cleaned_desc))
                
                # Start new description
                current_desc = line
            else:
                # Continue current description
                if current_desc:
                    current_desc += " " + line
        
        # Process last description
        if current_desc:
            cleaned_desc = self._clean_description(current_desc)
            if cleaned_desc:
                descriptions.append(self._analyze_single_description(cleaned_desc))
        
        # If parsing failed, create fallback descriptions
        if not descriptions:
            descriptions = self._create_fallback_descriptions(ai_response)
        
        return descriptions[:5]  # Ensure max 5 descriptions
    
    def _clean_description(self, description: str) -> str:
        """Clean and format a meta description"""
        # Remove numbering
        cleaned = description
        if cleaned and cleaned[0].isdigit():
            # Remove "1. ", "2. ", etc.
            cleaned = cleaned.split('.', 1)[-1].strip()
        
        # Remove extra whitespace
        cleaned = ' '.join(cleaned.split())
        
        # Remove quotes if present
        if cleaned.startswith('"') and cleaned.endswith('"'):
            cleaned = cleaned[1:-1]
        
        return cleaned
    
    def _analyze_single_description(self, description: str) -> Dict[str, Any]:
        """Analyze a single meta description"""
        char_count = len(description)
        word_count = len(description.split())
        
        # Check if length is optimal
        length_status = "optimal" if 150 <= char_count <= 160 else \
                      "short" if char_count < 150 else "long"
        
        return {
            "text": description,
            "character_count": char_count,
            "word_count": word_count,
            "length_status": length_status,
            "seo_score": self._calculate_seo_score(description, char_count),
            "recommendations": self._generate_recommendations(description, char_count)
        }
    
    def _calculate_seo_score(self, description: str, char_count: int) -> int:
        """Calculate SEO score for a meta description"""
        score = 0
        
        # Length scoring (40 points max)
        if 150 <= char_count <= 160:
            score += 40
        elif 140 <= char_count <= 170:
            score += 30
        elif 130 <= char_count <= 180:
            score += 20
        else:
            score += 10
        
        # Action words (20 points max)
        action_words = ['discover', 'learn', 'get', 'find', 'explore', 'unlock', 'master', 'boost', 'improve', 'achieve']
        if any(word.lower() in description.lower() for word in action_words):
            score += 20
        
        # Numbers or specifics (15 points max)
        if any(char.isdigit() for char in description):
            score += 15
        
        # Emotional triggers (15 points max)
        emotional_words = ['amazing', 'incredible', 'proven', 'secret', 'ultimate', 'essential', 'exclusive', 'free']
        if any(word.lower() in description.lower() for word in emotional_words):
            score += 15
        
        # Call to action (10 points max)
        cta_phrases = ['click', 'read more', 'learn more', 'discover', 'find out', 'see how']
        if any(phrase.lower() in description.lower() for phrase in cta_phrases):
            score += 10
        
        return min(score, 100)  # Cap at 100
    
    def _generate_recommendations(self, description: str, char_count: int) -> List[str]:
        """Generate recommendations for improving meta description"""
        recommendations = []
        
        if char_count < 150:
            recommendations.append("Consider adding more detail to reach optimal length (150-160 characters)")
        elif char_count > 160:
            recommendations.append("Shorten description to fit within optimal length (150-160 characters)")
        
        if not any(char.isdigit() for char in description):
            recommendations.append("Consider adding specific numbers or statistics for better appeal")
        
        action_words = ['discover', 'learn', 'get', 'find', 'explore', 'unlock', 'master', 'boost', 'improve', 'achieve']
        if not any(word.lower() in description.lower() for word in action_words):
            recommendations.append("Add action words to create urgency and encourage clicks")
        
        if description.count(',') > 2:
            recommendations.append("Simplify sentence structure for better readability")
        
        return recommendations
    
    def _analyze_meta_descriptions(self, descriptions: List[Dict[str, Any]], keywords: List[str]) -> Dict[str, Any]:
        """Analyze all generated meta descriptions"""
        if not descriptions:
            return {"error": "No descriptions generated"}
        
        # Calculate overall statistics
        avg_length = sum(desc["character_count"] for desc in descriptions) / len(descriptions)
        avg_score = sum(desc["seo_score"] for desc in descriptions) / len(descriptions)
        
        # Find best description
        best_desc = max(descriptions, key=lambda x: x["seo_score"])
        
        # Keyword coverage analysis
        keyword_coverage = self._analyze_keyword_coverage(descriptions, keywords)
        
        return {
            "total_descriptions": len(descriptions),
            "average_length": round(avg_length, 1),
            "average_seo_score": round(avg_score, 1),
            "best_description": best_desc,
            "keyword_coverage": keyword_coverage,
            "length_distribution": {
                "optimal": len([d for d in descriptions if d["length_status"] == "optimal"]),
                "short": len([d for d in descriptions if d["length_status"] == "short"]),
                "long": len([d for d in descriptions if d["length_status"] == "long"])
            }
        }
    
    def _analyze_keyword_coverage(self, descriptions: List[Dict[str, Any]], keywords: List[str]) -> Dict[str, Any]:
        """Analyze how well keywords are covered in descriptions"""
        coverage_stats = {}
        
        for keyword in keywords:
            coverage_count = sum(
                1 for desc in descriptions 
                if keyword.lower() in desc["text"].lower()
            )
            coverage_stats[keyword] = {
                "covered_count": coverage_count,
                "coverage_percentage": (coverage_count / len(descriptions)) * 100
            }
        
        return coverage_stats
    
    def _create_fallback_descriptions(self, ai_response: str) -> List[Dict[str, Any]]:
        """Create fallback descriptions if parsing fails"""
        # Split response into sentences and use first few as descriptions
        sentences = ai_response.split('. ')
        descriptions = []
        
        for i, sentence in enumerate(sentences[:5]):
            if len(sentence.strip()) > 50:  # Minimum length check
                desc_text = sentence.strip()
                if not desc_text.endswith('.'):
                    desc_text += '.'
                
                descriptions.append(self._analyze_single_description(desc_text))
        
        return descriptions
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for the meta description service"""
        try:
            # Test basic functionality
            test_result = await self.generate_meta_description(
                keywords=["test"],
                tone="General",
                search_intent="Informational Intent",
                language="English"
            )
            
            return {
                "status": "operational",
                "service": self.service_name,
                "test_passed": bool(test_result.get("meta_descriptions")),
                "last_check": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "service": self.service_name,
                "error": str(e),
                "last_check": datetime.utcnow().isoformat()
            }
