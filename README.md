# challenge_1_berkanan
Challenge 1 - Equipe Berkanan - Sistemas de Machine Learning 2026/02

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
- [Arquitetura](#-arquitetura)
- [Stack técnica](#-stack-técnica)
- [Estrutura do repositório](#-estrutura-do-repositório)
- [Quick start](#-quick-start)
- [Endpoints da API](#-endpoints-da-api)
- [Variáveis de ambiente](#-variáveis-de-ambiente)
- [Como funciona o pipeline](#-como-funciona-o-pipeline)
- [Limitações conhecidas](#-limitações-conhecidas)
- [Equipe e referências](#-equipe-e-referências)

---

## 🎯 Sobre o projeto

**Problema:** pessoas com diabetes tomam decisões alimentares sem verificar a veracidade das informações que recebem, especialmente em correntes de WhatsApp e redes sociais. Isso pode levar à redução ou abandono de tratamentos essenciais (ex.: insulina).

**Solução:** um chatbot que recebe uma afirmação em português (ex.: *"canela cura diabetes"*), classifica como **verdadeira ou falsa**, e apresenta **evidências de fontes oficiais** (SBD, Ministério da Saúde, MedlinePlus, OMS, CDC, etc.) com explicação contextualizada para o diabetes.

**Escopo:**
- ✅ Afirmações sobre alimentação, dietas e mitos relacionados a diabetes
- ❌ Prescrições médicas, dosagens de insulina, diagnósticos clínicos

---

## 🏗️ Arquitetura

O sistema é composto por **quatro camadas independentes**, cada uma com responsabilidade clara:

```text
┌──────────────────────────────────────────────────────────────────┐
│                        NAVEGADOR (Usuário)                       │
└──────────────────────────────┬───────────────────────────────────┘
                               │ HTTP
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│              FRONTEND — React + Vite + Tailwind                  │
│              (chat, histórico, markdown renderizado)             │
└──────────────────────────────┬───────────────────────────────────┘
                               │ fetch /api/analyze
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│              BACKEND — FastAPI (api/main.py)                     │
│              POST /api/analyze  ·  GET /api/history              │
└──────────────────────────────┬───────────────────────────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        ▼                      ▼                      ▼
┌────────────────┐   ┌─────────────────┐   ┌──────────────────┐
│ 1. ML          │   │ 2. RAG          │   │ 3. LLM (opcional)│
│ MultinomialNB  │   │ Embeddings +    │   │ Gemini gera      │
│ + TF-IDF       │   │ ChromaDB top-3  │   │ explicação em    │
│ → p_fake       │   │ → matched_src[] │   │ markdown         │
└────────┬───────┘   └────────┬────────┘   └─────────┬────────┘
         │                    │                      │
         └────────────────────┼──────────────────────┘
                              ▼
                   ┌──────────────────────┐
                   │ 4. PostgreSQL        │
                   │ Histórico persistido │
                   └──────────────────────┘
```

**Características importantes:**
- Cada camada é **independente** — a falha de uma não derruba as outras
- Se o LLM falhar (`429`, `503`, sem chave), `llm_explanation` vira `null` — classificação e evidências continuam
- Se o banco cair, a análise é devolvida com `id: null` — só não persiste no histórico
- Se o Chroma estiver vazio, `matched_sources: []` — a classificação ML continua

---

## 🧰 Stack técnica

### Backend

| Camada | Tecnologia |
|---|---|
| API | FastAPI + Uvicorn |
| Validação | Pydantic v2 |
| ML | scikit-learn (`MultinomialNB` + `TF-IDF`) |
| Embeddings | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` |
| Vector store | ChromaDB (via `langchain-chroma`) |
| Orquestração RAG | LangChain |
| LLM | Google Gemini (`google-genai`) |
| Banco relacional | PostgreSQL 16 + SQLAlchemy + psycopg2 |
| Scraping | Requests + BeautifulSoup4 + PyMuPDF |

### Frontend

| Camada | Tecnologia |
|---|---|
| Framework | React 18 |
| Build | Vite 5 |
| Estilo | Tailwind CSS |
| Roteamento | React Router |
| Animações | Framer Motion |
| Ícones | Lucide React |
| Markdown | react-markdown + remark-gfm |

---

## 📁 Estrutura do repositório

Monorepo com **backend na raiz** e **frontend em `frontend/`**:

```text
challenge_1_berkanan/
├── api/                       # Backend FastAPI
│   ├── main.py                # Ponto de entrada (uvicorn api.main:app)
│   ├── routes/                # Endpoints (/analyze, /history, /health)
│   ├── schemas/               # Modelos Pydantic
│   └── services/              # Orquestração ML + RAG + LLM
├── data/                      # Dataset rotulado + guidelines raspadas
│   ├── processed/             # CSVs (full, train, test) — versionados
│   └── raw/guidelines/        # Textos oficiais coletados (não versionados)
├── db/                        # PostgreSQL (models, schema, migrations)
├── docs/                      # Documentação adicional
│   └── environments.md        # Diferenças entre dev e prod
├── frontend/                  # React + Vite (monorepo)
│   ├── src/                   # Componentes, páginas, hooks, providers
│   ├── Dockerfile             # Build multi-stage (node → nginx)
│   ├── nginx.conf             # Serve SPA + proxy /api
│   ├── .env.development       # Vite dev (proxy)
│   └── .env.production        # Vite prod (URL pública)
├── knowledge_base/chromadb/   # Índice vetorial (gerado, não versionado)
├── models/                    # classifier_v2.joblib + metadados
├── scripts/                   # Pipeline: scraper, batch_ingest, treino
├── tests/                     # Testes de API
├── docker-compose.yml         # Perfis dev/prod
├── Dockerfile                 # Imagem do backend
├── render.yaml                # Config de deploy
├── requirements*.txt          # Dependências Python
└── README.md
```

---

## 🚀 Quick start

### Pré-requisitos

| Ferramenta | Versão | Verificação |
|---|---|---|
| Python | 3.13+ | `python --version` |
| Node.js | 20 LTS | `node --version` |
| Docker Desktop | 24+ | `docker --version` |
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
source venv/Scripts/activate          # Git Bash
# ou: .\venv\Scripts\Activate.ps1     # PowerShell

python -m pip install --upgrade pip
python -m pip install -r requirements.txt -r requirements-api.txt -r requirements-rag.txt
```

> ⏱️ Primeira instalação: ~15 min (torch + transformers, ~5 GB).

### 3. Configurar `.env`

```bash
cp .env.example .env
```

Edite `.env`:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=factchecker
DB_USER=admin
DB_PASS=adminpassword

CHROMA_PERSIST_DIRECTORY=knowledge_base/chromadb
EMBEDDING_MODEL_NAME=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2

GEMINI_API_KEY=                       # opcional
LLM_MODEL=gemini-3.8-flash
LLM_MAX_RETRIES=3

APP_ENV=development
FRONTEND_ORIGINS=http://localhost:5173,http://localhost:3000
PORT=8000
```

### 4. Subir o PostgreSQL

```bash
docker compose --profile dev up -d
sleep 10
docker compose ps                     # esperar "healthy"
docker exec -i factchecker_db psql -U admin -d factchecker < db/schema.sql
```

### 5. Popular a base RAG (só na primeira vez)

```bash
python scripts/scraper.py             # 5–15 min
python scripts/batch_ingest.py        # 3–10 min
```

### 6. Rodar o backend

```bash
uvicorn api.main:app --reload --port 8000
```

Confirme: `http://127.0.0.1:8000/health` → `{"status":"ok"}`

### 7. Frontend (em outro terminal)

```bash
cd frontend
npm install                           # primeira vez
npm run dev
```

Acesse **http://localhost:5173**

> 💡 Em dev, o Vite faz proxy de `/api/*` para `http://localhost:8000`, então **não há CORS** mesmo em origens cruzadas.

### Fluxo resumido (copiar e colar)

```bash
# Backend
python -m venv venv && source venv/Scripts/activate
python -m pip install -r requirements.txt -r requirements-api.txt -r requirements-rag.txt
cp .env.example .env
docker compose --profile dev up -d && sleep 10
docker exec -i factchecker_db psql -U admin -d factchecker < db/schema.sql
python scripts/scraper.py && python scripts/batch_ingest.py   # primeira vez
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
| `GET` | `/api/history` | Últimas 20 análises persistidas | — | `AnalysisResponse[]` |


### Exemplo com `curl`

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"text":"Canela cura diabetes?"}'
```

### Swagger UI

Documentação interativa em **http://127.0.0.1:8000/docs**.

---

## ⚙️ Variáveis de ambiente

### Backend (`.env`)

| Variável | Obrigatória | Padrão | Descrição |
|---|---|---|---|
| `DB_HOST` | ✅ | `localhost` | Host do PostgreSQL |
| `DB_PORT` | ✅ | `5432` | Porta |
| `DB_NAME` | ✅ | `factchecker` | Nome do banco |
| `DB_USER` | ✅ | `admin` | Usuário |
| `DB_PASS` | ✅ | `adminpassword` | Senha |
| `DATABASE_URL` | ❌ | — | Alternativa ao bloco `DB_*` (usado em prod) |
| `CHROMA_PERSIST_DIRECTORY` | ✅ | `knowledge_base/chromadb` | Diretório do índice vetorial |
| `EMBEDDING_MODEL_NAME` | ✅ | `paraphrase-multilingual-MiniLM-L12-v2` | Modelo de embeddings |
| `GEMINI_API_KEY` | ❌ | — | Chave do Google Gemini (sem ela, `llm_explanation: null`) |
| `LLM_MODEL` | ✅ | `gemini-3.8-flash` | Modelo Gemini |
| `LLM_MAX_RETRIES` | ❌ | `3` | Tentativas em caso de falha transitória |
| `APP_ENV` | ✅ | `development` | `development` ou `production` |
| `FRONTEND_ORIGINS` | ✅ | `http://localhost:5173,...` | Origens permitidas para CORS |
| `PORT` | ❌ | `8000` | Porta do backend |

### Frontend

| Arquivo | Variável | Valor em dev | Valor em prod |
|---|---|---|---|
| `.env.development` | `VITE_API_URL` | *(vazio — usa proxy)* | — |
| `.env.production` | `VITE_API_URL` | — | `https://seu-backend.onrender.com` |

---

## 🧠 Como funciona o pipeline

### 1. Classificação ML

- **Modelo:** `MultinomialNB` com TF-IDF (unigramas + bigramas)
- **Treino:** CSVs rotulados (`FAKE`/`REAL`) em `data/processed/`
- **Artefato:** `models/classifier_v2.joblib`
- **Threshold calibrado:** `0.29` (otimizado para recall de `FAKE`)
- **Saída:** `p_fake` ∈ [0, 1] → comparado ao threshold → `FAKE` ou `REAL`

> ⚠️ **`confidence_score` é sempre `p_fake`**, mesmo quando a classificação é `REAL`. Não é probabilidade de veracidade nem confiança genérica.

### 2. RAG (Retrieval-Augmented Generation)

- **Base:** documentos oficiais em `data/raw/guidelines/`
- **Chunking:** 800 chars com overlap de 120
- **Embeddings:** `paraphrase-multilingual-MiniLM-L12-v2`
- **Busca:** top-3 chunks mais similares à afirmação
- **Saída:** `matched_sources: [{text, source, similarity}]`

> O RAG **não influencia** a classificação. Ele apenas traz as evidências que serão exibidas ao usuário e usadas pelo LLM para gerar a explicação.

### 3. LLM (opcional)

- **Modelo:** Google Gemini (`gemini-3.8-flash`)
- **Prompt:** afirmação + classificação ML + trechos recuperados
- **Saída:** explicação em markdown
- **Falha:** se a cota estourar (429), o modelo for descontinuado (404) ou a chave estiver ausente, `llm_explanation` vira `null`

> O LLM **não classifica** e **não busca** — apenas redige com base no que o ML e o RAG já produziram.

### 4. Persistência

- **Banco:** PostgreSQL via SQLAlchemy
- **Tabela:** `analysis_history`
- **Falha:** se o DB cair, a resposta ainda é enviada com `id: null` — apenas não é salva no histórico

---

## ⚠️ Limitações conhecidas

Documentadas em `models/limitations.md`:

- **Dataset pequeno** (~164 exemplos). O classificador aprende padrões de palavras, não medicina.
- **Falsos positivos conhecidos**: afirmações verdadeiras curtas podem ser classificadas como `FAKE` se usarem vocabulário frequente em exemplos falsos no treino.
- **Classificador binário**: embora o schema aceite `INCONCLUSIVE` e `PARTIALLY_TRUE`, o modelo atual só produz `REAL` ou `FAKE`.
- **`confidence_score` é `p_fake`**: não é probabilidade de veracidade nem confiança calibrada.
- **LLM é opcional e falível**: cota do free tier (~20 req/dia), modelo pode ser descontinuado, chave pode expirar.
- **RAG depende de base pré-indexada**: o sistema não faz busca na web em tempo real. Se a afirmação fala de algo que não está no Chroma, `matched_sources` pode vir vazio.
- **Gemini 404 / 429**: o modelo `gemini-2.0-flash` foi descontinuado. Use `gemini-3.8-flash`.

---

## 👥 Equipe e referências

**Equipe Berkanan** — Tópicos Especiais de Engenharia de Software 2026/2.

**Fontes utilizadas no RAG:**
- Sociedade Brasileira de Diabetes (SBD)
- Ministério da Saúde (MS)
- MedlinePlus (NIH)
- Organização Mundial da Saúde (OMS)
- OPAS, CDC, NHS, ADA, IDF, NIDDK, SciELO

**Referências técnicas:**
- Scikit-learn — documentação oficial
- LangChain — documentação oficial
- ChromaDB — documentação oficial

---

## 📄 Licença

Projeto acadêmico. Uso educacional.

> 🩺 **Aviso final:** este sistema é uma ferramenta de triagem acadêmica. Ele **não substitui** orientação de médico ou nutricionista. Sempre procure um profissional de saúde antes de tomar decisões sobre tratamento.