from typing import Any, Dict, Optional
from sqlalchemy.orm import Session

from ..onboarding.data_integration import OnboardingDataIntegrationService

# Local module imports (to be created in this batch)
from .normalizers.website_normalizer import normalize_website_analysis
from .normalizers.research_normalizer import normalize_research_preferences
from .normalizers.api_keys_normalizer import normalize_api_keys
from .normalizers.persona_normalizer import normalize_persona_data
from .normalizers.competitor_normalizer import normalize_competitor_analysis
from .normalizers.analytics_normalizer import normalize_gsc_analytics, normalize_bing_analytics, normalize_analytics_combined
from .transformer import transform_to_fields
from .quality import calculate_quality_scores_from_raw, calculate_confidence_from_raw, calculate_data_freshness
from .transparency import build_data_sources_map, build_input_data_points
from .schema import validate_output


class AutoFillService:
    """Facade for building Content Strategy auto-fill payload."""

    def __init__(self, db: Session):
        self.db = db
        self.integration = OnboardingDataIntegrationService()

    async def get_autofill(self, user_id: str) -> Dict[str, Any]:
        import logging
        logger = logging.getLogger(__name__)
        
        # 1) Collect raw integration data
        integrated = await self.integration.process_onboarding_data(user_id, self.db)
        if not integrated:
            raise RuntimeError("No onboarding data available for user")

        website_raw = integrated.get('website_analysis', {})
        research_raw = integrated.get('research_preferences', {})
        api_raw = integrated.get('api_keys_data', {})
        session_raw = integrated.get('onboarding_session', {})
        persona_raw = integrated.get('persona_data', {})
        competitor_raw = integrated.get('competitor_analysis', [])
        gsc_raw = integrated.get('gsc_analytics', {})
        bing_raw = integrated.get('bing_analytics', {})

        # Preflight: check required data sources before doing heavy processing
        data_availability = {
            'website_analysis': bool(website_raw),
            'research_preferences': bool(research_raw),
            'api_keys_data': bool(api_raw),
            'onboarding_session': bool(session_raw),
            'persona_data': bool(persona_raw),
            'competitor_analysis': bool(competitor_raw),
            'gsc_analytics': bool(gsc_raw),
            'bing_analytics': bool(bing_raw),
        }
        missing_required = [k for k in ['website_analysis', 'research_preferences', 'onboarding_session'] if not data_availability[k]]
        missing_optional = [k for k in ['persona_data', 'competitor_analysis', 'gsc_analytics', 'bing_analytics', 'api_keys_data'] if not data_availability[k]]
        if missing_required:
            logger.warning(f"⚠️ Autofill preflight: missing required sources for user {user_id}: {missing_required}")
        if missing_optional:
            logger.warning(f"ℹ️ Autofill preflight: missing optional sources for user {user_id}: {missing_optional}")

        # Surface record-level presence to callers for validation (ids + timestamps)
        def _record_summary(raw: Dict[str, Any]) -> Dict[str, Any]:
            if not isinstance(raw, dict) or not raw:
                return {}
            return {
                'id': raw.get('id'),
                'status': raw.get('status'),
                'created_at': raw.get('created_at'),
                'updated_at': raw.get('updated_at')
            }

        source_records = {
            'onboarding_session': _record_summary(session_raw),
            'website_analysis': _record_summary(website_raw),
            'research_preferences': _record_summary(research_raw),
            'persona_data': _record_summary(persona_raw),
            'api_keys_data': {'count': len(api_raw) if isinstance(api_raw, dict) else 0},
            'competitor_analysis': {'count': len(competitor_raw) if isinstance(competitor_raw, list) else 0},
            'gsc_analytics': {'has_data': bool(gsc_raw)},
            'bing_analytics': {'has_data': bool(bing_raw)}
        }

        # Log raw data to diagnose field mapping issues
        logger.warning(f"🔍 RAW DATA for user {user_id}:")
        logger.warning(f"  Website Analysis keys: {list(website_raw.keys()) if website_raw else 'EMPTY'}")
        if website_raw:
            logger.warning(f"  Website content_type: {website_raw.get('content_type')}")
            logger.warning(f"  Website target_audience: {website_raw.get('target_audience')}")
            logger.warning(f"  Website writing_style: {website_raw.get('writing_style')}")
            logger.warning(f"  Website recommended_settings: {website_raw.get('recommended_settings')}")
            logger.warning(f"  Website style_guidelines: {website_raw.get('style_guidelines')}")
            logger.warning(f"  Website content_characteristics: {website_raw.get('content_characteristics')}")
            logger.warning(f"  Website crawl_result: {type(website_raw.get('crawl_result')).__name__ if website_raw.get('crawl_result') else 'None'}")
            logger.warning(f"  Website style_patterns: {type(website_raw.get('style_patterns')).__name__ if website_raw.get('style_patterns') else 'None'}")
        logger.warning(f"  Research Preferences keys: {list(research_raw.keys()) if research_raw else 'EMPTY'}")
        if research_raw:
            logger.warning(f"  Research content_types: {research_raw.get('content_types')}")
            logger.warning(f"  Research target_audience: {research_raw.get('target_audience')}")
            logger.warning(f"  Research writing_style: {research_raw.get('writing_style')}")
        logger.warning(f"  API Keys data: {list(api_raw.keys()) if api_raw else 'EMPTY'}")
        logger.warning(f"  Session data: {list(session_raw.keys()) if session_raw else 'EMPTY'}")
        logger.warning(f"  Persona data: {list(persona_raw.keys()) if persona_raw else 'EMPTY'}")
        logger.warning(f"  Competitor analysis: {len(competitor_raw) if competitor_raw else 0} competitors")
        if competitor_raw and len(competitor_raw) > 0:
            logger.warning(f"  🔍 Sample competitor keys: {list(competitor_raw[0].keys()) if competitor_raw[0] else 'EMPTY'}")
            logger.warning(f"  🔍 Sample competitor has analysis_data: {'analysis_data' in competitor_raw[0] if competitor_raw[0] else False}")
            if competitor_raw[0].get('analysis_data'):
                logger.warning(f"  🔍 Sample analysis_data type: {type(competitor_raw[0]['analysis_data'])}")
                logger.warning(f"  🔍 Sample analysis_data keys: {list(competitor_raw[0]['analysis_data'].keys()) if isinstance(competitor_raw[0]['analysis_data'], dict) else 'Not a dict'}")
        logger.warning(f"  GSC Analytics: {list(gsc_raw.keys()) if gsc_raw else 'EMPTY'}")
        logger.warning(f"  Bing Analytics: {list(bing_raw.keys()) if bing_raw else 'EMPTY'}")

        # 2) Normalize raw sources
        website = await normalize_website_analysis(website_raw)
        # Pass website data as fallback for research normalizer
        research = await normalize_research_preferences(research_raw, website_fallback=website_raw)
        api_keys = await normalize_api_keys(api_raw)
        persona = await normalize_persona_data(persona_raw) if persona_raw else {}
        # Always call normalize_competitor_analysis - it handles empty lists gracefully and returns structure
        # competitor_raw can be None, [], or a list with data - normalize handles all cases
        if competitor_raw is None:
            competitor = {}
        elif isinstance(competitor_raw, list):
            competitor = await normalize_competitor_analysis(competitor_raw)
        else:
            logger.warning(f"⚠️ Unexpected competitor_raw type: {type(competitor_raw)}, value: {competitor_raw}")
            competitor = {}
        
        # Log competitor normalization results
        logger.warning(f"🔍 COMPETITOR NORMALIZATION for user {user_id}:")
        logger.warning(f"  Raw competitor count: {len(competitor_raw) if competitor_raw else 0}")
        logger.warning(f"  Competitor raw type: {type(competitor_raw)}")
        logger.warning(f"  Competitor raw truthy: {bool(competitor_raw)}")
        logger.warning(f"  Normalized competitor keys: {list(competitor.keys()) if competitor else 'EMPTY'}")
        logger.warning(f"  Normalized competitor truthy: {bool(competitor)}")
        if competitor:
            logger.warning(f"  Top competitors: {len(competitor.get('top_competitors', []))}")
            if competitor.get('top_competitors'):
                logger.warning(f"  🔍 Sample top_competitor: {competitor['top_competitors'][0] if len(competitor['top_competitors']) > 0 else 'EMPTY'}")
            logger.warning(f"  Market gaps: {len(competitor.get('market_gaps', []))}")
            if competitor.get('market_gaps'):
                logger.warning(f"  🔍 Sample market_gap: {competitor['market_gaps'][0] if len(competitor['market_gaps']) > 0 else 'EMPTY'}")
            logger.warning(f"  Industry trends: {len(competitor.get('industry_trends', []))}")
            if competitor.get('industry_trends'):
                logger.warning(f"  🔍 Sample industry_trend: {competitor['industry_trends'][0] if len(competitor['industry_trends']) > 0 else 'EMPTY'}")
            logger.warning(f"  Emerging trends: {len(competitor.get('emerging_trends', []))}")
            if competitor.get('emerging_trends'):
                logger.warning(f"  🔍 Sample emerging_trend: {competitor['emerging_trends'][0] if len(competitor['emerging_trends']) > 0 else 'EMPTY'}")
            logger.warning(f"  Competitor strategies: {bool(competitor.get('competitor_content_strategies'))}")
            if competitor.get('competitor_content_strategies'):
                logger.warning(f"  🔍 Competitor strategies keys: {list(competitor['competitor_content_strategies'].keys())}")
        else:
            logger.warning(f"  ⚠️ COMPETITOR NORMALIZATION RETURNED EMPTY DICT!")
        
        # Normalize analytics data
        gsc = await normalize_gsc_analytics(gsc_raw) if gsc_raw else {}
        bing = await normalize_bing_analytics(bing_raw) if bing_raw else {}
        analytics = await normalize_analytics_combined(gsc, bing) if (gsc or bing) else {}
        
        # Log normalized data
        logger.warning(f"🔍 NORMALIZED DATA for user {user_id}:")
        logger.warning(f"  Normalized Research keys: {list(research.keys()) if research else 'EMPTY'}")
        if research:
            logger.warning(f"  Normalized content_preferences: {research.get('content_preferences')}")
            logger.warning(f"  Normalized audience_intelligence: {research.get('audience_intelligence')}")

        # 3) Quality/confidence/freshness (computed from raw, but returned as meta)
        quality_scores = calculate_quality_scores_from_raw({
            'website_analysis': website_raw,
            'research_preferences': research_raw,
            'api_keys_data': api_raw,
        })
        confidence_levels = calculate_confidence_from_raw({
            'website_analysis': website_raw,
            'research_preferences': research_raw,
            'api_keys_data': api_raw,
        })
        data_freshness = calculate_data_freshness(session_raw)

        # 4) Transform to frontend field map
        fields = transform_to_fields(
            website=website,
            research=research,
            api_keys=api_keys,
            session=session_raw,
            persona=persona,
            competitor=competitor,
            analytics=analytics,
        )

        # 5) Transparency maps
        sources = build_data_sources_map(website, research, api_keys, persona, competitor, analytics)
        input_data_points = build_input_data_points(
            website_raw=website_raw,
            research_raw=research_raw,
            api_raw=api_raw,
            persona_raw=persona_raw,
            competitor_raw=competitor_raw,
            gsc_raw=gsc_raw,
            bing_raw=bing_raw,
        )

        payload = {
            'fields': fields,
            'sources': sources,
            'quality_scores': quality_scores,
            'confidence_levels': confidence_levels,
            'data_freshness': data_freshness,
            'input_data_points': input_data_points,
            'meta': {
                'ai_used': False,  # Database autofill does NOT use AI
                'ai_overrides_count': 0,
                'data_source': 'database',
                'processing_time_ms': 0,  # Will be set by endpoint if needed
                'data_availability': data_availability,
                'missing_required_sources': missing_required,
                'missing_optional_sources': missing_optional,
                'source_records': source_records
            }
        }

        # Validate structure strictly
        validate_output(payload)
        return payload 