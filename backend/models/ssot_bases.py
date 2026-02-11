"""
Shared declarative bases for SSOT SaaS schema.

Use a single Base per database domain so SSOT models can share metadata
and relationships reliably during mapper configuration and table creation.
"""

from sqlalchemy.orm import declarative_base

# Platform DB metadata (users, subscriptions, analytics)
PlatformBase = declarative_base()

# User data DB metadata (profiles, projects, assets, personas)
UserDataBase = declarative_base()
