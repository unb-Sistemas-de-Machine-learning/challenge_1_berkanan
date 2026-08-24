# challenge_1_berkanan
Challenge 1 - Equipe Berkanan - Sistemas de Machine Learning 2026/02

## Chatbot de Verificação de Informações Nutricionais para Diabetes

Projeto acadêmico de Aprendizado de Máquina (ML) cujo objetivo é combater a desinformação alimentar voltada a pessoas com diabetes, por meio de um chatbot de checagem de fatos baseado em evidências científicas.

### Sumário

- [Objetivo de Negócio](#objetivo-de-negócio)
- [Objetivos Técnicos de ML](#objetivos-técnicos-de-ml)
- [Escopo](#escopo)
- [Ideia do Produto](#ideia-do-produto)
- [Requisitos Funcionais](#requisitos-funcionais)
- [Requisitos Não-Funcionais](#requisitos-não-funcionais)
- [Guide Questions (GQs)](#guide-questions-gqs)
- [Plano de Atividades das GQs Prioritárias](#plano-de-atividades-das-gqs-prioritárias)

### Objetivo de Negócio

> Reduzir a proporção de decisões alimentares tomadas por pessoas com diabetes sem verificação prévia de fontes confiáveis, por meio de um chatbot de checagem baseado em evidência científica, aumentando a frequência com que essas pessoas confirmam uma informação antes de segui-la ou repassá-la.

### Objetivos Técnicos de ML

#### 1. Abordagem de IA / Modelo

- **Escolha principal:** RAG (Geração Aumentada por Recuperação) — busca em documentos + IA. O sistema busca primeiro trechos oficiais em manuais/diretrizes médicas e a IA formula a resposta com base neles, evitando invenção de informação (hallucination) e garantindo fontes reais para cada checagem.
- **Plano B:** Prompting puro via API, caso o cronograma do semestre fique apertado.
- **Descartado:** Treinar modelo do zero — inviável no prazo da matéria.

#### 2. Plataforma / Interface

- **Prioridade:** Chatbot via WhatsApp ou Telegram — mais próximo da realidade de quem recebe correntes e fake news no dia a dia.
- **Alternativa:** Interface web rápida, caso a burocracia/API do WhatsApp complique a integração.

#### 3. Métricas e Escopo Técnico

- **Objetivo de ML:** classificar o texto em **Verdadeiro**, **Falso**, **Parcialmente Verdadeiro** ou **Sem Evidência Suficiente**, sempre com explicação embasada.
- **Métricas principais:** meta de acurácia geral + foco rigoroso em minimizar **falsos negativos** (evitar classificar uma fake news perigosa como verdadeira — o custo desse erro é assimétrico e mais grave).

### Escopo

**Trata:**
- Textos e afirmações sobre alimentação, dietas e mitos relacionados a diabetes, em português.

**Não trata:**
- Prescrições médicas.
- Dosagens de insulina.
- Diagnósticos clínicos.

### Ideia do Produto

#### Critérios Funcionais

- **Verificação de informação:** dado um texto/afirmação sobre dieta, alimento ou nutrição (ex.: "canela cura diabetes"), o sistema classifica como verdadeiro, falso, enganoso/parcialmente verdadeiro ou "sem evidência suficiente".
- **Chatbot funcional:** mantém conversa coerente, entende linguagem natural (erros de digitação, gírias, etc.) e responde com clareza.
- **Contextualização para diabetes:** não basta dizer "é falso" — precisa explicar por que é perigoso especificamente para quem tem diabetes (ex.: impacto glicêmico, interação com insulina/medicamentos).
- **Citação de fontes confiáveis:** toda resposta embasada em fontes como SBD (Sociedade Brasileira de Diabetes), Ministério da Saúde, artigos científicos etc.

#### Critérios Técnicos / de ML

- Acurácia do classificador de fake news (precisão, recall, F1-score — meta ex.: F1 ≥ 0.80 no teste).
- Taxa de falsos negativos baixa (custo do erro assimétrico).
- Qualidade da base de dados: dataset rotulado (fake/real) sobre nutrição e diabetes, com fontes documentadas e tamanho justificado.
- Tempo de resposta aceitável (ex.: < 3-5 segundos).

#### Critérios de Usabilidade / UX

- Testes de usabilidade com usuários reais (mesmo que grupo pequeno).
- Linguagem acessível, sem jargão técnico excessivo.
- Avaliação de facilidade de uso via SUS (System Usability Scale) ou entrevistas qualitativas.

#### Critérios de Impacto / Segurança

- Redução percebida de dúvidas/insegurança alimentar dos usuários testados (pré/pós teste).
- O sistema reforça que não substitui orientação médica/nutricional.
- Casos de teste específicos: o chatbot não deve dar conselho médico direto (ex.: dosagem de insulina), apenas checar informação e recomendar profissional.

### Requisitos Funcionais

| ID | Descrição |
|----|-----------|
| RF01 | Verificação de informações compartilhadas: classificar afirmação como verdadeira ou falsa. |
| RF02 | Classificação das informações por partes: parcialmente verdadeiras ou enganosas. |
| RF03 | Indicação do cenário de incerteza/falha ("sem evidência suficiente"). |
| RF04 | Coerência na conversa, entendimento de linguagem natural. |
| RF05 | Contextualização para diabetes nas explicações. |
| RF06 | Citação de fontes confiáveis. |
| RF07 | Explicação dos motivos da classificação. |
| RF08 | Apresentação das evidências e trechos das fontes. |
| RF09 | Solicitação de contexto adicional quando necessário. |
| RF10 | Orientação para procurar um profissional de saúde. |
| RF11 | Reformulação da pergunta quando ambígua. |
| RF12/RF13 | Alertas para informações potencialmente perigosas. |

### Requisitos Não-Funcionais

| ID | Descrição |
|----|-----------|
| RNF01 | Acurácia do classificador (meta ex.: F1 ≥ 0.80). |
| RNF02 | Taxa de falsos negativos baixa. |
| RNF03 | Tempo de resposta < 3-5 segundos. |
| RNF04 | Suporte a ~3 salas de conversa diferentes. |
| RNF05 | Proteção dos dados do usuário contra acesso não autorizado. |
| RNF06 | Minimização de dados coletados/armazenados. |
| RNF08 | Clareza das respostas para público sem conhecimento técnico. |
| RNF09 | Legibilidade: classificação, justificativa e fontes bem estruturadas. |

### Guide Questions (GQs)

#### Dados
- Critérios de seleção/validação de fontes (PubMed, nutrição, etc.) — **Responder já**
- Lidar com desatualização/revogação de estudos científicos — **Se sobrar tempo**
- Heurísticas nutricionais como sinal de suspeita (índice/carga glicêmica, evidência clínica vs. anedótica) — **Planejar**

#### Usuários
- Tratamento específico por tipo de diabetes (1, 2, gestacional...) ou generalizado — **Planejar**
- Adaptações de acessibilidade (idosos, baixa alfabetização digital, deficiência visual) — **Se sobrar tempo**
- Qual tipo de alimentação causa mais insegurança ao usuário — **Cortar sem dó**

#### Modelo
- Base local ou online — **Responder já**
- Generativa / Descritiva / Preditiva — **Responder já**
- Melhor tipo de treinamento — **Responder já**

#### Produção
- Plataforma (web ou mobile) — **Responder já**
- Ferramentas de software livre disponíveis — **Planejar**
- Ambiente de hospedagem — **Responder já**

#### Ética
- Armazenamento das informações do usuário — **Se sobrar tempo**
- Cuidados com informações com viés — **Cortar sem dó**
- Como deixar claro que o chatbot não substitui médico/nutricionista — **Responder já**

### Plano de Atividades das GQs Prioritárias

As 7 GQs abaixo foram definidas como prioridade, cada uma com atividade e recurso já mapeados (falta apenas responsável e prazo):

#### 1. Critérios de fontes confiáveis
- **Atividade:** levantar e comparar critérios de credibilidade científica (peer-review, tipo de estudo, data de publicação, conflito de interesse) e aplicar em checklist para 15-20 fontes candidatas.
- **Recurso:** PubMed, diretrizes da SBD, guidelines da ADA, critérios de avaliação de evidência tipo GRADE.

#### 2. Arquitetura de modelo (local/online, tipo, treinamento)
- **Atividade:** comparar 2-3 abordagens (LLM via API + prompt engineering vs. modelo de classificação treinado localmente com fine-tuning vs. RAG sobre base curada) num pequeno protótipo/POC com 5-10 exemplos.
- **Recurso:** Hugging Face, documentação de APIs (Anthropic, OpenAI), papers sobre RAG para fact-checking.

#### 3. Plataforma e hospedagem
- **Atividade:** listar requisitos técnicos (custo, facilidade de deploy, tempo de aula restante) e comparar 2-3 opções de stack.
- **Recurso:** Streamlit/Gradio (protótipo rápido), Vercel/Render/Railway (hospedagem gratuita), WhatsApp Business API.

#### 4. Comunicação de limites do chatbot
- **Atividade:** desenhar 3-5 respostas-padrão para quando a pergunta exigir decisão clínica, testando com 2-3 pessoas se a mensagem fica clara sem soar assustadora ou robótica.
- **Recurso:** exemplos de disclaimers de apps de saúde reais, heurísticas de UX writing para saúde.

#### 5. Diabetes tipo 1/2/gestacional vs. genérico
- **Atividade:** entrevistar ou pesquisar 3-5 diferenças nutricionais relevantes entre os tipos (ex.: contagem de carboidratos crítica no tipo 1; tipo 2 com mais foco em perda de peso) e decidir se o escopo do semestre permite diferenciar.
- **Recurso:** material da SBD sobre diferenças entre os tipos, entrevista rápida com alguém com diabetes (se houver acesso).

#### 6. Heurísticas nutricionais como sinal de fake news
- **Atividade:** listar 8-10 "bandeiras vermelhas" comuns em desinformação nutricional (promessa de cura milagrosa, ausência de fonte, linguagem absolutista "nunca/sempre", contradição com consenso científico) e testar contra 10 exemplos reais de correntes.
- **Recurso:** exemplos de checagem de fatos (Boatos.org, Lupa, Aos Fatos — buscar "diabetes"/"diet"), literatura sobre linguística de fake news.

#### 7. Armazenamento de dados sensíveis
- **Atividade:** mapear quais dados o sistema realmente precisa guardar (histórico de conversa? tipo de diabetes? nada?) e definir o mínimo necessário sob a LGPD para dados de saúde.
- **Recurso:** texto da LGPD (art. 11, dados sensíveis), guia de privacidade *by design*.
