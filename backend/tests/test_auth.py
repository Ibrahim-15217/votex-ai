"""Authentication and role-based access control."""

from fastapi.testclient import TestClient

DEMO_PASSWORD = "VotexDemo!23"


def login(client: TestClient, email: str, password: str = DEMO_PASSWORD):
    return client.post("/api/v1/auth/login", json={"email": email, "password": password})


def test_login_returns_token_and_profile(client: TestClient) -> None:
    response = login(client, "analyst@votex.demo")

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["expires_in"] > 0
    assert body["user"]["email"] == "analyst@votex.demo"
    assert body["user"]["role"] == "analyst"
    assert body["user"]["organisation"]["slug"] == "votex-demo-authority"


def test_wrong_password_and_unknown_email_look_identical(client: TestClient) -> None:
    wrong = login(client, "analyst@votex.demo", password="not-the-password")
    unknown = login(client, "nobody@votex.demo")

    assert wrong.status_code == 401
    assert unknown.status_code == 401
    assert wrong.json()["detail"] == unknown.json()["detail"]


def test_me_requires_a_valid_bearer_token(client: TestClient, tokens: dict[str, str]) -> None:
    assert client.get("/api/v1/auth/me").status_code == 401

    response = client.get("/api/v1/auth/me", headers=tokens["reporter@votex.demo"])
    assert response.status_code == 200
    assert response.json()["role"] == "reporter"


def test_tampered_token_is_rejected(client: TestClient, tokens: dict[str, str]) -> None:
    header = tokens["admin@votex.demo"]["Authorization"]
    token = header.split(" ", 1)[1]
    tampered = f"{token[:-4]}abcd"

    response = client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {tampered}"}
    )
    assert response.status_code == 401


def test_user_directory_is_role_limited_and_tenant_scoped(
    client: TestClient, tokens: dict[str, str]
) -> None:
    reporter = client.get("/api/v1/users", headers=tokens["reporter@votex.demo"])
    assert reporter.status_code == 403

    org_one = client.get("/api/v1/users", headers=tokens["analyst@votex.demo"])
    org_two = client.get("/api/v1/users", headers=tokens["analyst@inec.demo"])
    assert org_one.status_code == 200
    assert org_two.status_code == 200
    assert {user["email"] for user in org_one.json()} == {
        "admin@votex.demo",
        "analyst@votex.demo",
        "reporter@votex.demo",
    }
    assert {user["email"] for user in org_two.json()} == {
        "analyst@inec.demo",
        "reporter@inec.demo",
    }
