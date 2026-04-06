"""API package for ALwrity backend.

The onboarding endpoints are re-exported from a stable module
(`onboarding_endpoints`) to avoid issues where external tools overwrite
`onboarding.py`.
"""

import os

# Check podcast mode early
_is_podcast = os.getenv("ALWRITY_ENABLED_FEATURES", "").strip().lower() == "podcast"

# In podcast mode, don't import heavy onboarding endpoints
# They trigger heavy dependencies (exa_py, etc.)
if _is_podcast:
    __all__ = []
else:
    from .onboarding_endpoints import (
        health_check,
        get_onboarding_status,
        get_onboarding_progress_full,
        get_step_data,
        complete_step,
        skip_step,
        validate_step_access,
        get_api_keys,
        save_api_key,
        validate_api_keys,
        start_onboarding,
        complete_onboarding,
        reset_onboarding,
        get_resume_info,
        get_onboarding_config,
        generate_writing_personas,
        generate_writing_personas_async,
        get_persona_task_status,
        assess_persona_quality,
        regenerate_persona,
        get_persona_generation_options
    )

    __all__ = [
        'health_check',
        'get_onboarding_status',
        'get_onboarding_progress_full',
        'get_step_data',
        'complete_step',
        'skip_step',
        'validate_step_access',
        'get_api_keys',
        'save_api_key',
        'validate_api_keys',
        'start_onboarding',
        'complete_onboarding',
        'reset_onboarding',
        'get_resume_info',
        'get_onboarding_config',
        'generate_writing_personas',
        'generate_writing_personas_async',
        'get_persona_task_status',
        'assess_persona_quality',
        'regenerate_persona',
        'get_persona_generation_options'
    ] 