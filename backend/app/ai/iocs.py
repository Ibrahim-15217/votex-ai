"""Deterministic indicator-of-compromise extraction.

The extractor never resolves, fetches or contacts an indicator. It turns the
text an analyst already submitted, plus evidence metadata, into normalised
URLs, domains, IP addresses and file hashes that can be correlated safely.
"""

from __future__ import annotations

import ipaddress
import re
from dataclasses import dataclass
from urllib.parse import urlsplit, urlunsplit

from app.ai.url import extract_urls

DOMAIN_PATTERN = re.compile(
    r"(?<![\w@.-])((?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,24})(?![\w-])",
    re.IGNORECASE,
)
IPV4_PATTERN = re.compile(r"(?<![\d.])((?:\d{1,3}\.){3}\d{1,3})(?![\d.])")
SHA256_PATTERN = re.compile(r"(?<![a-fA-F0-9])[a-fA-F0-9]{64}(?![a-fA-F0-9])")
MD5_PATTERN = re.compile(r"(?<![a-fA-F0-9])[a-fA-F0-9]{32}(?![a-fA-F0-9])")

OFFICIAL_DOMAINS = ("inec.gov.ng", "cert.gov.ng", "nccc.gov.ng")
GENERIC_DOCUMENTATION_DOMAINS = (
    "example.com",
    "example.net",
    "example.org",
    "localhost",
    "localhost.localdomain",
)
PLATFORM_DOMAINS = (
    "facebook.com",
    "fb.com",
    "instagram.com",
    "t.me",
    "telegram.org",
    "tiktok.com",
    "twitter.com",
    "x.com",
    "whatsapp.com",
    "youtube.com",
    "facebook.example",
    "instagram.example",
    "social.example",
    "telegram.example",
    "tiktok.example",
    "twitter.example",
    "x.example",
    "youtube.example",
)

# File extensions that look like TLDs in free text. URLs still capture the real
# host, so skipping these avoids treating filenames as domains.
AMBIGUOUS_TLDS = frozenset(
    {
        "apk",
        "bat",
        "bin",
        "cfg",
        "cmd",
        "csv",
        "dat",
        "db",
        "dll",
        "doc",
        "docx",
        "eml",
        "exe",
        "gif",
        "htm",
        "html",
        "img",
        "ini",
        "iso",
        "jpeg",
        "jpg",
        "json",
        "lnk",
        "log",
        "md",
        "mov",
        "mp3",
        "mp4",
        "pdf",
        "png",
        "ps1",
        "py",
        "rar",
        "sh",
        "sql",
        "svg",
        "sys",
        "tmp",
        "txt",
        "vhd",
        "webp",
        "xls",
        "xlsm",
        "xlsx",
        "xml",
        "zip",
    }
)

MAX_VALUE_LENGTH = 2048


@dataclass(frozen=True)
class ExtractedIndicator:
    """One normalised indicator and the field it came from."""

    kind: str
    value: str
    display_value: str
    source: str


def _is_host_match(host: str, domains: tuple[str, ...]) -> bool:
    lowered = (host or "").lower().rstrip(".")
    return any(lowered == item or lowered.endswith(f".{item}") for item in domains)


def is_official_host(host: str) -> bool:
    """Return True when a host is on the government allowlist."""

    return _is_host_match(host, OFFICIAL_DOMAINS)


def is_generic_documentation_host(host: str) -> bool:
    """Return True for reserved documentation domains such as example.org."""

    return _is_host_match(host, GENERIC_DOCUMENTATION_DOMAINS)


def is_platform_host(host: str) -> bool:
    """Return True for social platforms that should not link unrelated cases."""

    return _is_host_match(host, PLATFORM_DOMAINS)


def _normalise_host(raw: str) -> str:
    host = (raw or "").strip().lower().rstrip(".")
    if host.startswith("www."):
        host = host[4:]
    return host


def _normalise_url(raw: str) -> tuple[str, str] | None:
    candidate = (raw or "").strip().rstrip(".,;:!?)]}'\"")
    if not candidate:
        return None
    if "://" not in candidate:
        candidate = f"http://{candidate}"
    try:
        parts = urlsplit(candidate)
    except ValueError:
        return None

    host = (parts.hostname or "").lower().rstrip(".")
    if host.startswith("www."):
        host = host[4:]
    if not host:
        return None

    scheme = (parts.scheme or "http").lower()
    netloc = host
    try:
        port = parts.port
    except ValueError:
        port = None
    if port and not ((scheme == "http" and port == 80) or (scheme == "https" and port == 443)):
        netloc = f"{host}:{port}"

    path = parts.path or "/"
    normalised = urlunsplit((scheme, netloc, path, parts.query, ""))
    return normalised[:MAX_VALUE_LENGTH], normalised


def _normalise_domain(raw: str) -> str | None:
    host = _normalise_host(raw)
    if not host or "." not in host or host.count(".") > 20:
        return None
    tld = host.rsplit(".", 1)[-1]
    if tld in AMBIGUOUS_TLDS:
        return None
    if host in {"localhost", "localhost.localdomain"} or host.startswith("-"):
        return None
    if _is_host_match(host, OFFICIAL_DOMAINS + GENERIC_DOCUMENTATION_DOMAINS):
        return None
    if _is_host_match(host, PLATFORM_DOMAINS):
        return None
    return host[:MAX_VALUE_LENGTH]


def _valid_ipv4(raw: str) -> str | None:
    try:
        address = ipaddress.IPv4Address(raw)
    except ValueError:
        return None
    if address.is_loopback or address.is_unspecified or address.is_multicast:
        return None
    return str(address)


def extract_iocs(
    *,
    text: str,
    reported_url: str | None = None,
    evidence_hashes: tuple[str, ...] = (),
    evidence_texts: tuple[str, ...] = (),
) -> list[ExtractedIndicator]:
    """Extract a deterministic, de-duplicated set of indicators.

    Source priority is reported URL, then the report narrative, then evidence.
    The first source that produced an indicator is retained.
    """

    found: dict[tuple[str, str], ExtractedIndicator] = {}

    def add(kind: str, value: str | None, display: str | None, source: str) -> None:
        if not value:
            return
        key = (kind, value)
        if key in found:
            return
        found[key] = ExtractedIndicator(
            kind=kind,
            value=value[:MAX_VALUE_LENGTH],
            display_value=(display or value)[:MAX_VALUE_LENGTH],
            source=source[:30],
        )

    def scan(text_value: str, source: str) -> None:
        if not text_value:
            return
        for raw_url in extract_urls(text_value):
            normalised = _normalise_url(raw_url)
            if normalised is None:
                continue
            value, display = normalised
            host = (urlsplit(value).hostname or "").lower()
            if is_official_host(host) or is_generic_documentation_host(host):
                continue
            add("url", value, display, source)
            address = _valid_ipv4(host)
            if address:
                add("ipv4", address, address, source)
            elif not is_platform_host(host):
                domain = _normalise_domain(host)
                add("domain", domain, domain, source)

        for match in DOMAIN_PATTERN.finditer(text_value):
            host = _normalise_domain(match.group(1))
            if host:
                add("domain", host, host, source)

        for match in IPV4_PATTERN.finditer(text_value):
            address = _valid_ipv4(match.group(1))
            if address:
                add("ipv4", address, address, source)

        for match in SHA256_PATTERN.finditer(text_value):
            digest = match.group(0).lower()
            add("sha256", digest, digest, source)

        for match in MD5_PATTERN.finditer(text_value):
            digest = match.group(0).lower()
            add("md5", digest, digest, source)

    if reported_url:
        scan(reported_url, "reported_url")
    scan(text, "description")
    for evidence_text in evidence_texts:
        scan(evidence_text, "evidence")

    for digest in evidence_hashes:
        candidate = (digest or "").strip().lower()
        if SHA256_PATTERN.fullmatch(candidate):
            add("sha256", candidate, candidate, "evidence")

    return list(found.values())
