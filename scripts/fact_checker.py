"""
fact_checker.py — Motor central do Fact-Checker de Diabetes e Nutrição.

Conecta os três componentes:
  1. ChromaDB (base de conhecimento) → busca por similaridade
  2. Modelo de classificação (TF-IDF + Logistic Regression) → FAKE/REAL
  3. PostgreSQL (Analysis_History) → persiste resultados

Uso:
  python scripts/fact_checker.py "Chá de manga cura diabetes"
  python scripts/fact_checker.py --interactive
"""
import os
import sys
import json
import argparse
import numpy as np
from datetime import datetime

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# Adiciona o diretório pai ao path para imports relativos
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report
import joblib

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# Modelo multilíngue — mesmo do batch_ingest
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
MODEL_VERSION = "tfidf-logreg-v1"


class DiabetesFactChecker:
    """Orquestrador: classifica alegações e busca evidências."""

    def __init__(self, chroma_dir: str, model_path: str | None = None):
        self.chroma_dir = chroma_dir
        self.model_path = model_path or os.path.join(
            PROJECT_ROOT, "data", "processed", "classifier.joblib"
        )
        self.classifier = None
        self.vectorstore = None

    # ------------------------------------------------------------------
    # 1. Treinamento do classificador
    # ------------------------------------------------------------------
    def train(self, train_csv: str, test_csv: str | None = None):
        """Treina o pipeline TF-IDF + LogisticRegression."""
        print("=" * 60)
        print("TREINANDO CLASSIFICADOR")
        print("=" * 60)

        df_train = pd.read_csv(train_csv)
        print(f"Dados de treino: {len(df_train)} registros")
        print(df_train["label"].value_counts().to_string())

        pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(
                max_features=5000,
                ngram_range=(1, 2),
                sublinear_tf=True,
            )),
            ("clf", LogisticRegression(
                max_iter=1000,
                class_weight="balanced",
                C=1.0,
            )),
        ])

        X_train = df_train["cleaned_text"].fillna(df_train["text"])
        y_train = df_train["label"]
        pipeline.fit(X_train, y_train)

        # Avalia no teste se disponível
        if test_csv and os.path.exists(test_csv):
            df_test = pd.read_csv(test_csv)
            X_test = df_test["cleaned_text"].fillna(df_test["text"])
            y_test = df_test["label"]
            y_pred = pipeline.predict(X_test)
            print("\n--- Relatório no conjunto de teste ---")
            print(classification_report(y_test, y_pred))

        # Salva
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(pipeline, self.model_path)
        self.classifier = pipeline
        print(f"\n✔ Modelo salvo em {self.model_path}")

    def _load_classifier(self):
        """Carrega o classificador do disco."""
        if self.classifier is None:
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(
                    f"Modelo não encontrado em {self.model_path}. "
                    "Rode primeiro: python scripts/fact_checker.py --train"
                )
            self.classifier = joblib.load(self.model_path)

    # ------------------------------------------------------------------
    # 2. Busca por similaridade no ChromaDB
    # ------------------------------------------------------------------
    def _load_vectorstore(self):
        """Carrega o ChromaDB."""
        if self.vectorstore is None:
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

        # Classificação
        proba = self.classifier.predict_proba([claim])[0]
        classes = self.classifier.classes_
        pred_idx = np.argmax(proba)
        classification = classes[pred_idx]
        confidence = float(proba[pred_idx])

        # Se confiança é baixa, marca como INCONCLUSIVE
        if confidence < 0.6:
            classification = "INCONCLUSIVE"

        # Busca evidências no ChromaDB
        evidence = self.search_evidence(claim)

        result = {
            "input_text": claim,
            "classification": classification,
            "confidence_score": round(confidence, 4),
            "matched_sources": evidence,
            "model_version": MODEL_VERSION,
            "timestamp": datetime.now().isoformat(),
        }

        # Persiste no PostgreSQL (se disponível e solicitado)
        if save_to_db:
            try:
                from db.database import insert_analysis
                row = insert_analysis(
                    input_text=claim,
                    classification=classification,
                    confidence_score=confidence,
                    matched_sources=evidence,
                    model_version=MODEL_VERSION,
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
        confidence = result["confidence_score"]

        # Emojis por classificação
        emoji = {"FAKE": "❌", "REAL": "✅", "INCONCLUSIVE": "⚠️"}.get(label, "❓")

        print(f"\n{emoji} Classificação: {label}")
        print(f"   Confiança: {confidence:.1%}")

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
        test_csv = os.path.join(
            PROJECT_ROOT, "data", "processed",
            "diabetes_nutrition_dataset_test.csv"
        )
        checker.train(train_csv, test_csv)
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