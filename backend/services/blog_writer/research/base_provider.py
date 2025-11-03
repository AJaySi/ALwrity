"""
Base Research Provider Interface

Abstract base class for research provider implementations.
Ensures consistency across different research providers (Google, Exa, etc.)
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class ResearchProvider(ABC):
    """Abstract base class for research providers."""
    
    @abstractmethod
    async def search(
        self,
        prompt: str,
        topic: str,
        industry: str,
        target_audience: str,
        config: Any,  # ResearchConfig
        user_id: str
    ) -> Dict[str, Any]:
        """Execute research and return raw results."""
        pass
    
    @abstractmethod
    def get_provider_enum(self):
        """Return APIProvider enum for subscription tracking."""
        pass
    
    @abstractmethod
    def estimate_tokens(self) -> int:
        """Estimate token usage for pre-flight validation."""
        pass

