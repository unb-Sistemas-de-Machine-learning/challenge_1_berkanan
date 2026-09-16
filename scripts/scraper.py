"""
scraper.py â€” Raspagem de conteÃºdo real sobre diabetes e nutriÃ§Ã£o.

Coleta textos de fontes oficiais e confiÃ¡veis (pÃ¡ginas HTML) e salva
como .txt na pasta data/raw/guidelines/ para alimentar o ChromaDB.
TambÃ©m raspa exemplos de fake news conhecidas para o dataset de treino.
"""
import os
import re
import json
import time
import hashlib
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}
TIMEOUT = 20


# ====================================================================
# Fontes oficiais: pÃ¡ginas HTML com conteÃºdo confiÃ¡vel sobre diabetes
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
    # MinistÃ©rio da SaÃºde
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


def fetch_page_text(url: str) -> str | None:
    """Faz GET na URL e extrai o texto limpo do body."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT, verify=False)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding or "utf-8"
        soup = BeautifulSoup(resp.text, "html.parser")

        # Remove scripts, estilos, nav, footer
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
        print(f"  âœ— Erro ao acessar {url}: {e}")
        return None


def scrape_official_sources(output_dir: str):
    """Raspa fontes oficiais e salva como .txt."""
    os.makedirs(output_dir, exist_ok=True)
    log_path = os.path.join(output_dir, "scraped_log.json")

    # Carrega log de URLs jÃ¡ raspadas
    scraped = set()
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            scraped = set(json.load(f))

    new_count = 0
    for source in OFFICIAL_SOURCES:
        url = source["url"]
        name = source["name"]

        if url in scraped:
            print(f"  â€” JÃ¡ raspado: {name}")
            continue

        print(f"  â†’ Raspando: {name} ({url})")
        text = fetch_page_text(url)
        if text and len(text) > 200:  # Ignora pÃ¡ginas quase vazias
            out_path = os.path.join(output_dir, f"{name}.txt")
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(f"Fonte: {url}\n")
                f.write(f"TÃ­tulo: {name}\n")
                f.write("=" * 80 + "\n\n")
                f.write(text)
            scraped.add(url)
            new_count += 1
            print(f"    âœ” Salvo ({len(text)} chars)")
        else:
            print(f"    âš  ConteÃºdo insuficiente, ignorado")

        time.sleep(1.5)  # Rate-limiting respeitoso

    # Persiste log
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(list(scraped), f, indent=2, ensure_ascii=False)

    print(f"\nâœ” Raspagem concluÃ­da. {new_count} novos documentos salvos.")


# ====================================================================
# Raspagem de exemplos fake/real para o dataset de treino
# ====================================================================
def scrape_fact_checks(output_path: str):
    """Busca manchetes de fact-checks sobre diabetes em sites brasileiros."""
    urls = [
        "https://www.boatos.org/?s=diabetes",
        "https://www.e-farsas.com/?s=diabetes",
    ]
    results = []

    for url in urls:
        print(f"  â†’ Raspando fact-checks: {url}")
        try:
            resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT, verify=False)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            for heading in soup.find_all(["h2", "h3"]):
                link = heading.find("a")
                if link and link.get_text(strip=True):
                    title = link.get_text(strip=True)
                    href = link.get("href", "")
                    if len(title) > 20:
                        results.append({
                            "text": title,
                            "url": href,
                            "source": url.split("/")[2],
                        })
        except Exception as e:
            print(f"    âœ— Erro: {e}")
        time.sleep(1)

    if results:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"  âœ” {len(results)} manchetes de fact-check salvas em {output_path}")
    else:
        print("  âš  Nenhuma manchete encontrada.")


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
    print("ETAPA 2: Raspagem de fact-checks (boatos.org, e-farsas)")
    print("=" * 60)
    scrape_fact_checks(FACTCHECK_PATH)

