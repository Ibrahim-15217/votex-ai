"""Shared value objects for the hybrid analyser."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Indicator:
    """A concrete signal extracted from the report."""

    code: str
    label: str
    category: str
    severity: str
    detail: str

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "label": self.label,
            "category": self.category,
            "severity": self.severity,
            "detail": self.detail,
        }


@dataclass(frozen=True)
class Reason:
    """A plain-language explanation of one contribution to the score."""

    component: str
    direction: str
    weight: float
    message: str

    def to_dict(self) -> dict:
        return {
            "component": self.component,
            "direction": self.direction,
            "weight": round(float(self.weight), 3),
            "message": self.message,
        }


@dataclass
class UrlResult:
    score: float
    findings: list[dict] = field(default_factory=list)
    indicators: list[Indicator] = field(default_factory=list)
    host: str | None = None
    is_official: bool = False
    has_url: bool = False


@dataclass
class NlpResult:
    score: float
    findings: list[dict] = field(default_factory=list)
    indicators: list[Indicator] = field(default_factory=list)


@dataclass
class MlResult:
    score: float
    probability: float
    model_version: str
    available: bool = True
    warning: str | None = None


@dataclass
class RuleResult:
    score: float
    findings: list[dict] = field(default_factory=list)
    indicators: list[Indicator] = field(default_factory=list)
