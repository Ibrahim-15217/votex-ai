"""Phase 0 health checks.

These tests prove the application imports, routes are mounted and the response
shape is stable enough for orchestration and the demo pre-flight.
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_ok() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "votex-ai-api"
    assert body["checks"]["api"] == "ok"
    assert body["checks"]["ai_engine"] in {"ok", "model-unavailable", "model-invalid"}
    assert "timestamp" in body


def test_ready_probe() -> None:
    response = client.get("/api/v1/ready")

    assert response.status_code == 200
    assert response.json() == {"ready": True, "phase": "hybrid-ai-engine"}


def test_root_identity_hides_secrets() -> None:
    response = client.get("/")

    assert response.status_code == 200
    body = response.json()
    assert body["service"] == "votex-ai-api"
    assert "secret_key" not in body
    assert "database_url" not in body


def test_unknown_route_is_404() -> None:
    response = client.get("/api/v1/does-not-exist")

    assert response.status_code == 404
