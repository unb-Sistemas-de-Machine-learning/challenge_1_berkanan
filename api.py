"""
api.py — FastAPI MVP para o classificador FAKE/REAL de diabetes/nutrição.

Endpoints:
    GET  /health   → status, nome do modelo e threshold calibrado
    POST /predict  → {"text": "..."} → {"label", "p_fake", "threshold"}

Uso local:
    uvicorn api:app --reload

Deploy (Render):
    buildCommand: pip install -r requirements-api.txt
    startCommand: uvicorn api:app --host 0.0.0.0 --port $PORT
"""

import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Garante que scripts/ seja encontrável independente do CWD
sys.path.insert(0, str(Path(__file__).resolve().parent / "scripts"))
import classifier as clf  # noqa: E402
from fact_checker import DiabetesFactChecker

# --------------------------------------------------------------------------- #
# Startup: carrega o modelo uma única vez                                      #
# --------------------------------------------------------------------------- #
_checker = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _checker
    chroma_dir = str(Path(__file__).resolve().parent / "knowledge_base" / "chromadb")
    _checker = DiabetesFactChecker(chroma_dir=chroma_dir)
    # Pré-carrega modelo e vectorstore
    _checker._load_classifier()
    _checker._load_vectorstore()
    print(f"[startup] Fact-Checker carregado: modelo '{_checker.classifier['model_name']}' — threshold={_checker.classifier['threshold']}")
    yield
    _checker = None


# --------------------------------------------------------------------------- #
# App                                                                          #
# --------------------------------------------------------------------------- #
app = FastAPI(
    title="Berkanan — Fact-Checker de Diabetes e Nutrição",
    description="Classifica afirmações sobre diabetes/nutrição como FAKE ou REAL.",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS aberto para o Streamlit Cloud poder chamar
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# --------------------------------------------------------------------------- #
# Schemas                                                                      #
# --------------------------------------------------------------------------- #
class PredictRequest(BaseModel):
    text: str


from typing import List, Dict, Any

class PredictResponse(BaseModel):
    label: str       # "FAKE" | "REAL"
    p_fake: float    # probabilidade da classe FAKE (0-1)
    threshold: float # limiar de decisão calibrado
    llm_explanation: str
    matched_sources: List[Dict[str, Any]]


class HealthResponse(BaseModel):
    status: str
    model: str
    threshold: float


# --------------------------------------------------------------------------- #
# Endpoints                                                                    #
# --------------------------------------------------------------------------- #
@app.get("/health", response_model=HealthResponse, tags=["infra"])
def health():
    """Verifica se a API está no ar e o modelo foi carregado."""
    if _checker is None or _checker.classifier is None:
        raise HTTPException(status_code=503, detail="Fact-Checker ainda não carregado.")
    return {
        "status": "ok",
        "model": _checker.classifier["model_name"],
        "threshold": _checker.classifier["threshold"],
    }


@app.post("/predict", response_model=PredictResponse, tags=["classificador"])
def predict(body: PredictRequest):
    """Classifica uma afirmação como FAKE ou REAL e gera explicação via RAG.

    - **text**: afirmação em português sobre diabetes ou nutrição
    """
    if _checker is None or _checker.classifier is None:
        raise HTTPException(status_code=503, detail="Fact-Checker ainda não carregado.")
    if not body.text.strip():
        raise HTTPException(status_code=422, detail="Campo 'text' não pode ser vazio.")
    
    result = _checker.check(body.text, save_to_db=False)
    
    return {
        "label": result["classification"],
        "p_fake": result["p_fake"],
        "threshold": result["threshold"],
        "llm_explanation": result.get("llm_explanation", "Explicação indisponível."),
        "matched_sources": result.get("matched_sources", [])
    }
