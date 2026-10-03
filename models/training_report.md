# Relatório de Treino — Comparação de Modelos

- Dataset: `data\processed\diabetes_nutrition_dataset_train.csv`
- Validação cruzada: StratifiedKFold, 5 folds, random_state=42
- Critério de seleção (refit): `f1_fake`
- Classe positiva (foco em recall): `FAKE`

## Resultados (ordenado por F1 da classe FAKE)

| Modelo | F1 (FAKE) | Recall (FAKE) | F1 (macro) | Tempo (s) |
|---|---|---|---|---|
| MultinomialNB | 0.9095 | 0.9765 | 0.8546 | 1.2 |
| LinearSVC | 0.9082 | 0.9647 | 0.8562 | 0.6 |
| LogisticRegression | 0.8908 | 0.9397 | 0.8296 | 11.0 |
| RandomForest | 0.8652 | 0.9397 | 0.7782 | 16.7 |

## Melhor modelo: `MultinomialNB`

Melhores hiperparâmetros encontrados:

```json
{
  "clf__alpha": 0.1,
  "clf__fit_prior": true,
  "tfidf__min_df": 1,
  "tfidf__ngram_range": [
    1,
    2
  ],
  "tfidf__sublinear_tf": true
}
```

## Observações
- Dataset pequeno e desbalanceado (FAKE >> REAL): resultados de CV têm variância considerável entre folds; tratar como estimativa, não valor definitivo.
- Métrica de seleção é F1/Recall da classe FAKE, não acurácia geral, por causa do custo assimétrico do falso negativo (RNF02).
- Próximo passo (Feature 2): calibração de threshold e avaliação final no conjunto de teste, separado deste treino/CV.