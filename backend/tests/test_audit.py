"""Audit chain browsing, verification and tamper detection."""

from fastapi.testclient import TestClient
from sqlalchemy import select, update

from app.db.models import AuditLog
from app.db.session import SessionLocal


def test_audit_chain_verifies(client: TestClient, tokens: dict[str, str]) -> None:
    response = client.get("/api/v1/audit/verify", headers=tokens["admin@votex.demo"])

    assert response.status_code == 200
    body = response.json()
    assert body["valid"] is True
    assert body["entries_checked"] > 0
    assert body["first_invalid_id"] is None
    assert body["latest_hash"] is not None
    assert len(body["latest_hash"]) == 64


def test_audit_list_is_newest_first_and_scoped(
    client: TestClient, tokens: dict[str, str]
) -> None:
    response = client.get(
        "/api/v1/audit", headers=tokens["analyst@votex.demo"], params={"page_size": 100}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] > 0
    ids = [entry["id"] for entry in body["items"]]
    assert ids == sorted(ids, reverse=True)
    assert all(entry["organisation_id"] is not None for entry in body["items"])

    filtered = client.get(
        "/api/v1/audit",
        headers=tokens["analyst@votex.demo"],
        params={"action": "incident.created", "page_size": 100},
    ).json()
    assert filtered["total"] > 0
    assert all(entry["action"] == "incident.created" for entry in filtered["items"])


def test_reporter_cannot_read_audit(client: TestClient, tokens: dict[str, str]) -> None:
    assert client.get("/api/v1/audit", headers=tokens["reporter@votex.demo"]).status_code == 403
    assert (
        client.get("/api/v1/audit/verify", headers=tokens["reporter@votex.demo"]).status_code
        == 403
    )


def test_tampering_breaks_the_chain_and_restore_succeeds(
    client: TestClient, tokens: dict[str, str]
) -> None:
    with SessionLocal() as db:
        entry = db.scalar(select(AuditLog).order_by(AuditLog.id).limit(1))
        assert entry is not None
        original = entry.detail_json
        entry_id = entry.id

    try:
        with SessionLocal() as db:
            db.execute(
                update(AuditLog)
                .where(AuditLog.id == entry_id)
                .values(detail_json='{"tampered":true}')
            )
            db.commit()

        broken = client.get("/api/v1/audit/verify", headers=tokens["analyst@votex.demo"])
        assert broken.status_code == 200
        body = broken.json()
        assert body["valid"] is False
        assert body["first_invalid_id"] == entry_id
        assert "failed hash verification" in body["message"]
    finally:
        with SessionLocal() as db:
            db.execute(
                update(AuditLog)
                .where(AuditLog.id == entry_id)
                .values(detail_json=original)
            )
            db.commit()

    restored = client.get("/api/v1/audit/verify", headers=tokens["analyst@votex.demo"])
    assert restored.json()["valid"] is True
