"""Evidence upload, listing and audited download."""

from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser
from app.db.session import get_db
from app.schemas.incidents import EvidenceOut
from app.services import evidence as evidence_service
from app.services import incidents as incident_service

router = APIRouter(prefix="/incidents", tags=["evidence"])
DbSession = Annotated[Session, Depends(get_db)]


@router.post(
    "/{incident_id}/evidence",
    response_model=EvidenceOut,
    status_code=status.HTTP_201_CREATED,
    summary="Upload evidence",
)
def upload_evidence(
    incident_id: str,
    current_user: CurrentUser,
    db: DbSession,
    file: Annotated[UploadFile, File(description="PNG, JPEG, WebP, PDF, TXT or EML up to 10 MB")],
) -> EvidenceOut:
    """Validate, hash and store one evidence file."""

    incident = incident_service.get_incident_for_user(db, current_user, incident_id)
    return evidence_service.store_evidence(db, current_user, incident, file)


@router.get(
    "/{incident_id}/evidence",
    response_model=list[EvidenceOut],
    summary="List evidence",
)
def list_evidence(
    incident_id: str, current_user: CurrentUser, db: DbSession
) -> list:
    """List evidence attached to an authorised incident."""

    incident = incident_service.get_incident_for_user(db, current_user, incident_id, full=True)
    return incident.evidence


@router.get(
    "/{incident_id}/evidence/{evidence_id}/download",
    response_class=FileResponse,
    summary="Download evidence and log the access",
)
def download_evidence(
    incident_id: str,
    evidence_id: str,
    current_user: CurrentUser,
    db: DbSession,
) -> FileResponse:
    """Return a stored file and append the access to timeline and audit chain."""

    incident = incident_service.get_incident_for_user(db, current_user, incident_id, full=True)
    evidence = evidence_service.find_evidence(incident, evidence_id)
    path = evidence_service.evidence_path(evidence)
    evidence_service.record_access(db, current_user, incident, evidence)

    return FileResponse(
        path,
        media_type=evidence.content_type,
        filename=evidence.original_filename,
        headers={
            "X-Content-SHA256": evidence.sha256,
            "Cache-Control": "no-store",
        },
    )
