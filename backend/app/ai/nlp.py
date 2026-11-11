"""NLP social-engineering signals (component ``N``).

This is the interpretable linguistic layer. It recognises pressure tactics,
credential requests, payment lures, authority impersonation and reassuring
security language. It deliberately does not attempt to be a language model: every
decision maps to a phrase an analyst can read.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.ai.types import Indicator, NlpResult


@dataclass(frozen=True)
class Signal:
    code: str
    label: str
    pattern: str
    weight: int
    severity: str
    detail: str


POSITIVE_SIGNALS: tuple[Signal, ...] = (
    Signal(
        "urgency_pressure",
        "Urgency or deadline pressure",
        r"\b(urgent(ly)?|immediately|right now|act now|final notice|last chance|"
        r"within \d+\s*(hours?|hrs?|minutes?|days?)|before (midnight|today|tomorrow)|"
        r"expires? (today|soon)|closes? (today|tonight)|cikin sa'?o'?i|nan take|kafin gobe|yau)\b",
        14,
        "high",
        "The message imposes a short deadline or urgent action.",
    ),
    Signal(
        "credential_request",
        "Request for credentials",
        r"\b(password|passcode|pin\b|otp\b|one[- ]time (code|password)|"
        r"login (details|credentials)|sign in with|re-?authenticate|"
        r"submit (your )?(username|password|credentials)|confirm your (password|pin|otp)|"
        r"kalmar sirri|shiga da (imel|kalmar))\b",
        20,
        "high",
        "The message asks for a password, PIN, OTP or login credential.",
    ),
    Signal(
        "sensitive_identity",
        "Request for sensitive identity data",
        r"\b(bvn|bank verification number|nin\b|national identification number|"
        r"date of birth|passport (number|photograph)|account number|bank details|"
        r"voter identification number|voter id|selfie|biometric)\b",
        16,
        "high",
        "The message asks for identity or banking data that electoral staff should never share.",
    ),
    Signal(
        "payment_demand",
        "Payment or fee request",
        r"\b(pay (a |the )?(processing |release |logistics |service |verification )?fee|"
        r"processing fee|release fee|logistics fee|service charge|"
        r"transfer (the )?(sum|amount|money)|remit|send (the )?(payment|receipt|money)|"
        r"naira\s?[0-9,]+|n[0-9][0-9,]{2,}|₦\s?[0-9,]+|biya\b|kudin)\b",
        18,
        "high",
        "The message asks the recipient to pay a fee or transfer money.",
    ),
    Signal(
        "threat_consequence",
        "Threat of loss or sanction",
        r"\b(suspend(ed|sion)?|cancel(led|lation)?|removed? from|deleted?|locked?|blocked?|"
        r"disqualif(y|ied)|forfeit|legal action|penalty|arrest|prosecut|"
        r"cire ku|rushe|asara|an cire)\b",
        12,
        "high",
        "The message threatens suspension, removal, loss or sanction.",
    ),
    Signal(
        "authority_claim",
        "Authority or insider claim",
        r"\b(chairman|commission(er)?|security (aide|unit|desk)|ict (desk|support|team|officer)|"
        r"supervisor|director|national situation room|returning officer|"
        r"sashen ict|shugaban gudanarwa|jami'in)\b",
        8,
        "medium",
        "The message claims authority or insider access.",
    ),
    Signal(
        "secrecy_pressure",
        "Secrecy or private-channel instruction",
        r"\b(do not (tell|share|use the public|use the official)|keep this (confidential|between us)|"
        r"private number|reply directly|between us|do not use the (official|public)|"
        r"kada ku (fada|gaya))\b",
        14,
        "high",
        "The message asks the recipient to bypass normal reporting channels.",
    ),
    Signal(
        "attachment_lure",
        "Attachment, macro or executable lure",
        r"\b(attached|attachment|enable macros?|macro|\.xlsm|\.docm|\.exe|\.scr|\.zip|"
        r"run (the )?(file|executable|program)|install (it )?(immediately|now)|"
        r"password[- ]protected (file|workbook)|kunna macro|sauke (fayil|kayan aiki))\b",
        16,
        "high",
        "The message asks the recipient to open an attachment, enable macros or run a file.",
    ),
    Signal(
        "result_manipulation",
        "Early, leaked or altered results",
        r"\b(leaked|early results|pre-?loaded|altered|doctored|"
        r"before the official announcement|circulate|forward immediately|share widely|"
        r"result(s)? (have been|were) (released|altered))\b",
        12,
        "high",
        "The message promotes early, leaked or altered results.",
    ),
    Signal(
        "reward_lure",
        "Reward, selection or entitlement lure",
        r"\b(congratulations|you (have been|are) (selected|shortlisted)|entitled|"
        r"reward|allowance|prize|exclusive opportunity|special (assignment|accreditation))\b",
        8,
        "medium",
        "The message uses a reward, selection or entitlement to attract the reader.",
    ),
    Signal(
        "registration_threat",
        "Registration or access loss threat",
        r"\b(removed from (the )?(register|supplementary register|deployment)|"
        r"registration will be (cancelled|removed)|lose (your )?(access|place|accreditation)|"
        r"could not be matched|flagged during duplicate checks)\b",
        14,
        "high",
        "The message threatens loss of registration, deployment or system access.",
    ),
    Signal(
        "call_to_action",
        "Call to confirm, validate or submit",
        r"\b(confirm your|validate your|verify your|update your|complete the|submit your|"
        r"re-?enter your|log in (with|at)|sign in (with|at)|download (and|the))\b",
        6,
        "low",
        "The message pushes the reader to confirm, validate or submit information.",
    ),
    Signal(
        "account_pressure",
        "Account or session problem claim",
        r"\b(account (session )?(expired|suspended|flagged|locked)|"
        r"security (update|patch|check)|mandatory (update|verification)|"
        r"re-?verify your account|restore (your )?access)\b",
        10,
        "medium",
        "The message claims an account or session problem that needs immediate action.",
    ),
)

NEGATIVE_SIGNALS: tuple[Signal, ...] = (
    Signal(
        "anti_fraud_disclaimer",
        "Security disclaimer",
        r"\b(never (ask|request|share)|will not ask|will never ask|do not (share|pay|send|enable)|"
        r"don'?t (share|pay|send)|not share (your )?credentials|"
        r"no (payment|fee) (is )?(required|needed)|free of charge|is free|are free|"
        r"report (any|suspicious|it|the (email|message))|"
        r"verify (it )?with your supervisor|kada ku (biya|kunna|bayar)|kyauta|ba a bukatar biya)\b",
        -20,
        "info",
        "The message warns against sharing credentials or paying fees.",
    ),
    Signal(
        "official_channel",
        "Official-channel guidance",
        r"\b(official (portal|domain|channel|notice|website|procedure|hotline)|"
        r"published government domain|announced only by|returning officer|"
        r"through your supervisor|local government office)\b",
        -8,
        "info",
        "The message points to an official channel or procedure.",
    ),
    Signal(
        "routine_administration",
        "Routine administration",
        r"\b(routine|meeting|briefing|training|refresher|holiday|office hours|"
        r"agenda|schedule|timetable|attendance (will be|is) recorded|"
        r"bring your (accreditation )?(badge|staff )?identification|arrive \d+ minutes early)\b",
        -6,
        "info",
        "The message describes ordinary administrative activity.",
    ),
    Signal(
        "security_notification",
        "Routine security notification",
        r"\b(password reset request was received|no password was changed|"
        r"for your security|if you did not (request|make) this|"
        r"audit log records|use your own account)\b",
        -14,
        "info",
        "The message is a routine security notification rather than a request.",
    ),
)

ALL_SIGNALS = POSITIVE_SIGNALS + NEGATIVE_SIGNALS


def analyse_text(text: str) -> NlpResult:
    """Score the narrative for social-engineering language."""

    haystack = (text or "").lower()
    findings: list[dict] = []
    indicators: list[Indicator] = []
    total = 12

    for signal in ALL_SIGNALS:
        match = re.search(signal.pattern, haystack, re.IGNORECASE)
        if not match:
            continue
        snippet = match.group(0).strip()
        total += signal.weight
        findings.append(
            {
                "code": signal.code,
                "label": signal.label,
                "weight": signal.weight,
                "detail": signal.detail,
                "snippet": snippet[:120],
            }
        )
        indicators.append(
            Indicator(
                code=signal.code,
                label=signal.label,
                category="content",
                severity=signal.severity,
                detail=f"{signal.detail} Matched: “{snippet[:80]}”.",
            )
        )

    score = max(0.0, min(100.0, float(total)))
    return NlpResult(score=round(score, 1), findings=findings, indicators=indicators)
