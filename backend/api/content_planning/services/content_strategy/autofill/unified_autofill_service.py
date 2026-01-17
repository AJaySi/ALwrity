"""
Unified AutoFill Service
Combines database autofill (18-19 fields) with AI autofill (11-12 fields) for optimal performance.
"""

from typing import Any, Dict
from sqlalchemy.orm import Session
from loguru import logger

from .autofill_service import AutoFillService
from .ai_structured_autofill import AIStructuredAutofillService

# Fields that come from database (18-19 fields)
DB_MAPPED_FIELDS = [
    'business_objectives', 'target_metrics', 'content_budget', 'team_size',
    'implementation_timeline', 'performance_metrics',
    'content_preferences', 'consumption_patterns', 'audience_pain_points',
    'buying_journey', 'top_competitors', 'market_gaps', 'industry_trends',
    'emerging_trends', 'preferred_formats', 'content_frequency',
    'optimal_timing', 'editorial_guidelines', 'brand_voice'
]

# Fields that require AI personalization (11 fields)
AI_GENERATED_FIELDS = [
    'seasonal_trends', 'competitor_content_strategies', 'market_share',
    'competitive_position', 'engagement_metrics', 'traffic_sources',
    'conversion_rates', 'content_roi_targets', 'ab_testing_capabilities',
    'content_mix', 'quality_metrics'
]


class UnifiedAutoFillService:
    """Combined database + AI autofill service."""
    
    def __init__(self, db: Session):
        self.db = db
        self.db_service = AutoFillService(db)
        self.ai_service = AIStructuredAutofillService()  # AI service doesn't need db session
    
    async def get_autofill(self, user_id: str) -> Dict[str, Any]:
        """
        Get autofill payload combining database fields (18-19) + AI fields (11-12).
        
        Flow:
        1. Fetch database-mapped fields (fast, no AI)
        2. Generate AI fields (personalized, focused prompt)
        3. Merge results (30 fields total)
        """
        try:
            logger.info(f"🚀 Starting unified autofill for user: {user_id}")
            
            # Step 1: Get database-mapped fields (fast, no AI)
            logger.info("📊 Step 1: Fetching database fields...")
            db_payload = await self.db_service.get_autofill(user_id)
            db_fields = db_payload.get('fields', {})
            
            # Extract only DB-mapped fields
            db_extracted_fields = {}
            for field_name in DB_MAPPED_FIELDS:
                if field_name in db_fields:
                    db_extracted_fields[field_name] = db_fields[field_name]
            
            logger.info(f"✅ Database fields extracted: {len(db_extracted_fields)} fields")
            
            # Step 2: Get AI-generated fields (personalized, focused prompt)
            logger.info("🤖 Step 2: Generating AI fields...")
            
            # Get raw onboarding data for AI context (AI service needs full context)
            from ..onboarding.data_integration import OnboardingDataIntegrationService
            integration = OnboardingDataIntegrationService()
            raw_data = await integration.process_onboarding_data(user_id, self.db)
            
            # Build AI context from raw onboarding data
            ai_context = {
                'website_analysis': raw_data.get('website_analysis', {}),
                'research_preferences': raw_data.get('research_preferences', {}),
                'onboarding_session': raw_data.get('onboarding_session', {}),
                'api_keys_data': raw_data.get('api_keys_data', {})
            }
            
            # Generate all fields with AI, then filter to only AI_GENERATED_FIELDS
            # TODO: Optimize AI service to generate only specific fields with focused prompt
            ai_payload = await self.ai_service.generate_autofill_fields(user_id, ai_context)
            all_ai_fields = ai_payload.get('fields', {})
            
            # Filter to only AI-generated fields (11 fields)
            ai_fields = {field: all_ai_fields[field] for field in AI_GENERATED_FIELDS if field in all_ai_fields}
            ai_meta = ai_payload.get('meta', {})
            
            logger.info(f"✅ AI fields generated: {len(ai_fields)} fields")
            
            # Step 3: Merge results
            all_fields = {**db_extracted_fields, **ai_fields}
            
            # Merge sources and input_data_points
            all_sources = {**db_payload.get('sources', {}), **ai_payload.get('sources', {})}
            all_input_data_points = {
                **db_payload.get('input_data_points', {}),
                **ai_payload.get('input_data_points', {})
            }
            
            # Combine quality scores and confidence levels
            all_quality_scores = {
                **db_payload.get('quality_scores', {}),
                **ai_payload.get('quality_scores', {})
            }
            all_confidence_levels = {
                **db_payload.get('confidence_levels', {}),
                **ai_payload.get('confidence_levels', {})
            }
            
            # Calculate combined meta
            combined_meta = {
                'ai_used': True,  # We used AI for 11 fields
                'ai_overrides_count': len(ai_fields),
                'db_fields_count': len(db_extracted_fields),
                'ai_fields_count': len(ai_fields),
                'total_fields': len(all_fields),
                'data_source': 'unified',  # Combined approach
                'ai_success_rate': ai_meta.get('success_rate', 0),
                'ai_attempts': ai_meta.get('attempts', 0),
                'processing_time_ms': ai_meta.get('processing_time_ms', 0)
            }
            
            logger.info(f"✅ Unified autofill complete: {len(all_fields)} total fields ({len(db_extracted_fields)} DB + {len(ai_fields)} AI)")
            
            return {
                'fields': all_fields,
                'sources': all_sources,
                'quality_scores': all_quality_scores,
                'confidence_levels': all_confidence_levels,
                'data_freshness': db_payload.get('data_freshness', {}),
                'input_data_points': all_input_data_points,
                'meta': combined_meta
            }
            
        except Exception as e:
            logger.error(f"❌ Error in unified autofill: {str(e)}")
            raise
