from typing import Any, Dict, Optional
from sqlalchemy.orm import Session
import logging
import traceback

from .autofill_service import AutoFillService
from ...ai_analytics_service import ContentPlanningAIAnalyticsService
from .ai_structured_autofill import AIStructuredAutofillService
from .transparency_service import AutofillTransparencyService

logger = logging.getLogger(__name__)

class AutoFillRefreshService:
    """Generates a fresh auto-fill payload for the Strategy Builder.
    This service does NOT persist anything. Intended for refresh flows.
    """

    def __init__(self, db: Session):
        self.db = db
        self.autofill = AutoFillService(db)
        self.ai_analytics = ContentPlanningAIAnalyticsService()
        self.structured_ai = AIStructuredAutofillService()
        self.transparency = AutofillTransparencyService(db)

    async def build_fresh_payload(self, user_id: int, use_ai: bool = True, ai_only: bool = False) -> Dict[str, Any]:
        """Build a fresh auto-fill payload.
        - Reads latest onboarding-integrated data
        - Optionally augments with AI overrides (hook, not persisted)
        - Returns payload in the same shape as AutoFillService.get_autofill, plus meta
        """
        logger.info(f"AutoFillRefreshService: starting build_fresh_payload | user=%s | use_ai=%s | ai_only=%s", user_id, use_ai, ai_only)
        
        # Base context from onboarding analysis (used for AI context only when ai_only)
        logger.debug("AutoFillRefreshService: processing onboarding context | user=%s", user_id)
        base_context = await self.autofill.integration.process_onboarding_data(user_id, self.db)
        logger.debug(
            "AutoFillRefreshService: context keys=%s | website=%s research=%s api=%s session=%s",
            list(base_context.keys()) if isinstance(base_context, dict) else 'n/a',
            bool((base_context or {}).get('website_analysis')),
            bool((base_context or {}).get('research_preferences')),
            bool((base_context or {}).get('api_keys_data')),
            bool((base_context or {}).get('onboarding_session')),
        )
        
        # Log detailed context analysis
        logger.info(f"AutoFillRefreshService: detailed context analysis | user=%s", user_id)
        if base_context:
            website_analysis = base_context.get('website_analysis', {})
            research_preferences = base_context.get('research_preferences', {})
            api_keys_data = base_context.get('api_keys_data', {})
            onboarding_session = base_context.get('onboarding_session', {})
            
            logger.info(f"  - Website analysis keys: {list(website_analysis.keys()) if website_analysis else 'None'}")
            logger.info(f"  - Research preferences keys: {list(research_preferences.keys()) if research_preferences else 'None'}")
            logger.info("  - API keys data present: %s | entry_count=%s", bool(api_keys_data), len(api_keys_data) if isinstance(api_keys_data, dict) else 0)
            logger.info(f"  - Onboarding session keys: {list(onboarding_session.keys()) if onboarding_session else 'None'}")
            
            # Log specific data points
            if website_analysis:
                logger.info(f"  - Website URL: {website_analysis.get('website_url', 'Not found')}")
                logger.info(f"  - Website status: {website_analysis.get('status', 'Unknown')}")
            if research_preferences:
                logger.info(f"  - Research depth: {research_preferences.get('research_depth', 'Not found')}")
                logger.info(f"  - Content types: {research_preferences.get('content_types', 'Not found')}")
            if api_keys_data:
                logger.info(f"  - API providers: {api_keys_data.get('providers', [])}")
                logger.info("  - API key data present: %s", bool(api_keys_data))
        else:
            logger.warning(f"AutoFillRefreshService: no base context available | user=%s", user_id)
        
        try:
            w = (base_context or {}).get('website_analysis') or {}
            r = (base_context or {}).get('research_preferences') or {}
            logger.debug("AutoFillRefreshService: website keys=%s | research keys=%s", len(list(w.keys())) if hasattr(w,'keys') else 0, len(list(r.keys())) if hasattr(r,'keys') else 0)
        except Exception:
            pass

        # 🚨 CRITICAL: Always use AI-only generation for refresh to ensure real AI values
        if use_ai:
            logger.info("AutoFillRefreshService: FORCING AI-only generation for refresh to ensure real AI values")
            try:
                ai_payload = await self.structured_ai.generate_autofill_fields(user_id, base_context)
                meta = ai_payload.get('meta') or {}
                logger.info("AI-only payload meta: ai_used=%s overrides=%s", meta.get('ai_used'), meta.get('ai_overrides_count'))
                
                # Log detailed AI payload analysis
                logger.info(f"AutoFillRefreshService: AI payload analysis | user=%s", user_id)
                logger.info(f"  - AI used: {meta.get('ai_used', False)}")
                logger.info(f"  - AI overrides count: {meta.get('ai_overrides_count', 0)}")
                logger.info(f"  - Success rate: {meta.get('success_rate', 0):.1f}%")
                logger.info(f"  - Attempts: {meta.get('attempts', 0)}")
                logger.info(f"  - Missing fields: {len(meta.get('missing_fields', []))}")
                logger.info(f"  - Fields generated: {len(ai_payload.get('fields', {}))}")
                
                # 🚨 VALIDATION: Ensure we have real AI-generated data
                if not meta.get('ai_used', False) or meta.get('ai_overrides_count', 0) == 0:
                    logger.error("❌ CRITICAL: AI generation failed to produce real values - returning error")
                    return {
                        'fields': {},
                        'sources': {},
                        'meta': {
                            'ai_used': False,
                            'ai_overrides_count': 0,
                            'ai_override_fields': [],
                            'ai_only': True,
                            'error': 'AI generation failed to produce real values. Please try again.',
                            'data_source': 'ai_generation_failed'
                        }
                    }
                
                logger.info("✅ SUCCESS: Real AI-generated values produced")
                return ai_payload
            except Exception as e:
                logger.error("AI-only structured generation failed | user=%s | err=%s", user_id, repr(e))
                logger.error("Traceback:\n%s", traceback.format_exc())
                # Return error instead of fallback to prevent stale data
                return {
                    'fields': {},
                    'sources': {},
                    'meta': {
                        'ai_used': False,
                        'ai_overrides_count': 0,
                        'ai_override_fields': [],
                        'ai_only': True,
                        'error': f'AI generation failed: {str(e)}. Please try again.',
                        'data_source': 'ai_generation_error'
                    }
                }

        # 🚨 CRITICAL: If AI is disabled, return error instead of stale database data
        logger.error("❌ CRITICAL: AI generation is disabled - cannot provide real AI values")
        return {
            'fields': {},
            'sources': {},
            'meta': {
                'ai_used': False,
                'ai_overrides_count': 0,
                'ai_override_fields': [],
                'ai_only': False,
                'error': 'AI generation is required for refresh. Please enable AI and try again.',
                'data_source': 'ai_disabled'
            }
        }
    
    async def build_fresh_payload_with_transparency(self, user_id: int, use_ai: bool = True, ai_only: bool = False, yield_callback=None) -> Dict[str, Any]:
        """Build a fresh auto-fill payload with transparency messages.
        
        Args:
            user_id: User ID to build payload for
            use_ai: Whether to use AI augmentation
            ai_only: Whether to use AI-only generation
            yield_callback: Callback function to yield transparency messages
        """
        logger.info(f"AutoFillRefreshService: starting build_fresh_payload_with_transparency | user=%s | use_ai=%s | ai_only=%s", user_id, use_ai, ai_only)
        
        # Phase 1: Initialization
        if yield_callback:
            logger.info("AutoFillRefreshService: generating autofill_initialization message")
            await yield_callback(self.transparency.generate_phase_message('autofill_initialization'))
        
        # Phase 2: Data Collection
        if yield_callback:
            logger.info("AutoFillRefreshService: generating autofill_data_collection message")
            await yield_callback(self.transparency.generate_phase_message('autofill_data_collection'))
        
        # Base context from onboarding analysis
        logger.debug("AutoFillRefreshService: processing onboarding context | user=%s", user_id)
        base_context = await self.autofill.integration.process_onboarding_data(user_id, self.db)
        
        # Phase 3: Data Quality Assessment
        if yield_callback:
            data_source_summary = self.transparency.get_data_source_summary(base_context)
            context = {'data_sources': data_source_summary}
            await yield_callback(self.transparency.generate_phase_message('autofill_data_quality', context))
        
        # Phase 4: Context Analysis
        if yield_callback:
            await yield_callback(self.transparency.generate_phase_message('autofill_context_analysis'))
        
        # Phase 5: Strategy Generation
        if yield_callback:
            await yield_callback(self.transparency.generate_phase_message('autofill_strategy_generation'))
        
        if ai_only and use_ai:
            logger.info("AutoFillRefreshService: AI-only refresh enabled; generating full 30+ fields via AI")
            
            # Phase 6: Field Generation
            if yield_callback:
                await yield_callback(self.transparency.generate_phase_message('autofill_field_generation'))
            
            try:
                ai_payload = await self.structured_ai.generate_autofill_fields(user_id, base_context)
                meta = ai_payload.get('meta') or {}
                
                # 🚨 VALIDATION: Ensure we have real AI-generated data
                if not meta.get('ai_used', False) or meta.get('ai_overrides_count', 0) == 0:
                    logger.error("❌ CRITICAL: AI generation failed to produce real values - returning error")
                    return {
                        'fields': {},
                        'sources': {},
                        'meta': {
                            'ai_used': False,
                            'ai_overrides_count': 0,
                            'ai_override_fields': [],
                            'ai_only': True,
                            'error': 'AI generation failed to produce real values. Please try again.',
                            'data_source': 'ai_generation_failed'
                        }
                    }
                
                # Phase 7: Quality Validation
                if yield_callback:
                    validation_context = {
                        'validation_results': {
                            'passed': len(ai_payload.get('fields', {})),
                            'total': 30  # Approximate total fields
                        }
                    }
                    await yield_callback(self.transparency.generate_phase_message('autofill_quality_validation', validation_context))
                
                # Phase 8: Alignment Check
                if yield_callback:
                    await yield_callback(self.transparency.generate_phase_message('autofill_alignment_check'))
                
                # Phase 9: Final Review
                if yield_callback:
                    await yield_callback(self.transparency.generate_phase_message('autofill_final_review'))
                
                # Phase 10: Complete
                if yield_callback:
                    logger.info("AutoFillRefreshService: generating autofill_complete message")
                    await yield_callback(self.transparency.generate_phase_message('autofill_complete'))
                
                logger.info("✅ SUCCESS: Real AI-generated values produced with transparency")
                return ai_payload
            except Exception as e:
                logger.error("AI-only structured generation failed | user=%s | err=%s", user_id, repr(e))
                logger.error("Traceback:\n%s", traceback.format_exc())
                return {
                    'fields': {},
                    'sources': {},
                    'meta': {
                        'ai_used': False,
                        'ai_overrides_count': 0,
                        'ai_override_fields': [],
                        'ai_only': True,
                        'error': f'AI generation failed: {str(e)}. Please try again.',
                        'data_source': 'ai_generation_error'
                    }
                }
        
        # 🚨 CRITICAL: Force AI generation for refresh - no fallback to database
        if use_ai:
            logger.info("AutoFillRefreshService: FORCING AI generation for refresh to ensure real AI values")
            
            # Phase 6: Field Generation (for AI generation)
            if yield_callback:
                await yield_callback(self.transparency.generate_phase_message('autofill_field_generation'))
            
            try:
                ai_payload = await self.structured_ai.generate_autofill_fields(user_id, base_context)
                meta = ai_payload.get('meta') or {}
                
                # 🚨 VALIDATION: Ensure we have real AI-generated data
                if not meta.get('ai_used', False) or meta.get('ai_overrides_count', 0) == 0:
                    logger.error("❌ CRITICAL: AI generation failed to produce real values - returning error")
                    return {
                        'fields': {},
                        'sources': {},
                        'meta': {
                            'ai_used': False,
                            'ai_overrides_count': 0,
                            'ai_override_fields': [],
                            'ai_only': False,
                            'error': 'AI generation failed to produce real values. Please try again.',
                            'data_source': 'ai_generation_failed'
                        }
                    }
                
                # Phase 7-10: Validation, Alignment, Review, Complete
                if yield_callback:
                    await yield_callback(self.transparency.generate_phase_message('autofill_quality_validation'))
                    await yield_callback(self.transparency.generate_phase_message('autofill_alignment_check'))
                    await yield_callback(self.transparency.generate_phase_message('autofill_final_review'))
                    await yield_callback(self.transparency.generate_phase_message('autofill_complete'))
                
                logger.info("✅ SUCCESS: Real AI-generated values produced with transparency")
                return ai_payload
            except Exception as e:
                logger.error("AI generation failed | user=%s | err=%s", user_id, repr(e))
                logger.error("Traceback:\n%s", traceback.format_exc())
                return {
                    'fields': {},
                    'sources': {},
                    'meta': {
                        'ai_used': False,
                        'ai_overrides_count': 0,
                        'ai_override_fields': [],
                        'ai_only': False,
                        'error': f'AI generation failed: {str(e)}. Please try again.',
                        'data_source': 'ai_generation_error'
                    }
                }
        
        # 🚨 CRITICAL: If AI is disabled, return error instead of stale database data
        logger.error("❌ CRITICAL: AI generation is disabled - cannot provide real AI values")
        return {
            'fields': {},
            'sources': {},
            'meta': {
                'ai_used': False,
                'ai_overrides_count': 0,
                'ai_override_fields': [],
                'ai_only': False,
                'error': 'AI generation is required for refresh. Please enable AI and try again.',
                'data_source': 'ai_disabled'
            }
        } 