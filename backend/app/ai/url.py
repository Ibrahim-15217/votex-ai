"""URL and domain intelligence (component ``U``).

The analyser never resolves, fetches or contacts a URL. It reasons only about
the string an analyst submitted, which keeps the prototype offline and safe.
"""

from __future__ import annotations

import ipaddress
import re
from urllib.parse import urlsplit

from app.ai.types import Indicator, UrlResult

URL_PATTERN = re.compile(r"https?://[^\s<>\"')\]]+", re.IGNORECASE)

OFFICIAL_DOMAINS = (
    "inec.gov.ng",
    "cert.gov.ng",
    "nccc.gov.ng",
)

RESERVED_SUFFIXES = (".example", ".test", ".invalid", ".localhost")

SHORTENER_HOSTS = (
    "bit.ly",
    "bit.example",
    "tinyurl.com",
    "t.co",
    "goo.gl",
    "ow.ly",
    "is.gd",
    "short.link",
    "short.example",
)

SUSPICIOUS_TLDS = (
    ".example",
    ".test",
    ".invalid",
    ".xyz",
    ".top",
    ".click",
    ".link",
    ".zip",
    ".mov",
    ".live",
    ".support",
    ".help",
)

BRAND_TOKENS = (
    "inec",
    "pvc",
    "votex",
    "inEC".lower(),
)

HOST_LURE_TOKENS = (
    "login",
    "log-in",
    "signin",
    "sign-in",
    "verify",
    "verification",
    "secure",
    "security",
    "update",
    "account",
    "portal",
    "pay",
    "payment",
    "confirm",
    "support",
    "staff",
    "pvc",
    "accreditation",
    "result",
    "results",
    "allowance",
    "activation",
    "session",
    "revalidate",
    "registration",
    "upload",
)

PATH_LURE_TOKENS = (
    "login",
    "signin",
    "verify",
    "secure",
    "update",
    "account",
    "pay",
    "payment",
    "confirm",
    "upload",
    "portal",
    "start",
    "leak",
)

IPV4_PATTERN = re.compile(r"^(\d{1,3}\.){3}\d{1,3}$")


def extract_urls(text: str) -> list[str]:
    """Return URL-like strings in first-seen order, without punctuation."""

    seen: set[str] = set()
    urls: list[str] = []
    for match in URL_PATTERN.finditer(text or ""):
        candidate = match.group(0).rstrip(".,;:!?)]}'\"")
        if candidate and candidate not in seen:
            seen.add(candidate)
            urls.append(candidate)
    return urls


def _is_official_host(host: str) -> bool:
    host = host.lower().rstrip(".")
    return any(host == domain or host.endswith(f".{domain}") for domain in OFFICIAL_DOMAINS)


def _is_reserved_host(host: str) -> bool:
    lowered = host.lower().rstrip(".")
    if lowered.endswith(RESERVED_SUFFIXES) or ".example." in lowered:
        return True
    if IPV4_PATTERN.match(lowered):
        try:
            address = ipaddress.IPv4Address(lowered)
        except ValueError:
            return False
        return any(address in network for network in (
            ipaddress.IPv4Network("192.0.2.0/24"),
            ipaddress.IPv4Network("198.51.100.0/24"),
            ipaddress.IPv4Network("203.0.113.0/24"),
        ))
    return False


def _analyse_single(raw_url: str) -> UrlResult:
    findings: list[dict] = []
    indicators: list[Indicator] = []

    def add(code: str, label: str, weight: int, detail: str, severity: str = "medium") -> None:
        findings.append(
            {"code": code, "label": label, "weight": weight, "detail": detail}
        )
        indicators.append(
            Indicator(
                code=code,
                label=label,
                category="url",
                severity=severity,
                detail=detail,
            )
        )

    try:
        parts = urlsplit(raw_url if "://" in raw_url else f"http://{raw_url}")
    except ValueError:
        return UrlResult(
            score=55.0,
            findings=[{"code": "url_unparseable", "label": "Malformed URL", "weight": 35, "detail": raw_url}],
            indicators=[],
            host=None,
            has_url=True,
        )

    host = (parts.hostname or "").lower().rstrip(".")
    is_official = _is_official_host(host)
    score = 20

    if is_official:
        findings.append(
            {
                "code": "official_domain",
                "label": "Official government domain",
                "weight": -20,
                "detail": f"{host} is on the official-domain allowlist.",
            }
        )
        indicators.append(
            Indicator(
                code="official_domain",
                label="Official government domain",
                category="url",
                severity="info",
                detail=f"{host} matches the official-domain allowlist.",
            )
        )
        return UrlResult(
            score=2.0,
            findings=findings,
            indicators=indicators,
            host=host,
            is_official=True,
            has_url=True,
        )

    if parts.scheme.lower() == "http":
        score += 10
        add(
            "plain_http",
            "Unencrypted HTTP link",
            10,
            "The link uses plain HTTP, so credentials or pages can be tampered with in transit.",
            "medium",
        )

    if IPV4_PATTERN.match(host):
        score += 22
        add(
            "ip_literal_host",
            "IP address instead of a domain",
            22,
            f"The link points directly to the IP address {host}.",
            "high",
        )

    if _is_reserved_host(host):
        score += 28
        add(
            "reserved_demo_host",
            "Reserved demo or documentation host",
            28,
            f"{host} is a reserved .example/.test/documentation host used to simulate an untrusted destination.",
            "high",
        )

    if host.startswith("xn--") or ".xn--" in host:
        score += 14
        add(
            "punycode_host",
            "Punycode host",
            14,
            "The host contains punycode, which can disguise lookalike characters.",
            "high",
        )

    if "@" in parts.netloc:
        score += 14
        add(
            "userinfo_trick",
            "Credential-like prefix in URL",
            14,
            "The URL uses an '@' construct that can hide the real destination.",
            "high",
        )

    if host in SHORTENER_HOSTS or any(host.endswith(f".{item}") for item in SHORTENER_HOSTS):
        score += 10
        add(
            "url_shortener",
            "URL shortener",
            10,
            "Shortened links hide the final destination from the reader.",
            "medium",
        )

    if any(host.endswith(tld) for tld in SUSPICIOUS_TLDS):
        score += 8
        add(
            "suspicious_tld",
            "High-abuse top-level domain",
            8,
            f"The host uses the high-abuse suffix ending '{host.rsplit('.', 1)[-1]}'.",
            "medium",
        )

    hyphen_count = host.count("-")
    if hyphen_count:
        weight = min(hyphen_count * 5, 15)
        score += weight
        add(
            "hyphenated_host",
            "Hyphenated host name",
            weight,
            f"The host contains {hyphen_count} hyphen(s), a common lookalike-domain pattern.",
            "medium",
        )

    if host.count(".") >= 3:
        score += 6
        add(
            "deep_subdomain",
            "Deep subdomain chain",
            6,
            "A long subdomain chain can push the real registrable domain out of view.",
            "medium",
        )

    lure_hits = sorted({token for token in HOST_LURE_TOKENS if token in host})
    if lure_hits:
        weight = min(len(lure_hits) * 4, 16)
        score += weight
        add(
            "host_lure_keywords",
            "Credential or payment words in host",
            weight,
            "The host contains lure vocabulary: " + ", ".join(lure_hits) + ".",
            "medium",
        )

    brand_hits = sorted({token for token in BRAND_TOKENS if token in host})
    if brand_hits:
        score += 15
        add(
            "brand_on_unofficial_domain",
            "Brand name on an unofficial domain",
            15,
            "The host references "
            + ", ".join(brand_hits)
            + " but is not on the official-domain allowlist.",
            "high",
        )

    path_hits = sorted({token for token in PATH_LURE_TOKENS if token in (parts.path or "").lower()})
    if path_hits:
        score += min(len(path_hits) * 3, 9)
        add(
            "path_lure_keywords",
            "Lure words in URL path",
            min(len(path_hits) * 3, 9),
            "The path contains: " + ", ".join(path_hits) + ".",
            "low",
        )

    if len(host) > 30:
        score += 4
        add(
            "long_host",
            "Unusually long host",
            4,
            f"The host is {len(host)} characters long, which makes manual review harder.",
            "low",
        )

    if parts.port and parts.port not in (80, 443):
        score += 4
        add(
            "nonstandard_port",
            "Non-standard port",
            4,
            f"The URL uses port {parts.port}.",
            "low",
        )

    if re.search(r"%[0-9a-fA-F]{2}", raw_url):
        score += 5
        add(
            "encoded_characters",
            "Encoded characters in URL",
            5,
            "Percent-encoding can conceal the true path or parameters.",
            "low",
        )

    score = max(0.0, min(100.0, float(score)))
    return UrlResult(
        score=round(score, 1),
        findings=findings,
        indicators=indicators,
        host=host or None,
        is_official=is_official,
        has_url=True,
    )


def analyse_url(text: str, reported_url: str | None) -> UrlResult:
    """Analyse the reported URL plus any URLs found in the narrative."""

    candidates: list[str] = []
    if reported_url:
        candidates.append(reported_url.strip())
    for candidate in extract_urls(text):
        if candidate not in candidates:
            candidates.append(candidate)

    if not candidates:
        return UrlResult(
            score=20.0,
            findings=[
                {
                    "code": "no_url",
                    "label": "No URL supplied",
                    "weight": 0,
                    "detail": "The report contains no link, so URL intelligence is neutral.",
                }
            ],
            indicators=[],
            host=None,
            is_official=False,
            has_url=False,
        )

    primary = _analyse_single(candidates[0])
    if len(candidates) > 1:
        extra = min(len(candidates) - 1, 3) * 3
        primary.score = min(100.0, primary.score + extra)
        primary.findings.append(
            {
                "code": "multiple_urls",
                "label": "Multiple links in one report",
                "weight": extra,
                "detail": f"{len(candidates)} distinct links were found in the report.",
            }
        )
        primary.indicators.append(
            Indicator(
                code="multiple_urls",
                label="Multiple links in one report",
                category="url",
                severity="low",
                detail=f"{len(candidates)} distinct links were found in the report.",
            )
        )
    return primary
