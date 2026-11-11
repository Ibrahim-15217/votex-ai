"""Incident, evidence and timeline schemas."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.common import ORMModel, UTCDateTime
from app.schemas.users import UserSummary

Category = Literal[
    "phishing",
    "fake_portal",
    "impersonation",
    "payment_fraud",
    "malware",
    "fake_result",
    "other",
]
Channel = Literal["email", "sms", "whatsapp", "web_form", "phone", "other"]
Priority = Literal["low", "medium", "high", "critical"]
Status = Literal[
    "submitted",
    "under_review",
    "assigned",
    "investigating",
    "escalated",
    "contained",
    "remediated",
    "recovered",
    "closed",
]
ResponseActionType = Literal[
    "warning_issued",
    "takedown_requested",
    "containment",
    "monitoring",
    "escalation",
    "other",
]


class IncidentCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=10, max_length=10_000)
    category: Category
    channel: Channel
    reported_url: str | None = Field(default=None, max_length=2048)
    state: str | None = Field(default=None, max_length=80)
    priority: Priority = "medium"

    @field_validator("reported_url")
    @classmethod
    def validate_reported_url(cls, value: str | None) -> str | None:
        if not value:
            return None
        if not value.startswith(("http://", "https://")):
            raise ValueError("The reported URL must start with http:// or https://.")
        return value


class EvidenceOut(ORMModel):
    id: str
    original_filename: str
    content_type: str
    size_bytes: int
    sha256: str
    created_at: UTCDateTime
    uploader: UserSummary


class IncidentEventOut(ORMModel):
    id: int
    event_type: str
    message: str
    metadata: dict = Field(validation_alias="event_metadata")
    created_at: UTCDateTime
    actor: UserSummary | None = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class IncidentListItem(ORMModel):
    id: str
    reference: str
    title: str
    category: str
    status: str
    priority: str
    risk_score: float | None = None
    ai_status: str
    created_at: UTCDateTime
    updated_at: UTCDateTime
    reporter: UserSummary
    assignee: UserSummary | None = None
    evidence_count: int


class AnalysisReason(BaseModel):
    component: str
    direction: str
    weight: float
    message: str


class AnalysisIndicator(BaseModel):
    code: str
    label: str
    category: str
    severity: str
    detail: str


class AnalysisFactor(BaseModel):
    key: str
    label: str
    score: float
    weight: float
    contribution: float


class IncidentAnalysisOut(ORMModel):
    id: str
    status: str
    model_version: str
    ruleset_version: str
    classification: str
    risk_score: float
    confidence: float
    url_score: float
    nlp_score: float
    ml_score: float
    indicator_score: float
    summary: str
    reasons: list[AnalysisReason] = Field(validation_alias="reasons_json")
    indicators: list[AnalysisIndicator] = Field(validation_alias="indicators_json")
    factors: list[AnalysisFactor] = Field(validation_alias="factors_json")
    features: dict = Field(validation_alias="features_json")
    warnings: list[str] = Field(validation_alias="warnings_json")
    latency_ms: int
    created_at: UTCDateTime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class IncidentDetail(IncidentListItem):
    description: str
    channel: str
    reported_url: str | None = None
    state: str | None = None
    classification: str | None = None
    closed_at: UTCDateTime | None = None
    events: list[IncidentEventOut]
    evidence: list[EvidenceOut]
    analysis: IncidentAnalysisOut | None = None


class IncidentPage(BaseModel):
    items: list[IncidentListItem]
    total: int
    page: int
    page_size: int


class AssignmentRequest(BaseModel):
    assignee_id: int


class StatusUpdateRequest(BaseModel):
    status: Status
    note: str | None = Field(default=None, max_length=1000)


class PriorityUpdateRequest(BaseModel):
    priority: Priority


class ResponseActionRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    action_type: ResponseActionType
    note: str = Field(min_length=3, max_length=2000)


class CommentRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    message: str = Field(min_length=2, max_length=4000)


class IncidentStats(BaseModel):
    """Aggregated counters for the operations overview."""

    total: int
    open: int
    critical: int
    unassigned: int
    closed: int
    last_7_days: int
    average_risk: float | None = None
    by_status: dict[str, int]
    by_priority: dict[str, int]
    by_category: dict[str, int]
