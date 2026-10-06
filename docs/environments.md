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

## Diferenças principais

| Aspecto | Desenvolvimento | Produção |
|---|---|---|
| Banco | PostgreSQL local em Docker | Postgres gerenciado ou banco externo |
| Chroma | Diretório local | Volume persistente em `/var/chroma` |
| CORS | Permite Vite/Next locais | Permite origem do frontend de produção |
| Secrets | `.env` local | Variáveis do provedor de deploy |
| Porta | `8000` | `PORT` do runtime |

## Recomendação

Manter o mesmo código em ambos os ambientes e ajustar somente variáveis de ambiente, sem alterar a assinatura dos endpoints nem a lógica de negócio central. Isso preserva o comportamento atual do sistema e facilita a migração para produção.
