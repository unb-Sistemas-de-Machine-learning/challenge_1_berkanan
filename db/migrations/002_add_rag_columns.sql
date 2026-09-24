-- Adiciona colunas para armazenar os dados do RAG
ALTER TABLE Analysis_History
    ADD COLUMN IF NOT EXISTS llm_explanation TEXT,
    ADD COLUMN IF NOT EXISTS llm_model VARCHAR(100),
    ADD COLUMN IF NOT EXISTS rag_sources_count INTEGER DEFAULT 0,
    ADD COLUMN IF NOT EXISTS response_time_ms INTEGER;

COMMENT ON COLUMN Analysis_History.llm_explanation
    IS 'Texto explicativo gerado pelo LLM (Gemini) com base nas evidências do RAG';
COMMENT ON COLUMN Analysis_History.llm_model
    IS 'Modelo LLM utilizado (ex: gemini-3.8-flash)';
