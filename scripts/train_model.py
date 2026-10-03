"""
train_model.py — Fase 2 / Feature 1

Compara 4 algoritmos de classificação (FAKE/REAL) via validação cruzada
estratificada + GridSearchCV, e gera um relatório de treino em Markdown.

Uso:
    python scripts/train_model.py
    python scripts/train_model.py --train data/processed/diabetes_nutrition_dataset_train.csv
    python scripts/train_model.py --cv 10 --scoring f1_fake

O dataset é desbalanceado (FAKE >> REAL), então:
  - usamos StratifiedKFold (mantém a proporção de classes em cada fold)
  - usamos class_weight="balanced" onde o modelo suporta
  - o scoring padrão do GridSearchCV é o F1 da classe FAKE, não a acurácia
    geral, porque o custo de um falso negativo (FAKE classificado como REAL)
    é maior que o de um falso positivo neste projeto.
"""

import argparse
import json
import time
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import make_scorer, f1_score, recall_score
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

RANDOM_STATE = 42
POSITIVE_LABEL = "FAKE"  # classe que mais importa não deixar passar

# Linhas identificadas como fora do escopo do projeto (não são sobre
# diabetes/nutrição) e fora do idioma (espanhol/inglês, não português) —
# mesma notícia (Ivermectina x Alzheimer) raspada em 3 idiomas de
# www.boatos.org. Excluídas por text_hash para manter rastreabilidade.
# Se a equipe decidir mantê-las, basta passar --keep-off-scope.
OFF_SCOPE_HASHES = {
    "15ec6675d4639e5df067bf1803105db3",  # ES: "Es falso que la Ivermectina..."
    "8744b5687b6494b628fbdf6ce59d8e39",  # EN: "It is false that Ivermectin..."
}


def build_search_space():
    """Define os 4 modelos e as grades de hiperparâmetros para o GridSearchCV.

    Cada modelo é um Pipeline(tfidf -> classificador) para que a busca de
    hiperparâmetros também cubra parâmetros do TF-IDF (ngram_range, min_df).
    """
    common_tfidf_grid = {
        "tfidf__ngram_range": [(1, 1), (1, 2)],
        "tfidf__min_df": [1, 2],
        "tfidf__sublinear_tf": [True],
    }

    models = {
        "LogisticRegression": {
            "pipeline": Pipeline([
                ("tfidf", TfidfVectorizer()),
                ("clf", LogisticRegression(
                    class_weight="balanced",
                    max_iter=2000,
                    random_state=RANDOM_STATE,
                )),
            ]),
            "param_grid": {
                **common_tfidf_grid,
                "clf__C": [0.1, 1.0, 3.0, 10.0],
            },
        },
        "LinearSVC": {
            "pipeline": Pipeline([
                ("tfidf", TfidfVectorizer()),
                ("clf", LinearSVC(
                    class_weight="balanced",
                    random_state=RANDOM_STATE,
                )),
            ]),
            "param_grid": {
                **common_tfidf_grid,
                "clf__C": [0.1, 1.0, 3.0, 10.0],
            },
        },
        "MultinomialNB": {
            # MultinomialNB não suporta class_weight; compensamos ajustando
            # class_prior a partir do próprio grid (uniforme vs. auto).
            "pipeline": Pipeline([
                ("tfidf", TfidfVectorizer()),
                ("clf", MultinomialNB()),
            ]),
            "param_grid": {
                **common_tfidf_grid,
                "clf__alpha": [0.1, 0.5, 1.0],
                "clf__fit_prior": [True, False],
            },
        },
        "RandomForest": {
            "pipeline": Pipeline([
                ("tfidf", TfidfVectorizer()),
                ("clf", RandomForestClassifier(
                    class_weight="balanced",
                    random_state=RANDOM_STATE,
                    n_jobs=-1,
                )),
            ]),
            "param_grid": {
                **common_tfidf_grid,
                "clf__n_estimators": [200, 400],
                "clf__max_depth": [None, 20],
            },
        },
    }
    return models


def get_scorer(name: str):
    """f1_fake (padrão): F1 da classe FAKE. macro: média das duas classes."""
    if name == "f1_fake":
        return make_scorer(f1_score, pos_label=POSITIVE_LABEL, average="binary")
    if name == "recall_fake":
        return make_scorer(recall_score, pos_label=POSITIVE_LABEL, average="binary")
    if name == "f1_macro":
        return "f1_macro"
    raise ValueError(f"scoring desconhecido: {name}")


def run(train_path: Path, cv_folds: int, scoring_name: str, out_dir: Path, keep_off_scope: bool):
    df = pd.read_csv(train_path)
    missing = {"cleaned_text", "label"} - set(df.columns)
    if missing:
        raise SystemExit(f"Colunas ausentes no CSV: {missing}")

    if not keep_off_scope and "text_hash" in df.columns:
        before = len(df)
        df = df[~df["text_hash"].isin(OFF_SCOPE_HASHES)]
        dropped = before - len(df)
        if dropped:
            print(f"Removidas {dropped} linha(s) fora de escopo/idioma (OFF_SCOPE_HASHES).")

    X = df["cleaned_text"].astype(str)
    y = df["label"].astype(str)

    print(f"Dataset: {len(df)} exemplos — {y.value_counts().to_dict()}")

    cv = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=RANDOM_STATE)
    scorer = get_scorer(scoring_name)
    models = build_search_space()

    results = []
    fitted = {}

    for model_name, spec in models.items():
        print(f"\n=== {model_name} ===")
        t0 = time.time()
        search = GridSearchCV(
            estimator=spec["pipeline"],
            param_grid=spec["param_grid"],
            scoring={
                "f1_fake": get_scorer("f1_fake"),
                "recall_fake": get_scorer("recall_fake"),
                "f1_macro": get_scorer("f1_macro"),
            },
            refit=scoring_name,
            cv=cv,
            n_jobs=-1,
        )
        search.fit(X, y)
        elapsed = time.time() - t0

        best_idx = search.best_index_
        cvres = search.cv_results_
        row = {
            "model": model_name,
            "best_params": search.best_params_,
            "cv_f1_fake": round(cvres["mean_test_f1_fake"][best_idx], 4),
            "cv_recall_fake": round(cvres["mean_test_recall_fake"][best_idx], 4),
            "cv_f1_macro": round(cvres["mean_test_f1_macro"][best_idx], 4),
            "train_seconds": round(elapsed, 1),
        }
        results.append(row)
        fitted[model_name] = search.best_estimator_
        print(f"  F1(FAKE)={row['cv_f1_fake']}  Recall(FAKE)={row['cv_recall_fake']}  "
              f"F1(macro)={row['cv_f1_macro']}  ({elapsed:.1f}s)")

    results.sort(key=lambda r: r["cv_f1_fake"], reverse=True)
    best = results[0]

    out_dir.mkdir(parents=True, exist_ok=True)
    write_report(results, best, train_path, cv_folds, scoring_name, out_dir / "training_report.md")

    with open(out_dir / "cv_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\nMelhor modelo: {best['model']} (F1 FAKE = {best['cv_f1_fake']})")
    print(f"Relatório salvo em {out_dir / 'training_report.md'}")
    return results, fitted


def write_report(results, best, train_path, cv_folds, scoring_name, out_path: Path):
    lines = []
    lines.append("# Relatório de Treino — Comparação de Modelos\n")
    lines.append(f"- Dataset: `{train_path}`")
    lines.append(f"- Validação cruzada: StratifiedKFold, {cv_folds} folds, random_state={RANDOM_STATE}")
    lines.append(f"- Critério de seleção (refit): `{scoring_name}`")
    lines.append(f"- Classe positiva (foco em recall): `{POSITIVE_LABEL}`\n")

    lines.append("## Resultados (ordenado por F1 da classe FAKE)\n")
    lines.append("| Modelo | F1 (FAKE) | Recall (FAKE) | F1 (macro) | Tempo (s) |")
    lines.append("|---|---|---|---|---|")
    for r in results:
        lines.append(
            f"| {r['model']} | {r['cv_f1_fake']} | {r['cv_recall_fake']} | "
            f"{r['cv_f1_macro']} | {r['train_seconds']} |"
        )

    lines.append(f"\n## Melhor modelo: `{best['model']}`\n")
    lines.append("Melhores hiperparâmetros encontrados:\n")
    lines.append("```json")
    lines.append(json.dumps(best["best_params"], indent=2, ensure_ascii=False))
    lines.append("```\n")

    lines.append("## Observações")
    lines.append(
        "- Dataset pequeno e desbalanceado (FAKE >> REAL): resultados de CV têm "
        "variância considerável entre folds; tratar como estimativa, não valor definitivo."
    )
    lines.append(
        "- Métrica de seleção é F1/Recall da classe FAKE, não acurácia geral, "
        "por causa do custo assimétrico do falso negativo (RNF02)."
    )
    lines.append(
        "- Próximo passo (Feature 2): calibração de threshold e avaliação final "
        "no conjunto de teste, separado deste treino/CV."
    )

    out_path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--train",
        type=Path,
        default=Path("data/processed/diabetes_nutrition_dataset_train.csv"),
        help="Caminho do CSV de treino (colunas: text,label,source,cleaned_text,text_hash)",
    )
    parser.add_argument("--cv", type=int, default=5, help="Número de folds da validação cruzada")
    parser.add_argument(
        "--scoring",
        default="f1_fake",
        choices=["f1_fake", "recall_fake", "f1_macro"],
        help="Métrica usada para escolher os melhores hiperparâmetros",
    )
    parser.add_argument("--out", type=Path, default=Path("models"), help="Diretório de saída")
    parser.add_argument(
        "--keep-off-scope",
        action="store_true",
        help="Não remove as linhas fora de escopo/idioma listadas em OFF_SCOPE_HASHES",
    )
    args = parser.parse_args()

    run(args.train, args.cv, args.scoring, args.out, args.keep_off_scope)