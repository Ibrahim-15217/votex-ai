"""Incident lifecycle, RBAC, tenant isolation and overview statistics."""

import re

from fastapi.testclient import TestClient

REFERENCE_PATTERN = re.compile(r"^VX-\d{4}-[0-9A-F]{6}$")


def create_incident(client: TestClient, token_headers: dict[str, str], title: str):
    return client.post(
        "/api/v1/incidents",
        headers=token_headers,
        json={
            "title": title,
            "description": (
                "Synthetic test report describing a suspicious message received by staff. "
                "No real voter data is included."
            ),
            "category": "phishing",
            "channel": "email",
            "reported_url": "https://example.org/suspicious",
            "state": "Lagos",
            "priority": "high",
        },
    )


def test_reporter_creates_incident_with_reference_and_timeline(
    client: TestClient, tokens: dict[str, str]
) -> None:
    response = create_incident(
        client, tokens["reporter@votex.demo"], "Suspicious staff verification email"
    )

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["status"] == "submitted"
    assert body["priority"] == "medium"  # reporters cannot self-elevate priority
    assert REFERENCE_PATTERN.match(body["reference"])
    assert body["reporter"]["email"] == "reporter@votex.demo"
    assert body["events"][0]["event_type"] == "created"
    assert body["ai_status"] in {"complete", "degraded"}
    assert body["analysis"] is not None
    assert body["analysis"]["risk_score"] == body["risk_score"]

    listed = client.get(
        "/api/v1/incidents",
        headers=tokens["reporter@votex.demo"],
        params={"search": body["reference"]},
    )
    assert listed.status_code == 200
    assert listed.json()["total"] == 1


def test_cross_tenant_incident_is_invisible(
    client: TestClient, tokens: dict[str, str]
) -> None:
    created = create_incident(
        client, tokens["reporter@votex.demo"], "Tenant isolation probe"
    ).json()

    foreign_detail = client.get(
        f"/api/v1/incidents/{created['id']}", headers=tokens["analyst@inec.demo"]
    )
    assert foreign_detail.status_code == 404

    foreign_list = client.get(
        "/api/v1/incidents",
        headers=tokens["analyst@inec.demo"],
        params={"search": created["reference"]},
    )
    assert foreign_list.status_code == 200
    assert foreign_list.json()["total"] == 0


def test_reporter_cannot_read_another_reporters_incident(
    client: TestClient, tokens: dict[str, str]
) -> None:
    # Seeded incident VX-2026-A10002 was submitted by the administrator.
    analyst_view = client.get(
        "/api/v1/incidents",
        headers=tokens["analyst@votex.demo"],
        params={"search": "VX-2026-A10002"},
    )
    incident_id = analyst_view.json()["items"][0]["id"]

    response = client.get(
        f"/api/v1/incidents/{incident_id}", headers=tokens["reporter@votex.demo"]
    )
    assert response.status_code == 404

    reporter_list = client.get(
        "/api/v1/incidents",
        headers=tokens["reporter@votex.demo"],
        params={"search": "VX-2026-A10002"},
    )
    assert reporter_list.json()["total"] == 0


def test_lifecycle_transitions_are_validated(
    client: TestClient, tokens: dict[str, str]
) -> None:
    created = create_incident(
        client, tokens["reporter@votex.demo"], "Lifecycle transition probe"
    ).json()
    incident_id = created["id"]

    forbidden = client.patch(
        f"/api/v1/incidents/{incident_id}/status",
        headers=tokens["reporter@votex.demo"],
        json={"status": "under_review"},
    )
    assert forbidden.status_code == 403

    invalid = client.patch(
        f"/api/v1/incidents/{incident_id}/status",
        headers=tokens["analyst@votex.demo"],
        json={"status": "contained"},
    )
    assert invalid.status_code == 409

    reviewed = client.patch(
        f"/api/v1/incidents/{incident_id}/status",
        headers=tokens["analyst@votex.demo"],
        json={"status": "under_review", "note": "Triage started."},
    )
    assert reviewed.status_code == 200
    assert reviewed.json()["status"] == "under_review"

    users = client.get("/api/v1/users", headers=tokens["analyst@votex.demo"]).json()
    analyst_id = next(u["id"] for u in users if u["email"] == "analyst@votex.demo")

    assigned = client.patch(
        f"/api/v1/incidents/{incident_id}/assignment",
        headers=tokens["analyst@votex.demo"],
        json={"assignee_id": analyst_id},
    )
    assert assigned.status_code == 200
    assert assigned.json()["status"] == "assigned"
    assert assigned.json()["assignee"]["email"] == "analyst@votex.demo"

    investigating = client.patch(
        f"/api/v1/incidents/{incident_id}/status",
        headers=tokens["analyst@votex.demo"],
        json={"status": "investigating"},
    )
    assert investigating.status_code == 200
    event_types = [event["event_type"] for event in investigating.json()["events"]]
    assert "status_changed" in event_types
    assert "assigned" in event_types


def test_assignment_rejects_cross_tenant_assignee(
    client: TestClient, tokens: dict[str, str]
) -> None:
    created = create_incident(
        client, tokens["reporter@votex.demo"], "Cross tenant assignment probe"
    ).json()
    foreign_users = client.get("/api/v1/users", headers=tokens["analyst@inec.demo"]).json()
    foreign_analyst = next(u for u in foreign_users if u["role"] == "analyst")

    response = client.patch(
        f"/api/v1/incidents/{created['id']}/assignment",
        headers=tokens["analyst@votex.demo"],
        json={"assignee_id": foreign_analyst["id"]},
    )
    assert response.status_code == 422


def test_priority_note_and_response_action(
    client: TestClient, tokens: dict[str, str]
) -> None:
    created = create_incident(
        client, tokens["reporter@votex.demo"], "Priority and response probe"
    ).json()
    incident_id = created["id"]

    priority = client.patch(
        f"/api/v1/incidents/{incident_id}/priority",
        headers=tokens["analyst@votex.demo"],
        json={"priority": "critical"},
    )
    assert priority.status_code == 200
    assert priority.json()["priority"] == "critical"

    comment = client.post(
        f"/api/v1/incidents/{incident_id}/comments",
        headers=tokens["reporter@votex.demo"],
        json={"message": "The message was also forwarded to two ward assistants."},
    )
    assert comment.status_code == 201
    assert comment.json()["event_type"] == "comment"

    action = client.post(
        f"/api/v1/incidents/{incident_id}/actions",
        headers=tokens["analyst@votex.demo"],
        json={
            "action_type": "warning_issued",
            "note": "Staff warning drafted for the morning bulletin.",
        },
    )
    assert action.status_code == 201
    assert action.json()["metadata"]["action_type"] == "warning_issued"


def test_stats_match_visible_list_scope(
    client: TestClient, tokens: dict[str, str]
) -> None:
    for email in ("analyst@votex.demo", "reporter@votex.demo", "analyst@inec.demo"):
        stats = client.get("/api/v1/incidents/stats", headers=tokens[email]).json()
        listed = client.get(
            "/api/v1/incidents", headers=tokens[email], params={"page_size": 100}
        ).json()
        assert stats["total"] == listed["total"]
        assert stats["open"] + stats["closed"] == stats["total"]
        assert set(stats["by_status"]).issubset(
            {
                "submitted",
                "under_review",
                "assigned",
                "investigating",
                "escalated",
                "contained",
                "remediated",
                "recovered",
                "closed",
            }
        )
