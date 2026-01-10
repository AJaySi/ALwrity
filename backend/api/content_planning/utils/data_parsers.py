"""
Data Parsing Utilities
Shared utilities for parsing and validating strategy data.
"""

import json
import re
from typing import Any, Optional, Dict, List


def parse_float(value: Any) -> Optional[float]:
    """
    Parse a value to float, handling various formats.
    
    Supports:
    - Numbers (int, float)
    - Strings with numbers
    - Percentages (e.g., "25%")
    - Suffixes (e.g., "10k", "5m")
    - Comma-separated numbers
    
    Args:
        value: Value to parse
        
    Returns:
        Parsed float value or None if parsing fails
    """
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        s = value.strip().lower().replace(",", "")
        # Handle percentage
        if s.endswith('%'):
            try:
                return float(s[:-1])
            except Exception:
                pass
        # Handle k/m suffix
        mul = 1.0
        if s.endswith('k'):
            mul = 1_000.0
            s = s[:-1]
        elif s.endswith('m'):
            mul = 1_000_000.0
            s = s[:-1]
        m = re.search(r"[-+]?\d*\.?\d+", s)
        if m:
            try:
                return float(m.group(0)) * mul
            except Exception:
                return None
    return None


def parse_int(value: Any) -> Optional[int]:
    """
    Parse a value to integer.
    
    Args:
        value: Value to parse
        
    Returns:
        Parsed integer value or None if parsing fails
    """
    f = parse_float(value)
    if f is None:
        return None
    try:
        return int(round(f))
    except Exception:
        return None


def parse_json(value: Any) -> Optional[Any]:
    """
    Parse a value to JSON (dict/list) or return as-is if already structured.
    
    Args:
        value: Value to parse
        
    Returns:
        Parsed JSON value, original value if already structured, or None
    """
    if value is None:
        return None
    if isinstance(value, (dict, list)):
        return value
    if isinstance(value, str):
        try:
            return json.loads(value)
        except Exception:
            # Accept plain strings in JSON columns
            return value
    return None


def parse_array(value: Any) -> Optional[List]:
    """
    Parse a value to array/list.
    
    Supports:
    - Lists (returned as-is)
    - JSON strings
    - Comma-separated strings
    
    Args:
        value: Value to parse
        
    Returns:
        Parsed list or None if parsing fails
    """
    if value is None:
        return None
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        # Try JSON first
        try:
            j = json.loads(value)
            if isinstance(j, list):
                return j
        except Exception:
            pass
        # Try comma-separated
        parts = [p.strip() for p in value.split(',') if p.strip()]
        return parts if parts else None
    return None


def parse_strategy_data(strategy_data: Dict[str, Any]) -> tuple[Dict[str, Any], Dict[str, str]]:
    """
    Parse and validate strategy data, returning cleaned data and warnings.
    
    Args:
        strategy_data: Raw strategy data dictionary
        
    Returns:
        Tuple of (cleaned_data, warnings_dict)
    """
    warnings: Dict[str, str] = {}
    cleaned = dict(strategy_data)
    
    # Numeric fields
    content_budget = parse_float(strategy_data.get('content_budget'))
    if strategy_data.get('content_budget') is not None and content_budget is None:
        warnings['content_budget'] = 'Could not parse number; saved as null'
    cleaned['content_budget'] = content_budget
    
    team_size = parse_int(strategy_data.get('team_size'))
    if strategy_data.get('team_size') is not None and team_size is None:
        warnings['team_size'] = 'Could not parse integer; saved as null'
    cleaned['team_size'] = team_size
    
    # Array fields
    array_fields = ['preferred_formats']
    for field in array_fields:
        if field in strategy_data:
            parsed = parse_array(strategy_data.get(field))
            if strategy_data.get(field) is not None and parsed is None:
                warnings[field] = 'Could not parse list; saved as null'
            cleaned[field] = parsed
    
    # JSON fields
    json_fields = [
        'business_objectives', 'target_metrics', 'performance_metrics', 'content_preferences',
        'consumption_patterns', 'audience_pain_points', 'buying_journey', 'seasonal_trends',
        'engagement_metrics', 'top_competitors', 'competitor_content_strategies', 'market_gaps',
        'industry_trends', 'emerging_trends', 'content_mix', 'optimal_timing', 'quality_metrics',
        'editorial_guidelines', 'brand_voice', 'traffic_sources', 'conversion_rates', 'content_roi_targets',
        'target_audience', 'content_pillars', 'ai_recommendations'
    ]
    for field in json_fields:
        if field in strategy_data:
            cleaned[field] = parse_json(strategy_data.get(field))
    
    # Boolean fields
    if 'ab_testing_capabilities' in strategy_data:
        cleaned['ab_testing_capabilities'] = bool(strategy_data.get('ab_testing_capabilities'))
    
    return cleaned, warnings
