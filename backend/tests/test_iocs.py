"""Pure IOC extraction: normalisation, noise rejection and de-duplication."""

from app.ai.iocs import extract_iocs

SHA256 = "a" * 64
MD5 = "b" * 32


def test_extracts_and_normalises_urls_domains_ips_and_hashes() -> None:
    text = (
        "Open HTTPS://WWW.Evil-Portal.Example/Login?token=1#fragment now. "
        "Backup at 192.0.2.44 and mirror evil-portal.example. "
        f"Sample hash {SHA256} and legacy {MD5}. "
        "Do not use inec.gov.ng, analyst@example.org or updated-voter-register.xlsm."
    )

    indicators = extract_iocs(text=text)
    by_key = {(item.kind, item.value) for item in indicators}

    assert ("url", "https://evil-portal.example/Login?token=1") in by_key
    assert ("domain", "evil-portal.example") in by_key
    assert ("ipv4", "192.0.2.44") in by_key
    assert ("sha256", SHA256) in by_key
    assert ("md5", MD5) in by_key

    assert not any("inec.gov.ng" in value for _, value in by_key)
    assert not any("example.org" in value for _, value in by_key)
    assert not any("xlsm" in value for _, value in by_key)


def test_excludes_platform_domains_and_loopback() -> None:
    indicators = extract_iocs(
        text="See facebook.example/votex-fake-page and 127.0.0.1 for details.",
        reported_url="https://facebook.example/votex-fake-page",
    )
    keys = {(item.kind, item.value) for item in indicators}

    assert ("domain", "facebook.example") not in keys
    assert ("ipv4", "127.0.0.1") not in keys
    # The exact fake page is still useful, even though the platform is not.
    assert ("url", "https://facebook.example/votex-fake-page") in keys


def test_deduplicates_and_respects_source_priority() -> None:
    domain = "duplicate-indicator.example"
    indicators = extract_iocs(
        text=f"Visit https://{domain}/login and https://{domain}/verify.",
        reported_url=f"https://{domain}/login",
        evidence_texts=(
            f"The same host {domain} appears in the attached email.",
        ),
    )
    domain_rows = [item for item in indicators if item.kind == "domain"]
    assert len(domain_rows) == 1
    assert domain_rows[0].source == "reported_url"

    url_rows = [item for item in indicators if item.kind == "url"]
    assert len(url_rows) == 2
    assert {item.value for item in url_rows} == {
        f"https://{domain}/login",
        f"https://{domain}/verify",
    }
