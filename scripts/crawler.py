import os
import requests
from bs4 import BeautifulSoup
import urllib.parse
import json
import time

def load_downloaded_log(log_path):
    if os.path.exists(log_path):
        with open(log_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_downloaded_log(log_path, log_data):
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(log_data, f, indent=4, ensure_ascii=False)

def download_pdf(url, output_dir):
    try:
        response = requests.get(url, stream=True, timeout=15)
        response.raise_for_status()
        
        filename = os.path.basename(urllib.parse.urlparse(url).path)
        if not filename.endswith('.pdf'):
            filename = f"document_{int(time.time())}.pdf"
            
        file_path = os.path.join(output_dir, filename)
        
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                
        return file_path
    except Exception as e:
        print(f"Erro ao baixar {url}: {e}")
        return None

def scrape_pdfs(seed_urls, output_dir, log_path):
    os.makedirs(output_dir, exist_ok=True)
    downloaded_urls = set(load_downloaded_log(log_path))
    new_downloads = []

    for seed_url in seed_urls:
        print(f"Buscando links de PDF em: {seed_url}")
        try:
            response = requests.get(seed_url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Encontra todos os links que terminam com .pdf
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.lower().endswith('.pdf'):
                    # Resolve URL relativa para absoluta
                    full_url = urllib.parse.urljoin(seed_url, href)
                    
                    if full_url not in downloaded_urls:
                        print(f"Encontrado novo PDF: {full_url}")
                        file_path = download_pdf(full_url, output_dir)
                        if file_path:
                            downloaded_urls.add(full_url)
                            new_downloads.append(full_url)
                            print(f"Salvo em: {file_path}")
                        time.sleep(1) # Rate limiting respeitoso
                    else:
                        print(f"PDF já baixado anteriormente: {full_url}")
        
        except Exception as e:
            print(f"Erro ao acessar {seed_url}: {e}")

    # Atualiza o log
    save_downloaded_log(log_path, list(downloaded_urls))
    print(f"Processo finalizado. {len(new_downloads)} novos PDFs baixados.")

if __name__ == "__main__":
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    OUTPUT_DIR = os.path.join(PROJECT_ROOT, "data", "raw", "guidelines")
    LOG_PATH = os.path.join(OUTPUT_DIR, "downloaded.json")
    
    # Exemplo de seed URLs
    SEED_URLS = [
        # Exemplo genérico, você pode substituir pelas páginas de diretrizes da SBD
        # "https://diretriz.diabetes.org.br/baixar-diretriz-em-pdf/"
    ]
    
    if not SEED_URLS:
        print("Edite o arquivo crawler.py e adicione URLs na lista SEED_URLS.")
    else:
        scrape_pdfs(SEED_URLS, OUTPUT_DIR, LOG_PATH)
