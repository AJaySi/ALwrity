"""
Frequency Calculator Utility
Calculates next execution time based on frequency string.
"""

from datetime import datetime, timedelta
from typing import Optional


def calculate_next_execution(frequency: str, base_time: Optional[datetime] = None) -> datetime:
    """
    Calculate next execution time based on frequency.
    
    Args:
        frequency: Frequency string ('Daily', 'Weekly', 'Monthly', 'Quarterly')
        base_time: Base time to calculate from (defaults to now if None)
        
    Returns:
        Next execution datetime
    """
    if base_time is None:
        base_time = datetime.utcnow()
    
    frequency_map = {
        'Daily': timedelta(days=1),
        'Weekly': timedelta(weeks=1),
        'Monthly': timedelta(days=30),
        'Quarterly': timedelta(days=90)
    }
    
    delta = frequency_map.get(frequency, timedelta(days=1))
    return base_time + delta

