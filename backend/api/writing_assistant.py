from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Any, Dict
from loguru import logger

from services.writing_assistant import WritingAssistantService


router = APIRouter(prefix="/api/writing-assistant", tags=["writing-assistant"])


class SuggestRequest(BaseModel):
    text: str
    max_results: int | None = 1


class SourceModel(BaseModel):
    title: str
    url: str
    text: str | None = ""
    author: str | None = ""
    published_date: str | None = ""
    score: float


class SuggestionModel(BaseModel):
    text: str
    confidence: float
    sources: List[SourceModel]


class SuggestResponse(BaseModel):
    success: bool
    suggestions: List[SuggestionModel]


assistant_service = WritingAssistantService()


@router.post("/suggest", response_model=SuggestResponse)
async def suggest_endpoint(req: SuggestRequest) -> SuggestResponse:
    try:
        suggestions = await assistant_service.suggest(req.text, req.max_results or 1)
        return SuggestResponse(
            success=True,
            suggestions=[
                SuggestionModel(
                    text=s.text,
                    confidence=s.confidence,
                    sources=[
                        SourceModel(**src) for src in s.sources
                    ],
                )
                for s in suggestions
            ],
        )
    except Exception as e:
        logger.error(f"Writing assistant error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


