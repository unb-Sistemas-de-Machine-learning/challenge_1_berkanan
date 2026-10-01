from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.analysis import router as analysis_router


app = FastAPI(
    title="Berkanan Fact Checker API",
    description="API para verificação de informações nutricionais relacionadas ao diabetes",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000"
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