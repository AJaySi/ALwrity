"""
LLM-Powered SEO Insights Service for Phase 2A.2

Provides AI-powered insights and recommendations based on enterprise SEO audits
and GSC analysis using Claude/GPT LLM models with advanced prompt engineering.

Features:
- 8 specialized insight generation methods
- Dynamic prompt templates with context awareness
- Priority-scored recommendations
- Traffic improvement strategies
- Implementation guides and phasing
- Competitive intelligence synthesis
- Content gap analysis
- AI-driven traffic projections
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
import asyncio
import json
from loguru import logger

from services.llm_providers.main_text_generation import llm_text_gen


@dataclass
class AIInsight:
    """Data class for AI-generated insights"""
    title: str
    description: str
    priority_score: int  # 1-10
    estimated_traffic_impact: str
    implementation_difficulty: str  # easy, moderate, hard
    estimated_time_to_implement: str  # days, weeks, months
    steps: List[str]
    tools_required: List[str]
    expected_outcomes: List[str]
    business_impact: str


class LLMInsightsService:
    """
    Service for generating AI-powered SEO insights and recommendations
    using LLM models with specialized prompts for different analysis types.
    """
    
    def __init__(self):
        """Initialize the LLM insights service"""
        self.service_name = "llm_insights_generator"
        self.version = "1.0"
        self.model_preference = "claude"  # Claude for superior reasoning
        logger.info(f"Initialized {self.service_name} v{self.version}")
    
    # ============= AUDIT INSIGHTS =============
    
    async def generate_enterprise_audit_insights(
        self,
        audit_results: Dict[str, Any],
        website_url: str,
        target_keywords: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive AI insights from complete enterprise audit results.
        
        Args:
            audit_results: Full audit data from enterprise_seo_service
            website_url: The audited website
            target_keywords: Keywords from analysis
            
        Returns:
            AI-generated insights with priority scoring
        """
        try:
            logger.info(f"Generating enterprise audit insights for {website_url}")
            
            # Extract key metrics from audit
            overall_score = audit_results.get('overall_score', 0)
            component_scores = audit_results.get('component_scores', {})
            priority_actions = audit_results.get('priority_actions', [])
            
            # Build context for LLM
            context = self._build_audit_context(
                website_url, audit_results, target_keywords
            )
            
            # Generate insights prompt
            prompt = self._build_audit_insights_prompt(context, overall_score, component_scores)
            
            # Call LLM
            insights_json = await self._call_llm_for_json(
                prompt=prompt,
                context_type="enterprise_audit_insights"
            )
            
            # Parse and structure insights
            insights = self._parse_insights_response(insights_json)
            
            # Add metadata
            result = {
                'status': 'completed',
                'website_url': website_url,
                'audit_overall_score': overall_score,
                'insights_generated': len(insights),
                'insights': insights,
                'generated_at': datetime.utcnow().isoformat(),
                'summary': self._generate_summary(insights, overall_score)
            }
            
            logger.info(f"Generated {len(insights)} insights for {website_url}")
            return result
            
        except Exception as e:
            logger.error(f"Enterprise audit insights generation failed: {str(e)}", exc_info=True)
            raise
    
    # ============= GSC INSIGHTS =============
    
    async def generate_gsc_analysis_insights(
        self,
        gsc_analysis: Dict[str, Any],
        website_url: str
    ) -> Dict[str, Any]:
        """
        Generate strategic insights from GSC analysis with keyword opportunities.
        
        Args:
            gsc_analysis: Full GSC analysis data
            website_url: Website being analyzed
            
        Returns:
            Strategic GSC-specific insights
        """
        try:
            logger.info(f"Generating GSC analysis insights for {website_url}")
            
            # Extract key GSC metrics
            performance_overview = gsc_analysis.get('performance_overview', {})
            content_opportunities = gsc_analysis.get('content_opportunities', [])
            technical_insights = gsc_analysis.get('technical_insights', {})
            
            # Build GSC context
            context = self._build_gsc_context(gsc_analysis, website_url)
            
            # Generate insights prompt
            prompt = self._build_gsc_insights_prompt(
                context, 
                len(content_opportunities),
                performance_overview
            )
            
            # Call LLM
            insights_json = await self._call_llm_for_json(
                prompt=prompt,
                context_type="gsc_analysis_insights"
            )
            
            # Parse insights
            insights = self._parse_insights_response(insights_json)
            
            result = {
                'status': 'completed',
                'website_url': website_url,
                'total_content_opportunities': len(content_opportunities),
                'insights': insights,
                'generated_at': datetime.utcnow().isoformat(),
                'focus_areas': self._identify_gsc_focus_areas(insights)
            }
            
            logger.info(f"Generated {len(insights)} GSC insights")
            return result
            
        except Exception as e:
            logger.error(f"GSC analysis insights generation failed: {str(e)}", exc_info=True)
            raise
    
    # ============= CONTENT STRATEGY =============
    
    async def generate_content_strategy_insights(
        self,
        current_content: Dict[str, Any],
        content_gaps: List[str],
        target_keywords: List[str],
        competitor_content: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate strategic content recommendations based on gaps and keywords.
        
        Args:
            current_content: Existing content analysis
            content_gaps: Identified content gaps
            target_keywords: Target keywords for content
            competitor_content: Optional competitor content analysis
            
        Returns:
            Content strategy insights with phased plan
        """
        try:
            logger.info("Generating content strategy insights")
            
            # Build content strategy context
            context = self._build_content_strategy_context(
                current_content, content_gaps, target_keywords, competitor_content
            )
            
            # Generate strategy prompt
            prompt = self._build_content_strategy_prompt(context, len(content_gaps))
            
            # Call LLM
            strategy_json = await self._call_llm_for_json(
                prompt=prompt,
                context_type="content_strategy_insights"
            )
            
            # Parse strategy insights
            insights = self._parse_strategy_response(strategy_json)
            
            result = {
                'status': 'completed',
                'gaps_addressed': len(content_gaps),
                'strategy_insights': insights,
                'phased_roadmap': self._create_content_roadmap(insights),
                'generated_at': datetime.utcnow().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Content strategy generation failed: {str(e)}", exc_info=True)
            raise
    
    # ============= TRAFFIC ROADMAP =============
    
    async def generate_traffic_improvement_roadmap(
        self,
        current_metrics: Dict[str, Any],
        identified_opportunities: List[Dict[str, Any]],
        implementation_timeline_weeks: int = 12
    ) -> Dict[str, Any]:
        """
        Generate phased roadmap for traffic improvement with revenue impact.
        
        Args:
            current_metrics: Current traffic/conversion metrics
            identified_opportunities: List of improvement opportunities
            implementation_timeline_weeks: Timeline for implementation
            
        Returns:
            Phased roadmap with traffic projections
        """
        try:
            logger.info(f"Generating traffic roadmap for {implementation_timeline_weeks} weeks")
            
            # Build roadmap context
            context = self._build_roadmap_context(
                current_metrics, identified_opportunities, implementation_timeline_weeks
            )
            
            # Generate roadmap prompt
            prompt = self._build_roadmap_prompt(context)
            
            # Call LLM
            roadmap_json = await self._call_llm_for_json(
                prompt=prompt,
                context_type="traffic_roadmap"
            )
            
            # Parse and structure roadmap
            phases = self._parse_roadmap_response(roadmap_json)
            
            result = {
                'status': 'completed',
                'timeline_weeks': implementation_timeline_weeks,
                'current_traffic': current_metrics.get('organic_traffic', 0),
                'projected_traffic': self._calculate_projected_traffic(phases),
                'phases': phases,
                'generated_at': datetime.utcnow().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Traffic roadmap generation failed: {str(e)}", exc_info=True)
            raise
    
    # ============= COMPETITIVE INSIGHTS =============
    
    async def generate_competitive_insights(
        self,
        primary_site_analysis: Dict[str, Any],
        competitor_analyses: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate competitive positioning insights and gap analysis.
        
        Args:
            primary_site_analysis: Analysis of primary website
            competitor_analyses: List of competitor analyses
            
        Returns:
            Competitive positioning insights
        """
        try:
            logger.info(f"Generating competitive insights vs {len(competitor_analyses)} competitors")
            
            # Build competitive context
            context = self._build_competitive_context(
                primary_site_analysis, competitor_analyses
            )
            
            # Generate competitive prompt
            prompt = self._build_competitive_insights_prompt(context)
            
            # Call LLM
            competitive_json = await self._call_llm_for_json(
                prompt=prompt,
                context_type="competitive_insights"
            )
            
            # Parse competitive insights
            insights = self._parse_competitive_response(competitive_json)
            
            result = {
                'status': 'completed',
                'competitors_analyzed': len(competitor_analyses),
                'competitive_positioning': insights,
                'opportunities': self._identify_competitive_opportunities(insights),
                'threats': self._identify_competitive_threats(insights),
                'generated_at': datetime.utcnow().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Competitive insights generation failed: {str(e)}", exc_info=True)
            raise
    
    # ============= PRIORITIZED RECOMMENDATIONS =============
    
    async def generate_prioritized_recommendations(
        self,
        all_recommendations: List[Dict[str, Any]],
        business_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate AI-prioritized recommendations based on impact and effort.
        
        Args:
            all_recommendations: All raw recommendations
            business_context: Business goals and constraints
            
        Returns:
            Prioritized and scored recommendations
        """
        try:
            logger.info(f"Prioritizing {len(all_recommendations)} recommendations")
            
            # Build prioritization context
            context = self._build_prioritization_context(
                all_recommendations, business_context
            )
            
            # Generate prioritization prompt
            prompt = self._build_prioritization_prompt(context)
            
            # Call LLM
            prioritized_json = await self._call_llm_for_json(
                prompt=prompt,
                context_type="prioritized_recommendations"
            )
            
            # Parse prioritized recommendations
            recommendations = self._parse_prioritized_response(prioritized_json)
            
            result = {
                'status': 'completed',
                'total_recommendations': len(recommendations),
                'quick_wins': [r for r in recommendations if r.get('priority_score', 0) >= 8],
                'high_impact': [r for r in recommendations if 6 <= r.get('priority_score', 0) < 8],
                'long_term': [r for r in recommendations if r.get('priority_score', 0) < 6],
                'recommendations': recommendations,
                'generated_at': datetime.utcnow().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Recommendation prioritization failed: {str(e)}", exc_info=True)
            raise
    
    # ============= QUICK WINS =============
    
    async def generate_quick_wins(
        self,
        audit_data: Dict[str, Any],
        max_days_to_implement: int = 7
    ) -> Dict[str, Any]:
        """
        Identify quick wins - high-impact items implementable in short timeframe.
        
        Args:
            audit_data: Complete audit data
            max_days_to_implement: Maximum days for "quick win"
            
        Returns:
            List of quick wins with implementation guides
        """
        try:
            logger.info(f"Generating quick wins (max {max_days_to_implement} days)")
            
            # Build quick wins context
            context = self._build_quick_wins_context(audit_data, max_days_to_implement)
            
            # Generate quick wins prompt
            prompt = self._build_quick_wins_prompt(context)
            
            # Call LLM
            quick_wins_json = await self._call_llm_for_json(
                prompt=prompt,
                context_type="quick_wins"
            )
            
            # Parse quick wins
            wins = self._parse_quick_wins_response(quick_wins_json)
            
            result = {
                'status': 'completed',
                'quick_wins_identified': len(wins),
                'total_potential_traffic': sum(w.get('estimated_traffic_gain', 0) for w in wins),
                'quick_wins': wins,
                'implementation_order': self._order_quick_wins(wins),
                'generated_at': datetime.utcnow().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Quick wins generation failed: {str(e)}", exc_info=True)
            raise
    
    # ============= KEYWORD EXPANSION =============
    
    async def generate_keyword_expansion(
        self,
        current_keywords: List[str],
        content_analysis: Dict[str, Any],
        target_difficulty: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate keyword expansion recommendations with difficulty and volume.
        
        Args:
            current_keywords: Current target keywords
            content_analysis: Content analysis data
            target_difficulty: Preferred difficulty level (low, medium, high)
            
        Returns:
            Expanded keyword list with scoring
        """
        try:
            logger.info(f"Generating keyword expansion from {len(current_keywords)} keywords")
            
            # Build keyword expansion context
            context = self._build_keyword_context(
                current_keywords, content_analysis, target_difficulty
            )
            
            # Generate keyword expansion prompt
            prompt = self._build_keyword_expansion_prompt(context)
            
            # Call LLM
            keywords_json = await self._call_llm_for_json(
                prompt=prompt,
                context_type="keyword_expansion"
            )
            
            # Parse expanded keywords
            expanded = self._parse_keyword_response(keywords_json)
            
            result = {
                'status': 'completed',
                'original_keywords': len(current_keywords),
                'expanded_keywords': len(expanded),
                'new_keywords': expanded,
                'categorized_by_difficulty': self._categorize_by_difficulty(expanded),
                'generated_at': datetime.utcnow().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Keyword expansion generation failed: {str(e)}", exc_info=True)
            raise
    
    # ============= HELPER METHODS =============
    
    async def _call_llm_for_json(
        self,
        prompt: str,
        context_type: str,
        max_tokens: int = 2000
    ) -> str:
        """Call LLM and ensure JSON response"""
        try:
            # System prompt for JSON generation
            system_prompt = """You are an expert SEO strategist and data analyst. 
            Generate detailed, actionable JSON responses with specific metrics and recommendations.
            Ensure all responses are valid JSON that can be parsed."""
            
            # Call LLM with JSON-focused settings
            response = llm_text_gen(
                prompt=prompt,
                system_prompt=system_prompt,
                user_id=None,
                preferred_provider="claude",
                flow_type=f"seo_{context_type}",
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            # Extract JSON if wrapped in text
            if isinstance(response, str):
                # Try to find JSON in response
                import re
                json_match = re.search(r'\{[\s\S]*\}', response)
                if json_match:
                    return json_match.group(0)
            
            return response
            
        except Exception as e:
            logger.error(f"LLM call failed for {context_type}: {str(e)}")
            raise
    
    def _build_audit_context(
        self,
        website_url: str,
        audit_results: Dict[str, Any],
        keywords: Optional[List[str]]
    ) -> str:
        """Build context string for audit insights"""
        score = audit_results.get('overall_score', 0)
        status = "strong" if score >= 70 else "moderate" if score >= 50 else "needs improvement"
        
        return f"""
Website: {website_url}
Overall Audit Score: {score}/100 ({status})
Target Keywords: {', '.join(keywords) if keywords else 'Not specified'}
Components Analyzed: {list(audit_results.get('component_scores', {}).keys())}
Priority Actions: {len(audit_results.get('priority_actions', []))}
"""
    
    def _build_audit_insights_prompt(
        self,
        context: str,
        overall_score: float,
        component_scores: Dict[str, float]
    ) -> str:
        """Build prompt for audit insights generation"""
        return f"""Based on this SEO audit data:

{context}

Component Scores: {json.dumps(component_scores, indent=2)}

Generate 5-7 specific, actionable AI insights in JSON format:
{{
  "insights": [
    {{
      "title": "Insight Title",
      "description": "Detailed description of the insight",
      "priority_score": 8,
      "estimated_traffic_impact": "15-25%",
      "implementation_difficulty": "moderate",
      "estimated_time_weeks": 2,
      "steps": ["Step 1", "Step 2"],
      "tools_required": ["Tool1"],
      "expected_outcomes": ["Outcome1"]
    }}
  ],
  "summary": "Overall summary of insights"
}}"""
    
    def _build_gsc_insights_prompt(
        self,
        context: str,
        opportunities_count: int,
        performance: Dict[str, Any]
    ) -> str:
        """Build prompt for GSC insights"""
        return f"""Based on Google Search Console analysis:

{context}

Total Opportunities Identified: {opportunities_count}
Current Performance: {json.dumps(performance, indent=2)}

Generate strategic GSC insights in JSON format focusing on:
1. Quick fixes for high-volume keywords
2. Keywords ready to rank higher
3. Content expansion opportunities
4. Technical SEO issues

Return as JSON with same structure as audit insights."""
    
    def _parse_insights_response(self, response_json: str) -> List[Dict[str, Any]]:
        """Parse LLM response into insights"""
        try:
            data = json.loads(response_json)
            return data.get('insights', [])
        except:
            logger.warning("Could not parse insights response as JSON")
            return []
    
    def _generate_summary(
        self,
        insights: List[Dict[str, Any]],
        overall_score: float
    ) -> str:
        """Generate summary of insights"""
        if not insights:
            return "No insights generated"
        
        high_priority = sum(1 for i in insights if i.get('priority_score', 0) >= 8)
        return f"{high_priority} high-priority insights identified for score improvement from {overall_score}/100"
    
    def _build_gsc_context(
        self,
        gsc_analysis: Dict[str, Any],
        website_url: str
    ) -> str:
        """Build GSC context for insights"""
        perf = gsc_analysis.get('performance_overview', {})
        return f"""
Website: {website_url}
Total Keywords Tracked: {perf.get('total_keywords_tracked', 0)}
Total Pages Indexed: {perf.get('total_pages_indexed', 0)}
Overall CTR: {perf.get('overall_ctr', 0):.2f}%
Average Position: {perf.get('average_position', 0):.1f}
"""
    
    def _identify_gsc_focus_areas(self, insights: List[Dict[str, Any]]) -> List[str]:
        """Identify focus areas from GSC insights"""
        focus_areas = set()
        for insight in insights:
            if "meta" in insight.get('title', '').lower():
                focus_areas.add("Meta Tags Optimization")
            if "ranking" in insight.get('title', '').lower():
                focus_areas.add("Ranking Improvement")
            if "content" in insight.get('title', '').lower():
                focus_areas.add("Content Expansion")
        return list(focus_areas)
    
    def _build_content_strategy_context(
        self,
        current_content: Dict[str, Any],
        content_gaps: List[str],
        target_keywords: List[str],
        competitor_content: Optional[Dict[str, Any]]
    ) -> str:
        """Build content strategy context"""
        return f"""
Current Content Assets: {current_content.get('total_content', 0)} pieces
Content Gaps Identified: {len(content_gaps)}
Gaps: {', '.join(content_gaps[:5])}
Target Keywords: {', '.join(target_keywords)}
Competitor Content Items: {competitor_content.get('total_items', 0) if competitor_content else 'N/A'}
"""
    
    def _build_content_strategy_prompt(self, context: str, gap_count: int) -> str:
        """Build content strategy prompt"""
        return f"""Based on content analysis:

{context}

Create a 3-phase content strategy plan for addressing {gap_count} content gaps.
Return JSON with phases, specific content pieces, keywords per content, and expected traffic impact."""
    
    def _parse_strategy_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse strategy response"""
        try:
            return json.loads(response).get('strategy_insights', [])
        except:
            return []
    
    def _create_content_roadmap(self, insights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create phased content roadmap"""
        return [
            {"phase": 1, "items": insights[:len(insights)//3], "timeline": "Weeks 1-4"},
            {"phase": 2, "items": insights[len(insights)//3:2*len(insights)//3], "timeline": "Weeks 5-8"},
            {"phase": 3, "items": insights[2*len(insights)//3:], "timeline": "Weeks 9-12"}
        ]
    
    def _build_roadmap_context(
        self,
        current_metrics: Dict[str, Any],
        opportunities: List[Dict[str, Any]],
        timeline: int
    ) -> str:
        """Build roadmap context"""
        return f"""
Current Traffic: {current_metrics.get('organic_traffic', 0)} monthly visits
Conversion Rate: {current_metrics.get('conversion_rate', 0):.2f}%
Opportunities Identified: {len(opportunities)}
Implementation Timeline: {timeline} weeks
"""
    
    def _build_roadmap_prompt(self, context: str) -> str:
        """Build roadmap generation prompt"""
        return f"""Create a detailed traffic improvement roadmap:

{context}

Generate phases with:
- Specific actions
- Expected traffic gains
- Dependencies
- Resource requirements
- Success metrics

Return as JSON with phase details and projections."""
    
    def _parse_roadmap_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse roadmap response"""
        try:
            return json.loads(response).get('phases', [])
        except:
            return []
    
    def _calculate_projected_traffic(self, phases: List[Dict[str, Any]]) -> int:
        """Calculate total projected traffic from phases"""
        total = 0
        for phase in phases:
            if 'projected_traffic_gain' in phase:
                total += phase['projected_traffic_gain']
        return total
    
    def _build_competitive_context(
        self,
        primary: Dict[str, Any],
        competitors: List[Dict[str, Any]]
    ) -> str:
        """Build competitive analysis context"""
        return f"""
Primary Site Score: {primary.get('score', 0)}/100
Competitors: {len(competitors)}
Average Competitor Score: {sum(c.get('score', 0) for c in competitors) / len(competitors) if competitors else 0:.1f}/100
"""
    
    def _build_competitive_insights_prompt(self, context: str) -> str:
        """Build competitive insights prompt"""
        return f"""Analyze competitive positioning:

{context}

Identify:
1. Competitive advantages
2. Competitive gaps
3. Market opportunities
4. Threat areas

Return as JSON with detailed analysis."""
    
    def _parse_competitive_response(self, response: str) -> Dict[str, Any]:
        """Parse competitive response"""
        try:
            return json.loads(response)
        except:
            return {}
    
    def _identify_competitive_opportunities(self, insights: Dict[str, Any]) -> List[str]:
        """Extract competitive opportunities"""
        return insights.get('opportunities', [])
    
    def _identify_competitive_threats(self, insights: Dict[str, Any]) -> List[str]:
        """Extract competitive threats"""
        return insights.get('threats', [])
    
    def _build_prioritization_context(
        self,
        recommendations: List[Dict[str, Any]],
        business: Dict[str, Any]
    ) -> str:
        """Build prioritization context"""
        return f"""
Total Recommendations: {len(recommendations)}
Business Goals: {business.get('goals', [])}
Budget: {business.get('budget', 'Not specified')}
Timeline: {business.get('timeline', 'Not specified')}
"""
    
    def _build_prioritization_prompt(self, context: str) -> str:
        """Build prioritization prompt"""
        return f"""Prioritize recommendations by impact and effort:

{context}

Score each 1-10 on:
- Impact
- Effort required
- Timeline
- Business alignment

Return JSON with prioritized list and scoring."""
    
    def _parse_prioritized_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse prioritized recommendations"""
        try:
            return json.loads(response).get('recommendations', [])
        except:
            return []
    
    def _build_quick_wins_context(
        self,
        audit_data: Dict[str, Any],
        max_days: int
    ) -> str:
        """Build quick wins context"""
        return f"""
Maximum Days to Implement: {max_days}
Focus on:
- High traffic potential
- Low effort
- Clear ROI
- Quick implementation
"""
    
    def _build_quick_wins_prompt(self, context: str) -> str:
        """Build quick wins prompt"""
        return f"""Identify quick wins from audit:

{context}

Return JSON with wins ranked by (impact × effort) score."""
    
    def _parse_quick_wins_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse quick wins response"""
        try:
            return json.loads(response).get('quick_wins', [])
        except:
            return []
    
    def _order_quick_wins(self, wins: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Order quick wins by priority"""
        return sorted(wins, key=lambda x: x.get('priority_score', 0), reverse=True)
    
    def _build_keyword_context(
        self,
        keywords: List[str],
        content_analysis: Dict[str, Any],
        target_difficulty: Optional[str]
    ) -> str:
        """Build keyword expansion context"""
        return f"""
Current Keywords: {', '.join(keywords)}
Content Quality Score: {content_analysis.get('quality_score', 0)}/100
Target Difficulty: {target_difficulty or 'Mixed'}
"""
    
    def _build_keyword_expansion_prompt(self, context: str) -> str:
        """Build keyword expansion prompt"""
        return f"""Expand keyword list based on:

{context}

Suggest 15-20 related keywords with:
- Difficulty estimate
- Volume estimate
- Relevance to current keywords
- Content opportunity

Return as JSON."""
    
    def _parse_keyword_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse keyword response"""
        try:
            return json.loads(response).get('keywords', [])
        except:
            return []
    
    def _categorize_by_difficulty(self, keywords: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Categorize keywords by difficulty"""
        return {
            'easy': [k.get('keyword', '') for k in keywords if k.get('difficulty', 'medium') == 'low'],
            'medium': [k.get('keyword', '') for k in keywords if k.get('difficulty', 'medium') == 'medium'],
            'hard': [k.get('keyword', '') for k in keywords if k.get('difficulty', 'medium') == 'high']
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for LLM insights service"""
        return {
            'status': 'operational',
            'service': self.service_name,
            'version': self.version,
            'llm_integration': 'available',
            'last_check': datetime.utcnow().isoformat()
        }
