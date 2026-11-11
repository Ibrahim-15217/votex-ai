"""Incident lifecycle, assignment, response actions and timeline."""

from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status as http_status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.core.time import utcnow
from app.db.models import Evidence, Incident, IncidentEvent, User
from app.schemas.incidents import IncidentCreate
from app.services.analysis import analyse_and_store
from app.services.audit import record_audit

ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    "submitted": {"under_review", "closed"},
    "under_review": {"assigned", "investigating", "closed"},
    "assigned": {"investigating", "under_review", "closed"},
    "investigating": {"escalated", "contained", "closed"},
    "escalated": {"investigating", "contained", "closed"},
    "contained": {"remediated", "closed"},
    "remediated": {"recovered", "closed"},
    "recovered": {"closed"},
    "closed": set(),
}

FULL_OPTIONS = (
    selectinload(Incident.reporter),
    selectinload(Incident.assignee),
    selectinload(Incident.events).selectinload(IncidentEvent.actor),
    selectinload(Incident.evidence).selectinload(Evidence.uploader),
    selectinload(Incident.analyses),
)

LIST_OPTIONS = (
    selectinload(Incident.reporter),
    selectinload(Incident.assignee),
    selectinload(Incident.evidence),
)


def humanise(value: str) -> str:
    """Turn a machine value into a readable label."""

    return value.replace("_", " ").replace("-", " ").strip().capitalize()


def generate_reference(db: Session) -> str:
    """Generate a unique, human-readable incident reference."""

    year = utcnow().year
    for _ in range(10):
        candidate = f"VX-{year}-{secrets.token_hex(3).upper()}"
        exists = db.scalar(select(Incident.id).where(Incident.reference == candidate))
        if not exists:
            return candidate
    raise HTTPException(
        status_code=http_status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Could not allocate an incident reference. Please retry.",
    )


def get_incident_for_user(
    db: Session, user: User, incident_id: str, *, full: bool = True
) -> Incident:
    """Load an incident inside the user's organisation.

    Reporters can only read incidents they submitted. Foreign and forbidden
    records both return 404 so existence is not leaked.
    """

    options = FULL_OPTIONS if full else LIST_OPTIONS
    incident = db.scalar(
        select(Incident)
        .options(*options)
        .where(
            Incident.id == incident_id,
            Incident.organisation_id == user.organisation_id,
        )
    )
    if incident is None:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Incident not found.")
    if user.role == "reporter" and incident.reporter_id != user.id:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Incident not found.")
    return incident


def reload_incident(db: Session, user: User, incident_id: str) -> Incident:
    """Reload an incident with its full timeline after a write."""

    db.expire_all()
    return get_incident_for_user(db, user, incident_id, full=True)


def add_event(
    db: Session,
    incident: Incident,
    actor: User | None,
    event_type: str,
    message: str,
    metadata: dict | None = None,
) -> IncidentEvent:
    """Append a timeline event and touch the incident."""

    event = IncidentEvent(
        incident_id=incident.id,
        actor_id=actor.id if actor else None,
        event_type=event_type,
        message=message,
        event_metadata=metadata or {},
        created_at=utcnow(),
    )
    incident.updated_at = utcnow()
    db.add(event)
    return event


def list_incidents(
    db: Session,
    user: User,
    *,
    status: str | None = None,
    priority: str | None = None,
    category: str | None = None,
    search: str | None = None,
    assigned_to_me: bool = False,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Incident], int]:
    """Return a filtered page of incidents visible to the user."""

    conditions = [Incident.organisation_id == user.organisation_id]
    if user.role == "reporter":
        conditions.append(Incident.reporter_id == user.id)
    if status:
        conditions.append(Incident.status == status)
    if priority:
        conditions.append(Incident.priority == priority)
    if category:
        conditions.append(Incident.category == category)
    if assigned_to_me:
        conditions.append(Incident.assignee_id == user.id)
    if search:
        term = f"%{search.strip()}%"
        conditions.append(or_(Incident.title.ilike(term), Incident.reference.ilike(term)))

    total = db.scalar(select(func.count()).select_from(Incident).where(*conditions)) or 0
    incidents = db.scalars(
        select(Incident)
        .options(*LIST_OPTIONS)
        .where(*conditions)
        .order_by(Incident.created_at.desc(), Incident.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return list(incidents), total


def create_incident(db: Session, user: User, payload: IncidentCreate) -> Incident:
    """Create an incident, its first timeline event and an audit entry."""

    priority = payload.priority if user.role in {"admin", "analyst"} else "medium"
    incident = Incident(
        reference=generate_reference(db),
        organisation_id=user.organisation_id,
        reporter_id=user.id,
        title=payload.title,
        description=payload.description,
        category=payload.category,
        channel=payload.channel,
        reported_url=payload.reported_url,
        state=payload.state,
        status="submitted",
        priority=priority,
        ai_status="pending",
        created_at=utcnow(),
        updated_at=utcnow(),
    )
    db.add(incident)
    db.flush()

    add_event(
        db,
        incident,
        user,
        "created",
        f"Incident reported through {humanise(payload.channel)}.",
        {"status": "submitted", "priority": priority},
    )
    record_audit(
        db,
        action="incident.created",
        actor_id=user.id,
        organisation_id=user.organisation_id,
        resource_type="incident",
        resource_id=incident.id,
        detail={
            "reference": incident.reference,
            "category": incident.category,
            "channel": incident.channel,
            "priority": incident.priority,
            "status": incident.status,
        },
    )
    db.commit()
    incident = reload_incident(db, user, incident.id)

    # Automatic triage: a failed analysis must never lose the report itself.
    try:
        analyse_and_store(db, incident, user, automatic=True)
    except Exception:
        incident = reload_incident(db, user, incident.id)
        incident.ai_status = "failed"
        db.commit()
    return reload_incident(db, user, incident.id)


def assign_incident(db: Session, user: User, incident: Incident, assignee_id: int) -> Incident:
    """Assign or reassign an incident to an analyst in the same organisation."""

    assignee = db.scalar(
        select(User).where(
            User.id == assignee_id,
            User.organisation_id == user.organisation_id,
            User.is_active.is_(True),
        )
    )
    if assignee is None or assignee.role not in {"admin", "analyst"}:
        raise HTTPException(
            status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Choose an active analyst or administrator in your organisation.",
        )

    previous_assignee = incident.assignee_id
    incident.assignee_id = assignee.id
    previous_status = incident.status
    if incident.status in {"submitted", "under_review"}:
        incident.status = "assigned"

    add_event(
        db,
        incident,
        user,
        "assigned",
        f"Assigned to {assignee.full_name}.",
        {
            "assignee_id": assignee.id,
            "previous_assignee_id": previous_assignee,
            "previous_status": previous_status,
            "status": incident.status,
        },
    )
    record_audit(
        db,
        action="incident.assigned",
        actor_id=user.id,
        organisation_id=user.organisation_id,
        resource_type="incident",
        resource_id=incident.id,
        detail={
            "reference": incident.reference,
            "assignee_id": assignee.id,
            "previous_assignee_id": previous_assignee,
            "status": incident.status,
        },
    )
    db.commit()
    return reload_incident(db, user, incident.id)


def change_status(
    db: Session,
    user: User,
    incident: Incident,
    target_status: str,
    note: str | None = None,
) -> Incident:
    """Apply an allowed status transition and record it."""

    if target_status not in ALLOWED_TRANSITIONS.get(incident.status, set()):
        raise HTTPException(
            status_code=http_status.HTTP_409_CONFLICT,
            detail=(
                f"Cannot move an incident from {humanise(incident.status)} "
                f"to {humanise(target_status)}."
            ),
        )
    if target_status == "assigned" and incident.assignee_id is None:
        raise HTTPException(
            status_code=http_status.HTTP_409_CONFLICT,
            detail="Assign the incident before moving it to Assigned.",
        )

    previous_status = incident.status
    incident.status = target_status
    incident.closed_at = utcnow() if target_status == "closed" else None

    message = f"Status changed from {humanise(previous_status)} to {humanise(target_status)}."
    if note:
        message = f"{message} {note.strip()}"
    add_event(
        db,
        incident,
        user,
        "status_changed",
        message,
        {"previous_status": previous_status, "status": target_status},
    )
    record_audit(
        db,
        action="incident.status_changed",
        actor_id=user.id,
        organisation_id=user.organisation_id,
        resource_type="incident",
        resource_id=incident.id,
        detail={
            "reference": incident.reference,
            "previous_status": previous_status,
            "status": target_status,
        },
    )
    db.commit()
    return reload_incident(db, user, incident.id)


def change_priority(db: Session, user: User, incident: Incident, priority: str) -> Incident:
    """Update the analyst-assigned priority."""

    previous = incident.priority
    if previous == priority:
        return incident
    incident.priority = priority
    add_event(
        db,
        incident,
        user,
        "priority_changed",
        f"Priority changed from {humanise(previous)} to {humanise(priority)}.",
        {"previous_priority": previous, "priority": priority},
    )
    record_audit(
        db,
        action="incident.priority_changed",
        actor_id=user.id,
        organisation_id=user.organisation_id,
        resource_type="incident",
        resource_id=incident.id,
        detail={
            "reference": incident.reference,
            "previous_priority": previous,
            "priority": priority,
        },
    )
    db.commit()
    return reload_incident(db, user, incident.id)


def record_response_action(
    db: Session,
    user: User,
    incident: Incident,
    action_type: str,
    note: str,
) -> IncidentEvent:
    """Record a response action without putting free text in the audit log."""

    event = add_event(
        db,
        incident,
        user,
        "response_action",
        note.strip(),
        {"action_type": action_type},
    )
    record_audit(
        db,
        action="incident.response_recorded",
        actor_id=user.id,
        organisation_id=user.organisation_id,
        resource_type="incident",
        resource_id=incident.id,
        detail={"reference": incident.reference, "action_type": action_type},
    )
    db.commit()
    db.refresh(event)
    return event


def add_comment(db: Session, user: User, incident: Incident, message: str) -> IncidentEvent:
    """Add an investigator note to the timeline."""

    event = add_event(db, incident, user, "comment", message.strip())
    record_audit(
        db,
        action="incident.comment_added",
        actor_id=user.id,
        organisation_id=user.organisation_id,
        resource_type="incident",
        resource_id=incident.id,
        detail={"reference": incident.reference},
    )
    db.commit()
    db.refresh(event)
    return event


def utc_today() -> datetime:
    """Expose a UTC datetime for seed and tests."""

    return datetime.now(timezone.utc)


def incident_stats(db: Session, user: User) -> dict:
    """Return scope-aware counters for the overview dashboard."""

    conditions = [Incident.organisation_id == user.organisation_id]
    if user.role == "reporter":
        conditions.append(Incident.reporter_id == user.id)

    rows = db.execute(
        select(
            Incident.status,
            Incident.priority,
            Incident.category,
            Incident.risk_score,
            Incident.assignee_id,
            Incident.created_at,
        ).where(*conditions)
    ).all()

    by_status: dict[str, int] = {}
    by_priority: dict[str, int] = {}
    by_category: dict[str, int] = {}
    risks: list[float] = []
    open_count = 0
    critical = 0
    unassigned = 0
    closed = 0
    recent_cutoff = utcnow() - timedelta(days=7)
    last_7_days = 0

    for status_value, priority_value, category_value, risk, assignee_id, created_at in rows:
        by_status[status_value] = by_status.get(status_value, 0) + 1
        by_priority[priority_value] = by_priority.get(priority_value, 0) + 1
        by_category[category_value] = by_category.get(category_value, 0) + 1
        if risk is not None:
            risks.append(float(risk))
        if status_value == "closed":
            closed += 1
        else:
            open_count += 1
            if assignee_id is None:
                unassigned += 1
        if priority_value == "critical" and status_value != "closed":
            critical += 1
        if created_at is not None:
            created_utc = (
                created_at.replace(tzinfo=timezone.utc)
                if created_at.tzinfo is None
                else created_at
            )
            if created_utc >= recent_cutoff:
                last_7_days += 1

    return {
        "total": len(rows),
        "open": open_count,
        "critical": critical,
        "unassigned": unassigned,
        "closed": closed,
        "last_7_days": last_7_days,
        "average_risk": round(sum(risks) / len(risks), 1) if risks else None,
        "by_status": by_status,
        "by_priority": by_priority,
        "by_category": by_category,
    }
