from scripts.fact_checker import DiabetesFactChecker


CHROMA_DIR = "knowledge_base/chromadb"


def analyze_claim(text: str) -> dict:
    checker = DiabetesFactChecker(CHROMA_DIR)

    result = checker.check(
        text,
        save_to_db=False
    )

    return result