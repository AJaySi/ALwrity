"""
Base class for SIF specialized agents.
"""
import traceback
import json
import asyncio
import re
from collections import Counter
from typing import List, Dict, Any, Optional
from datetime import datetime
from loguru import logger
from services.intelligence.txtai_service import TxtaiIntelligenceService
from services.intelligence.agents.core_agent_framework import BaseALwrityAgent, AgentAction, TaskProposal
from services.intelligence.sif_agents import SharedLLMWrapper, LocalLLMWrapper

try:
    # Try importing from pipeline first (standard location)
    from txtai.pipeline import Agent, LLM
    TXTAI_AVAILABLE = True
except ImportError:
    try:
        # Fallback to top-level import
        from txtai import Agent, LLM
        TXTAI_AVAILABLE = True
    except ImportError:
        TXTAI_AVAILABLE = False
        Agent = None
        LLM = None
        logger.warning("txtai not available, using fallback implementation")

class SIFBaseAgent(BaseALwrityAgent):
    def __init__(self, intelligence_service: TxtaiIntelligenceService, user_id: str, agent_type: str = "sif_agent", model_name: str = "Qwen/Qwen2.5-3B-Instruct", llm: Any = None, **kwargs):
        # Hybrid LLM Strategy:
        # 1. Shared LLM for external/high-quality generation
        self.shared_llm = SharedLLMWrapper(user_id)
        
        # 2. Local LLM for internal agent work (default for SIF agents)
        if llm is None:
            if not TXTAI_AVAILABLE:
                raise RuntimeError("txtai is required for SIF specialized agents but is not available")
            
            # Explicitly force task='language-generation' (txtai internal name) which maps to 'text-generation'
            # Using 'text-generation' directly fails because txtai mapping.get() defaults to 'text2text-generation'
            task_to_use = "language-generation"
            if any(x in model_name for x in ["Qwen", "Instruct", "GPT", "Llama"]):
                task_to_use = "language-generation"
            
            logger.info(f"[{self.__class__.__name__}] Initializing LocalLLMWrapper with model={model_name}, task={task_to_use}")
            llm = LocalLLMWrapper(model_name, task=task_to_use)
                
        self.intelligence = intelligence_service
        super().__init__(user_id, agent_type, model_name, llm, **kwargs)
        
    def _log_agent_operation(self, operation: str, **kwargs):
        """Standardized logging for agent operations."""
        logger.info(f"[{self.__class__.__name__}] {operation}")
        if kwargs:
            logger.debug(f"[{self.__class__.__name__}] Parameters: {kwargs}")

    def _create_txtai_agent(self):
        """
        SIF agents use the intelligence service directly, but we can expose
        capabilities via a standard agent interface if needed.
        """
        if not TXTAI_AVAILABLE or Agent is None:
            logger.warning(f"[{self.__class__.__name__}] txtai Agent not available (TXTAI_AVAILABLE={TXTAI_AVAILABLE}, Agent={Agent})")
            raise RuntimeError(f"[{self.__class__.__name__}] txtai Agent not available")
        
        # Return a simple agent that can use the LLM
        try:
            _llm_for_agent = self.llm
            for _ in range(3):
                _llm_for_agent = getattr(_llm_for_agent, "llm", _llm_for_agent)
            return Agent(llm=_llm_for_agent, tools=[])
        except Exception as e:
            logger.error(f"Failed to create txtai Agent for {self.__class__.__name__}: {e}")
            # Fail fast: Re-raise the exception instead of returning None
            raise e
