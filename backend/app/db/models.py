"""Database models for Phase 1.

All tenant-owned records carry an explicit ``organisation_id`` so isolation can
be enforced in the query layer rather than only in the interface.
"""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.time import utcnow
from app.db.base import Base


def new_uuid() -> str:
    """Return a new opaque identifier."""

    return str(uuid4())


class Organisation(Base):
    __tablename__ = "organisations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )

    users: Mapped[list["User"]] = relationship(back_populates="organisation")
    incidents: Mapped[list["Incident"]] = relationship(back_populates="organisation")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    organisation_id: Mapped[int] = mapped_column(
        ForeignKey("organisations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(160), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="reporter")
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    organisation: Mapped[Organisation] = relationship(back_populates="users")
    reported_incidents: Mapped[list["Incident"]] = relationship(
        foreign_keys="Incident.reporter_id", back_populates="reporter"
    )
    assigned_incidents: Mapped[list["Incident"]] = relationship(
        foreign_keys="Incident.assignee_id", back_populates="assignee"
    )


class Incident(Base):
    __tablename__ = "incidents"
    __table_args__ = (
        Index("ix_incidents_org_status", "organisation_id", "status"),
        Index("ix_incidents_org_created", "organisation_id", "created_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    reference: Mapped[str] = mapped_column(String(40), unique=True, index=True, nullable=False)
    organisation_id: Mapped[int] = mapped_column(
        ForeignKey("organisations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    reporter_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), index=True, nullable=False
    )
    assignee_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True, nullable=True
    )

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(40), nullable=False)
    channel: Mapped[str] = mapped_column(String(30), nullable=False)
    reported_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    state: Mapped[str | None] = mapped_column(String(80), nullable=True)

    status: Mapped[str] = mapped_column(String(30), default="submitted", nullable=False, index=True)
    priority: Mapped[str] = mapped_column(String(20), default="medium", nullable=False)
    ai_status: Mapped[str] = mapped_column(String(30), default="pending", nullable=False)
    risk_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    classification: Mapped[str | None] = mapped_column(String(40), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    organisation: Mapped[Organisation] = relationship(back_populates="incidents")
    reporter: Mapped[User] = relationship(
        foreign_keys=[reporter_id], back_populates="reported_incidents"
    )
    assignee: Mapped[User | None] = relationship(
        foreign_keys=[assignee_id], back_populates="assigned_incidents"
    )
    events: Mapped[list["IncidentEvent"]] = relationship(
        back_populates="incident", cascade="all, delete-orphan", order_by="IncidentEvent.id"
    )
    evidence: Mapped[list["Evidence"]] = relationship(
        back_populates="incident", cascade="all, delete-orphan", order_by="Evidence.created_at"
    )
    analyses: Mapped[list["IncidentAnalysis"]] = relationship(
        back_populates="incident",
        cascade="all, delete-orphan",
        order_by="IncidentAnalysis.created_at.desc()",
    )
    indicator_links: Mapped[list["IncidentIndicator"]] = relationship(
        back_populates="incident",
        cascade="all, delete-orphan",
        order_by="IncidentIndicator.id",
    )

    @property
    def evidence_count(self) -> int:
        """Number of evidence files attached to the incident."""

        return len(self.evidence)

    @property
    def latest_analysis(self) -> "IncidentAnalysis | None":
        """Most recent stored analysis, if the incident has been analysed."""

        return self.analyses[0] if self.analyses else None

    @property
    def analysis(self) -> "IncidentAnalysis | None":
        """Alias used by the API schema for the latest analysis."""

        return self.analyses[0] if self.analyses else None


class IncidentEvent(Base):
    __tablename__ = "incident_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    incident_id: Mapped[str] = mapped_column(
        ForeignKey("incidents.id", ondelete="CASCADE"), index=True, nullable=False
    )
    actor_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True, nullable=True
    )
    event_type: Mapped[str] = mapped_column(String(40), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    event_metadata: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )

    incident: Mapped[Incident] = relationship(back_populates="events")
    actor: Mapped[User | None] = relationship()


class Evidence(Base):
    __tablename__ = "evidence"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    incident_id: Mapped[str] = mapped_column(
        ForeignKey("incidents.id", ondelete="CASCADE"), index=True, nullable=False
    )
    organisation_id: Mapped[int] = mapped_column(
        ForeignKey("organisations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    uploaded_by_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(80), nullable=False)
    content_type: Mapped[str] = mapped_column(String(120), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )

    incident: Mapped[Incident] = relationship(back_populates="evidence")
    uploader: Mapped[User] = relationship()


class IncidentAnalysis(Base):
    """One stored, explainable AI analysis run.

    Analyses are append-only history: a re-run creates a new row, so an analyst
    can compare the current verdict with an earlier one.
    """

    __tablename__ = "incident_analyses"
    __table_args__ = (
        Index("ix_incident_analyses_incident_created", "incident_id", "created_at"),
        Index("ix_incident_analyses_org_created", "organisation_id", "created_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    incident_id: Mapped[str] = mapped_column(
        ForeignKey("incidents.id", ondelete="CASCADE"), index=True, nullable=False
    )
    organisation_id: Mapped[int] = mapped_column(
        ForeignKey("organisations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    requested_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True, nullable=True
    )

    status: Mapped[str] = mapped_column(String(20), default="complete", nullable=False)
    model_version: Mapped[str] = mapped_column(String(40), nullable=False)
    ruleset_version: Mapped[str] = mapped_column(String(40), nullable=False)
    classification: Mapped[str] = mapped_column(String(30), nullable=False)
    risk_score: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    url_score: Mapped[float] = mapped_column(Float, nullable=False)
    nlp_score: Mapped[float] = mapped_column(Float, nullable=False)
    ml_score: Mapped[float] = mapped_column(Float, nullable=False)
    indicator_score: Mapped[float] = mapped_column(Float, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)

    reasons_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    indicators_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    factors_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    features_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    warnings_json: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )

    incident: Mapped[Incident] = relationship(back_populates="analyses")
    requested_by: Mapped[User | None] = relationship()


class Indicator(Base):
    """A normalised indicator of compromise owned by one organisation.

    Indicators are extracted from incident text, the reported URL and evidence
    metadata. Values are normalised so the same domain, URL, IP address or file
    hash links incidents even when the report text differs.
    """

    __tablename__ = "indicators"
    __table_args__ = (
        UniqueConstraint(
            "organisation_id", "kind", "value", name="uq_indicators_org_kind_value"
        ),
        Index("ix_indicators_org_kind", "organisation_id", "kind"),
        Index("ix_indicators_org_last_seen", "organisation_id", "last_seen_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    organisation_id: Mapped[int] = mapped_column(
        ForeignKey("organisations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    kind: Mapped[str] = mapped_column(String(20), nullable=False)
    value: Mapped[str] = mapped_column(String(2048), nullable=False)
    display_value: Mapped[str] = mapped_column(String(2048), nullable=False)

    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )

    links: Mapped[list["IncidentIndicator"]] = relationship(
        back_populates="indicator", cascade="all, delete-orphan"
    )


class IncidentIndicator(Base):
    """Join row linking one incident to one normalised indicator."""

    __tablename__ = "incident_indicators"
    __table_args__ = (
        UniqueConstraint("incident_id", "indicator_id", name="uq_incident_indicator"),
        Index("ix_incident_indicators_indicator", "indicator_id"),
        Index("ix_incident_indicators_org_incident", "organisation_id", "incident_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    incident_id: Mapped[str] = mapped_column(
        ForeignKey("incidents.id", ondelete="CASCADE"), index=True, nullable=False
    )
    indicator_id: Mapped[int] = mapped_column(
        ForeignKey("indicators.id", ondelete="CASCADE"), index=True, nullable=False
    )
    organisation_id: Mapped[int] = mapped_column(
        ForeignKey("organisations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    source: Mapped[str] = mapped_column(String(30), default="description", nullable=False)
    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )

    incident: Mapped[Incident] = relationship(back_populates="indicator_links")
    indicator: Mapped[Indicator] = relationship(back_populates="links")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    organisation_id: Mapped[int | None] = mapped_column(
        ForeignKey("organisations.id", ondelete="SET NULL"), index=True, nullable=True
    )
    actor_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True, nullable=True
    )
    action: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    resource_type: Mapped[str | None] = mapped_column(String(40), nullable=True)
    resource_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    detail_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False, index=True
    )
    prev_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    entry_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)

    actor: Mapped[User | None] = relationship()
    organisation: Mapped[Organisation | None] = relationship()

    @property
    def detail(self) -> dict:
        """Return parsed audit detail for API serialisation."""

        import json

        try:
            return json.loads(self.detail_json or "{}")
        except (TypeError, ValueError):
            return {}

    @property
    def actor_email(self) -> str | None:
        """Return the actor email when the actor still exists."""

        return self.actor.email if self.actor else None
