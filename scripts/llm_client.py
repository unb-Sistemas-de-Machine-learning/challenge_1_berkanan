"""
llm_client.py — Módulo de integração com a API do Google Gemini (google-genai).

Este módulo contém a lógica para gerar respostas fundamentadas nas evidências
recuperadas pelo RAG, explicando o motivo pelo qual uma alegação é FAKE ou REAL.
"""
import os
import json
from google import genai

class GeminiClient:
    def __init__(self, model_name="gemini-3.8-flash", api_key=None):
        """
        Inicializa o cliente da API do Gemini.
        O SDK automaticamente lê a variável GEMINI_API_KEY do ambiente, mas
        permite passagem explícita caso necessário.
        """
        self.model_name = os.getenv("LLM_MODEL", model_name)
        # O Client detecta GEMINI_API_KEY automaticamente do ambiente (.env)
        self.client = genai.Client(api_key=api_key) if api_key else genai.Client()

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
    ) -> str:
        """
        Gera a explicação completa baseada em RAG chamando a API do Gemini.
        """
        prompt = self._build_prompt(claim, classification, confidence, evidence)
        
        try:
            interaction = self.client.interactions.create(
                model=self.model_name,
                input=prompt
            )
            return interaction.output_text
        except Exception as e:
            print(f"Erro ao chamar API Gemini: {e}")
            return f"Houve um problema ao gerar a explicação detalhada com o LLM. (Erro: {e})"
