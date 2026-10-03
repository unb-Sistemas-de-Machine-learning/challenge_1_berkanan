from scripts.fact_checker import DiabetesFactChecker


CHROMA_DIR = "knowledge_base/chromadb"

# Inicialização global para não carregar o modelo a cada requisição
_checker = None

def get_checker():
    global _checker
    if _checker is None:
        _checker = DiabetesFactChecker(CHROMA_DIR)
        _checker._load_classifier()
        _checker._load_vectorstore()
    return _checker


def analyze_claim(text: str) -> dict:
    checker = get_checker()

    result = checker.check(
        text,
        save_to_db=False
    )
    
    # Garantir que o nome bate com o esperado no bd/routes
    if "confidence_score" not in result:
        result["confidence_score"] = result.get("p_fake", 0.0)

    return result