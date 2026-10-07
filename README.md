# challenge_1_berkanan
Challenge 1 - Equipe Berkanan - Tópicos Especiais em Engenharia de Software - Sistemas de Machine Learning 2026/02

## Chatbot de Verificação de Informações Nutricionais para Diabetes

[![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=white)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-5-646CFF?logo=vite&logoColor=white)](https://vitejs.dev/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-vector_store-FF6F61)](https://www.trychroma.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)

Projeto acadêmico de Aprendizado de Máquina (ML) cujo objetivo é combater a desinformação alimentar voltada a pessoas com diabetes, por meio de um chatbot de checagem de fatos baseado em evidências científicas.

> ⚠️ **Aviso acadêmico:** este sistema não substitui orientação médica ou nutricional profissional. Ele apenas verifica alegações com base em evidências recuperadas de documentos oficiais.

---

## 📑 Sumário

- [Sobre o projeto](#-sobre-o-projeto)
- [Resultados e validação dos objetivos](#-resultados-e-validação-dos-objetivos)
- [Arquitetura](#️-arquitetura)
- [Login sem autenticação](#-login-sem-autenticação)
- [Stack técnica](#-stack-técnica)
- [Estrutura do repositório](#-estrutura-do-repositório)
- [Quick start](#-quick-start)
- [Endpoints da API](#-endpoints-da-api)
- [Variáveis de ambiente](#️-variáveis-de-ambiente)
- [Como funciona o pipeline](#-como-funciona-o-pipeline)
- [Pipeline offline (dados, treino e indexação)](#-pipeline-offline-dados-treino-e-indexação)
- [Testes](#-testes)
- [Deploy](#-deploy)
- [Limitações conhecidas](#️-limitações-conhecidas)
- [Equipe e referências](#-equipe-e-referências)

---

## 🎯 Sobre o projeto

**Problema:** pessoas com diabetes tomam decisões alimentares sem verificar a veracidade das informações que recebem, especialmente em correntes de WhatsApp e redes sociais. Isso pode levar à redução ou abandono de tratamentos essenciais (ex.: insulina).

**Solução:** um chatbot que recebe uma afirmação em português (ex.: *"canela cura diabetes"*), classifica como **verdadeira ou falsa**, e apresenta **evidências de fontes oficiais** (SBD, Ministério da Saúde, MedlinePlus, OMS, CDC, etc.) com explicação contextualizada para o diabetes.

**Escopo:**
- ✅ Afirmações sobre alimentação, dietas e mitos relacionados a diabetes
- ❌ Prescrições médicas, dosagens de insulina, diagnósticos clínicos

---

## ✅ Resultados e validação dos objetivos

### Métricas do classificador (conjunto de teste, 34 exemplos nunca vistos no treino)

A meta mínima de desempenho era a configuração calibrada com threshold `0.29`. O modelo em produção (`MultinomialNB`, threshold `0.5`) **superou essa meta** em todas as métricas, mantendo o recall de FAKE em 100%. Valores de [models/training_metadata.json](models/training_metadata.json):

| Métrica | Meta mínima (threshold 0.29) | Resultado final (threshold 0.5) | |
|---|---|---|---|
| Recall (FAKE) | 1.00 | **1.00** (22/22 — nenhuma fake news passou como verdadeira) | ✅ mantido |
| Precisão (FAKE) | 0.880 | **0.957** | ✅ superada |
| F1 (FAKE) | 0.936 | **0.978** | ✅ superada |
| F1 macro | 0.897 | **0.967** | ✅ superada |
| Recall (REAL) | 0.750 (9/12) | **0.917** (11/12) | ✅ superada |

Validação cruzada (5 folds, treino) — comparação de 4 algoritmos em [models/training_report.md](models/training_report.md): `MultinomialNB` (F1-FAKE 0.910), `LinearSVC` (0.908), `LogisticRegression` (0.869), `RandomForest` (0.865).

> Os números vêm de um conjunto de teste pequeno (34 exemplos); devem ser lidos como estimativa, não como desempenho garantido em produção.

### Objetivos x entregas

| Objetivo | Status | Evidência |
|---|---|---|
| **Negócio:** reduzir a desinformação alimentar e alertar sobre mitos perigosos | ✅ Atendido (escopo acadêmico) | Recall de FAKE = 1.0 no teste; métrica de seleção priorizou recall de FAKE (RNF02). Não houve avaliação com usuários reais. |
| **RNF02:** priorizar recall da classe FAKE (falso negativo é o erro mais caro) | ✅ Atendido | Seleção de modelo por F1/recall de FAKE + calibração de threshold ([scripts/calibrate_and_evaluate.py](scripts/calibrate_and_evaluate.py)). |
| Meta mínima de desempenho do classificador (threshold 0.29) | ✅ Superada | Com threshold 0.5, todas as métricas ficaram acima da meta e o recall de FAKE continuou em 1.0 (tabela acima). |
| **Produto:** interface de chat interativa | ✅ Atendido | Frontend React com chat, múltiplas conversas, histórico e tema claro/escuro. |
| **Produto:** justificar com base em fontes oficiais | ✅ Atendido | RAG sobre 3.896 trechos de 89 documentos de 12 instituições; cada resposta traz até 3 evidências com fonte e similaridade. |
| **Produto:** explicação clara para o usuário final | ⚠️ Parcial | Gemini gera explicação em markdown, mas depende de `GEMINI_API_KEY` e da cota do free tier. Sem ela, o usuário vê só rótulo + evidências. |
| Persistência e histórico das análises | ✅ Atendido | PostgreSQL (`analysis_history`) + `GET /api/history`. O histórico é global (não separado por usuário). |
| Resiliência a falhas de componentes | ✅ Atendido | LLM, Chroma e PostgreSQL podem falhar sem derrubar a análise (ver [Arquitetura](#️-arquitetura)); cenários cobertos por testes. |
| Autenticação de usuários | ➖ Fora do escopo | O login é só identificação local, sem autenticação (ver [Login sem autenticação](#-login-sem-autenticação)). |
| Restrição de escopo (apenas alimentação + diabetes) | ❌ Não implementado | Não há filtro de escopo: qualquer texto com 3+ caracteres é classificado como `REAL` ou `FAKE`. |
| Saída com 4 classes (`REAL`, `FAKE`, `INCONCLUSIVE`, `PARTIALLY_TRUE`) | ❌ Não implementado | Schema, banco e frontend aceitam as 4, mas o modelo é binário. |
| Implantação reproduzível | ✅ Atendido | `docker compose --profile prod` (db + backend + frontend/nginx), em uso numa VM Azure, e `render.yaml`. |
| Testes automatizados | ✅ Atendido | 12 testes de contrato da API + testes de contrato do classificador + smoke test end-to-end. |

### O problema foi resolvido?

**Como prova de conceito, sim.** O sistema completo (classificação ML + evidências RAG + explicação LLM + persistência + interface) funciona de ponta a ponta e cumpre o requisito de segurança prioritário: no teste, nenhuma afirmação falsa foi classificada como verdadeira.

Para uso real ainda faltam: dataset maior e mais variado (o classificador aprende estilo de escrita, não medicina — ver [models/limitations.md](models/limitations.md)), filtro de escopo, classe "inconclusivo" quando não houver evidência e avaliação com usuários.

---

## 🏗️ Arquitetura

O sistema é composto por um frontend estático e uma API que orquestra **três etapas de análise** e a **persistência**:

```text
┌──────────────────────────────────────────────────────────────────┐
│                        NAVEGADOR (Usuário)                       │
│   localStorage: sessão local (nome/e-mail) + conversas do chat   │
└──────────────────────────────┬───────────────────────────────────┘
                               │ HTTP
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│              FRONTEND — React + Vite + Tailwind                  │
│     /login · /chat · /chat/:id · /history                        │
│     dev: proxy do Vite  ·  prod: nginx (SPA + proxy /api)        │
└──────────────────────────────┬───────────────────────────────────┘
                               │ POST /api/analyze · GET /api/history
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│   BACKEND — FastAPI (api/main.py → api/routes/analysis.py)       │
│   api/services/fact_checker_service.py → DiabetesFactChecker     │
│   (scripts/fact_checker.py, carregado uma vez no startup)        │
└──────────────────────────────┬───────────────────────────────────┘
                               │ executado em sequência
        ┌──────────────────────┼──────────────────────┐
        ▼                      ▼                      ▼
┌────────────────┐   ┌─────────────────┐   ┌──────────────────┐
│ 1. ML          │   │ 2. RAG          │   │ 3. LLM (opcional)│
│ TF-IDF +       │   │ Embeddings +    │   │ Gemini redige    │
│ MultinomialNB  │   │ ChromaDB top-3  │   │ explicação com   │
│ → p_fake,label │   │ → matched_src[] │   │ base em 1 e 2    │
└────────┬───────┘   └────────┬────────┘   └─────────┬────────┘
         │                    │                      │
         └────────────────────┼──────────────────────┘
                              ▼
                   ┌──────────────────────┐
                   │ 4. PostgreSQL        │
                   │ analysis_history     │
                   └──────────────────────┘
```

**Responsabilidades e acoplamento:**
- **Só o ML classifica.** O RAG não influencia o rótulo; ele só traz evidências para exibição e para o prompt do LLM. O LLM não classifica nem busca.
- **Duas camadas de histórico:** as conversas do chat ficam no `localStorage` do navegador; a página `/history` lê as últimas 20 análises do PostgreSQL (de todos os usuários).
- **Login sem autenticação:** veja a seção abaixo.

**Degradação de cada componente:**

| Falha | Comportamento | Status |
|---|---|---|
| LLM (`429`, `503`, sem chave, modelo descontinuado) | `llm_explanation: null`; classificação e evidências continuam | ✅ coberto por testes |
| Volume do Chroma vazio (primeiro deploy) | No startup, o índice versionado é copiado para `CHROMA_PERSIST_DIRECTORY`; um índice já existente nunca é sobrescrito | ✅ coberto por testes |
| ChromaDB indisponível | `matched_sources: []`; classificação continua | ✅ |
| PostgreSQL fora do ar | Análise devolvida normalmente com `id: null` e `timestamp: null` (não entra no histórico; o frontend mostra "não persistido") | ✅ coberto por testes |
| Modelo `.joblib` ausente | API não sobe (falha no startup) | — |

### 🔓 Login sem autenticação

A tela de login **não autentica ninguém**. É apenas uma identificação local para personalizar a interface:

- o usuário informa nome e e-mail, sem senha;
- os dados ficam só no `localStorage` do navegador (`berkanan.session`) e nunca são enviados ao backend;
- as rotas `/chat` e `/history` exigem essa sessão local, mas isso é só navegação, não controle de acesso;
- a API é aberta: qualquer pessoa com a URL pode chamar `/api/analyze` e ler `/api/history`, que mostra as análises de todos os usuários.

Por isso, **não envie dados pessoais ou de saúde identificáveis nas afirmações**. Se o projeto evoluir para uso real, será preciso autenticação no backend (ex.: OAuth/JWT) e um histórico separado por usuário. O arquivo `frontend/src/lib/auth-client.ts` (SDK Lumi) é um resquício do template e não é usado pelo fluxo de login.

---

## 🧰 Stack técnica

### Backend

| Camada | Tecnologia |
|---|---|
| API | FastAPI + Uvicorn |
| Validação | Pydantic v2 |
| ML | scikit-learn (`TF-IDF` + `MultinomialNB`) |
| Embeddings | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` |
| Vector store | ChromaDB (via `langchain-chroma`) |
| Orquestração RAG | LangChain |
| LLM | Google Gemini (`google-genai`) com retry exponencial |
| Banco relacional | PostgreSQL 16 + SQLAlchemy 2 + psycopg2 |
| Scraping | Requests + BeautifulSoup4 + PyMuPDF |

### Frontend

| Camada | Tecnologia |
|---|---|
| Framework | React 18 + TypeScript |
| Build | Vite 5 (com pré-renderização) |
| Estilo | Tailwind CSS |
| Roteamento | React Router 6 |
| Animações | Framer Motion |
| Notificações | react-hot-toast |
| Ícones | Lucide React |
| Markdown | react-markdown + remark-gfm |
| Servidor em produção | nginx (Docker) ou site estático (Render) |

---

## 📁 Estrutura do repositório

Monorepo com **backend na raiz** e **frontend em `frontend/`**:

```text
challenge_1_berkanan/
├── api/                       # Backend FastAPI
│   ├── main.py                # Ponto de entrada (uvicorn api.main:app), CORS, /health
│   ├── routes/analysis.py     # /api/analyze, /api/history, /api/health
│   ├── schemas/analysis.py    # Modelos Pydantic (request/response)
│   └── services/              # Singleton do DiabetesFactChecker + tempo de resposta
├── data/
│   ├── processed/             # Dataset rotulado: full (164), train (130), test (34)
│   └── raw/guidelines/        # Só o scraped_log.json é versionado (textos brutos não)
├── db/                        # PostgreSQL: schema.sql, models.py (ORM), database.py, migrations/
├── docs/
│   └── environments.md        # Diferenças entre dev e prod
├── frontend/                  # React + Vite
│   ├── src/                   # Páginas, componentes, providers, cliente da API
│   ├── Dockerfile             # Build multi-stage (node → nginx)
│   ├── nginx.conf             # Serve o SPA + proxy /api e /health
│   ├── .env.development       # VITE_API_URL vazio (usa proxy)
│   └── .env.production        # URL pública da API
├── knowledge_base/chromadb/   # Índice vetorial pronto (~34 MB, versionado)
├── models/                    # classifier_v2.joblib + relatórios de treino e limitações
├── scripts/                   # Pipeline offline: scraping, dataset, treino, ingestão, CLI
├── tests/                     # Testes de contrato da API
├── docker-compose.yml         # Perfis dev (só banco) e prod (banco + API + frontend)
├── Dockerfile                 # Imagem do backend
├── render.yaml / Procfile     # Deploy no Render
└── requirements*.txt          # Dependências Python
```

---

## 🚀 Quick start

### Pré-requisitos

| Ferramenta | Versão | Verificação |
|---|---|---|
| Python | 3.13+ | `python --version` |
| Node.js | 20 LTS | `node --version` |
| Docker | 24+ | `docker --version` |
| Git Bash (Windows) | — | — |
| C++ Build Tools (Windows) | — | Para compilar `scikit-learn` e `chromadb` |

**Opcional:** chave do Gemini em [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) — sem ela, o sistema funciona com `llm_explanation: null`.

### 1. Clone o repositório

```bash
git clone https://github.com/<seu-usuario>/challenge_1_berkanan.git
cd challenge_1_berkanan
```

### 2. Backend — ambiente Python

```bash
python -m venv venv
source venv/bin/activate              # Linux/macOS
# ou: source venv/Scripts/activate    # Git Bash (Windows)
# ou: .\venv\Scripts\Activate.ps1     # PowerShell

python -m pip install --upgrade pip
python -m pip install -r requirements-api.txt
```

> `requirements-api.txt` inclui `requirements.txt` (ML, RAG, Gemini, PostgreSQL e FastAPI). `requirements-rag.txt` só é necessário para scripts de prototipação com `langchain-google-genai`.
>
> ⏱️ Primeira instalação: ~15 min (torch + transformers, ~5 GB).

### 3. Configurar `.env`

```bash
cp .env.example .env
```

O `.env.example` já vem pronto para o ambiente local. Preencha `GEMINI_API_KEY` se quiser as explicações do LLM. A conexão com o banco é feita por `DATABASE_URL`; os campos `DB_*` (comentados) são alternativa quando `DATABASE_URL` não está definida.

### 4. Subir o PostgreSQL

```bash
docker compose --profile dev up -d
docker compose ps                     # aguardar "healthy"
```

O `db/schema.sql` é aplicado automaticamente na primeira inicialização do volume. Para um banco já existente criado antes das colunas de RAG, aplique a migração:

```bash
docker exec -i factchecker_db psql -U admin -d factchecker < db/migrations/002_add_rag_columns.sql
```

### 5. Base RAG

O índice vetorial já está versionado em `knowledge_base/chromadb/`, então **não é preciso** reconstruí-lo. Para regenerar a partir das fontes, veja [Pipeline offline](#-pipeline-offline-dados-treino-e-indexação).

### 6. Rodar o backend

```bash
uvicorn api.main:app --reload --port 8000
```

Confirme: `http://127.0.0.1:8000/health` → `{"status":"ok"}`. O primeiro start baixa o modelo de embeddings (~470 MB) do Hugging Face.

### 7. Frontend (em outro terminal)

```bash
cd frontend
npm install                           # primeira vez
npm run dev
```

Acesse **http://localhost:5173**, informe nome e e-mail na tela de entrada e envie uma afirmação.

> 💡 Em dev, o Vite faz proxy de `/api/*` e `/health` para `http://localhost:8000`, então não há problema de CORS.

### Fluxo resumido (copiar e colar)

```bash
# Backend
python -m venv venv && source venv/bin/activate
python -m pip install -r requirements-api.txt
cp .env.example .env
docker compose --profile dev up -d
uvicorn api.main:app --reload --port 8000

# Frontend (outro terminal)
cd frontend && npm install && npm run dev
```

---

## 🔌 Endpoints da API

| Método | Rota | Descrição | Request | Response |
|---|---|---|---|---|
| `GET` | `/health` | Liveness probe | — | `{"status":"ok"}` |
| `GET` | `/api/health` | Liveness probe (prefixado) | — | `{"status":"ok"}` |
| `POST` | `/api/analyze` | Analisa uma afirmação | `{"text": "..."}` (mín. 3 chars) | `AnalysisResponse` |
| `GET` | `/api/history` | Últimas 20 análises persistidas | — | `AnalysisHistoryResponse[]` |

### Exemplo com `curl`

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"text":"Canela cura diabetes?"}'
```

### `AnalysisResponse`

| Campo | Tipo | Significado |
|---|---|---|
| `id` | UUID | ID do registro em `analysis_history` |
| `input_text` | string | Afirmação analisada |
| `classification` | `REAL` \| `FAKE` | Rótulo do classificador (o schema também aceita `INCONCLUSIVE` e `PARTIALLY_TRUE`, não produzidos hoje) |
| `confidence_score` | float 0–1 | **Sempre `p_fake`** — probabilidade de a afirmação ser falsa |
| `threshold` | float 0–1 | Corte usado: `FAKE` se `p_fake >= threshold` |
| `matched_sources` | `[{text, source, similarity}]` | Até 3 trechos recuperados do ChromaDB |
| `llm_explanation` | string \| null | Explicação em markdown do Gemini |
| `llm_model` | string \| null | Modelo LLM configurado |
| `model_version` | string | Nome do classificador (`MultinomialNB`) |
| `rag_sources_count` | int | Quantidade de evidências |
| `response_time_ms` | int | Tempo do pipeline |
| `timestamp` | datetime | Data da análise |

### Swagger UI

Documentação interativa em **http://127.0.0.1:8000/docs**.

---

## ⚙️ Variáveis de ambiente

### Backend (`.env`)

| Variável | Obrigatória | Padrão | Descrição |
|---|---|---|---|
| `DATABASE_URL` | ❌ | — | URL SQLAlchemy do PostgreSQL. Se definida, tem prioridade sobre `DB_*` |
| `DB_HOST` / `DB_PORT` / `DB_NAME` / `DB_USER` / `DB_PASS` | ❌ | `localhost` / `5432` / `factchecker` / `admin` / `adminpassword` | Usadas só sem `DATABASE_URL` |
| `CHROMA_PERSIST_DIRECTORY` | ❌ | `knowledge_base/chromadb` | Diretório do índice vetorial |
| `EMBEDDING_MODEL_NAME` | ❌ | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` | Modelo de embeddings (deve ser o mesmo da ingestão) |
| `GEMINI_API_KEY` | ❌ | — | Chave do Google Gemini (sem ela, `llm_explanation: null`) |
| `LLM_MODEL` | ❌ | `gemini-3.8-flash` | Modelo Gemini |
| `LLM_MAX_RETRIES` | ❌ | `3` | Tentativas em falhas transitórias (408, 429, 5xx) |
| `APP_ENV` | ❌ | `development` | `development` ou `production` (altera as origens CORS padrão) |
| `FRONTEND_ORIGINS` | ❌ | `http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173` | Origens CORS, separadas por vírgula |
| `PORT` | ❌ | `8000` | Porta do backend (Render/Procfile) |

### Frontend

| Arquivo | Variável | Valor em dev | Valor em prod |
|---|---|---|---|
| `.env.development` | `VITE_API_URL` | *(vazio — usa proxy)* | — |
| `.env.production` | `VITE_API_URL` | — | `https://seu-backend.onrender.com` (ou vazio se atrás do nginx) |

---

## 🧠 Como funciona o pipeline

### 1. Classificação ML

- **Modelo:** `TF-IDF` (unigramas + bigramas, `sublinear_tf`) + `MultinomialNB` (`alpha=0.1`)
- **Treino:** 128 exemplos rotulados (`FAKE`/`REAL`) de `data/processed/diabetes_nutrition_dataset_train.csv` (2 exemplos fora de escopo removidos)
- **Artefato:** `models/classifier_v2.joblib` (pipeline + threshold + metadados)
- **Threshold:** `0.5`, escolhido pela calibração out-of-fold (maior recall de FAKE com precisão mínima de 0.7). Supera a meta mínima definida com threshold `0.29` (ver [Resultados](#-resultados-e-validação-dos-objetivos))
- **Saída:** `p_fake` ∈ [0, 1] → `FAKE` se `p_fake >= 0.5`, senão `REAL`

> ⚠️ **`confidence_score` é sempre `p_fake`**, mesmo quando a classificação é `REAL`. Não é probabilidade de veracidade nem confiança genérica. O frontend o exibe como "Probabilidade de a afirmação ser falsa".

### 2. RAG (Retrieval-Augmented Generation)

- **Base:** 89 documentos de 12 instituições, raspados de páginas oficiais
- **Chunking:** 800 caracteres com overlap de 120 → **3.896 trechos** indexados
- **Embeddings:** `paraphrase-multilingual-MiniLM-L12-v2` (normalizados)
- **Busca:** top-3 trechos mais similares à afirmação (`similarity = 1 − distância`)
- **Saída:** `matched_sources: [{text, source, similarity}]` (texto truncado em 300 chars)

> O RAG **não influencia** a classificação. Ele apenas traz as evidências exibidas ao usuário e usadas pelo LLM.

### 3. LLM (opcional)

- **Modelo:** Google Gemini (`LLM_MODEL`, padrão `gemini-3.8-flash`)
- **Prompt:** afirmação + rótulo e `p_fake` do ML + trechos recuperados, com instruções para usar apenas as evidências, explicar o risco no caso FAKE, citar as fontes e terminar com aviso médico
- **Saída:** explicação em markdown
- **Falha:** cota estourada (429), modelo descontinuado (404) ou chave ausente → `llm_explanation: null`

> O LLM **não classifica** e **não busca** — apenas redige com base no que o ML e o RAG já produziram.

### 4. Persistência

- **Banco:** PostgreSQL via SQLAlchemy ORM
- **Tabela:** `analysis_history` (texto, rótulo, `p_fake`, fontes em JSONB, explicação, modelo, tempo de resposta)
- **Consulta:** `GET /api/history` devolve as 20 mais recentes

---

## 🔄 Pipeline offline (dados, treino e indexação)

Esses scripts **não rodam na API** — servem para regenerar dataset, modelo e índice. Os artefatos resultantes já estão versionados.

| Ordem | Script | Faz | Gera |
|---|---|---|---|
| 1 | `scripts/scraper.py` | Raspa páginas oficiais (SBD, MS, MedlinePlus, OMS…) e fact-checks | `data/raw/guidelines/*.txt`, `scraped_log.json` |
| 2 | `scripts/dataset_builder.py` | Monta o dataset rotulado (exemplos curados + fact-checks), deduplica e divide treino/teste | `data/processed/*.csv` |
| 3 | `scripts/train_model.py` | Compara 4 algoritmos com GridSearchCV + StratifiedKFold | `models/cv_results.json`, `models/training_report.md` |
| 4 | `scripts/calibrate_and_evaluate.py` | Calibra o threshold no treino (out-of-fold) e avalia uma vez no teste | `models/training_metadata.json` |
| 5 | `scripts/classifier.py --train` | Treina o vencedor e exporta o artefato | `models/classifier_v2.joblib` |
| 6 | `scripts/batch_ingest.py` | Chunking + embeddings + inserção deduplicada no Chroma | `knowledge_base/chromadb/` |

`scripts/run_pipeline.py` executa a raspagem e, em seguida, treino e ingestão em paralelo.

**CLIs úteis:**

```bash
python scripts/classifier.py "Canela cura diabetes"         # só o classificador
python scripts/fact_checker.py "Canela cura diabetes"       # ML + RAG + LLM
python scripts/fact_checker.py --interactive                # modo interativo
```

---

## 🧪 Testes

```bash
# Testes de contrato da API (12 testes; não precisam de banco, Chroma nem Gemini)
python -m pip install pytest
python -m pytest tests/

# Testes de contrato do classificador (formato da saída, coerência com o threshold, casos conhecidos)
python scripts/test_classifier.py

# Smoke test end-to-end contra uma API rodando
API_BASE_URL=http://127.0.0.1:8000 python scripts/smoke_test.py
```

Os testes de API cobrem: rejeição de texto curto (422), contrato de resposta e CORS, OpenAPI de `/health` e `/history`, resposta com o banco fora do ar, contagem de fontes na persistência, cópia do índice para um volume vazio do Chroma, medição de tempo, retry do Gemini e fallback sem chave ou com erro do LLM.

---

## 🚢 Deploy

### Docker Compose (tudo local)

```bash
cp .env.example .env
docker compose --profile prod up -d --build
```

Sobe `db` (PostgreSQL), `backend` (porta 8000) e `frontend` (nginx na porta 5173, com proxy de `/api` e `/health` para o backend).

### Operação em produção (VM com Docker Compose)

O ambiente da equipe roda numa VM Azure com o perfil `prod`. Endereço e credenciais de acesso são compartilhados por canal interno e **não devem ser commitados**. Na pasta do projeto, dentro da VM:

```bash
# Atualizar o código
git pull origin main

# Aplicar mudanças no backend (o código fica dentro da imagem, então é preciso rebuild)
sudo docker compose --profile prod up -d --build backend

# Aplicar mudanças no frontend
sudo docker compose --profile prod up -d --build frontend

# Aplicar mudanças no .env (ex.: GEMINI_API_KEY) — recria o container para ler as novas variáveis
sudo docker compose --profile prod up -d backend

# Logs do backend em tempo real (chamadas ao Gemini, erros de banco, etc.)
sudo docker compose --profile prod logs -f backend
```

> ⚠️ `docker compose restart` **não** relê o `.env` e **não** aplica código novo: ele só reinicia o mesmo container. Use `up -d` (com `--build` quando o código mudar).
>
> Em instalações com o Compose v1, troque `docker compose` por `docker-compose`.

Boas práticas para o repositório público: nunca commitar `.env`, chaves de API, IPs ou usuários de servidor. Restrinja `FRONTEND_ORIGINS` à origem real do frontend e troque as senhas padrão do PostgreSQL (`DB_PASS`/`DATABASE_URL`) no servidor.

---

## ⚠️ Limitações conhecidas

Detalhes do classificador em [models/limitations.md](models/limitations.md).

**Modelo e dados**
- **Dataset pequeno** (164 exemplos: 106 FAKE, 58 REAL). O classificador aprende padrões de palavras e estilo, não medicina.
- **Falsos positivos conhecidos**: afirmações verdadeiras curtas e diretas podem ser classificadas como `FAKE` (ex.: "A insulina é um hormônio produzido pelo pâncreas" → `p_fake = 0.68`).
- **Classificador binário**: o schema aceita `INCONCLUSIVE` e `PARTIALLY_TRUE`, mas o modelo só produz `REAL` ou `FAKE`, inclusive para textos fora do escopo.
- **`confidence_score` é `p_fake`**: não é probabilidade de veracidade nem confiança calibrada.
- **Rótulo e evidências são independentes**: o RAG pode trazer trechos que contradizem o rótulo do ML; o LLM recebe ambos e pode divergir do rótulo na explicação.

**Sistema**
- **LLM é opcional e falível**: cota do free tier (~20 req/dia), modelo pode ser descontinuado (ex.: `gemini-2.0-flash` foi retirado), chave pode expirar.
- **RAG depende de base pré-indexada**: não há busca na web em tempo real. Afirmações sobre temas ausentes da base trazem evidências pouco relevantes.
- **Login sem autenticação**: a API é aberta e o `/api/history` mostra análises de todos os usuários (ver [Login sem autenticação](#-login-sem-autenticação)).
- **Análises feitas com o banco fora do ar não entram no histórico**: a resposta chega ao usuário com `id: null`, mas não é gravada depois.
- **Latência**: sem cache, cada análise roda embeddings + busca + chamada ao Gemini; o frontend espera até 180 s.

---

## 👥 Equipe e referências

**Equipe Berkanan** — Tópicos Especiais em Engenharia de Software - Sistemas de Machine Learning 2026/02.

**Fontes utilizadas no RAG** (documentos indexados):
- Sociedade Brasileira de Diabetes (SBD) — 34
- NIDDK (NIH) — 12
- MedlinePlus (NIH) — 9
- CDC — 6
- ADA, Diabetes UK, NHS — 5 cada
- Organização Mundial da Saúde (OMS) — 4
- IDF, OPAS — 3 cada
- Ministério da Saúde (MS) — 2
- SciELO — 1

**Referências técnicas:**
- Scikit-learn — documentação oficial
- LangChain — documentação oficial
- ChromaDB — documentação oficial

---

## 📄 Licença

Projeto acadêmico. Uso educacional.

> 🩺 **Aviso final:** este sistema é uma ferramenta de triagem acadêmica. Ele **não substitui** orientação de médico ou nutricionista. Sempre procure um profissional de saúde antes de tomar decisões sobre tratamento.
