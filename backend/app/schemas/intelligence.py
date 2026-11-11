"""Indicator correlation and dashboard response schemas."""

from typing import Literal

from pydantic import BaseModel

from app.schemas.common import UTCDateTime
from app.schemas.users import OrganisationOut

IndicatorKind = Literal["url", "domain", "ipv4", "sha256", "md5"]


class IndicatorSummary(BaseModel):
    id: int
    kind: IndicatorKind
    value: str
    display_value: str
    incident_count: int
    first_seen_at: UTCDateTime
    last_seen_at: UTCDateTime
    example_incident_id: str | None = None
    example_incident_reference: str | None = None


class IndicatorPage(BaseModel):
    items: list[IndicatorSummary]
    total: int
    page: int
    page_size: int
    by_kind: dict[str, int]


class IndicatorIncidentItem(BaseModel):
    id: str
    reference: str
    title: str
    category: str
    status: str
    priority: str
    risk_score: float | None = None
    classification: str | None = None
    created_at: UTCDateTime
    assignee_name: str | None = None
    link_source: str
    first_seen_at: UTCDateTime


class IndicatorDetail(IndicatorSummary):
    incidents: list[IndicatorIncidentItem]


class SharedIndicatorRef(BaseModel):
    id: int
    kind: IndicatorKind
    value: str
    display_value: str


class RelatedIncidentItem(BaseModel):
    id: str
    reference: str
    title: str
    category: str
    status: str
    priority: str
    risk_score: float | None = None
    classification: str | None = None
    created_at: UTCDateTime
    assignee_name: str | None = None
    shared_count: int
    shared_indicators: list[SharedIndicatorRef]


class RelatedIncidentList(BaseModel):
    incident_id: str
    total: int
    items: list[RelatedIncidentItem]


class DashboardCount(BaseModel):
    key: str
    label: str
    count: int | None = None
    suppressed: bool = False


class TrendPoint(BaseModel):
    date: str
    total: int | None = None
    high_risk: int | None = None
    suppressed: bool = False


class IndicatorHighlight(BaseModel):
    id: int | None = None
    kind: IndicatorKind
    display_value: str
    incident_count: int
    organisation_count: int = 1
    suppressed: bool = False


class DashboardSummary(BaseModel):
    total: int | None = None
    open: int | None = None
    high_risk: int | None = None
    linked_incidents: int | None = None
    shared_indicators: int | None = None
    mean_risk: float | None = None
    mean_resolution_hours: float | None = None
    organisations: int | None = None
    suppressed_cells: int
    k_threshold: int


class DashboardResponse(BaseModel):
    scope: Literal["organisation", "national"]
    generated_at: UTCDateTime
    organisation: OrganisationOut | None = None
    summary: DashboardSummary
    trend: list[TrendPoint]
    severity: list[DashboardCount]
    categories: list[DashboardCount]
    channels: list[DashboardCount]
    states: list[DashboardCount]
    statuses: list[DashboardCount]
    top_indicators: list[IndicatorHighlight]
