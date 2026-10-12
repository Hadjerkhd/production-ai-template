import asyncio
import logging

from fastapi.testclient import TestClient

from app.main import app
from app.rate_limit import FixedWindowRateLimiter
from app.routes import llm

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
    assert response.headers["x-request-id"]


def test_prompt_over_limit_is_rejected(monkeypatch):
    async def fail_if_called(_query: str) -> str:
        raise AssertionError("oversized prompt reached the LLM service")

    monkeypatch.setattr(llm.llm_service, "generate_response", fail_if_called)

    response = client.post("/api/v1/generate", json={"query": "x" * 12001})

    assert response.status_code == 422


def test_generate_rate_limit_returns_retry_after(monkeypatch):
    async def fake_generate_response(query: str) -> str:
        return f"Answer: {query}"

    monkeypatch.setattr(llm.llm_service, "generate_response", fake_generate_response)
    monkeypatch.setattr(llm, "rate_limiter", FixedWindowRateLimiter(limit=1))

    first_response = client.post("/api/v1/generate", json={"query": "Hello"})
    second_response = client.post("/api/v1/generate", json={"query": "Again"})

    assert first_response.status_code == 200
    assert second_response.status_code == 429
    assert int(second_response.headers["retry-after"]) > 0


def test_generation_timeout_returns_gateway_timeout(monkeypatch):
    async def timeout(_query: str) -> str:
        raise asyncio.TimeoutError

    monkeypatch.setattr(llm.llm_service, "generate_response", timeout)
    monkeypatch.setattr(llm, "rate_limiter", FixedWindowRateLimiter(limit=10))

    response = client.post("/api/v1/generate", json={"query": "Hello"})

    assert response.status_code == 504


def test_health_and_readiness_endpoints():
    assert client.get("/api/v1/health").json() == {"status": "alive"}
    assert client.get("/api/v1/ready").json() == {"status": "ready"}


def test_request_completion_log_has_severity_and_request_id(caplog):
    caplog.set_level(logging.INFO)

    response = client.get("/")

    request_log = next(
        record
        for record in caplog.records
        if record.getMessage() == "HTTP request completed"
    )
    assert request_log.levelno == logging.INFO
    assert request_log.request_id == response.headers["x-request-id"]
    assert request_log.status_code == 200
