"""Resilience assessment and synthetic exercise endpoints.

Both modules are analyst-facing: reporters do not see organisational readiness
or exercise records. Tenant isolation is enforced in the service layer.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import AnalystUser
from app.db.session import get_db
from app.schemas.resilience import (
    AssessmentCreate,
    AssessmentDetail,
    AssessmentListItem,
    ExerciseCreate,
    ExerciseDetail,
    ExerciseListItem,
    ExerciseTaskUpdate,
    FindingUpdate,
    QuestionnaireOut,
    ResilienceSummary,
)
from app.services import resilience as resilience_service

router = APIRouter(prefix="/resilience", tags=["resilience"])
DbSession = Annotated[Session, Depends(get_db)]


@router.get("/questionnaire", response_model=QuestionnaireOut, summary="Readiness questionnaire")
def questionnaire(current_user: AnalystUser) -> QuestionnaireOut:
    """Return the fixed 12-control readiness questionnaire."""

    return resilience_service.questionnaire()


@router.get("/summary", response_model=ResilienceSummary, summary="Readiness headline counts")
def summary(current_user: AnalystUser, db: DbSession) -> ResilienceSummary:
    """Return the latest score and open findings for the caller's organisation."""

    return resilience_service.resilience_summary(db, current_user)


@router.get(
    "/assessments",
    response_model=list[AssessmentListItem],
    summary="List readiness assessments",
)
def list_assessments(current_user: AnalystUser, db: DbSession) -> list[AssessmentListItem]:
    return resilience_service.list_assessments(db, current_user)


@router.post(
    "/assessments",
    response_model=AssessmentDetail,
    status_code=status.HTTP_201_CREATED,
    summary="Score a readiness assessment",
)
def create_assessment(
    payload: AssessmentCreate, current_user: AnalystUser, db: DbSession
) -> AssessmentDetail:
    """Score a complete answer set and open a finding for every gap."""

    return resilience_service.create_assessment(db, current_user, payload)


@router.get(
    "/assessments/{assessment_id}",
    response_model=AssessmentDetail,
    summary="Assessment detail",
)
def get_assessment(
    assessment_id: str, current_user: AnalystUser, db: DbSession
) -> AssessmentDetail:
    return resilience_service.get_assessment(db, current_user, assessment_id)


@router.patch(
    "/findings/{finding_id}",
    response_model=AssessmentDetail,
    summary="Update a finding's remediation state",
)
def update_finding(
    finding_id: int, payload: FindingUpdate, current_user: AnalystUser, db: DbSession
) -> AssessmentDetail:
    return resilience_service.update_finding(db, current_user, finding_id, payload)


@router.get(
    "/exercises",
    response_model=list[ExerciseListItem],
    summary="List synthetic exercises",
)
def list_exercises(current_user: AnalystUser, db: DbSession) -> list[ExerciseListItem]:
    return resilience_service.list_exercises(db, current_user)


@router.post(
    "/exercises",
    response_model=ExerciseDetail,
    status_code=status.HTTP_201_CREATED,
    summary="Start a synthetic exercise",
)
def create_exercise(
    payload: ExerciseCreate, current_user: AnalystUser, db: DbSession
) -> ExerciseDetail:
    """Start the fixed phishing-triage tabletop with six tracked tasks."""

    return resilience_service.create_exercise(db, current_user, payload)


@router.get(
    "/exercises/{exercise_id}",
    response_model=ExerciseDetail,
    summary="Exercise detail",
)
def get_exercise(exercise_id: str, current_user: AnalystUser, db: DbSession) -> ExerciseDetail:
    return resilience_service.get_exercise(db, current_user, exercise_id)


@router.patch(
    "/exercises/{exercise_id}/tasks/{task_id}",
    response_model=ExerciseDetail,
    summary="Record exercise task progress",
)
def update_exercise_task(
    exercise_id: str,
    task_id: int,
    payload: ExerciseTaskUpdate,
    current_user: AnalystUser,
    db: DbSession,
) -> ExerciseDetail:
    return resilience_service.update_exercise_task(
        db, current_user, exercise_id, task_id, payload
    )


@router.post(
    "/exercises/{exercise_id}/complete",
    response_model=ExerciseDetail,
    summary="Complete an exercise",
)
def complete_exercise(
    exercise_id: str, current_user: AnalystUser, db: DbSession
) -> ExerciseDetail:
    """Close the exercise once every task is done or skipped."""

    return resilience_service.complete_exercise(db, current_user, exercise_id)
