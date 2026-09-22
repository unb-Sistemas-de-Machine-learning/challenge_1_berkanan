"""
calibrate_and_evaluate.py — Fase 2 / Feature 2

Pega o melhor modelo encontrado pelo train_model.py (lido de
models/cv_results.json), treina no dataset de treino completo, calibra
o threshold de decisão da classe FAKE no PRÓPRIO treino (via CV interna,
nunca no test set) e só então avalia uma única vez no test set.

Uso:
    python scripts/calibrate_and_evaluate.py
    python scripts/calibrate_and_evaluate.py --min-precision 0.7

Critério de calibração (padrão): dentre os thresholds que mantêm
precisão(FAKE) >= --min-precision no treino, escolhe o que maximiza
recall(FAKE). Se nenhum threshold atingir a precisão mínima, cai para o
threshold que maximiza F1(FAKE) — e avisa no relatório.
"""

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_predict

from train_model import OFF_SCOPE_HASHES, RANDOM_STATE, build_search_space

POSITIVE_LABEL = "FAKE"


def load_clean(path: Path, drop_off_scope: bool = True) -> pd.DataFrame:
    df = pd.read_csv(path)
    if drop_off_scope and "text_hash" in df.columns:
        before = len(df)
        df = df[~df["text_hash"].isin(OFF_SCOPE_HASHES)]
        dropped = before - len(df)
        if dropped:
            print(f"[{path.name}] removidas {dropped} linha(s) fora de escopo/idioma.")
    return df


def get_best_model_spec(cv_results_path: Path):
    with open(cv_results_path, encoding="utf-8") as f:
        results = json.load(f)
    best = max(results, key=lambda r: r["cv_f1_fake"])
    return best["model"], best["best_params"]


def build_pipeline_with_params(model_name: str, best_params: dict):
    spec = build_search_space()[model_name]
    pipeline = spec["pipeline"]
    # JSON não tem tupla; ngram_range volta como lista e precisa virar tupla.
    fixed_params = dict(best_params)
    if "tfidf__ngram_range" in fixed_params:
        fixed_params["tfidf__ngram_range"] = tuple(fixed_params["tfidf__ngram_range"])
    pipeline.set_params(**fixed_params)
    return pipeline


def get_probability_scores(pipeline, X, y):
    """Retorna P(FAKE) via CV interna no treino (out-of-fold), evitando
    calibrar o threshold com previsões 'vazadas' do próprio treino."""
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)

    if hasattr(pipeline.named_steps["clf"], "predict_proba"):
        proba = cross_val_predict(pipeline, X, y, cv=cv, method="predict_proba")
        classes = pipeline.fit(X, y).named_steps["clf"].classes_
    else:
        # LinearSVC não tem predict_proba nativo -> calibra via Platt scaling
        calibrated = CalibratedClassifierCV(pipeline, cv=cv, method="sigmoid")
        proba = cross_val_predict(calibrated, X, y, cv=cv, method="predict_proba")
        classes = calibrated.fit(X, y).classes_

    fake_idx = list(classes).index(POSITIVE_LABEL)
    return proba[:, fake_idx]


def sweep_thresholds(y_true, p_fake, min_precision: float):
    rows = []
    for t in np.arange(0.05, 0.96, 0.01):
        y_pred = np.where(p_fake >= t, "FAKE", "REAL")
        rows.append({
            "threshold": round(float(t), 2),
            "precision_fake": precision_score(y_true, y_pred, pos_label="FAKE", zero_division=0),
            "recall_fake": recall_score(y_true, y_pred, pos_label="FAKE", zero_division=0),
            "f1_fake": f1_score(y_true, y_pred, pos_label="FAKE", zero_division=0),
        })
    return pd.DataFrame(rows)


def choose_threshold(sweep_df: pd.DataFrame, min_precision: float):
    eligible = sweep_df[sweep_df["precision_fake"] >= min_precision]
    if len(eligible):
        # Em caso de empate no recall (comum quando o recall satura em 1.0
        # numa faixa de thresholds), prefere o threshold com maior precisão
        # dentro do empate — não o menor threshold da faixa.
        row = eligible.sort_values(
            ["recall_fake", "precision_fake"], ascending=[False, False]
        ).iloc[0]
        return float(row["threshold"]), False
    # fallback: nenhum threshold atinge a precisão mínima -> maximiza F1
    row = sweep_df.sort_values("f1_fake", ascending=False).iloc[0]
    return float(row["threshold"]), True


def evaluate_at_threshold(y_true, p_fake, threshold, texts=None):
    y_pred = np.where(p_fake >= threshold, "FAKE", "REAL")
    cm = confusion_matrix(y_true, y_pred, labels=["FAKE", "REAL"])
    tn_label, fn_label = "REAL", "FAKE"

    result = {
        "threshold": threshold,
        "precision_fake": round(precision_score(y_true, y_pred, pos_label="FAKE", zero_division=0), 4),
        "recall_fake": round(recall_score(y_true, y_pred, pos_label="FAKE", zero_division=0), 4),
        "f1_fake": round(f1_score(y_true, y_pred, pos_label="FAKE", zero_division=0), 4),
        "f1_macro": round(f1_score(y_true, y_pred, average="macro", zero_division=0), 4),
        "confusion_matrix": {
            "labels": ["FAKE", "REAL"],
            "matrix": cm.tolist(),
        },
    }

    false_negatives = []
    if texts is not None:
        y_true_arr = np.asarray(y_true)
        for i in range(len(y_true_arr)):
            if y_true_arr[i] == "FAKE" and y_pred[i] == "REAL":
                false_negatives.append({
                    "text": texts.iloc[i],
                    "p_fake": round(float(p_fake[i]), 4),
                })
    result["false_negatives"] = false_negatives
    result["false_negative_count"] = len(false_negatives)
    return result


def run(train_path: Path, test_path: Path, cv_results_path: Path,
        min_precision: float, out_dir: Path):
    train_df = load_clean(train_path)
    test_df = load_clean(test_path)

    X_train, y_train = train_df["cleaned_text"].astype(str), train_df["label"].astype(str)
    X_test, y_test = test_df["cleaned_text"].astype(str), test_df["label"].astype(str)

    model_name, best_params = get_best_model_spec(cv_results_path)
    print(f"Modelo escolhido (por cv_results.json): {model_name}")
    print(f"Hiperparâmetros: {best_params}")

    pipeline = build_pipeline_with_params(model_name, best_params)

    # 1) Calibração do threshold: só no treino, via probabilidades out-of-fold.
    p_fake_train_oof = get_probability_scores(pipeline, X_train, y_train)
    sweep_df = sweep_thresholds(y_train, p_fake_train_oof, min_precision)
    threshold, used_fallback = choose_threshold(sweep_df, min_precision)
    print(f"Threshold escolhido: {threshold} "
          f"({'fallback F1' if used_fallback else f'precisão >= {min_precision}'})")

    # 2) Treina o modelo final em TODO o treino.
    final_model = build_pipeline_with_params(model_name, best_params)
    if not hasattr(final_model.named_steps["clf"], "predict_proba"):
        final_model = CalibratedClassifierCV(final_model, cv=5, method="sigmoid")
    final_model.fit(X_train, y_train)

    # 3) Avaliação única no test set — em 0.5 (baseline) e no threshold calibrado.
    classes = final_model.classes_ if hasattr(final_model, "classes_") \
        else final_model.named_steps["clf"].classes_
    fake_idx = list(classes).index(POSITIVE_LABEL)
    p_fake_test = final_model.predict_proba(X_test)[:, fake_idx]

    eval_default = evaluate_at_threshold(y_test, p_fake_test, 0.5, texts=test_df["text"])
    eval_calibrated = evaluate_at_threshold(y_test, p_fake_test, threshold, texts=test_df["text"])

    print("\n=== Test set — threshold 0.5 (baseline) ===")
    print(f"  Precision(FAKE)={eval_default['precision_fake']}  "
          f"Recall(FAKE)={eval_default['recall_fake']}  F1(FAKE)={eval_default['f1_fake']}  "
          f"Falsos negativos: {eval_default['false_negative_count']}")

    print(f"\n=== Test set — threshold {threshold} (calibrado) ===")
    print(f"  Precision(FAKE)={eval_calibrated['precision_fake']}  "
          f"Recall(FAKE)={eval_calibrated['recall_fake']}  F1(FAKE)={eval_calibrated['f1_fake']}  "
          f"Falsos negativos: {eval_calibrated['false_negative_count']}")

    if eval_calibrated["false_negatives"]:
        print("\n  Falsos negativos (FAKE classificado como REAL):")
        for fn in eval_calibrated["false_negatives"]:
            print(f"    - (p_fake={fn['p_fake']}) {fn['text'][:90]}")

    out_dir.mkdir(parents=True, exist_ok=True)
    metadata = {
        "model": model_name,
        "best_params": best_params,
        "calibration": {
            "method": "out-of-fold CV no treino, sweep de threshold 0.05-0.95",
            "min_precision_target": min_precision,
            "fallback_used": used_fallback,
            "chosen_threshold": threshold,
        },
        "train_set": {
            "path": str(train_path),
            "n_examples": len(train_df),
            "label_counts": train_df["label"].value_counts().to_dict(),
        },
        "test_set": {
            "path": str(test_path),
            "n_examples": len(test_df),
            "label_counts": test_df["label"].value_counts().to_dict(),
        },
        "test_metrics_default_threshold_0_5": eval_default,
        "test_metrics_calibrated_threshold": eval_calibrated,
    }
    with open(out_dir / "training_metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print(f"\nMetadados salvos em {out_dir / 'training_metadata.json'}")

    return metadata


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", type=Path,
                         default=Path("data/processed/diabetes_nutrition_dataset_train.csv"))
    parser.add_argument("--test", type=Path,
                         default=Path("data/processed/diabetes_nutrition_dataset_test.csv"))
    parser.add_argument("--cv-results", type=Path, default=Path("models/cv_results.json"))
    parser.add_argument("--min-precision", type=float, default=0.7,
                         help="Precisão mínima da classe FAKE ao calibrar o threshold")
    parser.add_argument("--out", type=Path, default=Path("models"))
    args = parser.parse_args()

    run(args.train, args.test, args.cv_results, args.min_precision, args.out)