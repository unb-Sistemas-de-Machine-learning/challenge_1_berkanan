from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


Classification = Literal["REAL", "FAKE", "INCONCLUSIVE", "PARTIALLY_TRUE"]


class AnalysisRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=3,
        description="Afirmação ou texto que será analisado."
    )


class MatchedSource(BaseModel):
    text: str
    source: str
    similarity: float = Field(ge=0, le=1)


class AnalysisResponse(BaseModel):
    # id e timestamp ficam nulos quando o PostgreSQL está indisponível:
    # a análise é devolvida mesmo sem ser persistida no histórico.
    id: UUID | None = None
    input_text: str
    classification: Classification
    confidence_score: float = Field(ge=0, le=1)
    threshold: float = Field(ge=0, le=1)
    llm_explanation: str | None = None
    matched_sources: list[MatchedSource]
    model_version: str
    timestamp: datetime | None = None
    llm_model: str | None = None
    rag_sources_count: int = Field(ge=0)
    response_time_ms: int = Field(ge=0)


class AnalysisHistoryResponse(BaseModel):
    id: UUID
    input_text: str
    classification: Classification
    confidence_score: float | None = Field(default=None, ge=0, le=1)
    analysis_date: datetime
    user_feedback: bool | None = None
    model_version: str | None = None
    llm_explanation: str | None = None
    llm_model: str | None = None
    rag_sources_count: int = Field(ge=0)
    response_time_ms: int | None = Field(default=None, ge=0)
    matched_sources: list[MatchedSource] = Field(default_factory=list)

    model_config = {"from_attributes": True}

    @field_validator("matched_sources", mode="before")
    @classmethod
    def empty_sources_for_legacy_rows(cls, value):
        return value or []