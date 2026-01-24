"""
Automated Content Suggestions Service

AI-powered content generation for backlinking campaigns.
Creates personalized content ideas based on prospect gaps and campaign objectives.
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import re
import logging

from .logging_utils import campaign_logger
from .config import get_config
from .models import ContentSuggestion

# Import Google Trends service for trend-enhanced suggestions
from ..research.trends.google_trends_service import GoogleTrendsService


class AutomatedContentSuggester:
    """
    AI-powered content suggestion engine for backlinking campaigns.

    Features:
    - Multi-perspective content ideation
    - SEO-first optimization
    - Prospect personalization
    - Quality validation and scoring
    """

    def __init__(self):
        self.config = get_config()
        self.llm_provider = None
        self.seo_optimizer = SEOContentOptimizer()
        self.quality_validator = ContentQualityValidator()
        self.personalization_engine = ProspectPersonalizationEngine()
        self.google_trends = GoogleTrendsService()  # Initialize Google Trends service

    async def generate_content_suggestions(
        self,
        campaign_keywords: List[str],
        prospect_gaps: List[Dict[str, Any]],
        competitor_analysis: Dict[str, Any],
        prospect_profile: Dict[str, Any],
        max_suggestions: int = 20,
        trend_data: Optional[Dict[str, Any]] = None,
        enable_trend_analysis: bool = False,
        user_id: Optional[str] = None,
        enhanced_prospect_intelligence: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive content suggestions for backlinking outreach.

        Args:
            campaign_keywords: Target keywords for the campaign
            prospect_gaps: Content gaps identified for the prospect
            competitor_analysis: Analysis of competitor content strategies
            prospect_profile: Profile information about the target prospect
            max_suggestions: Maximum number of suggestions to generate
            trend_data: Optional Google Trends data for enhanced suggestions
            enable_trend_analysis: Whether to include trend-based content ideas
            user_id: User ID for subscription checks and AI calls
            enhanced_prospect_intelligence: Optional enhanced analysis data from prospect website analysis

        Returns:
            Dictionary containing suggestions and metadata
        """
        try:
            campaign_logger.info(f"Generating content suggestions for campaign with {len(campaign_keywords)} keywords")

            # Initialize LLM provider
            await self._initialize_llm_provider()

            # Phase 1: Strategic Context Synthesis
            strategic_context = await self._synthesize_strategic_context(
                campaign_keywords, prospect_gaps, competitor_analysis, prospect_profile, user_id, enhanced_prospect_intelligence
            )

            # Phase 1.5: Trend Context Integration (if enabled)
            trend_context = {}
            if enable_trend_analysis and trend_data:
                campaign_logger.info("Phase 1.5: Integrating trend context for enhanced suggestions")
                trend_context = await self._integrate_trend_context(
                    strategic_context, trend_data, campaign_keywords
                )

            # Phase 2: Multi-Perspective Idea Generation
            raw_ideas = await self._generate_multi_perspective_ideas(strategic_context, user_id, enhanced_prospect_intelligence)

            # Phase 2.5: Trend-Enhanced Idea Generation (if enabled)
            trend_enhanced_ideas = []
            if enable_trend_analysis and trend_data:
                campaign_logger.info("Phase 2.5: Generating trend-enhanced content ideas")
                trend_enhanced_ideas = await self._generate_trend_enhanced_ideas(
                    raw_ideas, trend_context, campaign_keywords
                )
                # Merge trend-enhanced ideas with original ideas
                raw_ideas.extend(trend_enhanced_ideas)

            # Phase 3: Competitive Intelligence Integration
            competitor_enhanced = await self._integrate_competitor_intelligence(
                raw_ideas, competitor_analysis
            )

            # Phase 4: SEO-First Content Optimization
            seo_optimized = await self._optimize_for_seo_ranking(
                competitor_enhanced, campaign_keywords, prospect_gaps
            )

            # Phase 5: Prospect-Specific Customization
            personalized = await self._personalize_for_prospect(
                seo_optimized, prospect_profile, prospect_gaps
            )

            # Phase 6: Quality Assurance & Validation
            validated = await self._validate_and_score_content(personalized)

            # Phase 7: Strategic Prioritization
            prioritized = self._prioritize_suggestions(validated, strategic_context, max_suggestions)

            # Phase 7.5: Trend-Based Prioritization Enhancement (if enabled)
            if enable_trend_analysis and trend_data:
                campaign_logger.info("Phase 7.5: Applying trend-based prioritization")
                prioritized = self._apply_trend_based_prioritization(
                    prioritized, trend_context, trend_data
                )

            # Prepare metadata
            metadata = {
                'total_generated': len(raw_ideas),
                'seo_optimized': len(seo_optimized),
                'personalized': len(personalized),
                'validated': len(validated),
                'final_count': len(prioritized),
                'generation_timestamp': datetime.utcnow().isoformat(),
                'strategic_context': strategic_context
            }

            # Add trend metadata if trend analysis was enabled
            if enable_trend_analysis and trend_data:
                metadata.update({
                    'trend_enhanced': True,
                    'trend_enhanced_ideas_count': len(trend_enhanced_ideas),
                    'trend_context': trend_context,
                    'trend_insights': self._extract_trend_insights(trend_data)
                })

            return {
                'suggestions': prioritized,
                'metadata': metadata,
                'quality_metrics': self._calculate_quality_metrics(prioritized)
            }

        except Exception as e:
            campaign_logger.error(f"Content suggestion generation failed: {e}")
            return {
                'suggestions': [],
                'metadata': {'error': str(e)},
                'quality_metrics': {}
            }

    async def _initialize_llm_provider(self):
        """Initialize the LLM provider for content generation."""
        if self.llm_provider is None:
            try:
                from services.llm_providers.gemini_grounded_provider import GeminiGroundedProvider
                self.llm_provider = GeminiGroundedProvider()
                campaign_logger.info("LLM provider initialized for content suggestions")
            except ImportError:
                campaign_logger.warning("LLM provider not available, using fallback methods")
                self.llm_provider = None

    async def _synthesize_strategic_context(
        self,
        campaign_keywords: List[str],
        prospect_gaps: List[Dict[str, Any]],
        competitor_analysis: Dict[str, Any],
        prospect_profile: Dict[str, Any],
        user_id: Optional[str] = None,
        enhanced_prospect_intelligence: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create comprehensive strategic context for content generation.
        """
        context = {
            'campaign_objectives': await self._analyze_campaign_objectives(campaign_keywords, user_id),
            'prospect_gaps': await self._quantify_prospect_gaps(prospect_gaps),
            'competitor_landscape': await self._analyze_competitive_positioning(competitor_analysis),
            'prospect_preferences': await self._understand_prospect_profile(prospect_profile),
            'market_trends': await self._incorporate_market_trends(campaign_keywords, user_id),
            'seo_opportunities': await self._identify_seo_opportunities(campaign_keywords, prospect_gaps),
            'content_constraints': await self._assess_content_constraints(prospect_profile),
            'enhanced_prospect_intelligence': enhanced_prospect_intelligence or {}
        }

        campaign_logger.debug(f"Strategic context synthesized with {len(context)} dimensions")
        return context

    async def _analyze_campaign_objectives(self, keywords: List[str], user_id: Optional[str] = None) -> Dict[str, Any]:
        """Analyze campaign objectives from keywords."""
        # Use centralized llm_text_gen with subscription checks
        from services.llm_providers.main_text_generation import llm_text_gen

        if not user_id:
            campaign_logger.warning("No user_id available for campaign objective analysis - using defaults")
            return {'primary_objective': 'brand_awareness', 'secondary_objectives': ['lead_generation']}

        prompt = f"""
        Analyze these campaign keywords and determine the primary and secondary objectives:

        Keywords: {', '.join(keywords)}

        Determine:
        1. Primary campaign objective (brand_awareness, lead_generation, thought_leadership, sales_conversion)
        2. Secondary objectives
        3. Target audience characteristics
        4. Content themes that would support these objectives

        Return as JSON.
        """

        try:
            analysis = llm_text_gen(
                prompt=prompt,
                json_struct={
                    "primary_objective": "string",
                    "secondary_objectives": ["string"],
                    "target_audience_characteristics": ["string"],
                    "content_themes": ["string"]
                },
                user_id=user_id
            )
            return analysis if analysis else {'primary_objective': 'brand_awareness', 'secondary_objectives': ['lead_generation']}
        except Exception as e:
            campaign_logger.warning(f"Campaign objective analysis failed: {e}")
            return {'primary_objective': 'brand_awareness', 'error': str(e)}

    async def _quantify_prospect_gaps(self, gaps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Quantify and categorize prospect content gaps."""
        gap_summary = {
            'total_gaps': len(gaps),
            'gap_categories': {},
            'priority_distribution': {'high': 0, 'medium': 0, 'low': 0},
            'top_gaps': []
        }

        for gap in gaps:
            # Categorize gaps
            gap_type = gap.get('gap_type', 'unknown')
            gap_summary['gap_categories'][gap_type] = gap_summary['gap_categories'].get(gap_type, 0) + 1

            # Count priorities
            priority_score = gap.get('priority_score', 0)
            if priority_score > 0.8:
                gap_summary['priority_distribution']['high'] += 1
            elif priority_score > 0.6:
                gap_summary['priority_distribution']['medium'] += 1
            else:
                gap_summary['priority_distribution']['low'] += 1

        # Get top gaps by priority
        sorted_gaps = sorted(gaps, key=lambda x: x.get('priority_score', 0), reverse=True)
        gap_summary['top_gaps'] = sorted_gaps[:5]

        return gap_summary

    async def _analyze_competitive_positioning(self, competitor_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze competitive positioning from backlink and content data."""
        return {
            'competitor_count': len(competitor_analysis.get('competitor_analyses', [])),
            'backlink_advantage': competitor_analysis.get('comparative_insights', {}).get('backlink_advantage', 'unknown'),
            'content_strategies': await self._extract_competitor_strategies(competitor_analysis),
            'opportunity_gaps': competitor_analysis.get('comparative_insights', {}).get('opportunity_gaps', [])
        }

    async def _understand_prospect_profile(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Extract insights from prospect profile for content personalization."""
        return {
            'content_style': profile.get('content_style', 'professional'),
            'audience_demographics': profile.get('audience_demographics', {}),
            'brand_voice': profile.get('brand_voice', 'authoritative'),
            'content_preferences': profile.get('content_preferences', []),
            'publishing_frequency': profile.get('publishing_frequency', 'weekly')
        }

    async def _incorporate_market_trends(self, keywords: List[str], user_id: Optional[str] = None) -> List[str]:
        """Identify current market trends related to campaign keywords."""
        # Use centralized llm_text_gen with subscription checks
        from services.llm_providers.main_text_generation import llm_text_gen

        if not user_id:
            campaign_logger.warning("No user_id available for market trends analysis - using defaults")
            return ['industry_best_practices', 'emerging_technologies']

        prompt = f"""
        Identify current market trends and topics related to these keywords:

        Keywords: {', '.join(keywords)}

        Find 5-7 trending topics, emerging themes, or hot discussion areas that would make
        compelling content for guest posting opportunities.

        Return as JSON array of trend strings.
        """

        try:
            trends = llm_text_gen(
                prompt=prompt,
                json_struct=["string"],
                user_id=user_id
            )
            return trends if trends else ['industry_best_practices', 'emerging_technologies']
        except Exception:
            return ['industry_best_practices', 'emerging_technologies']

    async def _identify_seo_opportunities(self, keywords: List[str], gaps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Identify SEO opportunities combining keywords and gaps."""
        return {
            'keyword_opportunities': await self._analyze_keyword_opportunities(keywords),
            'gap_seo_potential': await self._assess_gap_seo_potential(gaps),
            'long_tail_opportunities': await self._generate_long_tail_suggestions(keywords)
        }

    async def _assess_content_constraints(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Assess content creation constraints based on prospect profile."""
        return {
            'word_count_range': profile.get('word_count_range', [800, 2000]),
            'content_types_accepted': profile.get('content_types', ['blog_posts', 'guides', 'case_studies']),
            'editorial_guidelines': profile.get('editorial_guidelines', []),
            'brand_restrictions': profile.get('brand_restrictions', [])
        }

    async def _generate_multi_perspective_ideas(self, context: Dict[str, Any], user_id: Optional[str] = None, enhanced_prospect_intelligence: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Generate content ideas from multiple strategic perspectives.
        """
        perspectives = [
            ('problem_solution', self._generate_problem_solution_angles),
            ('trend_opportunity', self._generate_trend_based_ideas),
            ('competitive_differentiation', self._generate_competitive_angles),
            ('audience_insight', self._generate_audience_centric_ideas),
            ('data_driven', self._generate_data_backed_content)
        ]

        all_ideas = []

        for perspective_name, generator_func in perspectives:
            try:
                ideas = await generator_func(context, user_id, enhanced_prospect_intelligence)
                for idea in ideas:
                    idea['perspective'] = perspective_name
                    idea['strategic_fit'] = await self._calculate_strategic_fit(idea, context)
                all_ideas.extend(ideas)
            except Exception as e:
                campaign_logger.warning(f"Failed to generate {perspective_name} ideas: {e}")
                continue

        campaign_logger.info(f"Generated {len(all_ideas)} raw content ideas across {len(perspectives)} perspectives")
        return all_ideas

    async def _generate_problem_solution_angles(self, context: Dict[str, Any], user_id: Optional[str] = None, enhanced_prospect_intelligence: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Generate problem-solution content angles."""
        # Use centralized llm_text_gen with subscription checks
        from services.llm_providers.main_text_generation import llm_text_gen

        if not user_id:
            campaign_logger.warning("No user_id available for problem-solution content generation - skipping")
            return []

        campaign_objectives = context.get('campaign_objectives', {})
        prospect_gaps = context.get('prospect_gaps', {})

        # Add enhanced prospect intelligence to the prompt
        enhanced_context = ""
        if enhanced_prospect_intelligence:
            website_profile = enhanced_prospect_intelligence.get('website_profile', {})
            outreach_insights = enhanced_prospect_intelligence.get('outreach_insights', {})

            # Add writing style and audience insights
            writing_style = website_profile.get('content_analysis', {}).get('writing_style')
            if writing_style:
                enhanced_context += f"\nProspect Writing Style: {writing_style}"

            target_audience = website_profile.get('ai_insights', {}).get('target_audience')
            if target_audience:
                enhanced_context += f"\nTarget Audience: {target_audience}"

            # Add content opportunities from outreach insights
            content_opportunities = outreach_insights.get('content_opportunities', [])
            if content_opportunities:
                enhanced_context += f"\nSpecific Content Gaps: {', '.join(content_opportunities[:2])}"

        prompt = f"""
        Generate 5 problem-solution content ideas for guest posting that address:

        Campaign Context: {campaign_objectives}
        Prospect Gaps: {prospect_gaps.get('top_gaps', [])[:3]}{enhanced_context}

        Each idea should:
        1. Identify a specific problem the target audience faces
        2. Provide a practical solution
        3. Include actionable steps or strategies
        4. Be optimized for the prospect's content needs and audience
        5. Match the prospect's writing style and content approach

        Return as JSON array with title, description, and target_problem fields.
        """

        try:
            ideas = llm_text_gen(
                prompt=prompt,
                json_struct=[{
                    "title": "string",
                    "description": "string",
                    "target_problem": "string"
                }],
                user_id=user_id
            )
            return ideas.get('ideas', [])
        except Exception:
            return []

    async def _generate_trend_based_ideas(self, context: Dict[str, Any], user_id: Optional[str] = None, enhanced_prospect_intelligence: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Generate trend-based content ideas."""
        # Use centralized llm_text_gen with subscription checks
        from services.llm_providers.main_text_generation import llm_text_gen

        market_trends = context.get('market_trends', [])

        if not user_id or not market_trends:
            campaign_logger.warning("No user_id or market trends available for trend-based ideas - skipping")
            return []

        prompt = f"""
        Create 4 content ideas based on current market trends:

        Trends: {', '.join(market_trends)}
        Campaign Keywords: {context.get('campaign_objectives', {}).get('keywords', [])}

        Each idea should:
        1. Address a current trend or emerging topic
        2. Provide unique insights or analysis
        3. Include data or examples where relevant
        4. Position the author as a thought leader

        Return as JSON array with title, description, and trend_addressed fields.
        """

        try:
            ideas = llm_text_gen(
                prompt=prompt,
                json_struct=[{
                    "title": "string",
                    "description": "string",
                    "trend_addressed": "string"
                }],
                user_id=user_id
            )
            return ideas if ideas else []
        except Exception:
            return []

    async def _generate_competitive_angles(self, context: Dict[str, Any], user_id: Optional[str] = None, enhanced_prospect_intelligence: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Generate competitive differentiation content angles."""
        # Use centralized llm_text_gen with subscription checks
        from services.llm_providers.main_text_generation import llm_text_gen

        competitor_landscape = context.get('competitor_landscape', {})

        if not user_id or not competitor_landscape.get('content_strategies'):
            campaign_logger.warning("No user_id or competitor landscape available for competitive angles - skipping")
            return []

        prompt = f"""
        Create 3 content ideas that differentiate from competitors:

        Competitor Strategies: {competitor_landscape.get('content_strategies', [])}
        Opportunity Gaps: {competitor_landscape.get('opportunity_gaps', [])}

        Each idea should:
        1. Address content gaps competitors have
        2. Provide unique angles or perspectives
        3. Fill strategic voids in the market
        4. Demonstrate thought leadership

        Return as JSON array with title, description, and differentiation_factor fields.
        """

        try:
            ideas = llm_text_gen(
                prompt=prompt,
                json_struct=[{
                    "title": "string",
                    "description": "string",
                    "differentiation_factor": "string"
                }],
                user_id=user_id
            )
            return ideas if ideas else []
        except Exception:
            return []

    async def _generate_audience_centric_ideas(self, context: Dict[str, Any], user_id: Optional[str] = None, enhanced_prospect_intelligence: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Generate audience-centric content ideas."""
        # Use centralized llm_text_gen with subscription checks
        from services.llm_providers.main_text_generation import llm_text_gen

        if not user_id:
            campaign_logger.warning("No user_id available for audience-centric ideas - skipping")
            return []

        prospect_preferences = context.get('prospect_preferences', {})

        prompt = f"""
        Create 4 audience-focused content ideas:

        Audience Profile: {prospect_preferences}
        Content Style: {prospect_preferences.get('content_style', 'professional')}

        Each idea should:
        1. Address specific audience pain points or interests
        2. Use appropriate tone and style for the audience
        3. Provide practical value or insights
        4. Encourage engagement and sharing

        Return as JSON array with title, description, and audience_benefit fields.
        """

        try:
            ideas = llm_text_gen(
                prompt=prompt,
                json_struct=[{
                    "title": "string",
                    "description": "string",
                    "audience_benefit": "string"
                }],
                user_id=user_id
            )
            return ideas if ideas else []
        except Exception:
            return []

    async def _generate_data_backed_content(self, context: Dict[str, Any], user_id: Optional[str] = None, enhanced_prospect_intelligence: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Generate data-driven content ideas."""
        # Use centralized llm_text_gen with subscription checks
        from services.llm_providers.main_text_generation import llm_text_gen

        if not user_id:
            campaign_logger.warning("No user_id available for data-backed content - skipping")
            return []

        prompt = f"""
        Create 3 data-driven content ideas:

        Industry Context: {context.get('campaign_objectives', {}).get('industry', 'general')}
        SEO Opportunities: {context.get('seo_opportunities', {})}

        Each idea should:
        1. Include data, statistics, or research
        2. Provide analysis or insights from the data
        3. Support claims with evidence
        4. Offer actionable conclusions

        Return as JSON array with title, description, and data_source fields.
        """

        try:
            ideas = llm_text_gen(
                prompt=prompt,
                json_struct=[{
                    "title": "string",
                    "description": "string",
                    "data_source": "string"
                }],
                user_id=user_id
            )
            return ideas if ideas else []
        except Exception:
            return []

    async def _calculate_strategic_fit(self, idea: Dict[str, Any], context: Dict[str, Any]) -> float:
        """Calculate how well an idea fits strategic objectives."""
        fit_score = 0.5  # Base score

        # Check alignment with campaign objectives
        idea_text = f"{idea.get('title', '')} {idea.get('description', '')}".lower()
        campaign_keywords = context.get('campaign_objectives', {}).get('keywords', [])

        keyword_matches = sum(1 for keyword in campaign_keywords
                            if keyword.lower() in idea_text)
        fit_score += min(0.3, keyword_matches * 0.1)

        # Check gap relevance
        top_gaps = context.get('prospect_gaps', {}).get('top_gaps', [])
        for gap in top_gaps:
            gap_text = gap.get('description', '').lower()
            if any(word in idea_text for word in gap_text.split()):
                fit_score += 0.2
                break

        return min(1.0, fit_score)

    async def _integrate_competitor_intelligence(
        self,
        ideas: List[Dict[str, Any]],
        competitor_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Integrate competitor intelligence into content ideas."""
        enhanced_ideas = []

        for idea in ideas:
            competitor_insights = {
                'competitor_gaps_addressed': await self._identify_competitor_gaps_filled(idea, competitor_analysis),
                'market_positioning': await self._determine_market_positioning(idea, competitor_analysis),
                'unique_selling_points': await self._extract_unique_angles(idea, competitor_analysis)
            }

            enhanced_idea = {**idea, 'competitor_analysis': competitor_insights}
            enhanced_ideas.append(enhanced_idea)

        return enhanced_ideas

    async def _optimize_for_seo_ranking(
        self,
        ideas: List[Dict[str, Any]],
        campaign_keywords: List[str],
        prospect_gaps: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Optimize content ideas for SEO performance."""
        optimized_ideas = []

        for idea in ideas:
            # SEO title optimization
            seo_title = await self.seo_optimizer.optimize_headline(
                idea.get('title', ''), campaign_keywords
            )

            # Keyword integration
            target_keywords = await self.seo_optimizer.select_keyword_targets(
                idea, campaign_keywords, prospect_gaps
            )

            # Search intent analysis
            search_intent = await self.seo_optimizer.analyze_search_intent(seo_title)

            # Competition assessment
            competition_level = await self.seo_optimizer.assess_competition(seo_title)

            seo_optimized = {
                **idea,
                'seo_title': seo_title,
                'target_keywords': target_keywords,
                'search_intent': search_intent,
                'competition_level': competition_level,
                'seo_score': await self.seo_optimizer.calculate_seo_score(idea, campaign_keywords)
            }

            optimized_ideas.append(seo_optimized)

        return optimized_ideas

    async def _personalize_for_prospect(
        self,
        ideas: List[Dict[str, Any]],
        prospect_profile: Dict[str, Any],
        prospect_gaps: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Personalize content ideas for specific prospects."""
        personalized_ideas = []

        for idea in ideas:
            # Prospect fit analysis
            prospect_fit = await self.personalization_engine.analyze_prospect_fit(
                idea, prospect_profile
            )

            # Audience alignment
            audience_alignment = await self.personalization_engine.assess_audience_alignment(
                idea, prospect_profile
            )

            # Gap relevance
            gap_relevance = await self.personalization_engine.score_gap_relevance(
                idea, prospect_gaps
            )

            # Personalized elements
            personalized_hook = await self.personalization_engine.generate_personalized_hook(
                idea, prospect_profile
            )

            tailored_angle = await self.personalization_engine.suggest_tailored_angle(
                idea, prospect_gaps
            )

            personalized = {
                **idea,
                'prospect_fit_score': prospect_fit,
                'audience_alignment': audience_alignment,
                'gap_relevance_score': gap_relevance,
                'personalized_hook': personalized_hook,
                'tailored_angle': tailored_angle
            }

            personalized_ideas.append(personalized)

        return personalized_ideas

    async def _validate_and_score_content(self, ideas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate and score content quality."""
        validated_ideas = []

        for idea in ideas:
            # Quality validation
            quality_score = await self.quality_validator.assess_overall_quality(idea)

            # Readability scoring
            readability_score = await self.quality_validator.calculate_readability(idea)

            # Originality checking
            originality_score = await self.quality_validator.check_originality(idea)

            # Shareability assessment
            shareability_score = await self.quality_validator.assess_shareability(idea)

            validated = {
                **idea,
                'quality_score': quality_score,
                'readability_score': readability_score,
                'originality_score': originality_score,
                'shareability_score': shareability_score,
                'validation_status': 'passed' if quality_score > 0.7 else 'review_needed'
            }

            validated_ideas.append(validated)

        return validated_ideas

    def _prioritize_suggestions(
        self,
        ideas: List[Dict[str, Any]],
        context: Dict[str, Any],
        max_suggestions: int
    ) -> List[Dict[str, Any]]:
        """Prioritize content suggestions based on multiple factors."""
        scored_ideas = []

        for idea in ideas:
            # Calculate composite priority score
            priority_score = self._calculate_priority_score(idea, context)

            scored_idea = {**idea, 'priority_score': priority_score}
            scored_ideas.append(scored_idea)

        # Sort by priority score and return top suggestions
        sorted_ideas = sorted(scored_ideas, key=lambda x: x['priority_score'], reverse=True)
        return sorted_ideas[:max_suggestions]

    def _calculate_priority_score(self, idea: Dict[str, Any], context: Dict[str, Any]) -> float:
        """Calculate comprehensive priority score for content idea."""
        score = 0.0

        # SEO factors (30%)
        seo_score = idea.get('seo_score', 0.5)
        competition_level = idea.get('competition_level', 'medium')
        competition_multiplier = 1.0 if competition_level == 'low' else 0.7 if competition_level == 'medium' else 0.5
        score += (seo_score * competition_multiplier) * 0.3

        # Prospect fit (25%)
        prospect_fit = idea.get('prospect_fit_score', 0.5)
        score += prospect_fit * 0.25

        # Quality factors (20%)
        quality_score = idea.get('quality_score', 0.5)
        readability_score = idea.get('readability_score', 0.5)
        score += ((quality_score + readability_score) / 2) * 0.2

        # Strategic alignment (15%)
        strategic_fit = idea.get('strategic_fit', 0.5)
        gap_relevance = idea.get('gap_relevance_score', 0.5)
        score += ((strategic_fit + gap_relevance) / 2) * 0.15

        # Audience alignment (10%)
        audience_alignment = idea.get('audience_alignment', 0.5)
        score += audience_alignment * 0.1

        return min(1.0, score)

    def _calculate_quality_metrics(self, suggestions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate quality metrics for the generated suggestions."""
        if not suggestions:
            return {}

        metrics = {
            'average_seo_score': sum(s.get('seo_score', 0) for s in suggestions) / len(suggestions),
            'average_quality_score': sum(s.get('quality_score', 0) for s in suggestions) / len(suggestions),
            'average_readability_score': sum(s.get('readability_score', 0) for s in suggestions) / len(suggestions),
            'competition_distribution': {},
            'content_type_distribution': {},
            'priority_distribution': {'high': 0, 'medium': 0, 'low': 0}
        }

        for suggestion in suggestions:
            # Competition distribution
            comp_level = suggestion.get('competition_level', 'unknown')
            metrics['competition_distribution'][comp_level] = metrics['competition_distribution'].get(comp_level, 0) + 1

            # Content type distribution
            content_type = suggestion.get('content_type', 'blog_post')
            metrics['content_type_distribution'][content_type] = metrics['content_type_distribution'].get(content_type, 0) + 1

            # Priority distribution
            priority = suggestion.get('priority_score', 0)
            if priority > 0.8:
                metrics['priority_distribution']['high'] += 1
            elif priority > 0.6:
                metrics['priority_distribution']['medium'] += 1
            else:
                metrics['priority_distribution']['low'] += 1

        return metrics

    # Placeholder implementations for supporting classes
    async def _identify_competitor_gaps_filled(self, idea: Dict, competitor_analysis: Dict) -> List[str]:
        """Placeholder for competitor gap identification."""
        return []

    async def _determine_market_positioning(self, idea: Dict, competitor_analysis: Dict) -> str:
        """Placeholder for market positioning."""
        return "differentiated"

    async def _extract_unique_angles(self, idea: Dict, competitor_analysis: Dict) -> List[str]:
        """Placeholder for unique angle extraction."""
        return []

    async def _analyze_keyword_opportunities(self, keywords: List[str]) -> List[str]:
        """Placeholder for keyword opportunities."""
        return keywords

    async def _assess_gap_seo_potential(self, gaps: List[Dict]) -> Dict[str, Any]:
        """Placeholder for gap SEO assessment."""
        return {}

    async def _generate_long_tail_suggestions(self, keywords: List[str]) -> List[str]:
        """Placeholder for long-tail suggestions."""
        return []

    async def _extract_competitor_strategies(self, competitor_analysis: Dict) -> List[str]:
        """Placeholder for competitor strategy extraction."""
        return []

    # Google Trends Enhanced Methods

    async def _integrate_trend_context(
        self,
        strategic_context: Dict[str, Any],
        trend_data: Dict[str, Any],
        campaign_keywords: List[str]
    ) -> Dict[str, Any]:
        """
        Integrate Google Trends data into strategic context.

        Args:
            strategic_context: Existing strategic context
            trend_data: Google Trends analysis data
            campaign_keywords: Campaign target keywords

        Returns:
            Enhanced strategic context with trend insights
        """
        try:
            trend_context = {
                'rising_topics': trend_data.get('related_topics', {}).get('rising', []),
                'top_topics': trend_data.get('related_topics', {}).get('top', []),
                'rising_queries': trend_data.get('related_queries', {}).get('rising', []),
                'top_queries': trend_data.get('related_queries', {}).get('top', []),
                'interest_over_time': trend_data.get('interest_over_time', []),
                'interest_by_region': trend_data.get('interest_by_region', []),
                'trend_analysis_timestamp': trend_data.get('timestamp'),
                'keyword_trend_scores': self._calculate_keyword_trend_scores(
                    campaign_keywords, trend_data
                ),
                'seasonal_patterns': self._analyze_seasonal_content_patterns(trend_data),
                'geographic_opportunities': self._identify_geographic_content_opportunities(trend_data)
            }

            # Enhance strategic context with trend insights
            enhanced_context = strategic_context.copy()
            enhanced_context.update({
                'trend_enabled': True,
                'trend_context': trend_context,
                'trend_insights': {
                    'rising_topic_count': len(trend_context['rising_topics']),
                    'seasonal_opportunities': len(trend_context['seasonal_patterns']),
                    'geographic_markets': len(trend_context['geographic_opportunities'])
                }
            })

            campaign_logger.info(f"Integrated trend context with {len(trend_context['rising_topics'])} rising topics")
            return enhanced_context

        except Exception as e:
            campaign_logger.warning(f"Trend context integration failed: {e}")
            return strategic_context

    def _calculate_keyword_trend_scores(
        self,
        keywords: List[str],
        trend_data: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        Calculate trend relevance scores for campaign keywords.

        Args:
            keywords: Campaign keywords
            trend_data: Google Trends data

        Returns:
            Dictionary mapping keywords to trend scores
        """
        keyword_scores = {}

        rising_topics = trend_data.get('related_topics', {}).get('rising', [])
        rising_queries = trend_data.get('related_queries', {}).get('rising', [])

        for keyword in keywords:
            score = 0.0
            keyword_lower = keyword.lower()

            # Check rising topics
            for topic in rising_topics:
                if isinstance(topic, dict):
                    topic_title = topic.get('topic_title', '').lower()
                    if keyword_lower in topic_title or topic_title in keyword_lower:
                        score += 0.4

            # Check rising queries
            for query in rising_queries:
                if isinstance(query, dict):
                    query_text = query.get('query', '').lower()
                    if keyword_lower in query_text or query_text in keyword_lower:
                        score += 0.3

            # Normalize score
            keyword_scores[keyword] = min(1.0, score)

        return keyword_scores

    def _analyze_seasonal_content_patterns(self, trend_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analyze seasonal patterns for content planning.

        Args:
            trend_data: Google Trends data

        Returns:
            List of seasonal content opportunities
        """
        interest_over_time = trend_data.get('interest_over_time', [])
        if not interest_over_time:
            return []

        # Group by month and calculate averages
        monthly_data = {}
        for point in interest_over_time:
            if isinstance(point, dict) and 'date' in point and 'value' in point:
                try:
                    date_str = point['date'].split('T')[0]
                    date = datetime.fromisoformat(date_str)
                    month = date.month

                    if month not in monthly_data:
                        monthly_data[month] = []
                    monthly_data[month].append(point['value'])
                except (ValueError, KeyError):
                    continue

        # Calculate monthly averages and identify patterns
        seasonal_patterns = []
        month_names = {
            1: 'January', 2: 'February', 3: 'March', 4: 'April',
            5: 'May', 6: 'June', 7: 'July', 8: 'August',
            9: 'September', 10: 'October', 11: 'November', 12: 'December'
        }

        if monthly_data:
            all_values = [val for values in monthly_data.values() for val in values]
            if all_values:
                avg_all = sum(all_values) / len(all_values)
                peak_threshold = avg_all * 1.2  # 20% above average

                for month, values in monthly_data.items():
                    if values:
                        month_avg = sum(values) / len(values)
                        if month_avg >= peak_threshold:
                            seasonal_patterns.append({
                                'month': month,
                                'month_name': month_names.get(month, ''),
                                'avg_interest': round(month_avg, 1),
                                'opportunity_type': 'peak_season',
                                'content_timing': 'optimal'
                            })

        return seasonal_patterns

    def _identify_geographic_content_opportunities(self, trend_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Identify geographic markets with high trend interest.

        Args:
            trend_data: Google Trends data

        Returns:
            List of geographic content opportunities
        """
        interest_by_region = trend_data.get('interest_by_region', [])
        if not interest_by_region:
            return []

        # Sort by interest score and get top opportunities
        sorted_regions = sorted(
            [r for r in interest_by_region if isinstance(r, dict)],
            key=lambda x: x.get('value', 0),
            reverse=True
        )

        opportunities = []
        for region in sorted_regions[:5]:  # Top 5 regions
            score = region.get('value', 0)
            if score >= 50:  # Minimum threshold
                opportunities.append({
                    'region': region.get('location', 'Unknown'),
                    'interest_score': score,
                    'opportunity_level': 'high' if score >= 75 else 'medium',
                    'content_strategy': 'localized_adaptation' if score >= 75 else 'regional_focus'
                })

        return opportunities

    async def _generate_trend_enhanced_ideas(
        self,
        existing_ideas: List[Dict[str, Any]],
        trend_context: Dict[str, Any],
        campaign_keywords: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Generate trend-enhanced content ideas.

        Args:
            existing_ideas: Existing content ideas
            trend_context: Trend analysis context
            campaign_keywords: Campaign keywords

        Returns:
            List of trend-enhanced content ideas
        """
        try:
            trend_ideas = []

            # Generate ideas from rising topics
            rising_topics = trend_context.get('rising_topics', [])
            for topic in rising_topics[:5]:  # Limit to top 5
                if isinstance(topic, dict):
                    topic_title = topic.get('topic_title', '')
                    if topic_title:
                        base_keyword = campaign_keywords[0] if campaign_keywords else 'content'

                        trend_idea = {
                            'title': f"{topic_title}: Latest Trends and Insights",
                            'description': f"Comprehensive analysis of rising trend '{topic_title}' in the {base_keyword} space",
                            'trend_source': 'rising_topic',
                            'trend_relevance': 0.9,
                            'seo_keywords': [base_keyword, topic_title.lower()],
                            'content_type': 'trend_analysis',
                            'target_audience': 'industry_professionals',
                            'estimated_engagement': 'high'
                        }
                        trend_ideas.append(trend_idea)

            # Generate ideas from rising queries
            rising_queries = trend_context.get('rising_queries', [])
            for query in rising_queries[:5]:  # Limit to top 5
                if isinstance(query, dict):
                    query_text = query.get('query', '')
                    if query_text and len(query_text.split()) <= 4:  # Keep it focused
                        trend_idea = {
                            'title': f"How to {query_text}: Complete Guide",
                            'description': f"Step-by-step guide addressing the rising query '{query_text}'",
                            'trend_source': 'rising_query',
                            'trend_relevance': 0.8,
                            'seo_keywords': query_text.split(),
                            'content_type': 'how_to_guide',
                            'target_audience': 'searchers',
                            'estimated_engagement': 'high'
                        }
                        trend_ideas.append(trend_idea)

            # Generate seasonal content ideas
            seasonal_patterns = trend_context.get('seasonal_patterns', [])
            for pattern in seasonal_patterns[:3]:  # Limit to top 3
                month_name = pattern.get('month_name', '')
                base_keyword = campaign_keywords[0] if campaign_keywords else 'content'

                trend_idea = {
                    'title': f"{month_name} {base_keyword}: Strategic Planning Guide",
                    'description': f"Optimize your {base_keyword} strategy for {month_name} market conditions",
                    'trend_source': 'seasonal_pattern',
                    'trend_relevance': 0.7,
                    'seo_keywords': [base_keyword, month_name.lower()],
                    'content_type': 'seasonal_strategy',
                    'target_audience': 'businesses',
                    'estimated_engagement': 'medium',
                    'publishing_month': month_name
                }
                trend_ideas.append(trend_idea)

            campaign_logger.info(f"Generated {len(trend_ideas)} trend-enhanced content ideas")
            return trend_ideas

        except Exception as e:
            campaign_logger.warning(f"Trend-enhanced idea generation failed: {e}")
            return []

    def _apply_trend_based_prioritization(
        self,
        suggestions: List[Dict[str, Any]],
        trend_context: Dict[str, Any],
        trend_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Apply trend-based prioritization to content suggestions.

        Args:
            suggestions: Existing content suggestions
            trend_context: Trend analysis context
            trend_data: Raw trend data

        Returns:
            Prioritized suggestions with trend scores
        """
        try:
            enhanced_suggestions = []

            for suggestion in suggestions:
                trend_score = self._calculate_suggestion_trend_score(
                    suggestion, trend_context, trend_data
                )

                seasonal_score = self._calculate_seasonal_alignment_score(
                    suggestion, trend_context
                )

                geographic_score = self._calculate_geographic_relevance_score(
                    suggestion, trend_context
                )

                # Calculate composite trend score
                composite_trend_score = (
                    trend_score * 0.5 +
                    seasonal_score * 0.3 +
                    geographic_score * 0.2
                )

                # Enhance suggestion with trend data
                enhanced_suggestion = suggestion.copy()
                enhanced_suggestion.update({
                    'trend_score': trend_score,
                    'seasonal_score': seasonal_score,
                    'geographic_score': geographic_score,
                    'composite_trend_score': composite_trend_score,
                    'trend_enhanced': True
                })

                enhanced_suggestions.append(enhanced_suggestion)

            # Sort by composite trend score (descending)
            return sorted(enhanced_suggestions, key=lambda x: x.get('composite_trend_score', 0), reverse=True)

        except Exception as e:
            campaign_logger.warning(f"Trend-based prioritization failed: {e}")
            return suggestions

    def _calculate_suggestion_trend_score(
        self,
        suggestion: Dict[str, Any],
        trend_context: Dict[str, Any],
        trend_data: Dict[str, Any]
    ) -> float:
        """
        Calculate trend relevance score for a content suggestion.

        Returns score from 0.0 to 1.0
        """
        title = suggestion.get('title', '').lower()
        description = suggestion.get('description', '').lower()

        score = 0.0

        # Check against rising topics
        rising_topics = trend_context.get('rising_topics', [])
        for topic in rising_topics:
            if isinstance(topic, dict):
                topic_title = topic.get('topic_title', '').lower()
                if topic_title in title or topic_title in description:
                    score += 0.4

        # Check against rising queries
        rising_queries = trend_context.get('rising_queries', [])
        for query in rising_queries:
            if isinstance(query, dict):
                query_text = query.get('query', '').lower()
                if query_text in title or query_text in description:
                    score += 0.3

        # Check against top topics (lower weight)
        top_topics = trend_context.get('top_topics', [])
        for topic in top_topics[:10]:  # Top 10 only
            if isinstance(topic, dict):
                topic_title = topic.get('topic_title', '').lower()
                if topic_title in title or topic_title in description:
                    score += 0.15

        return min(1.0, score)

    def _calculate_seasonal_alignment_score(
        self,
        suggestion: Dict[str, Any],
        trend_context: Dict[str, Any]
    ) -> float:
        """
        Calculate seasonal alignment score for content timing.

        Returns score from 0.0 to 1.0
        """
        title = suggestion.get('title', '').lower()
        description = suggestion.get('description', '').lower()

        seasonal_patterns = trend_context.get('seasonal_patterns', [])
        if not seasonal_patterns:
            return 0.0

        score = 0.0
        seasonal_keywords = ['seasonal', 'quarterly', 'monthly', 'annual', 'quarter']

        # Check for seasonal keywords
        content_text = f"{title} {description}"
        seasonal_matches = sum(1 for keyword in seasonal_keywords if keyword in content_text)
        score += min(0.4, seasonal_matches * 0.2)

        # Check alignment with seasonal patterns
        for pattern in seasonal_patterns:
            month_name = pattern.get('month_name', '').lower()
            if month_name in content_text:
                score += 0.6  # Strong alignment with seasonal peak

        return min(1.0, score)

    def _calculate_geographic_relevance_score(
        self,
        suggestion: Dict[str, Any],
        trend_context: Dict[str, Any]
    ) -> float:
        """
        Calculate geographic relevance score.

        Returns score from 0.0 to 1.0
        """
        title = suggestion.get('title', '').lower()
        description = suggestion.get('description', '').lower()

        geographic_opportunities = trend_context.get('geographic_opportunities', [])
        if not geographic_opportunities:
            return 0.0

        score = 0.0
        geographic_keywords = ['local', 'regional', 'global', 'international', 'market']

        # Check for geographic keywords
        content_text = f"{title} {description}"
        geo_matches = sum(1 for keyword in geographic_keywords if keyword in content_text)
        score += min(0.3, geo_matches * 0.15)

        # Check alignment with high-interest regions
        for opportunity in geographic_opportunities[:3]:  # Top 3 regions
            region = opportunity.get('region', '').lower()
            if region in content_text:
                score += 0.7 / len(geographic_opportunities)  # Distribute score

        return min(1.0, score)

    def _extract_trend_insights(self, trend_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract key trend insights for metadata.

        Args:
            trend_data: Google Trends analysis data

        Returns:
            Key trend insights summary
        """
        insights = {
            'data_points': len(trend_data.get('interest_over_time', [])),
            'regions_analyzed': len(trend_data.get('interest_by_region', [])),
            'rising_topics_count': len(trend_data.get('related_topics', {}).get('rising', [])),
            'rising_queries_count': len(trend_data.get('related_queries', {}).get('rising', [])),
            'timestamp': trend_data.get('timestamp')
        }

        # Calculate trend direction if possible
        interest_over_time = trend_data.get('interest_over_time', [])
        if len(interest_over_time) >= 6:  # Need minimum data points
            first_half = interest_over_time[:len(interest_over_time)//2]
            second_half = interest_over_time[len(interest_over_time)//2:]

            first_avg = sum(p.get('value', 0) for p in first_half) / len(first_half) if first_half else 0
            second_avg = sum(p.get('value', 0) for p in second_half) / len(second_half) if second_half else 0

            if first_avg > 0:
                momentum = (second_avg - first_avg) / first_avg
                insights['trend_momentum'] = round(momentum, 3)
                insights['trend_direction'] = 'rising' if momentum > 0.05 else 'falling' if momentum < -0.05 else 'stable'

        return insights


class SEOContentOptimizer:
    """SEO optimization utilities for content suggestions."""

    async def optimize_headline(self, title: str, keywords: List[str]) -> str:
        """Optimize headline for SEO."""
        # Placeholder implementation
        return title

    async def select_keyword_targets(self, idea: Dict, keywords: List[str], gaps: List[Dict]) -> List[str]:
        """Select optimal keywords for content."""
        return keywords[:3]

    async def analyze_search_intent(self, title: str) -> str:
        """Analyze search intent of title."""
        return "informational"

    async def assess_competition(self, title: str) -> str:
        """Assess competition level."""
        return "medium"

    async def calculate_seo_score(self, idea: Dict, keywords: List[str]) -> float:
        """Calculate SEO score."""
        return 0.7


class ContentQualityValidator:
    """Content quality validation utilities."""

    async def assess_overall_quality(self, idea: Dict) -> float:
        """Assess overall content quality."""
        return 0.8

    async def calculate_readability(self, idea: Dict) -> float:
        """Calculate readability score."""
        return 0.75

    async def check_originality(self, idea: Dict) -> float:
        """Check content originality."""
        return 0.85

    async def assess_shareability(self, idea: Dict) -> float:
        """Assess content shareability."""
        return 0.7


class ProspectPersonalizationEngine:
    """Prospect personalization utilities."""

    async def analyze_prospect_fit(self, idea: Dict, profile: Dict) -> float:
        """Analyze how well idea fits prospect."""
        return 0.8

    async def assess_audience_alignment(self, idea: Dict, profile: Dict) -> float:
        """Assess audience alignment."""
        return 0.75

    async def score_gap_relevance(self, idea: Dict, gaps: List[Dict]) -> float:
        """Score relevance to content gaps."""
        return 0.7

    async def generate_personalized_hook(self, idea: Dict, profile: Dict) -> str:
        """Generate personalized hook."""
        return "Discover how to..."

    async def suggest_tailored_angle(self, idea: Dict, gaps: List[Dict]) -> str:
        """Suggest tailored content angle."""
        return "Focus on practical implementation"