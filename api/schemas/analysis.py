from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class AnalysisRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=3,
        description="Afirmação ou texto que será analisado."
    )


class AnalysisResponse(BaseModel):
    id: UUID | None = None
    input_text: str
    classification: str
    confidence_score: float
    threshold: float
    llm_explanation: str | None = None
    matched_sources: list[Any]
    model_version: str
    timestamp: datetime | None = None