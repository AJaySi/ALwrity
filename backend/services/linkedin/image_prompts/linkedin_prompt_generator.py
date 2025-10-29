"""
LinkedIn Image Prompt Generator Service

This service generates AI-optimized image prompts for LinkedIn content using Gemini's
capabilities. It creates three distinct prompt styles (professional, creative, industry-specific)
following best practices for image generation.
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger

# Import existing infrastructure
from ...onboarding.api_key_manager import APIKeyManager
from ...llm_providers.gemini_provider import gemini_text_response


class LinkedInPromptGenerator:
    """
    Generates AI-optimized image prompts for LinkedIn content.
    
    This service creates three distinct prompt styles following Gemini API best practices:
    1. Professional Style - Corporate aesthetics, clean lines, business colors
    2. Creative Style - Engaging visuals, vibrant colors, social media appeal  
    3. Industry-Specific Style - Tailored to specific business sectors
    """
    
    def __init__(self, api_key_manager: Optional[APIKeyManager] = None):
        """
        Initialize the LinkedIn Prompt Generator.
        
        Args:
            api_key_manager: API key manager for Gemini authentication
        """
        self.api_key_manager = api_key_manager or APIKeyManager()
        self.model = "gemini-2.0-flash-exp"
        
        # Prompt generation configuration
        self.max_prompt_length = 500
        self.style_variations = {
            'professional': 'corporate, clean, business, professional',
            'creative': 'engaging, vibrant, creative, social media',
            'industry_specific': 'industry-tailored, specialized, contextual'
        }
        
        logger.info("LinkedIn Prompt Generator initialized")
    
    async def generate_three_prompts(
        self, 
        linkedin_content: Dict[str, Any],
        aspect_ratio: str = "1:1"
    ) -> List[Dict[str, Any]]:
        """
        Generate three AI-optimized image prompts for LinkedIn content.
        
        Args:
            linkedin_content: LinkedIn content context (topic, industry, content_type, content)
            aspect_ratio: Desired image aspect ratio
            
        Returns:
            List of three prompt objects with style, prompt, and description
        """
        try:
            start_time = datetime.now()
            logger.info(f"Generating image prompts for LinkedIn content: {linkedin_content.get('topic', 'Unknown')}")
            
            # Generate prompts using Gemini
            prompts = await self._generate_prompts_with_gemini(linkedin_content, aspect_ratio)
            
            if not prompts or len(prompts) < 3:
                logger.warning("Gemini prompt generation failed, using fallback prompts")
                prompts = self._get_fallback_prompts(linkedin_content, aspect_ratio)
            
            # Ensure exactly 3 prompts
            prompts = prompts[:3]
            
            # Validate and enhance prompts
            enhanced_prompts = []
            for i, prompt in enumerate(prompts):
                enhanced_prompt = self._enhance_prompt_for_linkedin(
                    prompt, linkedin_content, aspect_ratio, i
                )
                enhanced_prompts.append(enhanced_prompt)
            
            generation_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"Generated {len(enhanced_prompts)} image prompts in {generation_time:.2f}s")
            
            return enhanced_prompts
            
        except Exception as e:
            logger.error(f"Error generating LinkedIn image prompts: {str(e)}")
            return self._get_fallback_prompts(linkedin_content, aspect_ratio)
    
    async def _generate_prompts_with_gemini(
        self, 
        linkedin_content: Dict[str, Any],
        aspect_ratio: str
    ) -> List[Dict[str, Any]]:
        """
        Generate image prompts using Gemini AI.
        
        Args:
            linkedin_content: LinkedIn content context
            aspect_ratio: Image aspect ratio
            
        Returns:
            List of generated prompts
        """
        try:
            # Build the prompt for Gemini
            gemini_prompt = self._build_gemini_prompt(linkedin_content, aspect_ratio)
            
            # Generate response using Gemini
            response = gemini_text_response(
                prompt=gemini_prompt,
                temperature=0.7,
                top_p=0.8,
                n=1,
                max_tokens=1000,
                system_prompt="You are an expert AI image prompt engineer specializing in LinkedIn content optimization."
            )
            
            if not response:
                logger.warning("No response from Gemini prompt generation")
                return []
            
            # Parse Gemini response into structured prompts
            prompts = self._parse_gemini_response(response, linkedin_content)
            
            return prompts
            
        except Exception as e:
            logger.error(f"Error in Gemini prompt generation: {str(e)}")
            return []
    
    def _build_gemini_prompt(
        self, 
        linkedin_content: Dict[str, Any],
        aspect_ratio: str
    ) -> str:
        """
        Build comprehensive prompt for Gemini to generate image prompts.
        
        Args:
            linkedin_content: LinkedIn content context
            aspect_ratio: Image aspect ratio
            
        Returns:
            Formatted prompt for Gemini
        """
        topic = linkedin_content.get('topic', 'business')
        industry = linkedin_content.get('industry', 'business')
        content_type = linkedin_content.get('content_type', 'post')
        content = linkedin_content.get('content', '')
        
        # Extract key content elements for better context
        content_analysis = self._analyze_content_for_image_context(content, content_type)
        
        prompt = f"""
        As an expert AI image prompt engineer specializing in LinkedIn content, generate 3 distinct image generation prompts for the following LinkedIn {content_type}:

        TOPIC: {topic}
        INDUSTRY: {industry}
        CONTENT TYPE: {content_type}
        ASPECT RATIO: {aspect_ratio}

        GENERATED CONTENT:
        {content}

        CONTENT ANALYSIS:
        - Key Themes: {content_analysis['key_themes']}
        - Tone: {content_analysis['tone']}
        - Visual Elements: {content_analysis['visual_elements']}
        - Target Audience: {content_analysis['target_audience']}
        - Content Purpose: {content_analysis['content_purpose']}

        Generate exactly 3 image prompts that directly relate to and enhance the generated content above:

        1. PROFESSIONAL STYLE:
        - Corporate aesthetics with clean lines and geometric shapes
        - Professional color palette (blues, grays, whites)
        - Modern business environment or abstract business concepts
        - Clean, minimalist design approach
        - Suitable for B2B and professional networking
        - MUST directly relate to the specific content themes and industry context above

        2. CREATIVE STYLE:
        - Eye-catching and engaging visual style
        - Vibrant colors while maintaining professional appeal
        - Creative composition that encourages social media engagement
        - Modern design elements with business context
        - Optimized for LinkedIn feed visibility
        - MUST visually represent the key themes and messages from the content above

        3. INDUSTRY-SPECIFIC STYLE:
        - Tailored specifically to the {industry} industry
        - Industry-relevant imagery, colors, and visual elements
        - Professional yet creative approach
        - Balanced design suitable for business audience
        - Industry-specific symbolism and aesthetics
        - MUST incorporate visual elements that directly support the content's industry context

        Each prompt should:
        - Be specific and detailed (50-100 words)
        - Include visual composition guidance
        - Specify color schemes and lighting
        - Mention LinkedIn optimization
        - Follow image generation best practices
        - Be suitable for the {aspect_ratio} aspect ratio
        - DIRECTLY reference and visualize the key themes, messages, and context from the generated content above
        - Create images that would naturally accompany and enhance the specific LinkedIn content provided

        Return the prompts in this exact JSON format:
        [
            {{
                "style": "Professional",
                "prompt": "Detailed prompt description that directly relates to the content above...",
                "description": "Brief description of the visual style and how it relates to the content"
            }},
            {{
                "style": "Creative", 
                "prompt": "Detailed prompt description that directly relates to the content above...",
                "description": "Brief description of the visual style and how it relates to the content"
            }},
            {{
                "style": "Industry-Specific",
                "prompt": "Detailed prompt description that directly relates to the content above...", 
                "description": "Brief description of the visual style and how it relates to the content"
            }}
        ]

        Focus on creating prompts that will generate high-quality, LinkedIn-optimized images that directly enhance and complement the specific content provided above.
        """
        
        return prompt.strip()
    
    def _analyze_content_for_image_context(self, content: str, content_type: str) -> Dict[str, Any]:
        """
        Analyze the generated LinkedIn content to extract key elements for image context.
        
        Args:
            content: The generated LinkedIn content
            content_type: Type of content (post, article, carousel, etc.)
            
        Returns:
            Dictionary containing content analysis for image generation
        """
        try:
            # Basic content analysis
            content_lower = content.lower()
            word_count = len(content.split())
            
            # Extract key themes based on content analysis
            key_themes = self._extract_key_themes(content_lower, content_type)
            
            # Determine tone based on content analysis
            tone = self._determine_content_tone(content_lower)
            
            # Identify visual elements that could be represented
            visual_elements = self._identify_visual_elements(content_lower, content_type)
            
            # Determine target audience
            target_audience = self._determine_target_audience(content_lower, content_type)
            
            # Determine content purpose
            content_purpose = self._determine_content_purpose(content_lower, content_type)
            
            return {
                'key_themes': ', '.join(key_themes),
                'tone': tone,
                'visual_elements': ', '.join(visual_elements),
                'target_audience': target_audience,
                'content_purpose': content_purpose,
                'word_count': word_count,
                'content_type': content_type
            }
            
        except Exception as e:
            logger.error(f"Error analyzing content for image context: {str(e)}")
            return {
                'key_themes': 'business, professional',
                'tone': 'professional',
                'visual_elements': 'business concepts',
                'target_audience': 'professionals',
                'content_purpose': 'informational',
                'word_count': len(content.split()) if content else 0,
                'content_type': content_type
            }
    
    def _extract_key_themes(self, content_lower: str, content_type: str) -> List[str]:
        """Extract key themes from the content for image generation context."""
        themes = []
        
        # Industry and business themes
        if any(word in content_lower for word in ['ai', 'artificial intelligence', 'machine learning']):
            themes.append('AI & Technology')
        if any(word in content_lower for word in ['marketing', 'branding', 'advertising']):
            themes.append('Marketing & Branding')
        if any(word in content_lower for word in ['leadership', 'management', 'strategy']):
            themes.append('Leadership & Strategy')
        if any(word in content_lower for word in ['innovation', 'growth', 'transformation']):
            themes.append('Innovation & Growth')
        if any(word in content_lower for word in ['data', 'analytics', 'insights']):
            themes.append('Data & Analytics')
        if any(word in content_lower for word in ['customer', 'user experience', 'engagement']):
            themes.append('Customer Experience')
        if any(word in content_lower for word in ['team', 'collaboration', 'workplace']):
            themes.append('Team & Collaboration')
        if any(word in content_lower for word in ['sustainability', 'environmental', 'green']):
            themes.append('Sustainability')
        if any(word in content_lower for word in ['finance', 'investment', 'economy']):
            themes.append('Finance & Economy')
        if any(word in content_lower for word in ['healthcare', 'medical', 'wellness']):
            themes.append('Healthcare & Wellness')
        
        # Content type specific themes
        if content_type == 'post':
            if any(word in content_lower for word in ['tip', 'advice', 'insight']):
                themes.append('Tips & Advice')
            if any(word in content_lower for word in ['story', 'experience', 'journey']):
                themes.append('Personal Story')
            if any(word in content_lower for word in ['trend', 'future', 'prediction']):
                themes.append('Trends & Future')
        
        elif content_type == 'article':
            if any(word in content_lower for word in ['research', 'study', 'analysis']):
                themes.append('Research & Analysis')
            if any(word in content_lower for word in ['case study', 'example', 'success']):
                themes.append('Case Studies')
            if any(word in content_lower for word in ['guide', 'tutorial', 'how-to']):
                themes.append('Educational Content')
        
        elif content_type == 'carousel':
            if any(word in content_lower for word in ['steps', 'process', 'framework']):
                themes.append('Process & Framework')
            if any(word in content_lower for word in ['comparison', 'vs', 'difference']):
                themes.append('Comparison & Analysis')
            if any(word in content_lower for word in ['checklist', 'tips', 'best practices']):
                themes.append('Checklists & Best Practices')
        
        # Default theme if none identified
        if not themes:
            themes.append('Business & Professional')
        
        return themes[:3]  # Limit to top 3 themes
    
    def _determine_content_tone(self, content_lower: str) -> str:
        """Determine the tone of the content for appropriate image styling."""
        if any(word in content_lower for word in ['excited', 'amazing', 'incredible', 'revolutionary']):
            return 'Enthusiastic & Dynamic'
        elif any(word in content_lower for word in ['challenge', 'problem', 'issue', 'difficult']):
            return 'Thoughtful & Analytical'
        elif any(word in content_lower for word in ['success', 'achievement', 'win', 'victory']):
            return 'Celebratory & Positive'
        elif any(word in content_lower for word in ['guide', 'tutorial', 'how-to', 'steps']):
            return 'Educational & Helpful'
        elif any(word in content_lower for word in ['trend', 'future', 'prediction', 'forecast']):
            return 'Forward-looking & Innovative'
        else:
            return 'Professional & Informative'
    
    def _identify_visual_elements(self, content_lower: str, content_type: str) -> List[str]:
        """Identify visual elements that could be represented in images."""
        visual_elements = []
        
        # Technology and digital elements
        if any(word in content_lower for word in ['ai', 'robot', 'computer', 'digital']):
            visual_elements.extend(['Digital interfaces', 'Technology symbols', 'Abstract tech patterns'])
        
        # Business and professional elements
        if any(word in content_lower for word in ['business', 'corporate', 'office', 'meeting']):
            visual_elements.extend(['Business environments', 'Professional settings', 'Corporate aesthetics'])
        
        # Growth and progress elements
        if any(word in content_lower for word in ['growth', 'progress', 'improvement', 'success']):
            visual_elements.extend(['Growth charts', 'Progress indicators', 'Success symbols'])
        
        # Data and analytics elements
        if any(word in content_lower for word in ['data', 'analytics', 'charts', 'metrics']):
            visual_elements.extend(['Data visualizations', 'Charts and graphs', 'Analytics dashboards'])
        
        # Team and collaboration elements
        if any(word in content_lower for word in ['team', 'collaboration', 'partnership', 'network']):
            visual_elements.extend(['Team dynamics', 'Collaboration symbols', 'Network connections'])
        
        # Industry-specific elements
        if 'healthcare' in content_lower:
            visual_elements.extend(['Medical symbols', 'Healthcare imagery', 'Wellness elements'])
        elif 'finance' in content_lower:
            visual_elements.extend(['Financial symbols', 'Money concepts', 'Investment imagery'])
        elif 'education' in content_lower:
            visual_elements.extend(['Learning symbols', 'Educational elements', 'Knowledge imagery'])
        
        # Default visual elements
        if not visual_elements:
            visual_elements = ['Professional business concepts', 'Modern design elements', 'Corporate aesthetics']
        
        return visual_elements[:4]  # Limit to top 4 elements
    
    def _determine_target_audience(self, content_lower: str, content_type: str) -> str:
        """Determine the target audience for the content."""
        if any(word in content_lower for word in ['ceo', 'executive', 'leader', 'manager']):
            return 'C-Suite & Executives'
        elif any(word in content_lower for word in ['entrepreneur', 'startup', 'founder', 'business owner']):
            return 'Entrepreneurs & Business Owners'
        elif any(word in content_lower for word in ['marketer', 'sales', 'business development']):
            return 'Marketing & Sales Professionals'
        elif any(word in content_lower for word in ['developer', 'engineer', 'technical', 'it']):
            return 'Technical Professionals'
        elif any(word in content_lower for word in ['student', 'learner', 'aspiring', 'career']):
            return 'Students & Career Changers'
        else:
            return 'General Business Professionals'
    
    def _determine_content_purpose(self, content_lower: str, content_type: str) -> str:
        """Determine the primary purpose of the content."""
        if any(word in content_lower for word in ['tip', 'advice', 'how-to', 'guide']):
            return 'Educational & Instructional'
        elif any(word in content_lower for word in ['story', 'experience', 'journey', 'case study']):
            return 'Storytelling & Experience Sharing'
        elif any(word in content_lower for word in ['trend', 'prediction', 'future', 'insight']):
            return 'Trend Analysis & Forecasting'
        elif any(word in content_lower for word in ['challenge', 'problem', 'solution', 'strategy']):
            return 'Problem Solving & Strategy'
        elif any(word in content_lower for word in ['success', 'achievement', 'result', 'outcome']):
            return 'Success Showcase & Results'
        else:
            return 'Informational & Awareness'
    
    def _parse_gemini_response(
        self, 
        response: str, 
        linkedin_content: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Parse Gemini response into structured prompt objects.
        
        Args:
            response: Raw response from Gemini
            linkedin_content: LinkedIn content context
            
        Returns:
            List of parsed prompt objects
        """
        try:
            # Try to extract JSON from response
            import json
            import re
            
            # Look for JSON array in the response
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                prompts = json.loads(json_str)
                
                # Validate prompt structure
                if isinstance(prompts, list) and len(prompts) >= 3:
                    return prompts[:3]
            
            # Fallback: parse response manually
            return self._parse_response_manually(response, linkedin_content)
            
        except Exception as e:
            logger.error(f"Error parsing Gemini response: {str(e)}")
            return self._parse_response_manually(response, linkedin_content)
    
    def _parse_response_manually(
        self, 
        response: str, 
        linkedin_content: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Manually parse response if JSON parsing fails.
        
        Args:
            response: Raw response from Gemini
            linkedin_content: LinkedIn content context
            
        Returns:
            List of parsed prompt objects
        """
        try:
            prompts = []
            lines = response.split('\n')
            
            current_style = None
            current_prompt = []
            current_description = None
            
            for line in lines:
                line = line.strip()
                
                if 'professional' in line.lower() and 'style' in line.lower():
                    if current_style and current_prompt:
                        prompts.append({
                            'style': current_style,
                            'prompt': ' '.join(current_prompt),
                            'description': current_description or f'{current_style} style for LinkedIn'
                        })
                    current_style = 'Professional'
                    current_prompt = []
                    current_description = None
                    
                elif 'creative' in line.lower() and 'style' in line.lower():
                    if current_style and current_prompt:
                        prompts.append({
                            'style': current_style,
                            'prompt': ' '.join(current_prompt),
                            'description': current_description or f'{current_style} style for LinkedIn'
                        })
                    current_style = 'Creative'
                    current_prompt = []
                    current_description = None
                    
                elif 'industry' in line.lower() and 'specific' in line.lower():
                    if current_style and current_prompt:
                        prompts.append({
                            'style': current_style,
                            'prompt': ' '.join(current_prompt),
                            'description': current_description or f'{current_style} style for LinkedIn'
                        })
                    current_style = 'Industry-Specific'
                    current_prompt = []
                    current_description = None
                    
                elif line and not line.startswith('-') and current_style:
                    current_prompt.append(line)
                    
                elif line.startswith('description:') and current_style:
                    current_description = line.replace('description:', '').strip()
            
            # Add the last prompt
            if current_style and current_prompt:
                prompts.append({
                    'style': current_style,
                    'prompt': ' '.join(current_prompt),
                    'description': current_description or f'{current_style} style for LinkedIn'
                })
            
            # Ensure we have exactly 3 prompts
            while len(prompts) < 3:
                style_name = ['Professional', 'Creative', 'Industry-Specific'][len(prompts)]
                prompts.append({
                    'style': style_name,
                    'prompt': f"Create a {style_name.lower()} LinkedIn image for {linkedin_content.get('topic', 'business')}",
                    'description': f'{style_name} style for LinkedIn content'
                })
            
            return prompts[:3]
            
        except Exception as e:
            logger.error(f"Error in manual response parsing: {str(e)}")
            return self._get_fallback_prompts(linkedin_content, "1:1")
    
    def _enhance_prompt_for_linkedin(
        self, 
        prompt: Dict[str, Any], 
        linkedin_content: Dict[str, Any],
        aspect_ratio: str,
        prompt_index: int
    ) -> Dict[str, Any]:
        """
        Enhance individual prompt with LinkedIn-specific optimizations.
        
        Args:
            prompt: Individual prompt object
            linkedin_content: LinkedIn content context
            aspect_ratio: Image aspect ratio
            prompt_index: Index of the prompt (0-2)
            
        Returns:
            Enhanced prompt object
        """
        try:
            topic = linkedin_content.get('topic', 'business')
            industry = linkedin_content.get('industry', 'business')
            content_type = linkedin_content.get('content_type', 'post')
            
            # Get the base prompt text
            base_prompt = prompt.get('prompt', '')
            style = prompt.get('style', 'Professional')
            
            # LinkedIn-specific enhancements based on style
            if style == 'Professional':
                enhancements = [
                    f"Professional LinkedIn {content_type} image for {topic}",
                    "Corporate aesthetics with clean lines and geometric shapes",
                    "Professional color palette (blues, grays, whites)",
                    "Modern business environment or abstract business concepts",
                    f"Aspect ratio: {aspect_ratio}",
                    "Mobile-optimized for LinkedIn feed viewing",
                    "High-quality, professional business aesthetic"
                ]
            elif style == 'Creative':
                enhancements = [
                    f"Creative LinkedIn {content_type} image for {topic}",
                    "Eye-catching and engaging visual style",
                    "Vibrant colors while maintaining professional appeal",
                    "Creative composition that encourages social media engagement",
                    f"Aspect ratio: {aspect_ratio}",
                    "Optimized for LinkedIn feed visibility and sharing",
                    "Modern design elements with business context"
                ]
            else:  # Industry-Specific
                enhancements = [
                    f"{industry} industry-specific LinkedIn {content_type} image for {topic}",
                    f"Industry-relevant imagery and colors for {industry}",
                    "Professional yet creative approach",
                    "Balanced design suitable for business audience",
                    f"Aspect ratio: {aspect_ratio}",
                    f"Industry-specific symbolism and {industry} aesthetics",
                    "Professional business appeal for LinkedIn"
                ]
            
            # Combine base prompt with enhancements
            enhanced_prompt_text = f"{base_prompt}\n\n"
            enhanced_prompt_text += "\n".join(enhancements)
            
            # Ensure prompt length is within limits
            if len(enhanced_prompt_text) > self.max_prompt_length:
                enhanced_prompt_text = enhanced_prompt_text[:self.max_prompt_length] + "..."
            
            return {
                'style': style,
                'prompt': enhanced_prompt_text,
                'description': prompt.get('description', f'{style} style for LinkedIn'),
                'prompt_index': prompt_index,
                'enhanced_at': datetime.now().isoformat(),
                'linkedin_optimized': True
            }
            
        except Exception as e:
            logger.error(f"Error enhancing prompt: {str(e)}")
            return prompt
    
    def _get_fallback_prompts(
        self, 
        linkedin_content: Dict[str, Any],
        aspect_ratio: str
    ) -> List[Dict[str, Any]]:
        """
        Generate fallback prompts if AI generation fails.
        
        Args:
            linkedin_content: LinkedIn content context
            aspect_ratio: Image aspect ratio
            
        Returns:
            List of fallback prompt objects
        """
        topic = linkedin_content.get('topic', 'business')
        industry = linkedin_content.get('industry', 'business')
        content_type = linkedin_content.get('content_type', 'post')
        content = linkedin_content.get('content', '')
        
        # Analyze content for better context
        content_analysis = self._analyze_content_for_image_context(content, content_type)
        
        # Create context-aware fallback prompts
        fallback_prompts = [
            {
                'style': 'Professional',
                'prompt': f"""Create a professional LinkedIn {content_type} image for {topic} in the {industry} industry.

Key Content Themes: {content_analysis['key_themes']}
Content Tone: {content_analysis['tone']}
Visual Elements: {content_analysis['visual_elements']}

Corporate aesthetics with clean lines and geometric shapes
Professional color palette (blues, grays, whites)
Modern business environment or abstract business concepts
Aspect ratio: {aspect_ratio}
Mobile-optimized for LinkedIn feed viewing
High-quality, professional business aesthetic
Directly represents the content themes: {content_analysis['key_themes']}""",
                'description': f'Clean, business-appropriate visual for LinkedIn {content_type} about {topic}',
                'prompt_index': 0,
                'fallback': True,
                'content_context': content_analysis
            },
            {
                'style': 'Creative',
                'prompt': f"""Generate a creative LinkedIn {content_type} image for {topic} in {industry}.

Key Content Themes: {content_analysis['key_themes']}
Content Purpose: {content_analysis['content_purpose']}
Target Audience: {content_analysis['target_audience']}

Eye-catching and engaging visual style
Vibrant colors while maintaining professional appeal
Creative composition that encourages social media engagement
Aspect ratio: {aspect_ratio}
Optimized for LinkedIn feed visibility and sharing
Modern design elements with business context
Visually represents: {content_analysis['visual_elements']}""",
                'description': f'Eye-catching, shareable design for LinkedIn {content_type} about {topic}',
                'prompt_index': 1,
                'fallback': True,
                'content_context': content_analysis
            },
            {
                'style': 'Industry-Specific',
                'prompt': f"""Design a {industry} industry-specific LinkedIn {content_type} image for {topic}.

Key Content Themes: {content_analysis['key_themes']}
Content Tone: {content_analysis['tone']}
Visual Elements: {content_analysis['visual_elements']}

Industry-relevant imagery and colors for {industry}
Professional yet creative approach
Balanced design suitable for business audience
Aspect ratio: {aspect_ratio}
Industry-specific symbolism and {industry} aesthetics
Professional business appeal for LinkedIn
Incorporates visual elements: {content_analysis['visual_elements']}""",
                'description': f'Industry-tailored professional design for {industry} {content_type} about {topic}',
                'prompt_index': 2,
                'fallback': True,
                'content_context': content_analysis
            }
        ]
        
        logger.info(f"Using context-aware fallback prompts for LinkedIn {content_type} about {topic}")
        return fallback_prompts
    
    async def validate_prompt_quality(
        self, 
        prompt: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate the quality of a generated prompt.
        
        Args:
            prompt: Prompt object to validate
            
        Returns:
            Validation results
        """
        try:
            prompt_text = prompt.get('prompt', '')
            style = prompt.get('style', '')
            
            # Quality metrics
            length_score = min(len(prompt_text) / 100, 1.0)  # Optimal length around 100 words
            specificity_score = self._calculate_specificity_score(prompt_text)
            linkedin_optimization_score = self._calculate_linkedin_optimization_score(prompt_text)
            
            # Overall quality score
            overall_score = (length_score + specificity_score + linkedin_optimization_score) / 3
            
            return {
                'valid': overall_score >= 0.7,
                'overall_score': round(overall_score, 2),
                'metrics': {
                    'length_score': round(length_score, 2),
                    'specificity_score': round(specificity_score, 2),
                    'linkedin_optimization_score': round(linkedin_optimization_score, 2)
                },
                'recommendations': self._get_quality_recommendations(overall_score, prompt_text)
            }
            
        except Exception as e:
            logger.error(f"Error validating prompt quality: {str(e)}")
            return {
                'valid': False,
                'overall_score': 0.0,
                'error': str(e)
            }
    
    def _calculate_specificity_score(self, prompt_text: str) -> float:
        """Calculate how specific and detailed the prompt is."""
        # Count specific visual elements, colors, styles mentioned
        specific_elements = [
            'wide-angle', 'close-up', 'low-angle', 'aerial',
            'blue', 'gray', 'white', 'red', 'green', 'yellow',
            'modern', 'minimalist', 'corporate', 'professional',
            'geometric', 'clean lines', 'sharp focus', 'soft lighting'
        ]
        
        element_count = sum(1 for element in specific_elements if element.lower() in prompt_text.lower())
        return min(element_count / 8, 1.0)  # Normalize to 0-1
    
    def _calculate_linkedin_optimization_score(self, prompt_text: str) -> float:
        """Calculate how well the prompt is optimized for LinkedIn."""
        linkedin_keywords = [
            'linkedin', 'professional', 'business', 'corporate',
            'mobile', 'feed', 'social media', 'engagement',
            'networking', 'professional audience'
        ]
        
        keyword_count = sum(1 for keyword in linkedin_keywords if keyword.lower() in prompt_text.lower())
        return min(keyword_count / 5, 1.0)  # Normalize to 0-1
    
    def _get_quality_recommendations(self, score: float, prompt_text: str) -> List[str]:
        """Get recommendations for improving prompt quality."""
        recommendations = []
        
        if score < 0.7:
            if len(prompt_text) < 100:
                recommendations.append("Add more specific visual details and composition guidance")
            
            if 'linkedin' not in prompt_text.lower():
                recommendations.append("Include LinkedIn-specific optimization terms")
            
            if 'aspect ratio' not in prompt_text.lower():
                recommendations.append("Specify the desired aspect ratio")
            
            if 'professional' not in prompt_text.lower() and 'business' not in prompt_text.lower():
                recommendations.append("Include professional business aesthetic guidance")
        
        return recommendations
