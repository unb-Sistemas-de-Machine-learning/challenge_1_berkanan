"""
database.py — Camada de acesso ao PostgreSQL para o Fact-Checker.

Funções reutilizáveis com context-manager, rollback em erro e tipagem clara.
"""
import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "factchecker")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASS = os.getenv("DB_PASS", "adminpassword")


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
