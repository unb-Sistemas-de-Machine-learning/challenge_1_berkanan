"""
scraper.py — Raspagem de conteúdo real sobre diabetes e nutrição.

Coleta textos de fontes oficiais e confiáveis (páginas HTML) e salva
como .txt na pasta data/raw/guidelines/ para alimentar o ChromaDB.
Também raspa exemplos de fake news estritamente pertinentes a diabetes e nutrição
para o dataset de treino.
"""
import os
import re
import json
import time
import requests
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}
TIMEOUT = 25

# ====================================================================
# Fontes oficiais: páginas HTML com conteúdo confiável sobre diabetes
# ====================================================================
OFFICIAL_SOURCES = [
    # SBD - Diretrizes individuais (HTML)
    {
        "url": "https://diretriz.diabetes.org.br/tratamento-do-diabetes-mellitus-tipo-1-no-sus/",
        "name": "SBD_diagnostico_tratamento_DM1",
    },
    {
        "url": "https://diretriz.diabetes.org.br/manejo-do-diabetes-mellitus-tipo-2/",
        "name": "SBD_tratamento_farmacologico_DM2",
    },
    {
        "url": "https://diretriz.diabetes.org.br/terapia-nutricional-no-pre-diabetes-e-no-diabetes-mellitus-tipo-2/",
        "name": "SBD_orientacao_nutricional",
    },
    {
        "url": "https://diretriz.diabetes.org.br/diagnostico-de-diabetes-mellitus/",
        "name": "SBD_definicao_diagnostico_classificacao",
    },
    {
        "url": "https://diretriz.diabetes.org.br/metas-de-controle-glicemico/",
        "name": "SBD_metas_tratamento",
    },
    {
        "url": "https://diretriz.diabetes.org.br/diagnostico-e-tratamento-da-neuropatiaperiferica-diabetica/",
        "name": "SBD_neuropatia",
    },
    {
        "url": "https://diretriz.diabetes.org.br/manejo-da-retinopatia-diabetica/",
        "name": "SBD_retinopatia",
    },
    {
        "url": "https://diretriz.diabetes.org.br/doenca-renal-do-diabetes/",
        "name": "SBD_doenca_renal",
    },
    # Ministério da Saúde
    {
        "url": "https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/d/diabetes",
        "name": "MS_diabetes_pagina_principal",
    },
    # SciELO - artigos abertos
    {
        "url": "https://www.scielo.br/j/abem/a/GFkWfNpjZXymkMRzY5s68PJ/?lang=pt",
        "name": "SciELO_terapia_nutricional_DM2",
    },
]

# Palavras-chave obrigatórias para filtrar notícias e evitar vazamento de escopo
DIABETES_KEYWORDS = [
    "diabet", "glicem", "insulin", "glicose", "hiperglicem", "hipoglicem",
    "açúcar", "acucar", "carboidrat", "hemoglobina glicada", "hba1c",
    "metformina", "quiabo", "pâncreas", "pancreas"
]


def is_relevant_factcheck(title: str) -> bool:
    """Verifica se o título de fato se refere a diabetes/nutrição e está em português."""
    t = title.lower()
    if not any(k in t for k in DIABETES_KEYWORDS):
        return False
    # Filtra potenciais falsos positivos ou artigos em espanhol
    if any(w in t for w in [" el ", " la ", " los ", " las ", " es falso que ", " previene "]):
        return False
    return True


def fetch_page_text(url: str) -> str | None:
    """Faz GET na URL e extrai o texto limpo do body."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT, verify=False)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding or "utf-8"
        soup = BeautifulSoup(resp.text, "html.parser")

        # Remove scripts, estilos, nav, footer, sidebars
        for tag in soup(["script", "style", "nav", "footer", "header",
                         "aside", "form", "noscript", "iframe"]):
            tag.decompose()

        # Pega o artigo principal ou o body inteiro
        article = soup.find("article") or soup.find("main") or soup.body
        if article is None:
            return None

        text = article.get_text(separator="\n", strip=True)
        # Remove linhas vazias consecutivas
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()
    except Exception as e:
        print(f"  ✗ Erro ao acessar {url}: {e}")
        return None


def scrape_official_sources(output_dir: str):
    """Raspa fontes oficiais e salva como .txt."""
    os.makedirs(output_dir, exist_ok=True)
    log_path = os.path.join(output_dir, "scraped_log.json")

    # Carrega log de URLs já raspadas
    scraped = set()
    if os.path.exists(log_path):
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                scraped = set(json.load(f))
        except Exception:
            scraped = set()

    new_count = 0
    for source in OFFICIAL_SOURCES:
        url = source["url"]
        name = source["name"]
        out_path = os.path.join(output_dir, f"{name}.txt")

        # Só pula se estiver no log E o arquivo físico existir e tiver conteúdo
        if url in scraped and os.path.exists(out_path) and os.path.getsize(out_path) > 200:
            print(f"  — Já raspado e existente: {name}")
            continue

        print(f"  → Raspando: {name} ({url})")
        text = fetch_page_text(url)
        if text and len(text) > 200:
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(f"Fonte: {url}\n")
                f.write(f"Título: {name}\n")
                f.write("=" * 80 + "\n\n")
                f.write(text)
            scraped.add(url)
            new_count += 1
            print(f"    ✔ Salvo ({len(text)} chars)")
        else:
            print(f"    ⚠ Conteúdo insuficiente ou falha, ignorado")

        time.sleep(1.5)  # Rate-limiting respeitoso

    # Atualiza log apenas com o que realmente foi raspado
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(list(scraped), f, indent=2, ensure_ascii=False)

    print(f"\n✔ Raspagem de fontes oficiais concluída. {new_count} novos documentos salvos.")


# ====================================================================
# Raspagem de exemplos fake/real para o dataset de treino
# ====================================================================
def scrape_fact_checks(output_path: str):
    """Busca manchetes de fact-checks estritamente sobre diabetes em sites brasileiros."""
    urls = [
        "https://www.boatos.org/?s=diabetes",
        "https://www.e-farsas.com/?s=diabetes",
    ]
    results = []
    seen_texts = set()

    for url in urls:
        print(f"  → Raspando fact-checks: {url}")
        try:
            resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT, verify=False)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            for heading in soup.find_all(["h2", "h3"]):
                link = heading.find("a")
                if link and link.get_text(strip=True):
                    title = link.get_text(strip=True)
                    href = link.get("href", "")
                    # Filtra tamanho e pertinência temática
                    if len(title) > 20 and is_relevant_factcheck(title):
                        clean_t = title.strip()
                        if clean_t not in seen_texts:
                            seen_texts.add(clean_t)
                            results.append({
                                "text": clean_t,
                                "url": href,
                                "source": url.split("/")[2],
                            })
        except Exception as e:
            print(f"    ✗ Erro ao acessar {url}: {e}")
        time.sleep(1)

    if results:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"  ✔ {len(results)} manchetes temáticas de fact-check salvas em {output_path}")
    else:
        print("  ⚠ Nenhuma manchete temática encontrada nos sites.")


# ====================================================================
if __name__ == "__main__":
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    GUIDELINES_DIR = os.path.join(PROJECT_ROOT, "data", "raw", "guidelines")
    FACTCHECK_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "factchecks.json")

    print("=" * 60)
    print("ETAPA 1: Raspagem de fontes oficiais (SBD, MS, SciELO)")
    print("=" * 60)
    scrape_official_sources(GUIDELINES_DIR)

    print()
    print("=" * 60)
    print("ETAPA 2: Raspagem de fact-checks temáticos (boatos.org, e-farsas)")
    print("=" * 60)
    scrape_fact_checks(FACTCHECK_PATH)
