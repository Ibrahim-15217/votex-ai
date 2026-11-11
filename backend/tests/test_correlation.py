"""Indicator correlation, related incidents, dashboards and CSV exports."""

from uuid import uuid4

from fastapi.testclient import TestClient


def create_incident(
    client: TestClient,
    headers: dict[str, str],
    *,
    title: str,
    description: str,
    reported_url: str | None,
    category: str = "phishing",
    channel: str = "email",
    state: str = "Lagos",
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
            "state": state,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def unique_host(prefix: str = "phase3") -> str:
    return f"{prefix}-{uuid4().hex[:10]}.example"


def test_shared_domain_links_incidents_and_respects_tenant(
    client: TestClient, tokens: dict[str, str]
) -> None:
    host = unique_host()
    first = create_incident(
        client,
        tokens["reporter@votex.demo"],
        title="Shared domain probe one",
        description="The page asks for staff credentials at the link below.",
        reported_url=f"https://{host}/login",
    )
    second = create_incident(
        client,
        tokens["reporter@votex.demo"],
        title="Shared domain probe two",
        description="A second report uses the same host with a different path.",
        reported_url=f"https://{host}/verify",
    )
    foreign = create_incident(
        client,
        tokens["reporter@inec.demo"],
        title="Foreign tenant domain probe",
        description="Synthetic report in another tenant using the same host.",
        reported_url=f"https://{host}/login",
    )

    related = client.get(
        f"/api/v1/incidents/{first['id']}/related",
        headers=tokens["analyst@votex.demo"],
    )
    assert related.status_code == 200, related.text
    body = related.json()
    assert body["total"] >= 1
    matched = next(item for item in body["items"] if item["id"] == second["id"])
    assert matched["shared_count"] >= 1
    assert any(
        indicator["kind"] == "domain" and indicator["value"] == host
        for indicator in matched["shared_indicators"]
    )
    assert all(item["id"] != foreign["id"] for item in body["items"])

    search = client.get(
        "/api/v1/indicators",
        headers=tokens["analyst@votex.demo"],
        params={"q": host, "kind": "domain"},
    )
    assert search.status_code == 200, search.text
    page = search.json()
    assert page["total"] == 1
    indicator = page["items"][0]
    assert indicator["value"] == host
    assert indicator["incident_count"] == 2
    assert indicator["example_incident_reference"] in {
        first["reference"],
        second["reference"],
    }

    detail = client.get(
        f"/api/v1/indicators/{indicator['id']}",
        headers=tokens["analyst@votex.demo"],
    )
    assert detail.status_code == 200, detail.text
    linked_ids = {item["id"] for item in detail.json()["incidents"]}
    assert {first["id"], second["id"]} <= linked_ids
    assert foreign["id"] not in linked_ids

    reporter_search = client.get(
        "/api/v1/indicators", headers=tokens["reporter@votex.demo"]
    )
    assert reporter_search.status_code == 403


def test_related_incidents_are_scoped_for_reporters(
    client: TestClient, tokens: dict[str, str]
) -> None:
    host = unique_host("reporter-scope")
    own = create_incident(
        client,
        tokens["reporter@votex.demo"],
        title="Reporter scope probe one",
        description="A synthetic report owned by the reporter.",
        reported_url=f"https://{host}/one",
    )
    same_reporter = create_incident(
        client,
        tokens["reporter@votex.demo"],
        title="Reporter scope probe two",
        description="Another synthetic report owned by the same reporter.",
        reported_url=f"https://{host}/two",
    )
    other_reporter = create_incident(
        client,
        tokens["admin@votex.demo"],
        title="Administrator report using the same domain",
        description="Another synthetic report in the same tenant.",
        reported_url=f"https://{host}/three",
    )

    related = client.get(
        f"/api/v1/incidents/{own['id']}/related",
        headers=tokens["reporter@votex.demo"],
    )
    assert related.status_code == 200, related.text
    ids = {item["id"] for item in related.json()["items"]}
    assert same_reporter["id"] in ids
    assert other_reporter["id"] not in ids


def test_evidence_hash_and_text_become_indicators(
    client: TestClient, tokens: dict[str, str]
) -> None:
    host = unique_host("evidence")
    incident = create_incident(
        client,
        tokens["reporter@votex.demo"],
        title="Evidence correlation probe",
        description="The report body contains no link.",
        reported_url=None,
        category="malware",
    )
    body = (
        "Synthetic evidence note.\n"
        f"The loader contacts https://{host}/collect before downloading.\n"
        f"Known sample SHA-256: {'c' * 64}\n"
    )
    upload = client.post(
        f"/api/v1/incidents/{incident['id']}/evidence",
        headers=tokens["reporter@votex.demo"],
        files={"file": ("correlation-note.txt", body.encode("utf-8"), "text/plain")},
    )
    assert upload.status_code == 201, upload.text
    file_hash = upload.json()["sha256"]

    domain_search = client.get(
        "/api/v1/indicators",
        headers=tokens["analyst@votex.demo"],
        params={"q": host, "kind": "domain"},
    )
    assert domain_search.status_code == 200
    assert domain_search.json()["total"] == 1

    hash_search = client.get(
        "/api/v1/indicators",
        headers=tokens["analyst@votex.demo"],
        params={"q": file_hash, "kind": "sha256"},
    )
    assert hash_search.status_code == 200
    assert hash_search.json()["total"] == 1
    assert hash_search.json()["items"][0]["value"] == file_hash


def test_dashboards_and_national_suppression(
    client: TestClient, tokens: dict[str, str]
) -> None:
    # One incident in a unique state gives the national dashboard a small cell.
    create_incident(
        client,
        tokens["reporter@votex.demo"],
        title="Small national cell probe",
        description="Synthetic report used to prove k-anonymity suppression.",
        reported_url=None,
        category="other",
        channel="phone",
        state="Zamfara",
    )

    organisation = client.get(
        "/api/v1/dashboards/organisation", headers=tokens["analyst@votex.demo"]
    )
    assert organisation.status_code == 200, organisation.text
    org = organisation.json()
    assert org["scope"] == "organisation"
    assert org["organisation"]["slug"] == "votex-demo-authority"
    assert len(org["trend"]) == 30
    assert len(org["severity"]) == 4
    assert len(org["categories"]) == 7
    assert org["summary"]["k_threshold"] == 5
    assert org["summary"]["total"] is not None
    assert org["summary"]["total"] >= 1
    assert org["summary"]["suppressed_cells"] == 0

    admin = client.get(
        "/api/v1/dashboards/national", headers=tokens["admin@votex.demo"]
    )
    assert admin.status_code == 200, admin.text
    national = admin.json()
    assert national["scope"] == "national"
    assert national["organisation"] is None
    assert national["summary"]["k_threshold"] == 5
    assert national["summary"]["organisations"] >= 2
    assert national["summary"]["suppressed_cells"] > 0
    assert len(national["trend"]) == 30
    suppressed_cells = [
        cell
        for section in ("severity", "categories", "channels", "states", "statuses")
        for cell in national[section]
        if cell["suppressed"]
    ]
    assert suppressed_cells
    assert all(cell["count"] is None for cell in suppressed_cells)

    analyst_national = client.get(
        "/api/v1/dashboards/national", headers=tokens["analyst@votex.demo"]
    )
    assert analyst_national.status_code == 403


def test_csv_exports_are_permission_checked_and_audited(
    client: TestClient, tokens: dict[str, str]
) -> None:
    host = unique_host("export")
    create_incident(
        client,
        tokens["reporter@votex.demo"],
        title="CSV export probe",
        description="Synthetic report used to test indicator export.",
        reported_url=f"https://{host}/start",
    )

    indicators = client.get(
        "/api/v1/indicators/export",
        headers=tokens["analyst@votex.demo"],
        params={"q": host},
    )
    assert indicators.status_code == 200, indicators.text
    assert indicators.headers["content-type"].startswith("text/csv")
    assert "kind,value,incident_count" in indicators.text
    assert host in indicators.text

    organisation = client.get(
        "/api/v1/dashboards/organisation/export",
        headers=tokens["analyst@votex.demo"],
    )
    assert organisation.status_code == 200
    assert "section,key,label,value,suppressed" in organisation.text
    assert "summary" in organisation.text

    national = client.get(
        "/api/v1/dashboards/national/export", headers=tokens["admin@votex.demo"]
    )
    assert national.status_code == 200
    assert "yes" in national.text

    reporter_export = client.get(
        "/api/v1/indicators/export", headers=tokens["reporter@votex.demo"]
    )
    assert reporter_export.status_code == 403
    analyst_national_export = client.get(
        "/api/v1/dashboards/national/export", headers=tokens["analyst@votex.demo"]
    )
    assert analyst_national_export.status_code == 403

    audit = client.get(
        "/api/v1/audit",
        headers=tokens["admin@votex.demo"],
        params={"action": "intelligence.exported", "page_size": 100},
    )
    assert audit.status_code == 200
    assert audit.json()["total"] >= 3
