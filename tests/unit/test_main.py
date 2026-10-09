from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the LLM Service API"}


def test_generate_without_auth(monkeypatch):
    async def fake_generate_response(query: str) -> str:
        return f"Answer: {query}"

    monkeypatch.setattr(
        "app.routes.llm.llm_service.generate_response", fake_generate_response
    )

    response = client.post("/api/v1/generate", json={"query": "Hello"})

    assert response.status_code == 200
    assert response.json() == {"answer": "Answer: Hello"}
