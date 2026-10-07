# Ambientes: desenvolvimento e produção

## Desenvolvimento local

O ambiente de desenvolvimento é pensado para manter o workflow atual do projeto sem quebrar a API local. O backend continua sendo executado via:

```powershell
uvicorn api.main:app --reload
```

A API deve responder em `http://localhost:8000` e a CORS aceita, por padrão, as origens Vite e Next:

- `http://localhost:5173`
- `http://localhost:3000`
- `http://127.0.0.1:5173`

O PostgreSQL local pode ser levantado com:

```powershell
docker compose --profile dev up -d
```

Esse perfil apenas sobe o banco, preservando o comportamento já validado em desenvolvimento.

## Produção

Para o ambiente de produção, o backend deve receber variáveis explícitas de ambiente, especialmente:

- `DATABASE_URL`
- `GEMINI_API_KEY`
- `LLM_MODEL`
- `LLM_MAX_RETRIES`
- `FRONTEND_ORIGINS`
- `CHROMA_PERSIST_DIRECTORY`
- `EMBEDDING_MODEL_NAME`
- `APP_ENV=production`
- `PORT=8000`

Na infraestrutura Render, o `render.yaml` já declara essas variáveis e monta um volume persistente em `/var/chroma` para o ChromaDB. O backend usa `uvicorn api.main:app --host 0.0.0.0 --port $PORT` como comando de start.

Para rodar a stack de produção localmente (banco + backend + frontend com nginx):

```bash
docker compose --profile prod up -d --build
```

O frontend fica em `http://localhost:5173` e o nginx encaminha `/api` e `/health` para o backend.

### Índice do ChromaDB em produção

O índice vetorial versionado (`knowledge_base/chromadb/`) vai junto com o código. Tanto o perfil `prod` do `docker-compose.yml` quanto o `render.yaml` definem `CHROMA_PERSIST_DIRECTORY=/var/chroma`, um volume que começa vazio. No startup, a API verifica se o volume já tem um índice (`chroma.sqlite3`); se não tiver, copia o índice versionado para ele (`ensure_chroma_index` em `api/services/fact_checker_service.py`). Um índice já existente no volume nunca é sobrescrito.

Para forçar a atualização do índice no volume depois de uma nova ingestão, apague o conteúdo do volume e reinicie o backend com `docker compose --profile prod up -d backend`.

### Aplicar mudanças no servidor

O código do backend fica dentro da imagem, e `docker compose restart` não relê o `.env`. Por isso:

- mudança de código: `docker compose --profile prod up -d --build backend` (ou `frontend`);
- mudança no `.env`: `docker compose --profile prod up -d backend`.

Endereços, usuários e chaves do servidor não devem ser commitados: o repositório é público.

## Diferenças principais

| Aspecto | Desenvolvimento | Produção |
|---|---|---|
| Banco | PostgreSQL local em Docker | Postgres gerenciado ou banco externo |
| Chroma | `knowledge_base/chromadb` (versionado) | Volume persistente em `/var/chroma` (populado automaticamente no primeiro start) |
| CORS | Permite Vite/Next locais | Permite origem do frontend de produção |
| Secrets | `.env` local | Variáveis do provedor de deploy |
| Porta | `8000` | `PORT` do runtime |

## Recomendação

Manter o mesmo código em ambos os ambientes e ajustar somente variáveis de ambiente, sem alterar a assinatura dos endpoints nem a lógica de negócio central. Isso preserva o comportamento atual do sistema e facilita a migração para produção.
