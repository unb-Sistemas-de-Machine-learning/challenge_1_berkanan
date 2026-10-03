from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.analysis import router as analysis_router


from contextlib import asynccontextmanager
from api.services.fact_checker_service import get_checker

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Carrega o checker e vectorstore na inicialização
    get_checker()
    print("[startup] Fact-Checker carregado com sucesso.")
    yield


app = FastAPI(
    title="Berkanan Fact Checker API",
    description="API para verificação de informações nutricionais relacionadas ao diabetes",
    version="1.0.0",
    lifespan=lifespan
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(analysis_router)


@app.get("/health")
async def health():
    return {
        "status": "ok"
    }