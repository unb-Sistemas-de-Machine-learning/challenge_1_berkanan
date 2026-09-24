"""
models.py — Modelos declarativos SQLAlchemy 2.0 para persistência de análises.

Compatível com o schema PostgreSQL (schema.sql) e projetado para uso
tanto nos scripts de inferência quanto nas rotas FastAPI (Fases 3 e 4).
"""
import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Text,
    Numeric,
    DateTime,
    Boolean,
    CheckConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.types import JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class AnalysisHistory(Base):
    """Mapeamento da tabela Analysis_History."""

    __tablename__ = "analysis_history"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    input_text: Mapped[str] = mapped_column(Text, nullable=False)
    classification: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    confidence_score: Mapped[float | None] = mapped_column(
        Numeric(5, 4),
        nullable=True,
    )
    # Suporta JSONB no PostgreSQL com fallback para JSON genérico em outros bancos
    matched_sources: Mapped[list] = mapped_column(
        JSONB().with_variant(JSON, "sqlite"),
        nullable=True,
        default=list,
    )
    analysis_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    user_feedback: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    model_version: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Colunas RAG adicionadas
    llm_explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    llm_model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    rag_sources_count: Mapped[int | None] = mapped_column(nullable=True, default=0)
    response_time_ms: Mapped[int | None] = mapped_column(nullable=True)

    __table_args__ = (
        CheckConstraint(
            "classification IN ('REAL', 'FAKE', 'INCONCLUSIVE', 'PARTIALLY_TRUE')",
            name="check_analysis_classification",
        ),
        CheckConstraint(
            "confidence_score >= 0 AND confidence_score <= 1",
            name="check_analysis_confidence_score",
        ),
    )

    def to_dict(self) -> dict:
        """Converte a instância para dicionário serializável."""
        return {
            "id": str(self.id),
            "input_text": self.input_text,
            "classification": self.classification,
            "confidence_score": float(self.confidence_score) if self.confidence_score is not None else None,
            "matched_sources": self.matched_sources or [],
            "analysis_date": self.analysis_date.isoformat() if self.analysis_date else None,
            "user_feedback": self.user_feedback,
            "model_version": self.model_version,
        }
