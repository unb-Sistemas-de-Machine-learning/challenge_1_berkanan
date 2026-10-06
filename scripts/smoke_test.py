"""End-to-end smoke test for a running Berkanan backend."""

import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
CLAIM = "Canela cura diabetes?"


def request_json(path: str, payload: dict | None = None) -> dict | list:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = Request(
        f"{BASE_URL}{path}",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST" if payload is not None else "GET",
    )
    try:
        with urlopen(request, timeout=180) as response:
            if response.status != 200:
                raise AssertionError(f"{path} returned HTTP {response.status}")
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise AssertionError(f"{path} returned HTTP {error.code}: {body}") from error
    except URLError as error:
        raise AssertionError(f"Could not reach API at {BASE_URL}: {error}") from error


def main() -> int:
    request_json("/health")
    request_json("/api/health")
    analysis = request_json("/api/analyze", {"text": CLAIM})
    required = (
        "id",
        "classification",
        "confidence_score",
        "matched_sources",
        "model_version",
        "rag_sources_count",
        "response_time_ms",
    )
    missing = [field for field in required if field not in analysis]
    if missing:
        raise AssertionError(f"Analysis response is missing fields: {missing}")
    if not analysis["id"]:
        raise AssertionError("Analysis response has no id")
    if not analysis["matched_sources"]:
        raise AssertionError(
            "No RAG sources were returned; populate the ChromaDB knowledge base first."
        )
    if analysis["rag_sources_count"] != len(analysis["matched_sources"]):
        raise AssertionError("rag_sources_count does not match matched_sources length")
    if not isinstance(analysis["response_time_ms"], int) or analysis["response_time_ms"] <= 0:
        raise AssertionError("response_time_ms must be a positive integer")

    history = request_json("/api/history")
    if not any(str(entry["id"]) == str(analysis["id"]) for entry in history):
        raise AssertionError("The new analysis was not found in /api/history")

    print(
        "Backend smoke test passed: health, analysis, RAG evidence, metrics, "
        "persistence and history are operational."
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, KeyError, TypeError, ValueError) as error:
        print(f"Backend smoke test failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error
