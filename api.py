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

# --------------------------------------------------------------------------- #
# Startup: carrega o modelo uma única vez                                      #
# --------------------------------------------------------------------------- #
_model = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _model
    _model = clf.load_model()
    print(f"[startup] modelo '{_model['model_name']}' carregado — threshold={_model['threshold']}")
    yield
    _model = None


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


class PredictResponse(BaseModel):
    label: str       # "FAKE" | "REAL"
    p_fake: float    # probabilidade da classe FAKE (0-1)
    threshold: float # limiar de decisão calibrado


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
    if _model is None:
        raise HTTPException(status_code=503, detail="Modelo ainda não carregado.")
    return {
        "status": "ok",
        "model": _model["model_name"],
        "threshold": _model["threshold"],
    }


@app.post("/predict", response_model=PredictResponse, tags=["classificador"])
def predict(body: PredictRequest):
    """Classifica uma afirmação como FAKE ou REAL.

    - **text**: afirmação em português sobre diabetes ou nutrição
    """
    if _model is None:
        raise HTTPException(status_code=503, detail="Modelo ainda não carregado.")
    if not body.text.strip():
        raise HTTPException(status_code=422, detail="Campo 'text' não pode ser vazio.")
    return clf.predict(body.text, model=_model)
