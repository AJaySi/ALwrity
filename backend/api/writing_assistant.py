from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Any, Dict
from loguru import logger

from services.writing_assistant import WritingAssistantService
from middleware.auth_middleware import get_current_user


router = APIRouter(prefix="/api/writing-assistant", tags=["writing-assistant"])


class SuggestRequest(BaseModel):
    text: str
    cursor_position: int | None = None


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
    message: str = ""


assistant_service = WritingAssistantService()


@router.post("/suggest", response_model=SuggestResponse)
async def suggest_endpoint(req: SuggestRequest, current_user: Dict[str, Any] = Depends(get_current_user)) -> SuggestResponse:
    try:
        user_id = current_user.get("id")
        suggestions = await assistant_service.suggest(req.text, user_id=user_id, cursor_position=req.cursor_position)
        return SuggestResponse(
            success=len(suggestions) > 0,
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
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Writing assistant error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


