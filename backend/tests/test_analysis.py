"""Hybrid AI analysis: scoring, persistence, RBAC and audit."""

from fastapi.testclient import TestClient

CLASSIFICATIONS = {"benign", "suspicious", "high_risk"}


def create(
    client: TestClient,
    headers: dict[str, str],
    *,
    title: str,
    description: str,
    category: str = "phishing",
    channel: str = "email",
    reported_url: str | None = "https://inec-verify.example/login",
) -> dict:
    response = client.post(
        "/api/v1/incidents",
        headers=headers,
        json={
            "title": title,
            "description": description,
            "category": category,
            "channel": channel,
            "reported_url": reported_url,
            "state": "Lagos",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_create_triggers_explainable_analysis(
    client: TestClient, tokens: dict[str, str]
) -> None:
    incident = create(
        client,
        tokens["reporter@votex.demo"],
        title="Credential harvest targeting presiding officers",
        description=(
            "Urgent: enter your password, OTP and BVN at the staff portal within 6 hours "
            "or your account will be suspended and you will be removed from deployment."
        ),
        reported_url="https://inec-staff-verify.example/login",
    )

    assert incident["ai_status"] in {"complete", "degraded"}
    assert incident["risk_score"] is not None
    analysis = incident["analysis"]
    assert analysis is not None
    assert analysis["classification"] in CLASSIFICATIONS
    assert analysis["classification"] == "high_risk"
    assert analysis["risk_score"] >= 65
    assert analysis["model_version"]
    assert analysis["ruleset_version"]
    assert 0.5 <= analysis["confidence"] <= 0.98
    assert analysis["latency_ms"] >= 0

    assert len(analysis["factors"]) == 4
    assert {factor["key"] for factor in analysis["factors"]} == {"U", "N", "M", "I"}
    weighted = sum(factor["contribution"] for factor in analysis["factors"])
    assert abs(weighted - analysis["risk_score"]) <= 0.11

    assert analysis["reasons"]
    assert any(reason["direction"] == "increases_risk" for reason in analysis["reasons"])
    assert any(indicator["code"] == "credential_request" for indicator in analysis["indicators"])
    assert any(indicator["code"] == "reserved_demo_host" for indicator in analysis["indicators"])


def test_benign_report_scores_much_lower(
    client: TestClient, tokens: dict[str, str]
) -> None:
    benign = create(
        client,
        tokens["reporter@votex.demo"],
        title="Routine briefing for presiding officers",
        description=(
            "The State Electoral Office will hold a free briefing for presiding officers "
            "on 20 November 2027. Attendance is free and no payment is required. "
            "Read the notice at the official page."
        ),
        category="other",
        channel="email",
        reported_url="https://inec.gov.ng/news/",
    )

    malicious = create(
        client,
        tokens["reporter@votex.demo"],
        title="Fake payment portal",
        description=(
            "Pay a N5,000 processing fee at the link today or your accreditation will be "
            "cancelled and you will lose your place."
        ),
        category="payment_fraud",
        channel="sms",
        reported_url="http://pvc-pay.example/verify",
    )

    assert benign["analysis"]["risk_score"] < malicious["analysis"]["risk_score"]
    assert benign["analysis"]["classification"] in {"benign", "suspicious"}
    assert malicious["analysis"]["classification"] == "high_risk"
    assert benign["analysis"]["url_score"] <= 5
    assert malicious["analysis"]["url_score"] >= 50


def test_analysis_is_deterministic_across_runs(
    client: TestClient, tokens: dict[str, str]
) -> None:
    incident = create(
        client,
        tokens["reporter@votex.demo"],
        title="Deterministic scoring probe",
        description=(
            "Confirm your login credentials at the portal before the deadline or access "
            "will be removed."
        ),
    )
    first = incident["analysis"]

    response = client.post(
        f"/api/v1/incidents/{incident['id']}/analyze",
        headers=tokens["analyst@votex.demo"],
    )
    assert response.status_code == 200, response.text
    second = response.json()["analysis"]

    assert second["id"] != first["id"]
    assert second["risk_score"] == first["risk_score"]
    assert second["classification"] == first["classification"]
    assert second["url_score"] == first["url_score"]
    assert second["nlp_score"] == first["nlp_score"]


def test_reanalysis_is_audited(
    client: TestClient, tokens: dict[str, str]
) -> None:
    incident = create(
        client,
        tokens["reporter@votex.demo"],
        title="Audit trail analysis probe",
        description="A suspicious message asking staff to verify their account at a lookalike domain.",
    )
    client.post(
        f"/api/v1/incidents/{incident['id']}/analyze",
        headers=tokens["analyst@votex.demo"],
    )

    audit = client.get(
        "/api/v1/audit",
        headers=tokens["analyst@votex.demo"],
        params={"action": "incident.analysed", "page_size": 100},
    )
    assert audit.status_code == 200
    matches = [
        entry
        for entry in audit.json()["items"]
        if entry["resource_id"] == incident["id"]
    ]
    assert len(matches) >= 2  # automatic analysis + manual re-run
    assert all("risk_score" in entry["detail"] for entry in matches)
    assert all("model_version" in entry["detail"] for entry in matches)


def test_reporter_cannot_reanalyse(
    client: TestClient, tokens: dict[str, str]
) -> None:
    incident = create(
        client,
        tokens["reporter@votex.demo"],
        title="Reporter permission probe",
        description="A report used to confirm that only analysts can re-run the analyser.",
    )
    response = client.post(
        f"/api/v1/incidents/{incident['id']}/analyze",
        headers=tokens["reporter@votex.demo"],
    )
    assert response.status_code == 403


def test_cross_tenant_cannot_analyse(
    client: TestClient, tokens: dict[str, str]
) -> None:
    incident = create(
        client,
        tokens["reporter@votex.demo"],
        title="Cross tenant analysis probe",
        description="A report used to confirm tenant isolation on the analysis endpoint.",
    )
    response = client.post(
        f"/api/v1/incidents/{incident['id']}/analyze",
        headers=tokens["analyst@inec.demo"],
    )
    assert response.status_code == 404


def test_seeded_incidents_are_backfilled(
    client: TestClient, tokens: dict[str, str]
) -> None:
    listing = client.get(
        "/api/v1/incidents",
        headers=tokens["analyst@votex.demo"],
        params={"search": "VX-2026-A10001"},
    ).json()
    assert listing["total"] == 1
    detail = client.get(
        f"/api/v1/incidents/{listing['items'][0]['id']}",
        headers=tokens["analyst@votex.demo"],
    ).json()

    assert detail["analysis"] is not None
    assert detail["analysis"]["classification"] in CLASSIFICATIONS
    assert detail["risk_score"] == detail["analysis"]["risk_score"]
    assert detail["analysis"]["summary"]
