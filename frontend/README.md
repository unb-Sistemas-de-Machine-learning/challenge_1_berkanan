# BERKANAN Chatbot

Interface web para verificar afirmações sobre alimentação, nutrição e diabetes com base em evidências. O Berkanan não é médico, nutricionista, diagnóstico ou ferramenta de prescrição.

Este frontend foi gerado na plataforma Lumi com Vite, React, TypeScript e Tailwind CSS. O briefing original mencionava Next.js; a camada de páginas usa React Router com as mesmas rotas (`/login`, `/chat`, `/chat/:id`, `/history`).

## Requisitos

- Node.js 18+
- Backend FastAPI do Berkanan em execução (padrão: `http://localhost:8000`)

## Instalação

```bash
npm install
cp .env.example .env
npm run dev
```

## Variáveis de ambiente

Crie um arquivo `.env` a partir de `.env.example`:

```
VITE_API_URL=http://localhost:8000
NEXT_PUBLIC_API_URL=http://localhost:8000
```

A URL da API nunca é espalhada pelos componentes. Todas as chamadas passam por `src/lib/api-client.ts`.

## Endpoints usados

- `GET /health`
- `GET /api/health`
- `GET /api/history`
- `POST /api/analyze`

Não existem login, conversas, mensagens ou usuários no backend.

## Autenticação

A tela `/login` usa autenticação mock/local. A sessão fica no `localStorage` deste navegador. Nenhuma senha é armazenada e nenhum `POST /login` é feito.

## Histórico

- Conversas: estado local persistido no navegador.
- Análises recentes sincronizadas: `GET /api/history`. Se o endpoint falhar, o histórico local é preservado e a indisponibilidade é indicada.

## Limitações

- O frontend apenas consome HTTP/JSON.
- Fontes, explicações e classificações nunca são inventadas.
- Confiança da classificação não deve ser lida como certeza científica.
