"""
database.py — Camada de acesso ao PostgreSQL para o Fact-Checker.

Suporta SQLAlchemy 2.0 (ORM) para integração com FastAPI (Fases 3 e 4)
e psycopg2 puro com context-manager para operações diretas/scripts legados.
"""
import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

# Carrega variáveis de ambiente do .env se disponível
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from sqlalchemy import create_engine, select, desc
from sqlalchemy.orm import sessionmaker, Session
from db.models import Base, AnalysisHistory

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "factchecker")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASS = os.getenv("DB_PASS", "adminpassword")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# SQLAlchemy Engine e SessionFactory
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Gerador de sessão SQLAlchemy para injeção de dependência no FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Cria tabelas no PostgreSQL via SQLAlchemy (se o banco estiver disponível)."""
    Base.metadata.create_all(bind=engine)


# ====================================================================
# Camada psycopg2 (compatibilidade direta com scripts existentes)
# ====================================================================

@contextmanager
def get_connection():
    """Context-manager que abre, faz commit e fecha a conexão automaticamente.
    Em caso de exceção, faz rollback."""
    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT,
        dbname=DB_NAME, user=DB_USER, password=DB_PASS
    )
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def insert_analysis(input_text: str, classification: str,
                    confidence_score: float, matched_sources: list,
                    model_version: str = "v1.0") -> dict | None:
    """Insere um registro de análise e retorna a linha criada."""
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                INSERT INTO Analysis_History
                    (input_text, classification, confidence_score,
                     matched_sources, model_version)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING *;
            """, (
                input_text,
                classification,
                round(confidence_score, 4),
                json.dumps(matched_sources, ensure_ascii=False),
                model_version,
            ))
            return dict(cur.fetchone())


def insert_analysis_orm(db: Session, input_text: str, classification: str,
                        confidence_score: float, matched_sources: list,
                        model_version: str = "v1.0") -> AnalysisHistory:
    """Insere um registro de análise utilizando SQLAlchemy ORM."""
    record = AnalysisHistory(
        input_text=input_text,
        classification=classification,
        confidence_score=round(confidence_score, 4),
        matched_sources=matched_sources,
        model_version=model_version,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_recent_analyses(limit: int = 20) -> list[dict]:
    """Retorna as análises mais recentes."""
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT * FROM Analysis_History
                ORDER BY analysis_date DESC
                LIMIT %s;
            """, (limit,))
            return [dict(row) for row in cur.fetchall()]


def get_recent_analyses_orm(db: Session, limit: int = 20) -> list[AnalysisHistory]:
    """Retorna análises recentes via SQLAlchemy ORM."""
    stmt = select(AnalysisHistory).order_by(desc(AnalysisHistory.analysis_date)).limit(limit)
    return list(db.scalars(stmt).all())


def search_analyses(query: str) -> list[dict]:
    """Busca análises cujo input_text contenha a query (case-insensitive)."""
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT * FROM Analysis_History
                WHERE input_text ILIKE %s
                ORDER BY analysis_date DESC;
            """, (f"%{query}%",))
            return [dict(row) for row in cur.fetchall()]


# ---------------------------------------------------------------------------
# Smoke-test rápido (roda só quando chamado diretamente)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    try:
        row = insert_analysis(
            input_text="Chá de folha de manga cura diabetes em 3 dias.",
            classification="FAKE",
            confidence_score=0.985,
            matched_sources=[{"source": "SBD_diretriz_2024.pdf", "page": 12}],
        )
        print("INSERT OK:", row)

        rows = get_recent_analyses(5)
        print(f"Últimas {len(rows)} análises:", rows)
    except Exception as e:
        print(f"Erro (o PostgreSQL está rodando?): {e}")
