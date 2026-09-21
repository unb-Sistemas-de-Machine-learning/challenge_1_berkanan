"""
scraper.py — Raspagem de conteúdo real sobre diabetes e nutrição.

Coleta textos de fontes oficiais e confiáveis (páginas HTML) e salva
como .txt na pasta data/raw/guidelines/ para alimentar o ChromaDB.
Também raspa exemplos de fake news conhecidas para o dataset de treino.
"""
import os
import re
import sys
import json
import time
import requests
import urllib3
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Corrige o mojibake (â†’, âœ”, Ã©...) que aparece no PowerShell: o console do
# Windows nem sempre usa UTF-8 por padrão, então forçamos a codificação de
# saída. Isso não muda o conteúdo dos arquivos salvos, só o que é impresso.
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# Estamos usando verify=False de propósito (ver fetch_page_text), então
# silenciamos o aviso repetido do urllib3 em vez de ignorá-lo linha a linha.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}
TIMEOUT = 25
MIN_CONTENT_CHARS = 200


def build_http_session() -> requests.Session:
    """Cria uma sessão com retry para falhas transitórias, incluindo 504."""
    retry = Retry(
        total=3,
        connect=3,
        read=3,
        status=3,
        backoff_factor=1.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET"}),
        respect_retry_after_header=True,
        raise_on_status=False,
    )
    session = requests.Session()
    session.headers.update(HEADERS)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


SESSION = build_http_session()


# ====================================================================
# Fontes oficiais: páginas HTML com conteúdo confiável sobre diabetes
# ====================================================================
OFFICIAL_SOURCES = [
    # SBD - Diretrizes individuais (HTML)
    # URLs revisadas em 2026-09; o site da SBD reorganizou os slugs desde
    # que a lista original foi montada, então os antigos devolviam 404.
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
        "name": "SBD_orientacao_nutricional_DM2",
    },
    {
        "url": "https://diretriz.diabetes.org.br/terapia-nutricional-no-diabetes-tipo-1/",
        "name": "SBD_orientacao_nutricional_DM1",
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
    {
        "url": "https://diretriz.diabetes.org.br/planejamento-metas-e-monitorizacao-do-diabetes-durante-a-gestacao/",
        "name": "SBD_diabetes_gestacional",
    },
    {
        "url": "https://diretriz.diabetes.org.br/atividade-fisica-e-exercicio-fisico-no-diabetes-mellitus-tipo-1/",
        "name": "SBD_atividade_fisica_DM1",
    },
    {
        "url": "https://diretriz.diabetes.org.br/atividade-fisica-e-exercicio-no-pre-diabetes-e-dm2/",
        "name": "SBD_atividade_fisica_DM2",
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
    {
        "url": "https://www.scielo.br/j/abem/a/NLm7zgDx85LgZhsLKywtgCB/?format=html&lang=pt",
        "name": "SciELO_diabetes_gestacional_algoritmo",
    },
    # OPAS/OMS - referência institucional internacional
    {
        "url": "https://www.paho.org/bra/index.php?option=com_content&view=article&id=5053:numero-de-pessoas-com-diabetes-nas-americas-triplicou-desde-1980&Itemid=839",
        "name": "OPAS_diabetes_americas_epidemiologia",
    },
    # Organização Mundial da Saúde
    {"url": "https://www.who.int/health-topics/diabetes", "name": "OMS_diabetes"},
    {"url": "https://www.who.int/news-room/fact-sheets/detail/diabetes", "name": "OMS_diabetes_fatos"},
    {"url": "https://www.who.int/publications/i/item/9789240075194", "name": "OMS_relatorio_diabetes"},
    {"url": "https://www.paho.org/en/topics/diabetes", "name": "OPAS_diabetes"},
    {"url": "https://www.paho.org/en/topics/noncommunicable-diseases", "name": "OPAS_doencas_cronicas"},
    # Centers for Disease Control and Prevention (CDC)
    {"url": "https://www.cdc.gov/diabetes/about/index.html", "name": "CDC_sobre_diabetes"},
    {"url": "https://www.cdc.gov/diabetes/signs-symptoms/index.html", "name": "CDC_sinais_sintomas"},
    {"url": "https://www.cdc.gov/diabetes/risk-factors/index.html", "name": "CDC_fatores_risco"},
    {"url": "https://www.cdc.gov/diabetes/prevention-type-2/index.html", "name": "CDC_prevencao_DM2"},
    {"url": "https://www.cdc.gov/diabetes/healthy-eating/index.html", "name": "CDC_alimentacao_saudavel"},
    {"url": "https://www.cdc.gov/diabetes/living-with/index.html", "name": "CDC_vivendo_diabetes"},
    {"url": "https://www.cdc.gov/diabetes/data-research/index.html", "name": "CDC_dados_diabetes"},
    # National Institute of Diabetes and Digestive and Kidney Diseases (NIDDK)
    {"url": "https://www.niddk.nih.gov/health-information/diabetes/overview/what-is-diabetes", "name": "NIDDK_o_que_e_diabetes"},
    {"url": "https://www.niddk.nih.gov/health-information/diabetes/overview/types", "name": "NIDDK_tipos_diabetes"},
    {"url": "https://www.niddk.nih.gov/health-information/diabetes/overview/symptoms-causes", "name": "NIDDK_sintomas_causas"},
    {"url": "https://www.niddk.nih.gov/health-information/diabetes/overview/tests-diagnosis", "name": "NIDDK_diagnostico"},
    {"url": "https://www.niddk.nih.gov/health-information/diabetes/overview/treatment", "name": "NIDDK_tratamento"},
    {"url": "https://www.niddk.nih.gov/health-information/diabetes/overview/diet-eating-physical-activity", "name": "NIDDK_dieta_atividade"},
    {"url": "https://www.niddk.nih.gov/health-information/diabetes/overview/preventing-problems", "name": "NIDDK_prevencao_complicacoes"},
    {"url": "https://www.niddk.nih.gov/health-information/diabetes/overview/insulin-medicines-treatments", "name": "NIDDK_insulina_medicamentos"},
    {"url": "https://www.niddk.nih.gov/health-information/diabetes/overview/managing-diabetes", "name": "NIDDK_controle_diabetes"},
    # MedlinePlus / National Library of Medicine
    {"url": "https://medlineplus.gov/diabetes.html", "name": "MedlinePlus_diabetes"},
    {"url": "https://medlineplus.gov/diabetestype1.html", "name": "MedlinePlus_DM1"},
    {"url": "https://medlineplus.gov/diabetestype2.html", "name": "MedlinePlus_DM2"},
    {"url": "https://medlineplus.gov/diabeticdiet.html", "name": "MedlinePlus_dieta_diabetes"},
    {"url": "https://medlineplus.gov/diabeticfoot.html", "name": "MedlinePlus_pe_diabetico"},
    # National Health Service (NHS)
    {"url": "https://www.nhs.uk/conditions/diabetes/", "name": "NHS_diabetes"},
    {"url": "https://www.nhs.uk/conditions/type-1-diabetes/", "name": "NHS_DM1"},
    {"url": "https://www.nhs.uk/conditions/type-2-diabetes/", "name": "NHS_DM2"},
    {"url": "https://www.nhs.uk/conditions/gestational-diabetes/", "name": "NHS_diabetes_gestacional"},
    {"url": "https://www.nhs.uk/conditions/diabetic-retinopathy/", "name": "NHS_retinopatia"},
    {"url": "https://www.nhs.uk/conditions/diabetic-neuropathy/", "name": "NHS_neuropatia"},
    {"url": "https://www.nhs.uk/live-well/eat-well/food-guidelines-and-food-labels/", "name": "NHS_guia_alimentar"},
    # Diabetes UK
    {"url": "https://www.diabetes.org.uk/about-diabetes/type-1-diabetes", "name": "DiabetesUK_DM1"},
    {"url": "https://www.diabetes.org.uk/about-diabetes/type-2-diabetes", "name": "DiabetesUK_DM2"},
    {"url": "https://www.diabetes.org.uk/about-diabetes/gestational-diabetes", "name": "DiabetesUK_gestacional"},
    {"url": "https://www.diabetes.org.uk/guide-to-diabetes/enjoy-food", "name": "DiabetesUK_alimentacao"},
    {"url": "https://www.diabetes.org.uk/guide-to-diabetes/complications", "name": "DiabetesUK_complicacoes"},
    # American Diabetes Association
    {"url": "https://diabetes.org/about-diabetes/type-1", "name": "ADA_DM1"},
    {"url": "https://diabetes.org/about-diabetes/type-2", "name": "ADA_DM2"},
    {"url": "https://diabetes.org/food-nutrition", "name": "ADA_nutricao"},
    {"url": "https://diabetes.org/health-wellness/fitness", "name": "ADA_atividade_fisica"},
    {"url": "https://diabetes.org/living-with-diabetes/treatment-care", "name": "ADA_tratamento"},
    # Mayo Clinic e Federação Internacional de Diabetes
    {"url": "https://www.mayoclinic.org/diseases-conditions/type-2-diabetes/symptoms-causes/syc-20351193", "name": "Mayo_DM2"},
    {"url": "https://www.mayoclinic.org/diseases-conditions/type-1-diabetes/symptoms-causes/syc-20353011", "name": "Mayo_DM1"},
    {"url": "https://idf.org/about-diabetes/what-is-diabetes/", "name": "IDF_o_que_e_diabetes"},
    {"url": "https://idf.org/about-diabetes/diabetes-complications/", "name": "IDF_complicacoes"},
]


def fetch_page_text(url: str) -> str | None:
    """Faz GET resiliente e extrai o texto limpo da página."""
    try:
        resp = SESSION.get(url, timeout=(10, TIMEOUT), verify=False)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding or "utf-8"
        soup = BeautifulSoup(resp.text, "html.parser")

        # Remove scripts, estilos, nav, footer
        for tag in soup(["script", "style", "nav", "footer", "header",
                         "aside", "form", "noscript", "iframe"]):
            tag.decompose()

        # Alguns sites usam divs em vez de article/main. Tenta o conteúdo
        # mais específico primeiro e usa o body como fallback.
        candidates = [
            soup.find("article"),
            soup.find("main"),
            soup.find(attrs={"role": "main"}),
            soup.body,
        ]
        for candidate in candidates:
            if candidate is None:
                continue
            text = candidate.get_text(separator="\n", strip=True)
            text = re.sub(r"\n{3,}", "\n\n", text).strip()
            if len(text) >= MIN_CONTENT_CHARS:
                return text
        print(f"  ⚠ Conteúdo realmente insuficiente: HTTP {resp.status_code} ({url})")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"  ✗ HTTP {getattr(e.response, 'status_code', '?')} após retries: {url}")
        return None
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
        with open(log_path, "r", encoding="utf-8") as f:
            scraped = set(json.load(f))

    new_count = 0
    for source in OFFICIAL_SOURCES:
        url = source["url"]
        name = source["name"]

        if url in scraped:
            print(f"  — Já raspado: {name}")
            continue

        print(f"  → Raspando: {name} ({url})")
        text = fetch_page_text(url)
        if text and len(text) >= MIN_CONTENT_CHARS:
            out_path = os.path.join(output_dir, f"{name}.txt")
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(f"Fonte: {url}\n")
                f.write(f"Título: {name}\n")
                f.write("=" * 80 + "\n\n")
                f.write(text)
            scraped.add(url)
            new_count += 1
            print(f"    ✔ Salvo ({len(text)} chars)")
        else:
            print("    ⚠ Fonte não salva; será tentada novamente na próxima execução.")

        time.sleep(1.5)  # Rate-limiting respeitoso

    # Persiste log
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(list(scraped), f, indent=2, ensure_ascii=False)

    print(f"\n✔ Raspagem concluída. {new_count} novos documentos salvos.")


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
        print(f"  → Raspando fact-checks: {url}")
        try:
            resp = SESSION.get(url, timeout=(10, TIMEOUT), verify=False)
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
            print(f"    ✗ Erro: {e}")
        time.sleep(1)

    if results:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"  ✔ {len(results)} manchetes de fact-check salvas em {output_path}")
    else:
        print("  ⚠ Nenhuma manchete encontrada.")


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