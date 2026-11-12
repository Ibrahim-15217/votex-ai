"""Resilience assessment and synthetic exercise services.

All reads and writes are scoped to the caller's organisation. A record that
belongs to another tenant returns 404 rather than 403 so existence is not
disclosed, matching the incident and evidence rules.
"""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone

from fastapi import HTTPException, status as http_status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.resilience import (
    CONTROL_KEYS,
    CONTROLS,
    EXERCISE_SCENARIO,
    EXERCISE_TASKS,
    MATURITY_LABELS,
    band_for,
    derive_findings,
    score_answers,
    summary_for,
)
from app.core.time import utcnow
from app.db.models import Exercise, ExerciseTask, ResilienceAssessment, ResilienceFinding, User
from app.schemas.resilience import (
    AssessmentCreate,
    AssessmentDetail,
    AssessmentListItem,
    ControlOut,
    ExerciseCreate,
    ExerciseDetail,
    ExerciseListItem,
    ExercisePerformance,
    ExerciseTaskOut,
    ExerciseTaskUpdate,
    FindingOut,
    FindingUpdate,
    QuestionnaireOut,
    ResilienceSummary,
)
from app.schemas.users import UserSummary
from app.services.audit import record_audit

NOT_FOUND = "Assessment not found."
EXERCISE_NOT_FOUND = "Exercise not found."

_ASSESSMENT_OPTIONS = (
    selectinload(ResilienceAssessment.findings),
    selectinload(ResilienceAssessment.created_by),
)
_EXERCISE_OPTIONS = (
    selectinload(Exercise.tasks).selectinload(ExerciseTask.completed_by),
    selectinload(Exercise.created_by),
)


def questionnaire() -> QuestionnaireOut:
    """Return the fixed control list and maturity labels."""

    return QuestionnaireOut(
        controls=[ControlOut(**asdict(control)) for control in CONTROLS],
        maturity_levels=MATURITY_LABELS,
        scoring_note=(
            "Every control is scored 0–4 with equal weight. The score is the mean "
            "maturity across the 12 controls, scaled to 100. It is a prototype "
            "readiness check, not a certified index."
        ),
    )


def _load_assessment(db: Session, user: User, assessment_id: str) -> ResilienceAssessment:
    assessment = db.scalar(
        select(ResilienceAssessment)
        .options(*_ASSESSMENT_OPTIONS)
        .where(
            ResilienceAssessment.id == assessment_id,
            ResilienceAssessment.organisation_id == user.organisation_id,
        )
    )
    if assessment is None:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return assessment


def _assessment_detail(assessment: ResilienceAssessment) -> AssessmentDetail:
    return AssessmentDetail(
        **AssessmentListItem.model_validate(assessment).model_dump(),
        notes=assessment.notes,
        summary=assessment.summary,
        answers=assessment.answers,
        controls=[ControlOut(**asdict(control)) for control in CONTROLS],
        findings=[FindingOut.model_validate(finding) for finding in assessment.findings],
        created_by=(
            UserSummary.model_validate(assessment.created_by)
            if assessment.created_by
            else None
        ),
    )


def create_assessment(db: Session, user: User, payload: AssessmentCreate) -> AssessmentDetail:
    """Score a complete answer set, open findings and audit the result."""

    answers = {key: int(payload.answers[key]) for key in CONTROL_KEYS}
    score = score_answers(answers)
    band = band_for(score)
    derived = derive_findings(answers)

    assessment = ResilienceAssessment(
        organisation_id=user.organisation_id,
        created_by_id=user.id,
        title=payload.title,
        notes=payload.notes or "",
        status="completed",
        assessment_date=utcnow(),
        score=score,
        band=band,
        answers_json=answers,
        summary=summary_for(score, band, derived),
    )
    db.add(assessment)
    db.flush()

    for item in derived:
        db.add(
            ResilienceFinding(
                assessment_id=assessment.id,
                organisation_id=user.organisation_id,
                category=item["category"],
                title=item["title"],
                detail=item["detail"],
                severity=item["severity"],
                remediation_status="open",
            )
        )

    record_audit(
        db,
        action="resilience.assessment_created",
        actor_id=user.id,
        organisation_id=user.organisation_id,
        resource_type="resilience_assessment",
        resource_id=assessment.id,
        detail={
            "score": score,
            "band": band,
            "open_findings": len(derived),
            "title": payload.title,
        },
    )
    db.commit()
    return _assessment_detail(_load_assessment(db, user, assessment.id))


def list_assessments(db: Session, user: User) -> list[AssessmentListItem]:
    """Return the organisation's assessments, newest first."""

    rows = db.scalars(
        select(ResilienceAssessment)
        .options(*_ASSESSMENT_OPTIONS)
        .where(ResilienceAssessment.organisation_id == user.organisation_id)
        .order_by(ResilienceAssessment.assessment_date.desc(), ResilienceAssessment.created_at.desc())
    ).all()
    return [AssessmentListItem.model_validate(row) for row in rows]


def get_assessment(db: Session, user: User, assessment_id: str) -> AssessmentDetail:
    return _assessment_detail(_load_assessment(db, user, assessment_id))


def update_finding(
    db: Session, user: User, finding_id: int, payload: FindingUpdate
) -> AssessmentDetail:
    """Update remediation state and return the refreshed parent assessment."""

    finding = db.get(ResilienceFinding, finding_id)
    if finding is None or finding.organisation_id != user.organisation_id:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Finding not found.")

    before = finding.remediation_status
    if payload.remediation_status is not None:
        finding.remediation_status = payload.remediation_status
    if "owner" in payload.model_fields_set:
        finding.owner = payload.owner or None
    if "due_date" in payload.model_fields_set:
        finding.due_date = payload.due_date
    finding.updated_at = utcnow()

    record_audit(
        db,
        action="resilience.finding_updated",
        actor_id=user.id,
        organisation_id=user.organisation_id,
        resource_type="resilience_finding",
        resource_id=str(finding.id),
        detail={
            "assessment_id": finding.assessment_id,
            "from_status": before,
            "to_status": finding.remediation_status,
            "severity": finding.severity,
            "note": payload.note or "",
        },
    )
    db.commit()
    return _assessment_detail(_load_assessment(db, user, finding.assessment_id))


def resilience_summary(db: Session, user: User) -> ResilienceSummary:
    """Return headline counts for the resilience page."""

    rows = db.scalars(
        select(ResilienceAssessment)
        .options(*_ASSESSMENT_OPTIONS)
        .where(ResilienceAssessment.organisation_id == user.organisation_id)
        .order_by(ResilienceAssessment.assessment_date.desc(), ResilienceAssessment.created_at.desc())
    ).all()

    open_by_severity = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    total_findings = 0
    open_findings = 0
    for assessment in rows:
        for finding in assessment.findings:
            total_findings += 1
            if finding.remediation_status == "resolved":
                continue
            open_findings += 1
            open_by_severity[finding.severity] = open_by_severity.get(finding.severity, 0) + 1

    latest = AssessmentListItem.model_validate(rows[0]) if rows else None
    return ResilienceSummary(
        total_assessments=len(rows),
        latest=latest,
        total_findings=total_findings,
        open_findings=open_findings,
        resolved_findings=total_findings - open_findings,
        open_by_severity=open_by_severity,
    )


# ---------------------------------------------------------------------------
# Synthetic exercises
# ---------------------------------------------------------------------------


def _load_exercise(db: Session, user: User, exercise_id: str) -> Exercise:
    exercise = db.scalar(
        select(Exercise)
        .options(*_EXERCISE_OPTIONS)
        .where(
            Exercise.id == exercise_id,
            Exercise.organisation_id == user.organisation_id,
        )
    )
    if exercise is None:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=EXERCISE_NOT_FOUND)
    return exercise


def _as_utc(value: datetime) -> datetime:
    """Normalise SQLite's naive timestamps before subtracting them."""

    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _performance(exercise: Exercise) -> ExercisePerformance:
    total = len(exercise.tasks)
    done = sum(1 for task in exercise.tasks if task.status == "done")
    skipped = sum(1 for task in exercise.tasks if task.status == "skipped")
    resolved = done + skipped
    completion = round(100 * done / total, 1) if total else 0.0
    end = _as_utc(exercise.completed_at or utcnow())
    elapsed = max(0, int((end - _as_utc(exercise.started_at)).total_seconds()))

    if total and resolved == total and completion >= 80:
        grade = "ready"
        note = "Every task was resolved and the decision path is complete."
    elif completion >= 50:
        grade = "developing"
        note = "Most tasks are complete; finish the remainder to reach a ready grade."
    else:
        grade = "needs_review"
        note = "Less than half of the tasks are complete. Review the scenario and retry."

    return ExercisePerformance(
        tasks_total=total,
        tasks_done=done,
        tasks_skipped=skipped,
        tasks_resolved=resolved,
        completion_pct=completion,
        elapsed_seconds=elapsed,
        grade=grade,
        note=note,
    )


def _exercise_detail(exercise: Exercise) -> ExerciseDetail:
    return ExerciseDetail(
        **ExerciseListItem.model_validate(exercise).model_dump(),
        tasks=[ExerciseTaskOut.model_validate(task) for task in exercise.tasks],
        performance=_performance(exercise),
        created_by=(
            UserSummary.model_validate(exercise.created_by) if exercise.created_by else None
        ),
    )


def create_exercise(db: Session, user: User, payload: ExerciseCreate) -> ExerciseDetail:
    """Start a new copy of the fixed synthetic phishing-triage scenario."""

    title = payload.title or str(EXERCISE_SCENARIO["title"])
    exercise = Exercise(
        organisation_id=user.organisation_id,
        created_by_id=user.id,
        scenario_key=str(EXERCISE_SCENARIO["key"]),
        title=title,
        summary=str(EXERCISE_SCENARIO["summary"]),
        status="running",
        started_at=utcnow(),
    )
    db.add(exercise)
    db.flush()

    for item in EXERCISE_TASKS:
        db.add(
            ExerciseTask(
                exercise_id=exercise.id,
                organisation_id=user.organisation_id,
                sequence=int(item["sequence"]),
                title=str(item["title"]),
                description=str(item["description"]),
                expected_action=str(item["expected_action"]),
                status="pending",
            )
        )

    record_audit(
        db,
        action="resilience.exercise_created",
        actor_id=user.id,
        organisation_id=user.organisation_id,
        resource_type="exercise",
        resource_id=exercise.id,
        detail={"scenario": exercise.scenario_key, "tasks": len(EXERCISE_TASKS)},
    )
    db.commit()
    return _exercise_detail(_load_exercise(db, user, exercise.id))


def list_exercises(db: Session, user: User) -> list[ExerciseListItem]:
    rows = db.scalars(
        select(Exercise)
        .options(*_EXERCISE_OPTIONS)
        .where(Exercise.organisation_id == user.organisation_id)
        .order_by(Exercise.created_at.desc())
    ).all()
    return [ExerciseListItem.model_validate(row) for row in rows]


def get_exercise(db: Session, user: User, exercise_id: str) -> ExerciseDetail:
    return _exercise_detail(_load_exercise(db, user, exercise_id))


def update_exercise_task(
    db: Session,
    user: User,
    exercise_id: str,
    task_id: int,
    payload: ExerciseTaskUpdate,
) -> ExerciseDetail:
    """Record progress on one exercise task."""

    exercise = _load_exercise(db, user, exercise_id)
    if exercise.status == "completed":
        raise HTTPException(
            status_code=http_status.HTTP_409_CONFLICT,
            detail="This exercise is completed and its record is read-only.",
        )

    task = next((item for item in exercise.tasks if item.id == task_id), None)
    if task is None:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Task not found.")

    before = task.status
    task.status = payload.status
    if payload.notes is not None:
        task.notes = payload.notes
    if payload.status in {"done", "skipped"}:
        task.completed_at = utcnow()
        task.completed_by_id = user.id
    else:
        task.completed_at = None
        task.completed_by_id = None
    task.updated_at = utcnow()

    record_audit(
        db,
        action="resilience.exercise_task_updated",
        actor_id=user.id,
        organisation_id=user.organisation_id,
        resource_type="exercise_task",
        resource_id=str(task.id),
        detail={
            "exercise_id": exercise.id,
            "sequence": task.sequence,
            "from_status": before,
            "to_status": task.status,
        },
    )
    db.commit()
    return _exercise_detail(_load_exercise(db, user, exercise.id))


def complete_exercise(db: Session, user: User, exercise_id: str) -> ExerciseDetail:
    """Close an exercise once every task is done or skipped."""

    exercise = _load_exercise(db, user, exercise_id)
    if exercise.status == "completed":
        return _exercise_detail(exercise)

    unresolved = [task for task in exercise.tasks if task.status in {"pending", "in_progress"}]
    if unresolved:
        raise HTTPException(
            status_code=http_status.HTTP_409_CONFLICT,
            detail=(
                "Finish or skip every task before completing the exercise. "
                f"Still open: {len(unresolved)}."
            ),
        )

    exercise.status = "completed"
    exercise.completed_at = utcnow()
    performance = _performance(exercise)

    record_audit(
        db,
        action="resilience.exercise_completed",
        actor_id=user.id,
        organisation_id=user.organisation_id,
        resource_type="exercise",
        resource_id=exercise.id,
        detail={
            "completion_pct": performance.completion_pct,
            "tasks_done": performance.tasks_done,
            "tasks_skipped": performance.tasks_skipped,
            "grade": performance.grade,
        },
    )
    db.commit()
    return _exercise_detail(_load_exercise(db, user, exercise.id))


def seeded_answers() -> dict[str, int]:
    """Deterministic answer set used by the demo tenant."""

    return {
        "governance.owner": 4,
        "governance.plan": 3,
        "governance.vendor": 2,
        "identity.mfa": 4,
        "identity.privileged": 3,
        "identity.phishing_resistant": 1,
        "network.inventory": 3,
        "network.email": 4,
        "data.backup": 3,
        "data.retention": 2,
        "response.exercise": 3,
        "people.awareness": 2,
    }
