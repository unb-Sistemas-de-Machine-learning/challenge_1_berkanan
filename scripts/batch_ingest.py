"""
batch_ingest.py â€” IngestÃ£o em larga escala de documentos no ChromaDB.

LÃª TODOS os formatos suportados (.pdf e .txt) da pasta de guidelines,
faz chunking, gera embeddings com modelo MULTILÃNGUE e insere em lotes.
"""
import os
import hashlib
from tqdm import tqdm
from langchain_community.document_loaders import PyMuPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# Modelo multilÃ­ngue â€” essencial para textos em portuguÃªs
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


def generate_chunk_id(chunk_text: str, source_name: str) -> str:
    """Hash MD5 do conteÃºdo + fonte para deduplicaÃ§Ã£o."""
    payload = f"{source_name}::{chunk_text}".encode("utf-8")
    return hashlib.md5(payload).hexdigest()


def load_document(file_path: str):
    """Escolhe o loader correto com base na extensÃ£o."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return PyMuPDFLoader(file_path).load()
    elif ext == ".txt":
        return TextLoader(file_path, encoding="utf-8").load()
    else:
        print(f"  âš  Formato nÃ£o suportado: {ext} â€” ignorando {file_path}")
        return []


def process_documents(raw_dir: str, chunk_size=800, chunk_overlap=120):
    """LÃª todos os PDFs e TXTs do diretÃ³rio e retorna chunks enriquecidos."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    supported = (".pdf", ".txt")
    files = [f for f in os.listdir(raw_dir)
             if os.path.splitext(f)[1].lower() in supported]
    print(f"Encontrados {len(files)} documentos em {raw_dir}")

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
            print(f"  âœ— Erro em {fname}: {e}")

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

    vectorstore = Chroma(
        persist_directory=persist_dir,
        embedding_function=embeddings,
        collection_metadata={"hnsw:space": "cosine"},
    )

    # Deduplica por chunk_id
    unique = {c.metadata["chunk_id"]: c for c in chunks}
    docs = list(unique.values())
    ids = list(unique.keys())
    print(f"Chunks Ãºnicos a inserir: {len(docs)}")

    for i in tqdm(range(0, len(docs), batch_size), desc="Ingerindo lotes"):
        batch_docs = docs[i : i + batch_size]
        batch_ids = ids[i : i + batch_size]
        try:
            vectorstore.add_documents(documents=batch_docs, ids=batch_ids)
        except Exception as e:
            print(f"  âœ— Erro no lote {i}â€“{i+batch_size}: {e}")

    print("âœ” IngestÃ£o concluÃ­da.")
    return vectorstore


def main():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_dir = os.path.join(project_root, "data", "raw", "guidelines")
    chroma_dir = os.path.join(project_root, "knowledge_base", "chromadb")

    if not os.path.exists(raw_dir):
        os.makedirs(raw_dir, exist_ok=True)
        print(f"DiretÃ³rio criado: {raw_dir}")
        print("Adicione PDFs ou TXTs lÃ¡, ou rode o scraper.py primeiro.")
        return

    chunks = process_documents(raw_dir)
    batch_ingest_chroma(chunks, chroma_dir)


if __name__ == "__main__":
    main()

