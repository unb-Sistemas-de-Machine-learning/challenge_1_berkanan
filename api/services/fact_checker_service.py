import logging
import os
import shutil
import time
from pathlib import Path

from scripts.fact_checker import DiabetesFactChecker


logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BUNDLED_CHROMA_DIR = PROJECT_ROOT / "knowledge_base" / "chromadb"
CHROMA_DIR = os.getenv("CHROMA_PERSIST_DIRECTORY", "knowledge_base/chromadb")

# Inicialização global para não carregar o modelo a cada requisição
_checker = None


def ensure_chroma_index(target_dir: str, bundled_dir: Path = BUNDLED_CHROMA_DIR) -> None:
    """Copia o índice versionado para target_dir quando ele ainda não tem um.

    Em produção, CHROMA_PERSIST_DIRECTORY aponta para um volume persistente
    (ex.: /var/chroma) que começa vazio. Um índice já existente no volume
    nunca é sobrescrito.
    """
    target = Path(target_dir).resolve()
    bundled = bundled_dir.resolve()
    if target == bundled or (target / "chroma.sqlite3").exists():
        return
    if not (bundled / "chroma.sqlite3").exists():
        logger.warning("Índice do ChromaDB não encontrado em %s; RAG ficará vazio.", bundled)
        return

    shutil.copytree(bundled, target, dirs_exist_ok=True)
    logger.info("Índice do ChromaDB copiado de %s para %s.", bundled, target)


def get_checker():
    global _checker
    if _checker is None:
        ensure_chroma_index(CHROMA_DIR)
        _checker = DiabetesFactChecker(CHROMA_DIR)
        _checker._load_classifier()
        _checker._load_vectorstore()
    return _checker


def analyze_claim(text: str) -> dict:
    started_at = time.perf_counter()
    checker = get_checker()

    result = checker.check(
        text,
        save_to_db=False
    )
    
    # Garantir que o nome bate com o esperado no bd/routes
    if "confidence_score" not in result:
        result["confidence_score"] = result.get("p_fake", 0.0)

    result["response_time_ms"] = max(
        0,
        int((time.perf_counter() - started_at) * 1000),
    )
    return result