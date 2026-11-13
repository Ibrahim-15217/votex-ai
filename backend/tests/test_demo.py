"""Public demo telemetry used by the sign-in screen.

The endpoint must stay unauthenticated, return only the synthetic demo tenant's
counts, and never widen to another organisation.
"""

from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.db.models import AuditLog, Incident, Indicator, Organisation
from app.db.session import SessionLocal


def _demo_org_id() -> int:
    with SessionLocal() as db:
        organisation_id = db.scalar(
            select(Organisation.id).where(Organisation.slug == "votex-demo-authority")
        )
    assert organisation_id is not None
    return organisation_id


def test_demo_telemetry_is_public(client: TestClient) -> None:
    response = client.get("/api/v1/demo/telemetry")

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"synthetic", "incidents", "indicators", "audit_entries"}
    assert body["synthetic"] is True
    assert body["incidents"] > 0
    assert body["indicators"] > 0
    assert body["audit_entries"] > 0


def test_demo_telemetry_matches_demo_tenant(client: TestClient) -> None:
    organisation_id = _demo_org_id()
    with SessionLocal() as db:
        expected = {
            "incidents": db.scalar(
                select(func.count())
                .select_from(Incident)
                .where(Incident.organisation_id == organisation_id)
            ),
            "indicators": db.scalar(
                select(func.count())
                .select_from(Indicator)
                .where(Indicator.organisation_id == organisation_id)
            ),
            "audit_entries": db.scalar(
                select(func.count())
                .select_from(AuditLog)
                .where(AuditLog.organisation_id == organisation_id)
            ),
        }

    response = client.get("/api/v1/demo/telemetry")
    body = response.json()

    for key, value in expected.items():
        assert body[key] == value


def test_demo_telemetry_does_not_include_other_tenants(client: TestClient) -> None:
    organisation_id = _demo_org_id()
    with SessionLocal() as db:
        total_incidents = db.scalar(select(func.count()).select_from(Incident))
        demo_incidents = db.scalar(
            select(func.count())
            .select_from(Incident)
            .where(Incident.organisation_id == organisation_id)
        )

    assert total_incidents is not None and demo_incidents is not None
    assert total_incidents > demo_incidents

    response = client.get("/api/v1/demo/telemetry")
    assert response.json()["incidents"] == demo_incidents
