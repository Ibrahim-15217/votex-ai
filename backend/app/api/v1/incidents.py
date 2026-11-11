"""Incident reporting, triage and response endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import AnalystUser, CurrentUser
from app.db.session import get_db
from app.schemas.incidents import (
    AssignmentRequest,
    CommentRequest,
    IncidentCreate,
    IncidentDetail,
    IncidentEventOut,
    IncidentPage,
    IncidentStats,
    PriorityUpdateRequest,
    ResponseActionRequest,
    Status,
    StatusUpdateRequest,
)
from app.schemas.intelligence import RelatedIncidentList
from app.services import analysis as analysis_service
from app.services import correlation as correlation_service
from app.services import incidents as incident_service

router = APIRouter(prefix="/incidents", tags=["incidents"])
DbSession = Annotated[Session, Depends(get_db)]


@router.get("/stats", response_model=IncidentStats, summary="Overview counters")
def stats(current_user: CurrentUser, db: DbSession) -> dict:
    """Return scope-aware counters for the operations dashboard."""

    return incident_service.incident_stats(db, current_user)


@router.get("", response_model=IncidentPage, summary="List incidents")
def list_incidents(
    current_user: CurrentUser,
    db: DbSession,
    status_filter: Annotated[Status | None, Query(alias="status")] = None,
    priority: Annotated[str | None, Query(pattern="^(low|medium|high|critical)$")] = None,
    category: Annotated[str | None, Query(max_length=40)] = None,
    search: Annotated[str | None, Query(max_length=120)] = None,
    assigned_to_me: bool = False,
    page: Annotated[int, Query(ge=1, le=10_000)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> IncidentPage:
    """Return a filtered page of incidents visible to the caller.

    Reporters only ever see incidents they submitted. Analysts and
    administrators see every incident in their organisation.
    """

    items, total = incident_service.list_incidents(
        db,
        current_user,
        status=status_filter,
        priority=priority,
        category=category,
        search=search,
        assigned_to_me=assigned_to_me,
        page=page,
        page_size=page_size,
    )
    return IncidentPage(items=items, total=total, page=page, page_size=page_size)


@router.post(
    "",
    response_model=IncidentDetail,
    status_code=status.HTTP_201_CREATED,
    summary="Report an incident",
)
def create_incident(
    payload: IncidentCreate, current_user: CurrentUser, db: DbSession
) -> IncidentDetail:
    """Create an incident and open its timeline."""

    return incident_service.create_incident(db, current_user, payload)


@router.get("/{incident_id}", response_model=IncidentDetail, summary="Incident detail")
def get_incident(incident_id: str, current_user: CurrentUser, db: DbSession) -> IncidentDetail:
    """Return one incident with its timeline and evidence list."""

    return incident_service.get_incident_for_user(db, current_user, incident_id)


@router.get(
    "/{incident_id}/related",
    response_model=RelatedIncidentList,
    summary="Incidents sharing an indicator",
)
def related_incidents(
    incident_id: str, current_user: CurrentUser, db: DbSession
) -> RelatedIncidentList:
    """Return visible incidents in the same organisation sharing an indicator.

    Reporters only see incidents they submitted, so cross-reporter correlation
    is never exposed to them.
    """

    incident = incident_service.get_incident_for_user(
        db, current_user, incident_id, full=False
    )
    return correlation_service.related_incidents(db, current_user, incident)


@router.patch(
    "/{incident_id}/assignment",
    response_model=IncidentDetail,
    summary="Assign or reassign an incident",
)
def assign_incident(
    incident_id: str,
    payload: AssignmentRequest,
    current_user: AnalystUser,
    db: DbSession,
) -> IncidentDetail:
    """Assign an incident to an active analyst in the same organisation."""

    incident = incident_service.get_incident_for_user(db, current_user, incident_id)
    return incident_service.assign_incident(db, current_user, incident, payload.assignee_id)


@router.patch(
    "/{incident_id}/status",
    response_model=IncidentDetail,
    summary="Advance the incident lifecycle",
)
def change_status(
    incident_id: str,
    payload: StatusUpdateRequest,
    current_user: AnalystUser,
    db: DbSession,
) -> IncidentDetail:
    """Apply an allowed status transition and record who made it."""

    incident = incident_service.get_incident_for_user(db, current_user, incident_id)
    return incident_service.change_status(db, current_user, incident, payload.status, payload.note)


@router.patch(
    "/{incident_id}/priority",
    response_model=IncidentDetail,
    summary="Update incident priority",
)
def change_priority(
    incident_id: str,
    payload: PriorityUpdateRequest,
    current_user: AnalystUser,
    db: DbSession,
) -> IncidentDetail:
    """Update the analyst-assigned priority."""

    incident = incident_service.get_incident_for_user(db, current_user, incident_id)
    return incident_service.change_priority(db, current_user, incident, payload.priority)


@router.post(
    "/{incident_id}/analyze",
    response_model=IncidentDetail,
    summary="Re-run the hybrid AI analysis",
)
def analyse_incident(
    incident_id: str,
    current_user: AnalystUser,
    db: DbSession,
) -> IncidentDetail:
    """Create a new explainable analysis without altering earlier runs."""

    incident = incident_service.get_incident_for_user(db, current_user, incident_id)
    try:
        analysis_service.analyse_and_store(db, incident, current_user, automatic=False)
    except Exception as exc:  # engine failures must not crash the request thread
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI analysis failed. The report is unchanged; please retry.",
        ) from exc
    return incident_service.reload_incident(db, current_user, incident_id)


@router.post(
    "/{incident_id}/actions",
    response_model=IncidentEventOut,
    status_code=status.HTTP_201_CREATED,
    summary="Record a response action",
)
def record_action(
    incident_id: str,
    payload: ResponseActionRequest,
    current_user: AnalystUser,
    db: DbSession,
) -> IncidentEventOut:
    """Record containment, takedown or warning activity on the timeline."""

    incident = incident_service.get_incident_for_user(db, current_user, incident_id)
    return incident_service.record_response_action(
        db, current_user, incident, payload.action_type, payload.note
    )


@router.post(
    "/{incident_id}/comments",
    response_model=IncidentEventOut,
    status_code=status.HTTP_201_CREATED,
    summary="Add an investigation note",
)
def add_comment(
    incident_id: str,
    payload: CommentRequest,
    current_user: CurrentUser,
    db: DbSession,
) -> IncidentEventOut:
    """Append a note to the incident timeline."""

    incident = incident_service.get_incident_for_user(db, current_user, incident_id)
    return incident_service.add_comment(db, current_user, incident, payload.message)
