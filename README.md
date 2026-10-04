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


---

# 🩺 Fact-Checker de Diabetes e Nutrição

Sistema de verificação de alegações sobre diabetes e nutrição usando IA, RAG (Retrieval-Augmented Generation) e bases de conhecimento oficiais.

## Arquitetura

```text
       Alegação do Usuário
                │
                ▼
┌───────────────────────────────────────┐
│         React + Vite (Frontend)       │
└───────────────────┬───────────────────┘
                    │ REST API (/api/analyze)
                    ▼
┌───────────────────────────────────────┐
│           FastAPI (Backend)           │
│             (api/main.py)             │
└───────────────────┬───────────────────┘
                    │
                    ▼
┌───────────────────────────────────────┐
│        fact_checker_service.py        │
│                                       │
│ 1. Classificação Base (MultinomialNB) │
│ 2. Busca RAG (ChromaDB)               │
│ 3. Síntese de Resposta (Gemini LLM)   │
│ 4. Persistência (PostgreSQL)          │
└───────────────────────────────────────┘
```

## Instalação e execução do backend

### Pré-requisitos

- Python **3.13.3** (versão verificada neste projeto) e `venv`.
- Docker Desktop com Docker Compose v2.
- Acesso à internet na primeira criação dos embeddings (download do modelo Hugging Face).
- No Windows, instale o **Microsoft Visual C++ Redistributable 2015–2022 x64** antes de carregar PyTorch. O erro `WinError 126` envolvendo `shm.dll` indica esse pré-requisito do runtime nativo; não copie DLLs para o repositório.
- `HF_TOKEN` é opcional. Sem ele, o Hugging Face Hub pode avisar sobre requisições não autenticadas, mas modelos públicos continuam disponíveis.

### Ambiente Python e configuração

No PowerShell:

```powershell
git clone <url-do-repositorio>
cd challenge_1_berkanan
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

No Git Bash para Windows, a ativação equivalente é `source venv/Scripts/activate`.
Edite `.env` se os valores locais forem diferentes. Nunca versione esse arquivo
nem coloque uma chave real no README. `GEMINI_API_KEY` pode ficar vazia: nesse
caso o backend mantém ML, recuperação RAG e persistência, mas retorna
`llm_explanation: null`. Em 503/429 e outros erros transitórios, o cliente SDK
faz até `LLM_MAX_RETRIES` tentativas com backoff exponencial; esgotadas as
tentativas, a análise continua sem explicação LLM.

O ChromaDB e os textos raspados são dados locais ignorados pelo Git. Para uma
instalação nova com evidências, baixe fontes oficiais e construa o índice:

```powershell
python scripts/scraper.py
python scripts/batch_ingest.py
```

Esses passos precisam de internet e podem levar algum tempo. O modelo já
treinado está em `models/classifier_v2.joblib`; não é necessário retreiná-lo
para iniciar a API.

### PostgreSQL

```powershell
docker compose --profile dev up -d
docker compose ps
docker compose exec -T db pg_isready -U admin -d factchecker
```

`db/schema.sql` é o schema inicial completo e é executado pelo entrypoint
oficial da imagem PostgreSQL **somente quando o volume de dados é criado**.
As migrations em `db/migrations/` são upgrades manuais para bancos existentes;
montá-las em uma subpasta de `docker-entrypoint-initdb.d` não as executa. Para
atualizar um banco antigo, aplique a migration disponível:

```powershell
docker compose exec -T db psql -U admin -d factchecker -f /migrations/002_add_rag_columns.sql
```

A migration é repetível e atualiza também `rag_sources_count` de registros
existentes. Não use `docker compose down -v` a menos que queira apagar
permanentemente o volume e os dados locais.

### Iniciar e verificar a API

```powershell
uvicorn api.main:app --reload --port 8000
```

Abra `http://localhost:8000/docs`. O padrão de `FRONTEND_ORIGINS` inclui as
origens do Vite (`http://localhost:5173` e `http://127.0.0.1:5173`) e
`http://localhost:3000`; sobrescreva a variável, se necessário, com uma lista
separada por vírgulas.

Com a API e o PostgreSQL ativos e o índice Chroma carregado, rode em outro
terminal:

```powershell
python scripts/smoke_test.py
```

O teste consulta os dois endpoints de health, analisa “Canela cura diabetes?”,
exige pelo menos uma fonte real, verifica a contagem e duração salvas e confirma
que a análise aparece no histórico. Não exige resposta do Gemini. A API também
expõe `GET /api/history`, `GET /api/health` e `GET /health`.

### Dependências e componentes

`requirements.txt` reúne as dependências de backend, ML e RAG; as versões
instaladas/testadas neste ambiente incluem FastAPI 0.142.2, Pydantic 2.13.5,
SQLAlchemy 2.1.3, ChromaDB 1.5.9, google-genai 2.28.0, sentence-transformers
6.1.0 e PyTorch 2.14.1+cpu. A integração Chroma usa o pacote recomendado
`langchain-chroma`; os scripts de ingestão e recuperação usam o mesmo pacote.
O modelo de embeddings é multilíngue
`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`.

## Componentes principais

| Componente | Localização | Responsabilidade |
|---|---|---|
| API | `api/` | FastAPI, contratos OpenAPI, análise e histórico. |
| Serviço ML/RAG | `api/services/`, `scripts/fact_checker.py` | Classificador local, embeddings, busca Chroma e explicação Gemini opcional. |
| Persistência | `db/` | Schema PostgreSQL, modelos SQLAlchemy e upgrades em `db/migrations/`. |
| Dados/índice | `data/`, `knowledge_base/chromadb/` | Datasets e corpus/índice local do RAG; preparar conforme instalação acima. |
| Modelo classificador | `models/classifier_v2.joblib` | Artefato de inferência já treinado. |

## Visão geral do ambiente e deploy

Este monorepo opera em desenvolvimento local e produção. O backend FastAPI
continua na raiz, com PostgreSQL pelo Docker Compose; o frontend React/Vite fica
em `frontend/`. Em desenvolvimento, a API atende em `http://localhost:8000` e
o Vite em `http://localhost:5173`. Em produção, o Render publica a API e o site
estático separadamente; Docker Compose também pode subir os três serviços.

### Pré-requisitos

- Python 3.13
- Node.js 20 ou compatível com o `package-lock.json` do frontend
- Docker Desktop + Docker Compose v2
- Chave válida do Gemini em `GEMINI_API_KEY`
- Acesso à internet para baixar o modelo de embeddings e popular o ChromaDB

### Desenvolvimento local

O fluxo usa dois terminais. No primeiro, na raiz do repositório:

```powershell
Copy-Item .env.example .env
.\venv\Scripts\Activate.ps1
docker compose --profile dev up -d
uvicorn api.main:app --reload --port 8000
```

No segundo terminal:

```powershell
cd frontend
npm install
npm run dev
```

O backend fica em `http://localhost:8000` e o frontend em
`http://localhost:5173`. Em desenvolvimento, as chamadas relativas a `/api` e
`/health` passam pelo proxy do Vite para `localhost:8000`, evitando CORS no
navegador; o padrão do backend também permite a origem `http://localhost:5173`.
Para criar o índice Chroma local, veja a seção **Fluxo do zero** no fim deste
documento.

### Variáveis de ambiente

| Nome | Obrigatória | Exemplo | Descrição |
|---|---:|---|---|
| `DATABASE_URL` | Sim em produção | `postgresql+psycopg2://user:pass@host:5432/db` | String completa de conexão com PostgreSQL. |
| `DB_HOST` | Não | `localhost` | Host do banco local. |
| `DB_PORT` | Não | `5432` | Porta do banco local. |
| `DB_NAME` | Não | `factchecker` | Nome do banco. |
| `DB_USER` | Não | `admin` | Usuário do banco. |
| `DB_PASS` | Não | `adminpassword` | Senha do banco. |
| `CHROMA_PERSIST_DIRECTORY` | Sim | `knowledge_base/chromadb` | Diretório persistente do ChromaDB. |
| `EMBEDDING_MODEL_NAME` | Sim | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` | Modelo de embedding utilizado pela busca por similaridade. |
| `GEMINI_API_KEY` | Sim para explicação LLM | `""` | Chave da API Gemini. Obtenha em `https://aistudio.google.com/app/apikey`. |
| `LLM_MODEL` | Sim | `gemini-3.8-flash` | Modelo LLM atual utilizado pela aplicação. |
| `LLM_MAX_RETRIES` | Não | `3` | Quantidade de tentativas para fallback de LLM. |
| `FRONTEND_ORIGINS` | Não em dev | `http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173` | Lista separada por vírgulas de origens permitidas pelo CORS. |
| `VITE_API_URL` | Em deploy estático | `https://berkanan-api.onrender.com` | URL pública da API compilada no frontend; vazia em dev usa o proxy do Vite. |
| `BACKEND_URL` | Não no Compose local | `http://backend:8000` | URL interna lida pelo nginx do frontend no perfil prod. |
| `APP_ENV` / `ENV` | Não | `development` | Declara se o ambiente corrente é local ou produção. |
| `PORT` | Não | `8000` | Porta do backend quando executado em container ou hosting. |

### Estrutura do monorepo

```text
.
├── api/                    # FastAPI e serviços do backend
├── db/                     # PostgreSQL, schema e migrations
├── scripts/                # Coleta, ingestão e utilitários
├── frontend/               # React + Vite + Tailwind
├── data/                   # Dados locais
├── knowledge_base/         # Índice ChromaDB
├── Dockerfile              # Imagem do backend
├── docker-compose.yml      # Perfis dev/prod
└── render.yaml             # Backend, frontend e banco no Render
```

O `package-lock.json` é a fonte de dependências do frontend nos builds npm;
`pnpm-lock.yml` também existe no repositório, mas não é usado neste fluxo.

### Produção local (Docker Compose)

Com o `.env` do backend configurado na raiz, suba a stack de produção local:

```powershell
docker compose --profile prod up -d --build
```

No perfil `prod`, o Compose sobrescreve `DB_HOST`, `DB_PORT` e `DATABASE_URL`
do `.env` para usar o hostname `db` na rede interna; o `.env` local continua
sendo usado pelo backend executado no host em desenvolvimento.
O frontend fica em `http://localhost:5173`. O nginx recebe
`BACKEND_URL=http://backend:8000` pelo Compose e encaminha `/api` e `/health`
pela rede interna; não é necessário expor a URL interna ao navegador.

### Deploy no Render

Conecte o repositório ao Render usando o `render.yaml`. Ele define o backend
Python, o banco PostgreSQL e um site estático Vite com `rootDir: frontend`.
Configure no painel:

- **Backend:** `GEMINI_API_KEY` com a chave real; `DATABASE_URL` com a conexão
  do PostgreSQL gerenciado; `FRONTEND_ORIGINS` com a origem pública exata do
  site estático (por exemplo, `https://berkanan-frontend.onrender.com`).
- **Frontend (Static Site):** `VITE_API_URL` com a URL pública do backend
  (por exemplo, `https://berkanan-api.onrender.com`).

O Render compila o frontend com `npm install && npm run build` e publica
`frontend/dist`. Não inclua barra final nem caminhos como `/api` no valor de
`VITE_API_URL`; a aplicação concatena os caminhos dos endpoints. O backend
mantém um disco persistente em `/var/chroma` para o índice vetorial.

A imagem Docker também pode ser usada em qualquer provedor que trate containers, com o mesmo conjunto de variáveis de ambiente.

### Estrutura de pastas

```text
.
├── api/                     # FastAPI e serviços do backend
├── db/                      # PostgreSQL, schema e modelos
├── frontend/                # React + Vite
├── data/                    # Dados e bases locais
├── knowledge_base/          # Índice vetorial do ChromaDB
├── models/                  # Artefatos do modelo e relatórios
├── scripts/                 # ETL, ingestão e utilitários
├── tests/                   # Testes de integração e API
├── .env.example             # Template de variáveis do ambiente
├── docker-compose.yml       # Perfis dev/prod
├── Dockerfile               # Imagem do backend
├── render.yaml              # Configuração de deploy
├── requirements*.txt        # Dependências Python
├── README.md                # Documentação principal
└── docs/                    # Documentação de ambientes
```

### Limitações conhecidas

- O dataset atual é pequeno para generalização ampla.
- `p_fake` representa um score de risco/discordância e não uma probabilidade estatística de veracidade formal.
- `llm_explanation` pode retornar `null` quando a chave do Gemini não está configurada ou a API falha.
- O classificador é binário e não cobre toda a complexidade da avaliação clínica ou nutricional.

### Aviso acadêmico

Este sistema é uma ferramenta de apoio para verificação de informações e não substitui orientação médica, nutricional ou profissional de saúde. O conteúdo gerado deve ser interpretado com crítico e sempre em conjunto com fontes confiáveis ou profissionais habilitados.

## Fluxo do zero

Os comandos abaixo são para PowerShell no Windows. Substitua a URL pelo
endereço real do repositório. No primeiro terminal, clone e configure o
backend:

```powershell
git clone https://github.com/unb-Sistemas-de-Machine-learning/challenge_1_berkanan.git
cd challenge_1_berkanan
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
```

Preencha `GEMINI_API_KEY` se quiser respostas com explicação Gemini; confira
`DATABASE_URL` e `FRONTEND_ORIGINS` no `.env`. Ainda no primeiro terminal,
baixe as fontes e popule o índice Chroma:

```powershell
python scripts/scraper.py
python scripts/batch_ingest.py
docker compose --profile dev up -d
uvicorn api.main:app --reload --port 8000
```

Em um segundo terminal, suba o frontend em modo de desenvolvimento:

```powershell
cd challenge_1_berkanan\frontend
npm install
npm run dev
```

Abra `http://localhost:5173`; a API e a documentação ficam em
`http://localhost:8000` e `http://localhost:8000/docs`. Para subir a stack
containerizada de produção local em vez dos dois servidores de desenvolvimento,
configure o `.env` da raiz e execute, a partir dela:

```powershell
docker compose --profile prod up -d --build
```
