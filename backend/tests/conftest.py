"""Shared pytest fixtures.

A throwaway SQLite database and evidence directory are created before the app
is imported, so tests never touch the developer's demo data.
"""

import os
import tempfile
from pathlib import Path

_TEST_ROOT = Path(tempfile.mkdtemp(prefix="votex-ai-tests-"))
os.environ["DATABASE_URL"] = f"sqlite:///{(_TEST_ROOT / 'test.db').as_posix()}"
os.environ["EVIDENCE_DIR"] = str(_TEST_ROOT / "evidence")
os.environ["SECRET_KEY"] = "test-only-secret-key-not-used-anywhere-else"
os.environ["AUTO_SEED"] = "false"
os.environ["ENVIRONMENT"] = "test"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.db.init_db import init_db  # noqa: E402
from app.main import app  # noqa: E402
from app.seed import seed_demo_data, seed_resilience_demo  # noqa: E402

DEMO_PASSWORD = "VotexDemo!23"


@pytest.fixture(scope="session")
def seeded() -> None:
    """Create the schema and deterministic demo data once per session."""

    init_db()
    assert seed_demo_data() is True
    seed_resilience_demo()


@pytest.fixture(scope="session")
def client(seeded: None) -> TestClient:
    """Return a test client with application lifespan handled."""

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="session")
def tokens(client: TestClient) -> dict[str, str]:
    """Sign in every demo account and return bearer headers by email."""

    headers: dict[str, str] = {}
    for email in (
        "admin@votex.demo",
        "analyst@votex.demo",
        "reporter@votex.demo",
        "analyst@inec.demo",
        "reporter@inec.demo",
    ):
        response = client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": DEMO_PASSWORD},
        )
        assert response.status_code == 200, response.text
        headers[email] = {"Authorization": f"Bearer {response.json()['access_token']}"}
    return headers
