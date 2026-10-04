"""
llm_client.py — Módulo de integração com a API do Google Gemini (google-genai).

Este módulo contém a lógica para gerar respostas fundamentadas nas evidências
recuperadas pelo RAG, explicando o motivo pelo qual uma alegação é FAKE ou REAL.
"""
import logging
import os

from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

RETRYABLE_STATUS_CODES = [408, 429, 500, 502, 503, 504]


class GeminiClient:
    def __init__(self, model_name="gemini-3.8-flash", api_key=None):
        """
        Inicializa o cliente da API do Gemini.
        O SDK automaticamente lê a variável GEMINI_API_KEY do ambiente, mas
        permite passagem explícita caso necessário.
        """
        self.model_name = os.getenv("LLM_MODEL") or model_name
        configured_api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.client = None
        if configured_api_key:
            retry_options = types.HttpRetryOptions(
                attempts=max(1, int(os.getenv("LLM_MAX_RETRIES", "3"))),
                initial_delay=0.5,
                max_delay=4.0,
                exp_base=2.0,
                http_status_codes=RETRYABLE_STATUS_CODES,
            )
            self.client = genai.Client(
                api_key=configured_api_key,
                http_options=types.HttpOptions(retry_options=retry_options),
            )

    def _build_prompt(self, claim: str, classification: str, confidence: float, evidence: list[dict]) -> str:
        """Constrói o prompt contendo a alegação, classificação ML e as evidências do ChromaDB."""
        
        # Formata as evidências recuperadas em texto
        evidence_text = ""
        if not evidence:
            evidence_text = "Nenhuma evidência oficial específica foi encontrada na base de conhecimento."
        else:
            for idx, ev in enumerate(evidence, 1):
                evidence_text += f"\n--- Evidência {idx} [Fonte: {ev.get('source', 'desconhecida')}] ---\n"
                evidence_text += f"{ev.get('text', '')}\n"

        prompt = f"""Você é um verificador de fatos (Fact-Checker) especialista em diabetes e nutrição.
A sua tarefa é analisar uma alegação feita por um usuário com base nas evidências fornecidas por diretrizes oficiais.
O modelo de aprendizado de máquina (ML) prévio já classificou essa alegação preliminarmente.

=== ALEGAÇÃO DO USUÁRIO ===
"{claim}"

=== CLASSIFICAÇÃO ML ===
Rótulo: {classification}
Confiança do Modelo: {confidence:.1%} de ser FAKE

=== EVIDÊNCIAS OFICIAIS RECUPERADAS (RAG) ===
{evidence_text}

=== INSTRUÇÕES ===
1. Responda diretamente e de forma clara, utilizando APENAS as evidências acima.
2. Não invente informações clínicas. Se a evidência for insuficiente, mencione isso.
3. Se a alegação for FAKE, explique POR QUE é perigoso para pessoas com diabetes acreditarem nisso.
4. Se a alegação for REAL, explique os fundamentos nutricionais/médicos que a suportam.
5. Em ambos os casos, mencione as fontes (arquivos) que serviram de base.
6. Use uma linguagem acessível e acolhedora, sem termos médicos extremamente complexos sem explicação.
7. Termine SEMPRE com o aviso: "⚠️ Lembre-se: este é um sistema acadêmico de checagem. Não substitui a orientação do seu médico ou nutricionista."
"""
        return prompt

    def generate_fact_check_response(
        self,
        claim: str,
        classification: str,
        confidence: float,
        evidence: list[dict],
    ) -> str | None:
        """
        Gera a explicação completa baseada em RAG chamando a API do Gemini.
        """
        if self.client is None:
            logger.warning("Gemini indisponível: GEMINI_API_KEY não está configurada.")
            return None

        prompt = self._build_prompt(claim, classification, confidence, evidence)
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text
        except Exception as e:
            logger.warning("Falha ao gerar explicação com Gemini: %s", e)
            return None
