# Limitações Conhecidas — Classificador v2 (MultinomialNB)

## Recall desigual entre classes

- **FAKE**: recall = 1.0 no test set (22/22) — o objetivo prioritário (RNF02)
  está sendo atingido.
- **REAL**: recall = 0.75 no test set (9/12) — 3 afirmações verdadeiras foram
  classificadas como FAKE.

## Causa provável: viés de estilo, não só de conteúdo

Os 3 falsos positivos (REAL → FAKE) e outros exemplos testados manualmente
têm um padrão em comum: são frases **curtas e diretas**, sem o estilo
técnico/institucional predominante nos exemplos REAL do dataset (que vêm
majoritariamente de `curated_expert`, com linguagem formal e frequentemente
citando SBD, Ministério da Saúde etc.).

Exemplos de frases verdadeiras e simples que o modelo classifica **incorretamente**
como FAKE:
- "A insulina é um hormônio produzido pelo pâncreas" (p_fake=0.68)
- "Diabetes tipo 2 está associado a resistência à insulina" (p_fake=0.67)
- "O exercício físico regular ajuda no controle glicêmico" (p_fake=0.50, no limite)

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
  o rótulo binário, para casos limítrofes (ex.: 0.29–0.5) o usuário ver que
  a confiança é baixa.