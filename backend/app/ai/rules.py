"""Indicators and policy rules (component ``I``).

This component reasons about structured report attributes and combinations that
automatically raise or lower priority: the chosen category, the channel, a
payment amount, a macro-enabled attachment, a credential request paired with an
action verb, and whether the destination is an official domain.
"""

from __future__ import annotations

import re

from app.ai.types import Indicator, RuleResult, UrlResult

CATEGORY_PRIOR = {
    "phishing": 62.0,
    "fake_portal": 68.0,
    "impersonation": 58.0,
    "payment_fraud": 70.0,
    "malware": 68.0,
    "fake_result": 52.0,
    "other": 30.0,
}

CHANNEL_WEIGHT = {
    "sms": 8.0,
    "whatsapp": 8.0,
    "web_form": 5.0,
    "email": 4.0,
    "phone": 4.0,
    "other": 0.0,
}

ATTACHMENT_PATTERN = re.compile(
    r"\.(xlsm|docm|xlsb|exe|scr|bat|cmd|ps1|js|vbs|zip|rar|7z)\b|"
    r"\b(enable macros?|macro[- ]enabled|attached (file|workbook|document))\b",
    re.IGNORECASE,
)

AMOUNT_PATTERN = re.compile(
    r"(?:naira|₦|n)\s?[0-9][0-9,]{2,}|\b[0-9][0-9,]{3,}\s*(?:naira|ngn)\b",
    re.IGNORECASE,
)

CREDENTIAL_ACTION_PATTERN = re.compile(
    r"\b(?:enter|submit|provide|send|reply with|share|confirm|upload|aika)\b[^.!?]{0,60}"
    r"\b(?:password|passcode|pin|otp|one[- ]time code|credentials?|account number|bvn|"
    r"bank details|voter id|passport number|kalmar sirri)\b",
    re.IGNORECASE,
)

BENIGN_POLICY_PATTERN = re.compile(
    r"\b(no (payment|fee) (is )?(required|needed)|is free|are free|free of charge|"
    r"ba a bukatar biya|karba kyauta)\b",
    re.IGNORECASE,
)

PHONE_PATTERN = re.compile(r"(?<!\d)(?:\+?234|0)[789][01]\d{8}(?!\d)")
EMAIL_PATTERN = re.compile(r"[a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,}", re.IGNORECASE)
OFFICIAL_EMAIL_DOMAINS = ("inec.gov.ng", "cert.gov.ng", "nccc.gov.ng")


def analyse_rules(
    *,
    text: str,
    category: str,
    channel: str,
    reported_url: str | None,
    url_result: UrlResult,
) -> RuleResult:
    """Apply structured and policy rules to the report."""

    findings: list[dict] = []
    indicators: list[Indicator] = []
    score = CATEGORY_PRIOR.get(category, 40.0)

    def add(code: str, label: str, weight: float, detail: str, severity: str = "medium") -> None:
        nonlocal score
        score += weight
        findings.append(
            {"code": code, "label": label, "weight": weight, "detail": detail}
        )
        indicators.append(
            Indicator(
                code=code,
                label=label,
                category="indicator",
                severity=severity,
                detail=detail,
            )
        )

    findings.append(
        {
            "code": "category_prior",
            "label": "Category risk prior",
            "weight": CATEGORY_PRIOR.get(category, 40.0),
            "detail": f"The report was filed as {category.replace('_', ' ')}.",
        }
    )

    channel_weight = CHANNEL_WEIGHT.get(channel, 0.0)
    if channel_weight:
        add(
            "channel_risk",
            "High-reach messaging channel",
            channel_weight,
            f"{channel.replace('_', ' ').title()} is a fast-spreading channel for electoral fraud.",
            "low",
        )

    if reported_url:
        add(
            "url_supplied",
            "Link supplied with the report",
            5,
            "The reporter supplied a destination link, which enables direct investigation.",
            "low",
        )

    amount = AMOUNT_PATTERN.search(text or "")
    if amount:
        add(
            "payment_amount",
            "Specific payment amount",
            12,
            f"The message names a payment amount: “{amount.group(0)}”.",
            "high",
        )

    attachment = ATTACHMENT_PATTERN.search(text or "")
    if attachment:
        add(
            "dangerous_attachment",
            "Attachment or macro instruction",
            14,
            f"The report references a risky file or macro: “{attachment.group(0)}”.",
            "high",
        )

    credential_action = CREDENTIAL_ACTION_PATTERN.search(text or "")
    if credential_action:
        add(
            "credential_action_pair",
            "Credential request paired with an action",
            14,
            f"The message asks the reader to act on credentials: “{credential_action.group(0)[:100]}”.",
            "high",
        )

    phone = PHONE_PATTERN.search(text or "")
    if phone:
        add(
            "phone_contact",
            "Phone number in the message",
            4,
            f"A phone contact was supplied: {phone.group(0)}.",
            "low",
        )

    emails = sorted(set(EMAIL_PATTERN.findall(text or "")))
    external_emails = [
        email
        for email in emails
        if not any(email.lower().endswith(domain) for domain in OFFICIAL_EMAIL_DOMAINS)
    ]
    if external_emails:
        add(
            "external_email",
            "Non-official email address",
            5,
            "The message references a non-official email address: " + ", ".join(external_emails[:3]) + ".",
            "medium",
        )

    if category == "impersonation" and url_result.has_url and not url_result.is_official:
        add(
            "impersonation_mismatch",
            "Impersonation plus unofficial destination",
            8,
            "The report claims authority while pointing at an unofficial destination.",
            "high",
        )

    if url_result.is_official:
        add(
            "official_destination",
            "Official destination",
            -18,
            "The supplied link is on the official-domain allowlist.",
            "info",
        )

    benign = BENIGN_POLICY_PATTERN.search(text or "")
    if benign:
        add(
            "no_fee_policy",
            "Explicit no-fee message",
            -12,
            f"The message explicitly states that no payment is required: “{benign.group(0)}”.",
            "info",
        )

    score = max(0.0, min(100.0, score))
    return RuleResult(score=round(score, 1), findings=findings, indicators=indicators)
