"""
Story Writer Service

Core service for generating stories using prompt chaining approach.
Migrated from ToBeMigrated/ai_writers/ai_story_writer/ai_story_generator.py
"""

from typing import Dict, Any, Optional, List
from loguru import logger
from fastapi import HTTPException
import json

from services.llm_providers.main_text_generation import llm_text_gen
from services.story_writer.service_components import (
    StoryContentMixin,
    StoryOutlineMixin,
    StoryServiceBase,
    StorySetupMixin,
)


class StoryWriterService(
    StoryContentMixin,
    StorySetupMixin,
    StoryOutlineMixin,
    StoryServiceBase,
):
    """Facade class combining story writer behaviours via modular mixins."""

    __slots__ = ()
