"""
batch_ingest.py — Ingestão em larga escala de documentos no ChromaDB.

Lê TODOS os formatos suportados (.pdf e .txt) da pasta de guidelines,
faz chunking, gera embeddings com modelo MULTILÍNGUE e insere em lotes com deduplicação.
"""
import os
import hashlib
from tqdm import tqdm
from langchain_community.document_loaders import PyMuPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# Modelo multilíngue — essencial para busca semântica em textos em português
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


def generate_chunk_id(chunk_text: str, source_name: str) -> str:
    """Hash MD5 do conteúdo + fonte para deduplicação precisa."""
    payload = f"{source_name}::{chunk_text}".encode("utf-8")
    return hashlib.md5(payload).hexdigest()


def load_document(file_path: str):
    """Escolhe o loader correto com base na extensão."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return PyMuPDFLoader(file_path).load()
    elif ext == ".txt":
        try:
            return TextLoader(file_path, encoding="utf-8").load()
        except Exception:
            return TextLoader(file_path, autodetect_encoding=True).load()
    else:
        print(f"  ⚠ Formato não suportado: {ext} — ignorando {file_path}")
        return []


def process_documents(raw_dir: str, chunk_size=800, chunk_overlap=120):
    """Lê todos os PDFs e TXTs do diretório e retorna chunks enriquecidos."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    supported = (".pdf", ".txt")
    files = [
        f for f in os.listdir(raw_dir)
        if os.path.splitext(f)[1].lower() in supported
    ]
    print(f"Encontrados {len(files)} documentos oficiais em {raw_dir}")

    all_chunks = []
    for fname in tqdm(files, desc="Processando documentos"):
        fpath = os.path.join(raw_dir, fname)
        try:
            docs = load_document(fpath)
            chunks = splitter.split_documents(docs)
            for c in chunks:
                c.metadata["source_file"] = fname
                c.metadata["chunk_id"] = generate_chunk_id(c.page_content, fname)
            all_chunks.extend(chunks)
        except Exception as e:
            print(f"  ✗ Erro ao processar {fname}: {e}")

    return all_chunks


def batch_ingest_chroma(chunks, persist_dir: str, batch_size=200):
    """Insere chunks no ChromaDB em lotes, sem duplicar."""
    if not chunks:
        print("Nenhum chunk para ingerir.")
        return None

    print(f"Carregando modelo de embeddings: {EMBEDDING_MODEL}")
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        encode_kwargs={"normalize_embeddings": True},
    )

    os.makedirs(persist_dir, exist_ok=True)
    vectorstore = Chroma(
        persist_directory=persist_dir,
        embedding_function=embeddings,
        collection_metadata={"hnsw:space": "cosine"},
    )

    # Deduplica por chunk_id
    unique = {c.metadata["chunk_id"]: c for c in chunks}
    docs = list(unique.values())
    ids = list(unique.keys())
    print(f"Total de chunks únicos a ingerir: {len(docs)}")

    for i in tqdm(range(0, len(docs), batch_size), desc="Ingerindo lotes"):
        batch_docs = docs[i : i + batch_size]
        batch_ids = ids[i : i + batch_size]
        try:
            vectorstore.add_documents(documents=batch_docs, ids=batch_ids)
        except Exception as e:
            print(f"  ✗ Erro no lote {i}–{i+batch_size}: {e}")

    print("✔ Ingestão no ChromaDB concluída com sucesso.")
    return vectorstore


def main():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_dir = os.path.join(project_root, "data", "raw", "guidelines")
    chroma_dir = os.path.join(project_root, "knowledge_base", "chromadb")

    if not os.path.exists(raw_dir):
        os.makedirs(raw_dir, exist_ok=True)
        print(f"Diretório criado: {raw_dir}")
        print("Adicione PDFs ou TXTs lá, ou rode o scraper.py primeiro.")
        return

    chunks = process_documents(raw_dir)
    batch_ingest_chroma(chunks, chroma_dir)


if __name__ == "__main__":
    main()
