"""Indicator correlation, related-incident lookup and privacy-safe dashboards.

Correlation is deliberately deterministic and local: indicators are extracted
from text, the reported URL and evidence metadata, normalised, then linked only
inside the same organisation. The national dashboard exposes aggregate counts
only and applies k-anonymity suppression (k >= 5) in this query layer, never in
the browser.
"""

from __future__ import annotations

import csv
import io
import logging
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.ai.iocs import extract_iocs
from app.core.config import settings
from app.core.time import utcnow
from app.db.models import (
    Incident,
    IncidentEvent,
    IncidentIndicator,
    Indicator,
    User,
)
from app.services.audit import record_audit

logger = logging.getLogger(__name__)

K_THRESHOLD = 5
TREND_DAYS = 30
TOP_INDICATORS = 8
TEXT_CONTENT_TYPES = {"text/plain", "message/rfc822"}
MAX_EVIDENCE_SCAN_BYTES = 512 * 1024

CATEGORY_LABELS = {
    "phishing": "Phishing",
    "fake_portal": "Fake portal",
    "impersonation": "Impersonation",
    "payment_fraud": "Payment fraud",
    "malware": "Malware",
    "fake_result": "False result claim",
    "other": "Other",
}
CHANNEL_LABELS = {
    "email": "Email",
    "sms": "SMS",
    "whatsapp": "WhatsApp",
    "web_form": "Web form",
    "phone": "Phone",
    "other": "Other",
}
STATUS_LABELS = {
    "submitted": "Submitted",
    "under_review": "Under review",
    "assigned": "Assigned",
    "investigating": "Investigating",
    "escalated": "Escalated",
    "contained": "Contained",
    "remediated": "Remediated",
    "recovered": "Recovered",
    "closed": "Closed",
}
SEVERITY_LABELS = {
    "benign": "Benign",
    "suspicious": "Suspicious",
    "high_risk": "High risk",
    "unclassified": "Unclassified",
}
KIND_LABELS = {
    "url": "URL",
    "domain": "domain",
    "ipv4": "IPv4",
    "sha256": "SHA-256",
    "md5": "MD5",
}
SEVERITY_ORDER = ("high_risk", "suspicious", "benign", "unclassified")
STATUS_ORDER = tuple(STATUS_LABELS)
CATEGORY_ORDER = tuple(CATEGORY_LABELS)
CHANNEL_ORDER = tuple(CHANNEL_LABELS)


def _as_utc(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _read_evidence_texts(incident: Incident) -> tuple[str, ...]:
    """Read small text/EML evidence files for local IOC extraction only."""

    base = Path(settings.evidence_dir).resolve()
    texts: list[str] = []
    for item in incident.evidence:
        if item.content_type not in TEXT_CONTENT_TYPES:
            continue
        if item.size_bytes > MAX_EVIDENCE_SCAN_BYTES:
            continue
        target = (base / incident.id / item.stored_filename).resolve()
        if base not in target.parents:
            continue
        try:
            texts.append(target.read_text(encoding="utf-8", errors="ignore"))
        except OSError:
            logger.warning("Could not scan evidence %s for indicators", item.id)
    return tuple(texts)


def sync_incident_indicators(
    db: Session,
    incident: Incident,
    actor: User | None = None,
    *,
    commit: bool = True,
) -> int:
    """Extract and link indicators for one incident. Idempotent."""

    evidence_hashes = tuple(item.sha256 for item in incident.evidence)
    extracted = extract_iocs(
        text=f"{incident.title}. {incident.description}",
        reported_url=incident.reported_url,
        evidence_hashes=evidence_hashes,
        evidence_texts=_read_evidence_texts(incident),
    )
    if not extracted:
        if commit:
            db.commit()
        return 0

    existing_rows = db.execute(
        select(Indicator.kind, Indicator.value)
        .join(IncidentIndicator, IncidentIndicator.indicator_id == Indicator.id)
        .where(IncidentIndicator.incident_id == incident.id)
    ).all()
    existing = {(row.kind, row.value) for row in existing_rows}

    seen_at = _as_utc(incident.created_at) or utcnow()
    new_links = 0
    for item in extracted:
        if (item.kind, item.value) in existing:
            continue

        indicator = db.scalar(
            select(Indicator).where(
                Indicator.organisation_id == incident.organisation_id,
                Indicator.kind == item.kind,
                Indicator.value == item.value,
            )
        )
        if indicator is None:
            indicator = Indicator(
                organisation_id=incident.organisation_id,
                kind=item.kind,
                value=item.value,
                display_value=item.display_value,
                first_seen_at=seen_at,
                last_seen_at=seen_at,
            )
            db.add(indicator)
            db.flush()
        elif seen_at > (_as_utc(indicator.last_seen_at) or seen_at):
            indicator.last_seen_at = seen_at

        db.add(
            IncidentIndicator(
                incident_id=incident.id,
                indicator_id=indicator.id,
                organisation_id=incident.organisation_id,
                source=item.source,
                first_seen_at=seen_at,
            )
        )
        existing.add((item.kind, item.value))
        new_links += 1

    if new_links:
        kinds = Counter(item.kind for item in extracted)
        kind_summary = ", ".join(
            f"{count} {KIND_LABELS.get(kind, kind)}" for kind, count in kinds.items()
        )
        plural = "" if new_links == 1 else "s"
        db.add(
            IncidentEvent(
                incident_id=incident.id,
                actor_id=actor.id if actor else None,
                event_type="indicators_linked",
                message=f"Correlation linked {new_links} indicator{plural}: {kind_summary}.",
                event_metadata={
                    "indicator_count": new_links,
                    "kinds": dict(kinds),
                    "automatic": True,
                },
                created_at=utcnow(),
            )
        )
        record_audit(
            db,
            action="incident.indicators_linked",
            actor_id=actor.id if actor else None,
            organisation_id=incident.organisation_id,
            resource_type="incident",
            resource_id=incident.id,
            detail={
                "reference": incident.reference,
                "indicator_count": new_links,
                "kinds": dict(kinds),
            },
        )

    if commit:
        db.commit()
    return new_links


def backfill_indicators(db: Session) -> int:
    """Link indicators for every incident that has none yet.

    Safe to call on every start. Returns the number of incidents that gained at
    least one new indicator link.
    """

    incidents = list(
        db.scalars(select(Incident).options(selectinload(Incident.evidence))).all()
    )
    linked = 0
    for incident in incidents:
        try:
            actor = db.get(User, incident.reporter_id)
            if sync_incident_indicators(db, incident, actor, commit=True):
                linked += 1
        except Exception:
            db.rollback()
            logger.exception("Indicator backfill failed for incident %s", incident.id)
    return linked


def _indicator_summary(indicator: Indicator, incident_count: int, example: tuple[str, str] | None) -> dict:
    return {
        "id": indicator.id,
        "kind": indicator.kind,
        "value": indicator.value,
        "display_value": indicator.display_value,
        "incident_count": incident_count,
        "first_seen_at": indicator.first_seen_at,
        "last_seen_at": indicator.last_seen_at,
        "example_incident_id": example[0] if example else None,
        "example_incident_reference": example[1] if example else None,
    }


def _example_incidents(db: Session, indicator_ids: list[int]) -> dict[int, tuple[str, str]]:
    if not indicator_ids:
        return {}
    rows = db.execute(
        select(IncidentIndicator.indicator_id, Incident.id, Incident.reference)
        .join(Incident, Incident.id == IncidentIndicator.incident_id)
        .where(IncidentIndicator.indicator_id.in_(indicator_ids))
        .order_by(IncidentIndicator.id)
    ).all()
    examples: dict[int, tuple[str, str]] = {}
    for indicator_id, incident_id, reference in rows:
        examples.setdefault(indicator_id, (incident_id, reference))
    return examples


def indicator_page(
    db: Session,
    user: User,
    *,
    query: str | None = None,
    kind: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    """Search the caller's organisation indicators, busiest first."""

    base_conditions = [Indicator.organisation_id == user.organisation_id]
    conditions = list(base_conditions)
    if kind:
        conditions.append(Indicator.kind == kind)
    if query:
        conditions.append(Indicator.value.ilike(f"%{query.strip()}%"))

    count_subquery = (
        select(
            IncidentIndicator.indicator_id.label("indicator_id"),
            func.count(IncidentIndicator.incident_id).label("incident_count"),
        )
        .group_by(IncidentIndicator.indicator_id)
        .subquery()
    )
    count_expression = func.coalesce(count_subquery.c.incident_count, 0)

    total = db.scalar(select(func.count()).select_from(Indicator).where(*conditions)) or 0
    rows = db.execute(
        select(Indicator, count_expression.label("incident_count"))
        .outerjoin(count_subquery, count_subquery.c.indicator_id == Indicator.id)
        .where(*conditions)
        .order_by(count_expression.desc(), Indicator.last_seen_at.desc(), Indicator.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    by_kind_rows = db.execute(
        select(Indicator.kind, func.count())
        .where(*base_conditions)
        .group_by(Indicator.kind)
    ).all()
    by_kind = {kind_value: count for kind_value, count in by_kind_rows}

    examples = _example_incidents(db, [indicator.id for indicator, _ in rows])
    items = [
        _indicator_summary(indicator, int(incident_count), examples.get(indicator.id))
        for indicator, incident_count in rows
    ]
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "by_kind": by_kind,
    }


def indicator_detail(db: Session, user: User, indicator_id: int) -> dict | None:
    """Return one indicator and the visible incidents linked to it."""

    indicator = db.scalar(
        select(Indicator).where(
            Indicator.id == indicator_id,
            Indicator.organisation_id == user.organisation_id,
        )
    )
    if indicator is None:
        return None

    conditions = [
        IncidentIndicator.indicator_id == indicator.id,
        Incident.organisation_id == user.organisation_id,
    ]
    if user.role == "reporter":
        conditions.append(Incident.reporter_id == user.id)

    rows = db.execute(
        select(Incident, IncidentIndicator.source, IncidentIndicator.first_seen_at)
        .join(IncidentIndicator, IncidentIndicator.incident_id == Incident.id)
        .options(selectinload(Incident.assignee))
        .where(*conditions)
        .order_by(Incident.created_at.desc())
        .limit(50)
    ).all()

    incidents = [
        {
            "id": incident.id,
            "reference": incident.reference,
            "title": incident.title,
            "category": incident.category,
            "status": incident.status,
            "priority": incident.priority,
            "risk_score": incident.risk_score,
            "classification": incident.classification,
            "created_at": incident.created_at,
            "assignee_name": incident.assignee.full_name if incident.assignee else None,
            "link_source": source,
            "first_seen_at": first_seen_at,
        }
        for incident, source, first_seen_at in rows
    ]
    summary = _indicator_summary(indicator, len(incidents), None)
    summary["incidents"] = incidents
    return summary


def related_incidents(db: Session, user: User, incident: Incident, limit: int = 8) -> dict:
    """Find visible incidents in the same tenant sharing at least one indicator."""

    indicator_ids = list(
        db.scalars(
            select(IncidentIndicator.indicator_id).where(
                IncidentIndicator.incident_id == incident.id
            )
        ).all()
    )
    if not indicator_ids:
        return {"incident_id": incident.id, "total": 0, "items": []}

    conditions = [
        Incident.organisation_id == user.organisation_id,
        Incident.id != incident.id,
        IncidentIndicator.indicator_id.in_(indicator_ids),
    ]
    if user.role == "reporter":
        conditions.append(Incident.reporter_id == user.id)

    shared_count = func.count(IncidentIndicator.indicator_id).label("shared_count")
    rows = db.execute(
        select(Incident, shared_count)
        .join(IncidentIndicator, IncidentIndicator.incident_id == Incident.id)
        .options(selectinload(Incident.assignee))
        .where(*conditions)
        .group_by(Incident.id)
        .order_by(shared_count.desc(), Incident.risk_score.desc(), Incident.created_at.desc())
        .limit(limit)
    ).all()
    if not rows:
        return {"incident_id": incident.id, "total": 0, "items": []}

    related_ids = [related.id for related, _ in rows]
    link_rows = db.execute(
        select(IncidentIndicator.incident_id, Indicator)
        .join(Indicator, Indicator.id == IncidentIndicator.indicator_id)
        .where(
            IncidentIndicator.incident_id.in_(related_ids),
            IncidentIndicator.indicator_id.in_(indicator_ids),
        )
        .order_by(Indicator.kind, Indicator.value)
    ).all()
    indicators_by_incident: dict[str, list[dict]] = {}
    for incident_id, indicator in link_rows:
        indicators_by_incident.setdefault(incident_id, []).append(
            {
                "id": indicator.id,
                "kind": indicator.kind,
                "value": indicator.value,
                "display_value": indicator.display_value,
            }
        )

    items = [
        {
            "id": related.id,
            "reference": related.reference,
            "title": related.title,
            "category": related.category,
            "status": related.status,
            "priority": related.priority,
            "risk_score": related.risk_score,
            "classification": related.classification,
            "created_at": related.created_at,
            "assignee_name": related.assignee.full_name if related.assignee else None,
            "shared_count": int(count),
            "shared_indicators": indicators_by_incident.get(related.id, []),
        }
        for related, count in rows
    ]
    return {"incident_id": incident.id, "total": len(items), "items": items}


def _severity_for(score: float | None) -> str:
    if score is None:
        return "unclassified"
    if score >= 65:
        return "high_risk"
    if score >= 35:
        return "suspicious"
    return "benign"


def _suppressed(value: int, *, enabled: bool) -> tuple[int | None, bool]:
    if enabled and 0 < value < K_THRESHOLD:
        return None, True
    return value, False


def _count_cell(key: str, label: str, count: int, *, suppress: bool) -> tuple[dict, int]:
    value, hidden = _suppressed(count, enabled=suppress)
    return (
        {"key": key, "label": label, "count": value, "suppressed": hidden},
        1 if hidden else 0,
    )


def _dashboard_data(db: Session, user: User, *, national: bool) -> dict:
    suppress = national
    scope_conditions = [] if national else [Incident.organisation_id == user.organisation_id]
    indicator_scope = [] if national else [Indicator.organisation_id == user.organisation_id]

    link_counts = (
        select(
            IncidentIndicator.incident_id.label("incident_id"),
            func.count(IncidentIndicator.indicator_id).label("indicator_count"),
        )
        .group_by(IncidentIndicator.incident_id)
        .subquery()
    )
    rows = db.execute(
        select(Incident, func.coalesce(link_counts.c.indicator_count, 0))
        .outerjoin(link_counts, link_counts.c.incident_id == Incident.id)
        .where(*scope_conditions)
        .order_by(Incident.created_at.desc())
    ).all()

    now = utcnow()
    today = now.date()
    trend_dates = [today - timedelta(days=offset) for offset in range(TREND_DAYS - 1, -1, -1)]
    trend_totals: Counter[date] = Counter()
    trend_high: Counter[date] = Counter()

    categories: Counter[str] = Counter()
    channels: Counter[str] = Counter()
    states: Counter[str] = Counter()
    statuses: Counter[str] = Counter()
    severities: Counter[str] = Counter()

    open_count = 0
    high_risk_open = 0
    linked_incidents = 0
    risks: list[float] = []
    resolutions: list[float] = []
    organisation_ids: set[int] = set()

    for incident, indicator_count in rows:
        statuses[incident.status] += 1
        categories[incident.category] += 1
        channels[incident.channel] += 1
        states[incident.state or "Not specified"] += 1
        severities[_severity_for(incident.risk_score)] += 1
        organisation_ids.add(incident.organisation_id)

        if incident.status != "closed":
            open_count += 1
            if incident.risk_score is not None and incident.risk_score >= 65:
                high_risk_open += 1
        if indicator_count:
            linked_incidents += 1
        if incident.risk_score is not None:
            risks.append(float(incident.risk_score))
        if incident.closed_at is not None:
            created = _as_utc(incident.created_at)
            closed = _as_utc(incident.closed_at)
            if created and closed and closed >= created:
                resolutions.append((closed - created).total_seconds() / 3600)

        created_date = (_as_utc(incident.created_at) or now).date()
        if created_date >= trend_dates[0]:
            trend_totals[created_date] += 1
            if incident.risk_score is not None and incident.risk_score >= 65:
                trend_high[created_date] += 1

    suppressed_cells = 0
    trend: list[dict] = []
    for day in trend_dates:
        total_value, total_hidden = _suppressed(trend_totals.get(day, 0), enabled=suppress)
        risk_value, risk_hidden = _suppressed(trend_high.get(day, 0), enabled=suppress)
        if total_hidden:
            suppressed_cells += 1
        if risk_hidden:
            suppressed_cells += 1
        trend.append(
            {
                "date": day.isoformat(),
                "total": total_value,
                "high_risk": risk_value,
                "suppressed": total_hidden or risk_hidden,
            }
        )

    severity_items: list[dict] = []
    for key in SEVERITY_ORDER:
        cell, hidden = _count_cell(key, SEVERITY_LABELS[key], severities.get(key, 0), suppress=suppress)
        severity_items.append(cell)
        suppressed_cells += hidden

    category_items: list[dict] = []
    for key in CATEGORY_ORDER:
        cell, hidden = _count_cell(key, CATEGORY_LABELS[key], categories.get(key, 0), suppress=suppress)
        category_items.append(cell)
        suppressed_cells += hidden

    channel_items: list[dict] = []
    for key in CHANNEL_ORDER:
        cell, hidden = _count_cell(key, CHANNEL_LABELS[key], channels.get(key, 0), suppress=suppress)
        channel_items.append(cell)
        suppressed_cells += hidden

    state_items: list[dict] = []
    for key, count in sorted(states.items(), key=lambda item: (-item[1], item[0]))[:12]:
        cell, hidden = _count_cell(key, key, count, suppress=suppress)
        state_items.append(cell)
        suppressed_cells += hidden

    status_items: list[dict] = []
    for key in STATUS_ORDER:
        cell, hidden = _count_cell(key, STATUS_LABELS[key], statuses.get(key, 0), suppress=suppress)
        status_items.append(cell)
        suppressed_cells += hidden

    if national:
        indicator_rows = db.execute(
            select(
                Indicator.kind,
                Indicator.value,
                func.max(Indicator.display_value),
                func.count(IncidentIndicator.incident_id).label("incident_count"),
                func.count(func.distinct(IncidentIndicator.organisation_id)).label("org_count"),
            )
            .join(IncidentIndicator, IncidentIndicator.indicator_id == Indicator.id)
            .where(*indicator_scope)
            .group_by(Indicator.kind, Indicator.value)
            .having(func.count(IncidentIndicator.incident_id) >= K_THRESHOLD)
            .order_by(func.count(IncidentIndicator.incident_id).desc(), Indicator.value)
            .limit(TOP_INDICATORS)
        ).all()
        top_indicators = [
            {
                "id": None,
                "kind": kind,
                "display_value": display,
                "incident_count": int(count),
                "organisation_count": int(org_count),
                "suppressed": False,
            }
            for kind, _value, display, count, org_count in indicator_rows
        ]
        shared_indicator_count = db.scalar(
            select(func.count())
            .select_from(
                select(Indicator.kind, Indicator.value)
                .join(IncidentIndicator, IncidentIndicator.indicator_id == Indicator.id)
                .where(*indicator_scope)
                .group_by(Indicator.kind, Indicator.value)
                .having(func.count(IncidentIndicator.incident_id) >= 2)
                .subquery()
            )
        ) or 0
    else:
        indicator_rows = db.execute(
            select(
                Indicator,
                func.count(IncidentIndicator.incident_id).label("incident_count"),
            )
            .join(IncidentIndicator, IncidentIndicator.indicator_id == Indicator.id)
            .where(*indicator_scope)
            .group_by(Indicator.id)
            .having(func.count(IncidentIndicator.incident_id) >= 2)
            .order_by(func.count(IncidentIndicator.incident_id).desc(), Indicator.value)
            .limit(TOP_INDICATORS)
        ).all()
        top_indicators = [
            {
                "id": indicator.id,
                "kind": indicator.kind,
                "display_value": indicator.display_value,
                "incident_count": int(count),
                "organisation_count": 1,
                "suppressed": False,
            }
            for indicator, count in indicator_rows
        ]
        shared_indicator_count = db.scalar(
            select(func.count())
            .select_from(
                select(Indicator.id)
                .join(IncidentIndicator, IncidentIndicator.indicator_id == Indicator.id)
                .where(*indicator_scope)
                .group_by(Indicator.id)
                .having(func.count(IncidentIndicator.incident_id) >= 2)
                .subquery()
            )
        ) or 0

    total_count = len(rows)
    total_value, total_hidden = _suppressed(total_count, enabled=suppress)
    open_value, open_hidden = _suppressed(open_count, enabled=suppress)
    high_risk_value, high_hidden = _suppressed(high_risk_open, enabled=suppress)
    linked_value, linked_hidden = _suppressed(linked_incidents, enabled=suppress)
    shared_value, shared_hidden = _suppressed(int(shared_indicator_count), enabled=suppress)
    suppressed_cells += sum(
        1
        for hidden in (
            total_hidden,
            open_hidden,
            high_hidden,
            linked_hidden,
            shared_hidden,
        )
        if hidden
    )

    mean_risk = None
    if risks and not (suppress and total_count < K_THRESHOLD):
        mean_risk = round(sum(risks) / len(risks), 1)
    mean_resolution = None
    if resolutions and not (suppress and len(resolutions) < K_THRESHOLD):
        mean_resolution = round(sum(resolutions) / len(resolutions), 1)

    return {
        "scope": "national" if national else "organisation",
        "generated_at": now,
        "organisation": None
        if national
        else {
            "id": user.organisation.id,
            "name": user.organisation.name,
            "slug": user.organisation.slug,
        },
        "summary": {
            "total": total_value,
            "open": open_value,
            "high_risk": high_risk_value,
            "linked_incidents": linked_value,
            "shared_indicators": shared_value,
            "mean_risk": mean_risk,
            "mean_resolution_hours": mean_resolution,
            "organisations": len(organisation_ids) if national else None,
            "suppressed_cells": suppressed_cells,
            "k_threshold": K_THRESHOLD,
        },
        "trend": trend,
        "severity": severity_items,
        "categories": category_items,
        "channels": channel_items,
        "states": state_items,
        "statuses": status_items,
        "top_indicators": top_indicators,
    }


def organisation_dashboard(db: Session, user: User) -> dict:
    """Exact, tenant-scoped situational awareness for one organisation."""

    return _dashboard_data(db, user, national=False)


def national_dashboard(db: Session, user: User) -> dict:
    """Cross-tenant aggregates with k-anonymity suppression applied here."""

    return _dashboard_data(db, user, national=True)


def _csv_value(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, datetime):
        return _as_utc(value).isoformat() if _as_utc(value) else ""
    return str(value)


def dashboard_csv(dashboard: dict) -> str:
    """Serialise a dashboard without ever writing a suppressed raw value."""

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["section", "key", "label", "value", "suppressed"])
    writer.writerow(
        [
            "meta",
            "scope",
            dashboard["scope"],
            dashboard["scope"],
            "no",
        ]
    )
    writer.writerow(
        [
            "meta",
            "generated_at",
            "Generated at",
            _csv_value(dashboard["generated_at"]),
            "no",
        ]
    )
    k = dashboard["summary"]["k_threshold"]
    writer.writerow(["meta", "k_threshold", "k-anonymity threshold", k, "no"])

    for key, value in dashboard["summary"].items():
        if key in {"suppressed_cells", "k_threshold"}:
            continue
        hidden = value is None and key in {
            "total",
            "open",
            "high_risk",
            "linked_incidents",
            "shared_indicators",
        }
        writer.writerow(
            ["summary", key, key.replace("_", " ").title(), "" if hidden else _csv_value(value), "yes" if hidden else "no"]
        )
    writer.writerow(
        [
            "summary",
            "suppressed_cells",
            "Suppressed cells",
            dashboard["summary"]["suppressed_cells"],
            "no",
        ]
    )

    for point in dashboard["trend"]:
        writer.writerow(
            [
                "trend",
                point["date"],
                point["date"],
                "" if point["total"] is None else point["total"],
                "yes" if point["suppressed"] else "no",
            ]
        )
        writer.writerow(
            [
                "trend_high_risk",
                point["date"],
                point["date"],
                "" if point["high_risk"] is None else point["high_risk"],
                "yes" if point["high_risk"] is None and point["suppressed"] else "no",
            ]
        )

    for section in ("severity", "categories", "channels", "states", "statuses"):
        for cell in dashboard[section]:
            writer.writerow(
                [
                    section,
                    cell["key"],
                    cell["label"],
                    "" if cell["suppressed"] else cell["count"],
                    "yes" if cell["suppressed"] else "no",
                ]
            )

    for item in dashboard["top_indicators"]:
        writer.writerow(
            [
                "top_indicators",
                item["kind"],
                item["display_value"],
                item["incident_count"],
                "no",
            ]
        )
    return buffer.getvalue()


def indicator_csv(items: list[dict]) -> str:
    """Serialise indicator rows for permission-checked export."""

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "kind",
            "value",
            "incident_count",
            "first_seen_at",
            "last_seen_at",
            "example_incident_reference",
        ]
    )
    for item in items:
        writer.writerow(
            [
                item["kind"],
                item["value"],
                item["incident_count"],
                _csv_value(item["first_seen_at"]),
                _csv_value(item["last_seen_at"]),
                item.get("example_incident_reference") or "",
            ]
        )
    return buffer.getvalue()


def record_export(
    db: Session,
    user: User,
    *,
    scope: str,
    row_count: int,
    suppressed_cells: int = 0,
    format_name: str = "csv",
) -> None:
    """Audit every CSV export without storing the exported rows."""

    record_audit(
        db,
        action="intelligence.exported",
        actor_id=user.id,
        organisation_id=user.organisation_id,
        resource_type="dashboard",
        resource_id=scope,
        detail={
            "scope": scope,
            "format": format_name,
            "row_count": row_count,
            "suppressed_cells": suppressed_cells,
        },
    )
    db.commit()
