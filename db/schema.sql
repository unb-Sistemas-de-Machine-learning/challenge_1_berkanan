-- ===========================================================
-- Schema: Analysis_History
-- Banco de conhecimento para o Fact-Checker de Diabetes
-- ===========================================================

CREATE TABLE IF NOT EXISTS Analysis_History (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    input_text TEXT NOT NULL,
    classification VARCHAR(50) NOT NULL
        CHECK (classification IN ('REAL', 'FAKE', 'INCONCLUSIVE')),
    confidence_score NUMERIC(5, 4)
        CHECK (confidence_score >= 0 AND confidence_score <= 1),
    matched_sources JSONB DEFAULT '[]'::jsonb,
    analysis_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    user_feedback BOOLEAN,
    model_version VARCHAR(100)
);

-- Índices para consultas frequentes
CREATE INDEX IF NOT EXISTS idx_analysis_classification
    ON Analysis_History (classification);

CREATE INDEX IF NOT EXISTS idx_analysis_date
    ON Analysis_History (analysis_date DESC);

CREATE INDEX IF NOT EXISTS idx_analysis_confidence
    ON Analysis_History (confidence_score DESC);

-- Índice GIN para buscas dentro do JSONB de fontes
CREATE INDEX IF NOT EXISTS idx_analysis_sources
    ON Analysis_History USING GIN (matched_sources);
