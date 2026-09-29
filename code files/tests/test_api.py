import os
os.environ["MOCK_MODE"] = "true"
from fastapi.testclient import TestClient
from backend.main import app
client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_generate_mock_document():
    response = client.post("/generate", json={
        "document_type": "Non-Disclosure Agreement",
        "parties": "Alice (Disclosing Party); Beta Ltd (Receiving Party)",
        "terms": "Keep information confidential; return materials on request",
        "effective_date": "2026-09-22",
    })
    assert response.status_code == 200
    data = response.json()
    assert "document_text" in data
    assert "CONFIDENTIAL" in data["document_text"].upper()
    assert "Alice" in data["document_text"]

def test_generate_rejects_empty_terms():
    response = client.post("/generate", json={
        "document_type": "Agreement", "parties": "A and B", "terms": "", "effective_date": "2026-09-22"
    })
    assert response.status_code == 422
