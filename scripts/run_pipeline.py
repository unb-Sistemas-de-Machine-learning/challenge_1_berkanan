"""
run_pipeline.py — Executa coleta, treinamento e embeddings com segurança.

A raspagem precisa terminar primeiro porque alimenta tanto o dataset quanto a
base de conhecimento. Depois disso, o treinamento do classificador e a geração
dos embeddings rodam em processos separados e em paralelo.

Uso:
    python scripts/run_pipeline.py
    python scripts/run_pipeline.py --skip-scrape
"""
import argparse
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

# Garante saída UTF-8 no Windows para evitar UnicodeEncodeError
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_python_executable() -> str:
    """Retorna o interpretador Python do virtualenv local se disponível."""
    if sys.prefix != getattr(sys, "base_prefix", sys.prefix):
        return sys.executable
    for venv_dir in ["venv", ".venv"]:
        venv_py = os.path.join(PROJECT_ROOT, venv_dir, "Scripts", "python.exe")
        if os.path.exists(venv_py):
            return venv_py
        venv_py_unix = os.path.join(PROJECT_ROOT, venv_dir, "bin", "python")
        if os.path.exists(venv_py_unix):
            return venv_py_unix
    return sys.executable


PYTHON = get_python_executable()



def run_step(label: str, args: list[str]) -> None:
    """Executa uma etapa e interrompe o pipeline se ela falhar."""
    print(f"\n{'=' * 60}\n{label}\n{'=' * 60}", flush=True)
    result = subprocess.run([PYTHON, *args], cwd=PROJECT_ROOT)
    if result.returncode != 0:
        raise RuntimeError(
            f"A etapa '{label}' terminou com código {result.returncode}."
        )


def prepare_dataset_and_train() -> None:
    """Gera os CSVs e treina o classificador, em sequência."""
    run_step("ETAPA 2A: dataset", ["scripts/dataset_builder.py"])
    run_step(
        "ETAPA 2B: treinamento do classificador",
        ["scripts/fact_checker.py", "--train"],
    )


def ingest_embeddings() -> None:
    """Gera embeddings e popula o ChromaDB."""
    run_step("ETAPA 2C: embeddings e ChromaDB", ["scripts/batch_ingest.py"])


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Popula a base e treina o classificador em paralelo."
    )
    parser.add_argument(
        "--skip-scrape",
        action="store_true",
        help="Reutiliza os arquivos já existentes em data/raw.",
    )
    args = parser.parse_args()

    try:
        if not args.skip_scrape:
            run_step("ETAPA 1: raspagem das fontes", ["scripts/scraper.py"])

        print(
            "\nAs etapas 2A/2B e 2C serão executadas em paralelo "
            "(dataset/treino de um lado; embeddings do outro).",
            flush=True,
        )
        with ThreadPoolExecutor(max_workers=2) as executor:
            jobs = [
                executor.submit(prepare_dataset_and_train),
                executor.submit(ingest_embeddings),
            ]
            for job in jobs:
                job.result()

        print("\n✔ Pipeline concluído: modelo treinado e ChromaDB atualizado.")
        return 0
    except (OSError, RuntimeError) as error:
        print(f"\n✗ Pipeline interrompido: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
