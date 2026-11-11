"""Evidence validation, hashing, tenant isolation and audited download."""

from hashlib import sha256

from fastapi.testclient import TestClient

from app.core.config import settings


def _own_incident(client: TestClient, tokens: dict[str, str]) -> dict:
    response = client.get(
        "/api/v1/incidents",
        headers=tokens["reporter@votex.demo"],
        params={"search": "VX-2026-A10001"},
    )
    assert response.status_code == 200
    return response.json()["items"][0]


def _upload(client: TestClient, headers: dict[str, str], incident_id: str, **overrides):
    files = overrides.pop(
        "files", {"file": ("staff-note.txt", b"synthetic evidence for tests\n", "text/plain")}
    )
    return client.post(
        f"/api/v1/incidents/{incident_id}/evidence", headers=headers, files=files, **overrides
    )


def test_upload_hashes_and_download_is_audited(
    client: TestClient, tokens: dict[str, str]
) -> None:
    incident = _own_incident(client, tokens)
    content = b"synthetic evidence for tests\n"

    upload = _upload(client, tokens["reporter@votex.demo"], incident["id"])
    assert upload.status_code == 201, upload.text
    evidence = upload.json()
    assert evidence["sha256"] == sha256(content).hexdigest()
    assert evidence["size_bytes"] == len(content)
    assert evidence["original_filename"] == "staff-note.txt"

    download = client.get(
        f"/api/v1/incidents/{incident['id']}/evidence/{evidence['id']}/download",
        headers=tokens["analyst@votex.demo"],
    )
    assert download.status_code == 200
    assert download.content == content
    assert download.headers["X-Content-SHA256"] == evidence["sha256"]

    audit = client.get(
        "/api/v1/audit",
        headers=tokens["analyst@votex.demo"],
        params={"action": "evidence.downloaded", "page_size": 100},
    )
    assert audit.status_code == 200
    assert any(
        entry["resource_id"] == evidence["id"] for entry in audit.json()["items"]
    )

    detail = client.get(
        f"/api/v1/incidents/{incident['id']}", headers=tokens["analyst@votex.demo"]
    ).json()
    assert any(event["event_type"] == "evidence_accessed" for event in detail["events"])


def test_cross_tenant_evidence_access_is_denied(
    client: TestClient, tokens: dict[str, str]
) -> None:
    incident = _own_incident(client, tokens)
    uploaded = _upload(client, tokens["reporter@votex.demo"], incident["id"])
    evidence_id = uploaded.json()["id"]

    response = client.get(
        f"/api/v1/incidents/{incident['id']}/evidence/{evidence_id}/download",
        headers=tokens["analyst@inec.demo"],
    )
    assert response.status_code == 404


def test_reporter_cannot_touch_another_reporters_evidence(
    client: TestClient, tokens: dict[str, str]
) -> None:
    # Seeded incident A10002 belongs to the administrator.
    analyst_view = client.get(
        "/api/v1/incidents",
        headers=tokens["analyst@votex.demo"],
        params={"search": "VX-2026-A10002"},
    ).json()["items"][0]

    response = _upload(client, tokens["reporter@votex.demo"], analyst_view["id"])
    assert response.status_code == 404


def test_unsupported_type_and_magic_mismatch_are_rejected(
    client: TestClient, tokens: dict[str, str]
) -> None:
    incident = _own_incident(client, tokens)

    unsupported = _upload(
        client,
        tokens["reporter@votex.demo"],
        incident["id"],
        files={"file": ("payload.exe", b"MZ fake executable", "application/octet-stream")},
    )
    assert unsupported.status_code == 415

    mismatch = _upload(
        client,
        tokens["reporter@votex.demo"],
        incident["id"],
        files={"file": ("screenshot.png", b"this is not a png", "image/png")},
    )
    assert mismatch.status_code == 415

    empty = _upload(
        client,
        tokens["reporter@votex.demo"],
        incident["id"],
        files={"file": ("empty.txt", b"", "text/plain")},
    )
    assert empty.status_code == 400


def test_size_limit_is_enforced(
    client: TestClient, tokens: dict[str, str], monkeypatch
) -> None:
    incident = _own_incident(client, tokens)
    monkeypatch.setattr(settings, "max_evidence_mb", 0)

    response = _upload(client, tokens["reporter@votex.demo"], incident["id"])
    assert response.status_code == 413
