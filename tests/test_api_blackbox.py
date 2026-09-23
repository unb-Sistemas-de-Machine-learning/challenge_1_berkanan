import json
import pytest
from fastapi.testclient import TestClient

from api import app

@pytest.fixture(scope="module")
def client():
    """Provides a TestClient with startup/shutdown events executed."""
    with TestClient(app) as c:
        yield c

def test_health_endpoint(client):
    """A chamada GET /health deve retornar 200 e os campos esperados."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    # Verifica presença dos campos básicos
    assert data["status"] == "ok"
    assert "model" in data
    assert "threshold" in data
    # O threshold deve estar no intervalo (0,1)
    assert 0.0 < data["threshold"] < 1.0

@pytest.mark.parametrize(
    "text,expected_label",
    [
        ("Canela cura diabetes tipo 2", "FAKE"),
        ("A contagem de carboidratos é recomendada pela SBD", "REAL"),
    ],
)
def test_predict_known_cases(client, text, expected_label):
    """Caso conhecido deve ser classificado corretamente."""
    payload = {"text": text}
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    result = response.json()
    assert "label" in result and "p_fake" in result and "threshold" in result
    assert result["label"] == expected_label
    # p_fake deve ser coerente com o label e o threshold retornado
    if result["label"] == "FAKE":
        assert result["p_fake"] >= result["threshold"]
    else:
        assert result["p_fake"] < result["threshold"]

def test_predict_missing_text(client):
    """Requisição sem campo 'text' deve retornar erro 422 (validacao FastAPI)."""
    response = client.post("/predict", json={})
    assert response.status_code == 422

def test_predict_empty_string(client):
    """Texto vazio deve ser rejeitado com erro 422 (campo vazio)."""
    payload = {"text": ""}
    response = client.post("/predict", json=payload)
    assert response.status_code == 422
    result = response.json()
    # Verifica que o erro contém a chave 'detail'
    assert "detail" in result
