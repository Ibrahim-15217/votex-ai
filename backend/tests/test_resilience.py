"""Resilience assessment scoring, remediation, exercises and tenant isolation."""

from uuid import uuid4

from fastapi.testclient import TestClient

from app.core.resilience import CONTROL_KEYS, CONTROLS


def answers(value: int) -> dict[str, int]:
    return {key: value for key in CONTROL_KEYS}


def create_assessment(
    client: TestClient,
    headers: dict[str, str],
    *,
    value: int = 2,
    title: str | None = None,
) -> dict:
    response = client.post(
        "/api/v1/resilience/assessments",
        headers=headers,
        json={
            "title": title or f"Resilience probe {uuid4().hex[:8]}",
            "notes": "Synthetic test assessment. No real organisational data.",
            "answers": answers(value),
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_questionnaire_exposes_the_fixed_control_set(
    client: TestClient, tokens: dict[str, str]
) -> None:
    response = client.get(
        "/api/v1/resilience/questionnaire", headers=tokens["analyst@votex.demo"]
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["controls"]) == 12
    assert [control["key"] for control in body["controls"]] == list(CONTROL_KEYS)
    assert {control["category"] for control in body["controls"]} == {
        "governance",
        "identity",
        "network",
        "data",
        "response",
        "people",
    }
    assert set(body["maturity_levels"]) == {"0", "1", "2", "3", "4"}
    assert "not a certified index" in body["scoring_note"]


def test_assessment_scores_answers_and_opens_findings(
    client: TestClient, tokens: dict[str, str]
) -> None:
    body = create_assessment(client, tokens["analyst@votex.demo"], value=2)

    assert body["score"] == 50.0
    assert body["band"] == "developing"
    assert body["total_findings"] == 12
    assert body["open_findings"] == 12
    assert "50.0/100" in body["summary"]
    assert all(finding["severity"] == "medium" for finding in body["findings"])
    assert all(finding["remediation_status"] == "open" for finding in body["findings"])
    assert body["created_by"]["email"] == "analyst@votex.demo"
    assert len(body["controls"]) == 12
    assert body["answers"] == answers(2)

    audit = client.get(
        "/api/v1/audit",
        headers=tokens["analyst@votex.demo"],
        params={"action": "resilience.assessment_created", "page_size": 100},
    ).json()
    assert any(entry["resource_id"] == body["id"] for entry in audit["items"])


def test_perfect_score_has_no_findings(
    client: TestClient, tokens: dict[str, str]
) -> None:
    body = create_assessment(client, tokens["admin@votex.demo"], value=4)

    assert body["score"] == 100.0
    assert body["band"] == "resilient"
    assert body["total_findings"] == 0
    assert body["findings"] == []


def test_incomplete_or_unknown_answers_are_rejected(
    client: TestClient, tokens: dict[str, str]
) -> None:
    partial = answers(3)
    partial.pop(CONTROL_KEYS[0])
    missing = client.post(
        "/api/v1/resilience/assessments",
        headers=tokens["analyst@votex.demo"],
        json={"title": "Incomplete assessment", "answers": partial},
    )
    assert missing.status_code == 422
    assert "Every control needs an answer" in missing.text

    unknown = answers(3)
    unknown["governance.unlisted"] = 3
    extra = client.post(
        "/api/v1/resilience/assessments",
        headers=tokens["analyst@votex.demo"],
        json={"title": "Unknown control assessment", "answers": unknown},
    )
    assert extra.status_code == 422
    assert "Unknown control keys" in extra.text


def test_reporters_cannot_use_resilience_endpoints(
    client: TestClient, tokens: dict[str, str]
) -> None:
    headers = tokens["reporter@votex.demo"]
    assert client.get("/api/v1/resilience/questionnaire", headers=headers).status_code == 403
    assert client.get("/api/v1/resilience/assessments", headers=headers).status_code == 403
    assert client.get("/api/v1/resilience/exercises", headers=headers).status_code == 403
    assert (
        client.post(
            "/api/v1/resilience/assessments",
            headers=headers,
            json={"title": "Reporter attempt", "answers": answers(3)},
        ).status_code
        == 403
    )


def test_assessments_and_findings_are_tenant_scoped(
    client: TestClient, tokens: dict[str, str]
) -> None:
    body = create_assessment(client, tokens["analyst@votex.demo"], value=1)
    finding_id = body["findings"][0]["id"]

    foreign_read = client.get(
        f"/api/v1/resilience/assessments/{body['id']}",
        headers=tokens["analyst@inec.demo"],
    )
    assert foreign_read.status_code == 404

    foreign_update = client.patch(
        f"/api/v1/resilience/findings/{finding_id}",
        headers=tokens["analyst@inec.demo"],
        json={"remediation_status": "resolved"},
    )
    assert foreign_update.status_code == 404

    own_read = client.get(
        f"/api/v1/resilience/assessments/{body['id']}",
        headers=tokens["analyst@votex.demo"],
    )
    assert own_read.status_code == 200


def test_finding_remediation_is_recorded_and_audited(
    client: TestClient, tokens: dict[str, str]
) -> None:
    body = create_assessment(client, tokens["analyst@votex.demo"], value=1)
    finding = body["findings"][0]

    response = client.patch(
        f"/api/v1/resilience/findings/{finding['id']}",
        headers=tokens["analyst@votex.demo"],
        json={
            "remediation_status": "resolved",
            "owner": "Response team",
            "note": "Closed in the synthetic test.",
        },
    )
    assert response.status_code == 200
    updated = response.json()
    changed = next(item for item in updated["findings"] if item["id"] == finding["id"])
    assert changed["remediation_status"] == "resolved"
    assert changed["owner"] == "Response team"
    assert updated["open_findings"] == body["open_findings"] - 1

    audit = client.get(
        "/api/v1/audit",
        headers=tokens["analyst@votex.demo"],
        params={"action": "resilience.finding_updated", "page_size": 100},
    ).json()
    entry = next(item for item in audit["items"] if item["resource_id"] == str(finding["id"]))
    assert entry["detail"]["to_status"] == "resolved"


def test_summary_reports_the_latest_assessment(
    client: TestClient, tokens: dict[str, str]
) -> None:
    response = client.get(
        "/api/v1/resilience/summary", headers=tokens["analyst@votex.demo"]
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total_assessments"] >= 2
    assert body["latest"] is not None
    assert 0 <= body["latest"]["score"] <= 100
    assert set(body["open_by_severity"]) == {"critical", "high", "medium", "low"}
    assert body["open_findings"] + body["resolved_findings"] == body["total_findings"]


def test_exercise_lifecycle_records_tasks_and_performance(
    client: TestClient, tokens: dict[str, str]
) -> None:
    created = client.post(
        "/api/v1/resilience/exercises",
        headers=tokens["analyst@votex.demo"],
        json={"title": f"Synthetic exercise {uuid4().hex[:8]}"},
    )
    assert created.status_code == 201, created.text
    exercise = created.json()
    assert exercise["status"] == "running"
    assert exercise["tasks_total"] == 6
    assert exercise["tasks_done"] == 0
    assert exercise["performance"]["grade"] == "needs_review"
    assert all(task["status"] == "pending" for task in exercise["tasks"])

    too_early = client.post(
        f"/api/v1/resilience/exercises/{exercise['id']}/complete",
        headers=tokens["analyst@votex.demo"],
    )
    assert too_early.status_code == 409
    assert "Finish or skip every task" in too_early.text

    for task in exercise["tasks"]:
        status = "done" if task["sequence"] <= 5 else "skipped"
        response = client.patch(
            f"/api/v1/resilience/exercises/{exercise['id']}/tasks/{task['id']}",
            headers=tokens["analyst@votex.demo"],
            json={"status": status, "notes": "Recorded in the synthetic test."},
        )
        assert response.status_code == 200, response.text

    completed = client.post(
        f"/api/v1/resilience/exercises/{exercise['id']}/complete",
        headers=tokens["analyst@votex.demo"],
    )
    assert completed.status_code == 200, completed.text
    body = completed.json()
    assert body["status"] == "completed"
    assert body["tasks_done"] == 5
    assert body["performance"]["tasks_skipped"] == 1
    assert body["performance"]["completion_pct"] == 83.3
    assert body["performance"]["grade"] == "ready"
    assert body["performance"]["elapsed_seconds"] >= 0

    readonly = client.patch(
        f"/api/v1/resilience/exercises/{exercise['id']}/tasks/{exercise['tasks'][0]['id']}",
        headers=tokens["analyst@votex.demo"],
        json={"status": "pending"},
    )
    assert readonly.status_code == 409

    audit = client.get(
        "/api/v1/audit",
        headers=tokens["analyst@votex.demo"],
        params={"action": "resilience.exercise_completed", "page_size": 100},
    ).json()
    assert any(entry["resource_id"] == exercise["id"] for entry in audit["items"])


def test_exercises_are_tenant_scoped(
    client: TestClient, tokens: dict[str, str]
) -> None:
    listed = client.get(
        "/api/v1/resilience/exercises", headers=tokens["analyst@votex.demo"]
    ).json()
    assert listed
    exercise_id = listed[0]["id"]

    foreign_read = client.get(
        f"/api/v1/resilience/exercises/{exercise_id}",
        headers=tokens["analyst@inec.demo"],
    )
    assert foreign_read.status_code == 404

    foreign_list = client.get(
        "/api/v1/resilience/exercises", headers=tokens["analyst@inec.demo"]
    )
    assert foreign_list.status_code == 200
    assert all(item["id"] != exercise_id for item in foreign_list.json())


def test_seeded_demo_contains_a_completed_exercise(
    client: TestClient, tokens: dict[str, str]
) -> None:
    listed = client.get(
        "/api/v1/resilience/exercises", headers=tokens["analyst@votex.demo"]
    ).json()
    seeded = [item for item in listed if item["status"] == "completed"]
    assert seeded
    assert any(item["tasks_done"] == 5 for item in seeded)


def test_audit_chain_still_verifies_after_resilience_writes(
    client: TestClient, tokens: dict[str, str]
) -> None:
    body = client.get("/api/v1/audit/verify", headers=tokens["analyst@votex.demo"]).json()

    assert body["valid"] is True
    assert body["entries_checked"] > 0
    assert body["first_invalid_id"] is None
