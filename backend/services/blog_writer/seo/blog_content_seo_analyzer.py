"""
Blog Content SEO Analyzer

Specialized SEO analyzer for blog content with parallel processing.
Leverages existing non-AI SEO tools and uses single AI prompt for structured analysis.
"""

import asyncio
import re
import textstat
from datetime import datetime
from typing import Dict, Any, List, Optional
from loguru import logger

from services.seo_analyzer import (
    ContentAnalyzer, KeywordAnalyzer, 
    URLStructureAnalyzer, AIInsightGenerator
)
from services.llm_providers.gemini_provider import gemini_structured_json_response


class BlogContentSEOAnalyzer:
    """Specialized SEO analyzer for blog content with parallel processing"""
    
    def __init__(self):
        """Initialize the blog content SEO analyzer"""
        self.content_analyzer = ContentAnalyzer()
        self.keyword_analyzer = KeywordAnalyzer()
        self.url_analyzer = URLStructureAnalyzer()
        self.ai_insights = AIInsightGenerator()
        self.gemini_provider = gemini_structured_json_response
        
        logger.info("BlogContentSEOAnalyzer initialized")
    
    async def analyze_blog_content(self, blog_content: str, research_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main analysis method with parallel processing
        
        Args:
            blog_content: The blog content to analyze
            research_data: Research data containing keywords and other insights
            
        Returns:
            Comprehensive SEO analysis results
        """
        try:
            logger.info("Starting blog content SEO analysis")
            
            # Extract keywords from research data
            keywords_data = self._extract_keywords_from_research(research_data)
            logger.info(f"Extracted keywords: {keywords_data}")
            
            # Phase 1: Run non-AI analyzers in parallel
            logger.info("Running non-AI analyzers in parallel")
            non_ai_results = await self._run_non_ai_analyzers(blog_content, keywords_data)
            
            # Phase 2: Single AI analysis for structured insights
            logger.info("Running AI analysis")
            ai_insights = await self._run_ai_analysis(blog_content, keywords_data, non_ai_results)
            
            # Phase 3: Compile and format results
            logger.info("Compiling results")
            results = self._compile_blog_seo_results(non_ai_results, ai_insights, keywords_data)
            
            logger.info(f"SEO analysis completed. Overall score: {results.get('overall_score', 0)}")
            return results
            
        except Exception as e:
            logger.error(f"Blog SEO analysis failed: {e}")
            # Fail fast - don't return fallback data
            raise e
    
    def _extract_keywords_from_research(self, research_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract keywords from research data"""
        try:
            logger.info(f"Extracting keywords from research data: {research_data}")
            
            # Extract keywords from research data structure
            keyword_analysis = research_data.get('keyword_analysis', {})
            logger.info(f"Found keyword_analysis: {keyword_analysis}")
            
            # Handle different possible structures
            primary_keywords = []
            long_tail_keywords = []
            semantic_keywords = []
            all_keywords = []
            
            # Try to extract primary keywords from different possible locations
            if 'primary' in keyword_analysis:
                primary_keywords = keyword_analysis.get('primary', [])
            elif 'keywords' in research_data:
                # Fallback to top-level keywords
                primary_keywords = research_data.get('keywords', [])
            
            # Extract other keyword types
            long_tail_keywords = keyword_analysis.get('long_tail', [])
            # Handle both 'semantic' and 'semantic_keywords' field names
            semantic_keywords = keyword_analysis.get('semantic', []) or keyword_analysis.get('semantic_keywords', [])
            all_keywords = keyword_analysis.get('all_keywords', primary_keywords)
            
            result = {
                'primary': primary_keywords,
                'long_tail': long_tail_keywords,
                'semantic': semantic_keywords,
                'all_keywords': all_keywords,
                'search_intent': keyword_analysis.get('search_intent', 'informational')
            }
            
            logger.info(f"Extracted keywords: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to extract keywords from research data: {e}")
            logger.error(f"Research data structure: {research_data}")
            # Fail fast - don't return empty keywords
            raise ValueError(f"Keyword extraction failed: {e}")
    
    async def _run_non_ai_analyzers(self, blog_content: str, keywords_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run all non-AI analyzers in parallel for maximum performance"""
        
        logger.info(f"Starting non-AI analyzers with content length: {len(blog_content)} chars")
        logger.info(f"Keywords data: {keywords_data}")
        
        # Parallel execution of fast analyzers
        tasks = [
            self._analyze_content_structure(blog_content),
            self._analyze_keyword_usage(blog_content, keywords_data),
            self._analyze_readability(blog_content),
            self._analyze_content_quality(blog_content),
            self._analyze_heading_structure(blog_content)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check for exceptions and fail fast
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                task_names = ['content_structure', 'keyword_analysis', 'readability_analysis', 'content_quality', 'heading_structure']
                logger.error(f"Task {task_names[i]} failed: {result}")
                raise result
        
        # Log successful results
        task_names = ['content_structure', 'keyword_analysis', 'readability_analysis', 'content_quality', 'heading_structure']
        for i, (name, result) in enumerate(zip(task_names, results)):
            logger.info(f"✅ {name} completed: {type(result).__name__} with {len(result) if isinstance(result, dict) else 'N/A'} fields")
        
        return {
            'content_structure': results[0],
            'keyword_analysis': results[1],
            'readability_analysis': results[2],
            'content_quality': results[3],
            'heading_structure': results[4]
        }
    
    async def _analyze_content_structure(self, content: str) -> Dict[str, Any]:
        """Analyze blog content structure"""
        try:
            # Parse markdown content
            lines = content.split('\n')
            
            # Count sections, paragraphs, sentences
            sections = len([line for line in lines if line.startswith('##')])
            paragraphs = len([line for line in lines if line.strip() and not line.startswith('#')])
            sentences = len(re.findall(r'[.!?]+', content))
            
            # Blog-specific structure analysis
            has_introduction = any('introduction' in line.lower() or 'overview' in line.lower() 
                                  for line in lines[:10])
            has_conclusion = any('conclusion' in line.lower() or 'summary' in line.lower() 
                                for line in lines[-10:])
            has_cta = any('call to action' in line.lower() or 'learn more' in line.lower() 
                          for line in lines)
            
            structure_score = self._calculate_structure_score(sections, paragraphs, has_introduction, has_conclusion)
            
            return {
                'total_sections': sections,
                'total_paragraphs': paragraphs,
                'total_sentences': sentences,
                'has_introduction': has_introduction,
                'has_conclusion': has_conclusion,
                'has_call_to_action': has_cta,
                'structure_score': structure_score,
                'recommendations': self._get_structure_recommendations(sections, has_introduction, has_conclusion)
            }
        except Exception as e:
            logger.error(f"Content structure analysis failed: {e}")
            raise e
    
    async def _analyze_keyword_usage(self, content: str, keywords_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze keyword usage and optimization"""
        try:
            # Extract keywords from research data
            primary_keywords = keywords_data.get('primary', [])
            long_tail_keywords = keywords_data.get('long_tail', [])
            semantic_keywords = keywords_data.get('semantic', [])
            
            # Use existing KeywordAnalyzer
            keyword_result = self.keyword_analyzer.analyze(content, primary_keywords)
            
            # Blog-specific keyword analysis
            keyword_analysis = {
                'primary_keywords': primary_keywords,
                'long_tail_keywords': long_tail_keywords,
                'semantic_keywords': semantic_keywords,
                'keyword_density': {},
                'keyword_distribution': {},
                'missing_keywords': [],
                'over_optimization': [],
                'recommendations': []
            }
            
            # Analyze each keyword type
            for keyword in primary_keywords:
                density = self._calculate_keyword_density(content, keyword)
                keyword_analysis['keyword_density'][keyword] = density
                
                # Check if keyword appears in headings
                in_headings = self._keyword_in_headings(content, keyword)
                keyword_analysis['keyword_distribution'][keyword] = {
                    'density': density,
                    'in_headings': in_headings,
                    'first_occurrence': content.lower().find(keyword.lower())
                }
            
            # Check for missing important keywords
            for keyword in primary_keywords:
                if keyword.lower() not in content.lower():
                    keyword_analysis['missing_keywords'].append(keyword)
            
            # Check for over-optimization
            for keyword, density in keyword_analysis['keyword_density'].items():
                if density > 3.0:  # Over 3% density
                    keyword_analysis['over_optimization'].append(keyword)
            
            return keyword_analysis
        except Exception as e:
            logger.error(f"Keyword analysis failed: {e}")
            raise e
    
    async def _analyze_readability(self, content: str) -> Dict[str, Any]:
        """Analyze content readability using textstat integration"""
        try:
            # Calculate readability metrics
            readability_metrics = {
                'flesch_reading_ease': textstat.flesch_reading_ease(content),
                'flesch_kincaid_grade': textstat.flesch_kincaid_grade(content),
                'gunning_fog': textstat.gunning_fog(content),
                'smog_index': textstat.smog_index(content),
                'automated_readability': textstat.automated_readability_index(content),
                'coleman_liau': textstat.coleman_liau_index(content)
            }
            
            # Blog-specific readability analysis
            avg_sentence_length = self._calculate_avg_sentence_length(content)
            avg_paragraph_length = self._calculate_avg_paragraph_length(content)
            
            readability_score = self._calculate_readability_score(readability_metrics)
            
            return {
                'metrics': readability_metrics,
                'avg_sentence_length': avg_sentence_length,
                'avg_paragraph_length': avg_paragraph_length,
                'readability_score': readability_score,
                'target_audience': self._determine_target_audience(readability_metrics),
                'recommendations': self._get_readability_recommendations(readability_metrics, avg_sentence_length)
            }
        except Exception as e:
            logger.error(f"Readability analysis failed: {e}")
            raise e
    
    async def _analyze_content_quality(self, content: str) -> Dict[str, Any]:
        """Analyze overall content quality"""
        try:
            # Word count analysis
            words = content.split()
            word_count = len(words)
            
            # Content depth analysis
            unique_words = len(set(word.lower() for word in words))
            vocabulary_diversity = unique_words / word_count if word_count > 0 else 0
            
            # Content flow analysis
            transition_words = ['however', 'therefore', 'furthermore', 'moreover', 'additionally', 'consequently']
            transition_count = sum(content.lower().count(word) for word in transition_words)
            
            content_depth_score = self._calculate_content_depth_score(word_count, vocabulary_diversity)
            flow_score = self._calculate_flow_score(transition_count, word_count)
            
            return {
                'word_count': word_count,
                'unique_words': unique_words,
                'vocabulary_diversity': vocabulary_diversity,
                'transition_words_used': transition_count,
                'content_depth_score': content_depth_score,
                'flow_score': flow_score,
                'recommendations': self._get_content_quality_recommendations(word_count, vocabulary_diversity, transition_count)
            }
        except Exception as e:
            logger.error(f"Content quality analysis failed: {e}")
            raise e
    
    async def _analyze_heading_structure(self, content: str) -> Dict[str, Any]:
        """Analyze heading structure and hierarchy"""
        try:
            # Extract headings
            h1_headings = re.findall(r'^# (.+)$', content, re.MULTILINE)
            h2_headings = re.findall(r'^## (.+)$', content, re.MULTILINE)
            h3_headings = re.findall(r'^### (.+)$', content, re.MULTILINE)
            
            # Analyze heading structure
            heading_hierarchy_score = self._calculate_heading_hierarchy_score(h1_headings, h2_headings, h3_headings)
            
            return {
                'h1_count': len(h1_headings),
                'h2_count': len(h2_headings),
                'h3_count': len(h3_headings),
                'h1_headings': h1_headings,
                'h2_headings': h2_headings,
                'h3_headings': h3_headings,
                'heading_hierarchy_score': heading_hierarchy_score,
                'recommendations': self._get_heading_recommendations(h1_headings, h2_headings, h3_headings)
            }
        except Exception as e:
            logger.error(f"Heading structure analysis failed: {e}")
            raise e
    
    # Helper methods for calculations and scoring
    def _calculate_structure_score(self, sections: int, paragraphs: int, has_intro: bool, has_conclusion: bool) -> int:
        """Calculate content structure score"""
        score = 0
        
        # Section count (optimal: 3-8 sections)
        if 3 <= sections <= 8:
            score += 30
        elif sections < 3:
            score += 15
        else:
            score += 20
        
        # Paragraph count (optimal: 8-20 paragraphs)
        if 8 <= paragraphs <= 20:
            score += 30
        elif paragraphs < 8:
            score += 15
        else:
            score += 20
        
        # Introduction and conclusion
        if has_intro:
            score += 20
        if has_conclusion:
            score += 20
        
        return min(score, 100)
    
    def _calculate_keyword_density(self, content: str, keyword: str) -> float:
        """Calculate keyword density percentage"""
        content_lower = content.lower()
        keyword_lower = keyword.lower()
        
        word_count = len(content.split())
        keyword_count = content_lower.count(keyword_lower)
        
        return (keyword_count / word_count * 100) if word_count > 0 else 0
    
    def _keyword_in_headings(self, content: str, keyword: str) -> bool:
        """Check if keyword appears in headings"""
        headings = re.findall(r'^#+ (.+)$', content, re.MULTILINE)
        return any(keyword.lower() in heading.lower() for heading in headings)
    
    def _calculate_avg_sentence_length(self, content: str) -> float:
        """Calculate average sentence length"""
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return 0
        
        total_words = sum(len(sentence.split()) for sentence in sentences)
        return total_words / len(sentences)
    
    def _calculate_avg_paragraph_length(self, content: str) -> float:
        """Calculate average paragraph length"""
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        if not paragraphs:
            return 0
        
        total_words = sum(len(paragraph.split()) for paragraph in paragraphs)
        return total_words / len(paragraphs)
    
    def _calculate_readability_score(self, metrics: Dict[str, float]) -> int:
        """Calculate overall readability score"""
        # Flesch Reading Ease (0-100, higher is better)
        flesch_score = metrics.get('flesch_reading_ease', 0)
        
        # Convert to 0-100 scale
        if flesch_score >= 80:
            return 90
        elif flesch_score >= 60:
            return 80
        elif flesch_score >= 40:
            return 70
        elif flesch_score >= 20:
            return 60
        else:
            return 50
    
    def _determine_target_audience(self, metrics: Dict[str, float]) -> str:
        """Determine target audience based on readability metrics"""
        flesch_score = metrics.get('flesch_reading_ease', 0)
        
        if flesch_score >= 80:
            return "General audience (8th grade level)"
        elif flesch_score >= 60:
            return "High school level"
        elif flesch_score >= 40:
            return "College level"
        else:
            return "Graduate level"
    
    def _calculate_content_depth_score(self, word_count: int, vocabulary_diversity: float) -> int:
        """Calculate content depth score"""
        score = 0
        
        # Word count (optimal: 800-2000 words)
        if 800 <= word_count <= 2000:
            score += 50
        elif word_count < 800:
            score += 30
        else:
            score += 40
        
        # Vocabulary diversity (optimal: 0.4-0.7)
        if 0.4 <= vocabulary_diversity <= 0.7:
            score += 50
        elif vocabulary_diversity < 0.4:
            score += 30
        else:
            score += 40
        
        return min(score, 100)
    
    def _calculate_flow_score(self, transition_count: int, word_count: int) -> int:
        """Calculate content flow score"""
        if word_count == 0:
            return 0
        
        transition_density = transition_count / (word_count / 100)
        
        # Optimal transition density: 1-3 per 100 words
        if 1 <= transition_density <= 3:
            return 90
        elif transition_density < 1:
            return 60
        else:
            return 70
    
    def _calculate_heading_hierarchy_score(self, h1: List[str], h2: List[str], h3: List[str]) -> int:
        """Calculate heading hierarchy score"""
        score = 0
        
        # Should have exactly 1 H1
        if len(h1) == 1:
            score += 40
        elif len(h1) == 0:
            score += 20
        else:
            score += 10
        
        # Should have 3-8 H2 headings
        if 3 <= len(h2) <= 8:
            score += 40
        elif len(h2) < 3:
            score += 20
        else:
            score += 30
        
        # H3 headings are optional but good for structure
        if len(h3) > 0:
            score += 20
        
        return min(score, 100)
    
    def _calculate_keyword_score(self, keyword_analysis: Dict[str, Any]) -> int:
        """Calculate keyword optimization score"""
        score = 0
        
        # Check keyword density (optimal: 1-3%)
        densities = keyword_analysis.get('keyword_density', {})
        for keyword, density in densities.items():
            if 1 <= density <= 3:
                score += 30
            elif density < 1:
                score += 15
            else:
                score += 10
        
        # Check keyword distribution
        distributions = keyword_analysis.get('keyword_distribution', {})
        for keyword, dist in distributions.items():
            if dist.get('in_headings', False):
                score += 20
            if dist.get('first_occurrence', -1) < 100:  # Early occurrence
                score += 20
        
        # Penalize missing keywords
        missing = len(keyword_analysis.get('missing_keywords', []))
        score -= missing * 10
        
        # Penalize over-optimization
        over_opt = len(keyword_analysis.get('over_optimization', []))
        score -= over_opt * 15
        
        return max(0, min(score, 100))
    
    def _calculate_weighted_score(self, scores: Dict[str, int]) -> int:
        """Calculate weighted overall score"""
        weights = {
            'structure': 0.2,
            'keywords': 0.25,
            'readability': 0.2,
            'quality': 0.15,
            'headings': 0.1,
            'ai_insights': 0.1
        }
        
        weighted_sum = sum(scores.get(key, 0) * weight for key, weight in weights.items())
        return int(weighted_sum)
    
    # Recommendation methods
    def _get_structure_recommendations(self, sections: int, has_intro: bool, has_conclusion: bool) -> List[str]:
        """Get structure recommendations"""
        recommendations = []
        
        if sections < 3:
            recommendations.append("Add more sections to improve content structure")
        elif sections > 8:
            recommendations.append("Consider combining some sections for better flow")
        
        if not has_intro:
            recommendations.append("Add an introduction section to set context")
        
        if not has_conclusion:
            recommendations.append("Add a conclusion section to summarize key points")
        
        return recommendations
    
    def _get_readability_recommendations(self, metrics: Dict[str, float], avg_sentence_length: float) -> List[str]:
        """Get readability recommendations"""
        recommendations = []
        
        flesch_score = metrics.get('flesch_reading_ease', 0)
        
        if flesch_score < 60:
            recommendations.append("Simplify language and use shorter sentences")
        
        if avg_sentence_length > 20:
            recommendations.append("Break down long sentences for better readability")
        
        if flesch_score > 80:
            recommendations.append("Consider adding more technical depth for expert audience")
        
        return recommendations
    
    def _get_content_quality_recommendations(self, word_count: int, vocabulary_diversity: float, transition_count: int) -> List[str]:
        """Get content quality recommendations"""
        recommendations = []
        
        if word_count < 800:
            recommendations.append("Expand content with more detailed explanations")
        elif word_count > 2000:
            recommendations.append("Consider breaking into multiple posts")
        
        if vocabulary_diversity < 0.4:
            recommendations.append("Use more varied vocabulary to improve engagement")
        
        if transition_count < 3:
            recommendations.append("Add more transition words to improve flow")
        
        return recommendations
    
    def _get_heading_recommendations(self, h1: List[str], h2: List[str], h3: List[str]) -> List[str]:
        """Get heading recommendations"""
        recommendations = []
        
        if len(h1) == 0:
            recommendations.append("Add a main H1 heading")
        elif len(h1) > 1:
            recommendations.append("Use only one H1 heading per post")
        
        if len(h2) < 3:
            recommendations.append("Add more H2 headings to structure content")
        elif len(h2) > 8:
            recommendations.append("Consider using H3 headings for better hierarchy")
        
        return recommendations
    
    async def _run_ai_analysis(self, blog_content: str, keywords_data: Dict[str, Any], non_ai_results: Dict[str, Any]) -> Dict[str, Any]:
        """Run single AI analysis for structured insights"""
        try:
            # Prepare context for AI analysis
            context = {
                'blog_content': blog_content,
                'keywords_data': keywords_data,
                'non_ai_results': non_ai_results
            }
            
            # Create AI prompt for structured analysis
            prompt = self._create_ai_analysis_prompt(context)
            
            # Get structured response from Gemini
            schema = {
                "type": "object",
                "properties": {
                    "content_quality_insights": {
                        "type": "object",
                        "properties": {
                            "engagement_score": {"type": "number"},
                            "value_proposition": {"type": "string"},
                            "content_gaps": {"type": "array", "items": {"type": "string"}},
                            "improvement_suggestions": {"type": "array", "items": {"type": "string"}}
                        }
                    },
                    "seo_optimization_insights": {
                        "type": "object",
                        "properties": {
                            "keyword_optimization": {"type": "string"},
                            "content_relevance": {"type": "string"},
                            "search_intent_alignment": {"type": "string"},
                            "seo_improvements": {"type": "array", "items": {"type": "string"}}
                        }
                    },
                    "user_experience_insights": {
                        "type": "object",
                        "properties": {
                            "content_flow": {"type": "string"},
                            "readability_assessment": {"type": "string"},
                            "engagement_factors": {"type": "array", "items": {"type": "string"}},
                            "ux_improvements": {"type": "array", "items": {"type": "string"}}
                        }
                    },
                    "competitive_analysis": {
                        "type": "object",
                        "properties": {
                            "content_differentiation": {"type": "string"},
                            "unique_value": {"type": "string"},
                            "competitive_advantages": {"type": "array", "items": {"type": "string"}},
                            "market_positioning": {"type": "string"}
                        }
                    }
                }
            }
            
            ai_response = self.gemini_provider(
                prompt=prompt,
                schema=schema,
                temperature=0.2,
                max_tokens=8192
            )
            
            return ai_response
            
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            # Fail fast - don't return mock data
            raise e
    
    def _create_ai_analysis_prompt(self, context: Dict[str, Any]) -> str:
        """Create AI analysis prompt"""
        blog_content = context['blog_content']
        keywords_data = context['keywords_data']
        non_ai_results = context['non_ai_results']
        
        prompt = f"""
        Analyze this blog content for SEO optimization and user experience. Provide structured insights based on the content and keyword data.

        BLOG CONTENT:
        {blog_content[:2000]}...

        KEYWORDS DATA:
        Primary Keywords: {keywords_data.get('primary', [])}
        Long-tail Keywords: {keywords_data.get('long_tail', [])}
        Semantic Keywords: {keywords_data.get('semantic', [])}
        Search Intent: {keywords_data.get('search_intent', 'informational')}

        NON-AI ANALYSIS RESULTS:
        Structure Score: {non_ai_results.get('content_structure', {}).get('structure_score', 0)}
        Readability Score: {non_ai_results.get('readability_analysis', {}).get('readability_score', 0)}
        Content Quality Score: {non_ai_results.get('content_quality', {}).get('content_depth_score', 0)}

        Please provide:
        1. Content Quality Insights: Assess engagement potential, value proposition, content gaps, and improvement suggestions
        2. SEO Optimization Insights: Evaluate keyword optimization, content relevance, search intent alignment, and SEO improvements
        3. User Experience Insights: Analyze content flow, readability, engagement factors, and UX improvements
        4. Competitive Analysis: Identify content differentiation, unique value, competitive advantages, and market positioning

        Focus on actionable insights that can improve the blog's performance and user engagement.
        """
        
        return prompt
    
    def _compile_blog_seo_results(self, non_ai_results: Dict[str, Any], ai_insights: Dict[str, Any], keywords_data: Dict[str, Any]) -> Dict[str, Any]:
        """Compile comprehensive SEO analysis results"""
        try:
            # Validate required data - fail fast if missing
            if not non_ai_results:
                raise ValueError("Non-AI analysis results are missing")
            
            if not ai_insights:
                raise ValueError("AI insights are missing")
            
            # Calculate category scores
            category_scores = {
                'structure': non_ai_results.get('content_structure', {}).get('structure_score', 0),
                'keywords': self._calculate_keyword_score(non_ai_results.get('keyword_analysis', {})),
                'readability': non_ai_results.get('readability_analysis', {}).get('readability_score', 0),
                'quality': non_ai_results.get('content_quality', {}).get('content_depth_score', 0),
                'headings': non_ai_results.get('heading_structure', {}).get('heading_hierarchy_score', 0),
                'ai_insights': ai_insights.get('content_quality_insights', {}).get('engagement_score', 0)
            }
            
            # Calculate overall score
            overall_score = self._calculate_weighted_score(category_scores)
            
            # Compile actionable recommendations
            actionable_recommendations = self._compile_actionable_recommendations(non_ai_results, ai_insights)
            
            # Create visualization data
            visualization_data = self._create_visualization_data(category_scores, non_ai_results)
            
            return {
                'overall_score': overall_score,
                'category_scores': category_scores,
                'detailed_analysis': non_ai_results,
                'ai_insights': ai_insights,
                'keywords_data': keywords_data,
                'visualization_data': visualization_data,
                'actionable_recommendations': actionable_recommendations,
                'generated_at': datetime.utcnow().isoformat(),
                'analysis_summary': self._create_analysis_summary(overall_score, category_scores, ai_insights)
            }
            
        except Exception as e:
            logger.error(f"Results compilation failed: {e}")
            # Fail fast - don't return fallback data
            raise e
    
    def _compile_actionable_recommendations(self, non_ai_results: Dict[str, Any], ai_insights: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Compile actionable recommendations from all sources"""
        recommendations = []
        
        # Structure recommendations
        structure_recs = non_ai_results.get('content_structure', {}).get('recommendations', [])
        for rec in structure_recs:
            recommendations.append({
                'category': 'Structure',
                'priority': 'High',
                'recommendation': rec,
                'impact': 'Improves content organization and user experience'
            })
        
        # Keyword recommendations
        keyword_recs = non_ai_results.get('keyword_analysis', {}).get('recommendations', [])
        for rec in keyword_recs:
            recommendations.append({
                'category': 'Keywords',
                'priority': 'High',
                'recommendation': rec,
                'impact': 'Improves search engine visibility'
            })
        
        # Readability recommendations
        readability_recs = non_ai_results.get('readability_analysis', {}).get('recommendations', [])
        for rec in readability_recs:
            recommendations.append({
                'category': 'Readability',
                'priority': 'Medium',
                'recommendation': rec,
                'impact': 'Improves user engagement and comprehension'
            })
        
        # AI insights recommendations
        ai_recs = ai_insights.get('content_quality_insights', {}).get('improvement_suggestions', [])
        for rec in ai_recs:
            recommendations.append({
                'category': 'Content Quality',
                'priority': 'Medium',
                'recommendation': rec,
                'impact': 'Enhances content value and engagement'
            })
        
        return recommendations
    
    def _create_visualization_data(self, category_scores: Dict[str, int], non_ai_results: Dict[str, Any]) -> Dict[str, Any]:
        """Create data for visualization components"""
        return {
            'score_radar': {
                'categories': list(category_scores.keys()),
                'scores': list(category_scores.values()),
                'max_score': 100
            },
            'keyword_analysis': {
                'densities': non_ai_results.get('keyword_analysis', {}).get('keyword_density', {}),
                'missing_keywords': non_ai_results.get('keyword_analysis', {}).get('missing_keywords', []),
                'over_optimization': non_ai_results.get('keyword_analysis', {}).get('over_optimization', [])
            },
            'readability_metrics': non_ai_results.get('readability_analysis', {}).get('metrics', {}),
            'content_stats': {
                'word_count': non_ai_results.get('content_quality', {}).get('word_count', 0),
                'sections': non_ai_results.get('content_structure', {}).get('total_sections', 0),
                'paragraphs': non_ai_results.get('content_structure', {}).get('total_paragraphs', 0)
            }
        }
    
    def _create_analysis_summary(self, overall_score: int, category_scores: Dict[str, int], ai_insights: Dict[str, Any]) -> Dict[str, Any]:
        """Create analysis summary"""
        # Determine overall grade
        if overall_score >= 90:
            grade = 'A'
            status = 'Excellent'
        elif overall_score >= 80:
            grade = 'B'
            status = 'Good'
        elif overall_score >= 70:
            grade = 'C'
            status = 'Fair'
        elif overall_score >= 60:
            grade = 'D'
            status = 'Needs Improvement'
        else:
            grade = 'F'
            status = 'Poor'
        
        # Find strongest and weakest categories
        strongest_category = max(category_scores.items(), key=lambda x: x[1])
        weakest_category = min(category_scores.items(), key=lambda x: x[1])
        
        return {
            'overall_grade': grade,
            'status': status,
            'strongest_category': strongest_category[0],
            'weakest_category': weakest_category[0],
            'key_strengths': self._identify_key_strengths(category_scores),
            'key_weaknesses': self._identify_key_weaknesses(category_scores),
            'ai_summary': ai_insights.get('content_quality_insights', {}).get('value_proposition', '')
        }
    
    def _identify_key_strengths(self, category_scores: Dict[str, int]) -> List[str]:
        """Identify key strengths"""
        strengths = []
        
        for category, score in category_scores.items():
            if score >= 80:
                strengths.append(f"Strong {category} optimization")
        
        return strengths
    
    def _identify_key_weaknesses(self, category_scores: Dict[str, int]) -> List[str]:
        """Identify key weaknesses"""
        weaknesses = []
        
        for category, score in category_scores.items():
            if score < 60:
                weaknesses.append(f"Needs improvement in {category}")
        
        return weaknesses
    
    def _create_error_result(self, error_message: str) -> Dict[str, Any]:
        """Create error result - this should not be used in fail-fast mode"""
        raise ValueError(f"Error result creation not allowed in fail-fast mode: {error_message}")
