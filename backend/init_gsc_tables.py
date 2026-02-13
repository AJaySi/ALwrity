#!/usr/bin/env python3
"""Initialize GSC service to create tables with expires_at column."""

from services.gsc_service import GSCService

def init_gsc_tables():
    """Initialize GSC service tables."""
    try:
        service = GSCService()
        service._init_gsc_tables()
        print('✅ GSC tables initialized successfully')
    except Exception as e:
        print(f'Error: {e}')
        raise

if __name__ == "__main__":
    init_gsc_tables()
