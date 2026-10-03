"""
test_classifier.py — Testes de contrato do classifier.py

Não usa pytest de propósito (o projeto não tem framework de testes ainda),
pra rodar em qualquer ambiente só com o requirements.txt já instalado:

    python scripts/test_classifier.py

Garante o que a Área 4 (API) vai depender:
  - load_model() carrega e tem os campos esperados
  - predict() sempre retorna {label, p_fake, threshold} no formato certo
  - o rótulo é sempre consistente com o threshold (label == FAKE <=> p_fake >= threshold)
  - o modelo classifica corretamente pelo menos os casos mais óbvios
    (regressão: se isso quebrar, alguém mexeu no pipeline sem querer)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import classifier as clf

FAILURES = []


def check(condition: bool, description: str):
    status = "OK  " if condition else "FAIL"
    print(f"[{status}] {description}")
    if not condition:
        FAILURES.append(description)


def test_model_file_exists():
    exists = Path(clf.MODEL_PATH).exists()
    check(exists, f"Arquivo do modelo existe em {clf.MODEL_PATH}")
    if not exists:
        print(f"  -> rode 'python scripts/classifier.py --train' antes de testar.")
    return exists


def test_load_model():
    model = clf.load_model()
    expected_keys = {
        "pipeline", "model_name", "best_params",
        "threshold", "fake_class_index", "trained_on_n_examples",
    }
    check(expected_keys.issubset(model.keys()),
          f"load_model() retorna todos os campos esperados ({expected_keys})")
    check(0.0 < model["threshold"] < 1.0,
          f"threshold está num intervalo plausível (threshold={model['threshold']})")
    check(model["trained_on_n_examples"] > 0,
          "modelo foi treinado com pelo menos 1 exemplo")
    return model


def test_predict_shape(model):
    result = clf.predict("Alguma afirmação qualquer sobre diabetes", model=model)
    check(set(result.keys()) == {"label", "p_fake", "threshold"},
          "predict() retorna exatamente {label, p_fake, threshold}")
    check(result["label"] in {"FAKE", "REAL"},
          f"label é FAKE ou REAL (veio: {result['label']})")
    check(0.0 <= result["p_fake"] <= 1.0,
          f"p_fake está entre 0 e 1 (veio: {result['p_fake']})")
    check(result["threshold"] == model["threshold"],
          "threshold retornado bate com o threshold do modelo carregado")


def test_label_matches_threshold(model):
    """Contrato central: label == FAKE se e somente se p_fake >= threshold."""
    samples = [
        "Canela cura diabetes tipo 2",
        "A metformina é o tratamento de primeira linha para diabetes tipo 2",
        "Chá de manga substitui insulina",
        "Diabetes tipo 2 está associado a resistência à insulina",
    ]
    all_consistent = True
    for text in samples:
        result = clf.predict(text, model=model)
        expected_label = "FAKE" if result["p_fake"] >= result["threshold"] else "REAL"
        consistent = result["label"] == expected_label
        all_consistent = all_consistent and consistent
        if not consistent:
            print(f"  -> inconsistência em: '{text}' "
                  f"(p_fake={result['p_fake']}, threshold={result['threshold']}, "
                  f"label={result['label']})")
    check(all_consistent, "label é sempre consistente com p_fake >= threshold, em todos os exemplos")


def test_known_cases(model):
    """Regressão: casos reais do dataset que o modelo já classifica
    corretamente hoje. Se isso falhar depois de uma mudança no pipeline,
    é sinal de que algo quebrou (não um limite conhecido do modelo).

    NOTA: o modelo tem uma limitação conhecida com frases curtas e
    genéricas fora do estilo "institucional/técnico" da classe REAL do
    dataset (ver LIMITATIONS.md ou training_report.md) — por isso os
    casos de teste usam exemplos reais do dataset, não frases inventadas.
    """
    known_fake = [
        "Canela cura diabetes tipo 2",
        "Chá de manga substitui insulina",
    ]
    known_real = [
        "A contagem de carboidratos é uma estratégia nutricional flexível recomendada pela SBD",
        "O exame periódico dos pés por profissional de saúde é fundamental para prevenção de úlceras",
    ]

    for text in known_fake:
        result = clf.predict(text, model=model)
        check(result["label"] == "FAKE",
              f"caso conhecido FAKE classificado corretamente: '{text}' "
              f"(veio: {result['label']}, p_fake={result['p_fake']})")

    for text in known_real:
        result = clf.predict(text, model=model)
        check(result["label"] == "REAL",
              f"caso conhecido REAL classificado corretamente: '{text}' "
              f"(veio: {result['label']}, p_fake={result['p_fake']})")


def main():
    print("=== Testes de contrato: scripts/classifier.py ===\n")

    if not test_model_file_exists():
        print("\nModelo não encontrado — abortando os demais testes.")
        sys.exit(1)

    model = test_load_model()
    print()
    test_predict_shape(model)
    print()
    test_label_matches_threshold(model)
    print()
    test_known_cases(model)

    print(f"\n{'='*50}")
    if FAILURES:
        print(f"{len(FAILURES)} teste(s) falharam:")
        for f in FAILURES:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print("Todos os testes passaram.")
        sys.exit(0)


if __name__ == "__main__":
    main()