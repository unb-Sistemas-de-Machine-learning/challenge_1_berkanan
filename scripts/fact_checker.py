"""
fact_checker.py — Motor central do Fact-Checker de Diabetes e Nutrição.

Conecta os três componentes:
  1. ChromaDB (base de conhecimento) → busca por similaridade
  2. Classificador FAKE/REAL (scripts/classifier.py) → modelo vencedor da
     comparação em train_model.py + threshold calibrado em
     calibrate_and_evaluate.py
  3. PostgreSQL (Analysis_History) → persiste resultados

Uso:
  python scripts/fact_checker.py "Chá de manga cura diabetes"
  python scripts/fact_checker.py --train
  python scripts/fact_checker.py --interactive
"""
import os
import sys
import argparse
from datetime import datetime

# Garante saída UTF-8 no Windows para evitar UnicodeEncodeError
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Adiciona o diretório pai ao path para imports relativos
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

import classifier as clf  # scripts/classifier.py — treino/inferência

# Modelo multilíngue — mesmo do batch_ingest
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


class DiabetesFactChecker:
    """Orquestrador: classifica alegações e busca evidências."""

    def __init__(self, chroma_dir: str, model_path: str | None = None):
        self.chroma_dir = chroma_dir
        self.model_path = model_path or clf.MODEL_PATH
        self.classifier = None
        self.vectorstore = None

    # ------------------------------------------------------------------
    # 1. Treinamento do classificador
    # ------------------------------------------------------------------
    def train(self, train_csv: str):
        """Treina o pipeline vencedor (train_model.py + calibrate_and_evaluate.py
        já devem ter rodado antes, para existir models/cv_results.json e
        models/training_metadata.json) e exporta o artefato final."""
        clf.train_and_export(
            train_path=train_csv,
            model_out_path=self.model_path,
        )
        # invalida cache em memória para forçar recarregar o novo artefato
        self.classifier = None

    def _load_classifier(self):
        """Carrega o classificador do disco (models/classifier_v2.joblib)."""
        if self.classifier is None:
            self.classifier = clf.load_model(self.model_path)

    # ------------------------------------------------------------------
    # 2. Busca por similaridade no ChromaDB
    # ------------------------------------------------------------------
    def _load_vectorstore(self):
        """Carrega o ChromaDB."""
        if self.vectorstore is None:
            from langchain_huggingface import HuggingFaceEmbeddings
            from langchain_community.vectorstores import Chroma

            if not os.path.exists(self.chroma_dir):
                print("⚠ ChromaDB não encontrado. Rode batch_ingest.py primeiro.")
                return
            embeddings = HuggingFaceEmbeddings(
                model_name=EMBEDDING_MODEL,
                encode_kwargs={"normalize_embeddings": True},
            )
            self.vectorstore = Chroma(
                persist_directory=self.chroma_dir,
                embedding_function=embeddings,
            )

    def search_evidence(self, claim: str, k: int = 3) -> list[dict]:
        """Busca os k chunks mais similares à alegação no ChromaDB."""
        self._load_vectorstore()
        if self.vectorstore is None:
            return []

        results = self.vectorstore.similarity_search_with_score(claim, k=k)
        evidence = []
        for doc, score in results:
            evidence.append({
                "text": doc.page_content[:300],
                "source": doc.metadata.get("source_file", "desconhecido"),
                "similarity": round(float(1 - score), 4),  # Converte distância em similaridade
            })
        return evidence

    # ------------------------------------------------------------------
    # 3. Classificação completa
    # ------------------------------------------------------------------
    def check(self, claim: str, save_to_db: bool = False) -> dict:
        """Pipeline completo: classifica + busca evidências + (opcionalmente) salva."""
        self._load_classifier()

        # Classificação — delega inteiramente ao classifier.py (modelo +
        # threshold calibrado). p_fake é sempre a probabilidade de FAKE,
        # independentemente do rótulo final.
        prediction = clf.predict(claim, model=self.classifier)
        classification = prediction["label"]
        p_fake = prediction["p_fake"]
        threshold = prediction["threshold"]

        # Busca evidências no ChromaDB
        evidence = self.search_evidence(claim)

        result = {
            "input_text": claim,
            "classification": classification,
            "p_fake": p_fake,
            "threshold": threshold,
            "matched_sources": evidence,
            "model_version": self.classifier["model_name"],
            "timestamp": datetime.now().isoformat(),
        }

        # Persiste no PostgreSQL (se disponível e solicitado)
        if save_to_db:
            try:
                from db.database import insert_analysis
                row = insert_analysis(
                    input_text=claim,
                    classification=classification,
                    confidence_score=p_fake,
                    matched_sources=evidence,
                    model_version=result["model_version"],
                )
                result["db_id"] = str(row["id"])
                print("  ✔ Resultado salvo no PostgreSQL")
            except Exception as e:
                print(f"  ⚠ Não foi possível salvar no DB: {e}")

        return result

    # ------------------------------------------------------------------
    # 4. Modo interativo
    # ------------------------------------------------------------------
    def interactive(self):
        """Loop interativo para testar alegações."""
        print("=" * 60)
        print("  FACT-CHECKER DE DIABETES E NUTRIÇÃO")
        print("  Digite uma alegação para verificar. 'sair' para encerrar.")
        print("=" * 60)

        while True:
            claim = input("\n🔍 Alegação: ").strip()
            if claim.lower() in ("sair", "exit", "quit", ""):
                print("Até logo!")
                break

            result = self.check(claim)
            self._print_result(result)

    @staticmethod
    def _print_result(result: dict):
        """Formata e imprime o resultado."""
        label = result["classification"]
        p_fake = result["p_fake"]

        emoji = {"FAKE": "❌", "REAL": "✅"}.get(label, "❓")

        print(f"\n{emoji} Classificação: {label}")
        print(f"   P(FAKE): {p_fake:.1%}  (threshold={result['threshold']})")

        if result["matched_sources"]:
            print(f"\n   📚 Evidências encontradas ({len(result['matched_sources'])}):")
            for i, src in enumerate(result["matched_sources"], 1):
                print(f"      {i}. [{src['source']}] (sim={src['similarity']:.2f})")
                print(f"         \"{src['text'][:120]}...\"")
        else:
            print("\n   📚 Nenhuma evidência encontrada na base de conhecimento.")


# ======================================================================
# CLI
# ======================================================================
def main():
    parser = argparse.ArgumentParser(
        description="Fact-Checker de Diabetes e Nutrição"
    )
    parser.add_argument("claim", nargs="?", help="Alegação a verificar")
    parser.add_argument("--train", action="store_true", help="Treinar o modelo")
    parser.add_argument("--interactive", "-i", action="store_true",
                        help="Modo interativo")
    parser.add_argument("--save-db", action="store_true",
                        help="Salvar resultado no PostgreSQL")
    args = parser.parse_args()

    chroma_dir = os.path.join(PROJECT_ROOT, "knowledge_base", "chromadb")
    checker = DiabetesFactChecker(chroma_dir)

    if args.train:
        train_csv = os.path.join(
            PROJECT_ROOT, "data", "processed",
            "diabetes_nutrition_dataset_train.csv"
        )
        checker.train(train_csv)
        return

    if args.interactive:
        checker.interactive()
        return

    if args.claim:
        result = checker.check(args.claim, save_to_db=args.save_db)
        checker._print_result(result)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()