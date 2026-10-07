# Limitações Conhecidas — Classificador v2 (MultinomialNB)

## Recall desigual entre classes

Valores do test set (34 exemplos) com o threshold em produção, `0.5`
(escolhido pela calibração out-of-fold em `calibrate_and_evaluate.py` e
gravado em `models/classifier_v2.joblib`):

- **FAKE**: recall = 1.0 (22/22) — o objetivo prioritário (RNF02) está sendo
  atingido.
- **REAL**: recall = 0.917 (11/12) — 1 afirmação verdadeira foi classificada
  como FAKE.

A configuração com threshold `0.29` era a **meta mínima** de desempenho
(recall FAKE 1.0, precisão FAKE 0.88, recall REAL 0.75). O threshold `0.5`
**superou essa meta**: manteve o recall de FAKE em 1.0 e subiu a precisão de
FAKE para 0.957 e o recall de REAL para 0.917. As métricas das duas
configurações estão em `models/training_metadata.json`.

## Causa provável: viés de estilo, não só de conteúdo

Os falsos positivos (REAL → FAKE) do test set e outros exemplos testados
manualmente têm um padrão em comum: são frases **curtas e diretas**, sem o estilo
técnico/institucional predominante nos exemplos REAL do dataset (que vêm
majoritariamente de `curated_expert`, com linguagem formal e frequentemente
citando SBD, Ministério da Saúde etc.).

Exemplos de frases verdadeiras e simples que o modelo classifica **incorretamente**
como FAKE:
- "A insulina é um hormônio produzido pelo pâncreas" (p_fake=0.68)
- "Diabetes tipo 2 está associado a resistência à insulina" (p_fake=0.67)

Caso limítrofe: "O exercício físico regular ajuda no controle glicêmico" tem
p_fake=0.4953 — fica REAL com o threshold 0.5 por uma margem mínima.

Hipótese: o TF-IDF + MultinomialNB está aprendendo, em parte, marcadores de
**estilo/formalidade** (presença de termos técnicos, citação de instituições,
frases mais longas) como proxy de "REAL", em vez de aprender só o conteúdo
factual. Isso é esperado dado o tamanho pequeno do dataset (128 exemplos) e
o desbalanceamento (82 FAKE vs. 46 REAL) — o modelo tem poucos exemplos REAL
"simples/curtos" para aprender que frases desse tipo também podem ser
verdadeiras.

## Recomendação para próximas iterações

- Priorizar a coleta de mais exemplos REAL **curtos e diretos** (não só
  técnicos/institucionais) ao expandir o dataset — provavelmente o ganho
  de qualidade mais alto por esforço no momento.
- Ao apresentar o trabalho, deixar claro que o alto recall em FAKE (o
  requisito de segurança prioritário, RNF02) tem como contrapartida um
  recall menor em REAL — é uma escolha de threshold deliberada (Feature 2),
  não um erro não percebido.
- Se o produto for usar isso em produção, considerar mostrar o `p_fake`
  junto com o rótulo (já exposto por `classifier.predict()`) em vez de só
  o rótulo binário, para casos limítrofes (ex.: 0.4–0.6) o usuário ver que
  a confiança é baixa. O frontend já exibe o `p_fake` como "Probabilidade de
  a afirmação ser falsa".