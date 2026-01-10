"""
Pydantic models for subscription API requests/responses.
"""

from pydantic import BaseModel
from typing import Optional, List


class PreflightOperationRequest(BaseModel):
    """Request model for pre-flight check operation."""
    provider: str
    model: Optional[str] = None
    tokens_requested: Optional[int] = 0
    operation_type: str
    actual_provider_name: Optional[str] = None


class PreflightCheckRequest(BaseModel):
    """Request model for pre-flight check."""
    operations: List[PreflightOperationRequest]
