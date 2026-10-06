from fastapi import APIRouter, Depends
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session
import logging

from db.database import (
    get_db,
    get_recent_analyses_orm,
    insert_analysis_orm,
)

from api.schemas.analysis import (
    AnalysisRequest,
    AnalysisHistoryResponse,
    AnalysisResponse,
)

from api.services.fact_checker_service import analyze_claim


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api",
    tags=["analysis"]
)


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/history", response_model=list[AnalysisHistoryResponse])
def history(db: Session = Depends(get_db)):
    analyses = get_recent_analyses_orm(db)
    return analyses


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze(
    request: AnalysisRequest,
    db: Session = Depends(get_db),
):
    #    Pipeline de análise (ML + RAG + Gemini).
    result = await run_in_threadpool(
        analyze_claim,
        request.text
    )

    #    Persistência é opcional. Se o banco estiver fora, a análise
    #    ainda é devolvida ao usuário (sem id nem timestamp).
    record = None
    try:
        record = insert_analysis_orm(
            db=db,
            input_text=result["input_text"],
            classification=result["classification"],
            confidence_score=result["confidence_score"],
            matched_sources=result["matched_sources"],
            model_version=result["model_version"],
            llm_explanation=result.get("llm_explanation"),
            llm_model=result.get("llm_model"),
            response_time_ms=result["response_time_ms"],
        )
    except Exception as exc:
        logger.exception(
            "Falha ao persistir análise (resposta ainda será enviada): %s",
            exc,
        )
        try:
            db.rollback()
        except Exception:
            pass

    if record is not None:
        return AnalysisResponse(
            id=record.id,
            input_text=record.input_text,
            classification=record.classification,
            confidence_score=record.confidence_score,
            threshold=result.get("threshold", 0.0),
            llm_explanation=result.get("llm_explanation"),
            matched_sources=record.matched_sources or [],
            model_version=record.model_version,
            timestamp=record.analysis_date,
            llm_model=record.llm_model,
            rag_sources_count=record.rag_sources_count or 0,
            response_time_ms=record.response_time_ms or 0,
        )

    return AnalysisResponse(
        id=None,
        input_text=result["input_text"],
        classification=result["classification"],
        confidence_score=result["confidence_score"],
        threshold=result.get("threshold", 0.0),
        llm_explanation=result.get("llm_explanation"),
        matched_sources=result.get("matched_sources") or [],
        model_version=result["model_version"],
        timestamp=None,
        llm_model=result.get("llm_model"),
        rag_sources_count=len(result.get("matched_sources") or []),
        response_time_ms=result["response_time_ms"],
    )