import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from api.routes.analysis import router as analysis_router
from api.services.fact_checker_service import get_checker


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_checker()
    print("[startup] Fact-Checker carregado com sucesso.")
    yield


app_env = (os.getenv("APP_ENV") or os.getenv("ENV") or "development").strip().lower()
default_frontend_origins = (
    "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"
    if app_env == "development"
    else "http://localhost:5173,http://localhost:3000"
)

frontend_origins = [
    origin.strip()
    for origin in os.getenv("FRONTEND_ORIGINS", default_frontend_origins).split(",")
    if origin.strip()
]

app = FastAPI(
    title="Berkanan Fact Checker API",
    description="API para verificação de informações nutricionais relacionadas ao diabetes",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=frontend_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analysis_router)


@app.get("/health")
async def health():
    return {"status": "ok"}