"""Weighted, explainable risk engine.

``R = 0.30U + 0.25N + 0.25M + 0.20I``

The score supports a human analyst. It is not evidence that an attack occurred,
and the interface always keeps the underlying component scores visible.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from app.ai import ml, nlp, rules, url as url_module
from app.ai.types import Indicator

WEIGHTS = {"U": 0.30, "N": 0.25, "M": 0.25, "I": 0.20}
COMPONENT_LABELS = {
    "U": "URL & domain",
    "N": "Language signals",
    "M": "ML classifier",
    "I": "Indicators & rules",
}
RULESET_VERSION = "electoral-rules-v1"
HIGH_RISK_THRESHOLD = 65.0
SUSPICIOUS_THRESHOLD = 35.0
SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2, "info": 3}


@dataclass
class AnalysisResult:
    risk_score: float
    classification: str
    confidence: float
    summary: str
    url_score: float
    nlp_score: float
    ml_score: float
    indicator_score: float
    reasons: list[dict] = field(default_factory=list)
    indicators: list[dict] = field(default_factory=list)
    factors: list[dict] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    model_version: str = ""
    ruleset_version: str = RULESET_VERSION
    features: dict = field(default_factory=dict)
    model_available: bool = True


def _band(score: float) -> str:
    if score >= HIGH_RISK_THRESHOLD:
        return "high_risk"
    if score >= SUSPICIOUS_THRESHOLD:
        return "suspicious"
    return "benign"


def _confidence(components: list[float], risk: float, model_available: bool) -> float:
    mean = sum(components) / len(components)
    spread = math.sqrt(sum((value - mean) ** 2 for value in components) / len(components))
    agreement = max(0.0, 1.0 - spread / 45.0)
    distance = min(1.0, abs(risk - 50.0) / 50.0)
    confidence = 0.5 + 0.25 * distance + 0.25 * agreement
    if not model_available:
        confidence -= 0.10
    return round(min(0.98, max(0.5, confidence)), 2)


def _component_message(component: str, score: float, findings: list[dict]) -> str:
    labels = [item["label"] for item in findings if item.get("weight", 0) > 0][:2]
    label = COMPONENT_LABELS.get(component, component)
    if labels:
        return f"{label} scored {score:.0f}/100. Top signals: {', '.join(labels).lower()}."
    if score >= 50:
        return f"{label} scored {score:.0f}/100 from structural features."
    return f"{label} scored {score:.0f}/100 with no strong negative signal."


def _dedupe_indicators(items: list[Indicator]) -> list[dict]:
    seen: set[str] = set()
    unique: list[Indicator] = []
    for item in items:
        if item.code in seen:
            continue
        seen.add(item.code)
        unique.append(item)
    unique.sort(key=lambda item: (SEVERITY_ORDER.get(item.severity, 9), item.category, item.code))
    return [item.to_dict() for item in unique]


def _summary(classification: str, reasons: list[dict], warnings: list[str]) -> str:
    top = [reason["message"] for reason in reasons if reason["direction"] == "increases_risk"][:2]
    if classification == "high_risk":
        lead = "High-risk pattern consistent with an electoral phishing or impersonation attempt."
    elif classification == "suspicious":
        lead = "Suspicious pattern that an analyst should review before closing."
    else:
        lead = "No strong phishing pattern detected; keep open only if new evidence appears."
    if top:
        return f"{lead} {' '.join(top)}"
    if warnings:
        return f"{lead} {warnings[0]}"
    return lead


def analyse_incident(
    *,
    title: str,
    description: str,
    category: str,
    channel: str,
    reported_url: str | None,
    state: str | None = None,
) -> AnalysisResult:
    """Run all four components and combine them into one explainable result."""

    text = f"{title}. {description}".strip()

    url_result = url_module.analyse_url(text, reported_url)
    nlp_result = nlp.analyse_text(text)
    ml_result = ml.predict(text, reported_url)
    rule_result = rules.analyse_rules(
        text=text,
        category=category,
        channel=channel,
        reported_url=reported_url,
        url_result=url_result,
    )

    components = {
        "U": url_result.score,
        "N": nlp_result.score,
        "M": ml_result.score,
        "I": rule_result.score,
    }

    risk = round(
        sum(WEIGHTS[key] * components[key] for key in WEIGHTS),
        1,
    )
    classification = _band(risk)
    confidence = _confidence(list(components.values()), risk, ml_result.available)

    warnings: list[str] = []
    if not url_result.has_url:
        warnings.append("No URL was supplied, so URL and domain intelligence is neutral.")
    if not ml_result.available and ml_result.warning:
        warnings.append(ml_result.warning)
    if len(text) < 40:
        warnings.append("The report is very short, which limits language analysis.")

    component_findings = {
        "U": url_result.findings,
        "N": nlp_result.findings,
        "M": [],
        "I": rule_result.findings,
    }

    reasons: list[dict] = []
    for key in ("U", "N", "M", "I"):
        score = components[key]
        contribution = WEIGHTS[key] * score
        if key == "M":
            message = (
                f"ML classifier scored {score:.0f}/100 "
                f"(phishing probability {ml_result.probability:.2f})."
            )
            if not ml_result.available:
                message = "ML classifier is unavailable; a neutral 50/100 was used."
        else:
            message = _component_message(key, score, component_findings[key])
        reasons.append(
            {
                "component": key,
                "direction": "increases_risk" if score >= 50 else "decreases_risk",
                "weight": round(contribution, 2),
                "message": message,
            }
        )

    # Add the strongest individual findings so the panel is not only four bars.
    detail_candidates: list[dict] = []
    for key in ("N", "I", "U"):
        for finding in component_findings[key]:
            if finding.get("weight", 0) <= 0:
                continue
            detail_candidates.append({"component": key, **finding})
    detail_candidates.sort(key=lambda item: item.get("weight", 0), reverse=True)
    for finding in detail_candidates[:4]:
        reasons.append(
            {
                "component": finding["component"],
                "direction": "increases_risk",
                "weight": round(float(finding.get("weight", 0)), 2),
                "message": finding["detail"],
            }
        )
    for finding in sorted(
        [item for item in component_findings["N"] + component_findings["I"] if item.get("weight", 0) < 0],
        key=lambda item: item.get("weight", 0),
    )[:2]:
        reasons.append(
            {
                "component": "N" if finding in component_findings["N"] else "I",
                "direction": "decreases_risk",
                "weight": round(float(finding.get("weight", 0)), 2),
                "message": finding["detail"],
            }
        )

    factors = [
        {
            "key": key,
            "label": COMPONENT_LABELS[key],
            "score": round(components[key], 1),
            "weight": WEIGHTS[key],
            "contribution": round(WEIGHTS[key] * components[key], 2),
        }
        for key in ("U", "N", "M", "I")
    ]

    indicators = _dedupe_indicators(
        [*url_result.indicators, *nlp_result.indicators, *rule_result.indicators]
    )

    return AnalysisResult(
        risk_score=risk,
        classification=classification,
        confidence=confidence,
        summary=_summary(classification, reasons, warnings),
        url_score=round(components["U"], 1),
        nlp_score=round(components["N"], 1),
        ml_score=round(components["M"], 1),
        indicator_score=round(components["I"], 1),
        reasons=reasons,
        indicators=indicators,
        factors=factors,
        warnings=warnings,
        model_version=ml_result.model_version,
        ruleset_version=RULESET_VERSION,
        features={
            "text_length": len(text),
            "has_url": url_result.has_url,
            "url_host": url_result.host,
            "official_host": url_result.is_official,
            "ml_probability": ml_result.probability,
            "model_available": ml_result.available,
            "category": category,
            "channel": channel,
            "state": state,
        },
        model_available=ml_result.available,
    )
