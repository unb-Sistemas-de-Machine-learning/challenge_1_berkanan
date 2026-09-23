"""
classifier.py — Fase 2 / Feature 3 (itens 1-2)

Interface simples de treino/inferência do classificador FAKE/REAL, usando
o melhor modelo + threshold calibrado encontrados nas etapas anteriores
(train_model.py e calibrate_and_evaluate.py).

Uso:
    # Treina no dataset completo e exporta models/classifier_v2.joblib
    python scripts/classifier.py --train

    # Classifica uma afirmação usando o modelo já exportado
    python scripts/classifier.py "Chá de manga cura diabetes"

    # Modo interativo
    python scripts/classifier.py --interactive

Uso programático (para o fact_checker.py ou a futura API):
    from classifier import load_model, predict
    model = load_model()
    result = predict("Canela cura diabetes", model=model)
    # result = {"label": "FAKE", "p_fake": 0.94, "threshold": 0.29}
"""

import argparse
import json
from pathlib import Path

import joblib
import pandas as pd

from train_model import OFF_SCOPE_HASHES, build_search_space

MODEL_PATH = Path("models/classifier_v2.joblib")
METADATA_PATH = Path("models/training_metadata.json")
CV_RESULTS_PATH = Path("models/cv_results.json")
DEFAULT_TRAIN_PATH = Path("data/processed/diabetes_nutrition_dataset_train.csv")

POSITIVE_LABEL = "FAKE"


def _load_clean_train(train_path: Path) -> pd.DataFrame:
    df = pd.read_csv(train_path)
    if "text_hash" in df.columns:
        df = df[~df["text_hash"].isin(OFF_SCOPE_HASHES)]
    return df


def _fix_ngram_range(params: dict) -> dict:
    fixed = dict(params)
    if "tfidf__ngram_range" in fixed:
        fixed["tfidf__ngram_range"] = tuple(fixed["tfidf__ngram_range"])
    return fixed


def train_and_export(
    train_path: Path = DEFAULT_TRAIN_PATH,
    cv_results_path: Path = CV_RESULTS_PATH,
    metadata_path: Path = METADATA_PATH,
    model_out_path: Path = MODEL_PATH,
):
    """Treina o modelo vencedor (definido em cv_results.json) em todo o
    dataset de treino e exporta o pipeline + threshold calibrado
    (definido em training_metadata.json, gerado pelo calibrate_and_evaluate.py)
    em um único artefato .joblib."""

    with open(cv_results_path, encoding="utf-8") as f:
        cv_results = json.load(f)
    best = max(cv_results, key=lambda r: r["cv_f1_fake"])
    model_name, best_params = best["model"], _fix_ngram_range(best["best_params"])

    with open(metadata_path, encoding="utf-8") as f:
        metadata = json.load(f)
    threshold = metadata["calibration"]["chosen_threshold"]

    df = _load_clean_train(train_path)
    X, y = df["cleaned_text"].astype(str), df["label"].astype(str)

    pipeline = build_search_space()[model_name]["pipeline"]
    pipeline.set_params(**best_params)
    pipeline.fit(X, y)

    fake_idx = list(pipeline.named_steps["clf"].classes_).index(POSITIVE_LABEL)

    artifact = {
        "pipeline": pipeline,
        "model_name": model_name,
        "best_params": best_params,
        "threshold": threshold,
        "fake_class_index": fake_idx,
        "trained_on_n_examples": len(df),
    }

    model_out_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifact, model_out_path)
    print(f"Modelo '{model_name}' (threshold={threshold}) exportado para {model_out_path}")
    print(f"Treinado com {len(df)} exemplos.")
    return artifact


def load_model(path: Path = MODEL_PATH):
    """Carrega o artefato exportado por train_and_export()."""
    if not Path(path).exists():
        raise FileNotFoundError(
            f"Modelo não encontrado em {path}. Rode "
            f"'python scripts/classifier.py --train' primeiro."
        )
    return joblib.load(path)


def predict(text: str, model=None) -> dict:
    """Classifica uma afirmação como FAKE ou REAL.

    Retorna: {"label": "FAKE"|"REAL", "p_fake": float, "threshold": float}
    """
    if model is None:
        model = load_model()

    p_fake = model["pipeline"].predict_proba([text])[0][model["fake_class_index"]]
    label = "FAKE" if p_fake >= model["threshold"] else "REAL"
    return {
        "label": label,
        "p_fake": round(float(p_fake), 4),
        "threshold": model["threshold"],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("text", nargs="?", help="Afirmação a classificar")
    parser.add_argument("--train", action="store_true", help="Treina e exporta o modelo")
    parser.add_argument("--interactive", action="store_true", help="Modo interativo")
    args = parser.parse_args()

    if args.train:
        train_and_export()
    elif args.interactive:
        model = load_model()
        print(f"Modelo: {model['model_name']}  threshold={model['threshold']}")
        print("Digite uma afirmação (ou 'sair' para encerrar):")
        while True:
            text = input("> ").strip()
            if text.lower() in {"sair", "exit", "quit"}:
                break
            if not text:
                continue
            result = predict(text, model=model)
            print(f"  {result['label']}  (p_fake={result['p_fake']}, threshold={result['threshold']})")
    elif args.text:
        result = predict(args.text)
        print(f"{result['label']}  (p_fake={result['p_fake']}, threshold={result['threshold']})")
    else:
        parser.print_help()