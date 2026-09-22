import os
import sys

# Garante saída UTF-8 no Windows para evitar UnicodeEncodeError
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


def process_pdf(pdf_path, chunk_size=1000, chunk_overlap=100):
    """
    Carrega o PDF e divide em chunks menores.
    """
    print(f"Processando documento: {pdf_path}")
    loader = PyMuPDFLoader(pdf_path)
    documents = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    
    chunks = text_splitter.split_documents(documents)
    print(f"Documento dividido em {len(chunks)} chunks.")
    return chunks

def ingest_to_chroma(chunks, persist_directory):
    """
    Gera os embeddings e ingere no ChromaDB.
    """
    print(f"Inicializando embeddings (HuggingFace: {EMBEDDING_MODEL})...")
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        encode_kwargs={"normalize_embeddings": True},
    )
    
    print(f"Ingerindo dados no ChromaDB em {persist_directory}...")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_directory
    )
    
    print("Ingestão concluída com sucesso.")
    return vectorstore

def main():
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    RAW_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
    CHROMA_DB_DIR = os.path.join(PROJECT_ROOT, "knowledge_base", "chromadb")
    
    # Exemplo: Se houvesse um pdf na pasta raw.
    # Como não temos ainda, vamos criar um mock para teste.
    test_pdf_path = os.path.join(RAW_DATA_DIR, "diretriz_mock.pdf")
    
    if not os.path.exists(test_pdf_path):
        print("PDF não encontrado para teste de ingestão. Você deve adicionar os PDFs na pasta data/raw/")
        print("Você pode testar a extração executando o script novamente depois de adicionar um arquivo .pdf")
        return
        
    chunks = process_pdf(test_pdf_path)
    if chunks:
        ingest_to_chroma(chunks, CHROMA_DB_DIR)

if __name__ == "__main__":
    main()
